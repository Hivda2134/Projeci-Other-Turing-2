# Anonymization Module (C9.3)

**Goal**  
Provide a minimal, deterministic, and privacy-preserving way to replace `source_id` with an anonymous identifier using a salted HMAC-SHA256. This enables analysis on aggregated data without exposing sensitive identifiers.

---

## Components

- `scripts/anonymize_heart_event.py`  
  CLI + library function. Reads **one** JSON event from `stdin`, returns JSON with `anonymous_id` (and without `source_id`).  
  Requires env var `HEART_PROTOCOL_SALT`.

- `scripts/run_anonymization.sh`  
  Batch helper. Reads `heart_ledger.jsonl` line-by-line and writes `heart_ledger_anonymized.jsonl`.  
  If `HEART_PROTOCOL_SALT` is missing, it generates a **temporary** salt for the run (for local testing only).

- `tests/test_anonymize_heart_event.py`  
  Unit tests for determinism, salt handling, and CLI behavior.

- `scripts/validate_anonymizer.py`  
  Smoke test for CI: runs the CLI with an ephemeral salt and validates output shape.

---

## Security & Privacy Model (MVP)

- **Deterministic mapping**: same `(source_id, salt)` → same `anonymous_id`.  
- **Salt secrecy**: the salt must be stored securely (e.g., as a secret in CI or a local `.env`).  
- **No reversible mapping**: without the salt, recovering `source_id` from `anonymous_id` is infeasible.
- **Scope**: only `source_id` is transformed in this MVP. Other fields remain untouched.

> ⚠️ Never commit the real salt to the repository. Treat it like a password.

---

## CLI Usage

### One event (stdin → stdout)
```bash
export HEART_PROTOCOL_SALT="your-secret-salt"
echo '{"source_id":"user-123","value":1}' | python3 scripts/anonymize_heart_event.py

Output (shape):

{"value":1,"anonymous_id":"<64-hex-hmac>"}

Batch mode (JSON Lines ledger)

# Uses heart_ledger.jsonl by default; writes heart_ledger_anonymized.jsonl
HEART_PROTOCOL_SALT="your-secret-salt" ./scripts/run_anonymization.sh

# Custom paths
HEART_PROTOCOL_SALT="your-secret-salt" ./scripts/run_anonymization.sh data/ledger.jsonl out/anonymized.jsonl

If HEART_PROTOCOL_SALT is not set, the wrapper generates a temporary salt and prints it to stderr (for local tests only).

⸻

Testing

Unit tests

python -m pip install -U pip pytest
pytest -q

Smoke test

python3 scripts/validate_anonymizer.py

Manual sanity check

export HEART_PROTOCOL_SALT="same-salt"
echo '{"source_id":"A"}' | python3 scripts/anonymize_heart_event.py > /tmp/a.json
echo '{"source_id":"A"}' | python3 scripts/anonymize_heart_event.py > /tmp/b.json
diff /tmp/a.json /tmp/b.json  # should be identical

⸻

Operational Guidance
	•	Where to run: Prefer running anonymization before sharing logs outside the secure workspace.
	•	Rotation: If you rotate the salt, you break cross-time linkage (privacy ↑, continuity ↓). Choose intentionally.
	•	Future extensions:
	•	Support Base64 output (shorter tokens).
	•	Hash other quasi-identifiers (configurable field list).
	•	Per-tenant/per-environment salt derivation.

⸻

Troubleshooting
	•	ERROR: environment variable HEART_PROTOCOL_SALT is not set.
→ Set export HEART_PROTOCOL_SALT="..." or use the wrapper which can generate a temporary salt.
	•	ledger file 'X' not found
→ Pass correct path: ./scripts/run_anonymization.sh path/to/ledger.jsonl out.jsonl.
	•	Non-UTF8 or malformed JSON lines
→ Clean/validate the ledger before running batch anonymization.
