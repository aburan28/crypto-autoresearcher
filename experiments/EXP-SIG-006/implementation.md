# EXP-SIG-006 implementation

Instrument: bit-identical copies of the pinned EXP-SIG-001..005 set in `src/`
(sha256 verified against the pinned values in every run receipt):
`h013_f5_signatures.sage`, `semaev_tree.py`, `ic_first_fall_fast.py`,
`macaulay_export.py`. The instrument is loaded, never modified. All new code
lives in `scripts/`.

## Scripts

- `scripts/diag_d6_null.sage` (Phase A, RUN-a): rebuilds the n=9 seed=1 sem +
  old null; verifies receipt ncols at D3..D6; proves the column-formation law
  (exact row enumeration vs simple up-closure-with-slack coverage, zero parity
  deviation); characterizes the missing monomials by (degree, block
  composition); enumerates both varieties over all 2^18 points (numpy parity);
  reproduces the pinned sr_pred series semantics (code loop == formal
  (1+z)^nb/Π(1+z^{d_i}) truncated-positive == receipts; Bardet textbook series
  for contrast); freeze degrees per n; fall arithmetic from column degrees +
  receipt ranks.
- `scripts/sig6_nulls.sage` (Phase B, RUN-b): corrected-null candidates N0
  (pinned old null, determinism rerun) and N2 (forced vanishing at a seeded
  random z), safe-pool construction + 60 rejection trials for the
  column-matched N1 (failed — recorded), per-null D3..D6 validation gates
  (extra=0, rank==sr_pred, rank==ncols−|V|, kernel identities), |V| per null.
- `scripts/sig6_n1_repair.sage` (Phase B2, RUN-c/RUN-d): N1 column-matched
  null by construction — safe pools (monomials whose D6 sextic up-closure
  stays inside the sem's D6 sextics), forced classes taken wholesale, free
  classes by seeded greedy set-cover, local swap repair until the D6 column
  set equals the sem's EXACTLY (RUN-d: donor filter requires s in upset; 5
  repairs). Then D3..D6 validation + |V|.
- `scripts/SIG6_run.sage` (Phase C, RUN-e/RUN-f): verbatim copy of the
  EXP-SIG-005 p2 driver (experiment id string edited) — sem D6 closure cell
  (A3_6/A4_6/A5, residual_6) with per-stage flush, soft cap, and SIGALRM
  stage censoring. RUN-f used soft-cap 250 s so the crosscheck censors
  cleanly inside the 300 s platform call cap.

## Runs

- RUN-a: diagnosis (valid).
- RUN-b: N0/N2 validation (valid; both FAIL D6 — the clean finding).
- RUN-c: N1 v1, 5 sextics short of exact column equality (superseded; retained).
- RUN-d: N1 v2, exact column equality; validation FAIL at D5 (369) and D6.
- RUN-e: sem reproduction attempt killed at 300 s platform cap (infrastructure;
  D6 classification numbers reproduced exactly; superseded by RUN-f).
- RUN-f: full sem closure reproduction (valid; crosscheck deliberately
  censored; all values == RUN-EXP-SIG-005-h).

Semantics notes: boolean monomials are frozensets; GF(2) bitmask echelon with
transformation tracking (pinned); `full_reduce` canonical reduction copied
verbatim from EXP-SIG-003 (inside the p2 driver); variety enumeration is a
numpy parity count over all 2^18 boolean points (exact, nb = 18).
