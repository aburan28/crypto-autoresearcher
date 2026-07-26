---
id: KN-LIT-119
type: literature
title: On the impact of decryption failures on the security of LWE/LWR based schemes
authors: [D'Anvers Jan-Pieter, Vercauteren Frederik, Verbauwhede Ingrid]
year: 2019
venue: PKC 2019 (ePrint 2018/1089)
identifiers:
  eprint: iacr:2018/1089
  doi: null
  url: https://eprint.iacr.org/2018/1089
tags: [decryption-failure, failure-boosting, failure-oracle, cca, lwe, lwr, ring-lwe, module-lwe, kem, multi-target, oracle-queries, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Quantifies how decryption failures degrade the chosen-ciphertext security of
lattice KEMs. Introduces *failure boosting* -- deliberately searching for
ciphertexts with elevated failure probability -- analyses the minimum adversary
effort to obtain a failure under three models, measures how much information a
failing ciphertext leaks, and combines these into an attack.

## Key claims (as reported)
- Failure boosting raises the effective failure rate; the paper computes the
  minimal adversary effort to obtain a failure for an adversary with a quantum
  computer, an adversary mounting a multi-target attack, and an adversary
  limited in oracle queries.
- The information an adversary derives from failing ciphertexts is quantified,
  and the two parts combine into an attack on (Ring/Module)-LWE and -LWR schemes
  with decryption failures.
- Reported result: schemes with relatively high failure rates lose significant
  security.
- **Scoping statement the authors make explicitly:** for the NIST candidates
  assessed, the number of required oracle queries is above practical limits,
  because of those schemes' conservative parameter choices.

## Relevance to this program
Directly load-bearing for the repository's ML-KEM line (RQ-MLKEM-001,
EXP-MLKEM-001), which studied failure-probability *modelling* without a
corresponding entry describing what an adversary does with failures. This is
that entry. It also supplies the correct framing for any future program claim
in this area: the security-relevant quantity is not the failure rate alone but
the failure rate combined with the query budget and the boosting gain, and the
conclusion for conservatively parameterised schemes was *negative* for the
attacker. Any internal result that revises a FIPS 203 failure rate must connect
to this chain before it can claim security relevance -- a revised rate is not by
itself an attack.

## Not verified here
The ePrint abstract was fetched and read. The failure-boosting analysis, the
information-leakage quantification, and the implementation were not reproduced.
Which specific NIST candidates were assessed, and their query thresholds, were
not extracted from the full text. Later work in this line (including
multi-ciphertext and directional-failure refinements) was not surveyed.
