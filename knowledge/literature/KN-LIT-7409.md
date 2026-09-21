---
id: KN-LIT-7409
type: literature
title: "Universally Composable Symbolic Analysis for Two-Party Protocols based on Homomorphic Encryption"
authors:
  - "Morten Dahl"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mpc, protocol, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a class of two-party function evaluation protocols in which the parties are allowed to use ideal functionalities as well as a set of powerful primitives, namely commitments, homomorphic encryption, and certain zero-knowledge proofs. With these it is possible to capture protocols for oblivious transfer, coin-flipping, and generation of multiplication-triples.

## Key claims (as reported)
- We show how any protocol in our class can be compiled to a symbolic representation expressed as a process in an abstract process calculus, and prove a general computational soundness theorem implying that if the protocol realises a given ideal functionality in the symbolic setting, then the original version also realises the ideal functionality in the standard computational UC setting.
- In other words, the theorem allows us to transfer a proof in the abstract symbolic setting to a proof in the standard UC model.
- Finally, we have verified that the symbolic interpretation is simple enough in a number of cases for the symbolic proof to be partly automated using the ProVerif tool.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410127 (1).pdf`
- `downloads/84410127 (2).pdf`
- `downloads/84410127 (3).pdf`
- `downloads/84410127.pdf`
