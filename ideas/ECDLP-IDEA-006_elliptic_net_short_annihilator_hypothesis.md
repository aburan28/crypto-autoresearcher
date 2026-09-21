# ECDLP-IDEA-006 — Elliptic-net short annihilator

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an EDS identity or recovered toy shift is not a break.

## Falsifiable hypothesis

Target-indexed elliptic-net blocks associated with `(P,Q=[x]P)` admit a constructible
annihilator or displacement representation of order `r=N^(rho+o(1))` with sufficiently
small `rho` that the unknown shift/index `x` can be recovered, including ambiguity
resolution, in total exponent below `1/2` without solving another order-`N` DLP.

The hypothesis predicts compression beyond the known equivalence between EDS problems and
ECDLP; simply expressing the input as an elliptic divisibility sequence is not new.

## Mechanism-new operation

Build exact Hankel/Toeplitz-like blocks from a rank-two elliptic net, recover a short
displacement annihilator, and use its eigenvalue/root data to locate the target shift.
The proposed new operation is **sub-square-root exact sequence-state compression with
index recovery**, not a recurrence identity, different linear solver, or precomputed
large-prime table.

## Assumptions

1. `<P>` has known prime order `N`, `Q=[x]P`, and the required elliptic-net values can be
   computed without knowing `x`.
2. Normalization removes projective/scale ambiguity and is identical for base and target blocks.
3. The recovered annihilator determines the index rather than transferring it to a
   multiplicative DLP of order `N`.
4. Block generation, rank computation, root/eigenvalue work, ambiguity enumeration, and
   stored samples are charged.
5. No target-specific successful blocks are selected after observation.
6. Scaling from toy periods is heuristic and model-bound.

## Semantic fingerprint

`rank_two_elliptic_net | exact_displacement_annihilator | compressed_target_shift_recovery | no_order_N_eigenvalue_DLP | removes_full_period_search`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a non-PDP representation.
2. `ledger/H-REP-001.yaml` — closest representation record, but this changes the object to a sequence state.
3. `ledger/EV-REP-001.yaml` — warns that compact-looking formulas can hide branch multiplicity.
4. `ledger/DEC-20260716-004.yaml` — rules out presenting a structured point subset as the mechanism.
5. `ledger/SYNTHESIS-20260716.md` — requires complete scaling and rho comparison.

## Closest primary literature

