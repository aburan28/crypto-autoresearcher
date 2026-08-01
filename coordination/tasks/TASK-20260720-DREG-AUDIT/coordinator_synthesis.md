# Coordinator synthesis — DREG n=17 audit (TASK-20260720-DREG-AUDIT)

Integrates the two independent audit reports in this directory with the
EXP-SIG-005 cascade evidence produced the same thread. Official status is set in
`ledger/DEC-20260720-002.yaml` (H-DREG-001) and `ledger/DEC-20260720-001.yaml`
(H-SIG-001).

## Inputs
- `validation_report.yaml` / `validation_notes.md` — Validator (VAL-20260720-DREG-AUDIT)
- `red_team_report.md` — Red Team
- `ledger/EV-SIG-005.yaml` — the D≤5 cascade extension + the D6 null-control failure

## What the audit established

1. **Receipt integrity: VERIFIED.** The Validator recomputed 9 sha256 hashes and
   reconstructed every rank from per-unit pivot ledgers; the n=17 sem
   (rank 125099 / sr_pred 126922 / deficit 1823) and null (rank==sr_pred 126922 /
   deficit 0) two-partition gates reproduce exactly, no defects. The n=17 numbers
   are real.

2. **The 1823 is a fixed-degree (D=5) deficit, not a d_reg measurement.** Both
   arms sit below full row rank at D=5 (125099, 126922 < 132719), so
   `d_reg(sem) < d_reg(null)` is not evaluable from any current cell.

3. **The "non-monotone dip" at n=17 is an off-lattice artifact.** n=17 ≡ 2 mod 3;
   the SIG cascade laws live on n ≡ 0 mod 3. On the lattice the D5 deficit is
   monotone increasing (909/1322/1862/1999 at n=9/12/15/18). The
   "relative-deficit → 0" plank is near-tautological (rank ~ n^5) and is not the
   d_reg-relevant invariant.

4. **The n-axis speedup case is quantitatively empty.** Linear D4 law confirmed
   to n=24; non-monotone D5 (residual_5 drops at n=18, replicated); no measured
   syzygy quantity is super-linear in n.

5. **The degree axis was the only live route — and it is not validly measured.**
   The Red-Team correctly named the degree axis as the remaining open direction
   and cautiously weighed the n=9 D6 data. This Coordinator's EXP-SIG-005 D6 run
   then showed that D6 data is invalid: the null control fails (sem/null differ in
   column count; sr_pred matches neither; null extra/residual ≠ 0). So **both**
   the residual_6 "explosion" **and** the deficit_6 "turnover" are inadmissible —
   the degree axis is unmeasured past D=5.

## Reconciliation of the two auditors

- Validator (integrity) and Red-Team (interpretation) do not conflict; the
  Red-Team explicitly takes the Validator's verified numbers as given.
- The one place the Red-Team had to hedge — the n=9 D6 "deficit turnover"
  (909→776) as a weak anti-speedup signal — is resolved by the new D6 null-control
  failure: that turnover is an artifact of the broken D6 baseline and carries no
  weight. This **removes** a caveat from the Red-Team's reasoning and leaves its
  recommended verdict intact and cleaner.

## Verdict (Coordinator)

- **H-DREG-001: INCONCLUSIVE, trending WEAKENED.** No generic prime-field ECDLP
  speedup is demonstrated. The n-axis is empty; the degree axis is unmeasured
  (broken instrument); d_reg is unreached. A scoped KILL is **not** earned
  (the KILL clause requires a d_reg comparison that no cell provides — AGENTS
  rule 6).
- **H-SIG-001: supported_scoped**, sharpened at D≤5 (2n/3+1 confirmed to n=24) and
  scope-bounded (D6 birth-law claim retracted as invalid).

## Highest-value next measurement (with prerequisite)

The Red-Team's #1 — the **D=6 rank deficit at n=12 (standard, on-lattice) on the
DREG block-m4ri instrument** (first non-anomalous degree-axis test; first chance
at an actual d_reg datum) — now has a hard **prerequisite**: repair the D6
semi-regular null (support-match its column set to the sem arm; recalibrate
sr_pred). Until that repair, no D6 non-rewritability/deficit/birth-law claim is
admissible on either instrument.

Secondary: replicate the DREG deficit across ≥3 curves/seeds at n=12,15
(currently single-seed 2026); measure the d_ff/d_reg first-fall ladder (the
hypothesis's own gap(n) metric, currently 2 samples).

## Infrastructure note

The host root disk reached 100% (ENOSPC) mid-thread, censoring the n=21 D5
deficit and the n=12 D6-null replication (AGENTS rule 5 — not evidence). Free
host disk / relocate Sage TMPDIR to the data volume before the next heavy batch.
