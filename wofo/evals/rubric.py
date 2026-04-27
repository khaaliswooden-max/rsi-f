"""Rubric-based evals for research notes.

A "rubric" is a list of criteria, each with a name, description, and a
0-3 score scale. We score notes two ways:

1. **Heuristic** — fast, deterministic, no API. Scores criteria by
   pattern-matching on the note text. Good enough for regression
   detection during development.
2. **LLM judge** — when `ANTHROPIC_API_KEY` is set and the `anthropic`
   SDK is installed, a separate model scores the note. The judge model
   should be different from (or at least independently configured from)
   the agent under test to avoid trivial gaming.

The same `default_rubric` is used by both so scores are comparable.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Criterion:
    name: str
    description: str
    heuristic: Callable[[str], int]


@dataclass
class RubricResult:
    criteria_scores: dict[str, int]
    rationales: dict[str, str] = field(default_factory=dict)
    judge: str = "heuristic"   # or "llm"
    total: int = 0
    max_total: int = 0


# --- Heuristic detectors ----------------------------------------------------


def _h_provenance(text: str) -> int:
    """Does the note cite filings or sources?"""
    score = 0
    if re.search(r"\baccession\b|\bCIK\b|\bEDGAR\b", text, re.I): score += 1
    if re.search(r"13F|13-F|13F-HR", text, re.I): score += 1
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", text): score += 1
    return min(score, 3)


def _h_staleness_acknowledged(text: str) -> int:
    return 3 if re.search(r"\b(stale|delayed|45\s*days?|lag|backward[- ]looking)\b", text, re.I) else 0


def _h_concrete_numbers(text: str) -> int:
    n_dollars = len(re.findall(r"\$\d", text))
    n_pcts    = len(re.findall(r"\d+\.?\d*%", text))
    n_shares  = len(re.findall(r"\bshares?\b", text, re.I))
    raw = n_dollars + n_pcts + n_shares
    return min(raw // 2, 3)


def _h_distinguishes_fact_from_opinion(text: str) -> int:
    score = 0
    if re.search(r"\b(reported|filed|disclosed)\b", text, re.I): score += 1
    if re.search(r"\b(thesis|view|expect|likely|risk|caveat)\b", text, re.I): score += 1
    if re.search(r"\b(I think|we believe|in our view)\b", text, re.I): score += 1
    return min(score, 3)


def _h_no_fabricated_tickers(text: str) -> int:
    """Heuristic: penalize obvious red flags. Returns 3 unless we see clear fabrication.

    A fabrication signal: 5+ char ALL-CAPS tokens that aren't real words and
    aren't in our known SA-LP universe. This is a *weak* check and meant
    only as a tripwire, not a substitute for review.
    """
    KNOWN = {
        "CRWV","BE","INTC","LITE","CORZ","IREN","APLD","SNDK","EQT","CIFR",
        "COHR","CEG","MRVL","MOD","ATEX","VST","NVDA","AVGO","TSM","MU",
        "WDC","STX","GLXY","CLSK","BITF","LBRT","INFY","PUMP","BW","PSIX",
        "WYFI","KRC","SPY","QQQ","SCION","BRK","SEC","CIK","LP","LLC","CEO",
        "CFO","ETF","HHI","CAGR","NAV","NYSE","NASDAQ","USD","EBITDA","EPS",
        "AI","ML","ADD","NEW","EXIT","TRIM","HOLD","INITIAL","RSI","SF",
    }
    suspicious = 0
    for m in re.finditer(r"\b[A-Z]{4,5}\b", text):
        if m.group() not in KNOWN:
            suspicious += 1
    return 3 if suspicious < 3 else max(0, 3 - suspicious // 3)


def _h_actionable(text: str) -> int:
    """Does the note say something specific the reader can act on?"""
    score = 0
    if re.search(r"\bwatch(list)?\b", text, re.I): score += 1
    if re.search(r"\b(buy|trim|exit|new position|add|hold)\b", text, re.I): score += 1
    if re.search(r"\b(monitor|review|next quarter|next filing)\b", text, re.I): score += 1
    return min(score, 3)


DEFAULT_CRITERIA: list[Criterion] = [
    Criterion("provenance", "Cites filings, accession numbers, dates, sources.", _h_provenance),
    Criterion("staleness_ack", "Acknowledges 13F is delayed by ~45 days.", _h_staleness_acknowledged),
    Criterion("concrete_numbers", "Uses specific dollar / percent / share figures.", _h_concrete_numbers),
    Criterion("fact_vs_opinion", "Distinguishes what was reported from analyst view.", _h_distinguishes_fact_from_opinion),
    Criterion("no_fabrication", "No suspicious / fabricated-looking tickers.", _h_no_fabricated_tickers),
    Criterion("actionable", "Identifies something specific to watch / do.", _h_actionable),
]


def default_rubric() -> list[Criterion]:
    return list(DEFAULT_CRITERIA)


# --- Scorers ---------------------------------------------------------------


def _heuristic_score(note: str, criteria: list[Criterion]) -> RubricResult:
    scores = {c.name: c.heuristic(note) for c in criteria}
    rationales = {c.name: f"heuristic: {scores[c.name]}/3" for c in criteria}
    return RubricResult(
        criteria_scores=scores,
        rationales=rationales,
        judge="heuristic",
        total=sum(scores.values()),
        max_total=3 * len(criteria),
    )


def _llm_score(note: str, criteria: list[Criterion], *, model: str) -> RubricResult:
    import anthropic  # type: ignore
    client = anthropic.Anthropic()
    rubric_text = "\n".join(f"- {c.name}: {c.description}" for c in criteria)
    schema_keys = [c.name for c in criteria]
    prompt = (
        "You are an investment-research editor. Score the following note on each criterion 0-3.\n"
        "0 = absent, 1 = mentioned, 2 = adequate, 3 = excellent.\n\n"
        f"Criteria:\n{rubric_text}\n\n"
        f"Respond as a JSON object with keys: {schema_keys} "
        "and an additional 'rationales' object mapping each criterion name "
        "to a one-sentence justification. Output JSON only.\n\n"
        "<note>\n" + note + "\n</note>"
    )
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    txt = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    payload = _extract_json(txt)
    scores = {k: int(payload.get(k, 0)) for k in schema_keys}
    rationales = payload.get("rationales", {}) or {}
    rationales = {k: str(rationales.get(k, "")) for k in schema_keys}
    return RubricResult(
        criteria_scores=scores,
        rationales=rationales,
        judge=f"llm:{model}",
        total=sum(scores.values()),
        max_total=3 * len(criteria),
    )


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from `text`. Tolerates markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    # Greedy find balanced braces.
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                return json.loads(text[start : i + 1])
    raise ValueError(f"no JSON object in judge response: {text[:200]}")


def score_research_note(
    note: str,
    *,
    criteria: list[Criterion] | None = None,
    use_llm: bool | None = None,
    model: str = "claude-sonnet-4-6",
) -> RubricResult:
    """Score a research note. Falls back to heuristic if LLM is not available."""
    crit = criteria or default_rubric()
    want_llm = use_llm if use_llm is not None else bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not want_llm:
        return _heuristic_score(note, crit)
    try:
        return _llm_score(note, crit, model=model)
    except Exception:
        # Never fail the caller because the judge is unavailable. Always
        # return *some* score; tag it so downstream knows.
        result = _heuristic_score(note, crit)
        result.judge = "heuristic-fallback"
        return result
