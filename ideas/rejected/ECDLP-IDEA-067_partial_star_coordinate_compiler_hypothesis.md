# ECDLP-IDEA-067 — Partial-star coordinate compiler

## Status and claim labels

- Class: `composition`
- Risk band: `conservative`
- State: `rejected_merged`
- Evidence scale: `toy` model derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with ledger `ECFG-H686/H643/H674`
- Breakthrough claim: **none**; smaller fixed-curve advice or faster online queries are not a single-target break.

## Falsifiable hypothesis

A coordinate evaluation code attached to a fixed `(E,P)` has partial-star product
dimension `N^(s+o(1))` with a local reconstruction map that compiles all factor-base
addition queries into advice smaller than the generic fixed-base `S*T^2` frontier. The
compiler preserves exact sources, amortizes relation collection and masked target descent,
and beats rho and BSGS after all offline advice, memory, and query costs.

## Mechanism-new operation

The proposed operation was a **coordinate partial-star/additive-expansion theorem with
source-local reconstruction**. Semantic review found this is the explicit open object in
ledger `ECFG-H686`, while `ECFG-H643/H674` already define and cost the fixed-curve
compiler. Attaching code vocabulary supplies no new mathematical operation.

## Assumptions

1. One fixed public curve/base pair serves many targets under a preregistered amortization model.
2. The coordinate code and partial-star space are constructed without scalar labels.
3. Local reconstruction returns endpoint sources, not only membership bits.
4. Advice size, construction, all target queries, calibration, descent, verification, and memory are charged against generic tradeoffs.
5. The same theorem holds on fresh curves or the claim is explicitly model-bound to fixed-curve reuse.
6. No post-hoc selector, explicit pair table, or omitted preprocessing is permitted.
7. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`fixed_curve_coordinate_code | partial_star_dimension | local_source_reconstruction | compiled_addition_advice | many_target_tradeoff`

Collision fingerprint: `ECFG_H686_coordinate_partial_star | ECFG_H643_fixed_curve_compiler | ECFG_H674_generic_frontier`. The candidate is not mechanism-new.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H643`, the closest fixed-curve compilation/advice lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H674`, the closest coordinate-code query compiler.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H686`, which records the same partial-star preprocessing theorem gap.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H685`, the adjacent online-query versus stored-state control.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H683`, the adjacent coordinate-advice representation boundary.

## Closest primary literature

- Couvreur, Gaborit, Gauthier-Umaña, Otmani, and Tillich, [Distinguisher-based attacks on public-key cryptosystems using Reed–Solomon codes](https://arxiv.org/abs/1307.6458), supplies star-product code structure in a different cryptographic setting.
- Guruswami and Kopparty, [Explicit subspace designs](https://doi.org/10.1007/s00493-014-3169-1), supplies limited-intersection linear spaces, not elliptic source reconstruction.
- Corrigan-Gibbs and Kogan, [The discrete-logarithm problem with preprocessing](https://eprint.iacr.org/2017/1113), supplies the fixed-base preprocessing tradeoff used here.

No source supplies the claimed elliptic partial-star theorem; the ledger already records
the same missing theorem, so novelty is unverified and the proposal is merged.

## Complete factor-base-to-target-descent path

1. Freeze `(E,P)`, amortization count, coordinate code, factor base, and generic tradeoff baseline.
2. Construct the partial-star advice without scalar labels.
3. Prove each local answer lifts to exact endpoint sources.
4. Collect and verify factor-base relations across the frozen target batch.
5. Calibrate and verify every factor-base log.
6. Query randomized masked targets through the same advice.
7. Recover source-labelled descents and candidate scalars.
8. Verify every recovered scalar on its target curve.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` per target; BSGS costs `N^(1/2+o(1))` time and memory.
Let advice size/construction be `S=N^s`, online time `T=N^t`, targets `D=N^d`, and
peak memory `N^mu`. Charge amortized construction exponent `s-d`, online exponent `t`,
and unamortized peak memory `mu`; peak memory is not divided by the target count. Compare
the unamortized point `(S,T)` to `S*T^2=Omega(epsilon*N)`.
Relation calibration and descent are included in `S,T`; a favorable subtotal is not a win.

## Likely fatal obstruction

The coordinate code's useful star-product space can have dimension comparable to the
full pair table, and local reconstruction can be the original ECDLP orientation problem.
Any smaller advice/query pair is already bounded by generic fixed-base tradeoffs. This is
the exact obstruction named in the existing ledger entries.

## Proof track

Prove a coordinate partial-star dimension and source-reconstruction theorem, then show its
complete `(S,T,D,mu)` point lies strictly beyond the generic advice frontier.

## Disproof track

Show star dimension or source reconstruction is full-size, or show the complete tradeoff
lies on/above generic `S*T^2`; semantic duplication already rejects this version.

## Positive and negative controls

- Positive code control: a synthetic code with planted small star product and local decoder.
- Positive source control: exhaustive factor-base additions.
- Negative generic control: matched random linear codes and generic fixed-base tables.
- Negative accounting control: report both online-only and fully amortized costs.
- Leakage control: no scalar-labelled coordinates or target-selected advice.

## Quantitative promotion and falsification gates

No active promotion gate exists. A versioned successor would need a theorem absent from
`ECFG-H686`, zero source errors, at least 100 fresh targets per largest size, and a 95%
confidence tradeoff strictly beyond generic fixed-base lookup with complete exponents
below `0.45`. Full star dimension, source ambiguity, or a generic-frontier match falsifies it.

## Artifact plan

- Collision report: `ideas/artifacts/ECDLP-IDEA-067/ledger_collision.md`
- Possible theorem: `ideas/artifacts/ECDLP-IDEA-067/partial_star_theorem.md`
- Verifier: `ideas/artifacts/ECDLP-IDEA-067/verify_sources.py`
- Retain code generators, star bases, advice, sources, targets, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. An online or
amortized win is not a generic single-target breakthrough.

## Exactly one next executable action

1. If reopened, first write `ideas/artifacts/ECDLP-IDEA-067/ledger_collision.md` identifying a theorem not already requested by `ECFG-H686`; otherwise execute nothing.
