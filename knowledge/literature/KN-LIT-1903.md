---
id: KN-LIT-1903
type: literature
title: "The Algebraic Isogeny Model: A General Model with"
authors:
  - "Applications to SQIsign"
  - "Key Exchanges"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/032"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/032"
tags: [complexity-theory, dlp, elliptic-curve, isogeny, pairing, pqc, protocol, provable-security, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the Algebraic Isogeny Model (AIM): an algebraic model, akin to the Algebraic Group Model in the group setting, for isogenies and supersingular elliptic curves. This model is significantly more general than previous ones, such as the Algebraic Group Action Model: the AIM works with arbitrary isogenies over Fp2 , rather than being limited to oriented ones, which gives considerably more power to the adversary.

## Key claims (as reported)
- Within this model, we obtain three results.
- First, we show that any result in the AGAM can be lifted to the AIM, strengthening previous results against more powerful adversaries.
- Then, we prove that the SQIsign identification protocol is ID-sound: in turn, this implies that SQIsign is EUF-CMA secure in the Quantum Random Oracle Model, resolving (in the AIM) a long-standing open problem.
- Lastly, we establish the equivalence of the DLOG and CDH problems for all SIDH-derived key exchanges, such as M-SIDH, binSIDH, and terSIDH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-032.pdf`
