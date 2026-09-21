---
id: KN-LIT-7605
type: literature
title: "On the last fall degree of Weil descent polynomial systems"
authors: []
year: null
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2103.07282"
  url: "https://arxiv.org/pdf/2103.07282"
tags: [weil-descent, last-fall-degree, summation-polynomial, semaev, groebner, solving-degree, binary-field, index-calculus, ecdlp, dlp, prior-art]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution

Continues the last-fall-degree line (KN-LIT-7607) for polynomial systems
arising from Weil descent, bounding the invariant that governs the solving
degree of these systems.

## Key claims (as reported)

- The **last fall degree is bounded independently of `n`**, the field
  extension degree. The complexity measure therefore does not grow with system
  size.
- Bounded-fall-degree results are stated for summation-polynomial systems over
  `F_2` specifically.
- The paper does **not** conclude that ECDLP index calculus thereby achieves
  subexponential complexity: the bound constrains one complexity measure
  without establishing an algorithmic breakthrough.

## Relevance to this program

**Direct prior art for KN-FIND-006.** That finding's headline conclusion — the
Macaulay rank deficit "stays in a narrow band", is "bounded, not growing with
system size", and therefore supplies "no asymptotic leverage against ECDLP" —
is the measured form of a statement this line of work **proves**. A finding
that measures over `k = 3..7` what the literature proves for all `n` is a
numerical corroboration, not a new result, and must be presented as such.

The last clause matters for framing elsewhere in this program too: a bounded
fall degree does not hand ECDLP a subexponential algorithm, so neither the
positive nor the negative reading of KN-FIND-006 moves an exponent.

## Not verified here

- Full text was not read; claims taken from a fetched summary of the PDF.
- **Authors, year, and publication venue were not established** and are
  recorded empty rather than guessed. Fill these before citing the record in
  any outward-facing document.
- The precise relationship between this paper and KN-LIT-7607 (strengthening,
  generalisation, or independent treatment) was not determined.
