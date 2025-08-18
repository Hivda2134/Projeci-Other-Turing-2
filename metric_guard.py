import os
import warnings
from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_visit

class EthicalTrapWarning(UserWarning):
    """
    Raised when a piece of code appears to exceed ethical
    complexity thresholds.
    """
    pass


def get_cyclomatic_complexity(filepath: str) -> float | None:
    """
    Returns the average cyclomatic complexity of the given file.

    Args:
        filepath (str): Path to the Python file.

    Returns:
        float | None: Average complexity, or None if the file
        cannot be processed.
    """
    try:
        with open(filepath, encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f'Error reading {filepath}: {e}')
        return None

    blocks = cc_visit(code)
    if not blocks:
        return 0.0

    total = sum(block.complexity for block in blocks)
    return total / len(blocks)


def get_maintainability_index(filepath: str) -> float | None:
    """
    Returns the maintainability index (0–100) for the given file.

    Args:
        filepath (str): Path to the Python file.

    Returns:
        float | None: MI score, or None on failure.
    """
    try:
        with open(filepath, encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f'Error reading {filepath}: {e}')
        return None

    return mi_visit(code, multi=True)


def ethical_trap_check(
    filepath: str,
    max_complexity: float = 10.0,
    min_maintainability: float = 60.0
) -> bool:
    """
    Performs an ethical-trap check on the given file.

    Args:
        filepath (str): Path to the Python file.
        max_complexity (float): Threshold for average cyclomatic complexity.
        min_maintainability (float): Minimum acceptable maintainability index.

    Returns:
        bool: True if the file is within ethical thresholds,
              False otherwise.
    """
    comp = get_cyclomatic_complexity(filepath)
    mi = get_maintainability_index(filepath)

    if comp is None or mi is None:
        # Cannot evaluate; treat as non-compliant
        return False

    if comp > max_complexity or mi < min_maintainability:
        warnings.warn(
            f'{filepath} failed ethical-trap check: '
            f'complexity={comp:.2f}, MI={mi:.2f}',
            EthicalTrapWarning
        )
        return False

    return True


if __name__ == '__main__':
    self_check = ethical_trap_check(__file__)
    print(f'ethical_trap_check(__file__) returned {self_check}')
