---
id: KN-LIT-3601
type: literature
title: "Efficient Oblivious Pseudorandom Function with Applications to Adaptive OT and Secure Computation of Set Intersection"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An Oblivious Pseudorandom Function (OPRF) [15] is a two-party protocol between sender S and receiver R for securely computing a pseudorandom function fk (·) on key k contributed by S and input x contributed by R, in such a way that receiver R learns only the value fk (x) while sender S learns nothing from the interaction. In other words, an OPRF protocol for PRF fk (·) is a secure computation for functionality FOPRF : (k, x) → (⊥, fk (x)).

## Key claims (as reported)
- We propose an OPRF protocol on committed inputs which requires only O(1) modular exponentiations, and has a constant number of communication rounds (two in ROM).
- Our protocol is secure in the CRS model under the Composite Decisional Residuosity (CDR) assumption, while the PRF itself is secure on a polynomially-sized domain under the Decisional q-Diffie-Hellman Inversion assumption on a group of composite order, where q is the size of the PRF domain, and it has a useful feature that fk is an injection for every k.
- A practical OPRF protocol for an injective PRF, even limited to a polynomiallysized domain, is a versatile tool with many uses in secure protocol design.
- We show that our OPRF implies a new practical fully-simulatable adaptive (and committed) OT protocol secure without ROM.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440575 (1).pdf`
- `downloads/54440575 (2).pdf`
- `downloads/54440575 (3).pdf`
- `downloads/54440575.pdf`
