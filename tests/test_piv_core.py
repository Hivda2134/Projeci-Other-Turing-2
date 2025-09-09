#!/usr/bin/env python3
import json
from lamutual_project.piv_core import calculate_piv

def test_piv_determinism():
    events = [
        {"event_type":"proposal"},
        {"event_type":"filter"},
        {"event_type":"synthesis"},
        {"event_type":"proposal"},
        {"event_type":"check_in"},
    ]
    a = calculate_piv(events)
    b = calculate_piv(events.copy())
    assert a == b

def test_piv_change_on_event_change():
    base = [
        {"event_type":"proposal"},
        {"event_type":"filter"},
        {"event_type":"synthesis"},
        {"event_type":"proposal"},
        {"event_type":"check_in"},
    ]
    a = calculate_piv(base)
    # change one event_type
    base[2]["event_type"] = "synthesis_modified"
    b = calculate_piv(base)
    assert a != b
