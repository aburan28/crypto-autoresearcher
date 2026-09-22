# EXP-ECDLP-ff8f9e — partition (lambda, PGL_2-stability) profile

Run RUN-ECDLP-3e2225, specification v1 (approved DEC-20260921-49e0f1),
canonical probability normalisation per level, the census's
primary ladder. Observable: the t != 0 level-character combined
norm ||g||_{1,*} (ffe1df's battery object, f68c7f's A(v) input).

| row | lambda | SE | n | verdict |
|---|---|---|---|---|
| POP2 | 0.4063 | 0.0079 | 10 | unresolved_battery_not_measured |
| POP4 | 0.4057 | 0.0079 | 10 | unresolved_battery_not_measured |
| POP16 | 0.2546 | 0.0613 | 10 | stable_below_random |
| POP64 | 0.9995 | 0.0010 | 10 | unresolved_battery_not_measured |
| RES4 | 0.0736 | 0.0022 | 10 | unstable |
| RES16 | 0.0736 | 0.0022 | 10 | unresolved_battery_not_measured |
| POP16M | 0.3421 | 0.0509 | 10 | - |
| RES4M | 0.4972 | 0.0027 | 10 | - |
| C02P16 | 0.4994 | 0.0002 | 10 | - |
| C02P16B | 0.4992 | 0.0002 | 10 | - |

## Controls

| control | result |
|---|---|
| C01_numerically_zero | PASS |
| C02P16_parseval_band | PASS |
| C02P16_seed_agreement_top8 | PASS |
| POP2_bridge_reproduces_VT | PASS |
| vhat0_all_levels | PASS |

## 0.39-reproduction

- POP16 (t-combined norm) lambda = 0.2546; in band [0.36, 0.42]: False
- VT (character construction, cited from RUN-ECDLP-ee15df): 0.4063
- The partition construction does NOT reproduce the band; the 0.39 is carried by the character construction alone (VT 0.4063, in-band).

## POP64 unbalanced-level observation (rule 8)

POP64 reads lambda = 0.9995 +- 0.001 -- far above the partition
Parseval level -- but this is the UNBALANCED-LEVEL artifact, not
structure: popcount mod 64 has only ~25 nonempty levels with
wildly unequal sizes (binomial popcount distribution), and the
probability normalisation gives a TINY level's indicator Fourier
mass ~ p/|A|^{1/2}, so the combined norm is dominated by the
smallest levels and grows like p^1 for ANY unbalanced partition.
A balanced-partition variant (equal-size levels) is the named
follow-up if the lane ever needs M >= 32 popcount partitions;
the verdict vocabulary correctly refuses to call this structure
(no battery reading; unresolved_battery_not_measured).

## Reading

The census's scoped negative extends from sets to PARTITIONS
-- the object class the lane's constructions actually key
on: every natural partition's t-combined norm is either
Moebius-unstable or at the partition Parseval level at this
ladder. Together with the closed set lane (census, digit
characters, cross-ratio coordinates), the synthetic lane's
remaining direction is the non-set escape hatch
(IDEA-20260921-4af08b: the stability-signal tradeoff as a
theorem, with the escape hatch stated).

Per-cell norms, argmax t, wall times, RSS: part_registry.json.

