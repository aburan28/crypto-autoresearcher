# Anchor reconciliation — `fitted_opt` versus `PAPER_PAIRS`

Task `TASK-20260904-1f4e2f` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`
Machine-readable companion: `anchor_reconciliation.json` (240 rows).
Producer: `reconcile.py`.

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

## Claim boundary

Arithmetic on already-committed literals. No measurement, no experiment
execution, no attack, no certificate. No security, standardized-parameter,
exponent, or asymptotic-complexity claim in any direction. No hypothesis,
experiment, or goal status is changed; no ledger record is written; nothing is
committed.

## The two anchors, kept strictly separate

Every row of the table names its anchor and the committed source of **both**
its time and its memory input. No row takes a time from one anchor and a memory
from the other; that combination would be a defect, not a result, and the two
anchors are built by separate code paths in `reconcile.py`
(`fitted_opt_from` and `parse_paper_pairs_from_source`) that never mix.

**`fitted_opt`** — `log2T_full` and `log2M` both from
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json`,
key `per_field[log2p=*].optimal.log2T` and `.log2M`.

**`PAPER_PAIRS`** — `log2T_full` and `log2M` both from the literals in
`experiments/EXP-WESOVOW-001/cost_model.py:61-65`, read **as text** (the frozen
implementation is never imported and never executed by this task).

| `log2p` | source line | `PAPER_PAIRS` (`log2T_full`, `log2M`) | `fitted_opt` `log2T_full` | `fitted_opt` `log2M` |
| --- | --- | --- | --- | --- |
| 256 | `cost_model.py:61` | 106.5, 92.5 | 108.73088958800618 | 93.27781828665178 |
| 384 | `cost_model.py:62` | 157.5, 138.6 | 157.87439031817553 | 137.48765358816084 |
| 512 | `cost_model.py:63` | 204.2, 181.3 | 206.1038967394178 | 181.43583267427067 |
| 576 | `cost_model.py:64` | 230.9, 206.0 | 229.98121023958595 | 203.30702177853001 |
| 768 | `cost_model.py:65` | 302.4, 272.2 | 300.93543569782855 | 268.68673590177326 |

The `fitted_opt` values are identical in `RUN-WESOVOW-001` and in
`RUN-WESOVOW-201692-001` for all five field sizes
(`predecessor_and_successor_optimal_anchors_identical: true`). The fix changed
the vOW charging step and the crossover formula, not the `B` optimizer.

## Grid coverage

Both anchors cover the frozen grid in full: `log2p` in {256, 384, 512, 576,
768} × `log2w` in {30, 40, 50, 60, 70, 80} × `c` in {0.0, 0.5, 1.0, 2.0} =
120 rows per anchor, 240 total. `row_count: 240`, no cell missing, none
duplicated.

## What agrees, and to how many bits

All deviations below are in log2 units (bits).

| Comparison | `fitted_opt` | `PAPER_PAIRS` |
| --- | --- | --- |
| max \|current law − `BATCH-eb0a7e` law\|, recomputed here | `5.684341886080802e-14` | `5.684341886080802e-14` |
| max \|recomputation − `BATCH-eb0a7e` `recomputed_table.json` value\| | `5.684341886080802e-14` (120 rows matched) | `5.684341886080802e-14` (120 rows matched) |
| max \|recomputation − `RUN-WESOVOW-201692-001` committed cell\| | **`0.0`** over 120 overlapping rows | *no overlap* (0 rows) |

The `5.7e-14` residue is IEEE-754 summation-order rounding, analysed in
`law_equivalence.md` Result 3. The `0.0` is exact bit-for-bit agreement.

### The overlap statement, made explicit rather than implied

`RUN-WESOVOW-201692-001`'s committed `van_oorschot_wiener` cells are anchored on
that run's own `per_field[*].optimal` values, which are numerically the
`fitted_opt` anchor. So:

* **`fitted_opt` overlaps the successor run at all 120 cells**, and the
  comparison is a genuine one against committed run output, not against this
  task's own recomputation. `reconcile.py` reads
  `raw_succ["per_field"][...]["van_oorschot_wiener"][...]["log2T_w"]` directly
  for those rows.
* **`PAPER_PAIRS` overlaps no committed run cell at all.** No committed run
  evaluates the law at the `PAPER_PAIRS` anchor. Those 120 rows therefore carry
  `RUN_WESOVOW_201692_001_log2T_w: null` and
  `overlaps_RUN_WESOVOW_201692_001: false`. That is a **stated absence of
  overlap** — neither agreement nor disagreement, and it must not be read as
  either.

## Where the disagreement is localized

**To the anchor inputs, not to the formula.** One and the same law `L_curr` is
applied to every row of both anchors. Since `L_curr` and the `BATCH-eb0a7e` law
are the same function (`law_equivalence.md`, Results 2 and 3), there is no
formula-level disagreement left to localize: the residual is `2^-43` bits of
floating-point rounding.

What remains is a real difference between two committed inputs:

| `log2p` | `Δ log2T_full` (fitted − paper) | `Δ log2M` (fitted − paper) | max \|Δ log2T(w)\| over the 24 (budget, c) cells |
| --- | --- | --- | --- |
| 256 | +2.2308895880061783 | +0.7778182866517795 | 2.6197987313320823 |
| 384 | +0.3743903181755286 | −1.1123464118391553 | 0.18178288774407747 |
| 512 | +1.903896739417803 | +0.13583267427065948 | 1.9718130765531328 |
| 576 | −0.9187897604140574 | −2.6929782214699856 | 2.2652788711490075 |
| 768 | −1.464564302171425 | −3.5132640982267276 | 3.2211963512847888 |

