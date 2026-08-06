---
id: KN-LIT-8ce0b5
type: literature
title: "Rank Bounds for NTT Twiddle-Factor Fault Attacks on ML-DSA (Lean 4 Machine-Checked)"
authors: [Gupta]
venue: "IACR ePrint 2026/1188"
year: 2026
url: "https://eprint.iacr.org/2026/1188"
citation_verified: partial
citation_verified_note: Abstract read from primary ePrint page. Full text not obtained.
added: 2026-08-05
tags: [ml-dsa, fips-204, ntt, twiddle-factor, fault-injection, formal-verification, lean4, rank-bound]
key_claim: >-
  Derives a formally machine-checked (Lean 4) upper bound on the number of
  independent linear constraints a twiddle-factor fault in the NTT can reveal
  about the ML-DSA secret key. Classified as IMPLEMENTATION/FAULT (security
  bound for a specific fault class); not a mathematical break of MSIS or
  SelfTargetMSIS.
dominated_by: null
relevance_to_mldsa_001: >-
  Relevant to the fault-proof boundary question: provides a formal leakage
  bound for the NTT fault class, which helps classify whether specific NTT
  faults are inside or outside the existing security proof guarantee.
---
