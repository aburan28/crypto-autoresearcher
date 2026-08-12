# Falsification review — TASK-20260724-936 / EXP-MLKEM-006

Independent Red Team session. No official state changed. Experiment artifacts untouched. No git commit. No runs fabricated.

Machine-readable verdict: `red_team_report.yaml` (`RT-20260724-005`)

Branch gate: `cursor/explore-ml-kem-cryptanalysis-a197`; `experiments/EXP-MLKEM-006/execution-report.yaml` present. Snapshot basis: Coordinator-verified `658f9e530ac27ab56092501138ce53409c8efb28` (TASK-20260724-934).

Inference: `requested_policy=review-xhigh`; `resolved_model=cursor-grok-4.5-high-fast`; `fallback_used=true`; `independent_session=true`.

## Verdict on outcome classification

**Disposition: `revise`.**

Executor class **`second_impl_unavailable`** is not the unique correct package class under a reading that privileges H-MLKEM-006 and the EXP-006 repair objective. Preferred corrected class: **`synthetic_control_inadequate`** (higher frozen precedence than `second_impl_unavailable`), because load-bearing adequacy never exercises wolfSSL/PQClean library compare symbols.

**GOAL-criterion-2 empty-neighborhood disposition: scoped yes.** Strict fixed-bound order re-checked empty may be recorded as unavailability for criterion 2. It must **not** be paired with a `CTRL-TRUE-LIBRARY-PATH-INTERPOSITION` pass, nor paraphrased as fixed-bound isolation / H-MLKEM-004 support / elevation of EV-MLKEM-008.

**Isolation claim (`isolated_to_audited_commits`): does not stand** — and the executor correctly did not emit it as the package class. Residual overclaim is the true-library-path / CTRL-pass narrative.

## Attack lines

| Line | Result | One-line hold |
|------|--------|---------------|
| 1 True library-path vs residual tautology | **Landed — most damaging** | `-DINTERPOSE_COMPARE` bypasses `mlkem_cmp*`; multiplicity gate by construction; library excluding-known-defect marginals still empty (OBJ-RT005-001 recurrence) |
| 2 Call-site wrapper vs `--wrap` attestation | **Landed** | `wrap_link_flags=[]`; `wrap_linked` hard-coded; fake per-symbol counters; `attributable_via_library_call_path` hard-coded; no decap/PQClean wrap |
| 3 second_impl_unavailable / widened / EV-008 honesty | **Landed as scope** | Empty-neighborhood unavailability OK if scoped; widened PQClean / EV-MLKEM-008 must not become H-MLKEM-004 / criterion-2 isolation |
| 4 Precedence licensing | **Landed** | `synthetic_control_inadequate` should outrank `second_impl_unavailable` when CTRL pass is false |
| 5 claim_tier upgrade | **Defeated** | Stays `laboratory_implementation_conformance` |
| 6 Coverage / docker / stale docs | **Landed with scope** | `G2G3_spot`, docker amd64-on-arm64, stale `implementation.md` dlopen text; nonfatal |

## OBJ-RT005-001 — answered or restated?

**Restated (not cured).**

EXP-005’s `adequacy_probe`/dlopen path is no longer load-bearing. EXP-006 moves the same multiplicity-gate comparator into `conformance_probe` via compile-time `library_cmp()` replacement. That is still harness-owned compare logic, not interposition onto wolfSSL/PQClean symbols “actually called” by substantive probes. Empty `library_G2_minus_G1_excluding_known_defect` / `library_G3_minus_G1_excluding_known_defect` confirm widened classes still add nothing on unmodified libraries.

## What the package does and does not license

**Does license (narrow)**

- Recording strict fixed-bound neighborhood emptiness as GOAL completion criterion 2’s **unavailability** limb (not isolation).
- Scoped laboratory observations: known wolfSSL AVX2 defect retained; no new reproducible primitive silent index / equal-length decap accept on post-fix backends or optional PQClean avx2 peer under grids actually run (API still partly `G2G3_spot`).
- Probe-local interposed object is G1-silent on R and G2/G3-visible by construction when called from `conformance_probe` under `-DINTERPOSE_COMPARE`.

**Does not license**

- Claim that OBJ-RT005-001 was repaired or that CTRL-TRUE-LIBRARY-PATH-INTERPOSITION truly passed against library entry points.
- `isolated_to_audited_commits`, H-MLKEM-004 support, or GOAL criterion 2 beyond unavailability.
- Paraphrase of EV-MLKEM-008 or any widened null as fixed-bound-tail isolation.
- Strong differential reference (anchor weak; NIST unused).
- Completeness of API-boundary multi-byte/alignment coverage.
- Native x86_64 AVX2 microarchitectural fidelity (docker amd64-on-arm64).
- MLWE hardness, passive ML-KEM security, crypto-scale validation, exploits, or disclosure-ready vulnerability claims.
- Any `claim_tier` above `laboratory_implementation_conformance`.

## Most damaging finding

The “true library-path” repair is a compile-time probe bypass: `library_cmp()` calls `mlkem_interposed_defective_compare` and never `mlkem_cmp_avx2`, while attestation still names `comparison_symbol: mlkem_cmp_avx2`, hard-codes `wrap_linked: true`, and collapses three wrap counters into one atomic. Combined with a CTRL pass that lets classification skip to `second_impl_unavailable`, the package invites reading an empty-neighborhood bookkeeping class as if instrument adequacy were cured.

## Next concrete action

Coordinator revises toward **`synthetic_control_inadequate`** (fail CTRL-TRUE-LIBRARY-PATH-INTERPOSITION), retains empty-neighborhood **`second_impl_unavailable` only as scoped criterion-2 disposition**, refuses H-MLKEM-004 / EV-MLKEM-008 / widened-null paraphrases, keeps `claim_tier` at `laboratory_implementation_conformance`, and either performs true symbol-level interposition with non-hard-coded attestation or rewrites the goal’s library-path adequacy conjunct.
