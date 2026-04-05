"""
auto_judge.py — Autonomous LLM Judge for RSI Self-Collection
=============================================================
Uses domain-specific quality dimensions from taxonomy.py to automatically
judge preference pairs using the configured LLM backend. This eliminates
the human annotation bottleneck and enables autonomous RSI data collection
at scale (10x+ throughput vs. manual annotation).

How it works:
  1. Pull a seed prompt from the domain's prompt library.
  2. Generate two responses via the LLM with different temperatures.
  3. Ask the LLM (as an expert judge) to score both responses on each
     domain-specific dimension using the taxonomy's 1-5 anchor descriptions.
  4. Convert dimension scores → weighted preference + confidence score.
  5. Write a PreferenceRecord-compatible JSONL entry to disk.

Usage (library):
    record = generate_and_judge("procurement")
    records = batch_collect("procurement", count=50)
    results = sweep_all_domains(count_per_domain=20)

Usage (CLI):
    python auto_judge.py --domain procurement --count 50
    python auto_judge.py --count 20          # sweeps all 10 domains
"""

import hashlib
import json
import logging
import os
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from domains.taxonomy import DOMAINS, Domain, ScoringDimension, DimensionWeight
from domains.prompt_generator import get_random_prompt, SeedPrompt
from llm_client import generate_response, generate_response_pair

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────

MIN_CONFIDENCE   = float(os.getenv("MIN_CONFIDENCE", "0.55"))
JUDGE_ANNOTATOR  = "auto_judge_v1"


# ── Weight mapping ─────────────────────────────────────────────────────────────

# Normalised weights: sum across dims = 1.0
# DimensionWeight values: CRITICAL=3, HIGH=2, STANDARD=1
def _normalised_weights(dimensions: list[ScoringDimension]) -> dict[str, float]:
    total = sum(d.weight.value for d in dimensions)
    return {d.name: d.weight.value / total for d in dimensions}


# ── Judge prompt builder ───────────────────────────────────────────────────────

def _build_judge_prompt(
    seed: SeedPrompt,
    response_a: str,
    response_b: str,
    domain: Domain,
) -> str:
    weights = _normalised_weights(domain.dimensions)

    dim_blocks = []
    for dim in domain.dimensions:
        w = weights[dim.name]
        anchors = "\n".join(
            f"       {score}: {text}" for score, text in sorted(dim.anchors.items())
        )
        dim_blocks.append(
            f"  • **{dim.name}** (weight={w:.2f}, priority={dim.weight.name})\n"
            f"    {dim.description}\n"
            f"    Scoring anchors:\n{anchors}"
        )
    dims_section = "\n".join(dim_blocks)

    dim_names = [d.name for d in domain.dimensions]
    example_out = json.dumps(
        {
            "scores": {
                "A": {k: 4 for k in dim_names},
                "B": {k: 3 for k in dim_names},
            },
            "weighted": {"A": 0.84, "B": 0.67},
            "preference": "A",
            "confidence": 0.73,
            "rationale": "Response A is preferred because …",
        },
        indent=2,
    )

    context_note = (
        f"\nContext hint: {seed.context}" if seed.context else ""
    )

    return f"""You are a calibrated expert evaluator for the **{domain.name}** domain.
Platform: {domain.platform}. {domain.description}

Your task: compare two AI responses and determine which better answers the query.{context_note}

## Scoring Dimensions
{dims_section}

## Instructions
1. Score each dimension for Response A and Response B independently on the 1–5 scale above.
2. Compute weighted score: sum(score_i × weight_i) for each response (already normalised).
3. Set **preference** = "A" | "B" | "TIE"  (use TIE only when |weighted_A − weighted_B| < 0.04).
4. Set **confidence** = |weighted_A − weighted_B| (a float 0–1 reflecting how decisive the judgment is).
5. Write a concise **rationale** (1–2 sentences) explaining the key differentiator.

## Query  [{seed.category} · {seed.difficulty}]
{seed.prompt}

## Response A
{response_a}

## Response B
{response_b}

## Output
Return ONLY valid JSON — no markdown fences, no extra text:
{example_out}
"""


# ── Output parsing ─────────────────────────────────────────────────────────────

