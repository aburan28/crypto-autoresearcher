# ECC2K-130 null note (Stage 0)

**Claim (structural, arithmetic-only):** ECC2K-130 uses a Koblitz curve over
`F_{2^{131}}` with **prime** extension degree `n = 131`.

**Consequence for T_k / Arm B:** There is **no intermediate subfield**
`F_{2^d}` with `1 < d < 131` and `d | 131` other than the trivial `F_2`.
Therefore the Gaudry / Gorla–Massierer **trace-zero variety** construction that
descends through a composite `F_{q^k}/F_q` with `q = 2^{16}` **does not apply**.
ECC2K-130 is a **null** for the T_k / Arm B line audited in this experiment.

**Not claimed:** Nothing about the hardness of ECDLP on ECC2K-130, Semaev
index calculus over `F_2`, or Frobenius-endomorphism speedups. This note only
records the absence of a T_k intermediate-subfield structure.

**Sources (internal):** `analysis/binstd-curve-audit/README.md` (prime extension
degrees include 131); EXP-BINSTD-1a7892 specification Stage 0 item (vii).

**T4 fields:** This note does not print `naive_bits`. The OPEN missing quantity
for the five composite ANSI rows remains:
per-trial cost at arity 10–22 over `F_2^{16}`.
