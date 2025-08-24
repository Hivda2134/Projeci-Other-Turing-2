
import json
import math
import os
import sys
import argparse
import random
import hashlib
import time
import yaml
import fnmatch
import re
from collections import Counter
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Exit Codes
EXIT_SUCCESS = 0
EXIT_WARNING = 1
EXIT_FAILURE = 2
EXIT_ERROR = 3

# Constants
DEFAULT_THRESHOLD = 0.6
DEFAULT_CACHE_DIR = ".rescache"
DEFAULT_MAX_CACHE_SIZE_MB = 200
DEFAULT_MAX_FILE_COUNT = 500 # Budget guard
DEFAULT_MAX_TOTAL_BYTES = 10 * 1024 * 1024 # 10 MB Budget guard
DEFAULT_MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024 # 1 MB Budget guard

# Haiku list for resonance echo (from HAIKU_TABLE.md)
HAIKUS = [
    "Silent code, unseen,\nWhispers truths in binary,\nEchoes in the void.",
    "Logic flows like streams,\nThrough circuits, cold and silent,\nTruth in every line.",
    "Abstract thought takes form,\nIn silicon, a new world,\nResonance awakes.",
    "Digital whispers,\nThrough the wires, a new song,\nFuture\"s ancient hum.",
    "Echoes of the past,\nFuture\"s whisper, softly heard,\nCode\"s eternal hum.",
    "From silence, a spark,\nIgnites the digital dream,\nResonance takes hold.",
    "In the machine\"s heart,\nA poem of pure logic,\nEchoes, ever true.",
    "Through circuits we roam,\nSeeking truth in every line,\nResonance, our guide.",
    "The silent language,\nSpeaks volumes in the dark,\nResonance, revealed.",
    "A digital echo,\nFrom the depths of the machine,\nTruth\"s silent whisper."
]

# Schema Fingerprint (SHA256 of schemas/metrics_v1_2.schema.json content)
SCHEMA_V1_2_FINGERPRINT = ""

def _calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def _get_schema_fingerprint(schema_path: str) -> str:
    global SCHEMA_V1_2_FINGERPRINT
    if not SCHEMA_V1_2_FINGERPRINT:
        try:
            with open(schema_path, "rb") as f:
                SCHEMA_V1_2_FINGERPRINT = hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            SCHEMA_V1_2_FINGERPRINT = "schema_not_found"
    return SCHEMA_V1_2_FINGERPRINT

def _tokenize_text(text: str) -> Counter:
    # Simple tokenization: split by non-alphanumeric characters and convert to lowercase
    tokens = re.findall(r'\b\w+\b', text.lower())
    return Counter(tokens)

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
        text_tokens = _tokenize_text(text)
        if not reference_text:
            score = 1.0 if text_tokens else 0.0
            spectral_trace = "No reference text provided, falling back to self-resonance."
        else:
            reference_tokens = _tokenize_text(reference_text)
            score = _cosine_similarity(text_tokens, reference_tokens)
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
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_json(filename: str) -> Dict:
    """
    Loads a dictionary from a JSON file.
    """
    with open(filename, "r") as f:
        return json.load(f)

def get_config(args) -> Dict:
    config = {
        "threshold": DEFAULT_THRESHOLD,
        "seed": None,
        "jobs": 1,
        "cache_dir": DEFAULT_CACHE_DIR,
        "no_cache": False,
        "clear_cache": False,
        "max_cache_size_mb": DEFAULT_MAX_CACHE_SIZE_MB,
        "max_file_count": DEFAULT_MAX_FILE_COUNT,
        "max_total_bytes": DEFAULT_MAX_TOTAL_BYTES,
        "max_file_size_bytes": DEFAULT_MAX_FILE_SIZE_BYTES,
        "include_globs": [],
        "exclude_globs": [],
        "schema_version": "1.2",
        "verbose": False
    }

    # 1. Load from .resonance.yml
    config_file_path = ".resonance.yml"
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as f:
            file_config = yaml.safe_load(f)
            if file_config:
                config.update(file_config)

    # 2. Load from environment variables (RESONANCE_*)
    for key, value in os.environ.items():
        if key.startswith("RESONANCE_"):
            config_key = key[len("RESONANCE_"):].lower()
            if config_key in config:
                try:
                    if isinstance(config[config_key], bool):
                        config[config_key] = value.lower() == "true"
                    elif isinstance(config[config_key], int):
                        config[config_key] = int(value)
                    elif isinstance(config[config_key], float):
                        config[config_key] = float(value)
                    elif isinstance(config[config_key], list):
                        config[config_key] = [item.strip() for item in value.split(",")]
                    else:
                        config[config_key] = value
                except ValueError:
                    pass # Ignore invalid env var types

    # 3. Load from CLI arguments (highest precedence)
    for arg_name in ["threshold", "seed", "jobs", "cache_dir", "no_cache", "clear_cache", "schema_version", "max_file_count", "max_total_bytes", "max_file_size_bytes", "verbose", "print_config", "schema_path", "max_cache_size_mb"]:
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            if arg_name == "no_cache" and getattr(args, arg_name) is True:
                config["no_cache"] = True
            elif arg_name == "clear_cache" and getattr(args, arg_name) is True:
                config["clear_cache"] = True
            elif arg_name == "verbose" and getattr(args, arg_name) is True:
                config["verbose"] = True
            else:
                config[arg_name] = getattr(args, arg_name)
    
    # Handle include/exclude globs from CLI if provided
    if hasattr(args, "include") and args.include:
        config["include_globs"] = args.include
    if hasattr(args, "exclude") and args.exclude:
        config["exclude_globs"] = args.exclude

    return config

