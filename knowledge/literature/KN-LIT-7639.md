---
id: KN-LIT-7639
type: literature
title: "Character sums over AG codes"
authors:
  - "Swastik Kopparty"
  - "Amnon Ta-Shma"
  - "Kedem Yakirevitch"
year: 2024
venue: "Electronic Colloquium on Computational Complexity (ECCC), Report No. 69"
identifiers:
  eprint: "ECCC TR24-069"
  doi: null
  arxiv: null
  url: "https://eccc.weizmann.ac.il/report/2024/069/"
tags: [character-sums, weil-bound, bombieri, algebraic-curves, function-fields, ecdlp, stepanov]
confidence: reported
citation_verified: read
added: "2026-08-02"
superseded_by: null
---

## Why this entry exists

Discharges — **partially, and the partiality is the point** — hypothesis
**(H1)** of `analysis/o2-sum-compatible-filters/O2_derivation_attempt.md` §7.5,
which that document flagged as *"Not re-verified by literature search in this
session"* under `AGENTS.md` rule 9, and which
`O2_composition_closure.md` §5.4 records as now **gating a headline closure**
(the `j = 2` four-tree). (H1) as stated there:

> Weil/Bombieri bound for multiplicative character sums on a smooth projective
> curve of genus `g` over `F_p`: `|Σ_P χ(F(P))| ≤ (2g−2+2m)√p` with `m` the
> number of distinct zeros and poles of `F`, valid when `F` is not a constant
> times a `k`-th power in `\bar F_p(C)`.

## Contribution

Strengthens the Stepanov–Bombieri approach to obtain non-trivial character-sum
bias bounds on **high**-genus curves (Hermitian function field, first levels of
the Hermitian tower), where the classical Weil machinery gives nothing. The
technical engine is a "universal derivative-fix" lemma (their Theorem 1.1)
relating pole divisors of Hasse derivatives in a function field.

The high-genus result is *not* what this program needs. What this program needs
is the **small-genus statement the paper recalls as classical**, which it states
explicitly in order to contrast it.

## Key claims (as reported)

- **§1, p.2 — the statement (H1) needs.** "For curves of small genus `g ≪ √q`,
  the Weil bounds themselves (along with related facts about the zeta functions
  of curves) do give such a bound. They imply that for any algebraic curve `C`
  of genus `g` contained in the plane, and any polynomial `f(X,Y)` of degree
  `d`, **unless `f` is the square of an algebraic function over `C`**, we have
  `Pr_{(x,y)∈C(F_q)}[f(x,y) is a perfect square in F_q] = 1/2 + O_{g,d}(1/√q)`."
- **§1, p.2 — the regime boundary.** "For large `g` (which is the case for the
  Hermitian and Garcia-Stichtenoth towers), however, the original Weil bound
  machine does not say anything."
- **§1, p.1 — the `g = 0` case, general character order.** The classical Weil
  bound for a polynomial `f` of degree `d` that is not a perfect power:
  `Pr_{x∈F_q}[f(x) is a perfect square] = 1/2 + O(d/√q)`.
- Attributes the curve-level generalisation of Weil's method to Bombieri's
  systematic Artin–Schreier-covering treatment.

## What this verifies for (H1), and what it does not

**Verified.**

1. **The bound exists in the form (H1) asserts**, with error `O(q^{-1/2})` and
   an implied constant depending on the **genus** and the **degree** — matching
   [D]'s `c₁·D` shape, where `D` is its divisor-complexity parameter.
2. **The non-degeneracy hypothesis is the right one.** "Unless `f` is the square
   of an algebraic function over `C`" is exactly (H1)'s "not a constant times a
   `k`-th power in `\bar F_p(C)`", at `k = 2`. [D]'s Lemma 7.2 Case-B branch,
   which handles precisely this degeneracy, is therefore addressing a real
   hypothesis and not a phantom.
3. **The regime is satisfied, with enormous margin.** The bound is stated as
   valid for `g ≪ √q`. This program's curve is `E/F_p`, an **elliptic** curve,
   so `g = 1` and `q = p`. At cryptographic `p` (256-bit) the condition
   `1 ≪ 2^{128}` is not close to binding. The paper's own warning — that the
   machinery says nothing at large genus — **does not touch this application**.
   Recording this explicitly because it is the one way (H1) could have been
   quietly inapplicable.

**Not verified, and still owed.**

1. **The explicit constant `(2g−2+2m)`.** This source gives `O_{g,d}(·)` and does
   not state [D]'s exact constant. Bombieri's original 1966 paper was **not**
   obtained. [D] §7.5 (H3) separately admits its own zero/pole count for `F_R`
   is asserted as `O(D)` rather than carried out, so the constant is unverified
   on **both** sides. This affects `c₁` — not the `p^{-1/2}` shape on which the
   closure rests.
2. **General character order `k > 2` on a curve.** This source's curve statement
   is quadratic (`perfect square`). The general-`k` statement was verified only
   in the `g = 0` polynomial case via secondary sources. F1 family C (quadratic
   characters) is therefore covered; **family D (cubic, quartic, octic residue
   characters, `k = 3,4,8`) is not covered by this entry** and needs either
   Bombieri's original or Perel'muter.
3. **Perel'muter** was searched for and no primary statement was retrieved.

## Relevance to this program

`O2_composition_closure.md` closes the `j = 2` Wagner four-tree by substituting
[D]'s Weil bound into [F]'s Theorem A. That closure is **conditional on (H1)**.
This entry moves (H1) from *entirely unverified* to *form, hypothesis and
validity regime verified from a current source, exact constant still untraced,
`k > 2` on curves still untraced*.

The closure's dependence is on the **shape** `Λ = O(D·p^{-1/2})`, which is
verified here, not on the constant, which is not. Independently,
`charfilter_decay.py` measures `Λ ~ p^{-0.457..-0.496}` on F1 family C over a
125× range in `p`, consistent with this bound on the class it governs.

## Not verified here

Bombieri's 1966 original text; the explicit `(2g−2+2m)` constant; general `k` on
curves of genus 1; Perel'muter's statement; and the paper's own high-genus
results, which are irrelevant to this program and were not assessed.
