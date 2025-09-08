#!/usr/bin/env python3
"""
Ghost Scanner – CI health sentinel.
Checks repository structure, schema presence, and core invariants.
"""
import sys, os, json

def check_files():
    required = [
"pyproject.toml",
        
        "heartbeat_log_schema.json",
        "scripts/piv_core.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"Missing critical files: {missing}", file=sys.stderr)
        return False
    return True

def check_json_schema():
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed", file=sys.stderr)
        return False
    if not os.path.exists("heartbeat_log_schema.json"):
        return True  # already flagged by check_files
    try:
        with open("heartbeat_log_schema.json") as f:
            schema = json.load(f)
        jsonschema.Draft7Validator.check_schema(schema)
    except Exception as e:
        print(f"Schema invalid: {e}", file=sys.stderr)
        return False
    return True

def main():
    ok = True
    if not check_files():
        ok = False
    if not check_json_schema():
        ok = False
    if not ok:
        sys.exit(1)
    print("Ghost Scanner passed.")
    return 0

if __name__ == "__main__":
    main()
