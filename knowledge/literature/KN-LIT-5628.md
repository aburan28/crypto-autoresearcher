---
id: KN-LIT-5628
type: literature
title: "One-Time Computable Self-Erasing Functions?"
authors:
  - "Stefan Dziembowski"
  - "Tomasz Kazana"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, provable-security, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper studies the design of cryptographic schemes that are secure even if implemented on untrusted machines that fall under adversarial control. For example, this includes machines that are infected by a software virus.

## Key claims (as reported)
- We introduce a new cryptographic notion that we call a one-time computable pseudorandom function (PRF), which is a PRF FK (·) that can be evaluated on at most one input, even by an adversary who controls the device storing the key K, as long as: (1) the adversary cannot “leak” the key K out of the device completely (this is similar to the assumptions made in the Bounded-Retrieval Model), and (2) the local read/write memory of the machine is restricted, and not too much larger than the size of K.
- In particular, the only way to evaluate FK (x) on such device, is to overwrite part of the key K during the computation, thus preventing all future evaluations of FK (·) at any other point x0 6= x.
- We show that this primitive can be used to construct schemes for password protected storage that are secure against dictionary attacks, even by a virus that infects the machine.
- Our constructions rely on the random-oracle model, and lower-bounds for graphs pebbling problems.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970124 (1).pdf`
- `downloads/65970124 (2).pdf`
- `downloads/65970124 (3).pdf`
- `downloads/65970124.pdf`
