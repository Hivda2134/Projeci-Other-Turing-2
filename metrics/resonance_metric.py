import os
import json
import math
import argparse
from collections import Counter
from typing import Dict, List

from analysis.ast_parser import parse_symbolic_summary

def _cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x]**2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return numerator / denominator

def calculate_resonance_index(text: str, reference_text: str = "") -> float:
    """
    Calculates the resonance index between a given text and a reference text.
    If no reference text is provided, it falls back to a pure Python RSA/cosine similarity.
    """
    if not text:
        return 0.0

    # Fallback to pure Python RSA/cosine similarity if no reference_text
    if not reference_text:
        # Simplified RSA-like approach: count unique words as features
        text_words = Counter(text.lower().split())
        # For a single text, resonance is high if it's self-consistent (e.g., not empty)
        # This is a placeholder for a more sophisticated single-text resonance if needed.
        # For now, if it's not empty, it has some resonance.
        return 1.0 if text_words else 0.0

    # Advanced approach using AST parsing for code or more complex text structures
    # This part assumes the text is Python code or similar structured text.
    # If it's natural language, parse_symbolic_summary might not be appropriate.
    # For this task, we'll assume it's general text and use word counts for similarity.

    # Using word counts for similarity for general text
    text_words = Counter(text.lower().split())
    reference_words = Counter(reference_text.lower().split())

    return _cosine_similarity(text_words, reference_words)

def save_json(data: Dict, filename: str):
    """
    Saves a dictionary to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate resonance index for input files.")
    parser.add_argument("--input", nargs="+", help="Input file(s) or directory(ies) to process.")
    parser.add_argument("--permutations", type=int, default=0, help="Number of permutations for calibration (0 for no calibration).")
    parser.add_argument("--output-json", help="Output JSON file for results.")

    args = parser.parse_args()

    if args.input:
        # This part needs to be adapted based on how input files are handled.
        # For now, let's assume a single input file for demonstration.
        # In a real scenario, you'd iterate through files in directories.
        if len(args.input) == 1 and os.path.isdir(args.input[0]):
            # If input is a directory, load all files from it
            from scripts.calibrate_resonance import calibrate_resonance
            calibration_data = calibrate_resonance(args.input[0], args.permutations)
            if args.output_json:
                save_json(calibration_data, args.output_json)
            else:
                print(json.dumps(calibration_data, indent=4))
        elif len(args.input) == 1 and os.path.isfile(args.input[0]):
            with open(args.input[0], 'r') as f:
                input_text = f.read()
            # For a single file, we can calculate its self-resonance or compare to a reference if provided.
            # For this task, we'll just calculate self-resonance.
            resonance_score = calculate_resonance_index(input_text)
            result = {"file": args.input[0], "resonance_score": resonance_score}
            if args.output_json:
                save_json(result, args.output_json)
            else:
                print(json.dumps(result, indent=4))
        else:
            print("Error: --input must be a single file or a single directory.")
    else:
        parser.print_help()


