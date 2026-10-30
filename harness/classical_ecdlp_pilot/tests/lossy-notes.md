# L9 exact lossy-projection implementation

Implementation source: `src/lossy.cpp`. SHA-256:
`f6d3decebfce83f04b5620de6101d3569435197701585f2b3f8d24cd6e48261d`.

This implements the finite observational panel, not a propagation algorithm,
scalar decoder, new ECDLP algorithm, attack benchmark or proof of probabilistic
impossibility. Scientific `--run` has **not** been called by this implementation
agent. Root owns source/protocol freeze, scientific execution and archival.

## Implemented calculation

For the full enumerated prime-order subgroup, `orbit[k]=[k]P`. This explicitly
charged scalar-labelled orbit is observational instrumentation; it is not a
public target-to-scalar constructor. The subgroup operation used in the panel
is `(i+j) mod r`. The development suite checks that rule against all 361
actual point additions on its p=17, order-19 fixture.

The measured quantity is

`D = H(pi(X+Y) | pi(X), pi(Y))`

for uniform independent X,Y over the **entire** subgroup, including identity.
Every pair is enumerated exactly. Integer histograms are exact; logarithms are
computed in `long double` with compensated accumulation. A lookup table stores
`c log2(c)` for c=0,...,r². Each pair of input fibres is processed with a small
output-count vector; storage never requires the full image-cubed array. The
declared supported order is r<=1023, and the actual frozen pilot is smaller.
An unsupported order is rejected, not classified as a mathematical negative.

All projection labels are output in canonical scalar-orbit order with their
raw-value dictionary, fibre sizes, support histogram, support-weighted pair
mass, and a canonical joint-table checksum. Thus the exact observed joint
table can be reconstructed from the row and cyclic operation. The FNV-1a
64-bit checksum is explicitly **not cryptographic** and is not a scientific
certificate. Its input is each nonzero `(a,b,c,count)` in ascending a,b,c
order, each field encoded as eight little-endian bytes. Root's artifact
digests supply cryptographic custody.

## Frozen projections

- Full canonical point encoding: identity 0, finite point `1+x*p+y`.
- Constant 0, including identity: a deliberate entropy-zero/lossy trap.
- Kummer x: identity 0, finite x+1.
- Quadratic character of x: identity 0, zero x 1, square 2, nonsquare 3.
- d-th power residue labels for d=3,5,7 when d divides p-1: identity 0,
  zero x 1, otherwise `x^((p-1)/d)+1`. An unavailable d produces a separate
  `not_applicable` row with its reason, not a failed/null observation.
- Top and bottom x windows at t=1,2,4,8: identity 0, finite window value+1.
  A top window wider than the field's canonical x width uses all x bits.
- x modulo 3,5,7,11: identity 0, finite residue+1.
- Deterministic rho-style coordinate partitions of sizes 16,32,64: identity
  0; finite `1 + mix64((1+x*p+y) XOR fixture.seed) mod buckets`.

The coordinate partitions are observational labels only. No factor-base arm,
relation collection, descent, quantum computation or simulated quantum attack
is included. There are exactly 22 rows per fixture including unavailable
power-residue entries; between 19 and 22 are measured projection rows.

## Unconditional relabeling ensemble and retained outcomes

Every measured projection uses **99** fixed seeded relabelings. The seed is

`fixture.seed XOR FNV1a64("L9.null.v1/" + fixture.id + "/" + projection.name)`.

FNV uses the standard offset `14695981039346656037` and prime
`1099511628211`. SplitMix64 comes from the frozen shared header. Each shuffle
starts from the original label vector; generator state continues between
the 99 repetitions. Fisher-Yates uses rejection-bounded draws to remove
modulo bias for an ideal uniform 64-bit source. Every shuffle's exact fibre
profile is checked. The relabeling includes the identity position: no
singleton/infinity label is pinned in the null ensemble.

Each row retains **all 99 individual unconditional null entropy values**, their mean,
sample standard deviation, descriptive Monte Carlo mean standard error,
minimum and maximum. These are a deterministic reproducible PRNG ensemble,
not an analytic proof of a universal null law or a multiple-testing-adjusted
significance result. The observed value has no pair-sampling error because
the finite population is fully enumerated. Root must retain every row and
split large JSONL output by rows rather than truncate the 99 outcomes.

## Negation-matched primary null

