# EXP-MONO-4e6faa implementation notes

## Provenance

`implementation/run_h_minus_stress.py` was left by a PRIOR executor session
that was interrupted mid-work by an infrastructure rate-limit (an
infrastructure failure, not a math or logic problem -- no run had yet been
recorded, so nothing about H-MONO-d4c511 or IDEA-20260904-4f614a is affected).
This session read the frozen contract chain (task card, specification, the
idea record's own D3 formulas, the hypothesis record), read the partial
script in full, fixed the one disclosed defect, ran it, and produced the run
package. No other line of the inherited script was altered.

## The one defect: dead `xcheck` block in `stage_1()`

The inherited script contained:

```python
xcheck = {"n": 0, "mismatch": 0}
...
if n_points % 5000 == 1 and xcheck["n"] < 400:
    xcheck["n"] += 1
    alt = RC.qe_from_resultant(
        s3tab, None, RC.to_fp([t1], p) if False else t1, t2, t3) \
        if False else None
    if alt is not None and RC.pnorm(alt, p) != qe:
        xcheck["mismatch"] += 1
```

`if False else None` made `alt` always `None`, so the intended cross-check
against `RC.qe_from_resultant` never executed anything, and `xcheck` was
never even included in `stage_1`'s returned dict. This does not affect the
correctness of the actual classification (which uses only
`RC.qe_from_sym` + `UC.classify_fibre`, both already independently verified
in EXP-MONO-0e6e8f and EXP-MONO-815525's own prior review cycles), but it is
dead weight that claims a cross-check happens when it does not.

### Investigation

Read `RC.qe_from_resultant`'s and `RC.compile_s3`'s actual signatures and
their one existing call site in `run_census.py` (its own Stage-0 check `(c)`,
lines ~628-674):

```python
def qe_from_resultant(s3tab, F, X1, X2, X3):
    """Q_e(T) via an INDEPENDENT runtime elimination: Res_U(S_3(x1,x2,U),
    S_3(x3,T,U)) as a 4x4 Sylvester determinant over F_{p^3}[T]."""
```

called as `qe_from_resultant(s3tab, F, X1, X2, X3)` where `F = RC.F3(p, e1,
e2, e3)` (a class implementing `F_p[X]/(g)` arithmetic, `g = X^3 - e1 X^2 +
e2 X - e3`) and `X1, X2, X3` are elements of that ring (3-tuples of `F_p`
coefficients). `run_census.py`'s own usage always calls this with `g`
**irreducible** (it is probing the g-irreducible / ordered-base stratum),
so `F` is genuinely a field there (`F_{p^3}`) and `X1, X2, X3` are the three
Frobenius-conjugate roots of `g`.

On EXP-MONO-4e6faa's own stratum, `g` always **splits** into three distinct
`F_p`-rational roots `t1, t2, t3` (that is the whole point of the
distinct-split stratum) -- `g` is never irreducible here, so `RC.F3(p, e1,
e2, e3)` does not construct a field. However, `RC.F3.mul` only invokes its
degree-3/4 reduction rule (`self.r3`, `self.r4`) when a factor has a nonzero
coefficient in the degree-1 or degree-2 slot of its 3-tuple representation.
Embedding a rational root `t` as the degree-0 tuple `(t, 0, 0)` keeps every
product of such tuples at degree 0 as well (`RC.F3.mul((t,0,0),(t,0,0))`
computes `c0 = t*t`, all other `c_i = 0`, output `(t*t % p, 0, 0)`), so the
reduction rule is never triggered and the "ring" arithmetic on these
elements is exactly ordinary `F_p` arithmetic. This makes the elimination in
`RC.qe_from_resultant` a genuinely independent computation on this stratum
too, not a tautology or type error.

**Verification before wiring it in**: a standalone throwaway script (not part
of the archived run) computed, on a Z=3 curve at p=101 (A=1, B=1), `qe` via
`RC.qe_from_sym` and the resultant path via `RC.F3(p,e1,e2,e3)` +
`RC.qe_from_resultant(s3tab, F, (t1,0,0), (t2,0,0), (t3,0,0))` +
`RC.to_fp(...)`, sampled every 3000th of the 152096 base points (51
samples), with 0 mismatches and 0 non-rational results. This confirmed the
wiring is correct before it was committed to the archived script.

### Fix applied (option (a): wire it correctly)

```python
if n_points % 5000 == 1 and xcheck["n"] < 400:
    xcheck["n"] += 1
    F = RC.F3(p, e1, e2, e3)
    X1, X2, X3 = (t1, 0, 0), (t2, 0, 0), (t3, 0, 0)
    alt = RC.qe_from_resultant(s3tab, F, X1, X2, X3)
    alt_fp = RC.to_fp(alt, p)
    if alt_fp is None:
        xcheck["non_rational"] += 1
        xcheck["mismatches"].append(
            {"e": [e1, e2, e3], "reason": "resultant_not_Fp_rational"})
    elif RC.pnorm(alt_fp, p) != qe:
        xcheck["mismatch"] += 1
        xcheck["mismatches"].append(
            {"e": [e1, e2, e3], "fast": qe, "resultant": RC.pnorm(alt_fp, p)})
```

`xcheck` is now included in `stage_1`'s returned dict as
`resultant_crosscheck`, and its summary line is logged to stdout. On the
archived run this sampled 31 base points (every 5000th of 152096, capped at
400) and found 0 mismatches and 0 non-rational results -- `RC.qe_from_sym`
and `RC.qe_from_resultant` agree on every sampled point.

No other change was made to `run_h_minus_stress.py`. `UC.classify_fibre` and
`RC.qe_from_sym` (the two functions actually load-bearing for the reported
five-class counts and Stage-2 residuals) were not touched, and neither prior
file (`EXP-MONO-0e6e8f/implementation/run_uncond_census.py`,
`EXP-MONO-815525/implementation/run_census.py`) was modified.

## Execution

Run 13.2s wall / 13.2s CPU / ~23MB peak RSS -- far inside the 900s/900s/128MiB
budget. Executed twice from a clean shell (plus a throwaway sanity check
during the fix's verification, not archived); all runs produced identical
mathematical output (curve, class counts, resultant cross-check, and R1/R2/R3),
differing only in the timing/RSS fields, as expected. See
`runs/RUN-MONO-4e6faa-1/` for the archived execution's full artifacts.
