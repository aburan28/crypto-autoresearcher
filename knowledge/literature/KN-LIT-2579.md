---
id: KN-LIT-2579
type: literature
title: "Aspects of Hyperelliptic Curves over Large Prime"
authors:
  - "Fields in Software Implementations"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, finite-field, hyperelliptic, implementation, jacobian, mov-fr, pairing, prime-field, provable-security, quantum, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an implementation of elliptic curves and of hyperelliptic curves of genus 2 and 3 over prime fields. To achieve a fair comparison between the different types of groups, we developed an ad-hoc arithmetic library, designed to remove most of the overheads that penalize implementations of curve-based cryptography over prime fields.

## Key claims (as reported)
- These overheads get worse for smaller fields, and thus for larger genera for a fixed group size.
- We also use techniques for delaying modular reductions to reduce the amount of modular reductions in the formulae for the group operations.
- The result is that the performance of hyperelliptic curves of genus 2 over prime fields is much closer to the performance of elliptic curves than previously thought.
- For groups of 192 and 256 bits the difference is about 14% and 15% respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560147 (1).pdf`
- `downloads/31560147 (2).pdf`
- `downloads/31560147.pdf`
