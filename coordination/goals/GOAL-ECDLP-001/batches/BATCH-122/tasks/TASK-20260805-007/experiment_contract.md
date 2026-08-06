# Experiment Contract — Multi-Target Index Calculus with BKK Speedup
**Task:** TASK-20260805-007, BATCH-122, GOAL-ECDLP-001
**Reserved evidence:** EV-SEMAEV-7f7d22
**Status:** proposed contract — pending Coordinator approval and EXP ID allocation
**Date:** 2026-08-05

---

## 1. Hypothesis (falsifiable)

**H-MTBK.** Applying the BKK sparse-check speedup (KN-FIND-c7d31e, factor
beta = 2/(m+1) on decomposition-search cost) to a multi-target index-calculus
attack reduces the measured crossover number of targets K* by factor beta in
BOTH channels, i.e. relation collection and descent both compress by beta.

Theory prediction (from TASK-20260805-005):

```
K*(std)  = ceil( s / (1 - t) )          [s = S_rel/sqrt(N), t = T_desc/sqrt(N)]
K*(BKK)  = ceil( s*beta / (1 - t*beta) )
R_theory = K*(BKK)/K*(std) = beta * (1-t) / (1 - t*beta)
```

**Falsification criteria.** Reject if any of:

1. Median measured R = K*(BKK)/K*(std) over the dataset deviates from R_theory by
   more than 25% relative (an interaction: BKK compresses one channel but not
   the other).
2. BKK factory check is not in BOTH channels with beta factor: measured
   S_rel,BKK/S_rel,std < beta or T_desc,BKK/T_desc,std < beta.
3. In the rescue regime t in [1, (m+1)/2): BKK does NOT yield a finite K* where
   standard IC has K* = infinity. This is the decisive new capability claim of
   IDEA-0cd03f.

A measured point strictly inside the rescue regime is the pre-registered
falsifier of the algebraic model, escalated to review-breakthrough if it survives
controls (rule 10: a non-generic signal is not promoted on one run).

---

## 2. Mechanism

Multi-target IC shares one factor base F (|F| = B, threshold x < t). Relation
collection (cost S_rel, one-time) + per-target descent (cost T_desc each).
BKK speedup (KN-FIND-c7d31e) shows group-law types of a candidate m-tuple sum
in factor (m+1)/2 fewer membership tests; applies identically to harvest and
descent channels because both enumerate F^m sums.

At crypto scale the per-target per-speedup constant does not change the asymptotic
beta_1, but the cross-over under multi-target amortization DOES improve: the
preprocessing is shared over k targets and the descent is the competitive cost.
This is the mechanism under test.

---

## 3. Factors / levels

| Factor | Levels | Notes |
|---|---|---|
| Semaev arity m | 3, 4, 5 | factor beta = 2/(m+1) = {0.5, 0.4, 0.333} |
| Curves | 5 toy prime-field curves | see 6.1 |
| B exponent (|F|=B ~ p^b) | b in {0.4, 0.5, 0.6} | B chosen as nearest |F| |
| Target count k | {2, 5, 10, 25, 50} | crossover read from measurements |
| Seeds | 10 per config | deterministic, recorded |

Design: 5 curves x 3 m x 3 b x 10 seeds = 450 config-run combos, each with a
full BKK and a full no-BKK pass (controls, Section 4).

---

## 4. Controls (pre-registered)

1. **Null no-BKK baseline.** For every config, run the SAME implementation with
   the BKK sparse check disabled (single boolean flag; code otherwise identical).
   The null object has identical shape (same curve, F, targets). K*(std) from runs.
2. **Factor-base non-interference** (rule from EXP-MTIC-001): the shared F log
   table must be target-independent; measure two disjoint target batches and
   require identical collected log sets (else targets interfere, invalidating CKT).
3. **Rho baseline**: per-target Pollard rho on the same 5 curves with the same
   instances, measured once per curve (not wall-clock for s and t, field ops).
4. **Smoke/validation control**: a tiny smoke (m=3, one curve, one seed, run to
   completion) mandatory BEFORE full run; review of the raw JSON before extension.

