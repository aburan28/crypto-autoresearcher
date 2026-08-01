# P1547 prime-to-p jet-coordinate theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-004`
- Candidate: `P1547`
- Claim: `CLM-P1547-PRIME-TO-P-JET-COORDINATE`
- Evidence scale: exact local-Artin filtration, finite-etale torsion,
  prime-to-`p` module, formal-defect, and first-jet statements; named arithmetic
  differential and cohomological route screen; no experiment
- Contract state: no IDEA-004 contract was drafted, approved, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__FINITE_NILPOTENT_JET_KERNEL_HAS_P_PRIMARY_FILTRATION__MULTIPLICATION_BY_ELL_IS_INVERTIBLE_ON_NATIVE_JET_FORMAL_AND_P_TYPICAL_TARGETS__EVERY_ADDITIVE_ORDER_ELL_IMAGE_IN_THOSE_TARGETS_IS_ZERO__PRIME_TO_P_TORSION_LIFTS_UNIQUELY_FINITE_ETALE__CANONICAL_TORSION_LIFT_HAS_ZERO_FORMAL_DEFECT__NON_TORSION_SECTIONS_STORE_ONLY_P_PRIMARY_LIFT_ERROR__FREE_FIRST_JET_CONSISTENCY_IS_ZEROTH_ORDER_TANGENT_DATA__HIGHER_FINITE_ADDITIVE_JETS_DO_NOT_ESCAPE__ADJOINED_ELL_TORSION_REIMPORTS_BASIS_OR_ORIENTATION__ETALE_COHOMOLOGY_AND_PAIRING_ROUTES_MOVE_THE_DLP_OR_REQUIRE_NON_GENERIC_EMBEDDING_COST__NONADDITIVE_TYPED_SCALAR_INVARIANT_UNCLASSIFIED__INCONCLUSIVE`

Every native finite-order deformation kernel of a smooth elliptic curve has a
filtration by additive residue-field tangent modules. For a subgroup order
`ell!=p`, multiplication by `ell` is an automorphism on every layer and hence
on the whole kernel. The same conclusion holds for formal `p`-adic, truncated
Witt, p-complete p-typical, crystalline, and additive arithmetic-differential
targets: they need not all be p-primary torsion, but `ell` is a unit.

Therefore any functional satisfying the IDEA-004 scalar law

```text
J([n]R)=[n]J(R)
```

is zero when its target is one of those native additive modules. Nonlinear
formulas do not escape because the scalar law itself makes the restriction to
`<P>` a homomorphism. Prime-to-`p` torsion does lift uniquely through the
thickening, but it lifts as the same finite-etale cyclic group. Giving that
group an explicit `Z/ell` coordinate requires the missing torsion basis or
orientation; it is not supplied by its zero formal jet.

An arbitrary nonadditive point invariant with a typed scalar inverse remains
outside this theorem. IDEA-004 names no such invariant and gives no complete
cost. Its proposed order-one experiment cannot promote the stated additive
fingerprint and is not executed.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-004_prime_to_p_jet_logarithm_hypothesis.md`:
  `e18a697e37a98855e475f9415ea076eac164eccfe060ec87b0c4f6acac6e76dc`
- `ideas/rejected/ECDLP-IDEA-140_de_rham_witt_torsion_residue_hypothesis.md`:
  `9616d6f2deee662ca6376a7e26b966be526acb4bf2929daa37182f26c4d4e13b`
- `ideas/artifacts/ECDLP-IDEA-005/p1543_r1_independent_audit.md`:
  `d7654a1286a42e67cd0aa9b73020c04389a7072c08762ebd09ef66c0eeeefeba`
- `ledger/H-JET-001.yaml`:
  `6b7440e4ceb6760d62813c6fb9054cec8f08a91b50a68f3b474b007ae83571ee`
- `ledger/EV-JET-001.yaml`:
  `1abfdcb0631cad1cdc7f0970b9e84cada7c47c1b6a96a22635cf975848de2984`
- `ledger/H-JETB-001.yaml`:
  `840e13ca276dba167d2adea86134b5af0e6cb59f664792c2ee2f04fb7a4003ef`
- `ledger/EV-JETB-001.yaml`:
  `a8887d69dea9a664d7399f5e62448267d8cebc2720a5783dfc60924994fbde2a`
- `ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md`:
  `f64cc45b05cc74364d87eec69f54ecda79100274c0b498103a6492fa61c62702`

IDEA-140 is preserved rejected evidence. P1543 is an independent predecessor
audit. JET and JETB are toy controls and are not promoted to a crypto-scale
theorem by this receipt.

## Frozen interface

Let

