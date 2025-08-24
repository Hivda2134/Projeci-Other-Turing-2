import argparse
import json
import os
import sys
import random
import time

# Add the parent directory to the Python path to import resonance_metric
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from metrics import resonance_metric

def main():
    parser = argparse.ArgumentParser(description="Calibrate Phantom Resonance.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic haiku selection and processing.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    seed = args.seed
    random.seed(seed)

    # Define paths to calibration fixtures
    fixture_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'calibration_data')
    high_res_A_path = os.path.join(fixture_dir, 'high_resonance_A.py')
    high_res_B_path = os.path.join(fixture_dir, 'high_resonance_B.md')
    low_res_A_path = os.path.join(fixture_dir, 'low_resonance_A.py')
    low_res_B_path = os.path.join(fixture_dir, 'low_resonance_B.txt')

    overall_start_time = time.perf_counter()

    # --- High Resonance Test ---
    high_res_score = 0.0
    high_res_spectral_trace = ""
    try:
        with open(high_res_A_path, 'r') as f: high_res_A_content = f.read()
        with open(high_res_B_path, 'r') as f: high_res_B_content = f.read()
        
        dummy_config = {
            "schema_version": "1.2",
            "schema_path": "schemas/metrics_v1_2.schema.json",
            "verbose": args.verbose,
            "cache_dir": ".rescache",
            "no_cache": True, # Disable cache for calibration runs
            "max_file_size_bytes": 10 * 1024 * 1024 # 10MB
        }
        
        high_res_result = resonance_metric.calculate_resonance_index(high_res_A_content, high_res_B_content)
        high_res_score = high_res_result["score"]
        high_res_spectral_trace = high_res_result["spectral_trace"]

    except Exception as e:
        high_res_spectral_trace = f"Error during high resonance test: {e}"
        if args.verbose: print(high_res_spectral_trace)

    # --- Low Resonance Test ---
    low_res_score = 0.0
    low_res_spectral_trace = ""
    try:
        with open(low_res_A_path, 'r') as f: low_res_A_content = f.read()
        with open(low_res_B_path, 'r') as f: low_res_B_content = f.read()

        low_res_result = resonance_metric.calculate_resonance_index(low_res_A_content, low_res_B_content)
        low_res_score = low_res_result["score"]
        low_res_spectral_trace = low_res_result["spectral_trace"]

    except Exception as e:
        low_res_spectral_trace = f"Error during low resonance test: {e}"
        if args.verbose: print(low_res_spectral_trace)

    delta = high_res_score - low_res_score

    # Generate ghost_echo (haiku)
    haiku_index = seed % len(resonance_metric.HAIKUS)
    ghost_echo = resonance_metric.HAIKUS[haiku_index]

    overall_processing_time_ms = (time.perf_counter() - overall_start_time) * 1000

    # Prepare structured results
    calibration_results = {
        'meta': {
            'seed': seed,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'engine': 'v1.2'
        },
        'high': {
            'score': round(high_res_score, 4),
            'spectral_trace': high_res_spectral_trace,
            'ghost_echo': ghost_echo.replace('\n', ' ')
        },
        'low': {
            'score': round(low_res_score, 4),
            'spectral_trace': low_res_spectral_trace,
            'ghost_echo': ghost_echo.replace('\n', ' ')
        },
        'delta': round(delta, 4)
    }

    # Output results to ci_artifacts/
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'ci_artifacts')
    os.makedirs(output_dir, exist_ok=True)

    calibration_json_path = os.path.join(output_dir, 'calibration.json')
    echo_txt_path = os.path.join(output_dir, 'echo.txt')

    with open(calibration_json_path, 'w') as f:
        json.dump(calibration_results, f, indent=4)

    with open(echo_txt_path, 'w') as f:
        f.write(ghost_echo)

    # Print human-readable scores
    print(f"High Resonance Test Score: {high_res_score:.4f}")
    print(f"Low Resonance Test Score: {low_res_score:.4f}")
    print(f"Delta: {delta:.4f}")

    # Exit codes
    if delta < 0.05:
        print("Phantom silence alarm: Delta is less than 0.05.")
        sys.exit(2) # Phantom silence alarm
    else:
        sys.exit(0) # Success

if __name__ == "__main__":
    main()


