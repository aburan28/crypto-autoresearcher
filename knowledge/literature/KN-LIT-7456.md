---
id: KN-LIT-7456
type: literature
title: "Verifiable Private Information Retrieval"
authors:
  - "Shany Ben-David"
  - "Yael Tauman Kalai"
  - "Omer Paneth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A computational PIR scheme allows a client to privately query a database hosted on a single server without downloading the entire database. We introduce the notion of verifiable PIR (vPIR) where the server can convince the client that the database satisfies certain properties without additional rounds and while keeping the communication sub-linear.

## Key claims (as reported)
- For example, the server can prove that the number of rows in the database that satisfy a predicate P is exactly n.
- We define security by modeling vPIR as an ideal functionality and following the real-ideal paradigm.
- Starting from a standard PIR scheme, we construct a vPIR scheme for any database property that can be verified by a machine that reads the database once and maintains a bounded size state between rows.
- We also construct vPIR with public verification based on LWE or on DLIN.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470131 (1).pdf`
- `downloads/137470131.pdf`
