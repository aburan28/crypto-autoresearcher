# EXP-ECDLP-b9ba72 — digit-character (lambda, PGL_2-stability) profile

Run RUN-ECDLP-ee15df under TASK-20260921-b61136, specification v1
(approved DEC-20260921-33f3b6), canonical probability
normalisation, the census's primary ladder verbatim.

| row | lambda | SE | n |
|---|---|---|---|
| VT | 0.4063 | 0.0079 | 10 |
| VR | 0.5009 | 0.0015 | 10 |
| VTM | 0.5001 | 0.0001 | 10 |
| VRM | 0.5022 | 0.0004 | 10 |
| C01 | 0.5159 | 0.0054 | 10 |
| C02A | 0.5007 | 0.0003 | 10 |
| C02B | 0.5011 | 0.0005 | 10 |

## Controls

| control | result |
|---|---|
| C01_numerically_zero | PASS |
| C02A_parseval_band | PASS |
| C02_seed_agreement | PASS |
| identity_check_1e-9 | PASS |
| vhat0_equals_1_all_ok_cells | PASS |

## Verdicts

- Thue-Morse: **unstable**
- Rudin-Shapiro: **stable_flat**

## Construction closure (DEC-20260921-8e8086 open item)

- VT lambda = 0.4063; in the ffe1df band [0.36, 0.42]: True
- census R03 mode-level bridge on the same primes: 0.41852885100311116
- The Thue-Morse level set reproduces the ffe1df band; the 0.39 is attributed to the character construction.

## Reading

The census's scoped negative extends over the digit-character
family at this ladder: no character is simultaneously
PGL_2-stable and above the random-set level. The
synthetic-statistic lane narrows to the cross-ratio family
(IDEA-20260921-3ecbe8) and the non-set escape hatch
(IDEA-20260921-4af08b).

Per-cell values, wall times, RSS: dc_registry.json.

