# Analysis — EXP-BINSTD-ffc4f4 Stages 0–1

Hypothesis: `H-BINSTD-39a59f`. Predecessor: `EXP-BINSTD-6c199f` /
`EV-BINSTD-78ca0d` / `DEC-20261003-9575fd` (weaken; O-FAIL-BAND median 1.0
vs band ≤0.90; catalog_seed 2026100327). Approval: `DEC-20261003-d4ae67`.
Producer: `TASK-20261003-b12bea` on `cursor/run-binstd-ffc4f4-stages01-ed0c`
tip `88c0909e0cef1724735a37cbf8399519380bd319`. Review plan:
`experiments/EXP-BINSTD-ffc4f4/review/review-plan.yaml` (written before this
file). No Stage-2. Parent EXP not re-run. No Bedrock / AUXIN. No break /
exponent / n≥131 transfer.

## Observation

Two authorized trial-plan-v1 runs completed and re-verified before any
band reading:

| run | stage | receipt | check.py | outcome |
|---|---|---|---|---|
| `RUN-BINSTD-27c203` | 0 | `output_validated`, certificate.kind=`none` | OK | `O-STAGE0-OK`, `twin_ok=true` |
| `RUN-BINSTD-4e4565` | 1 | `output_validated`, certificate.kind=`none` | OK | producer label `O-FAIL-BAND` |

Expected run count is 2/2 (trial-plan trials `stage0-disjoint-catalog-freeze`
and `stage1-replication-n17-l3`). No Stage-2 artifacts exist
(`stage2/gp-panels.json` / `stage2/null-panels.json` absent). `n_runs=2`
≤ `maximum_runs=4`. Manifest envelopes are schema-complete (`manifest.yaml`
plus additive `manifest_v2.yaml`). Execution-receipt SHA-256 values match
the on-disk companions for both runs. Frozen `specification.yaml` SHA-256
`0dbe5cd1a6e5fb41fe630e76d6c7fec3a16940c2190a7b73910b2d8129219911` matches
`trial-plan-v1.json`; implementation source hashes match the trial-plan
pin. `trial-plan.json` is byte-identical to `trial-plan-v1.json`.
`amazon_bedrock: NOT_USED`. `claims.break=false`.
`claims.exponent_move=false`.

Stage 0 freeze (`stage0/preregistered-predictions.json`): δ=0.10 →
band_upper=0.90; ε=0.15 specified not run; catalog_seed **2026100331**;
parent seed **2026100327 unused**; GP seeds
`{35,37,39,41,43,45,49,51,53,57,59,65}` with empty intersection against
the forbidden parent roster `{3,5,7,9,11,13,17,19,21,25,27,33}`. Independent
`check.py` Stage-0 probe agrees with `v-catalog.json` gp_catalog[0] and
refuses parent-seed reuse.

Stage 1 cell (n,ℓ)=(17,3): 12 matched pairs (min 8). Every pair has
`twin_ok=true` and `|Δ dimVV|=1` (GP dimVV=5, rand dimVV=6). Control table
`twin_fail=false`.

Blind re-derivation of the load-bearing quantity from
`stage1/panels.json` pair rows only (review-plan `blind_rederivation`;
producer `RESULTS.md` / control-table / Stage-1 raw-result summary not
used as inputs):

ratios = `[1.0, 0.666…, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.0, 1.0, 1.0, 1.0]`

median = **1.0** (exact median of 12 values). band_upper=0.90;
`1.0 ≤ 0.90` is false → preregistered **O-FAIL-BAND**. Polarity among
pairs: 1 ratio <1, 10 ratios =1, 1 ratio =1.2. Mean ≈ 0.989. After the
recompute, producer summaries agree: `panels.json` /
`control-table.json` / `RESULTS.md` / `RUN-BINSTD-4e4565/raw-result.json`
all report matched=12, median=1.0, `in_band=false`,
outcome `O-FAIL-BAND`.

No discrete_log / decomposition / key_recovery certificate applies
(`kind: none`). This is a measurement package.

## Comparison

Parent `EV-BINSTD-78ca0d` (`EXP-BINSTD-6c199f`, catalog_seed 2026100327,
12 matched pairs, twin OK): median **1.0** vs band ≤0.90, official
**weaken** at strength **preliminary** (unreplicated empirical_only).
Pair polarity there: 1 ratio <1, 7 =1, 4 =1.2.

This package uses a **disjoint** catalog and GP roster, does not re-run
the frozen parent EXP, and measures the same cell (17,3), same δ=0.10,
same match rule, same twin meters, same shared encoder pin. Median is
again **1.0** vs ≤0.90 with 12 matched pairs and twin OK. The producer
O-FAIL-BAND label therefore independently confirms the parent
observation at this toy cell; it is not a re-score of the parent pairs.

Both catalogs sit entirely on the match-edge GP dimVV=5 vs rand dimVV=6
(exact dimVV equality not observed). Pair-level polarity is not
identical (this catalog has more exact-1.0 ratios and only one 1.2),
but the **median** — the preregistered decision statistic — matches.

Stage-2 n∈{19,23} GP/random + random-vs-random null (ε=0.15) remains
specified in-contract and **not run** (trial-plan-v1). Absence is not a
null result.

## Inference

The Stages 0–1 package is valid. HEUR-BINSTD-adb7bb-H1's Stage-1
prediction (median N_var(GP)/N_var(rand) ≤ 0.90 at (17,3) under the
disjoint catalog) fails again at the declared toy scope. Official
producer label O-FAIL-BAND is retained as observation; Coordinator
decision is **weaken** of that heuristic at this cell, with evidence
strength **replicated** because the parent O-FAIL-BAND (median 1.0 vs
≤0.90, 12 pairs, twin OK) is independently reproduced under catalog_seed
2026100331.

`reject_scoped` is **not** used: the refutation basis is declared
`empirical_only` (no counterexample certificate beyond the measured
panels; no derivation that leftover GP structure cannot leave residual
encode advantage after dimVV matching). The user-bound for this review
forbids `reject_scoped` without a checkable refutation artifact that is
itself replicated. Unreplicated empirical-only would have stayed
weaken+replication; this tick *is* that replication, and still stays
**weaken** rather than scoped rejection because the proof_status is
empirical_only.

`support` is forbidden: the ≤0.90 band did not hold. `inconclusive` is
not applicable: matched≥8, twins OK, median vs band is decided.
Hypothesis `H-BINSTD-39a59f` / experiment `EXP-BINSTD-ffc4f4` move
approved → **analyzed**. No break; no exponent; no n≥131 transfer.

## Limitation

- Toy n=17, ℓ=3 only. Transfer of O-FAIL-BAND to n≥131 is an
  **unvalidated non-claim**.
- Stage-2 random-vs-random null (the declared encoder-artifact
  separator) was not authorized and was not run.
- All 12 pairs remain at |Δ dimVV|=1 (5 vs 6); exact product-dimension
  equality is untested on this catalog too.
- Shared XOR-SAT encoder pin; a different pin needs a new contract.
- Coordinator-inline review (PD-1): no independent validator/red-team
  session. Strength is replicated on the **measurement** (disjoint
  catalog vs parent), not `strong`.
- certificate.kind=`none`. Mean ratio is not the decision statistic.
- No KN-FIND: toy replication of a weaken; decision is not
  `support`/`reject_scoped`.
