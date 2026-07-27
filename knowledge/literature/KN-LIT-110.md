---
id: KN-LIT-110
type: literature
title: 'Report on the Security of LWE: Improved Dual Lattice Attack'
authors: [MATZOV]
year: 2022
venue: Technical report, Center of Encryption and Information Security (MATZOV), IDF; Zenodo
identifiers:
  eprint: null
  doi: 10.5281/zenodo.6412487
  url: https://zenodo.org/records/6493704
tags: [dual-attack, fft, distinguisher, lwe, lwr, kyber, saber, dilithium, gate-count, ram-model, sieving-cost, nist, contested, lattice, calibration]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
A technical report claiming that improvements to the dual lattice attack push
the security of three NIST finalists below the levels NIST required. It is the
most consequential concrete-security claim of the NIST process's final round,
and -- as with KN-LIT-109, on which it builds independently -- its analysis is
contested by KN-LIT-111.

## Key claims (as reported)
- Three stated improvements: enumerating over more coordinates of the secret
  combined with an improved FFT-based distinguisher; reduced estimated RAM-model
  gate counts for sieving relative to the previous estimates of KN-LIT-122,
  mainly via cheaper random-product-code decoding and fewer inner products; and
  a faster short-vector sampling procedure.
- Claimed security levels (log2 gate count) against the NIST requirement and the
  submitters' own claims, read directly from the report's Table 1: Kyber512
  required 143, claimed 151.5, MATZOV 137.5; Kyber768 required 207, claimed
  215.1, MATZOV 193.5; Kyber1024 required 272, claimed 287.3, MATZOV 257.8.
- Summary claim: Kyber's security is reduced to between 4 and 14 bits below the
  NIST cutoff; for almost all candidates and levels the attack cost falls below
  the requirement, with Dilithium at Security Level 2 the sole stated exception.
- The report frames itself as sharing cryptanalytic advances for public review,
  explicitly not as a complete analysis and not as a recommendation.

## Relevance to this program
Two distinct lessons, which should not be conflated. First, a substantial part
of the claimed reduction comes not from a new attack but from **re-costing an
existing one** -- cheaper gate counts for the same sieve. That is a pure cost-model
change, and it moves headline security numbers by bits; it is the clearest
available demonstration that in lattice cryptanalysis the cost model is a
first-class part of the claim, which is the same discipline KN-TECH-035
imposes on the ECDLP side. Second, these numbers are contested at the level of
their underlying heuristics (KN-LIT-111), so they must be cited as claimed,
never as established, and the episode belongs in the program's record of how
concrete-security disputes get resolved (KN-OPEN-016).

## Not verified here
The Zenodo abstract and the report PDF's introduction and Table 1 were fetched
and read; the quoted figures are transcribed from that table. None of the
gate-count estimates, the FFT distinguisher analysis, or the sieving re-costing
was re-derived or reproduced. Note the report exists in at least two versions
(Zenodo records 6412487 and 6493704); figures above are from the version
fetched here and version-to-version differences were not checked.
