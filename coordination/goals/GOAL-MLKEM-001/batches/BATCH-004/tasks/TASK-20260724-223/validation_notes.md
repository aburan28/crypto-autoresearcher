# Validation notes — TASK-20260724-223 / EXP-MLKEM-001

**Verdict:** `accept_with_qualifications` (contract terminal: `passed`). **Blockers:** none.

## Qualifications

1. **Snapshot receipt `commit_sha` is null.** The receipt exists and all declared artifact hashes match tree and commit `0d597dd0a01b78b31a92e568331245be855894d1`, which the dispatch archive block binds after verification. Not an integrity failure of the run package.
2. **Manifests record `dirty_tree: true`.** Expected for producer execution before the snapshot archive; does not invalidate the committed package.
3. **`execution-report.yaml` omits `CTRL-DELIBERATELY-WRONG-INDEPENDENCE`.** The negative control is reported `pass` in `RUN-MLKEM-004/summary.json`.

## Integrity summary

- Exactly four schema-complete terminal runs (`RUN-MLKEM-001`–`004`), all `completed_valid`.
- Source-lock vendor SHA-256 values match pinned commit `75c26949a902ca297b181375bfb7cfaf22cce784`.
- Port fidelity, exact-engine agreement, mass/identity/union controls all reported and spot-checked as pass.
- Budget/scope honored: no n=256, Monte Carlo, rare-event estimation, or deploy interaction.
- Inference: requested `review-xhigh`, resolved `cursor-grok-4.5-high`, `fallback_used: true`.

## Claim boundary

Toy exact-arithmetic audit receipt only. Validation establishes admissibility, not promotion or crypto-scale claims.
