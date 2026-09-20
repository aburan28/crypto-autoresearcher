# THM_QUOTIENT_DESCENT1 — Translations through a degree-2 quotient

- **ID:** THM-QUOTIENT-DESCENT1
- **Filed with:** IDEA-20260920-0490f5 / GOAL-GFPN-380702
- **Author:** top-level session, 2026-09-20
- **Lean stub:** `research/THM_QUOTIENT_DESCENT1.lean` (statement only; not yet checked in a Lean toolchain — coordinator mints the formal goal)
- **Status:** elementary lemma recorded for Galbraith's "larger group actions" thread. Closes the question of which translations descend through the canonical degree-2 (negation) quotient. Does **not** by itself yield an ECDLP algorithm.

## 0. Statement

Let `E` be an elliptic curve over a field `k` of characteristic not 2, with
identity `O`. Write `[-1]` for the negation automorphism and

```
x : E \ {O} → A^1
```

for the degree-2 quotient morphism identifying `P ~ -P` (equivalently: the
geometric quotient `E / ⟨[-1]⟩`). Extend in the usual way to a morphism
`E → P^1`.

**Lemma (translation descent through the degree-2 negation quotient).**
For `T ∈ E(k̄)`, the translation `τ_T : P ↦ P + T` descends through `x`
— that is, there exists a rational map `ψ : P^1 ⇢ P^1` with

```
x ∘ τ_T = ψ ∘ x
```

on a Zariski-open set — **if and only if** `2T = O`.

When the condition holds, `ψ` is a Möbius transformation of `P^1`
(an element of `PGL_2`), recovering the classical 2-torsion action on the
x-line.

## 1. Proof

Fibres of `x` (away from the branch locus) are sets of the form `{P, -P}`
with `P ≠ -P`.

(`⇒`) Suppose `x ∘ τ_T = ψ ∘ x`. Then `τ_T` sends fibres to fibres:
`{P+T, -P+T}` equals `{Q, -Q}` for `Q = P+T`. So

```
{P+T, -P+T} = {P+T, -(P+T)} = {P+T, -P-T}.
```

Hence `-P+T = -P-T` or `-P+T = P+T`.

- If `-P+T = P+T` then `-P = P`, so `2P = O` for a generic `P`, impossible.
- If `-P+T = -P-T` then `T = -T`, so `2T = O`.

(`⇐`) Suppose `2T = O`. Then `-T = T`, and

```
-(P+T) = -P - T = -P + T,
```

so `{P+T, -P+T} = {P+T, -(P+T)}` is again an `x`-fibre. The induced map on
`P^1` is regular outside a finite set and extends to an automorphism of
`P^1`.

## 2. "Any" degree-2 quotient

The same fibre argument applies to any degree-2 quotient morphism
`φ : E → C` that is Galois with deck transformation `[-1]` (i.e. any
coordinate in the `PGL_2`-orbit of `x`). Translation by `T` descends through
**every** such quotient if and only if it descends through `x`, hence if and
only if `2T = O`.

This is the precise sense in which 2-torsion — and only 2-torsion — supplies
"larger group actions" beyond `±1` on the x-line. Translations by points of
order `> 2` do not descend.

## 3. What this does not claim

- It does not give a new factor-base construction. Coset bases and torsion
  quotients remain the already-opened proposals `IDEA-20260918-c05e71` and
  `IDEA-20260918-7a11c2`.
- It does not change Gaudry/PDP cost on EcGFp5 or EcMasFp5 by itself.
- It does not assert anything about Weil descent, GHS, or oracle-assisted DH.

## 4. Lean statement (for the coordinator to mint)

See `research/THM_QUOTIENT_DESCENT1.lean`. The stub names the objects and the
biconditional; a checked proof is a separate formalization task, not part of
this intake.
