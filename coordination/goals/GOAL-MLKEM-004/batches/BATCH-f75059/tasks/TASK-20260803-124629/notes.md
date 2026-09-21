# VAL-20260803-124629 — what I actually re-derived

Independent validation of BATCH-f75059 batch 2 (`TASK-20260803-5f11b7`), snapshot
`e08462ac`. Verdict and per-claim status live in `report.yaml`; this file records
the commands, the raw outputs, and the reasoning behind the judgements that are
not simple number-matching.

**Everything below was run by me, in this session, with my own seeds and my own
code.** I did not execute `compare.py`, and I did not reuse a single producer
seed. Where a number could not be re-derived independently I said so rather than
copying it.

---

## 0. Snapshot integrity — checked first, because nothing else counts otherwise

```
git show --stat e08462ac                  # 8 files: 7 producer paths + snapshot receipt
git rev-parse e08462ac^                   # 6711b6ce..., matches snapshot_receipt.parent_sha
git diff e08462ac -- <task dir>           # empty
git status --porcelain                    # empty
sha256sum <task dir>/*                    # all 7 match receipt.json / snapshot_receipt.json
```

The reviewed object is a Coordinator-committed snapshot whose declared hashes bind
to the tree. Not a working-tree receipt. `/tmp/le` is at the pinned commit
`3e48ef421ec256afddb3e7d2249a77eab6e9ba12` with a clean tree, as the receipt claims.

---

## 1. P1 — the impossibility proof. This is the part I spent the most on.

### 1.1 Is line 540 an identity?

I read `/tmp/le/estimator/lwe_dual.py` at the pinned commit rather than trusting
the quote. `Nf`'s signature is

```python
def Nf(cls, params, m, beta_bkz, beta_sieve, k_enum, k_fft, p):
    mu = 0.5
    k_lat = params.n - k_fft - k_enum          # p.15
```

`k_lat` is **not a parameter**. There is no keyword, no branch, no call path by
which a caller supplies it independently. `MATZOV.cost` repeats the same
assignment at line 586. So `k_lat + k_fft + k_enum = n` is an identity, exactly as
the producer says. Not a default. This premise is correct.

### 1.2 Is R1 forced?

Yes, and it is a fact of the run rather than a modelling choice. The sieved
lattice has dimension `m + k_lat`; the run sieved the full `d = 60` dual lattice
with `m = 35`, so `k_lat = 25 = n`. I checked from `vectors.json` that this is
physically true and not just dimensional bookkeeping: `<||y||^2> = 129.556`, i.e.
rms 2.28 per y-coordinate against ~36.6 for uniform mod 127. Every one of the 25
secret coordinates really is absorbed by y-shortness.

### 1.3 Is R2 forced? — **No, and its stated premise is false.**

R2 is recorded as a design fact: `candidates_differ_on_coordinates = 25` in
`results.json`, and `compare.py:377` codes it as `r2 = (k_enum + k_fft == n)`.

I counted, from the co-archived `vectors.json`:

| group | coords differing from `s` | count |
|---|---|---|
| near_miss | **1** | 8 |
| secret_distribution | 16 / 17 / 18 / 19 / 21 / 23 | 8 |
| reference_zero | 19 | 1 |
| uniform | 24 | 2 |
| uniform | 25 | 14 |

**Only 14 of 33 wrong candidates differ on all 25 coordinates.** The near-miss
group — the batch's own live observation — differs on exactly one.

The conclusion nevertheless survives, under a *stronger* premise than the one the
producer coded. Any candidate differing from `s` on at least one coordinate
requires that coordinate to lie in MATZOV's guessed part, so `k_enum + k_fft ≥ 1`,
so `k_lat ≤ 24`, so `m + k_lat ≤ 59 < 60 = d`, contradicting R1's `k_enum + k_fft
= 0`. Emptiness holds for `h ≥ 1`, not just `h = n`.

So: a defective proof of a true statement. Defect 2.

### 1.4 The scope question — the one the card called load-bearing

**The impossibility is scope (B): "no tuple for the design this producer built."
It is not scope (A), and it is not a statement about the cost model.**

The decisive fact is that a *pure distinguisher* — no candidate scored at all —
**does** admit a tuple. I evaluated it:

```
Nf(params, m=35, beta_bkz=45, beta_sieve=60, k_enum=0, k_fft=0, p=2)
  = 2.978518720180076
