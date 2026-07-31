# Validation notes — TASK-20260724-921 / EXP-MLKEM-004

Independent of the Executor. No official state changed. No git commit performed.

## Branch / snapshot gate

- Checked out `cursor/explore-ml-kem-cryptanalysis-a197`; `git branch --show-current` confirmed.
- `experiments/EXP-MLKEM-004/execution-report.yaml` present.
- Snapshot receipt TASK-20260724-920: 53/53 artifact SHA-256 values match the working tree and `git show c3bd8ba:<path>`.
- Dispatch binds archive commit `c3bd8bab7bcc8a99ff4986822695fe6fa9af624a` (receipt field `commit_sha` remains null).

## A — Receipt / schema / argv

Four runs (RUN-MLKEM-013..016) each have manifest, command.txt, environment.json, raw.json, summary.json, stdout.txt, stderr.txt. Every `command.txt` is exact argv:

`python3 …/run_experiment.py --only RUN-MLKEM-0XX`

No descriptive pipe notation (contrast EXP-MLKEM-003).

## B — Metric re-derivation

1. Re-ran `synthetic_control.verify_control()`: G1 silent set = `{1536..1567}`, G2 and G3 detect; matches archived `synthetic_control_report.json`.
2. From RUN-MLKEM-016 `raw.json`: `silent_count` equals `len(hit_indices_in_known_omission)` (32/32/4).
3. Sum of embedded build-timing event `wall_seconds` = 302 (= reported total).
4. Seed-1 ciphertext SHA-256 values match archived vectors.

## C — Synthetic control & marginal honesty

Construction in `synthetic_control.py` returns equal for single-byte diffs confined to R and unequal for multi-byte / alignment patterns in R. That is truly G1-silent and G2/G3-visible.

`class_marginal_information` attributes only `synthetic_G2_pattern_detected` / `synthetic_G3_pattern_detected`. Library G2/G3-minus-G1 arrays (including positive-control rediscovery) are empty. Known wolfSSL rediscovery does **not** set marginal information.

## D — Second implementation / precedence

Attempts recorded for BoringSSL, PQClean (avx2 + aarch64), mlkem-native, aws-lc — all rejected under the fixed-bound hand-written vector-tail criterion (length-parameterized verify). `second_impl_unavailable` is correct and is **not** an isolation claim. With synthetic control adequate and no new silent/accept, precedence correctly lands on `second_impl_unavailable` rather than `isolated_to_audited_commits` or `generator_hardening_insufficient`.

## E — Build accounting / anchor

- Exact argv: pass.
- Build wall: pre-run receipt content embedded in RUN-013 raw (302 s); some events reconstructed (disclosed). Standalone file lives under `/tmp` (qualification).
- Anchor graded **weak** with honest `file_actually_validated_against`; unused NIST downloads did not upgrade the grade.

## F — KN-TECH-030 repair evidenced?

**Yes.** Artifacts plant and demonstrate a baseline-invisible synthetic positive control, redefine marginal information to exclude wolfSSL rediscovery, and thereby make the honesty class fire only when the synthetic control is missed. Relative to EXP-MLKEM-003 (empty G2/G3-minus-G1 on the known defect; isolation claim under an unreachable honesty gate), the repair is present and exercised. Terminal outcome is blocked by second-impl unavailability, not by generator-hardening failure.

## Qualifications (do not invalidate package)

| ID | Issue |
|----|--------|
| Q-EXEC-REPORT-WALL-SECONDS-PLACEHOLDER | execution-report lists 5400 s/run; manifests show ~12.6 s total |
| Q-MANIFEST-GIT-COMMIT-MISBIND-013-015 | RUN-013..015 cite unrelated `ef345b5` (P13 snapshot); package bound by `c3bd8ba` / parent `6ffc7dc` |
| Q-SNAPSHOT-RECEIPT-COMMIT-SHA-NULL | receipt `commit_sha` null; dispatch binds `c3bd8ba` |
| Q-BUILD-RECEIPT-TMP-PRIMARY | primary path `/tmp/...`; content archived in RUN-013 raw |
| Q-ANCHOR-WEAK-HONEST | informational honesty note |

## Verdict summary

| Question | Answer |
|----------|--------|
| Overall | **accept_with_qualifications** |
| KN-TECH-030 repair evidenced? | **Yes** |
| `second_impl_unavailable` correct? | **Yes** |
| Failed controls | **None** |
| Failed artifacts | **None** (qualifications only) |