def _parse_judgment(raw: str, domain: Domain) -> Optional[dict]:
    text = raw.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        inner = [l for l in lines[1:] if l.strip() != "```"]
        text = "\n".join(inner)

    # Extract first JSON object
    start, end = text.find("{"), text.rfind("}") + 1
    if start == -1 or end == 0:
        logger.warning("No JSON object in judge output: %s", text[:200])
        return None
    try:
        data = json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error: %s | raw: %s", exc, text[start:end][:300])
        return None

    required = {"scores", "weighted", "preference", "confidence"}
    if not required.issubset(data):
        logger.warning("Missing keys %s in judgment", required - data.keys())
        return None
    if data["preference"] not in ("A", "B", "TIE"):
        logger.warning("Bad preference value: %s", data["preference"])
        return None

    # Recompute weighted scores from raw dimension scores for integrity
    weights = _normalised_weights(domain.dimensions)
    for side in ("A", "B"):
        side_scores = data["scores"].get(side, {})
        if side_scores:
            raw = sum(side_scores.get(k, 3) * w for k, w in weights.items())
            data["weighted"][side] = round(raw / 5.0, 4)  # normalise to [0, 1]
    data["confidence"] = round(
        min(abs(data["weighted"].get("A", 0) - data["weighted"].get("B", 0)), 1.0), 4
    )
    return data


# ── Core public API ────────────────────────────────────────────────────────────

def judge_pair(
    prompt: str,
    response_a: str,
    response_b: str,
    domain_id: str,
    category: str = "general",
    difficulty: str = "medium",
    context: str = "",
) -> Optional[dict]:
    """
    Ask the LLM to judge which of two responses is better for the given domain.

    Returns dict with keys: scores, weighted, preference, confidence, rationale.
    Returns None on LLM failure or unparseable output.
    """
    domain = DOMAINS.get(domain_id)
    if domain is None:
        logger.error("Unknown domain_id: %s. Valid: %s", domain_id, list(DOMAINS))
        return None

    seed = SeedPrompt(
        domain=domain_id, category=category, prompt=prompt,
        difficulty=difficulty, context=context,
    )
    judge_prompt = _build_judge_prompt(seed, response_a, response_b, domain)
    raw = generate_response(judge_prompt, temperature=0.05, max_tokens=1400)
    if raw is None:
        logger.warning("LLM returned None for judge (domain=%s)", domain_id)
        return None
    return _parse_judgment(raw, domain)


def generate_and_judge(
    domain_id: str,
    category: Optional[str] = None,
    min_confidence: float = MIN_CONFIDENCE,
) -> Optional[dict]:
    """
    End-to-end: fetch seed prompt → generate pair → judge → return record dict.

    Returns a PreferenceRecord-compatible dict or None when:
    - No seed prompt available
    - LLM returns placeholder responses (no backend configured)
    - Judgment confidence below min_confidence
    """
    domain = DOMAINS.get(domain_id)
    if domain is None:
        logger.error("Unknown domain_id: %s", domain_id)
        return None

    seed: SeedPrompt = get_random_prompt(domain_id, category)
    if seed is None:
        logger.warning("No prompt available domain=%s category=%s", domain_id, category)
        return None

    # Generate two diverse responses
    resp_a, resp_b = generate_response_pair(
        seed.prompt,
        domain_id=domain_id,
        temperature_low=0.25,
        temperature_high=0.75,
        max_tokens_a=1024,
        max_tokens_b=800,
        randomize_order=True,
    )

    # Skip placeholder fallback (means no LLM backend is reachable)
    if "[Placeholder" in resp_a or "[Placeholder" in resp_b:
        logger.info("LLM backend unavailable — skipping domain=%s", domain_id)
        return None

    judge_prompt_obj = _build_judge_prompt(seed, resp_a, resp_b, domain)
    raw = generate_response(judge_prompt_obj, temperature=0.05, max_tokens=1400)
    if raw is None:
        return None

    judgment = _parse_judgment(raw, domain)
    if judgment is None:
        return None

    if judgment["confidence"] < min_confidence:
        logger.debug(
            "Confidence %.3f < %.3f — discarding (domain=%s)",
            judgment["confidence"], min_confidence, domain_id,
        )
        return None

    # Build PreferenceRecord-compatible dict
    ts = datetime.now(timezone.utc).isoformat()
    record_hash = hashlib.sha256(
        f"{domain_id}|{seed.prompt}|{JUDGE_ANNOTATOR}|{ts}".encode()
    ).hexdigest()[:16]

    winner = judgment["preference"]
    dim_scores = {
        k: (judgment["scores"][winner][k] if winner != "TIE" else judgment["scores"]["A"][k])
        for k in judgment["scores"].get("A", {})
    }

    return {
        "domain":            domain_id,
        "category":          seed.category,
        "prompt":            seed.prompt,
        "response_a":        resp_a,
        "response_b":        resp_b,
        "annotator_id":      JUDGE_ANNOTATOR,
        "preference":        winner,
        "dimension_scores":  dim_scores,
        "timestamp":         ts,
        "record_hash":       record_hash,
        "difficulty":        seed.difficulty,
        "notes":             (judgment.get("rationale") or "")[:500]
                             + f" [auto_judge conf={judgment['confidence']:.2f}]",
        "response_a_model":  os.getenv("LLM_BACKEND", "ollama"),
        "response_b_model":  os.getenv("LLM_BACKEND", "ollama"),
        # DPO-ready fields (bonus)
        "chosen":            resp_a if winner in ("A", "TIE") else resp_b,
        "rejected":          resp_b if winner in ("A", "TIE") else resp_a,
        "judge_confidence":  judgment["confidence"],
        "judge_weighted":    judgment.get("weighted", {}),
    }


