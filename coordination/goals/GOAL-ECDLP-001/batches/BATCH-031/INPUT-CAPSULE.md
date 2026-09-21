# INPUT CAPSULE — TASK-20260802-201 fresh attempt

Relay this file verbatim. It is the complete authorized repository input for an
Idea Generator without filesystem access.

## Task

Determine whether any certificate-bearing isogeny-transfer control inside the
frozen H-IT-001 boundary can beat a resource- and success-matched Pollard-rho
baseline after every field DLP and end-to-end cost is charged.

Do not execute an experiment, change status, or claim closure. Allowed verdicts:

- `BEATS_RHO`
- `OBSTRUCTED_IN_SCOPE`
- `UNRESOLVED`

`OBSTRUCTED_IN_SCOPE` requires a named obstruction, argument, and redirection.
`UNRESOLVED` requires the exact missing premise or inequality and cheapest
bounded discriminator.

## Integrity and sources

Authoritative BATCH-030 ledger/review commit:
`706e5298920e50b5d813c252796c0912c43a0f4a` (short `706e52989`).

Raw run snapshot:
`62055d2965fb54fc648c76b1eb48e24aafd8b2a8`.

Sources:

- `ledger/hypotheses/H-IT-001.yaml`
- `ledger/evidence/EV-IT-002.yaml`
- `ledger/decisions/DEC-20260801-002.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/SCOPE-DECISION.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/reviews/TASK-20260801-145/validation_report.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/reviews/TASK-20260801-146/red_team_report.yaml`
- `experiments/EXP-IT-001/results/transfer_gate_report.json`
- `experiments/EXP-IT-001/results/concrete_cost_table.json`
- `experiments/EXP-IT-001/results/HEUR_ISO_1_report.json`
- `docs/inventor-protocol.md`
- `docs/target-result-profile.md`
- `AGENTS.md`

Frozen disposition: BATCH-030 is inconclusive; its run remains valid only as a
toy density package; transfer interpretation is void; H-IT-001 remains
`specified`; HEUR-ISO-1 is unmeasured; every promotion gate is open.

## Frozen mechanism and boundary

H-IT-001 studies a prime-field curve `E/F_p` with prime-order subgroup `G` of
order `N`. It asks whether an ordinary-isogeny path can transfer ECDLP to one of:

- anomalous `N=p`;
- low-embedding-degree MOV/Frey–Ruck;
- subfield/Weil-descent-friendly families.

The registered charged gate is:

> `C_path + C_special >= 0.886*sqrt(N)` with high probability for generic
> curves under HEUR-ISO-1.

Its toy falsification boundary requires at least two unplanted certificate-
bearing paths with total charged ratio below `0.7`, at 20–28 bits.

Admissibility requires:

- isogeny degree coprime to `N`;
- an actually evaluated path/composed map on the subgroup;
- a special-family solve;
- pullback/scaling to the original non-special instance;
- final verification `[k]P=Q` on that original instance.

A direct BSGS solve followed by `[k]P=Q`, without isogeny evaluation, is a
non-transfer proxy.

Structured CM or pairing-friendly curves remain outside the generic claim.
Toy analysis licenses no crypto-scale or asymptotic conclusion. H-IT-001 is
currently `claim_kind: constant_factor`.

## Frozen equations and data

Reviewer-recomputed equations:

```text
matched_rho  = 0.886 * sqrt(N_star)
matched_bsgs = 2 * ceil(sqrt(N_star))
R_xfer       = (C_path + C_special + C_pullback) / matched_rho

total expected transfer cost
  = special-set construction/sieve
  + per-attempt cost / p_success
  + special-family field DLP
  + certificate generation and pullback
  + verification
```

Also charge preprocessing, amortization, memory, data/queries, parallelism,
retries, and material hidden terms.

Persisted planted cell:

```text
C_path = 9
C_pullback = 40
matched_rho = 641.609

executed substitution:
C_special_MOV = ceil(k*log2(p)) = 22
R_xfer = (9+22+40)/641.609 = 0.1107

frozen v3 formula:
C_special_MOV = ceil(0.886*sqrt(p^k)) = 1284
R_xfer = (9+1284+40)/641.609 = 2.08

field-DLP-inclusive k=1 toy charge:
approximately 2*sqrt(N_star) = 1448
```

The reported pass therefore charged pairing evaluation while omitting the
dominant field DLP. For the only observed special family, k=1 MOV, the field
DLP alone is matched-rho scale or worse.

Other frozen observations:

- 21 unplanted cells; all censored and `certificate_pass=false`.
- No unplanted transfer was measured.
- `rho_special_by_bits={20:0,24:0,28:0}` in run notation.
- The 20/24-bit zeros apply only to selected primes `2097169` and `33554467`.
- The 28-bit zero is a 50,000-class sample; one-sided 95% upper bound is about
  `6e-5`, not an exact density law.
