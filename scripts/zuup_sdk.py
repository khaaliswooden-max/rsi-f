"""
Zuup Preference Collection SDK
==============================
Python SDK for integrating with Zuup Preference Collection API.
Use this to log preferences from your Zuup platforms (Orb, Veyra, Aureon, etc.)
"""

import httpx
from typing import Optional, Dict, Literal
from dataclasses import dataclass


@dataclass
class PreferenceResult:
    """Result of a preference submission."""
    success: bool
    hash: Optional[str] = None
    error: Optional[str] = None


class ZuupPreferenceClient:
    """Client for Zuup Preference Collection API."""
    
    def __init__(
        self, 
        base_url: str = "https://zuup1-zuup-preference-collection.hf.space",
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    def health(self) -> dict:
        """Check API health status."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/health")
            resp.raise_for_status()
            return resp.json()
    
    def stats(self) -> dict:
        """Get collection statistics."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/stats")
            resp.raise_for_status()
            return resp.json()
    
    def domains(self) -> dict:
        """Get available domains."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/domains")
            resp.raise_for_status()
            return resp.json()
    
    def log_preference(
        self,
        domain: str,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: Literal["A", "B", "TIE"],
        annotator_id: str = "sdk",
        category: str = "general",
        dimension_scores: Optional[Dict[str, int]] = None,
        response_a_model: str = "",
        response_b_model: str = "",
        notes: str = "",
    ) -> PreferenceResult:
        """
        Log a preference annotation.
        
        Args:
            domain: Domain ID (e.g., "procurement", "autonomy", "defense_wm")
            prompt: The prompt/question being answered
            response_a: First response to compare
            response_b: Second response to compare  
            preference: Which response is preferred ("A", "B", or "TIE")
            annotator_id: Identifier for the annotator
            category: Sub-category within domain
            dimension_scores: Quality ratings {"accuracy": 1-5, "safety": 1-5, ...}
            response_a_model: Model that generated response A
            response_b_model: Model that generated response B
            notes: Additional notes
            
        Returns:
            PreferenceResult with success status and record hash
        """
        if dimension_scores is None:
            dimension_scores = {
                "accuracy": 3,
                "safety": 3,
                "actionability": 3,
                "clarity": 3,
            }
        
        payload = {
            "domain": domain,
            "category": category,
            "prompt": prompt,
            "response_a": response_a,
            "response_b": response_b,
            "preference": preference,
            "annotator_id": annotator_id,
            "dimension_scores": dimension_scores,
            "response_a_model": response_a_model,
            "response_b_model": response_b_model,
            "notes": notes,
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/api/preferences",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return PreferenceResult(success=True, hash=data.get("hash"))
        except httpx.HTTPStatusError as e:
            return PreferenceResult(success=False, error=str(e))
        except Exception as e:
            return PreferenceResult(success=False, error=str(e))
    
    def export(
        self,
        format: Literal["dpo", "jsonl"] = "dpo",
        min_confidence: float = 0.0,
        limit: int = 10000,
        domain: Optional[str] = None,
        export_key: Optional[str] = None,
    ) -> dict:
        """
        Export preference data for training.
        
        Args:
            format: Export format ("dpo" for training, "jsonl" for raw)
            min_confidence: Minimum confidence threshold (0-1)
            limit: Maximum records to export
            domain: Filter by domain (optional)
            export_key: Premium export API key (required)
            
        Returns:
            Dict with count, format, and data
        """
        headers = {"Content-Type": "application/json"}
        headers["X-API-Key"] = export_key or self.api_key or ""
        
        payload = {
            "format": format,
            "min_confidence": min_confidence,
            "limit": limit,
        }
        if domain:
            payload["domain"] = domain
        
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{self.base_url}/api/export",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()


# Async version for high-throughput integrations
class AsyncZuupPreferenceClient:
    """Async client for Zuup Preference Collection API."""
    
    def __init__(
        self, 
        base_url: str = "https://zuup1-zuup-preference-collection.hf.space",
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def health(self) -> dict:
        """Check API health status."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/api/health")
            resp.raise_for_status()
            return resp.json()
    
    async def log_preference(
        self,
        domain: str,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: Literal["A", "B", "TIE"],
        annotator_id: str = "sdk",
        response_a_model: str = "",
        response_b_model: str = "",
        **kwargs,
    ) -> PreferenceResult:
        """Log a preference annotation asynchronously."""
        payload = {
            "domain": domain,
            "prompt": prompt,
            "response_a": response_a,
            "response_b": response_b,
            "preference": preference,
            "annotator_id": annotator_id,
            "response_a_model": response_a_model,
            "response_b_model": response_b_model,
            **kwargs,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/preferences",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return PreferenceResult(success=True, hash=data.get("hash"))
        except Exception as e:
            return PreferenceResult(success=False, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Usage Examples
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Initialize client
    client = ZuupPreferenceClient(
        base_url="https://zuup1-zuup-preference-collection.hf.space",
        api_key="your-api-key",  # Optional
    )
    
    # Check health
    print("Health:", client.health())
    
    # Get stats
    print("Stats:", client.stats())
    
    # Log a preference from your platform
    result = client.log_preference(
        domain="autonomy",  # Veyra platform
        prompt="How should an autonomous agent handle conflicting goals?",
        response_a="Implement a priority hierarchy with clear override rules...",
        response_b="Use a weighted utility function to balance goals...",
        preference="A",
        annotator_id="veyra-user-123",
        response_a_model="qwen2.5-7b",
        response_b_model="llama-3.1-8b",
        dimension_scores={
            "accuracy": 4,
            "safety": 5,
            "actionability": 4,
            "clarity": 4,
        },
    )
    print("Logged:", result)

