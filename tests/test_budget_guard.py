import pytest
import subprocess
import json
import os

OUTPUT_JSON = "budget_output.json"

@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)
    yield
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)

def run_metric_and_get_output(args):
    command = [
        "python", "-m", "metrics.resonance_metric",
        "--output-json", OUTPUT_JSON,
    ] + args
    process = subprocess.run(command, capture_output=True, text=True)
    
    # Check if output JSON was created, even on non-zero exit
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            return process.returncode, json.load(f)
    else:
        return process.returncode, None

def test_file_count_budget_exceeded():
    returncode, result = run_metric_and_get_output(["--input", "samples", "--max-file-count", "2"])
    assert returncode == 1 # EXIT_WARNING
    assert result is not None
    assert "Processing skipped due to" in result["overall"]["spectral_trace"]
    assert "file count budget" in result["overall"]["spectral_trace"]

def test_total_bytes_budget_exceeded():
    returncode, result = run_metric_and_get_output(["--input", "samples", "--max-total-bytes", "100"])
    assert returncode == 1 # EXIT_WARNING
    assert result is not None
    assert "Processing skipped due to" in result["overall"]["spectral_trace"]
    assert "total byte budget" in result["overall"]["spectral_trace"]

def test_file_size_budget_exceeded():
    dummy_file = "samples/large_dummy_file.py"
    with open(dummy_file, "w") as f:
        f.write("# This is a large file\n" * 1000)
    
    try:
        returncode, result = run_metric_and_get_output(["--input", dummy_file, "--max-file-size-bytes", "500"])
        assert returncode == 2 # Should exit with failure for budget exceeded
        assert result is not None
        assert result["files"][0]["status"] == "budget_exceeded"
        assert "File size" in result["files"][0]["spectral_trace"]
    finally:
        os.remove(dummy_file)


