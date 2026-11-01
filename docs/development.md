# Development

How to set up the environment on the two GPUs this project uses, and the everyday commands.

## Hardware

| Machine | GPU | Backend | Use |
|---|---|---|---|
| Workstation | AMD Radeon RX 6800/6900 XT, 16 GB (gfx1030) | ROCm 7.2 | Data work, prototypes, small fine-tunes, GGUF inference |
| Work box | NVIDIA RTX PRO 6000 Blackwell, 96 GB (sm_120) | CUDA 13.0 | 4B–32B fine-tunes, vLLM evaluation |

## Environment

Python is pinned to 3.12 (`.python-version`) because the PyTorch ROCm/CUDA wheels are built for cp312/cp313. torch comes from the PyTorch indexes declared in `pyproject.toml`, selected with an extra:

```bash
uv sync --extra rocm --group dev     # AMD
uv sync --extra cuda --group dev     # NVIDIA
uv sync --extra rocm --group eval    # add lm-evaluation-harness
```

Smoke test:

```bash
uv run --extra rocm python -c "import torch; print(torch.__version__, torch.version.hip or torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Verified on the workstation (2026-10-30): torch `2.14.1+rocm7.2`, HIP 7.2, GPU visible, `is_bf16_supported()` true, no `HSA_OVERRIDE_GFX_VERSION` needed. bitsandbytes 0.50.2 NF4 quantise/dequantise and a `Linear4bit` forward/backward pass work, so QLoRA is viable locally. ROCm prints harmless `(null): No such file or directory` lines on startup.

### The extra trap

uv has no "default extra", and `uv run` re-syncs the environment before running. So:

| Command | Result |
|---|---|
| `uv run --extra rocm python ...` | Correct ROCm torch |
| `uv run python ...` | Re-syncs **without** the extra: removes ROCm torch, installs PyPI `torch` + `triton` (CUDA) |

If that happens, re-sync with the extra **and** reinstall Triton: `triton` and `triton-rocm` both install into the same `triton/` directory, so removing one corrupts the other (`AttributeError: module 'triton' has no attribute 'language'`).

```bash
uv sync --extra rocm --group dev --reinstall-package triton-rocm
```

Alternative: activate the venv once (`source .venv/bin/activate`) and call `python`/`pytest` directly; that never re-syncs.

### AMD notes (gfx1030)

- The RX 6800/6900 XT is not on AMD's official ROCm support matrix but works with the system `rocm-hip-sdk`. If `torch.cuda.is_available()` is `False` while `rocminfo` shows `gfx1030`, try `export HSA_OVERRIDE_GFX_VERSION=10.3.0`.
- No Flash Attention 2 on RDNA2: load models with `attn_implementation="sdpa"`.
- bitsandbytes 0.50 ships gfx1030 builds; 4-bit NF4 verified working (see smoke test above).
- Monitor with `amd-smi` or `rocm-smi`.

### NVIDIA Blackwell notes (sm_120)

- Needs CUDA ≥ 12.8 wheels; the `cuda` extra uses cu130.
- Start with `attn_implementation="sdpa"`; Flash Attention on sm_120 is not assumed.

## Commands

```bash
uv run --extra rocm pytest                                    # tests
uv run --extra rocm ruff check . && uv run --extra rocm ruff format .
uv run --extra rocm jupyter lab                               # notebooks/ for exploration (H1)
```

## Layout

```
radcheck/
├── src/radcheck/     # package code (inject.py, eval.py, train.py as milestones land)
├── tests/            # pytest
├── notebooks/        # exploration only, not imported by the package
├── data/             # local only, git-ignored (see docs/data.md)
└── docs/             # this documentation
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `torch.cuda.is_available()` is `False` right after a successful sync | A bare `uv run`/`uv add` re-synced without the GPU extra | See [The extra trap](#the-extra-trap) |
| `AttributeError: module 'triton' has no attribute 'language'` | `triton` (CUDA) was removed over `triton-rocm`; they share a directory | `uv sync --extra rocm --group dev --reinstall-package triton-rocm` |
| `SFTConfig.__init__() got an unexpected keyword argument 'warmup_ratio'` | Removed in transformers 5 | Use `warmup_steps=0.05` (a float in [0, 1) is a ratio) |
| `TensorBoardCallback requires tensorboard to be installed` | `report_to="tensorboard"` without the package | `tensorboard` is in the `dev` group; add packages with `uv add --no-sync ...` then `uv sync --extra rocm --group dev` |
| `apply_chat_template(..., tokenize=True)` returns 2 items | transformers 5 returns a `BatchEncoding` | Use `["input_ids"]`, or `tokenize=False` + `tok(...)` |
