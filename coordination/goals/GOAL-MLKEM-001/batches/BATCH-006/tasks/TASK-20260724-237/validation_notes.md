# Validation notes — TASK-20260724-237 / VAL-20260724-237

Independent validation of the Coordinator-committed EXP-MLKEM-003 snapshot
(`TASK-20260724-236`, dispatch-bound commit `e487652`). No experiment or
ledger artifacts were modified.

## Overall verdict

**accept_with_qualifications** (terminal contract: passed / admissible with
documented qualifications).

Isolation claim `isolated_to_audited_commits` is **supported by the raw
artifacts** for the isolation premise (known defect retained; nothing new on
postfix or liboqs). See Q-OUTCOME-PRECEDENCE-TENSION for class-uniqueness.

## Integrity (A)

- All specification `required_artifacts` present.
- All 50 `artifact_sha256` values in the snapshot receipt recomputed and
  matched the working tree and `git show e487652:<path>`.
- Parent `7bb0502` and archive commit `e487652` reachable from `HEAD`.
- Four run directories each have the seven required files; manifests carry
  commit, dirty_tree, env, seeds, timestamps, resources, validity, and
  inference (`executor-terra` → `cursor-grok-4.5-high`, `fallback_used: true`).
- **Failed artifact checks:** `command.txt` for RUN-MLKEM-009/010/011
  (descriptive, not exact). RUN-012 command passes.

## Independent recomputation (B)

From `RUN-MLKEM-010/raw.json` `BUILD-PREFIX-AVX2` / `ML-KEM-1024`:

| Class | silent ∩ {1536..1567} | matches report |
|-------|----------------------:|:--------------:|
| G1    | 32 (full set)         | yes            |
| G2    | 32 (full set)         | yes            |
| G3    | 4: 1536,1551,1552,1567| yes            |

`G2−G1 = []`, `G3−G1 = []`. Matches RUN-012 / execution report. No numeric
discrepancy. EXP-MLKEM-002 coverage map silent set identical. Vector file
SHA-256 matches `archive_key0` digests.

## Coordinator concerns C1–C6

| ID | Finding |
|----|---------|
| **C1** | Builds happened **outside** recorded runs. Six wolfSSL build dirs are symlinks to `/tmp/exp-mlkem-002/builds/`; `liboqs.a` mtime ~19:55 vs RUN-009 start 20:05:23. RUN-009 (~3.5 s) only recompiled probes + attest/anchor. Measurement grids are faithful; library-build wall clock is not. |
| **C2** | Commands for 009–011 are **descriptive summaries**, not exact argv. Not reproducible from `command.txt` alone; use `run_experiment.py`. |
| **C3** | Empty `G2_minus_G1` / `G3_minus_G1` and null anomalies are **genuine empty results**, confirmed by set difference on raw silent sets. |
| **C4** | NIST ACVP URLs retrieved (HTTP 200) and attempts recorded, but **validation used liboqs in-tree** `internalProjection.json` (9/9 and 1/1 pass). Grade `strong` is ACVP-projection-qualified, not NIST-download-applied. |
| **C5** | liboqs G4 `refused_by_harness_exact_length_api` is an **honest limitation / coverage gap**, not a library reject sold as a result. Separated from silent sets. |
| **C6** | NEON **was** run under qemu with **decap-boundary** rows (PREFIX 6931, POSTFIX 83). No primitive-only NEON verdict. NEON G4 rows absent. |

## Controls

All seven controls: **pass** (STRONG-ANCHOR and BACKEND-ATTESTATION with
qualifications above). No control **fail** or **invalid**.

## Protocol gates (D)

- No conformance verdict on primitive-only evidence: **pass**.
- Malformed-length never in silent/disagreement counts: **pass**.
- Reportable findings reproduce across ≥2 keys: **pass** (silent_votes min ≥8 on positive-control indices; decap accepts multi-seed).
- Negative harness before library conclusions: **pass**.
- Stage wall budgets respected; mutation cap reinterpreted per-class
  (undeclared deviation; does not relax an invalidation rule).
- Three declared deviations honestly scoped; plus undeclared cap note.

## Objection closure (E)

| Objection | Verdict |
|-----------|---------|
| OBJ-001 | **answered** |
| OBJ-002 | **partially answered** |
| OBJ-003 | **answered** |
| OBJ-004 | **answered** |
| OBJ-005 | **partially answered** |

## Failed checks summary

- Artifact fail: RUN-MLKEM-009/010/011 `command.txt` (exact-command bar).
- No control fail.
- No hash mismatch.
- No fabricated positive-control or isolation numbers detected.
