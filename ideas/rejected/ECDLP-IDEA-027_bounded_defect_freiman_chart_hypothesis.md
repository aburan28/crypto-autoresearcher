# ECDLP-IDEA-027 — Bounded-defect Freiman chart

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` search only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a small observed defect alphabet is not scalar recovery.

## Falsifiable hypothesis

A fixed target-independent rational chart `phi` on a declared family of ordinary
prime-field curves has addition defect
`D(R,S)=phi(R+S)-phi(R)-phi(S)` contained in an explicit automaton of size
`N^(delta+o(1))`, with complete defect-path entropy, ambiguity, and memory below
exponent `1/2`. Integrating that automaton along scalar addition chains recovers `x` from
`phi(P),phi(Q)` below rho/BSGS.

## Mechanism-new operation

Apply **bounded-defect integration of a global near-homomorphism**. This is not a curve
coordinate substitution: the proposed new operation is a target-independent finite defect
automaton whose states correct addition globally and can be inverted with sub-square-root
branching. It does not collect factor-base relations, enumerate scalar or deck orbits, or
substitute a solver.

## Assumptions

1. The chart family and defect automaton are frozen without targets or scalar labels.
2. Defect states are exactly computable from public point pairs.
3. All path branching and distinct histories, not only the defect support, are charged.
4. Coordinate poles, exceptional sums, and chart changes are retained.
5. A genuine character or scalar-labeled chart is classified as circular, not success.
6. Evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`global_rational_near_homomorphism | bounded_addition_defect | finite_defect_automaton | scalar_path_integration`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — prevents an ordinary coordinate change from counting.
2. `ledger/EV-REP-001.yaml` — supplies matched model controls.
3. `ledger/EV-REP-002.yaml` — requires branch and sign accounting.
4. `ledger/FINDING-PF-IC-001.md` — the direct-coordinate alternative to relation collection.
5. `ledger/SYNTHESIS-20260716.md` — enforces complete target and generic-baseline costs.

## Closest primary literature

- Green and Ruzsa, [Freiman's theorem in an arbitrary abelian group](https://arxiv.org/abs/math/0505198), gives the structural approximate-homomorphism boundary.
- Even-Zohar and Lovett, [The Freiman–Ruzsa theorem in finite fields](https://arxiv.org/abs/1212.5738), gives a finite-field stability boundary.
- Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), bounds generic encodings.

These sources suggest severe stability obstructions but do not analyze the proposed exact
elliptic rational-chart automaton. Novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is `phi(P)` plus the public finite defect alphabet.

1. Freeze bounded-degree charts, normalization, exceptional-point policy, and automaton construction.
2. Exhaust additions to build and independently verify the target-independent defect transition system.
3. Evaluate `phi(P),phi(Q)` and propagate all defect states along a balanced unknown-scalar addition-chain decoder.
4. Solve the resulting integer/coset constraints for every candidate scalar.
5. Return only a candidate satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Let chart construction be `N^c`, evaluation `N^e`, defect alphabet `N^delta`, transition
construction `N^t`, path entropy/branching `N^b`, residual ambiguity `N^u`, verification
`N^v`, exceptional-density reciprocal `N^zeta`, and bit-memory `N^s`. Rho costs
`N^1/2` time; BSGS costs `N^1/2` time/memory. The proposal has time exponent
`lambda=max(c,e,t,zeta,b+delta,u+v)` and memory exponent `mu=max(s,delta,b,u)`. Counting only distinct
defect values while ignoring path histories is invalid.

## Likely fatal obstruction

Stability may force every separating bounded-defect chart to be close to a true character,
whose public orientation is the DLP. Otherwise defect entropy across an `O(log N)`
addition chain may grow to `N^(1/2-o(1))` even if the one-step alphabet is small.

## Proof track

Construct a fixed rational chart and exact automaton, prove a sub-square-root global path
entropy bound, and give a decoder with `lambda,mu<1/2` on a declared infinite family.

## Disproof track

Show every bounded-degree chart has square-root defect entropy, becomes a scalar character,
or loses information under collisions; alternatively prove branch growth reaches rho.

## Positive and negative controls

- Positive control: canonical residues in an explicitly additive cyclic group.
- Positive instrumentation control: planted bounded-defect maps.
- Negative control: random permutations of elliptic point encodings.
- Representation control: ordinary `x`, `y`, Edwards, and Hessian charts at matched degree.
- Leakage control: blind scalar labels until chart and transition hashes are frozen.

## Quantitative promotion and falsification gates

Exhaust degree-at-most-eight rational maps on 10–18-bit curves, at least 100 curves per
size. Promotion only to scaling requires exact transitions, zero wrong scalars, and upper
95% `delta<=0.15`, `b+delta<=0.40`, `u<=0.20`, `lambda<=0.45`, and `mu<=0.45`,
stable under held-out curves and scalar-blind coordinate changes. Falsify if lower 95%
path entropy reaches `0.50`, all low-defect maps are circular characters, or one scalar
fails verification.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-027/freiman_chart_search.sage`
- `ideas/artifacts/ECDLP-IDEA-027/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-027/runs/<run_id>/defects.jsonl`
- `ideas/artifacts/ECDLP-IDEA-027/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-027/analysis.md`

## Interpretation boundary

This remains toy, heuristic, model-bound, and novelty-unverified. A compact one-step
defect set is neither a decoder nor a breakthrough; only complete verified recovery below
rho/BSGS can support escalation.

## Exactly one next executable action

1. Exhaust the frozen degree-at-most-eight charts on 10–18-bit curves and measure exact defect support, full path entropy, residual ambiguity, and blinded scalar recovery.
