---
id: KN-LIT-3967
type: literature
title: "From Private Simultaneous Messages to Zero-Information Arthur-Merlin Protocols and Back?"
authors:
  - "Benny Applebaum"
  - "Pavel Raykov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Göös, Pitassi and Watson (ITCS, 2015) have recently introduced the notion of Zero-Information Arthur-Merlin Protocols (ZAM). In this model, which can be viewed as a private version of the standard Arthur-Merlin communication complexity game, Alice and Bob are holding a pair of inputs x and y respectively, and Merlin, the prover, attempts to convince them that some public function f evaluates to 1 on (x, y).

## Key claims (as reported)
- In addition to standard completeness and soundness, Göös et al., require a “zero-knowledge” property which asserts that on each yesinput, the distribution of Merlin’s proof leaks no information about the inputs (x, y) to an external observer.
- In this paper, we relate this new notion to the well-studied model of Private Simultaneous Messages (PSM) that was originally suggested by Feige, Naor and Kilian (STOC, 1994).
- Roughly speaking, we show that the randomness complexity of ZAM corresponds to the communication complexity of PSM, and that the communication complexity of ZAM corresponds to the randomness complexity of PSM.
- This relation works in both directions where different variants of PSM are being used.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620669 (1).pdf`
- `downloads/95620669.pdf`
