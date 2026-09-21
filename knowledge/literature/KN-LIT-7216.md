---
id: KN-LIT-7216
type: literature
title: "Towards KEM Unification"
authors:
  - "Daniel J. Bernstein"
  - "Edoardo Persichetti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, mov-fr, pairing, pqc, protocol, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper highlights a particular construction of a correct KEM without failures and without ciphertext expansion from any correct deterministic PKE, and presents a simple tight proof of ROM IND-CCA2 security for the KEM assuming merely OW-CPA security for the PKE. Compared to previous proofs, this proof is simpler, and is also factored into smaller pieces that can be audited independently.

## Key claims (as reported)
- In particular, this paper introduces the notion of “IND-Hash” security and shows that this allows a new separation between checking encryptions and randomizing decapsulations.
- The KEM is easy to implement in constant time, given a constant-time implementation of the PKE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/tightkem-20180528.pdf`
