---
id: KN-LIT-ebd657
type: literature
title: Decomposition formula of the Jacobian group of plane curve (Draft)
authors: [Koh-ichi Nagao]
year: 2013
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2013/548
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2013/548
tags: [nagao, matsuo, diem, semaev, jacobian, plane-curve, riemann-roch,
  decomposition-attack, index-calculus, disjoint-factor-base,
  coset-factor-base, symmetry-breaking, factorial-yield, hyperelliptic,
  ecdlp, jacdlp, subexponential, large-characteristic, draft, unrefereed,
  joint-work, revision-note, retracted-proposition, broken-crossreference,
  priority, prior-art]
confidence: reported
citation_verified: read
frozen_source: inputs/NAGAO-2013-548/
source_record: SRC-NAGAO-2013-548
added: 2026-09-13
superseded_by: null
---

## Why this record exists

Section 7 of Nagao ePrint 2015/984 (`KN-LIT-71b758`) opens by crediting the
**disjoint factor base** to this paper and adds that Galbraith and Gebregiyorgis
ePrint 2014/806 "recently re-discovered" it. This program's mechanism-lane
hypothesis `H-SEMBIN-c59e50` was built on 2014/806 and calls coset typing that
paper's device, so whose construction it is bears on what that lane may call new.
`IDEA-20260913-352163` listed this paper as an unread pointer carrying no weight.

The paper was fetched, frozen at `inputs/NAGAO-2013-548/`
(`SRC-NAGAO-2013-548`), and read in full under `TASK-20260913-0188bf`, with
Section 7 and its footnote read in the PDF. **Page anchors below are PDF pages of
the frozen six-page file.** Note that `inputs/NAGAO-2013-548/provenance.json`
records `"pages": 2`; that field is wrong and the source record documents the
discrepancy rather than editing the immutable receipt.

## Contribution

The paper's stated subject is not factor bases at all. Abstract, page 1: "we give
an algorithm for decomposing given element of Jacobian gruop into the sum of the
decomposed factor, which consists of certain subset of the points of curve."
Sections 2–5 build that algorithm out of a Riemann–Roch space: pick `D := d∞ −
D_0`, take `H(x,y) := f_0 + A_1 f_1 + ... + A_{d−g} f_{d−g}` over a basis of
`L(D)` with the `A_i` as variables, form `S(x) := resultant_y(f, H)`, divide out
`φ_1(x) = Π_i (x − x(Q_i))`, and read off the coefficients `C_i` of the quotient
as degree-2 polynomials in the `A_i` (Lemma 1, page 2). Matching them against the
elementary symmetric functions `S_i(X_1, ..., X_d)` gives the system `EQS1`, and
Proposition 2 (page 2) states the equivalence between `EQS1` having a solution
and the divisor decomposition existing. Section 5 introduces an "absolute
resultant" to eliminate the `A_i`; Section 6 specialises to the hyperelliptic
case via Mumford representation (Lemma 6 and Proposition 4, page 4).

**Section 7, "Decomposed factor" (pages 4–5), is the part 2015/984 cites, and it
is two pages long, at the end, after the retraction.**

## The construction, exactly as frozen (Section 7, pages 4–5)

Fix a basis `[w_1, ..., w_n]` of `F_{p^n}/F_p` and positive integers `n_1, ...,
n_d` with `n_1 + ... + n_d ≈ ng`. Then:

- `B'_i := { Σ_j x_{i,j} w_j | x_{i,j} ∈ F_p }` for `i = 1, ..., d`. (The
  extraction and the PDF both print the summation's upper limit as `n_j`, which
  is evidently a typo for `n_i` — otherwise the `n_i` are never used and `|B_i| ≈
  p^{n_i}` two lines later does not follow.)
- `r_1, ..., r_d` elements of `F_{p^n}`, with **footnote 3** on page 5 supplying
  the disjointness recipe: "Take `r_{i+1} ∈ F_{p^n} \ ∪_{j=1}^i B'_j` and
  disjoint decomposed factor is constracted."
- `B_i := { P − ∞ ∈ Jac(C/F_{p^n}) | P ∈ C(F_{p^n}), ∃x ∈ B'_i such that x(P) = x
  + r_i }` for `i = 1, ..., d`.

