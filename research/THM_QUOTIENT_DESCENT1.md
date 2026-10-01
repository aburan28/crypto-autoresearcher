# THM_QUOTIENT_DESCENT1 — Only 2-torsion translations descend through a degree-2 quotient of E

- **Status:** PROVED (elementary); not yet formalized. Companion to `IDEA-20260920-0490f5`.
- **Closes:** the "Larger group actions?" question on Galbraith's ECC 2015 slides, for every
  x-type coordinate.
- **Reads:** none required; the proof uses only the group law. Kohel (INDOCRYPT 2012) and
  FGHR (J. Cryptology 2014) are not frozen and may already state this; until they are read
  the note claims only "formalized here", not novelty.

## Setting

Let E be an elliptic curve over a field k, char k ≠ 2. For S ∈ E[2](k) let
ι_S = [−1] ∘ τ_S, i.e. ι_S(P) = −P − S = −(P + S). Every ι_S is an involution of E
(as a curve, not as a group), and every degree-2 map φ: E → P^1 defined over k is the
quotient by some involution of this form up to an automorphism of P^1 (the x-coordinate is
the case S = O; the "x-coordinate on the translate" is the general case).

Write τ_T for translation by T ∈ E(k̄).

## Lemma

τ_T descends through φ = E/⟨ι_S⟩ — i.e. there is a map ψ: P^1 → P^1 with φ ∘ τ_T = ψ ∘ φ —
**if and only if 2T = O.**

## Proof

τ_T descends through the quotient by ι_S iff τ_T permutes the fibres of φ, iff
τ_T ∘ ι_S = ι_S ∘ τ_T (for a degree-2 quotient the fibre of P is {P, ι_S P}, so
"permutes fibres" is exactly "commutes with ι_S"). Compute both sides on P:

    τ_T ∘ ι_S (P) = −(P + S) + T
    ι_S ∘ τ_T (P) = −(P + T + S) = −P − T − S

Equal for all P iff −S + T = −T − S iff 2T = O. ∎

## Corollary (acting group for x-type summation polynomials)

Let f_m be any summation-type polynomial built on φ-values (f_m(φ(P_1),…,φ(P_m)) = 0 iff
Σ ±P_i ∈ {O} up to the fibre ambiguity). The group of translations acting on solutions
of f_m is E[2](k)^{m} ∩ {Σ T_i = O}, of order at most 4^{m−1} when full 2-torsion is
rational, so the full symmetry group from translations and permutations is a subgroup of
E[2](k)^{m−1} ⋊ S_m, order ≤ 4^{m−1}·m!. In particular:

- rational 2-torsion of rank 1 (double-odd curves, Montgomery form): (Z/2)^{m−1} ⋊ S_m;
- full rational 2-torsion: (Z/2)^{2(m−1)} ⋊ S_m;
- no rational 2-torsion (prime-order curves such as EcMasFp5): S_m only.

Anything larger — the (Z/4)^{m−1} of FGHR for curves with a rational 4-torsion point — must
come from a quotient of degree > 2, or from a curve automorphism, not from a translation
acting on a degree-2 coordinate. The trade this forces (higher quotient degree ⇒ higher
summation-polynomial degree) is what `IDEA-20260918-7a11c2` measures.

## Sage check (to run before minting the formal target)

    p = 1009; F = GF(p)
    E = EllipticCurve(F, [0, 2, 0, 5, 0])      # y^2 = x(x^2 + 2x + 5), T2 = (0,0)
    T2 = E(0, 0)
    P = E.random_point()
    assert (-(P + T2)).xy()[0] == (-P + T2).xy()[0]      # 2-torsion: commutes on x
    # pick T of order 3 (if present) and check the x-coordinates differ
    T3 = [Q for Q in E.torsion_subgroup() if Q.order() == 3]  # may be empty for this curve

## Formal target (for the Coordinator to mint)

    theorem_name: CryptoResearch.Quotient.translation_descends_iff_two_torsion
    statement: ∀ (S T : E), 2•S = 0 → ((∀ P, -(P+S)+T = -(P+T+S)) ↔ 2•T = 0)

The statement needs only the abelian-group structure of E(k̄); no scheme theory.
