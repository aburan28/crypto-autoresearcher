---
id: KN-LIT-5971
type: literature
title: "Provably Robust Sponge-Based PRNGs and KDFs"
authors:
  - "Peter Gaži"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of devising provably secure PRNGs with input based on the sponge paradigm. Such constructions are very appealing, as efficient software/hardware implementations of SHA-3 can easily be translated into a PRNG in a nearly black-box way.

## Key claims (as reported)
- The only existing sponge-based construction, proposed by Bertoni et al.
- (CHES 2010), fails to achieve the security notion of robustness recently considered by Dodis et al.
- (CCS 2013), for two reasons: (1) The construction is deterministic, and thus there are high-entropy input distributions on which the construction fails to extract random bits, and (2) The construction is not forward secure, and presented solutions aiming at restoring forward security have not been rigorously analyzed.
- We propose a seeded variant of Bertoni et al.’s PRNG with input which we prove secure in the sense of robustness, delivering in particular concrete security bounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650262 (1).pdf`
- `downloads/96650262.pdf`
