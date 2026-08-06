---
id: KN-LIT-3907
type: literature
title: "Fixing and Mechanizing the Security Proof of Fiat-Shamir with Aborts and Dilithium"
authors:
  - "Manuel Barbosa"
  - "Gilles Barthe"
  - "Christian Doczkal"
  - "Jelle Don"
  - "Serge Fehr"
  - "Benjamin Grégoire"
  - "Yu-Hsuan Huang"
  - "Andreas Hülsing"
  - "Yi Lee"
  - "Xiaodi Wu"
year: 2023
venue: "IACR ePrint preprint (CRYPTO 2023 or similar)"
identifiers:
  eprint: "2023/246"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/246"
tags: [dilithium, ml-dsa, fiat-shamir-with-aborts, cma-nma, easycrypt, rom, qrom, formal-verification, lattice-signature, pqc, provable-security]
confidence: abstract_verified
citation_verified: abstract_read_from_primary_eprint_page
eprint_id_correction: "2023/246 confirmed 2026-08-05; prior corpus entry had eprint:null (ANO-1 in BATCH-214d98)"
added: "2026-07-24"
updated: "2026-08-05"
superseded_by: null
---

## Contribution
Extends and consolidates the security justification for the Dilithium signature scheme. Identifies a subtle gap in several ROM and QROM CMA-to-NMA reductions for Fiat-Shamir-with-aborts schemes including Dilithium. Provides fixed proofs and a mechanized EasyCrypt verification.

## Key claims (abstract-verified, 2026-08-05)
- Gap in CMA-to-NMA reduction; uncovered when formalizing Kiltz-Lyubashevsky-Schaffner (Eurocrypt 2018) QROM proof.
- New fixed proofs for CMA-to-NMA in both ROM and QROM.
- Concrete security analysis shows claimed security level is still valid after the gap is addressed.
- Fully mechanized ROM proof for CMA-security of Dilithium in EasyCrypt proof assistant.

## Critical scope note for GOAL-MLDSA-001
The formal proof covers **CMA security in the ROM/QROM** — a purely cryptographic adversary model where the adversary queries signing oracles and hash oracles but does NOT physically tamper with the device. This proof does **NOT** cover:
- Physical fault injection (voltage glitch, laser, etc.)
- Any attack that requires manipulating the signing device's power or clock
- The Jendral (2024) nonce-erasure voltage-glitch attack (KN-LIT-4f3b80)
- The Shin et al. (2026) challenge-coefficient DFA (KN-LIT-340675)

Both Lane B hypotheses (H-MLDSA-f3a291, H-MLDSA-c7b4e8) are formally OUTSIDE this proof's scope by adversary-model construction, resolved at abstract level per DEC-20260805-6e3d22.

## Relevance to GOAL-MLDSA-001
- Primary source for the CMA-to-NMA tightness loss factor needed by IDEA-9c1e04 / EXP-MLDSA-3f7ab2
- Adversary model boundaries for Lane B fault coverage determination
- Full text access required for tightness factor; abstract only available here

## Local copies
- `downloads/140850158 (1).pdf`  (missing — not found on disk 2026-08-05)
- `downloads/140850158.pdf`  (missing — not found on disk 2026-08-05)
