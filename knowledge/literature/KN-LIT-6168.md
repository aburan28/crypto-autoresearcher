---
id: KN-LIT-6168
type: literature
title: "Receipt-Free Universally-Verifiable Voting With Everlasting Privacy"
authors:
  - "Tal Moran"
  - "Moni Naor⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first universally verifiable voting scheme that can be based on a general assumption (existence of a non-interactive commitment scheme). Our scheme is also the first receipt-free scheme to give “everlasting privacy” for votes: even a computationally unbounded party does not gain any information about individual votes (other than what can be inferred from the final tally).

## Key claims (as reported)
- Our voting protocols are designed to be used in a “traditional” setting, in which voters cast their ballots in a private polling booth (which we model as an untappable channel between the voter and the tallying authority).
- Following in the footsteps of Chaum and Neff [7,16], our protocol ensures that the integrity of an election cannot be compromised even if the computers running it are all corrupt (although ballot secrecy may be violated in this case).
- We give a generic voting protocol which we prove to be secure in the Universal Composability model, given that the underlying commitment is universally composable.
- We also propose a concrete implementation, based on the hardness of discrete log, that is slightly more efficient (and can be used in practice).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170368 (1).pdf`
- `downloads/41170368 (2).pdf`
- `downloads/41170368 (3).pdf`
- `downloads/41170368.pdf`
