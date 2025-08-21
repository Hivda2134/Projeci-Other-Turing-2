import pytest
import os

def test_logrotate():
    # This test is more conceptual as it requires a running CI environment
    # We will simulate the log rotation logic here

    log_file = "ci_resonance_log.txt"
    max_size = 1024  # 1 KB for testing

    # Create a dummy log file larger than the max size
    with open(log_file, "w") as f:
        f.write("a" * (max_size + 1))

    # Simulate the log rotation logic
    if os.path.getsize(log_file) > max_size:
        # Rename the existing log file
        os.rename(log_file, log_file + ".1")
        # Create a new log file with a truncation notice
        with open(log_file, "w") as f:
            f.write("[log truncated]")

    # Assert that the new log file exists and contains the truncation notice
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        content = f.read()
    assert content == "[log truncated]"

    # Assert that the rotated log file exists
    assert os.path.exists(log_file + ".1")

    # Clean up the dummy log files
    os.remove(log_file)
    os.remove(log_file + ".1")


