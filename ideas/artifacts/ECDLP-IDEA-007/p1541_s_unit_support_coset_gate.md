# P1541 Miller S-unit support-coset gate

## Status and claim boundary

- Record type: theorem-only producer gate
- Root hypothesis: `ECDLP-IDEA-007`
- Candidate: `P1541`
- Claim: `CLM-P1541-S-UNIT-SUPPORT-COSET-DECODER`
- Evidence scale: exact divisor-class and counting statements plus literature controls;
  no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `UNREVIEWED_EXACT_INTERFACE__SUPPORTED_PRINCIPAL_DIVISORS_ARE_THE_ABEL_JACOBI_KERNEL__TARGET_FUNCTIONS_FORM_AN_AFFINE_KERNEL_COSET__MILLER_PROGRAMS_CONSTRUCT_OR_VERIFY_AFTER_A_COSET_REPRESENTATIVE_IS_KNOWN__BOUNDED_COEFFICIENT_SUCCESS_IS_AT_MOST_CANDIDATE_MASS_OVER_N__STRUCTURED_COSET_DECODER_UNSUPPLIED__OPEN`

IDEA-007 is operation-distinct from the exhausted elliptic-net, translated-orbit,
QRT/Lax, scalar-period, and summation-polynomial solver families only at one point:
it proposes to find a supported principal divisor, rather than to encode or verify one
already known. This receipt freezes that point as an inhomogeneous kernel-coset problem.

The relevant S-unit group supplies homogeneous relations among fixed support points.
For a moving input `R`, every desired function lies in a torsor over that group. A
Miller program can compactly construct a function once one point of the torsor is
known; it does not presently provide that point. A qualifying successor must therefore
name a structured syndrome/coset decoder, not a function evaluator, certificate, lattice
format, or generic relation solver.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md`:
  `f87ad5d20669dc6e00eb9ab935d3945444999f899555caf4646da3fc7cfd74a0`
- `ledger/H-FB-001.yaml`:
  `5c63043f9f97e38a15aeb93c755bd9c4316884e45331ba583f027f3467d90f95`
- `ledger/EV-FB-001.yaml`:
  `2165d310ff41b9d575f7427ecc8465adcff391ed4ba11faaab8ab8ceba4f3f5b`
- `ledger/H-REP-001.yaml`:
  `55fa62651d57b3bd860c1e15ec60657ad5d502874d813f0d0e1288ff7ce6b483`
- `ideas/artifacts/ECDLP-IDEA-006/p1540_r1_independent_audit.md`:
  `8032be2d3a645ac64c046783191cc9c634715518eb18e4702acf66e077223d45`

## Exact genus-one divisor interface

Let `E/F_p` be a nonsingular elliptic curve with identity `O`, let

```text
G=<P>,  |G|=N prime,
S={F_1,...,F_B} subset G\{O},
F_i=[a_i]P.
```

For `e=(e_1,...,e_B) in Z^B`, define the degree-zero supported divisor

```text
D(e)=sum_(i=1)^B e_i*((F_i)-(O)).
```

The genus-one Abel-Jacobi isomorphism sends the divisor class of `D(e)` to

```text
theta(e)=sum_(i=1)^B [e_i]F_i in G.
```

Therefore

```text
D(e) is principal  iff  theta(e)=O.
```

Let

```text
L=ker(theta:Z^B -> G).
```

Then `L` is exactly the exponent lattice of principal divisors supported on
`S union {O}`. Modulo nonzero field constants, the corresponding rational functions
form the fixed-support function-field S-unit group.

Because every nonzero `F_i` generates the prime-order group `G`, `theta` is surjective.
The first isomorphism theorem gives

```text
Z^B/L ~= Z/NZ,
[Z^B:L]=det(L)=N.
```

This determinant is independent of the Miller representation, line-function
dictionary, lattice basis, or reduction backend.

## Moving-target coset theorem

For a moving input `R=[r]P`, IDEA-007 seeks coefficients `e` and a function `f_R` with

```text
div(f_R)=(R)-(O)+D(e).
```

The same Abel-Jacobi map gives

```text
div(f_R) exists  iff  R+theta(e)=O
                   iff  sum_i e_i*a_i=-r mod N.
```

If `e_0` is one solution, every solution is exactly

```text
e_0+L.
```

Thus the fixed-support S-unit group is the homogeneous kernel `L`, while the functions
for `R` form an affine torsor over it. Multiplying one known `f_R` by an S-unit walks
within this affine coset; it cannot create the first representative without solving the
inhomogeneous condition.

This distinction corrects the phrase "precomputed S-unit module." A target-independent
module can precompute homogeneous relations and function encodings. The moving zero at
`R` is not in the fixed support, and the required target function is not an element of
that module until a coset seed is supplied.

## Miller-program boundary

For curve points `A,B`, the standard line/vertical quotient has divisor

```text
(A)+(B)-(A+B)-(O).
```

Addition chains compose these elementary functions. Given coefficients `e` satisfying
`R+theta(e)=O`, one can group the points in the divisor by additions and construct or
evaluate a compact straight-line program for `f_R`. Conversely, replaying all line and
vertical divisors verifies both the program and the terminal group relation.

These are valuable construction and verification operations. They occur after the
support coefficients and their terminal zero-sum relation are known. Replacing an
explicit function by a short program reduces representation size; it does not alter
`theta`, `L`, the target syndrome `-R`, or the set of coefficient vectors that solve it.

The operation that would matter is therefore:

```text
SUPPORTED-COSET-DECODE(E,P,S,R,C):
  output e in a frozen admissible coefficient family C
  such that theta(e)=-R,
  or return a complete failure result.
