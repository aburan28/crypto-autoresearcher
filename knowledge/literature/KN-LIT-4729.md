---
id: KN-LIT-4729
type: literature
title: "Limitations on Transformations from Composite-Order to Prime-Order Groups: The Case of Round-Optimal Blind Signatures"
authors:
  - "Sarah Meiklejohn"
  - "Hovav Shacham"
  - "David Mandell Freeman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Beginning with the work of Groth and Sahai, there has been much interest in transforming pairing-based schemes in composite-order groups to equivalent ones in prime-order groups. A method for achieving such transformations has recently been proposed by Freeman, who identified two properties of pairings using composite-order groups — “cancelling” and “projecting” — on which many schemes rely, and showed how either of these properties can be obtained using prime-order groups.

## Key claims (as reported)
- In this paper, we give evidence for the existence of limits to such transformations.
- Specifically, we show that a pairing generated in a natural way from the Decision Linear assumption in prime-order groups can be simultaneously cancelling and projecting only with negligible probability.
- As evidence that these properties can be helpful together as well as individually, we present a cryptosystem whose proof of security makes use of a pairing that is both cancelling and projecting.
- Our example cryptosystem is a simple round-optimal blind signature scheme that is secure in the common reference string model, without random oracles, and based on mild assumptions; it is of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477523 (1).pdf`
- `downloads/6477523 (2).pdf`
- `downloads/6477523 (3).pdf`
- `downloads/6477523.pdf`
