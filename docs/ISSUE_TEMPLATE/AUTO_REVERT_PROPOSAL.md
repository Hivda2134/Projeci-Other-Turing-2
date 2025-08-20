---
name: Auto-Revert Proposal
about: Automatically generated proposal to revert changes due to Resonance Guard failure.
title: "[AUTO-REVERT] Resonance Guard Failure: "
labels: "bug, auto-revert, resonance-guard"
assignees: ''
---

## Resonance Guard Failure Detected

This issue has been automatically created because a recent push/PR failed the Resonance Guard check. The changes introduced a significant deviation from the project's established code resonance, indicating a potential misalignment with core principles or an unintended security risk.

**Reason for Failure:**

- **Resonance Score Below Threshold:** The calculated resonance score for the affected changes was below the configured `alert_threshold`.
- **Toxic Signal Detected:** One or more toxic signals were detected in the changes, indicating a potential security or privacy violation.

## Details of the Incident

**Commit/PR:** [Link to failing commit/PR]

**Affected Files:**
```
[List of affected files and their resonance/toxic scores]
```

**Observed Resonance Score:** `[Observed Score]`
**Configured Threshold:** `[Threshold Used]`
**Toxic Signals Detected:** `[List of detected toxic signals, if any]`

## Proposed Remediation: Automatic Revert

To maintain the integrity and security of the codebase, we propose an automatic revert of the failing changes. This action is critical to prevent the introduction of non-resonant or potentially harmful code.

**Revert Command (Example):**

```bash
git revert [Failing Commit SHA]
```

## Next Steps

1.  **Review:** A maintainer should review this issue and the proposed revert.
2.  **Approve/Execute Revert:** If approved, the revert should be executed.
3.  **Investigation:** Investigate the root cause of the resonance degradation or toxic signal detection. This may involve:
    -   Refining the `toxic_signals.yml` configuration.
    -   Retraining the ML toxic gate if false positives are suspected.
    -   Adjusting the `alert_threshold` if the project's resonance naturally shifted.
    -   Educating contributors on code resonance principles.

## Important Notes

-   This is an automated action. Please do not close this issue without addressing the underlying cause.
-   Further details about the Resonance Guard and its operation can be found in `docs/SECURITY.md` and `docs/USER_GUIDE_QUICK_START.md`.


