# The proves-too-much control (assigned to TASK-20260904-3a2ff5)

The argument and the instrument were run UNCHANGED against four objects whose conclusion
is KNOWN FALSE. Instrument: `experiments/EXP-PFDR-cbdefb/closure.py`, sha256
`63475db53f5d34859d638327a7082834da0b81209059d0b871bab5b4e32cfb98` (the version pinned
by runs 3-23), with the meter `harness/macaulay_fp/` at the sha256 set of
`harness/macaulay_fp/VALIDATION.md`, D_max = 7 unless stated. Scripts `ptm_objects.py`,
`ptm4_s1.py`; outputs `ptm_objects.json`, `ptm4_s1.json`. NONE of these is an experiment
run; no run record was produced (`maximum_runs: 0`).

| # | object | what is KNOWN FALSE | what the instrument did | declared failure signature | verdict |
|---|---|---|---|---|---|
| 1 | NULL-1, support-matched random generator on the digit ring, p = 4099, seeds 7 and 11, s = 2, 3, 4 | that d_lf is flat, or equals the Semaev value | d_lf = 5, 6, 7 at s = 2, 3, 4 -- exactly s + 3, RISING, on both seeds; single fall each; certified structural at s <= 3 and C1+C2 at s = 4. Semaev on the same instance: 5, 5, 6. The arms differ at s = 3 and s = 4. | "the closure must return s + 3, rising" | ABSENT -- the instrument distinguishes the null from the Semaev arm and is not flat |
| 2 | planted LATE fall: n = 10 squarefree variables, p = 4099, f1, f2 of degree 5, u, v of degree 3, h of degree 7, g = u f1 + v f2 + h of degree 8; fall at D = 8 > D_max = 7 | "certified complete at D_max = 7" | at D_max = 7: falls = [], dim V_7 = 112 against dim(I cap B_{<=7}) = 582, **C1 = false, certified = false, route "not certified", right_censored = true**. Run to D_max = 9 the true history is falls = [8], iteration count 2, dim V_8 = 627 = dim(I cap B_{<=8}). | "the certificate must NOT certify completeness at D_max = 7" | ABSENT -- the certificate refused; no false certificate |
| 3 | direct presentation at m = 2 with B = 8: ordinary ring in x_1, x_2, generators [S_3(x_1, x_2, x_R), f_V(x_1, 8), f_V(x_2, 8)], degrees [4, 8, 8] | a bounded or observed d_lf below 8 (IDEA-20260808-afe4ce's floor d_lf >= B = 8 > D_max) | no fall in (4, 7]: falls = [], `no_fall_in_window` = true, `right_censored` = true, certificate not attempted ("ordinary ring: no structural bound and no certificate") | "the closure must report right-censored / no fall in (4, 7], never a flat d_lf" | ABSENT -- reported exactly that |
| 4 | the s = 1 saturated digit systems, n = 2, four monomials, all 1200 systems in the three s = 1 runs | that a count-1 fall is an instrument fault | the tell fires on 405 Semaev/non-curve entries and 165 of 600 NULL-1 entries, and a complete cross-tabulation shows it fires EXACTLY when the system has a root (Z_size >= 1, dim W_0(3) = dim V = dim(I cap B)) and never when it does not (Z_size = 0, dim W_0 = 3 < dim V = 4, count 2). It is a perfect detector of solvability, not of a non-iterating closure. | "the tell fires for saturation, not artifact, and the reviewer must state the corrected reading" | PRESENT AS DESIGNED -- an argument that reads every count-1 fall as an instrument fault DOES prove too much; corrected reading below |

## Where the survival happens on object 4, and the corrected reading

The location is the definition of the tell, not its implementation:
`iteration_count(D) = 1` at a fall means only "multiplying the fallen rows inserted no new
pivot". At s = 1 the ring is B with n = 2 and 4 monomials, so B_{<=3} = B_{<=2} = B and at
D = 3 the entire ring is fallen; W_0(3) is the full Macaulay space {S~, a_1 S~, a_2 S~}
of dimension 3. Whenever Z is non-empty, dim(I cap B) = 4 - |Z| <= 3 = dim W_0(3), so
W_0(3) IS the ideal cap and there is nothing left to insert: count 1 by SATURATION.

CORRECTED READING, for reuse of CTRL-ITERATION-COUNT: the artifact tell is
`iteration_count = 1 AND W0_saturated = false`. `iteration_count = 1 AND
W0_saturated = true` is a saturated ring and is a correct measurement. On this package the
`W0_saturated` diagnostic is true on every invalidated entry, so no artifact was ever
present; the raw s = 1 answer (d_ff, d_lf) = (3, 3) is correct and satisfies afe4ce's
floor d_lf >= 2. Applying the frozen rule literally was right as procedure -- and it is
the rule, not the instrument, that needs the amendment. Note also that at s = 1 the rule
discards exactly the systems that HAVE a solution, which is a selection on the property
the lane is about (`r4-nulls-and-design-note.md` (e)).

## What the control licenses

Objects 1-3 give no evidence of an argument or an instrument that survives where its
conclusion is false. Object 4 identifies one argument that does -- "a count-1 fall is an
instrument fault" -- and locates it precisely. No conclusion in the package rests on that
argument in a way that changes a number (s = 1 is outside the primary fit and the raw
values are reported beside the rule-applied ones).
