"""Upload a radcheck model to the Hugging Face Hub as one tagged version (private by default).

One repo per model family; every recipe is a new commit plus a git tag (v1, v2, ...), so
`main` is the latest upload and older versions stay reachable with `revision="v1"`.

Usage:
    uv run --extra rocm python -m radcheck.publish --repo Crstian19/radcheck-qwen35-4b-lora-es \
        --folder outputs/train/qwen35-4b-v2 --base Qwen/Qwen3.5-4B --tag v2 --recipe v2 \
        --injector outputs/eval/qwen35-4b-v2-full.json --bench outputs/eval-bench/qwen35-4b-v2.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

from radcheck import guard, leaderboard
from radcheck.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_EXTENDED

LOGO = Path(__file__).resolve().parents[2] / "docs" / "img" / "logo.png"


def cover(key: str | None, out: Path) -> None:
    """Wide logo with the circle swapped for this model's mascot variant (plain logo if none)."""
    import numpy as np
    from PIL import Image, ImageDraw

    out.parent.mkdir(parents=True, exist_ok=True)
    mascot = leaderboard.mascot(key) if key else None
    if not mascot or mascot.parent.name != "mascot":
        shutil.copy2(LOGO, out)
        return
    logo = Image.open(LOGO).convert("RGBA")  # transparent background, readable on dark themes
    a = np.asarray(logo)[:, : logo.width * 2 // 5]  # the circle sits in the left 40%
    # near-black outline only (the blue text is bright, the transparent paper is skipped)
    ys, xs = np.where((a[..., :3].max(axis=2) < 120) & (a[..., 3] > 128))
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 1
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    # Mascot crops carry a 6 px margin around a ~1,154 px circle; keep the same proportion.
    r += round(r * 2 * 6 / 1154)
    box = tuple(round(v) for v in (cx - r, cy - r, cx + r, cy + r))
    pad = round(r * 2 * 6 / 1166)
    size = (box[2] - box[0], box[3] - box[1])
    # The mascots are already cut to their circle with a transparent margin: clear the old
    # circle and lay the mascot over it, so no white ring is left around it.
    icon = Image.open(mascot).convert("RGBA").resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((pad - 4, pad - 4, size[0] - pad + 3, size[1] - pad + 3), fill=255)
    logo.paste(Image.new("RGBA", size, (0, 0, 0, 0)), box[:2], mask)
    logo.alpha_composite(icon, box[:2])
    logo.save(out, optimize=True)


# Shown on every card: the models are public before the radiologist's review.
PREVIEW = """> [!WARNING]
> **Research preview, not validated by a physician.** Trained and evaluated only on
> injected and synthetic errors; no clinician has reviewed its output yet. It is a learning
> project, not a medical device: it does not judge clinical correctness and must not be
> used for patient care."""


RECIPES = {
    "v1": "Errors injected into CARES reports by rules (laterality, negation, measurement); "
    "up to 3 random errors per report, 50% clean reports.",
    "v2": "As v1, but at most one error per type and report (balanced types), and 80% of the "
    "clean reports mention both sides (hard negatives against laterality false alarms).",
    "v3": "As v2, plus a wider negation injector (both directions, more negation forms) and two "
    "new types: discordancia (finding missing from the conclusion) and transcripcion "
    "(speech-recognition slip). Uses an extended system prompt.",
    "v4": "As v3, plus 2,945 synthetic reports written by Qwen3.8-27B, an extra two-error copy "
    "of 25% of the reports, and ~8% of examples made of two reports pasted together (so the "
    "model keeps looking after the first error).",
    "v4.1": "The v4 recipe trained with several seeds (4B: 42, 7 and 13; 9B: 42 and 7) and the "
    "adapters averaged into one (a model soup: the exact mean of their weight updates, so the "
    "rank adds up). No extra training; it matches or beats the best single seed on most tests "
    "without having to pick one.",
}


def _row(name: str, path: str | None) -> str:
    if not path or not Path(path).exists():
        return ""
    d = json.loads(Path(path).read_text())
    s = d.get("summary", d)
    o, t = s["overall"], s["per_type"]
    per_type = " / ".join(f"{t[k]['f1']:.3f}" for k in ("lateralidad", "negacion", "medida"))
    return (
        f"| {name} | {s['examples']} | {o['precision']:.3f} | {o['recall']:.3f} | "
        f"**{o['f1']:.3f}** | {per_type} | {s['false_alarm_rate']:.1%} |\n"
    )


def model_card(args: argparse.Namespace) -> str:
    gguf = args.kind == "gguf"
    tags = ["radiology", "spanish", "medical", "error-detection"]
    tags += ["gguf", "llama.cpp"] if gguf else ["lora", "peft", "trl"]
    front = {
        "base_model": args.base,
        "license": "cc-by-nc-sa-4.0",
        "language": ["es"],
        "tags": tags,
        "pipeline_tag": "text-generation",
    }
    if not gguf:
        front["library_name"] = "peft"
    header = "---\n" + "\n".join(f"{k}: {json.dumps(v)}" for k, v in front.items()) + "\n---\n"
    usage = (
        "```bash\nllama-server -m <file>.gguf --jinja -ngl 99\n```\n\n"
        "Send the system prompt below and the report as the user message, with "
        '`chat_template_kwargs: {"enable_thinking": false}`.'
        if gguf
        else (
            "```python\nfrom peft import PeftModel\n"
            "from transformers import AutoModelForCausalLM, AutoTokenizer\n\n"
            f'base = AutoModelForCausalLM.from_pretrained("{args.base}", dtype="bfloat16")\n'
            f'model = PeftModel.from_pretrained(base, "{args.repo}", revision="{args.tag}")\n'
            f'tok = AutoTokenizer.from_pretrained("{args.repo}", revision="{args.tag}")\n'
            'messages = [{"role": "system", "content": SYSTEM_PROMPT},\n'
            '            {"role": "user", "content": report}]\n'
            "ids = tok.apply_chat_template(messages, add_generation_prompt=True,\n"
            '                              enable_thinking=False, return_tensors="pt")\n'
            "```"
        )
    )
    config = Path(args.folder or "") / "adapter_config.json"
    rank = json.loads(config.read_text())["r"] if config.is_file() else 16
    system = SYSTEM_PROMPT_EXTENDED if args.recipe not in ("v1", "v2") else SYSTEM_PROMPT
    gguf_lora = ""
    if args.gguf_lora:
        # LoRA as GGUF on top of a community Q4 base: no need to merge a model that does
        # not fit in RAM, and MoE experts can stay in system memory.
        name = Path(args.gguf_lora).name
        gguf_lora = f"""
### llama.cpp on a 16 GB GPU

`{name}` is this adapter converted to GGUF. Apply it at load time on top of a quantised base
model (for example `{args.gguf_base}`), keeping some MoE experts in system RAM:

```bash
llama-server -m <base>.gguf --lora {name} --jinja -ngl 99 --n-cpu-moe 20 -c 16384 -np 4
```

{args.gguf_note}
"""
    if args.key:
        # Release-style comparison: hero chart + HTML table, this model highlighted.
        results = (
            '<img style="width:100%;max-width:900px" src="assets/radcheck_bench.png" '
            'alt="RadCheck-Bench-ES F1 by model">\n\n' + leaderboard.html_table(args.key) + "\n"
        )
    else:
        results = (
            "| Test set | Reports | Precision | Recall | F1 | F1 lat / neg / med | False alarms |\n"
            "|---|---|---|---|---|---|---|\n"
            + _row("Injector test (CARES test reports)", args.injector)
            + _row("RadCheck-Bench-ES v1 test (independent)", args.bench)
        )
    if gguf and args.quant_bench:
        # Quantisation is not free (v4: Q4_K_M costs 1.4-1.8 F1 points), so show each file.
        rows = ""
        for path in args.quant_bench:
            s = json.loads(Path(path).read_text())["summary"]
            quant = Path(path).stem.split("-")[-2]  # <name>-<quant>-bench.json
            rows += (
                f"| {quant} | **{s['overall']['f1']:.3f}** | {s['overall']['precision']:.3f} | "
                f"{s['overall']['recall']:.3f} | {s['false_alarm_rate']:.1%} |\n"
            )
        results += (
            "\n### These GGUF files on RadCheck-Bench-ES\n\nMeasured with `llama-server` "
            f"on {args.quant_hw}. The chart and table above use the unquantised model.\n\n"
            "| File | F1 | Precision | Recall | False alarms |\n|---|---|---|---|---|\n" + rows
        )
    return f"""{header}
<p align="center"><img src="assets/logo.png" alt="radcheck" width="420"></p>

# radcheck: {args.base.split("/")[-1]} ({args.tag})

Flags **internal inconsistencies** in Spanish radiology reports: the same finding on
different sides (`lateralidad`), something asserted in one place and denied in another
(`negacion`), and the same measurement with a different number or unit (`medida`).
{"From recipe v3 on it also flags a finding missing from the conclusion (`discordancia`) and speech-recognition slips (`transcripcion`)." if args.recipe not in ("v1", "v2") else ""}
Output is JSON with the type, the exact fragment and a one-sentence explanation.

{"Merged and quantised build of the LoRA fine-tune, for llama.cpp." if gguf else f"LoRA adapter (r{rank}) trained with TRL SFT."}

{PREVIEW}

## Version {args.tag}

Training recipe **{args.recipe}**: {RECIPES[args.recipe]}

## Usage

{usage}
{gguf_lora}
System prompt (verbatim):

```text
{system}
```

## Results

Greedy decoding. A prediction counts when the type matches and the fragment overlaps the
changed text or the mention it contradicts. False alarms = clean reports with any flag.

{results}
RadCheck-Bench-ES is a separate set of 340 synthetic reports written by another LLM with
its own errors, never used for training; it measures generalisation beyond the injector.
The injector test is built by the same rules as the training data (recipes v1/v2, three
error types). Q4_K_M sizes are those of the GGUF files on the Hub.

## Data and licence

Trained on [CARES](https://huggingface.co/datasets/SINAI/CARES) (SINAI, CC BY-NC-SA 4.0)
with synthetic errors; no real patient data was added. Released under CC BY-NC-SA 4.0.
"""


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--repo", required=True)
    ap.add_argument("--folder", required=True, help="adapter dir, or dir with .gguf files")
    ap.add_argument("--base", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--recipe", choices=sorted(RECIPES), required=True)
    ap.add_argument("--kind", choices=["lora", "gguf"], default="lora")
    ap.add_argument("--injector", help="evaluation JSON on the injector test")
    ap.add_argument("--bench", help="evaluation JSON on RadCheck-Bench-ES")
    ap.add_argument(
        "--key",
        choices=[e.key for e in leaderboard.ENTRIES],
        help="leaderboard entry for this model: adds the comparison chart and table",
    )
    ap.add_argument(
        "--card-only",
        action="store_true",
        help="only refresh README and assets on main (no new version, no tag)",
    )
    ap.add_argument("--gguf-lora", help="adapter converted to GGUF, uploaded next to it")
    ap.add_argument("--gguf-base", default="", help="suggested quantised base for --gguf-lora")
    ap.add_argument("--gguf-note", default="", help="measured result of the GGUF setup")
    ap.add_argument(
        "--quant-bench", nargs="+", help="GGUF results on the bench, one JSON per file (gguf)"
    )
    ap.add_argument("--quant-hw", default="an AMD RX 6800", help="GPU of --quant-bench")
    ap.add_argument("--public", action="store_true")
    args = ap.parse_args()

    api = HfApi()
    api.create_repo(args.repo, private=not args.public, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        if args.key:
            leaderboard.hero_chart(
                args.key, stage / "assets" / "radcheck_bench.png", leaderboard.default_logos()
            )
        cover(args.key, stage / "assets" / "logo.png")
        (stage / "README.md").write_text(model_card(args), encoding="utf-8")
        if args.gguf_lora:
            shutil.copy2(args.gguf_lora, stage / Path(args.gguf_lora).name)
        if args.card_only:
            guard.check(stage)
            commit = api.upload_folder(
                repo_id=args.repo, folder_path=stage, commit_message="Model card: comparison"
            )
            print(f"{args.repo} card -> {commit.commit_url}")
            return
        src = Path(args.folder)
        patterns = ["*.gguf"] if args.kind == "gguf" else ["adapter_*", "*.jinja", "tokenizer*"]
        for pattern in patterns:
            for f in src.glob(pattern):
                if args.kind == "gguf" and "bf16" in f.name:
                    continue  # the unquantised file is as large as the base model
                shutil.copy2(f, stage / f.name)
        guard.check(stage)  # refuse to upload leaked endpoints, secrets or personal data
        commit = api.upload_folder(
            repo_id=args.repo,
            folder_path=stage,
            commit_message=f"{args.tag}: recipe {args.recipe}",
            delete_patterns=["*"],  # each version replaces the previous files
        )
    api.create_tag(args.repo, tag=args.tag, revision=commit.oid, exist_ok=True)
    print(f"{args.repo}@{args.tag} -> {commit.commit_url}")


if __name__ == "__main__":
    main()
