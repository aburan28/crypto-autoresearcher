---
id: KN-LIT-7220
type: literature
title: "Towards Non-Interactive Witness Hiding"
authors:
  - "Benjamin Kuykendall"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Witness hiding proofs require that the verifier cannot find a witness after seeing a proof. The exact round complexity needed for witness hiding proofs has so far remained an open question.

## Key claims (as reported)
- In this work, we provide compelling evidence that witness hiding proofs are achievable non-interactively for wide classes of languages.
- We use non-interactive witness indistinguishable proofs as the basis for all of our protocols.
- We give four schemes in different settings under different assumptions: – A universal non-interactive proof that is witness hiding as long as any proof system, possibly an inefficient and/or non-uniform scheme, is witness hiding, has a known bound on verifier runtime, and has short proofs of soundness. – A non-uniform non-interactive protocol justified under a worst-case complexity assumption that is witness hiding and efficient, but may not have short proofs of soundness. – A new security analysis of the two-message argument of Pass [Crypto 2003], showing witness hiding for any non-uniformly hard distribution.
- We propose a heuristic approach to removing the first message, yielding a non-interactive argument. – A witness hiding non-interactive proof system for languages with unique witnesses, assuming the non-existence of a weak form of witness encryption for any language in NP ∩ coNP.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550225 (1).pdf`
- `downloads/12550225.pdf`
