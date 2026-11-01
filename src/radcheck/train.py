"""LoRA / QLoRA supervised fine-tuning on the processed dataset.

Usage (smoke test on the AMD GPU):
    uv run --extra rocm python -m radcheck.train --model Qwen/Qwen3-0.6B \
        --output outputs/train/qwen3-0.6b-lora --max-steps 50
Full run with 4-bit base weights (QLoRA):
    uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3-4B --load-in-4bit \
        --output outputs/train/qwen3-4b-qlora --epochs 2
"""

from __future__ import annotations

import argparse

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

# Columns the trainer needs; "gold" and ids stay in the JSONL for evaluation only.
TRAIN_COLUMNS = ["prompt", "completion", "chat_template_kwargs"]

# Multimodal checkpoints (Gemma 4, Qwen3.5 wrappers...) keep vision/audio towers; LoRA
# "all-linear" must not adapt them for a text-only task.
NON_TEXT_MODULES = r".*(vision|visual|audio|multi_modal_projector|embed_vision|embed_audio).*"


def _prompt_is_prefix(tokenizer, example: dict) -> bool:
    """True if the chat template renders the prompt as an exact prefix of prompt+answer.

    TRL's conversational prompt-completion masking relies on it. Gemma 4 breaks it: the
    generation prompt ends with an empty thought block that the full render drops.
    """
    kw = example.get("chat_template_kwargs") or {}
    prompt = tokenizer.apply_chat_template(
        example["prompt"], add_generation_prompt=True, tokenize=False, **kw
    )
    full = tokenizer.apply_chat_template(
        example["prompt"] + example["completion"], tokenize=False, **kw
    )
    return full.startswith(prompt)


def _render(tokenizer, example: dict) -> dict:
    """Plain-text prompt/completion: the prompt exactly as at inference time, the completion
    the answer plus whatever the template appends after an assistant turn."""
    kw = example.get("chat_template_kwargs") or {}
    answer = example["completion"][0]["content"]
    prompt = tokenizer.apply_chat_template(
        example["prompt"], add_generation_prompt=True, tokenize=False, **kw
    )
    full = tokenizer.apply_chat_template(
        example["prompt"] + example["completion"], tokenize=False, **kw
    )
    # Trailing newline dropped so the completion ends with the end-of-turn token itself and
    # TRL does not append a second one.
    end_of_turn = full[full.rindex(answer) + len(answer) :].rstrip()
    return {"prompt": prompt, "completion": answer + end_of_turn}


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--data", default="data/processed")
    ap.add_argument("--output", required=True)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--max-steps", type=int, default=-1, help="overrides --epochs when > 0")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--load-in-4bit", action="store_true", help="QLoRA: base weights in NF4")
    ap.add_argument(
        "--no-grad-checkpointing",
        action="store_true",
        help="keep activations in memory: ~25%% faster, needs much more VRAM (96 GB GPU)",
    )
    ap.add_argument("--eval-steps", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42, help="LoRA init and data order")
    args = ap.parse_args()

    data = load_dataset(
        "json",
        data_files={"train": f"{args.data}/train.jsonl", "val": f"{args.data}/val.jsonl"},
    ).select_columns(TRAIN_COLUMNS)

    quantization = (
        BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        if args.load_in_4bit
        else None
    )

    # Load the model ourselves as a causal LM. Passing the name to SFTTrainer would pick the
    # class from config.architectures, which for Qwen3.5/3.6/3.8 is the multimodal
    # *ForConditionalGeneration: it loads the vision tower and LoRA "all-linear" would adapt
    # it too. AutoModelForCausalLM maps those checkpoints to the text-only *ForCausalLM.
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",  # RDNA2 has no Flash Attention 2; SDPA works on both GPUs
        quantization_config=quantization,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    eos_token = None
    if not _prompt_is_prefix(tokenizer, data["train"][0]):
        data = data.map(lambda ex: _render(tokenizer, ex), remove_columns=TRAIN_COLUMNS)
        # TRL appends eos_token to completions that do not end with it; make it the
        # template's end-of-turn token so nothing extra is learned after the turn.
        turn_end = data["train"][0]["completion"].rsplit("}", 1)[1].strip()
        if turn_end and turn_end in tokenizer.get_vocab():
            eos_token = turn_end
        print(f"chat template is not prefix-stable: training on rendered text (eos={eos_token!r})")

    config = SFTConfig(
        seed=args.seed,
        output_dir=args.output,
        bf16=True,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=0.05,  # transformers 5: a float in [0, 1) is a ratio of total steps
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        gradient_checkpointing=not args.no_grad_checkpointing,
        max_length=args.max_length,
        completion_only_loss=True,  # learn the JSON answer, not to rewrite the report
        eval_strategy="steps",
        eval_steps=args.eval_steps,
        logging_steps=10,
        save_strategy="steps",
        save_steps=args.eval_steps,
        save_total_limit=2,
        report_to="tensorboard",
        eos_token=eos_token,
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=data["train"],
        eval_dataset=data["val"],
        processing_class=tokenizer,
        peft_config=LoraConfig(
            r=args.rank,
            lora_alpha=2 * args.rank,
            lora_dropout=0.05,
            target_modules="all-linear",
            exclude_modules=NON_TEXT_MODULES,
            task_type="CAUSAL_LM",
        ),
    )
    trainer.train()
    trainer.save_model(args.output)


if __name__ == "__main__":
    main()
