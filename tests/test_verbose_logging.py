import pytest
import subprocess
import json
import os

def test_verbose_logging_resonance_echo():
    # Invoke the real module to ensure verbose run emits JSON containing resonance_echo
    # Use seed=10 so that (seed % len(HAIKUS)) == 0 given 10 entries
    command = [
        "python", "-m", "metrics.resonance_metric",
        "--input", "samples/add_ok.py",
        "--verbose",
        "--seed", "10"
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    # Should print JSON to stdout (since no --output-json was passed)
    assert result.returncode in (0, 1, 2)  # depending on threshold, but process should complete
    
    # Check if the expected haiku is present in the output
    # The haiku for seed 10 (10 % 10 = 0) is the first one in the HAIKUS list.
    # Assuming HAIKUS list is consistent with metrics/resonance_metric.py
    expected_haiku_start = "Silent code, unseen,"
    assert expected_haiku_start in result.stdout



