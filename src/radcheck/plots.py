"""Benchmark-style bar charts from saved evaluation results.

Usage:
    uv run --extra rocm python -m radcheck.plots --out docs/img

Reads outputs/eval/*-full.json (injector test, 1,626 examples) and
outputs/eval-bench/*.json (RadCheck-Bench-ES test, 340 items). Models missing a result
are skipped, so it can be re-run as evaluations land.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (label, injector result, bench result). Order = order in the charts (small to large).
MODELS = [
    ("Qwen3.5-4B", "outputs/eval/qwen35-4b-lora-full.json", "qwen35-4b-lora"),
    ("Qwen3.5-4B v2", "outputs/eval/qwen35-4b-v2-full.json", "qwen35-4b-v2"),
    ("Qwen3.5-9B", "outputs/eval/qwen35-9b-lora-full.json", "qwen35-9b-lora"),
    ("Qwen3.6-35B-A3B", "outputs/eval/qwen36-35b-a3b-lora-full.json", "qwen36-35b-a3b"),
    ("Qwen3.8-27B", "outputs/eval/qwen38-27b-lora-full.json", "qwen38-27b-lora"),
    ("Qwen3.8-27B v2", "outputs/eval/qwen38-27b-v2-full.json", "qwen38-27b-v2"),
    ("Gemma 4 31B", None, "gemma4-31b-lora"),
    ("Qwen3.8-27B (no fine-tune)", None, "qwen38-27b-base"),
]

# Reference categorical palette (dataviz skill, light mode), fixed order.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def _summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    d = json.loads(path.read_text())
    return d.get("summary", d)


def _style(ax, title: str, subtitle: str) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_2, length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=13, color=TEXT, fontweight="bold", pad=22)
    # Offset in points, not axes fraction, so it sits under the title at any figure height.
    ax.annotate(
        subtitle,
        (0, 1),
        xycoords="axes fraction",
        xytext=(0, 8),
        textcoords="offset points",
        fontsize=9,
        color=TEXT_2,
    )


def grouped_barh(
    rows: list[tuple[str, list[float | None]]],
    series: list[str],
    title: str,
    subtitle: str,
    out: Path,
    xmax: float = 1.0,
    pct: bool = False,
) -> None:
    """Horizontal grouped bars: one group per model, one bar per series, value labels."""
    n = len(series)
    h = 0.8 / n
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(rows) * max(n, 1.6) + 1.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for i, (label, values) in enumerate(rows):
        for j, v in enumerate(values):
            if v is None:
                continue
            y = i + (j - (n - 1) / 2) * h
            ax.barh(y, v, height=h * 0.86, color=SERIES[j], edgecolor=SURFACE, linewidth=1)
            text = f"{v * 100:.1f}%" if pct else f"{v:.3f}"
            ax.text(v + xmax * 0.01, y, text, va="center", fontsize=8, color=TEXT_2)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], color=TEXT, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, xmax * 1.1)
    if pct:
        ax.xaxis.set_major_formatter(lambda x, _: f"{x * 100:.1f}%")
    _style(ax, title, subtitle)
    if n > 1:
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in SERIES[:n]]
        ax.legend(
            handles,
            series,
            # Below the axis, centred: at the top it collided with long subtitles.
            loc="upper center",
            frameon=False,
            fontsize=9,
            labelcolor=TEXT_2,
            ncols=n,
            bbox_to_anchor=(0.5, -0.06),
        )
    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", default="docs/img")
    ap.add_argument("--bench-dir", default="outputs/eval-bench")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    data = []
    for label, injector, bench in MODELS:
        inj = _summary(Path(injector)) if injector else None
        ben = _summary(Path(args.bench_dir) / f"{bench}.json")
        if inj or ben:
            data.append((label, inj, ben))

    def f1(s):
        return s["overall"]["f1"] if s else None

    grouped_barh(
        [(lbl, [f1(inj), f1(ben)]) for lbl, inj, ben in data],
        ["Injector test (1,626)", "RadCheck-Bench-ES (340)"],
        "F1 by model",
        "LoRA r16 on each base model. Higher is better.",
        out / "f1-injector-vs-bench.png",
    )
    bench = [(lbl, ben) for lbl, _, ben in data if ben]
    grouped_barh(
        [
            (lbl, [s["overall"]["precision"], s["overall"]["recall"], s["overall"]["f1"]])
            for lbl, s in bench
        ],
        ["Precision", "Recall", "F1"],
        "RadCheck-Bench-ES: precision, recall and F1",
        "340 synthetic reports independent of the injector, half of them clean.",
        out / "bench-prf.png",
    )
    grouped_barh(
        [
            (lbl, [s["per_type"][t]["f1"] for t in ("lateralidad", "negacion", "medida")])
            for lbl, s in bench
        ],
        ["Laterality", "Negation", "Measurement"],
        "RadCheck-Bench-ES: F1 by error type",
        "57 / 57 / 56 errors per type.",
        out / "bench-per-type.png",
    )
    grouped_barh(
        [(lbl, [s["false_alarm_rate"]]) for lbl, s in bench],
        ["False alarms"],
        "RadCheck-Bench-ES: false alarms",
        "Clean reports where the model flags something (170). Lower is better.",
        out / "bench-false-alarms.png",
        xmax=max(s["false_alarm_rate"] for _, s in bench) or 0.1,
        pct=True,
    )


if __name__ == "__main__":
    main()
