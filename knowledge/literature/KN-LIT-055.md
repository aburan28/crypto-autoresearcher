---
id: KN-LIT-055
type: literature
title: CRYSTALS-Kyber - A CCA-Secure Module-Lattice-Based KEM (ML-KEM / FIPS 203)
authors: [Bos Joppe W., Ducas Leo, Kiltz Eike, Lepoint Tancrede, Lyubashevsky Vadim, Schanck John M., Schwabe Peter, Seiler Gregor, Stehle Damien]
year: 2018
venue: IEEE EuroS&P 2018, pp. 353-367; standardized as NIST FIPS 203 (2024)
identifiers:
  eprint: iacr:2017/634
  doi: 10.1109/EuroSP.2018.00032
  url: https://eprint.iacr.org/2017/634
tags: [kyber, ml-kem, module-lwe, kem, nist, fips-203, post-quantum, standard, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Kyber is an IND-CCA2-secure key-encapsulation mechanism (KEM) built on Module-LWE
(KN-LIT-054), with keys/ciphertexts roughly half the size of prior LWE KEMs and
CCA security via a Fujisaki-Okamoto-style transform. Standardized by NIST as
ML-KEM in FIPS 203 (2024).

## Key claims (as reported)
- Module-LWE KEM with three parameter sets (ML-KEM-512/768/1024).
- NIST standard: "Module-Lattice-Based Key-Encapsulation Mechanism Standard,"
  FIPS 203, published 2024-08-13 (doi:10.6028/NIST.FIPS.203,
  https://csrc.nist.gov/pubs/fips/203/final).

## Relevance to this program
POST-QUANTUM standard, ADJACENT to (not part of) the ECDLP mission -- recorded as
the intended NIST replacement for ECDLP/(EC)DH key establishment. Its security is
a Module-LWE question (KN-TECH-021, KN-TECH-022), unrelated to discrete logs; the
program's ECDLP work concerns the classical primitive Kyber is meant to succeed.

## Not verified here
Papers/standard not read; scheme and parameter details relayed from the abstract
and NIST CSRC page (hence confidence: reported). The FIPS 203 DOI follows the NIST
CSRC scheme and matches the final CSRC page (surfaced via search, not fetched).
Fields confirmed against IEEE/IACR/NIST records via search.
