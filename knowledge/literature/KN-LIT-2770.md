---
id: KN-LIT-2770
type: literature
title: "Bootstrapping BGV Ciphertexts with a Wider Choice of p and q"
authors:
  - "E. Orsini"
  - "J. van de Pol"
  - "N.P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, fhe, finite-field, implementation, lattice, number-theory, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a method to bootstrap a packed BGV ciphertext which does not depend (as much) on any special properties of the plaintext and ciphertext moduli. Prior “efficient” methods such as that of Gentry et al (PKC 2012) required a ciphertext modulus q which was close to a power of the plaintext modulus p.

## Key claims (as reported)
- This enables our method to be applied in a larger number of situations.
- Also unlike previous methods our depth grows only as O(log p+log log q) as opposed to the log q of previous methods.
- Our basic bootstrapping technique makes use of a representation of the group Z+ q over the finite field Fp (either based on polynomials or elliptic curves), followed by polynomial interpolation of the reduction mod p map over the coefficients of the algebraic group.
- This technique is then extended to the full BGV packed ciphertext space, using a method whose depth depends only logarithmically on the number of packed elements.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200107 (1).pdf`
- `downloads/90200107 (2).pdf`
- `downloads/90200107 (3).pdf`
- `downloads/90200107 (4).pdf`
- `downloads/90200107.pdf`
