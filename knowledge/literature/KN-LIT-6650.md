---
id: KN-LIT-6650
type: literature
title: "Simple and More Efficient PRFs with Tight Security from LWE and Matrix-DDH?"
authors:
  - "Tibor Jager"
  - "Rafael Kurek"
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct efficient and tightly secure pseudorandom functions (PRFs) with only logarithmic security loss and short secret keys. This yields very simple and efficient variants of well-known constructions, including those of Naor-Reingold (FOCS 1997) and Lewko-Waters (ACM CCS 2009).

## Key claims (as reported)
- Most importantly, in combination with the construction of Banerjee, Peikert and Rosen (EUROCRYPT 2012) we obtain the currently most efficient LWE-based PRF from a weak LWE-assumption with a much smaller modulus than the original construction.
- In comparison to the only previous construction with this property, which is due to Döttling and Schröder (CRYPTO 2015), we use a modulus of similar size, but only a single instance of the underlying PRF, instead of λ·ω(log λ) parallel instances, where λ is the security parameter.
- Like Döttling and Schröder, our security proof is only almost back-box, due to the fact that the number of queries made by the adversary and its advantage must be known a-priori.
- Technically, we introduce all-prefix universal hash functions (APUHFs), which are hash functions that are (almost-)universal, even if any prefix of the output is considered.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272221 (1).pdf`
- `downloads/11272221.pdf`
