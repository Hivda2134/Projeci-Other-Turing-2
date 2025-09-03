import pytest
from scripts.piv_core import calculate_piv

def test_deterministic_output():
    events = [{"event_type": "a"}, {"event_type": "b"}, {"event_type": "c"}]
    piv1 = calculate_piv(events)
    piv2 = calculate_piv(events)
    assert piv1 == piv2, "PIV must be deterministic for the same input"

def test_different_sequences():
    events1 = [{"event_type": "a"}, {"event_type": "b"}]
    events2 = [{"event_type": "a"}, {"event_type": "c"}]
    piv1 = calculate_piv(events1)
    piv2 = calculate_piv(events2)
    assert piv1 != piv2, "Different sequences should produce different PIVs"

def test_empty_input():
    piv = calculate_piv([])
    assert piv["piv_hash"] is None, "Empty input should yield None"