```text
E/F_p be ordinary,
H=<P> subset E(F_p),
ord(P)=ell prime,
ell!=p,
ell=p^(1+o(1)),
Q=[x]P.
```

Let `A` be either:

1. a finite local Artin `F_p`-algebra with residue field `F_p` and nilpotent
   maximal ideal `I`;
2. a truncated mixed-characteristic lift such as `W_h(F_p)`; or
3. a compatible p-adic inverse system of such lifts.

Write

```text
rho:E(A)->E(F_p)
```

for reduction and

```text
K_A=ker(rho).
```

The requested output is an explicitly represented additive module `M` and a
public evaluator

```text
J:H->M,
J([n]R)=[n]J(R),
J(P)!=0,
```

with a canonical basis and a direct typed inverse from `J(Q)` and `J(P)` to
`x mod ell`. A lift, cohomology class, residue, or abstract cyclic target is not
enough.

## Finite-order jet-kernel filtration

Because `E` is smooth, reduction through a nilpotent thickening is locally
surjective. Filter the reduction kernel by powers of the nilpotent ideal:

```text
K_A=K^1 superset K^2 superset ... superset K^h={O}.
```

The successive quotients are tangent modules of the form

```text
K^r/K^(r+1) isomorphic to Lie(E/F_p) tensor I^r/I^(r+1).
```

Each quotient is an additive `F_p`-vector space. Since `ell!=p`, multiplication
by `ell` is invertible on each quotient. Induction over the finite filtration
gives:

```text
[ell]:K_A->K_A is an automorphism.
```

This statement covers dual numbers, all finite nilpotent orders, constrained
coordinate charts after their additive target is identified, and finite
Greenberg or arithmetic-jet kernels. It is not restricted to first order.

For `W_h(F_p)`, the kernel has a finite filtration by p-power layers, so the
same argument applies. In the p-adic inverse limit, the additive target may be
torsion-free rather than p-primary torsion; nevertheless `ell` is a p-adic unit,
and multiplication by `ell` remains an automorphism. This corrects the common
but unnecessary claim that every p-complete target is p-primary torsion.

## Prime-to-p additive vanishing theorem

Let `M` be any additive group or module on which multiplication by `ell` is an
automorphism. If

```text
J:H->M
```

is a homomorphism, then

```text
O=J([ell]P)=[ell]J(P).
```

Applying `[ell]^(-1)` gives `J(P)=O`, and hence `J` is zero on all of `H`.

IDEA-004 asks for `J([n]R)=[n]J(R)` for every source scalar. That law makes
`J|H` a homomorphism even if its coordinate formula is nonlinear, branching,
defined by a Frobenius cocycle, or assembled from several jet levels. Thus no
native additive finite-order, formal, Witt, p-typical, crystalline, or p-adic
differential target can satisfy the requested nonzero scalar law.

This reconstructs and broadens IDEA-140's exact p-typical boundary while
preserving its scope: a nonadditive invariant or a target on which `[ell]` is
not invertible is not rejected by this theorem.

## Unique prime-to-p torsion lift

Multiplication by `ell` on an elliptic curve in characteristic `p` is finite
etale because `ell` is invertible in the base field. Equivalently, `E[ell]` is
a finite-etale group scheme. Finite-etale objects lift uniquely over nilpotent
thickenings.

The same fact follows directly from the kernel automorphism. Given any lift
`R_tilde` of `R in E(F_p)[ell]`, its error

```text
[ell]R_tilde in K_A
```

has a unique preimage `U in K_A` under `[ell]`; then

```text
s(R)=R_tilde-U
```

is the unique `ell`-torsion lift. The map

```text
s:E(F_p)[ell]->E(A)[ell]
```

is a group isomorphism inverse to reduction.

This canonical torsion lift has no independent formal-jet coordinate. Relative
to the torsion section, its kernel defect is zero. The lift preserves the
unknown relation exactly:

```text
s(Q)=[x]s(P).
```

Computing `x` from that equality is the same DLP in another finite-etale
encoding unless an additional coordinate is supplied.

## Non-torsion section defect

For an arbitrary public set section `t:E(F_p)->E(A)`, define

```text
epsilon_t(R)=t(R)-s(R) in K_A.
```

Then

```text
t(Q)-[x]t(P)=epsilon_t(Q)-[x]epsilon_t(P).
```

The right side is p-primary or p-adic lift error, not an `ell`-primary scalar
channel. If `epsilon_t` were additive on `H`, the vanishing theorem would make
it zero. If it is not additive, a lifted relation must satisfy an additional
defect equation; this is the exact P1543 torsion-versus-defect normal form.

Choosing a section whose defects encode `x` is allowed only after its public
construction and typed inverse are shown. A target-selected or known-log lift
merely writes the answer into the section.

