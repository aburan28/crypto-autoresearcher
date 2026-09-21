---
id: KN-LIT-7357
type: literature
title: "Unconditionally-Secure Robust Secret Sharing with Compact Shares"
authors:
  - "Alfonso Cevallos"
  - "Serge Fehr"
  - "Rafail Ostrovsky"
  - "Yuval Rabani"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, lattice, mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of reconstructing a shared secret in the presence of faulty shares, with unconditional security. We require that any t shares give no information on the shared secret, and reconstruction is possible even if up to t out of the n shares are incorrect.

## Key claims (as reported)
- The interesting setting is n/3 ≤ t < n/2, where reconstruction of a shared secret in the presence of faulty shares is possible, but only with an increase in the share size, and only if one admits a small failure probability.
- The goal of this work is to minimize this overhead in the share size.
- Known schemes either have a Ω(κn)-overhead in share size, where κ is the security parameter, or they have a close-to-optimal overhead of order O(κ + n) but have an exponential running time (in n).
- In this paper, we propose a new scheme that has a close-to-optimal overhead in the share size of order Õ(κ + n), and a polynomial running time.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370190 (1).pdf`
- `downloads/72370190 (2).pdf`
- `downloads/72370190 (3).pdf`
- `downloads/72370190.pdf`
