---
id: KN-LIT-2828
type: literature
title: "Calamari and Falafl: Logarithmic (Linkable) Ring Signatures from Isogenies and Lattices"
authors:
  - "Ward Beullens"
  - "Shuichi Katsumata"
  - "Federico Pintore"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, isogeny, lattice, pairing, pqc, sidh-csidh, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct efficient ring signatures (RS) from isogeny and lattice assumptions. Our ring signatures are based on a logarithmic OR proof for group actions.

## Key claims (as reported)
- We instantiate this group action by either the CSIDH group action or an MLWE-based group action to obtain our isogeny-based or lattice-based RS scheme, respectively.
- Even though the OR proof has a binary challenge space and therefore requires a number of repetitions which is linear in the security parameter, the sizes of our ring signatures are small and scale better with the ring size N than previously known post-quantum ring signatures.
- We also construct linkable ring signatures (LRS) that are almost as efficient as the non-linkable variants.
- The isogeny-based scheme produces signatures whose size is an order of magnitude smaller than all previously known logarithmic post-quantum ring signatures, but it is relatively slow (e.g.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491294 (1).pdf`
- `downloads/12491294.pdf`
