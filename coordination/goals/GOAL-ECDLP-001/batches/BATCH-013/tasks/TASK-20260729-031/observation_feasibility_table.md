# EXP-YIELD-003 observation feasibility table

**Companion to** `experiments/EXP-YIELD-003/specification.yaml`, frozen by
TASK-20260729-031 and snapshot-committed by TASK-20260729-032 in the same commit
as this file. **MANDATORY READING** for TASK-20260729-033 and for any reader of a
result.

**Why it is an OBSERVATION feasibility table and not a criterion feasibility
table.** DEFER-BATCH009-003 requires that every rule of a frozen contract be
evaluated with its arithmetic shown at the exact tuples that will run, and marked
CAN FIRE or CANNOT FIRE, before the freeze. **EXP-YIELD-003 has no success
criterion and no falsification criterion**, so there is no criterion here to make
feasible. What this table does instead is (i) evaluate every INVALIDATION rule,
which is an integrity check on the run rather than a criterion, and (ii) show that
the primary OBSERVATION is measurable at all, and at what precision, before it is
measured.

---

## 1. Session limits, stated first because they bound everything else

The authoring session **has no shell**. It ran no git command, no YAML or JSON
parser, no validator, no allocator, no dispatcher and **no interpreter**. It made
no commit and wrote no receipt.

Consequences, each carried at the point of use rather than only here:

- **S-1.** Every SHA-256 and every commit identifier in the contract is **QUOTED**
  from a committed receipt, specification or results summary with its source named.
  None was computed here and none is fabricated.
