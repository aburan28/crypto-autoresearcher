---
id: KN-LIT-6518
type: literature
title: "Security of Keyed Sponge Constructions Using a Modular Proof Approach"
authors:
  - "Elena Andreeva"
  - "Joan Daemen"
  - "Bart Mennink"
  - "Gilles Van Assche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Sponge functions were originally proposed for hashing, but find increasingly more applications in keyed constructions, such as encryption and authentication. Depending on how the key is used we see two main types of keyed sponges in practice: inner - and outer -keyed.

## Key claims (as reported)
- Earlier security bounds, mostly due to the well-known sponge indifferentiability result, guarantee a security level of c/2 bits with c the capacity.
- We reconsider these two keyed sponge versions and derive improved bounds in the classical indistinguishability setting as well as in an extended setting where the adversary targets multiple instances at the same time.
- For cryptographically significant parameter values, the expected workload for an attacker to be successful in an n-target attack against the outer-keyed sponge is the minimum over 2k /n and 2c /μ with k the key length and μ the total maximum multiplicity.
- For the inner-keyed sponge this simplifies to 2k /μ with maximum security if k = c.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400158 (1).pdf`
- `downloads/85400158.pdf`
