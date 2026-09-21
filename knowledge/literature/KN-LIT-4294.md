---
id: KN-LIT-4294
type: literature
title: "How to Obfuscate MPC Inputs"
authors:
  - "Ian McQuoid"
  - "Mike Rosulek"
  - "Jiayu Xu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the idea of input obfuscation for secure twoparty computation (io2PC). Suppose Alice holds a private value x and wants to allow clients to learn f (x, yi ), for their choice of yi , via a secure computation protocol.

## Key claims (as reported)
- The goal of io2PC is for Alice to encode x so that an adversary who compromises her storage gets only oracle access to the function f (x, ·).
- At the same time, there must be a 2PC protocol for computing f (x, y) that takes only this encoding (and not the plaintext x) as input.
- We show how to achieve io2PC for functions that have virtual black-box (VBB) obfuscation in either the random oracle model or generic group model.
- For functions that can be VBB-obfuscated in the random oracle model, we provide an io2PC protocol by replacing the random oracle with an oblivious PRF.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470145 (1).pdf`
- `downloads/137470145.pdf`
