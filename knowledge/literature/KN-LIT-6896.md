---
id: KN-LIT-6896
type: literature
title: "Super-Linear Time-Memory Trade-Offs for Symmetric Encryption"
authors:
  - "Wei Dai "
  - "Stefano Tessaro"
  - "Xihu Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We build symmetric encryption schemes from a pseudorandom function/permutation with domain size N which have very high security – in terms of the amount of messages q they can securely encrypt – assuming the adversary has S N bits of memory. We aim to minimize the number of calls k we make to the underlying primitive to achieve a certain q, or equivalently, to maximize the achievable q for a given k.

## Key claims (as reported)
- We target in particular q " N , in contrast to recent works (Jaeger and Tessaro, EUROCRYPT ’19; Dinur, EUROCRYPT ? ’20) which aim to beat the birthday barrier with one call when S N.
- Our first result gives new and explicit bounds for the Sample-thenExtract paradigm by Tessaro and Thiruvengadam (TCC ’18).
- We show  instantiations for which q  Ω pN {S qk .
- If S N 1α , Thiruvengadam and Tessaro’s weaker bounds only guarantee q ¡ N when k  Ω plog N q.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550214 (1).pdf`
- `downloads/12550214.pdf`
