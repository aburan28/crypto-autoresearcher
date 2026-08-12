---
id: KN-LIT-7607
type: literature
title: "Last fall degree, HFE, and Weil descent attacks on ECDLP"
authors:
  - "Huang, Ming-Deh A."
  - "Kosters, Michiel"
  - "Yeo, Sze Ling"
year: 2015
venue: "CRYPTO 2015, LNCS 9215, pp. 581-600; IACR ePrint 2015/573"
identifiers:
  eprint: "iacr:2015/573"
  doi: "10.1007/978-3-662-47989-6_28"
  arxiv: null
  url: "https://eprint.iacr.org/2015/573"
tags: [last-fall-degree, first-fall-degree, weil-descent, summation-polynomial, semaev, hfe, groebner, solving-degree, index-calculus, ecdlp, elliptic-curve, dlp, binary-field, prior-art]
confidence: reported
citation_verified: web
added: "2026-07-29"
supersedes: KN-LIT-475
superseded_by: null
---

## Contribution

Introduces the **last fall degree** of a polynomial system — an invariant
independent of the choice of monomial order — and derives complexity bounds
for solving polynomial systems in terms of it. Applies the machinery to Weil
descent attacks on HFE and on the ECDLP in small characteristic.

## Key claims (as reported)

- The last fall degree is monomial-order-independent, unlike the degree of
  regularity, and yields complexity bounds for system solving.
- Quasi-polynomial claims against HFE and subexponential claims for the ECDLP
  **depend on heuristic assumptions**, in particular the first fall degree
  assumption (that the first fall degree does not depend on `n`).
- The authors construct a Weil descent system from a set of summation
  polynomials **in which the first fall degree assumption is unlikely to
  hold** — i.e. the assumption underpinning the subexponential ECDLP estimate
  is not safe in general.

## Relevance to this program

This is the record the 2026-07-29 novelty screen found already present in the
corpus, as the title-only stub KN-LIT-475, at the moment KN-FIND-006 was
written. Had its content been recorded, the screen that produced KN-FIND-006
would have had the decisive prior art in hand.

Together with KN-LIT-7605, it establishes in **proved** form what KN-FIND-006
reports as a **measurement**: the degree invariant governing these systems is
bounded independently of the extension degree, and that boundedness does not
convert into a subexponential ECDLP algorithm. See
`docs/novelty-screen-20260729.md`.

Standing consequence for this program: no proposal may claim, as a new result,
either (a) that Weil-descended Semaev systems violate the semi-regular
prediction, or (b) that the resulting degree deficit is bounded in system
size, without citing this entry and KN-LIT-7605 and stating what it adds.

## Not verified here

- Full text was not read. Claims are from the abstract and search-result
  summaries.
- Whether this paper or KN-LIT-7605 states the specific low-degree counts
  KN-FIND-006 measures (`deficit(D=3) = 1`, `deficit(D=4) = 8k - 1`) was
  **not** determined. That is the question deciding whether KN-FIND-006 has a
  publishable quantitative residue.

## Supersession

Supersedes **KN-LIT-475**, which recorded the same paper (`iacr:2015/573`) as
a title-only stub: authors truncated mid-affiliation ("Ming-Deh A. Huang (USC",
"Michiel Kosters (TL@NTU"), the third author dropped, a stray "?" in the
title, and the body reading "No abstract was extractable from the first two
pages of the local PDF; contribution recorded from the title only."

Per AGENTS.md rule 2 the prior record is not edited away: KN-LIT-475 remains
in place with `superseded_by: KN-LIT-7607`.
