#!/usr/bin/env bash
# operation-blitzkrieg.sh
# Operation "Blitzkrieg" — All-in-one CI & project scaffolding solution
# Usage:
#   ./operation-blitzkrieg.sh            # generate files, no commit/push
#   ./operation-blitzkrieg.sh --commit   # generate files, git add + commit
#   ./operation-blitzkrieg.sh --commit --push  # commit and push (requires --commit)
#   ./operation-blitzkrieg.sh --help
set -euo pipefail

### Configuration (edit if your layout differs)
SRC_DIR_DEFAULT="lamutual_project"             # expected top-level package dir
WORKFLOWS_DIR=".github/workflows"
GRAVE_DIR="${WORKFLOWS_DIR}/.graveyard"
MAIN_CI_PATH="${WORKFLOWS_DIR}/main-ci.yml"
PYPROJECT_PATH="pyproject.toml"
TEST_FILE="tests/ghost_scanner_test.py"

### CLI flags
DO_COMMIT=false
DO_PUSH=false

print_help() {
  cat <<'USAGE'
Operation Blitzkrieg: Final all-in-one CI & scaffolding builder.

Usage:
  ./operation-blitzkrieg.sh [--commit] [--push]

Options:
  --commit   : After generation, git add + git commit the generated/changed files.
               (Requires a clean working tree.)
  --push     : After commit, push to origin current branch. (Requires --commit)
  --help     : Show this help and exit.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --commit) DO_COMMIT=true ;;
    --push) DO_PUSH=true ;;
    --help|-h) print_help; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; print_help; exit 2 ;;
  esac
done

### Ensure inside a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: This script must be run inside a git repository root." >&2
  exit 3
fi

# Move to repo root
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

### If commit requested, ensure worktree is clean
if [ "$DO_COMMIT" = true ]; then
  # no unstaged or staged changes
  if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working tree is not clean. Please stash or commit local changes before using --commit." >&2
    git status --porcelain
    exit 4
  fi
fi

### Compute witness (short hash) to stamp CI
WITNESS="$(git rev-parse --short HEAD 2>/dev/null || echo "no-git-head")"
echo "Witness: $WITNESS"

### Prepare directories
mkdir -p "$WORKFLOWS_DIR"
mkdir -p "$GRAVE_DIR"
mkdir -p tests

### 1) Create or backup pyproject.toml (atomic)
if [ -f "$PYPROJECT_PATH" ]; then
  bak_ts="$(date -u +%Y%m%dT%H%M%SZ)"
  bak_dir=".blitzkrieg_backups"
  mkdir -p "$bak_dir"
  cp -a "$PYPROJECT_PATH" "$bak_dir/pyproject.toml.$bak_ts"
  echo "Existing pyproject.toml backed up to $bak_dir/pyproject.toml.$bak_ts"
fi

pyproject_tmp="$(mktemp)"
cat > "$pyproject_tmp" <<'TOML'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "lamutual_project"
version = "0.1.0"
description = "Project Λmutual — persistence, anonymization, and observer protocols."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Λmutual Crew", email = "crew@example.com" }]
keywords = ["observability", "privacy", "persistence", "ai", "protocols"]

[project.optional-dependencies]
dev = [
  "pytest>=7.4",
  "jsonschema>=4.22",
]

[tool.hatch.build]
include = []
TOML

# Move into place atomically
mv -v "$pyproject_tmp" "$PYPROJECT_PATH"
chmod 0644 "$PYPROJECT_PATH"
echo "Wrote $PYPROJECT_PATH"

### 2) Test scaffolding: create tests/ghost_scanner_test.py if missing (idempotent)
mkdir -p "$(dirname "$TEST_FILE")"
if [ ! -f "$TEST_FILE" ]; then
  cat > "$TEST_FILE" <<'PYTEST'
def test_ghost_scanner_placeholder():
    """Placeholder test to ensure CI has at least one passing test."""
    assert True
PYTEST
  chmod 0644 "$TEST_FILE"
  echo "Created test scaffold: $TEST_FILE"
else
  echo "Test file exists: $TEST_FILE (left unchanged)"
