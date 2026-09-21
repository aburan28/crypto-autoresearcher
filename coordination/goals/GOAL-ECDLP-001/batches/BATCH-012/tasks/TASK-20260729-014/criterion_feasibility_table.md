# EXP-YIELD-002 criterion feasibility table

**Task** TASK-20260729-014 | **Goal** GOAL-ECDLP-001 | **Batch** BATCH-012 |
**Contract** `experiments/EXP-YIELD-002/specification.yaml` | **Date** 2026-07-29
(date precision only; the authoring session had no clock access and fabricates no
wall-clock time).

Mandatory under `DEFER-BATCH009-003`. Every criterion and every invalidation rule
in the frozen contract is evaluated here, **with the arithmetic shown, at the exact
48 tuples that will run**, and each is marked **CAN FIRE** or **CANNOT FIRE**,
including under the counterfactual in which the diagnostic is wrong and the
repaired null still falls short by the full `|S_(m-2)| exp(-lambda)` term.

**Nothing in this table is a result.** It is pre-data arithmetic on quantities
already committed at `2fb2bb7a111d999859612e52990eea7dc6bbac1a`. It computes no
efficiency `E`, no yield ratio `R`, no curve operation, and no statement about
decomposition yield in either direction. Claim tier **toy**.

---

## 1. Session limits, stated first because they bound everything else

- The authoring session had **no shell**. It ran no git command, no interpreter,
  no allocator, no validator and no dispatcher, and it **made no commit and wrote
  no receipt**.
- Every quantity in section 3 is **QUOTED** verbatim from the committed file
  `experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json`,
  sha256 `040207f85a3444a3377cdf5c86175fb70de6e47280f91c09a516f7a65d2125cd`,
  as bound by the `TASK-20260729-006` snapshot receipt. That hash is quoted from
  the receipt; it was **not computed here**.
- Every quantity in sections 4 to 9 that is not QUOTED is **arithmetic performed
  by hand in this session**. Square roots and exponentials were evaluated to the
  digits shown by hand and are declared to be **checkable, not machine-verified**.
  `TASK-20260729-016` is asked to re-derive them. Two classes of constant are
  singled out as **open for the reviewer**:
  - the two-sided Student-t tail probabilities at `t = 3.000`, taken as
    `0.00342` at 99 degrees of freedom and `0.00552` at 29 degrees of freedom;
  - the standard-normal two-sided tail at `3.000`, taken as `0.00270`.
  These enter only the chance-alarm budget of section 8. **No criterion threshold
  depends on them.**

---

## 2. The declared set: RC-C de-duplication, checked column by column

The declared set is the **49 criterion-evaluable cells** of the BATCH-011 package
(`summary.json` reports `n_evaluable_on_measured_B: 49` and
`n_eval_denominator: 49`; the null run reports `cells_evaluated: 49`),
**de-duplicated on measured `B` within each `(k, m)` column**.

Measured `B` values, enumerated per column:

| column | measured B values | duplicates |
|---|---|---|
| k=12, m=2 | 36, 42, 46, 54, 62 | none |
| k=14, m=2 | 34, 44, 56, 72, 86, 118 | none |
| k=16, m=2 | 38, 48, 58, 72, 88, 116, 144, 192, 246 | none |
| k=18, m=2 | 34, 44, 58, 82, 110, 140, 192, 264, 390 | none |
| k=12, m=3 | 16, 20, **22, 22** | **one** |
| k=14, m=3 | 20, 26, 34 | none |
| k=16, m=3 | 16, 22, 30, 38, 48, 58 | none |
| k=18, m=3 | 16, 24, 28, 34, 44, 58, 82 | none |

**Exactly one duplicate exists and the merged cells are named:**
`(k=12, beta=0.325, m=3)` and `(k=12, beta=0.350, m=3)`. Both carry `p=4099`,
`N=4001`, `B=22`, `C_red=1782`, `|S_1|=22` and
`P_pred=1452.1510155838187`. They select the same factor base and are **one**
parameter tuple, labelled `T-12-3-B22`.

`49 - 1 = 48` distinct parameter tuples. **Every per-tuple criterion in the
contract is denominated in 48.**

Binding committed reference for the merged tuple: the **first-listed** occurrence,
`beta = 0.325`, with `mu_001 = 1438.82`, `s_001 = 20.207699302768514`, 100
replicates. The `beta = 0.350` draw (`mu = 1439.23`, `s = 18.440105063352398`) is
a second independent Monte Carlo draw of the same tuple and is reported as an
**observation feeding nothing**. Pre-data consistency of the package's own two
draws, shown:

```
mu(0.350) - mu(0.325) = 1439.23 - 1438.82 = 0.41
sem(0.325) = 20.207699302768514 / 10 = 2.0207699
sem(0.350) = 18.440105063352398 / 10 = 1.8440105
sqrt(2.0207699^2 + 1.8440105^2) = sqrt(4.0835 + 3.4004) = sqrt(7.4839) = 2.73566
z = 0.41 / 2.73566 = 0.14987
```

Note that both merged cells sit **inside** the counterfactual-firing set of CR-1
(committed `z_sem` of `-6.597` and `-7.007`), so the merge removes one
counterfactually-firing tuple: **22 of 49 becomes 21 of 48**. That is recorded so
the change in count is traced to the merge and not mistaken for anything else.

The **four INV-4-failing tuples of the BATCH-011 package**, reported separately in
every artifact and named here:

| tuple | k | beta | m | N | B | C_red | committed z (single sd) |
|---|---|---|---|---|---|---|---|
| `T-18-3-B16` | 18 | 0.200 | 3 | 261707 | 16 | 688 | -12.439358544355992 |
| `T-16-3-B16` | 16 | 0.225 | 3 | 65633 | 16 | 688 | -5.899491744939043 |
| `T-18-3-B24` | 18 | 0.225 | 3 | 261707 | 24 | 2312 | -5.74856699942783 |
| `T-18-3-B28` | 18 | 0.250 | 3 | 261707 | 28 | 3668 | -3.9202705223876375 |

---

## 3. The 48 declared tuples, every quantity QUOTED