## Free first-jet and higher-jet screen

For a polynomial relation `S(z)=0`, substituting

```text
z+eps*v
```

with `eps^2=0` gives

```text
S(z)+eps*(grad S(z).v).
```

At a true zeroth-order point, the free first-order solutions are precisely the
Zariski tangent space. Existence of a free tangent lift therefore does not
filter a true relation or create source labels. The JETB evidence reproduces
this exactly on its toy Semaev fixtures; JET measures the corresponding screen
as overhead.

At higher finite order, the zero correction is always a lift along the
canonical torsion section, while every alternative section contributes the
successive p-primary defect layers above. The additive vanishing theorem applies
to the full finite filtration, not only its first tangent quotient.

A constrained nonlinear jet may define a nonadditive set map. It remains open
only if the constraint is public, target uniform, lift invariant, and comes
with a typed scalar law and inverse. IDEA-004 supplies no such constraint. A
constraint chosen after observing a favorable lift is a branch oracle, not a
jet coordinate.

## Canonical lift and Frobenius screen

The Serre-Tate/Borger-Gurney canonical lift is a canonical lift of the curve and
its ordinary Frobenius structure. Its construction can preserve prime-to-`p`
level structure because that structure is finite etale. This does not choose a
scalar coordinate inside one cyclic line.

On rational source points, Frobenius acts as the identity modulo `p`. A public
polynomial in Frobenius therefore acts by a known scalar on the rational line,
plus at most a native p-adic defect after a noncanonical lift. An additive
Frobenius-cocycle value in a native jet module vanishes on `H` by the theorem
above. Inverting `F-1` changes the task to selecting a torsor branch, with the
orientation boundary already audited in P1544.

Canonical curve data such as lifted coefficients, `j`, Serre-Tate parameter,
or Frobenius matrix are common to `P` and `Q`. They cannot reveal a scalar that
distinguishes two generators without a marked-point operation.

## Arithmetic differential-character screen

Arithmetic `delta`-characters can be nonzero additive maps

```text
psi:E(R)->R^+
```

on p-adic points. This is a meaningful operation on the infinite p-adic group,
not a generic-prime ECDLP coordinate. Since `ell` is a unit on the additive
p-adic target, restriction to the finite subgroup `H` gives

```text
psi(P)=0,
psi(Q)=0.
```

Partial arithmetic PDE characters and higher arithmetic jet order do not
change this finite-order restriction while their output remains additive in a
p-adic module. A nonadditive arithmetic differential invariant remains outside
scope and needs a scalar inverse rather than a nonzero value alone.

## Adjoined ell-primary target screen

To evade invertibility, a target `M` must contain actual `ell`-torsion. The
natural candidates are:

1. `E[ell]` or its lifted etale copy;
2. an etale cohomology or Tate-module line modulo `ell`;
3. a roots-of-unity target reached by a pairing; or
4. an abstract copy of `Z/ell`.

The first two preserve the source line but do not orient it. Choosing `s(P)` as
a basis makes `s(Q)=[x]s(P)` the original DLP. Choosing a different etale basis
requires expressing `P` and `Q` in that basis, again the missing torsion-module
coordinate.

The fourth candidate simply declares the desired answer map. A public evaluator
from curve points to that copy of `Z/ell` is exactly an ECDLP solver.

A pairing can orient the source line against a second independent torsion point
and move the scalar to `mu_ell`, but then extension degree, construction of the
second torsion direction, pairing evaluation, and the finite-field DLP must all
be charged. For generic prime-field curves with `ell` asymptotic to `p`, a small
embedding-degree route is not generic evidence. This is the P1542 pairing-lift
control, not a finite jet escape.

## Miller, residue, and cohomology screen

A p-typical `dlog`, residue, Cartier, Frobenius, or ghost coordinate with an
additive scalar law lands in a target on which `ell` is invertible and hence
vanishes on `H`. If a Miller or division function is built from a supplied
source divisor, its nonzero residues may verify that divisor but do not discover
it. Normalizing a function by a target-dependent branch can encode the missing
source.

Using coefficients modulo `ell` in etale cohomology creates an ell-primary
target, but it does not construct a canonical scalar basis for the rational
torsion line. A Kummer class, cocycle, or cohomological representative is an
encoding until a public point-to-coordinate evaluator and inverse are supplied.
Changing cohomology theories does not by itself change that operation.

## Anomalous control

The Semaev, Satoh-Araki, and Smart attacks apply when the relevant subgroup is
p-primary, notably `#E(F_p)=p`. Then multiplication by the subgroup order is not
invertible on the formal kernel, and a nonzero first formal quotient can carry
the scalar. This is exactly why the anomalous control works.

