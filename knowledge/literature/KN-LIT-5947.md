---
id: KN-LIT-5947
type: literature
title: "Proofs of Replicated Storage Without Timing Assumptions?"
authors:
  - "Ivan Damgård"
  - "Chaya Ganesh"
  - "Claudio Orlandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we provide a formal treatment of proof of replicated storage, a novel cryptographic primitive recently proposed in the context of a novel cryptocurrency, namely Filecoin. In a nutshell, proofs of replicated storage is a solution to the following problem: A user stores a file m on n different servers to ensure that the file will be available even if some of the servers fail.

## Key claims (as reported)
- Using proof of retrievability, the user could check that every server is indeed storing the file.
- However, what if the servers collude and, in order to save on resources, decide to only store one copy of the file?
- A proof of replicated storage guarantees that, unless the (potentially colluding) servers are indeed reserving the space necessary to store n copies of the file, the user will not accept the proofs.
- While some candidate proofs of replicated storage have already been proposed, their soundness relies on timing assumptions i.e., the user must reject the proof if the prover does not reply within a certain time-bound.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940316 (1).pdf`
- `downloads/116940316.pdf`
