# Analysis: EXP-BINSTD-38e4ad (H-BINSTD-c3d68f)

Review plan: `experiments/EXP-BINSTD-38e4ad/review/review-plan.yaml`
(`REVIEW-BINSTD-38e4ad-20261001`), written before this analysis.
Producer: TASK-20261001-b78ef3. Distinguishing outcome target:
`DO-1-null-confirms-HOLD-S` → scoped `support` (close fixed-target
orbit-clause seam as unsound at the tested cell). No deployed-curve
break; no satisfiability-preserving claim; no exponent claim.

## Observation

**Validity (J1).** Eight run directories under `runs/`. Execution report
lists the same eight completed IDs (`RUN-BINSTD-f9fb37` Stage 0;
`RUN-BINSTD-b50f23`, `099730`, `1d2240`, `06a5e0` Stage 1;
`RUN-BINSTD-46f8b5`, `1041c0`, `a1c040` Stage 2), `invalid: []`,
`failed: []`. Every run has `manifest.yaml`, `raw-result.json`,
`environment.json`, `stdout.log`, `command.txt`. All
`status: completed_valid`, `termination_reason: completed`,
`result.valid: true`. Within `maximum_runs: 12` (8 used). No Bedrock
in manifests/environments. `certificate.kind: none` on all eight
manifests and raw results. Claim boundary fields set
`deployed_curve_break_claimed: false` and
`fixed_target_orbit_clauses_satisfiability_preserving_claimed: false`
(or equivalent stage flags). Seeds match frozen protocol:
Stage 1 `{2026100117,2026100118,2026100119,2026100120}`, Stage 2 V'
`2026100121`, ordinary `2026100122`.

Raw metrics agree with stage summaries for all Stage-1 seeds
(closure/overlap/equivariance) and Stage-2 arms
(`leave_Vprime_fraction`, ordinary equivariance, H2 counts). Protocol
deviations disclosed: empty `S(R)` excluded from closure numerator;
Stage-2 controls use `n_targets=40`; manifests `dirty=true` at write
time prior to archive.

**Stage 0 (J2).** Lattice RECOMPUTED: `n=163` mid_lane_empty=true
(`ord_163(2)=162`); `n=29` and `n=37` mid_lane_empty=true
(`ord=28`, `36`); all three `forbidden_as_measurement_cell=true`.
Toy mid-lanes present for `{17,23,31,41}` as expected. Citation
re-read notes, conversion-cost note (`O(n^2)` once), and notation lock
(`n`=degree, `m`=arity) present. No scientific group walks on deployed
curves. No break.

**Blind re-derivation (J2/J3).** From the multiplicative-order definition
alone (not producer implementation): `ord_n(2)` recovers
`{17:8, 23:11, 29:28, 31:5, 37:36, 41:20, 163:162}`; mid-lane empty
iff `ord=n-1` holds for `{29,37,163}`. Trial division confirms
`65587` prime and `2*65587=131174` matches frozen / measured group
order. Stage-1 per-seed raw/manifest/census triples agree exactly on
the three primary metrics.

**Stage 1 (J3).** Tau-stability: `pass=true`, `leave_count=0`,
`dim_V=8`, `card_V=256`, Phi_17 factorisation matches frozen.
Per-seed MEASURED (200 eligible each; `n_targets_sigma_pm_R=0` all
seeds; `A2_alarm=false`):

| seed | run | closure | overlap | equivariance |
|------|-----|---------|---------|--------------|
| 2026100117 | b50f23 | 0.0 | 0 | 1.0 |
| 2026100118 | 099730 | 0.0 | 0 | 1.0 |
| 2026100119 | 1d2240 | 0.0 | 0 | 1.0 |
| 2026100120 | 06a5e0 | 0.0 | 0 | 1.0 |

Pooled: `closure_fraction=0.0`, `conjugate_overlap=0`,
`equivariance_agreement=1.0`, `n_targets_eligible=800`.
`HEUR_H1_holds: true`; `distinguishable_outcome_id: DO-1-null-confirms-HOLD-S`.
KN-FIND-47da4e ratio band retained as MODELED/PRIOR only (no WDSat
re-run). No fixed-target satisfiability claim. No deployed break.

**Stage 2 (J4).** V' control (`RUN-BINSTD-46f8b5`):
`leave_Vprime_fraction=0.9921875` (254/256), leave among squared
solution tuples `1.0` — artifact tell that non-stable V' is not a
tau-stable window. Ordinary-curve control (`RUN-BINSTD-1041c0`,
`b=t`): `equivariance_agreement=0.0`,
`ordinary_curve_equivariance_fails=true` as predicted. H2
(`RUN-BINSTD-a1c040`): `direct_count=103`, `per_orbit_sum=103`,
`h2_count_agreement=true`; `HEUR_H2_holds: true`. H2 framed as
preprocessing-only / true-by-construction — not an exponent lever.
No break.

## Comparison

Matches DO-1-null-confirms-HOLD-S and the frozen
`preregistered_prediction`: Stage 0 empty mid-lanes on `{163,29,37}`;
Stage 1 exact null on all four seeds; Stage 2 V' leave-fraction high,
ordinary equivariance fails, H2 counts equal. Does not light DO-2
(A2 failure) or DO-3 (instrument / stability failure). Proves-too-much
objects hold polarity: V' leaves; ordinary fails; no deployed break /
satisfiability / exponent path. Blind `ord_n(2)` and `l_order`
primality agree with producer. Multi-seed Stage-1 agreement is exact
(not approximate), matching a77711 A1/A2 under exhaustive census.

## Inference

Valid Stages 0–2 package supports H-BINSTD-c3d68f's scoped HOLD-S
restatement at strength `replicated` (four independent target-draw
seeds × 200 eligible targets with identical exact null, plus Stage-2
control polarity). Decision: `support` — close the fixed-target
tau-orbit CNF-clause seam as unsound at the tested cell
(`n=17`, `m=2`, `l=8`, tau-stable `V=ker f1(tau)`). Hypothesis
`approved → supported`. Experiment `approved → analyzed`. Promote
`KN-FIND-b69b8e` for the durable scoped boundary. Does **not** support
any deployed-curve security claim, satisfiability-preserving reading of
fixed-target orbit clauses, or exponent-class movement. H2 remains
preprocessing-only. Source IDEA-20260922-2a3771 claim text stays
immutable/`proposed`; only this hypothesis carries the HOLD-S
restatement.

## Limitation

- Toy tier only (`n=17`); optional extension cells `{23,31,41}` not run.
- No independent validator/red-team session (PD-1); independence is
  Coordinator-direct with within-protocol multi-seed replication.
- Manifests dirty-at-write; Stage-2 controls use `n_targets=40` vs
  Stage-1 `200`.
- Stage 1 does not re-run WDSat; KN-FIND-47da4e band is prior only.
- Empty-lattice note on K-163 is arithmetic, not an attack measurement.
- No transfer to `n≥131` claimed.
- Amazon Bedrock unused.
