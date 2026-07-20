# ECDLP-IDEA-054 — Conductor-growing trace-shift decoder

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `rejected_merged`
- Evidence scale: `toy` reasoning and preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: exact merge with conductor/orientation and trace-fiber lanes
  unless a target-coupled, nongeneric hidden-shift oracle is first specified.
- Breakthrough claim: **none**; conductor growth, trace labels, orbit pruning, or a toy
  hidden-shift match is not an ECDLP break.

## Falsifiable hypothesis

For `Q=[x]P` in a public prime-order subgroup of order `N=p^(1+o(1))`, the rejected
proposal asserted that a deterministic tower of conductor-growing isogeny or
endomorphism objects produces public trace words `T_P(k)` and `T_Q(k)` satisfying a
hidden-shift law `T_Q(k)=T_P(k+x)` on a domain of size `N^(rho+o(1))`, `rho<1/2`, with
enough collision resistance to recover `x` below rho and BSGS after tower construction,
trace evaluation, matching, output, verification, and memory are charged.

As titled, the traces are class/orientation labels already represented in the ledger.
They describe isogeny paths or multiply equivalent trace-fiber representatives; they do
not couple the ECDLP target scalar to an additive shift. The hypothesis is therefore
rejected unless an explicit target-dependent oracle identity is proved before any
experiment.

## Mechanism-new operation

The proposed operation was to compose conductor-prime ascents, evaluate Frobenius or
endomorphism traces at each level, and decode the target scalar as a shift between the
base and target trace sequences. A growing conductor was supposed to amplify a weak
orientation label into a sparse shift signature.

The operation is not mechanism-new in its current form. The ledger already composes
distinct and repeated conductor ascents, reuses orientations, performs mixed-CRT orbit
pruning, and proves that homomorphic trace-fiber multiplicity does not improve relation
probability or rank. A hidden-shift algorithm applied to public class labels is a solver
wrapper unless a theorem makes the sequence depend on `Q=[x]P` by translation rather
than by an isogeny endpoint choice.

## Assumptions

- The curve, subgroup, conductor tower, endomorphism orders, orientations, trace maps,
  sampling indices, and matching rule are public and target-independent.
- Every isogeny construction, torsion extension, CRT branch, rejected endpoint, trace
  evaluation, and scalar verification is charged.
- The hidden-shift identity is exact on a declared domain; approximate correlations,
  first-hit ordering, and target-selected subsequences are invalid.
- Classical time and bit memory are compared with rho and BSGS; a quantum hidden-shift
  claim would require a separate threat model and is outside this record.
- All finite tests are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`conductor_tower | Frobenius_endomorphism_trace_words | claimed_target_additive_shift | collision_resistant_shift_decoder | scalar_verification`

Collision fingerprint:
`orientation_and_trace_class_labels | conductor_composition | multiplicity_without_target_coupling | generic_shift_search`

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — requires an isogenous or conductor-related object to change the DLP operation, not merely expose another endpoint label.
2. `ledger/EV-ISO-001.yaml` — supplies the matched negative boundary for same-order isogeny structure and decomposition behavior.
3. `ledger/H-REP-001.yaml` — prevents a trace-word representation from receiving exponent credit without a new scalar operation.
4. `ledger/FINDING-PF-IC-001.md` — sets the complete rho boundary and rejects relation or label validity as a breakthrough.
5. `ledger/SYNTHESIS-20260716.md` — requires fresh targets, matched controls, complete scaling, descent, and memory accounting.

## Closest primary literature

