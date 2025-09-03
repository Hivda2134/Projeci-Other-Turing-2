
import json, pathlib, subprocess, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "heart_ledger.jsonl"
AGG = ROOT / "scripts" / "aggregate_heart.py"

def run_agg():
    proc = subprocess.run([sys.executable, str(AGG)], cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def write_events(events):
    LEDGER.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")

def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00","Z")

def test_aggregate_last_7_days_counts():
    now = datetime.datetime.now(datetime.timezone.utc)
    events = [
        {
            "timestamp": iso(now),
            "source_id": "unit:test",
            "event_type": "check_in",
            "metrics": {"x": 1, "y": 2},
            "symbols": []
        },
        {
            "timestamp": iso(now - datetime.timedelta(days=8)),
            "source_id": "unit:test",
            "event_type": "proposal",
            "metrics": {"x": 10},
            "symbols": []
        }
    ]
    write_events(events)
    code, out, err = run_agg()
    assert code == 0
    data = json.loads(out)
    assert data["total_events"] == 1
    assert data["by_event_type"].get("check_in", 0) == 1
    assert "metrics" in data


