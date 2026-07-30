---
id: KN-LIT-3660
type: literature
title: "Efficiently Testable Circuits Without Conductivity"
authors:
  - "Mirza Ahad Baig"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The notion of “efficiently testable circuits” (ETC) was recently put forward by Baig et al. Informally, an ETC compiler takes as input any Boolean circuit C and outputs a circuit/inputs tuple (C ′ , T) where (completeness) C ′ is functionally equivalent to C and (security) if C ′ is tampered in some restricted way, then this can be detected as C ′ will err on at least one input in the small test set T.

## Key claims (as reported)
- The compiler of Baig et al. detects tampering even if the adversary can tamper with all wires in the compiled circuit.
- Unfortunately, the model requires a strong “conductivity” restriction: the compiled circuit has gates with fan-out up to 3, but wires can only be tampered in one way even if they have fan-out greater than one.
- In this paper, we solve the main open question from their work and construct an ETC compiler without this conductivity restriction.
- While Baig et al. use gadgets computing the AND and OR of particular subsets of the wires, our compiler computes inner products with random vectors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369050 (1).pdf`
- `downloads/14369050.pdf`
