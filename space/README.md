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
inconsistencies: laterality, negation, measurement, findings missing from the conclusion
(`discordancia`) and dictation slips (`transcripcion`).
The interface is in English; reports, labels and the model's explanations are in Spanish (the task).

- Model: [`Crstian19/radcheck-qwen35-4b-gguf-es`](https://huggingface.co/Crstian19/radcheck-qwen35-4b-gguf-es)
  (Qwen3.5-4B + LoRA, v4.1, Q4_K_M), served with `llama-server` on the free CPU tier
  (2 vCPU), so each report takes a while.
- **Research preview, not validated by a physician.** Learning project, not a medical device.
  Never use real patient data.

Run locally:

```bash
docker build -t radcheck-space .
docker run --cpus 2 -p 7860:7860 radcheck-space
```
