---
id: KN-LIT-7633
type: literature
title: "Hidden Pairings and Trapdoor DDH Groups"
authors:
  - "Alexander W. Dent"
  - "Steven D. Galbraith"
year: 2006
venue: "ANTS-VII, Springer LNCS 4076, pp. 436–451"
identifiers:
  eprint: null
  doi: "10.1007/11792086_31"
  arxiv: null
  url: "https://doi.org/10.1007/11792086_31"
tags: [trapdoor-ddh, hidden-pairing, elliptic-curve, multivariate, dent-galbraith]
confidence: reported
citation_verified: false
added: "2026-07-31"
superseded_by: null
---

## Contribution (from published abstract; PDF not obtained)

Introduces trapdoor DDH groups: publish a group description supporting ordinary
group operations while retaining a private description that enables a bilinear
pairing (hence DDH, and potentially DLP). Two elliptic-curve constructions:
(1) factoring-based hidden pairing; (2) multivariate-equation disguise of a
Weil restriction / pairing-capable representation.

## Key claims (reported from Springer/ANTS abstract and secondary citations)

- Public description: group ops only; private description: pairing.
- Second construction aims at a practical trapdoor DLP-ish capability via
  disguised representation (security against algebraic recovery uncertain).
- Cited as unbroken (among the two) by Seurin (KN-LIT-5102) until later
  partial attacks in Kutas–Petit–Silva (KN-LIT-7634).

## Relevance to GOAL-ECTD-001

Abstract model for hiding an extra representation/operation rather than a
class-invariant weak curve — the conceptual lesson for prime-field trapdoors.

## Fetch obstruction (2026-07-31)

- No IACR ePrint found.
- Author page https://www.math.auckland.ac.nz/~sgal018/pubs.html lists the
  ANTS-VII citation but no open PDF link.
- Tried common author PDF filenames and Springer content/pdf URL: 404 / HTML
  paywall interstitial.
- Abstract verified via DOI landing metadata and consistent secondary citations
  (KN-LIT-5102, KN-LIT-7634). Upgrade to `citation_verified: true` when a PDF
  is obtained.
