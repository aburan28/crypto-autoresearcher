---
id: KN-LIT-6721
type: literature
title: "SNARGs for Monotone Policy Batch NP"
authors:
  - "Zvika Brakerski"
  - "Maya Farber Brodsky"
  - "Yael Tauman Kalai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a succinct non-interactive argument (SNARG) for the class of monotone policy batch NP languages, under the Learning with Errors (LWE) assumption. This class is a subclass of NP that is associated with a monotone function f : {0, 1}k → {0, 1} and an NP language L, and contains instances (x1 , . . . , xk ) such that f (b1 , . . . , bk ) = 1 where bj = 1 if and only if xj ∈ L.

## Key claims (as reported)
- Our SNARGs are arguments of knowledge in the non-adaptive setting, and satisfy a new notion of somewhere extractability against adaptive adversaries.
- This is the first SNARG under standard hardness assumptions for a subclass of NP that is not known to have a (computational) non-signaling PCP with parameters compatible with the standard framework for constructing SNARGs dating back to [Kalai-Raz-Rothblum, STOC ’13].
- Indeed, our approach necessarily departs from this framework.
- Our construction combines existing quasi-arguments for NP (based on batch arguments for NP) with a new type of cryptographic encoding of the instance and a new analysis going from local to global soundness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850464 (1).pdf`
- `downloads/140850464.pdf`
