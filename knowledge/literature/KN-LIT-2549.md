---
id: KN-LIT-2549
type: literature
title: "Anonymous Identification in Ad Hoc Groups"
authors:
  - "Yevgeniy Dodis"
  - "Aggelos Kiayias"
  - "Antonio Nicolosi"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce Ad hoc Anonymous Identification schemes, a new multi-user cryptographic primitive that allows participants from a user population to form ad-hoc groups, and then prove membership anonymously in such groups. Our schemes are based on the notion of accumulator with one-way domain, a natural extension of cryptographic accumulators we introduce in this work.

## Key claims (as reported)
- We provide a formal model for Ad hoc Anonymous Identification schemes and design secure such schemes both generically (based on any accumulator with one-way domain) and for a specific efficient implementation of such an accumulator based on the Strong RSA Assumption.
- A salient feature of our approach is that all the identification protocols take time independent of the size of the ad-hoc group.
- All our schemes and notions can be generally and efficiently amended so that they allow the recovery of the signer’s identity by an authority, if the latter is desired.
- Using the Fiat-Shamir transform, we also obtain constant-size, signerambiguous group and ring signatures (provably secure in the Random Oracle Model).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ad_hoc_groups (1).pdf`
- `downloads/ad_hoc_groups (2).pdf`
- `downloads/ad_hoc_groups.pdf`
- `downloads/subring.pdf`
