---
id: KN-LIT-5486
type: literature
title: "On the Impact of Known-Key Attacks on Hash Functions"
authors:
  - "Bart Mennink"
  - "Bart Preneel"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Hash functions are often constructed based on permutations or blockciphers, and security proofs are typically done in the ideal permutation or cipher model. However, once these random primitives are instantiated, vulnerabilities of these instantiations may nullify the security.

## Key claims (as reported)
- At ASIACRYPT 2007, Knudsen and Rijmen introduced known-key security of blockciphers, which gave rise to many distinguishing attacks on existing blockcipher constructions.
- In this work, we analyze the impact of such attacks on primitive-based hash functions.
- We present and formalize the weak cipher model, which captures the case a blockcipher has a certain weakness but is perfectly random otherwise.
- A specific instance of this model, considering the existence of sets of B queries whose XOR equals 0 at bit-positions C, where C is an index set, covers a wide range of known-key attacks in literature.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520234 (1).pdf`
- `downloads/94520234.pdf`
