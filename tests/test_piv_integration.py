#!/usr/bin/env python3
import json, subprocess, tempfile, pathlib
HERE = pathlib.Path.cwd()

def run_wrapper_with_ledger(ledger_events, input_event):
    ledger_file = HERE / "ci_artifacts" / "test_ledger.jsonl"
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    ledger_file.write_text("\n".join(json.dumps(e) for e in ledger_events)+"\n", encoding="utf-8")
    env = dict(**{"HEART_LEDGER_PATH": str(ledger_file)}, **{})
    proc = subprocess.run(
        ["python3", "scripts/heartbeat_with_piv.py"],
        input=json.dumps(input_event).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    assert proc.returncode == 0, f"wrapper failed: {proc.stderr.decode()}"
    out = json.loads(proc.stdout.decode())
    assert "piv" in out
    return out

def test_wrapper_injects_piv():
    ledger = [
        {"event_type":"proposal"},
        {"event_type":"filter"},
        {"event_type":"synthesis"},
    ]
    ev = {"event_type":"check_in", "agent":"test"}
    out = run_wrapper_with_ledger(ledger, ev)
    assert "piv" in out
    assert "piv_hash" in out["piv"]
