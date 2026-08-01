---
id: KN-LIT-4332
type: literature
title: "Identity-Based Aggregate Signatures"
authors:
  - "Craig Gentry"
  - "Zulfikar Ramzan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, mov-fr, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An aggregate signature is a single short string that convinces any verifier that, for all 1 ≤ i ≤ n, signer Si signed message Mi , where the n signers and n messages may all be distinct. The main motivation of aggregate signatures is compactness.

## Key claims (as reported)
- However, while the aggregate signature itself may be compact, aggregate signature verification might require potentially lengthy additional information – namely, the (at most) n distinct signer public keys and the (at most) n distinct messages being signed.
- If the verifier must obtain and/or store this additional information, the primary benefit of aggregate signatures is largely negated.
- This paper initiates a line of research whose ultimate objective is to find a signature scheme in which the total information needed to verify is minimized.
- In particular, the verification information should preferably be as close as possible to the theoretical minimum: the complexity of describing which signer(s) signed what message(s).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580260 (1).pdf`
- `downloads/39580260 (2).pdf`
- `downloads/39580260 (3).pdf`
- `downloads/39580260.pdf`
