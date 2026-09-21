---
id: KN-LIT-2328
type: literature
title: "Adaptive Oblivious Transfer with Access Control from Lattice Assumptions"
authors:
  - "Huaxiong Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Adaptive oblivious transfer (OT) is a protocol where a sender initially commits to a database {Mi }N i=1 . Then, a receiver can query the sender up to k times with private indexes ρ1 , . . . , ρk so as to obtain Mρ1 , . . . , Mρk and nothing else.

## Key claims (as reported)
- Moreover, for each i ∈ [k], the receiver’s choice ρi may depend on previously obtained messages {Mρj }j<i .
- Oblivious transfer with access control (OT-AC) is a flavor of adaptive OT where database records are protected by distinct access control policies that specify which credentials a receiver should obtain in order to access each Mi .
- So far, all known OT-AC protocols only support access policies made of conjunctions or rely on ad hoc assumptions in pairing-friendly groups (or both).
- In this paper, we provide an OT-AC protocol where access policies may consist of any branching program of polynomial length, which is sufficient to realize any access policy in NC1.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240260 (1).pdf`
- `downloads/106240260.pdf`
