---
id: KN-LIT-4489
type: literature
title: "Indistinguishability Obfuscation from LPN over Fp , DLIN, and"
authors:
  - "Aayush Jain"
  - "Huijia Lin"
  - "Amit Sahai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mov-fr, pairing, prime-field, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we study what minimal sets of assumptions suffice for constructing indistinguishability obfuscation (iO). We prove: Theorem(Informal): Assume sub-exponential security of the following assumptions: – the Learning Parity with Noise (LPN) assumption over general prime fields Fp with polynomially many LPN samples and error rate 1/kδ , where k is the dimension of the LPN secret, and δ > 0 is any constant; – the existence of a Boolean Pseudo-Random Generator (PRG) in NC0 with stretch n1+τ , where n is the length of the PRG seed, and τ > 0 is any constant; – the Decision Linear (DLIN) assumption on symmetric bilinear groups of prime order.

## Key claims (as reported)
- Then, (subexponentially secure) indistinguishability obfuscation for all polynomial-size circuits exists.
- Further, assuming only polynomial security of the aforementioned assumptions, there exists collusion resistant public-key functional encryption for all polynomial-size circuits.
- This removes the reliance on the Learning With Errors (LWE) assumption from the recent work of [Jain, Lin, Sahai STOC’21].
- As a consequence, we obtain the first fully homomorphic encryption scheme that does not rely on any lattice-based hardness assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760170 (1).pdf`
- `downloads/132760170.pdf`
