# Analysis: EXP-SEMBIN-d830d5 Stages 0–1 (H-SEMBIN-558848)

Review plan: `experiments/EXP-SEMBIN-d830d5/review/review-plan.yaml`
(`REVIEW-SEMBIN-d830d5-stages01-20261003`), written before this analysis.
Producer: TASK-20261003-c4c9c0. Snapshot archive: TASK-20261003-39b1dc at tip
`2eb03185df843f44a0da4d751ff5a7c7c0a946d9`. Distinguishing outcome target for
this package: **admission-gate pass** → Coordinator `expand` (authorize Stage 2
ladder under a versioned admission amendment). No O-* headline. No C1/C2/C3
support or falsification. No deployed-curve break / exponent / FIPS claim.
Amazon Bedrock NOT SELECTED.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | trial | status | check | outcome |
|-----|-------|--------|-------|---------|
| RUN-SEMBIN-938687 | stage0-feasibility-backend-freeze | completed_valid / output_validated | ok | S0-FREEZE-OK |
| RUN-SEMBIN-0b3eeb | stage1-cap-planted-untyped-smoke | completed_valid / output_validated | ok | SMOKE_PASS |

Each run has `manifest.yaml`, `raw-result.json`, `execution-receipt.json`,
`environment.json`, `command.txt`, `stdout.log`, `check.stdout.log`. Receipts
record `check_returncode: 0`, `returncode: 0`, `status: output_validated`.
`RESULTS.md` matches raw outcomes. `amazon_bedrock: NOT SELECTED` on both
raw-results and manifests. No Magma/Sage/AUXIN success path. Stage 2 is
explicitly **not** admitted (`stage2_admitted: false` on Stage-1 raw-result;
RESULTS.md: "Stage 2 / O-* headline: **not** decided").

**Stage 0 freeze (J2).** `stage0/preregistered-predictions.json` freezes C1
threshold (image_over_finite_k_cap ≥ 0.9 on ≥2/3 cells), C2 cost-reduction
0.2 at three sizes, seeds `{2026091805,2026091806,2026091807}`, cost-model
schema `[setup,search,solver,extract,verify,rank,LA]`, and candidate cells
`{(24,6,3),(30,7,3),(36,8,4)}`. Regime screen (operationalized as
`mk ≤ n−3` and `2^k ≥ 8 m²`):

| (n,k,m) | mk≤n−3 | 2^k≥8m² | feasible |
|---------|--------|---------|----------|
| (24,6,3) | 18≤21 yes | 64≥72 **no** | excluded |
| (30,7,3) | 21≤27 yes | 128≥72 yes | **kept** |
| (36,8,4) | 32≤33 yes | 256≥128 yes | **kept** |

`feasible_cells` in the freeze file and in RUN-SEMBIN-938687 raw-result are
exactly `{(30,7,3),(36,8,4)}`. Primary backend
`pure_python_macaulay_closure` available; `msolve` and `wdsat` unavailable;
no O-IMPEDIMENT (a usable primary exists). Frozen at `2026-10-03T02:29:16Z`
before Stage 1 (`2026-10-03T02:29:17Z`).

**Stage 1 smoke (J3).** On smoke cell `(n,k,m)=(12,4,3)` plus identity rows
over the candidate set:

- `finite-k-cap-identity.json`: `all_identities_hold: true` on four rows
  (24/6/3, 30/7/3, 36/8/4, 12/4/3); each row reports
  `identity_check_ratio_times_correction_equals_m_factorial: true` under the
  EXP-SEMBIN-92724f D1 exact-counting rule.
- `planted-relation-smoke.json`: `ok: true`, `group_law_reassociative: true`,
  `sum_on_curve: true` for a planted m-sum under independent BinaryCurve law
  (explicit note: not a C1/C2 claim).
- `untyped-descend-smoke.json`: `ok: true`, `solve_status: SMOKE_SOLVER_OK`,
  pure-Python GF(2) closure/rank modules import, F2 degree-weight pin
  `w(7)=3` expect 3. Wall clock ~0.18 s.