`sem_001 = s_001 / sqrt(n_rep)`, DETERMINED from QUOTED inputs.
`T = |S_(m-2)| exp(-lambda)`, QUOTED as `S_m_minus_2_term`.
`n_rep` follows the C-14 schedule: 100 where `C_red <= 10^4`, 30 where
`10^4 < C_red <= 10^6`, 10 above. **37 tuples at 100, 11 tuples at 30, 0 at 10** —
the 10-tier is unreachable because the largest `C_red` is 91922.

### 3.1 m = 2, 29 tuples, `|S_0| = 1`, so `T = exp(-lambda)`

| tuple | k | beta | B | C_red | n | P_pred | mu_001 | s_001 | sem_001 | lambda | T | z_sd_001 | z_sem_001 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-12-2-B36 | 12 | 0.400 | 36 | 648 | 100 | 599.097442009677 | 598.44 | 8.959301920858058 | 0.895930 | 0.16195951 | 0.8504756 | -0.073381 | -0.733809 |
| T-12-2-B42 | 12 | 0.425 | 42 | 882 | 100 | 792.3526169472469 | 792.13 | 11.96852353281538 | 1.196852 | 0.22044489 | 0.8021618 | -0.018600 | -0.186002 |
| T-12-2-B46 | 12 | 0.450 | 46 | 1058 | 100 | 930.4384211023745 | 929.25 | 12.565284065088367 | 1.256528 | 0.26443389 | 0.7676404 | -0.094580 | -0.945797 |
| T-12-2-B54 | 12 | 0.475 | 54 | 1458 | 100 | 1222.5715465471724 | 1223.64 | 16.466384490282564 | 1.646638 | 0.36440890 | 0.6946071 | +0.064887 | +0.648869 |
| T-12-2-B62 | 12 | 0.500 | 62 | 1922 | 100 | 1526.806569859355 | 1524.85 | 18.76940073738115 | 1.876940 | 0.48037991 | 0.6185484 | -0.104243 | -1.042425 |
| T-14-2-B34 | 14 | 0.350 | 34 | 578 | 100 | 569.0300714987135 | 568.66 | 4.546549363100671 | 0.454655 | 0.03477947 | 0.9658184 | -0.081396 | -0.813961 |
| T-14-2-B44 | 14 | 0.375 | 44 | 968 | 100 | 941.2915415755066 | 939.92 | 6.978581951987528 | 0.697858 | 0.05824659 | 0.9434173 | -0.196536 | -1.965359 |
| T-14-2-B56 | 14 | 0.400 | 56 | 1568 | 100 | 1497.2121970271833 | 1497.25 | 11.131332609196694 | 1.113133 | 0.09434984 | 0.9099644 | +0.003396 | +0.033961 |
| T-14-2-B72 | 14 | 0.425 | 72 | 2592 | 100 | 2400.834859878694 | 2401.36 | 19.96589010479542 | 1.996589 | 0.15596606 | 0.8555882 | +0.026302 | +0.263019 |
| T-14-2-B86 | 14 | 0.450 | 86 | 3698 | 100 | 3316.259743249783 | 3316.21 | 20.322796574439764 | 2.032280 | 0.22251640 | 0.8005019 | -0.002448 | -0.024477 |
| T-14-2-B118 | 14 | 0.475 | 118 | 6962 | 100 | 5688.376564839827 | 5697.34 | 35.98097701662237 | 3.598098 | 0.41891811 | 0.6577581 | +0.249116 | +2.491159 |
| T-16-2-B38 | 16 | 0.300 | 38 | 722 | 100 | 719.0323780774312 | 718.06 | 2.9329889605015977 | 0.293299 | 0.01100056 | 0.9890597 | -0.331531 | **-3.315314** |
| T-16-2-B48 | 16 | 0.325 | 48 | 1152 | 100 | 1142.931457181074 | 1142.39 | 4.622944533694533 | 0.462294 | 0.01755215 | 0.9826010 | -0.117124 | -1.171239 |
| T-16-2-B58 | 16 | 0.350 | 58 | 1682 | 100 | 1661.6050336235267 | 1660.9 | 6.054466587286254 | 0.605447 | 0.02562735 | 0.9746982 | -0.116449 | -1.164485 |
| T-16-2-B72 | 16 | 0.375 | 72 | 2592 | 100 | 2542.446385785088 | 2542.64 | 9.90104575641922 | 0.990105 | 0.03949233 | 0.9612773 | +0.019555 | +0.195549 |
| T-16-2-B88 | 16 | 0.400 | 88 | 3872 | 100 | 3760.942211551674 | 3762.6 | 14.369580664892363 | 1.436958 | 0.05899471 | 0.9427118 | +0.115368 | +1.153679 |
| T-16-2-B116 | 16 | 0.425 | 116 | 6728 | 100 | 6395.5482063098725 | 6394.02 | 23.81196541593526 | 2.381197 | 0.10250941 | 0.9025697 | -0.064178 | -0.641781 |
| T-16-2-B144 | 16 | 0.450 | 144 | 10368 | 30 | 9591.411456200445 | 9588.9 | 34.50572166447481 | 6.300000 | 0.15796931 | 0.8538760 | -0.072784 | -0.398653 |
| T-16-2-B192 | 16 | 0.475 | 192 | 18432 | 30 | 16070.770307723493 | 16056.1 | 50.49025170507055 | 9.218262 | 0.28083434 | 0.7551534 | -0.290557 | -1.591447 |
| T-16-2-B246 | 16 | 0.500 | 246 | 30258 | 30 | 24242.75204356428 | 24212.3 | 88.51851549934 | 16.161252 | 0.46101809 | 0.6306413 | -0.344019 | -1.884269 |
| T-18-2-B34 | 18 | 0.275 | 34 | 578 | 100 | 578.3599848111385 | 577.32 | 1.1090081108355294 | 0.110901 | 0.00220858 | 0.9977939 | -0.937761 | **-9.377612** |
| T-18-2-B44 | 18 | 0.300 | 44 | 968 | 100 | 967.2082974365062 | 966.28 | 1.7295997084629589 | 0.172960 | 0.00369879 | 0.9963080 | -0.536712 | **-5.367123** |
| T-18-2-B58 | 18 | 0.325 | 58 | 1682 | 100 | 1677.6000183805504 | 1677.18 | 3.2047313507224024 | 0.320473 | 0.00642703 | 0.9935936 | -0.131062 | -1.310620 |
| T-18-2-B82 | 18 | 0.350 | 82 | 3362 | 100 | 3341.484567098243 | 3340.0 | 6.364357823461099 | 0.636436 | 0.01284643 | 0.9872357 | -0.233263 | -2.332627 |
| T-18-2-B110 | 18 | 0.375 | 110 | 6050 | 100 | 5981.582614220122 | 5980.06 | 12.419290957167718 | 1.241929 | 0.02311746 | 0.9771477 | -0.122601 | -1.226007 |
| T-18-2-B140 | 18 | 0.400 | 140 | 9800 | 100 | 9619.744644416725 | 9615.51 | 16.726254086243454 | 1.672625 | 0.03744646 | 0.9632460 | -0.253174 | -2.531735 |
| T-18-2-B192 | 18 | 0.425 | 192 | 18432 | 30 | 17798.823649376893 | 17798.6 | 36.841318633033346 | 6.726234 | 0.07042991 | 0.9319931 | -0.006071 | -0.033250 |
| T-18-2-B264 | 18 | 0.450 | 264 | 34848 | 30 | 32628.39658964827 | 32600.4 | 50.74180756026296 | 9.264178 | 0.13315655 | 0.8753281 | -0.551746 | **-3.022037** |
| T-18-2-B390 | 18 | 0.475 | 390 | 76050 | 30 | 65997.85841974456 | 65970.233333 | 104.71165114282873 | 19.117723 | 0.29059215 | 0.7478206 | -0.263821 | -1.445005 |

