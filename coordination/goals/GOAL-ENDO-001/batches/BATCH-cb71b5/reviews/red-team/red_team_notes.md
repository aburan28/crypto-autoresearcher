# Red-team working notes — GOAL-ENDO-001 / BATCH-cb71b5 / RT-20260807-6042b7

Every command below was actually run in this session and every number quoted is
real output. Nothing here is estimated or reconstructed. Where I reproduced the
batch's own code I ran the **committed snapshot** copy, extracted with
`git archive 22eb74ba harness`, so my numbers are not contaminated by the
working-tree edits that were live during the review.

Review target named in the task card: snapshot commit `22eb74ba` on
`claude/ecdlp-endomorphism-analysis-4m2w3z`.

## 0. Repository state drift during the review

`HEAD` moved under me mid-review, from `22eb74ba` to `96f0b5ca`
("BATCH-cb71b5 snapshot 2: 109 proposals, 108 draft contracts, sampler
correction"). I reviewed `22eb74ba` as instructed and read `96f0b5ca` only to
check whether objections were already self-caught. Two of mine were (O3, O7);
the rest were not.

```
$ git log --oneline 22eb74ba..HEAD
96f0b5ca GOAL-ENDO-001 BATCH-cb71b5 snapshot 2: 109 proposals, 108 draft contracts, sampler correction
```

## 1. Provenance: the six snapshot-1 manifests cite a commit their code does not exist at

```
$ git ls-tree -r e34afdd0 --name-only | grep -E "harness/(run_icinv|exp_icinv|isogeny_class|run_ewalk2|run_volc_mtgt|run_jinv)"
   (no output; exit 1)
$ git ls-tree -r 22eb74ba --name-only | grep -E "harness/(run_icinv|exp_icinv|isogeny_class|run_ewalk2|run_volc_mtgt|run_jinv)"
harness/exp_icinv.py
harness/isogeny_class.py
harness/run_ewalk2.py
harness/run_icinv.py
harness/run_jinv.py
harness/run_volc_mtgt.py
```

All six run manifests under EXP-{INSTR,ICINV,JINV,EWALK,VOLC,MTGT} record
`code.commit: e34afdd0c3137c038042cae7c68495c700977afd` and `dirty: false`.
None of the modules they executed existed at that commit. The snapshot-2 runs
record this correctly:

```
$ grep -h -A2 "  code:" experiments/EXP-ICINV-9b1f7c/runs/*/manifest.yaml | grep -E "commit|dirty" | sort -u
    commit: 22eb74baa5e22f1ffcd974dc58e88395797ed3c4
    commit: 96f0b5caa16ccab2c5555907c9a951953046e251
    dirty: true
```

No experiment-contract file exists for any of the seven experiments:

```
$ for e in EXP-INSTR-2d32ba EXP-ICINV-180a0d EXP-JINV-6c5b8e EXP-EWALK-4fc679 \
           EXP-VOLC-9fec05 EXP-MTGT-321a54 EXP-ICINV-9b1f7c; do
    echo "$e: $(find experiments/$e -maxdepth 1 -type f | wc -l) contract files"; done
EXP-INSTR-2d32ba: 0 ... EXP-ICINV-9b1f7c: 0        (all zero)
```

## 2. C1 — replication of the committed ICINV at two other primes

Committed code, `--no-write`, run from the extracted snapshot.

```
$ cd $SCRATCH/snap && python3 -m harness.run_icinv --p 2003 --fb-m2 40 --fb-m3 13 \
      --window 400 --targets 400 --controls 3 --no-write
 trace=   36 order=1968 n_curves=104
   decomp_rate_m2  mean=0.81387 var=0.0005686 null=0.0003787 ratio=1.501 -> over-dispersed  [chi2=154.63 df=103 accept=[76.80,132.98]]
   decomp_rate_m3  mean=0.77986 var=0.001783  null=0.0004292 ratio=4.154 -> over-dispersed  [chi2=427.82 df=103 accept=[76.80,132.98]]
 trace=  -36 ... m2 ratio=1.721 over-dispersed ; m3 ratio=3.940 over-dispersed
 trace=   12 ... m2 ratio=2.068 over-dispersed ; m3 ratio=4.040 over-dispersed
 trace=  -12 ... m2 ratio=1.478 over-dispersed ; m3 ratio=5.922 over-dispersed
 NULL-C decomp_rate_m2: p=0.2020    NULL-C decomp_rate_m3: p=0.9420
 NULL-C liftable_density: p=0.0000

$ ... --p 6007 ... (same other args)
 NULL-C decomp_rate_m2: p=0.9185   decomp_rate_m3: p=0.9335   liftable_density: p=0.2935
```

Against the committed run's `p=0.538 / 0.062 / 0.0005`. The same statistic on
the same code evaluates to 0.538, 0.202, 0.9185 (m2) and 0.062, 0.942, 0.9335
(m3) at p = 4001, 2003, 6007. `liftable_density`, the one "positive", is
0.0005 / 0.0000 / 0.2935.

`decomp_rate_m2` is **over-dispersed in every class at p = 2003**, where the
committed p = 4001 run reported `invariant` for the target class.

## 3. C1 — spread of relation yield inside the committed target class

Read directly from `RUN-ICINV-p4001-a/raw-result.json`.

```
trace    n     #E  m2 min  m2 max   m2 sd  m3 min  m3 max   m3 sd  m3 max/min
  -30  138   4032  0.4675  0.6175  0.0261  0.4200  0.6175  0.0371       1.470
  -18   98   4020  0.4650  0.6275  0.0298  0.4375  0.6225  0.0352       1.423
   18   98   3984  0.5075  0.6075  0.0230  0.4425  0.6025  0.0292       1.362
   30  138   3972  0.4725  0.6225  0.0275  0.4125  0.6175  0.0356       1.497

target class t=30, m=3:  mean=0.5306  sd=0.0356  binomial-sd=0.0250  excess-sd=0.0254
                         best/mean = 1.1638   mean/worst = 1.2863
  rate_m3 by two_torsion_x: {1: (72, 0.5334, 0.0348), 3: (66, 0.5275, 0.0365)}
  rate_m3 by aut_order:     {2: (138, 0.5306)}
```

Neither the 2-torsion count nor `|Aut|` explains the spread.

## 4. C1 — the saturation-decay control the batch did not run

Same class (p=4001, t=30, 138 curves), same targets, committed
`exp_icinv.decomposition_rate_m3` and `binomial_null_verdict`, varying only the
factor-base size, i.e. varying |3V|/#E, which is the parameter that should
destroy a saturation artifact.

```
  fb   |3V|/#E  mean rate   obs sd  binom sd  var ratio      chi2  accept hi          verdict  max/min
   4    0.0234     0.0234   0.0073    0.0076      0.930     127.4      171.3        invariant    9.000
   5    0.0437     0.0437   0.0104    0.0102      1.032     141.4      171.3        invariant    3.375
   6    0.0745     0.0745   0.0142    0.0131      1.175     160.9      171.3        invariant    2.588
   7    0.1144     0.1144   0.0179    0.0159      1.265     173.4      171.3   over-dispersed    2.462
   9    0.2237     0.2237   0.0241    0.0208      1.337     183.2      171.3   over-dispersed    1.869
  11    0.3690     0.3690   0.0326    0.0241      1.826     250.1      171.3   over-dispersed    1.533
  13    0.5306     0.5306   0.0356    0.0250      2.037     279.1      171.3   over-dispersed    1.497
```

The batch ran only the last row. The over-dispersion decays as the density
falls — consistent with a saturation artifact — but is still 1.27–1.34 at
densities 0.11–0.22, which bracket the 1/m! ≈ 0.167 density a real m = 3
decomposition operates at. Neither reading is established by the batch's data.

## 5. C1/C4 — power characterisation of NULL-C, which EXP-INSTR never did

`EXP-INSTR-2d32ba` characterises NULL-B only: both directions of its control
carry `"null_kind": "NULL-B binomial"`. NULL-C (label permutation) is what C1
and C4 rest on. I planted a between-class mean shift into the real p = 4001
`rate_m3` values and ran the committed `permutation_null`, 12 repetitions each:

```
   delta  as % of mean   median p  power@0.05
   0.000          0.0%     0.0590        0.08
   0.002          0.4%     0.0595        0.08
   0.005          0.9%     0.0055        1.00
   0.010          1.9%     0.0000        1.00
   0.020          3.8%     0.0000        1.00
```

NULL-C is a *between-class mean* detector with power 1.00 at a 0.9% shift —
that is, it is maximally sensitive to exactly the #E confound the batch's own
`CORR-20260807-a05e1e` identifies, and it says nothing about within-class
structure. Note also that at delta = 0 the median p is 0.059, not 0.5: the real
data already carries a small class effect from #E.

## 6. C1/C4 — honest detection bounds for the NULL-B design

Chi-square dispersion test, Wilson–Hilferty band as the harness computes it.

```
 EXP-INSTR control config           n=  40 T=400 -> var-ratio >= 1.490, excess sd >= 4.77% of the mean
 EXP-ICINV target class, m=3        n= 138 T=400 -> var-ratio >= 1.250, excess sd >= 2.36% of the mean
 EXP-ICINV control class            n=  98 T=400 -> var-ratio >= 1.300, excess sd >= 2.58% of the mean
 EXP-VOLC (whole class)             n= 138 T=300 -> var-ratio >= 1.250, excess sd >= 3.19% of the mean
 EXP-VOLC larger stratum            n=  72 T=300 -> var-ratio >= 1.355, excess sd >= 3.80% of the mean
 the CRATER at p=4001 (level 0)     n=   3 T=300 -> var-ratio >= 3.668, excess sd >= 9.82% of the mean
```

## 7. C3 — seed sensitivity of the 1.641 speedup, and the untested |Aut| = 4 arm

Committed `harness/run_ewalk2.py`, unmodified.

```
  seed= 20260807  j0 speedup=1.6411  ratio-to-ceiling=0.9475  generic=1.0000  fruitless={'j0': 0, 'generic': 0}
  seed=        1  j0 speedup=1.3705  ratio-to-ceiling=0.7913  generic=1.0000  fruitless={'j0': 2, 'generic': 0}
  seed=        2  j0 speedup=1.7100  ratio-to-ceiling=0.9873  generic=1.0000  fruitless={'j0': 2, 'generic': 0}
  seed=        3  j0 speedup=1.9227  ratio-to-ceiling=1.1101  generic=1.0000  fruitless={'j0': 0, 'generic': 0}
  seed=        4  j0 speedup=2.0333  ratio-to-ceiling=1.1739  generic=1.0000  fruitless={'j0': 0, 'generic': 2}
  seed=        5  j0 speedup=1.6521  ratio-to-ceiling=0.9538  generic=1.0000
  seed=        6  j0 speedup=1.6806  ratio-to-ceiling=0.9703  generic=1.0000
  seed=        7  j0 speedup=1.8646  ratio-to-ceiling=1.0765  generic=1.0000
  --> mean=1.7344 sd=0.2046 min=1.3705 max=2.0333   ceiling=sqrt(3)=1.7321
  --> seeds where the observed speedup EXCEEDS the ceiling: 3/8

  trials=  24  j0 speedup=1.6411   trials=  96  1.6143   trials= 240  1.6942
```

At seed 4 the ratio-to-ceiling is 1.1739, which trips the harness's own
`exceeds_incremental_ceiling_by_15pct` and therefore GOAL-ENDO-001 pause
condition P3. The reported 1.641 is one draw at 0.4 sigma below a mean that
sits on the ceiling.

`fruitless_total` is 0 in every arm of the reported run, so C3's attribution of
the 5.3% shortfall to fruitless-cycle cost is contradicted by the run's own
counter.

The j = 1728 (|Aut| = 4) arm — the case whose failure produced
`CORR-20260807-df0585` — was refused at p = 100003 because 100003 ≡ 3 mod 4.
I ran it at the nearest prime ≡ 1 mod 12:

```
prime = 1 mod 12 near 100003: 100057   (p%3 = 1, p%4 = 1)
        j0: observed=1.9292 ceiling=1.7321 ratio=1.1138
     j1728: observed=1.3974 ceiling=1.4142 ratio=0.9881
   generic: observed=1.0000 ceiling=1.0000 ratio=1.0000
  refusals: []
     j1728    plain N=  50153 aut=4 solved=47/48 mean_steps=215.81 fruitless=0
     j1728 quotient N=  50153 aut=4 solved=48/48 mean_steps=139.19 fruitless=0
     j1728    plain N=  50153 aut=4 solved=48/48 mean_steps=186.33 fruitless=0
     j1728 quotient N=  50153 aut=4 solved=48/48 mean_steps=148.60 fruitless=0
     generic  plain N=50263 mean_steps=211.31 ; quotient N=50263 mean_steps=211.31   (identical)
     generic  plain N=99527 mean_steps=319.79 ; quotient N=99527 mean_steps=319.79   (identical)
```

The corrected walk is sound at |Aut| = 4 — but that is my measurement, not the
batch's. The generic arm returns identical step counts to the digit because for
`kind == "generic"` the code passes `phi=None, lam=None, aut_order=2` in *both*
modes, so `rho()` receives identical arguments and is deterministic. The
`lam != ±1` branch of `canon` — the exact site of CORR-20260807-df0585 — is
never executed in the generic arm.

## 8. C5 — the ell = 2 MTGT run measures the identity map

```
selected trace=-124 n=4126 N=2063 source curve (a,b)=(444,888)
kernel generator of order 2: (935, 0)   [2]gen = None
kernel_pts actually used by transport_table: []   len = 0
velu_odd(ell=2) -> (a2,b2)=(444,888)    source (a,b)=(444,888)
TARGET CURVE == SOURCE CURVE ? True
j(source)= 737   j(target)= 737
velu_image(empty kernel, P) == P ? True
```

`velu_odd` loops `range((ell-1)//2)`, which is empty at ell = 2, so it returns
`(a, b)` unchanged; `transport_table` then calls `velu_image` with an empty
kernel, which is the identity. `RUN-MTGT-p4001e2`'s `transport_over_rebuild =
0.0575`, `same_isogeny_class: true`, `transport_certificate_verified: true` and
`entries_lost_to_kernel: 0` are all trivially true of the identity map. The run
is `valid: true` in the ledger with no correction record.

## 9. C5 — the rebuild baseline is inflated by ~log2(N)

`build_table(E, P, N, S)` is `[(E.mul(s, P), s) for s in range(1, S+1)]` — a
full double-and-add per entry — for a table of **consecutive** multiples, which
costs one addition per entry ([s]P = [s−1]P + P). I benchmarked both, taking
`min` over 7 repetitions (which favours whichever side is being tested).

```
     p  ell       N  sameE  t/reb(batch)  t/reb(obvious)  inflation  log2N
  4001    2    2063   True        0.0242          0.2699      11.17     12
  2003    3     691  False        0.1395          1.6430      11.78     10
  4001    3    1373  False        0.1495          1.6693      11.17     11
  4001    5     823  False        0.2707          3.1332      11.57     10
  4001    7     587  False        0.3939          4.1986      10.66     10
  4001   11     373  False        0.6718          7.1162      10.59      9
  4001   13     317  False        0.7505          8.7228      11.62      9
  4001   23     179  False        1.3444         15.7446      11.71      8
```

The `t/reb(batch)` column reproduces the committed run records (0.1552 at
ell = 3, 0.4151 at ell = 7 — mine are 0.1395 and 0.3939 with `min`-timing).
The inflation factor is 10.6–11.8, i.e. log2(N), exactly as the algorithm
predicts. Against a correct rebuild, transport **loses at every odd ell**.

Least-squares fit of the batch's own column:

```
  transport/rebuild = 0.06007*ell - 0.02560   -> crosses 1.0 at ell = 17.1
```

## 10. C4 — "volcano level" is the 2-torsion count, and it resolves 2 of 5 levels

```
p=4001 t=30   D = t^2-4p = -15104 = D0*f^2 with D0=-59, f=16
the 2-volcano therefore has DEPTH 4 -> 5 levels

 level  conductor  h(D0 f^2)
     4         16         72     (floor)
     3          8         36
     2          4         18
     1          2          9
     0          1          3     (crater, maximal order O_K)
            total        138     <- equals the enumerated class size

enumerated class size: 138
experiment's 'levels_observed' strata: {1: 72, 3: 66}
ell_subgroup_count(ell=2) and two_torsion_x_count agree on ALL 138 curves
   -- they are the same computation
```

`ell_subgroup_count(E, ·, 2)` and `exp_icinv.two_torsion_x_count(p, a, b)` are
character-for-character the same expression. The reported strata are floor (72)
and levels 0–3 pooled (3+9+18+36 = 66).

I then built the real 2-isogeny graph on the class — Velu with a 2-torsion
kernel, `v = 3x0^2 + a`, `w = x0*v`, `a' = a - 5v`, `b' = b - 7w`, edges
resolved up to isomorphism `(a,b) ~ (u^4 a, u^6 b)` — and assigned each curve
its level by distance to the floor:

```
TRUE level distribution (0 = crater): {0: 3, 1: 9, 2: 18, 3: 36, 4: 72}
expected from class numbers h(D0 f'^2): {0: 3, 1: 9, 2: 18, 3: 36, 4: 72}

 level    n  mean rate_m3       sd
     0    3        0.4800   0.0173
     1    9        0.4456   0.0430
     2   18        0.4489   0.0311
     3   36        0.4411   0.0382
     4   72        0.4519   0.0366

NULL-C on TRUE level:                  obs=0.00118228 null=0.00133614 p=0.3115
NULL-C on the batch's degree binary:   obs=0.00134137 null=0.00134166 p=0.3708
```

The conclusion survives on the correct variable — but as my measurement, and
with the crater at n = 3, where the design detects nothing below a 9.8% excess.

Also: the committed `run_volc` returns `{"invalid": True}` for `ell != 2`, yet
`RUN-VOLC-p2003e3` and `RUN-VOLC-p4001e7` are committed `valid: true` with
`levels_observed: [1]` and `[0]`. They are outputs of superseded code and carry
no correction record.

## 11. C2 — where the "~3%" figure is not

From `RUN-JINV-p1009-a/raw-result.json`:

```
     j0: gb_seconds ratio = 0.9956  (-0.44%)   gb_size ratio = 1.0102  (+1.02%)
         trivial_frac ratio = 0.9714 (-2.86%)  S_3 support 9 vs 13 (-30.8%)   n_curves=6
  j1728: gb_seconds ratio = 0.9933  (-0.67%)   gb_size ratio = 1.0341  (+3.41%)
         trivial_frac ratio = 0.9429 (-5.71%)  S_3 support 10 vs 13 (-23.1%)  n_curves=4
                                                                   generic n_curves=12
```

No metric equals −3%. The Groebner-time movement is −0.44% and −0.67%, with no
dispersion estimate reported for any arm. The only ~3% quantity is
`gb_size_mean` for j = 1728 at **+3.41%** — the special-j basis is *larger*.

I verified the monomial-support counts by hand from
`S_3 = (x1-x2)^2 x3^2 - 2((x1+x2)(x1x2+a) + 2b)x3 + ((x1x2-a)^2 - 4b(x1+x2))`:
generic 3 + 4 + 1 + 3 + 2 = 13; a = 0 drops `a x1 x3`, `a x2 x3`, `-2a x1x2`,
`a^2` → 9; b = 0 drops `-4b x3`, `-4b x1`, `-4b x2` → 10. Exact and correct.

## 12. What the batch had already caught by snapshot 2

`CORR-20260807-a05e1e` (committed at 96f0b5ca) supersedes the NULL-C rows of
every EXP-ICINV-180a0d run: the hash-and-lift target sampler's acceptance rate
is `(#E - 1 + z)/(2p)`, so it encodes the class label into the target multiset.
It forbids citing the p-values C1 quotes. Its `other_experiments` clause records
that the JINV Groebner timing "inherits a weaker form of the same confound and
is recorded here as a limitation rather than a result", and the working-tree
`harness/run_jinv.py` now reads
`EXP_JINV = "EXP-JINV-dd60d3"   # supersedes EXP-JINV-6c5b8e (confounded sampler)`
with no run under that experiment id.

Uniform-sampler results (EXP-ICINV-9b1f7c, snapshot 2):

```
RUN-ICINV-p4001-uniform  eff_m2 p=0.131   eff_m3 p=0.295   liftable p=0.0005
RUN-ICINV-p6007-uniform  eff_m2 p=0.1955  eff_m3 p=0.6905  liftable p=0.09
  target verdicts at BOTH primes: decomp_rate_m2 over-dispersed,
                                  decomp_rate_m3 over-dispersed,
                                  order invariant, s3_support invariant
```

On the corrected instrument, relation yield is over-dispersed within the class
at both m and both primes. DECOMPOSITION.md §5 prediction 1 predicted zero.

## Scripts

All under
`/tmp/claude-0/-home-user-crypto-autoresearcher/b52846f7-5db8-56b6-88ae-b50d19eb64dd/scratchpad/`:
`rt1_velu_ell2.py`, `rt2_rebuild_cost.py`, `rt3_nullc_power.py`,
`rt4_saturation_decay.py`, `rt5_ewalk.py`, `rt6_volcano_levels.py`,
`rt7_true_levels.py`, and `snap/` (the `git archive 22eb74ba harness` extract).
These are scratch, not durable artifacts; every one of them runs against the
committed snapshot and can be regenerated from the commands recorded above.
