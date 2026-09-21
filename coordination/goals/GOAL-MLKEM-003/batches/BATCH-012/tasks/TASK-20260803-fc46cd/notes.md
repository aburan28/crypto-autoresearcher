# VAL-20260803-1a074b — what I re-derived

Validator notes for `TASK-20260803-fc46cd`, validating `TASK-20260803-69f3cd`
at snapshot `1cd863b1`. Terminal verdict in `report.yaml`:
**ADMISSIBLE_WITH_DEFECTS**.

Everything below is a **cost-model estimate**, not a measurement. No ML-KEM
break claim, no security proof, no FIPS 203 set affected or cleared. Rule 12
UNMET and UNWAIVED; no `EV-*` or `KN-*` status changed or proposed to change.

I did not accept the producer's transcript as proof of anything. Where I could
run it, I ran it.

---

## 0. Integrity, before any number

- `1cd863b1` reachable from `HEAD`; parent `079bdb8b` matches the snapshot
  receipt. Working tree clean.
- All **8 producer artifacts** hash-identical across four places: my working
  tree, `git show 1cd863b1:<path>`, the snapshot receipt's `source_path_sha256`,
  and the producer's own `receipt.json` `artifact_sha256`.
- Estimator `/tmp/le` at `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`, clean.
- Shim clean in git; `all.py` and `known_answer_control.py` SHA-256 both match
  the values quoted in `report.md`.
- The snapshot receipt is at `.../BATCH-012/archives/TASK-20260803-3fac41/`,
  not under `tasks/` as my brief said. Immaterial.

## 1. Step 0 control — re-run, not trusted

```
PYTHONPATH=tools/sage_free_estimator/shim:/tmp/le python3 tools/sage_free_estimator/known_answer_control.py
```

Exit 0, PASS, stdout **byte-identical** to the block quoted in `report.md`,
stderr empty. Wall clock 38.6 s vs the producer's 29.1 s — timing variance.

## 2. S1 — the headline. Reproduced, including the part that mattered most

The question I was asked to settle was not "do the numbers match" but "was the
shim genuinely off the path". I checked that from *inside* the interpreter
rather than from the command line, because the producer's own `live_probes`
show the trap: `/tmp/sagevenv/bin/python -c "import sage.all"` resolves to
**the shim** when the shim is on `PYTHONPATH` — the venv's real Sage is
shadowed. So "we used the venv python" proves nothing by itself.

My run recorded, from within the process:

```
shim_dir_on_sys_path : []
sage_all_is_shim     : false
sage.all.__file__    : /tmp/sagevenv/lib/python3.11/site-packages/sage/all.py
sage_version         : 10.8.7
```

Reading `reserve_checks.py:258` confirms the producer did the same thing
correctly — `env["PYTHONPATH"] = os.environ.get("ESTIMATOR_PATH", "/tmp/le")`
**overwrites** the inherited value rather than prepending, so the shim is gone.

**Is passagemath a real Sage, or a re-export of something shim-like?** Real.
`RR` is `sage.rings.real_mpfr.RealField_class` (MPFR, 53-bit default);
`RealField` is a `cython_function_or_method`; `find_root` comes from
`sage.numerical.optimize`; `RealDistribution` from
`sage.probability.probability_distribution`; the dependency stack carries
`cysignals`, `gmpy2`, `passagemath-flint/pari/ntl/linbox`.

The clean discriminator is `PowerSeriesRing`. Under passagemath it returns
`Power Series Ring in x over Rational Field`. Under the shim it raises
`NotImplementedError: PowerSeriesRing is not shimmed`. The shim is
`sage.all._RealField` over mpmath at 200-bit precision. **Two genuinely
independent arithmetic backends**, which is what makes the agreement mean
anything.

My six values, all exact matches to the producer's:

| set | primal_bdd | matzov |
|---|---|---|
| K-512 | 140.1994731076207 | 139.65604148085845 |
| K-768 | 200.9587149140538 | 196.36624335005874 |
| K-1024 | 270.7236234535225 | 262.3356800074737 |

Optima also match under both backends: β = 387/589/823, β′ = 391/583/804,
p = 5/4/4, t = 50/60/120, ζ = 0/20/0.

### The discrepancy I was asked to adjudicate

> summary prose says the K-512 and K-1024 matzov deltas are `0.0`;
> `results.json` records `4.155e-11` and `2.632e-11`.

**`report.md` is right. `results.json` is measuring something else under a name
that says otherwise.**

I computed both sides at full precision:

