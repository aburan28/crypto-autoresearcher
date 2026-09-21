---
id: KN-LIT-109
type: literature
title: Faster Dual Lattice Attacks for Solving LWE with Applications to CRYSTALS
authors: [Guo Qian, Johansson Thomas]
year: 2021
venue: ASIACRYPT 2021, LNCS 13093, Springer, pages 33-62
identifiers:
  eprint: null
  doi: 10.1007/978-3-030-92068-5_2
  url: https://doi.org/10.1007/978-3-030-92068-5_2
tags: [dual-attack, fft, distinguisher, lwe, kyber, dilithium, bkw, security-estimate, contested, lattice]
confidence: reported
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
Proposes a two-step lattice reduction strategy for the dual attack on LWE that
combines the "dimensions for free" trick (KN-LIT-105) with the sieve's
production of many short vectors, together with an FFT-based distinguishing
step borrowed from Bleichenbacher-style techniques. The claim is that this
removes the reason dual attacks were considered weaker than primal attacks, and
reduces the security of CRYSTALS parameter sets.

## Key claims (as reported)
- The inability to combine "dimensions for free" with bulk short-vector output
  from sieving was believed to be the main reason dual attacks underperformed
  primal attacks; the new two-step reduction strategy allows both.
- Applied to CRYSTALS-Kyber, the reported improvement reaches on the order of
  several bits, with an extrapolation model attributed to Albrecht et al.;
  Kyber-768 is claimed solvable with classical gate complexity below its claimed
  security level.
- Gains are also reported against parameters from a draft Homomorphic Encryption
  Standard, including a 192-bit-target parameter set claimed solvable in
  `2^187.0` operations in the classical RAM model.

## Relevance to this program
This paper is one half of the most instructive live controversy in concrete
lattice cryptanalysis. Its claims are **contested**: Ducas and Pulles
(KN-LIT-111) argue the heuristics underlying this attack family contradict
unconditional theorems in some regimes and well-tested heuristics in others,
and that the success probabilities are presumably significantly overestimated.
The program should therefore treat the numbers above strictly as *claimed*, and
should treat the episode itself as the reference case for what happens when an
attack's analysis rests on unexamined heuristics -- see KN-OPEN-016. It is also
a caution about extrapolation models: the security reductions are asserted at
parameter sizes far beyond anything demonstrated experimentally.

## Not verified here
Author, title, venue, year, volume, and page range were confirmed against the
Springer DOI record, DBLP, and the publisher listing; no complete abstract or
full text was fetched, and the quoted figures come from a publisher-hosted
partial abstract. No claim in this entry has been checked against the paper's
own analysis, and the contested status is recorded on the authority of
KN-LIT-111 rather than of this paper.
