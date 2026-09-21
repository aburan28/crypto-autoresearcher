# IDEA-059 One-Map Cremona Derivation Gate

## Candidate A: Use The Summation Relation As A Coordinate

For three unordered x-coordinates, let `e1,e2,e3` be the elementary
symmetric invariants and let `S4_e(e1,e2,e3;x_Q)` be the exact four-point
Semaev relation with the target x-coordinate fixed.  The tempting triangular
map is

```text
(e1,e2,e3) -> (e1,e2,S4_e).
```

It makes the summation equation linear in the new third coordinate.  On the
frozen `F_1033` fixture, however, `S4_e` is an irreducible quartic in `e3`
over `F_1033(e1,e2)`.  The inverse therefore has four generic branches.  This
map is finite of degree four, not birational, and cannot enter the Cremona
grammar.  Its apparent Newton shrinkage moves the missing degree into source
inversion.

## Candidate B: Elliptic Group-Addition Cremona Map

For four ordered source points define

```text
T(P1,P2,P3,P4) = (R1,R2,R3,R4)
R1 = P1
R2 = P1 + P2
R3 = P3
R4 = P1 + P2 + P3 + P4.
```

The integer matrix is

```text
[1 0 0 0]
[1 1 0 0]
[0 0 1 0]
[1 1 1 1]
```

and has determinant one.  Its inverse is

```text
P1 = R1
P2 = R2 - R1
P3 = R3
P4 = R4 - R2 - R3.
```

Thus `T` is a target-independent automorphism of the group variety `E^4`, not
merely an affine rational formula.  On the fiber `R4=Q`, the original direct
summation relation becomes a serial addition representation with factor-base
conditions on

```text
P1, R2-P1, P3, Q-R2-P3.
```

Complete elliptic addition charts make the map and inverse global; vertical,
doubling, identity, and denominator-zero cases are chart cases rather than
discarded exceptional components.

## Frozen Saturated Comparison

P1492 independently compares the direct `S6` square-up with the exact serial
`S3` representation induced by this map.  For selector degree `r`, both have

```text
mixed volume = 16*r^4.
```

The frozen fixture values are

```text
r = 4:  4096
r = 7:  38416
r = 12: 331776.
```

The complete synthetic sweep through `r=128` has the same identity.  Every
ordered signed source path is retained and independently replayed.  The
serial coordinates change the equation shape but do not cancel the dominant
selector faces after source-complete saturation.

## Review Verdict

- Candidate A shrinks the visible summation equation but is not Cremona: its
  inverse is generically four-valued.
- Candidate B is a genuine target-independent elliptic-syzygy Cremona map
  with an exact inverse, but its source-complete mixed volume is identical to
  the direct system.

IDEA-059 therefore has no passing map in its currently specified grammar and
must not enter the 540-CPU-hour scaling campaign.  This does not close a future
non-group-linear birational map with a separately supplied inverse and strict
saturated-volume certificate; such a map is a new concrete hypothesis.