| set | shim | real Sage | **true delta** |
|---|---|---|---|
| K-512 | 139.65604148085845 | 139.65604148085845 | **0.0** |
| K-768 | 196.36624335399668 | 196.36624335005874 | **3.9379e-09** |
| K-1024 | 262.33568000747368 | 262.33568000747368 | **0.0** |

That is exactly `report.md`'s table. `results.json`'s `comparison_vs_shim`
compares Sage against `ANCHOR_MATZOV` (`reserve_checks.py:68-72`), which holds
the **rounded published** values `139.6560414809 / 196.3662433540 /
262.3356800075`. Its `delta_bits` are those anchors' rounding residue.

Root cause is an asymmetry two lines apart: `ANCHOR_PRIMAL` (`:63-67`) is stored
full-precision, `ANCHOR_MATZOV` (`:68-72`) rounded. That is why every primal
delta comes out exactly `0.0` and no matzov delta does. Nothing is fabricated —
the code computes what it says — but a field named `shim_anchor` inside a block
named `comparison_vs_shim` does not hold a shim value. **Defect D-1.** The
Coordinator's snapshot commit message propagated the mislabelled reading
("against the shim's 196.366243354 and 262.3356800075").

Does it matter? No. Every figure involved is ≤ 4e-09 bits against a 0.001-bit
statement scale.

### Coverage fact — established independently, because the producer's check failed

The producer's DEF-B (repo root six levels up instead of seven) killed their
automated version, so I did it myself:

- `EXP-MLKEM-015/implementation/reproduce_estimates.py:16` imports the
  **module-level** `dual_hybrid` (= `DualHybrid`), line 43 calls it. `matzov(`
  occurs **0** times.
- `RUN-MLKEM-015-001/raw-result.json` records `dual_fft_MATZOV_log2` =
  143.78847824788485 / 203.78786306762115 / 273.81726768503654 — the DualHybrid
  numbers — and `sage_version: 10.9`.

Confirmed: **no archived Sage run ever exercised the matzov path.**

### Is passagemath 10.8.7 a fair reference for a 10.9 number?

Adequate for the purpose, with the caveat the producer already states. I add a
corroboration the producer did not make: the archived **sagemath 10.9** run's
`primal_bdd` values are 140.1994731076207 / 200.9587149140538 /
270.7236234535225, and my **passagemath 10.8.7** run reproduces all three to
floating-point equality. So the two Sages demonstrably agree on the one
estimator path for which a 10.9 reference exists. There is no 10.9 matzov
number to compare against — that is precisely the coverage gap above — so the
matzov path is verified shim-vs-passagemath only.

Acquisition negatives independently reconfirmed: no `sage` binary, `apt-cache
policy sagemath` → `Candidate: (none)`, no conda/mamba/micromamba, no
`sagemath-standard` binary wheel. I did **not** re-run the pip source build;
its PARI/GP failure rests on the transcript alone (`gp` is genuinely absent).

## 3. S2 — arithmetic verified, and it holds

Every plane size recomputed from the declared ranges:

| set / stage | plane | points | β scanned | remainder |
|---|---|---|---|---|
| K-768 A | 27·43·7 = 8127 | 113,778 | 14 → 413–517 | **0** |
| K-768 B | 31·31·7 = 6727 | 73,997 | 11 → 565–575 | **0** |
| K-1024 A | 8127 | 121,905 | 15 → 647–759 | **0** |
| K-1024 B | 16·31·7 = **3472** | 65,968 | 19 → 799–817 | **0** |

I initially got a non-zero remainder for K-1024 stage B and had to look closer:
that stage's `k_enum` centre is **0**, so the ±15 window **clips** to 0–15 (16
values, not 31). With the correct plane the remainder is 0. The producer's
annotation already records `3472`. **All four remainder checks are 0 as
claimed.**

589 > 575 and 823 > 817, so **neither incumbent β was scanned**, and every β
actually reached lies strictly *below* its incumbent on both sets.

**Does `report.md` read stronger than the coverage supports?** Substantively,
no — this is handled well. The report says in bold that both stages truncated,
that the incumbent's own β was not reached, that S2 "does not establish global
optimality", and it repeats the limitation under "Does not survive". That is
correct scoping.

One presentational catch (**D-4**): the table's "best found" column shows
196.3662433539967 / 262.3356800074737, which are the **incumbent** values.
`results.json` says so (`best_found.source: "incumbent"`); the table does not.
Since the incumbent was never evaluated by the scan, the scan's own best must be
strictly worse — and it is not reported anywhere.

