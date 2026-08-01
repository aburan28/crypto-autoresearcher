---
id: KN-LIT-5494
type: literature
title: "On the Impossibility of Basing Public-Coin One-Way Permutations on Trapdoor Permutations"
authors:
  - "Takahiro Matsuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One of the fundamental research themes in cryptography is to clarify what the minimal assumptions to realize various kinds of cryptographic primitives are, and up to now, a number of relationships among primitives have been investigated and established. Among others, it has been suggested (and sometimes explicitly claimed) that a family of one-way trapdoor permutations (TDP) is sufficient for constructing almost all the basic primitives/protocols in both “public-key” and “private-key” cryptography.

## Key claims (as reported)
- In this paper, however, we show strong evidence that this is not the case for the constructions of a one-way permutation (OWP), one of the most fundamental primitives in private cryptography.
- Specifically, we show that there is no black-box construction of a OWP from a TDP, even if the TDP is ideally secure, where, roughly speaking, ideal security of a TDP corresponds to security satisfied by random permutations and thus captures major security notions of TDPs such as one-wayness, claw-freeness, security under correlated inputs, etc.
- Our negative result might at first sound unexpected because both OWP and (ideally secure) TDP are primitives that implement a “permutation” that is “one-way”.
- However, our result exploits the fact that a TDP is a “secret-coin” family of permutations whose permutations become available only after some sort of key generation is performed, while a OWP is a publicly computable function which does not have such key generation process.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83490112 (1).pdf`
- `downloads/83490112 (2).pdf`
- `downloads/83490112 (3).pdf`
- `downloads/83490112.pdf`
