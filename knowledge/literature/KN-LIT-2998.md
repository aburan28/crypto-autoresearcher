---
id: KN-LIT-2998
type: literature
title: "Compact VSS and Efficient Homomorphic UC Commitments"
authors:
  - "Ivan Damgård"
  - "Bernardo David"
  - "Irene Giacomelli"
  - "Jesper Buus Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new compact verifiable secret sharing scheme, based on this we present the first construction of a homomorphic UC commitment scheme that requires only cheap symmetric cryptography, except for a small number of seed OTs. To commit to a k-bit string, the amortized communication cost is O(k) bits.

## Key claims (as reported)
- Assuming a sufficiently efficient pseudorandom generator, the computational complexity is O(k) for the verifier and O(k1+ ) for the committer (where  < 1 is a constant).
- In an alternative variant of the construction, all complexities are O(k · polylog(k)).
- Our commitment scheme extends to vectors over any finite field and is additively homomorphic.
- By sending one extra message, the prover can allow the verifier to also check multiplicative relations on committed strings, as well as verifying that committed vectors a, b satisfy a = φ(b) for a linear function φ.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730260 (1).pdf`
- `downloads/88730260 (2).pdf`
- `downloads/88730260 (3).pdf`
- `downloads/88730260.pdf`
