# Analysis — EXP-BINSTD-cf4bf7 / H-BINSTD-4a2f99

Review plan: `experiments/EXP-BINSTD-cf4bf7/review/review-plan.yaml`
(`REVIEW-BINSTD-cf4bf7-20261001`). Producer: `TASK-20261001-18804b`
(package tip at review start ~`8cb686690`; implementation commit
`b471693a4`). Evidence: `EV-BINSTD-01a202`. Decision:
`DEC-20261001-8e3e9b`.

Class: **measurement** (HOLD-N-corrected null-object instrument /
structural arithmetic + primary toy-pair construction). No ECDLP
attack, no break, no rho competitiveness claim, no exponent-moving
claim. Transfer to deployed c2pnb/c2tnb beyond disclosed ratio errors
is an explicit non-claim.

---

## Observation

**Validity.** Six runs:

| Run | Stage | Status | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-7d4512` | 0 | `completed_valid` | ladder/census/lattice `all_match=true`; role_guards_ok; ord_17(4)=4; 32 subspaces; f_null_pred=2; f_contrast_pred=7 |
| `RUN-BINSTD-847e2c` | 1 | `completed_valid` | composite #E=17180121128 l=65587; null #E=137439487532 l=230603167; both `*_ok=true`; seed 20261001 |
| `RUN-BINSTD-bfa01e` | 4 | `completed_valid` | null n=37: f=2; ord_37(2)=36; formula/cyclotomic agree; `verified=true` |
| `RUN-BINSTD-0f3a44` | 4 | `completed_valid` | contrast n=31: f=7; ord_31(2)=5; `n31_labeled_as_null=false` |
| `RUN-BINSTD-068959` | 2 | `failed_infrastructure` | `instrument_unavailable` (WDSat/CNF-XOR absent); optional; **not** H1 falsification |
| `RUN-BINSTD-c302de` | 3 | `failed_infrastructure` | skip-with-stage2; optional; **not** math evidence |

Manifest metrics agree with `raw-result.json` and with stage YAML
artifacts. `n_runs=6 ≤ maximum_runs=24`. Required Stage 0/1/4
artifacts present. Optional Stage 2/3 receipts present as
`instrument_unavailable` / skip. Certificate kind is `none` on all
runs (Stage 4 structural f-certs use `kind: none` with
`verified: true` via cyclotomic_sum_crosscheck — not
discrete_log/decomposition/key_recovery). No Bedrock. No
break/rho/exponent claim flags.

**Stage 0.** Corrected five-pair ladder with primitive-prime nulls:
pair1 (28 vs 29) +4.5pp; pair2 PRIMARY (34 vs 37) **−17.0pp**
(disclosed worst); pair3 (38 vs 37) −11.1pp; pair4 (28 vs 29)
+11.9pp; pair5 (38 vs 37) +0.2pp. Ord/f census for
`{17,29,31,37,41,53}` all_match_frozen; role_guards_ok;
`n31_labeled_as_null=false`; `n41_labeled_as_poor=false`. Lattice:
`ord_17(4)=4`, f=5, 32 stable subspaces, dims
`{0,1,4,5,8,9,12,13,16,17}`. Preregistered predictions committed
before any Stage 2 attempt.

**Stage 1.** Primary composite arm over `F_{2^{34}}` with F_4
coeffs A=0, B=1 (modulus `t^34+t^7+1`); `#E=17180121128`,
`l=65587` (probable prime), cofactor 261944. Null arm over
`F_{2^{37}}` A=0,B=1; `#E=137439487532`, `l=230603167` (probable
prime), cofactor 596. Pure-Python Hasse/BSGS+LCM+Weil order path
(no Sage/PARI); producer notes validation on n=5..12 exhaustive
before n=34/37. Worst ladder error −17.0pp disclosed beside the
primary cell.

**Stage 4.** Null certificate: f(37)=2 by formula and cyclotomic
sum; `mid_dimension_stable_V_present=false`; labeled null arm.
Contrast certificate: f(31)=7; `n31_labeled_as_null=false`;
`role: contrast_not_null`. Cross-checks agree with Stage 0 census.

