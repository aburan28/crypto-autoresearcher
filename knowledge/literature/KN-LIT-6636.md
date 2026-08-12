---
id: KN-LIT-6636
type: literature
title: "Signatures Resilient to Continual Leakage on Memory and Computation"
authors:
  - "Tal Malkin"
  - "Isamu Teranishi"
  - "Yevgeniy Vahlis"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recent breakthrough results by Brakerski et al and Dodis et al have shown that signature schemes can be made secure even if the adversary continually obtains information leakage from the secret key of the scheme. However, the schemes currently do not allow leakage on the secret key and randomness during signing, except in the random oracle model.

## Key claims (as reported)
- Further, the random oracle based schemes require updates to the secret key in order to maintain security, even when no leakage during computation is present.
- We present the first signature scheme that is resilient to full continual leakage: memory leakage as well as leakage from processing during signing (both from the secret key and the randomness), in key generation, and in update.
- Our scheme can tolerate leakage of a 1 − o(1) fraction of the secret key between updates, and is proven secure in the standard model based on the symmetric external DDH (SXDH) assumption in bilinear groups.
- The time periods between updates are a function of the amount of leakage in the period (and nothing more).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970088 (1).pdf`
- `downloads/65970088 (2).pdf`
- `downloads/65970088 (3).pdf`
- `downloads/65970088.pdf`
