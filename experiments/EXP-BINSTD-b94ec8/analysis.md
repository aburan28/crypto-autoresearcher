# Analysis: EXP-BINSTD-b94ec8 Stages 0–1 (H-BINSTD-dfc684)

Review plan: `experiments/EXP-BINSTD-b94ec8/review/review-plan.yaml`
(`REVIEW-BINSTD-b94ec8-20261003`), written before this analysis.
Producer: TASK-20261003-4d4739. Snapshot: TASK-20261003-75b740
(tip `f66c1dbfa7c0bcaaf0182ef389b88c3e798e756e`). Stages 0–1 only.
Headline O-\* deferred to Stage 2. No break / exponent / deployed attack.
Amazon Bedrock: NOT_USED.

## Observation

**Validity (J1).** Two run directories under `runs/`:

| run | stage | status / outcome | key flags |
|-----|-------|------------------|-----------|
| RUN-BINSTD-ebcf55 | 0 | completed / worksheet_ok=true | preregistered_match=true; admissible={(31,5),(31,6)} |
| RUN-BINSTD-8453bf | 1 | completed / SETUP_PASS | e0_overall_ok=true; structure_equal_across_curve_shapes=true; impediments=[] |

Each run has `manifest.yaml`, `manifest_v2.yaml` (schema completion),
`raw-result.json`, `execution-receipt.json`, `environment.json`,
`stdout.log`, `command.txt`. Raw flags agree with RESULTS.md. Within
`maximum_runs: 3` (2 used). `amazon_bedrock: NOT_USED` on both raw
results and RESULTS. Claims: break=false, exponent_move=false,
deployed_attack=false. No Stage-2 leaf-count artifacts present.
Certificate.kind on manifests is none for the run envelope; planted SAT
certificates live inside fixture E0 (group-arithmetic, pass rate 1.0).

**Stage 0 (J2).** Worksheet artifacts:
`stage0/preregistered-predictions.json`, `stage0/worksheet-note.md`.
Producer reports:

- counting identity (A) frozen (gauge-fixed search `|V^m/S_m|=2^{ml}/m!`)
- `ord_n(2)` = `{17:8, 23:11, 29:28, 31:5, 37:36, 41:20}`
- dual-route (div vs iter) agree on all six n
- m=4 admissibility screen computed = expected = `{(31,5),(31,6)}`
- search sizes: l=5 → `2^{20}/24 = 43690.666…`, multiset 52360;
  l=6 → `2^{24}/24 = 699050.666…`, multiset 766480
- claim-(D): D3=11.01 bits; gap above D3 ≈ 116.405 bits; matched rho
  60.809 bits; per-instance factor 131 (~7.03 bits) does not close the
  gap and is withdrawn after (A)
- `worksheet_ok=true`, `preregistered_match=true`

**Blind re-derivation (J2).** From the multiplicative-order definition
alone (not producer `implementation/` or Stage-0 stdout):
`ord_n(2)` recovers exactly `{17:8, 23:11, 29:28, 31:5, 37:36, 41:20}` —
match. Admissible-cell set from contract prediction equals producer
screen `{(31,5),(31,6)}`; search sizes recompute as `2^{ml}/24`.

**Stage 1 fixture E0 (J3).** `stage1/fixture-E0.json` and
`stage1/curves-and-bases.json`:

- `n=31`, modulus `0x80000009`, Phi_31 six quintics, `ord_n(2)=5`
- bases: stable_V5, stable_V6, window_deg_5, window_deg_6
- curves: koblitz_a0, koblitz_a1, ordinary
- 12 arms; every arm `ok=true`
- planted SAT: requested=20, planted=20, certified=20,
  `certificate_pass_rate=1.0` on every arm
- at fixed (base,l), export structure equal across curve shapes
  (l=5: n_vars=20, n_xor_rows=20, n_cnf_clauses=80, blocks [5,5,5,5];
   l=6: n_vars=24, n_xor_rows=24, n_cnf_clauses=96, blocks [6,6,6,6])
- `overall_ok=true`, `structure_equal_across_curve_shapes=true`
- search sizes printed beside the fixture (same as Stage 0)

No UNSAT leaf-count medians, ratios, or O-\* label in this package.

