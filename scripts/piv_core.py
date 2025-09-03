import hashlib
import json
from typing import List, Dict

def calculate_piv(events: List[Dict]) -> Dict:
    """
    Calculate a simple Persistent Identity Vector (PIV).
    For MVP: hash of the last 5 event_type values (deterministic).
    """
    if not events:
        return {"piv_hash": None}

    last_events = events[-5:]
    event_types = [e.get("event_type", "") for e in last_events]
    joined = "|".join(event_types)
    piv_hash = hashlib.sha256(joined.encode("utf-8")).hexdigest()

    return {"piv_hash": piv_hash}

if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, list):
            raise ValueError("Input must be a list of events")
        piv = calculate_piv(data)
        print(json.dumps(piv))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
