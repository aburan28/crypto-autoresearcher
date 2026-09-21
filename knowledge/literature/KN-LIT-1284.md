---
id: KN-LIT-1284
type: literature
title: "Practical Investigation on the Distinguishability of Longa’s Atomic Patterns"
authors:
  - "Sze Hei Li"
  - "Zoya Dyka"
  - "Alkistis Aikaterini Sigourou"
  - "Peter Langendoerfer"
  - "Ievgen Kabin"
year: 2024
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2409.11868"
  url: "https://arxiv.org/abs/2409.11868"
tags: [curve-arithmetic, elliptic-curve, finite-field, pairing, quantum, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper investigates the distinguishability of the atomic patterns for elliptic curve point doubling and addition operations proposed by Longa [2]. We implemented a binary elliptic curve scalar multiplication kP algorithm with Longa's atomic patterns for the NIST elliptic curve P-256 using the open-source cryptographic library FLECC in C.

## Key claims (as reported)
- We measured and analysed an electromagnetic trace of a single kP execution on a microcontroller (TI Launchpad F28379 board).
- Due to various technical limitations, significant differences in the execution time and the shapes of the atomic blocks could not be determined.
- Further investigations of the side channel analysis-resistance can be performed based on this work.
- Last but not least, we examined and corrected Longa’s atomic patterns corresponding to formulae proposed by Longa.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2409.11868v2.pdf`
