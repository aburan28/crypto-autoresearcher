# IDEA-052 Source-Labelled Wedge Derivation Gate

Date: 2026-07-17

## Canonical Expansion

Let the factor base have labels `e_0,...,e_(B-1)` in a source space `S`, and
let `v_i` be the corresponding complete addition-law evaluation vectors in an
evaluation space `V`.  Define

```text
Omega = sum_i e_i tensor v_i in S tensor V.
```

Antisymmetrizing two copies gives, in odd characteristic,

```text
Alt(Omega tensor Omega)
  = 2 sum_(i<j) (e_i wedge e_j) tensor (v_i wedge v_j).
```

The source coefficients `e_i wedge e_j` form the standard basis of
`Lambda^2(S)`.  Their exact dimension is

```text
dim Lambda^2(S) = B*(B-1)/2.
```

Thus the canonical source-labelled wedge is exactly the unordered pair surface.
Evaluation-vector dependencies can compress the relation certificate but do not
identify which independent source coefficient produced it.

## Second Addition And Pluecker Pairing

For a four-dimensional target quotient `W_T`, the second pair is joined through

```text
H(u wedge v, w wedge z) = det[u,v,w,z].
```

The relation condition `H=0` is the generic Pluecker orthogonality predicate
already implemented and independently verified by PO-transfer-004.  Source
extraction retains a pair label on each side; materializing coefficients uses
the pair surface, while testing all pair-pair coefficients is quartic without a
new query data structure.

PO-transfer-004 found no persistent elliptic incidence excess.  Its charged toy
fit was `0.958`; even its unimplemented ideal-oracle floor fit was `0.561`, and
the concrete sub-pair-pair query gate failed.  This is positive evidence for the
identity and negative evidence for the proposed source-reporting complexity.

## Repeated-Source Obstruction

Antisymmetry gives

```text
e_i wedge e_i = 0.
```

A fixed pairing therefore loses any tuple with an equal-index pair.  Cycling
through all three pairings repairs multiplicity pattern `2+2`, but no pairing
can repair a valid `3+1` tuple: every partition into two pairs contains one
equal-index pair.

On `E/F_11: y^2=x^3+x+5`, whose group has prime order 11, choose generator
`P=(0,4)`.  The repeat-stress factor base

```text
[P, -3P, 2P, -2P]
```

has 14 ordered four-source identity relations.  Eight have multiplicity pattern
`3+1` and vanish in all three pair-wedge charts.  A symmetric control
`[P,-P,2P,-2P]` has 36 relations; all are covered after cycling the three
pairings, while a fixed pairing still misses four `2+2` rows.

Using slot-coloured copies can represent repeats, but it replaces `S` by a
larger occurrence-labelled space and retains quadratic pair state.  Symmetric or
divided-power labels change the proposed exterior mechanism and require a new
identity and cost contract.

## Decision Boundary

The exact wedge/Pluecker certificate and its planted controls are retained.  The
natural source-labelled formulation neither avoids the quadratic pair surface
nor covers complete repeated-source relations.  This does not rule out an
explicit curve-specific syzygy outside the canonical pair wedge, but such a
successor must name its coefficients and prove source decoding before scoring.