### 3.2 m = 3, 19 tuples, `|S_1| = B`, so `T = B exp(-lambda)`

| tuple | k | beta | B | C_red | n | P_pred | mu_001 | s_001 | sem_001 | lambda | T | z_sd_001 | z_sem_001 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-12-3-B16 | 12 | 0.275 | 16 | 688 | 100 | 645.568750542173 | 632.65 | 10.591949487199885 | 1.059195 | 0.17195701 | 13.4722459 | -1.219676 | **-12.196764** |
| T-12-3-B20 | 12 | 0.300 | 20 | 1340 | 100 | 1153.000627880879 | 1137.82 | 15.822487513381425 | 1.582249 | 0.33491627 | 14.3079597 | -0.959434 | **-9.594337** |
| T-12-3-B22 | 12 | 0.325 | 22 | 1782 | 100 | 1452.1510155838187 | 1438.82 | 20.207699302768514 | 2.020770 | 0.44538865 | 14.0926559 | -0.659700 | **-6.596998** |
| T-14-3-B20 | 14 | 0.300 | 20 | 1340 | 100 | 1305.8513372300656 | 1287.89 | 10.210803349908618 | 1.021080 | 0.08063060 | 18.4506882 | -1.759052 | **-17.590523** |
| T-14-3-B26 | 14 | 0.325 | 26 | 2938 | 100 | 2714.7393765034135 | 2690.24 | 19.738758468013785 | 1.973876 | 0.17678561 | 21.7869449 | -1.241181 | **-12.411812** |
| T-14-3-B34 | 14 | 0.350 | 34 | 6562 | 100 | 5444.332306142441 | 5415.01 | 34.22282745758917 | 3.422283 | 0.39484927 | 22.9085741 | -0.856805 | **-8.568055** |
| T-16-3-B16 | 16 | 0.225 | 16 | 688 | 100 | 700.239731629407 | 684.66 | 2.6408599762466416 | 0.264086 | 0.01048253 | 15.8331555 | **-5.899492** | **-58.994917** |
| T-16-3-B22 | 16 | 0.250 | 22 | 1782 | 100 | 1779.436658096176 | 1759.56 | 7.018474898365733 | 0.701847 | 0.02715098 | 21.4107146 | -2.832048 | **-28.320480** |
| T-16-3-B30 | 16 | 0.275 | 30 | 4510 | 100 | 4386.543552898432 | 4358.4 | 16.825905952165286 | 1.682591 | 0.06871543 | 28.0077694 | -1.672632 | **-16.726322** |
| T-16-3-B38 | 16 | 0.300 | 38 | 9158 | 100 | 8580.836005197178 | 8548.04 | 34.74958614679802 | 3.474959 | 0.13953347 | 33.0510288 | -0.943781 | **-9.437812** |
| T-16-3-B48 | 16 | 0.325 | 48 | 18448 | 30 | 16118.334665688975 | 16070.666667 | 71.94649991886132 | 13.135487 | 0.28107812 | 36.2385292 | -0.662548 | **-3.628924** |
| T-16-3-B58 | 16 | 0.350 | 58 | 32538 | 30 | 25690.62389826237 | 25672.666667 | 77.69229018392357 | 14.184641 | 0.49575671 | 35.3283693 | -0.231133 | -1.265966 |
| T-18-3-B16 | 18 | 0.200 | 16 | 688 | 100 | 703.054445298532 | 687.14 | 1.279362214842879 | 0.127936 | 0.00262889 | 15.9579929 | **-12.439359** | **-124.393585** |
| T-18-3-B24 | 18 | 0.225 | 24 | 2312 | 100 | 2325.6064584777687 | 2301.85 | 4.132587909323022 | 0.413259 | 0.00883431 | 23.7889104 | **-5.748567** | **-57.485670** |
| T-18-3-B28 | 18 | 0.250 | 28 | 3668 | 100 | 3670.0252224971387 | 3641.62 | 7.245730195129133 | 0.724573 | 0.01401567 | 27.6102985 | **-3.920271** | **-39.202705** |
| T-18-3-B34 | 18 | 0.275 | 34 | 6562 | 100 | 6513.574109440055 | 6481.16 | 13.740539445102739 | 1.374054 | 0.02507384 | 33.1580885 | -2.359013 | **-23.590129** |
| T-18-3-B44 | 18 | 0.300 | 44 | 14212 | 30 | 13874.674397229266 | 13830.033333 | 22.505912377729167 | 4.108967 | 0.05430501 | 41.6742999 | -1.983526 | **-10.864220** |
| T-18-3-B58 | 18 | 0.325 | 58 | 32538 | 30 | 30647.782484712883 | 30601.1 | 56.63942211861835 | 10.340921 | 0.12432988 | 51.2191318 | -0.824205 | **-4.514356** |
| T-18-3-B82 | 18 | 0.350 | 82 | 91922 | 30 | 77571.47167723569 | 77483.633333 | 173.7918857145807 | 31.725983 | 0.35124013 | 57.7128077 | -0.505423 | -2.768314 |

