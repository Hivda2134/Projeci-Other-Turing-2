
#!/usr/bin/env python3
import sys, json, pathlib, datetime, statistics

LEDGER = pathlib.Path("heart_ledger.jsonl")

def parse_lines(p: pathlib.Path):
    if not p.exists():
        return []
    items = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception as e:
            # skip malformed lines; validator should catch in CI
            print(f"Warning: skip line {n}: {e}", file=sys.stderr)
    return items

def in_last_days(ts: str, days: int) -> bool:
    try:
        dt = datetime.datetime.fromisoformat(ts.replace("Z","+00:00"))
    except Exception:
        return False
    return dt >= (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7))

def main():
    data = parse_lines(LEDGER)
    week = [x for x in data if isinstance(x, dict) and "timestamp" in x and in_last_days(x["timestamp"], 7)]
    count = len(week)
    event_types = {}
    for x in week:
        et = x.get("event_type", "unknown")
        event_types[et] = event_types.get(et, 0) + 1
    # metrics summary (best-effort on numeric values)
    def collect_metric(name):
        vals = []
        for x in week:
            m = x.get("metrics", {})
            v = m.get(name)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        return vals
    keys = set()
    for x in week:
        if isinstance(x.get("metrics"), dict):
            keys.update(x["metrics"].keys())
    metrics_summary = {}
    for k in sorted(keys):
        vals = collect_metric(k)
        if vals:
            metrics_summary[k] = {
                "count": len(vals),
                "mean": sum(vals)/len(vals),
                "median": statistics.median(vals),
                "min": min(vals),
                "max": max(vals)
            }
    out = {
        "range": "last_7_days",
        "total_events": count,
        "by_event_type": event_types,
        "metrics": metrics_summary,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    pathlib.Path("ci_artifacts").mkdir(exist_ok=True, parents=True)
    pathlib.Path("ci_artifacts/heart_weekly_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())


