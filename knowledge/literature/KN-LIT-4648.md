---
id: KN-LIT-4648
type: literature
title: "Lattice-Based Fully Dynamic Multi-Key FHE with Short Ciphertexts"
authors:
  - "Zvika Brakerski"
  - "Renen Perlman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a multi-key fully homomorphic encryption scheme that supports an unbounded number of homomorphic operations for an unbounded number of parties. Namely, it allows to perform arbitrarily many computational steps on inputs encrypted by an a-priori unbounded (polynomial) number of parties.

## Key claims (as reported)
- Inputs from new parties can be introduced into the computation dynamically, so the final set of parties needs not be known ahead of time.
- Furthermore, the length of the ciphertexts, as well as the space complexity of an atomic homomorphic operation, grow only linearly with the current number of parties.
- Prior works either supported only an a-priori bounded number of parties (López-Alt, Tromer and Vaikuntanthan, STOC ’12), or only supported single-hop evaluation where all inputs need to be known before the computation starts (Clear and McGoldrick, Crypto ’15, Mukherjee and Wichs, Eurocrypt ’16).
- In all aforementioned works, the ciphertext length grew at least quadratically with the number of parties.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140188 (1).pdf`
- `downloads/98140188.pdf`
