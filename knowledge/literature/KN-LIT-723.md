---
id: KN-LIT-723
type: literature
title: "Variants of the AES Key Schedule for Better Truncated Differential Bounds"
authors:
  - "Patrick Derbez"
  - "Pierre-Alain Fouque"
  - "Jérémy Jean"
  - "Baptiste Lambin"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/095"
  doi: "10.1007/978-3-030-10970-7_2"
  arxiv: null
  url: "https://eprint.iacr.org/2019/095"
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Differential attacks are one of the main ways to attack block ciphers. Hence, we need to evaluate the security of a given block cipher against these attacks.

## Key claims (as reported)
- One way to do so is to determine the minimal number of active S-boxes, and use this number along with the maximal differential probability of the S-box to determine the minimal probability of any differential characteristic.
- Thus, if one wants to build a new block cipher, one should try to maximize the minimal number of active Sboxes.
- On the other hand, the related-key security model is now quite important, hence, we also need to study the security of block ciphers in this model.
- In this work, we search how one could design a key schedule to maximize the number of active S-boxes in the related-key model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-095.pdf`
