# Degree, inventory and a certified complementary-point reference

Producer TASK-20261029-2e3655. This is symbolic analysis and fixed software
correctness testing. Independent review is pending at this producer snapshot.
No scientific run, measured advantage, novelty claim, proof-assistant proof,
unknown-scalar recovery or general ECDLP algorithm is established here.

## Inputs and literature

The accepted inputs are the exact, even-s, raw-S3 presentation results in
`research/prime_sat_regularity_20261029/grouped-proof.md`, as scoped by
DEC-20261029-0857a9, and the original presentation analysis in `proof.md`,
as scoped by DEC-20261029-ce5c57. Their hashes and decisions are pinned in
`coordination/prime_sat_costbridge_20261029/source-inputs.json`.

For even s>=2, p>max(3,s), nonsingular E over F_p, target R=(r,t) with t!=0,
and the nonzero original weights specified there, these inputs give

    d_bit = 1+3s/2,      d_group = s+1.

The qualified mutant-closure caps are d_bit+1 and d_group+1, respectively.
They use the relevant closure convention and maximal input degree, not an
assertion about actual F4/SAT work. See Salizzoni, Definitions 2.4-2.5 and
Propositions 3.10/3.13, https://arxiv.org/html/2304.13485 .

The S3 polynomial is standard; its algebraic-closure point interpretation is
given by Kosters-Yeo, Section 2 and Proposition 2.1,
https://arxiv.org/html/1503.08001 . Rational completeness below requires an
additional argument using t!=0. Binary-field first-fall conclusions from that
paper are not prime-field conclusions.

Square-root extraction and the shared-nonsquare certificate are standard
mechanisms, not claimed inventions: RFC 9380, Appendix I.1/I.4 and F.2.1.1,
https://www.rfc-editor.org/rfc/rfc9380.html#appendix-I and
https://www.rfc-editor.org/rfc/rfc9380.html#appendix-F.2.1.1 . The implementation
uses ordinary Tonelli-Shanks, not the RFC's constant-time implementation.

## 1. What the lower degree does to local monomial inventory

Before imposing S3, the local highest-part quotients have Hilbert series

    H_bit(T)=(1+T)^(2s),        H_group(T)=(1+3T)^s.

The first counts squarefree monomials on 2s bits. The second chooses either
no indicator or one of three indicators in each of s two-bit groups.
Consequently their cumulative normal-monomial capacities through degree d are

    C_bit(d)=sum_{j=0}^{min(d,2s)} binom(2s,j),
    C_group(d)=sum_{j=0}^{min(d,s)} binom(s,j)*3^j.

Both total dimensions equal 4^s. Evaluate at each presentation's own
preceding degree, regularity threshold, and mutant cap:

| Position | Bit cutoff | Group cutoff | Bit capacity compared with grouped 4^s |
|---|---:|---:|---|
| preceding | 3s/2 | s | strictly smaller for every even s>=2 |
| regularity | 3s/2+1 | s+1 | equal for s=2; strictly smaller for even s>=4 |
| mutant cap | 3s/2+2 | s+2 | equal for s=2,4; strictly smaller for even s>=6 |

Proof: the grouped inventory is saturated at d=s. Every binomial coefficient
through degree 2s in the bit inventory is positive, so it saturates exactly
when d>=2s. Solving each displayed inequality against 2s gives the stated
small-s boundaries. By symmetry of binom(2s,j), already the prefix through s
contains at least half of 4^s. Each displayed bit cutoff is >=s. Thus, at all
three paired positions,

    4^s/2 <= C_bit <= C_group = 4^s.

These particular inventories have the same exponential order in s. This
statement is a symbolic count, not a measured bound or solver lower bound.

Ordinary ambient monomials are a different quantity. With no local reduction,
the cumulative number through degree d in n variables is binom(n+d,d), by
stars and bars. Hence

    A_bit(d)=binom(2s+d,d),     A_group(d)=binom(3s+d,d).

At the three bit cutoffs they are binom(7s/2+k,3s/2+k), k=0,1,2; at the
three grouped cutoffs they are binom(4s+k,s+k). These are capacities of a
potential ambient monomial list, not the number a sparse or adaptive solver
must materialize. They must not be substituted for the local normal counts.

Four distinct objects matter: the local highest-part quotient counted here;
the full highest-part quotient after S3, whose homogeneous degree component
vanishes at the stated regularity; the affine solution quotient; and the
actual rows, columns and pivots processed by an algorithm. No identification
of these objects is asserted. In particular, the local-domain generators
plus a listed constant 1, or those generators with no extra equation, have
the same local inventory and very different solving obligations. This
control refutes any deduction of necessary solver work from local capacity
alone. Likewise two upper solving-degree bounds do not order actual solving
degrees. Nothing here closes grouped representations or SAT methods.

