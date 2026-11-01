# Data

Where the data comes from, under which licence, and the hard rules about patient data. Nothing under `data/` is committed to git.

## Sources

| Dataset | Content | Licence | Access |
|---|---|---|---|
| [SINAI/CARES](https://huggingface.co/datasets/SINAI/CARES) | 3,219 Spanish radiology reports (`full_text`, ICD-10 codes, anatomical area); 2,253 train / 966 test | CC BY-NC-SA 4.0 | Accept the terms on Hugging Face, then `hf auth login` |
| Radiologist set | ~100 synthetic reports written from scratch by the collaborating radiologist, with and without realistic errors | To be agreed in writing (proposal: CC BY 4.0) | Private until agreed |

Candidates for later (not used yet): PadChest report text (Spanish; research-only agreement, no redistribution), Open-i (English, CC BY-NC-ND).

## Licence consequences

- CC BY-NC-SA applies to CARES-derived data **and** to models fine-tuned on it: non-commercial use only, attribution, same licence for derivatives.
- If radcheck ever becomes a product, retrain on data with a compatible licence (e.g. synthetic reports owned by the project).

## Patient data rules

- **Never** store, train on, or send to any API a real patient report, even if de-identified. Health data is a special category under GDPR art. 9.
- The radiologist's reports are invented from scratch, not paraphrased from real cases.
- Demo inputs are synthetic. The demo does not log request bodies.

## Download

```bash
uv run --extra rocm hf auth login       # once; browser or token from huggingface.co/settings/tokens
uv run --extra rocm python -c "from datasets import load_dataset; load_dataset('SINAI/CARES').save_to_disk('data/raw/cares')"
```

## Radiologist test set

The collaborating radiologist writes reports from scratch in a plain-text format (one `### Informe NNN` block per report, followed by a `CLAVE:` answer key; see the docstring of `src/radcheck/radiologist.py`). Convert and evaluate:

```bash
uv run --extra rocm python -m radcheck.radiologist data/radiologist/informes.md --out data/radiologist/test.jsonl
uv run --extra rocm python -m radcheck.evaluate --backend hf --model Qwen/Qwen3-0.6B \
    --adapter outputs/train/<run> --data data/radiologist/test.jsonl
```

The converter fails loudly (`FormatError: Informe 017: ...`) when a quoted fragment in the key is not literally present in the report, which is the most likely mistake when filling the key by hand.
