# ECDLP-IDEA-162 — Multiplicative Witt-Kummer source symbol

## Status and claim labels

- Class: `arithmetic-representation`
- Risk band: `high-risk`
- Top lane: `none`
- State: `rejected_scoped_symbol_aggregates_or_relocates_dlp`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: finite checks would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid symbol or relation certificate is not an ECDLP break.

## Falsifiable hypothesis

A public nonadditive Witt/Kummer or Contou-Carrère symbol on the divisor data of a five-source elliptic relation returns a compact multiplicative residue whose canonical inverse identifies every exact signed factor-base source. Repeating it across relations and masked targets would give a complete sub-rho factor-base-to-target descent.

## Mechanism-new operation

The proposed operation is **multiplicative local-symbol evaluation with residue-to-source inversion**, not an additive de Rham-Witt logarithm. It is distinct only if the symbol is constructed from the endpoint without a supplied divisor and its residue support is biconditional to source identities. Miller S-units, tame-symbol verification, supplied divisors, and a `mu_N` exponent oracle are controls.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta` and one target-uniform divisor/symbol construction are frozen.
2. The symbol is nonadditive on the prime-to-`p` subgroup and computable from endpoints alone.
3. Its value and local residues invert to exact signed sources, including multiplicity and exceptional strata.
4. No source divisor, scalar label, factor table, or multiplicative DLP oracle is supplied.
5. Symbol construction, local fields, outputs, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_constructed_divisor | nonadditive_Witt_Kummer_symbol | compact_multiplicative_residue | exact_residue_source_inverse | blind_target_descent`

Dropping endpoint construction or source inversion merges the record into IDEA-007/040/119/140 controls.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1051`, a failed source/certificate boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, where public features miss factor-log orientation.
3. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the mixed norm/symbol control.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete source-query and descent gate.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1470`, the nearest exact public relation-surface control.

## Closest primary literature

- Gorchinskiy and Osipov, [A higher-dimensional Contou-Carrère symbol](https://arxiv.org/abs/1505.03829), constructs local symbols but not endpoint-to-source inversion.
- Bloch and Kato, [p-adic étale cohomology](https://doi.org/10.1007/BF02831624), supplies nearby symbol/cohomology structure, not a prime-order ECDLP decoder.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives relation equations but no multiplicative source symbol.

No checked source supplies the proposed pipeline; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, divisor recipe, symbol, local parameters, factor base, masks, and verifier.
2. Construct the divisor and symbol from each public endpoint without source or scalar advice.
3. Invert every residue to exact signed factor-base tuples and record every branch.
4. Verify tuples directly and preserve misses, collisions, multiplicities, poles, infinity, and failed endpoints.
5. Collect rank `B`, solve factor-base logs, and independently verify them.
6. Apply the identical symbol to fresh `Q+[t]P` masks.
7. Substitute logs, remove masks, keep every ambiguity candidate, and verify `[x]P=Q`.
8. Report divisor construction, local expansions, symbol values, outputs, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, symbol plus source inversion `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Every divisor coefficient, local expansion, multiplicative readout, and source branch is charged.

## Likely fatal obstruction

Local symbols aggregate valuations of an already supplied divisor; constructing that divisor is the missing source search. When an `N`-torsion signal survives, it lands in a multiplicative group where exponent extraction is another DLP. Exact support decoration therefore assumes sources or relocates hardness.

## Proof track

An outside-scope successor must construct a divisor from endpoints alone, prove a nonadditive source biconditional, avoid a multiplicative DLP, and derive `lambda,mu<=0.45`.

## Disproof track

Reduce the symbol to aggregate divisor data, exhibit source-distinct equal residues, show the divisor requires the original relation fiber, or identify the readout as a `mu_N` DLP.

## Positive and negative controls

- Supplied divisors with known local symbols.
- Miller-function and tame-symbol relation certificates.
- Random divisors matched for degree and local support.
- Exhaustive toy fibers, rho, BSGS, and independent source/scalar checks.

## Quantitative promotion and falsification gates

This version is rejected. Reopening needs a new endpoint-constructed nonadditive symbol and exact inverse with `lambda,mu<=0.45`. One supplied divisor, aggregate collision, multiplicative-DLP return, missed source, or complete exponent at least `0.5` is falsifying.

## Artifact plan

- Scoped symbol obstruction: `ideas/artifacts/ECDLP-IDEA-162/witt_kummer_symbol_no_go.md`
- Prospective divisor/symbol specification: `ideas/artifacts/ECDLP-IDEA-162/symbol_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-162/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-162/cost_analysis.md`

All paths are prospective; no experiment ran.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. Any finite check is toy and any projection heuristic and model-bound. Symbol correctness or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-162/witt_kummer_symbol_no_go.md` formalizing the divisor-construction versus multiplicative-return dichotomy without executing a symbol computation.
