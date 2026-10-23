# Odd torsion translation under explicit additive laws

This elementary derivation concerns one mechanism in lead 6. It supplies a
precise formal target; it is not a novelty claim, a new ECDLP algorithm, or a
claim that torsion methods are exhausted.

## Statement

Let A carry an associative, commutative addition with a two-sided zero. Define
nP by repeated addition. Suppose r is odd, rP=0, and T+T=0. Then r(P+T)=T.
If T≠0, P+T is outside the kernel of multiplication by r.

In the Lean source, oddness is the explicit witness `r = k + k + 1` for a
natural k. The model includes the additive laws as structure fields; it does
not assume the desired conclusion. Inverses, primality of r, and a finite
carrier are not needed. Every abelian group satisfies the stated additive laws.

## Derivation

Repeated addition distributes over a sum by induction and the additive laws.
Thus r(P+T)=rP+rT. The first term is zero. Writing r=k+k+1 gives
rT=kT+kT+T. Distribution identifies kT+kT with k(T+T)=k0=0, so rT=T.
Nonzero T then gives the kernel exclusion.

The two-element XOR model is a non-vacuous positive control. With P=false,
T=true, and r=3, the translated scalar multiple is true. With r=2 it is false:
the oddness hypothesis cannot be dropped. The separate nonzero hypothesis is
also essential for the kernel-exclusion conclusion.

## Formal scope and remaining bridge

The source is [Torsion.lean](../../formal/scoped-obstructions/ScopedObstructions/Torsion.lean).
It uses a dependency-free Lean workspace pinned to 4.22.0. The project audit
rejects every global axiom dependency; the existing repository worker also
checks that the exact requested declaration is a theorem and scans forbidden
proof constructs.

A successful kernel check establishes this formal conditional statement.
Independent semantic-fidelity review remains necessary. No concrete elliptic
curve representation, point arithmetic, rational two-torsion certificate, or
factor-base membership checker is imported by this file. The statement does
not exclude even translations of tuples with preserved total, or T-closed
mixed-domain factor bases.

The imported advisory claim `torsion_subgroup_obstruction` retains its original
`not_formalized` label; this new proof result is separate from promotion of
that application. The remaining obligations are tracked in
[the problem record](../../problems/ten-lead-proof-scope-and-artifact-access.md).
