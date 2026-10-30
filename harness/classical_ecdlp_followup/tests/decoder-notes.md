# Public-input approximate decoder: implementation and development checks

Source: `src/decoder.cpp`, SHA-256
`7ffb572cac3dea4251b1e3c8b3d6e61c7959e789043f1b7e1105b173ad6d118a`.
This collaborator performed development tests only. No scientific `--run`
command on the new cohort was invoked. Root owns prospective source/input
freeze, genuine admission, execution and the final observation report.

## What the program implements

The candidate uses public curve/base/subgroup parameters and public target
points. Its measurement path does not call `lab::orbit`, `Curve.points`,
`read_fixtures`, `certify`, a scalar dictionary, or a truth-label file.
Fixture parsing checks prime p and r, nonsingularity, canonical parameters,
Hasse sanity, nonidentity P with [r]P=O, coprime cofactor, and target subgroup
membership. It trusts the independently prepared public whole-curve order N;
it does not repeat a full point census. The parser accepts only the five
public target columns `fixture_id target_id Qx Qy Qinf`; extra columns are
rejected. No OS-enforced blindness is claimed.

The public input domain is p<=65535, prime odd r<=8191, ordinary non-anomalous
non-special-j short Weierstrass curves, and gcd(N/r,r)=1. The fixed protocol
uses the narrower 8/10/12-bit cohort. Oversized N is rejected before squaring
the Hasse difference to avoid signed overflow on malformed input.

## Unlabelled sampling

Each sample chooses infinity with probability 1/N. Otherwise it samples a
uniform finite point using random x and Tonelli–Shanks. A nonsingular nonzero
square has two roots, selected equiprobably. A zero root is accepted with
probability one half. Consequently every finite rational point has the same
accepted proposal weight 1/(2p), including rational 2-torsion. Combining the
finite-point distribution with infinity's 1/N weight gives uniform E(Fp),
under an ideal uniform source. SplitMix64 with rejection-bounded draws is the
frozen reproducible PRNG implementation.

Multiplication by h=N/r sends this distribution uniformly to the unique
order-r subgroup: gcd(h,r)=1 and N=hr imply a surjective homomorphism with
h-element fibres. The sampler performs only public field/group operations,
without learning the logarithms of its samples. Development checks verify
its membership on an independently generated small curve. Per-sample [r]X
checks are not performed during measurement; membership follows from the
public certified group-order/cofactor assumptions. On-curve checks and all
performed arithmetic are counted.

## Features and fixed transition construction

The four feature IDs are:

- `x_mod_7`: infinity 0; finite 1+x mod 7 (domain size 8).
- `power_residue_5`: available only when 5 divides p−1; infinity 0, x=0
  label 1, and the five nonzero x^((p−1)/5) values receive labels 2..6 in
  ascending root-value order. A public multiplicative generator is found
  from factorization of p−1. No EC orbit is enumerated. Root-value labels
  differ by a categorical renaming from the scale panel's raw values.
- `x_hash_7`: infinity 0; finite
  `1+mix64(uint64(x) XOR fixture.seed XOR FNV1a64("L9.scale.xhash7.v1")) mod 7`.
  The avalanche and FNV constants match the scale panel. This is a public,
  sign-invariant control, not an exact matched-fibre relabeling.
- `constant`: every point receives label 0 (domain size 1).

For each applicable fixture-feature, 2048 unlabelled uniform X samples build
two tables for a=phi(X), c=phi(2X+bP), b in {0,1}. Every cell has fixed
Laplace pseudocount 1:

`K_b[a,c] = (count_b[a,c]+1)/(row_count[a]+number_of_states)`.

Unobserved rows therefore remain uniform rather than receiving an assumed
deterministic transition. Kernel rows are checked to sum to one. Training
seed is `fixture.seed XOR FNV1a64("decoder.train.v1/"+feature_id)`.
Different features use independent declared PRNG streams, not a common-random-
numbers feature comparison. The trained tables and raw transition counts are
retained in each kernel row.

