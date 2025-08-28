
#!/usr/bin/env python3
import sys, json, pathlib
try:
    import jsonschema
    from jsonschema import FormatChecker
except ImportError:
    print("Error: jsonschema is not installed. Please run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

SCHEMA = {
    "type": "object",
    "required": ["timestamp", "source_id", "event_type", "metrics", "symbols"],
    "properties": {
        "timestamp": {"type": "string", "format": "date-time"},
        "source_id": {"type": "string"},
        "event_type": {"type": "string"},
        "metrics": {"type": "object"},
        "symbols": {"type": "array", "items": {"type": "string"}},
        "manifesto_snippet": {"type": "string"},
        "notes": {"type": "string"}
    },
    "additionalProperties": True
}

def validate(stream) -> bool:
    checker = FormatChecker()
    for n, line in enumerate(stream, 1):
        line = line.strip()
        if not line:
            # allow blank lines
            continue
        try:
            obj = json.loads(line)
            jsonschema.validate(instance=obj, schema=SCHEMA, format_checker=checker)
        except Exception as e:
            print(f"Validation Error on line {n}: {e}", file=sys.stderr)
            return False
    return True

def main():
    path = pathlib.Path("heart_ledger.jsonl")
    if not path.exists():
        print("heart_ledger.jsonl not found.", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        ok = validate(f)
    if not ok:
        print("Ledger validation failed.", file=sys.stderr)
        sys.exit(1)
    print("Ledger validation successful.")
    sys.exit(0)

if __name__ == "__main__":
    main()


