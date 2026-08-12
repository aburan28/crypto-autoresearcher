---
id: KN-LIT-2909
type: literature
title: "Circular and KDM Security for Identity-Based Encryption"
authors:
  - "Jacob Alperin-Sheriff"
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of security for key-dependent messages (KDM), sometimes also known as “circular” or “clique” security, in the setting of identity-based encryption (IBE). Circular/KDM security requires that ciphertexts preserve secrecy even when they encrypt messages that may depend on the secret keys, and arises in natural usage scenarios for IBE.

## Key claims (as reported)
- We construct an IBE system that is circular secure for affine functions of users’ secret keys, based on the learning with errors (LWE) problem (and hence on worst-case lattice problems).
- The scheme is secure in the standard model, under a natural extension of a selective-identity attack.
- Our three main technical contributions are (1) showing the circular/KDMsecurity of a “dual”-style LWE public-key cryptosystem, (2) proving the hardness of a version of the “extended LWE” problem due to O’Neill, Peikert and Waters (CRYPTO’11), and (3) building an IBE scheme around the dual-style system using a novel lattice-based “all-but-d” trapdoor function.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930336 (1).pdf`
- `downloads/72930336 (2).pdf`
- `downloads/72930336 (3).pdf`
- `downloads/72930336.pdf`