**Stages 2–3 (optional).** `sat_engine_available=false`;
`instrument_unavailable.yaml` written; Stage 3 skipped with Stage 2.
Modeled WDSat conflict-ratio prior is **not** recorded as a
measurement (measured-vs-modeled separation held).

---

## Comparison

Blind re-derivation this review session (from hypothesis statement /
parameters; without reading producer implementation):

| Quantity | Predicted / frozen | Recomputed | Match |
| --- | --- | --- | --- |
| ord_17(2), f(17) | 8, 3 | 8, 3 | yes |
| ord_29(2), f(29) | 28, 2 | 28, 2 | yes |
| ord_31(2), f(31) | 5, 7 | 5, 7 | yes |
| ord_37(2), f(37) | 36, 2 | 36, 2 | yes |
| ord_41(2), f(41) | 20, 3 | 20, 3 | yes |
| ord_53(2), f(53) | 52, 2 | 52, 2 | yes |
| ord_17(4) | 4 | 4 | yes |
| ladder err pp (pairs 1–5) | +4.5/−17.0/−11.1/+11.9/+0.2 | +4.452/−17.008/−11.097/+11.852/+0.203 → disclosed 1-dp | yes (disclosed rounding) |

Stage 1 Hasse spot-check: composite `|t|=251943 ≤ 2√q=262144`;
null `|t|=534059 ≤ 2√q≈741455`. Both l divide N exactly;
Miller–Rabin (k=16, seed 0) probable-prime for both l.

Stage 4 certificates agree with the independent census recompute.
Producer Stage 0 `all_match` / Stage 4 `match_expected` flags are
consistent with this recompute.

No optional Stage 2 conflict-ratio measurement exists to compare
against HEUR-H1 thresholds (basis-blind ≈1 vs material ≤0.5).

---

## Inference

Stages 0/1/4 package is **valid**. Stage 0/4 arithmetic certifies
the HOLD-N restatement: primitive-prime null precondition
(`ord_n(2)=n-1`), primary null f(37)=2, contrast f(31)=7 with n=31
**not** a null, n=41 not a poor control, corrected ladder with
disclosed ratio errors including primary −17.0pp. This maps to
**DO-1-structural-null-confirmed** (`support_scoped_instrument`) and
the already-absorbed **DO-2** contrast reading.

Stage 1 constructs the primary toy pair needed for a later optional
WDSat arm; it does **not** by itself license a stability-pruning or
basis-blind solving-step claim (those require Stage 2/3).

Stages 2–3 absence is **DO-6-infrastructure-wdsat**: checkpoint the
optional arm; **never** `reject_scoped` on H1 from infra
(AGENTS.md rule 3).

Official decision: **support** (scoped instrument / DO-1) at
strength **preliminary**. Hypothesis `approved → supported`.
Experiment `approved → analyzed`. Keep Stage 2 optional when a
CNF-XOR/WDSat engine clears. No KN-FIND (strength below
replicated/strong). No break; no rho; no exponent.

---

## Limitation

- Toy tier only: field degrees 28–38 / census n≤53 vs deployed
  161–353 bits; no transfer beyond disclosed ratio errors.
- Primary pair-2 ratio error −17.0pp is large; cell findings are
  per-cell, not "matched-size".
- Stage 1 orders via pure-Python probable-prime path — not a
  certified factorization of group order beyond the recorded
  probable-prime + subgroup checks.
- Optional WDSat conflict-ratio and within-curve non-stable control
  unmeasured (infra); HEUR-H1 untested.
- Single unreplicated producer package; Coordinator-direct review
  without independent validator/red-team (PD-1).
- Manifests record dirty-tree at producer write.
- Certificate.kind remains `none`; no discrete_log / decomposition /
  key_recovery claim.
- Source IDEA-20260922-9e5383 claim text stays immutable/proposed;
  HOLD-N restatement lives on H-BINSTD-4a2f99 only.
