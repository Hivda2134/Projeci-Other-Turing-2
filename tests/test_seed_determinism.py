import pytest
import subprocess
import os
import json

def test_seed_determinism():
    # Define a temporary file to store the output of the script
    output_file = "temp_output.json"

    # Run the script twice with the same seed and input
    command = ["python", "-m", "metrics.resonance_metric", "--input", "samples/add_ok.py", "--seed", "123", "--output-json", output_file]

    # First run
    subprocess.run(command, check=True)
    with open(output_file, "r") as f:
        first_run_output = json.load(f)

    # Second run
    subprocess.run(command, check=True)
    with open(output_file, "r") as f:
        second_run_output = json.load(f)

    # Assert that the outputs are identical
    assert first_run_output == second_run_output

    # Clean up the temporary file
    os.remove(output_file)


