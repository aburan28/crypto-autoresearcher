---
id: KN-LIT-2866
type: literature
title: "Chain Reductions for Multi-Signatures and the HBMS Scheme"
authors:
  - "Mihir Bellare"
  - "Wei Dai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, mov-fr, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Existing proofs for existing Discrete Log (DL) based multisignature schemes give only weak guarantees if the schemes are implemented, as they are in practice, in 256-bit groups. This is because the underlying reductions, which are mostly in the standard model and from DL, are loose.

## Key claims (as reported)
- We show that relaxing either the model or the assumption suffices to obtain tight reductions.
- Namely we give (1) tight proofs from DL in the Algebraic Group Model, and (2) tight, standard-model proofs from well-founded assumptions other than DL.
- We first do this for the classical 3-round schemes, namely BN and MuSig.
- Then we give a new 2-round multi-signature scheme, HBMS, as efficient as prior ones, for which we do the same.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900238 (1).pdf`
- `downloads/130900238.pdf`