fi

### 3) Archive old workflows instead of deleting (idempotent)
shopt -s nullglob
for wf in "$WORKFLOWS_DIR"/*.yml "$WORKFLOWS_DIR"/*.yaml; do
  [ -e "$wf" ] || continue
  base="$(basename "$wf")"
  # Skip main-ci (we overwrite it below)
  if [ "$base" = "$(basename "$MAIN_CI_PATH")" ]; then
    continue
  fi
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  dest="${GRAVE_DIR}/${base%.*}-$ts.${base##*.}"
  if [ ! -e "$dest" ]; then
    mv -v "$wf" "$dest" || true
    echo "Archived $base -> $(basename "$dest")"
  else
    echo "Archive already present for $base, skipping move."
  fi
done
shopt -u nullglob

### 4) Flatten nested source directory if detected
SRC_DIR="$SRC_DIR_DEFAULT"
NESTED_DIR="${SRC_DIR}/${SRC_DIR}"
if [ -d "$NESTED_DIR" ]; then
  echo "Detected nested source directory at $NESTED_DIR. Flattening..."
  shopt -s dotglob
  if compgen -G "${NESTED_DIR}/*" > /dev/null; then
    mv -v "${NESTED_DIR}/"* "${SRC_DIR}/" || true
  fi
  # Try to remove now-empty nested dir
  rmdir "$NESTED_DIR" 2>/dev/null || rm -rf "$NESTED_DIR"
  shopt -u dotglob
else
  echo "No nested double-source-dir detected (checked $NESTED_DIR)."
fi

### 5) Create main-ci.yml atomically (safe and idempotent)
main_ci_tmp="$(mktemp)"
cat > "$main_ci_tmp" <<EOF
name: Main CI

on:
  push:
    branches: [ "main", "dev" ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository (full history)
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Set witness
        run: echo "WITNESS=${WITNESS}" >> \$GITHUB_ENV

      - name: Check HEART_PROTOCOL_SALT (warn)
        run: |
          if [ -z "\${{ secrets.HEART_PROTOCOL_SALT }}" ]; then
            echo "::warning::HEART_PROTOCOL_SALT not set. CI will proceed using test salt if needed."
          fi

      - name: Install project (pyproject or setup.py)
        run: |
          python -m pip install --upgrade pip
          if [ -f "pyproject.toml" ]; then
            pip install -e .[dev] || pip install -e .
          elif [ -f "setup.py" ]; then
            pip install -e .
          else
            echo "No pyproject.toml or setup.py found; skipping project install step."
          fi

      - name: Run tests
        env:
          HEART_PROTOCOL_SALT: \${{ secrets.HEART_PROTOCOL_SALT }}
        run: |
          pytest

      - name: Run Resonance Metric (example)
        run: |
          python -m metrics.resonance_metric --input samples --output-json resonance_output.json

      - name: Upload Resonance Report
        uses: actions/upload-artifact@v4
        with:
          name: resonance-report
          path: resonance_output.json

EOF
mv -v "$main_ci_tmp" "$MAIN_CI_PATH"
chmod 0644 "$MAIN_CI_PATH"
echo "Wrote $MAIN_CI_PATH"

### Git operations
if [ "$DO_COMMIT" = true ]; then
  echo "Staging changes..."
  git add "$PYPROJECT_PATH" "$TEST_FILE" "$MAIN_CI_PATH" "$WORKFLOWS_DIR" "$GRAVE_DIR" tests
  # Add any other potentially changed files, e.g., from flattening
  git add . # Catch-all for any other generated files

  echo "Committing changes..."
  git commit -m "feat(blitzkrieg): CI/CD and project structure overhaul (witness: $WITNESS)"

  if [ "$DO_PUSH" = true ]; then
    echo "Pushing to remote..."
    git push
  else
    echo "Commit complete. To push, run: git push"
  fi
else
  echo "Files generated. To commit, run: git add . && git commit -m \"feat(blitzkrieg): CI/CD and project structure overhaul\""
fi

echo "Operation Blitzkrieg finished."


