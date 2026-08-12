---
id: KN-LIT-7398
type: literature
title: "Universally Composable Commitments"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
) Ran Canetti? and Marc Fischlin?? We propose a new security measure for commitment protocols, called Universally Composable (UC) Commitment.

## Key claims (as reported)
- The measure guarantees that commitment protocols behave like an “ideal commitment service,” even when concurrently composed with an arbitrary set of protocols.
- This is a strong guarantee: it implies that security is maintained even when an unbounded number of copies of the scheme are running concurrently, it implies non-malleability (not only with respect to other copies of the same protocol but even with respect to other protocols), it provides resilience to selective decommitment, and more.
- Unfortunately, two-party uc commitment protocols do not exist in the plain model.
- However, we construct two-party uc commitment protocols, based on general complexity assumptions, in the common reference string model where all parties have access to a common string taken from a predetermined distribution.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390019 (1).pdf`
- `downloads/21390019 (2).pdf`
- `downloads/21390019 (3).pdf`
- `downloads/21390019.pdf`
