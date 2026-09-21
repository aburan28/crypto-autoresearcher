---
id: KN-LIT-7473
type: literature
title: "Very-efficient simulatable flipping of many coins into a well?"
authors:
  - "Luís T. A. N. Brandão"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents new cryptographic protocols for a standalone simulatable two-party parallel coin-flipping (into a well) and a universally composable commitment scheme, with near optimal asymptotic communication rate, in the static and computational malicious model. The approach, denoted expand-mask-hash, uses in both protocols a pseudo-random generator (PRG) and a collision-resistant hash function (CR-Hash) to combine separate extractable commitments and equivocable commitments (associated with short bit-strings) into a unified extractable-and-equivocable property amplified to a larger target length, amortizing the cost of base commitments.

## Key claims (as reported)
- The new stand-alone coin-flipping protocol is based on a simple augmentation of the traditional coin-flipping template.
- To the knowledge of the author, it is the first proposal simultaneously shown to be two-side-simulatable and having an asymptotic (as the target length increases) communication rate converging to two bits per flipped coin and computation rate per party converging to that of PRG-generating and CR-hashing a bit-string with the target length.
- The new universally composable commitment scheme has efficiency comparable to very recent state-of-the-art constructions – namely asymptotic communication rate as close to 1 as desired, for each phase (commit and open) – while following a distinct design approach.
- Notably it does not require explicit use of oblivious transfer and it uses an erasure encoding instead of stronger error correction codes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140239 (1).pdf`
- `downloads/96140239 (2).pdf`
- `downloads/96140239 (3).pdf`
- `downloads/96140239 (4).pdf`
- `downloads/96140239.pdf`
