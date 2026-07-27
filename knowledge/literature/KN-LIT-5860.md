---
id: KN-LIT-5860
type: literature
title: "Practical Security Analysis of PUF-based Two-Player Protocols"
authors:
  - "Ulrich Rührmair ∗"
  - "Marten van Dijk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, mpc, protocol, provable-security, quantum, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent years, PUF-based schemes have not only been suggested for the basic tasks of tamper sensitive key storage or the identification of hardware systems, but also for more complex protocols like oblivious transfer (OT) or bit commitment (BC), both of which possess broad and diverse applications. In this paper, we continue this line of research.

## Key claims (as reported)
- We first present an attack on two recent OT- and BC-protocols which have been introduced at CRYPTO 2011 by Brzuska et al.
- The attack quadratically reduces the number of CRPs which malicious players must read out in order to cheat, and fully operates within the original communication model of [1, 2].
- In practice, this leads to insecure protocols when electrical PUFs with a medium challenge-length are used (e.g., 64 bits), or whenever optical PUFs are employed.
- These two PUF types are currently among the most popular designs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280249 (1).pdf`
- `downloads/74280249 (2).pdf`
- `downloads/74280249 (3).pdf`
- `downloads/74280249.pdf`
