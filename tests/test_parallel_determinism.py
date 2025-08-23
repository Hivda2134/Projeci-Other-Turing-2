import pytest
import subprocess
import json
import os

@pytest.fixture(autouse=True)
def cleanup_files():
    output_file = "parallel_output.json"
    if os.path.exists(output_file):
        os.remove(output_file)
    yield
    if os.path.exists(output_file):
        os.remove(output_file)

def run_metric_and_get_output(args):
    output_file = "parallel_output.json"
    command = [
        "python", "-m", "metrics.resonance_metric",
        "--output-json", output_file,
    ] + args
    process = subprocess.run(command, capture_output=True, text=True)
    
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            return process.returncode, json.load(f)
    else:
        print(f"STDOUT: {process.stdout}")
        print(f"STDERR: {process.stderr}")
        return process.returncode, None

def test_parallel_determinism():
    input_dir = "samples"

    # Run with 1 job
    returncode_1_job, result_1_job = run_metric_and_get_output([
        "--input", input_dir,
        "--seed", "123",
        "--jobs", "1"
    ])
    assert returncode_1_job in [0, 2]
    assert result_1_job is not None

    # Run with 2 jobs
    returncode_2_jobs, result_2_jobs = run_metric_and_get_output([
        "--input", input_dir,
        "--seed", "123",
        "--jobs", "2"
    ])
    assert returncode_2_jobs in [0, 2]
    assert result_2_jobs is not None

    # Ensure overall scores are identical
    assert result_1_job["overall"]["score"] == pytest.approx(result_2_jobs["overall"]["score"])
    assert result_1_job["overall"]["resonance_echo"] == result_2_jobs["overall"]["resonance_echo"]

    # Ensure file-level results are identical (after sorting by path for comparison)
    files_1_job = sorted(result_1_job["files"], key=lambda x: x["path"])
    files_2_jobs = sorted(result_2_jobs["files"], key=lambda x: x["path"])

    assert len(files_1_job) == len(files_2_jobs)
    for i in range(len(files_1_job)):
        assert files_1_job[i]["path"] == files_2_jobs[i]["path"]
        assert files_1_job[i]["score"] == pytest.approx(files_2_jobs[i]["score"])
        assert files_1_job[i]["status"] == files_2_jobs[i]["status"]
        assert files_1_job[i]["spectral_trace"] == files_2_jobs[i]["spectral_trace"]


