# Analysis: EXP-BINSTD-27f623 (H-BINSTD-b1f016) Stages 0–2

## Stages 0–1 (retained; EV-BINSTD-93aee1 / DEC-20261003-947da5)

Review plan: `experiments/EXP-BINSTD-27f623/review/review-plan.yaml`
(`REVIEW-BINSTD-27f623-20261003`), written before Stages 0–1 analysis.
Producer: TASK-20261003-f99058 (snapshot TASK-20261003-54b1e6).
Decision then: `replicate`. Stub/toy scale only.

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


---

## Stage 2 (EV-BINSTD-8a1bbf / DEC-20261003-31466e)

Review plan: `experiments/EXP-BINSTD-27f623/review/review-plan-stage2.yaml`
(`REVIEW-BINSTD-27f623-S2-20261003`), written before this Stage-2 analysis.
Producer: TASK-20261003-a5bab8 (snapshot TASK-20261003-f8f3ab).
Admission: DEC-20261003-6d20b7 / AMD-EXP-BINSTD-27f623-20261003-stage2.
Prior: EV-BINSTD-93aee1 / DEC-20261003-947da5 replicate. Stub/toy only.

### Observation

**Validity (J1).** One Stage-2 run directory: `RUN-BINSTD-d15ac1`. Has
`manifest.yaml` + additive `manifest_v2.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`, `execution-receipt.json`
(`status: output_validated`), and `check.stdout.log` reporting
`{"ok": true, "stage": 2, "outcome": "S2-REPLICATE-AGREE"}`. Nested
manifest: `status: completed`, `result.valid: true`, outcome
`S2-REPLICATE-AGREE`, `certificate.kind: none`, `amazon_bedrock: NOT_USED`.
Admission `DEC-20261003-6d20b7`. Wall time ~0.108 s. Raw metrics agree with
`stage2/independent-rederive.json` and `RESULTS.md`:
`independent_ord_eq_n_minus_1_rate=1.0`,
`independent_usable_empty_rate=1.0`,
`posthoc_ord_agreement_rate=1.0`; members `[11,13,19]`.
`sha256(stage2/independent-rederive.json)` matches raw
`artifact_sha256` (`be06c2d6461b84ca1295bdb66ea46da04d233004b751c11607090ca96e93cbc6`).
No break / exponent / deployed insecurity claim. No Bedrock.

**Independent method (J2).** Three rows, method
`divisor_ladder_pow_only`, `reads_stage1_census=false`,
`order_verified=true`, `ord_equals_n_minus_1=true`,
`usable_dimensions=[]` for n∈{11,13,19}. Post-hoc Stage-1 comparison:
each member has `ord_agree=true` and `usable_empty_agree=true`
(independent_ord equals stage1_ord equals n−1).

**Blind re-derivation (J3).** From the order statement and panel
parameters alone (not producer implementation / Stage-2 run dir):
iteration and divisor-test `ord_n(2)` agree and equal `n−1` for
n∈{11,13,19}. Under the Part-1 usable filter, `ord=n−1` implies
usable emptiness — matching producer independent rows and Stage-1
census on these three members.

### Comparison

Matches S2-REPLICATE-AGREE: all three rates 1.0; independent method
does not read Stage-1 census for the measurement; post-hoc agreement
complete; blind ord re-derivation agrees. Does not light
S2-REPLICATE-DISAGREE or O-IMPEDIMENT. Proves-too-much objects hold:
no break / exponent / n≥131 security transfer; 3-member agreement is
not restated as full-|F|=12 independent re-derive.

### Inference

Stage-2 package is **valid** and, together with Stages 0–1
(EV-BINSTD-93aee1 E-GATE-HOLDS), **supports** the scoped instrument
claim of H-BINSTD-b1f016 / HEUR-BINSTD-11aa69-H1 at strength
**replicated** and `claim_tier: toy`: on the Stage-0-frozen stub panels,
usable emptiness when `ord_n(2)=n−1` holds under Part-1 dual-route
census (Stages 0–1), and an independent pow-only divisor ladder
re-derives `ord_n(2)=n−1` with empty usable on the first 3 forced-
negatives in agreement with Stage 1 (Stage 2). Preferred decision:
**support** (scoped). Promote KN-FIND-643b49. Empty usable ≠ security
claim about any curve. Stage-2 coverage is the protocol's declared
first-3 members only — not a silent upgrade to full-panel independent
replication.

Official decision target: `support`; hypothesis `analyzed` → `supported`.

### Limitation

- Stage-2 independent re-derive covers only the first 3 of 12 Stage-0
  forced-negatives (`{11,13,19}`); remaining 9 F members were not
  independently re-derived under this contract.
- Stub/toy odd primes only; no transfer to a security claim about n≥131.
- Instrument / observational; `certificate.kind=none`.
- No independent validator/red-team session (PD-1); Stage 2 is the
  protocol's declared independent re-derive path within one codebase.
- Producer Stage-2 manifest originally flat; nested envelope via
  immutable `manifest_v2.yaml` schema supersession (no re-measurement).
- No break; no exponent; Amazon Bedrock not used.
