# Targeted exact projection follow-up: implementation notes

Implementation: `src/projection_scale.cpp`, C++20. This is an exact finite
observation/control instrument. It supplies no scalar decoder, attack-cost
comparison, significance result or novelty claim. The implementation author
ran development self-tests only; no `--run` of the fresh follow-up cohort was
executed. Root owns source/protocol freeze, admission and scientific execution.

## Interface and domains

```
projection_scale --self-test
projection_scale --run FIXTURES_TSV FRESH_OUTPUT_JSONL
```

Output scope is `exploratory_toy_followup`, track `L9-scale`, fixture key
`fixture`, and feature key `projection`. Exactly six rows are emitted for every
fixture, in this order:

1. `full_point`
2. `constant`
3. `kummer_x`
4. `x_mod_7`
5. `power_residue_5`
6. `x_hash_7`

An unavailable fifth-power map is a separate `not_applicable` row, not a
negative observation. Thus the 24-fixture frozen cohort will produce 144 rows.
No root cohort measurement was performed by this collaborator.

`r` must be odd prime and at most 8191; public field primes are bounded by the
shared header to 65535. The registered root cohort has r below 4096. Both
`ordinary` and `power5` strata require nonspecial-j, non-anomalous, ordinary
curves; `power5` also requires p=1 mod 5. The shared reader certifies the small
field/subgroup/whole-curve parameters by its explicit enumerative checks. The
module additionally checks the follow-up stratum conditions. All unsupported
parameters are rejected and are not mathematical negative results.

## Actual computations

For `orbit[k]=[k]P`, all ordered point pairs are counted for

```
Dpair = H(phi(X+Y) | phi(X),phi(Y)).
Db    = H(phi(2X+bP) | phi(X)),  b in {0,1}.
```

The scalar-labelled orbit is explicitly charged observational/reference
instrumentation. It is not a public target-to-scalar map or an uncharged
constructor for the separate approximate decoder. Pair operations use
`(i+j)%r`; unary operations use `(2*i+b)%r`. The development suite checks both
against actual EC addition on the p=61,r=19 fixture.

Integer conditional/joint counts are exact. Instead of adding logarithms in
the hot pair loops, the code accumulates integer *frequencies of counts*, then
evaluates

```
(sum_n margin_count_frequency[n]*n*log2(n)
 -sum_n joint_count_frequency[n]*n*log2(n)) / population.
```

Long-double logarithms and compensated summation supply the final numerical
entropy. Marginal and joint population sums are checked separately. Pair log
tables stop at the square of the largest input fibre size; unary tables use
the same available bound. This avoids an r-squared long-double table for a
small-alphabet projection. Exact support histograms, weighted support and
nonzero-cell counts are retained. The 64-bit FNV joint-table checksums are
explicitly noncryptographic; root's artifact hashes provide custody.

### Frozen feature definitions

Except for the deliberately constant projection, infinity has raw label zero.

- Full point: finite label `1+x*p+y`.
- Constant: every point has label zero.
- Kummer: finite label `x+1`.
- Modulo seven: finite label `1+(x mod 7)`.
- Fifth power: x=0 has label 1; otherwise `1+x^((p-1)/5) mod p`. It is available
  only when 5 divides p-1. The exponentiation is counted.
- Public x hash: finite label
  `1+mix64(uint64(x) XOR fixture.seed XOR FNV1a64("L9.scale.xhash7.v1")) mod 7`.
  `mix64` is the SplitMix64 finalizer. The hash depends on x alone and therefore
  retains point-sign symmetry. It is a public feature-complexity control,
  not an exact fibre-matched analytic null.

## Null ensembles and analytic shortcuts

Every applicable row retains 99 unrestricted-null entropy values for the pair
statistic and each unary statistic. Negation-invariant rows additionally retain
99 sign-pair-matched values for all three statistics. The latter permute labels
among the nonzero `{k,-k}` pairs and fix identity; exact fibre profiles are
checked for every measured shuffle. Fisher-Yates uses rejection-bounded draws
from SplitMix64. Every shuffle starts with the original labels; RNG state
continues between repetitions. The seeds are:

```
fixture.seed XOR FNV1a64("L9.scale.unconditional.v1/"+fixture.id+"/"+projection)
fixture.seed XOR FNV1a64("L9.scale.sign-pair.v1/"+fixture.id+"/"+projection)
```

For `x_mod_7`, available `power_residue_5`, and `x_hash_7`, all 99 unrestricted
and all 99 matched pair/unary values are measured by exact census. Nothing is
estimated by pair sampling. Their primary reference is the sign-pair matched
mean. Every individual value, mean, draw SD and range is retained; no inferential
test or multiple-comparison interpretation is performed.

