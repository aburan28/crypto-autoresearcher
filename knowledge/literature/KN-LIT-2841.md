---
id: KN-LIT-2841
type: literature
title: "Careful with Composition: Limitations of the Indifferentiability Framework"
authors:
  - "Thomas Ristenpart"
  - "Hovav Shacham"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We exhibit a hash-based storage auditing scheme which is provably secure in the random-oracle model (ROM), but easily broken when one instead uses typical indifferentiable hash constructions. This contradicts the widely accepted belief that the indifferentiability composition theorem from [27] applies to any cryptosystem.

## Key claims (as reported)
- We characterize the uncovered limitations of indifferentiability by showing that the formalizations used thus far implicitly exclude security notions captured by experiments that have multiple, disjoint adversarial stages.
- Examples include deterministic public-key encryption (PKE), password-based cryptography, hash function nonmalleability, and more.
- We formalize a stronger notion, reset indifferentiability, that enables a composition theorem covering such multi-stage security notions, but our results show that practical hash constructions cannot be reset indifferentiable.
- We finish by giving direct security proofs for several important PKE schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320491 (1).pdf`
- `downloads/66320491 (2).pdf`
- `downloads/66320491 (3).pdf`
- `downloads/66320491.pdf`