- `F_hit=0`, zero uncensored samples, KS/tail unavailable, and
  `rate_iso_1_pass=false`.
- HEUR-ISO-1 is unmeasured, not falsified.
- The run’s measured `p_success=0` makes its expected-cost row unbounded. This
  is not proof that the true probability is mathematically zero.
- No algorithmic time-memory tradeoff was supplied.

## Binding review findings

Validator VAL-20260801-145 and Red Team RT-20260801-146 independently found:

1. Under the frozen formula, the planted control has `R_xfer=2.08`; F2 voids
   the transfer harness.
2. The “certificate” was direct BSGS with no isogeny pullback. The planted
   two-hop walk returned to its special start, and the recovered one-hop edge
   joined two special curves.
3. The identical-shape null gate never ran (`R_null=null` on all 21 cells).
4. The null plant had `edge_ledger=[]`; recomputation was not independent.
5. Field-DLP, special-set construction, full expected cost, algorithmic memory,
   time-memory tradeoffs, `dominated_by`, and quantitative `sota_delta` were
   absent.
6. Matched rho dominates the observed transfer row in time and O(1) memory.
   This is scoped adverse accounting, not universal closure.

DEC-20260801-002 requires any later repair to provide:

- field-DLP-inclusive MOV cost or the frozen formula;
- an actual anomalous trace-1 control, not a k=1 MOV endpoint;
- genuine transfer on a non-special instance;
- a live identical-shape null and raw edge ledger;
- `dominated_by` and quantitative `sota_delta`;
- a density regime admitting `N* | p^k-1`, `k>=2`, or a trace-1 class, with
  confidence bounds;
- complete implementation archival if an experiment is later approved.

This task decides whether such an Executor repair is worth admitting. It does
not run it.

## Required derivation

For every admissible candidate family/control:

1. State the transfer map and certificate semantics.
2. Derive every cost and success-probability term; no free field DLP.
3. Compare with matched rho at the same success/resource boundary.
4. State feasible parameter inequalities, if any.
5. Audit time, memory, and data/query Pareto axes.
6. Give `dominated_by`.
7. Quantify `sota_delta`, including asymptotic-exponent delta and, where
   possible, log2 time, memory, and data/query ratios.
8. Label each statement as derivation, heuristic, observation, or conjecture.

If no candidate beats rho, name the narrow obstruction and argue it. Rejected
candidate count is not an obstruction.

## Successor requirement

For `OBSTRUCTED_IN_SCOPE`, propose one fresh exponent-first successor with:

- mechanism and structural ingredient;
- numbered predictions;
- test boundary, budget, stopping rule, and falsification criteria;
- identical-shape null and destruction parameter;
- required artifacts;
- per-attempt-cost times inverse-success bookkeeping;
- `dominated_by` and quantitative `sota_delta` against a named prior best.

It remains a proposal. Any breakthrough claim requires separate
`review-breakthrough` review at max effort.

## Binding research obligations

- Target-class work changes an asymptotic exponent or central structural
  barrier; constant-factor work is not target-class.
- Total expected cost equals per-attempt cost times inverse success probability.
- Apparent signals are artifacts until an identical-shape null distinguishes
  them.
- Closure requires a named obstruction, argument, and redirection.
- `dominated_by: null` is allowed only after checking every Pareto row.
- `sota_delta` must be quantitative.
- Toy evidence is not crypto-scale evidence.

## Returned artifacts

Return exactly four complete UTF-8 payloads and no commentary outside markers:

```text
---BEGIN ARTIFACT: feasibility-rerank.md---
[payload]
---END ARTIFACT: feasibility-rerank.md---
---BEGIN ARTIFACT: pareto-frontier.yaml---
[payload]
---END ARTIFACT: pareto-frontier.yaml---
---BEGIN ARTIFACT: successor-proposal.yaml---
[payload or explicit not_applicable record]
---END ARTIFACT: successor-proposal.yaml---
---BEGIN ARTIFACT: provenance.yaml---
[payload]
---END ARTIFACT: provenance.yaml---
```

The Coordinator writes them verbatim under
`BATCH-031/tasks/TASK-20260802-201/`.

## Provenance

```yaml
requested_policy: research-deep
runtime: codex_cli
resolution_source: explicit_codex_role_session
resolved_model_id: gpt-5.6-sol
reasoning_effort: high
model_verified: false
adapter_probe_status: not_run_backend_unavailable
runtime_binding_verified: true
fallback_allowed: false
fallback_used: false
degraded_allowed: false
degraded_requirements: []
independent_session_required: false
```

Record actual session/backend/timestamps verbatim when supplied; otherwise use
`not_reported`. Any model/effort/capability mismatch invalidates the attempt.

Prior attempt: `failed_infrastructure/tool_surface_stall`, zero artifacts,
session ID not captured, evidence effect none.
