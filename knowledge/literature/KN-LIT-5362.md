---
id: KN-LIT-5362
type: literature
title: "On Lightweight Stream Ciphers with Shorter Internal States"
authors:
  - "Frederik Armknecht"
  - "Vasily Mikhalev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To be resistant against certain time-memory-data-tradeoff (TMDTO) attacks, a common rule of thumb says that the internal state size of a stream cipher should be at least twice the security parameter. As memory gates are usually the most area and power consuming components, this implies a sever limitation with respect to possible lightweight implementations.

## Key claims (as reported)
- In this work, we revisit this rule.
- We argue that a simple shift in the established design paradigm, namely to involve the fixed secret key not only in the initialization process but in the keystream generation phase as well, enables stream ciphers with smaller area size for two reasons.
- First, it improves the resistance against the mentioned TMDTO attacks which allows to choose smaller state sizes.
- Second, one can make use of the fact that storing a fixed value (here: the key) requires less area size than realizing a register of the same length.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400108 (1).pdf`
- `downloads/85400108.pdf`
