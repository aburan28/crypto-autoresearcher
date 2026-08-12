---
id: KN-LIT-4964
type: literature
title: "Moving a Step of ChaCha in Syncopated Rhythm"
authors:
  - "Shichang Wang"
  - "Meicheng Liu"
  - "Shiqi Hou"
  - "Dongdai Lin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, mov-fr, pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The stream cipher ChaCha is one of the most widely used ciphers in the real world, such as in TLS, SSH and so on. In this paper, we study the security of ChaCha via differential cryptanalysis based on probabilistic neutrality bits (PNBs).

## Key claims (as reported)
- We introduce the syncopation technique for the PNB-based approximation in the backward direction, which significantly amplifies its correlation by utilizing the property of ARX structure.
- In virtue of this technique, we present a new and efficient method for finding a good set of PNBs.
- A refined framework of keyrecovery attack is then formalized for round-reduced ChaCha.
- The new techniques allow us to break 7.5 rounds of ChaCha without the last XOR and rotation, as well as to bring faster attacks on 6 rounds and 7 rounds of ChaCha.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850410 (1).pdf`
- `downloads/140850410.pdf`
