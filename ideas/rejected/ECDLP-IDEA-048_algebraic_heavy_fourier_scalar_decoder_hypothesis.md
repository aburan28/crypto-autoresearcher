# ECDLP-IDEA-048 — Algebraic heavy-Fourier scalar decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct sparse-Fourier implementation, a toy-heavy
  coefficient, or a verified toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Let `E/F_p` contain a public prime-order subgroup `<P>` of order
`N=p^(1+o(1))`, and let `Q=[x]P`. There is a deterministic,
target-independent algebraic predicate `b:E(F_p)->{-1,0,+1}` with an explicit
exception rule and a public straight-line program such that the scalar-indexed signal

`F_P(u)=b([u]P),  u in Z/NZ`

has a reproducible, sparse set of Fourier coefficients of magnitude at least
`tau=N^(-delta+o(1))`. A fixed significant-Fourier-coefficient algorithm, using only
chosen evaluations of `F_P` and `F_Q(t)=b([t]Q)`, finds the significant spectra in
sub-rho time and memory. Since

`hat(F_Q)(k)=hat(F_P)(k*x^(-1))`,

matching a separated coefficient at frequency `j` for `P` to frequency `k` for `Q`
returns the candidate `x=k*j^(-1) mod N`. Complete matching, ambiguity output, and
source-curve verification remain below both rho and BSGS after every setup query,
target query, coefficient estimate, failed match, and stored bit is charged.

This predicts an algebraic point predicate with a learnable heavy scalar-frequency
signature. It does not infer an attack from generic Fourier correctness or from a signal
whose frequency table was obtained by enumerating all `N` scalar labels.

## Mechanism-new operation

Construct `b` from `(E,P,N)` before seeing `Q`. Give a preregistered
significant-Fourier-coefficient (SFT) routine oracle access to `u -> b([u]P)` and retain
all coefficients above the frozen threshold, including confidence intervals and complex
phase. Repeat with `t -> b([t]Q)`. Multiplication of the hidden scalar permutes the
frequency indices but leaves coefficient values unchanged, so a target-independent
coefficient-signature rule generates a complete list of ratios `k/j`, which is verified
directly on `E`.

The proposed new operation is **query-sublinear recovery of a scalar-induced frequency
permutation from an algebraic point signal**. Unlike `ECDLP-IDEA-001`, it does not
factor an addition-incidence tensor or produce factor-base decompositions. Unlike an
orbit dictionary (`ECDLP-IDEA-011`), affine hard-bit decoder (`ECDLP-IDEA-045`), or a
post-hoc selector, it permits neither an `N`-entry transform nor
predicate choice after scalar labels or target data are observed. If the SFT needs dense
sampling, if coefficient matching needs a square-root list, or if selecting `b` uses
the discrete logarithm table, the mechanism is invalid.

## Assumptions

1. `E(F_p)` has a public subgroup `<P>` of prime order
   `N=p^(1+o(1))`; `Q=[x]P` with `x!=0 mod N` is the only target-dependent input.
2. The predicate grammar, coefficient derivation, zero/pole convention, SFT algorithm,
   threshold, precision, confidence schedule, and matching rule are frozen from public
   inputs before target evaluation.
3. At least one coefficient signature is separated enough that every compatible
   frequency match can be listed without an `N^(1/2)` search.
4. The SFT guarantee applies to exact chosen-query access over `Z/NZ`, and its query,
   arithmetic, precision, failure-probability, and bit-memory costs are charged.
5. Predicate construction and evaluation use no scalar-indexed table, pairing target,
   auxiliary DLP, scalar-labeled training set, or target-conditioned branch.
6. Applicability is measured per declared generic curve family, including curves with no
   coefficient above threshold; favorable-curve selection is forbidden.
7. Any finite preflight conclusion remains toy, heuristic, model-bound, and
   novelty-unverified until a theorem and independent scaling evidence exist.

