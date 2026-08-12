# Falsification review — TASK-20260724-929 / EXP-MLKEM-005

Independent Red Team session. No official state changed. Experiment artifacts untouched. No git commit.

Machine-readable verdict: `red_team_report.yaml` (`RT-20260724-004`)

Branch gate: `cursor/explore-ml-kem-cryptanalysis-a197`; `experiments/EXP-MLKEM-005/execution-report.yaml` present. Snapshot basis: Coordinator-verified `63e7467f96b6c1b52f7a8ce25399a875e19ba52f` (TASK-20260724-927).

Inference: `requested_policy=review-xhigh`; `resolved_model=cursor-grok-4.5-high-fast`; `fallback_used=true`; `independent_session=true`.

## Verdict on outcome classification

**Disposition: `revised`.**

Under the frozen EXP-MLKEM-005 precedence text, **`isolated_to_audited_commits` is the correct class** and does not flip to `generator_hardening_insufficient`, `synthetic_control_inadequate`, `second_impl_unavailable`, or `systemic_incomplete_comparison`.

**Isolation claim survival under `criterion_used=widened_optimized_compare` only: revised yes.** It survives as a laboratory null on the measured wolfSSL post-fix backends and pinned PQClean avx2 verify peer under that widened criterion. It does **not** survive as strict fixed-bound-tail isolation, as audited-library G2/G3 instrument-power proof, or as crypto-scale / MLWE evidence.

## Attack lines

| Line | Result | One-line hold |
|------|--------|---------------|
| 1 Relocated adequacy tautology | **Landed — most damaging** | Injected SO is still single-byte-silent / multi-byte-unequal by construction; path is `adequacy_probe` dlopen, not wolfSSL/PQClean; library excluding-known-defect marginals empty |
| 2 Empty-neighborhood widening abuse | **Landed with scope** | Measuring W1 PQClean is authorized; keeping the strong isolation class name after criterion downgrade answers a weaker question |
| 3 Widened→strict scope inflation | **Landed as scope** | Package mostly discloses `criterion_used`; bare class label still invites paraphrase as H-MLKEM-004-style isolation |
| 4 Post-fix/peer null underpowered | **Landed** | Primitive zeros real and scoped; API still `G2G3_spot`; coverage report omits NEON; PQClean packaged as 1024-only |
| 5 Discriminating-power flag | **Landed** | Flag true from adequacy object only while library marginals empty |
| 6 Weak anchor / docker AVX2 | **Defeated as flip** | Qualifies reference/environment only |
| 7 Crypto-scale / MLWE | **Defeated** | No such claim in package; standing prohibition |
| 8 Licensing under widened criterion | **Landed as scope** | Class licenses widened laboratory isolation only |

## DEC-015 repairs — answered or restated?

**Second peer (DEC-015 item 2): answered for reachability.**
Strict neighborhood re-checked empty; PQClean measured under `widened_optimized_compare`; isolation-versus-systemic is no longer blocked by `second_impl_unavailable`.

**Library-facing adequacy (DEC-015 item 1): restated for audited-library power.**
Python `synthetic_cmp` is gone and scorers do not special-case `len(diffs)==1`, but `defective_compare.c` retains the multiplicity gate and is exercised only through the harness adequacy probe. Empty `library_G2_minus_G1_excluding_known_defect` / `library_G3_minus_G1_excluding_known_defect` show widened classes still add nothing on real libraries.

## What the isolation claim does and does not license

**Does license (narrow)**

- Recording `isolated_to_audited_commits` with **`criterion_used=widened_optimized_compare`** bound to the claim.
- Scoped laboratory observations: known wolfSSL AVX2 defect retained; PREFIX-NEON silents treated as prior known NEON class; no new reproducible primitive silent index / equal-length decap accept on post-fix SCALAR/AVX2/NEON or PQClean avx2 verify under grids actually run.
- Injected-object control is G1-silent on R and G2/G3-visible via `adequacy_probe` dlopen without scorer `len(diffs)==1` branching.

**Does not license**

- Strict fixed-bound-tail isolation or support of H-MLKEM-004’s mechanism class.
- Claim that G2/G3 have discriminating power against unmodified wolfSSL/PQClean compare paths beyond the injected defect object.
- Systemic cleanliness of untested implementations, backends, or parameter sets.
- Strong differential reference (anchor weak; NIST unused).
- Completeness of API-boundary multi-byte/alignment coverage (`G2G3_spot` only).
- Completeness of packaged coverage accounting (NEON omitted from `class_coverage_report.json`).
- MLWE hardness, passive ML-KEM security, crypto-scale validation, exploits, or disclosure-ready vulnerability claims.

## Most damaging finding

The adequacy “repair” relocates the EXP-MLKEM-004 multiplicity tautology into a dlopen’d C object that never sits on the audited libraries’ compare/decap entries, then sets `added_discriminating_power` true while real-library marginal sets stay empty. Combined with empty-neighborhood widening to the same PQClean verify previously rejected under strict mechanism match, the strong class name `isolated_to_audited_commits` is easy to over-read as answering the original fixed-bound isolation question.

## Next concrete action

Coordinator accepts `isolated_to_audited_commits` only as **revised / criterion-bound** (`widened_optimized_compare`), refuses strict fixed-bound or H-MLKEM-004 support upgrades, retains OBJ-RT005-001..005 as standing scope limits, and either places a baseline-invisible defect on a real library compare entry before claiming audited-library instrument power or downgrades adequacy success language to injected-object reachability.