Bold `z` values exceed `3.000` in magnitude. **Independent count check:** the
committed package's `z_sem` exceeds 3 at 22 of the 49 cells before de-duplication
(4 at m=2, 18 at m=3), which reproduces exactly the figure red-team objection OB-6
records. After the RC-C merge, **21 of 48**. The committed `z_sd` exceeds 3 at
**4** cells, exactly the four `INV-4` failures. Both counts were re-derived here
from the table above, cell by cell, and not copied from a review report.

---

## 4. The counterfactual, defined numerically before it is used

**THE COUNTERFACTUAL.** The diagnostic is wrong: the pre-marking does nothing, and
the repaired null still falls short of `P_pred` by the **full**
`T = |S_(m-2)| exp(-lambda)` term at every tuple. Then

```
mu_rep = P_pred - T                            at every declared tuple
mu_rep - mu_001 = 0                            (the arms coincide)
sign(mu_rep - P_pred) < 0                      at all 48 tuples, so n_neg = 48
```

Taking `s_rep` equal to the committed `s_001` (the pre-marking changes the spread
by `O(1/N)`), the counterfactual statistics are, **exactly**, the committed
columns of section 3:

```
counterfactual |z_sem|   = |z_sem_001|                    (column 14)
counterfactual |z_sd|    = |z_sd_001|                     (column 13)
counterfactual |z_shift| = T / sqrt(sem_rep^2 + sem_001^2)
                         = |z_sem_001| / sqrt(2) = |z_sem_001| / 1.4142136
```

This is the single most useful property of this design: **the counterfactual
values are already committed and hash-bound**, so the firability of every
criterion is decidable before any draw exists, without a simulation.

---

## 5. Two known second-order terms, quantified before data (OB-10)

Write `E = exp(-lambda)` (QUOTED per tuple as `exp_minus_lambda`, and equal to `T`
at m=2 and to `T/B` at m=3), and

```
f(lambda) = E (1 + lambda) - sqrt(E)      the exact process bias above P_pred
g(lambda) = sqrt(E) - E                   the identity-convention difference at m=2
```

Derivations are in the contract's `process_specification.effect_size_arithmetic_OB_10`.
`f < g` for every `lambda > 0` (their difference is `E(2 + lambda) - 2 sqrt(E)`,
whose expansion is `-lambda^2/4 + O(lambda^3)` and which is negative throughout the
realised range), so `g/sem` bounds both.

### 5.1 `g(lambda) / sem_001`, all 48 tuples

`sqrt(E)` computed by hand to seven places.

| tuple | E | sqrt(E) | g | sem_001 | g/sem |
|---|---|---|---|---|---|
| T-12-2-B36 | 0.8504756 | 0.9222124 | 0.0717368 | 0.895930 | 0.08007 |
| T-12-2-B42 | 0.8021618 | 0.8956401 | 0.0934783 | 1.196852 | 0.07810 |
| T-12-2-B46 | 0.7676404 | 0.8761510 | 0.1085106 | 1.256528 | 0.08636 |
| T-12-2-B54 | 0.6946071 | 0.8334307 | 0.1388236 | 1.646638 | 0.08431 |
| **T-12-2-B62** | 0.6185484 | 0.7864785 | 0.1679301 | 1.876940 | **0.08947** |
| T-14-2-B34 | 0.9658184 | 0.9827610 | 0.0169426 | 0.454655 | 0.03726 |
| T-14-2-B44 | 0.9434173 | 0.9712968 | 0.0278795 | 0.697858 | 0.03995 |
| T-14-2-B56 | 0.9099644 | 0.9539195 | 0.0439551 | 1.113133 | 0.03949 |
| T-14-2-B72 | 0.8555882 | 0.9249801 | 0.0693919 | 1.996589 | 0.03476 |
| T-14-2-B86 | 0.8005019 | 0.8947077 | 0.0942058 | 2.032280 | 0.04636 |
| T-14-2-B118 | 0.6577581 | 0.8110229 | 0.1532648 | 3.598098 | 0.04260 |
| T-16-2-B38 | 0.9890597 | 0.9945148 | 0.0054551 | 0.293299 | 0.01860 |
| T-16-2-B48 | 0.9826010 | 0.9912623 | 0.0086613 | 0.462294 | 0.01874 |
| T-16-2-B58 | 0.9746982 | 0.9872680 | 0.0125698 | 0.605447 | 0.02076 |
| T-16-2-B72 | 0.9612773 | 0.9804475 | 0.0191702 | 0.990105 | 0.01936 |
| T-16-2-B88 | 0.9427118 | 0.9709334 | 0.0282216 | 1.436958 | 0.01964 |
| T-16-2-B116 | 0.9025697 | 0.9500367 | 0.0474670 | 2.381197 | 0.01993 |
| T-16-2-B144 | 0.8538760 | 0.9240541 | 0.0701781 | 6.300000 | 0.01114 |
| T-16-2-B192 | 0.7551534 | 0.8689956 | 0.1138422 | 9.218262 | 0.01235 |
| T-16-2-B246 | 0.6306413 | 0.7941292 | 0.1634879 | 16.161252 | 0.01012 |
| T-18-2-B34 | 0.9977939 | 0.9988963 | 0.0011024 | 0.110901 | 0.00994 |
| T-18-2-B44 | 0.9963080 | 0.9981523 | 0.0018443 | 0.172960 | 0.01066 |
| T-18-2-B58 | 0.9935936 | 0.9967916 | 0.0031980 | 0.320473 | 0.00998 |
| T-18-2-B82 | 0.9872357 | 0.9936074 | 0.0063717 | 0.636436 | 0.01001 |
| T-18-2-B110 | 0.9771477 | 0.9885079 | 0.0113602 | 1.241929 | 0.00915 |
| T-18-2-B140 | 0.9632460 | 0.9814510 | 0.0182050 | 1.672625 | 0.01088 |
| T-18-2-B192 | 0.9319931 | 0.9653979 | 0.0334048 | 6.726234 | 0.00497 |
| T-18-2-B264 | 0.8753281 | 0.9355896 | 0.0602615 | 9.264178 | 0.00650 |
| T-18-2-B390 | 0.7478206 | 0.8647663 | 0.1169457 | 19.117723 | 0.00612 |
| T-12-3-B16 | 0.8420154 | 0.9176104 | 0.0755950 | 1.059195 | 0.07137 |
| T-12-3-B20 | 0.7153980 | 0.8458121 | 0.1304141 | 1.582249 | 0.08242 |
| T-12-3-B22 | 0.6405753 | 0.8003595 | 0.1597842 | 2.020770 | 0.07907 |
| T-14-3-B20 | 0.9225344 | 0.9604865 | 0.0379521 | 1.021080 | 0.03717 |
| T-14-3-B26 | 0.8379594 | 0.9154012 | 0.0774418 | 1.973876 | 0.03923 |
| T-14-3-B34 | 0.6737816 | 0.8208420 | 0.1470604 | 3.422283 | 0.04297 |
| T-16-3-B16 | 0.9895722 | 0.9947724 | 0.0052002 | 0.264086 | 0.01969 |
| T-16-3-B22 | 0.9732143 | 0.9865162 | 0.0133019 | 0.701847 | 0.01895 |
| T-16-3-B30 | 0.9335923 | 0.9662258 | 0.0326335 | 1.682591 | 0.01940 |
| T-16-3-B38 | 0.8697639 | 0.9326116 | 0.0628477 | 3.474959 | 0.01809 |
| T-16-3-B48 | 0.7549694 | 0.8688898 | 0.1139204 | 13.135487 | 0.00867 |
| T-16-3-B58 | 0.6091098 | 0.7804548 | 0.1713450 | 14.184641 | 0.01208 |
| T-18-3-B16 | 0.9973746 | 0.9986864 | 0.0013118 | 0.127936 | 0.01025 |
| T-18-3-B24 | 0.9912046 | 0.9955926 | 0.0043880 | 0.413259 | 0.01062 |
| T-18-3-B28 | 0.9860821 | 0.9930167 | 0.0069346 | 0.724573 | 0.00957 |
| T-18-3-B34 | 0.9752379 | 0.9875413 | 0.0123034 | 1.374054 | 0.00895 |
| T-18-3-B44 | 0.9471432 | 0.9732128 | 0.0260696 | 4.108967 | 0.00634 |
| T-18-3-B58 | 0.8830885 | 0.9397277 | 0.0566392 | 10.340921 | 0.00548 |
| T-18-3-B82 | 0.7038147 | 0.8389370 | 0.1351223 | 31.725983 | 0.00426 |

