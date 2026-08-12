---
id: KN-LIT-3564
type: literature
title: "Efficient Generic Forward-Secure Signatures With An Unbounded Number Of Time Periods"
authors:
  - "Tal Malkin"
  - "Daniele Micciancio"
  - "Sara Miner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first efficient forward-secure digital signature scheme where the total number of time periods for which the public key is used does not have to be fixed in advance. The number of time periods for which our scheme can be used is bounded only by an exponential function of the security parameter (given this much time, any scheme can be broken by exhaustive search), and its performance depends (minimally) only on the time elapsed so far.

## Key claims (as reported)
- Our scheme achieves excellent performance overall, is very competitive with previous schemes with respect to all parameters, and outperforms each of the previous schemes in at least one parameter.
- Moreover, the scheme can be based on any underlying digital signature scheme, and does not rely on specific assumptions.
- Its forward security is proven in the standard model, without using a random oracle.
- As an intermediate step in designing our scheme, we propose and study two general composition operations that can be used to combine any existing signature schemes (whether standard or forward-secure) into new forward-secure signature schemes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/EC02final (1).pdf`
- `downloads/EC02final (2).pdf`
- `downloads/EC02final.pdf`
