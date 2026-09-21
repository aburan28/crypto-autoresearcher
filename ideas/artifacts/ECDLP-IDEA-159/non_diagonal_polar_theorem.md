# IDEA-159 non-diagonal polar generic-stalk theorem gate

Status:
`SCOPED_NEGATIVE_GENERIC_STALK_REES_TRICHOTOMY__SOURCE_INDEXED_CENTER_OPEN`

This is a theorem-only producer receipt. No contract, Rees algebra,
normalization, chart computation, source tuple, toy curve, or experiment was
run. It screens ECDLP-IDEA-159's required first operation: a target-independent
polar ideal that is nonunit on the generic all-distinct relation stratum and
whose blowup has exceptional valuations labeling every generic source.

The result is scoped to ordinary blowups of coherent ideals on the reduced
source-labelled relation incidence. It is not a lower bound against every
birational, derived, stacky, or noncommutative representation. It shows that
the stated generic-stalk requirement cannot hold for an ordinary ideal in the
way IDEA-159 needs.

## Frozen interface

Let `X` be the reduced all-distinct source-labelled five-point addition
incidence over the public target base. The argument is componentwise, so fix
one irreducible component `X_i` with generic point `eta_i`. Then

```text
O_(X_i,eta_i) = K(X_i)
```

is a field.

Let `J subset O_X` be a coherent target-independent ideal sheaf defined from
the incidence equations, a conormal construction, Jacobian minors, or fixed
polar data. Let

```text
Bl_J(X) = Proj_X(sum_(n>=0) J^n)
```

be its ordinary Rees blowup, followed if desired by normalization.

IDEA-159 requires `J` to be nonunit at generic all-distinct source points and
requires exceptional divisorial valuations over those points to distinguish
the exact source components.

## Lemma 1: the generic stalk has no proper nonzero ideal

At `eta_i`, the stalk `J_(eta_i)` is an ideal of the field `K(X_i)`. Hence

```text
J_(eta_i) = 0  or  J_(eta_i) = O_(X_i,eta_i).
```

There is no third case corresponding to a proper nonzero generic ideal.

If `J` is nonzero on the integral component, one nonzero local generator
becomes invertible in the function field, so `J_(eta_i)=O_(X_i,eta_i)`. By
coherence, `J` is the unit ideal on a dense open neighborhood of `eta_i`.

If `J_(eta_i)=0`, then `J` vanishes identically on that reduced component.
The positive-degree part of its Rees algebra restricts to zero, so its
relative Proj supplies no blowup chart or exceptional divisor over the
generic component.

Thus the phrase "proper nonunit ideal at the generic stalk" is algebraically
impossible on a reduced irreducible component.

## Lemma 2: a proper center changes only its support

Let `Z=V(J)`. The blowup morphism

```text
b: Bl_J(X) --> X
```

is an isomorphism over `X minus Z`. Therefore every exceptional valuation is
centered over `Z`.

For any nonzero ideal on `X_i`, `Z intersect X_i` is a proper closed subset.
The generic all-distinct point lies outside it, and the blowup has no
source-specific exceptional data there. Normalizing the blowup cannot create
an exceptional divisor over an open set on which the original blowup is
already an isomorphism and the source is normal/smooth.

Consequently a polar ideal supported on a discriminant, ramification locus,
rank-drop locus, tangency locus, or other proper critical set can label only
that lower-dimensional set. It cannot be biconditional with all generic
all-distinct source tuples.

## Lemma 3: divisorial centers do not atomize sources

Suppose `J` defines an effective Cartier divisor on the smooth all-distinct
stratum. Then `J` is invertible there. Blowing up an invertible ideal is an
isomorphism: the center is already Cartier, so the universal operation that
makes it Cartier changes nothing.

Thus moving the polar center from a codimension-at-least-two critical locus to
a divisor does not create source atoms. The alternatives are:

1. `J` is unit generically: no generic exceptional valuation;
2. `J` is invertible but nonunit along a divisor: the blowup is still an
   isomorphism there; or
