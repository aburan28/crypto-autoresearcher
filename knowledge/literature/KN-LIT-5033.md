---
id: KN-LIT-5033
type: literature
title: "Multiparty Computation from Somewhat Homomorphic Encryption"
authors:
  - "Ivan Damgård"
  - "Valerio Pastro"
  - "Nigel Smart"
  - "Sarah Zakarias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a general multiparty computation protocol secure against an active adversary corrupting up to n − 1 of the n players. The protocol may be used to compute securely arithmetic circuits over any finite field Fpk .

## Key claims (as reported)
- Our protocol consists of a preprocessing phase that is both independent of the function to be computed and of the inputs, and a much more efficient online phase where the actual computation takes place.
- The online phase is unconditionally secure and has total computational (and communication) complexity linear in n, the number of players, where earlier work was quadratic in n.
- Moreover, the work done by each player is only a small constant factor larger than what one would need to compute the circuit in the clear.
- We show this is optimal for computation in large fields.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170637 (1).pdf`
- `downloads/74170637 (2).pdf`
- `downloads/74170637 (3).pdf`
- `downloads/74170637 (4).pdf`
- `downloads/74170637 (5).pdf`
- `downloads/74170637.pdf`
