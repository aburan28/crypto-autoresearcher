---
id: KN-LIT-2656
type: literature
title: "Basing PRFs on Constant-Query Weak PRFs: Minimizing Assumptions for Efficient Symmetric Cryptography?"
authors:
  - "Ueli Maurer"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Although it is well known that all basic private-key cryptographic primitives can be built from one-way functions, finding weak assumptions from which practical implementations of such primitives exist remains a challenging task. Towards this goal, this paper introduces the notion of a constant-query weak PRF, a function with a secret key which is computationally indistinguishable from a truly random function when evaluated at a constant number s of known random inputs, where s can be as small as two.

## Key claims (as reported)
- We provide iterated constructions of (arbitrary-input-length) PRFs from constant-query weak PRFs that even improve the efficiency of previous constructions based on the stronger assumption of a weak PRF (where polynomially many evaluations are allowed).
- One of our constructions directly provides a new mode of operation using a constant-query weak PRF for IND-CPA symmetric encryption which is essentially as efficient as conventional PRF-based counter-mode encryption.
- Furthermore, our constructions yield efficient modes of operation for keying hash functions (such as MD5 and SHA-1) to obtain iterated PRFs (and hence MACs) which rely solely on the assumption that the underlying compression function is a constant-query weak PRF, which is the weakest assumption ever considered in this context.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500166 (1).pdf`
- `downloads/53500166 (2).pdf`
- `downloads/53500166 (3).pdf`
- `downloads/53500166.pdf`
