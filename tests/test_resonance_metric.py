import pytest
from metrics.resonance_metric import calculate_resonance_index, save_json
import os
import json

# Happy-path test
def test_calculate_resonance_index_happy_path():
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A quick brown fox jumps over a lazy dog."
    # Expect high similarity for similar texts
    assert calculate_resonance_index(text1, text2) > 0.6

# Mismatch test
def test_calculate_resonance_index_mismatch():
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "The cat sat on the mat."
    # Expect low similarity for dissimilar texts
    assert calculate_resonance_index(text1, text2) < 0.5

# No-text cases
def test_calculate_resonance_index_no_text():
    assert calculate_resonance_index("", "") == 0.0
    assert calculate_resonance_index("hello", "") == 1.0 # Fallback case
    assert calculate_resonance_index("", "world") == 0.0

# Test save_json function
def test_save_json(tmp_path):
    data = {"key": "value", "number": 123}
    filename = tmp_path / "test.json"
    save_json(data, filename)
    assert os.path.exists(filename)
    with open(filename, "r") as f:
        loaded_data = json.load(f)
    assert loaded_data == data