```

The output must be found from public point and function-field data without known
`a_i`, known `r`, an oracle-injected support, or enumeration whose full cost exceeds the
gate.

## Full-kernel precomputation is already factor-log state

Suppose preprocessing outputs a full basis for `L`. Smith normal form computes the
cyclic quotient `Z^B/L` and the images of all standard basis vectors, up to one
automorphism of `Z/NZ`. Those images are the relative factor-base logarithms
`c*a_i mod N` for one unknown nonzero scale `c`.

Add the public known-log anchor `P` to the support. A full kernel basis for the enlarged
map

```text
Z^(B+1) -> G,
(e_0,e_1,...,e_B) |-> [e_0]P+sum_i [e_i]F_i
```

fixes the quotient scale because the first standard basis vector maps to `1 mod N`.
Smith normal form then recovers every `a_i`. Consequently, a claimed cheap algorithm
that constructs the complete principal-divisor lattice, rather than a small sampled
subset, already performs the factor-log solve in its preprocessing. That cost cannot be
hidden under "S-unit basis construction."

This is not a lower bound against partial relation sampling. It is a semantic and cost
identity for complete-kernel claims.

## Candidate-mass success bound

Let `C subset Z^B` be any finite target-independent coefficient family permitted by a
frozen support, sparsity, norm, and bit-length rule. For uniform `R in G`, define

```text
M_R=|{e in C: theta(e)=-R}|.
```

Double counting gives

```text
sum_(R in G) M_R=|C|,
E_R[M_R]=|C|/N.
```

Therefore

```text
Pr_R[M_R>=1] <= min(1,|C|/N).
```

The same statement holds for uniform relation inputs `[a]P` and for blinded target
inputs `Q+[t]P`. It is independent of how functions are encoded or verified.

For coefficient alphabet `[-H,H]` and support size at most `k`,

```text
|C| <= sum_(j=0)^k binom(B,j)*(2H)^j
```

after omitting zero coefficient choices in an upper bound. A proposal with
`|C|=N^(gamma+o(1))`, `gamma<1`, has success exponent at least `1-gamma`. A proposal
with larger candidate mass may have abundant witnesses, but must still locate one
without materializing the same mass or solving the hidden modular syndrome.

This is a one-sided density bound, not a query lower bound. A structured decoder could
in principle beat enumeration. Such a decoder is precisely the mechanism P1541 keeps
open and must state explicitly.

## Relation collection and target descent are the same decoder family

For a uniform known relation sample `R=[a]P`, a successful coefficient vector gives

```text
a+sum_i e_i*a_i=0 mod N.
```

After enough independent rows, factor-base logs can be solved. For the target descent,
one samples `R_t=Q+[t]P`; the same decoder gives

```text
x+t+sum_i e_i*a_i=0 mod N.
```

Hence

```text
x=-t-sum_i e_i*a_i mod N.
```

Miller verification certifies each equation geometrically, but it does not improve the
row yield, rank, or target success probability by itself. A relation-only certificate
or a fast verifier is not a descent algorithm.

## Structured-decoder route screen

### Generic lattice reduction

The exact lattice `L` has determinant `N` in dimension `B`. A target is an inhomogeneous
coset. Applying generic CVP, nearest-plane, LLL, BKZ, or subset-sum machinery is a solver
choice unless the public point-derived basis has a proved geometry that changes the
complete exponent. A short vector in `L` is a homogeneous relation; the target needs a
representative in a different coset.

### Sparse addition chains

A sparse coefficient vector is an elliptic subset-sum or signed decomposition. Miller
lines record a chosen addition tree after the leaves are selected. Meet-in-the-middle,
generalized birthday, and summation-polynomial solvers remain the existing decomposition
controls unless a function-module invariant selects the support without their tables.

### Pairing or character evaluation

Evaluating a target function or S-unit at torsion points can map a verified divisor
relation to roots of unity. If exponent labels are required, the result is a
Frey-Ruck/MOV-style finite-field DLP whose extension degree, setup, and label recovery
must be charged. A multiplicative character can reject candidates; it does not
automatically output one coefficient vector.

### Full S-unit basis

Constructing all fixed-support S-units gives `L`. With a known-log anchor, it gives the
factor-base logarithms through Smith normal form. Without a target coset representative,
it still does not descend `R`. Calling this preprocessing polynomial in the output size
is insufficient when the output or its construction has exponent at least one half.

### Implicit algebraic syndrome decoder

This is the live exception. A compact target-independent arithmetic operation might use
function evaluations, valuations, residues, sparse module structure, or another exact
invariant to decode `-R` into one admissible `e` without enumerating `C`, computing the
full kernel, or solving another order-`N` DLP. No such operation is supplied in
IDEA-007. Its equations, success density, ambiguity, relation rank, target descent, and
complete cost are the required P1541 evidence.

## Complete cost gate

Retain IDEA-007's notation:

```text
B=N^(beta+o(1)),
dictionary/module setup=N^(c+o(1)),
one decoder attempt=N^(u+o(1)),
relation and descent reciprocal densities=N^(delta+o(1)), N^(delta_t+o(1)),
certificate verification=N^(v+o(1)),
stored state=N^(s+o(1)).
```

Under a verified sparse factor-log solve, the complete optimistic exponents are

```text
lambda=max(c, beta+u+delta, 2*beta, beta+v, u+delta_t, v),
mu=max(s,beta).
```

Dense rows replace `2*beta` by `3*beta`. The candidate-mass theorem additionally
requires

```text
delta,delta_t >= max(0,1-log_N(|C|))+o(1)
```

for uniform relation and blinded-target inputs. Decoder construction, failed attempts,
coefficient bit lengths, Smith form or module algebra, Miller-program generation,
complete divisor verification, rank defects, and final scalar verification all count.

Promotion would require one exact decoder with point estimate `lambda<=0.45`, upper
confidence bound below `0.50`, `mu<=0.45`, independent reproduction, and a mechanism
ablation showing that the function module changes the exponent rather than only the
certificate format. No current artifact meets this gate.

## Controls and falsifiers

### Required positive controls

- Given a planted coefficient vector satisfying the group relation, construct a Miller
  program and reproduce its complete divisor, including vertical-line exceptions.
- Given a full kernel basis with an included `P` anchor on a tiny group, recover all
  factor-base logs by Smith normal form.
- Exhaustively enumerate tiny `C` and verify the exact affine-coset partition and
  candidate-mass counts.

### Required negative controls

- Remove the Miller representation but preserve the same coefficient search; unchanged
  yield and search work identifies a representation-only control.
- Shuffle one support point, multiplicity, or target syndrome; every false divisor
  certificate must fail.
- Compare against direct subset sum, summation-polynomial decomposition, rho, BSGS, and
  pairing-transfer controls with all preprocessing and memory charged.
- Blind targets by unknown harness randomizers and forbid target-trained bases or
  post-hoc coefficient caps.

### Immediate falsifiers for the current formulation

- The reducer receives a supported divisor, group relation, coefficient vector, or
  known target log and only constructs its function.
- The claimed precomputed module contains only homogeneous S-units and no operation that
  finds a moving-target coset representative.
- A complete kernel basis is declared free or its factor-log content is omitted.
- Success is reported only among accepted outputs rather than over every uniform input
  and failed attempt.
- Pairing or character output is not converted to `x` with the field-DLP cost charged.
- Relation validity, a short program, or a recovered toy scalar is called a generic
  Shoup-bound improvement.

## Literature boundary

1. Victor S. Miller, *Short Programs for Functions on Curves: A STOC Rejection*,
   <https://doi.org/10.4230/LIPIcs.FUN.2024.34>. This gives the short-program
   construction context for functions with prescribed divisors; it does not supply the
   moving-support coset decoder.
2. Pierrick Gaudry, *Index calculus for abelian varieties of small dimension and the
   elliptic curve discrete logarithm problem*,
   <https://doi.org/10.1016/j.jsc.2008.08.005>. This supplies the divisor-class relation
   and decomposition control.
3. Gerhard Frey and Hans-Georg Ruck, *A remark concerning m-divisibility and the
   discrete logarithm in the divisor class group of curves*,
   <https://doi.org/10.1090/S0025-5718-1994-1218343-6>. This supplies the pairing
   transfer boundary.
4. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>. This is the generic comparison, not a
   theorem against coordinate-aware S-unit operations.

The exact sequence between functions, supported divisors, and divisor classes is
standard function-field algebra. The potentially new object is not the sequence or the
Miller encoding; it is an efficient structured decoder for the inhomogeneous target
coset. Novelty remains unverified.

## Producer decision

The IDEA-007 next action to draft a toy contract is premature. The named mechanism does
not yet specify the operation that chooses a target coset representative. A toy Miller
program generator would validate only construction and verification after support is
known, while the support-coset theorem shows that this is the original decomposition
condition.

P1541 is queued for one independent theorem audit. No contract, executable, point
fixture, S-unit basis, lattice reducer, relation campaign, or target descent should be
built until the audit either names a structured public syndrome decoder or returns the
candidate terminal inconclusive.

## Exactly one next action

Independently reconstruct the genus-one Abel-Jacobi kernel, moving-target affine-coset,
full-kernel factor-log, and candidate-mass theorems; then either specify one
target-independent implicit support-coset decoder with exact equations, complete
relation-to-descent output, and `lambda,mu<=0.45`, or return P1541 terminal
inconclusive. Do not draft or execute an IDEA-007 contract during that audit.

