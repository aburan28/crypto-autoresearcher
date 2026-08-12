---
id: KN-LIT-4081
type: literature
title: "Generic Attack on Duplex-Based AEAD Modes using Random Function Statistics"
authors:
  - "Henri Gilbert"
  - "Rachelle Heim Boissier"
  - "Louiza Khati"
  - "Yann Rotella"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Duplex-based authenticated encryption modes with a sufficiently large key length are proven to be secure up to the birthday bound c 2 2 , where c is the capacity. However this bound is not known to be tight and the complexity of the best known generic attack, which is based on c multicollisions, is much larger: it reaches 2α where α represents a small security loss factor.

## Key claims (as reported)
- There is thus an uncertainty on the true extent of c security beyond the bound 2 2 provided by such constructions.
- In this paper, we describe a new generic attack against several duplex-based AEAD modes.
- Our attack leverages random functions statistics and pro3c duces a forgery in time complexity O(2 4 ) using negligible memory and no encryption queries.
- Furthermore, for some duplex-based modes, our attack recovers the secret key with a negligible amount of additional computations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004225 (1).pdf`
- `downloads/14004225.pdf`
