---
id: KN-LIT-4808
type: literature
title: "Lower Bounds for Multi-Server Oblivious RAMs"
authors:
  - "Kasper Green Larsen"
  - "Mark Simkin"
  - "Kevin Yeo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we consider the construction of oblivious RAMs (ORAM) in a setting with multiple servers and the adversary may corrupt a subset of the servers. We present an Ω(log n) overhead lower bound for any k-server ORAM that limits any PPT adversary to distinguishing advantage at most 1/4k when only one server is corrupted.

## Key claims (as reported)
- In other words, if one insists on negligible distinguishing advantage, then multi-server ORAMs cannot be faster than single-server ORAMs even with polynomially many servers of which only one unknown server is corrupted.
- Our results apply to ORAMs that may err with probability at most 1/128 as well as scenarios where the adversary corrupts larger subsets of servers.
- We also extend our lower bounds to other important data structures including oblivious stacks, queues, deques, priority queues and search trees.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550221 (1).pdf`
- `downloads/12550221.pdf`
