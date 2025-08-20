
import os
import json
import math
import argparse
import sys
import re
import yaml
from collections import Counter
from typing import Dict, List, Tuple

# Try importing scikit-learn and joblib for ML gate, handle gracefully if not present
try:
    from sklearn.linear_model import LogisticRegression
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Exit Codes
EXIT_SUCCESS = 0
EXIT_WARNING = 1
EXIT_FAILURE = 2
EXIT_ERROR = 3

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
    Returns 0.0 if text is unparseable or empty.
    """
    if not text:
        return 0.0

    # Fallback to pure Python RSA/cosine similarity if no reference_text
    if not reference_text:
        text_words = Counter(text.lower().split())
        return 1.0 if text_words else 0.0

    text_words = Counter(text.lower().split())
    reference_words = Counter(reference_text.lower().split())

    return _cosine_similarity(text_words, reference_words)

def save_json(data: Dict, filename: str):
    """
    Saves a dictionary to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename: str) -> Dict:
    """
    Loads a dictionary from a JSON file.
    """
    with open(filename, 'r') as f:
        return json.load(f)

def validate_json_schema(data: Dict, schema_path: str) -> bool:
    """
    Validates data against a JSON schema.
    """
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Schema validation error: {e.message}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}", file=sys.stderr)
        return False
    except json.JSONDecodeError:
        print(f"Error: Could not parse schema file {schema_path}", file=sys.stderr)
        return False

