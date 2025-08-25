OPA-v1 — Observer Protocol Addendum (C7 scope)
Purpose: Define allowed interventions, auditing, and kill-switch logic for Negative Space tests.
Rules:
• Allowed transforms: bounded-drift deterministic masking (alpha,beta ≤ 0.01), optional clover_density ≤ 0.001.
• Audit: every intervention emits .sig with {engine, seed, params, src, dst, ts, original_sha256}; ledger is JSONL.
• Kill-switch: abort if integrity_drift > 0.02 or detection_alert >= threshold.
• No network; private artifacts only; dual approval required for any merge to main.


