---
id: KN-LIT-3275
type: literature
title: "Cryptanalysis of the NTRU Signature Scheme (NSS) from Eurocrypt 2001"
authors:
  - "Craig Gentry"
  - "Jakob Jonsson"
  - "Jacques Stern"
  - "Michael Szydlo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 1996, a new cryptosystem called NTRU was introduced, related to the hardness of finding short vectors in specific lattices. At Eurocrypt 2001, the NTRU Signature Scheme (NSS), a signature scheme apparently related to the same hard problem, was proposed.

## Key claims (as reported)
- In this paper, we show that the problem on which NSS relies is much easier than anticipated, and we describe an attack that allows efficient forgery of a signature on any message.
- Additionally, we demonstrate that a transcript of signatures leaks information about the secret key: using a correlation attack, it is possible to recover the key from a few tens of thousands of signatures.
- The attacks apply to the recently proposed parameter sets NSS251-3-SHA1-1, NSS347-3-SHA1-1, and NSS503-3-SHA1-1 in [2].
- Following the attacks, NTRU researchers have investigated enhanced encoding/verification methods in [11].

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/22480001 (1).pdf`
- `downloads/22480001 (2).pdf`
- `downloads/22480001.pdf`
