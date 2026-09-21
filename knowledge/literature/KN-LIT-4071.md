---
id: KN-LIT-4071
type: literature
title: "Generalized Fuzzy Password-Authenticated Key Exchange from Error Correcting Codes"
authors:
  - "Jonathan Bootle"
  - "Sebastian Faller"
  - "Julia Hesse"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fuzzy Password-Authenticated Key Exchange (fuzzy PAKE) allows cryptographic keys to be generated from authentication data that is both fuzzy and of low entropy. The strong protection against offline attacks offered by fuzzy PAKE opens an interesting avenue towards secure biometric authentication, typo-tolerant password authentication, and automated IoT device pairing.

## Key claims (as reported)
- Previous constructions of fuzzy PAKE are either based on Error Correcting Codes (ECC) or generic multi-party computation techniques such as Garbled Circuits.
- While ECC-based constructions are significantly more efficient, they rely on multiple special properties of error correcting codes such as maximum distance separability and smoothness.
- We contribute to the line of research on fuzzy PAKE in two ways.
- First, we identify a subtle but devastating gap in the security analysis of the currently most efficient fuzzy PAKE construction (Dupont et al., Eurocrypt 2018), allowing a man-in-the-middle attacker to test individual password characters.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438305 (1).pdf`
- `downloads/14438305.pdf`
