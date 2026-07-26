---
id: KN-LIT-7278
type: literature
title: "Tweakable Blockciphers with Beyond Birthday-Bound Security"
authors:
  - "Will Landecker"
  - "Thomas Shrimpton"
  - "R. Seth Terashima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Liskov, Rivest and Wagner formalized the tweakable blockcipher (TBC) primitive at CRYPTO’02. The typical recipe for instantiating a TBC is to start with a blockcipher, and then build up a construction that admits a tweak.

## Key claims (as reported)
- Almost all such constructions enjoy provable security only to the birthday bound, and the one that does achieve security beyond the birthday bound (due to Minematsu) severely restricts the tweak size and requires per-invocation blockcipher rekeying.
- This paper gives the first TBC construction that simultaneously allows for arbitrarily “wide” tweaks, does not rekey, and delivers provable security beyond the birthday bound.
- Our construction is built from a blockcipher and an -AXU2 hash function.
- As an application of the TBC primitive, LRW suggest the TBC-MAC construction (similar to CBC-MAC but chaining through the tweak), but leave open the question of its security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170014 (1).pdf`
- `downloads/74170014 (2).pdf`
- `downloads/74170014 (3).pdf`
- `downloads/74170014 (4).pdf`
- `downloads/74170014 (5).pdf`
- `downloads/74170014.pdf`
