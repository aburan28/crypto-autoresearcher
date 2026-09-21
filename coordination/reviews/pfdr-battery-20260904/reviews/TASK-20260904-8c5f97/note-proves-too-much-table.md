# proves_too_much control — the argument run unchanged against three objects
# for which its conclusion is KNOWN FALSE

Red team, TASK-20260904-8c5f97. Computations: `scripts/proves_too_much.py`
(objects 1 and 2, run through BOTH my own code and the producer's meter) and
`scripts/r3_direct_firstfall.py` (object 3). Meter version recorded in
`out/proves_too_much.json` (`meter_version_sha256`, ten files, matching
`harness/macaulay_fp/VALIDATION.md`).

The argument under test is claim (A) of IDEA-20260903-26aa81 as carried into
H-PFDR-09e1b0: *M_D over F_p is the specialization of one integer matrix family
in (A, B, x_R); its rank equals the generic rank off a set of density
deg(P_D)/p, for p not dividing the content of P_D; hence every graded invariant
is the same integer at every prime above a small threshold.*

| # | object | conclusion known false because | what the argument did | what a direct exact rank showed | failure signature |
|---|---|---|---|---|---|
| 1 | the same (2,2,3) digit system at p = 2 | every degree-4 entry has content 16, so the top form vanishes mod 2 | **PREDICTED the drop**: p = 2 divides the content of the top block (invariant factors (16), (16,16), (16) at D = 4,5,6), so the content clause fires | own code and the METER agree exactly, 24/24 draws: profiles (full, top) at D=3..6 in {[4,6,4,1]/[4,6,4,1], [5,11,14,11]/[4,6,4,1], [6,14,16,9]/[4,6,4,1], [6,15,20,15]/[4,6,4,1]}; **0 of 24 at the 2^64 profile** | **appeared as required** — the pipeline did NOT report the 2^64 profile at p = 2 |
| 1b | the same system at p = 3 | small field ⇒ ~26 of 64 cube values vanish, above the 16-zero threshold for a D = 6 full-rank drop | the argument as written **declines** (its bound 30/3 > 1 is vacuous); the sharpened criterion of the R1 note **predicts** drops | own code and the METER agree: 23 of 24 at the reference, one draw with full_rank@6 = **13** (reproduces Stage 0's 23/24 by an independent route) | **appeared** |
| 2 | multiplication by ell^2 from degree 1 to degree 3 on F_p[a_1..a_6]/(a_i^2), s = 6 > p = 3 (Wilson W_{1,3}) | 3 divides binom(3,1), so the rank is 5 < 6 = min(C(6,1), C(6,3)) | **PARTIAL SURVIVAL — this is the finding.** Read literally ("p not dividing the content of P_D", P_D a maximal minor), it declines correctly. Read as Stage 0 §4 *operationalizes* it — content of the ENTRIES, "content gcd = 1, so no prime divides the whole row … no odd prime divides any entry's content" — it concludes p-independence, which is FALSE here | measured ranks: p = 2 → 0, **p = 3 → 5**, p = 5, 7, 11, 13, 4099 → 6. Entry content is 2!, so 3 divides no entry and drops the rank anyway | **the argument survives where its conclusion is false**, and the survival is located exactly at the entry-content-for-minor-content substitution (objection RT-O2) |
| 3 | the direct presentation with B = round(p^{1/2}) (the positive control) | the matrix size grows with p, so no single integer family exists and flatness is false | **DECLINED, correctly**: row and column counts depend on p, so claim (A)'s hypothesis is absent and no p-flatness statement is derivable | first fall moved 66 (B = 64, p = 4099) → 130 (B = 128, p = 16411), reproduced independently for B ∈ {4,5,6,8,10,12,64,128}, always B + 2 with fall_dim 2 | **appeared as required** (the measured first fall moves) |

## What the control adds beyond the plan's expectation

* Object 2 is the only survival, and it is a survival of the *implemented*
  content check rather than of the written argument. The repair is a
  computation the package does not contain and I performed: the integer
  invariant factors of the top blocks are (16), (16, 16), (16), so p = 2 is the
  only prime at which the (2, 2, 3) top rank profile [1, 2, 1] fails. With that
  computation in hand the argument's conclusion for this object is safe; without
  it, the record's odd-prime exclusion rests on an insufficient check.
* Object 1 doubles as the fixed-shape p-sensitivity control that
  CTRL-POSITIVE-P-DEPENDENCE cannot provide (see the R3 note §4): the producer's
  own meter, on the sweep's own construction, returns a *different* profile at
  p = 2 and reproduces the p = 3 rank drop. The instrument is not blind to p.