**MAXIMUM `g/sem` OVER ALL 48 TUPLES = 0.08947, AT `T-12-2-B62`.**

### 5.2 `f(lambda) / sem_001` at the six largest-ratio tuples

`f = E(1 + lambda) - sqrt(E)`:

| tuple | E | lambda | f | sem_001 | f/sem |
|---|---|---|---|---|---|
| **T-12-2-B46** | 0.7676404 | 0.26443389 | 0.0944749 | 1.256528 | **0.07519** |
| T-12-2-B36 | 0.8504756 | 0.16195951 | 0.0660057 | 0.895930 | 0.07367 |
| T-12-2-B42 | 0.8021618 | 0.22044489 | 0.0833538 | 1.196852 | 0.06964 |
| T-12-2-B54 | 0.6946071 | 0.36440890 | 0.1142962 | 1.646638 | 0.06941 |
| T-12-3-B20 | 0.7153980 | 0.33491627 | 0.1091838 | 1.582249 | 0.06901 |
| T-12-2-B62 | 0.6185484 | 0.48037991 | 0.1292084 | 1.876940 | 0.06884 |

Since `f < g` everywhere, `f/sem <= 0.08947` at every one of the 48 tuples, and its
own tightest maximum is **0.07519 at `T-12-2-B46`**. The largest absolute bias in
bins is `f = 0.13063` at `T-16-3-B58`, the largest-`lambda` tuple.

### 5.3 The identity-bin convention at m = 3 is negligible

At m = 3 the difference between the RC-A-literal uniform pre-marking and the
structurally exact antipodal-pair pre-marking is `(B/N)(E - sqrt(E)) + O(1/N)`.
The largest `B/N` in the declared set is `22/4001 = 0.005499` at `T-12-3-B22`, and
`|E - sqrt(E)| <= 0.1714`, so the difference is at most `0.000943` bins there,
i.e. `0.000943/2.020770 = 0.00047` standard errors. At every other m = 3 tuple
`B/N` is smaller. **Below 0.001 standard errors at every m = 3 tuple.**

### 5.4 Binding conclusion of section 5

**THE IDENTITY-BIN CONVENTION AND THE EXACT PROCESS BIAS TOGETHER CANNOT PRODUCE
AN EXCURSION ABOVE `0.08947 + 0.07519 = 0.16466` STANDARD ERRORS AT ANY DECLARED
TUPLE**, against a threshold of `3.000`. **NO OUTCOME OF THIS EXPERIMENT MAY BE
EXPLAINED BY EITHER OF THEM, IN EITHER DIRECTION, BY ANY RECORD.** This is
recorded before data precisely so that it cannot be introduced afterwards.

---

## 6. Criterion-by-criterion firability

### CR-1 — primary, standard-error-of-the-mean reading, threshold 3.000

Counterfactual statistic = `|z_sem_001|` from section 3. **CAN FIRE.**

**Counterfactual firing set, 21 of 48 tuples, NAMED (PRED-ID: set identity, never
cardinality):**

