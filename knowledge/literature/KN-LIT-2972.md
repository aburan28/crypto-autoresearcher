---
id: KN-LIT-2972
type: literature
title: "Combiners for Backdoored Random Oracles"
authors:
  - "Balthazar Bauer"
  - "Pooya Farshim"
  - "Sogol Mazaheri"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We formulate and study the security of cryptographic hash functions in the backdoored random-oracle (BRO) model, whereby a big brother designs a “good” hash function, but can also see arbitrary functions of its table via backdoor capabilities. This model captures intentional (and unintentional) weaknesses due to the existence of collisionfinding or inversion algorithms, but goes well beyond them by allowing, for example, to search for structured preimages.

## Key claims (as reported)
- The latter can easily break constructions that are secure under random inversions.
- BROs make the task of bootstrapping cryptographic hardness somewhat challenging.
- Indeed, with only a single arbitrarily backdoored function no hardness can be bootstrapped as any construction can be inverted.
- However, when two (or more) independent hash functions are available, hardness emerges even with unrestricted and adaptive access to all backdoor oracles.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993444 (1).pdf`
- `downloads/10993444.pdf`
