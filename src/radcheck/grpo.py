"""GRPO (online RL) on top of a fine-tuned LoRA adapter, with radcheck's metric as reward.

For every prompt the model samples several answers; each answer is scored with the same rule
as the evaluation (type must match, fragment must overlap the error or its counterpart), and
the policy is pushed towards the answers that scored above the group average. No reward model:
the reward is computed, so it cannot be fooled by fluent but wrong text.

If the SFT model already gets a prompt right, all answers in a group score the same and
there is nothing to learn from it; on our data that was 80-88% of the groups.

Run 1 (synthetic reports only, false alarm = 0, no KL) made the model trigger-happy.
Run 2 defaults: false alarm = -1, KL beta 0.04, CARES + synthetic mixed.

Usage:
    uv run --extra cuda python -m radcheck.grpo --model Qwen/Qwen3.5-4B \
        --adapter outputs/train/qwen35-4b-v3 --data data/processed-v3s/train.jsonl \
        --only-prefix syn- --output outputs/train/qwen35-4b-v3-grpo --max-steps 150
"""

from __future__ import annotations

import argparse
import json

import torch
from datasets import Dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer

from radcheck.metrics import _matches
from radcheck.prompts import CHAT_TEMPLATE_KWARGS, parse_output


def example_reward(
    report: str, gold: list[dict], pred: list[dict] | None, clean_penalty: float = -1.0
) -> float:
    """Per-answer score in [-1, 1]: invalid JSON -1, clean report 1 or `clean_penalty`, else F1.

    The first run used 0 for a false alarm on a clean report: flagging something cost
    less than it could earn on reports with errors, and false alarms doubled (12% -> 26%).
    A false alarm now costs as much as invalid JSON.
    """
    if pred is None:
        return -1.0
    if not gold:
        return 1.0 if not pred else clean_penalty
    unmatched, tp = list(gold), 0
    for p in pred:
        hit = next((g for g in unmatched if _matches(p, g, report)), None)
        if hit is not None:
            unmatched.remove(hit)
            tp += 1
    if tp == 0:
        return 0.0
    precision, recall = tp / len(pred), tp / len(gold)
    return 2 * precision * recall / (precision + recall)


CLEAN_PENALTY = -1.0


def radcheck_reward(completions, report, gold, **kwargs) -> list[float]:
    return [
        example_reward(r, json.loads(g), parse_output(c[0]["content"]), CLEAN_PENALTY)
        for c, r, g in zip(completions, report, gold, strict=True)
    ]


def load(path: str, only_prefix: str | None) -> Dataset:
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    if only_prefix:
        rows = [r for r in rows if str(r["report_id"]).startswith(only_prefix)]
    return Dataset.from_list(
        [
            {
                "prompt": r["prompt"],
                "report": r["prompt"][-1]["content"],
                "gold": json.dumps(r["gold"], ensure_ascii=False),  # one column type for all
            }
            for r in rows
        ]
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter", required=True, help="SFT LoRA adapter to continue from")
    ap.add_argument("--data", required=True)
    ap.add_argument("--only-prefix", help="keep only reports whose id starts with this")
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-steps", type=int, default=150)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--num-generations", type=int, default=8)
    ap.add_argument("--batch-size", type=int, default=16, help="completions per micro-batch")
    ap.add_argument("--beta", type=float, default=0.04, help="KL penalty; TRL's default is 0")
    ap.add_argument("--clean-penalty", type=float, default=-1.0, help="false alarm reward")
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    global CLEAN_PENALTY
    CLEAN_PENALTY = args.clean_penalty

    dataset = load(args.data, args.only_prefix).shuffle(seed=args.seed)
    print(f"{len(dataset)} prompts")

    tok = AutoTokenizer.from_pretrained(args.adapter, padding_side="left")
    base = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.bfloat16, attn_implementation="sdpa"
    )
    # Continue training the SFT adapter; with beta > 0 TRL keeps a frozen copy of it ("ref").
    model = PeftModel.from_pretrained(base, args.adapter, is_trainable=True)

    config = GRPOConfig(
        output_dir=args.output,
        max_steps=args.max_steps,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,  # 16 = 2 prompts x 8 answers
        gradient_accumulation_steps=4,
        num_generations=args.num_generations,
        max_completion_length=256,
        temperature=1.0,
        # KL to the SFT adapter keeps the policy from drifting away from what already works.
        beta=args.beta,
        chat_template_kwargs=CHAT_TEMPLATE_KWARGS,
        bf16=True,
        gradient_checkpointing=True,
        logging_steps=5,
        save_steps=50,
        save_total_limit=2,
        report_to="tensorboard",
        seed=args.seed,
    )
    trainer = GRPOTrainer(
        model=model,
        reward_funcs=radcheck_reward,
        args=config,
        train_dataset=dataset,
        processing_class=tok,
    )
    trainer.train()
    trainer.save_model(args.output)
    tok.save_pretrained(args.output)


if __name__ == "__main__":
    main()
