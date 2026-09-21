---
id: KN-LIT-c5dceb
type: literature
title: >-
  Equations System coming from Weil descent and subexponential attack for
  algebraic curve cryptosystem (Draft)
authors: [Koh-ichi Nagao]
year: 2013
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2013/549
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2013/549
tags: [nagao, semaev, weil-descent, first-fall-degree, fake-first-fall-degree,
  field-equations, groebner, f4, index-calculus, decomposition-attack,
  characteristic-two, small-characteristic, jacobian, ecdlp, jacdlp,
  subexponential, weight-theory, macaulay, draft, unrefereed, joint-work,
  revision-note, retracted-lemma, numbering-gap, prior-art]
confidence: reported
citation_verified: read
frozen_source: inputs/NAGAO-2013-549/
source_record: SRC-NAGAO-2013-549
added: 2026-09-13
superseded_by: null
---

## Why this record exists

Nagao ePrint 2015/984 (`KN-LIT-71b758`, frozen at `inputs/NAGAO-2015-984/`)
claims ECDLP over `F_{2^n}` in `O(n^{8w+1})` — polynomial — under the first fall
degree assumption. Two of its lemmas are not proved there. Its **Lemma 3** is
attributed to this paper with the proof declined outright ("Proof of this Lemma
is complicated and not constructive"), and its **Lemma 5** is likewise "also the
author's result in [11]". Lemma 3 is what licenses replacing the *true* first
fall degree `d_F` (2015/984 Definition 5) with the *fake* one `d'_F` taken modulo
the field equations (Definition 6) — and `d'_F` is the only one of the two a
Macaulay-rank computation can produce. So an instrument this program is designing
rests on a lemma whose only published proof is here, and which no agent in this
program had opened. `IDEA-20260913-352163` recorded that as a disclosed
limitation with the pointer unread.

The paper was fetched, frozen at `inputs/NAGAO-2013-549/`
(`SRC-NAGAO-2013-549`), and read in full under `TASK-20260913-0188bf`. Every
statement quoted below was re-read in the PDF, because the extraction is poor
(overset-arrow vectors emitted as standalone lines). **Page anchors below are
PDF pages of the frozen nine-page file**, counted with `pdfminer`. Note that
`inputs/NAGAO-2013-549/provenance.json` records `"pages": 2`; that field is
wrong and the source record documents the discrepancy rather than editing the
immutable receipt.

## Contribution

The paper revises Petit–Quisquater-style first-fall-degree estimates for the
polynomial systems that come out of Weil descent, and concludes — **under its own
Assumption 1** — that both ECDLP over `F_{p^n}` for small `p` and JACDLP for a
small-constant-genus plane curve over `F_{p^n}` cost `O(exp(n^{2/3+o(1)}))`
(Theorems 1 and 2, page 8), at `d = O(n^{1/3})`, `n_0 = O(n^{2/3})`.

The machinery is in two layers:

- **Section 2 (page 3–5): a rewriting lemma about the field-equation ideal.**
  This is the layer 2015/984 borrows.
- **Section 3 (pages 5–7): "Weight Theory and precise estimation of first fall
  degree".** A `p`-adic digit-sum weight `wt(e) = sum_k e_k` is attached to
  exponents (Definition 2, page 5), the degree of a Weil-descended monomial is
  shown to equal its weight (Lemma 3, page 5), and a multiplier is inserted to
  pin the descended components' degrees exactly (Lemmas 4–8, page 6). The
  section's output is **Proposition 1 (page 7)**: the first fall degree of
  `{[F_0]#_k | k = 1..n} ∪ S_fe` is `<= (p-1)d·α + 1`, with `α ~ log_p(2^d)`.

Section 4 (pages 7–8) then costs the Weil-descent computation itself (Lemmas
11–13) and assembles the theorems.

## Key claims (as stated in the source)

| # | claim | where | status in the source |
|---|---|---|---|
| C1 | If `F = Σ_i G_i(X_i^p − X_i)` and `D := deg F`, then there exist `G'_1..G'_N` with `F = Σ_i G'_i(X_i^p − X_i)` and `deg G'_i <= D − p` for all `i` | **Lemma 2, page 4** | **proved, pages 4–5**, by descent on the leading monomial |
| C2 | `deg(wd(m)) = Σ_i wt(e_i)` for a global monomial `m = Π X_i^{e_i}` with `0 <= e_i <= p^{n_0−1}` | Lemma 3, page 5 | proved, via the invertibility of `M = (w_j^{p^{i−1}})` (Assumption 2, page 5) |
| C3 | `wt(p^α − 1) = (p−1)α`, and `wt(x) < (p−1)α` for every other `x <= 2p^α − p^{α−1} − 2` | Lemma 5, page 6 | "Proof. trivial." |
| C4 | The multiplied system `{[m_0·F]#_i = 0} ∪ S_fe` has the same solutions as `{[F]#_i = 0} ∪ S_fe` | Lemma 6, page 6 | stated; rests on `τ` lying outside the base subspace |
| C5 | `[m_1·F_0]#_k ≡ Σ_{i=1}^n [w_i·m_1]#_k [F_0]#_i mod S_fe` | **Lemma 9, page 7** | **proved**, a two-line bilinearity computation |
| C6 | first fall degree of `{[F_0]#_k} ∪ S_fe` is `<= (p−1)dα + 1` | Proposition 1, page 7 | assembled from C1, C2, C5 and Lemmas 7–8 |
| C7 | ECDLP over `F_{p^n}` and JACDLP for small genus are `O(exp(n^{2/3+o(1)}))` | Theorems 1–2, page 8 | **conditional on Assumption 1** (page 3) |

**C1 is 2015/984's Lemma 3 and C5 is 2015/984's Lemma 5.** The correspondence is
a renaming and nothing more: C1's `G`/`D` are 2015/984's `f`/`deg F`, and C5's
basis `{w_i}` and polynomials `m_1`, `F_0` are 2015/984's `{α_i}`, `m`, `F`. Both
statements are present here **with proofs**.

## What C1's proof actually is, and why "not constructive" is the right word for
## the wrong reason

The proof (pages 4–5) fixes a degree-compatible monomial order, considers the set
`G` of all coefficient tuples representing `F`, and for each tuple defines
`ψ(G)` as the largest of the `LM(G_i X_i^p)` and `IND(G)`/`NUM(G)` as the set and
count of indices attaining it. Then:

- If `NUM(G) = 1`, no cancellation occurs at the top, so `D = deg F = deg ψ(G) >=
  p + deg LM(G_i)` and the bound `deg G_i <= D − p` is immediate.
- If `NUM(G) > 1` and `deg ψ(G) > D`, an explicit `G^new` is constructed with
  `ψ(G^new) < ψ(G)`, and the lemma follows by induction on `ψ(G)` (well-founded,
  since a monomial order is a well-order).

This is a **complete argument and a constructive one in the logical sense** — the
descent exhibits the rewritten tuple. Two blemishes, both notational rather than
structural:

1. The remaining case `NUM(G) > 1` with `deg ψ(G) <= D` is not spelled out. It is
   immediate (`deg(G_i X_i^p) <= D` for every `i` gives the bound directly), but
   the printed case analysis does not state it.
2. Step 1) of the construction is printed as `X_{I_1}^p | G_{I_i}`, divisibility
   of the whole polynomial. Only `X_{I_1}^p | LT(G_{I_i})` follows from
   `LM(G_{I_1}X_{I_1}^p) = LM(G_{I_i}X_{I_i}^p)`, and only that is used — the
   construction divides `LT(G_{I_i})` by `X_{I_1}^p` and nothing else. So the
   printed claim is stronger than what holds and stronger than what is needed.
   Relatedly, the sentence defining the notation reads "let `LM(H)` (resp.
   `LM(H)`) be the leading term (resp. leading monomial)", i.e. `LT` is printed
   as `LM`.

