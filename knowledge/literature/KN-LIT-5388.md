---
id: KN-LIT-5388
type: literature
title: "On Rejection Sampling in Lyubashevsky’s Signature Scheme"
authors:
  - "Julien Devevey"
  - "Omar Fawzi"
  - "Alain Passelègue"
  - "Damien Stehlé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, pqc, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lyubashevsky’s signatures are based on the Fiat-Shamir with aborts paradigm, whose central ingredient is the use of rejection sampling to transform secret-dependent signature samples into samples from (or close to) a secret-independent target distribution. Several choices for the underlying distributions and for the rejection sampling strategy can be considered.

## Key claims (as reported)
- In this work, we study Lyubashevsky’s signatures through the lens of rejection sampling, and aim to minimize signature size given signing runtime requirements.
- Several of our results concern rejection sampling itself and could have other applications.
- We prove lower bounds for compactness of signatures given signing runtime requirements, and for expected runtime of perfect rejection sampling strategies.
- We also propose a Rényi-divergence-based analysis of Lyubashevsky’s signatures which allows for larger deviations from the target distribution, and show hyperball uniforms to be a good choice of distributions: they asymptotically reach our compactness lower bounds and offer interesting features for practical deployment.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910286 (1).pdf`
- `downloads/137910286.pdf`
