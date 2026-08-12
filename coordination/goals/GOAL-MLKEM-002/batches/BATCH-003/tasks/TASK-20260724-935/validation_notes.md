# Validation notes — TASK-20260724-935 / EXP-MLKEM-006

Independent of the Executor. No official state changed. No git commit performed.

Inference: `requested_policy=review-xhigh` (alias `review-adversarial`); `resolved_model=cursor-grok-4.5-high-fast`; `fallback_used=true`; `independent_session=true`.

## Branch / snapshot gate

- Checked out `cursor/explore-ml-kem-cryptanalysis-a197`; `git branch --show-current` confirmed.
- Snapshot receipt TASK-20260724-934: **92/92** artifact SHA-256 values match the working tree and `git show 658f9e53:<path>`.
- Receipt `parent_sha` `40939c22b544bd850fd266eecca18ba7d848d600` equals `git rev-parse 658f9e53^`.
- Archive commit and parent are both ancestors of HEAD (`6e1856da4c7830f92325075c09bfbdcb6ab02b73`).
- Dispatch binds archive commit `658f9e530ac27ab56092501138ce53409c8efb28` (receipt field `commit_sha` remains null). Receipt file hash `b0651a7440cb48050d21f04247cb850d2207ec4f1e18e62bcc749840704e209d` matches dispatch post-commit record.
- **Hash mismatches: none.**

## A — Receipt / schema / argv

Four terminal runs (RUN-MLKEM-021..024) each have manifest, command.txt, environment.json, raw.json, summary.json, stdout.txt, stderr.txt. Every `command.txt` is exact argv matching the manifest `run.command` field:

`python3 …/run_experiment.py --only RUN-MLKEM-0XX`

No descriptive pipe notation. Terminal manifests record `resolved_model: cursor-grok-4.5-high-fast` with `fallback_used: true`.

## B — Metric re-derivation

1. From archived wrap-attest: `library_call_path_exercised` re-derived as `(sum(wrap_call_counts)>0) ∧ wrap_linked` → true; `attested` formula matches archived true; method=`call_site_wrapper_INTERPOSE_COMPARE`.
2. G1 silent set = `{1536..1567}`; G2/G3 marginals non-empty (32 / 28 indices); `scoring_uses_diff_count_branch=false`; `so_local_dlopen_load_bearing=false`.
3. RUN-022 positive-control silent counts 32/32/4; `new_silent_index_candidates=[]`; negative harness detected on 512/768/1024.
4. Postfix wolfSSL and PQClean G1 silent counts are 0; PREFIX-NEON silents are the known defect class.
5. Build-timing event sum = 531 (= reported total). Seed-1 CT SHA-256 matches vectors and archive_key0.
6. All 456 malformed-length rows have `counted_as_comparison_omission: false`.
7. Measured run wall sum matches manifests (≈11.45 s).
8. Attempt1 archived `no_wrapped_conformance_probe_built` / `pass=false` — SO-local path rejected.

## C — True library-path interposition (OBJ-RT005-001 repair)

Load-bearing path is `conformance-wrap-*` built with `-DINTERPOSE_COMPARE` + `compare_wrap.o`. Probe `library_cmp` routes to `mlkem_interposed_defective_compare`; wrap-attest derives `library_call_path_exercised` from wrap call counts, not a hard-coded true. Python `verify_control` requires `attested` and exercised path before `pass`. Terminal report sets `so_local_dlopen_load_bearing=false`. `adequacy_probe.c` dlopen residue is not load-bearing.

## D — Second peer / criterion_used / precedence

Strict fixed-bound neighborhood re-checked empty; `goal_criterion_2_disposition=second_impl_unavailable`; optional PQClean pin under `criterion_used=widened_optimized_compare` is laboratory continuity only — not H-MLKEM-004 / GOAL criterion 2.

Under frozen precedence the terminal class is **`second_impl_unavailable`** (fires before `isolated_to_audited_commits`).

## E — Build accounting / anchor

- Exact argv: pass.
- Build wall: pre-run receipt embedded in RUN-021 raw (531 s).
- Anchor graded **weak** with honest `file_actually_validated_against`; unused NIST downloads did not upgrade the grade.

## Qualifications (do not invalidate package)

| ID | Issue |
|----|--------|
| Q-SNAPSHOT-RECEIPT-COMMIT-SHA-NULL | receipt `commit_sha` null; dispatch binds `658f9e53` |
| Q-DIRTY-TREE-AT-EXECUTION | manifests/report disclose dirty_tree true at measurement |
| Q-BUILD-RECEIPT-TMP-PRIMARY | primary build/wrap/mechanism paths under `/tmp`; content archived |
| Q-STALE-IMPLEMENTATION-MD-DLOPEN-LANGUAGE | implementation.md still says dlopen; load-bearing path is wrap |
| Q-WRAP-CALL-COUNTER-ALIASED | three wrap counters alias one atomic |
| Q-CALL-SITE-WRAPPER-NOT-LD-WRAP | equivalent call-site wrapper, not ld `--wrap` |
| Q-SCORE-FROM-GRID-LIBRARY-CALL-PATH-FIELD | non-exercised `library_call_path` preset true; exercised field derived |
| Q-ANCHOR-WEAK-HONEST | informational honesty note |
| Q-AVX2-DOCKER-ON-ARM64 | AVX2 measured under docker amd64 on arm64 host |
| Q-OUTCOME-IS-SECOND-IMPL-NOT-ISOLATION | terminal class is not isolation |

## Verdict summary

| Question | Answer |
|----------|--------|
| Overall | **accept_with_qualifications** (terminal contract: **passed**) |
| Hash match | **92 / 92** (0 mismatch, 0 missing) |
| Outcome `second_impl_unavailable` supported? | **Yes** |
| True-path wrap attestation / not SO-local? | **Yes** |
| `library_call_path_exercised` from attestation? | **Yes** |
| Failed controls | **None** |
| Failed artifacts | **None** (qualifications only) |
