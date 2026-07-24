---
id: KN-LIT-060
type: literature
title: Fully Homomorphic Encryption Using Ideal Lattices
authors: [Gentry Craig]
year: 2009
venue: STOC 2009, pp. 169-178
identifiers:
  eprint: null
  doi: 10.1145/1536414.1536440
  url: https://dl.acm.org/doi/10.1145/1536414.1536440
tags: [fhe, fully-homomorphic-encryption, ideal-lattice, bootstrapping, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The first fully homomorphic encryption (FHE) scheme, built from ideal lattices,
enabling evaluation of arbitrary circuits over ciphertexts. Its central technique
is *bootstrapping*: homomorphically evaluating the decryption circuit to refresh
ciphertext noise, allowing unbounded computation.

## Key claims (as reported)
- FHE from an average-case ideal-lattice problem plus the sparse subset-sum
  problem; bootstrapping turns a "somewhat homomorphic" scheme into a fully
  homomorphic one.
- A landmark feasibility result; later schemes (BGV, GSW, ...) improved
  efficiency and assumptions.

## Relevance to this program
POST-QUANTUM construction, ADJACENT to (not part of) the ECDLP mission. Recorded
as context for the lattice-crypto map: FHE is the flagship "advanced primitive"
that lattices enable and elliptic-curve/discrete-log crypto does not. Unrelated to
ECDLP hardness; included for corpus completeness of the lattice landscape.

## Not verified here
Full paper not read; the FHE/bootstrapping construction relayed from the abstract
(hence confidence: reported). Fields confirmed against the ACM DL DOI / DBLP
records via search, not by fetching the primary page.
