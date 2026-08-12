---
id: KN-LIT-7138
type: literature
title: "Tight Time-Memory Trade-offs for Symmetric Encryption"
authors:
  - "Joseph Jaeger"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Concrete security proofs give upper bounds on the attacker’s advantage as a function of its time/query complexity. Cryptanalysis suggests however that other resource limitations – most notably, the attacker’s memory – could make the achievable advantage smaller, and thus these proven bounds too pessimistic.

## Key claims (as reported)
- Yet, handling memory limitations has eluded existing security proofs.
- This paper initiates the study of time-memory trade-offs for basic symmetric cryptography.
- We show that schemes like counter-mode encryption, which are affected by the Birthday Bound, become more secure (in terms of time complexity) as the attacker’s memory is reduced.
- One key step of this work is a generalization of the Switching Lemma: For adversaries with S bits of memory issuing q distinct queries, we prove an n-to-n bit random function indistinguishable from a permutation as long as S ˆq !

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760325 (1).pdf`
- `downloads/114760325.pdf`
