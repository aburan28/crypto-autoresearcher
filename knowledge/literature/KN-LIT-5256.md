---
id: KN-LIT-5256
type: literature
title: Obfuscating Conjunctions
authors:
- Zvika Brakerski
- Guy N. Rothblum
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- obfuscation
- conjunctions
- provable-security
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
We show how to securely obfuscate the class of conjunction functions (functions like f (x1 , . . . , xn ) = x1 ∧ ¬x4 ∧ ¬x6 ∧ · · · ∧ xn−2 ). Given any function in the class, we produce an obfuscated program which preserves the input-output functionality of the given function, but reveals nothing else.

## Key claims (as reported)
- Our construction is based on multilinear maps, and can be instantiated using the recent candidates proposed by Garg, Gentry and Halevi (EUROCRYPT 2013) and by Coron, Lepoint and Tibouchi (CRYPTO 2013).
- We show that the construction is secure when the conjunction is drawn from a distribution, under mild assumptions on the distribution.
- Security follows from multilinear entropic variants of the Diffie-Hellman assumption.
- We conjecture that our construction is secure for any conjunction, regardless of the distribution from which it is drawn.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420305 (1).pdf`
- `downloads/80420305 (2).pdf`
- `downloads/80420305 (3).pdf`
- `downloads/80420305.pdf`
