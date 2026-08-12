---
id: KN-LIT-3121
type: literature
title: "Constant-Round Private Function Evaluation with Linear Complexity"
authors:
  - "Jonathan Katz"
  - "Lior Malka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of private function evaluation (PFE) in the two-party setting. Here, informally, one party holds an input x while the other holds a (circuit describing a) function f ; the goal is for one (or both) of the parties to learn f (x) while revealing nothing more to either party.

## Key claims (as reported)
- In contrast to the usual setting of secure computation, where the function being computed is known to both parties, PFE is useful in settings where the function (i.e., algorithm) itself must remain secret, e.g., because it is proprietary or classified.
- It is known that PFE can be reduced to standard secure computation by having the parties evaluate a universal circuit, and this is the approach taken in most prior work.
- Using a universal circuit, however, introduces additional overhead and results in a more complex implementation.
- We show here a completely new technique for PFE that avoids universal circuits, and results in constant-round protocols with communication/computational complexity linear in the size of the circuit computing f .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730547 (1).pdf`
- `downloads/70730547 (2).pdf`
- `downloads/70730547 (3).pdf`
- `downloads/70730547.pdf`
