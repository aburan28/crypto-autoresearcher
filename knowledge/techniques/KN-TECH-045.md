---
id: KN-TECH-045
type: technique
title: Overstretched NTRU and the fatigue point as an instance-validity check
tags: [ntru, overstretched-ntru, fatigue-point, dense-sublattice, instance-validity, hygiene, parameter-regime, bkz, structure, lattice]
confidence: reported
complexity: fatigue point at q ~ 0.004 * n^2.484 for ternary NTRU; above it, lattice reduction succeeds at substantially lower block size than the standard estimate predicts
applicability: any NTRU-shaped lattice instance, including NTRU-based FHE and any internal experiment measuring reduction behaviour on an NTRU lattice; a precondition check, not an attack
source_refs: [KN-LIT-112, KN-LIT-113, KN-LIT-114, KN-LIT-052, KN-TECH-041, KN-TECH-030]
added: 2026-07-24
superseded_by: null
---

## Method
An NTRU lattice with a large modulus `q` relative to its dimension `n` is
*overstretched*: it contains an exceptionally dense sublattice, and BKZ finds
secret-key information at a much lower block size than the standard LWE-style
estimate predicts. The boundary is the **fatigue point**. For ternary NTRU with
the standard secret distribution, KN-LIT-114 settles it asymptotically at
`q = n^(2.484+o(1))` and concretely at `q ~ 0.004 * n^2.484`, improving
Kirchner-Fouque's upper bound of `n^(2.783+o(1))` (KN-LIT-113) and supplying the
mechanism that the earlier impossibility argument lacked.

## Use it the way Pohlig-Hellman is used
This is the lattice counterpart of KN-TECH-030: a condition on the instance
that, if unchecked, manufactures an apparent algorithmic advantage that is
really an artifact of parameter choice. The obligations are the same in shape.

1. **State `q` against the fatigue point.** An experiment reporting that some
   reduction strategy beat the predicted block size on an NTRU-shaped lattice
   has reported nothing until it states `q / (0.004 * n^2.484)`. Above 1, the
   effect is expected and is not the mechanism under test.
2. **Do not generalise across the boundary.** Behaviour measured in the
   overstretched regime does not transfer below it, which is exactly the error
   that made NTRU-based FHE schemes appear secure (KN-LIT-112).
3. **Toy scale is where this bites.** As with accidental smooth group order on
   the ECDLP side, small `n` with a convenient `q` lands in the overstretched
   regime easily, so the check matters most in precisely the experiments the
   program can afford to run.

## Applicability limits
The concrete fatigue point is stated for ternary NTRU with standard secret
deviation; other secret distributions shift it and this corpus does not record
by how much. The result concerns NTRU lattices specifically -- plain LWE lattices
have no analogous dense sublattice and no fatigue point. Being below the fatigue
point means the overstretched phenomenon does not apply; it is not a security
proof, and says nothing about the many other ways an NTRU parameter set can be
weak.

## Verified vs reported
The fatigue-point values, the dense-sublattice mechanism, and the improvement
over Kirchner-Fouque are reported from KN-LIT-114's abstract; the constant 0.004
and the exponent 2.484 were not re-derived and the supporting experiments were
not reproduced. The Kirchner-Fouque bound is recorded at second hand (see
KN-LIT-113's own verification caveat). The framing of the fatigue point as a
program-side instance-validity gate, and the parallel to Pohlig-Hellman, are
this program's own reasoning and are not claims made by any cited source.
