"""
Automated Preference Collection Pipeline
=========================================
Captures preferences from Zuup platform usage automatically.
Integrates with Orb, Aureon, Veyra, and other Zuup platforms.

This module provides:
1. Event hooks for platform integrations
2. Automatic preference extraction from user interactions
3. Quality gates for DPO-trainable data
4. Batch submission to preference API

Usage:
    # In your Zuup platform code:
    from scripts.collection_pipeline import PreferenceCollector
    
    collector = PreferenceCollector(domain="defense_wm", api_key="...")
    
    # When user selects between two responses:
    collector.log_comparison(
        prompt="User's question",
        response_a="First AI response",
        response_b="Second AI response", 
        selected="A",  # User's choice
        user_id="user123"
    )
"""

import os
import sys
import json
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import queue

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.zuup_sdk import ZuupPreferenceClient, AsyncZuupPreferenceClient


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

ZUUP_API_KEY = os.getenv("ZUUP_API_KEY", "")
DEFAULT_BATCH_SIZE = 10
DEFAULT_FLUSH_INTERVAL = 60  # seconds


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CollectedPreference:
    """A preference collected from platform usage."""
    domain: str
    category: str
    prompt: str
    response_a: str
    response_b: str
    preference: Literal["A", "B", "TIE"]
    user_id: str
    timestamp: str
    session_id: str = ""
    response_a_model: str = ""
    response_b_model: str = ""
    response_time_a: float = 0.0  # seconds
    response_time_b: float = 0.0
    confidence: float = 1.0  # User confidence in selection
    context: Dict = None  # Additional context
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass 
class QualityMetrics:
    """Quality metrics for a preference pair."""
    prompt_length: int
    response_a_length: int
    response_b_length: int
    length_ratio: float  # Ratio of response lengths
    has_code: bool
    has_formatting: bool
    response_time_diff: float
    is_valid: bool
    rejection_reason: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY GATES
# ═══════════════════════════════════════════════════════════════════════════════

class QualityGate:
    """Validates preferences for DPO trainability."""
    
    # Thresholds
    MIN_PROMPT_LENGTH = 10
    MIN_RESPONSE_LENGTH = 50
    MAX_RESPONSE_LENGTH = 10000
    MIN_LENGTH_RATIO = 0.3  # Shorter response must be at least 30% of longer
    MAX_RESPONSE_TIME_DIFF = 30  # seconds - if too different, might indicate issue
    
    @classmethod
    def validate(cls, pref: CollectedPreference) -> QualityMetrics:
        """Validate a preference pair for quality."""
        
        prompt_len = len(pref.prompt)
        resp_a_len = len(pref.response_a)
        resp_b_len = len(pref.response_b)
        
        # Calculate length ratio
        max_len = max(resp_a_len, resp_b_len)
        min_len = min(resp_a_len, resp_b_len)
        length_ratio = min_len / max_len if max_len > 0 else 0
        
        # Check for code/formatting
        has_code = "```" in pref.response_a or "```" in pref.response_b
        has_formatting = any(c in pref.response_a + pref.response_b 
                           for c in ["**", "##", "- ", "1. "])
        
        # Response time difference
        time_diff = abs(pref.response_time_a - pref.response_time_b)
        
        # Validation checks
        is_valid = True
        rejection_reason = ""
        
        if prompt_len < cls.MIN_PROMPT_LENGTH:
            is_valid = False
            rejection_reason = f"Prompt too short ({prompt_len} chars)"
        elif resp_a_len < cls.MIN_RESPONSE_LENGTH:
            is_valid = False
            rejection_reason = f"Response A too short ({resp_a_len} chars)"
        elif resp_b_len < cls.MIN_RESPONSE_LENGTH:
            is_valid = False
            rejection_reason = f"Response B too short ({resp_b_len} chars)"
        elif resp_a_len > cls.MAX_RESPONSE_LENGTH:
            is_valid = False
            rejection_reason = f"Response A too long ({resp_a_len} chars)"
        elif resp_b_len > cls.MAX_RESPONSE_LENGTH:
            is_valid = False
            rejection_reason = f"Response B too long ({resp_b_len} chars)"
        elif length_ratio < cls.MIN_LENGTH_RATIO:
            is_valid = False
            rejection_reason = f"Response length ratio too skewed ({length_ratio:.2f})"
        elif pref.response_a.strip() == pref.response_b.strip():
            is_valid = False
            rejection_reason = "Responses are identical"
        elif pref.prompt.strip() in pref.response_a or pref.prompt.strip() in pref.response_b:
            # Check if response just echoes prompt
            if len(pref.response_a) < len(pref.prompt) * 1.5:
                is_valid = False
                rejection_reason = "Response too similar to prompt"
        
        return QualityMetrics(
            prompt_length=prompt_len,
            response_a_length=resp_a_len,
            response_b_length=resp_b_len,
            length_ratio=length_ratio,
            has_code=has_code,
            has_formatting=has_formatting,
            response_time_diff=time_diff,
            is_valid=is_valid,
            rejection_reason=rejection_reason
        )


