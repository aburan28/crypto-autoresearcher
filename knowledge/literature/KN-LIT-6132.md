---
id: KN-LIT-6132
type: literature
title: "Random-Index Oblivious RAM"
authors:
  - "Shai Halevi"
  - "Eyal Kushilevitz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the notion of Random-index ORAM (RORAM), which is a weak form of ORAM where the Client is limited to asking for (and possibly modifying) random elements of the N -items memory, rather than specific ones. That is, whenever the client issues a request, it gets in return a pair (r, xr ) where r ∈R [N ] is a random index and xr is the content of the r-th memory item.

## Key claims (as reported)
- Then, the client can also modify the content to some new value x′r .
- We first argue that the limited functionality of RORAM still suffices for certain applications.
- These include various applications of sampling (or sub-sampling) and, in particular, the very-large-scale MPC application in the setting of Benhamouda et al.
- Clearly, RORAM can be implemented using any ORAM scheme (by the Client selecting the random r’s by itself), but the hope is that the limited functionality of RORAM can make it faster and easier to implement than ORAM.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470054 (1).pdf`
- `downloads/137470054.pdf`
