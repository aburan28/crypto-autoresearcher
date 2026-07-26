---
id: KN-LIT-6699
type: literature
title: "SipHash: a fast short-input PRF"
authors:
  - "Jean-Philippe Aumasson"
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, prime-field, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SipHash is a family of pseudorandom functions optimized for short inputs. Target applications include network traffic authentication and hash-table lookups protected against hash-flooding denial-of-service attacks.

## Key claims (as reported)
- SipHash is simpler than MACs based on universal hashing, and faster on short inputs.
- Compared to dedicated designs for hash-table lookup, SipHash has well-defined security goals and competitive performance.
- For example, SipHash processes a 16-byte input with a fresh key in 140 cycles on an AMD FX-8150 processor, which is much faster than state-of-the-art MACs.
- We propose that hash tables switch to SipHash as a hash function.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/siphash-20120918.pdf`
