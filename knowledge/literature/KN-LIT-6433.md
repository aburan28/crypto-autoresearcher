---
id: KN-LIT-6433
type: literature
title: "Secure Conversion Between Boolean and Arithmetic Masking of Any Order"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, mpc, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An effective countermeasure against side-channel attacks is to mask all sensitive intermediate variables with one (or more) random value(s). When a cryptographic algorithm involves both arithmetic and Boolean operations, it is necessary to convert from arithmetic masking to Boolean masking and vice versa.

## Key claims (as reported)
- At CHES 2001, Goubin introduced two algorithms for secure conversion between arithmetic and Boolean masks, but his approach can only be applied to first-order masking.
- In this paper, we present and evaluate new conversion algorithms that are secure against attacks of any order.
- To convert masks of a size of k bits securely against attacks of order n, the proposed algorithms have a time complexity of O(n2 k) in both directions and are proven to be secure in the Ishai, Sahai, and Wagner (ISW) framework for private circuits.
- We evaluate our algorithms using HMAC-SHA-1 as example and report the execution times we achieved on a 32-bit AVR microcontroller.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310157 (1).pdf`
- `downloads/87310157 (2).pdf`
- `downloads/87310157 (3).pdf`
- `downloads/87310157.pdf`
