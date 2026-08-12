# Validation notes — TASK-20260724-230 / EXP-MLKEM-002

**Admissibility:** `accept_with_qualifications` (contract terminal: `passed`). **Blockers:** none.

Independent session. Did not produce the run package. Wrote only under this task write scope. No git commit.

## Snapshot integrity

- Receipt: `coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/archives/TASK-20260724-229/snapshot-receipt.json`
- `parent_sha` `e829ef7c26549dc3ee62796c89f16b1d1ac2500b` matches `git rev-parse 28608fb^`
- Dispatch binds `commit_sha` `28608fb8a48ffbb8291c82810f2867553d3fe6f1`; receipt field remains null
- Recomputed SHA-256 for all 39 `artifact_sha256` paths: **0 mismatches** vs working tree and vs `git show 28608fb:<path>`
- Receipt file hash `aed0e0460d61027fd01231d5026d4c3746fe73537476b99295c67b246a8fa508` matches dispatch `path_sha256`

## Artifact completeness

All specification `required_artifacts` present. Exactly four runs (`RUN-MLKEM-005`–`008`), each `completed_valid` / `validity_status: valid`, with manifest fields for command, git commit, dirty tree, environment, timing, resources (`peak_rss_bytes`), validity reason, and inference (`executor-terra` → `cursor-grok-4.5-high`, `fallback_used: true`).

## Independent re-derivations (matched)

| Metric | Reported | Recomputed | Match |
| --- | ---: | ---: | --- |
| PREFIX-AVX2 ML-KEM-1024 silent count | 32 | 32 (`1536..1567`) | yes |
| PREFIX-NEON silent counts | 384 / 544 / 784 | 384 / 544 / 784 | yes |
| Postfix AVX2/NEON silent & AVX2 disagreements | 0 | 0 | yes |
| PREFIX AVX2 ML-KEM-1024 disagreements | 32 | 32 | yes |
| Coverage fraction (all attested) | 1.0 | 1.0 | yes |
| Integration accept true/false | 43 / 21 | 43 / 21 of 64 | yes |
| Negative harness ranges | half-buffers | `[384,768)`, `[544,1088)`, `[784,1568)` | yes |
| Manifest wall sum | 0.6655… s | 0.6655488014221191 | yes |

NEON-1024 pattern: `(i % 64) >= 32` on full 64-byte blocks **plus** remainder second half `1552..1567` → 784 (matches report prose).

Reproduction: RUN-006 `unstable_silent_indices: []` and `mutation_events == 4 * ct_len` for all x86 grids. RUN-008 raw lacks those fields; `/tmp` NEON grid logs (non-archived) show the same empty-unstable / full-coverage pattern. Harness requires both seeds and both xor ops before a silent index is reportable.

## Source evidence

Annotated tags peel to the recorded commits. ASM evidence matches premise verdicts (`mlkem_cmp_avx2` / `mlkem_cmp_neon`; lines 8930 / 8942 for NEON reduction). `source-lock.yaml` file hashes match `/tmp/exp-mlkem-002/wolfssl-{5.9.1,5.9.2}`.

## Controls

| Control | Validator |
| --- | --- |
| CTRL-SOURCE-PREMISE | pass |
| CTRL-BACKEND-ATTESTATION | pass (NEON objdump absent in receipt; direct symbol + macros + self-test) |
| CTRL-VALID-KAT | pass |
| CTRL-SCALAR-CROSS-COMMIT | pass |
| CTRL-IMPLICIT-REJECTION-SHAPE | pass |
| CTRL-LENGTH-VERSUS-CONTENT | pass (vacuous empty malformed table) |
| CTRL-NEGATIVE-HARNESS | pass |

## Deviations and budget

Header `__has_include`, attest length/index, and qemu `-L` are harness repairs preserving frozen comparison semantics. Manifest wall times exclude build/repair under `/tmp` → incomplete stage accounting, still under 5400 s.

## Anomaly (43/64)

Raw `integration_checks`: 64 rows (`xor_0x01` × 32 indices × 2 seeds); 43 accept. Seed agreement: 20 both-true, 9 both-false, 3 disagree (`1539`, `1544`, `1564`). Explained in artifacts; not re-interpreted as an exploit.

## Input reconstructibility

`vectors/` absent. Replay path: committed `SEED_MATERIAL` in `comparison_probe.c` + recorded `ct_sha256_*` digests. Sufficient for this laboratory protocol.

## Commands run (validator scratch)

```bash
python3 -c '...'  # SHA-256 of all receipt paths; metric re-derivation from raw.json + coverage_maps.json
git rev-parse HEAD; git show -s --format='%H %P' 28608fb
git -C /tmp/exp-mlkem-002/wolfssl rev-parse v5.9.1-stable v5.9.1-stable^{} v5.9.2-stable v5.9.2-stable^{}
# read-only sed/rg on /tmp/exp-mlkem-002/wolfssl-5.9.{1,2} ASM files
# aarch64-linux-gnu-nm/objdump on /tmp harness NEON probe (corroboration only)
```

## Claim boundary

Admissible laboratory conformance-audit receipt for the two exact commits and attested backends only. Validation establishes admissibility, not promotion or attack claims.
