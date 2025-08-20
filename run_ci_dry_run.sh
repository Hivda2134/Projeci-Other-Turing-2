#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting CI Dry Run ---"

echo "Step 1: Install dependencies"
python3 -m pip install --upgrade pip
pip install pytest
# pip install -e . # This would install the current directory as a package, not strictly needed for this dry run

echo "Step 2: Run pytest"
PYTHONPATH=. pytest -q

echo "Step 3: Run Resonance Metric and Check Threshold"

# Generate calibration data if not present
if [ ! -f calibration.json ]; then
  echo "calibration.json not found. Running calibration script..."
  PYTHONPATH=. python3 scripts/calibrate_resonance.py samples/
fi

# Read the suggested_alert_threshold from calibration.json
THRESHOLD=$(jq -r ".suggested_alert_threshold" calibration.json)
echo "Suggested Alert Threshold: $THRESHOLD"

# Run the resonance metric for samples and output to ci_resonance.json
PYTHONPATH=. python3 -m metrics.resonance_metric --input samples/ --output-json ci_resonance.json

# Read the resonance score from ci_resonance.json (aligned_average)
CURRENT_RESONANCE=$(jq -r ".aligned_average" ci_resonance.json)
echo "Current Resonance Score (aligned_average): $CURRENT_RESONANCE"

# Compare and set status
if (( $(echo "$CURRENT_RESONANCE < $THRESHOLD" | bc -l) )); then
  echo "Resonance score ($CURRENT_RESONANCE) is below the threshold ($THRESHOLD)."
  echo "CI Status: FAILURE"
  exit 1
else
  echo "Resonance score ($CURRENT_RESONANCE) is above or equal to the threshold ($THRESHOLD)."
  echo "CI Status: SUCCESS"
fi

echo "--- CI Dry Run Complete ---"


