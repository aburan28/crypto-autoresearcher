---
id: KN-LIT-6379
type: literature
title: "SCALES MPC with Small Clients and Larger Ephemeral Servers"
authors:
  - "Anasuya Acharya"
  - "Carmit Hazay"
  - "Vladimir Kolesnikov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The recently proposed YOSO model is a groundbreaking approach to MPC, executable on a public blockchain, circumventing adaptive player corruption by hiding the corruption targets until they are worthless. Players are selected unpredictably from a large pool to perform MPC subtasks, in which each selected player sends a single message (and reveals their identity).

## Key claims (as reported)
- While YOSO MPC has attractive asymptotic complexity, unfortunately, it is concretely prohibitively expensive due to the cost of its building blocks.
- We propose a modification to the YOSO model that preserves resilience to adaptive server corruption, but allows for much more efficient protocols.
- In SCALES (Small Clients And Larger Ephemeral Servers) only the servers facilitating the MPC computation are ephemeral (unpredictably selected and “speak once”).
- Input providers (clients) publish problem instance and collect the output, but do not otherwise participate in computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470096 (1).pdf`
- `downloads/137470096.pdf`
