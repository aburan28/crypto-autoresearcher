# TASK-20260722-014 — adversarial notes on frontier-B certificate contract

## Scope

Independent review of the immutable TASK-20260722-012 package archived by
TASK-20260722-013 at commit `9df2118`. This note reconstructs attack points
against the schema; it does not execute controls or authorize an experiment.

## Snapshot and runtime gates

- Recomputed producer artifact SHA-256 values match the snapshot receipt and
  the Git blobs at `9df2118`.
- Producer inference metadata matches DEC-20260722-004 (`research-sol-max` →
  `gpt-5.6-sol-high`, `fallback_used: true`).
- This review session used an auditable Grok fallback after Sol and Claude Task
  API limits (`DEC-20260723-001`); equivalence to `review-xhigh` is not claimed.

## Adversarial reconstructions attempted

### 1. Omitted attempt via post-hoc IDs

If attempt IDs are minted only at receipt time, an omitted attempt is
invisible. The contract defeats this by requiring a Coordinator-verified
pre-execution schedule seal and set/cardinality/multiplicity equality against
that seal. Residual risk: operational failure to run the seal gate before
activation — named as a scoped no-go, not silently tolerated.

### 2. Successful-only denominators

Charging only `RELATION_VALID` attempts understates cost. The contract keeps
every schedule node (including `NOT_ACTIVATED`, invalid, timeout, and
infrastructure terminals) in the bijection and resource totals, while rank
credit requires independent row verification and `rank_increment = 1`.

### 3. Misread of `r/p_L`

Under IID Bernoulli yield with `p >= p_L > 0`, `E[N_r] = r/p <= r/p_L`.
So `r/p_L` is an **upper** bound on conditional expected trials, not a lower
bound and not a high-probability budget. The contract forbids `ceil(r/p_L)`
and uses the binomial / negative-binomial tail at declared `alpha_tail`.
Symbolic recomputation agrees with the derivation note.

### 4. State-dependent rank yield

Incremental-rank success probability can drift with current matrix rank or
adaptive sources. The contract's fixed within-stratum IID model would then be
false. The specified response is to invalidate the finite probability subgate
only, not to invent a sequential model under version 1 — acceptable for PASS
on schema honesty; a later protocol must defend or drop that subgate.

### 5. Illicit scalar cost

Summing CPU, wall, bytes, and group operations into one score can hide
parallelism or memory. The contract sets `no_scalarization: true`, separates
additive vs non-additive coordinates, uses interval-union wall measure, and
forbids summing peaks. Shared-work double-count and unowned shared work are
fatal controls.

### 6. Certificate/row and wrong-field rank cheats

A valid group equality with a row from different summands, or producer rank
over a different field, must earn zero rank. The contract requires independent
coefficient derivation, schema-bound row hashes, and an independent
elimination path — with planted controls for both cheats.

### 7. Claim inflation

The package repeatedly bounds itself to toy conservation. No route in the
schema upgrades a passing certificate into an ECDLP attack improvement,
lower bound, or breakthrough.

## Non-blocking residuals

1. No concrete public fixture or sealed schedule instance is in the package.
2. Independent verifier binary/artifact hash is required by the campaign
   certificate but not yet pinned.
3. `group_operations_by_declared_type` needs an explicit frozen type
   vocabulary inside each schedule.

These residuals motivate the single next action (protocol design), not a
schema REVISE.

## Verdict

`PASS` — prior frontier-B REVISE obligations are discharged at theory/schema
level. Authorize no implementation or experiment.
