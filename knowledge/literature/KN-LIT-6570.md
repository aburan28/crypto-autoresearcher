---
id: KN-LIT-6570
type: literature
title: "Session-Key Generation using Human Passwords Only"
authors:
  - "Oded Goldreich"
  - "Yehuda Lindell"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present session-key generation protocols in a model where the legitimate parties share only a human-memorizable password. The security guarantee holds with respect to probabilistic polynomial-time adversaries that control the communication channel (between the parties), and may omit, insert and modify messages at their choice.

## Key claims (as reported)
- Loosely speaking, the effect of such an adversary that attacks an execution of our protocol is comparable to an attack in which an adversary is only allowed to make a constant number of queries of the form “is w the password of Party A”.
- We stress that the result holds also in case the passwords are selected at random from a small dictionary so that it is feasible (for the adversary) to scan the entire directory.
- We note that prior to our result, it was not clear whether or not such protocols were attainable without the use of random oracles or additional setup assumptions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390406 (1).pdf`
- `downloads/21390406 (2).pdf`
- `downloads/21390406.pdf`
