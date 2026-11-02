# Generation provenance

Every prompt template in this directory is versioned with the benchmark. This file records
what produced `raw.jsonl`, so a run can be reproduced or audited.

## Generator (clean reports + corruptions)

| Field | Value |
|---|---|
| Model | a general-purpose LLM (`RADCHECK_BENCH_MODEL`) |
| Endpoint | OpenAI-compatible endpoint (`RADCHECK_BENCH_BASE_URL`) |
| Temperature | 0.75, +0.05 per retry |
| `seed` | per item: `13 + crc32(id) + 7919 * attempt` (a fixed seed made the server replay the same report for different specs, producing duplicates) |
| Thinking | disabled per call: `chat_template_kwargs.enable_thinking=false` |
| Response format | `{"type": "json_object"}` |
| Max tokens | 4000 |

## Independent checker (§7.5)

| Field | Value |
|---|---|
| Model id | a self-hosted Qwen3.8 flash deployment (`RADCHECK_BENCH_CHECK_MODEL`) |
| Endpoint | private OpenAI-compatible server (`RADCHECK_BENCH_CHECK_BASE_URL`) |
| Temperature | 0.1, up to 3 attempts |
| Prompt | `checker_system.txt` + `checker_user.txt` (receives only `informe`) |

The checker is a **different model family** from the generator on purpose, to keep
the second opinion independent in the way that matters most (different weights, different
biases). It disagrees with 10 of 400 main-track labels (2.5%); every disagreement is listed in
`review.jsonl` rather than dropped.

## Prompt files

| File | Used for |
|---|---|
| `generator_system.txt` | system prompt for both generation calls |
| `clean_report.txt` | clean report, one per spec |
| `corrupt.txt` | the single minimal edit (lateralidad / negacion / medida) |
| `corrupt_discordancia.txt` | extra track: finding dropped from the conclusion |
| `corrupt_transcripcion.txt` | extra track: speech-recognition word swap |
| `checker_system.txt`, `checker_user.txt` | independent verification |

## Not used, by design

- CARES (`SINAI/CARES`) was never opened, downloaded or read. No text in this benchmark is
  derived from it.
- `src/radcheck/inject.py` was not read or imported. The corruption step is an LLM call with
  its own prompt, so generated errors do not inherit the injector's eligibility rules.

## Credentials

The API key is read from `RADCHECK_BENCH_API_KEY` at call time. It is never written to a file, a log,
or an output artefact.
