# Implementation note — EXP-BINSTD-a8efe2 / TASK-20261001-f5e965

Observations only. No hypothesis-status change. No AUXIN. No Bedrock.
No f37254 phi-transport. No cdca3a Hamming-weight protocol.

## What was implemented

| path | role |
|---|---|
| `implementation/gf2n.py` | F_{2^9} schoolbook field; dual moduli |
| `implementation/encoder.py` | Semaev S_3 CNF-XOR encoder; clause-width / subst counts; relabel GL(l) |
| `implementation/runpack.py` | Immutable run packages |
| `implementation/stage0_run.py` | Dual-modulus + predictions + census + reverify checklist |
| `implementation/stage1_run.py` | Structural fixture + certificate equality (l∈{3,4}) |
| `implementation/stage2a_run.py` | Encoder clause-width / subst summaries (l∈{6,7,8}) |
| `implementation/stage3_run.py` | Unmatched vs width-matched discriminator (fixture scale) |
| `implementation/stage2b_probe.py` | WDSat/CNF-XOR probe → instrument_unavailable |

## Protocol deviations / observations

1. **Stage 0 predictions committed before Stage 1 encode** (required). Artifacts under `stage0/`.
2. **Cross-arm solution-tuple multiset identity** is not claimed: that requires
   field-isomorphism transport owned by IDEA-20260922-f37254 (excluded).
   `certificate_set_equality` = per-arm encoder ↔ algebraic-oracle multiset
   equality, brute-forced over \(2^{ml}\) assignments. All Stage-1 cells passed.
3. **Normal basis**: constructible (element found); not folded into
   pentanomial/trinomial ratios; full structure-constant encoder not expanded
   (`skipped` encoding with reason — not invalidation).
4. **Stage 3 unmatched N_leaf**: invertible per-block \(F_2\)-linear
   relabelling **preserves** algebraic solution-count (bijection on \(V_l^3\)).
   Unmatched therefore showed **no** large algebraic N_leaf effect at fixture
   scale. Width-matched stayed in [0.9,1.1]. Outcome recorded as
   `discriminator_null_on_N_leaf_axis` — complete measurement; 7ef636-style
   ORDER/conflict effect is a different observable (needs Stage 2b SAT).
   Not framed as H1 falsification.
5. **Stage 2b**: WDSat/CNF-XOR absent → `instrument_unavailable.yaml`
   (infrastructure). Explicitly not H1 falsification.
6. **Measured vs modeled**: naive 5/3 term-count ratio always in a separate
   MODELED column; never mixed into measured ratios.

## Runs

| run_id | stage | status / termination |
|---|---|---|
| `RUN-BINSTD-54aa8c` | 0 | `completed_valid` / completed |
| `RUN-BINSTD-ffab44` | 1 | `completed_valid` / completed |
| `RUN-BINSTD-53d976` | 2a | `completed_valid` / completed |
| `RUN-BINSTD-7979df` | 3 | `completed_valid` / completed |
| `RUN-BINSTD-ad5e6f` | 2b | `failed_infrastructure` / instrument_unavailable |

## certificate.kind

All manifests use `none` (pure measurement / infrastructure). Vocabulary
restricted to `discrete_log|decomposition|key_recovery|none`.
