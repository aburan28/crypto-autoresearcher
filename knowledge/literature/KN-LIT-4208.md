---
id: KN-LIT-4208
type: literature
title: "High-Throughput Secure Three-Party Computation for Malicious Adversaries and an Honest Majority"
authors:
  - "Jun Furukawa"
  - "Yehuda Lindell"
  - "Ariel Nof"
  - "Or Weinstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we describe a new protocol for secure threeparty computation of any functionality, with an honest majority and a malicious adversary. Our protocol has both an information-theoretic and computational variant, and is distinguished by extremely low communication complexity and very simple computation.

## Key claims (as reported)
- We start from the recent semi-honest protocol of Araki et al.
- (ACM CCS 2016) in which the parties communicate only a single bit per AND gate, and modify it to be secure in the presence of malicious adversaries.
- Our protocol follows the paradigm of first constructing Beaver multiplication triples and then using them to verify that circuit gates are correctly computed.
- As in previous work (e.g., the so-called TinyOT and SPDZ protocols), we rely on the cut-and-choose paradigm to verify that triples are correctly constructed.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210124 (1).pdf`
- `downloads/10210124.pdf`
