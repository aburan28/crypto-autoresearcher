---
id: KN-LIT-2782
type: literature
title: "Bounded-Collusion IBE from Key Homomorphism"
authors:
  - "Shafi Goldwasser"
  - "Allison Lewko"
  - "David A. Wilson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we show how to construct IBE schemes that are secure against a bounded number of collusions, starting with underlying PKE schemes which possess linear homomorphisms over their keys. In particular, this enables us to exhibit a new (bounded-collusion) IBE construction based on the quadratic residuosity assumption, without any need to assume the existence of random oracles.

## Key claims (as reported)
- The new IBE’s public parameters are of size O(tλ log I) where I is the total number of identities which can be supported by the system, t is the number of collusions which the system is secure against, and λ is a security parameter.
- While the number of collusions is bounded, we note that an exponential number of total identities can be supported.
- More generally, we give a transformation that takes any PKE satisfying Linear Key Homomorphism, Identity Map Compatibility, and the Linear Hash Proof Property and translates it into an IBE secure against bounded collusions.
- We demonstrate that these properties are more general than our quadratic residuosity-based scheme by showing how a simple PKE based on the DDH assumption also satisfies these properties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940201 (1).pdf`
- `downloads/71940201 (2).pdf`
- `downloads/71940201 (3).pdf`
- `downloads/71940201.pdf`
