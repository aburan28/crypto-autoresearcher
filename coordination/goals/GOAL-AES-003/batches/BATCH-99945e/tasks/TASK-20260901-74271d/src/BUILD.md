# BUILD.md — TASK-20260901-74271d (BATCH-99945e hardening battery)

## Environment

- Host: arm64-apple-darwin25.6.0, 14 CPUs, 48 GiB RAM (same host class as the
  BATCH-fe0bdc producer BUILD.md).
- Python: 3.12.8 (stdlib only; no third-party imports anywhere in this task).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-batch99945e-20260901`, HEAD `3252e9cec` at
  session start; no `git add`/commit performed by this task (constraint).

## Reuse disclosure (lineage, per task card)

| file | provenance | changes |
|---|---|---|
| src/affarm046.c | BYTE-IDENTICAL copy of BATCH-fe0bdc TASK-20260901-f5d3a4 src/affarm046.c (sha256 c7d06faf...ce4a, both copies verified equal) | none |
| src/rc8probe_feistel.c | BYTE-IDENTICAL copy of BATCH-014 TASK-20260805-b95720 src/rc8probe_feistel.c (sha256 9b36c0e7...8566, both copies verified equal) | none |
| src/rbijarm046.c | derived from the producer's affarm046.c | added PI[16]/INV_PI, set_nibble_perm_sbox() (Fisher-Yates over 16 symbols + nibble byte lift), affine_over_gf2() gate, `pinbij` mode; arm-mode sbox token changed from `identity` to `nibble_perm <draw_seed>`; receipt gains sbox_draw_seed/pi_table_hex/construction fields. Round functions, geometry, worker, thread-seed and key formulas UNCHANGED. |
| src/bridge_j2.py | adapted copy of producer src/bridge.py | cell list -> J2 cells (r=3, r=7, A={0}, S={0}); seed -> "46060902a"; metadata fields. Cipher convention UNCHANGED. |
| src/census_ext.py | adapted copy of producer src/census046.py | rmax 10 -> 16; rho handling for r=11..16 (reported as data, not numerically preregistered); metadata. Geometry, matrices, convention, frozen cell set, rho recursion UNCHANGED. |
| src/keyed_r16.py | trial semantics of producer src/bridge.py | one cell (r=16, A={0}, S={0}); key expansion extended to 17 round-key blocks with the canonical xtime rcon continuation (disclosed convention extension, PREREGISTRATION.md sec. 4); seed "46060903a". |
| src/feistel_bridge.py | FRESH Python port of the BATCH-014 C oracle + worker stream semantics | expression-identical; adds per-trial identity-law logging; parity-gated against the byte-identical C copy on the same stream. |
| src/draw_bij.py | fresh | independent Python implementation of the J4 frozen-table draw (cross-check of the C pinbij table). |
| src/build_pins.py, src/analyze742.py | fresh | RUN 1 / RUN 7 orchestrators. |

KAT pins (FIPS-197 C.1 r=10 enc/dec; BATCH-003 r=5/r=10 anchors; 512-vector
roundtrips) are re-run in RUN 1 on both SPN binaries as the convention-drift
control (producer lineage).

## Build commands (RUN 1, orchestrated by src/build_pins.py)

```sh
cc -O2 -pthread -o src/rbijarm046 src/rbijarm046.c
cc -O2 -pthread -o src/affarm046 src/affarm046.c
cc -O2 -pthread -o src/rc8probe_feistel src/rc8probe_feistel.c
```

## Run commands (in order; each stamped in budget_stamps.jsonl; MAX 8 RUNS)

- RUN 1: `python3 src/build_pins.py` -> runs/build_pins.json (+ runs/draw_bij.json).
  Includes affarm046 pin 46060901, rbijarm046 pin 46060901, affarm046
  pinidentity 46060901, rbijarm046 pinbij 46064002 (FROZEN J4 table, PRE-ARM),
  draw_bij.py 46064002 cross-check. Exit != 0 => HALT.
- RUN 2 (J4): `/usr/bin/time -l src/rbijarm046 arm RBIJ-R6-A0-S0 6 1 1 30 46064001 4 8 nibble_perm 46064002`
  -> runs/J4_rbij_arm.json (stdout), runs/J4_rbij_arm.timing.txt, runs/J4_rbij_arm.err.
- RUN 3 (J3): `/usr/bin/time -l src/affarm046 arm J3-RERUN-R6-A0-S0 6 1 1 30 46063002 2 8 identity`
  -> runs/J3_affine_rerun.json (+ .timing.txt, .err).
- RUN 4 (J2): `python3 src/bridge_j2.py runs/J2_keyed_bridge.json`.
- RUN 5 (J1): `python3 src/census_ext.py runs/J1_census_ext.json` then
  `python3 src/keyed_r16.py runs/J1_keyed_r16.json` (one run slot).
- RUN 6 (GUARD): `src/rc8probe_feistel detcheck 531001` -> runs/GUARD_c_detcheck.json;
  `src/rc8probe_feistel arm GUARD-XCHK 5 1 1 9 531001 999 1` -> runs/GUARD_c_stream_xchk.json;
  `python3 src/feistel_bridge.py runs/GUARD_feistel_bridge.json runs/GUARD_c_stream_xchk.json`
  (exact-aggregate port-parity gate + identity-law read on the first 500 trials).
- RUN 7: `python3 src/analyze742.py` -> runs/decision_analysis.json.
- RUN 8: reserved for repair (unused unless a slot fails).

## Determinism

Arm receipts are deterministic functions of (name, rounds, amask, smask,
log2N, seed, arm_id, threads, sbox draw seed): per-thread splitmix64 streams
with the campaign seed formula; the J4 S-box table is a deterministic function
of the pinned draw seed 46064002 (verified C-vs-Python byte-identical in
RUN 1 and re-verified against the arm receipt in RUN 7).

## Budget

Declared wall clock 2700 s (binding stop recorded in budget_stamps.jsonl);
maximum 8 runs; memory budget 4 GiB (census matrices are 128x128 bit-integers;
arms are O(1) per trial).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL
session model); model_verified: false; fallback_used: true (session-backend
transport under inference amendment DEC-20260831-0d1eeb);
degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
