# P1543 global-lift torsion-or-defect gate

## Status and claim boundary

- Record type: theorem-only producer gate
- Root hypothesis: `ECDLP-IDEA-005`
- Candidate: `P1543`
- Claim: `CLM-P1543-HEIGHT-COMPRESSING-GLOBAL-LIFT`
- Evidence scale: exact local lifting, reduction-kernel, counting, and cost
  statements plus a conditional Xedni control; no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `UNREVIEWED_SCOPED_LIFT_DICHOTOMY__PRIME_TO_P_GROUP_COMPATIBLE_LIFT_IS_TORSION_AND_HEIGHT_ZERO__NONTORSION_SET_SECTION_CARRIES_A_FORMAL_GROUP_DEFECT_SYNDROME__GLOBAL_RELATIONS_MUST_CANCEL_BOTH_FINITE_AND_LOCAL_OFFSETS__XEDNI_FIXED_ARITY_DENSITY_CONTROL_PRESERVED__STRUCTURED_DEFECT_COMPRESSION_UNSUPPLIED__OPEN`

IDEA-005 is operation-distinct from the pairing, S-unit, scalar-orbit, and same-field
transfer lanes only at one point: a public global point-lift rule must turn useful
finite-field relations into short, recoverable Mordell-Weil relations without importing
the scalar. Choosing another number-field model, coordinate representative, lattice
basis, or reduction backend is a control.

This receipt freezes the exact local obstruction that every global lift encounters. A
group-compatible lift of the prime-to-characteristic subgroup is the unique torsion lift;
it has zero canonical height and preserves the original relation problem verbatim. A
non-torsion set-theoretic section differs from that torsion lift by a point in the formal
reduction kernel. A global dependence must then satisfy both the original finite-group
syndrome and a second local defect syndrome. No current artifact compresses or decodes
that defect.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-005_height_compressing_global_lift_hypothesis.md`:
  `2dfa7872bc6c0eab05b062136a3c8b9f254ead2a7d5efd841663df34168ec713`
- `ledger/H-REP-001.yaml`:
  `55fa62651d57b3bd860c1e15ec60657ad5d502874d813f0d0e1288ff7ce6b483`
- `ledger/EV-REP-001.yaml`:
  `58b7418de68ece4710ac37968693d60c717fff73f5ae9ac9b4c10d25978920f1`
- `ledger/EV-REP-002.yaml`:
  `2ab05ae78dfb2159b12ec48f143274ece51e51d8fe974c4d57648e5984ec0b3c`
- `ledger/SYNTHESIS-20260716.md`:
  `d7c50575cd139dc11f5edae9045841717b200cd6e2c8b0611c8d210e2a5a1425`

The mutable finding ledger is a destination for this producer record and is not used as
a hash-bound mathematical input.

## Local prime-to-p torsion lift

Let `E/F_p` have a prime-order subgroup `G=<P>` of order `N!=p`. Let
`mathcal E/O_v` be a smooth proper elliptic model over a henselian discrete valuation
ring of characteristic zero with residue field `F_p`, fraction field `K_v`, and good
reduction `E`.

Because `N` is invertible in `O_v`, the finite group scheme `mathcal E[N]` is etale.
Hensel lifting gives a unique point above every rational special-fiber `N`-torsion point:

```text
t:G -> mathcal E(K_v)[N],
red(t(R))=R.
```

Uniqueness makes `t` a group homomorphism. In particular,

```text
t([a]P)=[a]t(P).
```

This is the strongest possible scalar-compatible local lift, but it is torsion. Its
Neron-Tate height is zero, every characteristic-zero logarithm kills it as torsion, and
its relation lattice is exactly the order-`N` source relation lattice. Computing a short
Mordell-Weil basis of the free part does not orient this torsion line.

If the lifted torsion point is required over a global number field `K`, its field of
definition, defining polynomial, local embedding, torsion basis, and representation are
charged. A canonical lift of the curve does not make that global torsion state free, and
it does not turn the torsion point into a positive-height Mordell-Weil coordinate.

This explains why ordinary canonical-lift geometry alone is not the IDEA-005 operation.

## Exact torsion-or-defect decomposition

Let a target-independent set section

```text
s:G -> mathcal E(K)
```

be defined over a global field `K` embedded in `K_v`, with `red(s(R))=R`. It need not
be a homomorphism. Compare it locally with the unique torsion lift:

```text
u(R)=s(R)-t(R) in E_1(K_v),
E_1(K_v)=ker(red:mathcal E(K_v)->E(F_p)).
```

For public factor-base points `F_i`, coefficients `e_i`, and target `R`, commutativity
and the homomorphism property of `t` give

```text
sum_i [e_i]s(F_i)-s(R)
 =t(sum_i [e_i]F_i-R)+sum_i [e_i]u(F_i)-u(R).