`T-16-2-B38` (3.315314), `T-18-2-B34` (9.377612), `T-18-2-B44` (5.367123),
`T-18-2-B264` (3.022037), `T-12-3-B16` (12.196764), `T-12-3-B20` (9.594337),
`T-12-3-B22` (6.596998), `T-14-3-B20` (17.590523), `T-14-3-B26` (12.411812),
`T-14-3-B34` (8.568055), `T-16-3-B16` (58.994917), `T-16-3-B22` (28.320480),
`T-16-3-B30` (16.726322), `T-16-3-B38` (9.437812), `T-16-3-B48` (3.628924),
`T-18-3-B16` (124.393585), `T-18-3-B24` (57.485670), `T-18-3-B28` (39.202705),
`T-18-3-B34` (23.590129), `T-18-3-B44` (10.864220), `T-18-3-B58` (4.514356).

Verdict: **CAN FIRE at 21 tuples; CANNOT FIRE at the other 27** even under the
full counterfactual. Retained. See section 7.

### CR-2 — secondary, single-replicate-standard-deviation reading, threshold 3.000

Counterfactual statistic = `|z_sd_001|`. **CAN FIRE.**

**Counterfactual firing set, 4 of 48 tuples, NAMED:** `T-16-3-B16` (5.899492),
`T-18-3-B16` (12.439359), `T-18-3-B24` (5.748567), `T-18-3-B28` (3.920271).
This set is exactly the four BATCH-011 `INV-4` failures and is a **strict subset**
of CR-1's 21.

Chance-alarm risk under a correct diagnostic: the statistic
`(mu_rep - P_pred)/s_rep` has expectation at most `0.0895/sqrt(n)` and standard
deviation `1/sqrt(n)`, i.e. `0.100` at `n = 100` and `0.183` at `n = 30`. Reaching
`3.000` requires a `30`-standard-deviation excursion at the 37 tuples with 100
replicates and a `16`-standard-deviation excursion at the 11 with 30. **Its
per-tuple chance-alarm probability is below `1e-20`.**

Verdict: **CAN FIRE, with essentially no power and essentially no chance-alarm
risk.** RETAINED BECAUSE RC-E REQUIRES BOTH READINGS TO BE REPORTED AND BOTH TO
PASS, not because it discriminates. This weakness is declared rather than hidden:
under the SEM reading the BATCH-011 firing count was 22 of 49 and under this
reading it was 4 of 49, and that gap is the whole reason RC-E exists.

### CR-3 — the pre-registered upward shift, threshold 3.000

Counterfactual statistic = `|z_sem_001| / 1.4142136`, so it fires where
`|z_sem_001| > 4.242641`. **CAN FIRE.**

**Counterfactual firing set, 18 of 48 tuples, NAMED:** `T-18-2-B34` (6.63105),
`T-18-2-B44` (3.79514), `T-12-3-B16` (8.62525), `T-12-3-B20` (6.78419),
`T-12-3-B22` (4.66478), `T-14-3-B20` (12.43893), `T-14-3-B26` (8.77776),
`T-14-3-B34` (6.05823), `T-16-3-B16` (41.71725), `T-16-3-B22` (20.02777),
`T-16-3-B30` (11.82680), `T-16-3-B38` (6.67352), `T-18-3-B16` (87.95656),
`T-18-3-B24` (40.65003), `T-18-3-B28` (27.71934), `T-18-3-B34` (16.68078),
`T-18-3-B44` (7.68210), `T-18-3-B58` (3.19212).

This set is a **strict subset** of CR-1's 21; the three CR-1 tuples it omits are
`T-16-2-B38`, `T-18-2-B264` and `T-16-3-B48`. CR-3 therefore adds **no** per-tuple
firability beyond CR-1. It is retained because it is **part of the pre-registered
prediction as `DEC-20260729-001` NA-1 states it** — the clause that the mean is
shifted UP by `|S_(m-2)| exp(-C_red/N)` — and because it tests the mechanism
(the size and direction of the shift) and not only the endpoint. Its declared cost
is that it doubles the chance-alarm budget of section 8, and that cost is
recorded rather than absorbed silently.

### CR-4 — aggregate sign, thresholds `n_neg >= 35` or `n_neg <= 13`

Under the counterfactual every tuple is short, so `n_neg = 48 >= 35`.
**CAN FIRE, AND FIRES WITH CERTAINTY.**

Null reference: with 48 independent per-tuple Monte Carlo streams and a per-tuple
negative-sign probability `p`, `n_neg ~ Binomial(48, p)`. The declared positive
bias `f(lambda)` puts `p` between `0.472` and `0.500`; CR-4's thresholds are
evaluated at the **conservative end `p = 0.500`**, giving mean `24.0` and standard
deviation `sqrt(48 x 0.25) = sqrt(12) = 3.464102`. With a continuity correction,

```
P(n_neg >= 35) = P(Z >= (34.5 - 24)/3.464102) = P(Z >= 3.031089) = 0.001218
P(n_neg <= 13) = P(Z <= (13.5 - 24)/3.464102) = P(Z <= -3.031089) = 0.001218
two-sided                                                        = 0.002436
```

Independence licence, recorded because `OB-9` forbids repeating BATCH-011's error:
`OB-9`'s non-independence concerns the **measured curve quantities** `B`, `C_red`,
`h` and `S_m`, which in EXP-YIELD-002 are **fixed constants quoted from a
committed file and carry no randomness at all**. The only randomness here is the
per-tuple RNG stream, and the contract's seed derivation makes those streams
independent by construction. `OB-9` is **not retracted and not repaired**; it does
not apply to this statistic, and the reason is stated rather than assumed.

Verdict: **CAN FIRE**, and it is the criterion that carries the counterfactual
power at the 27 tuples where CR-1 and CR-2 have none.

---

## 7. The `CANNOT FIRE` finding, and the replacement made before the freeze

**AT 27 OF THE 48 DECLARED TUPLES, NEITHER CR-1 NOR CR-2 CAN FIRE EVEN UNDER THE
FULL COUNTERFACTUAL**, because at those tuples the omitted term `T` is smaller
than `3.000` standard errors of the mean at the fixed replicate count.

**The 27 tuples, NAMED (PRED-ID):**

m = 2, 25 tuples — `T-12-2-B36`, `T-12-2-B42`, `T-12-2-B46`, `T-12-2-B54`,
`T-12-2-B62`, `T-14-2-B34`, `T-14-2-B44`, `T-14-2-B56`, `T-14-2-B72`,
`T-14-2-B86`, `T-14-2-B118`, `T-16-2-B48`, `T-16-2-B58`, `T-16-2-B72`,
`T-16-2-B88`, `T-16-2-B116`, `T-16-2-B144`, `T-16-2-B192`, `T-16-2-B246`,
`T-18-2-B58`, `T-18-2-B82`, `T-18-2-B110`, `T-18-2-B140`, `T-18-2-B192`,
`T-18-2-B390`.

