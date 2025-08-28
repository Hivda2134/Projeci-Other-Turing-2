
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "heart_ledger.jsonl"
VALIDATOR = ROOT / "scripts" / "validate_heart.py"

def run_validator():
    proc = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def write_lines(lines):
    LEDGER.write_text("\n".join(lines) + "\n", encoding="utf-8")

def test_validate_success():
    obj = {
        "timestamp": "2025-01-01T00:00:00Z",
        "source_id": "unit:test",
        "event_type": "check_in",
        "metrics": {"f1_data_density": 0.7},
        "symbols": ["ok"]
    }
    write_lines([json.dumps(obj)])
    code, out, err = run_validator()
    assert code == 0, f"Expected success, got {code}, stderr={err}"

def test_validate_failure_missing_required():
    obj = {
        "timestamp": "2025-01-01T00:00:00Z",
        "source_id": "unit:test",
        "event_type": "check_in",
        "metrics": {}
    }
    write_lines([json.dumps(obj)])
    code, out, err = run_validator()
    assert code != 0, "Expected failure due to missing \'symbols\'"

def test_validate_ignores_blank_lines():
    obj = {
        "timestamp": "2025-01-01T00:00:00Z",
        "source_id": "unit:test",
        "event_type": "check_in",
        "metrics": {},
        "symbols": []
    }
    write_lines(["", json.dumps(obj), ""])
    code, out, err = run_validator()
    assert code == 0


