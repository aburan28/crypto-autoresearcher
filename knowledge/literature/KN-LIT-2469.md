---
id: KN-LIT-2469
type: literature
title: An Asymptotically Optimal Method for Converting Bit Encryption to Multi-Bit Encryption
authors:
- Takahiro Matsuda
- Goichiro Hanaoka
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- public-key
- provable-security
- key-encapsulation
- foundations
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
Myers and Shelat (FOCS 2009) showed how to convert a chosen ciphertext secure (CCA secure) PKE scheme that can encrypt only 1-bit plaintexts into a CCA secure scheme that can encrypt arbitrarily long plaintexts (via the notion of key encapsulation mechanism (KEM) and hybrid encryption), and subsequent works improved efficiency and simplicity. In terms of efficiency, the best known construction of a CCA secure KEM from a CCA secure 1-bit PKE scheme, has the public key size Ω(k) · |pk| and the ciphertext size Ω(k2 ) · |c|, where k is a security parameter, and |pk| and |c| denote the public key size and the ciphertext size of the underlying 1-bit scheme, respectively.

## Key claims (as reported)
- In this paper, we show a new CCA secure KEM based on a CCA secure 1-bit PKE scheme which achieves the public key size 2 · |pk| and the ciphertext size (2k + o(k)) · |c|.
- These sizes are asymptotically optimal in the sense that they are the same as those of the simplest “bitwiseencrypt” construction (seen as a KEM by encrypting a k-bit random session-key) that works for the chosen plaintext attack and non-adaptive chosen ciphertext attack settings.
- We achieve our main result by developing several new techniques and results on the “double-layered” construction (which builds a KEM from an inner PKE/KEM and an outer PKE scheme) by Myers and Shelat and on the notion of detectable PKE/KEM by Hohenberger, Lewko, and Waters (EUROCRYPT 2012).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520132 (1).pdf`
- `downloads/94520132.pdf`
