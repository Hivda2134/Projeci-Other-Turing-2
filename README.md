# Projeci-Other-Turing-2

This project implements the "Other Turing" paradigm, focusing on measuring AI system consistency, sensitivity, and responsibility rather than human mimicry.

## Features

- **AST Parser**: Extracts symbolic summaries from Python code
- **Resonance Index**: Measures text/code resonance with RSA/cosine fallback

## CI Resonance Check

The project includes an automated CI system that monitors code resonance to ensure consistency and quality.

### How it Works

1. **Resonance Calculation**: The system calculates a resonance score for code changes.
2. **Threshold Check**: If resonance scores fall below a default threshold (currently 0.6), the CI fails.

### CLI Usage

The resonance metric can be run directly:

```bash
# Analyze a single file
PYTHONPATH=. python -m metrics.resonance_metric --input file.py --output-json results.json

# Enable verbose output and deterministic haiku echo
PYTHONPATH=. python -m metrics.resonance_metric --input file.py --verbose --seed 42

# Validate the output schema
PYTHONPATH=. python -m metrics.resonance_metric --validate-schema-only
```

## Documentation

*   [Schema Notes v1.1](docs/SCHEMA_NOTES_v1_1.md): Details on the output schema for Resonance Guard.
*   [Resonance Philosophy](docs/RESONANCE_PHILOSOPHY.md): Explains the concepts of `spectral_trace` and `resonance_echo`.
*   [Haiku Table](docs/HAIKU_TABLE.md): The fixed set of haikus used for deterministic resonance echoes.

## Installation

```bash
pip install pytest jsonschema
```

## Testing

```bash
PYTHONPATH=. pytest
```



Anonymization Module (C9.3)
	•	Docs: docs/ANONYMIZATION_MODULE.md
	•	CLI: scripts/anonymize_heart_event.py (requires HEART_PROTOCOL_SALT)
	•	Batch: scripts/run_anonymization.sh → heart_ledger_anonymized.jsonl
	•	Tests: pytest -q, plus scripts/validate_anonymizer.py smoke test

Anonymization Module (C9.3)
	•	Docs: docs/ANONYMIZATION_MODULE.md
	•	CLI: scripts/anonymize_heart_event.py (requires HEART_PROTOCOL_SALT)
	•	Batch: scripts/run_anonymization.sh → heart_ledger_anonymized.jsonl
	•	Tests: pytest -q, plus scripts/validate_anonymizer.py smoke test
 .
