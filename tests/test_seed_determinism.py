import pytest
import subprocess
import os
import json

def remove_non_deterministic_fields(data):
    if "overall" in data and "processing_time_ms" in data["overall"]:
        del data["overall"]["processing_time_ms"]
    if "files" in data:
        for file_data in data["files"]:
            if "parse_time_ms" in file_data:
                del file_data["parse_time_ms"]
    return data

def test_seed_determinism():
    # Define a temporary file to store the output of the script
    output_file = "temp_output.json"

    # Run the script twice with the same seed and input
    command = ["python", "-m", "metrics.resonance_metric", "--input", "samples/add_ok.py", "--seed", "123", "--output-json", output_file]

    # First run
    process1 = subprocess.run(command, capture_output=True, text=True)
    assert process1.returncode in [0, 2]
    with open(output_file, "r") as f:
        first_run_output = json.load(f)

    # Second run
    process2 = subprocess.run(command, capture_output=True, text=True)
    assert process2.returncode in [0, 2]
    with open(output_file, "r") as f:
        second_run_output = json.load(f)

    # Remove non-deterministic fields before comparison
    first_run_output = remove_non_deterministic_fields(first_run_output)
    second_run_output = remove_non_deterministic_fields(second_run_output)

    # Assert that the outputs are identical
    assert first_run_output == second_run_output

    # Clean up the temporary file
    os.remove(output_file)


