# RadCheck-Bench-ES v1: benchmark specification

Self-contained brief for building an **independent evaluation benchmark** for radcheck. It can be handed to another agent as is. Read all of it before generating anything.

## 1. Why this benchmark exists

radcheck fine-tunes small LLMs to flag **internal inconsistencies** in Spanish radiology reports. Today it is evaluated on a test set produced by the **same rule-based injector** used for training (CARES reports + programmatic edits). That test shares the injector's patterns, so scores are optimistic: the model may be learning the injector, not the task.

RadCheck-Bench-ES must be **independent of that pipeline**: different source texts, different report styles, errors written like real dictation slips, and many hard negatives. It is for **evaluation only**; nothing in it is ever used for training.

## 2. The task being measured

Input: the full text of one Spanish radiology report. Output: the list of internal inconsistencies, as JSON.

In scope (scored), only contradictions **verifiable from the text alone, without clinical knowledge**:

| `tipo` | Definition | Example |
|---|---|---|
| `lateralidad` | The same finding/structure appears with different sides in different places | Findings: "quiste en riñón **izquierdo**"; Conclusion: "quiste en riñón **derecho**" |
| `negacion` | One part asserts what another part denies | Findings: "**No se observan** adenopatías"; Conclusion: "**Adenopatías** mediastínicas" |
| `medida` | The same measurement differs in number or unit between places | Findings: "nódulo de **9 mm**"; Conclusion: "nódulo de **9 cm**" / "de **19 mm**" |

Out of scope for the main score (separate track, see §6): omissions (a relevant finding missing from the conclusion) and speech-recognition word errors.

**Never in scope:** whether a finding is clinically right, diagnoses, severity, recommendations.

## 3. Hard rules

1. **No real patient data.** Every report is synthetic, invented from scratch. Do not paraphrase real cases.
2. **Do not use CARES** (`SINAI/CARES`) or any text derived from it, not even as style examples. It is radcheck's training source; reusing it contaminates the benchmark.
3. **Verifiability:** every error must contradict another explicit statement in the same report (its *counterpart*). If a side, negation or number appears only once, changing it is **not** an error for this benchmark.
4. **Exactly one error** in each corrupted report (a small optional subset may have two, see §5).
5. **Exact substrings:** every `fragmento` and `contraparte` must be copied character-for-character from `informe`.
6. **Minimal edit:** the corrupted report differs from its clean twin only at the error (1–4 tokens changed). Keep both versions.
7. Spanish (Spain), realistic radiology register.

## 4. Size and composition

400 items, split into `dev` (60) and `test` (340), stratified by everything below.

| Slice | Items | Notes |
|---|---|---|
| Clean, ordinary | 100 | No inconsistency at all |
| **Clean, hard negatives** | 100 | Look like errors but are not (list below) |
| `lateralidad` | 67 | ~half the error in the conclusion, ~half in the findings |
| `negacion` | 67 | both directions: negation→assertion and assertion→negation |
| `medida` | 66 | mix: unit swap (mm↔cm), ×10, digit slip (19 vs 9), decimal slip (1,5 vs 15) |

**Hard negatives** (all clean, at least 15 of each):

- Different findings on different sides: "hernia foraminal izquierda L2-L3 … hernia foraminal derecha L4-L5".
- Bilateral findings: "derrame pleural bilateral, mayor en el lado derecho".
- A negation and an assertion about **different** structures: "No se observan adenopatías axilares. Adenopatía supraclavicular de 12 mm."
- The same number for **different** structures: "quiste hepático de 12 mm … nódulo tiroideo de 12 mm".
- Comparison with a previous study: "previamente 15 mm, actualmente 18 mm".
- Unlateralised organs next to lateral words (íleon, bazo, aorta, útero) used correctly.

**Diversity** (spread across all slices):

