---
id: KN-LIT-7174
type: literature
title: "To Infinity and Beyond: Combined Attack on ECC using Points of Low Order"
authors:
  - "Junfeng Fan"
  - "Benedikt Gierlichs"
  - "Frederik Vercauteren"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, elliptic-curve, isogeny, pairing, prime-field, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a novel combined attack against ECC implementations that exploits specially crafted, but valid input points. The core idea is that after fault injection, these points turn into points of very low order.

## Key claims (as reported)
- Using side channel information we deduce when the point at infinity occurs during the scalar multiplication, which leaks information about the secret key.
- In the best case, our attack breaks a simple and differential side channel analysis resistant implementation with input/output point validity and curve parameter checks using a single query.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170143 (1).pdf`
- `downloads/69170143 (2).pdf`
- `downloads/69170143 (3).pdf`
- `downloads/69170143.pdf`
