---
id: KN-LIT-7634
type: literature
title: "Trapdoor DDH Groups from Pairings and Isogenies"
authors:
  - "Péter Kutas"
  - "Christophe Petit"
  - "Javier Silva"
year: 2020
venue: "SAC 2020, Springer LNCS 12804; IACR ePrint 2019/1290"
identifiers:
  eprint: "2019/1290"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/1290"
tags: [trapdoor-ddh, pairing, isogeny, supersingular, dent-galbraith]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Contribution

Constructs trapdoor DDH groups using pairings and isogenies of supersingular
elliptic curves, addressing shortcomings of prior Dent–Galbraith / Seurin
constructions. Also gives partial attacks on a Dent–Galbraith construction and
a formal notion of trapdoor pairings.

## Key claims (from fetched SAC preproceedings PDF)

- Public group is a supersingular curve; trapdoor is a secret isogeny from a
  distortion-map-equipped starting curve.
- Trapdoor enables evaluating a symmetric pairing / solving DDH; DLP and CDH
  remain hard under stated assumptions.
- Does **not** claim a full trapdoor ECDLP solver.

## Relevance to GOAL-ECTD-001

Nearest modern construction of secret-isogeny trapdoor capability; supports the
campaign's "trapdoor DDH first" intermediate objective. Ordinary prime-field
analogue remains open.

## Local copies

- `inputs/ECTD-TESKE-20260731/sources/kutas-2019-1290.pdf`
  (SAC 2020 preproceedings mirror; direct eprint PDF returned HTTP 403;
  sha256 `a7f94571aa03ce34bd04d1d5343dceaff4273131390ee89c7bc516366eb0f9ec`)
