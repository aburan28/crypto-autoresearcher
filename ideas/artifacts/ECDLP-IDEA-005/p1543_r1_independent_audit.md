# P1543 R1 independent global-lift audit

## Status and claim boundary

- Record type: independent theorem-only audit
- Root hypothesis: `ECDLP-IDEA-005`
- Candidate: `P1543`
- Claim: `CLM-P1543-HEIGHT-COMPRESSING-GLOBAL-LIFT`
- Evidence scale: exact good-reduction, formal-group, Mordell-Weil-coordinate,
  counting, and conditional Xedni statements; no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__FINITE_ETALE_SECTION_IS_TORSION_AND_GLOBAL_HEIGHT_ZERO__CANONICAL_TEICHMULLER_LIFT_IS_THE_SAME_GROUP_SECTION__NONTORSION_SECTION_HAS_EXACT_FORMAL_DEFECT_SYNDROME__PRIME_TO_P_MULTIPLICATION_DOES_NOT_SUPPRESS_FIRST_JET_DEFECT__FIXED_COEFFICIENT_AND_XEDNI_DENSITY_GATES_RECONSTRUCTED__MORDELL_WEIL_COORDINATES_REQUIRE_THE_ORIGINAL_PREIMAGE__STRUCTURED_DEFECT_DECODER_UNCLASSIFIED__INCONCLUSIVE`

The producer's torsion-or-defect theorem reconstructs. Independent review adds two
useful normal forms. First, multiplication by the prime-to-`p` subgroup order is an
automorphism on the first formal-group quotient, so the arbitrary-lift error suppressed
by the anomalous `N=p` attack survives on the generic `N!=p` lane. Second, expressing
a non-torsion lift in a known Mordell-Weil basis makes the requested section exactly a
preimage/decomposition algorithm for the original reduced group.

Canonical curve and point lifting, coordinate Hensel sections, denominator ideals,
elliptic divisibility sequences, local or global heights, and Mordell-Weil sieves do not
supply the missing joint decoder. This is a terminal scoped inconclusive disposition,
not a lower bound against every target-independent nonlinear point section whose formal
defects have a new compact relation and descent algorithm.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-005_height_compressing_global_lift_hypothesis.md`:
  `2dfa7872bc6c0eab05b062136a3c8b9f254ead2a7d5efd841663df34168ec713`
- `ideas/artifacts/ECDLP-IDEA-005/p1543_global_lift_torsion_defect_gate.md`:
  `37288382aeabdf4ce43ae95a32f0c86e59dd9200dfbeb80654a89f765f4c1631`
- `ideas/rejected/ECDLP-IDEA-109_serre_tate_torsion_section_jet_coordinate_hypothesis.md`:
  `d3982502bb0373037086be8e00cc2563d92f5125dc90e100bb295cc0cecdd606`
- `ideas/rejected/ECDLP-IDEA-129_cross_characteristic_lubin_tate_linearizer_hypothesis.md`:
  `713b48bb0b8b6da486a518111d8700a13cb5505ecea92f6423f31ca52acc1b6b`
- `ideas/rejected/ECDLP-IDEA-263_arithmetic_differential_character_scalar_digits_hypothesis.md`:
  `4697d7694899774ca7ce7199bb3836209e3ae292734e0fee0df1ca163dd4fdc2`
- `ideas/rejected/ECDLP-IDEA-269_mordell_weil_sieve_target_return_hypothesis.md`:
  `d98151c88aa82a3044b551958366d5bd71eaf0bc88d2e02a805ac9908e734baa`

## Finite-etale torsion section

Let `O_v` be a henselian discrete valuation ring of characteristic zero, with residue
field `F_p`, fraction field `K_v`, and a smooth proper elliptic model `mathcal E/O_v`.
Let

```text
G=<P> subset E(F_p)[N],
N prime,
N!=p.
```

Because `N` is invertible in `O_v`, `mathcal E[N]` is finite etale. Henselian
invariance of finite-etale sections gives a unique lift of every point in `G`:

