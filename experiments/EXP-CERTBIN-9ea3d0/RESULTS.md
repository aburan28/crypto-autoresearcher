# RESULTS EXP-CERTBIN-9ea3d0

Label (n=19): **O-MIXED**

Reason: n=19 ratios not uniformly in the birthday band and not uniformly at r^{0.05}

n=17 nearby kernel_ok=True; r_is_prime=False; not pooled with n=19.

No ECDLP solve. No exponent claim. No AUXIN. NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED.

Executor observations only. No hypothesis-status, experiment-status, or goal-status edit. The n=19 label above is the sole observation label in this file.

## Frozen prediction reference (Stage 0, not adjusted)

- File: `experiments/EXP-CERTBIN-9ea3d0/stage0/preregistered-predictions.json`
- SHA-256 (frozen before Stage 1 and unchanged after Stages 1–2): `88dc63059d55c0ba75f8d8930b34688fa33a8777c07bb68a0013d9c3df7956b0`
- Quantity: informative_colliding_pairs / (C_eff(C_eff-1)/(2 r))
- Formula (frozen): ratio in [1/2, 2] at n=19 for every frozen seed and k in {2,3}
- Measured Stage-0 freeze: n=19 order 523492, r=130873 (prime), C_eff=1145, birthday_expectation=5.004393572394611, r^{0.05}=1.8023639941375367
- Kernel checks on G and 3G: both identity to O (measured)
- Certificate kind: none (collision-count measurement; no discrete-log solve claimed)

## Stage 1 comparison statistics (measured, n=19, not pooled with n=17)

Z/rZ control (seed 2026100303): colliding_pairs=8, ratio=1.5985952911717105 (in [1/2, 2]), heaviest_fiber=2 (tail max 4).

| seed_name | k | informative_colliding_pairs | raw | kernel_pairs | ratio | heaviest_fiber | B_phys |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary | 2 | 20 | 20 | 0 | 3.996488227929276 | 3 | 76 |
| primary | 3 | 22 | 22 | 0 | 4.396137050722204 | 3 | 114 |
| holdout | 2 | 18 | 18 | 0 | 3.5968394051363486 | 3 | 76 |
| holdout | 3 | 7 | 7 | 0 | 1.3987708797752467 | 2 | 114 |

Tail check (measured): all n=19 heaviest_fiber ≤ 4 and Z/rZ heaviest_fiber ≤ 4: pass.
in_band (every n=19 ratio in [1/2, 2]): false.
uniform r^{0.05} reading: false.

## Stage 2 nearby object (measured, n=17, not pooled)

- order=130972, odd_part=32743, r_work=130972, r_is_prime=False
- kernel_ok=True
- C_eff_n17=1145, birthday_expectation_n17=5.00061081757933 (denominator = order, because r is not prime)
- k=2 informative_colliding_pairs=47, ratio=9.398851803218616, heaviest_fiber=3
- k=3 informative_colliding_pairs=28, ratio=5.5993159678749205, heaviest_fiber=3
- `pooled_with_n19`: false

n=17 rows are not used in the n=19 label.

## Runs and checks

| stage | RUN id | check.py | wrapper wall_seconds (measured) | peak RSS (measured) |
| --- | --- | --- | --- | --- |
| 0 | RUN-CERTBIN-a8c7f1 | exit 0 pass | 0.190293550491333 (payload wall_seconds) | not separately wrapped |
| 1 | RUN-CERTBIN-a008c1 | exit 0 pass | 1.3674476146697998 | 128794624 bytes |
| 2 | RUN-CERTBIN-6319c2 | exit 0 pass | 0.47020840644836426 | 124784640 bytes |

Implementation: numpy 2.4.6 Field/TableField path. Magma/Sage/AUXIN/Bedrock not used.

## Protocol notes (not evidence against the heuristic)

- Stage 1/2 `run.py` re-invokes Stage 0 and rewrites `stage0/cell-n19.json` wall_seconds. Executor restored the Stage-0 freeze copy. `preregistered-predictions.json` hash was unchanged.
- No dedicated `dispatch_queue.json` listed TASK-20261003-81ebdd; claim was not written into a foreign GOAL-ECDLP2M-001 batch claims directory.
- Amazon Bedrock: NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED.

## Artifact paths

- `experiments/EXP-CERTBIN-9ea3d0/stage0/preregistered-predictions.json`
- `experiments/EXP-CERTBIN-9ea3d0/stage0/cell-n19.json`
- `experiments/EXP-CERTBIN-9ea3d0/stage1/n19-census.json`
- `experiments/EXP-CERTBIN-9ea3d0/stage2/n17-nearby.json`
- `experiments/EXP-CERTBIN-9ea3d0/RESULTS.md`
- `experiments/EXP-CERTBIN-9ea3d0/runs/RUN-CERTBIN-a8c7f1/`
- `experiments/EXP-CERTBIN-9ea3d0/runs/RUN-CERTBIN-a008c1/`
- `experiments/EXP-CERTBIN-9ea3d0/runs/RUN-CERTBIN-6319c2/`
