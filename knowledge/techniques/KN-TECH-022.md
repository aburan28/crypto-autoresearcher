---
id: KN-TECH-022
type: technique
title: Structured-lattice problems (ideal/module) and the NIST PQC lattice schemes
tags: [ring-lwe, module-lwe, ntru, kyber, dilithium, falcon, nist, post-quantum, structured-lattice, adjacent]
confidence: reported
complexity: security parameterized to ~128/192/256-bit targets via BKZ/sieving estimates on the underlying module/ideal lattice
applicability: efficient lattice cryptosystems (KEMs and signatures) — post-quantum replacements for ECDLP/(EC)DH crypto
source_refs: [KN-LIT-052, KN-LIT-053, KN-LIT-054, KN-LIT-055, KN-LIT-056, KN-LIT-057]
added: 2026-07-23
superseded_by: null
---

## Landscape
Practical lattice crypto uses ALGEBRAICALLY STRUCTURED lattices for efficiency:
- **NTRU** (KN-LIT-052): short vectors in a convolution-ring lattice.
- **Ring-LWE** (KN-LIT-053): LWE over a polynomial ring (ideal lattices) -- small
  keys, near-linear ops.
- **Module-LWE/SIS** (KN-LIT-054): interpolates unstructured and ring settings
  over module lattices (tunable "module rank"), a more conservative assumption.
Deployed NIST standards built on these:
- **ML-KEM / Kyber** (KN-LIT-055, FIPS 203): Module-LWE KEM.
- **ML-DSA / Dilithium** (KN-LIT-056, FIPS 204): Module-LWE/SIS Fiat-Shamir-with-
  aborts signature.
- **FN-DSA / Falcon** (KN-LIT-057, FIPS 206 draft): NTRU-lattice GPV hash-and-sign.

## Relevance to this program
ADJACENT to (not part of) the ECDLP mission: these are the concrete schemes chosen
to REPLACE ECDLP/(EC)DH crypto because ECDLP falls to Shor while lattice problems
are conjectured quantum-hard. Recorded so the corpus documents what supersedes the
program's classical primitive, and where the two domains do and do not touch
(the lattice/ECDLP intersection is confined to signature nonce leakage,
KN-TECH-019, not to the schemes' core hardness).

## Applicability limits
Concrete security rests on cryptanalysis of the structured lattice (BKZ/sieving
estimates, KN-TECH-020, KN-TECH-023), not on the asymptotic worst-case reductions.
The added ring/module structure is a potential attack surface: whether it enables
attacks beyond generic (unstructured) lattice algorithms is an active question
(KN-OPEN-012). None of this bears on ECDLP hardness.
