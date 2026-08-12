---
id: KN-LIT-2757
type: literature
title: "Blockwise-Adaptive Attackers Revisiting the (in)security of some provably secure Encryption Modes: CBC, GEM, IACBC"
authors:
  - "Antoine Joux"
  - "Gwenaëlle Martinet"
  - "Frédéric Valette"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we show that the natural and most common way of implementing modes of operation for cryptographic primitives often leads to insecure implementations. We illustrate this problem by attacking several modes of operation that were proved to be semantically secure against either chosen plaintext or chosen ciphertext attacks.

## Key claims (as reported)
- The problem stems from the simple following fact: in the definition and proofs of semantic security, messages are considered as atomic objects that cannot be split; however, in most practical implementations, messages are subdivided into smaller chunks than can be easily manipulated.
- Depending on the implementation, each chunk may consist of one or several blocks of the underlying primitive.
- The key point here is that upon reception of a processed chunk, the attacker can now adapt his choice for the next chunk.
- Since the possibility of adapting within a single message is not taken into account in the current security models, this leaves room for unexpected attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420017 (1).pdf`
- `downloads/24420017 (2).pdf`
- `downloads/24420017.pdf`
