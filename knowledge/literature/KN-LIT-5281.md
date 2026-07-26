---
id: KN-LIT-5281
type: literature
title: "Oblivious Transfer from Weak Noisy Channels Jürg Wullschleger"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Various results show that oblivious transfer can be implemented using the assumption of noisy channels. Unfortunately, this assumption is not as weak as one might think, because in a cryptographic setting, these noisy channels must satisfy very strong security requirements.

## Key claims (as reported)
- Unfair noisy channels, introduced by Damgård, Kilian and Salvail [Eurocrypt ’99], reduce these limitations: They give the adversary an unfair advantage over the honest player, and therefore weaken the security requirements on the noisy channel.
- However, this model still has many shortcomings: For example, the adversary’s advantage is only allowed to have a very special form, and no error is allowed in the implementation.
- In this paper we generalize the idea of unfair noisy channels.
- We introduce two new models of cryptographic noisy channels that we call the weak erasure channel and the weak binary symmetric channel, and show how they can be used to implement oblivious transfer.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440328 (1).pdf`
- `downloads/54440328 (2).pdf`
- `downloads/54440328 (3).pdf`
- `downloads/54440328.pdf`