## Comparison

Matches the frozen Stages 0–1 success gate of EXP-BINSTD-b94ec8 /
DEC-20261002-e6818c: Stage-0 worksheet present with screen
`{(31,5),(31,6)}`; fixture E0 passes with certificate_pass_rate=1.0;
no O-ARTIFACT / O-IMPEDIMENT. Does **not** light O-NULL / O-DIVISOR /
O-SHAPE (Stage 2 metrics absent). Blind `ord_n(2)` agrees with
producer. Proves-too-much control: Stages 0–1 must not be read as H1
support or as any break/exponent claim — they are not.

## Inference

Stages 0–1 package is valid and confirms the exact Stage-0
admissibility/counting worksheet plus Stage-1 instrument readiness
(fixture E0). Preferred Coordinator transition: **expand** — authorize
`/run` Stage 2 under the already-approved contract (Stages 0–2 were
authorized by DEC-20261002-e6818c; trial-plan-v1 admitted 0–1 first).
Do **not** support, weaken, or reject_scoped H1: the shape-null
measurement has not run. Evidence strength **preliminary** (first
observation; no independent validator/red-team; PD-1). Knowledge
promotion not warranted.

## Limitation

- Stage 2 (CNF-XOR leaf counts, ratios, O-\* decision) not executed.
- WDSat build readiness for Stage 2 not evidenced in this package
  (SETUP_PASS is fixture/export only); a missing WDSat at Stage 2 is
  O-IMPEDIMENT, never negative evidence against H1.
- Single primary seed / unreplicated setup package.
- No independent validator/red-team session (PD-1).
- Manifest schema completed additively via manifest_v2.yaml; original
  flat manifests remain byte-identical.
- Toy tier at n=31; claim-(D) forbids deployed/exponent reading.
- Amazon Bedrock unused; must stay unused on Stage 2.

---

# Analysis: EXP-BINSTD-b94ec8 Stage 2 (H-BINSTD-dfc684)

Review plan: `experiments/EXP-BINSTD-b94ec8/review/review-plan-stage2.yaml`
(`REVIEW-BINSTD-b94ec8-stage2-20261003`), written before this Stage-2
analysis. Producer: TASK-20261003-43c403. Snapshot: TASK-20261003-72bf6d
(tip `29d66c5f54e05eeaccb12cb073d916f67b8aa3b6`). Prior expand:
EV-BINSTD-0e42ac / DEC-20261003-8881ef. No re-run in this review.
No break / exponent / deployed attack. Amazon Bedrock: NOT_USED.

## Observation

**Validity (J1).** One Stage-2 run directory:

| run | stage | status / outcome | key flags |
|-----|-------|------------------|-----------|
| RUN-BINSTD-e8660a | 2 | failed_infrastructure / O-IMPEDIMENT | wdsat_build_ok=true; stable_bases_are_window_proxy=true; leaf_census_attempted=false |

Artifacts present: `manifest.yaml`, `manifest_v2.yaml` (additive schema
completion; original sha256 `96416447…` matches registry superseded_path;
v2 sha256 `27759a86…`), `raw-result.json`, `execution-receipt.json`
(`status: output_validated`, `check_returncode: 0`), `environment.json`,
`stdout.log`, `command.txt`, `check.stdout.log` = `OK`, stage2
`arm-summaries.json` and `leaf-counts.jsonl`. Raw flags agree with
RESULTS.md. Claims: break=false, exponent_move=false,
deployed_attack=false. `amazon_bedrock: NOT_USED` on raw, manifests,
RESULTS, and snapshot receipt.

**Impediment identity (J2).** Stage-1
`curves-and-bases.json` records:

- `stable_V5.kind = window_proxy_for_stable_dim` (l=5; Phi_31-ker deferred)
- `stable_V6.kind = window_proxy_for_stable_dim` (l=6; Phi_31-ker deferred)
- `window_deg_5.kind = window_deg`, `window_deg_6.kind = window_deg`

Blind re-derivation from that JSON alone (not `implementation/run.py`
or Stage-2 stdout) recovers exactly those four kinds. Therefore
stable and window controls are not distinct bases — Stage-2 H1 null
cannot start. Producer correctly sets
`stable_bases_are_window_proxy=true`, `leaf_census_attempted=false`,
impediment id
`frobenius_stable_bases_are_window_proxy_stage1_deferred_phi31_ker`.