## 2. Complete rational two-summand enumeration

Here the assumptions weaken to any prime p>3, nonsingular
E:y^2=f(x)=x^3+a*x+b, finite R=(r,t) on E with t!=0, and ordered coordinate
domains D1,D2, each without duplicates. Domains may overlap. Points at
infinity are not domain elements. Bit labels with noninjective coordinate
maps require a separate multiplicity account and are not this API's output.

For every x in D1, find all roots y of y^2=f(x), at most two. For each
P=(x,y), compute Q=R-P, discard Q=infinity, and test x(Q) in D2. Retain one
witness P,Q for each distinct ordered projected pair (x(P),x(Q)).

Soundness follows from the construction. For completeness, any ordered
decomposition P+Q=R in the two domains has its x(P) visited and its y(P)
among the complete lift roots; then its unique complementary Q is checked.
Zero radicands give one lift, not two; P=R gives infinity and is excluded;
P=-R gives 2R, which is finite because t!=0. All other additions use the
usual chord or tangent rule. This includes zero-ordinate lifts and targets
of order three. Therefore the projected output size K satisfies

    K <= 2|D1| - 1_{r in D1} <= 2|D1|.

The subtraction uses the single invalid lift P=R whenever r is visited.
Filtering D2 and collapsing any duplicate projections can only lower K.

### Independent S3 completeness calculation

Write x for the first coordinate and z for the second, and set

    h=x-r,       c=-r*x-2r^2-a.

Starting with the standard short-Weierstrass S3,

    S3(x,z,r)=(x-z)^2*r^2
      -2*((x+z)*(x*z+a)+2b)*r+(x*z-a)^2-4b*(x+z),

substitute t^2=r^3+a*r+b and collect powers of z. The result is

    S3 = h^2*z^2 + (2h*c-4t^2)*z + c^2-4t^2*(x+r).

Its discriminant is

    (2h*c-4t^2)^2 -4h^2*(c^2-4t^2*(x+r))
       =16t^2*(t^2-h*c+h^2*(x+r))=16t^2*f(x).

The last equality follows by expansion using t^2=r^3+a*r+b. Since 16t^2
is a nonzero square, for h!=0 the polynomial has a rational root exactly
when f(x) is a square or zero. Given y^2=f(x), all second roots are

    z = (-(2h*c-4t^2) +/- 4t*y)/(2h^2).

For y=0 these coincide. For a point P=(x,y) with x!=r, the addition rule
also gives x(R-P)=(t+y)^2/h^2-r-x. The same identity reduces that expression
to (-h*c+2t^2+2t*y)/h^2, exactly one root above; the other sign uses -y.
Thus these rational roots have rational point witnesses, not just points
over the algebraic closure.

When h=0, the coefficient of z is -4t^2, nonzero. There is exactly one root

    z=(c^2-8t^2*r)/(4t^2)=(3r^2+a)^2/(4t^2)-2r=x(2R).

The first lift R yields infinity; -R yields the finite 2R. The linear
branch is essential. With t=0 the discriminant argument and this nonzero
linear coefficient fail, so such targets are rejected rather than covered
by a false extension.

## 3. Certificate and independent checker

`reference.solve(instance, mode="all")` returns one lift record for each
D1 coordinate in declared order, a global nonsquare Z, all distinct sorted
projected pairs and aligned rational witnesses. Each lift record is:

* zero: roots=[0] and f(x)=0;
* square: roots are exactly the two signs of a nonzero verified square root;
* nonsquare: a nonzero w with w^2=Z*f(x).

The checker certifies Z by Euler's criterion once. If f(x)!=0 and w!=0 with
w^2=Z*f(x), then f(x) is nonsquare, since division of a nonzero square by
a nonsquare is nonsquare in F_p. Producing w costs a square root of Z*f(x);
it is not free evidence. Omitting w!=0 would invalidate this reasoning.

`check_reference.verify` imports no producer helper. It checks exact D1
coverage, each root/sign or nonsquare certificate, then constructs all
second roots using the independent quadratic/linear formulas above and
compares the complete projected set after D2 membership. For every returned
witness it separately checks on-curve membership and the group sum. If
P=(x,y), Q=(u,v), use n=v-y,d=u-x for distinct abscissas; use
n=3x^2+a,d=2y for doubling. Inverse points and d=0 cannot sum to finite R.
For d!=0 the two division-free conditions are

    n^2=(r+x+u)*d^2,       n*(x-r)=(t+y)*d.

