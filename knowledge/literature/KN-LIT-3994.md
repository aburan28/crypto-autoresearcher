---
id: KN-LIT-3994
type: literature
title: "Fully Homomorphic NIZK and NIWI Proofs"
authors:
  - "Prabhanjan Ananth"
  - "Apoorvaa Deshpande"
  - "Yael Tauman Kalai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we define and construct fully homomorphic non-interactive zero knowledge (FH-NIZK) and non-interactive witnessindistinguishable (FH-NIWI) proof systems. We focus on the NP complete language L, where, for a boolean circuit C and a bit b, the pair (C, b) ∈ L if there exists an input w such that C(w) = b.

## Key claims (as reported)
- For this language, we call a non-interactive proof system fully homomorphic if, given instances (Ci , bi ) ∈ L along with their proofs Πi , for i ∈ {1, . . . , k}, and given any circuit D : {0, 1}k → {0, 1}, one can efficiently compute a proof Π for (C ∗ , b) ∈ L, where C ∗ (w(1) , . . . , w(k) ) = D(C1 (w(1) ), . . . , Ck (w(k) )) and D(b1 , . . . , bk ) = b.
- The key security property is unlinkability: the resulting proof Π is indistinguishable from a fresh proof of the same statement.
- Our first result, under the Decision Linear Assumption (DLIN), is an FH-NIZK proof system for L in the common random string model.
- Our more surprising second result (under a new decisional assumption on groups with bilinear maps) is an FH-NIWI proof system that requires no setup.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11891160 (1).pdf`
- `downloads/11891160.pdf`
