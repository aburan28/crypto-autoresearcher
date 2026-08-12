---
id: KN-LIT-6339
type: literature
title: "Round-Robin is Optimal: Lower Bounds for Group Action Based Protocols"
authors:
  - "Daniele Cozzo"
  - "Emanuele Giunta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, isogeny, mpc, pairing, pqc, protocol, quantum, sidh-csidh, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An hard homogeneous space (HHS) is a finite group acting on a set with the group action being hard to invert and the set lacking any algebraic structure. As such HHS could potentially replace finite groups where the discrete logarithm is hard for building cryptographic primitives and protocols in a post-quantum world.

## Key claims (as reported)
- Threshold HHS-based primitives typically require parties to compute the group action of a secret-shared input on a public set element.
- On one hand this could be done through generic MPC techniques, although they incur in prohibitive costs due to the high complexity of circuits evaluating group actions known to date.
- On the other hand round-robin protocols only require black box usage of the HHS.
- However these are highly sequential procedures, taking as many rounds as parties involved.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369125 (1).pdf`
- `downloads/14369125.pdf`
