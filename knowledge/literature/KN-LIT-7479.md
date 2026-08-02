---
id: KN-LIT-7479
type: literature
title: 'VOLE-PSI: Fast OPRF and Circuit-PSI from Vector-OLE'
authors:
- Peter Rindal
- Phillipp Schoppmann
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- private-set-intersection
- oblivious-prf
- vector-ole
- mpc
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
In this work we present a new construction for a batched Oblivious Pseudorandom Function (OPRF) based on Vector-OLE and the PaXoS data structure. We then use it in the standard transformation for achieving Private Set Intersection (PSI) from an OPRF.

## Key claims (as reported)
- Our overall construction is highly efficient with O(n) communication and computation.
- We demonstrate that our protocol can achieve malicious security at only a very small overhead compared to the semi-honest variant.
- For input sizes n = 220 , our malicious protocol needs 6.2 seconds and less than 59 MB communication.
- This corresponds to under 450 bits per element, which is the lowest number for any published PSI protocol (semi-honest or malicious) to date.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960366 (1).pdf`
- `downloads/126960366.pdf`
