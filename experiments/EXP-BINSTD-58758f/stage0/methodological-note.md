# Methodological note — EXP-BINSTD-58758f Stage 0 (HOLD-O)

Task: `TASK-20261001-c04c94`. Observations / certificates only. No deployed-curve
break claim. No free-cofactor framing.

## Target-side reading (closed)

The HOLD-O correction replaces the false step "quotients of S are trivial or
all of S" by the chain

```text
E > 2E > 4E = C
```

with quotients `E/2E ≅ Z/2` (parity map `π = Tr(x)+Tr(a)`) and `E/4E ≅ Z/4`.
Both quotients are identically 0 on C-targets, so they carry **no** information
about a C-target discrete log. Target-side "spend the cofactor via a group
quotient" therefore closes to the same C-reduction rho already performs
(Theorem-C style prime-order rigidity on C). Hand-checked on `Z/12` and on the
n=19 Koblitz order group `Z/(4·130873)`.

## Leg-side lever (out of scope — DC-04)

The same chain is nontrivial on legs. Parity alignment and the nonlinear E/4E
bit as window conditions are owned by the DC-04 cluster:

- `IDEA-20260922-1b16d7`
- `IDEA-20260922-153a90`

This experiment cross-cites those records and does **not** redesign or claim
that lever.

## Part (B) pricing: base-size, not free

Whether builders restrict candidate x-coordinates to one cofactor coset
(`H_unspent`) or admit all cosets (`H_spent`) is an engineering code/spec read
(Stage 0 builder audit). If unrestricted windows are larger, yield conservation
prices the effect as ordinary factor-base **size**:

```text
V / V_C  ~  4^{m-1}
```

at about 4× the unknowns — the standard base-size trade. The protocol forbids
calling this a free structural / free cofactor gain.

## Null controls (h=1 impossible)

No ordinary binary Weierstrass curve `y²+xy=x³+a x²+b` has odd order (rational
2-torsion `(0,√b)` always exists). The h=1 null is forbidden. Controls are:

1. h=2 sibling (Z/4 undefined; parity ratio still ~2) — Stage 2;
2. relabelled `Z/(4l)` generic group — Stage 1 replica.

## ECC2K-130

Named structural setting only. No scientific group walk at deployed m≥131.
