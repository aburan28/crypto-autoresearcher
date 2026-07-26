---
id: KN-LIT-3850
type: literature
title: "Faster Secure Two-Party Computation in the Single-Execution Setting"
authors:
  - "Xiao Wang"
  - "Alex J. Malozemoff"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mpc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new protocol for two-party computation, secure against malicious adversaries, that is significantly faster than prior work in the single-execution setting (i.e., non-amortized and with no preprocessing). In particular, for computational security parameter κ and statistical security parameter ρ, our protocol uses only ρ garbled circuits and O(ρ + κ) public-key operations, whereas previous work with the same number of garbled circuits required either O(ρ · n + κ) public-key operations (where n is the input/output length) or a second execution of a secure-computation sub-protocol.

## Key claims (as reported)
- Our protocol can be based on the decisional Diffie-Hellman assumption in the standard model.
- We implement our protocol to evaluate its performance.
- With ρ = 40, our implementation securely computes an AES evaluation in 65 ms over a local-area network using a single thread without any pre-computation, 22× faster than the best prior work in the non-amortized setting.
- The relative performance of our protocol is even better for functions with larger input/output lengths.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210107 (1).pdf`
- `downloads/10210107.pdf`
