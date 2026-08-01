# ECDLP-IDEA-045 — Algebraic hard-bit leakage with shift decoding

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; predicate correctness, nonzero toy bias, or toy scalar
  recovery is not a break.

## Falsifiable hypothesis

Let `E/F_p` contain a prime-order subgroup `<P>` of order
`N=p^(1+o(1))`, and let `Q=[x]P`. There is a deterministic,
target-independent rational-function character predicate

`b_f(R) in {-1,0,+1}`

with an explicit zero/exception rule and a public straight-line program, such that its
correlation with a fixed scalar hard bit is

`epsilon_f = |N^(-1) sum_(u mod N) b_f([u]P) h_N(u)| = N^(-delta+o(1))`

for `delta<1/4` on a generic declared curve family. Here `h_N` is the balanced
most-significant-bit sign on `Z/NZ`. Random affine queries
`[t]Q+[a]P=[t*x+a]P` then turn `b_f` into a noisy hidden-number oracle.
A target-independent robust decoder recovers a short list containing `x` with complete
time and bit-memory exponents below `1/2`, after predicate construction, every query,
erasures, list size, and verification are charged.

This is not the claim that coordinate bits look nonrandom on a few curves. It predicts a
uniform, predeclared algebraic bias and a complete affine-shift decoder that beat both rho
and BSGS without training on scalar labels.

## Mechanism-new operation

Freeze `f` from the public tuple `(E,P,N)` before seeing `Q` or any scalar
labels. Evaluate a multiplicative-character or comparably explicit trace-function bit on
`R=[t]Q+[a]P`. Because `t` and `a` are public, a proved correlation with
`h_N(log_P R)` supplies noisy observations of `h_N(t*x+a)`. Feed the complete
observations, including erasures and the unknown global correlation sign, to a
preregistered hidden-number/list decoder; run both global signs if necessary and verify
the returned list on `E`.

The proposed new operation is **a scalar-hard-bit predictor realized by a public
algebraic predicate with affine-shift decoding**. It is not an ambient Fourier
factorization, an orbit table, a post-hoc coordinate selector, a learned classifier, a
different generic solver, or a relation-only certificate. If the useful predicate is
selected after scalar labels are inspected, stored as `N` values, or evaluated by first
computing a discrete logarithm, this record is invalid.

## Assumptions

1. `E(F_p)` has a public prime subgroup `<P>` of prime order
   `N=p^(1+o(1))`, and `Q=[x]P` is the only target-dependent input.
2. The predicate grammar, coefficient derivation, character convention, exceptional
   values, and both possible correlation signs are frozen from `(E,P,N)`.
3. The correlation lower bound holds per declared generic curve family, not only after
   averaging over favorable curves, predicates, or targets.
4. The hidden-number decoder accepts affine samples `(t,a,b_f([t]Q+[a]P))`,
   charges deterministic noise and erasures, and returns every surviving candidate.
5. Predicate degree, straight-line-program length, coefficient generation, scalar
   multiplications, sample storage, decoding, output size, and verification are charged.
6. No scalar-labeled training set, target-conditioned predicate choice, pairing,
   root-of-unity DLP, or explicit `N`-entry truth table is available.
7. Any inference from the finite preflight remains toy, heuristic, model-bound, and
   novelty-unverified.

## Semantic fingerprint

`public_rational_character_predicate | scalar_hard_bit_bias | affine_queries_tQ_plus_aP | robust_hidden_number_list_decoder | complete_verified_scalar_recovery`

The indispensable operation is a proved, target-independent bias that survives generic
curves and supplies the exact noisy observations required by the decoder. Low-degree
coordinate statistics without this bias are negative controls. A spectral transform or
orbit-index table merges into the occupied representation lanes.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — establishes that ordinary prime-field
   factor-base membership and full relation accounting do not already beat rho.
2. `ledger/H-FB-001.yaml` — prevents a coordinate predicate or factor-base shape
   from being credited without a new source of scalar information.
3. `ledger/EV-FB-001.yaml` — provides the matched random-yield and density controls
   that the affine-query stream must beat.
4. `ledger/H-REP-001.yaml` — rules out relabeling an order-`N` orbit or changing
   equations without a cheaper public decoder.
5. `ledger/SYNTHESIS-20260716.md` — requires end-to-end target descent and full
   rho/BSGS accounting rather than a correctness-only observation.

## Closest primary literature