---

## 5. Metrics

- S_rel(std), S_rel(BKK): measured total enumeration attempts / harvested
  relations (field operations), not wall clock.
- T_desc(std), T_desc(BKK): per-target, averaged at constant target set.
- K* measured: smallest k such that `k*T_desc + S_rel < k*sqrt(N)` (strict
  inequality; equality does not cross).
- R_measured = K*(BKK)/K*(std) vs. R_theory at the same (s,t) from raw metrics.

---

## 6. Instances and dataset

### 6.1 Curves
5 short-Weierstrass y^2 = x^3 + a x + b, prime p ~ 1000 (F_1009 family),
prime-order subgroup N in (p-200, p+200) (Hasse). Generated with deterministic
seeds, frozen in frozen-instances.yaml at contract. SM (SMALL totals) ensured:

- m=3: require B^3/N in [0.05, 0.8] to keep enumeration non-degenerate.
- If for some (m,b) the yield degenerates (B^m/N < 0.05 or > 0.8), drop the cell
  and record the exclusion in the run report; a dropped cell is a scoped negative,
  not evidence.

### 6.2 Frozen factor base
F = {P : x(P) in [0, t-1]}, |F| ~ B. For each (curve, b): B = round(p^b);
threshold t = smallest integer with |F| >= B. Deterministic.

---

## 7. Budgets

- Budget (wall): per config <= 600 wall seconds; total cap 48h core-hours.
- Memory cap 8 GB.
- maximum_runs per config: 1 (deterministic seeds; replicate semantics come from
  the 10-seed spread, not re-runs).
- Stopping rule: any cell exceeding 10x its expected median cost is stopped and
  its metrics recorded as "timed-out" (never synthesized into K*), per stopping
  rule rule 5 in AGENTS.md (timeouts are not evidence against the mechanism).

---

## 8. Required artifacts (complete before any run retires)

- `specification.yaml` — contract snapshot (frozen, hashes).
- `frozen-instances.yaml` — instances, curves, F, targets, seeds, SHA-256.
- `implementation.md` — code layout, algorithms, the BKK flag entry point.
- `execution-report.yaml` per config — git head + dirty state, model/policy
  provenance, exact command, stdout/stderr, machine details.
- raw JSON per config (attempt-level timings + relation counts + failure modes).
- stats table — K*(std), K*(BKK), R for every completed cell.
- `analysis.md` — the pre-registered comparison to R_theory.

---

## 9. Evidence and review plan

- Execution by Executor under policy `executor-implementation`.
- First a smoke run review (review-adversarial) — must pass before full dataset.
- After the full run, Validator checks controls (null object shape, non-
 interference, budget honesty) then Coordinator review per DEC flow.
- In the Rescue-regime cells (t > 1): results are toy-scale and claim_tier "toy".
  They are never presented as crypto-scale validation (rule 7). Promotion gate for
  the constant-factor claim only after review.
- Reserved evidence record EV-SEMAEV-7f7d22, produced on acceptance.

---

## 10. Pre-registered validation plan (the "what does this mean" section)

A. If R_measured ~ = R_theory in both the standard and rescue windows: algebraic
   model confirmed at toy scale → supports H-MT-BKK as a CONST resource in the
   multi-target attack, formalizable.
B. If R_measured > 1.25 R_theory: interaction; escalation, new mechanism record.
C. If K* rescue cells fail (no finite K*(BKK) where theory predicts): BKK factor
   does not apply to descent in multi-target; scoped negative, revisit Theorem
   applicability.
D. No promotion inside C (toy again); any numeric signal is a toy-xscaled signal.

---

## 11. Coordination notes

- Contract produced under TASK-20260805-007 (Coordinator-authored; subagent
  returned no artifact).
- References: KN-FIND-c7d31e (BKK theorem), KN-FIND-2a8b7e (empirical formula),
  EXP-MTIC-001 (multi-target framework and controls), EXP-SEMAEV-001/002
  (Semaev pipeline), DEC-20260805-364e9e (approval of the direction).
- Status for Coordinator: `proposed`. RD to review and grant EXP ID.