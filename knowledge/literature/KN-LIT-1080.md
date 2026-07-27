---
id: KN-LIT-1080
type: literature
title: "Classical and Quantum Meet-in-the-Middle Nostradamus Attacks on AES-like Hashing"
authors:
  - "Zhiyu Zhang"
  - "Siwei Sun"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/772"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/772"
tags: [cryptanalysis, glv-gls, hash, pairing, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At EUROCRYPT 2006, Kelsey and Kohno proposed the so-called chosen target forced-prefix (CTFP) preimage attack, where for any challenge prefix P , the attacker can generate a suffix S such that H(P ∥S) = y for some hash value y published in advance by the attacker. Consequently, the attacker can pretend to predict some event represented by P she did not know before, and thus this type of attack is also known as the Nostradamus attack.

## Key claims (as reported)
- At ASIACRYPT 2022, Benedikt et al. convert Kelsey et al.’s attack to a quantum one, reducing the time complexity √ √ from O( n · 22n/3 ) to O( 3 n · 23n/7 ).
- CTFP preimage attack is less investigated in the literature than (second-)preimage and collision attacks and lacks dedicated methods.
- In this paper, we propose the first dedicated Nostradamus attack based on the meet-in-the-middle (MITM) attack, and the MITM Nostradamus attack could be up to quadratically accelerated in the quantum setting.
- According to the recent works on MITM preimage attacks on AES-like hashing, we build an automatic tool to search for optimal MITM Nostradamus attacks and model the tradeoff between the offline and online phases.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-772.pdf`
