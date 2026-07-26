---
id: KN-LIT-2500
type: literature
title: "An Incremental PoSW for General Weight Distributions"
authors:
  - "Hamza Abusalah"
  - "Valerio Cini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A proof of sequential work (PoSW) scheme allows the prover to convince a verifier that it computed a certain number of computational steps sequentially. Very recently, graph-labeling PoSW schemes, found applications in light-client blockchain protocols, most notably bootstrapping.

## Key claims (as reported)
- A bootstrapping protocol allows a light client, with minimal information about the blockchain, to hold a commitment to its stable prefix.
- An incremental PoSW (iPoSW) scheme allows the prover to non-trivially increment proofs: given χ, π1 and integers N1 , N2 such that π1 is a valid proof for N1 , it generates a valid proof π for N1 + N2 .
- In this work, we construct an iPoSW scheme based on the skiplist-based PoSW scheme of Abusalah et al. and prove its security in the random oracle model by employing the powerful on-the-fly sampling technique of Döttling et al.
- Moreover, unlike the iPoSW scheme of Döttling et al., ours is the first iPoSW scheme which is suitable for constructing incremental non-interactive arguments of chain knowledge (SNACK) schemes, which are at the heart of space and time efficient blockchain light-client protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004405 (1).pdf`
- `downloads/14004405.pdf`
