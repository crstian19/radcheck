"""Comparison table (HTML) and hero chart (PNG) for the Hugging Face model cards.

Every radcheck model card shows the same comparison, with the card's own model highlighted,
in the style of large model releases: grouped rows, one column per model, best value bold.

Usage (normally called from radcheck.publish):
    uv run --extra rocm python -m radcheck.leaderboard --highlight qwen35-4b-v3 --out /tmp/card
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ACCENT = "#2a78d6"  # radcheck blue (slot 1 of the dataviz reference palette)
NEUTRAL = "#b9b8b2"
SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


@dataclass(frozen=True)
class Entry:
    key: str
    name: str
    size: str  # shown under the name
    bench: str | None  # RadCheck-Bench-ES v1 test result
    injector: str | None  # injector test v1 (1,626 examples, 3 types)
    q4_gb: float | None  # Q4_K_M GGUF size of the base model
    fine_tuned: bool = True


# Columns, in display order. Q4 sizes: our own file for the 4B, unsloth's Q4_K_M for the rest.
ENTRIES = [
    Entry(
        "qwen35-9b-v4",
        "radcheck 9B v4",
        "Qwen3.5-9B",
        "outputs/eval-night/qwen35-9b-v4-e2-bench.json",
        None,
        5.7,
    ),
    Entry(
        "qwen35-4b-v4",
        "radcheck 4B v4",
        "Qwen3.5-4B",
        "outputs/eval-v4/qwen35-4b-v4-bench.json",
        None,
        2.7,
    ),
    Entry(
        "qwen35-4b-v3",
        "radcheck 4B v3",
        "Qwen3.5-4B",
        "outputs/eval-v3/qwen35-4b-v3-bench.json",
        None,
        2.7,
    ),
    Entry(
        "qwen35-4b-v2",
        "radcheck 4B v2",
        "Qwen3.5-4B",
        "outputs/eval-bench/qwen35-4b-v2.json",
        "outputs/eval/qwen35-4b-v2-full.json",
        2.7,
    ),
    Entry(
        "qwen35-4b-v1",
        "radcheck 4B v1",
        "Qwen3.5-4B",
        "outputs/eval-bench/qwen35-4b-lora.json",
        "outputs/eval/qwen35-4b-lora-full.json",
        2.7,
    ),
    Entry(
        "qwen36-35b-a3b-v1",
        "radcheck 35B-A3B",
        "Qwen3.6-35B-A3B MoE",
        "outputs/eval-bench/qwen36-35b-a3b.json",
        "outputs/eval/qwen36-35b-a3b-lora-full.json",
        22.0,
    ),
    Entry(
        "qwen38-27b-v2",
        "radcheck 27B v2",
        "Qwen3.8-27B",
        "outputs/eval-bench/qwen38-27b-v2.json",
        "outputs/eval/qwen38-27b-v2-full.json",
        16.5,
    ),
    Entry(
        "qwen38-27b-v1",
        "radcheck 27B v1",
        "Qwen3.8-27B",
        "outputs/eval-bench/qwen38-27b-lora.json",
        "outputs/eval/qwen38-27b-lora-full.json",
        16.5,
    ),
    Entry(
        "gemma4-31b-v1",
        "Gemma 4 31B + LoRA",
        "not released",
        "outputs/eval-bench/gemma4-31b-lora.json",
        None,
        18.3,
    ),
    Entry(
        "qwen38-27b-base",
        "Qwen3.8-27B",
        "no fine-tune",
        "outputs/eval-bench/qwen38-27b-base.json",
        None,
        16.5,
        fine_tuned=False,
    ),
]


def _summary(path: str | None) -> dict | None:
    if not path or not Path(path).exists():
        return None
    d = json.loads(Path(path).read_text())
    return d.get("summary", d)


# (section, label, getter, higher_is_better, formatter)
def _rows():
    def bench(f):
        return lambda e: f(_summary(e.bench)) if _summary(e.bench) else None

    def inj(f):
        return lambda e: f(_summary(e.injector)) if _summary(e.injector) else None

    pct = "{:.1%}".format
    num = "{:.3f}".format
    bench_title = "RadCheck-Bench-ES v1 test <sub><small>(independent, 340 reports)</small></sub>"
    return [
        (bench_title, "F1", bench(lambda s: s["overall"]["f1"]), True, num),
        (bench_title, "Precision", bench(lambda s: s["overall"]["precision"]), True, num),
        (bench_title, "Recall", bench(lambda s: s["overall"]["recall"]), True, num),
        (
            bench_title,
            "F1 laterality",
            bench(lambda s: s["per_type"]["lateralidad"]["f1"]),
            True,
            num,
        ),
        (bench_title, "F1 negation", bench(lambda s: s["per_type"]["negacion"]["f1"]), True, num),
        (bench_title, "F1 measurement", bench(lambda s: s["per_type"]["medida"]["f1"]), True, num),
        (bench_title, "False alarms", bench(lambda s: s["false_alarm_rate"]), False, pct),
        (
            "Injector test <sub><small>(CARES test reports, 1,626)</small></sub>",
            "F1",
            inj(lambda s: s["overall"]["f1"]),
            True,
            num,
        ),
        (
            "Injector test <sub><small>(CARES test reports, 1,626)</small></sub>",
            "False alarms",
            inj(lambda s: s["false_alarm_rate"]),
            False,
            pct,
        ),
        ("Deployment", "Q4_K_M size (GB)", lambda e: e.q4_gb, False, "{:.1f}".format),
        (
            "Deployment",
            "Fits a 16 GB GPU",
            lambda e: None if e.q4_gb is None else float(e.q4_gb < 14),
            True,
            lambda v: "yes" if v else "no (CPU offload)",
        ),
    ]


def html_table(highlight: str) -> str:
    entries = ENTRIES
    th = "padding:10px 7px;text-align:center;border-bottom:2px solid {c};color:{c};font-size:13px"
    head = '<th style="padding:10px 7px;text-align:left;border-bottom:2px solid #2a78d6"></th>'
    for e in entries:
        hl = e.key == highlight
        style = th.format(c=ACCENT) + (
            ";font-weight:700;background:rgba(42,120,214,0.12)" if hl else ";font-weight:500"
        )
        head += f'<th style="{style}">{e.name}<br><sub><small>({e.size})</small></sub></th>'
    body, section = "", None
    for title, label, get, higher, fmt in _rows():
        if title != section:
            section = title
            body += (
                f'<tr><td colspan="{len(entries) + 1}" style="padding:8px 12px;font-weight:600;'
                f'color:{ACCENT};background:rgba(42,120,214,0.08)">{title}</td></tr>\n'
            )
        values = [get(e) for e in entries]
        present = [v for v in values if v is not None]
        best = (max if higher else min)(present) if present else None
        cells = ""
        for e, v in zip(entries, values, strict=True):
            hl = e.key == highlight
            style = "padding:7px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15)"
            if hl:
                style += ";background:rgba(42,120,214,0.06);color:#2a78d6"
            if v is not None and v == best and label != "Q4_K_M size (GB)":
                style += ";font-weight:700"
            cells += f'<td style="{style}">{"-" if v is None else fmt(v)}</td>'
        body += (
            '<tr><td style="padding:7px;padding-left:20px;border-bottom:1px solid '
            f'rgba(128,128,128,0.15)">{label}</td>{cells}</tr>\n'
        )
    return (
        '<div style="overflow-x:auto;width:100%"><table style="min-width:860px;width:100%;'
        "border-collapse:collapse;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,"
        f"'Segoe UI',Roboto,sans-serif\"><thead><tr>{head}</tr></thead><tbody>\n{body}"
        "</tbody></table></div>"
    )


# Columns of the hero chart: one per model family (latest version), then the references.
# The card's own model replaces the entry of its family and moves to the front.
HERO = [
    "qwen35-4b-v4",
    "qwen35-9b-v4",
    "qwen36-35b-a3b-v1",
    "qwen38-27b-v2",
    "gemma4-31b-v1",
    "qwen38-27b-base",
]
REFERENCES = {"gemma4-31b-v1", "qwen38-27b-base"}  # drawn after the dotted separator
# Badges under the bars: the mascot for radcheck models, the maker's avatar (from its
# Hugging Face organisation) for the reference models.
IMG = Path(__file__).resolve().parents[2] / "docs" / "img"
LOGOS = {
    "gemma4-31b-v1": IMG / "logos" / "google.png",
    "qwen38-27b-base": IMG / "logos" / "qwen.png",
}


# One mascot variant per size (ring colour + accessories); other sizes use the plain icon.
MASCOTS = {
    "qwen35-4b": "radcheck-4b",
    "qwen35-9b": "radcheck-9b",
    "qwen38-27b": "radcheck-27b",
    "qwen36-35b": "radcheck-35b-a3b",
}


def _mascot(key: str) -> Path:
    name = next((m for prefix, m in MASCOTS.items() if key.startswith(prefix)), None)
    return IMG / "mascot" / f"{name}.png" if name else IMG / "logo-icon.png"


def default_logos() -> dict[str, Path]:
    logos = {e.key: _mascot(e.key) for e in ENTRIES if e.key.startswith("qwen") and e.fine_tuned}
    return {k: p for k, p in (logos | LOGOS).items() if p.exists()}


# Pastel tints for the other columns (light versions of the reference palette hues).
TINTS = ["#d6e6f8", "#e4dcf6", "#d5efe4", "#f8e3d4", "#e7e6e1"]
PANELS = [
    ("F1", lambda s: s["overall"]["f1"]),
    ("Precision", lambda s: s["overall"]["precision"]),
    ("Recall", lambda s: s["overall"]["recall"]),
    ("Laterality F1", lambda s: s["per_type"]["lateralidad"]["f1"]),
    ("Negation F1", lambda s: s["per_type"]["negacion"]["f1"]),
    ("Measurement F1", lambda s: s["per_type"]["medida"]["f1"]),
]


def _family(key: str) -> str:
    return key.rsplit("-", 1)[0]


def _hero_columns(highlight: str) -> list[Entry]:
    by_key = {e.key: e for e in ENTRIES}
    keys = [k for k in HERO if _family(k) != _family(highlight) or k in REFERENCES]
    return [by_key[highlight]] + [by_key[k] for k in keys if k != highlight]


def _bar(ax, x: float, height: float, width: float, color: str, solid: bool) -> None:
    """Bar with rounded top corners; non-highlighted bars fade towards the baseline."""
    import numpy as np
    from matplotlib.colors import to_rgb
    from matplotlib.patches import FancyBboxPatch

    # Data units per pixel differ on x and y; mutation_aspect keeps the corners circular.
    # The box starts one radius below the baseline (hidden by ylim) so only the top is round.
    bbox = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    aspect = ((y1 - y0) / bbox.height) / ((x1 - x0) / bbox.width)
    radius = width * 0.12
    below = radius * aspect
    patch = FancyBboxPatch(
        (x - width / 2, -below),
        width,
        height + below,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        mutation_aspect=aspect,
        linewidth=0,
        facecolor=color if solid else "none",
    )
    ax.add_patch(patch)
    if not solid:
        top, bottom = np.array(to_rgb(color)), np.array(to_rgb("#f1f0ec"))
        grad = np.linspace(0, 1, 256)[:, None, None]
        img = bottom * (1 - grad) + top * grad
        im = ax.imshow(
            img,
            extent=(x - width / 2, x + width / 2, 0, height),
            origin="lower",
            aspect="auto",
            zorder=1,
        )
        im.set_clip_path(patch)


def _round_logo(path: Path, px: int = 160):
    """Logo as an RGBA array cropped to a circle, so square avatars look like badges."""
    import numpy as np
    from PIL import Image, ImageDraw

    im = Image.open(path).convert("RGBA").resize((px, px), Image.LANCZOS)
    mask = Image.new("L", (px, px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, px - 1, px - 1), fill=255)
    im.putalpha(Image.composite(im.getchannel("A"), mask, mask))
    return np.asarray(im)


def hero_chart(highlight: str, out: Path, logos: dict[str, Path] | None = None) -> None:
    """Release-style evaluation figure: one small panel per metric, this card's model first.

    logos maps an entry key to an image drawn under its bars and in the legend.
    """
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage

    plt.rcParams["font.family"] = ["Google Sans", "DejaVu Sans"]
    cols = _hero_columns(highlight)
    data = {e.key: _summary(e.bench) for e in cols}
    cols = [e for e in cols if data[e.key]]
    colors = {}
    tints = iter(TINTS)
    for e in cols:
        colors[e.key] = ACCENT if e.key == highlight else next(tints)
    badges = {k: _round_logo(p) for k, p in (logos or {}).items()}

    def badge(ax, key: str, xy, zoom: float, coords: str = "data", offset=(0, 0)) -> None:
        if key in badges:
            box = OffsetImage(badges[key], zoom=zoom)
            ax.add_artist(
                AnnotationBbox(
                    box, xy, xycoords=coords, xybox=offset, boxcoords="offset points",
                    frameon=False, annotation_clip=False,
                )
            )  # fmt: skip

    fig = plt.figure(figsize=(15, 10.2), dpi=150)
    fig.patch.set_facecolor("white")
    fig.text(
        0.045,
        0.94,
        "radcheck: RadCheck-Bench-ES evaluation",
        fontsize=30,
        fontweight="bold",
        color=TEXT,
    )
    # Legend: square + bold name + light size, laid out left to right, wrapping.
    renderer = fig.canvas.get_renderer()
    x, y = 0.045, 0.885
    for e in cols:
        fig.patches.append(
            plt.Rectangle(
                (x, y - 0.004),
                0.012,
                0.018,
                transform=fig.transFigure,
                color=colors[e.key],
                figure=fig,
            )
        )
        if e.key in badges:
            x += 0.004
            badge(fig, e.key, (x + 0.022, y + 0.006), 0.14, coords="figure fraction")
            x += 0.026
        t1 = fig.text(
            x + 0.018, y, e.name, fontsize=15, fontweight="bold", color=TEXT, va="baseline"
        )
        w1 = t1.get_window_extent(renderer).width / fig.bbox.width
        t2 = fig.text(
            x + 0.018 + w1 + 0.004, y, f"({e.size})", fontsize=15, color=TEXT_2, va="baseline"
        )
        w2 = t2.get_window_extent(renderer).width / fig.bbox.width
        x += 0.018 + w1 + 0.004 + w2 + 0.025
        if x > 0.8:
            x, y = 0.045, y - 0.04

    n_ref = sum(e.key in REFERENCES for e in cols)
    grid = fig.add_gridspec(
        2,
        3,
        left=0.045,
        right=0.97,
        top=0.78,
        bottom=0.11 if badges else 0.07,
        hspace=0.42,
        wspace=0.12,
    )
    for i, (title, get) in enumerate(PANELS):
        ax = fig.add_subplot(grid[i // 3, i % 3])
        ax.set_xlim(-0.6, len(cols) - 0.4)
        ax.set_ylim(0, 112)
        for j, e in enumerate(cols):
            v = 100 * get(data[e.key])
            hl = e.key == highlight
            _bar(ax, j, v, 0.8, colors[e.key], solid=hl)
            label = f"{v:.1f}".rstrip("0").rstrip(".")
            ax.text(
                j,
                v + 3,
                label,
                ha="center",
                va="bottom",
                fontsize=13,
                fontweight="bold" if hl else "normal",
                color=TEXT,
            )
        if n_ref:
            ax.axvline(
                len(cols) - n_ref - 0.5,
                ymin=0,
                ymax=0.95,
                color=TEXT,
                linestyle=(0, (2, 2)),
                linewidth=1.3,
            )
        ax.axhline(0, color="#9a9994", linewidth=1)
        for j, e in enumerate(cols):
            badge(ax, e.key, (j, 0), 0.16, offset=(0, -17))
        ax.set_xticks([])
        ax.set_yticks([])
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.set_xlabel(title, fontsize=17, color="#2b2b2b", labelpad=36 if badges else 10)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--highlight", required=True, choices=[e.key for e in ENTRIES])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    hero_chart(args.highlight, out / "assets" / "radcheck_bench.png", default_logos())
    (out / "table.html").write_text(html_table(args.highlight), encoding="utf-8")
    print(f"wrote {out}/assets/radcheck_bench.png and {out}/table.html")


if __name__ == "__main__":
    main()
