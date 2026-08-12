---
id: KN-LIT-3021
type: literature
title: "Composability and On-Line Deniability of Authentication"
authors:
  - "Yevgeniy Dodis"
  - "Jonathan Katz"
  - "Adam Smith"
  - "Shabsi Walfish"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protocols for deniable authentication achieve seemingly paradoxical guarantees: upon completion of the protocol the receiver is convinced that the sender authenticated the message, but neither party can convince anyone else that the other party took part in the protocol. We introduce and study on-line deniability, where deniability should hold even when one of the parties colludes with a third party during execution of the protocol.

## Key claims (as reported)
- This turns out to generalize several realistic scenarios that are outside the scope of previous models.
- We show that a protocol achieves our definition of on-line deniability if and only if it realizes the message authentication functionality in the generalized universal composability framework; any protocol satisfying our definition thus automatically inherits strong composability guarantees.
- Unfortunately, we show that our definition is impossible to realize in the PKI model if adaptive corruptions are allowed (even if secure erasure is assumed).
- On the other hand, we show feasibility with respect to static corruptions (giving the first separation in terms of feasibility between the static and adaptive setting), and show how to realize a relaxation termed deniability with incriminating abort under adaptive corruptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440145 (1).pdf`
- `downloads/54440145 (2).pdf`
- `downloads/54440145 (3).pdf`
- `downloads/54440145.pdf`
