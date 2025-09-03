#!/usr/bin/env bash
set -euo pipefail
# Run the Python tests we added (pytest recommended).
if command -v pytest >/dev/null 2>&1; then
  pytest -q
else
  echo "pytest not found; run 'pip install pytest' then './scripts/run_piv_tests.sh'"
  exit 0
fi
