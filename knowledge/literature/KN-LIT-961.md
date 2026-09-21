---
id: KN-LIT-961
type: literature
title: "Computing 2a-isogenies in Legendre Form"
authors:
  - "Jesse Elliott∗ Aaron Hutchinson David Jao"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/870"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/870"
tags: [curve-arithmetic, elliptic-curve, finite-field, hash, isogeny, mov-fr, pairing, pqc, side-channel, sidh-csidh, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a method for efficiently computing 2a -isogenies in Legendre form with applications in post-quantum cryptography. An example of a secure application is the Charles-GorenLauter (CGL) hash function [3], which recently saw significant improvement in complexity by Doliskani et al.

## Key claims (as reported)
- The majority of work on isogeny computation uses elliptic curves in Montgomery form; this includes the original work on SIDH by Jao, De Feo and Plût [10] and the state of the art implementation of SIKE [8].
- Elliptic curves in twisted Edwards form have also been used due to their efficient elliptic curve arithmetic, and complete Edwards curves have been used for their benefit of providing added security against side channel attacks (see Azarderakhsh et al.
- As far as we know, elliptic curves in Legendre form have not yet been explored for isogeny-based cryptography.
- Legendre form has the benefit of a very simple defining equation, and the simplest possible representation of the 2-torsion subgroup.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-870.pdf`