## Semantic fingerprint

`public_algebraic_point_predicate | chosen_query_scalar_signal | significant_fourier_coefficient_learning | hidden_scalar_frequency_permutation | ratio_match_and_source_curve_verification`

The indispensable operation is a sublinear SFT that exposes a sparse, matchable
frequency signature from a target-independent algebraic predicate. A dense DFT, a
materialized orbit table, an addition-incidence factorization, or a label-selected
predicate is a duplicate/control, not this mechanism.

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — rules out a relabeled order-`N` orbit unless the public
   decoder and its complete cost are genuinely smaller.
2. `ledger/FINDING-PF-IC-001.md` — supplies the prime-field rho floor that the full SFT
   setup, target phase, and output must beat.
3. `ledger/H-FB-001.yaml` — prevents an algebraic coordinate predicate from receiving
   credit without a new source of scalar information.
4. `ledger/EV-FB-001.yaml` — supplies matched random-signal and density controls for any
   apparent coefficient concentration.
5. `ledger/SYNTHESIS-20260716.md` — requires verified target descent and complete
   precomputation, memory, failure, and output accounting.

## Closest primary literature

- Akavia, Goldwasser, and Safra, [Proving Hard-Core Predicates Using List
  Decoding](https://www.cs.tau.ac.il/~safra/PapersAndTalks/hardcore.pdf), gives the
  significant-Fourier/list-decoding framework over finite abelian groups.
- Galbraith, Laity, and Shani, [Finding Significant Fourier Coefficients:
  Clarifications, Simplifications, Applications and
  Limitations](https://arxiv.org/abs/1607.01842), records the exact query-access
  assumptions and limitations relevant to cryptographic bit-security reductions.
- Boneh and Shparlinski, [On the Unpredictability of Bits of the Elliptic Curve
  Diffie--Hellman Scheme](https://doi.org/10.1007/3-540-44647-8_12), is the closest
  elliptic-coordinate bit-prediction boundary; it does not construct the asserted heavy
  scalar-frequency predicate.
- Kohel and Shparlinski, [On exponential sums and group generators for elliptic curves
  over finite fields](https://doi.org/10.1007/10722028_24), supplies the nearby
  square-root exponential-sum boundary for algebraic functions composed with elliptic
  group characters.
- Shoup, [Lower Bounds for Discrete Logarithms and Related
  Problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic square-root
  control that a coordinate-specific signal must escape.

No checked source supplies a generic prime-field elliptic predicate with the stated
heavy, matchable scalar spectrum and complete sub-rho recovery path. That is a nearby-
literature result only; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the scalar convention, exact complex root-of-unity convention, predicate `b`,
   exception value `0`, SFT pseudocode, precision, and failure budget.
2. Use the known-scalar query base `u -> [u]P` as the setup factor base. Run the SFT on
   `F_P(u)=b([u]P)` without materializing the `N` samples; retain every reported
   `(j,hat(F_P)(j),error)` triple and all failed queries.
3. Independently estimate each retained setup coefficient on a frozen validation sample.
   Apply the predeclared separation rule to form the complete anchor set; do not choose an
   anchor because it later matches `Q`.
4. Query `F_Q(t)=b([t]Q)` at the exact indices chosen by the same SFT algorithm and retain
   every reported target coefficient with its error interval.
5. Match all setup/target coefficient values whose certified error regions intersect.
   For each nonzero anchor frequency `j` and matched target frequency `k`, emit
   `x_candidate=k*j^(-1) mod N`; retain the full cross-match list.
6. Compute `[x_candidate]P` for every emitted value. Accept only the unique candidate
   equal to `Q`; report failure or ambiguity otherwise.
7. Record a scalar only after source-curve verification. The setup factor base has known
   scalar indices, and the spectral permutation replaces relation collection and linear
   algebra rather than leaving them uncharged.

## Full rho/BSGS cost model

Let predicate construction cost `N^(c+o(1))`, one predicate/group query cost
`N^(e+o(1))`, and retained predicate state use `N^(s+o(1))` bits. Let the threshold be
`tau=N^(-delta+o(1))`. Let the two complete SFT passes, including validation and numerical
precision, use `N^(q+o(1))` oracle queries, `N^(z+o(1))` non-oracle bit operations, and
`N^(z_m+o(1))` bits. Let the setup and target heavy sets have size
`H=N^(h+o(1))`; Parseval gives only the control `h<=2*delta+o(1)`. Let complete matching,
candidate output, and verification cost `N^(v+o(1))`, with the naive cross-match control
`v<=2*h+o(1)` but no right to omit it.

- Pollard rho: `N^(1/2+o(1))` group operations and constant state, apart from
  constant-factor automorphism gains.
- BSGS: `N^(1/2+o(1))` group operations and `N^(1/2+o(1))` stored points.
- Predicate setup: `T_build=N^(c+o(1))` and state `N^(s+o(1))` bits.
- Both query streams: `T_query=N^(e+q+o(1))`, including scalar multiplications,
  predicate evaluations, erasures, retries allowed by the frozen SFT, and validation.
- SFT arithmetic: `T_SFT=N^(z+o(1))`; if a cited guarantee is polynomial in
  `1/tau`, its actual degree is included in `z`, not hidden in `o(1)`.
- Matching/output/verification: `T_match=N^(v+o(1))` and at least
  `N^(h+o(1))` stored coefficient records.

The full time exponent is `lambda=max(c,e+q,z,v)` and the bit-memory exponent is
`mu=max(s,z_m,h)`. Promotion requires upper confidence bounds
`lambda<1/2` and `mu<1/2` against both baselines. Dense sampling forces `q=1`; a
Fourier-flat signal has `delta=1/2+o(1)` and no sub-rho learner; an unseparated heavy set
can force `v>=1/2` even if SFT itself is fast.

## Likely fatal obstruction

For the contract's bounded-degree character predicates, standard hybrid elliptic
character-sum bounds force nontrivial normalized coefficients to the
`O(N^(-1/2))` scale when the associated sheaf is nontrivial. A coefficient above that
floor may occur only through exceptional/trivial-sheaf cases, degree-growing predicates,
or an orientation hidden in predicate selection.
Even a genuinely heavy spectrum can have many repeated or near-equal coefficients, so
matching the frequency permutation may require a square-root-or-larger cross product.
Finally, significant-Fourier algorithms can have a high polynomial dependence on
`1/tau`; that exponent may meet rho long before a toy coefficient looks small.

## Proof track

Give an explicit predicate family and prove a uniform lower bound and separation theorem
for its nonzero scalar-Fourier coefficients on the declared curve family. Instantiate a
specific finite-abelian SFT theorem with exact query, bit-operation, precision, memory,
and failure bounds. Prove the frequency-permutation identity, completeness of the
interval-based matching rule, and uniqueness after source-curve verification. Substitute
the actual exponents to prove `lambda<1/2` and `mu<1/2`.

## Disproof track

Prove any one of: all permitted predicates have maximum nontrivial coefficient
`N^(-1/2+o(1))`; predicate degree or SLP size reaches the rho exponent; the SFT theorem's
dependence on `tau` forces `e+q>=1/2` or `z>=1/2`; coefficient multiplicity forces
`v>=1/2`; applicability tends to zero; or the only separating predicate was selected
using scalar labels or target data. Any one closes the exact mechanism.

## Positive and negative controls

- Positive SFT control: a query oracle `u -> sign(cos(2*pi*j_0*u/N))` with hidden
  planted `j_0`, passed through the exact same precision, learner, and matching code.
- Positive group-wiring control: a planted predicate table exposed only through group
  queries on tiny cyclic groups, with its dense table inaccessible to the learner.
- Positive instrumentation control: exhaustive toy DFTs verify all reported frequencies,
  coefficients, error intervals, ratios, and scalar candidates.
- Negative arithmetic control: independent random ternary signals with the same erasure
  rate and marginal distribution.
- Negative geometry control: randomly permute scalar-to-point labels while preserving the
  predicate multiset; algebraic coefficient concentration should disappear.
- Leakage control: a dense DFT, scalar-indexed predicate table, and best-after-label
  predicate search are measured only as invalid oracle arms and can never promote.

## Quantitative promotion and falsification gates

The frozen preflight covers ordinary prime-order curves at field sizes
`10,11,12,13,14,16,18,20` bits, at least 24 independent curves per size, exhaustive DFT
truth through 14 bits, the contract's fixed predicate grammar, and all planted/random
controls. Escalation to a larger scaling study requires all of:

- zero SFT completeness, coefficient-interval, frequency-permutation, candidate, or
  scalar-verification mismatches on exhaustive and planted cells;
- at least 99% planted-frequency recovery at every declared threshold and erasure rate;
- a multiplicity-corrected lower 95% bound with `delta<=0.20` for a predicate frozen
  before labels on every declared family at both largest completed sizes;
- at most `N^0.10` separated heavy coefficients and a complete-match exponent upper 95%
  bound `v<=0.30` on the same cells;
- upper 95% bounds `lambda<=0.45` and `mu<=0.45`, including both SFT passes,
  validation, precision, misses, coefficient output, matching, and verification;
- at least 95% independently verified recovery on held-out curves with no predicate,
  threshold, anchor, or matching-rule reselection.

Falsify the preflight claim if exhaustive controls fail after independent repair, every
fixed non-oracle predicate has a lower 95% fitted `delta>=0.25`, any complete-cost lower
95% bound reaches `lambda>=0.50` or `mu>=0.50`, matching emits an
`N^(1/2)` list, or usefulness depends on scalar labels or target data. A timeout or an
unsupported cell is coverage evidence only.

## Artifact plan

- Frozen contract: `ideas/contracts/ECDLP-EXP-CONTRACT-048_heavy_fourier_preflight.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-048/heavy_fourier.py`
- Planned predicate grammar: `ideas/artifacts/ECDLP-IDEA-048/predicates.yaml`
- Planned SFT specification: `ideas/artifacts/ECDLP-IDEA-048/sft_spec.md`
- Planned manifests: `ideas/artifacts/ECDLP-IDEA-048/runs/<run-id>/manifest.yaml`
- Planned raw queries: `ideas/artifacts/ECDLP-IDEA-048/runs/<run-id>/queries.jsonl`
- Planned spectra: `ideas/artifacts/ECDLP-IDEA-048/runs/<run-id>/spectra.jsonl`
- Planned candidates: `ideas/artifacts/ECDLP-IDEA-048/runs/<run-id>/candidates.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-048/analysis.md`
- Required retained data: predicate SLPs, exact query indices, outputs and erasures,
  coefficient estimates and intervals, all matches and candidates, exhaustive DFT truth,
  resource metrics, seeds, commands, environment, commit, dirty-tree state, stdout,
  stderr, and checksums.

## Interpretation boundary

A valid Fourier identity, a correct learner, a toy-heavy coefficient, or a verified toy
scalar establishes only implementation correctness on that cell. A heavy coefficient
found after label-based predicate selection is invalid. Only a target-independent
predicate with independently replicated, complete sub-rho setup, query, SFT, matching,
output, verification, and bit-memory costs can support escalation; it would still remain
heuristic, model-bound, and novelty-unverified until crypto-scale evidence exists.

## Exactly one next executable action

1. Independently review the theorem-to-pseudocode bindings and frozen query/precision accounting in `ideas/contracts/ECDLP-EXP-CONTRACT-048_heavy_fourier_preflight.yaml`; do not execute the predicate matrix before coordinator approval.
