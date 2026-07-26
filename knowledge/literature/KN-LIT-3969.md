---
id: KN-LIT-3969
type: literature
title: "From Selective to Full Security: Semi-Generic Transformations in the Standard Model"
authors:
  - "Michel Abdalla"
  - "Dario Fiore⋆"
  - "Vadim Lyubashevsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose an efficient, standard model, semigeneric transformation of selective-secure (Hierarchical) Identity-Based Encryption schemes into fully secure ones. The main step is a procedure that uses admissible hash functions (whose existence is implied by collision-resistant hash functions) to convert any selective-secure wildcarded identity-based encryption (WIBE) scheme into a fully secure (H)IBE scheme.

## Key claims (as reported)
- Since building a selective-secure WIBE, especially with a selective-secure HIBE already in hand, is usually much less involved than directly building a fully secure HIBE, this transform already significantly simplifies the latter task.
- This black-box transformation easily extends to schemes secure in the Continual Memory Leakage (CML) model of Brakerski et al.
- (FOCS 2010), which allows us obtain a new fully secure IBE in that model.
- We furthermore show that if a selective-secure HIBE scheme satisfies a particular security notion, then it can be generically transformed into a selective-secure WIBE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930318 (1).pdf`
- `downloads/72930318 (2).pdf`
- `downloads/72930318 (3).pdf`
- `downloads/72930318.pdf`
