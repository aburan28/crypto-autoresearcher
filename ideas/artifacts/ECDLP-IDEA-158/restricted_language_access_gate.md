# IDEA-158 restricted-language and induced-template access gate

Status:
`SCOPED_NEGATIVE_LIFT_INVARIANT_FIXED_BRANCH_DELETION__INDUCED_TEMPLATE_SUPPORT_ROUTER_OPEN`

This is a theorem-only producer receipt. No contract, CSP solver, finite-field
search, toy curve, relation campaign, or timing run was executed. It separates
two different meanings of a "restricted x-only relation" that were conflated
in the prior IDEA-158 boundary:

1. delete a fixed proper subset of signed summation branches on the ambient
   Kummer quotient; or
2. restrict the full relation to the sparse factor-base domain and ask only
   for a polymorphism of that induced template.

The first route is impossible as a lift-invariant x-only relation. The second
route is a real exception to the prior ambient polymorphism theorem, but a WNU
identity alone does not provide access to the induced relation. Explicit access
costs `B^m`; implicit support access is the unresolved target-local summation
router.

## Frozen signed-branch model

Let

```text
G=Z/NZ,  K_star=(G minus {0})/{+1,-1},
```

with prime `N`. For fixed arity `m>=3` and a sign vector
`e=(e1,...,em) in {+1,-1}^m`, put

```text
H_e={x in G^m: sum_i ei*xi=0}.
```

The global pairs `e` and `-e` define the same hyperplane. Thus the full affine
Kummer summation relation is the union of `2^(m-1)` distinct branch
hyperplanes, restricted to nonzero coordinates and then quotiented by
independent coordinate signs.

For a fixed branch family `S`, closed under global negation, write

```text
U_S=union_(e in S) H_e.
```

It would define an x-only relation on `K_star^m` only if membership were
unchanged when any chosen lift `xi` is independently replaced by `-xi`.

## Theorem 1: fixed proper branch deletion is not x-only

Assume

```text
N > 2^(m-1)+m-1.
```

If `U_S` restricted to tuples with every coordinate nonzero is invariant under
all independent coordinate sign changes, then `S` is empty or contains every
branch modulo global negation.

Proof. There are `L=2^(m-1)` distinct branch hyperplanes. Inside one `H_e`,
each intersection with another branch hyperplane has at most `N^(m-2)`
points. Each coordinate-zero section also has at most `N^(m-2)` points. Hence

```text
|(H_e intersect (G minus {0})^m)
  minus union_(f not equal +/-e) H_f|
  >= N^(m-1)-(L-1+m)N^(m-2) > 0.
```

Every branch therefore has a nonzero-coordinate point belonging to no other
branch. A union of branch hyperplanes on the affine chart uniquely determines
its included branch set.

For `d=(d1,...,dm) in {+1,-1}^m`, changing lifts by `x-->d*x`
maps `H_e` to `H_(e*d)`. Lift invariance consequently gives

```text
S=S*d
```

modulo global negation for every `d`. The independent sign-change group acts
transitively on the `L` branch classes. Its only invariant subsets are the
empty set and the full set.

Thus a fixed parity class, preferred sign pattern, or proper signed branch
catalog is not a well-defined relation on x-coordinate orbits. Choosing one
requires an additional orientation section, y-sign advice, or another public
structure beyond the x-only quotient.

## Scope of Theorem 1

The theorem does not prohibit a proper relation of the form

```text
full_R_m(x1,...,xm) and C([x1],...,[xm]),
```

where `C` is a genuine lift-invariant predicate on the x-orbits. Such a chart
deletes whole quotient tuples rather than selected signed branches. It must
still cover enough exact sources, and any family of charts must charge every
chart, overlap, missed source, and target descent.

The theorem also does not cover a relation induced only on the factor base.

## Model correction: ambient and induced polymorphisms differ

Let `F_x subset K_star` have size `B`. The previous IDEA-158 theorem chain
rules out an idempotent WNU

```text
w:K_star^k-->K_star
```

that preserves the full ambient summation relation, public constants, and
`F_x` as a unary relation.

