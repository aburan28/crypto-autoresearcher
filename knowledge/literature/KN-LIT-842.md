---
id: KN-LIT-842
type: literature
title: "Automatic Classical and Quantum Rebound Attacks on AES-like Hashing by Exploiting Related-key Differentials"
authors:
  - "Xiaoyang Dong"
  - "Zhiyu Zhang"
  - "Siwei Sun"
  - "Congming Wei"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/111"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/111"
tags: [cryptanalysis, hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Collision attacks on AES-like hashing (hash functions constructed by plugging AES-like ciphers or permutations into the famous PGV modes or their variants) can be reduced to the problem of finding a pair of inputs respecting a differential of the underlying AES-like primitive whose input and output differences are the same. The rebound attack due to Mendel et al. is a powerful tool for achieving this goal, whose quantum version was first considered by Hosoyamada and Sasaki at EUROCRYPT 2020.

## Key claims (as reported)
- In this work, we automate the process of searching for the configurations of rebound attacks by taking related-key differentials of the underlying block cipher into account with the MILPbased approach.
- In the quantum setting, our model guide the search towards characteristics that minimize the resources (e.g., QRAM) and complexities of the resulting rebound attacks.
- We apply our method to Saturnin-hash, SKINNY, and Whirlpool and improved results are obtained.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900110 (1).pdf`
- `downloads/130900110.pdf`
- `downloads/2021-1119.pdf`
