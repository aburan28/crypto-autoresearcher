---
id: KN-LIT-3614
type: literature
title: "Efficient Pseudorandom Functions via On-the-Fly Adaptation"
authors:
  - "Nico Döttling"
  - "Dominique Schröder"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pseudorandom functions (PRFs) are one of the most fundamental building blocks in cryptography with numerous applications such as message authentication codes and private key encryption. In this work, we propose a new framework to construct PRFs with the overall goal to build efficient PRFs from standard assumptions with an almost tight proof of security.

## Key claims (as reported)
- The main idea of our framework is to start from a PRF for any small domain (i.e. poly-sized domain) and turn it into an `-bounded pseudorandom function, i.e., into a PRF whose outputs are pseudorandom for the first ` distinct queries to F .
- In the second step, we apply a novel technique which we call on-the-fly adaptation that turns any bounded PRF into a fully-fledged (large domain) PRF.
- Both steps of our framework have a tight security reduction, meaning that any successful attacker can be turned into an efficient algorithm for the underlying hard computational problem without any significant increase in the running time or loss of success probability.
- Instantiating our framework with specific number theoretic assumptions, we construct a PRF based on k-LIN (and thus DDH) that is faster than all known constructions, which reduces almost tightly to the underlying problem, and which has shorter keys.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160352 (1).pdf`
- `downloads/92160352 (2).pdf`
- `downloads/92160352.pdf`
