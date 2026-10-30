# L2/L6 implemented diagnostics

Implementation: `src/sequences.cpp`, C++20 with the root-owned `src/common.hpp`.
These are finite exploratory observations and known controls. There is no new
ECDLP algorithm, unknown-index locator, cheap uniform reverse-state constructor,
or blind target-to-scalar decoder in this module.

## L2: EDS and translated coordinate blocks

The module evaluates the ordinary division-polynomial values W_n=psi_n(P) in
F_p, with psi_0=0, psi_1=1, psi_2=2y and standard psi_3/psi_4 seeds. Its odd/even
recurrences divide only by 2y(P), which is nonzero at a finite point of odd prime
order. It checks x([n]P)=x(P)-W_(n-1)W_(n+1)/W_n^2 for every 1<=n<r, W_r=0,
and Ward's two-index identity for all 1<=n<=m<=min(r-1,16). All failures throw.
It computes Berlekamp-Massey linear complexities of W prefixes of lengths
8,16,... and the complete r+1-value prefix. It does **not** assume W has period r.

For every known shift k in the explicitly enumerated truth orbit, it forms the
public translated sequence a_Q(n)=x(Q+[n]P), with Q=[k]P. It uses its certified
period r and represents infinity by the distinct symbol -1. A five-position
cyclic window is excluded if any input/output is infinity; excluded windows are
counted. Infinity is never silently mapped to an F_p value for interpolation or
linear complexity. The first half of remaining windows fit a four-input
quadratic over F_p; the untouched second half provides exact-match counts.

The frozen 15-feature order is
`1,x0,x1,x2,x3,x0^2,x0*x1,x0*x2,x0*x3,x1^2,x1*x2,x1*x3,x2^2,x2*x3,x3^2`.
RREF chooses the earliest available column/row pivot and sets free coefficients
to zero. Inconsistent training systems have no predictor; their would-be test
windows are not included in `test_predictions_attempted`. Consistent systems
with rank below 15 are explicitly counted as underidentified. There is no
least-squares or other silently substituted fit.

The JSON records every target's truth-shift, rank, consistency, training/test
window counts, exact matches if consistent, and BM complexity at the declared
coordinate prefixes. A JSON null in a BM profile means that prefix contains
infinity. Every full-period coordinate prefix contains infinity and is therefore
reported null. All scalar shifts include both signs; their labels are truth-side
instrumentation, not inputs to a proposed locator. The module also fits 99
seeded multiset-preserving permutations of the same coordinate/infinity list.
These are a deterministic PRNG ensemble, not new independent curves.

Modular additions, multiplications, inversions, feature rows, Gaussian row
eliminations, BM symbols, translated-sequence copies and shuffle swaps are
counted. Arithmetic counters exclude the shared EC certification/orbit backend;
the complete process cost must include it. Both packed coefficient bit length
and actual fixed-array payload bytes are named separately. No operation-count
ratio or timing is claimed as a solver advantage.

## L6: exact finite periodic residuals

The measured successor uses base 2, not IDEA-070's original base p. For each
e=0,...,min(bit_length(r),6) and j=0,...,2^e-1, it constructs the entire vector
`a((2^e*n+j) mod r)`, 0<=n<r. Exact lexicographic comparison deduplicates these
vectors across depths. The module records states per depth, total distinct
states, defined transitions, symbol lookups, comparison calls/symbols and stored
vector payload bytes. It verifies that equal residual functions have equal
observed 0/1 child residuals. Leaves need not have explored outgoing edges;
this is a bounded-depth residual measurement, not a complete automaton theorem.

Controls are full-point encodings, one seeded cyclic orientation change, and
99 frequency-preserving permutations. The full point code is zero for infinity
and 1+x+p*y for finite points. It is injective on the actual coordinate domain;
it is not an unknown scalar label. The x-only ambiguity is checked to have one
singleton fibre and (r-1)/2 two-element fibres, while full points have ambiguity
one. Constructing their truth orbit/dictionary costs r point additions and r
stored points. The orbit is built once per fixture and shared: L2 charges its
point additions, and L6 records reuse with zero additional orbit additions.

Small finite residual counts do not imply a cheap constructor or target
orientation. Storage figures are payloads, not complete allocator overhead;
the root runner's measured process RSS supplies the broader memory observable.
No cyclic-orientation ambiguity is solved by these controls.

## CLI and preservation

`--self-test` runs fixed developer controls only. `--run FIXTURES_TSV OUTPUT_JSONL`
reads/certifies the root manifest and emits one L2 and one L6 row per fixture.
It refuses to overwrite an existing output path. A late exception returns
nonzero and leaves any partial output for the root to archive. A single aggregate
JSONL may exceed 64 KiB after retaining all per-target data; partition by track
and fixture for Git publication rather than deleting cases or treating the
partition limit as a research budget.

No `--run` on the pilot cohort was executed by the module author before root
freeze/dispatch. A p=17, a=b=2, P=(5,1), r=N=19 developer fixture is embedded in
self-tests. Its two diagnostic rows were also emitted by a temporary C++ JSON
integration driver and parsed as JSON: 19 target profiles, 18 coordinate
identities, 136 Ward identities and 99 null permutations were present. This was
a fixed developer fixture check, not a registered scientific cohort.

## Development validation

Final source was compiled successfully with:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror src/sequences.cpp -o /tmp/ecdlp-sequences-dev
/tmp/ecdlp-sequences-dev --self-test
g++ -std=c++20 -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined \
  -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
  src/sequences.cpp -o /tmp/ecdlp-sequences-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/ecdlp-sequences-sanitized --self-test
```

Both final self-tests exit 0. Leak detection is explicitly disabled for the
known environment restriction; ASan and UBSan remain enabled. Controls check BM
on zero, geometric and Fibonacci sequences; exact recovery of 15 quadratic
coefficients from a full-rank unisolvent design; rejection of contradictory
interpolation; the known three-function periodic parity 2-kernel with six
transitions; and all p17 EDS, Ward, coordinate and residual smoke checks.

Earlier strict compilation exposed a sign-conversion warning in the shared
header, repaired by its owner, and a misleading-indentation warning in this
module, repaired before the final builds. One obsolete binary self-test ran
after that failed compilation because commands had been separated by a newline;
it is excluded from final-source validation. Both final compilation exit codes
were checked before final-source execution. No scientific conclusion follows
from those development repairs or the passing controls.