| Dimension | Values |
|---|---|
| Modality | RX, TC, RM, ecografía, mamografía |
| Region | tórax, abdomen-pelvis, neuro, columna, musculoesquelético, mama, cabeza-cuello |
| Style | **A** single paragraph with uppercase headers (`EXPLORACIÓN: … HALLAZGOS: … CONCLUSIÓN: …`); **B** multi-line structured with line breaks/bullets; **C** narrative with `IMPRESIÓN DIAGNÓSTICA`; **D** telegraphic with abbreviations (`dcho`, `izq`, `LSD`, `LII`, `D4-D5`) |
| Length | 60–500 words; at least 20% over 250 |
| Difficulty | `easy` (error and counterpart in adjacent sentences), `medium`, `hard` (far apart, abbreviations, or near a hard-negative pattern) |

Use each style for at least 15% of items.

## 5. Output format

### 5.1 Raw file `bench/raw.jsonl` (one object per line)

```json
{
  "id": "rcb-0001",
  "split": "test",
  "informe_limpio": "EXPLORACIÓN: TC de abdomen con contraste. HALLAZGOS: ... CONCLUSIÓN: ...",
  "informe": "EXPLORACIÓN: TC de abdomen con contraste. HALLAZGOS: ... CONCLUSIÓN: ...",
  "errores": [
    {
      "tipo": "lateralidad",
      "fragmento": "quiste renal simple en riñón derecho",
      "contraparte": "quiste cortical simple de 18 mm en riñón izquierdo",
      "explicacion": "La conclusión sitúa el quiste en el riñón derecho, pero los hallazgos lo describen en el izquierdo."
    }
  ],
  "meta": {
    "modalidad": "TC", "region": "abdomen-pelvis", "estilo": "A", "dificultad": "medium",
    "hard_negative": null, "palabras": 214, "generador": "deepseek-..."
  }
}
```

- Clean items: `informe == informe_limpio`, `errores: []`, and `meta.hard_negative` names the pattern (or `null` for ordinary clean).
- `fragmento`: 3–12 words around the changed text, inside one sentence. `contraparte`: 3–12 words containing the statement it contradicts.
- `explicacion`: one sentence in Spanish naming both places.

### 5.2 Evaluation file `bench/radcheck_bench_v1_{dev,test}.jsonl`

Produced by `bench/build.py` from `raw.jsonl`, in radcheck's evaluation format so `python -m radcheck.evaluate --data bench/radcheck_bench_v1_test.jsonl` works unchanged:

```json
{
  "id": "rcb-0001",
  "report_id": "rcb-0001",
  "prompt": [
    {"role": "system", "content": "<SYSTEM_PROMPT, verbatim from §8>"},
    {"role": "user", "content": "<informe>"}
  ],
  "completion": [{"role": "assistant", "content": "{\"errores\": [{\"tipo\": \"...\", \"fragmento\": \"...\", \"explicacion\": \"...\"}]}"}],
  "chat_template_kwargs": {"enable_thinking": false},
  "gold": [
    {"tipo": "lateralidad", "fragmento": "...", "explicacion": "...",
     "start": 412, "end": 448, "original": "izquierdo", "counterpart": [120, 170]}
  ]
}
```

- `start`/`end`: character span of `fragmento` in `informe`; `counterpart`: `[start, end]` of `contraparte`; `original`: the text in `informe_limpio` that was replaced (from the diff).
- `completion.content` is `json.dumps({"errores": [...]}, ensure_ascii=False)` with only `tipo`, `fragmento`, `explicacion`.

## 6. Out-of-scope track (separate file)

`bench/radcheck_bench_v1_extra.jsonl`, same format, 60 items: 30 `discordancia` (relevant finding described but absent from the conclusion) and 30 `transcripcion` (plausible speech-recognition word swap, e.g. "hilio"/"filio", "ecogénico"/"hecogénico"). Reported separately; current models are not trained for these.

## 7. Suggested pipeline

