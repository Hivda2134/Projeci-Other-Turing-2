import json
import os
import unittest
import jsonschema

class TestMetricsSchemaV1_2(unittest.TestCase):

    def setUp(self):
        # Construct the absolute path to the schema file
        self.schema_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "schemas", "metrics_v1_2.schema.json"
        )
        with open(self.schema_path, "r") as f:
            self.schema = json.load(f)

    def test_valid_full_output(self):
        """Test a valid output with all fields populated."""
        valid_data = {
            "metrics_version": "1.2",
            "overall": {
                "score": 0.85,
                "threshold_used": 0.6,
                "threshold_source": "CLI_or_Default",
                "resonance_echo": "Silent code, unseen...",
                "processing_time_ms": 1234.5,
                "status": "ok",
                "spectral_trace": "All files processed successfully."
            },
            "files": [
                {
                    "path": "src/main.py",
                    "score": 0.9,
                    "status": "ok",
                    "spectral_trace": "Resonance calculated using provided reference text.",
                    "size_bytes": 1024,
                    "parse_time_ms": 50.1
                },
                {
                    "path": "src/utils.py",
                    "score": 0.8,
                    "status": "ok",
                    "spectral_trace": "Resonance calculated using provided reference text.",
                    "size_bytes": 512,
                    "parse_time_ms": 25.0
                }
            ]
        }
        try:
            jsonschema.validate(instance=valid_data, schema=self.schema)
        except jsonschema.ValidationError as e:
            self.fail(f"Validation failed unexpectedly:\n{e}")

    def test_valid_budget_exceeded_status(self):
        """Test a valid output where the budget was exceeded."""
        budget_exceeded_data = {
            "metrics_version": "1.2",
            "overall": {
                "score": 0.0,
                "threshold_used": 0.6,
                "threshold_source": "Config_File",
                "resonance_echo": "A digital echo...",
                "processing_time_ms": 10.0,
                "status": "budget_exceeded",
                "spectral_trace": "Processing skipped due to file count budget (500) exceeded."
            },
            "files": []
        }
        try:
            jsonschema.validate(instance=budget_exceeded_data, schema=self.schema)
        except jsonschema.ValidationError as e:
            self.fail(f"Validation failed unexpectedly:\n{e}")

    def test_invalid_metrics_version(self):
        """Test that an invalid metrics_version is rejected."""
        invalid_data = {
            "metrics_version": "1.1", # Invalid version
            "overall": {
                "score": 0.85,
                "threshold_used": 0.6,
                "threshold_source": "CLI_or_Default",
                "resonance_echo": "Silent code, unseen...",
                "processing_time_ms": 1234.5,
                "status": "ok",
                "spectral_trace": "All files processed successfully."
            },
            "files": []
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_data, schema=self.schema)

    def test_missing_required_overall_property(self):
        """Test that missing a required property in 'overall' is rejected."""
        invalid_data = {
            "metrics_version": "1.2",
            "overall": {
                "score": 0.85,
                "threshold_used": 0.6,
                # "threshold_source" is missing
                "resonance_echo": "Silent code, unseen...",
                "processing_time_ms": 1234.5,
                "status": "ok",
                "spectral_trace": "All files processed successfully."
            },
            "files": []
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_data, schema=self.schema)

    def test_invalid_file_status(self):
        """Test that an invalid status in a file object is rejected."""
        invalid_data = {
            "metrics_version": "1.2",
            "overall": {
                "score": 0.85,
                "threshold_used": 0.6,
                "threshold_source": "CLI_or_Default",
                "resonance_echo": "Silent code, unseen...",
                "processing_time_ms": 1234.5,
                "status": "ok",
                "spectral_trace": "All files processed successfully."
            },
            "files": [
                {
                    "path": "src/main.py",
                    "score": 0.9,
                    "status": "file_is_sad", # Invalid status
                    "spectral_trace": "Resonance calculated using provided reference text.",
                    "size_bytes": 1024,
                    "parse_time_ms": 50.1
                }
            ]
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_data, schema=self.schema)

    def test_negative_processing_time(self):
        """Test that a negative processing_time_ms is rejected."""
        invalid_data = {
            "metrics_version": "1.2",
            "overall": {
                "score": 0.85,
                "threshold_used": 0.6,
                "threshold_source": "CLI_or_Default",
                "resonance_echo": "Silent code, unseen...",
                "processing_time_ms": -100, # Invalid time
                "status": "ok",
                "spectral_trace": "All files processed successfully."
            },
            "files": []
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_data, schema=self.schema)

if __name__ == "__main__":
    unittest.main()