```

and by KA-3 / KA-5 (which I reproduced exactly) it is invariant in `p` and in
`beta_bkz` there, so the tuple is essentially unique rather than merely
admissible. `wellposedness.md` §5 **computes with that very tuple**
(`lsigma_s = 24.406`; I get 24.40583).

A split-secret design — sieve on `m + k_lat` with `k_lat < n`, enumerate/FFT the
rest — also admits tuples, which the producer names in §6.

So the honest maximal scope is: *no tuple exists for any design that sieves the
full `m+n` dual lattice **and** scores at least one candidate different from `s`.*
That is a statement about the producer's measurement design. It says nothing
whatever about whether `MATZOV.Nf` is right.

`wellposedness.md` §§5–6 state this correctly. The **headline** — "NO SUCH TUPLE
EXISTS. … The admissible set is empty" — and `report.md`'s §0 table row do not,
and the headline is what gets cited. Defect 1.

### 1.5 The 351-pair enumeration

`351 = (25+1)(25+2)/2` — the count is right and the enumeration is complete as
advertised. But R1 forces the sum to 0 and R2 forces it to 25, so the loop is a
one-line tautology. More importantly it enumerates only *inside* the fixed
conjunction R1 ∧ R2, so it structurally cannot discover what §1.4 above
discovers. Calling it "checked in code, not asserted" attributes computational
force to prose. Defect 3.

### 1.6 What the producer got right, and it is the hard part

**No tuple was manufactured.** `admissible_tuples_found` is `[]`, no residual
against a predicted `N` appears anywhere, and the one sub-comparison that *is*
well-posed is explicitly not licensed as a departure. Given a card that asked for
a tuple, declaring honestly that none exists is the harder and correct output.
I want that on the record alongside the three defects above.

### 1.7 The unit inconsistency — confirmed

`Hf` returns `RR(...)/log(2.0)`, i.e. **bits**. Line 555 sums
`k_enum*Hf(Xs) + k_fft*log(p) + log(1/mu)`, where `log` is natural. Measured:

```
Hf = 2.0470955928998906   nat entropy = 1.4189385385552487   ratio = 1.4426950408889636 = 1/ln 2
```

`MATZOV.cost` line 610 uses `2**(k_enum*H)`, confirming bits is intended for `Hf`.
Real, and correctly recorded as an observation rather than as "the estimator is
wrong" — the discrepancy is confined to `Nf`'s sample-count term.

---

## 2. P1b — the known-answer controls, re-run

Run in the producer's rebuilt venv against `/tmp/le` at the pinned commit, with my
own reimplementation of `Nf`, `Hf` and `deltaf`:

```
KA-0a  LWE.dual_hybrid is lwe_dual.matzov        True
KA-0b  type name                                 MATZOV
KA-0c  lwe_dual.dual_hybrid is a plain function, distinct from the public callable   True
KA-1   Hf 2.0470955928998906 vs mine             diff exactly 0.0
KA-2   Nf vs my reimplementation, 6-point grid    max rel err 2.39e-15
KA-3   Nf(p=2) == Nf(p=127) == 2.978518720180076  exact
KA-5   Nf(bb=45) == Nf(bb=300)                    exact
```

**KA-6, round-tripped independently.** I ran
`LWE.dual_hybrid(schemes.Kyber512, red_cost_model=RC.ADPS16)` myself:

```
log2(rop) = 115.50989392453226   beta 395   p 5   zeta 0   t 40   beta' 395   (5.2 s)
```

against the pinned tree's own docstring at `estimator/lwe.py:55`:
`dual_hybrid :: rop: ≈2^115.5, …, β: 395, p: 5, ζ: 0, t: 40, β': 395`. Match on
every field. This is the strongest control in the package and it holds. It
establishes that the callable reproduces its own repository's documented output —
not that the cost model is right, and the producer does not claim otherwise.

**KA-0d does not do what it says.** `matzov.Nf is MATZOV.Nf` is **False** in
CPython (each classmethod access builds a fresh bound method). `compare.py:222`
actually evaluates `==`, which is True and is the correct test. Description and
code disagree. Conclusion unaffected — KA-0a covers it. Defect 9.

---

## 3. The vector-null — does each null remove only the object it names?