For `ell!=p`, `[ell]` is invertible on the same formal target and the channel
vanishes. Reproducing an anomalous attack validates implementation plumbing only;
it gives no interpolation or scaling evidence for the generic prime-to-`p`
family.

## Complete cost receipt

Use the frozen direct-recovery model

```text
lambda=max(c,kappa,e+delta+o+u,v),
mu=max(s,kappa,o,u).
```

Native additive finite-order, formal, Witt, p-complete, crystalline, and
arithmetic-differential targets have no nonzero candidate regardless of cost.
The finite-etale torsion lift is efficiently computable but returns the original
DLP encoding. A complete ell-torsion orientation table has state exponent one;
generic source or target DLP has time exponent at least one half. Pairing routes
must charge their non-generic extension and finite-field costs.

No explicit nonadditive scalar invariant remains to receive favorable
parameters. IDEA-004 supplies no construction exponent `c`, target/precision
exponent `kappa`, evaluation `e`, usable density `delta`, output `o`, ambiguity
`u`, inversion `v`, or state `s` for such an operation. Missing parameters are
not assigned optimistic zeros.

## Independent findings

1. Every finite nilpotent jet kernel has a filtration by additive
   characteristic-`p` tangent modules.
2. Multiplication by `ell!=p` is invertible on finite jet, formal, truncated
   Witt, p-complete p-typical, crystalline, and additive p-adic targets.
3. Every additive map from the order-`ell` subgroup to one of those targets is
   zero; a nonlinear formula with the requested scalar law is still additive
   on `H`.
4. Prime-to-`p` torsion lifts uniquely as a finite-etale group and has zero
   formal defect relative to that canonical torsion section.
5. Every non-torsion set section differs by p-primary lift error and must solve
   the additional defect equation reconstructed in P1543.
6. Free first-jet consistency is the tangent space of the zeroth-order relation;
   JET/JETB toy evidence is consistent with, but not needed for, the module
   theorem.
7. Higher finite additive jet order does not escape the prime-to-`p` vanishing
   argument.
8. Canonical lifts and Frobenius lifts preserve etale torsion but do not orient
   its cyclic source line.
9. Arithmetic delta-characters vanish on finite prime-to-`p` torsion when their
   output is additive p-adic data.
10. Etale cohomology, abstract ell-modules, and pairings either preserve/move
    the DLP or require orientation and non-generic extension costs.
11. An arbitrary nonadditive, lift-invariant, typed scalar invariant remains
    unclassified, but IDEA-004 supplies none with a complete cost.

## Disposition and next action

P1547 is terminal inconclusive within finite nilpotent additive jets, formal
groups, truncated and p-complete Witt targets, p-typical and crystalline
residues, additive arithmetic differential characters, finite-etale torsion
lifts, free first jets, higher finite additive jets, Frobenius-polynomial and
named cohomological/pairing routes. Preserve IDEA-004, IDEA-140, P1543, JET,
JETB, and this receipt. Do not implement or execute a jet preflight.

Exactly one next action: rerank outside additive local lifts, p-typical targets,
finite-etale re-encodings, torsion orientation, and free tangent consistency.
Bind one mechanism-distinct P1548 theorem question. Reopening IDEA-004 requires
an explicit nonadditive point invariant or genuinely constructed ell-primary
module, a canonical basis, lift-invariance theorem, typed scalar inverse, and
complete costs in the proposal.

No generic-prime ECDLP recovery, relation campaign, direct scalar solve,
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Primary references

1. J. Borger and L. Gurney, *Canonical lifts of families of elliptic curves*,
   <https://arxiv.org/abs/1608.05912>.
2. The Stacks Project, Lemma 39.9.9, multiplication prime to the characteristic
   on an abelian variety is etale,
   <https://stacks.math.columbia.edu/tag/0BFH>.
3. A. Buium and L. E. Miller, *Purely Arithmetic PDEs Over a p-Adic Field:
   delta-Characters and delta-Modular Forms*,
   <https://doi.org/10.4171/MEMS/6>.
4. I. A. Semaev, *Evaluation of discrete logarithms in a group of p-torsion
   points of an elliptic curve in characteristic p*,
   <https://doi.org/10.1090/S0025-5718-98-00887-4>.
5. N. P. Smart, *The discrete logarithm problem on elliptic curves of trace
   one*, <https://doi.org/10.1007/s001459900052>.
6. V. Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>.

These sources establish the canonical-lift, prime-to-characteristic etale,
arithmetic-differential, anomalous, and generic controls. The finite-jet
filtration and prime-to-`p` vanishing deductions above are exact. None supplies
the missing nonadditive scalar invariant or canonically based ell-primary
coordinate for the generic prime-field subgroup.
