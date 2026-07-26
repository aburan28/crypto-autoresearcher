---
id: KN-LIT-2663
type: literature
title: "Batch NFS"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, factoring, hyperelliptic, implementation, mov-fr, number-theory, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper shows, assuming standard heuristics regarding the number-field sieve, that a “batch NFS” circuit of area L1.181...+o(1) factors L0.5+o(1) separate B-bit RSA keys in time L1.022...+o(1) . Here L = exp((log 2B )1/3 (log log 2B )2/3 ).

## Key claims (as reported)
- The circuit’s area-time product (priceperformance ratio) is just L1.704...+o(1) per key.
- For comparison, the best area-time product known for a single key is L1.976...+o(1) .
- This paper also introduces new “early-abort” heuristics implying that “early-abort ECM” improves the performance of batch NFS by a superpolynomial factor, specifically exp((c + o(1))(log 2B )1/6 (log log 2B )5/6 ) where c is a positive constant.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/batchnfs-20141109.pdf`
