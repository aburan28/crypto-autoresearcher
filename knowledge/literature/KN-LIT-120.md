---
id: KN-LIT-120
type: literature
title: Explicit hard instances of the shortest vector problem
authors: [Buchmann Johannes, Lindner Richard, Ruckert Markus, Schneider Michael]
year: 2008
venue: PQCrypto 2008 (ePrint 2008/333)
identifiers:
  eprint: iacr:2008/333
  doi: 10.1007/978-3-540-88403-3_6
  url: https://eprint.iacr.org/2008/333
tags: [svp-challenge, darmstadt, lattice-challenge, benchmark, ajtai, worst-case, records, calibration, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Constructs an explicit sequence of lattice bases of growing dimension, built on
Ajtai's worst-case construction, that can be expected to be hard SVP instances,
and uses them to found the TU Darmstadt Lattice Challenge. This is the origin of
the public benchmark that lets lattice reduction claims be checked by anyone.

## Key claims (as reported)
- Ajtai's construction defines the relevant lattices only implicitly; the paper
  gives explicit integral bases. For any `m >= 500` a lattice `L_m` of dimension
  m is constructed with parameters chosen as functions of m.
- The construction plus the pseudo-random choice of `L_m` guarantees the
  *existence* of vectors `v` with `||v||_2 < n(m)` that are hard to find. The
  hardness expectation is inherited from Ajtai's worst-case-to-average-case
  result; it is not a proof that any particular instance is hard.
- Challenge protocol: contestants receive a basis and a norm bound
  `nu = ceil(sqrt(m))` initially; each accepted solution `v` reduces `nu` to
  `||v||_2`. Hosted at latticechallenge.org.

## Relevance to this program
Establishes for lattices what the ECDLP record computations establish for curves
(KN-TECH-036): an externally maintained, adversarially attacked, publicly
falsifiable ceiling on demonstrated capability. Note the design property that
makes it useful and that the ECDLP challenges share -- the *challenger* need not
know the answer, so nothing is taken on the organisers' word.

Two related but distinct challenge families now exist and should not be
conflated. This paper's Lattice Challenge uses Ajtai-style bases with a
worst-case pedigree. The separate **SVP Challenge** uses random lattices in the
sense of Goldstein-Mayer and is the one whose dimensions are quoted in the
sieving literature (KN-LIT-106 reports SVP-151/153/155). The **LWE Challenge**
(KN-LIT-121) is a third. A claimed "dimension d record" is meaningless without
saying which family it is in.

## Not verified here
The ePrint abstract and the PDF's construction and challenge sections were
fetched and read. The construction was not implemented, the existence argument
was not re-derived, and Ajtai's underlying worst-case result was not checked.
The current state of the hall of fame is a live web resource and is not frozen
by this entry; the SVP Challenge hall of fame displayed a dimension-210 entry
(Euclidean norm 3808, seed 0, Ding and Zhao) when retrieved on 2026-07-24,
which is a website reading subject to caching, not a verified record.
