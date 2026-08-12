---
id: KN-LIT-7551
type: literature
title: "Zero-Knowledge Functional"
authors:
  - "Elementary Databases"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Zero-knowledge elementary databases (ZK-EDBs) enable a prover to commit a database D of key-value (x, v) pairs and later provide a convincing answer to the query send me the value D(x) associated with x without revealing any extra knowledge (including the size of D ). After its introduction, several works extended it to allow more expressive queries, but the expressiveness achieved so far is still limited: only a relatively simple queriesrange queries over the keys and values can be handled by known constructions.

## Key claims (as reported)
- In this paper we introduce a new notion called zero knowledge func- tional elementary databases (ZK-FEDBs), which allows the most general functional queries.
- Roughly speaking, for any Boolean circuit f, ZK-FEDBs allows the ZK-EDB prover to provide convincing answers to the queries of the form send me all records (x, v) in D satisfying f (x, v) = 1, without revealing any extra knowledge (including the size of D ).
- We present a construction of ZK-FEDBs in the random oracle model and generic group model, whose proof size is only linear in the length of record and the size of query circuit, and is independent of the size of input database D .
- Our technical constribution is two-fold.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438217 (1).pdf`
- `downloads/14438217.pdf`
