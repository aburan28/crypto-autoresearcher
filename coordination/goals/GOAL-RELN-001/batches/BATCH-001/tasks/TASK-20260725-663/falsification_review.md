# TASK-20260725-663 falsification review

## Verdict

**PASS**

Reviewed only Coordinator snapshot `TASK-20260725-662` at commit
`7efaf655b540c13408fa669860ff8acf3da4d453` (parent
`2d53e2ff4657ec69148f1994b2ed92bd97c78add`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the two producer artifacts,
and producer SHA-256 digests match the receipt `source_path_sha256` map and
the dispatch-queue archive digests. The receipt still shows
`pending_post_commit` with null commit metadata; Git checks bind the review.
Working-tree-only producer edits were not treated as durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`, independent session. Equivalence to `review-xhigh` is
not claimed.

No measurement, implementation, or experiment is authorized by this PASS.

## What was attacked

Attempt to falsify that the BATCH-001 decomposition-probability protocol is
honest on:

1. Cost honesty of `p_exist` vs charged `p_solve`
2. KN-LIT-009 heuristics kept `reported` only
3. ICEX feed only via charged Clopper-Pearson `p_L` (`declared_p_lower_solve`)
4. Present-tense non-authorization (PASS ≠ auto-execution)

## Snapshot hash verification

| Path | Receipt digest | Git blob at `7efaf655b540` |
| --- | --- | --- |
| `decomp_probability_protocol.yaml` | `500144fe117e9257d03f7b80016b59abcac0bf475b621ddcc4aaa2879b0e4362` | match |
| `protocol_design_note.md` | `f12bc3d79ae9761e6245a56b4bed2533218467526df45a04f4ddcac4a46bf950` | match |
| `snapshot-receipt.json` | `bfecec7c5074eb9e616d9068c2b2b49e1c9b3096258501e24e1a41c8d0951462` | match |

## Axis results

### Cost honesty (`p_exist` vs `p_solve`) — not falsified

Dual metrics survive: `Y_exist` (toy enumeration oracle for mathematical
existence; not free ICEX supply) vs `Y_solve` (charged algebraic solver within
budget; ICEX pin). Both require independently re-verified decomposition
certificates. Forbidden paths include oracle-as-ICEX, enumeration-only counted
as `p_solve`, and omitting failed Groebner attempts from the resource vector.
`CTRL-ORACLE-SOLVE-SEPARATION` and `STOP-ORACLE-LEAK` reject `p_exist`-only
packages. Censored timeouts contribute `Y_solve=0` still in `N` (cost, not
existence refutation). Five named stages remain required (LA/descent may be
`zero` / `not_applicable` for pure calibration, not silently dropped).

**Residual (nonblocking):** seal oracle-enumeration wall-time as separate audit
overhead and freeze Semaev/oracle→stage ownership at schedule seal.

### KN-LIT-009 reported-only — not falsified

`contested_heuristics.status: reported_not_established`; `HEUR-SEMAEV-2015-4.3`
is a reporting reference with explicit forbidden uses; `P_reported` may not be
labeled established; prohibited claims block asymptotic validation and
`α<1/2`. `RULE-HEUR-TRACK` upgrades residual metadata only to
`measured_at_toy_scope` per cell — never established complexity.
`STOP-HEURISTIC-OVERCLAIM` / `CTRL-REPORTED-LABEL` present. Novelty correctly
`adaptation` vs KN-LIT-009 / KN-LIT-025; prior EV-SEMAEV-001 3/6 is correctly
labeled uncontrolled confound.

### ICEX feed via charged Clopper-Pearson `p_L` — not falsified

`p_L_source_for_ICEX: declared_p_lower_solve` (one-sided Clopper-Pearson on
`p_solve`; `0` if `x_solve=0`); `ceil(r/p_L)` forbidden (`STOP-NO-CEIL-RP`).
ICEX package forbids presenting `p_exist` as charged relation probability,
established KN-LIT-009 exponents, `ceil(r/p_L)`, and crypto extrapolation.
Outcome packages are measured `p_solve_L` ladder / heuristic rejected at toy /
scoped no-go. Aligns with certificate-contract `probability_gate` lower-bound
method.

**Residual (nonblocking):** seal `alpha_estimation` (and `alpha_tail` if a
finite-tail claim is made) in the future schedule.

### Present-tense non-authorization — not falsified

`status: review_only_design`; authorization text; `activation_blocked_until`
(null verifier hash, unsealed schedule, missing separate Coordinator ledger
authorization, open ECDLP residuals, etc.); `post_pass_executor_gate` states
review PASS only allows scheduling a later executor task. Verifier hash is
null by construction. No runs authorized now.

### Baseline fairness — not falsified (scoped)

Pollard-rho / BSGS are not owed as primary controls on a relation-supply
probability calibration card; end-to-end ICEX comparison remains downstream
with G4 `C_decomp`. Closest specialized baselines are Semaev 2015 §4.3
(reported heuristic) and PKM 2016 / KN-TECH-003 constructions; matching them
is adaptation, not novelty.

## Nonblocking residuals (do not flip PASS)

1. **Absolute tolerance 0.05** can vacuously match rare-event cells — prefer
   CI-overlap or relative tolerance at seal; does not change the ICEX pin.
2. **Heuristic K vs signed-sum `Y_exist`** — pin the exact `P_reported`
   evaluation convention before `RULE-HEUR-TRACK` adjudication.
3. **Deferred bytes / alpha / PKM** — fixtures, schedules, verifier hash, and
   PKM literature fixture remain hard-gated; do not invent PKM maps or reuse
   the ECDLP alignment fixture as a RELN ladder cell.
4. **Solver confounder** — sympy Buchberger vs F4 can widen solve-gap; that is
   what `H-SOLVE-GAP` / charged `p_solve` are for.

## Overclaim check

No breakthrough, attack improvement, lower bound, crypto-scale relevance,
fallback-equivalence, or KN-LIT-009-established claim was found.
`PROTOCOL_COMPLETE_REVIEW_REQUIRED` is scoped to review-only design
completeness, not executable readiness.

## Narrowest supported statement

At snapshot `7efaf655b540`, TASK-20260725-661 specifies a review-only toy
prime-field `P(decomp)` versus `B` protocol with dual certificate-backed
metrics, Clopper-Pearson `declared_p_lower_solve` as the sole ICEX
relation-supply pin, KN-LIT-009 heuristics kept reported, and hard activation
gates. It authorizes no runs and does not establish Semaev 2015 complexity
claims.

## Next concrete action

Coordinator may ledger-archive this PASS via `TASK-20260725-664`. Do not admit
implementation until a separate ledger authorization exists; keep activation
failing closed while verifier hash, fixtures, sealed schedules (with
`alpha_estimation` and heuristic-K pin), and ECDLP residuals remain unset.
