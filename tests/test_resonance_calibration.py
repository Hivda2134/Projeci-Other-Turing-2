import json
import os
import pytest
from typing import Union
from ..scripts.calibrate_resonance import calibrate_resonance


def test_calibrate_resonance(tmp_path):
    # Create a dummy samples directory and files for testing
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    (samples_dir / "sample1.py").write_text("def func1():\n    pass")
    (samples_dir / "sample2.py").write_text("class ClassA:\n    pass")

    calibration_data = calibrate_resonance(str(samples_dir), num_permutations=5) # Use fewer permutations for faster test

    # Assert that calibration.json would be created (though we don't write it in the test function itself)
    # The script writes it if run as main, but here we just check the returned data.
    assert "score_distribution" in calibration_data
    assert "suggested_alert_threshold" in calibration_data
    assert "aligned_average" in calibration_data
    assert "mismatched_average" in calibration_data

    # Assert threshold is within [0.5, 0.7]
    threshold = calibration_data["suggested_alert_threshold"]
    assert 0.5 <= threshold <= 0.7

    # Test that aligned scores are generally high and mismatched are lower
    for score in calibration_data["score_distribution"]["aligned"]:
        assert score > 0.9 # Aligned should be very high
    for score in calibration_data["score_distribution"]["mismatched"]:
        assert score < 0.8 # Mismatched should be lower