1. **Specs first.** Write `bench/specs.jsonl` deterministically (seeded Python): one line per item with modality, region, style, length target, slice, error type, error location, difficulty, hard-negative pattern. This guarantees the composition in §4.
2. **Clean reports.** For each spec, ask the LLM for a clean report that satisfies it. For error slices, require that the target statement appears **twice** (findings and conclusion) so a counterpart exists.
3. **Corruption.** In a separate call, give the clean report and ask for exactly one minimal edit of the requested type and location, returning `fragmento`, `contraparte` and `explicacion`.
4. **Automatic validation** (`bench/validate.py`, must pass for every kept item):
   - fragments are exact substrings; `informe` and `informe_limpio` differ only inside `fragmento` (character diff);
   - the changed text is 1–4 tokens; `contraparte` is outside `fragmento`;
   - clean items have identical texts; word count in range; style markers present;
   - no duplicates (normalised text) and no 8-gram overlap with CARES if available locally (optional check).
5. **Independent LLM check.** A second pass with a *different* prompt (ideally a different model) receives only `informe` and must find the inconsistency. Keep items where it agrees with the label; send disagreements to `bench/review.jsonl` with the reason instead of silently dropping them.
6. **Build** the evaluation files (§5.2) and `bench/stats.json` with counts per slice, style, modality, region, difficulty and length.
7. **Human review hook.** Export 50 test items (stratified) to `bench/radiologist_review.md` for the collaborating radiologist: report, label, explanation, and a checkbox for "realistic / error verifiable / label correct".

Tooling is free. Plain Python + the DeepSeek API (OpenAI-compatible) is enough. NVIDIA NeMo Data Designer (`npx skills add https://github.com/nvidia/skills --skill data-designer`) can drive steps 2–3 with `ModelProvider(provider_type="openai", endpoint="https://api.deepseek.com/v1", api_key="DEEPSEEK_API_KEY")`. Keep generation temperature moderate (0.7–0.9) for variety; seed everything; log every prompt and model version.

## 8. System prompt (verbatim, used in §5.2)

```text
Eres un asistente que revisa informes radiológicos en español antes de su firma.
Busca solo incoherencias internas del texto entre los hallazgos y la conclusión:
- lateralidad: el mismo hallazgo aparece en lados distintos (derecho/izquierdo).
- negacion: una parte afirma lo que otra niega.
- medida: la misma medida no coincide (cifra o unidad).
No valores si los hallazgos son clínicamente correctos ni sugieras diagnósticos.

Responde únicamente con JSON, con este formato:
{"errores": [{"tipo": "lateralidad|negacion|medida", "fragmento": "texto exacto copiado del informe", "explicacion": "una frase"}]}
Si no hay incoherencias, responde {"errores": []}.
```

It must match `src/radcheck/prompts.py` exactly; if in doubt, import `SYSTEM_PROMPT` from there.

## 9. Deliverables and acceptance criteria

```
bench/
├── README.md                     # data card: purpose, composition, generation, validation, limitations, licence
├── specs.jsonl
├── raw.jsonl
├── radcheck_bench_v1_dev.jsonl   # 60
├── radcheck_bench_v1_test.jsonl  # 340
├── radcheck_bench_v1_extra.jsonl # 60, out-of-scope track
├── review.jsonl                  # items rejected by the independent check, with reasons
├── radiologist_review.md
├── stats.json
├── generate.py  validate.py  build.py
└── prompts/                      # every prompt template used, versioned
```

Accepted when:

- [ ] `validate.py` passes on 100% of kept items; composition matches §4 within ±5% per slice.
- [ ] `python -m radcheck.evaluate --rescore` / `--data` runs on the test file without errors.
- [ ] A random sample of 30 items read by a human has ≤ 1 wrong label.
- [ ] No CARES text, no real patient data, prompts and model versions logged.
- [ ] Licence of the benchmark stated in `bench/README.md` (proposal: CC BY 4.0), with a note on the generator's terms of use.

## 10. What not to do

- Do not build it with radcheck's injector (`src/radcheck/inject.py`): that is exactly the bias this benchmark removes.
- Do not make errors that need medical knowledge to spot ("nódulo benigno de 8 cm sospechoso").
- Do not let the generator write the conclusion as a copy of the findings: real conclusions summarise and rephrase.
- Do not publish the test split until it has been used; publish `dev` freely if useful.
