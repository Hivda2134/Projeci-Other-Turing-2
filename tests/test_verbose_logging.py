import pytest
import subprocess

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
    assert "resonance_echo" in result.stdout
    assert "Silent code, unseen," in result.stdout


