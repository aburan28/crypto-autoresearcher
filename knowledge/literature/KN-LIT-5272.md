---
id: KN-LIT-5272
type: literature
title: "Oblivious Parallel RAM:"
authors:
  - "Improved Efficiency"
  - "Generic Constructions"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAM (ORAM) garbles read/write operations by a client (to access a remote storage server or a random-access memory) so that an adversary observing the garbled access sequence cannot infer any information about the original operations, other than their overall number. This paper considers the natural setting of Oblivious Parallel RAM (OPRAM) recently introduced by Boyle, Chung, and Pass (TCC 2016A), where m clients simultaneously access in parallel the storage server.

## Key claims (as reported)
- The clients are additionally connected via point-to-point links to coordinate their accesses.
- However, this additional inter-client communication must also remain oblivious.
- The main contribution of this paper is twofold: We construct the first OPRAM scheme that (nearly) matches the storage and server-client communication complexities of the most efficient single-client ORAM schemes.
- Our scheme is based on an extension of Path-ORAM by Stefanov et al (CCS 2013).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620807 (1).pdf`
- `downloads/95620807.pdf`
