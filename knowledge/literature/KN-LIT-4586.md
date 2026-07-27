---
id: KN-LIT-4586
type: literature
title: "Key Recovery from Gram–Schmidt Norm"
authors:
  - "Leakage in Hash-and-Sign Signatures"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we initiate the study of side-channel leakage in hash-and-sign lattice-based signatures, with particular emphasis on the two efficient implementations of the original GPV lattice-trapdoor paradigm for signatures, namely NIST second-round candidate Falcon and its simpler predecessor DLP. Both of these schemes implement the GPV signature scheme over NTRU lattices, achieving great speed-ups over the general lattice case.

## Key claims (as reported)
- Our results are mainly threefold.
- First, we identify a specific source of side-channel leakage in most implementations of those schemes, namely, the one-dimensional Gaussian sampling steps within lattice Gaussian sampling.
- It turns out that the implementations of these steps often leak the Gram–Schmidt norms of the secret lattice basis.
- Second, we elucidate the link between this leakage and the secret key, by showing that the entire secret key can be efficiently reconstructed solely from those Gram–Schmidt norms.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105241 (1).pdf`
- `downloads/12105241.pdf`
