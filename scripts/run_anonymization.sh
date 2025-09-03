#!/usr/bin/env bash
set -euo pipefail

# Usage:
# HEART_PROTOCOL_SALT=... ./scripts/run_anonymization.sh [ledger_file] [out_file]
# If HEART_PROTOCOL_SALT is not set, a temporary test salt is generated for this run (printed to stderr).

LEDGER="${1:-heart_ledger.jsonl}"
OUT="${2:-heart_ledger_anonymized.jsonl}"

if [ ! -f "$LEDGER" ]; then
  echo "ERROR: ledger file '$LEDGER' not found." >&2
  exit 2
fi

if [ -z "${HEART_PROTOCOL_SALT:-}" ]; then
  echo "WARNING: HEART_PROTOCOL_SALT not set. Generating a temporary salt for this run." >&2
  HEART_PROTOCOL_SALT="$(python3 - <<'PY
import secrets
print(secrets.token_hex(16))
PY
)"
  export HEART_PROTOCOL_SALT
  echo "Generated temporary HEART_PROTOCOL_SALT (for this run only): $HEART_PROTOCOL_SALT" >&2
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUT")"
: > "$OUT"

while IFS= read -r line || [ -n "$line" ]; do
  # Skip empty lines
  if [ -z "$line" ]; then
    continue
  fi
  # Feed line into python anonymizer
  echo "$line" | python3 scripts/anonymize_heart_event.py >> "$OUT"
done < "$LEDGER"

echo "Anonymized ledger written to: $OUT" >&2
exit 0


