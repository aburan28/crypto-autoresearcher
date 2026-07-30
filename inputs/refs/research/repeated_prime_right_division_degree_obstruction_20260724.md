# Repeated-Prime Right-Division Degree Obstruction

Date: 2026-07-24

## Handoff: explicit divided-orientation map gate

### Claim or task

Test whether the repeated-prime divided-orientation branch can be promoted by
carrying the divided orientation after each accepted quotient as an explicit
rational map.

### Status

`NEGATIVE RESULT / RIGHT-DIVISION DEGREE OBSTRUCTION / MODEL-BOUND / NOT-A-BREAK`

### Assumptions

- Ordinary prime-field repeated-prime toy fixtures from the existing
  `ell=3`, conductor-9 and conductor-27 profile.
- Current source conductor is `ell^s`, initial conductor is `ell^e`, and the
  quotient line is the accepted ascending line.
- `omega_0` denotes the original Frobenius-order imaginary element.
- This note analyzes explicit rational-map carriage of the primitive divided
  orientation; it does not rule out a compact SLP or other implicit evaluator.

### Result

For a candidate quotient line `L`, the pushed correspondence is

```text
Delta_L = pi_L omega_0 dual(pi_L).
```

On the accepted ascending quotient, if the target conductor exponent is `s'`,
then `omega_0` is divisible in the target endomorphism ring by
`ell^(e-s')`.  Since `Delta_L` has the extra quotient factor `[ell]`, extracting
the primitive target orientation requires right division by

```text
ell^(1 + e - s').
```

At step index `r`, this is `ell^(r+2)`.  The same profile records that a
torsion-killing-only selector needs quotient level `ell^(r+1)`, so bounded
`ell^2` killing cannot be the general escape.

The explicit rational map for the primitive target orientation has degree at
least the norm of the canonical imaginary element in the target order.  In the
recorded conductor-27 fixtures, the first accepted quotient would already carry
degree lower bound `243`; in a tall-conductor family this scales with the
remaining target conductor discriminant, not only with the local prime `ell`.

### Evidence

Artifacts:

- contract:
  `experiments/ecdlp_isogeny/iso_repeated_prime_right_division_degree_proxy_contract.md`
- analyzer:
  `experiments/ecdlp_isogeny/iso_repeated_prime_right_division_degree_proxy.py`
- result:
  `experiments/ecdlp_isogeny/iso_repeated_prime_right_division_degree_proxy_result.json`
- verifier:
  `experiments/ecdlp_isogeny/iso_repeated_prime_right_division_degree_proxy_verify.py`
- verifier result:
  `experiments/ecdlp_isogeny/iso_repeated_prime_right_division_degree_proxy_verify.json`

Hashes:

```text
contract sha256: 3d2b15413703f78c5022077e066945345b7498f26b12d517945d8c6f005cce58
analyzer sha256: 7048db63a2aaee60d12d142df872b6a8abcbc01b208eaa4e599a80cd8cdbc10a
result sha256:   5392a1d1160a9cb810824403197c4f68b8f62e60d997c2792241dd43d98d2365
verifier sha256: 9bd27de5a43ee9a3ff052314109ee862ac2864aa54612475dc25735056a3d12b
verify result:   744c0bea9abd78890540d279eaa88ad5113027996dc5e82328c8c600cb4c2343
```

The verified scientific payload is
`41fefce8edf7a2ea4e2b38c083f618ac64e00e346b5cb871d5b74bf283bb2b24`.
The verifier passes with zero failures and payload
`af69ad8cacfcfb206c3fec6d3efc1e9f28d5b385c98e82c7838c8cc925911eba`.

Compact result table:

| p | initial exponent | max right-division power | max explicit-map degree lower bound | fixed `ell^2` failure |
|---:|---:|---:|---:|---|
| 67 | 2 | 3 | 27 | false |
| 73 | 2 | 3 | 27 | false |
| 103 | 2 | 3 | 27 | false |
| 577 | 3 | 4 | 243 | true |
| 619 | 3 | 4 | 243 | true |
| 757 | 3 | 4 | 243 | true |

Claim gates in the result set:

```text
explicit_map_right_division_is_compact = false
fixed_ell2_sieve_is_general = false
general_isogeny_complexity_improvement = false
scallop_break = false
ecdlp_consequence = false
compact_slp_evaluator_remains_open = true
```

### Interpretation

This closes one natural promotion route for repeated-prime divided orientations:
explicitly carrying the primitive divided orientation as a rational map is not a
local-cost algorithm.  It inherits degree proportional to the remaining
conductor, so it does not yield the requested isogeny-complexity breakthrough.

The branch is not dead.  The remaining target is sharper:

```text
construct gamma_r = omega_0 / ell^r as a compact straight-line evaluator
on E_r[ell], without E[ell^(r+1)] lifts and without expanding gamma_r to its
full rational map.
```

### Failure modes

- The proxy is degree-based and does not prove a lower bound against every
  implicit representation.
- The fixtures are small, special, and `ell=3` only.
- The result depends on the current local-power profile as input evidence.
- A protocol exposing a Bockstein/cross-level character could bypass this
  public-acquisition obstruction, but no such passive transcript is currently
  identified.

### Next concrete action

Implement a sentinel right-division gate: forbid `torsion_basis(ell^(r+1))`,
forbid full lift-order torsion-field basis construction, and require a candidate
`x`-only or pushed-forward compact evaluator to recover the existing nine
exact repeated-prime composites while rejecting under-division and over-division
controls.
