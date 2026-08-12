---
id: KN-LIT-5361
type: literature
title: "On Kilian’s Randomization of Multilinear Map Encodings"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, number-theory, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Indistinguishability obfuscation constructions based on matrix branching programs generally proceed in two steps: first apply Kilian’s randomization of the matrix product computation, and then encode the matrices using a multilinear map scheme. In this paper we observe that by applying Kilian’s randomization after encoding, the complexity of the best attacks is significantly increased for CLT13 multilinear maps.

## Key claims (as reported)
- This implies that much smaller parameters can be used, which improves the efficiency of the constructions by several orders of magnitude.
- As an application, we describe the first concrete implementation of multiparty non-interactive Diffie-Hellman key exchange secure against existing attacks.
- Key exchange was originally the most straightforward application of multilinear maps; however it was quickly broken for the three known families of multilinear maps (GGH13, CLT13 and GGH15).
- Here we describe the first implementation of key exchange that is resistant against known attacks, based on CLT13 multilinear maps.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210130 (1).pdf`
- `downloads/119210130.pdf`
