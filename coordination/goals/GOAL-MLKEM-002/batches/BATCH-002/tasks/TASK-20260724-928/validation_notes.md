# Validation notes — TASK-20260724-928 / EXP-MLKEM-005

Independent of the Executor. No official state changed. No git commit performed.

## Branch / snapshot gate

- Checked out `cursor/explore-ml-kem-cryptanalysis-a197`; `git branch --show-current` confirmed.
- Snapshot receipt TASK-20260724-927: **76/76** artifact SHA-256 values match the working tree and `git show 63e7467:<path>`.
- Receipt `parent_sha` `655420934c21377712d1992d6759013becbdf350` equals `git rev-parse 63e7467^`.
- Archive commit and parent are both ancestors of HEAD (`214c0cfa4324a9a734dd0e66b791db019955bc2c`).
- Dispatch binds archive commit `63e7467f96b6c1b52f7a8ce25399a875e19ba52f` (receipt field `commit_sha` remains null). Receipt file hash matches dispatch post-commit record.

## A — Receipt / schema / argv

Four runs (RUN-MLKEM-017..020) each have manifest, command.txt, environment.json, raw.json, summary.json, stdout.txt, stderr.txt. Every `command.txt` is exact four-token argv matching the manifest `command` field:

`python3 …/run_experiment.py --only RUN-MLKEM-0XX`

No descriptive pipe notation. Terminal manifests record `resolved_model: cursor-grok-4.5-high-fast` with `fallback_used: true`.

## B — Metric re-derivation

1. Rescored library-facing adequacy from archived G1 silent flags + G2/G3 observations via `score_from_observations()`: G1 silent set = `{1536..1567}`, 8+8 marginal findings, `pass=true`, matches archived report; `scoring_uses_diff_count_branch=false`.
2. From RUN-MLKEM-018 `raw.json`: positive-control `silent_count` equals `len(hit_indices_in_known_omission)` (32/32/4).
3. Sum of embedded build-timing event `wall_seconds` = 830 (= reported total).
4. Seed-1 ciphertext SHA-256 values match archived vectors and appear in RUN-017 raw.
5. All 456 malformed-length rows have `counted_as_comparison_omission: false`.
6. Measured run wall sum in execution-report equals sum of manifest walls (≈782.08 s).

## C — Library-facing adequacy (DEC-015 repair)

Construction uses a dlopen-injected defective comparator (`defective_compare.c` / `adequacy_probe.c`). Scoring path uses compare_rc + G1 silent-set membership only; no `len(diffs)==1` branch in generator or scorer. Marginal information attributes only adequacy G2/G3 detections; library rediscovery arrays are empty.

## D — Second peer / criterion_used / precedence

Strict fixed-bound neighborhood empty (EV-MLKEM-007); `criterion_used=widened_optimized_compare`; PQClean `202a8f96…` avx2 pinned and measured (`BUILD-PQCLEAN` in RUN-018 grids and RUN-019 malformed table). Postfix wolfSSL and PQClean silent counts are zero. PREFIX-NEON silents are disclosed as the known NEON defect class and do not populate `new_silent_index_candidates`.

Under frozen precedence the terminal class is **`isolated_to_audited_commits`**, scoped to the widened criterion — not a strict fixed-bound-tail isolation claim.

## E — Build accounting / anchor

- Exact argv: pass.
- Build wall: pre-run receipt embedded in RUN-017 raw (830 s).
- Anchor graded **weak** with honest `file_actually_validated_against`; unused NIST downloads did not upgrade the grade.

## Qualifications (do not invalidate package)

| ID | Issue |
|----|--------|
| Q-SNAPSHOT-RECEIPT-COMMIT-SHA-NULL | receipt `commit_sha` null; dispatch binds `63e7467` |
| Q-EXECUTOR-RESOLVED-MODEL-TYPO-FAILED-ATTEMPTS | failed-attempt manifests use `cursor-grok-4.5-high-fast-fast`; terminal runs correct |
| Q-DIRTY-TREE-AT-EXECUTION | manifests/report disclose dirty_tree true at measurement |
| Q-BUILD-RECEIPT-TMP-PRIMARY | primary build/mechanism paths under `/tmp`; content archived in RUN-017 / selection md |
| Q-ANCHOR-WEAK-HONEST | informational honesty note |
| Q-AVX2-DOCKER-ON-ARM64 | AVX2 measured under docker amd64 on arm64 host |
| Q-ISOLATION-SCOPED-TO-WIDENED-CRITERION | isolation claim bound to widened_optimized_compare |

## Verdict summary

| Question | Answer |
|----------|--------|
| Overall | **accept_with_qualifications** (terminal contract: **passed**) |
| Hash match | **76 / 76** (0 mismatch, 0 missing) |
| Outcome `isolated_to_audited_commits` supported? | **Yes** (scoped to `widened_optimized_compare`) |
| Library-facing adequacy / no `len(diffs)==1`? | **Yes** |
| Failed controls | **None** |
| Failed artifacts | **None** (qualifications only) |
