---
id: KN-LIT-3904
type: literature
title: "Fine-Tuning Groth-Sahai Proofs"
authors:
  - "Alex Escala"
  - "Jens Groth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Groth-Sahai proofs are efficient non-interactive zero-knowledge proofs that have found widespread use in pairing-based cryptography. We propose efficiency improvements of Groth-Sahai proofs in the SXDH setting, which is the one that yields the most efficient non-interactive zero-knowledge proofs. – We replace some of the commitments with ElGamal encryptions, which reduces the prover’s computation and for some types of equations reduces the proof size. – Groth-Sahai proofs are zero-knowledge when no public elements are paired to each other.

## Key claims (as reported)
- We observe that they are also zero-knowledge when base elements for the groups are paired to public constants. – The prover’s computation can be reduced by letting her pick her own common reference string.
- By giving a proof she has picked a valid common reference string this does not compromise soundness. – We define a type-based commit-and-prove scheme, which allows commitments to be reused in many different proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830130 (1).pdf`
- `downloads/83830130 (2).pdf`
- `downloads/83830130 (3).pdf`
- `downloads/83830130 (4).pdf`
- `downloads/83830130 (5).pdf`
- `downloads/83830130.pdf`
