# Projeci-Other-Turing-2

This project implements the "Other Turing" paradigm, focusing on measuring AI system consistency, sensitivity, and responsibility rather than human mimicry.

## Features

- **AST Parser**: Extracts symbolic summaries from Python code
- **Resonance Index**: Measures text/code resonance with RSA/cosine fallback
- **Calibration System**: Automatically calibrates resonance thresholds
- **CI/CD Integration**: Automated resonance checks in GitHub Actions

## CI Resonance Check

The project includes an automated CI system that monitors code resonance to ensure consistency and quality.

### How it Works

1. **Calibration**: The system uses `scripts/calibrate_resonance.py` to analyze sample code files and determine optimal resonance thresholds
2. **Threshold Detection**: Calibration generates a `calibration.json` file with suggested alert thresholds (typically between 0.5-0.7)
3. **CI Integration**: GitHub Actions workflow runs resonance checks on every PR and push
4. **Failure Policy**: If resonance scores fall below the calibrated threshold, the CI fails and posts a comment on the PR

### Overriding Thresholds

To override the default resonance threshold:

1. Modify the `suggested_alert_threshold` value in `calibration.json`
2. Commit the changes to apply the new threshold
3. Valid threshold range: 0.5 - 0.7

### Manual Calibration

Run calibration manually:

```bash
PYTHONPATH=. python scripts/calibrate_resonance.py samples/
```

### CLI Usage

The resonance metric can be run directly:

```bash
# Analyze a single file
PYTHONPATH=. python -m metrics.resonance_metric --input file.py --output-json results.json

# Calibrate with permutations
PYTHONPATH=. python -m metrics.resonance_metric --input samples/ --permutations 200 --output-json calibration.json
```

## Installation

```bash
pip install pytest
```

## Testing

```bash
PYTHONPATH=. pytest
```