The two-input projection entropy measured by the earlier pilot does not
justify this unary state model. The new construction measures and tests the
unary model directly. In particular, uniform individual marginals do not
establish an exact Markov conditional law after conditioning on past states.

## Held-out one-step calibration

Each feature has 512 fresh unlabelled samples with seed
`fixture.seed XOR FNV1a64("decoder.heldout.v1/"+feature_id)`.
These are independent draws from the same finite population, not necessarily
distinct points or a different curve. For b=0 and b=1, output contains the
complete held-out transition count table, conditional-model top-1 hits and
log-loss in bits, and the corresponding held-out scores of a training-output-
marginal-only reference. Its pseudocount is also one.

Calibration does not modify the kernels, smoothing, features, beam widths,
views or decoding policy. `calibration_used_for_tuning` is false. Its sampling
and arithmetic costs are recorded separately. Both b scores share the same
512 X draws; they are not 1024 independent populations.

## Four public rerandomizations and canonical range

For every public Q, sample four public R values. Start at R and condition the
end state on `phi(Q+[2^ell]R)`, where ell=ceil(log2 r). After j prefix steps,
the actual point is `[2^j]R+[prefix]P`. For any fixed prefix, an independent
uniform R makes this point uniform because r is odd. This is a one-time
marginal statement; it does not remove history dependence or make the four
view likelihoods conditionally independent given a prefix.

View seed is `fixture.seed XOR FNV1a64("decoder.views.v1/"+feature_id)
XOR mix64(target_ordinal+0x52a090)`. Ordinal is public file position within its
fixture, fixed independently of the hidden scalar. No target coordinate or
scalar label enters the random/tie seed. The four sampled points, public
shifted targets and start/terminal labels are output for replay. The same
views are reused across both beam widths and both prefix modes.

A backward DP sums only legal canonical bit strings, using the MSB comparison
state against r−1. At a prefix with n legal completions, the score is

`sum_i ln(L_i(prefix)) − (4−1) ln(n)`.

Here L_i is the sum of the trained model's endpoint likelihood over legal
remaining suffixes for view i. The subtraction corrects repetition of the
prefix prior when multiplying four per-view averages. It remains a fixed
conditional-independence heuristic, not the exact joint multiview likelihood.

The two prefix modes are explicitly paired:

- `model` propagates alpha through the learned transition kernels, and uses
  `alpha dot beta_remaining` for each view.
- `exact` maintains each hypothesized prefix's actual public EC point by
  doubling/adding P, projects its current state exactly, and uses
  `beta_remaining[exact_state]`. Its extra group/feature operations are
  charged. Unknown future suffixes still use the approximate learned model.
  The word "exact" refers to prefix state, not an exact probabilistic solver.

Beam widths are 1 and 8. Both modes and widths use identical public
prefix-tie seeds, separate from Q and scalar labels. At the leaves, every
canonical candidate is verified by the full public equation [k]P=Q. Since P
has prime order r and candidates lie in [0,r), at most one can verify.

For the constant feature all state likelihoods reduce to the legal prefix
prior. Candidate sets are independent of Q and the hidden scalar, and both
modes give identical candidates. With uniform independent target scalars,
their exact marginal success reference is candidate_count/r. For learned
coordinate models, B/r is a descriptive comparator, not an exact null theorem.

## Mixing diagnostics

Each kernel records the floating Dobrushin coefficient
`delta(K)=0.5 max_{a,b} sum_c |K[a,c]-K[b,c]|`, its maximum over b=0,1, and
`delta_max^t` for t=0..ell. Computation counts are included in setup.

For exact row-stochastic trained matrices, prefixes followed by the same fixed
t-bit suffix have one-view endpoint absolute-probability difference at most
delta_max^t; a product of four [0,1] likelihoods differs by at most
4 delta_max^t. This says nothing directly about posterior ratios, pruning
success, the real non-Markov EC process, or ECDLP security. The emitted values
are finite-precision diagnostics, not rigorous numerical certificates.

## Output, costs and witness semantics

