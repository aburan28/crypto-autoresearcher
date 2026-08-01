---
id: KN-LIT-5462
type: literature
title: "On the Efficiency of Bit Commitment Reductions"
authors:
  - "Samuel Ranellucci"
  - "Alain Tapp"
  - "Severin Winkler"
  - "Jürg Wullschleger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Two fundamental building blocks of secure two-party computation are oblivious transfer and bit commitment. While there exist unconditionally secure implementations of oblivious transfer from noisy correlations or channels that achieve constant rates, similar constructions are not known for bit commitment.

## Key claims (as reported)
- In this paper, we show that any protocol that implements n instances of bit commitment with an error of at most 2−k needs at least Ω(kn) instances of a given resource such as oblivious transfer or a noisy channel.
- This implies in particular that it is impossible to achieve a constant rate.
- We then show that it is possible to circumvent the above lower bound by restricting the way in which the bit commitments can be opened.
- We present a protocol that achieves a constant rate in the special case where only a constant number of instances can be opened, which is optimal.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730511 (1).pdf`
- `downloads/70730511 (2).pdf`
- `downloads/70730511 (3).pdf`
- `downloads/70730511.pdf`
