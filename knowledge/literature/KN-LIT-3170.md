---
id: KN-LIT-3170
type: literature
title: "Correlated Extra-Reductions Defeat"
authors:
  - "Blinded Regular Exponentiation"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, pairing, provable-security, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Walter & Thomson (CT-RSA ’01) and Schindler (PKC ’02) have shown that extra-reductions allow to break RSA-CRT even with message blinding. Indeed, the extra-reduction probability depends on the type of operation (square, multiply, or multiply with a constant).

## Key claims (as reported)
- Regular exponentiation schemes can be regarded as protections since the operation sequence does not depend on the secret.
- In this article, we show that there exists a strong negative correlation between extra-reductions of two consecutive operations, provided that the first feeds the second.
- This allows to mount successful attacks even against blinded asymmetrical computations with a regular exponentiation algorithm, such as Square-and-Multiply Always or Montgomery Ladder.
- We investigate various attack strategies depending on the context—known or unknown modulus, known or unknown extra-reduction detection probability, etc.—and implement them on two devices: a single core ARM Cortex-M4 and a dual core ARM Cortex M0-M4.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130201 (1).pdf`
- `downloads/98130201.pdf`
