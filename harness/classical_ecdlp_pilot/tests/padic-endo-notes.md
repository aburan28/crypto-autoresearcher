# L1 and L3 implementation notes

This is an implementation/development record, not a scientific trial, novelty claim or ECDLP recovery result. Root owns protocol freeze and pilot execution. No `--run` on the scientific fixture manifest was invoked by this implementation task.

## Interface

Compile `src/padic_endo.cpp` with C++20 and the root-owned `src/common.hpp`. CLI:

```
padic-endo --self-test
padic-endo --run FIXTURES_TSV OUTPUT_JSONL
```

The second command emits one L1 and one L3 row per certified fixture. It returns nonzero on any failed invariant. Partially written rows must be preserved and classified by the supervisor if a later failure occurs. The common fixture parser independently certifies field/subgroup primality, whole-curve order, generator order and non-anomalous status.

## L1: explicit section and exact arithmetic

For a finite point R=(x,y) in the odd-prime subgroup, y is nonzero. Work in Z/p² using the canonical integral curve coefficients a,b. The x section is x^p mod p² (including x=0), whose reduction is x and whose p-th power is itself. The unique Hensel y section reducing to y is obtained from

`c = ((x_lift³+a*x_lift+b−y²)/p) / (2y) mod p`,

with the residual first reduced modulo p² and explicitly checked divisible by p. Then `y_lift=y+p*c mod p²`. Infinity maps to canonical projective infinity. Every point is checked against the full Jacobian curve equation over Z/p² and for unimodularity: at least one coordinate must be a unit mod p.

The ring multiply canonicalizes both factors before an unsigned 64-bit product. Since p<=65535, p²<2³² and the product fits uint64 exactly. Unit inverses use Euler's exponent p(p−1)−1, after explicitly rejecting nonunits. No floating-point p-adic calculation is used.

The code computes `[r]S(R)` by both left-to-right and right-to-left double-and-add. At every step its reduction is checked against separately coded common affine multiplication of the public R by the known intermediate scalar. It verifies the projective curve equation after every nontrivial operation. The two paths' formal parameters must agree. With Jacobian affine coordinates x=X/Z²,y=Y/Z³, the local parameter is `t=−XZ/Y`; Y must be a unit and t must be divisible by p. The recorded value is t/p mod p. It never substitutes zero for a failed chart.

The incomplete Jacobian formulas are used on a checked restricted path, not asserted complete on all pairs over a ring. Left-to-right proper scalar prefixes stay below r; before a bit-one addition the even prefix is never congruent to 1 mod odd r. The only opposite reduction can occur at the final sum r, where the addition has a unit y-difference and yields a valid point in the infinity chart. Right-to-left accumulation is strictly smaller than the current power-of-two summand, so equal nonidentity reductions cannot occur; a partial sum r is final. Nonidentity points in the order-r subgroup have no y=0. Curve/unimodularity/reduction checks fail closed if these conditions are violated. The formulas are not exposed as a general group implementation over arbitrary ring charts.

L1 records the full section-defect profile, every pair additivity defect, a defect histogram, image size, sign checks and a first nonadditive witness. It checks actual formal-point doubling for all p parameters `t=p*c`. A separately marked hard-lift control constructs `[k]S(P)` by r sequential projective additions using **known scalar labels** and checks its formal response equals k*D(P) mod p. This is deliberately supplied advice and is excluded from the public computable-section prediction.

The fixed public predictor is `D(Q)/D(P) mod p`, then reduced modulo r, with the constant-zero predictor when D(P)=0. This weak predictor is fully specified rather than fitted from pilot outcomes. It is not a claimed decoder, and wrapping when r>p remains part of its actual misses. Counts for nontrivial targets exclude scalar labels 0,+1,−1.

Before any pilot data, the primary null was fixed to 99 sign-pair permutations with independent sign orientations, holding labels 0,+1,−1 fixed. This preserves the exact feature multiset, generator calibration and the known odd symmetry. A second, explicitly secondary 99-permutation reference shuffles all labels without conditioning those anchors. Both raw hit-count arrays are emitted. These are exploratory diagnostic references, not claims of significance or successful scalar recovery. The two RNG domains are fixture.seed XOR `0x4c315045524d5554` and `0x4c31554e434f4e44`.

## L3: endomorphism controls

Every fixture exhaustively checks negation with eigenvalue r−1. Its witness `1+(r−1)=0 mod r` holds for every k; the compatible scalar count is r.

For a=0 and p=1 mod 3, search for an explicit nontrivial cube root beta in Fp, verify beta³=1, and map `(x,y)` to `(beta*x,y)`. An enumerated reference orbit finds the induced subgroup eigenvalue lambda. Lookup probes and cube-root candidate tests are recorded, and every target is checked against `[lambda*k]P`. The relation `1+lambda+lambda²=0 mod r` must hold and is explicitly classified k-independent. If the subgroup is not stable, the row reports that condition; it does not invent an eigenvalue. Non-j0 fixtures report the extra action inapplicable.

The orbit enumeration is explicitly charged r reference additions; neither its dictionary nor eigenvalue lookup is presented as cheap inversion. A new non-generic coordinate observable and decoder remain absent. No rho experiment or advantage is asserted.

## Development checks

The fixed developer fixtures are (p,a,b,P,r,N)=(5,0,1,(0,1),3,6), (17,2,2,(5,1),19,19), and (23,1,1,(17,3),7,28). These are not the scientific pilot cohort. The final explicit assertion counter is 365,912. Additional internal `require` checks in profiles and arithmetic also run but are not added to that counter.

Checks include exhaustive multiplication calibration over the three small p² rings; all unit inverse checks; Teich/Hensel and sign checks; independent affine-vs-Jacobian addition/doubling over p² on all applicable developer pairs; nonunit inversion rejection; non-unimodular point rejection; both full L1/L3 rows; hard-lift linearity; and null-multiset preservation. JSON output calibration on the p17/r19 developer fixture verifies both row types, profile length, 361 exact pairs and 99 permutation counts.

Exact normal build command:

```
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror src/padic_endo.cpp -o /tmp/padic-endo-selftest
/tmp/padic-endo-selftest --self-test
```

Sanitizer build replaces `-O2` with `-O1 -g -fno-omit-frame-pointer -fsanitize=undefined,address`; run with `ASAN_OPTIONS=detect_leaks=0`. Leak checking is not available under environment tracing. The initial strict compile encountered a signed-char conversion warning in root-owned common.hpp; root corrected it. Earlier intermediate self-test versions passed 364,848 checks before independent affine p² pair checks were added. Final normal/sanitizer output and source hashes are reported to root separately so stale intermediate digests are not treated as final.

Counters name their scope: p² ring arithmetic includes construction and verification; the public-section snapshot is separately emitted from later controls. Independent affine reduction checks, orbit additions, lookup probes and root-search candidates are separate counters. Total runtime/memory and certification overhead are the supervisor's measurements. These are not converted into a comparative attack cost.