**WDSat (not blocking).** Vendored `inputs/TRIMOSKA-WDSAT-2024` capacity
smoke: `wdsat_probe.build_ok=true`, `make_returncode=0`, binary sha256
`c77db8d750d2c2186245efb42d2c25ca17c24b93215ad1bfee13fd3917cc183b`.
Missing WDSat is NOT the impediment.

**Primary metrics (unset).**
`koblitz_ordinary_median_leaf_ratio: null`, `window_stable_ratio: null`.
`leaf-counts.jsonl` is a probe note only (no per-target leaf rows).

## Comparison

Matches the contract's O-IMPEDIMENT / infrastructure-stop class and
AGENTS.md rule 5: instrument readiness failure is never negative
mathematical evidence against H1. Distinct from O-NULL / O-DIVISOR /
O-SHAPE (those require leaf-count ratios). Distinct from O-ARTIFACT
(fixture E0 already passed at Stage 1; this stop is base-identity, not
planted-cert failure). Proves-too-much: reading window_proxy as H1
falsification is forbidden by the review plan and by the absence of
any ratio measurement.

## Inference

Stage-2 package is valid as an instrument stop. Preferred Coordinator
transition: **refine** — author an additive amendment that constructs
and binds explicit Phi_31-ker Frobenius-stable V5/V6 (distinct from
window_deg controls), then re-admit `/run` Stage 2 leaf census under
the already-approved protocol (DEC-20261002-e6818c) and prior expand
(DEC-20261003-8881ef). Do **not** support, weaken, or reject_scoped H1:
no leaf counts exist. Hypothesis and experiment remain **approved**.
Evidence strength **preliminary**. Knowledge promotion not warranted.

## Limitation

- No Stage-2 scientific measurement (census not started).
- Coordinator-direct / same-session review (PD-1).
- Stage-1 deferred Phi_31-ker bases; window_proxy is disclosed debt, not
  a secret defect discovered after H1 measurement.
- Toy tier at n=31; claim-(D) forbids deployed/exponent reading.
- Additive manifest_v2 schema completion; original flat manifest
  byte-identical.
- Amazon Bedrock unused; must stay unused on any Stage-2 re-run.

---

# Analysis: EXP-BINSTD-b94ec8 Stage 2 refine / Phi_31-ker (H-BINSTD-dfc684)

Review plan:
`experiments/EXP-BINSTD-b94ec8/review/review-plan-stage2-r2.yaml`
(`REVIEW-BINSTD-b94ec8-stage2-r2-20261003`), written before this analysis.
Producer: TASK-20261003-81632a. Snapshot: TASK-20261003-f701df
(tip `137e8c0740347c17a949b19b360c611261140d3f`). Amendment:
`AMD-EXP-BINSTD-b94ec8-20261003-phi31ker`. Prior Stage-2 refine decision:
EV-BINSTD-671f89 / DEC-20261003-031dba. No re-run in this review.
No break / exponent / deployed attack. Amazon Bedrock: NOT_USED.

## Observation

**Validity (J1).** One Stage-2 refine run directory:

| run | stage | status / outcome | key flags |
|-----|-------|------------------|-----------|
| RUN-BINSTD-377a61 | 2 | failed_infrastructure / O-IMPEDIMENT | phi31_ker_bound=true; stable_bases_are_window_proxy=false; wdsat_build_ok=true; leaf_census_attempted=false; impediment=semaev_m4_cnf_xor_instance_export_not_implemented |

Artifacts present: `manifest.yaml`, `manifest_v2.yaml` (additive schema
completion; original sha256 `80999878…` matches registry superseded_path;
v2 sha256 `68c7cfe4…`), `raw-result.json`, `execution-receipt.json`
(`status: output_validated`, `check_returncode: 0`), `environment.json`,
`stdout.log`, `command.txt`, `check.stdout.log` = `OK`, additive
`stage1/phi31-ker-bases.json`, `stage2/r2-phi31ker/{arm-summaries.json,
leaf-counts.jsonl, RESULTS.md}`. Raw flags agree with r2 RESULTS.md.
Claims: break=false, exponent_move=false, deployed_attack=false.
`amazon_bedrock: NOT_USED` on raw, manifests, r2 RESULTS, and snapshot.
Prior Stage-2 paths (`runs/RUN-BINSTD-e8660a/`,
`stage2/{leaf-counts,arm-summaries}.json*`, top-level `RESULTS.md`) were
not rewritten.

