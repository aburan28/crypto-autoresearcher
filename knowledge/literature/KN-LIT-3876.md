---
id: KN-LIT-3876
type: literature
title: "Fiat–Shamir Bulletproofs are Non-Malleable (in the Algebraic Group Model) Chaya Ganesh1[0000−0002−2909−9177] , Claudio Orlandi2[0000−0003−4992−0249]"
authors:
  - "Mahak Pancholi"
  - "Akira Takahashi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bulletproofs (Bünz et al. IEEE S&P 2018) are a celebrated ZK proof system that allows for short and efficient proofs, and have been implemented and deployed in several real-world systems.

## Key claims (as reported)
- In practice, they are most often implemented in their non-interactive version obtained using the Fiat-Shamir transform, despite the lack of a formal proof of security for this setting.
- Prior to this work, there was no evidence that malleability attacks were not possible against Fiat-Shamir Bulletproofs.
- Malleability attacks can lead to very severe vulnerabilities, as they allow an adversary to forge proofs re-using or modifying parts of the proofs provided by the honest parties.
- In this paper, we show for the first time that Bulletproofs (or any other similar multi-round proof system satisfying some form of weak unique response property) achieve simulation-extractability in the algebraic group model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760140 (1).pdf`
- `downloads/132760140.pdf`
