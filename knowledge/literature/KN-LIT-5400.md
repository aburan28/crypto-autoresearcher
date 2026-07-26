---
id: KN-LIT-5400
type: literature
title: "On Seed-Incompressible Functions"
authors:
  - "Shai Halevi"
  - "Steven Myers"
  - "Charles Rackoff"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate a new notion of security for “cryptographic functions” that we term seed incompressibility (SI). We argue that this notion captures some of the intuition for the alleged security of constructions in the random-oracle model, and indeed we show that seed incompressibility suffices for some applications of the random oracle methodology.

## Key claims (as reported)
- Very roughly, a function family fs (·) with |s| = n is seed incompressible if given (say) n/2 bits of advice (that can depend on the seed s) and an oracle access to fs (·), an adversary cannot “break fs (·)” any better than given only oracle access to fs (·) and no advice.
- The strength of this notion depends on what we mean by “breaking fs (·)”.
- We first show that for any family fs there exists an adversary that can distinguish fs (·) from a random function using n/2 bits of advice, so seed incompressible pseudo-random functions do not exist.
- Then we consider the weaker notion of seed-incompressible correlation intractability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49480014 (1).pdf`
- `downloads/49480014 (2).pdf`
- `downloads/49480014 (3).pdf`
- `downloads/49480014.pdf`
