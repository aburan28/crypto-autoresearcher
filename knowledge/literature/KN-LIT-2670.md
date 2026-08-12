---
id: KN-LIT-2670
type: literature
title: "Batching Techniques for Accumulators with Applications to IOPs and Stateless Blockchains"
authors:
  - "Dan Boneh"
  - "Benedikt Bünz"
  - "Ben Fisch"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present batching techniques for cryptographic accumulators and vector commitments in groups of unknown order. Our techniques are tailored for distributed settings where no trusted accumulator manager exists and updates to the accumulator are processed in batches.

## Key claims (as reported)
- We develop techniques for non-interactively aggregating membership proofs that can be verified with a constant number of group operations.
- We also provide a constant sized batch non-membership proof for a large number of elements.
- These proofs can be used to build the first positional vector commitment (VC) with constant sized openings and constant sized public parameters.
- As a core building block for our batching techniques we develop several succinct proof systems in groups of unknown order.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940442 (1).pdf`
- `downloads/116940442.pdf`
