---
id: KN-LIT-1965
type: literature
title: "“BREAKMEIFYOUCAN!”: Exploiting Keyspace Reduction and Relay"
authors:
  - "Attacks in DES"
  - "AES-protected NFC Technologies"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/100"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/100"
tags: [cryptanalysis, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents an in-depth analysis of vulnerabilities in MIFARE Ultralight C (MF0ICU2), MIFARE Ultralight AES (MF0AES), NTAG 223 DNA (NT2H2331G0 and NT2H2331S0), NTAG 224 DNA (NT2H2421G0 and NT2H2421S0), and widely circulated counterfeit Ultralight C cards based on Giantec GT23SC4489, Feiju FJ8010, and USCUID-UL. We reveal multiple avenues to substantially weaken the security of each technology and its implementation across a range of configurations.

## Key claims (as reported)
- We demonstrate how, through relay-based man-in-the-middle techniques and partial key overwrites — optionally combined with tearing techniques — an attacker can reduce the keyspace of two-key Triple DES (2TDEA) from 2112 to 228 or less in certain real-world deployments, thereby making brute-force key recovery feasible with modest computational resources.
- We further discuss how the MIFARE Ultralight AES protocol can be similarly affected, particularly when CMAC integrity checks are not enforced.
- We also find that the security offered by NTAG 223 DNA and NTAG 224 DNA is undermined by the absence of integrity checks on commands and the calculation of a CMAC over Secure Unique NFC (SUN) messages, providing an unauthenticated ciphertext oracle that facilitates key recovery.
- Field observations, especially in hospitality deployments, underscore the urgent need for proper configuration, key diversification, and counterfeit detection.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-100.pdf`
