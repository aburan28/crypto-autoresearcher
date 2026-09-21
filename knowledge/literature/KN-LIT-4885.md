---
id: KN-LIT-4885
type: literature
title: "Meet-in-the-Middle Preimage Attacks"
authors:
  - "Against Reduced SHA"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Preimage resistance of several hash functions has already been broken by the meet-in-the-middle attacks and they utilize a property that their message schedules consist of only permutations of message words. It is unclear whether this type of attacks is applicable to a hash function whose message schedule does not consist of permutations of message words.

## Key claims (as reported)
- This paper proposes new attacks against reduced SHA-0 and SHA-1 hash functions by analyzing a message schedule that does not consist of permutations but linear combinations of message words.
- The newly developed cryptanalytic techniques enable the meet-in-the-middle attack to be applied to reduced SHA-0 and SHA-1 hash functions.
- The attacks find preimages of SHA-0 and SHA-1 in 2156.6 and 2159.3 compression function computations up to 52 and 48 steps, respectively, compared to the brute-force attack, which requires 2160 compression function computations.
- The previous best attacks find preimages up to 49 and 44 steps, respectively.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770071 (1).pdf`
- `downloads/56770071 (2).pdf`
- `downloads/56770071 (3).pdf`
- `downloads/56770071.pdf`
