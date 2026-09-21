---
id: KN-LIT-4776
type: literature
title: "Logarithmic-Size (Linkable)"
authors:
  - "Daniel Slamanig"
  - "Christoph Striecks"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A 1-out-of-N ring signature scheme, introduced by Rivest, Shamir, and Tauman-Kalai (ASIACRYPT ’01), allows a signer to sign a message as part of a set of size N (the so-called “ring”) which are anonymous to any verifier, including other members of the ring. Threshold ring (or “thring”) signatures generalize ring signatures to t-out-of-N parties, with t ≥ 1, who anonymously sign messages and show that they are distinct signers (Bresson et al., CRYPTO’02).

## Key claims (as reported)
- Until recently, there was no construction of ring signatures that both (i) had logarithmic signature size in N , and (ii) was secure in the plain model.
- The work of Backes et al.
- (EUROCRYPT’19) resolved both these issues.
- However, threshold ring signatures have their own particular problem: with a threshold t ≥ 1, signers must often reveal their identities to the other signers as part of the signing process.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770128 (1).pdf`
- `downloads/131770128.pdf`
