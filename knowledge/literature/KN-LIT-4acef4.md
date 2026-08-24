---
id: KN-LIT-4acef4
type: literature
title: "One Discrete Gaussian Sample in 2^{n/2+o(n)} Time"
authors:
  - "Jiseung Kim"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1599"
identifiers:
  eprint: iacr:2026/1599
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1599"
tags: [lattices, discrete-gaussian, sampling, svp, cvp, superlattice, smoothing]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Shows that for every rank-n lattice L ⊆ R^n given by a rational basis and
every rational s > 0, one sample from D(L,s) within statistical distance
exp(-Ω(n^3)) is obtainable in expected 2^{n/2+o(n)} time and space on every
execution. The algorithm samples from random superlattices that are smooth at
the required scale with constant probability, then outputs the first point in
L; the 2^{n/2} factor is tight in the Gaussian-mass comparison. This answers
the "one sample above smoothing" question left open by ADRS (STOC 2015),
which sampled 2^{n/2} Gaussians in 2^{n+o(n)} time.

## Key claims (as reported)
- One discrete Gaussian sample at an arbitrary rational parameter in expected
  2^{n/2+o(n)} time and 2^{n/2+o(n)} space on every execution.
- Tightness: the 2^{n/2} factor is tight in the Gaussian-mass comparison.
- For every fixed rational α < 1.4697, exact CVP on targets with dist(y,L) ≤
  αλ₁(L) (no uniqueness assumption) and an exact-SVP algorithm in
  2^{0.7315n+o(n)} time.

## Relevance
- DGS sampling is a foundational submachine of SVP/Hessian-style lattice
  algorithms the program tracks (sieving uses DGS submachines; the
  superlattice sampling connects to the 2^{0.7314n} SVP record in
  KN-LIT-b875db and the 2^{0.6039n} mid-point Hessian work in
  KN-LIT-b8093a).

## Not verified here
- Only the first-page abstract was read; exact sampling details and the
  tightness proof were not independently reproduced.