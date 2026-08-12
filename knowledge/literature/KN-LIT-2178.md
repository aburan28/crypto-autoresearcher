---
id: KN-LIT-2178
type: literature
title: "A PCP Theorem for Interactive Proofs and Applications"
authors:
  - "Gal Arnon⋆"
  - "Alessandro Chiesa⋆⋆"
  - "Eylon Yogev⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The celebrated PCP Theorem states that any language in NP can be decided via a verifier that reads O(1) bits from a polynomially long proof. Interactive oracle proofs (IOP), a generalization of PCPs, allow the verifier to interact with the prover for multiple rounds while reading a small number of bits from each prover message.

## Key claims (as reported)
- While PCPs are relatively well understood, the power captured by IOPs (beyond NP) has yet to be fully explored.
- We present a generalization of the PCP theorem for interactive languages.
- We show that any language decidable by a k(n)-round IP has a k(n)round public-coin IOP, where the verifier makes its decision by reading only O(1) bits from each (polynomially long) prover message and O(1) bits from each of its own (random) messages to the prover.
- Our result and the underlying techniques have several applications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760226 (1).pdf`
- `downloads/132760226.pdf`
