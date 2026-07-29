---
id: KN-LIT-5723
type: literature
title: "Parallelizable Delegation from LWE"
authors:
  - "Cody Freitag"
  - "Rafael Pass"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first non-interactive delegation scheme for P with time-tight parallel prover efficiency based on standard hardness assumptions. More precisely, in a time-tight delegation scheme—which we refer to as a SPARG (succinct parallelizable argument)—the prover’s parallel running time is t + polylog(t), while using only polylog(t) processors and where t is the length of the computation.

## Key claims (as reported)
- (In other words, the proof is computed essentially in parallel with the computation, with only some minimal additive overhead in terms of time).
- Our main results show the existence of a publicly-verifiable, non-interactive, SPARG for P assuming polynomial hardness of LWE.
- Our SPARG construction relies on the elegant recent delegation construction of Choudhuri, Jain, and Jin (FOCS’21) and combines it with techniques from Ephraim et al (EuroCrypt’20).
- We next demonstrate how to make our SPARG time-independent—where the prover and verifier do not need to known the running-time t in advance; as far as we know, this yields the first construction of a time-tight delegation scheme with time-independence based on any hardness assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470130 (1).pdf`
- `downloads/137470130.pdf`