m = 3, 2 tuples — `T-16-3-B58`, `T-18-3-B82`.

`25 + 2 = 27 = 48 - 21`, consistent with section 6.

**Disposition, recorded as `DEFER-BATCH009-003` requires.**

- **NOT REMOVED.** `RC-C` binds the declared set to the whole criterion-evaluable
  set de-duplicated on measured `B`. Dropping 27 tuples would narrow a control
  whose value is completeness and would make the declared count something other
  than the de-duplicated criterion-evaluable set. The removal is therefore
  declined, deliberately, and the reason is recorded.
- **THE COST IS DECLARED.** Those 27 tuples contribute to the chance-alarm budget
  of section 8 while contributing **zero** counterfactual per-tuple power. That is
  a real cost of keeping them and it is stated rather than absorbed.
- **REPLACED AT THE AGGREGATE LEVEL BY CR-4**, which was added to the contract
  **before the freeze for exactly this reason**. CR-4 draws its power from the
  **sign** at all 48 tuples including those 27, and it fires with certainty under
  the counterfactual. Adding CR-4 makes the prediction **harder to pass, never
  easier**: it creates an additional way for the prediction to be missed and no
  route by which a miss is reported as a pass.
- **THE LIMIT IS INFORMATIONAL, NOT EDITORIAL.** No per-tuple criterion can have
  power at those 27 tuples at the fixed replicate count, because `T` is genuinely
  below `3 sem` there. The only escape is more replicates, which **RC-E forbids**
  — raising the count tightens `sem` by `sqrt(count)` and would fire the criterion
  on the section 5 second-order terms rather than on a measurement fault. The
  escape is therefore **declared unavailable rather than quietly taken**.

No other criterion or invalidation rule in the contract is `CANNOT FIRE`, so no
other removal or replacement is required or made.

---

## 8. Chance-alarm budget, computed and recorded BEFORE data

Under a **correct** diagnostic the statistics are centred to within `0.16466`
standard errors (section 5.4), so a chance exceedance of `3.000` is possible at any
tuple. Because `s_rep` is estimated from `n_rep` replicates, the reference is a
two-sided Student-t tail at `n_rep - 1` degrees of freedom.

```
CR-1  37 tuples at 99 df x 0.00342  = 0.12654
      11 tuples at 29 df x 0.00552  = 0.06072
                              CR-1  = 0.18726 expected exceedances
CR-2  48 tuples x  below 1e-20            = below 5e-19  (negligible)
CR-3  same per-tuple reference as CR-1    = 0.18726 expected exceedances
CR-4  one test, two-sided                 = 0.00244
                                   TOTAL  = 0.37696, recorded as 0.377
```

By the union bound, **the probability that at least one criterion registers a
chance alarm under a perfectly correct diagnostic is AT MOST 0.377.** The true
value is lower, because CR-1 and CR-3 are positively correlated by construction:
CR-3's numerator equals CR-1's numerator minus the committed arm's own sampling
error, giving a correlation of exactly `1/sqrt(2) = 0.7071`.

For reference, the standard-normal figure for CR-1 alone is
`1 - (1 - 0.00270)^48 = 1 - 0.99730^48 = 0.1217`.

**Why this is recorded here and not later.** `MISS-MARGINAL` in the frozen
contract routes a single, modest exceedance to `inconclusive` rather than to a
measurement-fault reading. That branch is only honest if the chance-alarm rate is
on the record **before the numbers exist**. It is. It is a pre-registered reading,
not a post-hoc excuse, and it does **not** convert a miss into a pass: under
`MISS-MARGINAL` the pre-registered prediction is recorded as **NOT MET**,
`EV-ECDLP-008` observation `O-4` is **neither confirmed nor superseded**, and the
discrimination remains **undischarged**.

---

## 9. Invalidation rules, evaluated

| rule | statistic and threshold | can it fire? |
|---|---|---|
| **IV-1a** comparability of means | `|z_comp| >= 3.000` at more than 2 of 48 | **CAN FIRE.** Under a correct re-implementation the expected number of exceedances is `0.187`; by the Poisson approximation `P(3 or more) = 0.00036`, so it almost never fires on chance. Under a real defect that shifts the mean it fires at many tuples at once. |
| **IV-1b** comparability of spread | `|ln(s_asrec/s_001)| >= 3.000/sqrt(n-1)`, i.e. `0.30151` at the 37 tuples with `n=100` and `0.55709` at the 11 with `n=30`, at more than 2 of 48 | **CAN FIRE.** Worked defect: substituting independent throws for antipodal pairs changes the sd by the analytic factor `1/sqrt(2) = 0.70711`, whose log is `-0.34657`. That **exceeds `0.30151`** and so fires at all 37 tuples with `n=100`; it does **not** exceed `0.55709` and so does not fire at the 11 tuples with `n=30`. Detection coverage for that specific defect is therefore **37 of 48 tuples**, far above the 2-tuple trigger. Stated so the coverage is known rather than assumed universal. |
| **IV-2** known-answer, KA-1/2/5/6/7 | exact equality, tolerance **zero** | **CAN FIRE** on any defect in pre-marking count, without-replacement sampling, double-counting of a pre-marked bin, identity-bin coverage, or antipodal pairing. Zero chance-alarm risk by construction. |
| **IV-2** known-answer, KA-3 | `|mean - 7.243921| <= 4.000 x sd/sqrt(1e6)` | **CAN FIRE.** Chance-alarm probability `0.0000633` (two-sided normal at 4.000). A bias as small as `0.001` bins would be roughly `4` standard errors at `1e6` replicates, so the case has real power against a systematic error in the closed form. |
| **IV-2** known-answer, KA-4 | each of 11 marginals within `[0.27095, 0.27451]` | **CAN FIRE.** Per-bin chance-alarm `0.0000633`, so `11 x 0.0000633 = 0.0007` expected. Detects a non-uniform pre-marking. |
| **IV-2** known-answer, KA-6 frequency | `[0.08976, 0.09206]` | **CAN FIRE.** Detects an identity bin excluded from, or over-represented in, the throw universe. |
| **IV-2** known-answer, KA-8 | `|P_pred_recomputed - P_pred_quoted| <= 1e-9` at the four `INV-4` tuples | **CAN FIRE**, and it is DETERMINED rather than SAMPLED. It fires only on a genuine arithmetic or parse defect. The BATCH-011 validator already reproduced `P_pred` at all 49 cells to a maximum absolute difference of `0.0`, so a firing here would indicate a defect in **this** batch's reader. |
| **IV-3** infrastructure | any terminal status other than `completed_valid` | **CAN FIRE**, and its firing is **infrastructure signal and never a negative mathematical result**. |
| **IV-4** input integrity | hash mismatch; `cells` length not 49; `n_evaluable_on_measured_B` not 49; de-duplication not yielding 48; any odd `C_red`; any recomputed `lambda`, `exp(-lambda)`, `T` or `P_pred` differing from the QUOTED value by more than `1e-9` | **CAN FIRE.** The odd-`C_red` clause is **unreachable on the declared set** — all 49 committed `C_red` values are even, `C_red_is_even` is `true` at all 49, and the largest is `91922` — so it can fire only on a read or parse error, which is exactly what it is for. |
| **IV-5** incomplete coverage | any arm not measuring all 48 tuples | **CAN FIRE**, and it names the unreached tuples rather than substituting an estimate. |
| **IV-6** scope breach | forbidden import, curve operation, any `E` or `R` computed, any unlisted file read or written | **CAN FIRE** on inspection of the committed driver, which is what `TASK-20260729-020` and `TASK-20260729-021` check. |