```

Reduction first yields the exact biconditional

```text
sum_i [e_i]s(F_i)=s(R)
iff
sum_i [e_i]F_i=R
and
sum_i [e_i]u(F_i)=u(R).
```

The second equality lives in the formal reduction kernel. After entering a convergent
formal-logarithm chart, it gives the necessary additive condition

```text
sum_i e_i*log_E(u(F_i))=log_E(u(R)).
```

Using the kernel group equality avoids any convergence convention; the logarithm is an
analysis and implementation tool, not an extra assumption.

The kernel is pro-`p` and contains no nontrivial `N`-torsion. Therefore any group
homomorphism `u:G->E_1(K_v)` is zero. A scalar-compatible section is forced back to
the torsion lift. Every genuinely non-torsion section has a nonlinear defect map `u` and
adds a second target-dependent syndrome.

This is not an impossibility theorem against using the defect. A mechanism-new lift could
make the public values `u(R)` lie in a compact structured family with a direct joint
decoder. IDEA-005 must state and cost that structure; shared denominator ideals without
such a decoder are representation evidence only.

## Relation-density consequence

For a finite target-independent coefficient family `C subset Z^B`, define the lifted
witness count

```text
M_R=|{e in C:
       sum_i [e_i]F_i=R and sum_i [e_i]u(F_i)=u(R)}|.
