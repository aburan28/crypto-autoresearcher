---
id: KN-LIT-5127
type: literature
title: "New MILP Modeling: Improved Conditional Cube Attacks on Keccak-based Constructions"
authors:
  - "Ling Song"
  - "Jian Guo"
  - "Danping Shi"
  - "San Ling"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a new MILP modeling to find better or even optimal choices of conditional cubes, under the general framework of conditional cube attacks. These choices generally find new or improved attacks against the keyed constructions based on Keccak permutation and its variants, including Keccak-MAC, KMAC, Keyak, and Ketje, in terms of attack complexities or the number of attacked rounds.

## Key claims (as reported)
- Interestingly, conditional cube attacks were applied to round-reduced Keccak-MAC, but not to KMAC despite the great similarity between Keccak-MAC and KMAC, and the fact that KMAC is the NIST standard way of constructing MAC from SHA-3.
- As examples to demonstrate the effectiveness of our new modeling, we report key recovery attacks against KMAC128 and KMAC256 reduced to 7 and 9 rounds, respectively; the best attack against Lake Keyak with 128-bit key is improved from 6 to 8 rounds in the nonce-respected setting and 9 rounds of Lake Keyak can be attacked if the key size is of 256 bits; attack complexity improvements are found generally on other constructions.
- Our new model is also applied to Keccak-based full-state keyed sponge and gives a positive answer to the open question proposed by Bertoni et al. whether cube attacks can be extended to more rounds by exploiting full-state absorbing.
- To verify the correctness of our attacks, reduced-variants of the attacks are implemented and verified on a PC practically.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272328 (1).pdf`
- `downloads/11272328.pdf`
