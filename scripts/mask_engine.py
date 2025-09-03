
#!/usr/bin/env python3
import hashlib, json, os, random
from datetime import datetime
from typing import Dict

def _rng(seed:int)->random.Random:
    r = random.Random()
    r.seed(seed)
    return r

def compute_signature(data_bytes: bytes) -> str:
    return hashlib.sha256(data_bytes).hexdigest()

def write_signature(sig_path: str, context: Dict):
    ctx = dict(context)
    # Attach UTC timestamp and original file hash if available
    ctx["ts"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    src = ctx.get("src")
    if src and os.path.exists(src):
        try:
            with open(src, "rb") as f: ctx["original_sha256"] = compute_signature(f.read())
        except Exception:
            ctx["original_sha256"] = None
    ctx_bytes = json.dumps(ctx, sort_keys=True).encode("utf-8")
    sig_hex = compute_signature(ctx_bytes)
    payload = {"sig": sig_hex, "context": ctx}
    os.makedirs(os.path.dirname(sig_path), exist_ok=True)
    with open(sig_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, sort_keys=True)
        f.write("\n")

def _benign_jitter(text: str, alpha: float, beta: float, r: random.Random) -> str:
    # Tiny whitespace/spacing jitter; zero-widths as covert carrier
    alpha = max(0.0, min(alpha, 0.01))
    beta  = max(0.0, min(beta,  0.01))
    out = []
    for ch in text:
        out.append(ch)
        if ch in ".;,!?":
            if r.random() < alpha: out.append(" ")
        if ch == " " and r.random() < alpha/2: out.append(" ")
        if r.random() < beta:
            out.append("\u200b" if r.randint(0,1)==0 else "\u200c")  # ZW space / non-joiner
    return "".join(out)

def _clover_overlay(text: str, r: random.Random, density: float=0.0) -> str:
    # Replace visible 🍀 with sparse zero-widths (bit-level ghost signature)
    if density <= 0: return text
    out=[]
    for ch in text:
        out.append(ch)
        if ch == "\n" and r.random() < density:
            out.append("\u200b")  # invisible marker
    return "".join(out)

def mask_text(text: str, *, alpha: float=0.002, beta: float=0.002, seed: int=42, clover_density: float=0.0) -> str:
    r = _rng(seed)
    t = _benign_jitter(text, alpha, beta, r)
    if clover_density > 0: t = _clover_overlay(t, r, clover_density)
    return t

def mask_file(path_in: str, path_out: str, *, alpha: float=0.002, beta: float=0.002, seed: int=42, clover_density: float=0.0):
    with open(path_in, "r", encoding="utf-8") as fin:
        data = fin.read()
    masked = mask_text(data, alpha=alpha, beta=beta, seed=seed, clover_density=clover_density)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    with open(path_out, "w", encoding="utf-8") as fout:
        fout.write(masked)
    sig_ctx = {
        "engine": "K2-mask",
        "alpha": alpha, "beta": beta,
        "seed": seed, "clover_density": clover_density,
        "src": os.path.abspath(path_in),
        "dst": os.path.abspath(path_out)
    }
    write_signature(path_out + ".sig", sig_ctx)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--alpha", type=float, default=0.002)
    ap.add_argument("--beta", type=float, default=0.002)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--clover-density", type=float, default=0.0)
    args = ap.parse_args()
    mask_file(args.inp, args.out, alpha=args.alpha, beta=args.beta, seed=args.seed, clover_density=args.clover_density)