Known controls use the following explicitly labelled derivations:

- Constant and full-point projections have pair entropy zero. Their observed
  pair statistics use the exact constant/bijection identity instead of looping
  over r-squared pairs. Their observed unary statistics are still computed by
  complete r-point censuses. Any relabeling of an injective or constant map
  keeps all three entropies zero, so all null values are derived and consume
  no permutation or pair/unary visits.
- Kummer observed pair and unary entropies are measured. The unrestricted 99
  nulls are also fully measured. Its sign-pair labels are injective on the
  nonzero pairs, with one separate identity label. A sign-pair shuffle is
  consequently a bijective relabeling of its codomain. Applying the same
  codomain relabeling to input/output feature variables preserves conditional
  entropy. All 99 matched values therefore equal the measured observed value;
  they are derived without pretending to have run 99 pair censuses.

Origin fields (`*_pair_value_origin`, `*_unary_value_origin`) distinguish
`derived_exact_invariance` from actual census values. Logical populations are
separate from actual `*_visits`; derived values have zero visits/swaps. The
observed/full conditional cell counts of a derived control are logical exact
counts, not a claim that those cells were physically visited. Each row exposes
the actual pair and unary visit totals, projection evaluations/powers and log
table storage. Full process resource records also include certification,
orbit, sorting, codec and allocation work not represented by pair visits.

For Kummer the development/calibration requirements are:

```
Dpair=(1-1/r)^2;  D0=0;  D1=(r-1)/r.
```

The pair statistic conditioned on both input points being nonidentity is one
bit. Doubling is deterministic on x-coordinates. For `b=1`, each nonidentity
sign pair has two distinct output x-values: equality would require 4X=0 or
2P=0, impossible in the stated odd prime-order subgroup. The identity input
has a single output, yielding D1=(r-1)/r. The scientific rows verify these
finite-r references numerically; all derivations have their stated scope and
are not a general ECDLP claim.

## Lossless bounded row encoding

Labels and finite dictionaries use `base64_uint16_little_endian_v1`:
`projection_labels_u16le_base64` with `projection_labels_count`, and
`raw_dictionary_u16le_base64` with `raw_dictionary_count`. Decode base64 into
bytes, then successive unsigned 16-bit little-endian words. Label order is the
canonical orbit order k=0,...,r-1. Dictionary order is sorted raw feature value.
Fibre sizes are run-length pairs `[size,consecutive_dictionary_labels]` in
`fibre_sizes_rle`. No outcome or null value is dropped by this encoding.

Full-point raw labels may exceed uint16. That control instead includes its
exact dictionary-regeneration descriptor: sort the public `0`/`1+x*p+y`
values over its explicitly enumerated orbit. Its entire compressed label
vector and exact all-one fibre profile remain present. This is representational
compression, not an uncharged fast inverse.

All pair/unary integer tables reconstruct exactly from the decoded label
vector and the declared cyclic addition/double/add rules. Large tables are
not duplicated in each JSON row. Any unexpected row above 60 KiB is written
and then rejected, allowing root's failure-rescue path to retain the complete
stream rather than silently dropping the offending row. Normal output
overwrites are refused.

## Development validation

Final strict normal and AddressSanitizer/UndefinedBehaviorSanitizer tests pass
769 checks. Commands, with the follow-up directory as cwd:

```sh
set -e
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror src/projection_scale.cpp \
  -o /tmp/projection-scale-final
/tmp/projection-scale-final --self-test
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -fsanitize=address,undefined \
  -fno-omit-frame-pointer src/projection_scale.cpp \
  -o /tmp/projection-scale-final-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/projection-scale-final-sanitized --self-test
```

Leak detection was explicitly disabled for the inherited tracing limitation;
no leak-check pass is claimed. The checks include six small odd prime cyclic
orders, independent slow contingency-map references for pair and unary
entropy, constant/injective/Kummer controls, a dyadic two-symbol domain with
four pair/two unary input cells, explicit matched Kummer reshuffles, wrong-sum
and wrong one-bit calibration traps, malformed/non-invariant label rejection,
codec byte order/padding/range and maximum supported label count, all 361
actual EC pair operations plus 38 unary operations, and serialization of all
six p=61 feature/control rows with every null array retained.

The first strict build reported misleading indentation in three compact
statements and an unnecessary range-loop copy. Those diagnostics were repaired
before the first successful self-test. The intermediate suite had 726 checks;
dyadic-domain and maximum-codec checks strengthened the final suite to 769.
These are development attempts, not scientific measurements or evidence of a
cryptanalytic effect. No new-cohort result is claimed here.
