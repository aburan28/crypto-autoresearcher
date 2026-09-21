---
id: KN-LIT-7054
type: literature
title: "The Relationship between Password-Authenticated Key Exchange and Other Cryptographic Primitives"
authors:
  - "Minh-Huyen Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of password-authenticated key exchange (PAK) also known as session-key generation using passwords: constructing session-key generation protocols that are secure against active adversaries (person-in-the-middle) and only require the legitimate parties to share a low-entropy password (e.g. coming from a dictionary of size poly(n)). We study the relationship between PAK and other cryptographic primitives.

## Key claims (as reported)
- The main result of this paper is that password-authenticated key exchange and public-key encryption are incomparable under black-box reductions.
- In addition, we strengthen previous results by Halevi and Krawczyk [14] and Boyarsky [5] and show how to build key agreement and semi-honest oblivious transfer from any PAK protocol that is secure for the Goldreich-Lindell (GL) definition [11].
- We highlight the difference between two existing definitions of PAK, namely the indistinguishability-based definition of Bellare, Pointcheval and Rogaway (BPR) [1] and the simulation-based definition of Goldreich and Lindell [11] by showing that there exists a PAK protocol that is secure for the BPR definition and only assumes the existence of one-way functions in the case of exponential-sized dictionaries.
- Hence, unlike the GL definition, the BPR definition does not imply semi-honest oblivious transfer for exponental-sized dictionaries under black-box reductions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_456 (1).pdf`
- `downloads/3378_456 (2).pdf`
- `downloads/3378_456 (3).pdf`
- `downloads/3378_456.pdf`
