---
title: radcheck
emoji: 🩻
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: cc-by-nc-sa-4.0
short_description: Inconsistencies in Spanish radiology reports
---

# radcheck demo

Paste a (synthetic) Spanish radiology report and the model highlights internal
inconsistencies between findings and conclusion: laterality, negation and measurement.
The interface is in English; reports, labels and the model's explanations are in Spanish (the task).

- Model: `Crstian19/radcheck-qwen35-4b-gguf-es` (Qwen3.5-4B + LoRA, recipe v2, Q4_K_M), served
  with `llama-server` on CPU.
- Needs a `HF_TOKEN` secret (a **read-only** token) because the model repo is private.
- Learning project, not a medical device. Never use real patient data.

Run locally:

```bash
docker build -t radcheck-space .
docker run -p 7860:7860 -e HF_TOKEN=<read-only token> radcheck-space
```
