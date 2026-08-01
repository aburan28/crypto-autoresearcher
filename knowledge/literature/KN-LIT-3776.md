---
id: KN-LIT-3776
type: literature
title: "Fair-Zero Knowledge"
authors:
  - "Matt Lepinski"
  - "Silvio Micali"
  - "abhi shelat"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, side-channel, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce Fair Zero-Knowledge, a multi-verifier ZK system where every proof is guaranteed to be “zero-knowledge for all verifiers.” That is, if an honest verifier accepts a fair zero-knowledge proof, then he is assured that all other verifiers also learn nothing more than the verity of the statement in question, even if they maliciously collude with a cheating prover. We construct Fair Zero-Knowledge systems based on standard complexity assumptions (specifically, the quadratic residuosity assumption) and an initial, one-time use of a physically secure communication channel (specifically, each verifier sends the prover a private message in an envelope).

## Key claims (as reported)
- All other communication occurs (and must occur) on a broadcast channel.
- The main technical challenge of our construction consists of provably removing any possibility of using steganography in a ZK proof.
- To overcome this technical difficulty, we introduce tools —such as Unique Zero Knowledge— that may be of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_246 (1).pdf`
- `downloads/3378_246 (2).pdf`
- `downloads/3378_246 (3).pdf`
- `downloads/3378_246.pdf`
