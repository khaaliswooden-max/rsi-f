"""
DPO Training Pipeline
=====================
Export preferences from Zuup and train using TRL/Unsloth.
Designed for RTX 4090 with QLoRA.
"""

import os
import sys
import json
import argparse
import traceback
from datetime import datetime
from pathlib import Path

# Allow importing domains when run from scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import httpx
from datasets import Dataset

try:
    from domains.taxonomy import get_all_domains
except ImportError:
    get_all_domains = None


def export_preferences(
    api_url: str,
    export_key: str,
    min_confidence: float = 0.6,
    domain: str = None,
    limit: int = 10000,
) -> list:
    """Export DPO-formatted preferences from API."""
    print(f"📥 Exporting preferences from {api_url}...")
    
    payload = {
        "format": "dpo",
        "min_confidence": min_confidence,
        "limit": limit,
    }
    if domain:
        payload["domain"] = domain
    
    resp = httpx.post(
        f"{api_url}/api/export",
        json=payload,
        headers={"X-API-Key": export_key},
        timeout=60,
    )
    resp.raise_for_status()
    
    data = resp.json()
    print(f"✓ Exported {data['count']} DPO pairs")
    return data["data"]


def prepare_dataset(dpo_data: list) -> Dataset:
    """Convert exported data to HuggingFace Dataset."""
    # Ensure required columns
    cleaned = []
    for item in dpo_data:
        cleaned.append({
            "prompt": item["prompt"],
            "chosen": item["chosen"],
            "rejected": item["rejected"],
            "chosen_model": item.get("chosen_model", ""),
            "rejected_model": item.get("rejected_model", ""),
            "domain": item.get("domain", ""),
            "confidence": item.get("confidence", 0.5),
        })
    
    dataset = Dataset.from_list(cleaned)
    print(f"✓ Created dataset with {len(dataset)} examples")
    print(f"  Columns: {dataset.column_names}")
    return dataset


def _training_metrics_from_trainer(trainer):
    """Extract training metrics from trainer.state.log_history."""
    out = {}
    if not getattr(trainer, "state", None) or not getattr(trainer.state, "log_history", None):
        return out
    history = trainer.state.log_history
    if not history:
        return out
    # Last entry often has loss
    last = history[-1]
    if "loss" in last:
        out["final_loss"] = last["loss"]
    if "epoch" in last:
        out["final_epoch"] = last["epoch"]
    # Optional: steps
    loss_entries = [h for h in history if "loss" in h]
    if loss_entries:
        out["num_logged_steps"] = len(loss_entries)
        losses = [h["loss"] for h in loss_entries]
        out["min_loss"] = min(losses)
        out["mean_loss"] = sum(losses) / len(losses)
    return out


def train_dpo_unsloth(
    dataset: Dataset,
    model_name: str = "unsloth/Qwen2.5-7B-bnb-4bit",
    output_dir: str = "./dpo_output",
    max_steps: int = 500,
    batch_size: int = 2,
    learning_rate: float = 2e-5,
):
    """Train using Unsloth + TRL DPO. Returns dict of training metrics or None on import error."""
    try:
        from unsloth import FastLanguageModel
        from trl import DPOConfig, DPOTrainer
    except ImportError:
        print("❌ Please install unsloth and trl:")
        print("   pip install unsloth trl")
        return None

    print(f"🚀 Loading model: {model_name}")
    
    # Load model with 4-bit quantization
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=2048,
        dtype=None,  # Auto-detect
        load_in_4bit=True,
    )
    
    # Add LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    
    print(f"✓ Model loaded with LoRA adapters")
    
    # Prepare for DPO training
    def format_prompt(example):
        return f"### Question:\n{example['prompt']}\n\n### Answer:\n"
    
    # Format dataset
    def format_examples(examples):
        formatted = {
            "prompt": [format_prompt({"prompt": p}) for p in examples["prompt"]],
            "chosen": examples["chosen"],
            "rejected": examples["rejected"],
        }
        return formatted
    
    formatted_dataset = dataset.map(
        format_examples,
        batched=True,
        remove_columns=dataset.column_names,
    )
    
    # DPO training config
    training_args = DPOConfig(
        output_dir=output_dir,
        num_train_epochs=1,
        max_steps=max_steps,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        logging_steps=10,
        save_steps=100,
        bf16=True,
        optim="adamw_8bit",
        seed=42,
        beta=0.1,  # DPO beta parameter
        max_prompt_length=512,
        max_length=1024,
    )
    
    # Create trainer
    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=formatted_dataset,
        tokenizer=tokenizer,
    )
    
    print(f"🏋️ Starting DPO training...")
    print(f"   Output: {output_dir}")
    print(f"   Steps: {max_steps}")
    print(f"   Batch: {batch_size} x 4 (grad accum)")
    
    # Train!
    trainer.train()
    
    # Save final model
    final_path = os.path.join(output_dir, "final")
    model.save_pretrained(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"✓ Model saved to {final_path}")
    
    # Optionally merge and save full model
    print(f"📦 Merging LoRA weights...")
    merged_model = model.merge_and_unload()
    merged_path = os.path.join(output_dir, "merged")
    merged_model.save_pretrained(merged_path)
    tokenizer.save_pretrained(merged_path)
    print(f"✓ Merged model saved to {merged_path}")

    return _training_metrics_from_trainer(trainer)


