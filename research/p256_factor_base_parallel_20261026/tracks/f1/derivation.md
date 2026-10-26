# A quadratic-chain quotient and exterior-cube extractor

26 October 2026, TASK-20261026-a0cc5b. Derived argument, prepared before data.
This is neither a proof-assistant certificate nor an independently reviewed
complexity claim.

## Scalar quotient retains the chain

Over K=Fp, put S=2^k and

    A = K[z0,...,z(k-1)] /
        (zi^2-z(i+1)-2 for i<k-1, z(k-1)^2-c-2).

Successively adjoining each variable backwards gives a free K-module with the
S binary monomials `product zi^ei`, `ei in {0,1}`, as basis. Elimination identifies
A with K[t]/(D_S(t)-c), with t=z0. Multiplication C by z0 is constructed directly
by binary carries: `zi^2=z(i+1)+2`, and the last carry uses `z(k-1)^2=c+2`.
The solver does not expand D_S or enumerate its roots to construct C.

For c different from ±2, D_S-c is separable (odd p and p does not divide S).
Thus over an algebraic closure A is a product of S fields, and C is diagonal
with the S distinct scalar roots as eigenvalues. The input is not admitted when
this separability condition fails.

## Distinct-coordinate factor space

On V=exterior^3 A, dimension C(S,3), define E1, E2 and E3 by the elementary
symmetric action of C in the three slots. For example E1 applies C in each
single slot and sums; E2 applies C in each pair of slots; E3 applies it in all
three. These operators commute. In the wedge of the scalar eigenbasis, one
one-dimensional character corresponds to each unordered three-element root set,
with E1,E2,E3 eigenvalues its elementary symmetric coordinates.

For the committed symmetric relation polynomial P=S4(s1,s2,s3,x(Q)), the exact
kernel of P(E1,E2,E3) is therefore the direct sum of all distinct-coordinate
characters satisfying S4. It has one dimension per geometric state. This is the
same reduced distinct-divisor algebra as the first pass, represented by its
regular character module rather than an expanded Groebner calculation.

The implementation expands only the fixed-degree S4 into ordered root variables
x1,x2,x3. A symmetric polynomial F(C1,C2,C3) preserves the alternating relations,
so its action descends to the wedge quotient. Its column on
`vi wedge vj wedge vl` is exactly

    sum fabc (C^a vi) wedge (C^b vj) wedge (C^c vl).

There is no extra factor of 6. The quotient map from the tensor cube sends the
displayed ordered tensor to that wedge; symmetry makes its image independent
of the representative modulo alternating relations. This avoids dense products
of the 560-dimensional elementary operators. It does not hide the size of the
resulting operator or its elimination.

## Repeated coordinates without a root-domain scan

For exactly two equal coordinates, use A tensor A with characters (x,y), and
evaluate S4 at `(2x+y,x^2+2xy,x^2*y)`. Let W be the relation operator's kernel.
Multiplication by x-y commutes with every coordinate operator. Its image on W
removes exactly diagonal characters and retains every off-diagonal character.
The resulting character count is a subset of S(S-1); x is the distinguished
repeated coordinate. The all-equal stratum uses A itself and substitution
`(3x,3x^2,x^3)`. Both constructions are reduced because they are invariant
subspaces of a product of one-dimensional separable characters. All three
strata together exhaust coordinate triples, including repetitions.

## Certified rational character extraction

An RREF kernel basis K is checked by M*K=0, and its dimension equals
`n-rank(M)`. Independent pivot rows of K give a square invertible row minor.
Solving on that minor restricts each E_i to the kernel; full rectangular
identities `E_i*K=K*T_i` are checked, not inferred from the minor alone.

If there are d characters, some `T1+t*T2+t^2*T3` separates them among
`0 <= t <= 2*C(d,2)`: each pair forbids at most two t values, and the actual p
must exceed this bound. The code checks a squarefree completely split
characteristic polynomial of degree d, each one-dimensional eigenspace and all
three eigenvalue identities. If no such complete extraction is certified, it
reports unknown; it does not reinterpret a missing eigenvalue as an empty set.
Extracted monic cubics are factored, their root multiplicity stratum is checked,
each root is checked against the original scalar chain, every Fp curve lift
and sign is checked, and all signed point sums are verified.

The separate reference enumerates the full small fixed domains, computes an
independent quadratic-resultant S4 condition and uses Jacobian point arithmetic.
It never supplies roots, matrix coefficients or answers to the implicit solver.
Equality of complete state and signed-solution sets is a further finite-instance
check. It is not independent scientific review or a cost theorem.

## Arity-four control is explicitly finite enumeration

The depth-two arity-four control is a separate complete inverse-chain
enumeration, followed by all signs and point checks. It is not called implicit
extraction. Its five coordinate partitions are `[1,1,1,1]`, `[2,1,1]`, `[2,2]`,
`[3,1]`, `[4]`, with respective counts

    C(S,4), 3*C(S,3), C(S,2), S*(S-1), S.

Their sum is C(S+3,4). Five deterministically constructed positive targets,
one from each partition, are retained as correctness controls; every domain
state and every signed solution remains in the comparison. A generic monic
quartic remainder circuit verifies squarefree supports numerically. Repeated
coordinate factors themselves must not be claimed to divide a separable F.

## Limits

The new implicit representation stores a C(S,3)-dimensional operator and pays
for its construction, elimination, kernel extraction, curve lifting, failures
and verification. Its dimension still grows cubically in S and exponentially
in k. No method-cost comparison, high-depth solve, success-rate estimate,
large-base advantage or end-to-end ECDLP implication follows from completing
the fixed k=3/k=4 cases. A watchdog or memory failure is an unresolved execution.
