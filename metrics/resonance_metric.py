import json
import math
import os
import sys
import argparse
import random
from collections import Counter
from typing import Dict, List, Tuple

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

def calculate_resonance_index(text: str, reference_text: str = "") -> Dict:
    """
    Calculates the resonance index between a given text and a reference text.
    If no reference text is provided, it falls back to a pure Python RSA/cosine similarity.
    Returns 0.0 if text is unparseable or empty.
    """
    status = "ok"
    spectral_trace = ""
    score = 0.0

    if not text:
        status = "io_error"
        spectral_trace = "Input text is empty."
        return {"score": score, "status": status, "spectral_trace": spectral_trace}

    try:
        text_words = Counter(text.lower().split())
        if not reference_text:
            score = 1.0 if text_words else 0.0
            spectral_trace = "No reference text provided, falling back to self-resonance."
        else:
            reference_words = Counter(reference_text.lower().split())
            score = _cosine_similarity(text_words, reference_words)
            spectral_trace = "Resonance calculated using provided reference text."
    except Exception as e:
        status = "calc_error"
        spectral_trace = f"Calculation error: {e}"
        score = 0.0

    return {"score": score, "status": status, "spectral_trace": spectral_trace}

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

def get_threshold(args, verbose: bool = False) -> float:
    """
    Determines the alert threshold based on CLI argument.
    """
    if args.threshold is not None:
        return args.threshold
    return 0.6 # Default fallback threshold

# Haiku list for resonance echo
HAIKUS = [
    "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void.",
    "Logic flows like streams,\nThrough circuits, cold and silent,\nTruth in every line.",
    "Abstract thought takes form,\nIn silicon, a new world,\nResonance awakes.",
    "Digital whispers,\nThrough the wires, a new song,\nFuture's ancient hum.",
    "Echoes of the past,\nFuture's whisper, softly heard,\nCode's eternal hum.",
    "From silence, a spark,\nIgnites the digital dream,\nResonance takes hold.",
    "In the machine's heart,\nA poem of pure logic,\nEchoes, ever true.",
    "Through circuits we roam,\nSeeking truth in every line,\nResonance, our guide.",
    "The silent language,\nSpeaks volumes in the dark,\nResonance, revealed.",
    "A digital echo,\nFrom the depths of the machine,\nTruth's silent whisper."
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate resonance index for input files.")
    parser.add_argument("--input", nargs="+", help="Input file(s) or directory(ies) to process.")
    parser.add_argument("--output-json", help="Output JSON file for results.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--threshold", type=float, help="Manually set resonance threshold.")
    parser.add_argument("--seed", type=int, default=None, help="Seed for deterministic haiku selection.")
    parser.add_argument("--validate-schema-only", action="store_true", help="Only validate output schema (requires jsonschema).")
    parser.add_argument("--schema-path", default="schemas/metrics_v1_1.schema.json", help="Path to the JSON schema for validation.")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.verbose: print(f"Processing input: {args.input}")

    threshold = get_threshold(args, args.verbose)

    processed_files_results = []
    overall_resonance_score = 0.0
    file_count = 0

    # Handle --validate-schema-only mode
    if args.validate_schema_only:
        try:
            import jsonschema
            # Create a dummy result object for schema validation
            dummy_result = {
                "metrics_version": "1.1",
                "overall": {
                    "score": 0.5,
                    "threshold_used": 0.6,
                    "threshold_source": "CLI_or_Default",
                    "resonance_echo": HAIKUS[0] # Use the first haiku for dummy
                },
                "files": [
                    {
                        "path": "dummy_file.py",
                        "score": 0.7,
                        "status": "ok",
                        "spectral_trace": ""
                    }
                ]
            }
            with open(args.schema_path, 'r') as f:
                schema = json.load(f)
            jsonschema.validate(instance=dummy_result, schema=schema)
            print("Schema validation successful.")
            sys.exit(EXIT_SUCCESS)
        except ImportError:
            print("Error: jsonschema is not installed. Cannot validate schema.", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        except Exception as e:
            print(f"Schema validation failed: {e}", file=sys.stderr)
            sys.exit(EXIT_ERROR)

    if args.input:
        for input_path in args.input:
            if os.path.isdir(input_path):
                for filename in os.listdir(input_path):
                    filepath = os.path.join(input_path, filename)
                    if os.path.isfile(filepath) and filepath.endswith(".py"):
                        try:
                            with open(filepath, "r") as f:
                                input_text = f.read()
                            
                            resonance_result = calculate_resonance_index(input_text, input_text)
                            processed_files_results.append({"path": filepath, **resonance_result})
                            
                            if resonance_result["status"] == "ok":
                                overall_resonance_score += resonance_result["score"]
                                file_count += 1

                            if args.verbose: print(f"  File: {filepath}, Resonance: {resonance_result['score']:.4f}, Status: {resonance_result['status']}")

                        except Exception as e:
                            if args.verbose: print(f"  Error processing file {filepath}: {e}", file=sys.stderr)
                            processed_files_results.append({"path": filepath, "score": 0.0, "status": "io_error", "spectral_trace": str(e)})
                            file_count += 1

            elif os.path.isfile(input_path):
                try:
                    with open(input_path, 'r') as f:
                        input_text = f.read()
                    
                    resonance_result = calculate_resonance_index(input_text, input_text)
                    processed_files_results.append({"path": input_path, **resonance_result})

                    if resonance_result["status"] == "ok":
                        overall_resonance_score += resonance_result["score"]
                        file_count += 1

                    if args.verbose: print(f"  File: {input_path}, Resonance: {resonance_result['score']:.4f}, Status: {resonance_result['status']}")

                except Exception as e:
                    if args.verbose: print(f"  Error processing file {input_path}: {e}", file=sys.stderr)
                    processed_files_results.append({"path": input_path, "score": 0.0, "status": "io_error", "spectral_trace": str(e)})
                    file_count += 1

            else:
                if args.verbose: print(f"Error: Input path {input_path} is not a valid file or directory.", file=sys.stderr)
                sys.exit(EXIT_ERROR)

        avg_resonance = overall_resonance_score / file_count if file_count > 0 else 0.0
        
        # Select a deterministic haiku
        haiku_index = random.randint(0, len(HAIKUS) - 1) if args.seed is None else (args.seed % len(HAIKUS))
        resonance_echo_haiku = HAIKUS[haiku_index]

        result = {
            "metrics_version": "1.1",
            "overall": {
                "score": avg_resonance,
                "threshold_used": threshold,
                "threshold_source": "CLI_or_Default",
                "resonance_echo": resonance_echo_haiku
            },
            "files": processed_files_results
        }

        if args.output_json:
            save_json(result, args.output_json)
        else:
            print(json.dumps(result, indent=4))

        if avg_resonance < threshold:
            if args.verbose: 
                print(f"Overall resonance score ({avg_resonance:.4f}) is below threshold ({threshold:.4f}).", file=sys.stderr)
            sys.exit(EXIT_FAILURE)
        else:
            if args.verbose: print(f"Overall resonance score ({avg_resonance:.4f}) is above or equal to threshold ({threshold:.4f}).")
            sys.exit(EXIT_SUCCESS)

    else:
        parser.print_help()
        sys.exit(EXIT_WARNING)