def run_one_domain(
    domain_id: str,
    domain_name: str,
    api_url: str,
    export_key: str,
    min_confidence: float,
    output_dir: str,
    model_name: str,
    max_steps: int,
    batch_size: int,
    learning_rate: float,
    export_only: bool,
) -> dict:
    """
    Run export + optional training for one domain. Writes session_report.json
    in output_dir and returns a session result dict.
    """
    import time
    start = time.time()
    report = {
        "domain_id": domain_id,
        "domain_name": domain_name,
        "status": "success",
        "num_examples": 0,
        "output_dir": os.path.abspath(output_dir),
        "duration_seconds": 0.0,
        "training_metrics": None,
    }
    try:
        dpo_data = export_preferences(
            api_url=api_url,
            export_key=export_key,
            min_confidence=min_confidence,
            domain=domain_id,
        )
        if not dpo_data:
            report["status"] = "skipped_no_data"
            report["duration_seconds"] = round(time.time() - start, 2)
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "session_report.json"), "w") as f:
                json.dump(report, f, indent=2)
            return report
        report["num_examples"] = len(dpo_data)

        dataset = prepare_dataset(dpo_data)
        dataset_path = os.path.join(output_dir, "dataset")
        os.makedirs(dataset_path, exist_ok=True)
        dataset.save_to_disk(dataset_path)
        print(f"✓ Dataset saved to {dataset_path}")

        if export_only:
            report["status"] = "success"
            report["duration_seconds"] = round(time.time() - start, 2)
            with open(os.path.join(output_dir, "session_report.json"), "w") as f:
                json.dump(report, f, indent=2)
            return report

        metrics = train_dpo_unsloth(
            dataset=dataset,
            model_name=model_name,
            output_dir=output_dir,
            max_steps=max_steps,
            batch_size=batch_size,
            learning_rate=learning_rate,
        )
        if metrics is None and not export_only:
            report["status"] = "failed"
            report["error_message"] = "Training failed (e.g. missing unsloth/trl)"
        report["training_metrics"] = metrics
        report["duration_seconds"] = round(time.time() - start, 2)
        with open(os.path.join(output_dir, "session_report.json"), "w") as f:
            json.dump(report, f, indent=2)
        return report
    except Exception as e:
        report["status"] = "failed"
        report["error_message"] = str(e)
        report["duration_seconds"] = round(time.time() - start, 2)
        report["traceback"] = traceback.format_exc()
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "session_report.json"), "w") as f:
            json.dump(report, f, indent=2)
        return report


def main():
    parser = argparse.ArgumentParser(description="Train DPO from Zuup preferences")
    parser.add_argument("--api-url", default="https://zuup1-zuup-preference-collection.hf.space")
    parser.add_argument("--export-key", required=True, help="Export API key")
    parser.add_argument("--domain", default=None, help="Filter by domain (ignored if --all-domains)")
    parser.add_argument("--all-domains", action="store_true", help="Run export+train for each domain; output-dir is base dir")
    parser.add_argument("--min-confidence", type=float, default=0.6)
    parser.add_argument("--model", default="unsloth/Qwen2.5-7B-bnb-4bit")
    parser.add_argument("--output-dir", default=f"./dpo_output_{datetime.now().strftime('%Y%m%d_%H%M')}")
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--export-only", action="store_true", help="Only export, don't train")
    args = parser.parse_args()

    if args.all_domains:
        if get_all_domains is None:
            print("❌ --all-domains requires domains.taxonomy (run from repo root or fix path)")
            return
        base_dir = os.path.abspath(args.output_dir)
        domains = get_all_domains()
        results = []
        for d in domains:
            domain_output_dir = os.path.join(base_dir, d.id)
            print(f"\n{'='*60}\n📂 Domain: {d.name} ({d.id})\n{'='*60}")
            r = run_one_domain(
                domain_id=d.id,
                domain_name=d.name,
                api_url=args.api_url,
                export_key=args.export_key,
                min_confidence=args.min_confidence,
                output_dir=domain_output_dir,
                model_name=args.model,
                max_steps=args.max_steps,
                batch_size=args.batch_size,
                learning_rate=args.lr,
                export_only=args.export_only,
            )
            results.append(r)
        aggregate = {
            "base_output_dir": base_dir,
            "finished_at": datetime.now().isoformat(),
            "sessions": results,
        }
        aggregate_path = os.path.join(base_dir, "all_domains_report.json")
        with open(aggregate_path, "w") as f:
            json.dump(aggregate, f, indent=2)
        print(f"\n🎉 All domains complete. Aggregate report: {aggregate_path}")
        return

    # Single run
    domain_id = args.domain
    domain_name = "all"
    if domain_id and get_all_domains is not None:
        from domains.taxonomy import get_domain
        d = get_domain(domain_id)
        if d:
            domain_name = d.name
    output_dir = os.path.abspath(args.output_dir)
    print(f"\n{'='*60}\n📂 Run: {domain_name}\n{'='*60}")
    r = run_one_domain(
        domain_id=domain_id,
        domain_name=domain_name,
        api_url=args.api_url,
        export_key=args.export_key,
        min_confidence=args.min_confidence,
        output_dir=output_dir,
        model_name=args.model,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        export_only=args.export_only,
    )
    if r["status"] == "skipped_no_data":
        print("❌ No data exported. Check API key and filters.")
        return
    if r["status"] == "failed":
        print("❌ Run failed:", r.get("error_message", ""))
        return
    print("🎉 Training complete!")


if __name__ == "__main__":
    main()

