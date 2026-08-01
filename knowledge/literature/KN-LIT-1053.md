---
id: KN-LIT-1053
type: literature
title: "Triangulating Rebound Attack on AES-like Hashing"
authors:
  - "Xiaoyang Dong"
  - "(B) "
  - "Jian Guo (B) "
  - "Shun Li"
  - "(B) "
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/731"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/731"
tags: [cryptanalysis, hash, mpc, pairing, pqc, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The rebound attack was introduced by Mendel et al. at FSE 2009 to fulfill a heavy middle round of a differential path for free, utilizing the degree of freedom from states. The inbound phase was extended to 2 rounds by the Super-Sbox technique invented by Lamberger et al. at ASIACRYPT 2009 and Gilbert and Peyrin at FSE 2010.

## Key claims (as reported)
- In ASIACRYPT 2010, Sasaki et al. further reduced the requirement of memory by introducing the non-full-active Super-Sbox.
- In this paper, we further develop this line of research by introducing Super-Inbound, which is able to connect multiple 1-round or 2-round (non-full-active) Super-Sbox inbound phases by utilizing fully the degrees of freedom from both states and key, yet without the use of large memory.
- This essentially extends the inbound phase by up to 3 rounds.
- We applied this technique to find classic or quantum collisions on several AES-like hash functions, and improved the attacked round number by 1 to 5 in targets including AES128 and SKINNY hashing modes, Saturnin-Hash, and Grøstl-512.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070027 (1).pdf`
- `downloads/135070027.pdf`
- `downloads/2022-731.pdf`
