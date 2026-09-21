---
id: KN-LIT-5359
type: literature
title: "On Instantiating Unleveled Fully-Homomorphic Signatures from Falsifiable Assumptions"
authors:
  - "Romain Gay"
  - "Bogdan Ursu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We build the first unleveled fully homomorphic signature scheme in the standard model. Our scheme is not constrained by any a-priori bound on the depth of the functions that can be homomorphically evaluated, and relies on subexponentially-secure indistinguishability obfuscation, fully-homomorphic encryption and a non-interactive zeroknowledge (NIZK) proof system with composable zero-knowledge.

## Key claims (as reported)
- Our scheme is also the first to satisfy the strong security notion of contexthiding for an unbounded number of levels, ensuring that signatures computed homomorphically do not leak the original messages from which they were computed.
- All building blocks are instantiable from falsifiable assumptions in the standard model, avoiding the need for knowledge assumptions.
- The main difficulty we overcome stems from the fact that bootstrapping, which is a crucial tool for obtaining unleveled fully homomorphic encryption (FHE), has no equivalent for homomorphic signatures, requiring us to use novel techniques.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602170 (1).pdf`
- `downloads/14602170.pdf`