**Blind re-derivation (cap identity).** From the closed form
`2^{mk} / C(2^k+m−1, m) · ∏_{j=1}^{m−1}(1+j/2^k) = m!` alone (not from
`implementation/run.py`):

| (n,k,m) | product | m! | match |
|---------|---------|----|-------|
| (30,7,3) | 6.0 | 6 | yes |
| (36,8,4) | 24.0 | 24 | yes |
| (12,4,3) | 6.0 | 6 | yes |
| (24,6,3) | 6.0 | 6 | yes |

Agrees with `stage1/finite-k-cap-identity.json`.

## Comparison

Against the frozen Stages 0–1 admission contract
(DEC-20261002-5c465c + AMD-EXP-SEMBIN-d830d5-20261003-admission +
trial-plan-v1):

- Stage 0 required a non-empty feasible subset under HEUR-YT inequalities or
  an O-IMPEDIMENT stop. Observed: two feasible cells, primary backend present
  → S0-FREEZE-OK (matches success path; not impediment).
- Stage 1 required finite-k cap identity, planted group-law check, and
  untyped descend/solver smoke, else O-ARTIFACT. Observed: all three true →
  SMOKE_PASS.
- Against H-SEMBIN-558848 C1/C2/C3: **no comparison is possible**. No typed
  arm, no cost-per-relation ladder, no degenerate/null controls on the Stage-2
  cells, no image_over_finite_k_cap measurement. The smoke cell (12,4,3) fails
  both HEUR-YT clauses (`mk=12 ≰ 9`, `16 ≯≫ 9`).

Predecessor EV-SEMBIN-4614e7 named the missing in-regime + solver-degree
measurement; Stages 0–1 only freeze the cells and smoke the scoring/instrument
path that Stage 2 must use. They do not yet supply that measurement.

## Inference

Compatible readings limited to admission:

1. **Instrument ready for Stage 2.** The pure-Python Macaulay closure path,
   D1 cap identity, and planted verifier smoke are operational on this host
   without Magma/Sage/AUXIN/Bedrock.
2. **Two-cell freeze is a protocol fact, not a C1 result.** C1 asks for ≥2/3
   of ladder cells; with only two frozen cells, Stage 2 can still score C1 on
   that two-cell ladder, but C2's literal "three increasing feasible sizes"
   cannot be met without a third in-regime cell or an explicit C2 re-scope
   amendment.
3. **No scientific direction on H-SEMBIN-558848 yet.** Support, weaken, and
   reject_scoped are all incompatible with the observation set: C1–C3 were
   not tested. Neutral + expand is the only Coordinator transition that matches
   the prior and the data.

Incompatible / rejected readings:

- Reading SMOKE_PASS as O-CONSERVED or as HEUR-YT validation (proves-too-much
  object in the review plan).
- Treating (24,6,3) exclusion as negative evidence against HEUR-YT (it is a
  Stage-0 feasibility screen under a concrete `2^k ≥ 8 m²` cut; the cell was
  never a science measurement).

## Limitation

- Stages 0–1 only; Stage 2 ladder (typed / untyped / degenerate / randomized
  null, cost model, solver degree, Macaulay dimension) was not run.
- Only two of three candidate cells cleared the regime screen; C2 as frozen
  needs a third cell or amendment before a three-size conservation claim can
  be scored.
- Primary backend is pure-Python Macaulay closure; msolve F4 step-degree
  trace and WDSat are unavailable — Stage 2 degree metrics will be
  pure-Python instruments unless backends appear (missing backend →
  O-IMPEDIMENT for that arm, never evidence against C1–C3).
- Coordinator-inline review only (PD-1): no independent validator/red-team
  session on this admission package. Appropriate for instrument readiness;
  Stage 2 claim-changing review must open a full `review_plan` with owned
  joints before any support/weaken/reject_scoped on C1–C3.
- Claim tier remains measurement/toy for any Stage-2 transfer; nothing here
  is a FIPS or deployed-curve statement.
- Tip SHA `2eb03185df843f44a0da4d751ff5a7c7c0a946d9` is the producer/snapshot
  tip cited by the driving session; this analysis does not re-execute trials.
