#!/usr/bin/env python3
"""
heartbeat_with_piv.py

Wrapper that enriches incoming heartbeat events with a deterministic PIV.
Reads one JSON event from stdin, computes PIV based on last N events from ledger,
and writes the enriched event JSON to stdout.

Environment:
  HEART_LEDGER_PATH (optional): path to ledger jsonl (default "heart_ledger.jsonl")
If ledger not found, PIV will be computed from the single incoming event (still deterministic).
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from lamutual_project.piv_core import calculate_piv


LEDGER = os.environ.get("HEART_LEDGER_PATH", "heart_ledger.jsonl")

def read_ledger(path: str):
    p = Path(path)
    if not p.exists():
        return []
    out = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # skip malformed lines
                continue
    return out

def main():
    raw = sys.stdin.read()
    if not raw:
        print("No input event provided on stdin.", file=sys.stderr)
        sys.exit(2)
    try:
        event = json.loads(raw)
    except Exception as e:
        print("Invalid JSON on stdin:", e, file=sys.stderr)
        sys.exit(3)

    ledger_events = read_ledger(LEDGER)
    # compute pivot candidates: last ledger events + this event
    history = ledger_events + [event]
    pivot = calculate_piv(history)
    # inject into outgoing event under 'piv' field (optional object)
    enriched = dict(event)
    enriched["piv"] = pivot
    # print single-line JSON suitable for append to ledger
    print(json.dumps(enriched, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
