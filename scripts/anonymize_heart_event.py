#!/usr/bin/env python3
"""
anonymize_heart_event.py

MVP anonymizer: reads a single JSON line from stdin, replaces 'source_id'
with a deterministic salted HMAC-SHA256 'anonymous_id', and writes JSON to stdout.

Behavior:
- Requires environment variable HEART_PROTOCOL_SALT to be set.
- If HEART_PROTOCOL_SALT is missing, exits with code 2 and a descriptive error.
- The module exposes anonymize_event(dict, salt) for unit testing and reuse.
"""

from __future__ import annotations
import os
import sys
import json
import hmac
import hashlib
from typing import Dict, Any

ENV_SALT = "HEART_PROTOCOL_SALT"


def anonymize_event(event: Dict[str, Any], salt: str) -> Dict[str, Any]:
    """
    Replace 'source_id' with 'anonymous_id' computed as HMAC-SHA256(salt, source_id).
    If 'source_id' not present, returns event unchanged.
    The function does not mutate the input dict (returns a new dict).
    """
    out = dict(event)  # shallow copy
    source = out.pop("source_id", None)
    if source is None:
        return out
    # Ensure deterministic encoding
    if not isinstance(source, (str, bytes)):
        source = json.dumps(source, sort_keys=True, ensure_ascii=False)
    if isinstance(source, str):
        source_bytes = source.encode("utf-8")
    else:
        source_bytes = source
    salt_bytes = salt.encode("utf-8")
    digest = hmac.new(salt_bytes, source_bytes, hashlib.sha256).hexdigest()
    out["anonymous_id"] = digest
    return out


def _read_stdin_one() -> str:
    """
    Read a single JSON line from stdin. If multiple lines are present,
    read entire stdin and process as one JSON text.
    """
    data = sys.stdin.read()
    if not data:
        return ""
    return data.strip()


def main() -> int:
    salt = os.environ.get(ENV_SALT)
    if not salt:
        sys.stderr.write(f"ERROR: environment variable {ENV_SALT} is not set.\n")
        return 2
    raw = _read_stdin_one()
    if not raw:
        sys.stderr.write("ERROR: no input found on stdin (expected a single JSON line).\n")
        return 3
    try:
        event = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"ERROR: could not parse JSON from stdin: {e}\n")
        return 4
    out = anonymize_event(event, salt)
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