3. `J` is noninvertible on a proper higher-codimension/branch locus: the
   exceptional data covers only that locus.

None supplies a valuation word for every generic all-distinct source.

## Lemma 4: reducible source incidence does not help for free

The source-labelled incidence may have many irreducible components. Apply
Lemma 1 at every component generic point. The ideal is either unit or zero on
each component.

- Unit components acquire no exceptional generic valuation.
- Zero components have no positive-degree Rees algebra at their generic
  points.
- Choosing different zero/unit behavior across components already encodes a
  partition of source components in the ideal support.

One binary partition is not a canonical exact source inverse. A family of
centers refined until every component has a unique valuation word is a
source-indexed component dictionary unless a compact public rule and complete
sub-rho construction bound are separately proved. This receipt does not claim
a universal lower bound for all such rules; it identifies the missing
operation rather than granting it to the polar blowup.

## Consequence for Jacobian and polar ideals

On the smooth/etale all-distinct locus, the relative Jacobian/Fitting ideal is
the unit ideal, reproducing the scoped IDEA-097 result. A different polar
ideal can be nonunit only by defining a proper closed polar/critical locus or
by vanishing identically on a component.

The first case is not source-complete. The second has no ordinary Rees
exceptional divisor at the generic point. Selecting a polar direction after
seeing the target/source, or adding closures of individual source sheets to
the center, is respectively post-hoc selection or explicit source advice.

Hence "non-diagonal" changes the name of the center but does not evade the
generic-stalk trichotomy.

## Cost and descent disposition

The required generic valuation/source operation does not exist for the
frozen ordinary ideal, so its specialization and source-inverse exponents are
not finite algorithmic costs.

A branch-locus-only blowup has relation density equal to the exceptional
locus density and misses generic accepted tuples. A component-indexed center
must charge every generator, chart, normalized component, valuation word,
source inverse, relation attempt, rank row, factor-log solve, masked descent,
and output. No compact component rule is supplied by IDEA-159.

This receipt does not prove that every possible target-specialized nonlinear
representation costs at least rho. It closes only ordinary target-independent
polar/Rees atomization of generic all-distinct sheets.

## Disposition for ECDLP-IDEA-159

The declared generic-stratum polar blowup is scoped negative:

- a generic stalk is a field and has no proper nonzero ideal;
- a nonzero coherent ideal is unit on a dense open set;
- blowups are isomorphisms away from their proper centers;
- invertible/Cartier centers also blow up trivially; and
- centers supported on critical loci do not label generic source tuples.

Independent review should either accept scoped rejection or specify a
different nonordinary representation with a compact target-independent
source-component rule and complete cost. No Rees algebra should be constructed
before that operation exists.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

An independent reviewer should verify:

1. the reduced all-distinct incidence is treated componentwise;
2. an ideal of a function field is only zero or the whole field;
3. a nonzero coherent ideal is unit on a dense open of an integral component;
4. the blowup is an isomorphism away from its center;
5. blowing up an invertible ideal is an isomorphism;
6. normalization is not claimed to change a normal open set already preserved
   by the blowup;
7. zero/unit choices across components are recognized as source advice; and
8. no conclusion is extended to arbitrary derived or target-local nonlinear
   representations.

## Primary references

- The Stacks Project, *Blowing up*:
  <https://stacks.math.columbia.edu/tag/085P>.
- The Stacks Project, *Blow up algebras*:
  <https://stacks.math.columbia.edu/tag/052P>.
- Teissier, *Varietes polaires II*:
  <https://eudml.org/doc/142481>.
- Duarte, Jeffries, and Nunez-Betancourt, *Nash blowups of toric varieties in
  prime characteristic*: <https://arxiv.org/abs/2208.05599>.

The references supply the ordinary blowup/Rees and neighboring polar/Nash
geometry. None supplies a generic elliptic source atomizer or a below-rho
ECDLP algorithm.
