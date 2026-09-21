---
id: KN-LIT-5246
type: literature
title: "NTRU Fatigue: How Stretched is Overstretched ? Léo Ducas & Wessel van Woerden"
authors:
  - "Cryptology Group"
  - "The Netherlands"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Until recently lattice reduction attacks on NTRU lattices were thought to behave similar as on (ring-)LWE lattices with the same parameters. However several works (Albrecht-Bai-Ducas 2016, KirchnerFouque 2017) showed a significant gap for large moduli q, the so-called overstretched regime of NTRU.

## Key claims (as reported)
- With the NTRU scheme being a finalist to the NIST PQC competition it is important to understand —both asymptotically and concretely— where the fatigue point lies exactly, i.e. at which q the overstretched regime begins.
- Unfortunately the analysis by Kirchner and Fouque is based on an impossibility argument, which only results in an asymptotic upper bound on the fatigue point.
- It also does not really explain how lattice reduction actually recovers secret-key information.
- We propose a new analysis that asymptotically improves on that of Kirchner and Fouque, narrowing down the fatigue point for ternary NTRU from q ď n2.783`op1q to q “ n2.484`op1q , and finally explaining the mechanism behind this phenomenon.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900104 (1).pdf`
- `downloads/130900104.pdf`