- **S-2.** Every per-tuple quantity in section 2 below is **QUOTED** from section 3
  of the committed BATCH-012 criterion feasibility table at
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md`,
  which in turn quotes IN-1 at commit `2fb2bb7a111d999859612e52990eea7dc6bbac1a`.
  **No column was recomputed here except where a row is explicitly marked
  HAND-DERIVED.**
- **S-3.** Every probability and every standard-normal tail value in sections 3 and
  4 is **HAND-DERIVED AND NOT MACHINE-VERIFIED**. Each is given with its defining
  formula so that re-derivation is mechanical. **None of them binds anything**,
  because this contract has no criterion for a number to bind — and they are
  flagged rather than asserted precisely because RT21-1 is a case of an unverified
  numeric claim in a frozen contract surviving three independent reviews.
- **S-4.** No timestamp beyond date precision is asserted anywhere.

---

## 2. The 48 declared tuples, named, with the quantities the observation needs

The declared set is the RC-C de-duplicated criterion-evaluable set of the BATCH-011
package: 49 cells merged to 48 distinct parameter tuples, with
`(k=12, beta=0.325, m=3)` and `(k=12, beta=0.350, m=3)` merged on identical
measured `B = 22`, `C_red = 1782`, `|S_1| = 22` and
`P_pred = 1452.1510155838187`, under the label `T-12-3-B22`.

`48` is a **COUNT**; its 48 members are the 48 rows of tables 2.1 and 2.2 below and
are named there individually. `29` and `19` are **COUNTS**; their members are the
rows of 2.1 and of 2.2 respectively.

Columns:

- `n` — the C-14 replicate count. **DETERMINED** from `C_red`.
- `s_001` — the committed single-replicate standard deviation of the BATCH-011
  antipodal arm at that tuple. **QUOTED**, SAMPLED in origin.
- `sem_001` — `s_001 / sqrt(n)`. **QUOTED** from the committed table; see 2.3.
- `sd(z_sem)` — the standard deviation of `z_sem` under a centred null, which is
  `sqrt((n-1)/(n-3))` and depends on `n` alone. **DETERMINED**.

`s_001` is **not** the standard deviation EXP-YIELD-003 will measure. The
experiment measures its own `s_rep` and computes `sem_rep = s_rep/sqrt(n_rep)` from
it in full double precision. `s_001` and `sem_001` are the closest committed
pre-data reference for the scale of the process, and **nothing in the primary
observation consumes them**.

### 2.1 The 29 tuples at m = 2 (`|S_0| = 1`)

| tuple | n | s_001 | sem_001 | sd(z_sem) |
|---|---|---|---|---|
| T-12-2-B36 | 100 | 8.959301920858058 | 0.895930 | 1.0102567 |
| T-12-2-B42 | 100 | 11.96852353281538 | 1.196852 | 1.0102567 |
| T-12-2-B46 | 100 | 12.565284065088367 | 1.256528 | 1.0102567 |
| T-12-2-B54 | 100 | 16.466384490282564 | 1.646638 | 1.0102567 |
| T-12-2-B62 | 100 | 18.76940073738115 | 1.876940 | 1.0102567 |
| T-14-2-B34 | 100 | 4.546549363100671 | 0.454655 | 1.0102567 |
| T-14-2-B44 | 100 | 6.978581951987528 | 0.697858 | 1.0102567 |
| T-14-2-B56 | 100 | 11.131332609196694 | 1.113133 | 1.0102567 |
| T-14-2-B72 | 100 | 19.96589010479542 | 1.996589 | 1.0102567 |
| T-14-2-B86 | 100 | 20.322796574439764 | 2.032280 | 1.0102567 |
| T-14-2-B118 | 100 | 35.98097701662237 | 3.598098 | 1.0102567 |
| T-16-2-B38 | 100 | 2.9329889605015977 | 0.293299 | 1.0102567 |
| T-16-2-B48 | 100 | 4.622944533694533 | 0.462294 | 1.0102567 |
| T-16-2-B58 | 100 | 6.054466587286254 | 0.605447 | 1.0102567 |
| T-16-2-B72 | 100 | 9.90104575641922 | 0.990105 | 1.0102567 |
| T-16-2-B88 | 100 | 14.369580664892363 | 1.436958 | 1.0102567 |
| T-16-2-B116 | 100 | 23.81196541593526 | 2.381197 | 1.0102567 |
| T-16-2-B144 | 30 | 34.50572166447481 | 6.300000 | 1.0363755 |
| T-16-2-B192 | 30 | 50.49025170507055 | 9.218262 | 1.0363755 |
| T-16-2-B246 | 30 | 88.51851549934 | 16.161252 | 1.0363755 |
| T-18-2-B34 | 100 | 1.1090081108355294 | 0.110901 | 1.0102567 |
| T-18-2-B44 | 100 | 1.7295997084629589 | 0.172960 | 1.0102567 |
| T-18-2-B58 | 100 | 3.2047313507224024 | 0.320473 | 1.0102567 |
| T-18-2-B82 | 100 | 6.364357823461099 | 0.636436 | 1.0102567 |
| T-18-2-B110 | 100 | 12.419290957167718 | 1.241929 | 1.0102567 |
| T-18-2-B140 | 100 | 16.726254086243454 | 1.672625 | 1.0102567 |
| T-18-2-B192 | 30 | 36.841318633033346 | 6.726234 | 1.0363755 |
| T-18-2-B264 | 30 | 50.74180756026296 | 9.264178 | 1.0363755 |
| T-18-2-B390 | 30 | 104.71165114282873 | 19.117723 | 1.0363755 |

### 2.2 The 19 tuples at m = 3 (`|S_1| = B`)

| tuple | n | s_001 | sem_001 | sd(z_sem) |
|---|---|---|---|---|
| T-12-3-B16 | 100 | 10.591949487199885 | 1.059195 | 1.0102567 |
| T-12-3-B20 | 100 | 15.822487513381425 | 1.582249 | 1.0102567 |
| T-12-3-B22 | 100 | 20.207699302768514 | 2.020770 | 1.0102567 |
| T-14-3-B20 | 100 | 10.210803349908618 | 1.021080 | 1.0102567 |
| T-14-3-B26 | 100 | 19.738758468013785 | 1.973876 | 1.0102567 |
| T-14-3-B34 | 100 | 34.22282745758917 | 3.422283 | 1.0102567 |
| T-16-3-B16 | 100 | 2.6408599762466416 | 0.264086 | 1.0102567 |
| T-16-3-B22 | 100 | 7.018474898365733 | 0.701847 | 1.0102567 |
| T-16-3-B30 | 100 | 16.825905952165286 | 1.682591 | 1.0102567 |
| T-16-3-B38 | 100 | 34.74958614679802 | 3.474959 | 1.0102567 |
| T-16-3-B48 | 30 | 71.94649991886132 | 13.135487 | 1.0363755 |
| T-16-3-B58 | 30 | 77.69229018392357 | 14.184641 | 1.0363755 |
| T-18-3-B16 | 100 | 1.279362214842879 | 0.127936 | 1.0102567 |
| T-18-3-B24 | 100 | 4.132587909323022 | 0.413259 | 1.0102567 |
| T-18-3-B28 | 100 | 7.245730195129133 | 0.724573 | 1.0102567 |
| T-18-3-B34 | 100 | 13.740539445102739 | 1.374054 | 1.0102567 |
| T-18-3-B44 | 30 | 22.505912377729167 | 4.108967 | 1.0363755 |
| T-18-3-B58 | 30 | 56.63942211861835 | 10.340921 | 1.0363755 |
| T-18-3-B82 | 30 | 173.7918857145807 | 31.725983 | 1.0363755 |

### 2.3 The C-14 schedule membership, and a disclosed discrepancy in the quoted `sem_001` column

**The counts, with their members named.** `37` is a **COUNT** — the 37 tuples at
`n = 100` are every row of 2.1 and 2.2 whose `n` column reads 100. `11` is a
**COUNT** and its 11 members are named individually here so that no later record
has to infer them: `T-16-2-B144`, `T-16-2-B192`, `T-16-2-B246`, `T-18-2-B192`,
`T-18-2-B264`, `T-18-2-B390`, `T-16-3-B48`, `T-16-3-B58`, `T-18-3-B44`,
`T-18-3-B58`, `T-18-3-B82`. `37 + 11 = 48`.

The 10-replicate tier of C-14 is **unreachable** on this set: the largest declared
`C_red` is 91922 at `T-18-3-B82`, below the 10^6 boundary. The tier is quoted whole
rather than truncated to its reachable part.

**Disclosed discrepancy, recorded against a committed artifact rather than hidden.**
This session **hand-checked three of the eleven 30-replicate rows** against
`s_001 / sqrt(30)` with `sqrt(30) = 5.477225575051661`, and obtained:

| tuple | quoted `sem_001` | HAND-DERIVED `s_001/sqrt(30)` | absolute difference |
|---|---|---|---|
| T-16-2-B144 | 6.300000 | about 6.299854 | about 1.5e-4 |
| T-16-2-B192 | 9.218262 | about 9.218217 | about 4.5e-5 |
| T-16-3-B48 | 13.135487 | about 13.135573 | about 8.6e-5 |

For `T-16-3-B48` the committed EXP-YIELD-002 manifest at
`c7189f80225bad0d0d2aa28cbbbb11e672d30dd6` records `sem_001` as
`13.135573646367982`, which **agrees with the hand computation and not with the
quoted table column**. At the `n = 100` rows the quoted column is exactly
`s_001/10` and no discrepancy arises.

**Disposition.** This is a **presentation-level rounding in a committed
coordination artifact**, not a defect in EXP-YIELD-003 and not a defect in any
committed run record. **Nothing in EXP-YIELD-003 consumes the `sem_001` column**:
the primary observation is built from `s_rep` measured by this experiment, in full
double precision. The discrepancy is recorded here, and the reviewer is asked at
OI-4 to re-derive all eleven rows and to rule on whether this reading is right.
The eight remaining 30-replicate rows were **not** hand-checked and no claim is made
about them.

---

## 3. Is the primary observation measurable at all? The arithmetic, shown

The primary observation OM-5 is the mean, sample standard deviation (denominator
47) and standard error of the 48-entry `z_sem` vector.

### 3.1 Per tuple

`z_sem = (mu_rep - P_pred) / (s_rep / sqrt(n_rep))` is a **self-normalising**
statistic: its numerator and denominator are both measured at the same tuple in the
same stream. Under a null centred at `P_pred`, and to the normal approximation for
the replicate distribution, `z_sem` is a Student-t variate on `n_rep - 1` degrees of
freedom. Its scale therefore **does not depend on `s_001`, on `P_pred`, on `N`, on
`B` or on `C_red` at all** — only on `n_rep`:

- `n_rep = 100`: `Var(z_sem) = 99/97 = 1.02061856`, `sd = 1.0102567`.
- `n_rep = 30`: `Var(z_sem) = 29/27 = 1.07407407`, `sd = 1.0363755`.

**This is why the observation is measurable at every one of the 48 tuples without
exception, and why it would be measurable even at a tuple whose `s_001` were
unknown.** The `s_001` and `sem_001` columns of section 2 are context, not
prerequisites.

The declared positive second-order process bias shifts each `z_sem` upward by a
**MAGNITUDE** in the interval `[0.00468, 0.07542]` with mean `0.02638`, as measured
across all 48 tuples in the committed EXP-YIELD-002 package. Strictly, that makes
each `z_sem` a **non-central** t with that noncentrality; the effect on the variance
is second order and is **ignored** in the aggregate arithmetic below, which is
therefore an approximation and is labelled as one.

### 3.2 In aggregate — the standard error of the 48-tuple mean

Under the independent-stream design of this contract — the 48 per-tuple streams are
distinct by construction, since the seed string's `k`, `m` and `B` fields are unique
across the de-duplicated set — the variance of the mean is the mean of the variances
divided by 48:

```
Var(mean) = ( 37 x (99/97) + 11 x (29/27) ) / 48 / 48
          = ( 37.76288672 + 11.81481477 ) / 48 / 48
          = 49.57770149 / 48 / 48
          = 1.03286878 / 48
