# EXP-ECDLP-fac9ea v4 extension — R07 index-5 coset level decision

Run RUN-ECDLP-ccf8f0 under TASK-20260921-a5e995, amendment DEC-20260921-a796fe
(the named successor of DEC-20260921-4516a0). Decision quantity is
delta = lambda(R07) - lambda(C02A) on the same ladder — convention-free
under any uniform transform prefactor. The absolute gate thresholds
(1/4, 1/6) are deliberately NOT applied (convention-relative).

Ladder (p = 1 mod 5, 11 primes): [4111, 9421, 21661, 49681, 114161, 262151, 602311, 1383691, 3178691, 7302731, 16777291]

| row | lambda | SE | n |
|---|---|---|---|
| R07 | 0.5091 | 0.0053 | 11 |
| R07M | 0.5081 | 0.0062 | 11 |
| C02A | 0.4997 | 0.0005 | 11 |
| C02B | 0.5002 | 0.0002 | 11 |

## Controls

| control | result |
|---|---|
| C01_numerically_zero | PASS |
| C02A_parseval_band | PASS |
| C02_seed_agreement | PASS |
| R07M_moebius_stability | PASS |
| all_ok_cells_vhat0_equals_1 | PASS |

## Decision

delta = lambda(R07) - lambda(C02A) = 0.0094 +- 0.0053 (0.0107 at 2SE).
VERDICT: at_random_level.

The R07 excess of the census (0.5709 on 4 points) does NOT survive
the congruence-complete ladder: the index-5 coset sits at the
random-set level like every other stable row, and the census's
scoped negative closes over the full registry — no natural
coordinate statistic is simultaneously PGL_2-stable and above the
random-set level. Synthetic-statistic design remains the named
successor.

Per-cell raw values and wall times: r07_registry.json;
manifest: manifest.yaml.

