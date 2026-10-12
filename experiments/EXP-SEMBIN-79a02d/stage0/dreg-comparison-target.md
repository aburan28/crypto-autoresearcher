# EXP-SEMBIN-79a02d — Stage 0: verbatim DREG rank-comparison target

Frozen before Stage 1 (see `stage0/FREEZE.sha256`). Quotations are verbatim,
copied from the files at repository HEAD `dd387eed33ba3a5e4f08adc49a4d591e595c37fb`,
with file:line.

## A. The d_reg "full rank" comparison (what C3 is about)

`experiments/EXP-DREG-001/specification.yaml:47`

```
      - d_reg(n) per system (first D at which full rank is reached), >=8 R
```

`experiments/EXP-DREG-001/analysis.md:122-126`

```
- Success clause (i): d_reg(sem) < d_reg(null) at any n — **not evaluable**: no
  past-wall d_reg measured; d_reg(n) at D=5 is >5 for sem at n=15,18 (rank
  69,073 < 74,880 = nrows; 143,882 < 152,532) and >5 for the null (70,935 <
  74,880; plateau at pred). d_reg by the "full rank" definition was not reached
  at D=5 in any measured cell.
```

Reading (mechanical): the DREG "full rank" target that `rank` is compared
against for `d_reg` is **nrows** (`74,880 = nrows`). It is not the
degree-exactly-D monomial count. → The C3 Stage-0 clause ("comparison target
is nrows") is satisfied by the text; the Stage-0 branch of O-C3-FALSE does
not fire.

## B. What the instrument code itself compares (recorded for completeness)

`src/h012c_block_m4ri.py:316-319`

```
        res = {"status": "completed_valid", "which": which,
               "n": n, "ti": ti, "d": st["d"], "nb": st["nb"],
               "nrows": st["nrows"], "ncols": st["ncols"], "pred": st["pred"],
               "rank": st["rank_acc"], "deficit": st["pred"] - st["rank_acc"],
```

`src/h012c_block_m4ri.py:240` and `:245`

```
        pred, HF = semireg_rank_pred(eq_degs, nb, D)
```
```
              "nrows": nrows, "ncols": ncols, "pred": int(pred[D]),
```

Reading: the code's only explicit comparison is `deficit = pred[D] - rank`
against the semi-regular Hilbert-series prediction (`src/h012_peel_rank.py:50-67`),
and it emits no degree. Neither `nrows` nor a degree-exactly-D monomial count
appears in a comparison in the code. This is recorded as an observation for
the reviewers; under the frozen falsification text ("compares rank against
the degree-exactly-D monomial count ... rather than nrows") it does not fire
O-C3-FALSE, because the comparison is against neither.

## C. Row construction the nrows refers to

`src/macaulay_export.py:24-41` (rows = nonzero products m·f, deg m <= D - deg f;
columns = occurring monomials). Reproduced in this experiment's §1(iv)
definition.