No invalidation rule in the contract is `CANNOT FIRE`.

---

## 10. Budget feasibility

The dominant cost is clearing one `N`-length boolean array per replicate, not the
random draws.

```
Main arms, both processes, 48 tuples:
  k=12, N=4001      8 tuples,  sum n_rep =  800  ->  3.20e6 x 2 arms =  6.4e6
  k=14, N=16619     9 tuples,  sum n_rep =  900  ->  1.50e7 x 2 arms =  3.0e7
  k=16, N=65633    15 tuples,  sum n_rep = 1150  ->  7.55e7 x 2 arms =  1.51e8
  k=18, N=261707   16 tuples,  sum n_rep = 1180  ->  3.09e8 x 2 arms =  6.18e8
                                            TOTAL  approximately 8.1e8 byte-clears
Random draws, both arms:            below 2e7
High-precision block, 4 tuples x 10000 replicates x 2 processes:
  (3 x 261707 + 65633) x 10000 x 2  = 1.70e10 byte-clears
Known-answer arm at N = 11:         negligible
Peak memory: one boolean array of length at most 261707 = 0.262 MB, plus the
  parsed IN-1 document.
```

Against the declared budget of **600 s per run, 4 GB, 3 runs** (1800 s total,
matching the `TASK-20260729-018` card): the memory cap is not approached by three
orders of magnitude, and the compute is dominated by the diagnostic block, which
executes **last** under `ST-2` so that a cap bind costs the block that feeds
nothing before it costs a criterion quantity. **The binding cost of this
experiment is implementation time, not compute.**

---

## 11. What this table does not do

- It computes **no** efficiency `E`, **no** yield ratio `R`, and quotes none —
  including the value `0.85`, which exists in the record only as a hypothetical
  worked case inside the committed `EXP-YIELD-001` v2 amendment clause C-3 and
  never as a measurement.
- It specifies and performs **no** curve arithmetic.
- It does **not** un-fire `INV-4`, does not re-dispose it, and does not adjudicate
  `INV-5` in either direction.
- It touches **no** cost model. Even a fully repaired null yields no cost-model
  consequence: the counterfactual branch on the committed data is `O-6`, not
  `O-4`.
- It moves **no** hypothesis and meets **no** completion criterion of
  `GOAL-ECDLP-001`.
- It is scoped to the 48 declared parameter tuples, the four tested field sizes
  `k in {12, 14, 16, 18}` with group orders `4001, 16619, 65633, 261707`, the
  frozen beta grid as realised in the source package, arities `m in {2, 3}`, the
  x-interval factor-base convention with `B` measured, the one prime-order curve
  per size of the source package, this simulator, this budget and this platform.
  **Nothing here is evidence about cryptographic-size curves in either
  direction.** Claim tier **toy**.

---

## 12. Items left open for `TASK-20260729-016`

1. **Re-derive the hand arithmetic.** Every `sqrt(E)`, `f`, `g` and ratio in
   section 5, and every division in sections 6 and 8, was computed by hand without
   an interpreter. They are offered for re-derivation, not for adjudication by
   quotation.
2. **Re-check the declared tail constants** named in section 1: the two-sided
   Student-t tails `0.00342` (99 df) and `0.00552` (29 df) at `t = 3.000`, and the
   standard-normal two-sided tail `0.00270`. They enter only the section 8
   chance-alarm budget and no criterion threshold depends on them.
3. **Assess the RC-F disclosure.** The contract discloses that the Coordinator
   read the committed `EXP-YIELD-001` driver in order to state truthfully whether
   this contract's identity-bin treatment differs from what that driver did. The
   process specification is therefore **not** a fully blind re-derivation, and the
   reviewer must judge what that subtracts from, or contributes to, `RC-F`. **No
   card in BATCH-012 may declare `RC-F` discharged, and neither this table nor the
   contract does.**
4. **Test the CR-4 independence licence** in section 6 adversarially. The claim is
   that `OB-9`'s non-independence does not reach CR-4 because the correlated
   quantities are fixed constants here and the only randomness is the seeded RNG.
   If that claim fails, CR-4's threshold is mis-calibrated and the contract needs a
   versioned amendment **before** any run.
5. **Confirm the ID check.** `tools/allocate_id.py --check` was **not run** — the
   authoring session had no shell — and the check recorded in the contract is a
   worktree glob and string search, which cannot see non-ancestor branches. Three
   ID collisions are already on record in this campaign across exactly such
   branches.