**Where "not constructive" comes from is a different sentence, and it is this
paper's own.** Page 5, immediately after Lemma 2: "when `deg f ~
exp(n^{1/3+O(1)})`, computation of such `G'_i` is very difficult and its
complexity (using direct computation) seems to be exponential of `n`, although
computation of `wd(f)` is subexponential." So the non-constructivity 2015/984
reports is about the **cost of producing the witnesses**, not about the existence
proof. That distinction is decisive for anything that only needs the bound.

## Directions of the inequalities, and what 2013/549 does *not* say

Every inequality in the paper that bears on this question points the same way and
none of them is `d_F <= d'_F`:

- C1 bounds the **rewritten coefficients**: `deg G'_i <= D − p`. At `p = 2` that
  is `deg G'_i <= D − 2`.
- C6 bounds the **first fall degree from above**: `<= (p−1)dα + 1`.
- Lemma 1 (page 3) bounds the **Gröbner cost from above**: `<=
  O(N^{D_ff·C+O(1)})`.

**The inequality `d_F <= d'_F` does not appear in this paper, in either
direction.** It cannot: 2013/549 predates the true/fake distinction and works
with a single notion — Definition 1 (page 3), attributed to Petit et al., with no
field-equation reduction in it. The true/fake split is 2015/984's Definitions 5
and 6, and the inequality between them is 2015/984's **Lemma 4**, which that
paper states immediately after Lemma 3 with **no proof printed at all**.

