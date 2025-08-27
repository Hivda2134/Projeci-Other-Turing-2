
#!/usr/bin/env python3
import sys, pathlib, re, json

GHOST_RE = re.compile(r'[\u00ad\u200b-\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]')

TEXT_EXTS = {
    ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".zsh", ".env", ".gitignore",
    ".css", ".scss", ".less", ".html", ".xml",
    ".csv", ".tsv",
}

EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", ".next", ".cache", ".idea", ".vscode", "ci_artifacts", "ci_artifacts_private", ".pytest_cache", "__pycache__"}

def is_probably_text(p: pathlib.Path) -> bool:
    if p.suffix.lower() in TEXT_EXTS:
        return True
    try:
        data = p.read_bytes()[:2048]
        return b"\x00" not in data
    except Exception:
        return False

def iter_text_files(root: pathlib.Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if parts & EXCLUDE_DIRS:
            continue
        if path.stat().st_size > 2 * 1024 * 1024:  # skip >2MB
            continue
        if is_probably_text(path):
            yield path

def main():
    root = pathlib.Path(".").resolve()
    findings = []
    for f in iter_text_files(root):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        matches = [(m.group(0), f"U+{ord(m.group(0)):04X}", m.start()) for m in GHOST_RE.finditer(text)]
        if matches:
            findings.append({"file": str(f), "count": len(matches),
                             "positions": [{"codepoint": m[1], "pos": m[2]} for m in matches]})

    report_path = pathlib.Path("ci_artifacts/ghost_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({"findings": findings}, indent=2), encoding="utf-8")

    if findings:
        print("❌ Ghost characters detected in repository:")
        for item in findings:
            print(f" - {item['file']} (count={item['count']})")
        sys.exit(2)
    else:
        print("✅ Repository is clean (no ghost characters).")
        sys.exit(0)

if __name__ == "__main__":
    main()


