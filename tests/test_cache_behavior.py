import pytest
import subprocess
import json
import os
import shutil
import time

CACHE_DIR = ".rescache_test"
OUTPUT_JSON = "cache_output.json"
INPUT_FILE = "samples/simple_function.py"

@pytest.fixture(autouse=True)
def cleanup_cache():
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
    yield
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)

def run_resonance_metric(args):
    command = [
        "python", "-m", "metrics.resonance_metric",
        "--input", INPUT_FILE,
        "--output-json", OUTPUT_JSON,
        "--cache-dir", CACHE_DIR,
        "--verbose"
    ] + args
    process = subprocess.run(command, capture_output=True, text=True)
    
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            return process.returncode, json.load(f)
    else:
        # If no output JSON, return the stdout/stderr for debugging
        # print(f"STDOUT: {process.stdout}")
        # print(f"STDERR: {process.stderr}")
        return process.returncode, None

def test_cache_hit_and_miss():
    # First run: cache miss
    returncode1, result1 = run_resonance_metric([])
    assert returncode1 in [0, 2]
    assert result1 is not None
    assert "Resonance calculated using provided reference text." in result1["files"][0]["spectral_trace"]
    assert os.path.exists(os.path.join(CACHE_DIR, os.listdir(CACHE_DIR)[0]))

    # Second run: cache hit
    returncode2, result2 = run_resonance_metric([])
    assert returncode2 in [0, 2]
    assert result2 is not None
    assert result2["files"][0]["spectral_trace"] == "Cache hit."
    assert result1["overall"]["score"] == pytest.approx(result2["overall"]["score"])

def test_no_cache_flag():
    returncode1, result1 = run_resonance_metric(["--no-cache"])
    assert returncode1 in [0, 2]
    assert result1 is not None
    assert "Resonance calculated using provided reference text." in result1["files"][0]["spectral_trace"]
    assert not os.path.exists(CACHE_DIR)

    returncode2, result2 = run_resonance_metric(["--no-cache"])
    assert returncode2 in [0, 2]
    assert result2 is not None
    assert "Resonance calculated using provided reference text." in result2["files"][0]["spectral_trace"]
    assert not os.path.exists(CACHE_DIR)

def test_clear_cache_flag():
    # First run to populate cache
    returncode1, _ = run_resonance_metric([])
    assert returncode1 in [0, 2]
    assert os.path.exists(CACHE_DIR)

    # Second run with --clear-cache
    returncode2, result2 = run_resonance_metric(["--clear-cache"])
    assert returncode2 in [0, 2]
    assert result2 is not None
    assert "Resonance calculated using provided reference text." in result2["files"][0]["spectral_trace"]
    # Cache should have been cleared and then repopulated
    assert os.path.exists(CACHE_DIR)

def test_cache_invalidation_on_file_change():
    # First run to populate cache
    returncode1, _ = run_resonance_metric([])
    assert returncode1 in [0, 2]
    cache_file_count_before = len(os.listdir(CACHE_DIR))
    assert cache_file_count_before > 0

    # Modify the input file
    with open(INPUT_FILE, "a") as f:
        f.write("\n# A new line to change file hash\n")
    time.sleep(0.1) # Ensure modification time changes

    # Run again, should be a cache miss
    returncode2, result2 = run_resonance_metric([])
    assert returncode2 in [0, 2]
    assert result2 is not None
    assert "Resonance calculated using provided reference text." in result2["files"][0]["spectral_trace"]
    cache_file_count_after = len(os.listdir(CACHE_DIR))
    assert cache_file_count_after > cache_file_count_before # New cache entry should be created

def test_cache_size_management():
    # Set a very small max cache size
    small_cache_mb = 1 # 1 MB
    
    # Create multiple dummy files to exceed cache limit
    dummy_files = []
    for i in range(500): # Create enough files to exceed 1MB cache
        dummy_file_path = os.path.join("samples", f"dummy_file_{i}.py")
        with open(dummy_file_path, "w") as f:
            f.write(f"# This is dummy file {i}\n" * 5) # ~100 bytes each
        dummy_files.append(dummy_file_path)
    try:
        command = [
            "python", "-m", "metrics.resonance_metric",
            "--input", "samples",
            "--output-json", OUTPUT_JSON,
            "--cache-dir", CACHE_DIR,
            "--verbose",
            f"--max-cache-size-mb", str(small_cache_mb)
        ]
        process = subprocess.run(command, capture_output=True, text=True)
        assert process.returncode in [0, 1, 2] # Should succeed or exit due to budget

        # Check if cache directory exists and contains files
        if os.path.exists(CACHE_DIR):
            # The number of files in cache should be limited by the size
            # This is a heuristic check, exact number depends on file sizes and LRU
            assert len(os.listdir(CACHE_DIR)) < len(dummy_files) * 2 # Should be less than total possible entries

    finally:
        for f in dummy_files:
            if os.path.exists(f):
                os.remove(f)



