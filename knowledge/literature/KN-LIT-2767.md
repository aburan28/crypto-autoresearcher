---
id: KN-LIT-2767
type: literature
title: "Boosting OMD for Almost Free Authentication of Associated Data"
authors:
  - "Reza Reyhanitabar"
  - "Serge Vaudenay"
  - "Damian Vizár"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose pure OMD (p-OMD) as a new variant of the Offset Merkle-Damgård (OMD) authenticated encryption scheme. Our new scheme inherits all desirable security features of OMD while having a more compact structure and providing higher efficiency.

## Key claims (as reported)
- The original OMD scheme, as submitted to the CAESAR competition, couples a single pass of a variant of the Merkle-Damgård (MD) iteration with the counter-based XOR MAC algorithm to provide privacy and authenticity.
- Our improved p-OMD scheme dispenses with the XOR MAC algorithm and is purely based on the MD iteration; hence, the name “pure” OMD.
- To process a message of l blocks and associated data of a blocks, OMD needs l + a + 2 calls to the compression function while p-OMD only requires max {l, a} + 2 calls.
- Therefore, for a typical case where l ≥ a, p-OMD makes just l + 2 calls to the compression function; that is, associated data is processed almost freely compared to OMD.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400117 (1).pdf`
- `downloads/85400117.pdf`
