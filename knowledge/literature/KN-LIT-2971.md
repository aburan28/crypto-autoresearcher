---
id: KN-LIT-2971
type: literature
title: "Combined Fault and Leakage Resilience: Composability"
authors:
  - "Maximilian Orlt"
  - "Okan Seker"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, mpc, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Real-world cryptographic implementations nowadays are not only attacked via classical cryptanalysis but also via implementation attacks, including passive attacks (observing side-channel information about the inner computation) and active attacks (inserting faults into the computation). While countermeasures exist for each type of attack, countermeasures against combined attacks have only been considered recently.

## Key claims (as reported)
- Masking is a standard technique for protecting against passive side-channel attacks, but protecting against active attacks with additive masking is challenging.
- Previous approaches include running multiple copies of a masked computation, requiring a large amount of randomness or being vulnerable to horizontal attacks.
- An alternative approach is polynomial masking, which is inherently fault-resistant.
- This work presents a compiler based on polynomial masking that achieves linear computational complexity for affine functions and cubic complexity for non-linear functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850219 (1).pdf`
- `downloads/140850219.pdf`
