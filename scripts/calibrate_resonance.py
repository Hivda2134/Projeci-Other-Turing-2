import json
import os
import random
from collections import Counter
from typing import Dict, List, Tuple

from analysis.ast_parser import parse_symbolic_summary
from metrics.resonance_metric import calculate_resonance_index

def _load_samples(directory: str) -> Dict[str, str]:
    samples = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                samples[filename] = f.read()
    return samples

def _generate_mismatched_sample(original_code: str) -> str:
    # Simple permutation: shuffle lines or replace keywords
    lines = original_code.split("\n")
    random.shuffle(lines)
    mismatched_code = "\n".join(lines)
    # Replace common keywords to further reduce resonance
    replacements = {"def": "func", "class": "type", "import": "bring"}
    for old, new in replacements.items():
        mismatched_code = mismatched_code.replace(old, new)
    return mismatched_code

def calibrate_resonance(samples_dir: str, num_permutations: int = 200) -> Dict:
    samples = _load_samples(samples_dir)
    scores = {"aligned": [], "mismatched": []}

    for name, code in samples.items():
        # Aligned samples: compare code with itself (should be 1.0)
        scores["aligned"].append(calculate_resonance_index(code, code)["score"])

        # Mismatched samples: compare original code with permuted versions
        for _ in range(num_permutations):
            mismatched_code = _generate_mismatched_sample(code)
            scores["mismatched"].append(calculate_resonance_index(code, mismatched_code)["score"])

    # Calculate score distribution and suggest alert_threshold
    aligned_avg = sum(scores["aligned"]) / len(scores["aligned"])
    mismatched_avg = sum(scores["mismatched"]) / len(scores["mismatched"]) if scores["mismatched"] else 0.0

    # A simple heuristic for threshold: midpoint between mismatched_avg and aligned_avg
    # Or, a percentile of mismatched scores that ensures most aligned scores are above it.
    # For now, let's use a simple average, or a fixed value if averages are too close.
    alert_threshold = (aligned_avg + mismatched_avg) / 2.0
    # Ensure the threshold is within the desired range [0.5, 0.7]
    alert_threshold = max(0.5, min(0.7, alert_threshold))
    if abs(aligned_avg - mismatched_avg) < 0.1: # If averages are too close, use a default
        alert_threshold = 0.6 # A reasonable default for code similarity

    return {
        "score_distribution": scores,
        "suggested_alert_threshold": alert_threshold,
        "aligned_average": aligned_avg,
        "mismatched_average": mismatched_avg,
    }

if __name__ == "__main__":
    # This part would typically be run via CLI or a separate script
    # For direct execution, you might pass a samples directory.
    # Example: python scripts/calibrate_resonance.py samples/
    import sys
    if len(sys.argv) > 1:
        calibration_data = calibrate_resonance(sys.argv[1])
        output_file = "calibration.json"
        with open(output_file, "w") as f:
            json.dump(calibration_data, f, indent=4)
        print(f"Calibration data saved to {output_file}")
    else:
        print("Usage: python scripts/calibrate_resonance.py <samples_directory>")


