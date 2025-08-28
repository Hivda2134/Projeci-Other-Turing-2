
#!/usr/bin/env python3
import sys, json, pathlib
try:
    import jsonschema
    from jsonschema import FormatChecker
except ImportError:
    print("Error: jsonschema is not installed. Please run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

SCHEMA_PATH = pathlib.Path("scripts/heartbeat_log_schema.json")
LEDGER_PATH = pathlib.Path("heart_ledger.jsonl")

def load_schema():
    if not SCHEMA_PATH.exists():
        print(f"Schema not found at {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(1)
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

def validate_stream(stream, schema) -> bool:
    checker = FormatChecker()
    for n, line in enumerate(stream, 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            jsonschema.validate(instance=obj, schema=schema, format_checker=checker)
        except Exception as e:
            print(f"Validation Error on line {n}: {e}", file=sys.stderr)
            return False
    return True

def main():
    if not LEDGER_PATH.exists():
        print(f"{LEDGER_PATH} not found.", file=sys.stderr)
        sys.exit(1)
    schema = load_schema()
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        ok = validate_stream(f, schema)
    if not ok:
        print("Ledger validation failed.", file=sys.stderr)
        sys.exit(1)
    print("Ledger validation successful.")
    sys.exit(0)

if __name__ == "__main__":
    main()


