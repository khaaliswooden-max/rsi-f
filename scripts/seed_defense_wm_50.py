"""
50 synthetic defense_wm (Orb) preferences for DPO cold-start.
Run: python scripts/seed_defense_wm_50.py
"""

import httpx
import asyncio
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Import preferences from category files
from defense_wm_preferences_3d_reconstruction import RECONSTRUCTION_PREFS
from defense_wm_preferences_isr_analysis import ISR_PREFS
from defense_wm_preferences_geospatial import GEOSPATIAL_PREFS
from defense_wm_preferences_sensor_fusion import SENSOR_FUSION_PREFS

API_BASE = "https://zuup1-zuup-preference-collection.hf.space"
API_KEY = os.getenv("ZUUP_API_KEY", "zuup-seed-key")

# Local mode: save directly to JSONL file
LOCAL_MODE = os.getenv("LOCAL_MODE", "true").lower() == "true"
DATA_DIR = Path(__file__).parent.parent / "preference_data"

# Combine all preferences
DEFENSE_WM_PREFERENCES = (
    RECONSTRUCTION_PREFS +  # 13 items
    ISR_PREFS +             # 12 items
    GEOSPATIAL_PREFS +      # 13 items
    SENSOR_FUSION_PREFS     # 12 items
)  # Total: 50 items


def generate_hash(record: dict) -> str:
    """Generate a unique hash for a preference record."""
    content = f"{record['prompt']}{record['response_a']}{record['response_b']}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def save_local(preferences: list) -> dict:
    """Save preferences directly to local JSONL file."""
    results = {"success": 0, "failed": 0, "errors": []}
    
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / "defense_wm_preferences.jsonl"
    
    # Read existing hashes to avoid duplicates
    existing_hashes = set()
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line.strip())
                    if rec.get("record_hash"):
                        existing_hashes.add(rec["record_hash"])
                except:
                    pass
    
    with open(filepath, 'a', encoding='utf-8') as f:
        for i, pref in enumerate(preferences):
            record = {
                "domain": "defense_wm",
                "category": pref["category"],
                "prompt": pref["prompt"],
                "response_a": pref["chosen"],
                "response_b": pref["rejected"],
                "preference": "A",
                "annotator_id": "synthetic_seed_v1",
                "dimension_scores": {
                    "accuracy": 5,
                    "completeness": 5,
                    "clarity": 5,
                    "relevance": 5
                },
                "metadata": {
                    "source": "synthetic",
                    "generator": "seed_defense_wm_50_v1",
                    "batch_index": i,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
            record["record_hash"] = generate_hash(record)
            
            if record["record_hash"] in existing_hashes:
                print(f"[SKIP] [{i+1}/50] Duplicate: {pref['prompt'][:40]}...")
                continue
            
            try:
                f.write(json.dumps(record) + "\n")
                results["success"] += 1
                print(f"[OK] [{i+1}/50] {pref['category']}: {pref['prompt'][:50]}...")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"index": i, "error": str(e)})
                print(f"[ERR] [{i+1}/50] Error: {e}")
    
    return results


async def submit_preferences_api():
    """Submit all preferences to the API."""
    async with httpx.AsyncClient(timeout=60) as client:
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i, pref in enumerate(DEFENSE_WM_PREFERENCES):
            try:
                response = await client.post(
                    f"{API_BASE}/api/preferences",
                    headers={"X-API-Key": API_KEY},
                    json={
                        "domain": "defense_wm",
                        "category": pref["category"],
                        "prompt": pref["prompt"],
                        "response_a": pref["chosen"],
                        "response_b": pref["rejected"],
                        "preference": "A",
                        "annotator_id": "synthetic_seed_v1",
                        "dimension_scores": {
                            "accuracy": 5,
                            "completeness": 5,
                            "clarity": 5,
                            "relevance": 5
                        },
                        "metadata": {
                            "source": "synthetic",
                            "generator": "seed_defense_wm_50_v1",
                            "batch_index": i,
                            "generated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                if response.status_code == 200:
                    results["success"] += 1
                    print(f"[OK] [{i+1}/50] {pref['category']}: {pref['prompt'][:50]}...")
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "index": i,
                        "status": response.status_code,
                        "response": response.text[:200]
                    })
                    print(f"[FAIL] [{i+1}/50] Failed: {response.status_code}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"index": i, "error": str(e)})
                print(f"[ERR] [{i+1}/50] Error: {e}")
            
            await asyncio.sleep(0.1)
        
        return results


def submit_preferences():
    """Submit preferences - locally or via API based on mode."""
    if LOCAL_MODE:
        return save_local(DEFENSE_WM_PREFERENCES)
    else:
        return asyncio.run(submit_preferences_api())


def main():
    mode = "LOCAL" if LOCAL_MODE else "API"
    print(f"Defense WM Preferences: {len(DEFENSE_WM_PREFERENCES)} total [{mode} mode]")
    print(f"  - 3D Reconstruction: {len(RECONSTRUCTION_PREFS)}")
    print(f"  - ISR Analysis: {len(ISR_PREFS)}")
    print(f"  - Geospatial: {len(GEOSPATIAL_PREFS)}")
    print(f"  - Sensor Fusion: {len(SENSOR_FUSION_PREFS)}")
    
    if LOCAL_MODE:
        print(f"Writing to: {DATA_DIR / 'defense_wm_preferences.jsonl'}")
    else:
        print(f"API: {API_BASE}")
    print("=" * 60)
    
    results = submit_preferences()
    
    print("=" * 60)
    print(f"Results: {results['success']} success, {results['failed']} failed")
    
    if results["errors"]:
        print("\nErrors (first 5):")
        for err in results["errors"][:5]:
            print(f"  - Index {err.get('index')}: {str(err)[:100]}")


if __name__ == "__main__":
    main()