```

```
SEM(mean) = sqrt(1.03286878) / sqrt(48)
          = 1.01630152 / 6.92820323
          = about 0.146691                      [HAND-DERIVED, MAGNITUDE]
```

Two reference magnitudes beside it, both **HAND-DERIVED**:

- The naive standard-normal figure, ignoring the t correction, is
  `1/sqrt(48) = 0.14433757`. The t correction raises it by about 1.6 per cent.
- The **realised** figure in the committed EXP-YIELD-002 package is
  `0.9750016841736118 / sqrt(48) = about 0.14073`, agreeing to the precision this
  session can compute by hand with the `0.140729` recorded at EV-ECDLP-009
  observation O-6 and at DEC-20260729-002 rationale R-8.

`37` and `11` above are **COUNTS**, and their members are named in section 2.3.
`0.146691`, `0.14433757` and `0.14073` are **MAGNITUDES**.

### 3.3 The high-precision block, for scale

At 10000 replicates rather than 100, a **fixed offset in bins** is rescaled in
standard-error units by `sqrt(10000/100) = 10`. An offset producing a `z_sem` of
about `+0.36` at 100 replicates therefore produces a **MAGNITUDE** of about `+3.6`
at 10000. That is the whole reason the block exists at that precision and it is
also why the block **feeds no criterion**: the criteria of the predecessor contract
were deliberately not evaluated at that precision, and this contract has no criteria
at all.

---

## 4. What the design can and cannot say about its own resume condition

**Every figure in this section is HAND-DERIVED AND NOT MACHINE-VERIFIED, feeds
nothing, and is listed at OI-3 for re-derivation.** The model is: the replicated
48-tuple mean `M` is Normal with standard deviation `sigma = 0.146691` from section
3.2, and the two named branch edges are the resume condition's own `about 0.14` and
`about +0.25`, carried verbatim from DEC-20260729-002 NA-1.

The standardised edges are **MAGNITUDES**:

```
0.14 / 0.146691 = 0.954389
0.25 / 0.146691 = 1.704194
```

### 4.1 Under a centred replication (`mu = 0`)

| region | branch | probability (HAND-DERIVED) |
|---|---|---|
| `-0.14 <= M <= +0.14` | "chance and closed" | about 0.660 |
| `+0.14 < M <= +0.25` | **UNASSIGNED — inconclusive on the shift** | about 0.126 |
| `M > +0.25` | "driver, numpy build and platform" | about 0.044 |
| `M < -0.14` | **UNASSIGNED — inconclusive on the shift** | about 0.170 |

### 4.2 Under an exactly reproducing deterministic shift (`mu = 0.361024`)

| region | branch | probability (HAND-DERIVED) |
|---|---|---|
| `-0.14 <= M <= +0.14` | "chance and closed" | about 0.066 |
| `+0.14 < M <= +0.25` | **UNASSIGNED — inconclusive on the shift** | about 0.159 |
| `M > +0.25` | "driver, numpy build and platform" | about 0.775 |
| `M < -0.14` | **UNASSIGNED — inconclusive on the shift** | about 0.000 |

### 4.3 The reading, stated plainly and before the data exist

**THIS DESIGN DOES NOT CLEANLY SEPARATE ITS OWN TWO RESUME BRANCHES.** The two
named thresholds sit at **MAGNITUDES** of about 0.95 and about 1.70 standard errors
of the quantity being measured. Under a centred replication the design lands in an
**unassigned** region about 0.296 of the time; under an exactly reproducing shift it
lands unassigned about 0.159 of the time. The unassigned interval is therefore not a
drafting oversight to be argued away after the fact — it is a region this
measurement reaches with non-negligible probability, and its disposition is fixed in
advance as **inconclusive on the shift**, never assigned to the nearer named branch.

**What this section is not.** It is **not** a power calculation, because there is no
criterion to have power. It is **not** a prediction, and no branch is expected or
preferred. It is **not** a threshold: no record may compare a realised `M` against
any figure here to produce a verdict. It is the measurability check
DEFER-BATCH009-003 requires, expressed for a contract that has observations instead
of criteria.

---

## 5. Every invalidation rule, evaluated, marked CAN FIRE or CANNOT FIRE

The rules divide into two kinds and this table says which each is. **MECHANICAL**
rules have no chance-alarm rate at all: under a correct implementation on correct
inputs they fire with probability exactly zero, and they fire with certainty on the
defect they name. **STOCHASTIC** rules have a chance-alarm rate, and it is computed.
A rule that could fire only on chance and never on a defect would be useless; a rule
that could fire on neither would have to be removed before the freeze.

### IV-1 INPUT INTEGRITY — **CAN FIRE** — MECHANICAL

Evaluated at the exact declared tuples as: five SHA-256 comparisons (IN-1, IN-2,
IN-3 and the two EXP-YIELD-002 files read only for IV-2); one length comparison of
IN-1's `cells` array against 49; one field comparison of IN-2's
`n_evaluable_on_measured_B` against 49; one de-duplication count against 48; **48**
parity tests on `C_red`; and **4 x 48 = 192** absolute-difference tests of the
driver's recomputed `lambda`, `exp(-lambda)`, `T` and `P_pred` against the QUOTED
values at a tolerance of 1e-9. `48`, `49`, `192` are **COUNTS**; the 48 members are
named in section 2.

*Reachable triggers, named*: a changed or truncated input blob; a wrong path; a
parse producing an odd `C_red`; an input read from the working tree that differs
from the pinned commit. *Chance component*: **none**. The committed EXP-YIELD-002
re-derivation leg recorded a maximum absolute difference of **0.0** across all 48
tuples against the same tolerance, so on correct inputs this rule does not fire.

### IV-2 SEED INTEGRITY AND COLLISION — **CAN FIRE** — MECHANICAL

EXP-YIELD-003 derives **73** seeds. `73` is a **COUNT** and its members are: the 48
declared tuples under arm label `REPLICATE-REPAIRED`; the five seeded known-answer
cases `KA-1`, `KA-2`, `KA-3`, `KA-4`, `KA-6`; and the ten high-precision block
tuples under each of `HIGHPREC-REPAIRED` and `HIGHPREC-ASRECORDED`, which is 20.
`48 + 5 + 20 = 73`.

The comparison pool is those 73, plus the **105** derived seeds recorded in the
three committed EXP-YIELD-002 run `results.json` files, plus the derived seeds IN-1
records for the BATCH-011 antipodal arm (whose count is **not** asserted here,
because this session did not enumerate them).

*Chance component, computed*: pairs among the 73 own seeds is
`73 x 72 / 2 = 2628`; cross-pairs against the 105 is `73 x 105 = 7665`; sub-total
`10293`. At a 64-bit derived seed the chance-collision probability is a
**MAGNITUDE** of about `10293 / 2^64 = about 5.6e-16`, ignoring the IN-1 cross-pairs,
which raise it by a factor of order one. **HAND-DERIVED.**

*Reachable trigger, and it is not hypothetical*: **IV-2d fires with certainty on the
DEV-4 defect.** Under the EXP-YIELD-002 seed rule, the two high-precision legs at a
block tuple derived from the single arm label `HIGHPREC` and therefore produced
**identical seed strings**. Had IV-2d existed in that contract it would have fired
at all four block tuples before any draw. The rule is written to fire on exactly the
defect the predecessor shipped.

*Scope, disclosed*: IV-2b and IV-2c compare only against seeds recorded in files
this contract reads and hash-binds. They **do not** cover every BATCH-011 derived
seed, because the other BATCH-011 run records are outside the permitted inputs.
Master-seed block disjointness (130xxx against 120xxx and 110200–110799) is a
**design fact and not a proof about derived seeds**, since the derivation is a
SHA-256 digest. That residual is disclosed and not claimed away.

### IV-3 SIMULATOR KNOWN-ANSWER DEFECT — **CAN FIRE** — the only STOCHASTIC rule

Per case, with `2 x Phi(-4) = 6.33425e-5` as the two-sided 4-sigma tail
(**HAND-DERIVED**):

| case | tolerance | chance-alarm probability under a correct simulator |
|---|---|---|
| KA-1 zero throws | ZERO | exactly 0 — with `C_red = 0` the count is deterministically 3 |
| KA-2 full pre-marking | ZERO | exactly 0 — with `s = N = 11` the count is deterministically 11 |
| KA-3 exact expectation | 4-sigma on the mean at 10^6 | about 6.334e-5 |
| KA-4 pre-marking uniformity | 4-sigma on each of 11 bins | about `11 x 6.334e-5 = 6.968e-4` |
| KA-5 without replacement | ZERO | exactly 0 |
| KA-6 identity-bin accounting | ZERO on the implication, 4-sigma on one frequency | about 6.334e-5 |
| KA-7 antipodal pairing | ZERO | exactly 0 |
| KA-8 P_pred reproduction | 1e-9 absolute, DETERMINED | exactly 0 — no random number is consumed |

**Total chance-alarm probability for IV-3 is a MAGNITUDE of about `8.235e-4`**, being
`6.334e-5 + 6.968e-4 + 6.334e-5`, carried entirely by the three tolerance-bearing
cases KA-3, KA-4 and KA-6. `three` is a **COUNT** and those three are its members.

*Reachable triggers, named*: an off-by-one in the pre-mark; a `replace=True`
sampling call; a missing `(N - g) mod N` mark; an identity-bin double count; a wrong
`ddof`; a `P_pred` formula transcribed wrongly. The five zero-tolerance and
DETERMINED cases fire with certainty on the defects they name and never on chance.

### IV-4 INFRASTRUCTURE — **CAN FIRE** — MECHANICAL

*Reachable triggers, named*: the ST-1 cap of 600 seconds per run; the 4 GB memory
cap; a crash; a budget cancellation. *Arithmetic against the declared tuples*: the
ESTIMATE in the contract's budget note is of order 30 seconds total against a
per-run cap of 600 seconds, and peak memory below 0.3 MB against a cap of 4 GB, so
**the rule is not expected to fire — which is not the same as CANNOT FIRE**, because
the 30 seconds is an estimate derived by ratio from a committed measurement and not
a guarantee. A firing of IV-4 is **infrastructure signal and is never a negative
mathematical result**.

### IV-5 INCOMPLETE COVERAGE — **CAN FIRE** — MECHANICAL

*Reachable trigger*: an ST-1 cap bind partway through the 48-tuple arm or the
10-tuple block. *Arithmetic*: the rule is evaluated by comparing the count of tuples
actually measured against 48 in the primary arm and against 10 in the block, and by
enumerating the difference **by label**. Note the strengthening over the predecessor:
**OM-5 is not computed at all unless all 48 were measured** — a mean over fewer is a
different quantity, reported under a different name with its member set enumerated.

### IV-6 SCOPE BREACH — **CAN FIRE** — MECHANICAL

*Reachable triggers, named*: an import of `harness/`, `tools/`, `orchestration/`,
`experiments/EXP-YIELD-001/driver/yield_census.py` or
`experiments/EXP-YIELD-002/driver/repaired_null.py`; any curve operation; any
computation of an efficiency `E` or a yield ratio `R`; a read of a file not named in
`inputs`; a twelfth written file; **the application of any threshold to any quantity
of this contract**. The last of these is the one this contract adds over its
predecessor and is the mechanical enforcement of the no-criterion design.

### IV-7 ENVIRONMENT DISCLOSURE DEFECT — **CAN FIRE** — MECHANICAL

*Evaluated as*: six required strings x three manifests x three `results.json`, each
present and each recorded before the first draw of its run; plus one equality test
of `numpy.__version__` across the three arms. *Reachable triggers, named*: a missing
`platform.processor()` string; an environment block written after the arm rather
than before it; a mixed-version environment. **PP-1's re-execution is expressly
outside the single-version rule** and a numpy difference between the three arms and
PP-1 is expected under PP-1 case two and does not fire this rule.

*Why it is not decorative*: the pin is **load-bearing**. numpy does not guarantee
bit-identical `Generator` output across versions, and RT29-6 records that
`shuffle=True` and `shuffle=False` return the same **set** of pre-marked bins but
leave the generator in **different states**, so the following `rng.integers` call
differs. An unrecorded version makes the run irreproducible in principle, not merely
in practice.

---

## 6. The RC-21B block selection, re-derived from the quoted lambda column

The rule, fixed before data and keyed **only** on DETERMINED quantities: order the
29 declared m = 2 tuples by `lambda = C_red/N` **ascending**, and take **the three
smallest and the three largest**. Ties would break by order of first appearance in
IN-1's `cells` array; the 29 quoted values are pairwise distinct as quoted to eight
decimal places, so no tie arises.

No SAMPLED quantity enters the rule — no `z` statistic, no residual, no committed
mean — so **it cannot be tuned to the data in either direction**.

The three smallest and three largest, with `lambda` **QUOTED** from IN-1 via the
committed BATCH-012 table section 3:

| rank from the bottom | tuple | lambda | | rank from the top | tuple | lambda |
|---|---|---|---|---|---|---|
| 1 | T-18-2-B34 | 0.00220858 | | 1 | T-12-2-B62 | 0.48037991 |
| 2 | T-18-2-B44 | 0.00369879 | | 2 | T-16-2-B246 | 0.46101809 |
| 3 | T-18-2-B58 | 0.00642703 | | 3 | T-14-2-B118 | 0.41891811 |

The nearest non-selected neighbours, recorded so the boundary is checkable:
`T-18-2-B82` at `0.01284643` from below, and `T-12-2-B54` at `0.36440890` from
above.

**The selection was made BY HAND from the quoted column and was not
machine-verified.** The **rule** is the binding object and the six names are its
stated consequence; where they disagree the rule governs and the disagreement is a
defect to be reported. TASK-20260729-033 is required at OI-1 to re-apply the rule to
IN-1 and to confirm or contradict the six names.

The block therefore covers **10** tuples — `six` m = 2 by this rule plus the `four`
m = 3 INV-4-failing tuples `T-18-3-B16`, `T-16-3-B16`, `T-18-3-B24`, `T-18-3-B28`
carried from the predecessor. `10`, `six` and `four` are **COUNTS** and every member
is named. Each of the 10 runs in **both** legs, giving **20** seeded streams.

---

## 7. Removal record

**No invalidation rule was removed or replaced before the freeze.** All seven —
IV-1, IV-2, IV-3, IV-4, IV-5, IV-6, IV-7 — are marked **CAN FIRE** in section 5,
each with at least one named reachable trigger. `seven` is a **COUNT** and its
members are those seven identifiers.

This record exists because DEFER-BATCH009-003 requires that a rule which CANNOT FIRE
be removed or replaced **before** the freeze with the removal recorded here. The
check was performed and its result was that no removal was warranted; that is
recorded rather than left as a silent absence.

Two rules of the predecessor contract are **deliberately absent** and their absence
is recorded here rather than discovered later:

- **IV-1 of EXP-YIELD-002, the comparability rule on the as-recorded arm**, is
  absent because EXP-YIELD-003 runs no 48-tuple as-recorded arm and has no criterion
  for a comparability anchor to anchor. Its absence removes nothing this contract
  needs.
- **CR-4 of EXP-YIELD-002, the aggregate-sign window**, is absent because it was a
  **criterion** and this contract has none. `n_neg` is still reported, as observation
  OM-6, with the tuples it counts named, and **no window, threshold or reading may
  be applied to it by any later record**.

---

## 8. What this table does not do

- It states **no prediction**, because the contract registers none.
- It states **no power**, because there is no criterion to have power. The only
  sensitivity statement anywhere is the measurability magnitude of section 3.2, and
  it is stated as a magnitude.
- It **does not reproduce the EXP-YIELD-002 clause C-20 power sentence**, in whole
  or in paraphrase, and it creates no clause making any sentence mandatory on any
  downstream record. That sentence is **false as to its five-per-cent clause**; the
  correction is on the record at DEC-20260729-002 and any record quoting the
  sentence carries the correction beside it, verbatim.
- It **does not quote any high-precision difference column as a confirmation of
  `T`** — not EXP-YIELD-002's, whose two legs share a seed under DEV-4 and whose
  error bar is quantified nowhere, and not EXP-YIELD-003's, which feeds nothing.
- It **does not test** EV-ECDLP-008 observation O-4 component (d), which is
  **untouched and still unarchived**. The only mutation that would test it is
  RT21-3's structurally exact pre-marking arm, deferred as DEFER-BATCH013-001 at a
  stated cost of order 10^4 replicates per tuple.
- It makes **no statement about decomposition yield**, moves no hypothesis, touches
  no cost model, computes no efficiency `E` and no yield ratio, does not un-fire or
  re-dispose INV-4, and declares INV-5 neither way.
- It **does not** say the repaired null lands **on** `P_pred`. It lands **at or
  slightly above** it.
- It is **not durable or official** until TASK-20260729-032 commits it and the
  dispatcher post-commit verifier accepts that commit.
