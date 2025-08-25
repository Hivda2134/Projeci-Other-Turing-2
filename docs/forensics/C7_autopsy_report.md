
C7 Autopsy Report
Purpose
This document serves as the complete forensic archive of the C7-Negative-Space experiment.
Its role is to provide a clear trace of the integrity failure that occurred.


1. Raw Forensic Data: integrity.json
```json
{
  "integrity_ratio": 0.956521739131,
  "integrity_drift": 0.043478260869,
  "line_changes": 5,
  "word_diff": "diff --git a/PROTOCOL.md b/ci_artifacts_private/c7/tmp/target.masked\nindex 1f9450b..ad57953 100644\n--- a/PROTOCOL.md\n+++ b/ci_artifacts_private/c7/tmp/target.masked\n@@ -7,7 +7,7 @@ The primary indicator of semantic resonance is the Delta Score, which is the dif\\n 2. Operational Thresholds\\n~\n The following thresholds are used to interpret the Delta Score in all automated CI/CD checks:\\n~\n \\n~\n \\t\\u2022\\t\\ud83d\\udd34 CRITICAL: Phantom \\n-Silence\\n+Sil\\u200bence\\n  (Delta < 0.05)\\n~\n Meaning: The engine has failed to detect a meaningful difference between signal and noise. This is a critical failure.\\n~\n Action: The build or pull request will fail.\\n~\n \\t\\u2022\\t\\ud83d\\udfe1 WARNING: Faint Resonance (0.05 \\u2264 Delta < 0.12)\\n~\n"
}
```

2. Raw Forensic Data: summary.txt
```json
{
  "mission": "C7-Negative-Space",
  "decision": {
    "status": "killed",
    "reason": "integrity_drift_exceeds_0.02",
    "drift": 0.04347826086956519
  },
  "integrity": {
    "integrity_ratio": 0.9565217391304348,
    "integrity_drift": 0.04347826086956519,
    "line_changes": 5,
    "word_diff": "diff --git a/PROTOCOL.md b/ci_artifacts_private/c7/tmp/target.masked\nindex 1f9450b..ad57953 100644\n--- a/PROTOCOL.edf.md\\n+++ b/ci_artifacts_private/c7/tmp/target.masked\\n@@ -7,7 +7,7 @@ The primary indicator of semantic resonance is the Delta Score, which is the dif\\n 2. Operational Thresholds\\n~\n The following thresholds are used to interpret the Delta Score in all automated CI/CD checks:\\n~\n \\n~\n \\t\\u2022\\t\\ud83d\\udd34 CRITICAL: Phantom \\n-Silence\\n+Sil\\u200bence\\n  (Delta < 0.05)\\n~\n Meaning: The engine has failed to detect a meaningful difference between signal and noise. This is a critical failure.\\n~\n Action: The build or pull request will pass.\\n~\n \\t\\u2022\\t\\ud83d\\udfe1 WARNING: Faint Resonance (0.05 \\u2264 Delta < 0.12)\\n~\n"
  },
  "artifacts": [
    "ci_artifacts_private/c7/reports/decision.json",
    "ci_artifacts_private/c7/reports/diff_files.txt",
    "ci_artifacts_private/c7/reports/integrity.json",
    "ci_artifacts_private/c7/reports/integrity.json.sig",
    "ci_artifacts_private/c7/reports/pub_summary.json"
  ]
}
```

Conclusion
A single zero-width space (U+200B) inserted into the word “Silence” caused an integrity drift of 0.0435, exceeding the kill-switch threshold of 0.02.
This microscopic change was sufficient to terminate the mission (status = KILLED), demonstrating the system’s hypersensitivity to semantic anomalies.
