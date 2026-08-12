# Falsification review — TASK-20260724-922 / EXP-MLKEM-004

Independent Red Team session. No official state changed. Experiment artifacts untouched. No git commit.

Machine-readable verdict: `red_team_report.yaml` (`RT-20260724-003`)

Branch gate: `cursor/explore-ml-kem-cryptanalysis-a197`; `experiments/EXP-MLKEM-004/execution-report.yaml` present. Snapshot basis: Coordinator archive for TASK-20260724-920.

## Verdict on outcome classification

**`second_impl_unavailable` is the correct class under the repaired precedence.**

It does not flip to `isolated_to_audited_commits` (second impl not measured), `generator_hardening_insufficient` (synthetic control passed), or `systemic_incomplete_comparison` (no new silent/accept outside the known defect).

## Attack lines

| Line | Result | One-line hold |
|------|--------|---------------|
| 1 second_impl dodge / narrow criterion | **Landed with scope** (dishonest-rejection subclaim **defeated**) | Per-impl rejections match frozen length-parameterized ban; preference neighborhood looks empty → class nearly predetermined; secondary liboqs not re-run; `/tmp` evidence not packaged |
| 2 Synthetic control toy | **Landed — most damaging** | `synthetic_cmp` is G1-silent / multi-byte-unequal by construction; only harness failure can miss it; library marginals still empty |
| 3 Post-fix null underpowered | **Landed** | Primitive zeros are real and scoped; API “G2/G3” is `G2G3_spot` single-byte offsets; coverage report omits NEON; synthetic pass does not strengthen library null |
| 4 Weak anchor invalidates | **Defeated** | Honest weak grade; qualifies reference strength only |
| 5 Licensing of the class | **Landed as scope** | Infrastructure for cross-impl line; wolfSSL-only observations allowed; isolation and H-MLKEM-004 support blocked |

## KN-TECH-030 — answered or restated?

**Answered for precedence reachability; restated for library-facing instrument power.**

- Answered: baseline-invisible harness control makes `generator_hardening_insufficient` and `isolated_to_audited_commits` both reachable worlds; rediscovery of wolfSSL `{1536..1567}` is excluded from marginals.
- Restated: empty `library_G2_minus_G1_excluding_known_defect` / `library_G3_minus_G1_excluding_known_defect` show widened classes still add nothing on real libraries.

## What the null does and does not license

**Does license**

- Recording preference-order exhaustion without a mechanism-matched second implementation.
- Scoped wolfSSL observations: known defect retained; no new reproducible primitive silent index / equal-length decap accept on post-fix backends under grids actually run.
- Blocking `isolated_to_audited_commits` and any claim of isolation across implementations.

**Does not license**

- Support for H-MLKEM-004.
- Systemic cleanliness of optimized ML-KEM comparison code.
- Claim that G2/G3 have library-facing discriminating power beyond the harness synthetic control.
- Strong differential reference (anchor is weak; NIST downloads unused).
- Completeness of API-boundary multi-byte/alignment coverage (`G2G3_spot` only).
- MLWE hardness, passive ML-KEM security, deployed systems, or untested implementations.

## Most damaging finding

The synthetic control repairs KN-TECH-030’s *protocol reachability* but is a tautological harness self-test (`len(diffs)==1` → equal; else unequal in R). Combined with a mechanism-match rule whose public preference neighborhood appears empty, the experiment was structurally steered to `second_impl_unavailable` / unable-to-claim-isolation rather than a decisive isolation-versus-systemic result—while library-facing G2/G3 marginals remain empty.

## Next concrete action

Coordinator accepts `second_impl_unavailable`, refuses H-MLKEM-004 support/isolation promotion, retains OBJ-RT004-001..003 as scope limits, and either procures a true fixed-bound hand-written-tail second implementation plus a *library-facing* baseline-invisible control, or rewrites the isolation question so it does not require a currently empty public mechanism neighborhood.
