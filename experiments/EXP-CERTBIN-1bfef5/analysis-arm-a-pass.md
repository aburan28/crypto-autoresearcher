# Analysis: EXP-CERTBIN-1bfef5 Stage-1 re-admit (H-CERTBIN-4d3853)

Review plan: `experiments/EXP-CERTBIN-1bfef5/review/review-plan-arm-a-pass.yaml`
(`REVIEW-CERTBIN-1bfef5-ARM-A-PASS-20261003`), written before this analysis.
Producer: TASK-20261003-1782c9. Snapshot: TASK-20261003-4d9aa1 @
`344f2f8b18`. Re-admit: DEC-20261003-954f1b / AMD-20261003-9ef431.
Design approval: DEC-20261002-711879. Prior refine package
EV-CERTBIN-cc1d02 / DEC-20261003-be5e40 / RUN-CERTBIN-ae7b9c /
RUN-CERTBIN-d4f1ee unchanged (immutable). Decision target: **expand**
(O-ARM-A-PASS identity gate; not E-SET/E-POLY). No break; no exponent;
no ECC2K-130; no Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Two new run directories under `runs/`:
`RUN-CERTBIN-68f37f` (Stage 0 verify-existing) and `RUN-CERTBIN-6e4916`
(Stage 1 arm-(a) score). Each has `manifest.yaml`, additive
`manifest_v2.yaml`, `raw-result.json`, `environment.json`, `command.txt`,
`execution-receipt.json` (`status: output_validated`), and
`check.stdout.log` = `PASS`. Stage-0 and Stage-1 producer status both
`completed_valid`. Required Stage-0 freeze artifacts remain present;
Stage-1 gate + arm-(a) artifacts present under `stage1/` and mirrored in
the Stage-1 run_dir. Amazon Bedrock not used. `certificate.kind: none`
on Stage 1. Producer claims: `break: false`, `exponent_move: false`.

**Stage 0 (J2).** `RUN-CERTBIN-68f37f` reports `freeze_mode:
verify_existing`, `worksheet_ok: true`, `mismatches: []`. Prior bound
`stage0/*` hashes were not rewritten.

**Stage 1 (J3) — blind gate + agreement re-derivation.**

| gate | source | blind check | producer |
| --- | --- | --- | --- |
| C_PIN | six `EXP-CERTBIN-e94b27/impl/*.py` | sha256 match expected digests | `ok: true` |
| C_SELF | `stage1/c-self.json` | `mismatches: []` | `ok: true` |
| census | `archived-label-census.json` | counts==expected; `label_rows=288` | `ok: true` |
| C_FIX | `c-fix.json` triples | three (nv,D,neq) triples `ok: true` | `ok: true` |
| arm-(a) | `arm-a-basis-swap.json` | `n_agree=288`, `n_disagree=0`, seed `2026092691`, `identity_selfcheck_ok=true` | O-ARM-A-PASS 288/288 |

Blind re-hash of pinned instruments, census recount, and arm-(a)
n_agree/n_disagree match producer fields. `impediments: []` —
IMP-ARM-A-BASIS-SWAP cleared by the wired wrapper.

**Scope / non-claims (J4).** RESULTS.md and AMD C-4 state O-ARM-A-PASS
is the Stage-1 identity-gate pass only — not E-SET/E-POLY. No break, no
exponent, no Bedrock, Stage 2 not authorized under this trial-plan card.
Prior O-IMPEDIMENT package under `runs/RUN-CERTBIN-d4f1ee/` unchanged.

## Comparison

Against H-CERTBIN-4d3853 distinguishable outcomes and AMD C-4:

- Stage 0 verify-existing freeze: **holds** → Stage 1 may be read.
- Instrument gates: **all pass**.
- Arm-(a) identity control: **executed** and **exact 288/288** →
  **O-ARM-A-PASS** by contract (identity gate).
- O-E-SET / O-E-POLY / O-MIXED: **not evaluable** (Stage 2 arms (b)–(d)
  not authorized/run under this card). Arm-(a) exact is a *precondition*
  for those outcomes, not the outcomes themselves.
- O-ARTIFACT: **not met** (no label disagreement; gates pass).
- O-IMPEDIMENT: **cleared** for IMP-ARM-A-BASIS-SWAP (empty impediments).

## Inference

The re-admit package is **valid**. Stage 0 freeze verifies; Stage 1
gates pass; arm-(a) random poly-V / normal-field basis-swap agrees
288/288 with RUN-CERTBIN-c417e0 on the RC-1 archived targets. Official
reading: **O-ARM-A-PASS** as preregistered identity-gate — scoped support
for label/iteration/dimension invariance under the wired basis change at
this toy cell and seed, **not** support for Proposition B/F as theorems,
**not** E-SET/E-POLY rates. Decision: **expand** — authorize design/admit
of Stage 2 (arms (b)–(d) + structured W_4/M_4 rates) under a separate
trial-plan card, keeping Stage-1 identity gate as a precondition.
Hypothesis and experiment `approved → analyzed`. Do **not** support
(H's empirical claims require Stage 2). Do **not** weaken/reject_scoped
(pass is not a falsifier). No break; no exponent; no ECC2K-130.

## Limitation

- Toy RC-1 cell only (n=17, m=2, l=9); Stage 2 not run; no transfer to
  n≥131 / ECC2K-130.
- Single seed (`2026092691`); first unreplicated wired observation.
- No independent validator/red-team (review-plan PD-1) → strength
  capped at preliminary.
- Stage 0 Proposition B/F note remains observational, not machine-checked
  proof; `certificate.kind=none`.
- O-ARM-A-PASS ≠ O-E-SET/O-E-POLY; absence of Stage 2 is not a null
  result on rates.
