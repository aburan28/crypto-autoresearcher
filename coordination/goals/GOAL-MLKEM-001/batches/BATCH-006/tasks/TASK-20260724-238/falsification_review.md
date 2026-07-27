# Falsification review — TASK-20260724-238 / EXP-MLKEM-003

Independent Red Team session. No official state changed. Experiment artifacts untouched.

## Verdict on outcome classification

**`isolated_to_audited_commits` is the wrong class under the frozen precedence.**

Correct class: **`generator_hardening_insufficient`**.

Reason: `specification.yaml` ranks `generator_hardening_insufficient` above `isolated_to_audited_commits` and defines it as G2/G3/G4 producing no finding that G1 did not already produce, including on the positive control. Committed `class_marginal_information` has `G2_minus_G1: []` and `G3_minus_G1: []`. On PREFIX-AVX2 ML-KEM-1024, G1 and G2 both recover `{1536..1567}`; G3 recovers a subset. Rediscovery is not marginal information. The Executor’s `G2_or_G3_added_discriminating_power_on_positive_control: true` contradicts those empty arrays and the metric definition.

Scoped measurement text (“no new silent indices on postfix/liboqs under grids run”) can survive as observation. It does not unlock the isolation outcome class.

## Attack lines

| Line | Result | One-line hold |
|------|--------|---------------|
| 1 Representativeness of liboqs | **Landed** (vacuous-portable-C subclaim **defeated**) | First-preference convenience; AVX2 verify is length-driven intrinsics, not wolfSSL-style fixed-bound asm; liboqs grid is combined/partial G2 |
| 2 Generator still blind / precedence | **Landed — class-flipping** | Empty marginals ⇒ `generator_hardening_insufficient` |
| 3 Run-record faithfulness | **Landed** | ~11s total; RUN-009 ~3.5s; wolfSSL builds are EXP-002 symlinks; purpose overclaims computation recorded |
| 4 Anchor grade | **Landed** | NIST files fetched, unused; validation = liboqs in-tree KAT; liboqs self-check `n_tested=1` graded strong under ACVP-sounding name |
| 5 Coverage gaps as results | **Landed** | liboqs G4 = harness refuse; no NEON G4 rows; coverage report omits NEON; liboqs combined class with null coverage |
| 6 Scope of the null | **Landed** | Isolation (even if it stood) licenses only exercised backends/grids; not ML-KEM generally, not security, not untested projects |

## OBJ-001..005 — answered vs restated

| Prior objection | Disposition |
|-----------------|-------------|
| OBJ-001 primitive ≠ API accept | **Answered** — decap-boundary + message-stability measured |
| OBJ-002 single-byte generator blindness | **Restated, not answered** — classes added; marginal information empty; blindness becomes `generator_hardening_insufficient` |
| OBJ-003 dispatch / NEON API | **Answered with scope** — NEON decap under qemu present; native silicon still open |
| OBJ-004 vector archival | **Answered** — `vectors/` present |
| OBJ-005 weak anchor | **Restated with rebranding** — in-tree liboqs KAT wearing NIST_ACVP name; downloaded NIST unused |

## What the null does and does not license

**Does license:** laboratory observation of no new reproducible silent index / equal-length decap accept on the exact backends and mutation grids executed, outside the known v5.9.1 defect; re-detection of that positive control.

**Does not license:** `isolated_to_audited_commits` under frozen precedence; claim that hardening added discriminating power; systemic cleanliness of optimized ML-KEM comparison code; ML-KEM/MLWE security; other implementations/versions; independent NIST ACVP certification from unused downloads; clean liboqs malformed-length handling; native NEON attestation.

## Most damaging finding

Outcome misclassification via inverted precedence: empty `G2_minus_G1` / `G3_minus_G1` requires `generator_hardening_insufficient` above `isolated_to_audited_commits`, and the Executor treated rediscovery as added discriminating power.

## Next concrete action

Coordinator rejects `isolated_to_audited_commits`, records `generator_hardening_insufficient`, and retains OBJ-RT003-001..006 as scope limits. Optional cheapest repair path if isolation is still desired: second implementation with fixed-bound asm tails under full per-class G2/G3, plus validation against the already-downloaded NIST ACVP prompt/expected pair with honest naming.
