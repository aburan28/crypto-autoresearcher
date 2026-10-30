#set page(margin: 1.6cm, numbering: "1")
#set text(font: "Liberation Sans", size: 9pt)
#show raw: set text(font: "Liberation Sans")
#set par(justify: true)
= Lean `decide` certificate for the Nagao 2015/984 Lemma 4 counterexample
2026-10-29. Source finding `KN-FIND-936151` (write-once, not edited). Full text: `report.md`.

*Scope.* A kernel-checked finite computation over F₂, N ≤ 3. It asserts nothing about Nagao's Proposition 5, Semaev's Assumption 1, p ≥ 3, N > 3, the literal >= reading of condition (1), or any elliptic curve. It is no stronger than the Python certificates it mirrors (`tools/lemma4_inside_form.py`, `recheck.py`).

#figure(image("diagram.svg", width: 100%), caption: [What is proved (green), assumed (dashed), and mirrored.])

*Theorem.* Equality reading of condition (1), field equations Xᵢ² + Xᵢ as generators of the true system (inside form), d\_F(S) ≤ d'\_F(S) for S = {f₁, f₂} ∪ S\_fe:

#table(columns: 5, [witness], [ring], [f₁, f₂], [d'\_F / d\_F], [Lean theorem],
 [A], [F₂[X,Y]], [X²Y, XY + X], [2 / 3], [`lemma4_inside_false_A`],
 [B], [F₂[X₁,X₂,X₃]], [X₁X₂ + X₃, X₁X₃ + X₂], [2 / 3], [`lemma4_inside_false_B`])

Corollary `lemma4_inside_false`. All goals by `decide +kernel`; axioms: propext, Classical.choice, Quot.sound. Receipt `verification.json`: machine\_verified, semantic review pending.

*Hypothesis-delta table* (declaration `lemma4_inside_false`):
#table(columns: (3fr, 2fr, 3fr), [binder / side condition], [claim states it?], [status],
 [`Poly` = exponent-vector list, odd multiplicities], [over F₂], [implied (no bridge to `MvPolynomial`)],
 [equality reading of cond. (1)], [finding §3], [implied; `>=` reading out of scope],
 [cofactors: degree ≤ D, multilinear if fake], [no], [*scoping*: leading-form argument not in Lean],
 [fake side drops generators reducing to 0], [finding §2], [*scoping*: only Xᵢ²+Xᵢ → 0 checked],
 [`FirstFall` over D ≥ 1, sum ≠ 0], [Defs 5/6], [implied])

Two `scoping` rows cap fidelity at _partial_. Unformalized step (`proof_map.prerequisites`): the transcription of Nagao's Definitions 5/6 into the finite model. Not added: independence from the chosen definitions, the outside form, any consumer's instances.
