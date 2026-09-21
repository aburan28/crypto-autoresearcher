---
id: KN-LIT-3377
type: literature
title: "Delay Encryption"
authors:
  - "Jeffrey Burdges"
  - "Luca De Feo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, isogeny, mov-fr, pairing, provable-security, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new primitive named Delay Encryption, and give an efficient instantation based on isogenies of supersingular curves and pairings. Delay Encryption is related to Time-lock Puzzles and Verifiable Delay Functions, and can be roughly described as “time-lock identity based encryption”.

## Key claims (as reported)
- It has several applications in distributed protocols, such as sealed bid Vickrey auctions and electronic voting.
- We give an instantiation of Delay Encryption by modifying Boneh and Frankiln’s IBE scheme, where we replace the master secret key by a long chain of isogenies, as in the isogeny VDF of De Feo, Masson, Petit and Sanso.
- Similarly to the isogeny-based VDF, our Delay Encryption requires a trusted setup before parameters can be safely used; our trusted setup is identical to that of the VDF, thus the same parameters can be generated once and shared for many executions of both protocols, with possibly different delay parameters.
- We also discuss several topics around delay protocols based on isogenies that were left untreated by De Feo et al., namely: distributed trusted setup, watermarking, and implementation issues.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960126 (1).pdf`
- `downloads/126960126.pdf`
