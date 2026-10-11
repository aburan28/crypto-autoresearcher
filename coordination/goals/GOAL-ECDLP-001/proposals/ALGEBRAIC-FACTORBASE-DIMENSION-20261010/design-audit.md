# Algebraic factor-base dimension design audit

## Audit basis

- Idea: `IDEA-20261009-a7733f`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- The intake labels this as a theorem-closed finite sanity control. Its
  measurements must not be promoted to a universal theorem or an ECDLP cost
  claim.

## Immediate protocol error

The proposed values `p in {2^16, 2^20, 2^24}` are not prime fields. They are
powers of two, so the stated `F_p` objects and the Hasse--Weil comparison are
not the intended characteristic-two prime-field experiment. The contract must
replace them with an explicit list of odd primes (or consistently reformulate
the entire experiment over finite fields of characteristic two, with a field
size parameter `q`, not `p`). Each accepted row needs its field definition,
prime or irreducibility certificate, curve nonsingularity certificate, and
exact bit length.

## Scope and mathematical contract

The headline quantifier—“for every tested algebraic factor base”—is too broad
for the proposed finite enumeration. A factor base is not defined by a degree
alone. For every family, the record must name the ambient variety, the map or
equations, the subset of `E(F_p)` actually used as factor-base elements, and
the membership and relation costs. In particular, a graph in `E x E` or a
pullback from a cover is not automatically a subset of `E`; the projection,
fiber selection, and any quotient or multiplicity convention must be stated.
The experiment must count the union after normalization, including component
intersections and singular points, rather than report a per-component count
that can be mistaken for the total factor base.

Hasse--Weil applies to a specified smooth projective geometrically
irreducible curve, with component and genus hypotheses. It does not by itself
prove a lower bound for an arbitrary reducible, singular, non-geometrically
irreducible, or higher-dimensional construction. The claimed “genus about
`p^0.4`” threshold also does not follow from the displayed bound: the lower
bound `p + 1 - 2g sqrt(p)` becomes weak at a scale controlled by `g` near
`sqrt(p)`, not automatically `p^0.4`. Any exponent statement must be derived
from an explicitly stated inequality and parameter regime, or removed from
the finite control.

Likewise, “defining equations are exponential-size” is not a certificate.
The record must measure a declared representation size—dense coefficient bit
length, sparse encoding length, arithmetic-circuit size, or another fixed
model—and include the cost of constructing, evaluating, and testing the
family. A high-genus curve can have a compact description, so genus alone is
not an encoding lower bound. Factor-base cardinality alone is also not an
index-calculus obstruction unless relation generation and linear-algebra costs
are included.

The positive comparison `x in F_q over F_{q^2}` must be a separately defined
extension-field control. It needs exact `q`, the extension polynomial and
irreducibility certificate, the Weil-restriction or coordinate map, the
meaning of “x in F_q”, and the counted factor-base elements. It is not a
valid control merely because its cardinality is expected to be `q`.

## Required runnable contract

Before approval, the experiment must freeze:

- an explicit prime/field table and exact curve or variety equations;
- one or more named algebraic-family constructors, with map degree, domain,
  codomain, normalization, components, and point-selection rules;
- exact point-counting certificates or independently checked counts for every
  family and parameter row;
- genus and geometric-integrity checks on normalized components;
- the representation-size model and construction, membership, relation, and
  linear-algebra cost measurements;
- a positive extension-field control with its own exact field and map
  certificates;
- raw counts and certificates, not only a fitted `|F|/p` curve; and
- exact commands, source/dependency hashes, seeds where enumeration is
  randomized, stdout/stderr, validity states, and archive handoff.

The stopping rule must refer to the repaired rows and named families. A
failed field certificate, point count, normalization, or extension control is
`invalid` or `failed_infrastructure`, never evidence for or against the
dimension claim. Three finite sizes cannot establish an exponent by fitting;
at most they provide an implementation check against the stated bound.

## Interpretation and disposition

A valid run could establish only the measured cardinalities and costs for the
named families and parameter rows. It cannot establish the universal
quantifier, exclude compact high-genus descriptions, or change the
prime-field ECDLP frontier. A deviation is meaningful only after the exact
family, point-counting, and representation contracts are valid; it closes no
broader class than the tested scope.

Disposition: **keep proposed and do not approve as a claim-changing
experiment.** The idea is largely an implementation sanity check for an
existing knowledge row, but it is not runnable until the field table, family
definitions, Hasse--Weil hypotheses, genus/encoding model, and extension
control are repaired. If those repairs are not worthwhile, retain the idea as
a theorem receipt and do not dispatch a finite enumeration.

Next action: replace the invalid power-of-two field rows and publish a
family-by-family contract with exact point-count and representation-size
certificates, then rerun readiness. Do not report a finite fit as a universal
dimension obstruction.
