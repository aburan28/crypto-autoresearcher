---
id: KN-LIT-3942
type: literature
title: "FPGA Design of Self-Certified Signature Verification on Koblitz Curves?"
authors:
  - "Kimmo Järvinen"
  - "Juha Forsten"
  - "Jorma Skyttä"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, implementation, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Elliptic curve signature schemes offer shorter signatures compared to other methods and a family of curves called Koblitz curves can be used for reducing the cost of signing and verification. This paper presents an FPGA implementation designed specifically for rapid verification of self-certified identity based signatures using Koblitz curves.

## Key claims (as reported)
- Verification requires computation of three elliptic curve point multiplications which are computed efficiently with 3-term multiple point multiplication and joint sparse form.
- Certain improvements to precomputations associated with multiple point multiplications are introduced.
- It is shown that, when using parallel processors, it is possible to gain considerable increases in the number of operations per second by allowing slightly longer computation times for single operations.
- It is demonstrated that up to 166,000 verifications per second can be computed using a single Altera Stratix II FPGA.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270256 (1).pdf`
- `downloads/47270256 (2).pdf`
- `downloads/47270256 (3).pdf`
- `downloads/47270256.pdf`
