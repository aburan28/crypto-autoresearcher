---
id: KN-LIT-7269
type: literature
title: "Triply Adaptive UC NIZK"
authors:
  - "Ran Canetti"
  - "Pratik Sarkar"
  - "Xiao Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-interactive zero knowledge (NIZK) enables proving the validity of NP statement without leaking anything else. We study multiinstance NIZKs in the common reference string (CRS) model, against an adversary that adaptively corrupts parties and chooses statements to be proven.

## Key claims (as reported)
- We construct the first such triply adaptive NIZK that provides full adaptive soundness, as well as adaptive zero-knowledge, assuming either LWE or else LPN and DDH (previous constructions rely on non-falsifiable knowledge assumptions).
- In addition, our NIZKs are universally composable (UC).
- Along the way, we: - Formulate an ideal functionality, FNICOM , which essentially captures non-interactive commitments, and show that it is realizable by existing protocols using standard assumptions. - Define and realize, under standard assumptions, Sigma protocols which satisfy triply adaptive security with access to FNICOM . - Use the Fiat-Shamir transform, instantiated with correlation intractable hash functions, to compile a Sigma protocol with triply adaptive security with access to FNICOM into a triply adaptive UCNIZK argument in the CRS model with access to FNICOM , assuming LWE (or else LPN and DDH). - Use the UC theorem to obtain UC-NIZK in the CRS model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910210 (1).pdf`
- `downloads/137910210.pdf`
