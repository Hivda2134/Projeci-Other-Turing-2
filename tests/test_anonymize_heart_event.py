#!/usr/bin/env python3
import os
import json
import subprocess
import tempfile
import sys
import pytest

# Import the anonymize_event function for direct unit testing
from scripts.anonymize_heart_event import anonymize_event

SALT_A = "test_salt_a"
SALT_B = "test_salt_b"


def test_anonymize_creates_anonymous_id_and_is_deterministic():
    event = {"source_id": "user-123", "value": 1}
    out1 = anonymize_event(event, SALT_A)
    out2 = anonymize_event(event, SALT_A)
    assert "anonymous_id" in out1
    assert out1["anonymous_id"] == out2["anonymous_id"]
    assert out1["anonymous_id"] != anonymize_event({"source_id": "user-456"}, SALT_A)["anonymous_id"]


def test_different_salts_produce_different_hashes():
    event = {"source_id": "user-123"}
    a = anonymize_event(event, SALT_A)["anonymous_id"]
    b = anonymize_event(event, SALT_B)["anonymous_id"]
    assert a != b


def test_script_exits_when_salt_missing(tmp_path):
    # run the CLI without HEART_PROTOCOL_SALT
    p = subprocess.run(
        [sys.executable, "scripts/anonymize_heart_event.py"],
        input=json.dumps({"source_id": "x"}).encode("utf-8"),
        capture_output=True,
    )
    assert p.returncode != 0
    assert b"ERROR: environment variable HEART_PROTOCOL_SALT is not set" in p.stderr


def test_cli_with_salt(tmp_path):
    # run the CLI with salt set and check output is valid JSON with anonymous_id
    proc = subprocess.run(
        [sys.executable, "scripts/anonymize_heart_event.py"],
        input=json.dumps({"source_id": "user-789"}).encode("utf-8"),
        env={**os.environ, "HEART_PROTOCOL_SALT": "somesalt"},
        capture_output=True,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout.decode("utf-8"))
    assert "anonymous_id" in out