Rows have track `L9-decoder`, scope `exploratory_toy_followup` and row_kind:
`kernel`, `target`, or `not_applicable` for an unavailable fifth-power map.
There is one kernel and 8 targets × 2 widths × 2 modes for each applicable
fixture-feature in the frozen cohort. Candidate scalars are integer arrays;
exact-prefix log-zero leaf scores are serialized as JSON null, never Infinity
or NaN. A null score is not an omitted trial or resource failure. Any verified
candidate necessarily has a finite score in these tests.

Targets emit `verified_scalar` or null, public candidate-verification counts,
and `toy_discrete_log_witness`. A positive verified scalar is a toy per-instance
discrete-log witness, which the root's independent arithmetic checker must
classify correctly. Unconditional `attack_claimed:false` is not used to hide
such witnesses. `attack_advantage_claimed:false` and
`solver_gain_claimed:false` make clear that a positive instance is not evidence
of a new fast algorithm. No novelty or rho advantage is asserted.

Counters distinguish field arithmetic, group additions, scalar multiplication,
sampling/root work, feature calls, DP multiply-add terms, beam children,
verification and calibration. Validation counters are shared once per fixture
and repeated in kernel rows with that label. View counters are shared once
per feature-target, repeated across its four cases with that label. Inference
and verification counters are per case and can be summed. Calibration is
additional charged study work. The public Tonelli nonresidue cache is reused
across features; setup counters are incremental, so no standalone cold bound
is asserted for a later individual feature. Total batch cost includes all of
these stages, parsing/validation and wall time; raw field-operation counts are
not interchangeable with complete group-operation or elapsed-time costs.

The numeric kernel payload field counts trained probabilities, raw training
counts and row masses only. It excludes calibration tables, marginal arrays,
objects and allocator overhead. Beam/DP payloads count their arrays rather
than complete process peak RSS. No memory advantage is inferred.

## Development verification

Final normal and combined ASan/UBSan executions both passed **2794 checks**.
Leak detection was explicitly disabled (`ASAN_OPTIONS=detect_leaks=0`), so no
leak-check success is claimed. Compiler: g++ 14.2.0.

```sh
set -e
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror src/decoder.cpp \
  -o /tmp/classical-followup-decoder-final-v5
/tmp/classical-followup-decoder-final-v5 --self-test
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -fsanitize=address,undefined \
  -fno-omit-frame-pointer src/decoder.cpp \
  -o /tmp/classical-followup-decoder-final-v5-sanitized
ASAN_OPTIONS=detect_leaks=0 \
  /tmp/classical-followup-decoder-final-v5-sanitized --self-test
```

Checks include all finite-field square/non-square cases on five small primes;
all curve point-pair additions and small scalar multiplications on p=17 and
p=23; uniform-sampler subgroup membership; an independently checked fifth-root
alphabet on p=61; exhaustive legal-prefix counts; backward-DP sums against
direct branch enumeration; scalar-labelled cyclic full-state positive controls
for both prefix modes and both widths; constant negative controls; stochastic
kernel/count/calibration checks; rerandomization identities; delta=1 permutation
and delta=0 identical-row calibrations; invalid-terminal, depth and malformed
order rejections. The scalar-labelled positive control is an abstract toy
state machine confined to development, not a candidate-accessible EC lookup.

A separate development integration helper includes this source and emits four
kernel rows plus 16 target rows on the already-known p=61,r=19 fixture and one
canned public target. Python only parses/validates the JSON; all EC/model
calculations are C++. It checked coverage, 2048/512 counts, finite-or-null
scores, canonical unique candidates, public witness consistency and constant-
mode equality. The largest row was 7881 bytes. These 20 canned development
rows are not scientific cohort observations and were not produced by `--run`.

Earlier strict compilation found four misleading-indentation warnings; they
were corrected before testing. One initial serialization assertion wrongly
treated valid null log-zero scores as real numbers and raised TypeError;
the validator was corrected to distinguish null from nonfinite JSON. No
mathematical result was inferred from those tooling failures. Earlier
2793-check versions preceded the final oversized-order rejection test; final
source identity and 2794-check commands above supersede them.
