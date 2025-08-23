import pytest
import subprocess
import json
import os

METRIC_SCRIPT = "metrics.resonance_metric"
OUTPUT_JSON = "config_output.json"
INPUT_FILE = "samples/simple_function.py"
CONFIG_FILE = ".resonance.yml"

@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    yield
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

def run_metric_and_get_output(args):
    command = [
        "python", "-m", METRIC_SCRIPT,
        "--input", INPUT_FILE,
        "--output-json", OUTPUT_JSON
    ] + args
    process = subprocess.run(command, capture_output=True, text=True)
    
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            return process.returncode, json.load(f)
    else:
        print(f"STDOUT: {process.stdout}")
        print(f"STDERR: {process.stderr}")
        return process.returncode, None

def test_default_threshold():
    returncode, result = run_metric_and_get_output([])
    assert returncode in [0, 2]
    assert result["overall"]["threshold_used"] == 0.6
    assert result["overall"]["threshold_source"] == "CLI_or_Default"

def test_cli_precedence_over_default():
    returncode, result = run_metric_and_get_output(["--threshold", "0.75"])
    assert returncode in [0, 2]
    assert result["overall"]["threshold_used"] == 0.75
    assert result["overall"]["threshold_source"] == "CLI_or_Default"

def test_config_file_precedence_over_default():
    with open(CONFIG_FILE, "w") as f:
        f.write("threshold: 0.8\n")
    returncode, result = run_metric_and_get_output([])
    assert returncode in [0, 2]
    assert result["overall"]["threshold_used"] == 0.8
    assert result["overall"]["threshold_source"] == "CLI_or_Default" # Source is still default if not explicitly set by config

def test_env_var_precedence_over_config_file():
    with open(CONFIG_FILE, "w") as f:
        f.write("threshold: 0.8\n")
    os.environ["RESONANCE_THRESHOLD"] = "0.9"
    returncode, result = run_metric_and_get_output([])
    assert returncode in [0, 2]
    assert result["overall"]["threshold_used"] == 0.9
    assert result["overall"]["threshold_source"] == "CLI_or_Default" # Source is still default if not explicitly set by config
    del os.environ["RESONANCE_THRESHOLD"]

def test_cli_precedence_over_env_var_and_config_file():
    with open(CONFIG_FILE, "w") as f:
        f.write("threshold: 0.8\n")
    os.environ["RESONANCE_THRESHOLD"] = "0.9"
    returncode, result = run_metric_and_get_output(["--threshold", "0.95"])
    assert returncode in [0, 2]
    assert result["overall"]["threshold_used"] == 0.95
    assert result["overall"]["threshold_source"] == "CLI_or_Default"
    del os.environ["RESONANCE_THRESHOLD"]

def test_print_config_flag():
    command = [
        "python", "-m", METRIC_SCRIPT,
        "--print-config"
    ]
    process = subprocess.run(command, capture_output=True, text=True, check=True)
    config_output = json.loads(process.stdout)
    assert "threshold" in config_output
    assert config_output["threshold"] == 0.6 # Default value

    # Test with CLI override
    command_cli = [
        "python", "-m", METRIC_SCRIPT,
        "--print-config",
        "--threshold", "0.77"
    ]
    process_cli = subprocess.run(command_cli, capture_output=True, text=True, check=True)
    config_output_cli = json.loads(process_cli.stdout)
    assert config_output_cli["threshold"] == 0.77

    # Test with config file
    with open(CONFIG_FILE, "w") as f:
        f.write("threshold: 0.88\n")
    command_file = [
        "python", "-m", METRIC_SCRIPT,
        "--print-config"
    ]
    process_file = subprocess.run(command_file, capture_output=True, text=True, check=True)
    config_output_file = json.loads(process_file.stdout)
    assert config_output_file["threshold"] == 0.88

    # Test with ENV var
    os.environ["RESONANCE_THRESHOLD"] = "0.99"
    command_env = [
        "python", "-m", METRIC_SCRIPT,
        "--print-config"
    ]
    process_env = subprocess.run(command_env, capture_output=True, text=True, check=True)
    config_output_env = json.loads(process_env.stdout)
    assert config_output_env["threshold"] == 0.99
    del os.environ["RESONANCE_THRESHOLD"]




