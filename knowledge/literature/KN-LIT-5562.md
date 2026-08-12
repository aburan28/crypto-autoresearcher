---
id: KN-LIT-5562
type: literature
title: "On the Salsa20 Core Function"
authors:
  - "Julio Cesar Hernandez-Castro"
  - "Juan M. E. Tapiador"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we point out some weaknesses in the Salsa20 core function that could be exploited to obtain up to 231 collisions for its full (20 rounds) version. We first find an invariant for its main building block, the quarterround function, that is then extended to the rowround and columnround functions.

## Key claims (as reported)
- This allows us to find an input subset of size 232 for which the Salsa20 core behaves exactly as the transformation f (x) = 2x.
- An attacker can take advantage of this for constructing 231 collisions for any number of rounds.
- We finally show another weakness in the form of a differential characteristic with probability one that proves that the Salsa20 core does not have 2nd preimage resistance.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860470 (1).pdf`
- `downloads/50860470 (2).pdf`
- `downloads/50860470 (3).pdf`
- `downloads/50860470.pdf`
