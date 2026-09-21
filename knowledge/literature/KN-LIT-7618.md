---
id: KN-LIT-7618
type: literature
title: "CRYSTALS-Kyber: Algorithm Specifications And Supporting Documentation (Round 3)"
authors: [Avanzi Roberto, Bos Joppe, Ducas Léo, Kiltz Eike, Lepoint Tancrède, Lyubashevsky Vadim, Schanck John M., Schwabe Peter, Seiler Gregor, Stehlé Damien]
year: 2021
venue: NIST PQC Round 3 submission package; pq-crystals.org
identifiers:
  eprint: null
  doi: null
  url: https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf
tags: [kyber, ml-kem, nist, specification, module-lwe, concrete-security, primary-source, lattice]
confidence: reported
citation_verified: read
added: 2026-07-31
superseded_by: null
---

## Contribution
Primary Round-3 specification for CRYSTALS-Kyber (the scheme standardized as
ML-KEM / FIPS 203). Defines parameter sets Kyber512/768/1024, the Module-LWE
problem instance, FO-transform KEM construction, and the security-estimate
methodology used in the submission (core-SVP / ADPS16-style costing via the
public `pq-crystals/security-estimates` scripts).

## Key claims (as reported; read from local PDF copy)
- Parameters: n=256, q=3329; (k, η1, η2) = (2,3,2) / (3,2,2) / (4,2,2) for
  Kyber512/768/1024 (ciphertext compression differs at Kyber1024).
- Security estimates in the supporting scripts report classical core-SVP costs
  near 118 / 183 / 256 for the three sets (reproduced in EXP-MLKEM-015 /
  RUN-MLKEM-015-001).
- These core-SVP numbers are deliberately not the same cost convention as the
  NIST classical Category cutoffs 143 / 207 / 272 used in MATZOV / Carrier
  comparisons (KN-LIT-110, KN-LIT-7617).

## Local artifact
`experiments/EXP-MLKEM-015/vendor-lock/kyber-round3-specification.pdf`
(sha256 to be recorded in EXP-MLKEM-015 source-lock).

## Relevance
Mandatory primary for RQ-MLKEM-003 / GOAL-MLKEM-003 before any parameter-level
claim. FIPS 203 text remains preferred when network policy permits nist.gov;
until then this Round-3 spec plus the pinned security-estimates scripts are
the parameter and core-SVP baseline sources.
