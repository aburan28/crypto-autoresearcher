---
id: KN-LIT-6678
type: literature
title: "Simulatable Commitments and Efficient Concurrent Zero-Knowledge"
authors:
  - "Daniele Micciancio"
  - "Erez Petrank"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define and construct simulatable commitments. These are commitment schemes such that there is an efficient interactive proof system to show that a given string c is a legitimate commitment on a given value v, and furthermore, this proof is efficiently simulatable given any proper pair (c, v).

## Key claims (as reported)
- Our construction is provably secure based on the Decisional Diffie-Hellman (DDH) assumption.
- Using simulatable commitments, we show how to efficiently transform any public coin honest verifier zero knowledge proof system into a proof system that is concurrent zero-knowledge with respect to any (possibly cheating) verifier via black box simulation.
- By efficient we mean that our transformation incurs only an additive overhead (both in terms of the number of rounds and the computational and communication complexity of each round), and the additive term is close to optimal (for black box simulation): only ω(log n) additional rounds, and ω(log n) additional public key operations for each round of the original protocol, where n is a security parameter, and ω(log n) can be any superlogarithmic function of n independent of the complexity of the original protocol.
- The transformation preserves (up to negligible additive terms) the soundness and completeness error probabilities, and the new proof system is proved secure based on the DDH assumption, in the standard model of computation, i.e., no random oracles, shared random strings, or public key infrastructure is assumed.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560140 (1).pdf`
- `downloads/26560140 (2).pdf`
- `downloads/26560140.pdf`
