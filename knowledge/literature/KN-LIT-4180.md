---
id: KN-LIT-4180
type: literature
title: "Herding Hash Functions and the Nostradamus Attack"
authors:
  - "John Kelsey"
  - "Tadayoshi Kohno"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we develop a new attack on Damgård-Merkle hash functions, called the herding attack, in which an attacker who can find many collisions on the hash function by brute force can first provide the hash of a message, and later “herd” any given starting part of a message to that hash value by the choice of an appropriate suffix. We focus on a property which hash functions should have–Chosen Target Forced Prefix (CTFP) preimage resistance–and show the distinction between Damgård-Merkle construction hashes and random oracles with respect to this property.

## Key claims (as reported)
- We describe a number of ways that violation of this property can be used in arguably practical attacks on real-world applications of hash functions.
- An important lesson from these results is that hash functions susceptible to collision-finding attacks, especially brute-force collision-finding attacks, cannot in general be used to prove knowledge of a secret value.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040184 (1).pdf`
- `downloads/40040184 (2).pdf`
- `downloads/40040184 (3).pdf`
- `downloads/40040184.pdf`