- Couveignes, [Hard homogeneous spaces](https://eprint.iacr.org/2006/291), gives the
  primary homogeneous-space/vectorization setting closest to conductor and isogeny
  actions; it does not expose an ECDLP scalar shift.
- Childs, Jao, and Soukharev, [Constructing elliptic curve isogenies in quantum
  subexponential time](https://arxiv.org/abs/1012.4019), connects isogeny actions with
  hidden-shift methods in a different problem and threat model.
- Kuperberg, [A subexponential-time quantum algorithm for the dihedral hidden subgroup
  problem](https://arxiv.org/abs/quant-ph/0302112), supplies the primary hidden-shift
  algorithmic boundary; it is not a classical sub-rho ECDLP decoder.

No cited source proves that conductor traces of `[x]P` form the asserted classical
additive hidden shift. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze the conductor primes, tower depth, endpoint selection, orientations, trace-word
  alphabet, domain, collision rule, and abort conditions.
- Construct the full tower for the known base `P`, retaining every endpoint and CRT
  branch, and evaluate `T_P(k)` without an `N`-entry scalar table.
- Establish on known-scalar targets `[r]P` that `T_[r]P(k)=T_P(k+r)` exactly, not merely
  up to endpoint relabeling, automorphism, or a target-selected alignment.
- Treat the known-index trace words as the factor base/dictionary and retain all repeated
  labels and candidate shifts.
- Collect enough independently verified shift equations to determine any required trace
  dictionary or auxiliary linear system; charge tower and trace construction.
- Evaluate the frozen trace oracle on `Q+[t]P`, emit every compatible shift candidate,
  remove `t`, and verify `[x]P=Q`.
- If the target trace depends only on the curve/isogeny endpoint or if evaluating it at
  index `k` already requires `[k]Q`, the path collapses to public labels or generic
  scalar search and terminates.

## Full rho/BSGS cost model

Let tower construction and orientation cost `N^(a+o(1))` time and `N^(s+o(1))` bits;
trace-word domain size be `N^d`; one word evaluation cost `N^e`; retained distinct
signatures number `N^h`; collision/matching cost `N^v`; and complete masked-target
evaluation/output cost `N^u`. Let any auxiliary factor-base dictionary have size
`B=N^beta` and sparse solve cost `N^(2*beta)`.

- Pollard rho: `N^(1/2+o(1))` group operations and negligible asymptotic memory.
- BSGS: `N^(1/2+o(1))` time and `N^(1/2+o(1))` stored points.
- Tower and trace setup: `N^(a+o(1))` plus `N^(d+e+o(1))` if all domain words are read.
- Signature storage and matching: `N^(max(h,v)+o(1))` time and `N^(h+o(1))` bits at
  minimum.
- Auxiliary factor-log work: `N^(2*beta+o(1))` time and `N^(beta+o(1))` memory.
- Target descent, full candidate output, and verification: `N^(u+o(1))`.

The complete time exponent is `lambda=max(a,d+e,v,2*beta,u)` and bit-memory exponent
is `mu=max(s,h,beta)`. Promotion requires upper 95% bounds below `1/2` for both.
If the trace alphabet has only `N^h` distinguishable words, generic collision ambiguity
forces about `N^(1-h)` candidates; if exact word evaluation requires scalar walks, then
`d+e>=1/2` at the useful coverage point.

## Likely fatal obstruction

Frobenius trace and conductor data describe the curve, endomorphism order, torsion
action, or isogeny path and are independent of the chosen subgroup point scalar.
Homomorphic trace fibers multiply successes and trials equally. A sequence built from
`[k]Q` can satisfy a formal shift law, but evaluating it is simply generic scalar
multiplication and classical hidden-shift recovery retains the birthday barrier.
Conductor growth also raises torsion-field and endpoint-enumeration costs.

## Proof track

Provide an explicit, classically evaluable oracle and prove the exact identity
`T_Q(k)=T_P(k+x)` with target-independent orientation. Prove a collision/uniqueness
bound, a complete classical decoder, and tower/trace/output exponents giving
`lambda,mu<1/2`. The oracle must not evaluate unknown scalar multiples or consume an
isogeny-path secret equivalent to `x`.

## Disproof track

Prove the trace word factors through curve or endpoint invariants; show trace-fiber
multiplicity cancels; demonstrate two different scalars with identical words; reduce
oracle evaluation to `[k]Q`; or establish `lambda>=1/2` from tower/domain/candidate
cost. Any one confirms the exact merge/reject verdict.

## Positive and negative controls

- Positive hidden-shift control: planted cyclic sequences with a unique shift and the
  same alphabet, domain, and matching implementation.
- Positive tower control: known conductor ascents with independently certified endpoints
  and orientations.
- Negative scalar control: random points on one fixed endpoint; curve-level trace words
  should remain unchanged.
- Negative multiplicity control: matched random homomorphism fibers with the same kernel
  size.
- Baseline control: BSGS and rho on the identical subgroup and target batch.
- Leakage control: reject any sequence, orientation, or alignment selected after scalar
  labels or target results are exposed.

## Quantitative promotion and falsification gates

A counterfactual preflight would cover conductor towers of depths 1--4 on at least 24
ordinary toy curves per 10--20-bit size, at least four conductor-prime schedules, 256
known-scalar targets and 100 blind masked descents per largest cell, plus planted shift
controls. Reconsideration requires zero tower/orientation/shift mismatches, at least
`0.99` unique-shift recovery on planted and known-scalar controls, collision-list exponent
upper 95% bound `v<=0.30`, and complete `lambda,mu<=0.45`. Falsify if target trace words
are scalar-independent, the shift identity needs `[k]Q` enumeration, applicability falls
below 95%, ambiguity reaches exponent `0.50`, or any lower 95% complete-cost exponent is
at least `0.50`.

## Artifact plan

- Equivalence note: `ideas/artifacts/ECDLP-IDEA-054/trace_invariance.md`
- Tower manifests: `ideas/artifacts/ECDLP-IDEA-054/towers.jsonl`
- Trace words: `ideas/artifacts/ECDLP-IDEA-054/trace_words.jsonl`
- Collision/candidate ledger: `ideas/artifacts/ECDLP-IDEA-054/candidates.jsonl`
- Planned audit runs: `ideas/artifacts/ECDLP-IDEA-054/runs/<run-id>/`
- Cost analysis: `ideas/artifacts/ECDLP-IDEA-054/cost_model.json`
- Required retained data: conductor orders, endpoints, orientations, trace evaluations,
  repeated labels, shifts, candidates, verification, seeds, commands, environment,
  resource measurements, stdout, stderr, and checksums.

## Interpretation boundary

This is a preserved rejected/merged record. It is toy, heuristic, model-bound, and
novelty-unverified. Correct conductor arithmetic, trace identities, orbit pruning, or a
toy shift does not establish ECDLP progress. A new proposal requires a public
target-coupled oracle identity and complete classical sub-rho recovery, not another
conductor schedule or hidden-shift solver substitution.

## Exactly one next executable action

1. Exhaustively replay the frozen trace-word construction on 8--12-bit conductor towers and test whether every word is invariant under replacing `P` by `[r]P`; stop the lane without collection if scalar independence holds.
