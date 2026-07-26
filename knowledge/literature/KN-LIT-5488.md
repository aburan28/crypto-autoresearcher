---
id: KN-LIT-5488
type: literature
title: "On the Implementation of a Fast Prime Generation Algorithm"
authors:
  - "Christophe Clavier"
  - "Jean-Sébastien Coron"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A side-channel analysis of a cryptographic algorithm generally concentrates on the encryption or decryption phases, rarely on the key generation phase. In this paper, we show that, when not properly implemented, the fast prime generation algorithm proposed by Joye and Paillier at CHES 2006 is susceptible to side-channel analysis; its main application is the generation of RSA key-pairs for embedded platforms like smart-cards.

## Key claims (as reported)
- Our attack assumes that some parity bit can be recovered through SPA when it appears in a branch condition.
- Our attack can be combined with Coppersmith’s theorem to improve its efficiency; we show that for 1024-bit RSA moduli, one can recover the factorization of roughly 1/1000 of the RSA moduli.
- Key-words : Simple Power Analysis, Prime generation algorithm, Coppersmith’s theorem.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270443 (1).pdf`
- `downloads/47270443 (2).pdf`
- `downloads/47270443 (3).pdf`
- `downloads/47270443.pdf`
