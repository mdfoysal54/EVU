from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.model_lab.sft.metrics import task_distribution
from app.model_lab.sft.mixture import MixtureConfig, mix_specialized
from app.model_lab.sft.schema import SFTExample
import app.model_lab.sft.trainer as trainer_module
from app.model_lab.sft.trainer import SFTTrainer


def load_jsonl(path: Path | str) -> list[dict]:
    path_obj = Path(path)
    if not path_obj.is_file():
        print(f"[!] File not found: {path_obj}")
        return []

    records = []
    with path_obj.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    records.append(data)
            except json.JSONDecodeError as err:
                print(f"[!] JSON parse error in {path_obj.name} line {idx}: {err}")
    return records


def extract_instruction_response(record: dict) -> tuple[str, str]:
    """Extract instruction and response across common dataset schemas."""
    if "messages" in record and isinstance(record["messages"], list):
        user_msgs = [
            m.get("content", "")
            for m in record["messages"]
            if isinstance(m, dict) and m.get("role") == "user"
        ]
        assistant_msgs = [
            m.get("content", "")
            for m in record["messages"]
            if isinstance(m, dict) and m.get("role") == "assistant"
        ]
        if user_msgs and assistant_msgs:
            return "\n\n".join(user_msgs).strip(), "\n\n".join(assistant_msgs).strip()

    prompt_keys = ["prompt", "instruction", "input", "question", "text", "query", "user"]
    instruction = ""
    for k in prompt_keys:
        val = record.get(k)
        if val and isinstance(val, str) and val.strip():
            instruction = val.strip()
            break

    resp_keys = ["response", "output", "completion", "answer", "target", "assistant", "chosen"]
    response = ""
    for k in resp_keys:
        val = record.get(k)
        if val and isinstance(val, str) and val.strip():
            response = val.strip()
            break

    return instruction, response


def build_sft_example(
    inst: str, resp: str, record: dict, target_cls: type = SFTExample
) -> Any:
    sig = inspect.signature(target_cls.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}

    kwargs: dict[str, Any] = {}

    if "instruction" in valid_params:
        kwargs["instruction"] = inst
    elif "prompt" in valid_params:
        kwargs["prompt"] = inst
    elif "input" in valid_params:
        kwargs["input"] = inst
    elif "text" in valid_params and "response" not in valid_params and "completion" not in valid_params:
        kwargs["text"] = f"{inst}\n\n{resp}"

    if "response" in valid_params:
        kwargs["response"] = resp
    elif "completion" in valid_params:
        kwargs["completion"] = resp
    elif "output" in valid_params:
        kwargs["output"] = resp

    if "task" in valid_params and "task" in record:
        kwargs["task"] = record["task"]

    try:
        return target_cls(**kwargs)
    except TypeError:
        try:
            return target_cls(inst, resp)
        except TypeError:
            return target_cls(f"{inst}\n\n{resp}")


