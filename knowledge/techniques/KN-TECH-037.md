---
id: KN-TECH-037
type: technique
title: Quantum ECDLP resource estimation (Shor circuits for elliptic curves)
tags: [quantum, shor, resource-estimate, toffoli, qubits, reversible-arithmetic, nist-curves, prime-field, post-quantum, cost-model, model-boundary, ecdlp]
confidence: reported
complexity: 9n + 2*ceil(log2 n) + 10 logical qubits and <= 448 n^3 log2(n) + 4090 n^3 Toffoli gates for an n-bit prime field; P-256 needs 2330 logical qubits and ~1.26e11 Toffoli gates
applicability: scoping the model boundary of any classical advantage claim, and comparing ECC against RSA at matched classical security; logical-qubit counts only, no error correction
source_refs: [KN-LIT-098, KN-LIT-099, KN-TECH-005]
added: 2026-07-24
superseded_by: null
---

## Method
Shor's discrete-logarithm algorithm (KN-LIT-098) needs only a reversible
implementation of the group law, so it applies to elliptic curves directly.
Roetteler, Naehrig, Svore and Lauter (KN-LIT-099) make this concrete: build
reversible circuits for modular addition, multiplication and inversion,
compose them into controlled point addition, classically simulate the
resulting Toffoli network, and interpolate to full Shor cost -- the point
addition is run 2n times and needs no extra qubits.

## Reported figures (logical qubits / Toffoli gates / Toffoli depth)
| Curve size | Qubits | Toffoli gates | Toffoli depth |
| --- | --- | --- | --- |
| 110-bit | 1014 | 9.44e9 | 8.66e9 |
| 160-bit | 1466 | 2.97e10 | 2.73e10 |
| 192-bit (P-192) | 1754 | 5.30e10 | 4.86e10 |
| 224-bit (P-224) | 2042 | 8.43e10 | 7.73e10 |
| 256-bit (P-256) | 2330 | 1.26e11 | 1.16e11 |
| 384-bit (P-384) | 3484 | 4.52e11 | 4.15e11 |
| 521-bit (P-521) | 4719 | 1.14e12 | 1.05e12 |

For comparison at matched classical security, factoring a 3072-bit RSA modulus
is reported at 6146 qubits and 1.86e13 Toffoli gates, so ECC is the cheaper
quantum target.

## Why the program records this
Purely as a **model boundary**. GOAL-CRYPTO-001 seeks a classical advantage
over Pollard rho; the quantum model already gives polynomial time, so a
proposal must state which model it is in or the comparison is meaningless.
Two failure modes this table is meant to prevent:

- A "quantum-inspired" classical mechanism that silently imports a quantum
  resource (superposition access, amplitude amplification, or an oracle that
  is only cheap on a quantum machine). The classical cost of emulating it must
  be charged.
- A timeline claim. P-256 at 2330 logical qubits and ~2^37 Toffoli gates looks
  small next to 2^128 classical group operations, but these are *logical*
  qubits in a fault-free model with no error-correction overhead. They are a
  lower bound on hardware requirements, not a forecast, and the corpus should
  not be cited as one.

## Applicability limits
The estimates are for elliptic curves over *prime* fields in Weierstrass form
and were simulated for the NIST curves; binary-field and other representations
are not covered. Error correction, routing, magic-state distillation, and
physical-qubit overhead are all excluded, and those factors dominate any real
device estimate. The Toffoli counts come from an interpolation of simulated
data points, not a closed-form circuit analysis.

## Verified vs reported
The table is read directly from the ePrint text of KN-LIT-099 and is that
paper's simulation output; nothing here was reproduced, so confidence is
`reported`. Note the published Springer summary quotes a different RSA-3072
Toffoli figure (1.5e14) than the ePrint table (1.86e13) -- the discrepancy is
recorded in KN-LIT-099 and is unresolved here. Shor's underlying algorithm is
`established` (KN-LIT-098); its elliptic-curve specialization is downstream
work and is not in Shor's paper. The model-boundary argument in the third
section is this program's policy, not a claim from either source.
