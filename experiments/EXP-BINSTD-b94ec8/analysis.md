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
