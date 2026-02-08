"""
Shared LLM client for preference pair generation.
Supports Ollama (default) and optional Claude/OpenAI via env vars.
Used by annotation UIs and optional batch generation scripts.
"""

import os
import random
from typing import Optional, Tuple

import httpx

# Backend selection: ollama | anthropic | openai
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
DEFAULT_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Optional Anthropic/OpenAI for generate_response when backend is set
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def generate_response(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
) -> Optional[str]:
    """
    Generate a single response from the configured LLM backend.
    Returns None on failure so callers can fall back to placeholders.
    """
    max_tokens = max_tokens or DEFAULT_MAX_TOKENS
    if LLM_BACKEND == "ollama":
        return _generate_ollama(prompt, temperature, max_tokens)
    if LLM_BACKEND == "anthropic" and HAS_ANTHROPIC and ANTHROPIC_API_KEY:
        return _generate_anthropic(prompt, temperature, max_tokens)
    if LLM_BACKEND == "openai" and HAS_OPENAI and OPENAI_API_KEY:
        return _generate_openai(prompt, temperature, max_tokens)
    return _generate_ollama(prompt, temperature, max_tokens)


def _generate_ollama(prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
    """Generate using local Ollama API."""
    try:
        with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
            r = client.post(
                f"{OLLAMA_BASE.rstrip('/')}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False,
                    "options": {"num_predict": max_tokens},
                },
            )
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip() or None
    except Exception:
        return None


def _generate_anthropic(prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
    """Generate using Anthropic API."""
    if not HAS_ANTHROPIC or not ANTHROPIC_API_KEY:
        return None
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if msg.content and len(msg.content) > 0:
            return msg.content[0].text.strip()
        return None
    except Exception:
        return None


def _generate_openai(prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
    """Generate using OpenAI API."""
    if not HAS_OPENAI or not OPENAI_API_KEY:
        return None
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if r.choices and r.choices[0].message.content:
            return r.choices[0].message.content.strip()
        return None
    except Exception:
        return None


def generate_response_pair(
    prompt: str,
    domain_id: Optional[str] = None,
    temperature_low: float = 0.3,
    temperature_high: float = 0.7,
    max_tokens_a: int = 1024,
    max_tokens_b: int = 512,
    randomize_order: bool = True,
) -> Tuple[str, str]:
    """
    Generate two responses for pairwise comparison (e.g. preference annotation).
    Uses low temperature for higher-quality response and high temperature for more varied.
    Returns (response_a, response_b). If LLM fails, returns placeholder strings so UI still works.
    """
    resp_a = generate_response(prompt, temperature=temperature_low, max_tokens=max_tokens_a)
    resp_b = generate_response(prompt, temperature=temperature_high, max_tokens=max_tokens_b)

    if resp_a is None or resp_b is None:
        return _placeholder_responses(prompt, domain_id)

    if randomize_order and random.random() > 0.5:
        return resp_b, resp_a
    return resp_a, resp_b


def get_placeholder_responses(prompt: str, domain_id: Optional[str] = None) -> Tuple[str, str]:
    """Return placeholder response pair without calling LLM (e.g. when use_llm=False)."""
    return _placeholder_responses(prompt, domain_id)


def _placeholder_responses(prompt: str, domain_id: Optional[str]) -> Tuple[str, str]:
    """Fallback when LLM is unavailable (e.g. Ollama not running)."""
    domain_name = domain_id or "this domain"
    a = f"""**Response A**

Based on my analysis of your {domain_name} query:

1. **Primary Analysis**: The core issue involves understanding fundamental requirements.
2. **Key Considerations**: Regulatory factors, technical feasibility, resource implications.
3. **Recommended Approach**: A phased approach prioritizing risk mitigation.
4. **Next Steps**: Document current state, identify stakeholders, develop roadmap.

*[Placeholder – start Ollama or set LLM_BACKEND/API keys for live responses]*"""
    b = f"""**Response B**

Thank you for this {domain_name} question. Here's my analysis:

**Executive Summary**: This requires balancing immediate needs against long-term objectives.

**Technical Perspective**:
- Option 1: Conservative approach minimizing risk
- Option 2: Aggressive approach maximizing benefits
- Option 3: Balanced trade-off approach

**Recommendations**:
1. Conduct thorough assessment
2. Engage stakeholders early
3. Establish success metrics
4. Implement iterative improvements

*[Placeholder – start Ollama or set LLM_BACKEND/API keys for live responses]*"""
    return a, b