```text
t:G -> mathcal E(O_v)[N],
red(t(R))=R.
```

Uniqueness and compatibility of addition with reduction imply

```text
t(R+S)=t(R)+t(S),
t([a]P)=[a]t(P).
```

Thus the strongest scalar-compatible local section is an isomorphic copy of the same
finite order-`N` group. If this point is realized over a global number field, it remains
torsion and has global Neron-Tate height zero. A local point alone has no global canonical
height until such a globalization is specified; this corrects that minor category shortcut
in informal statements of the producer gate.

On the canonical ordinary lift over Witt vectors, the elliptic Teichmuller lift is an
injective group section of reduction. By the uniqueness above, its restriction to `G` is
exactly `t`. Explicit coordinate polynomials or a fast point-lifting algorithm therefore
compute a new representation of the same torsion problem, not a positive-height
Mordell-Weil coordinate.

## Exact defect biconditional

Let a target-independent set section into a fixed global curve be

```text
s:G -> mathcal E(K),
red(s(R))=R,
K embedded in K_v.
```

It need not preserve addition. Define its local defect relative to the torsion section by

```text
u(R)=s(R)-t(R) in E_1(K_v),
E_1(K_v)=ker(red).
```

For factor points `F_i`, integers `e_i`, and target `R`,

```text
sum_i [e_i]s(F_i)-s(R)
 = t(sum_i [e_i]F_i-R)
   + sum_i [e_i]u(F_i)-u(R).
```

Reduction followed by the uniqueness of the torsion lift gives the exact biconditional

```text
sum_i [e_i]s(F_i)=s(R)
iff
sum_i [e_i]F_i=R
and
sum_i [e_i]u(F_i)=u(R).
```

The reduction kernel is a pro-`p` group. It has no nontrivial `N`-torsion, so every
homomorphism `G -> E_1(K_v)` is zero. Consequently a group-compatible section has
`u=0` and is the torsion section. Every non-torsion section is nonlinear and adds the
second target-dependent syndrome displayed above.

This is a classification of sections, not an impossibility theorem against exploiting a
nonlinear defect.

## Formal-log and first-jet normal forms

For any set section `s`, multiplication by `N` removes the torsion component:

```text
[N]s(R)=[N]u(R) in E_1(K_v).
```

Where the formal logarithm converges,

```text
log_E(u(R))=N^(-1)*log_E([N]s(R)).
```

Thus the defect can be evaluated from a supplied non-torsion lift without first locating
the torsion point. This does not make it scalar compatible. It merely gives an additive
coordinate for the second syndrome. In ramified fields the logarithm may have a
`p`-power torsion kernel, so exact acceptance must replay the group equality, not only
the logarithmic equality.

The formal filtration gives the sharper distinction from anomalous-curve attacks. For a
local parameter and `E_m={R:v(parameter(R))>=m}`,

```text
E_1/E_2 is isomorphic to F_p^+,
[a] acts on E_1/E_2 as multiplication by a mod p.
```

Hence:

```text
N!=p  => [N] is an automorphism on E_1/E_2,
N=p   => [p] kills E_1/E_2.
```

The Smart/Satoh-Araki first-jet effect on anomalous curves works because multiplication
by the group order pushes arbitrary lift error one level deeper. On the generic
prime-to-`p` subgroup, multiplication by `N` preserves that first-order error. A
coordinate-wise Hensel lift, noncanonical curve lift, arithmetic jet, or delta-character
therefore faces the same choice: use the torsion section and get zero additive data, or
retain a nonlinear defect that does not obey the hidden scalar law.

Voloch's descent formulation agrees with this split. Its Witt-vector map handles the
`p`-primary part of `E(F_q)`; its prime-to-`p` part is the usual multiplicative
MOV/Frey-Ruck descent. It does not provide a Witt additive coordinate on `G`.

## Fixed-family density reconstruction

Freeze factor points `F_1,...,F_B` and a finite target-independent coefficient family
`C subset Z^B`. For each `e in C`, the finite syndrome

