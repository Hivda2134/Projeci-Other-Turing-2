import pytest
import json
from jsonschema import validate, ValidationError

# Define the schema directly for testing
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Resonance Metrics v1.1 Schema",
    "description": "Schema for the Resonance Guard v2-enterprise+ output.",
    "type": "object",
    "required": ["metrics_version", "overall", "files"],
    "properties": {
        "metrics_version": {
            "type": "string",
            "pattern": "^1\\.1$"
        },
        "overall": {
            "type": "object",
            "required": ["score", "threshold_used", "threshold_source", "resonance_echo"],
            "properties": {
                "score": {"type": "number"},
                "threshold_used": {"type": "number"},
                "threshold_source": {"type": "string"},
                "resonance_echo": {"type": "string"}
            },
            "additionalProperties": False
        },
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "score", "status", "spectral_trace"],
                "properties": {
                    "path": {"type": "string"},
                    "score": {"type": "number"},
                    "status": {"type": "string", "enum": ["ok", "syntax_error", "io_error", "calc_error"]},
                    "spectral_trace": {"type": "string"}
                },
                "additionalProperties": False
            }
        }
    },
            "additionalProperties": False
}

def test_valid_schema_data():
    valid_data = {
        "metrics_version": "1.1",
        "overall": {
            "score": 0.75,
            "threshold_used": 0.6,
            "threshold_source": "CLI_or_Default",
            "resonance_echo": "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void."
        },
        "files": [
            {
                "path": "dummy_file.py",
                "score": 0.8,
                "status": "ok",
                "spectral_trace": ""
            },
            {
                "path": "file2.py",
                "score": 0.5,
                "status": "syntax_error",
                "spectral_trace": "Syntax error in line 10."
            }
        ]
    }
    validate(instance=valid_data, schema=SCHEMA)

def test_invalid_schema_data_missing_required_field():
    invalid_data = {
        "metrics_version": "1.1",
        "overall": {
            "score": 0.75,
            "threshold_used": 0.6,
            "threshold_source": "CLI_or_Default",
            "resonance_echo": "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void."
        },
        "files": [
            {
                "path": "file1.py",
                "score": 0.8,
                "status": "ok",
                "spectral_trace": ""
            },
            {
                "path": "file2.py",
                "score": 0.5,
                "spectral_trace": "Syntax error in line 10."
            } # Missing status
        ]
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_data, schema=SCHEMA)

def test_invalid_schema_data_wrong_type():
    invalid_data = {
        "metrics_version": "1.1",
        "overall": {
            "score": "not a number", # Incorrect type
            "threshold_used": 0.6,
            "threshold_source": "CLI_or_Default",
            "resonance_echo": "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void."
        },
        "files": [
            {
                "path": "file1.py",
                "score": 0.8,
                "status": "ok",
                "spectral_trace": ""
            }
        ]
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_data, schema=SCHEMA)

def test_invalid_schema_data_invalid_enum_value():
    invalid_data = {
        "metrics_version": "1.1",
        "overall": {
            "score": 0.75,
            "threshold_used": 0.6,
            "threshold_source": "CLI_or_Default",
            "resonance_echo": "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void."
        },
        "files": [
            {
                "path": "file1.py",
                "score": 0.8,
                "status": "invalid_status", # Invalid enum value
                "spectral_trace": ""
            }
        ]
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_data, schema=SCHEMA)


