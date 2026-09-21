# ECDLP-IDEA-164 — Miller-coboundary HDX source transgression

## Status and claim labels

- Class: `algorithmic-representation`
- Risk band: `conservative-theorem-gated`
- Top lane: `none`
- State: `deferred_needs_miller_coboundary_source_identity`
- Cohort: `20260718-b`
- Evidence scale: literature and semantic audit only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cochain, local view, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A frozen family of Miller/divisor functions evaluated on a public endpoint forms a scalar-blind sheaf 1-cochain on an implicit high-dimensional expander. A proved coboundary identity equals source-bearing local views of the elliptic relation fiber, and cosystolic decoding recovers every exact signed factor-base atom with complete sub-rho descent.

## Mechanism-new operation

The operation is **endpoint Miller evaluation transgressed by a source-biconditional coboundary identity, then HDX local decoding**. A vague endpoint-to-local-view encoder collides with IDEA-132; the new operation exists only if the explicit Miller coboundary produces source-bearing restrictions without first knowing a divisor/source. Applying an HDX decoder to supplied local views is a control.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, Miller functions, an implicit complex, sheaf, orientations, and masks are frozen.
2. Endpoint evaluations construct the cochain without a source divisor or relation tuple.
3. One symbolic coboundary identity is biconditional to all exact signed sources.
4. The complex, local restrictions, decoder lists, and source inverse remain sub-rho and cover all strata.
5. Setup, evaluations, failed targets, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_Miller_evaluations | implicit_HDX_sheaf_cochain | source_biconditional_coboundary | cosystolic_exact_atom_decoder | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit local-view/source hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source gate.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, where explicit source edges exceed budget.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the exact ancestry barrier.

## Closest primary literature

- First and Kaufman, [Cosystolic expansion of sheaves on posets](https://arxiv.org/abs/2208.01778), supplies sheaf/cosystolic machinery but not elliptic endpoint cochains.
- Miller, [The Weil pairing, and its efficient calculation](https://crypto.stanford.edu/miller/miller.pdf), supplies Miller functions but no source-bearing HDX transgression.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies the relation equations.

No checked source gives the claimed identity and complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze functions, complex, sheaf, coboundary, decoder, factor base, masks, and verifier.
2. Prove endpoints alone construct the cochain and the coboundary/source biconditional.
3. Evaluate known `R_j=[r_j]P`, decode every local-view list, and lift atoms to signed point tuples.
4. Verify tuples; preserve cohomology ambiguity, misses, false atoms, repeats, infinity, and output.
5. Collect rank `B`, solve factor-base logs, and independently verify them.
6. Apply the identical cochain/decoder to fresh `Q+[t]P` masks.
7. Substitute factor logs, remove masks, retain all candidates, and verify `[x]P=Q`.
8. Report complex construction, face restrictions, lists, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, cochain/decoder/source inversion `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

All faces, restrictions, Miller evaluations, decoder lists, and ancestry are charged.

## Likely fatal obstruction

Miller evaluations are public aggregates. Making the cochain source-bearing may require the missing divisor/source, while materializing all face restrictions restores `B^m` ancestry. Expansion helps decode a supplied word; it does not construct the received word.

## Proof track

Derive the exact endpoint coboundary identity, implicit-complex bounds, source inverse, and `lambda,mu<=0.45` complete descent.

## Disproof track

Show the cochain needs a source divisor, find source-distinct equal local views, prove face materialization exponent at least `0.5`, or reduce the decoder to supplied-syndrome circularity.

## Positive and negative controls

- HDX/sheaf codes with supplied codewords and errors.
- Miller evaluations on supplied divisors.
- IDEA-132 endpoint-syndrome and explicit source-edge controls.
- Exhaustive toy fibers, rho, BSGS, and blind-target verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires the explicit coboundary/source theorem and formal `lambda,mu<=0.45`. A later approved toy test needs complete all-strata recall and zero false atoms. A supplied source, local-view collision, explicit `B^m` face deck, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Coboundary theorem: `ideas/artifacts/ECDLP-IDEA-164/miller_coboundary_source_theorem.md`
- Sheaf/complex specification: `ideas/artifacts/ECDLP-IDEA-164/hdx_sheaf_spec.md`
- Fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-164/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-164/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-164/cost_analysis.md`

All paths are prospective; no experiment is authorized.

## Interpretation boundary

This is deferred and novelty-unverified. Any finite evidence is toy and projections heuristic and model-bound. A valid cochain or relation is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-164/miller_coboundary_source_theorem.md` deriving the endpoint-only coboundary/source identity before constructing an HDX instance.