**Window_proxy gate cleared (J2 progress).** Blind read of
`stage1/phi31-ker-bases.json` alone (not `implementation/run.py` /
`phi31_ker.py` / Stage-2 stdout):

- `stable_V5.kind = phi31_ker`, `frobenius_stable=true`,
  `distinct_from_window_deg=true`, basis_hex
  `{0x2,0x4,0x10,0x100,0x10000}`
- `stable_V6.kind = phi31_ker`, `frobenius_stable=true`,
  `distinct_from_window_deg=true`, basis_hex
  `{0x1,0x2,0x4,0x10,0x100,0x10000}`
- `window_deg_5.kind = window_deg`, basis_hex `{0x1,0x2,0x4,0x8,0x10}`
- `window_deg_6.kind = window_deg`, basis_hex `{0x1,0x2,0x4,0x8,0x10,0x20}`
- `window_proxy=false`, `selected_factor_hex=0x25`
- set-equality: V5 ≠ window_deg_5, V6 ≠ window_deg_6

Matches producer `phi31_ker_bound=true` and
`stable_bases_are_window_proxy=false`. Prior refine successor
(DEC-20261003-031dba) discharged on the base-identity gate.

**New impediment (J2 block).** After bases + WDSat OK, producer records
`impediments: [semaev_m4_cnf_xor_instance_export_not_implemented]`:
Stage-1 fixture E0 supplies structure skeletons + planted group-arithmetic
certificates only; full Semaev m=4 CNF-XOR/ANF instance export for the
50-target UNSAT leaf census is not implemented. Census correctly not
started. WDSat capacity-smoke still `build_ok=true` (binary sha256
`c77db8d750d2c2186245efb42d2c25ca17c24b93215ad1bfee13fd3917cc183b`) —
not the blocker.

**Primary metrics (unset).**
`koblitz_ordinary_median_leaf_ratio: null`, `window_stable_ratio: null`.
`stage2/r2-phi31ker/leaf-counts.jsonl` is a refine probe note only (no
per-target leaf rows).

## Comparison

Matches the contract's O-IMPEDIMENT / infrastructure-stop class and
AGENTS.md rule 5. Distinct from the prior Stage-2 stop
(RUN-BINSTD-e8660a / window_proxy): that gate is cleared; the new stop is
downstream instrument debt (Semaev export). Distinct from O-NULL /
O-DIVISOR / O-SHAPE (those require leaf-count ratios). Distinct from
O-ARTIFACT (fixture E0 already passed; this is missing export, not a
planted-cert failure). Proves-too-much: reading Semaev-export
O-IMPEDIMENT as H1 falsification, or reading Phi_31-ker bind alone as H1
support, is forbidden by the review plan and by the absence of any ratio
measurement.

## Inference

Stage-2 refine package is valid: window_proxy cleared (progress);
census still blocked on Semaev m=4 CNF-XOR instance export
(infra impediment, not H1 falsification). Preferred Coordinator
transition: **refine** — implement / bind Semaev m=4 CNF-XOR/ANF instance
export under an additive amendment, then re-admit `/run` Stage 2 leaf
census under DEC-20261002-e6818c / DEC-20261003-8881ef /
DEC-20261003-031dba authority. Do **not** support, weaken, or
reject_scoped H1: no leaf counts exist. Hypothesis and experiment remain
**approved**. Evidence strength **preliminary**. Knowledge promotion not
warranted.

## Limitation

- No Stage-2 scientific measurement (census not started).
- Coordinator-direct / same-session review (PD-1).
- Semaev m=4 export path still missing after Phi_31-ker bind.
- Toy tier at n=31; claim-(D) forbids deployed/exponent reading.
- Additive r2 artifacts; prior Stage-2 immutable bytes preserved.
- Amazon Bedrock unused; must stay unused on any Stage-2 re-run.