```

Dropping the defect condition can only increase this count. Each coefficient vector has
one finite-group syndrome, so for uniform `R in G`,

```text
Pr[M_R>=1] <= min(1,|C|/N).
```

For support at most `r` and coefficients in `[-H,H]`,

```text
|C|<=sum_(j=0)^r binom(B,j)*(2H)^j.
```

This is a witness-availability bound, not a decoder lower bound. A large structured
family may contain many witnesses, and an implicit joint solver could avoid enumerating
it. The current hypothesis gives no equations or cost for such a solver.

The same bound applies to known-scalar relation collection and blinded targets
`Q+[a]P` when the finite input is uniform. The defect condition may make the true
density lower; it cannot justify reporting a larger density from finite relations alone.

## Xedni fixed-arity control

Jacobson, Koblitz, Silverman, Stein, and Teske analyze the closest concrete global-lift
route. Under Lang's height conjecture and a discriminant-versus-lifted-height condition,
their fixed-arity lifted points, if dependent, have a relation with coefficients bounded
by an absolute constant. Random finite points have such a relation with probability
`O(1/p)=O(1/N)`, so the expected repetition cost is linear rather than square root.

The theorem is conditional and scoped to the stated Xedni construction and fixed number
of points. It does not cover a factor base growing as `N^beta`, a new correlated lift,
or a structured implicit defect decoder. It is nevertheless the mandatory negative
control. A toy short vector, smaller curve coefficients, or a different LLL backend does
not remove its mechanism.

## Height and bit-cost gate

Retain the IDEA-005 notation:

```text
B=N^beta,
global setup=N^c,
one relation trial=N^kappa,
reciprocal relation density=N^delta,
coefficient/log-height scale=N^h,
blind descent=N^tau,
stored state=N^s,
all number-field bit arithmetic=N^chi.
```

The complete exponents are

```text
lambda=max(c,beta+kappa+delta,2*beta,tau,chi),
mu=max(s,beta).
```

The following are charged explicitly inside these terms:

- global curve and field degree, discriminant, integral model, and local embedding;
- torsion-lift or non-torsion-section construction for every used point;
- denominator ideals, units, class groups, saturation, regulators, and precision;
- the complete defect values or a proved compressed representation;
- all failed lift/lattice trials and both relation and blinded-target densities;
- coefficient bit lengths and operation counts rather than a symbolic height label; and
- independent finite-field rank, factor-log solve, exact source output, and verification.

A relation of height below `N^(1/2)` is not sufficient. The relation family must occur
at adequate density, cancel the defect, span the factor-base logarithms, and support a
blind target descent. No current construction supplies `lambda,mu<=0.45`.

## Controls and falsifiers

### Required positive controls

- The unique local torsion lift must preserve every order-`N` relation exactly, while
  exposing zero canonical height and no free Mordell-Weil orientation.
- A planted characteristic-zero curve with known non-torsion relations must be recovered
  and reduce correctly.
- Exhaustive tiny instances must replay both the finite syndrome and the local defect
  equality for every accepted relation.

### Required negative controls

- The published Xedni lift and arbitrary integer-coordinate lifts.
- Random lattices matched in dimension, determinant, coefficient size, and precision.
- A supplied scalar-labeled torsion basis or target-dependent lift, which receives no
  mechanism credit.
- EDS, p-adic logarithm, canonical-lift, and Mordell-Weil-sieve representations that do
  not remove the torsion-or-defect dichotomy.

### Immediate falsifiers for the current formulation

- The lift is called scalar-compatible but is non-torsion without publishing its defect.
- The canonical torsion lift is inserted into a free Mordell-Weil lattice or assigned
  nonzero height.
- A relation is accepted after finite reduction without checking the complete global and
  local equality.
- Favorable lifts, curves, or short vectors are selected after seeing the target.
- Number-field degree, discriminant, saturation, precision, failed trials, or blind
  descent is omitted from `chi`, `delta`, or `tau`.
- A toy dependence, correct reduced relation, height slope, or lattice speedup is called
  scalar recovery, a Shoup-bound improvement, or a breakthrough.

## Literature boundary

1. Michael J. Jacobson, Neal Koblitz, Joseph H. Silverman, Andreas Stein, and Edlyn
   Teske, *Analysis of the Xedni Calculus Attack*,
   <https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf>. This is the conditional
   fixed-arity coefficient and density control.
2. James Borger and Lance Gurney, *Canonical lifts of families of elliptic curves*,
   <https://arxiv.org/abs/1608.05912>. This supplies canonical curve-lift geometry, not
   a positive-height scalar-compatible point section.
3. Kristin Lauter and Katherine Stange, *The elliptic curve discrete logarithm problem
   and equivalent hard problems for elliptic divisibility sequences*,
   <https://arxiv.org/abs/0803.0728>. This blocks a change from global point lifts to
   EDS association without a new operation.
4. Joseph H. Silverman, *The Arithmetic of Elliptic Curves*,
   <https://doi.org/10.1007/978-0-387-09494-6>. This supplies good reduction, formal
   groups, torsion reduction, and canonical-height background.
5. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>. This controls any route that reduces to
   the original group oracle; it does not classify a future coordinate-aware defect
   decoder.

No source or audited artifact supplies the required public non-torsion section with a
compressed joint finite-and-defect decoder and complete sub-rho factor-base-to-target
cost. Novelty of such a future operation remains unverified.

## Producer decision

The IDEA-005 instruction to implement a 12--24-bit lift comparison is premature. Without
a specified non-torsion section and defect-compression theorem, the experiment would
compare Xedni-style coordinate choices and lattice backends. A planted global relation
would test plumbing; the unique torsion lift would preserve the original DLP without
height information.

P1543 is queued for one independent theorem audit. No Sage implementation, number-field
catalog, lattice sweep, global-point table, relation campaign, factor-log solve, or blind
descent should be built until review either specifies one structured defect decoder with
complete costs or returns the candidate terminal inconclusive.

## Exactly one next action

Independently reconstruct the finite-etale torsion lift, torsion-or-defect biconditional,
pro-`p` homomorphism gate, coefficient-family density bound, Xedni scope, and complete
bit-cost model; then either specify one target-independent non-torsion section whose
formal-kernel defects admit a direct joint decoder with `lambda,mu<=0.45`, or return
P1543 terminal inconclusive. Do not draft or execute an IDEA-005 contract during review.
