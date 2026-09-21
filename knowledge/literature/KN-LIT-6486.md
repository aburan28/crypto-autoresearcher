---
id: KN-LIT-6486
type: literature
title: "Security Amplification for the Cascade of Arbitrarily Weak PRPs: Tight Bounds via the Interactive Hardcore Lemma"
authors:
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the task of amplifying the security of a weak pseudorandom permutation (PRP), called an ε-PRP, for which the computational distinguishing advantage is only guaranteed to be bounded by some (possibly non-negligible) quantity ε < 1. We prove that the cascade (i.e., sequential composition) of m ε-PRPs (with independent keys) is an ((m − (m − 1)ε)εm + ν)-PRP, where ν is a negligible function.

## Key claims (as reported)
- In the 1 asymptotic setting, this implies security amplification for all ε < 1 − poly , and the result extends to two-sided PRPs, where the inverse of the given permutation is also queried.
- Furthermore, we show that this result is essentially tight.
- This settles a long-standing open problem due to Luby and Rackoff (STOC ’86).
- Our approach relies on the first hardcore lemma for computational indistinguishability of interactive systems: Given two systems whose states do not depend on the interaction, and which no efficient adversary can distinguish with advantage better than ε, we show that there exist events on the choices of the respective states, occurring each with probability at least 1 − ε, such that the two systems are computationally indistinguishable conditioned on these events.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970037 (1).pdf`
- `downloads/65970037 (2).pdf`
- `downloads/65970037 (3).pdf`
- `downloads/65970037.pdf`