### NULL-V

Paired arms, my own error batch shared between them:

| arm | mean | sd over e | iid sd | inflation | N_eff |
|---|---|---|---|---|---|
| sieve database | +0.400664 | 0.084160 | 0.004400 | 365.9× | 49.0 |
| random dirs, matched ‖x‖ | +0.400609 | 0.083975 | 0.004400 | 364.3× | 49.2 |

**Paired sd ratio 0.9978** against the producer's 0.9974. That ratio is the
load-bearing quantity and it reproduces to 0.04%. My absolute sds sit 4.4% below
the producer's, which is ordinary Monte-Carlo variation for an sd estimated from
1000 draws of a heavy-tailed scalar.

**Does it remove only what it names?** Yes, and the naming is honest. Removed:
lattice membership, integrality, the exact 3-term relations, ball saturation —
all four named. Preserved: `N`, `m`, `q`, `σ_e`, and the exact empirical ‖x‖
distribution (each surrogate carries the norm of the vector it replaces), so `a_x`
is identical by construction — I checked it is byte-identical between arms. The
surrogate additionally removes *integrality of the phase* by being real-valued,
but integrality is explicitly listed in `removes_object`, so the null is not
silently coarser than advertised. And since the correct candidate is scored,
`Dphase = 0` and the y-part is irrelevant to both arms — genuinely apples to
apples. `can_it_fail: YES`, correctly.

### NULL-IID

```
mean +0.407374   sd 0.004353   iid 0.004417   inflation 0.97×   N_eff 18454 vs N 17919
```

Removes only the shared `e`; the database is untouched. Decisive, and it is what
turns NULL-V from "the surrogate agrees" into "the mechanism is identified."
`N_eff` exceeding `N` by 2–3% is inside the ~4.5% relative error of an `N_eff`
from 1000 draws.

### The analytic model — I re-derived it rather than checking arithmetic

For a family spread over directions, `S(e) ≈ mean_i exp(−2π²‖x_i‖²‖e‖²/(q²m))`,
so `S ≈ exp(−a_x‖e‖²/(mσ²))`; with `Var(‖e‖²) = 2mσ⁴` this gives
`sd(S) = S·a_x·√(2/m)`, **manifestly independent of N**. Numerically
`0.403821 × 0.890209 × √(2/35) = 0.085932` against the producer's 0.085933.
My own m-sweep model tracks my own measurement to 1.1 / 1.7 / 1.2 / 1.8 % at
m = 35 / 70 / 140 / 280.

### The sweeps

```
m-sweep  N_eff  43.8 /  90.7 / 184.4 / 353.0   (producer 44.9 / 93.8 / 173.8 / 349.7)
         N_eff/m 1.25 /  1.30 /  1.32 /  1.26
N-sweep  N_eff  42.6 /  46.7 /  45.4 /  42.0 over N = 1000 … 60000   (60× range)
```

Linear in `m`, independent of `N`. The `N`-independence is the discriminating
prediction — it is the one that would have failed had the inflation been a genuine
loss of independent samples. It didn't.

Scope note, not a defect (the producer states the preservation explicitly): the
m-sweep varies the *surrogate* at m > 35 while reusing the m = 35 measured norms,
so "N_eff linear in m" is a property of the surrogate model plus the m = 35
equivalence from NULL-V, not a measured property of sieve databases at larger m.

### NULL-T

Labelled `can_it_fail: NO`, which is unusually honest and correct — with `b`
uniform, `x·b` is uniform mod q for every fixed nonzero `x`, so any code that
reads `b` passes. Reproduced anyway; my group means +0.000036 / +0.000174 /
+0.000306 against the producer's +0.000001 / −0.000175 / −0.000206.

---

## 4. The two batch-1 corrections

### #1 — OBS-6's `9 of 9, z = −2.31`: **UPHELD, and I can sharpen it**

My 1000 fresh uniform targets give mean rank **4.910 ± 2.625 of 9**, reproducing
the producer's 5.051 ± 2.571. Mid-pack, as a null must be.

But the producer stops at "single-draw fluctuation." I measured the thing that
names *why the statistic was wrong*:

```
P(all 8 secret-shaped candidates beat the nominal secret in one draw) = 0.1020  (1000 draws)
```

