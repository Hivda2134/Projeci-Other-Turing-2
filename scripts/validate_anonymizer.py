#!/usr/bin/env python3
"""
Simple validator for the anonymizer: run a smoke test using an ephemeral salt.
Exits 0 if ok, non-zero if not.
"""
import subprocess, json, os, sys
evt = {"source_id":"smoke-test-user","x":1}
env = {**os.environ, "HEART_PROTOCOL_SALT":"smoke_salt_42"}
p = subprocess.run([sys.executable, "scripts/anonymize_heart_event.py"], input=json.dumps(evt).encode("utf-8"), env=env, capture_output=True)
if p.returncode != 0:
    sys.stderr.write("anonymizer CLI smoke test failed:\\n")
    sys.stderr.write(p.stderr.decode("utf-8"))
    raise SystemExit(2)
try:
    out = json.loads(p.stdout.decode("utf-8"))
except Exception as e:
    sys.stderr.write("anonymizer output not valid JSON: " + str(e) + "\\n")
    raise SystemExit(3)
if "anonymous_id" not in out:
    sys.stderr.write("anonymous_id missing in anonymizer output\\n")
    raise SystemExit(4)
print("anonymizer smoke test OK")


