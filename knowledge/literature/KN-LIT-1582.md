---
id: KN-LIT-1582
type: literature
title: "Bypassing the Random-Probing Model in Masking Security Proofs"
authors:
  - "Julien Béguinot"
  - "Gianluca Brian"
  - "Loı̈c Masure"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/288"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/288"
tags: [finite-field, mpc, pairing, pqc, provable-security, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
model called random probing (Eurocrypt’14). As a result, the noise requirements of such proofs must scale with the field size of the circuit which, beyond not reflecting real-world physics of target devices, is often prohibitive, especially in the post-quantum era.

## Key claims (as reported)
- That is why it is critical to find alternative strategies to the reduction to the random-probing model.
- In this paper, we establish for the first time a masking security proof bypassing this reduction, answering positively to the above question.
- Contrary to the common belief that directly working in the noisy-leakage model is not convenient, we show how to reach this goal by leveraging an extension of the Xor lemma.
- We also show how to leverage the IOS framework (CHES’21) in order to derive composable security directly in the noisyleakage model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-288.pdf`