The unconditional reference above is secondary whenever the exact subgroup
projection is negation invariant: `labels[k] == labels[r-k]` for every k.
For such a projection there is a second independent 99-member ensemble.
It fixes the identity's label and permutes the original labels of nonzero
unordered pairs `{k,r-k}`. Both members of each destination pair receive
the same permuted label. This preserves negation invariance, every label's
point-fibre size and the entire feature multiset. No sign orientation draw
is needed because each source pair's two labels are equal. A non-invariant
projection gets `matched_null_applicable=false` and an explicit reason,
not fabricated matched observations.

The matched seed is

`fixture.seed XOR FNV1a64("L9.sign-pair-null.v1/" + fixture.id + "/" + projection.name)`.

Each matched shuffle starts from the original pair-label vector and uses the
same rejection-bounded Fisher-Yates procedure with its independent RNG state
continuing across 99 repetitions. The identity is fixed even if its feature
value also occurs on nonzero pairs. All 99 `matched_null_entropy_bits` are
retained with summary moments and exact additional pair/cell counters.
`primary_reference_kind` and `primary_observed_minus_reference_mean_bits`
explicitly select this matched ensemble where applicable. Existing `null_*`
fields retain the unconditional ensemble; their unqualified gap is not the
primary comparison for a negation-invariant projection.

For Kummer x, the matched operation is merely a bijective renaming of the
distinct sign-pair image labels, with the identity image fixed. Conditional
entropy is invariant under that relabeling of the output and both input
alphabets. Every matched Kummer entropy must therefore equal the observed
finite-r value `(1-1/r)^2`. The implementation checks that equality on every
matched Kummer permutation. A gap against the unconditional reference can
thus reflect already-known point-negation symmetry, not a new EC mechanism.
For coarser invariant features, which assign the same value to several
sign-pairs, the matched null can genuinely reassign which pairs share a
feature; its entropy need not be invariant. Such a gap remains an observation,
not a scalar decoder or novelty claim.

## Calibrations and development tests

Required controls are checked during every measured row where applicable:

- Constant projection D=0; full point D=0.
- Kummer x D=(1-1/r)² bits over the full group.
- Kummer x D=1 bit after conditioning both inputs to be nonidentity.

The development test passes **576 checks**, including six odd prime cyclic
orders, independent slow contingency-map entropy comparisons, deliberate
wrong one-bit Kummer calibration and wrong group-sum mutation detection,
malformed/missing image-label rejection, exact permutation fibre preservation,
all 361 EC pair-sum checks, 19 actual EC projection calculations, and 99-null
output serialization on the p=17 order-19 Kummer fixture. Additional tests
verify matched identity/sign invariance, complete multiset preservation,
Kummer entropy equality under repeated pair shuffles, rejection of a
non-invariant matched-null request, and serialization of all matched samples.

Commands actually executed on the final source:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  /workspace/classical-ecdlp-lab/src/lossy.cpp -o /tmp/ecdlp-lossy-selftest
/tmp/ecdlp-lossy-selftest --self-test
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  /workspace/classical-ecdlp-lab/src/lossy.cpp -o /tmp/ecdlp-lossy-selftest-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/ecdlp-lossy-selftest-sanitized --self-test
```

Both final executions exited 0 with

`L9 SELF_TEST_PASS checks=576 null_repetitions=99; exact toy entropy calibration only`.

No warnings were emitted. Leak detection was explicitly disabled; no
LeakSanitizer pass is claimed. Earlier development suites passed at 80 and
111 checks before the independent reference and EC pair-sum suite were fully
strengthened; 472 checks passed before the matched-null extension. Those
earlier suites are not the final source receipt.

## Cost and interpretation limits

Each row records r projection evaluations, actual feature exponentiation
calls, exact observed/unconditional/matched/calibration pair visits, conditional and nonzero
joint cells, support sizes, and logarithm-table entries/storage bytes. The
enumerated orbit requires r group additions and is reused across the panel.
Fixture certification, dictionary construction, sorting, parsing and process
costs remain in the full command's external elapsed/CPU/memory receipt; the
local counters are not a complete machine-instruction model.

The output refuses to overwrite an existing path. Any calibration,
histogram-mass, fibre-profile or malformed-input failure exits nonzero;
previous partial output remains for the root runner to archive. No successful
completion line is printed after a thrown error.

Below-null entropy may motivate a separately frozen structural/prediction
study. It is not scalar-bit leakage or scalar recovery. Constant and full
point projections both have zero conditional entropy and radically different
fibre sizes. Failure of this finite panel cannot close all probabilistic
representations or belief-propagation algorithms. No propagation decoder or
target-local unknown-scalar constructor is supplied.