and one then decomposes `D_0 + Σ_{i=1}^d (P_i − ∞) = 0` with `(P_i − ∞) ∈ B_i`.

This is a **coset-shifted, pairwise-disjoint family of factor bases**: `d`
distinct `F_p`-subspaces-plus-translates `B'_i + r_i` of the `x`-line, one per
summand slot, with the shifts chosen so the pieces do not overlap.

The yield accounting is stated in full on page 5, immediately after:

> "Note that `B_i`'s are essentially disjoint, `|B_i| ≈ p^{n_i}`, and the
> probability that the decomposition success is `O(p^{n_1+...+n_d−ng}) ≈ 1`. From
> the disjointness, it is improved that the term of `1/d!` in the probability is
> omitted. (Remark that it is needed to compute gaussian elimination of `d`-times
> size matrix in the last step.)"

So both halves of the trade are here: the removed `1/d!`, and the `d`-times
larger linear algebra it costs. This is the same accounting 2015/984 Section 7
uses and the same accounting `H-SEMBIN-c59e50` attributes to 2014/806.

## Key claims (as stated in the source)

| # | claim | where | status in the source |
|---|---|---|---|
| C1 | `deg_x S(x) = d + g`, `φ_1 | S`, and the coefficients `C_i` of `S/φ_1` are degree-`<= d_y` polynomials in the `A_i` | Lemma 1, page 2 | stated; the hyperelliptic restatement (Lemma 6, page 4) sharpens total degree to 2 |
| C2 | `EQS1` has a solution `(a; x_1..x_d)` **iff** there are `P_i` with `x(P_i) = x_i` and `D_0 + ΣP_i ∼ 0` | Proposition 2, page 2 | proved from Lemmas 2 and 3 |
| C3 | the `A_i` can be eliminated by an absolute-resultant construction, giving equations `H_i` in the `X_j` only | Prop. 3, page 3 | see the retraction below; footnote 2 also declares an unrepaired projective-vs-affine gap |
| C4 | **disjoint coset-shifted decomposed factors `B_i = B'_i + r_i`, "essentially disjoint", removing the `1/d!` from the success probability at the cost of a `d`-times larger final matrix** | **§7, pages 4–5, footnote 3** | **stated with a counting argument; explicitly credited to earlier work, see below** |
| C5 | JACDLP for small genus `g` over `F_{p^n}` with `log p = O((ng)^2)` is subexponential in `N = ng log p` | Proposition 5, page 5 | proof given, but it cites "Proposition ??" **twice** |

## Is it the elliptic case? — precisely

