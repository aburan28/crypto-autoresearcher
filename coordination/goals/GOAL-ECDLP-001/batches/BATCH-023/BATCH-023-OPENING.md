# BATCH-023 OPENING

- **Goal**: GOAL-ECDLP-001 / SG-ECDLP-001 / RQ-ECDLP-002
- **Opened by**: DEC-20260801-007 (2026-08-01)
- **Queue**: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/dispatch_queue.json`
- **Experiment**: EXP-EQD-001 (frozen at TASK-20260801-019, status `review_required`)
- **Hypothesis**: H-EQD-001 (status `specified`, NOT approved)
- **Budget**: twenty-third of 50 batches under BUDGET-AMEND-20260730-001. No pause
  condition fires; GOAL-ECDLP-001 stays `active`.

## What closed

BATCH-022 closed as an **RC-22 NON-EXECUTION** on EXP-SMTH-001. The independent
review REV-20260801-012 returned REVISE and TASK-20260801-013 recorded
APPROVAL_DETERMINATION NOT APPROVED. Two fatal defects, both demonstrated before
any compute:

- **RV012-A1** — TAIL-DS-1 fails on a *correct* null. `p_ext = min_j rho(u_j)`
  makes `n * p_ext` asymptotically Exp(1), so the analytic pass probability is
  `1/e`, not the `1 - 1/e` the contract asserted; the reviewer measured the
  declared null arm passing 0 of 8 at bits 16 and 0 of 8 at bits 20. M-1, M-2,
  M-4 and M-6 were jointly unreachable.
- **RV012-A2** — the leading coefficient of `S_3` in `Z` is `(x_1 - x_2)^2`, zero
  exactly on the diagonal, so ENC-B was undefined on 512 of the 131328 enumerated
  half-tuples; dropping them leaves 130816 and M-0 fired on every outcome.

This is a **contract-design failure caught before compute**. It is *not* a
mathematical result about HEUR-DS-1 in either direction and it is *not* an
infrastructure failure. H-SMTH-001 does not move and stays `specified`. No
evidence record is filed, because no run exists.

The attainability duty, introduced at BATCH-022 in response to BATCH-021, caught
both defects on its **first use** for about two minutes of CPU. It is retained
and extended by AP-2 and ATS-1.

## What opened

EXP-EQD-001 measures the **joint law of the half-arity Semaev fibre invariants
`(e_1, e_2)` directly**, against a **matched random-factor-base null**, with every
threshold a stated order statistic of a **measured** null distribution under a rule
frozen before the calibration ran, and with the rejection side of every substantive
branch certified by a **measured** power curve against pre-declared planted
deviations. No factorization, no Dickman model, no smoothness statistic, no search,
no timing, no cost identity, no R.

Calibration-first lifecycle: 019 author → 020 snapshot (CALIBRATION_AUTHORIZATION)
→ 021 driver + RUN-EQD-001-calib (null and planted objects only) → 022 snapshot
(binds DRIVER_SHA256) → **032 independent validation of the calibration package** →
023 freeze RR-EQD-1 + ATTAIN-RR-EQD-1 against the measured
null, or record CAL-STOP-1 → 024 snapshot → 025 independent review (attainability
duty **and** ATS-1 anti-tuning duty, each with its own deliverable file) → 026
approval snapshot (APPROVAL_DETERMINATION) → 027 RUN-EQD-001-real → 028 snapshot →
029 Validator → 030 Red Team → 031 ledger.

**No run is authorized by this opening.** The calibration and the real arm are
gated on two separate receipts.

TASK-20260801-032 is inserted at a free id rather than by renumbering, because the
contract names 023, 025, 026, 027 and 029 by number and is not edited to follow a
queue. Its number is the highest in the batch and it runs between 022 and 023; the
`depends_on` edges carry the order, not the ids. It exists because the calibration
being *non-evidential about every hypothesis* is not the same thing as its needing no
integrity check — every threshold in the batch is an order statistic of the CAL-1
output, so a defect there would produce a reading rule whose numbers look traceable
and are wrong. 025 asks whether the calibration *tuned*; 032 asks whether it is
*sound*.

## Scope

Toy ceiling. Limb **L2** only. Limb **L1** — that `(e_1, e_2)` is not uniform on
`F_p x F_p`, admissible-support density about 1/8 — is a **derivation**, never a
finding of this batch. Limb **L3** is instrument characterization. Equidistribution
of the fibre invariants is a **load-bearing input** to HEUR-DS-1 and is **not
identical** to it; nothing here validates or refutes HEUR-DS-1 at any tier, and the
direct smoothness measurement remains **owed** (OPEN-BATCH023-A).

Forbidden throughout: `support`, S1_met, F1_met, F2_met, structure_gate_passed,
asymptotic promotion, reject_scoped-as-impossibility, `dominated_by: null`. Gates
G1–G4 stay OPEN. EXP-SMTH-001 and every EXP-DS-001 artifact are untouched; H-DS-001,
H-IC-001, H-STR-002 and H-SMTH-001 are unaltered; FAEST and XEDN are left alone.

## Standing harness caveat

Under this harness the authoring and reviewing sessions both resolve to
`claude-opus-5`. Reviews here are independent in the AGENTS.md sense but **not** in
the model sense, and none is admissible toward the three-model closure quorum of
AGENTS.md rule 13.
