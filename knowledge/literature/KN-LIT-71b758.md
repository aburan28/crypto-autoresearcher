---
id: KN-LIT-71b758
type: literature
title: Complexity of ECDLP under the First Fall Degree Assumption (Draft)
authors: [Koh-ichi Nagao]
year: 2015
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2015/984
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2015/984
tags: [nagao, semaev, summation-polynomial, index-calculus, characteristic-two,
  binary-field, ecdlp, first-fall-degree, fake-first-fall-degree, groebner,
  weil-descent, chained-system, disjoint-factor-base, coset-factor-base,
  symmetry-breaking, polynomial-time-claim, asymptotic-complexity, draft,
  unproven-step, contested]
confidence: reported
citation_verified: read
frozen_source: inputs/NAGAO-2015-984/
source_record: SRC-NAGAO-2015-984
supersedes: KN-LIT-456
added: 2026-09-13
superseded_by: null
---

## Why this record exists

`KN-LIT-456` has been this program's entry for this paper since 2026-07-24 and
carries no content whatsoever: "No abstract was extractable from the first two
pages of the local PDF; contribution recorded from the title only." It is a
title and nothing else, and under core rule 9 it supports nothing.

That mattered more than a routine stub, because the paper turns out to be a
direct commentary on `inputs/SEMAEV-2015-310/` — the frozen source
`GOAL-SEMBIN-5078bc` exists to audit. Its reference [14] is Semaev 2015/310; its
Lemma 1 and Propositions 2, 3 and 4 are each labelled "Semaev [14]"; and its
Section 7 modifies exactly the construction this program has been costing. It
also reaches, from the same assumption, a *qualitatively stronger* conclusion
than Semaev does — polynomial rather than subexponential — which the program had
no record of at all.

The paper was therefore fetched and read in full. It is frozen at
`inputs/NAGAO-2015-984/` (single version, received 2015-10-12, CC BY, retrieval
receipt in `provenance.json`).

`KN-LIT-456` is not corrected or rewritten. It remains the immutable record of
what this program held while the paper was unread, and points here.

## Contribution

Nagao takes Semaev's characteristic-2 chained-`S_3` algorithm and replaces its
single factor base with **m disjoint cosets**, then observes that this removes
the `1/m!` decomposition-yield penalty which is what forces Semaev to take
`m ~ n^{1/2}`. With the penalty gone the factor-base dimension `k` may be fixed
at a small *constant* `C_0` with `m ~ n/C_0`, the factor base shrinks to `O(n)`
elements, and — **under the first fall degree assumption** — the whole ECDLP
cost becomes polynomial in `n`.

The paper also does two things that are independently useful regardless of
whether Theorem 1 survives:

1. It separates the **true** first fall degree (Definition 5) from a **"Fake
   first fall degree"** taken modulo the field equations (Definition 6), states
   flatly that "many researchers misunderstand the definition of first fall
   degree" and use the fake one, and then proves (Lemmas 3 and 4) that
   `d_F <= d'_F`, so the fake version is a valid *upper* bound and the
   misunderstanding is safe in the direction it is usually used.
2. It generalises the degree bound off characteristic 2: the first fall degree of
   the descended system is `<= 3p + 1` for `p >= 3` (Proposition 2, via Lemma 6),
   with Semaev's `<= 4` at `p = 2` an exceptional case rather than the pattern.

## Key claims (as stated in the source)

| # | claim | where | status in the source |
|---|---|---|---|
| C1 | `d_F({F↓_j} ∪ S_fe) <= (p-1)n + deg F` for a Weil descent | Lemma 6 | proved, with "we use heuristic argument only here" in its own footnote 4 |
| C2 | `d_F(EQS2) <= 4` (p = 2), `<= 3p+1` (p >= 3) | Prop. 2 | proved from Lemma 6; the `p = 2` half is attributed to Semaev |
| C3 | disjoint cosets make decomposition success `O(1)` rather than `1/m!` | §7 | counting argument, `∏_i #Fb_i ~ p^n ~ #E(F_{p^n})` |
| C4 | `d_F(EQS4) <= 4` (p = 2) — the same bound **after the coset shift** | Prop. 5 | **PROOF OMITTED**: "The situation is the same as the Semaev's case. So, we omit the proof" (footnote 6) |
| C5 | ECDLP over `F_{2^n}` is `O(n^{8w+1})`; over `F_{p^n}` is `O(n^{(6p+2)w+1})` | Thm. 1 | follows from C3 + C4 + Lemma 2, under Assumption 1 |

