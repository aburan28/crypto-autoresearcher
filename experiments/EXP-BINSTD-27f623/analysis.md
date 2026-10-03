# Analysis: EXP-BINSTD-27f623 (H-BINSTD-b1f016) Stages 0–1

Review plan: `experiments/EXP-BINSTD-27f623/review/review-plan.yaml`
(`REVIEW-BINSTD-27f623-20261003`), written before this analysis.
Producer: TASK-20261003-f99058 (snapshot TASK-20261003-54b1e6).
Decision target: `replicate` preferred over `support` for this first
positive instrument package. Stub/toy scale only.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-95fcfd` (Stage 0) and `RUN-BINSTD-60aff6` (Stage 1). Both have
`manifest.yaml` + additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`,
and `check.stdout.log` reporting `{"ok": true, ...}`. Nested manifests:
`status: completed`, `result.valid: true`, outcomes `S0-FREEZE-OK` /
`E-GATE-HOLDS`, `certificate.kind: none`, `amazon_bedrock: NOT_USED`.
Within `maximum_runs: 3`. Wall times ~0.11 s each. Raw Stage-1 metrics
agree with `stage1/census-matrix.json` and `RESULTS.md`:
`empty_usable_rate_on_ord_eq_n_minus_1=1.0`,
`synthetic_injection_catch_rate=1.0`, `positive_control_nonempty_count=4`,
`route_agreement_rate=1.0`. Stage-0 `artifact_sha256` entries match the
committed stage0 files (frozen-panels / gate-api /
preregistered-predictions). No break / exponent / deployed insecurity
claim. No Bedrock.

**Stage 0 (J2).** `frozen-panels.json`: |F|=12 odd primes
`{11,13,19,29,37,53,59,61,67,83,101,107}` (>=10), |C|=4
`{17,23,31,41}` (>=3), seed `2026100311`, usable filter
`stable_dimensions excluding {0,1,n-1,n}`, predicate source
`EXP-BINSTD-178742/.../part1_surface.py`.
`preregistered-predictions.json` carries `frozen_before_stage1: true` and
HEUR-BINSTD-11aa69-H1 thresholds (empty rate 1.0, catch rate 1.0,
positive nonempty min 1). `gate-api.json` present. Outcome
`S0-FREEZE-OK` / `completed_valid`. No Stage-1 rates in Stage 0.

**Stage 1 (J3).** Census matrix: 12 forced-negative rows all
`usable_dimensions=[]`, `routes_agree=true`, `order_verified=true`,
`ord_n_2=n-1`. Four positive-control rows all nonempty usable
(`17->{8,9}`, `23->{11,12}`, `31->{5,6,10,11,15,16,20,21,25,26}`,
`41->{20,21}`), `ord_n_2 < n-1`. Injection on n=11:
`injected_usable=[2]`, gate `accepted=false`,
`failure_signature=SYNTHETIC_NONEMPTY_INJECTION_REJECTED`. Aggregate
outcome `E-GATE-HOLDS`.

**Blind re-derivation.** From the order statement and panel parameters
alone (not producer implementation): iteration and divisor-test
`ord_n(2)` agree and equal `n-1` for every n in F; agree and are strictly
less than `n-1` for every n in C. Under the Part-1 usable filter, `ord=n-1`
implies stable dimensions subset of `{0,1,n-1,n}` when Phi_n is irreducible over
F2, hence usable emptiness on F is the structural prediction of
HEUR-BINSTD-11aa69-H1. Producer row rates match that prediction at the
frozen stub panel.

## Comparison

Matches E-GATE-HOLDS: Stage-0 freeze complete; empty usable rate 1.0 on F;
injection rejected; positive nonempty count 4 (>=1); route agreement 1.0.
Does not light E-GATE-FAILS, O-CONTROL-FAIL, or O-IMPEDIMENT.
Proves-too-much objects hold: injection rejected; positives nonempty;
no break / exponent / n>=131 security transfer filed.
Blind ord re-derivation agrees with producer dual-route columns.

## Inference

First Stages 0–1 package is **valid** and **supports** the scoped
instrument claim of H-BINSTD-b1f016 / HEUR-BINSTD-11aa69-H1 at
strength **preliminary** and `claim_tier: toy`: on the Stage-0-frozen
odd-prime panels, usable_dimensions is empty for every forced-negative
with `ord_n(2)=n-1` under both Part-1 routes, the synthetic non-empty
injection is rejected, and positive controls with `ord_n(2)<n-1` are
nonempty. Standing preference and review-evidence rule: prefer
**replicate** over **support** on first unreplicated positive package.
Do not promote to KN-FIND. Empty usable != security claim about any
curve. Stage 2 (independent re-derive) remains unauthorized until a
later decision.

Official decision target: `replicate`; hypothesis `approved` → `analyzed`.

## Limitation

- First unreplicated observation; no independent validator/red-team (PD-1).
- Stub/toy odd primes only (|n|<=107 on F; Part-1 toy positives); no
  transfer to a security claim about n>=131.
- Instrument / observational; `certificate.kind=none`; no discrete_log /
  decomposition / key_recovery claim.
- Stage 2 independent re-derive not run and not authorized by
  DEC-20261003-e9b17b.
- Producer manifests originally flat; nested envelopes supplied by
  immutable `manifest_v2.yaml` schema supersessions (no re-measurement).
- Strength preliminary — insufficient for support or KN-FIND promotion.
- No break; no exponent; Amazon Bedrock not used.
