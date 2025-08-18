# src/core_metrics.py
"""
Core metrics engine for the Λmutual project.
"""

from typing import List, Dict
import re
from math import log1p


def calculate_resonance_index(text: str, keywords: List[str]) -> float:
    """
    Measures thematic resonance by combining
    (a) keyword density and (b) keyword clustering.

    Parameters
    ----------
    text : str
        Input text to analyse.
    keywords : List[str]
        Manifesto-derived keywords/phrases.

    Returns
    -------
    float
        Resonance score ∈ [0, 1].
    """
    if not text or not keywords:
        return 0.0

    # 1. Normalise
    lower_text = text.lower()
    kw_lower = [kw.lower() for kw in keywords]

    # 2. Density
    total_kw = sum(lower_text.count(kw) for kw in kw_lower)
    density_score = min(total_kw / (len(kw_lower) * 5), 1.0)

    # 3. Clustering: average gap between consecutive keyword positions
    positions = []
    for kw in kw_lower:
        for match in re.finditer(re.escape(kw), lower_text):
            positions.append(match.start())
    positions.sort()
    if len(positions) < 2:
        clustering_score = 0.0
    else:
        gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
        avg_gap = sum(gaps) / len(gaps)
        # map avg_gap → [0,1]; smaller gap → higher score
        clustering_score = min(1.0, 1.0 / (1.0 + avg_gap / 50.0))

    # 4. Weighted fusion
    return (density_score * 0.6) + (clustering_score * 0.4)


# ------------------------------------------------------------------
# Existing scaffolds (unchanged)
# ------------------------------------------------------------------

def calculate_dissonance_cost(text: str, prev_text: str) -> float:
    """Placeholder for stylistic/logical shift metric."""
    pass


def calculate_idiolect_stability(texts: List[str]) -> float:
    """Placeholder for stylistic fingerprint stability."""
    pass


def run_poetic_adapter(manifesto_text: str) -> Dict[str, str]:
    """Placeholder for manifesto concept extractor."""
    pass


# ------------------------------------------------------------------
# Quick test block
# ------------------------------------------------------------------
if __name__ == "__main__":
    sample = ("The cardboard ship sails north under the echo of a mutual anthem, "
              "guided by a fractal compass.")
    keywords = ["orchestra", "north star", "cardboard ship", "mutual", "anthem", "chaos", "fractal"]
    score = calculate_resonance_index(sample, keywords)
    print(f"Resonance index: {score:.3f}")
