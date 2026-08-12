---
id: KN-LIT-4436
type: literature
title: "Improved Setup Assumptions for 3-Round Resettable Zero Knowledge"
authors:
  - "Giovanni Di Crescenzo"
  - "Giuseppe Persiano"
  - "Ivan Visconti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the bare public-key model, introduced by Canetti et al. [STOC 2000], it is only assumed that each verifier deposits during a setup phase a public key in a file accessible by all users at all times.

## Key claims (as reported)
- As pointed out by Micali and Reyzin [Crypto 2001], the notion of soundness in this model is more subtle and complex than in the classical model.
- Indeed Micali and Reyzin have introduced four different notions which are called (from weaker to stronger): one-time, sequential, concurrent and resettable soundness.
- In this paper we introduce the counter public-key model (the cPK model for short), an augmentation of the bare public-key model in which each verifier is equipped with a counter and, like in the original bare public-key model, the key of the verifier can be used for any polynomial number of interactions with provers.
- In the cPK model, we give a three-round concurrently-sound resettable zero-knowledge argument of membership for NP.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33290521 (1).pdf`
- `downloads/33290521 (2).pdf`
- `downloads/33290521 (3).pdf`
- `downloads/33290521.pdf`
