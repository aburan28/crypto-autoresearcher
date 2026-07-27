---
id: KN-LIT-3125
type: literature
title: "Constrained PRFs for NC1 in"
authors:
  - "Shota Yamada"
  - "Takashi Yamakawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose new constrained pseudorandom functions (CPRFs) in traditional groups. Traditional groups mean cyclic and multiplicative groups of prime order that were widely used in the 1980s and 1990s (sometimes called “pairing free” groups).

## Key claims (as reported)
- Our main constructions are as follows. – We propose a selectively single-key secure CPRF for circuits with depth O(log n) (that is, NC1 circuits) in traditional groups where n is the input size.
- It is secure under the L-decisional Diffie-Hellman inversion (L-DDHI) assumption in the group of quadratic residues QRq and the decisional Diffie-Hellman (DDH) assumption in a traditional group of order q in the standard model. – We propose a selectively single-key private bit-fixing CPRF in traditional groups.
- It is secure under the DDH assumption in any primeorder cyclic group in the standard model. – We propose adaptively single-key secure CPRF for NC1 and private bit-fixing CPRF in the random oracle model.
- To achieve the security in the standard model, we develop a new technique using correlated-input secure hash functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993207 (1).pdf`
- `downloads/10993207.pdf`
