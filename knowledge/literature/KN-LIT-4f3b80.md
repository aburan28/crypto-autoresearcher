---
id: KN-LIT-4f3b80
type: literature
title: "A Single-Trace Side-Channel Attack on ML-DSA: Practical Full-Key Recovery from a Single Faulty Signature"
authors: [Jendral]
venue: "IACR ePrint 2024/238"
year: 2024
url: "https://eprint.iacr.org/2024/238"
citation_verified: partial
citation_verified_note: Abstract read from primary ePrint page. Full text not obtained.
added: 2026-08-05
corrects_rq_mldsa_001_provisional:
  year_correction: "2024, not 2026 as stated in RQ-MLDSA-001 motivation (canonical per DEC-20260805-0d59ff)"
  probability_correction: "0.582 (58.2%), not ~53% as stated in RQ-MLDSA-001 motivation (canonical per DEC-20260805-0d59ff)"
tags: [ml-dsa, fips-204, voltage-glitch, single-trace, fault-injection, cortex-m4, hedged-signing]
key_claim: >-
  Single-trace voltage-glitch attack on hedged ML-DSA implemented on Cortex-M4;
  claims full key recovery from a single faulty signature with success probability
  0.582 (~58.2%). Classified as IMPLEMENTATION/FAULT level; not a mathematical
  break of MSIS or SelfTargetMSIS.
dominated_by: null
relevance_to_mldsa_001: >-
  Directly relevant to the fault-proof boundary question. Establishes that
  hedging does not prevent fault exploitation at the implementation level on
  at least one hardware target.
---