# ── Batch collection ───────────────────────────────────────────────────────────

def batch_collect(
    domain_id: str,
    count: int = 20,
    min_confidence: float = MIN_CONFIDENCE,
    output_path: Optional[str] = None,
) -> list[dict]:
    """
    Autonomously generate `count` preference records for a domain and write
    them to the JSONL store (picked up automatically by HF CommitScheduler).

    Returns the list of accepted records.
    """
    if output_path is None:
        data_dir = Path(os.getenv("PREFERENCE_DATA_DIR", "/tmp/preference_data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(data_dir / f"{domain_id}_preferences.jsonl")

    records: list[dict] = []
    attempts = 0
    max_attempts = count * 6

    print(f"[auto_judge] batch_collect domain={domain_id} target={count} "
          f"min_conf={min_confidence}")

    while len(records) < count and attempts < max_attempts:
        attempts += 1
        try:
            rec = generate_and_judge(domain_id, min_confidence=min_confidence)
        except Exception as exc:
            logger.warning("Attempt %d failed: %s", attempts, exc)
            continue

        if rec is None:
            continue

        records.append(rec)
        with open(output_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")

        print(
            f"  [{len(records):3d}/{count}] pref={rec['preference']} "
            f"conf={rec['judge_confidence']:.2f}  cat={rec['category']}"
        )

    print(f"[auto_judge] Done — {len(records)}/{count} records "
          f"({attempts} attempts) → {output_path}")
    return records


def sweep_all_domains(
    count_per_domain: int = 20,
    min_confidence: float = MIN_CONFIDENCE,
) -> dict[str, list[dict]]:
    """
    Run batch_collect across all 10 domains. Returns {domain_id: records}.
    Domains are shuffled to avoid systematic bias in partial runs.
    """
    domain_ids = list(DOMAINS.keys())
    random.shuffle(domain_ids)
    results: dict[str, list[dict]] = {}

    for did in domain_ids:
        print(f"\n{'─'*60}\n  Domain: {did}\n{'─'*60}")
        results[did] = batch_collect(did, count=count_per_domain,
                                     min_confidence=min_confidence)

    total = sum(len(v) for v in results.values())
    print(f"\n[auto_judge] Sweep complete — {total} total records across "
          f"{len(domain_ids)} domains.")
    return results


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    ap = argparse.ArgumentParser(
        description="Autonomous RSI preference collection via domain-aware LLM judge"
    )
    ap.add_argument("--domain",  default=None,
                    help="Single domain ID (omit to sweep all domains)")
    ap.add_argument("--count",   type=int, default=20,
                    help="Preference records to generate per domain (default: 20)")
    ap.add_argument("--min-confidence", type=float, default=MIN_CONFIDENCE,
                    dest="min_confidence",
                    help=f"Minimum judge confidence threshold (default: {MIN_CONFIDENCE})")
    ap.add_argument("--output",  default=None,
                    help="Output JSONL path (only with --domain)")
    args = ap.parse_args()

    if args.domain:
        batch_collect(
            domain_id=args.domain,
            count=args.count,
            min_confidence=args.min_confidence,
            output_path=args.output,
        )
    else:
        sweep_all_domains(
            count_per_domain=args.count,
            min_confidence=args.min_confidence,
        )
