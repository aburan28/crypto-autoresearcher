---
id: KN-LIT-7604
type: literature
title: "Notes on summation polynomials"
authors:
  - "Kosters, Michiel"
  - "Yeo, Sze Ling"
year: 2015
venue: "arXiv preprint (math.NT)"
identifiers:
  eprint: null
  doi: null
  arxiv: "1503.08001"
  url: "https://arxiv.org/abs/1503.08001"
tags: [summation-polynomial, semaev, weil-descent, first-fall-degree, degree-of-regularity, groebner, binary-field, index-calculus, ecdlp, elliptic-curve, dlp, prior-art]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution

Studies the polynomial systems obtained by Weil descent of Semaev's summation
polynomials, and shows that the descent behaves far better than the generic
heuristics predict — for reasons that are structural rather than accidental.

## Key claims (as reported)

- The Weil descent to `F_2` of the third summation polynomial `S_3`, for
  ordinary curves in general, has **first fall degree 2** — "much lower than
  expected".
- The stated cause is **the existence of a group morphism to `F_2` which gives
  a linear polynomial after Weil descent**. The low degree is therefore forced
  by a structural map, not by a coincidence of the chosen system.
- The paper explicitly casts doubt on the Gröbner-basis heuristics claiming
  that the first fall degree is close to the degree of regularity — the
  heuristic underpinning the Petit–Quisquater subexponential estimate
  (see KN-LIT-005).
- The morphism is not only an obstruction: the authors note it can be used to
  speed up relation generation for the ECDLP.

## Relevance to this program

**Direct prior art for KN-FIND-006.** That finding reports, for the same system
family (Weil descent to `GF(2)` of a chained `S_3`), a degree-3 Macaulay
deficit whose mechanism is "a subset-sum of descended quadrics degenerates to
an **affine** form `P`, and the multiplier is its exact complement, so the
relation is the Boolean identity `P*(1+P) = P + P^2 = 0`". The affine form
whose appearance drives that degeneration is the linear polynomial this paper
attributes to the group morphism to `F_2`. Any novelty claim about the
mechanism of low-degree behaviour in this family must cite and distinguish
this paper first.

More generally: any proposal asserting that Weil-descended Semaev systems
depart from the Bardet–Faugère–Salvy semi-regular prediction is asserting
something already established here and in KN-LIT-7607.

## Not verified here

- Full text was not read. Contribution and claims above are taken from the
  arXiv abstract and search-result summaries, not from the body.
- The identification of this paper's linear polynomial with the affine form in
  KN-FIND-006's degree-3 mechanism is a **judgement made during the
  2026-07-29 novelty screen, not a verified equality**. It is the single
  highest-value item to confirm against the body of the paper before any
  novelty verdict on KN-FIND-006 is recorded as settled.
  See `docs/novelty-screen-20260729.md`.
- Page/section numbers not recorded.
