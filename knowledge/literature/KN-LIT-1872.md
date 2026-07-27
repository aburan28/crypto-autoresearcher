---
id: KN-LIT-1872
type: literature
title: "Side-Channel Attacks Revisited — an Optimization Problem Perspective:"
authors:
  - "Space Reduction"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1468"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1468"
tags: [fhe, glv-gls, hash, mov-fr, pairing, provable-security, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel analysis (SCA) attacks rely on leakage from a target device. It is common to assume that linear operations implemented by XOR gates produce symmetric leakage and carry negligible side-channel information.

## Key claims (as reported)
- In practice, leakage from XOR gates produces complex, non-independent, and time-varying asymmetric behavior.
- The paper introduces Feature Estimation based Attacks (FEbA) – a dedicated profiling attack that exploits these asymmetries.
- The attack is versatile; it was demonstrated to be successful against the sharing and refreshing phases in maskingbased implementations by greatly narrowing the guessing key space, with no access to intermediate values.
- Such attacks have implications for designs such as ASCON, GIBBON, and ACE, where XORs that utilize the key are vulnerable to attacks regardless of the inherent SCA protection levels used in them (e.g., sponge rate, the leak-free components for re-keying, and masking order d).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1468.pdf`
