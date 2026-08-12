---
id: KN-LIT-6816
type: literature
title: "Streaming Functional Encryption"
authors:
  - "Jiaxin Guan"
  - "Alexis Korb"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of streaming functional encryption (sFE) which is designed for scenarios in which data arrives in a streaming manner and is computed on in an iterative manner as the stream arrives. Unlike in a standard functional encryption (FE) scheme, in an sFE scheme, we (1) do not require the entire data set to be known at encryption time and (2) allow for partial decryption given only a prefix of the input.

## Key claims (as reported)
- More specifically, in an sFE scheme, we can sequentially encrypt each data point xi in a stream of data x = x1 . . . xn as it arrives, without needing to wait for all n values.
- We can then generate function keys for streaming functions which are stateful functions that take as input a message xi and a state sti and output a value yi and the next state sti+1 .
- For any k ≤ n, a user with a function key for a streaming function f can learn the first k output values y1 . . . yk where (yi , sti+1 ) = f (xi , sti ) and st1 = ⊥ given only ciphertexts for the first k elements x1 . . . xk .
- In this work, we introduce the notion of sFE and show how to construct it from FE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850111 (1).pdf`
- `downloads/140850111.pdf`
