#!/usr/bin/env python3
import json, hashlib, pathlib, datetime

root = pathlib.Path(__file__).resolve().parents[1]
state = root/"memory/state.json"
timeline = root/"memory/timeline.jsonl"
outdir = root/"ci_artifacts"
outdir.mkdir(exist_ok=True)

def sha256(p: pathlib.Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
snapshot = {
    "ts": now,
    "hashes": {
        "state.json": sha256(state),
        "timeline.jsonl": sha256(timeline)
    }
}
(outdir/"witness_snapshot.json").write_text(json.dumps(snapshot, indent=2))
print(f"Snapshot @ {now}")
for k,v in snapshot["hashes"].items():
    print(f"{k}: {v}")
