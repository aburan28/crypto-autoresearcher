---
id: KN-LIT-4088
type: literature
title: "Generic Constructions for Chosen-Ciphertext Secure Attribute Based Encryption"
authors:
  - "Shota Yamada"
  - "Nuttapong Attrapadung"
  - "Goichiro Hanaoka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we propose generic conversions for transforming a chosen-plaintext (CPA) secure attribute-based encryption (ABE) to a chosen-ciphertext (CCA) secure ABE. The only known generic conversion, to the best of our knowledge, was presented by Goyal et al. in ACM-CCS 2006, which itself subsumes the well-known IBE-to-PKE conversion by Canetti, Halevi, and Katz proposed in Eurocrypt 2004.

## Key claims (as reported)
- The method by Goyal et al. has some restrictions that it assumes the delegatability of the original ABE and can deal only with the key-policy type of ABE with large attribute universe.
- In contrast, our methodology is applicable also to those ABE schemes without known delegatability.
- Furthermore, it works for both key-policy or ciphertext-policy flavors of ABE and can deal with both small and large universe scheme.
- More precisely, our method assumes only either delegatability or a newly introduced property called verifiability of ABE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710074 (1).pdf`
- `downloads/65710074 (2).pdf`
- `downloads/65710074 (3).pdf`
- `downloads/65710074.pdf`