The criticism of the prior 1701-point scan is **correct**: 1701 = 21·9·9 fits
the described grid, and I measured incumbent `k_fft` = 60 (K-768) and 120
(K-1024) under both backends. Both exceed that grid's 0–40 range.

## 4. S3 — the null that ran is not the null that was needed

**NULL-1 root cause confirmed exactly.** `hasattr(NoiseDistribution,
'CenteredBinomial')` → `False`; module-level `CenteredBinomial` is at
`estimator/nd.py:296` (producer said 296 — exact); `schemes.py:22` uses it that
way. Genuine `implementation_error`, correctly diagnosed, correctly treated as
evidence in neither direction, correctly not rerun on a spent
`maximum_runs = 1`. I did not rerun it either — that would be repairing a
producer artifact.

**NULL-2 reproduced.** I recomputed 4 of 18 cells and all four match to full
float precision, including the sole negative one:

| cell | my value |
|---|---|
| ADPS16 @ 512 | 3.903481062696514 |
| **LaaMosPol14 @ 512** | **−1.6228820366036985** |
| CheNgu12 @ 512 | 76.41722361794504 |
| BDGL16 @ 1024 | 10.299859176913628 |

**Is NULL-2 a null of the right shape?** No. A null object replaces the
**object** with a structureless one of the same shape — non-Kyber LWE instances,
which is exactly what NULL-1 was. NULL-2 keeps the same three Kyber instances
and the same two cost functions and varies only the reduction cost model. That
is a frame-sensitivity sweep.

And read as the inventor protocol directs, NULL-2 points **toward** artifact,
not away: removing the frame the signal is attributed to does not shrink the
ordering, it **amplifies** it by two orders of magnitude — from
+0.54/+4.59/+8.39 bits under `RC.MATZOV` to +76/+166/+280 under `CheNgu12` and
`ABLR21`, models in which such a gap is not credible as an attack comparison.

To the producer's credit, `report.md` explicitly lists "DEF-7's null of the
right shape (NULL-1) did not run" under *Remains uncheckable*, and records the
enumeration-model oddity as ANOM-C without drawing a conclusion. That is honest
executor behaviour. The consequence still needs saying plainly (**D-6**): the
ANOM-3 ordering has **no null-object control**, for the second consecutive
batch, and BATCH-012 is the final authorised batch.

## 5. S4 — the numbers are right; what they are called is not

I reimplemented the inflation recipe from scratch (subclass `MATZOV`,
`Nf → Nf·2^δ`, full re-optimisation, `primal_bdd` untouched). All six sampled
integer-δ rows reproduce, max deviation **4.6e-07** — i.e. rounding of the
reported 6-dp figures:

| set | δ | mine | claimed |
|---|---|---|---|
| K-512 | 2 | +0.07604915 | +0.076049 |
| K-512 | 4 | −0.33151154 | −0.331512 |
| K-768 | 16 | +0.72891092 | +0.728911 |
| K-768 | 24 | −1.51553592 | −1.515536 |
| K-1024 | 24 | +3.63719594 | +3.637196 |
| K-1024 | 32 | +1.97412073 | +1.974121 |

Then I probed the claimed flip points and got a **negative** margin at both —
which looked at first like an overshoot. It is not. Scanning K-512 with a
**fresh process per evaluation** (to rule out caching) shows why:

| δ | 2.0 | 2.2 | 2.3 | 2.4 | 2.6 | 2.7 | 2.75 | 2.777 | **2.7773** | 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| margin | +0.0760492 | +0.0760491 | +0.0760491 | +0.0760491 | +0.0760490 | +0.0760490 | +0.0760490 | +0.0760490 | **−0.1218969** | −0.1218969 |
| β | 387 | 387 | 387 | 387 | 387 | 387 | 387 | 387 | **388** | 388 |

**The margin is a step function.** It is constant to seven decimal places
across the whole plateau and then jumps 0.198 bits when the optimiser's integer
β increments. It never equals zero — it jumps across zero. Bisecting for a
"root" here converges to the **jump location**.

So both flip points are correct *as jump locations*, and I bracketed both:

- K-512: jump lies in (2.777, 2.7773]. Producer's 2.77728 is inside it. ✔
- K-768: +0.11440793 at δ=19.671, −0.63266046 at δ=19.67163 → jump in
  (19.671, 19.67163]. Producer's 19.67163 is at the edge of it. ✔
- K-1024: +1.97412073 at δ=32 > 0 → no flip within 32. ✔

**Both corrections of the BATCH-011 red team hold.** K-768 does flip (margin
decays +0.7289 → +0.3947 → +0.1144 → −0.6327 → −1.5155 across δ = 16 → 24), and
2.3732 *is* linear interpolation — I get 2 + 2·0.076049/(0.076049+0.331512) =
**2.373191**, which rounds to 2.3732.