## Where the weight sits

**C4 is the load-bearing unproven step.** Everything else is bookkeeping around
it. The coset shift is precisely what changes the descended system: substituting
`X_i = v_i + Σ_j X_ij α_j` instead of `X_i = Σ_j X_ij α_j` makes the Weil
descent *affine* rather than linear, and the paper's own footnote 1 flags that
"the values `v_1, ..., v_N` must be needed" in the descent definition for this
reason. Whether the first-fall-degree bound is invariant under that shift is the
whole question, and it is asserted rather than argued.

**Assumption 1 is applied at a variable count no one has tested.** The paper's
Assumption 1 (its own numbering) says the degree occurring in the F4 computation
is `<= d_F`. Semaev applies it at `N ~ (m-2)n ~ n^{3/2}` Boolean variables;
Nagao applies it at `N = n(m-1) ~ n^2/C_0`, since `m ~ n/C_0`. The polynomial
conclusion comes entirely from holding a *constant* degree bound while the
variable count grows quadratically. Semaev's own Section 4.4 records that `d_F4`
generally exceeds 4 once `k > ⌈n/m⌉`, and `KN-LIT-e77232` records Kosters
reaching degree 5 at `n = 45`.

**The paper says its own constants are bad, in capitals.** Section 6: "we adopt
the easy and rough estimation ... Many complicated terms are included into the
`o(1)` term and so for normal size input `n`, `o(1)` has HUGE value although
`lim_{n→∞} o(1) = 0`." So `O(n^{8w+1})` being polynomial does not by itself say
anything about any concrete curve, and the paper offers no table, no timing, and
no measurement of any kind — eight pages, zero data points.

## Relevance to this program

- It is the **prior art for the mechanism lane's central idea.** This program's
  coset-typed-factor-base hypothesis, built on Galbraith–Gebregiyorgis
  2014/806, is a composition Nagao published in 2015: disjoint cosets applied to
  Semaev's chained `S_3` system, with the `m!` removal as the stated point.
  Section 7's opening sentence even credits the idea to the author's own earlier
  2013/548 and says 2014/806 "re-discovered" it. Any novelty claim in that lane
  has to be stated against this record.
- It supplies a **falsifiable, cheap, and unowned audit target**: Proposition 5.
  The affine-invariance question is exactly the one this program's mechanism lane
  needs answered, it is answerable at small `n` by degree-4 Macaulay rank rather
  than a full Gröbner run, and a *failure* is as useful as a success because the
  paper's Theorem 1 has no other support.
- It makes the program's own citations of "the first fall degree assumption"
  **ambiguous in a checkable way.** `GOAL-DREG-001` measures a
  first-fall-degree quantity and `GOAL-SEMBIN-5078bc` cites Semaev's
  Assumption 1 throughout. Definitions 5 and 6 are different quantities. Which
  one each of those records means has not been checked.
- Its `p >= 3` extension (`d_F <= 3p+1`) is a **prime-field prediction** the
  program can use as a nearby-object control for characteristic-2 claims,
  independent of whether Theorem 1 holds.

## What this record does not assert

That Theorem 1 is true, that the first fall degree assumption holds at
`N ~ n^2`, or that Proposition 5 is correct. It also does not assert Nagao's
priority over Galbraith–Gebregiyorgis: 2013/548 and 2014/806 are not frozen
here, so §7's priority sentence is recorded as this paper's assertion and is
unchecked. No concrete cost is quoted above, because the source contains none.

## Citations

- Frozen source: `inputs/NAGAO-2015-984/` (`SRC-NAGAO-2015-984`), provenance
  `retrieved`, read in full by this session.
- `KN-LIT-fa346d` / `inputs/SEMAEV-2015-310/` — the paper this one comments on,
  provenance `internal`.
- `KN-LIT-e77232` — the ellipticnews/ePrint dispute over Semaev 2015/310,
  provenance `internal`. Postdates neither: this paper was received six months
  after that thread and does not cite it.
- Nagao ePrint 2013/548 (disjoint factor base) and 2013/549 (Weil-descent
  equation systems, source of Lemmas 3 and 5) are cited *by* this paper as
  references [10] and [11] and are **not** frozen here; provenance for both is
  `recalled` and neither may support a decision until read.
- Galbraith and Gebregiyorgis ePrint 2014/806 is this paper's reference [5].