It does not by itself rule out an operation

```text
w_F:F_x^k-->F_x
```

that preserves only the induced target fiber

```text
T_R={a in F_x^m: full_R_(m+1)(a,R)}.
```

The constants and adjacent translated Kummer windows used by the ambient
interpretation need not lie in `F_x`. Claiming that the ambient theorem closes
the induced template would therefore overstate the evidence.

Indeed, if `T_R` is a singleton, every idempotent operation on `F_x` preserves
it: applying the operation to copies of its sole tuple returns that tuple.
Such a vacuous WNU says nothing about how to find the hidden tuple.

## Proposition 2: the induced template has an access obligation

Consider the endpoint-labelled relation graph

```text
Gamma_F={(a1,...,am,R): ai in F_x and full_R_(m+1)(a1,...,am,R)}.
```

Every factor-base tuple has at least one signed endpoint, so for fixed arity

```text
|Gamma_F| >= B^m.
```

An explicit relation table or complete source-labelled template therefore has
at least `B^m` entries. At the balanced five-source index-calculus choice

```text
m=5, B=N^(1/5),
```

this is `N` entries, already above rho in time and memory.

A single target fiber may be small; under the usual random-density heuristic
its expected cardinality is `B^m/N=Theta(1)`. But constructing that small
fiber by scanning the endpoint graph still costs `B^m`. Its small output does
not provide an output-sensitive locator.

Standard bounded-width CSP results treat the finite template and its relations
as fixed and accessible. Here the domain, factor base, curve, and induced
relation all scale with `N`; their construction and access cannot be omitted
from the ECDLP cost model.

If the relation is kept implicit, a support query for a prefix
`(a1,...,as)` asks whether there exist remaining factor-base values with

```text
full_R_(m+1)(a1,...,as,a_(s+1),...,a_m,R).
```

After subtracting the public prefix, this is exactly an `(m-s)`-source
restricted summation/completion query, including all sign and exceptional
strata. Returning witnesses is the corresponding exact source-unranking
problem.

Therefore a WNU identity on the induced sparse template is not an ECDLP
algorithm unless it is accompanied by one of:

1. a charged explicit relation representation below rho; or
2. a target-independent implicit support and witness router with complete
   setup, query, output, source, rank, and blind-descent costs below rho.

For five sources, the second item is operationally the P1515/IDEA-165 target
router: the current favorable gate is setup at most `B^2.25`, per-target query
at most `B^1.25`, exact all-strata source output, and no hidden `B^3` state or
scan.

This is an interface and accounting reduction, not an unconditional lower
bound against every implicit data structure.

## Disposition

The most direct "branch-deleting promise" successor is closed:

- fixed signed branch subsets are not lift-invariant x-only relations;
- selecting a branch requires the orientation information the quotient erased;
- a genuine quotient predicate may delete whole tuples but must prove complete
  source coverage and cannot call that branch selection; and
- an induced factor-base WNU can be vacuous unless its relation-access and
  witness-generation operation is explicitly constructed and charged.

The surviving IDEA-158 operation is now one compact target-uniform support
router for an induced factor-base relation, together with a non-affine WNU and
exact signed-source inverse. Without that router, the proposal semantically
reduces to P1515 rather than supplying a new bounded-width algorithm.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

1. Verify distinctness and irredundancy of the signed branch hyperplanes on the
   nonzero affine chart.
2. Verify transitivity of independent lift changes modulo global negation.
3. Confirm that the no-go is limited to fixed signed branch families.
4. Confirm the ambient-versus-induced polymorphism correction.
5. Check the `B^m` endpoint-graph count and balanced `B=N^(1/m)` cost.
6. Check that every implicit support query is typed as residual restricted
   summation rather than treated as free template access.
7. Preserve arbitrary implicit support data structures as open.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
- Barto and Kozik, *Constraint Satisfaction Problems of Bounded Width*:
  <https://doi.org/10.1109/FOCS.2009.32>
- Barto, Bulin, Krokhin, and Oprsal,
  *Algebraic approach to promise constraint satisfaction*:
  <https://arxiv.org/abs/1811.00970>
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>
