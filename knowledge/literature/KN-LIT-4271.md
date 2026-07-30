---
id: KN-LIT-4271
type: literature
title: "How to Compute under AC 0 Leakage without Secure Hardware"
authors:
  - "Guy N. Rothblum⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of computing securely in the presence of leakage on the computation’s internals. Our main result is a general compiler that compiles any algorithm P , viewed as a boolean circuit, into a functionally equivalent algorithm P ′ .

## Key claims (as reported)
- The compiled P ′ can then be run repeatedly on adversarially chosen inputs in the presence of leakage on its internals: In each execution of P ′ , an AC 0 adversary can (adaptively) choose any leakage function that can be computed in AC 0 and has bounded output length, apply it to the values on P ′ ’s internal wires in that execution, and view its output.
- We show that no such leakage adversary can learn more than P ’s input-output behavior.
- In particular, the internals of P are protected.
- Security does not rely on any secure hardware, and is proved under a computational intractability assumption regarding the hardness of computing inner products for AC 0 circuits with pre-processing.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170547 (1).pdf`
- `downloads/74170547 (2).pdf`
- `downloads/74170547 (3).pdf`
- `downloads/74170547 (4).pdf`
- `downloads/74170547 (5).pdf`
- `downloads/74170547.pdf`