So the dependency structure is:

> 2013/549 Lemma 2 (proved here) → 2015/984 Lemma 3 (borrowed) → 2015/984 Lemma 4
> `d_F <= d'_F` (asserted there, unproved) → the fake-degree substitution.

C1 is the load-bearing *ingredient* for that direction — turning "the excess
vanishes mod `S_fe`" into "the excess is a degree-controlled combination of field
equations" is exactly the step the inequality needs — but the assembled
inequality itself is only in 2015/984, and only as a statement.

## The revision note, and what it does to the machinery

Page 1 carries **two** unintegrated revision notes, both already folded into the
single frozen version.

**"Revise 6 NOV."** Section 3's multiplier was a pure monomial `m_0 = Π_i
X_i^{p^α−1−E_i}`. The note says plainly that the required property fails for it:
"For our aim, the solution of the equations system `{[m_0 F]#_i = 0} ∪ S_fe` must
equals to `{[F]#_i = 0} ∪ S_fe`. However, it is not true." The repair takes `τ ∈
F_{p^n} \ {Σ x_i w_i | x_i ∈ F_p}` and replaces the multiplier by the
**polynomial** `Π_i (X_i − τ)^{p^α−1−E_i}` — the note's own parenthesis: "(not
monomial but polynomial)" — and asserts "we have this property and all lemmas
still hold."

Three things follow, and they should be kept apart:

- **The repair is in the body.** Page 6 defines `m_0 := Π_i (X_i −
  τ)^{p^α−1−E_i}`, and Lemma 6 (page 6) is precisely the solution-set equality
  the note says the monomial version lacked. So the frozen text *is* the repaired
  version; the note explains a change already made.
- **The repair does not touch C1.** Lemma 2 lives in Section 2, is a statement
  about the field-equation ideal alone, and mentions neither `m_0`, nor `τ`, nor
  Section 3. The lemma 2015/984 borrows is upstream of the repair. What the
  repair touches is Section 3's weight bookkeeping, where `m_0` is now a
  polynomial and the arguments of Lemmas 7–8 must range over `Mon(m_0)` rather
  than over a single monomial — which, as printed on page 6, they do.
- **"All lemmas still hold" is the author's assertion and was not verified
  here.** Section 3's arguments read as internally consistent with a polynomial
  `m_0`, but checking them is a separate task and this record does not claim it
  was done.

**"Revise 9/8."** "Lemma 9 of the first version of this manuscript is false and I
delete the content of §4 and related footnote." The note adds that "this revise
does not influence our theorems". The frozen text bears a matching scar: **there
is no Lemma 10 anywhere.** Lemma 9 (page 7) is followed directly by Lemma 11
(page 7). The numbering is consistent with a deletion and renumbering.

That matters for one specific reason. **2015/984's Lemma 5 is this paper's
current Lemma 9** — the same number as the statement the author declares false in
the first version. The current Lemma 9 (C5 above) is proved here in two lines and
there is no reason to doubt it. But *whether the retracted first-version Lemma 9
is the same statement* cannot be determined from the frozen bytes, because the
first version is not frozen and ePrint serves only the latest PDF.

**Is the frozen version the one 2015/984 cites?** Not settleable from these bytes
alone, and the honest answer is a strong inference rather than a fact. The
landing page records the last revision as 2013-11-05 and no later one; the served
`last-modified` matches; 2015/984 was received 2015-10-12, nearly two years
after. So these bytes are the only version ePrint was serving when 2015/984 was
written. That is an inference about what was *available*, not about what the
author had in hand, and 2015/984's reference [11] gives only the bare URL with no
version or date.

## Things in this paper that bear on claims elsewhere in this program

1. **Nagao says the first fall degree assumption has counterexamples.** Page 3,
   in the paragraph after his Assumption 1: "This assumption has some counter
   examples and Petit et al. assume that the polynomials `f_1, ..., f_l` are
   general polynomials. However, if `f_1, ..., f_l` are randomly chosen, the
   value of `D_ff` seems to be very large. In our situation, we treat only the
   cases that `D_ff ~ max_i deg f_i` and so, `f_1, ..., f_l` cannot be randomly
   chosen." The author of the polynomial-time claim states on the record that the
   assumption it rests on has counterexamples, and that his systems are
   *deliberately* outside the genericity hypothesis under which it is assumed.

2. **He proposes a stronger definition and says he cannot discharge it.** Same
   page: for any invertible `l × l` matrix `M` he sets `(f^{(M)}_i) := M(f_i)`,
   defines `D_ff(M)` for the transformed system, and puts `D_ff := max_M
   D_ff(M)`, remarking that the assumption "seems to be true" for this version.
   Then: "However, by using this new assumption, I can not prove that the
   equations system coming from Weil descent have low first fall degree in strict
   way and it remains a future work." This is carried forward as
   `KN-OPEN-7f0511`.

3. **His Assumption 1 carries a `+ O(1)` that 2015/984's does not.** Here (page
   3): "Upper bound of the degree of the polynomial for computing Gröbner basis
   of `f_1, ..., f_l` of F4 algorithm is `D_ff + O(1)`", and Lemma 1 charges
   `O(N^{D_ff·C+O(1)})`. 2015/984's Assumption 1 reads "is `<= d_F`" and its
   Lemma 2 charges `O(N^{d_F w})`. Against a subexponential target the slack is
   invisible. Against a claim that *names* a polynomial exponent it is not: under
   this paper's version the exponent in 2015/984's Theorem 1 would be `8w + 1 +
   O(1)` with the `O(1)` unspecified, so the assumption as the cited predecessor
   states it does not determine the exponent the later paper reports.

4. **It is the weaker-conclusion half of one author's programme.** Subexponential
   here (Theorems 1–2), polynomial in 2015/984, from the same assumption; the
   difference is the disjoint factor base of 2013/548 (`KN-LIT-ebd657`). The two
   2013 papers were received the same day, are both self-described joint work with
   Matsuo and Takagi, and each cites the other — so agreement between them
   corroborates nothing.

5. **It says the result is not practical.** Page 2: "although its complexity is
   subexponential, the practical computation, especially in cases of `p > 2` or
   `g >= 2`, is difficult and it is only a result of the complexity."

## Relevance to this program

- **It discharges the existence half of the Lemma 3 dependency.** The statement
  2015/984 declines to prove is here as Lemma 2 (page 4) with a complete proof
  (pages 4–5). An instrument that needs only the *bound* — that a fake first fall
  at degree `d'` implies a true one at degree `<= d'` — is not harmed by the
  non-constructivity, because the non-constructivity is about computing witnesses
  and the instrument does not compute them.
- **It leaves the assembled inequality undischarged.** `d_F <= d'_F` is not here.
  It is 2015/984's Lemma 4, printed without proof. Anything relying on that
  direction is relying on a one-line unproved lemma of the 2015 paper plus a
  proved rewriting lemma of this one — which is a better position than before the
  read, and not the same as a proof.
- **It sharpens, and does not resolve, the definitional question.** The corpus now
  holds three inequivalent first-fall-degree definitions across two Nagao papers:
  Definition 1 here (Petit-style, no field equations), `D_ff := max_M D_ff(M)`
  here (page 3, undischarged for descent systems), and the true/fake pair of
  2015/984. Which one a degree-4 GF(2) Macaulay rank bounds is a checkable and
  unchecked question; see `KN-OPEN-7f0511` and, for the separate Semaev-side
  version of the problem, `KN-OPEN-d218ec`.

## What this record does not assert

That Lemma 2, Proposition 1, Theorem 1 or Theorem 2 is correct — the proofs were
read for presence and structure, not certified, and this reading was not an
independent adversarial review. That "all lemmas still hold" after the 6 NOV
repair, which is the author's assertion and unchecked here. That the frozen bytes
are the bytes 2015/984 read; that is an inference from the recorded revision
history, and the earlier revision is not obtainable. That the retracted
first-version Lemma 9 is or is not the statement 2015/984 borrows as its Lemma 5.
And nothing at all about Galbraith–Gebregiyorgis 2014/806, Semaev's summation
polynomial paper, Faugère et al., or Petit–Quisquater: none of them is frozen in
this repository and none was opened for this record.

## Citations

- Frozen source: `inputs/NAGAO-2013-549/` (`SRC-NAGAO-2013-549`), provenance
  `retrieved`, read in full under `TASK-20260913-0188bf`; hashes verified against
  both the `.sha256` sidecars and `provenance.json`.
- `KN-LIT-71b758` / `inputs/NAGAO-2015-984/` — the paper that cites this one as
  [11] for its Lemmas 3 and 5; provenance `internal`.
- `KN-LIT-ebd657` / `inputs/NAGAO-2013-548/` — this paper's companion and its
  reference [6]; provenance `retrieved`, read under the same task.
- `KN-OPEN-7f0511` — the open problem this paper's page-3 remark opens;
  provenance `internal`.
- `KN-OPEN-d218ec` — the adjacent, distinct Semaev-side definitional problem;
  provenance `internal`.
- This paper's references [2] (Faugère–Perret–Petit–Renault), [7]
  (Petit–Quisquater) and [8] (Semaev) are named here **only** as this paper's
  own bibliography. None is frozen in this repository and none was opened; they
  are pointers under AGENTS.md rule 9 and support nothing.
