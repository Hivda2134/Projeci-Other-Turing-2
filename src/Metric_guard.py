# src/metric_guard.py
"""
Ethical-trap guardrail for the Λmutual metrics engine.
Raises warnings when a single metric is gamed at the expense
of overall code health.
"""

from typing import Dict, Tuple
from radon.metrics import mi_visit
from radon.complexity import cc_visit
import subprocess
import sys


def get_cyclomatic_complexity(filepath: str) -> float:
    """Return average cyclomatic complexity of a file."""
    try:
        blocks = cc_visit(open(filepath, encoding="utf-8").read())
        return sum(b.complexity for b in blocks) / max(len(blocks), 1)
    except Exception:
        return 0.0


def get_maintainability_index(filepath: str) -> float:
    """Return Radon MI score (0-100)."""
    try:
        return mi_visit(open(filepath, encoding="utf-8").read(), multi=True)
    except Exception:
        return 0.0


def ethical_trap_check(filepath: str) -> Tuple[bool, Dict[str, float]]:
    """
    Returns (is_safe, metrics_dict).
    Raises EthicalTrapWarning if cyclomatic is "too good" while MI is poor.
    """
    cc = get_cyclomatic_complexity(filepath)
    mi = get_maintainability_index(filepath)

    metrics = {"cyclomatic": cc, "maintainability": mi}

    # Tweak thresholds as project matures
    if cc < 2.0 and mi < 50:
        raise EthicalTrapWarning(
            f"Cyclomatic complexity ({cc:.2f}) is suspiciously low "
            f"while maintainability index ({mi:.1f}) is poor. "
            f"Check for obfuscation or logic removal."
        )
    return True, metrics


class EthicalTrapWarning(RuntimeWarning):
    """Raised when a metric may have been gamed."""
    pass


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else __file__
    safe, metrics = ethical_trap_check(target)
    print(f"{target} -> {metrics} | Safe: {safe}")
