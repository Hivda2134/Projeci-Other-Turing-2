#!/usr/bin/env python3
"""
main.py  –  Master orchestrator for the Resonance & Ethics toolchain.

Usage:
    python main.py path/to/file.py
"""

import argparse
import sys
from pathlib import Path

from core_metrics import calculate_resonance_index
from metric_guard import (
    ethical_trap_check,
    EthicalTrapWarning,
    get_cyclomatic_complexity,
    get_maintainability_index,
)

MANIFESTO_KEYWORDS = [
    'resonance',
    'ethics',
    'adaptation',
    'dissonance',
    'stability',
    'poetic',
    'guardian',
    'manifesto',
]


def analyze_file(filepath: str) -> None:
    """
    Runs the full diagnostic on the supplied file and prints a report.

    Args:
        filepath (str): Absolute or relative path to the Python file.
    """
    path = Path(filepath)
    if not path.is_file():
        print(f'Error: {filepath} is not a valid file.')
        return

    # Build a minimal idiolect snapshot placeholder
    idiolect_snapshot = {'keywords': MANIFESTO_KEYWORDS, 'weights': {}}

    # --- Core Metrics ---
    complexity = get_cyclomatic_complexity(filepath)
    maintainability = get_maintainability_index(filepath)
    resonance = calculate_resonance_index(filepath, idiolect_snapshot)

    # --- Guard Check ---
    guard_ok = ethical_trap_check(filepath)

    # --- Report ---
    print('\n==== Resonance & Ethics Report ====')
    print(f'File: {path.resolve()}')
    print('-' * 40)
    if complexity is not None:
        print(f'Average Cyclomatic Complexity : {complexity:.2f}')
    else:
        print('Average Cyclomatic Complexity : N/A')

    if maintainability is not None:
        print(f'Maintainability Index (0-100)  : {maintainability:.2f}')
    else:
        print('Maintainability Index (0-100)  : N/A')

    if resonance is not None:
        print(f'Resonance Index               : {resonance:.2f}')
    else:
        print('Resonance Index               : N/A')

    print(f'Ethical-Trap Check            : {"PASS" if guard_ok else "FAIL"}')
    print('=' * 40)


def main() -> None:
    """
    CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description='Analyze a Python file for resonance and ethical traps.'
    )
    parser.add_argument(
        'filepath',
        help='Path to the Python file to analyze.'
    )

    args = parser.parse_args()

    try:
        analyze_file(args.filepath)
    except KeyboardInterrupt:
        print('\nInterrupted by user.')
        sys.exit(130)
    except Exception as e:
        print(f'Unexpected error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
