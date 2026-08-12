---
id: KN-LIT-942
type: literature
title: "Verifiable Isogeny Walks: Towards an Isogeny-based Postquantum VDF"
authors:
  - "Jorge Chavez-Saab"
  - "Francisco Rodrı́guez-Henrı́quez"
  - "Mehdi Tibouchi"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1289"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1289"
tags: [dlp, elliptic-curve, hash, isogeny, pairing, quantum, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we investigate the problem of constructing postquantum-secure verifiable delay functions (VDFs), particularly based on supersingular isogenies. Isogeny-based VDF constructions have been proposed before, but since verification relies on pairings, they are broken by quantum computers.

## Key claims (as reported)
- We propose an entirely different approach using succinct non-interactive arguments (SNARGs), but specifically tailored to the arithmetic structure of the isogeny setting to achieve good asymptotic efficiency.
- We obtain an isogeny-based VDF construction with postquantum security, quasi-logarithmic verification, and requiring no trusted setup.
- As a building block, we also construct non-interactive arguments for isogeny walks in the supersingular graph over Fp2 , which may be of independent interest.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1289.pdf`