```text
sigma(e)=sum_i [e_i]F_i
```

is one point of `G`. Therefore, for uniform `R in G`, a union bound gives

```text
Pr[there exists e in C with sigma(e)=R]
 <= min(1,|C|/N).
```

Requiring the defect equality only removes witnesses, so the same upper bound holds for
global lifted relations. If support is at most `r` and nonzero coefficients lie in
`[-H,H]`,

```text
|C| <= sum_(j=0)^r binom(B,j)*(2H)^j.
```

This is not a decoder lower bound. A large implicit family may have sufficient witness
mass, and a new structured algorithm could search it without enumeration.

## Exact Xedni scope

Jacobson, Koblitz, Silverman, Stein, and Teske analyze fixed arity `2<=r<=9`. Their
Theorem 4.1 assumes Lang's lower height conjecture and the additional comparison

```text
log|D| >= C_1*max_i h_hat(P_i)
```

for the lifted curves. Under those assumptions, dependence forces a relation whose
coefficients are bounded by a constant independent of `p`. Reducing that relation gives
a constant-size coefficient relation among random points of `E(F_p)`. The paper derives
a success probability below `C_0/p`, so expected trials are linear in `p` in that model.

The theorem is conditional, fixed-arity, and tied to the stated discriminant-height
comparison. It does not cover a growing factor base, a correlated section that violates
that comparison, or a new implicit coefficient family. The producer preserves these
limits correctly.

## Mordell-Weil coordinate gate

Suppose the image of `s` lies in a known finitely generated subgroup

```text
Gamma = T direct_sum <M_1,...,M_r> subset E(K).
```

Write

```text
s(R)=tau(R)+sum_(j=1)^r c_j(R)M_j.
```

Reduction gives

```text
R=red(tau(R))+sum_j c_j(R)*red(M_j).
```

Computing the Mordell-Weil coordinate vector `c(R)` is therefore already a public
multi-generator preimage/decomposition algorithm for the reduced target. If the section
were a homomorphism, its finite image would lie in `T` and all free coordinates would
vanish. If it is not a homomorphism, its coordinate map is another expression of the
nonlinear defect.

Exact global dependencies among lifted factor points are integer dependencies among
their Mordell-Weil coordinate columns plus a torsion check. They can eliminate redundant
columns, but the remaining free coordinates of a fresh target still have to be found.
The positive-definite height pairing can rank candidate coordinate vectors after they are
specified; it does not construct `c(R)`. LLL, BKZ, saturation, a new basis, or a
Mordell-Weil sieve changes the backend for this preimage unless it supplies a new
target-independent section and decoder.

This gate is exact at the operation level and does not assert a generic lower bound for
all structured lattice preimage problems.

## Named route screen

### Canonical and coordinate lifts

- The canonical ordinary curve plus elliptic Teichmuller point lift is the torsion section.
- A coordinate-wise or noncanonical Hensel section can be public and cheap locally, but
  its first-jet defect survives multiplication by `N` and must satisfy the second syndrome.
- Truncating a local lift to finite `p`-adic precision gives congruence evidence, not an
  exact global Mordell-Weil relation.
- Globalizing exact coordinate lifts requires the number field, common curve, embeddings,
  denominators, and point construction to be published and charged. No audited theorem
  keeps those data below the cap while providing the joint decoder.

### Denominators, heights, and elliptic sequences

Denominator ideals and local or global heights are attached to already supplied global
points. Their factorization may score or reject a proposed relation, but no artifact maps a
fresh finite point to a useful global point and exact source tuple. Lauter and Stange show
that the EDS Association, EDS Residue, and width-three EDS index problems are
subexponentially equivalent to ECDLP in their stated models. Replacing the missing
section by an elliptic divisibility sequence is therefore not a free operation.

### Global sieves and auxiliary reductions

