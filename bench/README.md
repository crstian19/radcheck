# RadCheck-Bench-ES v1

Independent benchmark for detecting **internal inconsistencies** in Spanish radiology reports.

## Why it exists

radcheck is trained on CARES reports with errors inserted by a rule-based injector, and its
own test set is built by the **same injector**. That test shares the injector's patterns, so
its scores are optimistic: the model may learn the injector instead of the task.

This benchmark breaks that dependency: different source texts, different writing styles,
errors written like real dictation slips, and many hard negatives. **Evaluation only**:
nothing here is used for training.

## What is measured

Input: the full text of one report. Output: the list of inconsistencies, as JSON.

Only contradictions that can be **verified from the text alone**, without clinical knowledge,
are scored:

| `tipo` | Definition |
|---|---|
| `lateralidad` (laterality) | The same finding appears with different sides (right/left) |
| `negacion` (negation) | One part asserts what another part denies |
| `medida` (measurement) | The same measurement differs (number or unit) |

Out of scope: whether a finding is clinically right, diagnoses, severity, recommendations.
A finding missing from the conclusion and dictation typos go to a separate track (`extra`)
that does not count towards the main score.

Report text, labels and explanations are in Spanish, as in the task.

## Files

| File | Content |
|---|---|
| `specs.jsonl` | 460 composition specs, generated with seed 13 |
| `raw.jsonl` | Full items: clean report, corrupted report, labels, metadata |
| `radcheck_bench_v1_dev.jsonl` | 60 items, radcheck evaluation format |
| `radcheck_bench_v1_test.jsonl` | 340 items |
| `radcheck_bench_v1_extra.jsonl` | 60 items of the out-of-scope track |
| `review.jsonl` | Items rejected by the independent check, with the reason |
| `stats.json` | Counts per slice, style, modality, region, difficulty and length |
| `radiologist_review.md` | 50 stratified test items with checkboxes, for the radiologist (Spanish) |
| `report.html` | **Self-contained web report**: composition, acceptance criteria, all 460 items and the rejections |
| `generate.py` `validate.py` `build.py` `check.py` `report.py` | Pipeline |
| `run_generate.sh` `run_check.sh` | Launchers that resolve the API key at run time |
| `prompts/` | Every prompt template and the model sheet (`MODEL.md`) |

## Composition

400 main items (dev 60 / test 340) and 60 in the extra track.

| Slice | N |
|---|---|
| Clean, ordinary | 100 |
| **Clean, hard negative** | 100 |
| `lateralidad` | 67 |
| `negacion` | 67 |
| `medida` | 66 |
| `discordancia` (extra) | 30 |
| `transcripcion` (extra) | 30 |

Hard negatives, at least 15 of each pattern: different sides for different findings;
asymmetric bilateral finding; negation and assertion about different structures; the same
number for different structures; comparison with a previous study; unlateralised organs next
to side words.

Diversity: five modalities (X-ray, CT, MRI, ultrasound, mammography), seven regions, four
styles (A headers in one paragraph, B structured, C narrative with IMPRESIÓN DIAGNÓSTICA, D
telegraphic with abbreviations), 60–500 words and three difficulty levels.

## How it was generated

1. `specs.jsonl` with Python and a fixed seed: fixes the composition before spending tokens.
2. An LLM writes the clean report for each spec; for error slices the target finding must
   appear **twice** (findings and conclusion).
3. A second call makes **one** minimal edit and returns the original and replaced text. The
   `fragmento` is **not written by the model**: it is derived in code from the actual edit, so
   it is always an exact substring of the report.
4. `validate.py` applies every rule and `generate.py` retries the rejected items.
5. An **independent check** sees only the report, with another prompt and **another model**
   (`qwen3.8-flash`, a different family). Disagreements are logged in `review.jsonl` instead of
   being silently dropped.
6. `build.py` writes the evaluation files and the statistics.

Generator model and versions: `prompts/MODEL.md`. The key is read from `DEEPSEEK_API_KEY` and
is never written to disk or to a log.

## Independence from the training pipeline

- **CARES was not used.** It was not downloaded, opened or read; no text derives from it. The
  optional 8-gram overlap check from the spec therefore does not apply: only duplicate
  detection.
- **The injector was not used** (`src/radcheck/inject.py`). Corruptions are LLM calls with
  their own prompts, so they do not inherit the injector's eligibility rules.

## Automatic validation

Every kept item passes: fragment and counterpart are exact substrings; the corrupted report
differs from the clean one **only** inside the fragment; the edit is 1–4 tokens; the
counterpart does not overlap the fragment; fragment and counterpart have 3–12 words; sides,
polarity and numbers really contradict each other; the hard-negative pattern is present; the
report is complete; no duplicates.

## Limitations

- **Synthetic.** Reports are written by a model, not a radiologist. They cover register and
  structure but not the variety of a real department.
- **Generator bias.** Errors and texts share an author; an error that looks natural to the
  generator may be rare in practice.
- **One independent check.** It is another model, not a radiologist. Human validation
  (`radiologist_review.md`) is what decides.
- **Untrained extra track.** `discordancia` and `transcripcion` are not in radcheck's training
  data up to recipe v2; their scores measure zero-shot ability.
- **Fixed composition.** The slice proportions are deliberate, not the real prevalence of
  errors in a department.

## Licence

The benchmark items are released under **CC BY 4.0**: use, share and adapt with attribution.

The text was generated with DeepSeek models served through an OpenAI-compatible gateway. When
reusing the corpus, also respect the generator provider's terms of use. The pipeline code
(`*.py`) follows the radcheck repository's MIT licence.

## Reproduce

```bash
python bench/generate.py specs                 # specs.jsonl (offline)
DEEPSEEK_API_KEY=... python bench/generate.py generate
python bench/validate.py
DEEPSEEK_API_KEY=... RADCHECK_BENCH_CHECK_MODEL=qwen3.8-flash python bench/generate.py check
python bench/build.py
python bench/check.py                          # independent check -> review.jsonl
python bench/report.py                         # report.html
```