# ═══════════════════════════════════════════════════════════════════════════════
# DEDUPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class DeduplicationCache:
    """Prevents duplicate preference submissions."""
    
    def __init__(self, max_size: int = 10000):
        self.cache = set()
        self.max_size = max_size
    
    def _hash(self, pref: CollectedPreference) -> str:
        """Generate hash for preference."""
        content = f"{pref.prompt}|{pref.response_a[:100]}|{pref.response_b[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_duplicate(self, pref: CollectedPreference) -> bool:
        """Check if preference is a duplicate."""
        h = self._hash(pref)
        if h in self.cache:
            return True
        
        # Add to cache
        if len(self.cache) >= self.max_size:
            # Remove oldest (convert to list, remove first half)
            self.cache = set(list(self.cache)[self.max_size // 2:])
        
        self.cache.add(h)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class PreferenceCollector:
    """
    Collects and submits preferences from platform usage.
    
    Features:
    - Batched submission for efficiency
    - Quality validation
    - Deduplication
    - Async support
    - Background processing
    """
    
    def __init__(
        self,
        domain: str,
        api_key: str = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        flush_interval: int = DEFAULT_FLUSH_INTERVAL,
        enable_quality_gate: bool = True,
        auto_flush: bool = True,
    ):
        self.domain = domain
        self.api_key = api_key or ZUUP_API_KEY
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.enable_quality_gate = enable_quality_gate
        
        self.client = ZuupPreferenceClient(api_key=self.api_key)
        self.queue = queue.Queue()
        self.dedup_cache = DeduplicationCache()
        
        # Statistics
        self.stats = {
            "collected": 0,
            "submitted": 0,
            "rejected_quality": 0,
            "rejected_duplicate": 0,
            "failed": 0,
        }
        
        # Background flusher
        self._stop_event = threading.Event()
        if auto_flush:
            self._start_background_flusher()
    
    def _start_background_flusher(self):
        """Start background thread for periodic flushing."""
        def flusher():
            while not self._stop_event.is_set():
                self._stop_event.wait(self.flush_interval)
                if not self._stop_event.is_set():
                    self.flush()
        
        self._flusher_thread = threading.Thread(target=flusher, daemon=True)
        self._flusher_thread.start()
    
    def log_comparison(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        selected: Literal["A", "B", "TIE"],
        user_id: str,
        category: str = "general",
        session_id: str = "",
        response_a_model: str = "",
        response_b_model: str = "",
        response_time_a: float = 0.0,
        response_time_b: float = 0.0,
        confidence: float = 1.0,
        context: Dict = None,
    ):
        """
        Log a user preference comparison.
        
        Args:
            prompt: The user's question/prompt
            response_a: First response shown
            response_b: Second response shown
            selected: User's selection ("A", "B", or "TIE")
            user_id: Identifier for the user (anonymized)
            category: Domain sub-category
            session_id: Session identifier
            response_a_model: Model that generated response A
            response_b_model: Model that generated response B
            response_time_a: Time to generate response A
            response_time_b: Time to generate response B
            confidence: User's confidence in their selection (0-1)
            context: Additional context dictionary
        """
        pref = CollectedPreference(
            domain=self.domain,
            category=category,
            prompt=prompt,
            response_a=response_a,
            response_b=response_b,
            preference=selected,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            response_a_model=response_a_model,
            response_b_model=response_b_model,
            response_time_a=response_time_a,
            response_time_b=response_time_b,
            confidence=confidence,
            context=context,
        )
        
        self.stats["collected"] += 1
        
        # Quality validation
        if self.enable_quality_gate:
            metrics = QualityGate.validate(pref)
            if not metrics.is_valid:
                self.stats["rejected_quality"] += 1
                return False
        
        # Deduplication
        if self.dedup_cache.is_duplicate(pref):
            self.stats["rejected_duplicate"] += 1
            return False
        
        # Add to queue
        self.queue.put(pref)
        
        # Auto-flush if batch size reached
        if self.queue.qsize() >= self.batch_size:
            self.flush()
        
        return True
    
    def flush(self) -> int:
        """Submit all queued preferences."""
        submitted = 0
        
        while not self.queue.empty():
            try:
                pref = self.queue.get_nowait()
                
                result = self.client.log_preference(
                    domain=pref.domain,
                    category=pref.category,
                    prompt=pref.prompt,
                    response_a=pref.response_a,
                    response_b=pref.response_b,
                    preference=pref.preference,
                    annotator_id=f"platform_{pref.user_id}",
                    response_a_model=pref.response_a_model,
                    response_b_model=pref.response_b_model,
                    notes=json.dumps({
                        "session": pref.session_id,
                        "confidence": pref.confidence,
                        "response_time_a": pref.response_time_a,
                        "response_time_b": pref.response_time_b,
                    })
                )
                
                if result.success:
                    self.stats["submitted"] += 1
                    submitted += 1
                else:
                    self.stats["failed"] += 1
                    
            except queue.Empty:
                break
            except Exception as e:
                self.stats["failed"] += 1
                print(f"[ERROR] Failed to submit preference: {e}")
        
        return submitted
    
    def get_stats(self) -> Dict:
        """Get collection statistics."""
        return {
            **self.stats,
            "queue_size": self.queue.qsize(),
            "acceptance_rate": (
                self.stats["submitted"] / self.stats["collected"] 
                if self.stats["collected"] > 0 else 0
            ),
        }
    
    def stop(self):
        """Stop background processing and flush remaining."""
        self._stop_event.set()
        self.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class OrbIntegration:
    """Integration for Orb (Defense World Models) platform."""
    
    def __init__(self, api_key: str = None):
        self.collector = PreferenceCollector(
            domain="defense_wm",
            api_key=api_key
        )
    
    def on_scene_comparison(
        self,
        query: str,
        scene_a: str,  # Scene description/analysis A
        scene_b: str,  # Scene description/analysis B
        selected: str,
        user_id: str,
        scene_type: str = "3d_reconstruction",
    ):
        """Log when user selects between two scene analyses."""
        self.collector.log_comparison(
            prompt=query,
            response_a=scene_a,
            response_b=scene_b,
            selected=selected,
            user_id=user_id,
            category=scene_type,
        )


class AureonIntegration:
    """Integration for Aureon (Procurement) platform."""
    
    def __init__(self, api_key: str = None):
        self.collector = PreferenceCollector(
            domain="procurement",
            api_key=api_key
        )
    
    def on_rfp_analysis(
        self,
        rfp_section: str,
        analysis_a: str,
        analysis_b: str,
        selected: str,
        user_id: str,
        category: str = "rfp_analysis",
    ):
        """Log when user selects between two RFP analyses."""
        self.collector.log_comparison(
            prompt=f"Analyze this RFP section:\n\n{rfp_section}",
            response_a=analysis_a,
            response_b=analysis_b,
            selected=selected,
            user_id=user_id,
            category=category,
        )
    
    def on_proposal_draft(
        self,
        requirement: str,
        draft_a: str,
        draft_b: str,
        selected: str,
        user_id: str,
    ):
        """Log when user selects between two proposal drafts."""
        self.collector.log_comparison(
            prompt=f"Draft proposal section for:\n\n{requirement}",
            response_a=draft_a,
            response_b=draft_b,
            selected=selected,
            user_id=user_id,
            category="proposal_writing",
        )


class CiviumIntegration:
    """Integration for Civium (Halal Compliance) platform."""
    
    def __init__(self, api_key: str = None):
        self.collector = PreferenceCollector(
            domain="halal",
            api_key=api_key
        )
    
    def on_ingredient_check(
        self,
        ingredient: str,
        assessment_a: str,
        assessment_b: str,
        selected: str,
        user_id: str,
    ):
        """Log when user selects between two ingredient assessments."""
        self.collector.log_comparison(
            prompt=f"Assess halal status of ingredient: {ingredient}",
            response_a=assessment_a,
            response_b=assessment_b,
            selected=selected,
            user_id=user_id,
            category="ingredient_analysis",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test the collection pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test preference collection pipeline")
    parser.add_argument("--domain", default="procurement", help="Domain to test")
    parser.add_argument("--api-key", help="Zuup API key")
    parser.add_argument("--test-submit", action="store_true", help="Submit a test preference")
    
    args = parser.parse_args()
    
    api_key = args.api_key or ZUUP_API_KEY
    
    if not api_key:
        print("[ERROR] No API key provided")
        print("  Set ZUUP_API_KEY or pass --api-key")
        return
    
    collector = PreferenceCollector(
        domain=args.domain,
        api_key=api_key,
        auto_flush=False,  # Manual flush for testing
    )
    
    if args.test_submit:
        print(f"[TEST] Submitting test preference for {args.domain}...")
        
        result = collector.log_comparison(
            prompt="What is the difference between FFP and CPFF contracts?",
            response_a="""FFP (Firm Fixed Price) places cost risk on the contractor - the price is set at award and doesn't change regardless of actual costs. CPFF (Cost Plus Fixed Fee) places cost risk on the government - they reimburse allowable costs plus a fixed fee. FFP is preferred when requirements are well-defined; CPFF is used for R&D or uncertain scope.""",
            response_b="FFP means fixed price, CPFF means cost plus fee. They're different contract types.",
            selected="A",
            user_id="test_user",
            category="far_dfars",
        )
        
        if result:
            print("[OK] Preference queued")
            submitted = collector.flush()
            print(f"[OK] Submitted {submitted} preference(s)")
        else:
            print("[FAILED] Preference rejected by quality gate or duplicate")
    
    print("\nStatistics:")
    for k, v in collector.get_stats().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

