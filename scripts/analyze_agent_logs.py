#!/usr/bin/env python3
"""
analyze_agent_logs.py

Scan agent-manus logs for:
 - ERROR/Exception occurrences
 - unusually long steps (lines containing 'duration=')
 - 'self-correct' indicators (keywords like 'corrected','fixing','asking for intent','clarify')
Usage:
  python3 scripts/analyze_agent_logs.py [logs_directory]
Default logs_directory: logs/agent
Outputs JSON summary to stdout.
"""
from __future__ import annotations
import json,sys,pathlib,re,statistics
LOG_DIR = sys.argv[1] if len(sys.argv) > 1 else "logs/agent"
p = pathlib.Path(LOG_DIR)
summary = {"files_scanned":0, "errors":{}, "exceptions":{}, "slow_entries":[],"self_corrections":[], "durations":[]}

if not p.exists():
    print(json.dumps({"error":"log directory not found", "path": str(p)}))
    sys.exit(0)

for f in sorted(p.glob("**/*.log")):
    summary["files_scanned"] += 1
    text = f.read_text(encoding="utf-8", errors="ignore")
    # count ERROR lines
    errs = re.findall(r'^(.*ERROR.*)$', text, flags=re.M)
    excs = re.findall(r'^(.*Exception:.*)$', text, flags=re.M)
    if errs:
        summary["errors"][str(f)] = len(errs)
    if excs:
        summary["exceptions"][str(f)] = len(excs)
    # durations like "duration=1234ms" or "took 1.23s"
    for m in re.finditer(r'duration\s*=\s*([0-9]+)ms', text):
        try:
            summary["durations"].append(int(m.group(1)))
            summary["slow_entries"].append({"file": str(f), "duration_ms": int(m.group(1))})
        except:
            pass
    for m in re.finditer(r'took\s+([0-9]+\.[0-9]+)s', text):
        try:
            summary["durations"].append(int(float(m.group(1))*1000))
        except:
            pass
    # self-corrections heuristics
    for kw in ["corrected","fixing","fixed","asked for clarification","asking for clarification","requesting intent","self-correct","rolled back","rollback"]:
        if kw in text.lower():
            summary["self_corrections"].append({"file": str(f), "keyword": kw})
# stats
if summary["durations"]:
    summary["duration_ms_mean"] = statistics.mean(summary["durations"])
    summary["duration_ms_max"] = max(summary["durations"])
else:
    summary["duration_ms_mean"] = 0
    summary["duration_ms_max"] = 0

print(json.dumps(summary, indent=2))
