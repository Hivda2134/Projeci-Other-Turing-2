#!/usr/bin/env python3
"""
Ghost Scanner – Unicode Hayalet Avcısı
Detects invisible/hazardous Unicode code-points in project files.
Run:  python tests/ghost_scanner.py
Exit 0 → clean, 1 → ghosts found.
"""

import sys
from pathlib import Path

# Unicode ranges known to cause CI or security issues
GHOST_RANGES = {
    0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF,       # zero-width
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,       # bidi override
    0x0000, 0x0001, 0x0002, 0x0003, 0x0004,       # control chars
}

def scan_file(path: Path) -> list[tuple[int, str]]:
    ghosts = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                for ch in line:
                    cp = ord(ch)
                    if cp in GHOST_RANGES:
                        ghosts.append((line_no, f"U+{cp:04X} {ch!r}"))
    except UnicodeDecodeError:
        pass  # skip binary files
    return ghosts

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ghost_count = 0
    for path in root.rglob("*.py"):
        hits = scan_file(path)
        if hits:
            print(f"👻 {path.relative_to(root)}")
            for ln, ghost in hits:
                print(f"   line {ln}: {ghost}")
            ghost_count += len(hits)
    if ghost_count:
        print(f"\nTotal ghosts found: {ghost_count}")
        sys.exit(1)
    print("✅ No ghosts detected.")

if __name__ == "__main__":
    main()
