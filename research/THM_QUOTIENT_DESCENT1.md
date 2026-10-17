# THM_QUOTIENT_DESCENT1 — Only 2-torsion translations descend through a degree-2 quotient of E

- **Status:** PROVED (elementary). The Lemma's group-law identity is formalized as
  `CryptoResearch.Quotient.translation_descends_iff_two_torsion`
  (`formal/CryptoResearch/Quotient/TranslationDescent.lean`, target
  `formal/targets/quotient-translation-descent.yaml`); see "Formal target" below.
  Despite its name, the theorem proves commutation with ι_S; descent follows as stated in the file header (sheriff SHF-20261017-e4d7f6 L-N9).
  Companion to `IDEA-20260920-0490f5`.
- **Closes:** the "Larger group actions?" question on Galbraith's ECC 2015 slides, for every
  x-type coordinate.
- **Reads:** none required; the proof uses only the group law. Kohel (INDOCRYPT 2012) and
  FGHR (J. Cryptology 2014) are not frozen and may already state this; until they are read
  the note claims only "formalized here", not novelty.

## Setting

Let E be an elliptic curve over a field k, char k ≠ 2. For S ∈ E(k) let
ι_S = [−1] ∘ τ_S, i.e. ι_S(P) = −P − S = −(P + S). Every ι_S is an involution of E
(as a curve, not as a group), whatever the order of S, and every degree-2 map φ: E → P^1
defined over k is the quotient by some involution of this form up to an automorphism of
P^1 (the x-coordinate is the case S = O; the x-coordinate on a translate, P ↦ x(P + R),
is the quotient by ι_{2R}).

*Correction (2026-10-16, sheriff case SHF-20261016-3caa6f, finding L2).* This paragraph
first read "For S ∈ E[2](k)", restricting the degree-2 quotients to those by ι_S with S
2-torsion. That is wrong: S may be any point of E(k). The case reader's counterexample is
φ = x(P + R) on a curve over F_1009 with R of order 3, whose involution is P ↦ −P − 2R
with 2R not 2-torsion
(`research/sheriff/SHF-20261016-3caa6f/scripts/readers/lean/descent_check.out`). The
Lemma below is unaffected: its proof never uses the order of S, and it holds for every
S ∈ E(k), as the formal statement now says.

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

## Formal target

    theorem_name: CryptoResearch.Quotient.translation_descends_iff_two_torsion
    name_note: proves commutation with ι_S; descent follows as stated in the file header (sheriff L-N9)
    statement: ∀ (S T : E), (∀ P, -(P+S)+T = -(P+T+S)) ↔ (2:ℕ)•T = 0
    file:      formal/CryptoResearch/Quotient/TranslationDescent.lean
    target:    formal/targets/quotient-translation-descent.yaml

The statement needs only the abelian-group structure of E(k̄); no scheme theory. It is
proved for any additive commutative group and is built and axiom-audited by the
`formal-workspace` job of `.github/workflows/lean-verification.yml`. It formalizes the
Lemma's computation only: that degree-2 maps are quotients by some ι_S, and that
"descends" means "commutes with ι_S", remain the prose argument above.

*History.* The target was first written as a hypothesis `2•S = 0` plus this statement,
and committed as an unchecked statement stub, `research/THM_QUOTIENT_DESCENT1.lean`, that
declared it as a Lean axiom. Sheriff finding L1 (SHF-20261016-3caa6f) flagged the stub;
it was removed on 2026-10-16 when the theorem was proved. The hypothesis on S was unused
and is dropped, so the proved statement is stronger. Records that cite the stub (for
example `ledger/handoffs/TASK-20260923-aa277e.yaml` and the EXP-GFPN-05ff43 v1→v2
amendment) describe it, correctly, as an unchecked stub; the file is in git history.