These are equivalent to the usual sum coordinates and avoid sharing the
producer's addition or square-root routines.

First mode returns at most one checked witness and always complete=false.
Its certificate covers a D1 prefix; a successful witness need not exhaust
that prefix's models. If it reports none, the checker requires the whole
D1 covered with no models, but still reports completeness_verified=false
under this output contract. All-mode output cost must not be compared with
first-witness cost without a separate, fixed question and protocol.

The input premise is **p prime**, not a probable-prime result. Neither API
supplies a primality proof. Successful validation is conditional on this
premise and explicitly returns primality_verified=false. Composite moduli
are outside the correctness theorem; rejection of some composites does not
certify accepted moduli. The checker does not authenticate event counts or
prove source execution history.

## 4. Full cost expression, including certificate production

Let B1=|D1|, B2=|D2|, S(p) the chosen nonzero square-root cost after nonsquare
setup, E(p) the Euler exponentiation cost, G(p) complete group-addition cost,
and M(D2) membership cost. Setup includes parsing/hashing the exact input,
coefficient normalization, domain construction/indexing and nonsquare search
and certification. A safe producer expression is

    T_setup + O(B1*(E(p)+S(p)+G(p)+M(D2)+1))
      + O(K log(K+1)) comparisons + output/certificate serialization.

There is at most one Euler test and one square-root extraction per nonzero
radicand, including nonsquare rows' twisted roots; at most two group
operations and two memberships per x. Zero radicands need neither Euler nor
square-root extraction. These are algorithmic counts, not measured CPU
times. Sorting projected output and exact input/certificate I/O are charged.

For p=3 mod4 the implementation verifies Z=-1 and uses exponent (p+1)/4
for square roots. For other primes it verifies a supplied Z or scans
2,3,... deterministically until an Euler-certified nonsquare is found,
then uses Tonelli-Shanks. Every actual probe is recorded in setup. A
deterministic scan has no expected-constant guarantee here: its actual
probe count, and in a crude worst case up to p-2 probes, belongs to setup.
No random sampling assumption is used. With a supplied valid Z, conventional
Euler exponentiation costs O(log p) field multiplications and Tonelli-Shanks
admits O((log p)^2) field multiplications. This is an arithmetic-operation
description; multiplication and inversion on log p-bit integers, Python
object overhead and bit comparisons are not unit-time CPU operations.

The checker pays one Euler exponentiation for Z, O(B1) root/certificate
arithmetic and at most one field inversion per rational-lift coordinate
to form all second roots, plus memberships, set construction, output
ordering, O(K) witness checks and input/certificate reading. It does not
repeat square-root extraction. If I(p) denotes field inversion cost, a safe
expression is

    T_check_setup + E(p) + O(B1*(I(p)+M(D2)+1))
      + O(K log(K+1)) comparisons + certificate/output reading.

The producer's additional twisted-root computation is therefore part of
the total even though checking each nonroot row uses only multiplications.
No claim of improved combined cost follows without matched measurement.

For modular interval windows, membership uses a modular subtraction and
integer comparison, with no B2-element index. For explicit lists, Python
sets cost O(B2) construction and storage under the usual expected hash
model; lookup is expected O(1), not a proven worst-case bound. Sorted
lists would instead charge sorting and O(log B2) comparisons per lookup.
D1 explicit input and duplicate checking similarly charge O(B1) storage.
Stored records and models give O(B1+B2+K) field-sized values overall, or
O((B1+B2+K) log p) value bits plus input length and representation overhead.
First mode may stop early; its actual prefix and retained output replace
full enumeration work, but setup and the weaker certificate scope remain.

Neither operational module scans all y in F_p or loops over D1 times D2.
The separate fixed tiny software-test oracle does both to check correctness.
That oracle is outside operational cost and is not a benchmark baseline.

## 5. What is now testable and what remains open

The certificate contract gives a complete reference for future identical
projected-set tests, with rational witness reconstruction and checker costs
explicit. A future grouped-versus-bit or SAT test must keep the domain,
output mode, projection multiplicity, exceptional cases, source, setup and
verification accounting fixed. Any comparative execution requires a new
frozen protocol and admission; none is performed here. The fixed software
results are recorded separately in unit-test-results.json.

This analysis neither establishes nor rules out an actual SAT/Gröbner gain.
The degree theorem still applies to its precise raw generator list; arbitrary
circuit lifting, membership additions, preprocessing or reduced substitution
do not inherit its exact degree without another proof. A two-summand
decomposition routine supplies no unknown scalar by itself. A general
prime-field ECDLP speedup still needs a scalar-compatible extraction method
and a matched end-to-end setup/query/memory/bit-cost advantage.