Under the null the nominal secret and the 8 secret-shaped candidates are
exchangeable, so `P(nominal ranks last) = 1/9 = 0.1111`. My 0.1020 is that value.
**Batch 1 observed a one-in-nine event and scored it as z = −2.31, a
one-in-a-hundred event**, by treating a rank-among-9 as approximately normal. The
observation was the null behaving exactly as a null must; the `z` was
mis-specified.

OBS-6's factual content ("the producer did not name this") stands. Its inferential
content does not. Superseding, not deletion — and not by me.

### #2 — OBS-4's `~20% unreported uncertainty`: **UPHELD, understated, and it only reclassifies half of OBS-4**

The producer's 0.0041 across-instance spread is not a clean instance-variance
estimate; it still contains the Monte-Carlo error of a 500-draw mean. Decomposing:

| quantity | across-inst sd | MC floor √(⟨sd²⟩/500) | **genuine instance sd** |
|---|---|---|---|
| correct-secret mean | 0.004070 | 0.003880 | **≤ 0.00123** |
| ingredient-1 global ratio | 0.009684 | 0.009346 | 0.00254 |
| **ingredient-2 uniform sd ratio** | **0.052087** | **0.012009** | **0.05068** |
| near-miss delta vs best | 0.000043 | 0.000031 | 0.000030 |

Three consequences.

**(a) The correction is conservative.** The true instance-to-instance sd of the
correct-secret mean is ≤ 0.00123, so the ratio to the 0.089 per-draw spread is
≥ 70×, not 22×. The producer's 0.0041 is an upper bound not labelled as one.

**(b) It does not refute OBS-4's second clause.** "That uncertainty does not
shrink with N" remains true, and batch 2's own NULL-SWEEP *confirms* it —
`N_eff ≈ 44`, independent of `N` over a 60× range. Batch 2 does not claim
otherwise, but §7's framing invites the reading that OBS-4 was wrong. OBS-4 was
right, and was about a different thing.

**(c) The inference §7 draws from it is false for one quantity.** "Every ingredient
ratio in this report is therefore far better determined across instances than the
per-draw sd suggests" holds for three of the four rows above and fails for the
ingredient-2 uniform ratio, whose genuine instance sd is 0.0507 — four times its
own per-instance sem and 13× the per-draw sem quoted in §4.1. So §4.1's "accurate
to **0.2%**" is not supported; the supported statement is **1.00 ± 0.05**. That
number is disclosed in the same sentence ("across 10 instances (1.0021 ± 0.0521)")
but the headline is 25× tighter than the batch's own data allows. Defects 4 and 5.

---

## 5. The post-hoc corrections — principled or fitted?

### D1 (discretised error, Var 4.0833): **principled**

`compare.py:94` samples `np.rint(rng.normal(0, σ))`. I derived the exact law of
`round(N(0,2))` from first principles and got `Var = 4.083333333333334`, matching
4.0833. That is the exact variance of the distribution the code actually samples —
**zero free parameters, derived not fitted**.

The decisive test for fitted-vs-principled: the mean predicted advantage under the
exact discrete characteristic function is **0.4072111022**, and under a plain
continuous Gaussian at variance 4.0833 it is **0.4072133231** — agreement to five
decimals. So the entire effect is *one derived number*, the realized variance, not
a curve with knobs. It is a specification/implementation mismatch in the frozen
law, correctly identified.

My reproduction of the effect:

| prediction | decile ratio spread | trend corr | global ratio |
|---|---|---|---|
| frozen, continuous σ²=4 | 0.0115 | −0.977 | 0.9760 |
| exact discrete cf | **0.0030** | −0.629 | 0.9939 |

(producer: 0.0077 → 0.0028, corr −0.9695 → +0.7571). The shrinkage reproduces;
its exact factor is seed-dependent (3.8× for me, 2.8× for them).

**Caveat.** "The −1.8% common offset disappears entirely … A +0.15% residual
remains, unexplained" reports below the noise floor: the global ratio's sem at
2000 draws is 0.48%. My post-correction offset is −0.6%, also within ~1.3 sem of
zero, and the residual trend *changes sign* between our seeds. The correction is
real; the leftover is noise. Defect 6.

### D2 (`c4`): **principled**

