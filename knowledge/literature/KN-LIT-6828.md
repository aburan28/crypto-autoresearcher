---
id: KN-LIT-6828
type: literature
title: "Strong Security from Probabilistic Signature Schemes"
authors:
  - "Sven Schäge"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new and very weak security notion for signature schemes called target randomness security. In contrast to previous security definitions we focus on signature schemes with (public coin) probabilistic signature generation where the randomness used during signature generation is exposed as part of the signature.

## Key claims (as reported)
- To prove practical usefulness of our notion we present a new signature transformation for mapping target randomness secure signature schemes to weakly secure signature schemes.
- It is well-known that, using chameleon hash functions, the resulting weakly secure scheme can then be turned into a fully secure one.
- Our transformation outputs signature schemes that in general produce signatures with l elements, where l is the bit length of the input randomness.
- We present an instantiation of a target randomness secure signature scheme based on the RSA assumption and show that after applying our new signature transformation to this scheme, we can accumulate the l signature elements into a single element.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930087 (1).pdf`
- `downloads/72930087 (2).pdf`
- `downloads/72930087 (3).pdf`
- `downloads/72930087.pdf`
