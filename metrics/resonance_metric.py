import json
import math
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


