---
id: KN-LIT-3757
type: literature
title: "Efficient Leakage-Resilient MACs without Idealized Assumptions"
authors:
  - "Francesco Berti"
  - "Chun Guo"
  - "Thomas Peters"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security proofs of leakage-resilient MACs based on symmetric building blocks currently rely on idealized assumptions that hardly translate into interpretable guidelines for the cryptographic engineers implementing these schemes. In this paper, we first present a leakageresilient MAC that is both efficient and secure under standard and easily interpretable black box and physical assumptions.

## Key claims (as reported)
- It only requires a collision resistant hash function and a single call per message authentication to a Tweakable Block Cipher (TBC) that is unpredictable with leakage.
- This construction leverages two design twists: large tweaks for the TBC and a verification process that checks the inverse TBC against a constant.
- It enjoys beyond birthday security bounds.
- We then discuss the cost of getting rid of these design twists.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900271 (1).pdf`
- `downloads/130900271.pdf`