`c4(n) = √(2/(n−1))·Γ(n/2)/Γ((n−1)/2)` — I reproduce `c4(16) = 0.983484` and
`c4(8) = 0.965030`. Textbook unbiasing factor, computed from `n` alone, not from
the data, applied identically to all three groups, with raw values reported
alongside. It cannot manufacture the near-miss departure (0.1447 → 0.1499 leaves
6.7× concentration).

Its normality/independence assumption is only approximately met — the candidate
scores within a draw share `e`. And it happens to move the uniform ratio *toward*
agreement (0.9814 → 0.9978), the direction that flatters the headline. Since the
raw figure is right next to it and the correction is 1.7%, that is a disclosure
caveat rather than a defect.

---

## 6. The near-miss departure — the control the producer did not run

This is the batch's declared live observation and it is the one signal with **no
null of its own shape**. NULL-V, NULL-IID and NULL-SWEEP are nulls for the
variance inflation of the *database mean*; none is a null for *concentration
across near-copy candidates*. The report also states no prediction for what the
near-miss ratio should do as the parameter meant to destroy it increases, which
`docs/inventor-protocol.md` §3 requires. And §10's PAC-1 identifiability
disclaimer is applied to the length sub-comparison but not to §4.3.

So I ran the decay check. Eight candidates at Hamming distance `h` from `s`,
500 draws each, c4-corrected sd ratio to `√(1/2N)`:

```
h= 1   0.146      <- reproduces the reported near-miss 0.1503
h= 2   0.213
h= 3   0.234
h= 5   0.325
h= 8   0.352
h=12   0.352
```

(`h = 25` degenerates — all eight candidates collapse to `s + 1` on every
coordinate, so the spread is identically zero. Uninformative, discarded.)

**The quantity does decay in the required direction.** It is therefore *not* the
canonical artifact tell, and the observation survives. But it also shows the
mechanism plainly: near-miss candidates are near-copies that share the same `x·e`
realisation, so their spread cannot be `√(1/2N)` — the same shared-error mechanism
NULL-IID isolated for NULL-V, restated on a different candidate population. That
connection is not drawn in §4.3, and the PAC-1 limitation (a matched-norm
random-direction family would plausibly reproduce the concentration too) is not
applied there either. Defect 7.

---

## 7. D-7 — the 4166-vs-4075 rebuild anomaly, settled experimentally

The producer's explanation is testable, so I tested it. I reconstructed the
`[C]+[D]` sequence exactly and ran it three ways in the producer's own rebuilt
venv:

```
mode=full      db=4166  0.88s  first=(-10, 3, -2, -4, 5, 1, 3, -5)
mode=seedonly  db=4166  0.91s  first=(5, -10, -3, -3, 0, 8, 0, -12)
mode=none      db=4075  0.95s  first=(3, 4, 0, 6, 2, 3, 0, 2)
```

- `full` = `FPLLL.set_random_seed(1)` → dim-60 qary draw → BKZ-30×4 → dim-50 draw
  → `gauss_sieve` with `seed=12345`. **Reproduces the producer's transcript
  exactly, db size *and* first-entry bytes.**
- `none` = no fpylll seeding at all, i.e. the recipe as written. **Reproduces
  `KN-TECH-14efa5`'s 4075 exactly.**

So the explanation is **established, not merely plausible**: the difference is
unpinned randomness in the recipe's own verification figure, consumed by the
preceding fpylll block. `KN-TECH-14efa5` does pin no seed for that check.

**One sub-claim is unsupported.** "The first database entry printed is
byte-identical to batch 1's …, so it is the same lattice family." My `none` run
gives 4075 with a *different* first entry, and `seedonly` gives 4166 with a
different first entry — identical first entries can accompany different db sizes
and vice versa, and one truncated 8-of-50 vector does not identify a lattice. Not
load-bearing.

**No measurement is contaminated.** `compare.py:137` sets
`FPLLL.set_random_seed(fpylll_seed)` and `:141` constructs
`Siever(Bred, SieverParams(threads=1), seed=sieve_seed)`, so the measurement pins
both of its own seeds, exactly as the producer states.

---

## 8. D-6 — is reusing batch 1's seeds sound?

The reuse is real: `instance 20260803001`, `candidates 20260803002`,
`sieve 469431436621`, `fpylll 20260803005`, identical to the seeds printed in
batch 1's own transcript. The primary database is the *same* 17,919 vectors.

