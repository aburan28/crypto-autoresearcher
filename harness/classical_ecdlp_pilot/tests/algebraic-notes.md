# L5/L7/L8 algebraic diagnostic implementation

This implements finite **enumerative controls**, not a new direct-inversion construction. The executable interface is `algebraic --self-test` or `algebraic --run FIXTURES_TSV OUTPUT_JSONL`. Existing output files are refused so a failed or completed attempt cannot be overwritten silently. Root owns scientific execution after the protocol/source freeze; the module author has run development tests only.

## Development checks

The fixed unit fixtures are (p,a,b,P,r,#E) = (5,0,1,(0,1),3,6), (17,2,2,(5,1),19,19), and (23,1,1,(17,3),7,28). All are checked by the common certificate routine. The p=5 fixture is an exception control, not an ordinary-curve study instance. The three fixtures produce three track rows each internally; `--self-test` reports nine rows and exits nonzero on any failed identity, count, mutation or encoding check.

Compile commands:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror src/algebraic.cpp -o /tmp/ecdlp-algebraic-development
/tmp/ecdlp-algebraic-development --self-test
g++ -std=c++20 -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror src/algebraic.cpp -o /tmp/ecdlp-algebraic-development-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/ecdlp-algebraic-development-sanitized --self-test
```

Leak checking is explicitly disabled under the known environment tracing limitation. ASan/UBSan and normal final-source results are reported to root separately; no scientific `--run` is part of this development check.

## L5: branch algebra and target pinning

For each t=1,...,6, explicitly evaluate all `2^t` Boolean Lagrange idempotents

`e_u(x) = product_i (x_i if u_i=1 else 1-x_i)`

at every Boolean assignment. The resulting evaluation matrix is checked entry by entry, its exact rank is computed by Gaussian elimination over Fp, and idempotence, pairwise orthogonality and the partition of unity are checked. The known reduced algebra is `Fp^(2^t)`; the recorded rank is the computed rank of this explicit evaluation map. No Gröbner basis or radical normal form of a new ladder quotient is calculated.

Independently project branch labels to the explicitly enumerated EC endpoints `[u]P`. Record the point-image size and the first actual pair of different labels with the same endpoint, if any. Without canonical range, orbit wrap can merge distinct labelled branches. With `u<r`, the supported endpoint labels are injective. Two syntactic copies retaining an additional selector remain distinct support points; merely deleting their labels is not a lossless quotient.

For every canonical target, enumerate the complete bit domain to check exactly one target preimage; an incompatible full scalar prefix checks a zero-solution restriction. These are target-local truth controls. The original theorem-deferred IDEA-111 solver is not launched, its frozen gate is not changed, and no target-local constructive invariant is supplied. Point tables, explicit evaluation matrices and their operations are charged.

## L7: coefficient-prefix equality

Construct each target's Boolean truth table by actual EC point comparisons against a previously constructed complete orbit. Inputs `b>=r` are zero. Compute its multilinear coefficients independently by the Boolean Möbius transform. For every MSB prefix of every canonical target, compare explicit truth summation with the top coefficient after substituting the fixed prefix. If d low bits remain, that coefficient is the XOR of `a[(v<<d)|(2^d-1)]` over submasks v of the fixed high prefix. This is a finite algebraic identity, not an efficient oracle.

Controls include explicit bijective affine bit maps, a charged tiny seeded permutation table, a wrong top-coefficient mutation, two satisfying inputs whose parity cancels, an unconstrained doubled witness, zero-polynomial equation/indicator orientation, and the invalid naive `x OR x -> x+x` substitution. The same compact parity specification applies to the permutation; it is not evidence of EC-specific tractability. All truth construction, Möbius XORs, prefix summation and coefficient access are recorded. Calibration map/table entries are separately named. The all-target prototype refuses r>4096 instead of starting an undeclared huge enumeration.

## L8: Fp count and degree audit

For each target, separately interpolate its truth table over Fp using subtraction, rather than reusing characteristic-two coefficients. Verify every Boolean value. Use the explicit polynomial constraints

`b_i(b_i-1)=0`, `C_range(b)-1=0`, `P_Q(b)-1=0`,

and degree-one prefix pins. The `z(z-1)` root condition is checked for every z in the field. Since those equations force each variable to be 0 or 1, the Boolean truth enumeration exhausts all solutions over Fp; it is unnecessary to enumerate every tuple in Fp^ell. The source code records the degree of each equation class, target-degree minima/maxima across all targets, sums with every prefix length and the exact nonnegative Ax–Katz lower-bound exponent `max(0,ceil((n-sum d_i)/max d_i))`. That exponent is zero for this encoding; a known singleton cannot simultaneously be subject to a positive divisibility conclusion.

The field polynomial is constructed from the **full truth table**. It is not a gate-polynomial compiler and not an inexpensive public exact-residue algorithm. Its target/singleton and empty-prefix counts share L7's truth evidence and are not independent scientific confirmation. The explicit integer count pair 0 and p has the same divisibility receipt and rejects a divisibility-only existence inference. Integer unweighted counts, Fp coefficients and F2 tagged counts are kept separate.

## Accounting and limits

Rows label their scope `exploratory_toy_diagnostic` and outcome `complete_control`. Exact matrix entries, algebraic operations, orbit entries, Boolean truth entries, prefix checks and encoded coefficient payload are recorded with their own units. One orbit is shared by all three track rows within a fixture; its repeated reference counts are not three physical orbit constructions. L7 and L8 also share truth tables. The OS receipt records complete process cost, including certification and controls; arithmetic counters do not replace wall time or include every low-level operation inside the common field inversion routine. No ratio to group-addition counts or solver speed claim is made.

The main-coefficient payload field counts three byte arrays and two int64 coefficient arrays. It excludes vector allocator overhead, the separately disclosed orbit, calibration temporaries and rank-matrix storage; it is not a claim of complete process peak memory. No standalone successful control proves an unrestricted lemma or closes any wider mathematical family. Exact replay and the source hash are necessary for these finite observations; independent review and all missing fast constructions remain downstream.
