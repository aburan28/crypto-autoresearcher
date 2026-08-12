---
id: KN-LIT-056
type: literature
title: CRYSTALS-Dilithium - A Lattice-Based Digital Signature Scheme (ML-DSA / FIPS 204)
authors: [Ducas Leo, Kiltz Eike, Lepoint Tancrede, Lyubashevsky Vadim, Schwabe Peter, Seiler Gregor, Stehle Damien]
year: 2018
venue: IACR TCHES 2018(1):238-268; standardized as NIST FIPS 204 (2024)
identifiers:
  eprint: iacr:2017/633
  doi: 10.13154/tches.v2018.i1.238-268
  url: https://tches.iacr.org/index.php/TCHES/article/view/839
tags: [dilithium, ml-dsa, module-lwe, module-sis, fiat-shamir-with-aborts, signature, nist, fips-204, post-quantum, standard, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Dilithium is a Fiat-Shamir-with-aborts signature (KN-LIT-059) over module
lattices, with security resting on Module-LWE and Module-SIS (KN-LIT-054). It
avoids discrete Gaussian sampling for easy constant-time implementation.
Standardized by NIST as ML-DSA in FIPS 204 (2024).

## Key claims (as reported)
- Module-LWE/SIS signature with three parameter sets (ML-DSA-44/65/87); compact
  public keys; rejection sampling makes the output secret-independent.
- NIST standard: "Module-Lattice-Based Digital Signature Standard," FIPS 204,
  published 2024-08-13 (doi:10.6028/NIST.FIPS.204,
  https://csrc.nist.gov/pubs/fips/204/final). ePrint 2017/633 carries the variant
  title "Digital Signatures from Module Lattices."

## Relevance to this program
POST-QUANTUM standard, ADJACENT to the ECDLP mission -- recorded as the intended
NIST replacement for ECDSA/EdDSA. Its security is a module-lattice question, not a
discrete-log one; the nonce-leakage lattice attacks that break ECDSA (KN-TECH-019)
do not carry over, as Dilithium's rejection sampling removes the secret-dependent
leakage those attacks exploit.

## Not verified here
Papers/standard not read; scheme details relayed from the abstract and NIST CSRC
page (hence confidence: reported). The FIPS 204 DOI follows the NIST CSRC scheme
and matches the final CSRC page (surfaced via search, not fetched). Fields
confirmed against TCHES/IACR/NIST records via search.