- Lauter and Stange, [The ECDLP and equivalent hard problems for elliptic divisibility sequences](https://arxiv.org/abs/0803.0728), is the closest and strongest equivalence boundary.
- Stange and Shparlinski, [Character sums with division polynomials](https://arxiv.org/abs/0912.5246), supplies nearby pseudorandomness evidence.
- Shoup, [Lower Bounds for Discrete Logarithms](https://www.shoup.net/papers/dlbounds1.pdf), applies if block access is simulable by generic operations.
- Corrigan-Gibbs, Henzinger, and Wu, [The Structured Generic-Group Model](https://eprint.iacr.org/2026/384), charges a useful structured subset of small density.

The literature establishes hardness equivalences but does not rule out every special
displacement algorithm. No novelty is claimed; status remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is a frozen set of normalized elliptic-net anchor states.

1. Define a rank-two net `W(a,b)` for `(P,Q)` and a one-dimensional base sequence for `P`;
   prove which computable block is shifted by the unknown `x`.
2. Sample deterministic anchor indices and store `r` normalized base states with exact
   recurrence certificates.
3. Form structured block matrices and recover the minimal displacement annihilator; verify
   it on withheld base indices.
4. Compute the target block from public `(P,Q)` and reduce it to coordinates in the anchor basis.
5. Solve the annihilator's index-location problem, charging root finding or eigenvalue
   logarithms and retaining all candidate shifts.
6. Descend each surviving shift to `x mod N` and verify `[x]P=Q`; reject a method that needs
   an order-`N` DLP to label an eigenvalue.

## Full rho/BSGS cost model

Let annihilator order `r=N^rho`, block construction cost `N^a`, structured linear algebra
exponent `omega_s` in `r`, target block cost `N^q`, index-location/ambiguity cost `N^tau`,
and stored state `N^s`.

- Pollard rho: `N^(1/2+o(1))` time, constant state.
- BSGS: `N^(1/2+o(1))` time and memory.
- Block/anchor construction: `N^(a+o(1))`.
- Annihilator recovery: `r^(omega_s+o(1))=N^(omega_s*rho+o(1))`.
- Target evaluation: `N^(q+o(1))`.
- Index location and descent: `N^(tau+o(1))`.
- Memory exponent: `mu=max(s,2*rho)` for explicit blocks, or the measured compressed value.

Total time exponent is `lambda=max(a,omega_s*rho,q,tau)`. With practical
`omega_s≈2`, even `rho=1/4` reaches the rho boundary. Any finite-field DLP in the
annihilator eigenvalues contributes exponent `1/2` and kills promotion.

## Likely fatal obstruction

The useful elliptic-net period is order `N`, and its linear/displacement complexity is
expected to be `N^(1-o(1))` or to encode the original DLP in an eigenvalue. Lauter–Stange
show that several apparently simpler EDS problems are subexponentially equivalent to
ECDLP. Apparent low rank at tiny periods may be normalization degeneracy or a recurrence
that predicts values without locating the hidden shift.

## Proof track

Prove a uniform upper bound on exact displacement order, an efficient target-block
construction, and an algebraic index-location algorithm that does not invoke an order-`N`
DLP; then derive `lambda<1/2` and verify the shift on the curve.

## Disproof track

Prove a linear-complexity lower bound for the normalized blocks; show the annihilator
eigenvalue label is exactly an order-`N` DLP; find target blocks indistinguishable across
many shifts; or fit a full-cost lower confidence bound at least `1/2`.

## Positive and negative controls

- Positive control: planted linear-recurring sequences with known displacement rank and shift.
- Positive instrumentation control: exhaustive elliptic nets where every candidate shift is checked.
- Negative control: random periodic sequences with matched alphabet, period, and normalization.
- Negative mechanism control: EDS recurrence evaluation without index recovery.
- Degeneracy control: random projective rescalings and alternative valid net normalizations.

## Quantitative promotion and falsification gates

Use prime-order toy curves with periods from 12 through 34 bits, at least 100 instances per
size, exhaustive ranks through 22 bits, and withheld-block validation. Promotion requires:

- exact annihilator prediction on all withheld samples and exact target recovery;
- upper 95% bound `rho<=0.18` with measured `omega_s<=2.2`;
- upper 95% bounds `a<=0.30`, `q<=0.20`, `tau<=0.40`, hence `lambda<=0.45`;
- at least 1,000 independent target shifts recovered at the two largest sizes with zero errors;
- memory upper 95% exponent `mu<=0.45`.

Falsify the scoped claim if exact displacement-rank slope has lower 95% bound `>=0.25`
for `omega_s>=2`, index location requires an order-`N` field DLP, one accepted shift is
wrong, or every full-cost configuration has lower 95% `lambda>=0.50`. A rank-library
failure is infrastructure, not evidence.

## Artifact plan

- Contract: `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-006/net_annihilator.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-006/runs/<run-id>/`
- Planned blocks/sketches: `ideas/artifacts/ECDLP-IDEA-006/runs/<run-id>/blocks/`
- Planned raw ranks: `ideas/artifacts/ECDLP-IDEA-006/runs/<run-id>/raw.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-006/analysis.md`

## Interpretation boundary

This is a toy, heuristic, model-bound, novelty-unverified high-risk hypothesis. Recurrence
correctness, low toy rank, or a recovered toy shift is not evidence of a better-than-rho
algorithm unless index location, ambiguity, memory, and all preprocessing are included.

## Exactly one next executable action

1. After coordinator approval, execute the frozen rank-and-index-location preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml` over its complete preregistered toy matrix.