A Mordell-Weil sieve begins with a global curve, a known finite-index subgroup or basis,
and computable local images. Applied after `c(R)` is known it can remove candidates;
asked to produce `c(R)`, it is the preimage problem above. Auxiliary reductions do not
repair the absent scalar-compatible positive-height section, and their cumulative
modulus, residue state, saturation, and ambiguity must be charged.

### Arithmetic characters

Every additive characteristic-zero logarithm, formal character, or delta-character kills
the prime-to-`p` torsion section. Evaluating it on a non-torsion section measures `u(R)`
but does not imply `value([a]P)=a*value(P)`. Nonadditive ramification and oriented-branch
data are a distinct mechanism and remain outside this audit.

## Complete cost receipt

Use the root model

```text
lambda=max(c,beta+kappa+delta,2*beta,tau,chi),
mu=max(s,beta).
```

The canonical torsion route has no height-compression decoder: it preserves the original
order-`N` relation and descent problem. The non-torsion routes supply no joint
finite-and-defect witness density, independent relation rank, factor-log completion,
blind target section, field degree, discriminant, saturation, precision, failed-trial,
bit-time, or peak-memory receipt. No values `lambda,mu<=0.45` are established.

The root's proposed coordinate-lift experiment would measure backend-dependent height
slopes before defining the missing section and decoder. It remains premature and is not
authorized by this audit.

## Independent findings

1. The finite-etale torsion lift and exact defect biconditional reconstruct.
2. Global height language applies only after a global realization; any such realization
   of the compatible section remains torsion and height zero.
3. The canonical elliptic Teichmuller lift is the same torsion section, not an exception.
4. Prime-to-`p` multiplication preserves first formal-jet defect noise, while the
   anomalous `N=p` control suppresses it.
5. The coefficient-family density bound and the conditional fixed-arity Xedni `C_0/p`
   boundary reconstruct with their exact scopes.
6. Known Mordell-Weil coordinates turn section construction into the original reduced
   preimage problem; heights and sieves do not produce those coordinates.
7. No named canonical, coordinate, denominator, height, EDS, character, or sieve route
   supplies a structured nonlinear defect decoder and complete sub-rho path.
8. An arbitrary target-independent non-torsion section with a mechanism-new compact
   defect equation remains unclassified.

## Disposition and next action

P1543 is terminal inconclusive within the audited section, first-jet, fixed-family,
fixed-arity, Mordell-Weil-coordinate, and named arithmetic routes. Preserve the producer
and this independent receipt. Do not draft or execute an IDEA-005 contract and do not
run the proposed coordinate-lift benchmark.

The next mechanism-distinct theorem lane is IDEA-160's nonadditive ramification data:
independently audit whether any publicly canonical oriented branch can evade the
generator-invariance theorem and return a typed scalar digit without an orientation table.
That lane is not repaired or prejudged by the additive defect result here.

## Primary references

1. Michael J. Jacobson, Neal Koblitz, Joseph H. Silverman, Andreas Stein, and Edlyn
   Teske, *Analysis of the Xedni Calculus Attack*,
   <https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf>.
2. Jose Felipe Voloch, *The discrete logarithm problem on elliptic curves and descents*,
   <https://web.ma.utexas.edu/users/voloch/Preprints/disclog3.pdf>.
3. James Borger and Lance Gurney, *Canonical lifts of families of elliptic curves*,
   <https://arxiv.org/abs/1608.05912>.
4. Liam Bitting and Luis R. A. Finotti, *Canonical Liftings of Edwards Curves*,
   <https://web.math.utk.edu/~lfinotti/papers/liam1.pdf>.
5. Kristin E. Lauter and Katherine E. Stange, *The elliptic curve discrete logarithm
   problem and equivalent hard problems for elliptic divisibility sequences*,
   <https://arxiv.org/abs/0803.0728>.
6. Joseph H. Silverman, *The Arithmetic of Elliptic Curves*, second edition, Springer,
   2009, Chapters VII and VIII.

These sources establish the cited lift, descent, formal-group, Xedni, and EDS controls.
None supplies the missing structured nonlinear defect decoder or a generic-prime
sub-rho ECDLP algorithm.
