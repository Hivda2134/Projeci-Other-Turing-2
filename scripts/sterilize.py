
#!/usr/bin/env python3
import unicodedata, sys, pathlib, re, argparse, json, difflib

# Broad set of invisible/control-like characters:
# - U+00AD SOFT HYPHEN
# - U+200B..U+200F ZWSP..RLM
# - U+202A..U+202E Bidi Embedding/Override
# - U+2060 WORD JOINER
# - U+2066..U+2069 LRI/RLI/FSI/PDI (isolate)
# - U+FEFF ZERO WIDTH NO-BREAK SPACE (BOM)
GHOST_RE = re.compile(r'[\u00ad\u200b-\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]')

def sterilize_text(text: str, form: str = 'NFC'):
    normalized = unicodedata.normalize(form, text)
    cleaned = GHOST_RE.sub('', normalized)
    return cleaned, normalized

def make_diff(original: str, cleaned: str, path: str):
    if original == cleaned:
        return ""
    a = original.splitlines(keepends=True)
    b = cleaned.splitlines(keepends=True)
    diff = difflib.unified_diff(a, b, fromfile=path, tofile=f"{path} (sterilized)")
    return ''.join(diff)

def scan_ghosts(text: str):
    found = [(m.group(0), f"U+{ord(m.group(0)):04X}", m.start()) for m in GHOST_RE.finditer(text)]
    return found

def main():
    ap = argparse.ArgumentParser(description="Sterilize text files against invisible/ghost Unicode chars.")
    ap.add_argument("src", help="Source file path")
    ap.add_argument("dst", help="Destination file path (can be same as src)")
    ap.add_argument("--nfkc", action="store_true", help="Use NFKC normalization instead of NFC")
    ap.add_argument("--report-dir", default="ci_artifacts/sterilize_reports", help="Directory to write reports")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    dst = pathlib.Path(args.dst)
    report_dir = pathlib.Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    text = src.read_text(encoding="utf-8")
    form = 'NFKC' if args.nfkc else 'NFC'
    cleaned, normalized = sterilize_text(text, form=form)

    ghosts_before = scan_ghosts(text)
    ghosts_after = scan_ghosts(cleaned)
    diff_text = make_diff(text, cleaned, str(src))

    report = {
        "file": str(src),
        "normalization": form,
        "changed": text != cleaned,
        "ghosts_before_count": len(ghosts_before),
        "ghosts_after_count": len(ghosts_after),
        "ghosts_before": [{"char": g[0], "codepoint": g[1], "pos": g[2]} for g in ghosts_before],
        "ghosts_after": [{"char": g[0], "codepoint": g[1], "pos": g[2]} for g in ghosts_after],
    }
    (report_dir / (src.name + ".json")).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if diff_text:
        (report_dir / (src.name + ".diff")).write_text(diff_text, encoding="utf-8")

    dst.write_text(cleaned, encoding="utf-8")

    if ghosts_after:
        print(f"❌ Residual ghosts remain in {src} after sterilization.", file=sys.stderr)
        sys.exit(3)
    else:
        print(f"✅ Sterilized {src} -> {dst} [{form}], changes: {text != cleaned}")
        sys.exit(0)

if __name__ == "__main__":
    main()


