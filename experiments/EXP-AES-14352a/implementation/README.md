# EXP-AES-14352a Stage 1 — program-local P_RD ∧ F_fp

**Claim ceiling:** toy / reduced-round AES-128 on the pinned FIPS-197 harness only.
**Not claimed:** published ACC/ACP margins (RQ-AES-003 R3); Stage 2 CM-3; full-round AES.

## Harness pin

- Module: `coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/aes_reduced.py`
- Expected MODULE_SHA256: `2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447`
- Convention: `AES(key, rounds=r, final_mix_columns=False)` (C1–C3)

## Byte numbering

AES state bytes **column-major 0..15** (Shin POINTER / AES literature).

### Diagonals D

| Id | Bytes |
|----|-------|
| D0 | {0, 5, 10, 15} |
| D1 | {1, 6, 11, 12} |
| D2 | {2, 7, 8, 13} |
| D3 | {3, 4, 9, 14} |

### Inverse diagonals ID

| Id | Bytes |
|----|-------|
| ID0 | {3, 6, 9, 12} |
| ID1 | {2, 5, 8, 15} |
| ID2 | {1, 4, 11, 14} |
| ID3 | {0, 7, 10, 13} |

## P_RD (program-local related-differential / zero-difference)

1. Structure: plaintexts vary only on **D0**; inactive diagonal bytes fixed per key.
2. Sample a base pair `(P1, P2)` with `P1 ≠ P2` on D0.
3. Encrypt both at `r` rounds → `(C1, C2)`.
4. Build related ciphertexts by **exchanging** values on one chosen inverse-diagonal `IDj` between C1 and C2 → `(C3, C4)`; decrypt → `(P3, P4)`.
5. **P_RD ACCEPT** iff `P3 ⊕ P4` is inactive on at least one full diagonal `Dk` (all 4 bytes zero). Record which diagonals.

## F_fp (program-local Shin-style friend-pair filter)

1. Friend of `(P1, P2)`: **same D0 bytes**, different constants on inactive diagonals (D1∪D2∪D3).
2. For each friend, repeat the same inverse-diagonal exchange and check the same inactive-diagonal predicate for every `IDj` in the declared subset.
3. **F_fp ACCEPT** iff **all** `B` friend certificates succeed (joint friend suppression). Budget exhausted / any friend fails → F_fp fail.
4. **Misaligned sibling:** use `IDj` rotated by `+1 mod 4` relative to the pair’s declared table; predicted null excess.

**Joint ACCEPT = P_RD AND F_fp.**

## Frozen Stage-1 pilot budget (THIS attempt)

Declared cheap pilot so all 16 seeds and all control arms finish in-session.
Program-local scale; **toy tier**. Exact numbers are hash-committed in `frozen_query_schedule.json`.

| Parameter | Value |
|-----------|-------|
| `structure_size` | 256 (enumerate free byte = state[0] ∈ D0; other D0 bytes fixed per key) |
| `n_pairs_per_key` | 32 (sampled without replacement from C(256,2)) |
| `friend_bound_B` | 4 |
| `idj_subset` | [0, 1] (ID0, ID1) — not all four |
| `seeds` | 2026091001 .. 2026091016 |
| `rounds_primary` | 5 |
| `rounds_null` | 10 |
| `rounds_graded` | [4, 5, 6] spot |

A pair is counted **ACCEPT for P_RD** if any `IDj` in the subset yields P_RD ACCEPT.
A pair is counted **ACCEPT for joint** if there exists an `IDj` in the subset such that P_RD ACCEPT holds for the base pair **and** F_fp ACCEPT holds for that same `IDj` over all B friends.

## Ordering

1. FIPS-197 pin receipt
2. Freeze + sha256-commit query schedule
3. Controls (null / ablation / sibling / graded) → `controls_receipt.json`
4. Only then AES r=5 primary joint rates

## Entrypoint

```bash
python3 experiments/EXP-AES-14352a/implementation/run_stage1.py \
  --run-id RUN-AES-a36d0b \
  --out-dir experiments/EXP-AES-14352a/runs/RUN-AES-a36d0b
```

Prior attempt `RUN-AES-0739d9` retained (immutable); `RUN-AES-a36d0b` is the Stage-1 package with corrected zero-event HEUR labeling.