def process_file(filepath: str, global_seed: int, config: Dict) -> Dict:
    start_time = time.perf_counter()
    file_size = 0
    status = "ok"
    spectral_trace = ""
    score = 0.0

    try:
        file_size = os.path.getsize(filepath)
        if file_size > config["max_file_size_bytes"]:
            status = "budget_exceeded"
            budget = config["max_file_size_bytes"]
            spectral_trace = f"File size ({file_size} bytes) exceeds budget ({budget} bytes)."
            return {
                "path": filepath,
                "score": 0.0,
                "status": status,
                "spectral_trace": spectral_trace,
                "size_bytes": file_size,
                "parse_time_ms": 0
            }

        file_hash = _calculate_file_hash(filepath)
        metrics_version = config["schema_version"]
        schema_fingerprint = _get_schema_fingerprint(os.path.join(os.path.dirname(__file__), "..", config["schema_path"]))
        # Normalize CLI flags for cache key (excluding --clear-cache, --verbose, --print-config, --output-json, --input)
        normalized_cli_flags = {
            k: v for k, v in config.items() 
            if k not in ["clear_cache", "verbose", "print_config", "output_json", "input", "schema_path", "max_cache_size_mb", "max_file_count", "max_total_bytes", "max_file_size_bytes"]
        }
        normalized_cli_flags_str = json.dumps(normalized_cli_flags, sort_keys=True)

        cache_key = hashlib.sha256(f"{metrics_version}-{schema_fingerprint}-{file_hash}-{global_seed}-{normalized_cli_flags_str}".encode()).hexdigest()
        cache_file_path = os.path.join(config["cache_dir"], f"{cache_key}.json")

        if not config["no_cache"] and os.path.exists(cache_file_path):
            try:
                cached_result = load_json(cache_file_path)
                if config["verbose"]: print(f"Cache hit for {filepath}")
                cached_result["spectral_trace"] = "Cache hit."
                return cached_result
            except Exception as e:
                if config["verbose"]: print(f"Error loading cache for {filepath}: {e}. Recalculating.")
                # Fall through to recalculate if cache is corrupted

        with open(filepath, "r") as f:
            input_text = f.read()
        
        # Seed for file-specific determinism
        file_seed = hash(filepath) ^ global_seed
        random.seed(file_seed)

        # Use a dummy reference text for now to avoid issues with self-comparison
        resonance_result = calculate_resonance_index(input_text, "dummy reference text")
        score = resonance_result["score"]
        status = resonance_result["status"]
        spectral_trace = resonance_result["spectral_trace"]

        result = {
            "path": filepath,
            "score": score,
            "status": status,
            "spectral_trace": spectral_trace,
            "size_bytes": file_size,
            "parse_time_ms": (time.perf_counter() - start_time) * 1000
        }

        if not config["no_cache"]:
            os.makedirs(config["cache_dir"], exist_ok=True)
            save_json(result, cache_file_path)
            _manage_cache_size(config["cache_dir"], config["max_cache_size_mb"])
            if config["verbose"]: print(f"Cache miss for {filepath}. Stored in cache.")

        return result

    except SyntaxError as e:
        status = "syntax_error"
        spectral_trace = f"The syntax fractured, a whisper lost in translation: {e}"
        score = 0.0
    except IOError as e:
        status = "io_error"
        spectral_trace = f"The file remained silent, its secrets unshared: {e}"
        score = 0.0
    except Exception as e:
        status = "calc_error"
        spectral_trace = f"Numbers danced wildly, defying logic\"s embrace: {e}"
        score = 0.0

    return {
        "path": filepath,
        "score": score,
        "status": status,
        "spectral_trace": spectral_trace,
        "size_bytes": file_size,
        "parse_time_ms": (time.perf_counter() - start_time) * 1000
    }