- Boneh and Shparlinski, [On the Unpredictability of Bits of the Elliptic Curve
  Diffie--Hellman Scheme](https://doi.org/10.1007/3-540-44647-8_12), proves
  reductions for coordinate-bit prediction in an ECDH setting; it does not construct the
  scalar-bit predicate asserted here.
- Boneh and Venkatesan, [Hardness of Computing the Most Significant Bits of Secret
  Keys in Diffie-Hellman and Related
  Schemes](https://crypto.stanford.edu/~dabo/pubs/abstracts/dhmsb.html), introduces
  the hidden-number decoding boundary used by the affine-query path.
- Farashahi and Shparlinski, [Pseudorandom Bits From Points on Elliptic
  Curves](https://arxiv.org/abs/1005.4771), gives character-sum evidence for
  square-root cancellation in related elliptic-coordinate sequences and is therefore a
  nearby obstruction, not support for a useful bias.

These sources bound nearby predictors and decoders but do not establish this mechanism
or its novelty. The novelty claim remains unverified.

## Complete factor-base-to-target-descent path

1. Fix the public scalar convention `0,...,N-1`, balanced bit `h_N`, predicate
   `b_f`, exception symbol `0`, and a deterministic affine-mask stream
   `(t_i,a_i)` with `t_i != 0 mod N`.
2. Treat the known-mask points `A_i=[a_i]P` and multipliers `t_i` as a
   known-log affine factor base. Their construction uses ordinary public scalar
   multiplication and does not contain target or hidden-log data.
3. Construct `f` and its evaluation straight-line program from `(E,P,N)`. Retain
   the expanded degree and a fully tabulated `N`-value predicate only as forbidden
   cost controls.
4. For each frozen mask, compute `R_i=[t_i]Q+A_i` and record
   `y_i=b_f(R_i)`, including every zero, denominator exception, retry prohibition,
   group operation, and predicate operation.
5. Send the complete triples `(t_i,a_i,y_i)` to the preregistered robust
   hidden-number decoder. Decode both possible global correlation signs and retain the
   entire candidate list; no target-dependent resampling or predicate selection is
   allowed.
6. Independently compute `[x_j]P` for every returned `x_j`, accept exactly the
   value equal to `Q`, and report failure or ambiguity otherwise.
7. Record the recovered scalar only after original-curve verification. Because the
   affine factor base has known logs, no uncharged relation matrix or base-log phase is
   omitted.

## Full rho/BSGS cost model

Let predicate degree be `D=N^(d+o(1))`, target-independent predicate construction
cost `N^(c+o(1))`, one complete predicate/query evaluation cost
`N^(e+o(1))`, and retained predicate state use `N^(s+o(1))` bits. Let
`epsilon=N^(-delta+o(1))` and let the robust decoder require
`M=N^(2*delta+o(1))` affine samples, including logarithmic confidence factors and
erasures. Let its **total** decoding time be `N^(z+o(1))`, bit memory
`N^(z_m+o(1))`, and output-list size `N^(zeta+o(1))`.

- Pollard rho baseline: `N^(1/2+o(1))` group operations with constant state, apart
  from constant-factor automorphism gains.
- BSGS baseline: `N^(1/2+o(1))` group operations and
  `N^(1/2+o(1))` stored points.
- Predicate construction: `T_build=N^(c+o(1))`; a dense degree-`D`
  representation ordinarily forces `c>=d`, while any sparse high-degree circuit must
  charge its actual SLP size.
- Affine factor-base and target queries:
  `T_query=N^(e+2*delta+o(1))`, including `M` scalar multiplications,
  predicate calls, failed/zero outputs, and stored masks.
- Hidden-number decoding: `T_decode=N^(z+o(1))` for the complete data, not a
  per-sample cost.
- Candidate verification: `T_verify=N^(zeta+o(1))` group operations.

The full time exponent is
`lambda=max(c,e+2*delta,z,zeta)` and the bit-memory exponent is
`mu=max(s,2*delta,z_m,zeta)`. Promotion requires `lambda<1/2` and
`mu<1/2` against both baselines. In particular, square-root cancellation
`delta>=1/2-o(1)` is far worse than rho, while even `delta>=1/4` makes
ordinary quadratic-sample recovery meet or exceed the rho exponent.

## Likely fatal obstruction

Known character-sum behavior strongly suggests that any bounded-degree rational predicate
has only square-root-scale correlation with an interval bit along a generic prime-order
elliptic orbit. A degree-growing predicate can manufacture structure only by paying in
degree, coefficient generation, SLP size, exceptional density, or a hidden scalar-indexed
table. The per-curve correlation may also have adversarial deterministic noise that an
average-case hidden-number theorem cannot decode. The likely outcome is
`delta>=1/4`, `e+2*delta>=1/2`, or a predicate whose selection already uses
the scalar orientation it purports to reveal.

## Proof track

Give an explicit predicate family and prove a uniform per-curve correlation lower bound,
with all zeros and poles included. Prove that random public affine masks turn that
deterministic predicate into the declared robust hidden-number instance, establish
sample/list bounds, and derive `lambda<1/2` and `mu<1/2` using the actual SLP.
Finally prove that the seven-step path returns only scalars that verify on the source
curve.

## Disproof track

Prove any one of: a character-sum upper bound forcing `delta>=1/4-o(1)` for the
allowed predicate grammar; degree/SLP/query cost forcing `e+2*delta>=1/2`; a
generic family on which the correlation vanishes; a noise pattern outside the decoder's
guarantee; list exponent `zeta>=1/2`; or dependence on scalar-labeled predicate
selection. Any of these closes the exact claimed mechanism.

## Positive and negative controls

- Positive algorithm control: a planted noisy `h_N(log_P R)` oracle at declared
  biases, passed through the identical affine-query and decoder implementation.
- Positive instrumentation control: exhaustive toy logs verify every predicate value,
  correlation, affine equation, returned candidate, and exception.
- Negative arithmetic control: independently random bits with identical zero rate.
- Negative structure control: randomly permute the scalar-to-point encoding while
  preserving predicate marginals; geometric correlation should disappear.
- Negative mechanism control: fixed low-degree coordinate characters evaluated without
  label-based selection and compared with their character-sum bounds.
- Leakage control: a scalar-indexed truth table and a best-after-label predicate search
  are measured only as invalid oracle arms and can never promote.

## Quantitative promotion and falsification gates

The frozen preflight covers field sizes `8,9,10,11,12,13,14,16` bits, at least 24
independent ordinary prime-order curves per size, exhaustive scalar truth through 12 bits,
and the preregistered predicate arms in the contract. Escalation requires all of:

- zero predicate, affine-equation, decoder, or scalar-verification mismatches on
  exhaustive cells;
- at least 99% planted-oracle recovery at each declared bias and sample size;
- a predeclared non-oracle predicate with a multiplicity-corrected lower 95% bias bound
  corresponding to `delta<=0.20` on every one of the two largest completed sizes;
- upper 95% bounds `lambda<=0.45` and `mu<=0.45` with construction,
  erasures, all affine samples, decoding, list output, and verification charged;
- at least 95% verified recovery on held-out curves without predicate reselection;
- stable sign, bias, and recovery conclusions under leave-largest-size-out and
  leave-curve-family-out analyses.

Falsify the preflight claim if exhaustive checks fail after independent repair, every
predeclared predicate has a lower 95% fitted `delta>=0.25`, any complete-cost lower
95% bound reaches `lambda>=0.50` or `mu>=0.50`, the decoder needs an
`N^(1/2)` list, or the useful arm depends on scalar labels. A timeout or unsupported
cell is infrastructure/coverage evidence only.

## Artifact plan

- Frozen contract: `ideas/contracts/ECDLP-EXP-CONTRACT-045_hard_bit_shift_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-045/hard_bit_shift.py`
- Planned predicate specification: `ideas/artifacts/ECDLP-IDEA-045/predicates.yaml`
- Planned manifests: `ideas/artifacts/ECDLP-IDEA-045/runs/<run-id>/manifest.yaml`
- Planned raw queries: `ideas/artifacts/ECDLP-IDEA-045/runs/<run-id>/queries.jsonl`
- Planned decoder output: `ideas/artifacts/ECDLP-IDEA-045/runs/<run-id>/candidates.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-045/analysis.md`
- Required retained data: predicate SLPs, all masks, outputs and erasures, exhaustive
  labels, correlations, candidates, resource metrics, seeds, command, environment,
  commit, dirty-tree state, stdout, stderr, and artifact checksums.

## Interpretation boundary

A correct predictor implementation, a nonzero toy correlation, or verified toy scalar
recovery is not an ECDLP breakthrough. Bias fitted from labeled toy or selected curves is
not a public oracle. Only a target-independent predicate with independently replicated
sub-rho construction, query, decode, output, verification, and bit-memory costs can
support escalation, and all claims remain heuristic, model-bound, and
novelty-unverified until then.

## Exactly one next executable action

1. Independently review the frozen design in `ideas/contracts/ECDLP-EXP-CONTRACT-045_hard_bit_shift_preflight.yaml` and, only after coordinator approval, execute its complete toy matrix without changing predicates or sample schedules.
