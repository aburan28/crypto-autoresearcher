---
id: KN-LIT-095
type: literature
title: Solving a 112-bit Prime Elliptic Curve Discrete Logarithm Problem on Game Consoles using Sloppy Reduction
authors: [Bos Joppe W., Kaihara Marcelo E., Kleinjung Thorsten, Lenstra Arjen K., Montgomery Peter L.]
year: 2012
venue: International Journal of Applied Cryptography, 2(3):212-228
identifiers:
  eprint: null
  doi: 10.1504/IJACT.2012.045590
  url: https://www.joppebos.com/files/noan112.pdf
tags: [record-computation, prime-field, secp112r1, pollard-rho, distinguished-points, cell-processor, playstation-3, baseline, calibration, ecdlp]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The largest publicly completed prime-field ECDLP computation. A parallelized
Pollard rho implementation on the Cell processor, run on a cluster of about
215 PlayStation 3 consoles at EPFL, solved the discrete logarithm on the
standardized curve secp112r1 over the 112-bit prime p = (2^128 - 3)/(11*6949).
The paper's technical contribution is "sloppy reduction": reducing modulo the
special-form multiple 2^128 - 3 rather than p, in 4-way SIMD, so that
x * 2^128 == x * 3 makes reduction nearly free.

## Key claims (as reported)
- New prime-field ECDLP record, superseding a 109-bit prime-field record from
  October 2002.
- Expected iteration count sqrt(pi * n / 2) ~= 8.4 * 10^16 for the order-n
  subgroup, with n = 4451685225093714776491891542548933.
- Elapsed 13 January 2009 to 8 July 2009, not running continuously; the
  authors state the same computation with their final code would take about
  3.5 months of continuous running on that cluster.
- The target point was chosen verifiably-not-pre-cooked, from digits of pi;
  the recovered logarithm is published (k = 312521636014772477161767351856699).

## Relevance to this program
This is the single most important calibration point for GOAL-CRYPTO-001. The
goal's threshold is a certificate-verified advantage on a recognized curve
above 96 bits; this record establishes that the *state of the art for a fully
completed prime-field solve is 112 bits*, achieved with roughly 2^56.2
iterations and six months of a 200-console cluster. Any proposal claiming a
crypto-size prime-field solve must be measured against that, and any claimed
advantage at 112-128 bits is immediately checkable against a real published
cost rather than an extrapolated one. It also gives the program a concrete,
reproducible target instance: secp112r1 with a published solution is an
end-to-end test of a solver and its certificate machinery, at a scale that is
hard but not hypothetical.

## Not verified here
The author-hosted PDF and the EPFL Infoscience copy were fetched, and the
abstract, the curve/parameter section, and the reported timings and iteration
counts were read directly. The SIMD arithmetic sections were not checked and
no timing was reproduced. Authors, title and the 2009 announcement were
confirmed against the archived LACAL announcement page and the July 2009
cryptography-list posting. The venue fields are for the later journal version
(IJACT 2(3):212-228, 2012) and were confirmed against the Inderscience article
record and the EPFL Infoscience entry; the fetched PDF is the author preprint,
so the bibliographic fields are `web`-level while the technical claims above
are read-level. Note the journal shortens the title to "Solving 112-bit prime
ECDLP on game consoles using sloppy reduction."
