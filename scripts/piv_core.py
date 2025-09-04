#!/usr/bin/env python3
"""
piv_core.py

Simple deterministic Persistent Identity Vector (PIV) MVP.

Function:
  calculate_piv(events: list[dict]) -> dict

Current deterministic method (MVP):
  - Take the last up to 5 event_type values, join with '|'
  - Compute SHA256 and return a short hex digest and metadata
"""
from __future__ import annotations
import hashlib
from typing import List, Dict

SEED = 42  # conceptual seed used in the method metadata (not mixed into hash for simplicity)

def _last_n_event_types(events: List[Dict], n: int = 5):
    types = [e.get("event_type","") for e in events if isinstance(e, dict)]
    return types[-n:]

def calculate_piv(events: List[Dict]) -> Dict:
    """
    Calculate a deterministic PIV from given events list.
    Returns a dict like:
      {"piv_hash": "<sha256hex>", "method": "sha256-last5", "seed": 42}
    """
    last_types = _last_n_event_types(events, 5)
    joined = "|".join(last_types).encode("utf-8")
    h = hashlib.sha256(joined).hexdigest()
    # short representation to keep logs compact
    return {"piv_hash": h, "piv_short": h[:16], "method": "sha256-last5", "seed": SEED}
    
# small command-line utility for quick tests
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    if isinstance(data, dict) and "events" in data:
        print(json.dumps(calculate_piv(data["events"]), indent=2))
    else:
        print("Usage: echo '{\"events\": [{...}, ...]}' | python3 scripts/piv_core.py")
