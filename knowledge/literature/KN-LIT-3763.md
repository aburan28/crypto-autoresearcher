---
id: KN-LIT-3763
type: literature
title: "Efficient Secure Two-Party Computation Using Symmetric Cut-and-Choose"
authors:
  - "Yan Huang"
  - "Jonathan Katz⋆"
  - "David Evans⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Beginning with the work of Lindell and Pinkas, researchers have proposed several protocols for secure two-party computation based on the cut-and-choose paradigm. In current instantiations of this approach, one party generates κ garbled circuits; some fraction of those are “checked” by the other party, and the remaining fraction are evaluated.

## Key claims (as reported)
- We introduce here the idea of symmetric cut-and-choose protocols, in which both parties generate κ circuits to be checked by the other party.
- The main advantage of our technique is that κ can be reduced by a factor of 3 while attaining the same statistical security level as in prior work.
- Since the number of garbled circuits dominates the costs of the protocol, especially as larger circuits are evaluated, our protocol is expected to run up to 3 times faster than existing schemes.
- Preliminary experiments validate this claim.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420149 (1).pdf`
- `downloads/80420149 (2).pdf`
- `downloads/80420149 (3).pdf`
- `downloads/80420149.pdf`