**No elliptic construction is stated separately, and the elliptic case is the
`g = 1` instance of what is stated.** Section 2 (page 1) fixes `C : f(x,y) = 0` a
plane curve of small genus `g`; Section 7's construction is for `Jac(C/F_{p^n})`
and is written with `P − ∞` throughout, which at `g = 1` is the standard
identification of an elliptic curve with its Jacobian. The words "elliptic curve"
appear in Section 7 only in its *attribution* paragraph (Diem's `log p = O(n^2)`
result, and Matsuo's 120-bit binary elliptic experiment), never in the
construction. Proposition 5's proof takes `d = ng` and `n_1 = ... = n_d = 1`,
which at `g = 1` is `d = n` slots of one `F_p`-dimension each — the same "many
summands, constant-size coset" shape 2015/984 Section 7 uses at `p = 2`.

So: the construction covers the elliptic case by specialisation, and the paper
never specialises it.

## The paper does not claim the construction as its own

This is the single most important thing in the frozen bytes for the priority
question, and it is stated twice.

Section 7's opening paragraph (page 4) credits two predecessors:

> "In 2009, Diem [2] proposes the way of taking decomposed factor, called
> Diem-variant, and shows ECDLP of elliptic curves over `F_{p^n}` satisfying
> `log p = O(n^2)` has subexponential complexity when input size `n log p` goes
> to infinity. In 2005 or 2006, soon after the Semaev's formula is discoverd,
> Matsuo also found the simmilar and more general way of taking decomposed factor
> (for exapmle distinct or non-equal size decomposed factor). Matsuo tries to
> decompose an element of elliptic curve over around 120-bit size binary field,
> but, huge memory workstation does not returns the reply and it it not presented
> and only the researchers around him knows this."

and the next paragraph (page 5) states this paper's own contribution as a
generalisation:

> "Here, we propose the way of taking decomposed factor of Jacobian of the curve,
> which is **the generalization of Matsuo's decomposed factor**."

Two consequences. First, on this source's own account the disjoint/coset factor
base **predates this paper** and is not Nagao's. Second, the specific priority
Nagao asserts is unverifiable in principle from any artifact: Matsuo's work is
described as unpublished and unpresented, "only the researchers around him knows
this". What *is* checkable from these bytes is the negative — that 2013/548 does
not claim invention.

## The retraction, and where it lands

Page 1 carries an unintegrated revision note:

> "revise 6 Nov First version of this manuscript, we use Weil descent like
> techinique and the decomposition problem of Jacobian reduces to solving exact
> `g` number equations system. However, **Proposition 3 is not true and this
> thechnique can not be used**. So, we re-write §4 and show that the
> decomposition problem of Jacobian reduces to solving some equations system
> (however, the number of the equations is quite large)."

What this does and does not touch:

- **It does not touch Section 7.** The retraction is about the equation-system
  machinery — the reduction from a divisor decomposition to polynomials — not
  about how the factor base is chosen. Section 7 is downstream of it in the
  paper's narrative and independent of it as a construction: `B_i = B'_i + r_i`
  and the `1/d!` counting argument do not use Proposition 3.
- **It does degrade what Section 7 sits on top of.** The replacement is weaker by
  the author's own parenthesis — "the number of the equations is quite large" —
  and Proposition 5, the paper's only complexity claim, is built on the rewritten
  machinery.
- **A statement numbered Proposition 3 is still printed**, on page 3 in Section 5
  (the absolute-resultant section), asserting the equivalence of `H_i(x_1..x_d) =
  0` with the divisor decomposition. Whether that is the retracted statement left
  in place, a renumbered survivor, or a new statement **cannot be determined from
  the frozen bytes**, because the first version is not frozen and ePrint serves
  only the latest PDF. The served `last-modified` is 2013-12-13, a month after
  the "6 Nov" note, so at least one further change exists that the note does not
  describe.

## Two further defects in the frozen bytes

1. **Proposition 5's proof cites `"Proposition ??"` twice** (page 5) — unresolved
   LaTeX cross-references. The two propositions the paper's only DLP-complexity
   statement depends on are therefore not named anywhere in it. One is clearly
   meant to be the decomposition equivalence and the other the Weil-descent
   degree bound, but *which* statements those are is a guess, and after a
   retraction that renumbered or replaced results, guessing is not available.
2. **Footnote 2, page 3**, on the resultant argument: "We do not use homogenious
   polynomial system and projective variety. So, there is some gap. However, it
   seems to negligible and continue the discussion." A self-declared unrepaired
   gap in the elimination step.

## Relevance to this program

- **It converts an unread pointer into a checked source for one narrow fact**:
  that a disjoint coset-shifted factor base with explicit `1/d!` removal is
  present in a 2013 Nagao preprint, at §7 pages 4–5, and that the paper credits
  the idea to Diem (2009) and Matsuo (2005/2006, unpublished) rather than
  claiming it.
- **It bears on `H-SEMBIN-c59e50`'s novelty language, narrowly.** That record
  calls the device "a PUBLISHED device: Galbraith-Gebregiyorgis 2014/806 section
  4.2 coset-typed factor bases" and lists 2014/806 as "the published device that
  removes the m!". As an account of where this program *read* the device that is
  accurate and properly provenanced (`KN-LIT-439`, verified under
  `TASK-20260913-6519c9`). As a *priority* statement it is too narrow: the
  construction and its `1/d!` accounting are in these 2013 bytes, and 2013/548
  itself points further back. What the reading does **not** do is trigger that
  hypothesis's own `novelty_status: known` condition, which requires prior work
  that already composes a typed factor base with an auxiliary-variable
  presentation *and derives the degree consequence*. Section 7 composes the coset
  family with a Weil-descent system in the **large-characteristic** Diem regime
  (`log p = O((ng)^2)`, Proposition 5) and derives a degree bound of the form
  `<= Const_1^d`; it derives no first-fall-degree consequence and says nothing
  about a chained presentation. The consequence is an attribution correction, not
  a novelty downgrade; the disposition is the top-level Coordinator's under
  `DEC-20260913-8d19e5`.
- **It is the ingredient that separates the two Nagao conclusions.** 2013/549
  (`KN-LIT-c5dceb`) reaches subexponential ECDLP/JACDLP under the first fall
  degree assumption; 2015/984 reaches polynomial from the same assumption. The
  difference is this §7 construction. Reading the pair makes 2015/984's
  Proposition 5 — the unproved affine-invariance step — the *only* new
  mathematical content between subexponential and polynomial.
- **The companion pair corroborates nothing.** 2013/548 and 2013/549 were
  received the same day, are both self-described joint work with Matsuo and
  Takagi, both carry a "6 Nov" note retracting a numbered result, and each cites
  the other.

## The priority question, stated no wider than the bytes allow

**Supported by the frozen bytes.** The last revision of ePrint 2013/548 contains,
in §7 (pages 4–5) with footnote 3, a disjoint coset-shifted factor base for
Jacobians of small-genus plane curves — the elliptic case included by
specialisation at `g = 1` — together with the explicit statement that
disjointness removes the `1/d!` yield term at the cost of a `d`-times larger
final linear algebra. The paper attributes the idea to Diem (2009) and to Matsuo
(2005 or 2006, unpublished), and describes its own construction as a
generalisation of Matsuo's.

**Not supported, and not to be inferred.** Nothing here dates §7: two earlier
revisions exist, neither is frozen, and ePrint does not serve them. Nothing here
says what Galbraith–Gebregiyorgis 2014/806 contains — it is not frozen in this
repository, no agent in this program has opened it, and it must not be
characterised from memory. Therefore nothing here supports or refutes 2015/984's
"recently re-discovered by [5]", which remains that paper's assertion. And the
Matsuo attribution is to unpublished, unpresented work, so no artifact can
confirm or refute it.

**What would settle it.** Freeze and read 2014/806 — its construction, its
section, and its own attributions — which converts "whose device is it" from an
assertion into a comparison of two read texts. If the *date* of §7 becomes
load-bearing, an earlier revision of 2013/548 would have to be recovered from
outside ePrint (a web archive or the authors), and its absence should be recorded
as an impediment rather than resolved by inference.

## What this record does not assert

That any statement in the paper is correct. That Proposition 5 is correct — its
proof depends on two propositions it fails to name. That the printed Proposition
3 is or is not the retracted one. Any claim about Galbraith–Gebregiyorgis
2014/806, Diem's 2011 preprint, Matsuo's unpublished work, or Semaev's summation
polynomials: none is frozen here and none was opened for this record. And no
change to `H-SEMBIN-c59e50`, which is another session's record and whose status
only a committed Coordinator decision may move.

## Citations

- Frozen source: `inputs/NAGAO-2013-548/` (`SRC-NAGAO-2013-548`), provenance
  `retrieved`, read in full under `TASK-20260913-0188bf`; hashes verified against
  both the `.sha256` sidecars and `provenance.json`.
- `KN-LIT-71b758` / `inputs/NAGAO-2015-984/` — the paper whose §7 credits this
  one; provenance `internal`.
- `KN-LIT-c5dceb` / `inputs/NAGAO-2013-549/` — this paper's companion, received
  the same day; provenance `retrieved`, read under the same task.
- `KN-LIT-439` — this program's record of Galbraith–Gebregiyorgis 2014/806, read
  under `TASK-20260913-6519c9`. Cited here **only** to name where this program
  read the coset device; that paper is not frozen in `inputs/` and was not opened
  for this record, so nothing about its content is asserted above.
- This paper's references [2] (Diem), [3] (Faugère–Perret–Petit–Renault), [9]
  (Semaev) and the unpublished Matsuo work are named **only** as this paper's own
  attributions. None is frozen here and none was opened; under AGENTS.md rule 9
  they are pointers and support nothing.