Whether that inherits batch 1's idiosyncrasies is an empirical question, and §4's
decomposition answers it. For the correct-secret mean (genuine instance sd
≤ 0.00123 = 0.3% of the score), ingredient 1 (0.00254), and the near-miss delta
(0.000030, 1.9% relative), the choice of instance is immaterial — the design is
sound and the free reproduction check is a genuine bonus.

The exception is the ingredient-2 uniform sd ratio, genuine instance sd 0.0507,
where the primary instance is *not* interchangeable with an arbitrary one. As it
happens the primary's 0.9978 sits 0.04 instance-sd from the 9-instance mean of
1.00207, so it is a typical instance rather than a flattering one. The soundness
problem is not the seed reuse; it is quoting that ratio to 0.2%.

Verdict: **sound and adequately disclosed**, with independence genuinely supplied
by nine distinct-seeded replicates (20260803206 … 20260811206, all nine
certificates carrying 0 violating entries).

---

## 9. Things the producer did not declare

- `verify_instrument_f75059.py` — which produced the `[A]`–`[F]` block and the
  4166 figure — is **not among the seven archived artifacts**; only its stdout is
  in the transcript. I could exercise D-7 only because the file happened to
  survive in a session scratchpad outside the snapshot. A later reviewer cannot
  rely on that. Defect 8.
- `results.json` `S2.design_facts.candidates_differ_on_coordinates = 25` is a
  recorded design fact that the co-archived `vectors.json` falsifies for 19 of 33
  wrong candidates. Defect 2.
- The near-miss departure has no matched-shape null and no decay prediction, and
  §10's PAC-1 disclaimer is not extended to §4.3. Defect 7.
- KA-0d's description does not match its code. Defect 9.

---

## 10. Where I could not check

- **Batch-1 z-scores** (`report.md` §8, +0.22 / +0.14 / +0.22 / +0.27 / +0.12).
  These are z-scores of a fixed single draw against a *resampled* distribution;
  verifying them to two decimals needs the producer's exact 2000-draw stream,
  which I deliberately did not reuse. My independent resampled means and sds match
  to ~0.7% and 0.2%, which bounds every z shift below 0.1 — so "batch 1's
  realisation is unremarkable" is supported, and the specific two-decimal values
  are `unable_to_check`.
- **Replicate raw per-draw data** is not archived, only the per-instance summaries.
  My variance decompositions in §4 and §8 use the producer's reported per-instance
  mean and sd as inputs; the decomposition arithmetic is mine, the inputs are not
  independently regenerated.
- **The sieve database itself** I took as given — certified by me (0 violating
  entries of 447,975, 0 all-zero, 17,919 distinct y-parts, recomputed by integer
  numpy from `A` and `X` alone) but not regenerated, since regenerating it needs
  the producer's seeds and would defeat the independence I was asked for.

---

## 11. Independence limit, stated because it matters

Batch 1's producer, both its reviewers, batch 2's producer and I all resolve to
`claude-opus-5`, and no backend is probe-verified in this environment. The
producer discloses this itself in `receipt.json`
(`inference.independence_limit_note`), which is the right thing to have done.

My session, my seeds, my code and my reasoning are independent. The underlying
model is not. That matters least for the numerical recomputations in §§2–5, where
independent code either matches or does not, and most for §1.4 — the judgement
about what R1 and R2 *should* be is exactly the kind of modelling call a
correlated model is likely to make the same way twice. **A genuinely independent
check of the P1 modelling judgement remains outstanding.** I flag it rather than
let a matching conclusion pass for corroboration.

---

## 12. Verdict

**ADMISSIBLE_WITH_DEFECTS.** Ten numbered defects in `report.yaml`. Every
quantitative claim I could re-derive reproduced, from the archived raw data, on my
own seeds, with my own code — including all six known-answer controls, the KA-6
Kyber512 round trip at cryptographic parameters, the certificate, both post-hoc
corrections, all four nulls, both sweeps, the success curve, and every replicate
summary. The defects are scope, precision and control-completeness defects in how
results are *stated*. I found no fabrication, no manufactured tuple, no discarded
run, and no smoothed-over anomaly.

Admissibility is not promotion, and it is not an ML-KEM claim of any kind. Rule 12
is UNMET and UNWAIVED; no `EV-MLKEM-*` or `KN-*` status changes here.