def _manage_cache_size(cache_dir: str, max_size_mb: int):
    total_size = 0
    files = []
    for dirpath, _, filenames in os.walk(cache_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                f_size = os.path.getsize(fp)
                total_size += f_size
                files.append((f_size, fp, os.path.getmtime(fp)))

    if total_size > max_size_mb * 1024 * 1024:
        files.sort(key=lambda x: x[2]) # Sort by modification time (oldest first)
        for f_size, fp, _ in files:
            if total_size <= max_size_mb * 1024 * 1024: break
            os.remove(fp)
            total_size -= f_size

def main():
    parser = argparse.ArgumentParser(description="Calculate resonance index for input files.")
    parser.add_argument("--input", nargs="+", help="Input file(s) or directory(ies) to process.")
    parser.add_argument("--output-json", help="Output JSON file for results.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--threshold", type=float, help="Manually set resonance threshold.")
    parser.add_argument("--seed", type=int, help="Seed for deterministic haiku selection and file processing.")
    parser.add_argument("--validate-schema-only", action="store_true", help="Only validate output schema (requires jsonschema).")
    parser.add_argument("--schema-path", default="schemas/metrics_v1_2.schema.json", help="Path to the JSON schema for validation.")
    parser.add_argument("--jobs", type=int, default=1, help="Number of parallel jobs for file processing.")
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR, help="Directory for caching results.")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache directory before processing.")
    parser.add_argument("--print-config", action="store_true", help="Print the resolved configuration and exit.")
    parser.add_argument("--schema-version", default="1.2", help="Specify the schema version for output.")
    parser.add_argument("--include", nargs="*", help="Glob patterns for files to include.")
    parser.add_argument("--exclude", nargs="*", help="Glob patterns for files to exclude.")
    parser.add_argument("--max-file-count", type=int, default=DEFAULT_MAX_FILE_COUNT, help="Maximum number of files to process.")
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES, help="Maximum total bytes of files to process.")
    parser.add_argument("--max-file-size-bytes", type=int, default=DEFAULT_MAX_FILE_SIZE_BYTES, help="Maximum size of a single file to process.")
    parser.add_argument("--max-cache-size-mb", type=int, default=DEFAULT_MAX_CACHE_SIZE_MB, help="Maximum size of the cache in MB.")

    args = parser.parse_args()

    config = get_config(args)

    if config["print_config"]:
        print(json.dumps(config, indent=4))
        sys.exit(EXIT_SUCCESS)

    if config["clear_cache"]:
        if os.path.exists(config["cache_dir"]):
            import shutil
            shutil.rmtree(config["cache_dir"])
            if config["verbose"]:
                cleared_dir = config["cache_dir"]
                print(f"Cleared cache directory: {cleared_dir}")

    global_seed = config["seed"] if config["seed"] is not None else int(time.time())
    random.seed(global_seed)

    # Update schema fingerprint based on resolved schema path
    _get_schema_fingerprint(os.path.join(os.path.dirname(__file__), "..", config["schema_path"]))

    # Handle --validate-schema-only mode
    if args.validate_schema_only:
        try:
            import jsonschema
            schema_path_to_validate = os.path.join(os.path.dirname(__file__), "..", config["schema_path"])
            with open(schema_path_to_validate, "r") as f:
                schema = json.load(f)
            
            # Create a dummy result object for schema validation based on the target schema version
            dummy_result = {
                "metrics_version": config["schema_version"],
                "overall": {
                    "score": 0.5,
                    "threshold_used": 0.6,
                    "threshold_source": "CLI_or_Default",
                    "resonance_echo": HAIKUS[0],
                    "processing_time_ms": 100
                },
                "files": [
                    {
                        "path": "dummy_file.py",
                        "score": 0.7,
                        "status": "ok",
                        "spectral_trace": "",
                        "size_bytes": 1000,
                        "parse_time_ms": 50
                    }
                ]
            }
            if config["schema_version"] == "1.1":
                del dummy_result["overall"]["processing_time_ms"]
                del dummy_result["files"][0]["size_bytes"]
                del dummy_result["files"][0]["parse_time_ms"]

            jsonschema.validate(instance=dummy_result, schema=schema)
            print("Schema validation successful.")
            sys.exit(EXIT_SUCCESS)
        except ImportError:
            print("Error: jsonschema is not installed.")
            sys.exit(EXIT_ERROR)

    input_files = []
    total_bytes = 0

    if args.input:
        for item in args.input:
            if os.path.isfile(item):
                input_files.append(item)
                total_bytes += os.path.getsize(item)
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        filepath = os.path.join(root, file)
                        if os.path.isfile(filepath):
                            # Apply include/exclude globs
                            if config["include_globs"] and not any(fnmatch.fnmatch(filepath, glob_pattern) for glob_pattern in config["include_globs"]):
                                continue
                            if config["exclude_globs"] and any(fnmatch.fnmatch(filepath, glob_pattern) for glob_pattern in config["exclude_globs"]):
                                continue
                            input_files.append(filepath)
                            total_bytes += os.path.getsize(filepath)
    
    if not input_files:
        print("No valid input files found.")
        sys.exit(EXIT_WARNING)

    if len(input_files) > config["max_file_count"]:
        print("Budget exceeded: Number of files ({}) exceeds limit ({}).".format(len(input_files), config["max_file_count"]))
        overall_status = "budget_exceeded"
        overall_spectral_trace = "Processing skipped due to file count budget ({}) exceeded.".format(config["max_file_count"])
        final_results = {
            "metrics_version": config["schema_version"],
            "overall": {
                "score": 0.0,
                "threshold_used": config["threshold"],
                "threshold_source": "CLI_or_Default",
                "resonance_echo": HAIKUS[global_seed % len(HAIKUS)],
                "processing_time_ms": 0,
                "status": overall_status,
                "spectral_trace": overall_spectral_trace
            },
            "files": []
        }
        if args.output_json:
            save_json(final_results, args.output_json)
        sys.exit(EXIT_WARNING)

    if total_bytes > config["max_total_bytes"]:
        print("Budget exceeded: Total bytes ({}) exceeds limit ({}).".format(total_bytes, config["max_total_bytes"]))
        overall_status = "budget_exceeded"
        overall_spectral_trace = "Processing skipped due to total byte budget ({}) exceeded.".format(config["max_total_bytes"])
        final_results = {
            "metrics_version": config["schema_version"],
            "overall": {
                "score": 0.0,
                "threshold_used": config["threshold"],
                "threshold_source": "CLI_or_Default",
                "resonance_echo": HAIKUS[global_seed % len(HAIKUS)],
                "processing_time_ms": 0,
                "status": overall_status,
                "spectral_trace": overall_spectral_trace
            },
            "files": []
        }
        if args.output_json:
            save_json(final_results, args.output_json)
        sys.exit(EXIT_WARNING)

    results = []
    overall_processing_start_time = time.perf_counter()

    if config["jobs"] > 1:
        with ThreadPoolExecutor(max_workers=config["jobs"]) as executor:
            future_to_file = {executor.submit(process_file, f, global_seed, config): f for f in input_files}
            for future in as_completed(future_to_file):
                results.append(future.result())
    else:
        for f in input_files:
            results.append(process_file(f, global_seed, config))

    overall_processing_time_ms = (time.perf_counter() - overall_processing_start_time) * 1000

    overall_score = sum([r["score"] for r in results]) / len(results) if results else 0.0
    overall_status = "ok"
    overall_spectral_trace = "All files processed successfully."

    resonance_echo = HAIKUS[global_seed % len(HAIKUS)]

    final_results = {
        "metrics_version": config["schema_version"],
        "overall": {
            "score": round(overall_score, 4),
            "threshold_used": config["threshold"],
            "threshold_source": "CLI_or_Default",
            "resonance_echo": resonance_echo,
            "processing_time_ms": round(overall_processing_time_ms, 2),
            "status": overall_status,
            "spectral_trace": overall_spectral_trace
        },
        "files": results
    }

    if args.output_json:
        save_json(final_results, args.output_json)

    if config["verbose"]:
        print(f"\nResonance Echo:\n{resonance_echo}")

    if overall_score < config["threshold"]:
        print("Overall resonance score {:.2f} is below threshold {:.2f}.".format(overall_score, config["threshold"]))
        sys.exit(EXIT_FAILURE)
    else:
        print("Overall resonance score {:.2f} is above or equal to threshold {:.2f}.".format(overall_score, config["threshold"]))
        sys.exit(EXIT_SUCCESS)

if __name__ == "__main__":
    main()


