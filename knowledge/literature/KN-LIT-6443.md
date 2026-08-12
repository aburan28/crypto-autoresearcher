---
id: KN-LIT-6443
type: literature
title: "Secure Massively Parallel Computation for Dishonest Majority"
authors:
  - "Rex Fernando"
  - "Ilan Komargodski"
  - "Yanyi Liu"
  - "Elaine Shi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work concerns secure protocols in the massively parallel computation (MPC) model, which is one of the most widely-accepted models for capturing the challenges of writing protocols for the types of parallel computing clusters which have become commonplace today (MapReduce, Hadoop, Spark, etc.). Recently, the work of Chan et al.

## Key claims (as reported)
- (ITCS ’20) initiated this study, giving a way to compile any MPC protocol into a secure one in the common random string model, achieving the standard secure multi-party computation definition of security with up to 1/3 of the parties being corrupt.
- We are interested in achieving security for much more than 1/3 corruptions.
- To that end, we give two compilers for MPC protocols, which assume a simple public-key infrastructure, and achieve semi-honest security for allbut-one corruptions.
- Our first compiler assumes hardness of the learningwith-errors (LWE) problem, and works for any MPC protocol with “short” output—that is, where the output of the protocol can fit into the storage space of one machine, for instance protocols that output a trained machine learning model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550233 (1).pdf`
- `downloads/12550233.pdf`
