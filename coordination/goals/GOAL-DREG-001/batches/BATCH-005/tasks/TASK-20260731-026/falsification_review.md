# Falsification review — TASK-20260731-026 (CTRL-B admission)

**Verdict: PASS** (`RT-20260731-013`)

Independent Red Team review of producer snapshot `TASK-20260731-025` commit
`2f7771fa0124cca31ef446fbec6aefc5b64a52d7`. Preferred policy `review-xhigh`
unavailable; resolved `cursor-grok-4.5-high-fast` with `fallback_used: true`
under `AMEND-PATH-001-001`.

## Critical anomaly

Executor reports `deficit_genuine=17947` while keeping `raw_headline_value=17947`
labeled `quarantined_confounded`, with `rank_null_restricted=156520`.

This is **not** automatic FAIL. The two quantities share a number only when
`rank(null|sem_support) = sr_pred`. That is exactly the upper endpoint of the
preregistered interval `[1931, 17947]`.

| Quantity | Formula | Status |
| --- | --- | --- |
| raw headline | `sr_pred − rank_sem` | still `quarantined_confounded` |
| deficit_genuine | `rank(null\|sem_support) − 138573` | admitted after support alignment |

Arithmetic check: `156520 − 138573 = 17947`. Formulas remain distinct; Q4 allows
structural citation of `17947` only with `structural_metric_id=deficit_genuine`.

## Attempts to falsify

### 1. Support-gap confound reopened?

**Failed to falsify (confound stays closed).**

- Independent regenerate-and-match rebuilt sem/null from `(n=12,t=3,ti=0,seed=2026)`.
- System hashes matched CTRL-A pins (`c47d17c3…`, `f2f61073…`).
- Recomputed set digests matched the receipt exactly:
  - `restricted_support_hash=8a1bf796ccb340181af0c78920e9ebc9d527743d87d6053333ed3d4cbb7bae17`
  - `deleted_set_hash=a0203e81cd0947aea405bdb7c7ae98b2ddd60c970b96b1a7d2a5caf4b5d6809b`
- `deleted = null \\ sem` with degree histogram `{6: 16016}`; `kept == sem`
  (`174035` columns). Ncols-only mutation is blocked.

### 2. Quarantine honesty / smuggling raw under a new name?

**Failed to falsify.**

Receipt keeps `raw_headline_status: quarantined_confounded` and does not set
`structural_metric_id` to `deficit_vs_sr_pred` / `raw_deficit`. Claim boundary
text states citation is allowed only as admitted `deficit_genuine`. Q1/Q2/Q4
field checks are coherent with the protocol machine.

### 3. Instrumentally fake restriction (metadata 174035, ranked full null)?

**Failed to falsify on available artifacts.**

- Scratch restricted pickle `sha256=a1fb380a…` matches receipt; differs from full
  null `9cb27677…` (nnz `5468179` vs `5768183`).
- `kept_idx` partitions `190051` into `174035` kept + `16016` deleted;
  `restriction_sha256` matches; every restricted column equals the corresponding
  full-null column (0 mismatches).
- Chunk coverage ends at `174035`, not `190051`; final unit spent ~58s reduce
  with `k=0` (real work, not a skip-to-sr_pred).

### 4. Sibling-worktree pickle undermines rebuild-and-match?

**Residual only; not REVISE.**

Protocol permits reusing the d6-null adjacency pickle. Executor claimed bytewise
rebuild identity; Red Team verified pickle hashes and column-subset identity.
Pickle bytes remain outside the Git snapshot (sibling/scratch paths).

### 5. Claim boundary overreach?

**Failed to falsify.** Receipt marks `is_d_reg_theorem=false`,
`is_crypto_scale=false`, cell-only structural citation.

## What remains open (nonblocking)

1. **Narrative debt:** BATCH-002 informal “genuine signal is O(10³)” / “~89% is
   support gap” was an envelope, not a hard prediction. Coordinator synthesis
   must supersede that expectation when citing admitted `deficit_genuine=17947`.
2. **Rank not re-executed here:** No second full chunked rank (~2300s). Optional
   Validator re-rank or one-column deletion mutation if stronger certainty is
   needed before ledger promotion.
3. **Archive receipt metadata** still shows `pending_post_commit` / null
   `commit_sha`; durable binding used Git commit `2f7771fa` (same pattern as
   prior PASS reviews).

## Narrowest supported statement

For the single frozen cell `(n=12,t=3,ti=0,seed=2026,D=6)`, the admitted CTRL-B
receipt’s measured `rank(null|sem_support)=156520` yields
`deficit_genuine=17947` under support alignment, with independently regenerated
set hashes. The formula `sr_pred−rank_sem` remains quarantined even though it
equals that number. Not a `d_reg` theorem; not crypto-scale; not an automatic
`H-DREG-001` status change.

## Next concrete action

Coordinator archive task `TASK-20260731-027` may accept this PASS. If promoting,
cite `deficit_genuine=17947` from the admitted receipt, keep raw headline
quarantined, and correct the BATCH-002 O(10³) informal expectation for this cell.
