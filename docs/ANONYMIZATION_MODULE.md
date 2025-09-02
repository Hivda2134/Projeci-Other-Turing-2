# Anonymization Module (C9.3)

## Overview
This document details the implementation and usage of the anonymization module within the Heart Protocol v2. The module provides an opt-in mechanism to protect sensitive `source_id` data using salted HMAC (Hash-based Message Authentication Code).

## 1. `scripts/anonymize.py`

### Purpose
This script contains the core logic for anonymizing data fields using salted HMAC. It ensures that sensitive identifiers, such as `source_id`, are transformed into irreversible, non-traceable hashes while maintaining data integrity for analytical purposes.

### Function: `anonymize_data(data, salt, fields_to_anonymize)`
- `data` (dict): The dictionary containing the heartbeat log entry.
- `salt` (str): A unique, securely managed string used as a salt for the HMAC calculation. This salt is crucial for preventing rainbow table attacks and ensuring the uniqueness of hashes across different contexts or periods.
- `fields_to_anonymize` (list): A list of string keys representing the fields within the `data` dictionary that need to be anonymized. Currently, the primary field targeted for anonymization is `source_id`.

### How it Works
For each specified field in `fields_to_anonymize`:
1. The original value of the field is converted to a string and then encoded into bytes (UTF-8).
2. A salted HMAC-SHA256 hash is computed using the provided `salt` and the encoded original value.
3. The original value in the `data` dictionary is replaced with its hexadecimal HMAC hash representation.

### Example Usage (within other scripts)
```python
import hmac
import hashlib

from scripts.anonymize import anonymize_data

# Example heartbeat log entry
heartbeat_entry = {
    "timestamp": "2025-01-01T12:00:00Z",
    "source_id": "unique_user_identifier_123",
    "event_type": "data_submission",
    "metrics": {"value": 100},
    "symbols": ["A", "B"]
}

# A securely managed salt (e.g., from environment variables or a configuration system)
secure_salt = os.environ.get("ANONYMIZATION_SALT") # Example: retrieve from environment

if secure_salt:
    anonymized_entry = anonymize_data(heartbeat_entry, secure_salt, ["source_id"])
    print("Anonymized Entry:", anonymized_entry)
else:
    print("Warning: ANONYMIZATION_SALT not set. Data will not be anonymized.")

```

## 2. `scripts/ingest_heartbeat.py`

### Purpose
This command-line interface (CLI) tool facilitates the ingestion of heartbeat log entries into the `heart_ledger.jsonl` file. It provides an opt-in mechanism for anonymizing `source_id` data during the ingestion process.

### Usage
```bash
python3 scripts/ingest_heartbeat.py [--anonymize --salt <YOUR_SALT>] [--input_file <PATH_TO_FILE>]
```

### Arguments
- `--anonymize`: (Optional flag) If present, enables the anonymization of the `source_id` field for each ingested log entry. When this flag is used, the `--salt` argument becomes mandatory.
- `--salt <YOUR_SALT>`: (Required if `--anonymize` is used) Specifies the salt string to be used for HMAC calculation during anonymization. This salt should be kept confidential and consistent for a given anonymization context.
- `--input_file <PATH_TO_FILE>`: (Optional) Specifies the path to a JSONL (JSON Lines) file containing heartbeat log entries. If this argument is omitted, the script will read log entries from standard input (stdin).

### How it Works
1. **Input Reading**: The script reads heartbeat log entries either from a specified input file or from stdin, expecting one JSON object per line.
2. **Anonymization (Opt-in)**: If the `--anonymize` flag is provided along with a `--salt`:
   - For each valid JSON log entry, the `anonymize_data` function from `scripts/anonymize.py` is called to hash the `source_id` field.
   - If `source_id` is `None` or not present, it is skipped.
3. **Output Writing**: The processed (anonymized or original) log entries are appended to the `heart_ledger.jsonl` file.

### Error Handling
- If `--anonymize` is used without `--salt`, an error message is printed, and the script exits.
- Invalid JSON lines in the input are skipped, and an error message is printed to stderr.
- If the specified `--input_file` does not exist, an error message is printed, and the script exits.

## 3. Security Considerations
- **Salt Management**: The security of the anonymization process heavily relies on the confidentiality and uniqueness of the salt. It is critical to:
    - Use a strong, randomly generated salt.
    - Never hardcode the salt in the codebase.
    - Manage the salt securely (e.g., via environment variables, secure configuration management systems, or a dedicated secrets management service).
    - Rotate salts periodically if the threat model requires it.
- **Irreversibility**: HMAC is a one-way cryptographic hash function. Once `source_id` values are anonymized, they cannot be reversed to their original form. This ensures privacy.
- **Collision Resistance**: While HMAC is designed to be collision-resistant, it's important to understand that different original values *could* theoretically produce the same hash, especially with weak salts or very small input spaces. However, for typical `source_id` values and strong salts, this risk is negligible.

## 4. Integration and Validation
- **Schema Compatibility**: The anonymized `source_id` (a hexadecimal string) remains compatible with the `heartbeat_log_schema.json`, which expects `source_id` to be a string.
- **`validate_heart.py`**: This script will continue to validate the schema of both original and anonymized heartbeat entries without modification.
- **`aggregate_heart.py`**: The aggregation script will process the hashed `source_id` values as distinct identifiers, allowing for collective trend analysis without exposing individual `source_id`s.

## 5. Future Enhancements
- Consider adding support for anonymizing other fields based on future privacy requirements.
- Implement a salt rotation mechanism within the system.
- Explore integration with a dedicated secrets management system for salt retrieval.

