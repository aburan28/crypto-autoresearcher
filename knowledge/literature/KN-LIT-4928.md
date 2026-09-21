---
id: KN-LIT-4928
type: literature
title: "MiniLEGO: Efficient Secure Two-Party Computation From General Assumptions"
authors:
  - "Tore Kasper Frederiksen"
  - "Thomas Pelle Jakobsen"
  - "Jesper Buus Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, hash, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One of the main tools to construct secure two-party computation protocols are Yao garbled circuits. Using the cut-and-choose technique, one can get reasonably efficient Yao-based protocols with security against malicious adversaries.

## Key claims (as reported)
- At TCC 2009, Nielsen and Orlandi [28] suggested to apply cut-andchoose at the gate level, while previously cut-and-choose was applied on the circuit as a whole.
- This idea allows for a speed up with practical significance (in the order of the logarithm of the size of the circuit) and has become known as the “LEGO” construction.
- Unfortunately the construction in [28] is based on a specific number-theoretic assumption and requires public-key operations per gate of the circuit.
- The main technical contribution of this work is a new XORhomomorphic commitment scheme based on oblivious transfer, that we use to cope with the problem of connecting the gates in the LEGO construction.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810535 (1).pdf`
- `downloads/78810535 (2).pdf`
- `downloads/78810535 (3).pdf`
- `downloads/78810535.pdf`
