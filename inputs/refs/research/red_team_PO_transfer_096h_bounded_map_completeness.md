# Red Team: PO96H Bounded-Map Completeness

## Claim or task

Audit whether PO96H's `15/15` result proves absence of degree-2, degree-3,
and degree-4 elliptic subcovers for its two curves over `F_127`.

## Status

```text
NEGATIVE RESULT / DEGREE-3 SEARCH INCOMPLETE / DEGREE-4 CHART CENSUS ONLY /
PO96H AGGREGATE ABSENCE CLAIM REJECTED / TOY / MODEL-BOUND
```

## Frozen audited artifacts

- contract SHA-256:
  `228bfe30f2154de14ad4f66c2164a21ff93522579c4f8b4eba04802586f5d3a2`
- producer SHA-256:
  `148e4a50d5c3c371480dd0d9ae4563bf84bac20787c074594edff14bca2e9024`
- result SHA-256:
  `0aba60eb3cb5da2a0e957f2c9b55119fe954d94efd5ac465649d1dad4c7cdb29`

The producer reruns successfully.  This audit narrows interpretation; it does
not alter the historical result.

## Decisive degree-3 counterexample

The producer always maps the split source triple to the distinguished Shaska
cubic

```text
4*s^3 + b^2*s^2 + 2*b*s + 1.
```

It never tests the opposite orientation.  Over `F_127`, let

```text
f(s) = s^3 + 4*s + 1,
g(s) = 4*s^3 + 16*s^2 + 8*s + 1.
```

Here `f` splits and `g` is irreducible.  Under

```text
s = (94*x + 1)/(x + 85),
```

take

```text
H*: y^2 = (x^3 + 110*x + 121)*(9*x^2 + 101*x + 25).
```

The exact degree-3 map is

```text
u = s^2/f(s),
v = y*(s^3 - 4*s - 2)/((x + 85)^3*f(s)^2),
```

and satisfies

```text
v^2 = 11*u^3 + 93*u^2 + 64*u + 16.
```

The target cubic is squarefree with discriminant `122`.  Exact substitution
verifies the function-field identity and map degree three, while PO96H's
`degree_three_subcovers` returns no candidate.  Its synthetic control uses the
same accepted orientation and therefore does not detect the defect.

## Surviving boundaries

- The exhaustive rational `PGL_2(F_127)` involution search supports no
  `F_127`-rational separable degree-2 elliptic subcover for either fixture.
- The degree-3 output proves only no hit in one oriented Shaska chart.
- The degree-4 output proves only that neither target invariant appears among
  the enumerated smooth `F_127` parameter rows.  It does not prove absence of
  rational or geometric degree-4 maps.
- The character calculation proves a formal group-algebra orthogonality sum,
  not an evaluated pull-push correspondence on differentials and divisors.
- The isogeny replay proves one rational isogeny at each preselected degree
  `13` and `7`; uniqueness, volcano orientation, and identification of the
  elliptic image inside the Jacobian remain open.

## Stronger continuation

Use the integral Rosati-symmetric endomorphism

```text
N = F + V + 20.
```

It satisfies `N^2=21*N` for H7 and `N^2=39*N` for H10.  Test whether it kills
the complete geometric `J[3]`.  This saturation question is independent of
the defective bounded-map census and exposes the primitive integral Hom
lattice without the extraneous characteristic-127 factor in PO96H's
`Q[F]` projector.

## Required repair

1. Recover this swapped-orientation counterexample as a registered positive
   control.
2. Search both cubic orientations for the fixtures.
3. Replace the degree-4 self-census control with independently supplied exact
   generic and degenerate degree-4 maps.
4. Keep all degree-3 and degree-4 absence booleans out of promotion gates until
   those repairs pass.

## Handoff: PO96H-V2 bounded-map falsifier

### Claim or task

Repair the degree-3 orientation defect before interpreting either fixture's
empty chart search as a subcover negative.

### Status

NEGATIVE RESULT

### Assumptions

- All maps and curves are over `F_127`.
- Exact function-field substitution and degree are the acceptance tests.

### Evidence so far

- A concrete omitted degree-3 cover is given above.
- The existing one-sided search returns a false negative on it.

### Failure modes

- A repaired search may still omit finite-field twists or descent cases.
- A chart match without an exact map remains insufficient.

### Next concrete action

Implement a versioned PO96H-V2 positive-control gate that recovers the exact
swapped-orientation map above and both complementary Shaska orientations.

### Artifact paths

- `research/PO_transfer_096h_p127_cm3_correspondence_preflight_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_096h_p127_cm3_correspondence_preflight.sage`
- `experiments/ecdlp_isogeny/po_transfer_096h_p127_cm3_correspondence_preflight.json`
- `research/PO_transfer_096i_p127_divided_frobenius_projector_contract.md`
