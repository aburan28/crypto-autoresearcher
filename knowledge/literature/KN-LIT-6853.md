---
id: KN-LIT-6853
type: literature
title: "Structure-Preserving Smooth Projective Hashing"
authors:
  - "Olivier Blazy"
  - "Céline Chevalier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, mpc, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Smooth projective hashing has proven to be an extremely useful primitive, in particular when used in conjunction with commitments to provide implicit decommitment. This has lead to applications proven secure in the UC framework, even in presence of an adversary which can do adaptive corruptions, like for example Password Authenticated Key Exchange (PAKE), and 1-out-of-m Oblivious Transfer (OT).

## Key claims (as reported)
- However such solutions still lack in efficiency, since they heavily scale on the underlying message length.
- Structure-preserving cryptography aims at providing elegant and efficient schemes based on classical assumptions and standard group operations on group elements.
- Recent trend focuses on constructions of structurepreserving signatures, which require message, signature and verification keys to lie in the base group, while the verification equations only consist of pairing-product equations.
- Classical constructions of Smooth Projective Hash Function suffer from the same limitation as classical signatures: at least one part of the computation (messages for signature, witnesses for SPHF) is a scalar.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031131 (1).pdf`
- `downloads/10031131.pdf`
