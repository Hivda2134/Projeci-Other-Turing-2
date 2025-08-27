
.PHONY: scan sterilize-all
scan:
	python3 tests/ghost_scanner.py

# Caution: edits files in place across the repo.
sterilize-all:
	@python3 - <<\'PY\'
import pathlib, subprocess
exts = {".md",".txt",".py",".js",".ts",".tsx",".jsx",".json",".yaml",".yml",".toml",".ini",".cfg",".sh",".bash",".zsh",".css",".scss",".less",".html",".xml",".csv",".tsv"}
exclude = {".git",".venv","venv","node_modules","dist","build",".next",".cache",".idea",".vscode","ci_artifacts",".pytest_cache","__pycache__"}
for p in pathlib.Path(".").rglob("*"):
    if not p.is_file(): continue
    if set(p.parts) & exclude: continue
    if p.suffix.lower() not in exts: continue
    subprocess.run(["python3","scripts/sterilize.py",str(p),str(p)], check=True)
PY


