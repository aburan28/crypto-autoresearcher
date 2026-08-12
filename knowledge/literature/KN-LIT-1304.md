---
id: KN-LIT-1304
type: literature
title: "SQIPrime: A dimension 2 variant of SQISignHD with non-smooth challenge isogenies"
authors:
  - "Max Duparc"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/773"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/773"
tags: [endomorphism, isogeny, pqc, quantum, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce SQIPrime, a post-quantum digital signature scheme based on the Deuring correspondence and Kani’s Lemma. Compared to its predecessors that are SQISign and especially SQISignHD, SQIPrime further expands the use of high dimensional isogenies, already in use in the verification in SQISignHD, to all its subroutines.

## Key claims (as reported)
- In doing so, it no longer relies on smooth degree isogenies (of dimension 1).
- Intriguingly, this includes the challenge isogeny which is also a non-smooth degree isogeny, but has an accessible kernel.
- The fact that the isogenies do not have rational kernel allows to fit more rational power 2 torsion points which are necessary when computing and representing the response isogeny.
- SQIPrime operates with prime numbers of the form p = 2α f − 1.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-773.pdf`