def build_config(args: argparse.Namespace) -> Any:
    """Build SFTTrainingConfig if present, matching accepted attributes."""
    config_cls = getattr(trainer_module, "SFTTrainingConfig", None)
    if not config_cls:
        # Check module members for any Config class
        for attr in dir(trainer_module):
            if "Config" in attr:
                config_cls = getattr(trainer_module, attr)
                break

    if not config_cls:
        return None

    candidate_values = {
        "learning_rate": args.lr,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "per_device_train_batch_size": args.batch_size,
        "max_length": args.max_length,
        "max_seq_length": args.max_length,
        "epochs": args.epochs,
        "num_train_epochs": args.epochs,
        "output_dir": args.output,
        "output": args.output,
        "device": args.device,
    }

    sig = inspect.signature(config_cls.__init__)
    valid_fields = set(sig.parameters.keys()) - {"self"}

    cfg_kwargs = {k: v for k, v in candidate_values.items() if k in valid_fields}

    try:
        return config_cls(**cfg_kwargs)
    except Exception as e:
        print(f"[!] Warning: Failed instantiating {config_cls.__name__} ({e}). Using default.")
        try:
            return config_cls()
        except Exception:
            return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Train specialized SFT model.")
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--coding", required=True)
    parser.add_argument("--tool-use", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B", help="Base model name or path")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default="cpu")

    args = parser.parse_args()

    # 1. Load data
    raw_reasoning = load_jsonl(args.reasoning)
    raw_coding = load_jsonl(args.coding)
    raw_tool_use = load_jsonl(args.tool_use)

    print(
        f"[*] Loaded raw rows -> Reasoning: {len(raw_reasoning)} | "
        f"Coding: {len(raw_coding)} | Tool-Use: {len(raw_tool_use)}"
    )

    for r in raw_reasoning:
        r.setdefault("task", "reasoning")
    for r in raw_coding:
        r.setdefault("task", "coding")
    for r in raw_tool_use:
        r.setdefault("task", "tool_use")

    try:
        records = mix_specialized(
            raw_reasoning,
            raw_coding,
            raw_tool_use,
            MixtureConfig(),
        )
    except Exception as e:
        print(f"[!] mix_specialized failed ({e}), merging lists directly.")
        records = raw_reasoning + raw_coding + raw_tool_use

    if not records:
        records = raw_reasoning + raw_coding + raw_tool_use

    try:
        print("dataset distribution:", task_distribution(records))
    except Exception:
        pass

    # 2. Build SFTExamples
    examples: list[SFTExample] = []
    for record in records:
        inst, resp = extract_instruction_response(record)
        if inst and resp:
            examples.append(build_sft_example(inst, resp, record, SFTExample))

    print(f"[*] Total valid SFT training examples: {len(examples)}")
    if not examples:
        raise ValueError("0 training examples prepared.")

    # 3. Load base model & tokenizer
    print(f"[*] Loading model & tokenizer from: {args.model}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            torch_dtype=torch.float32 if args.device == "cpu" else torch.bfloat16,
            trust_remote_code=True,
        )
        if args.device != "cpu" and torch.cuda.is_available():
            model = model.to(args.device)
    except Exception as e:
        print(f"[!] Error loading base model ({e}). Attempting fallback dummy initialization if supported.")
        raise

    # 4. Build configuration object
    config = build_config(args)
    print(f"[*] Loaded SFT config: {config}")

    # 5. Initialize SFTTrainer(model, tokenizer, config=config)
    trainer_init_sig = inspect.signature(SFTTrainer.__init__)
    trainer_init_params = set(trainer_init_sig.parameters.keys()) - {"self"}

    init_kwargs = {}
    if "model" in trainer_init_params:
        init_kwargs["model"] = model
    if "tokenizer" in trainer_init_params:
        init_kwargs["tokenizer"] = tokenizer
    if "config" in trainer_init_params and config is not None:
        init_kwargs["config"] = config

    trainer = SFTTrainer(**init_kwargs)
    print(f"[*] SFTTrainer successfully instantiated.")

    # 6. Locate and trigger training method on trainer instance
    train_method = None
    for name in ["train", "fit", "run", "train_epoch"]:
        if hasattr(trainer, name) and callable(getattr(trainer, name)):
            train_method = getattr(trainer, name)
            break

    if not train_method:
        available_methods = [m for m in dir(trainer) if not m.startswith("_") and callable(getattr(trainer, m))]
        raise AttributeError(f"No train method found on SFTTrainer. Available methods: {available_methods}")

    print(f"[*] Calling trainer.{train_method.__name__}()...")

    # Map parameters to the training method
    method_sig = inspect.signature(train_method)
    method_params = set(method_sig.parameters.keys()) - {"self"}

    call_kwargs = {}
    if "dataset" in method_params:
        call_kwargs["dataset"] = examples
    elif "examples" in method_params:
        call_kwargs["examples"] = examples
    elif "train_dataset" in method_params:
        call_kwargs["train_dataset"] = examples

    if "epochs" in method_params:
        call_kwargs["epochs"] = args.epochs
    if "output_dir" in method_params:
        call_kwargs["output_dir"] = args.output

    # If method accepts no named dataset, pass examples positionally if accepted
    if not call_kwargs and len(method_params) > 0:
        result = train_method(examples)
    else:
        result = train_method(**call_kwargs)

    print("[*] Training completed successfully!")
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()