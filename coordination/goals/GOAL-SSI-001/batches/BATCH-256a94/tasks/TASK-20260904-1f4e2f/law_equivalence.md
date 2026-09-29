# Law equivalence — three statements of the vOW charging law

Task `TASK-20260904-1f4e2f` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

## Claim boundary

Algebra and floating-point arithmetic on committed formula statements. No
security, standardized-parameter, exponent, or asymptotic-complexity claim in
any direction. No status change, no ledger record, no commit.

## The three statements

All in the frozen contract's log2 units, with `ov := c*sqrt(log2p)`.

**L_pred** — the predecessor law, serialized at
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:13` as
`"T_full / sqrt(min(w, M))"` and executed at `cost_model.py:270` of blob
`96e77f9f5` (commit `8c5188b90`, and also the state at `bd47a3f5c`):

```
log2T_pred(w) = log2T_full - 0.5*min(log2w, log2M) + ov
```

**L_curr** — the law carried by the current committed
`experiments/EXP-WESOVOW-001/cost_model.py`, serialized at `:239` as
`"T(w) = T_full * sqrt(M / min(w, M))"`, executed at `:273-275`, and serialized
identically at
`runs/RUN-WESOVOW-201692-001/raw-result.json:13`:

```
log2T_curr(w) = log2T_full + 0.5*max(0, log2M - log2w) + ov
```

**L_eb0a7e** — the law derived independently in
`coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py`,
function `corrected_law`:

```python
    overhead_bits = overhead_c * math.sqrt(log2p)
    memory_penalty = 0.5 * max(0.0, log2_m - log2_w)
    return log2_t_full + overhead_bits + memory_penalty
```

i.e.

```
log2T_eb(w) = log2T_full + ov + 0.5*max(0, log2M - log2w)
```

## Result 1 — L_curr's serialized text and its executable expression agree

`T(w) = T_full * sqrt(M / min(w, M))` gives, in log2,

```
log2T_full + 0.5*(log2M - min(log2w, log2M))
```

and for all real `log2w, log2M`,
`log2M - min(log2w, log2M) = max(0, log2M - log2w)`
(if `log2w <= log2M` both sides are `log2M - log2w`; otherwise both are `0`).
So `cost_model.py:239` and `cost_model.py:273-275` state the same function.
**Exact identity, no tolerance involved.**

The same argument applies verbatim to the amendment's own two statements at
`TASK-20260809-ef3e58/protocol_amendment.yaml`
(`linear_law: 'T(w) = T_full * sqrt(M / min(w, M))'` and
`log2_law: log2(T(w)) = log2(T_full) + 0.5*max(0, log2(M) - log2(w)) + overhead_bits`),
so the frozen amendment, the implementation and the successor run all state one
law.

## Result 2 — L_curr and L_eb0a7e are the same function

Both are `log2T_full + ov + 0.5*max(0, log2M - log2w)`. They differ **only in
the order in which three real numbers are added**:

* `L_curr`: `(log2T_full + penalty) + ov`
* `L_eb0a7e`: `(log2T_full + ov) + penalty`

Over the reals, addition is associative and commutative, so the two are
**algebraically identical, everywhere, with no restriction on `w` relative to
`M`** — including the clamp region `w > M`, where both reduce to
`log2T_full + ov` because the shared `max(0, ·)` clamp is the same clamp.

There is no min/max clamp difference to find: `L_curr` and `L_eb0a7e` use the
identical `max(0.0, log2M - log2w)` expression. That was the boundary case
worth suspecting, and it is not present.

## Result 3 — the algebra is confirmed numerically, including at the clamp

`reconcile.py` implements `law_curr` and `law_eb0a7e` as **separate functions**
so the claim is tested rather than assumed by shared code, and evaluates both
over the entire frozen grid under both anchors (240 rows):

* maximum `|L_curr - L_eb0a7e|`, **fitted_opt anchor**: `5.684341886080802e-14`
  bits;
* maximum `|L_curr - L_eb0a7e|`, **PAPER_PAIRS anchor**: `5.684341886080802e-14`
  bits;
* 76 of 240 rows show a non-zero difference; all 240 are below `2^-43` bits.

The largest single difference is at `anchor=fitted_opt, log2p=512, log2w=30,
c=0.5`: `293.13552157553784` versus `293.1355215755379`, difference
`-5.684341886080802e-14` bits. That is one unit in the last place of an IEEE-754
double near `2^8.2`, and it is exactly the residue predicted by Result 2: the
two implementations sum the same three addends in different orders, and
floating-point addition is not associative. It is a rounding artifact of the
evaluation, not a difference between the laws.

Boundary cases checked explicitly, not skipped:

| Case | Where checked | Outcome |
| --- | --- | --- |
| `w > M` (`log2w = log2M + 1`) | RG-4 cap rows, both anchors, all 5 fields × 4 `c` | both laws give `log2T_full + ov`; deviation `<= 1e-12` |
| `w = M` exactly | RG-4 cap rows, both anchors, all 5 fields × 4 `c` | `L_curr` and `L_eb0a7e` both give `log2T_full + ov` |
| smallest budget at largest field (`log2w = 30`, `log2p = 768`) | grid row, both anchors | in-grid, difference at or below `5.7e-14` bits |
| largest overhead `c = 2.0` | grid rows, both anchors | in-grid, difference at or below `5.7e-14` bits |

## Result 4 — L_pred is a different law, and by how much

`L_curr(w) - L_pred(w) = 0.5*max(0, log2M - log2w) + 0.5*min(log2w, log2M)
= 0.5*log2M` for every `w`, every `c`, and every field size — a constant
vertical offset equal to half the anchor's log2 memory. This is why the two
laws never agree at any grid cell under a real anchor, and it is what the
naming collision on `T_full` recorded in `CORR-20260806-3ac71e` amounts to
numerically.

Concrete cells, `fitted_opt` anchor, all four `c` values identically (the
offset is independent of `c`):

| `log2p` | `0.5*log2M` = `L_curr - L_pred` (bits) |
| --- | --- |
| 256 | 46.63890914332589 |
| 384 | 68.74382679408042 |
| 512 | 90.71791633713534 |
| 576 | 101.65351088926502 |
| 768 | 134.34336795088663 |

Minimum absolute separation observed over all 240 real-anchor rows: `46.25`
bits (`anchor_reconciliation.json` → `controls."RG-3".min_abs_separation_bits`).

`L_pred` also fails the frozen specification's C4: at `w = M` it returns
`log2T_full - 0.5*log2M`, i.e. the deficits tabulated above, rather than
`log2T_full`. `L_curr` and `L_eb0a7e` both satisfy C4 — with the disclosure
carried in `controls_report.md` that for these two laws C4 is algebraically
entailed rather than independently confirmed.

## Verdict

The law carried by the current committed `cost_model.py` and by
`RUN-WESOVOW-201692-001` **is the same law** as the one derived independently in
`BATCH-eb0a7e`'s `corrected_charging.py`, and the same law as the one frozen in
protocol amendment `TASK-20260809-ef3e58`. Pairwise equality is proved
algebraically above and confirmed numerically to `5.7e-14` bits over the full
frozen grid under both anchors. No `(p, log2w, c)` cell exists at which they
differ by any amount attributable to the formulas rather than to
double-precision summation order.

`L_pred` is a genuinely different law, offset by exactly `0.5*log2M` bits, and
remains correctly serialized in the immutable predecessor run.