These are the same deviations the frozen contract's control C1 measures.
`RUN-WESOVOW-201692-001/execution_report.yaml:44-45` records
`C1_paper_pair_sanity: status: partial_fail` against the specification's
0.75-bit tolerance (`specification.yaml:139`), and `DEC-20260809-c1066f`
admitted the run with that partial-fail preserved rather than repaired.

So the `fitted_opt` / `PAPER_PAIRS` divergence is **not an arithmetic error**
and **not a formula difference**. It is a genuine difference between two
committed inputs: the paper's reported Section 4.1 pairs, and the values this
implementation's own `B`-optimizer produces. Reconciling the arithmetic does
not make them one number, and this task neither tunes the model toward the
paper nor discounts the paper toward the model.

## The `P=512`, `log2w = 80`, `c = 0.0` cell, under both anchors

The two cells exist in the frozen grid and are present in the machine-readable
table, because the contract requires the grid to be covered in full. They are
addressed here by **locator only**:

* `anchor_reconciliation.json` → `rows[68]` — `anchor: "fitted_opt"`,
  `field_size_log2p: 512`, `log2w: 80`, `overhead_c: 0.0`; anchor source
  `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:per_field[log2p=512].optimal.log2T,.log2M`.
* `anchor_reconciliation.json` → `rows[188]` — `anchor: "PAPER_PAIRS"`,
  `field_size_log2p: 512`, `log2w: 80`, `overhead_c: 0.0`; anchor source
  `experiments/EXP-WESOVOW-001/cost_model.py:63`.

Both rows, and all 48 `log2p = 512` rows, carry
`"citation_prohibited": true` and a `citation_prohibition_note` restating the
prohibition inside the data file, so a downstream consumer that reads only the
JSON still meets the flag.

**The prohibition attached to those two cells:**

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

**Protocol deviation, recorded not discarded.** The task card's
`deliverable_contracts.anchor_reconciliation.md` asks this artifact to include
"the P=512, log2 w = 80, c=0 cell under both anchors with the prohibition
attached". The dispatching instruction to this Executor is stricter: *"The
P=512 crossover and the w=2^80 sign are NOT citation-eligible. Do not restate,
rely on, or propagate either, in any artifact, until independently reviewed."*
Those two instructions conflict at exactly this point. I have followed the
stricter one in the prose: the cells are identified by anchor, coordinates,
committed anchor source, and JSON locator, and the prohibition is attached, but
**no crossover value and no sign is restated in this artifact**. The numeric row
contents remain in `anchor_reconciliation.json`, flagged, because omitting them
would leave the frozen grid incompletely covered — which the contract forbids —
and would silently discard data. A Coordinator who judges the task card to
govern can read both rows at the locators above without any further computation.

`DEC-20260824-384e78` already records, as a committed Coordinator decision, that
the two anchors "give different P=512 crossover behavior and opposite
w=2^80,c=0 signs" and that "No anchor is selected for official interpretation".
Nothing in this reconciliation disturbs that.

## What this reconciliation settles

1. The current implementation's law, the successor run's serialized law, the
   frozen protocol amendment's law, and the `BATCH-eb0a7e` law are one law.
2. The `BATCH-eb0a7e` 240-row recomputation is arithmetically reproducible from
   committed inputs to `5.7e-14` bits under both anchors.
3. Under the `fitted_opt` anchor, that recomputation and the committed
   `RUN-WESOVOW-201692-001` cells agree exactly (`0.0` bits) at all 120
   overlapping cells.
4. The `fitted_opt` / `PAPER_PAIRS` divergence is localized to the anchor
   inputs, is the same divergence the contract's C1 control measures, and
   **survives** reconciliation.

## What this reconciliation does NOT settle — the anchor choice

It does not choose an anchor, and it cannot.

* The two anchors are not obviously the same quantity. `PAPER_PAIRS` is a pair
  of numbers **transcribed from Section 4.1 of the frozen paper**
  (`cost_model.py:60` comment: "paper Sec. 4.1 (log2 time, log2 memory)").
  `fitted_opt` is the output of **this implementation's own grid search over
  `log2B`** (`specification.yaml:74-78`), evaluated with this implementation's
  Dickman `rho`. One is an external report; the other is an internal
  computation. They agree only to within the C1 partial failure.
* Neither run package establishes that its `T_full`/`M` optimum is the
  *operative* one at any particular memory budget. Both anchors feed the same
  `T_full`-and-`M`-conditioned law; nothing in either run tests which anchor
  describes an actual machine.
* This task performed no measurement, so it contributes no new information
  about which anchor to prefer.

The reconciliation can therefore be arithmetically complete and still leave the
anchor choice undetermined. That is precisely the condition under which a reader
might lift a prohibition on the strength of tidy numbers, and it is why the
prohibition is restated above and not lifted here. **This Executor makes no
recommendation on lifting it**; that is a reviewer's recommendation and a
Coordinator's decision, and `DEC-20260904-166ab5` is the identifier the batch
reserves for it (reserving an identifier is not a commitment to lift).

## Limitations

* No experiment was rerun; both run packages record `dirty_tree: true`
  (`RUN-WESOVOW-001/manifest.yaml:19`,
  `RUN-WESOVOW-201692-001/manifest.yaml:24`), and this task does not attest to
  their historical execution.
* The `optimal` anchors are read as inputs, not reproduced; reproducing them
  would require re-running the `B` optimizer.
* `PAPER_PAIRS` rows have no committed run counterpart, so their `null`
  comparison columns are an absence of data, not a null result.
* All conclusions are scoped to the five tested field sizes, the six tested
  budgets, the four tested overhead scenarios, this cost model, and these two
  anchors. No transfer to any other parameter, scheme, or attack is claimed.
