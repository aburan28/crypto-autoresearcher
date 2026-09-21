---
id: KN-LIT-7617
type: literature
title: Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber
authors: [Carrier Kevin, Meyer-Hilfiger Charles, Shen Yixin, Tillich Jean-Pierre]
year: 2025
venue: ePrint 2022/1750 (rev. 2025-06-11); CRYPTO 2025 line
identifiers:
  eprint: iacr:2022/1750
  doi: null
  url: https://eprint.iacr.org/2022/1750
tags: [dual-attack, polar-code, fft, lwe, kyber, ml-kem, matzov, repaired-heuristics, concrete-security, contested, lattice, nist]
confidence: reported
citation_verified: read
added: 2026-07-31
superseded_by: null
---

## Contribution
A coding-theoretic repair of the MATZOV dual-attack template (KN-LIT-110)
that replaces modulus switching with generalized polar decoding over Z_q and
avoids the independence assumptions contested by Ducas–Pulles (KN-LIT-111).
Claims experimental backup of the repaired analysis and concrete costs for
Kyber-512/768/1024.

## Key claims (as reported; read from ePrint PDF abstract + §5 / App. C)
- Analysis does **not** use the flawed MATZOV independence assumptions
  criticized in KN-LIT-111; polar-code decoding distortion is benchmarked.
- Enumeration over a secret portion is replaced by iterating “assume that
  portion is zero” over choices of the enumerated coordinates.
- In the same nearest-neighbor cost model as the Kyber submission / MATZOV,
  claimed attack costs put Kyber-512/768/1024 at **3.5 / 11.9 / 12.3 bits
  below** the NIST classical requirements (143 / 207 / 272 bits).
- Appendix C.1 lists attack parameters (m, β_bkz, β_sieve, n_enu, n_fft,
  k_fft, n_lat, …) for three cost-model variants (C0 / CC / CN columns in
  Table 5.1).
- Authors state they are outside the Ducas–Pulles contradictory regime for
  the chosen parameters.

## Relevance to this program
This is the leading **post-objection** dual-attack claim against Kyber /
ML-KEM parameters. Settling whether its cost arithmetic and polar-decoding
heuristics survive independent re-derivation and small-dimension experiments
is exactly KN-OPEN-016’s residual question and the target lane of
GOAL-MLKEM-003 / RQ-MLKEM-003.

## Local primary
- HAL PDF: `experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`
  (hal-05406481; ePrint was CONNECT-403 from this harness).
- Authors' optimizer pickle:
  `experiments/EXP-MLKEM-010/vendor-lock/optimized_withExperimentalPolar.pkl`
  from `kevin-carrier/CodedDualAttack` @ `9c1367f`.

## Program verification (EV-MLKEM-016 / KN-FIND-016)
- Table 5.1 Algorithm-3.1 columns match the pickle within 0.05 bits (all nine
  cells); Theorem 4.1 recomputed from pickle intermediates matches.
- Abstract shortfalls 3.5/11.9/12.3 are exactly NIST−CC and are arithmetically
  supported given those intermediates.
- **Table C.2 erratum:** printed `log2(Tsample)=143.30` for CN/Kyber-512 is
  inconsistent with pickle ≈134.30; digit transposition explains the
  paper-only Thm-4.1 anomaly. Table 5.1 CN 134.5 is the consistent figure.
- Polar-decoding / `Pwrong` heuristics were **not** validated here.
  lattice-estimator MATZOV dual comparison is EV-MLKEM-015 / KN-FIND-015.

## Not verified here
Full proofs of Lemmas 3.x–4.x were not re-derived. Polar decoder experiments
were not reproduced. FIPS 203 text was not cross-checked (nist.gov blocked;
Kyber Round-3 KN-LIT-7618 is the parameter primary).