But the *reason* given for the correction is wrong (**D-3**). `report.md` says
interpolation understates the flip point "because the optimiser recovers some of
the loss." The optimiser recovers **nothing** across that interval: margin
constant to 7 dp, β pinned at 387. The real reason is that the function is a
step function, so interpolating between the δ=2 and δ=4 rows has no basis. And
the definition itself — "the delta at which the margin reaches 0"
(`reserve_checks.py:553`) — describes an object that does not exist (**D-2**).

**On decay (D-7).** Two destroying parameters were applied in this package and
they disagree. Under N-inflation the margin decays on all three sets — true,
reproduced. Under removal of the `RC.MATZOV` frame it does not decay, it
amplifies. The summary sentence "the artifact tell is not triggered" is scoped
to the first axis only, but as written (and as repeated in the commit message)
it reads as a general clearance. The correct statement: *the artifact tell is
not triggered on the N-inflation axis; on the cost-model-frame axis the
package's own data is consistent with it being triggered.* Neither axis is the
null-object control.

## 6. S5 — reproduces exactly, and no value is transferred

Recomputed from matzov's **own** optimum (β′ = 391/583/804, (p, k_fft) =
(5,50)/(4,60)/(4,120)), margins 3.343959 / 10.633757 / 9.664320:

| model | log2 M | c\* |
|---|---|---|
| A (sieve only) | 89.743525 / 130.159852 / 176.481052 | **0.037261 / 0.081698 / 0.054761** |
| P (peak incl. FFT) | 116.096405 / 130.161113 / 240.000000 | **0.028803 / 0.081697 / 0.040268** |

Exact to 6 dp on both models. The K-768 near-coincidence is real and correctly
explained: `4^60 = 2^120` sits *below* the sieve's `2^130.16`, so Model P is
sieve-dominated there.

**Transfer check (the DEF-12/CE-1 defect).** `EV-MLKEM-020.yaml` states verbatim
that "primal_bdd/RC.MATZOV costs 140.1994731076207 / 200.9587149140538 /
270.7236234535225 bits" and that charging erases the undercut "for every c above
c\* = 0.03164649 / 0.04588645 / 0.00705473 (Model A)". Those `log2(rop)` values
are `primal_bdd`'s — I reproduced them under both backends. **The producer's
attribution is correct.**

I searched the whole package for 0.0316 / 0.0459 / 0.0071. Each occurs exactly
once, under an explicit owner label — the `results.json` key is literally
`primal_bdd_cstar_for_contrast_not_transferred` with
`owner_attack: estimator.lwe_primal.primal_bdd`. The two attacks' memory figures
are also distinct (matzov 89.74/130.16/176.48 vs EV-MLKEM-020's primal-derived
88.49/131.66/180.92). **No transfer anywhere. DEF-12/CE-1 is not repeated.**

## 7. What I could not check

- The ~376k individual `MATZOV.cost` evaluations behind S2. I verified totals,
  plane arithmetic, β coverage and the incumbent-exclusion facts, not each point.
- 14 of the 18 NULL-2 cells.
- The producer's 14-iteration bisection end to end (I bracketed instead).
- The pip source build of `sagemath-standard` (R9b) — transcript only.
- Upstream sagemath 10.9, still unobtainable.
- NULL-1 — deliberately not rerun; that would be repairing a producer artifact.

## 8. Verdict

**ADMISSIBLE_WITH_DEFECTS.** Seven numbered defects in `report.yaml`: D-1
(mislabelled `shim_anchor` field), D-2 (flip point is a discontinuity, not a
zero), D-3 (stated mechanism contradicted by the data), D-4 (S2 "best found" is
the incumbent), D-5 (mixed-attribution c\* list), D-6 (**high** — the real null
object has now gone unrun twice), D-7 (artifact-tell claim scoped to one axis
while the other disagrees).

D-1, D-4 and D-5 change no conclusion. D-2, D-3 and D-7 are characterisation
errors — right numbers, wrong description. D-6 is substantive and is *not* the
executor's fault.

The package is admissible as evidence of what it actually measured: instrument
agreement, box coverage, cost-model-frame sensitivity, N-decay sensitivity, and
per-attack c\*. It is **not** admissible as evidence that ANOM-3's internal
comparison is a finding rather than an artifact — and the producer never claims
it is. S1 removes the instrument objection and leaves the model objection
untouched; that self-assessment is accurate and I confirm it.