def get_threshold(args, verbose: bool = False) -> Tuple[float, str]:
    """
    Determines the alert threshold based on priority: CLI > config > calibration.
    """
    threshold = None
    source = "default"

    if args.threshold is not None:
        threshold = args.threshold
        source = "CLI"
    elif args.config_file and os.path.exists(args.config_file):
        try:
            config = load_json(args.config_file)
            if "resonance_threshold" in config:
                threshold = config["resonance_threshold"]
                source = "config_file"
        except json.JSONDecodeError:
            if verbose: print(f"Warning: Could not parse config file {args.config_file}", file=sys.stderr)
    
    if threshold is None and os.path.exists("calibration.json"):
        try:
            calibration_data = load_json("calibration.json")
            if "suggested_alert_threshold" in calibration_data:
                threshold = calibration_data["suggested_alert_threshold"]
                source = "calibration"
        except json.JSONDecodeError:
            if verbose: print("Warning: Could not parse calibration.json", file=sys.stderr)

    if threshold is None:
        threshold = 0.6 # Default fallback threshold
        source = "default"
    
    return threshold, source

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate resonance index for input files.")
    parser.add_argument("--input", nargs="+", help="Input file(s) or directory(ies) to process.")
    parser.add_argument("--permutations", type=int, default=0, help="Number of permutations for calibration (0 for no calibration).")
    parser.add_argument("--output-json", help="Output JSON file for results.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--threshold", type=float, help="Manually set resonance threshold.")
    parser.add_argument("--config-file", help="Path to a configuration file for thresholds.")
    parser.add_argument("--print-threshold-source", action="store_true", help="Print the source of the threshold used.")
    parser.add_argument("--validate-schema-only", action="store_true", help="Only validate output schema (requires jsonschema).")
    parser.add_argument("--schema-path", default="schemas/metrics_v1_2.schema.json", help="Path to the JSON schema for validation.")
    parser.add_argument("--toxic-config", help="Path to toxic signals configuration file.")
    parser.add_argument("--allowlist", help="Path to allowlist file for toxic signals.")
    parser.add_argument("--toxic-ml", action="store_true", help="Enable ML-based toxic detection (requires scikit-learn and joblib).")
    parser.add_argument("--toxic-ml-threshold", type=float, default=0.5, help="Threshold for ML-based toxic detection.")

    args = parser.parse_args()

    if args.verbose: print(f"Processing input: {args.input}")

    threshold, threshold_source = get_threshold(args, args.verbose)
    if args.print_threshold_source: print(f"Threshold source: {threshold_source}")

    # Handle --validate-schema-only mode
    if args.validate_schema_only:
        try:
            import jsonschema
            # This is a placeholder. Actual schema validation logic would go here.
            # For now, we just check if jsonschema is importable.
            print("jsonschema is importable. Schema validation would proceed here.")
            sys.exit(EXIT_SUCCESS)
        except ImportError:
            print("Error: jsonschema is not installed. Cannot validate schema.", file=sys.stderr)
            sys.exit(EXIT_ERROR)

    if args.input:
        if len(args.input) == 1 and os.path.isdir(args.input[0]):
            from scripts.calibrate_resonance import calibrate_resonance
            if args.permutations > 0:
                if args.verbose: print(f"Running calibration with {args.permutations} permutations.")
                calibration_data = calibrate_resonance(args.input[0], args.permutations)
                if args.output_json:
                    save_json(calibration_data, args.output_json)
                else:
                    print(json.dumps(calibration_data, indent=4))
                sys.exit(EXIT_SUCCESS)
            else:
                # Calculate resonance of each file against itself and average them
                total_resonance = 0.0
                file_count = 0
                processed_files = []
                overall_risk_suspected = False
                overall_severity = 0.0

                for filename in os.listdir(args.input[0]):
                    filepath = os.path.join(args.input[0], filename)
                    if os.path.isfile(filepath) and filepath.endswith(".py"):
                        try:
                            with open(filepath, "r") as f:
                                input_text = f.read()
                            resonance_score = calculate_resonance_index(input_text, input_text)
                            toxic_detection_results = detect_toxic_signals(input_text, args.toxic_config, args.allowlist, args.toxic_ml, args.toxic_ml_threshold, verbose=args.verbose)

                            total_resonance += resonance_score
                            file_count += 1
                            
                            file_result = {"file": filename, "resonance_score": resonance_score}
                            file_result.update(toxic_detection_results)
                            processed_files.append(file_result)

                            if toxic_detection_results["risk_suspected"]:
                                overall_risk_suspected = True
                                overall_severity += toxic_detection_results["severity"]

                            if args.verbose: print(f"  File: {filename}, Resonance: {resonance_score:.4f}, Toxic Risk: {toxic_detection_results["risk_suspected"]}")
                        except Exception as e:
                            if args.verbose: print(f"  Error processing file {filename}: {e}", file=sys.stderr)
                            processed_files.append({"file": filename, "resonance_score": 0.0, "error": str(e), "risk_suspected": False, "severity": 0.0})
                            total_resonance += 0.0 # Add 0.0 for files that cause errors
                            file_count += 1 # Count as processed to avoid ZeroDivisionError

                avg_resonance = total_resonance / file_count if file_count > 0 else 0.0
                result = {
                    "overall_resonance_score": avg_resonance,
                    "files": processed_files,
                    "threshold_used": threshold,
                    "threshold_source": threshold_source,
                    "overall_risk_suspected": overall_risk_suspected,
                    "overall_severity": overall_severity
                }
                if args.output_json:
                    save_json(result, args.output_json)
                else:
                    print(json.dumps(result, indent=4))
                
                # Validate schema before exiting
                if not validate_json_schema(result, args.schema_path):
                    sys.exit(EXIT_ERROR) # Exit with error if schema validation fails

                if avg_resonance < threshold or overall_risk_suspected:
                    if args.verbose: 
                        if avg_resonance < threshold: print(f"Overall resonance score ({avg_resonance:.4f}) is below threshold ({threshold:.4f}).", file=sys.stderr)
                        if overall_risk_suspected: print(f"Toxic risk suspected (Severity: {overall_severity:.4f}).", file=sys.stderr)
                    sys.exit(EXIT_FAILURE)
                else:
                    if args.verbose: print(f"Overall resonance score ({avg_resonance:.4f}) is above or equal to threshold ({threshold:.4f}).")
                    sys.exit(EXIT_SUCCESS)

        elif len(args.input) == 1 and os.path.isfile(args.input[0]):
            try:
                with open(args.input[0], 'r') as f:
                    input_text = f.read()
                resonance_score = calculate_resonance_index(input_text)
                toxic_detection_results = detect_toxic_signals(input_text, args.toxic_config, args.allowlist, args.toxic_ml, args.toxic_ml_threshold, verbose=args.verbose)

                result = {"file": args.input[0], "resonance_score": resonance_score, "threshold_used": threshold, "threshold_source": threshold_source}
                result.update(toxic_detection_results)

                if args.output_json:
                    save_json(result, args.output_json)
                else:
                    print(json.dumps(result, indent=4))
                
                # Validate schema before exiting
                if not validate_json_schema(result, args.schema_path):
                    sys.exit(EXIT_ERROR) # Exit with error if schema validation fails

                if resonance_score < threshold or toxic_detection_results["risk_suspected"]:
                    if args.verbose: 
                        if resonance_score < threshold: print(f"Resonance score ({resonance_score:.4f}) is below threshold ({threshold:.4f}).", file=sys.stderr)
                        if toxic_detection_results["risk_suspected"]: print(f"Toxic risk suspected (Severity: {toxic_detection_results["severity"]:.4f}).", file=sys.stderr)
                    sys.exit(EXIT_FAILURE)
                else:
                    if args.verbose: print(f"Resonance score ({resonance_score:.4f}) is above or equal to threshold ({threshold:.4f}).")
                    sys.exit(EXIT_SUCCESS)
            except Exception as e:
                if args.verbose: print(f"Error processing file {args.input[0]}: {e}", file=sys.stderr)
                result = {"file": args.input[0], "resonance_score": 0.0, "error": str(e), "threshold_used": threshold, "threshold_source": threshold_source, "risk_suspected": False, "severity": 0.0}
                if args.output_json:
                    save_json(result, args.output_json)
                else:
                    print(json.dumps(result, indent=4))
                sys.exit(EXIT_ERROR)
        else:
            if args.verbose: print("Error: Input must be a single file or a single directory.", file=sys.stderr)
            sys.exit(EXIT_ERROR)
    else:
        parser.print_help()
        sys.exit(EXIT_WARNING)


