---
id: KN-LIT-4845
type: literature
title: "Maliciously Secure Oblivious Linear Function Evaluation with Constant Overhead"
authors:
  - "Satrajit Ghosh"
  - "Jesper Buus Nielsen"
  - "Tobias Nilges"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we consider the problem of oblivious linear function evaluation (OLE). OLE is a special case of oblivious polynomial evaluation (OPE) and deals with the oblivious evaluation of a linear function f (x) = ax + b.

## Key claims (as reported)
- This problem is non-trivial in the sense that the sender chooses a, b and the receiver x, but the receiver may only learn f (x).
- We present a highly efficient and UC-secure construction of OLE in the OT-hybrid model that requires only O(1) OTs per OLE.
- The construction is based on noisy encodings introduced by Naor and Pinkas (STOC’99) and used for passive secure OLEs by Ishai, Prabhakaran and Sahai (TCC’09).
- A result asymptotically similar to ours is known by applying the IPS compiler to the mentioned passive secure OLE protocol, but our protocol provides better constants and would be considerably simpler to implement.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240163 (1).pdf`
- `downloads/106240163.pdf`
