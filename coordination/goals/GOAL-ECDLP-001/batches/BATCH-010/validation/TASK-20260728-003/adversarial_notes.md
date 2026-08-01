# TASK-20260728-003 — adversarial notes on EXP-RT1476-001

**VAL-20260728-001 companion.** Independent, non-originating Validator session.
Snapshot 777b1e43 (`research/ecdlp-solve-20260727`), clean for every
EXP-RT1476-001 path.

Two reconstructions, in the order the handoff requires: first the strongest case
that the measured exponents mean what the Executor says they mean, then the
strongest case that they do not. Then which one I could not break, and the one
check a third party can run without a computer to decide between them.

Nothing here is evidence for or against ECDLP hardness. Nothing here assigns
evidence strength or changes a record status.

---

## Part 1 — The strongest case FOR the Executor's reading

The Executor's reading, stated as fairly as I can put it: *the backward 3-sum
state of the serial-S3 2|3 split over a random x-line factor base is generic at
three toy sizes — `beta_deg = 0.5985` against a gate of 0.3 and a generic
prediction of 0.6 — and the instrument that says so is calibrated, because the
same instrument returns 0.2034 on a factor base with a planted collapse.*

### 1.1 The primary metric is exact, not estimated

`backward_state_support_size` is not a fit, a sample, or a bound. It is the
cardinality of `{u : ∃ (x3,x4,x5) ∈ V³ closing the chain}`, computed by
exhaustive enumeration over `V³` using the group law — at most `28³ = 21,952`
chain evaluations at the largest size. I read the code (`backward_state_group_law`)
and re-executed it. There is no solver, no CAS, no tolerance, no convergence
criterion and no random sampling anywhere in it. If the group law is right, the
number is right. The group law is verified 3,191 times, by three independent
implementations, with zero failures.

This matters more than it sounds. Most experimental exponents in this repository
rest on a measurement that could in principle be wrong in a direction. This one
cannot be wrong in a direction; it can only be wrong outright, and three
independent group-law implementations agreeing 3,191 times bounds that.

### 1.2 The measurement survives every robustness cut I applied

Recomputed by me from the 27 `raw-result.json`, not taken from
`results_summary.json`:

| cut | main `beta_deg` |
|---|---|
| pooled, 3 size-points | 0.5985 |
| all 9 cells, OLS | 0.5987 |
| per seed | 0.5940 / 0.6053 / 0.5968 |
| pairwise | 0.5790 / 0.5978 / 0.6119 |
| drop p=1009 | 0.6119 |
| drop p=65521 | 0.5978 |
| drop p=16769023 | 0.5790 |
| success subset only | 0.5982 |

Total spread under leave-one-prime-out is 0.033. The gate is at 0.3. Every
variant clears the gate by roughly eight times the instability. Whatever else is
uncertain here, "not below 0.3" is not.

### 1.3 The positive control differs in exactly one respect, and I checked it mechanically

Not asserted — checked. For all nine `(p, seed)` cells, `main` and `posctl`
share `p`, `a`, `b`, `n`, the base point, `L`, `targets_screened = 1200`, the
`S_3` link polynomials coefficient by coefficient, the resultant routine, the
`FieldOps` counter, the module, the session and the machine. For every
`target_index` appearing in both arms' measured lists the `(r_scalar, x_R)` pair
is identical — 95 comparisons, 0 disagreements. The only differing input is `V`.

And the planted state really is `6L+1`. At `L=28`, **all 31** measured targets
return exactly 169. At `L=9`, 32 of 33 return exactly 55. At `L=4`, 29 of 30
failure targets return exactly 25. The exceptions are not noise: for a certified
success `R = [m]P` the index `m` lies in a window of size `O(L)`, so
`x([j]P) = x([-j]P)` folds two indices together whenever `k + k' = 2m`, which is
reachable at small `L` and not at `L=28`. The control behaves exactly as its
`concrete_construction` predicted, including where it deviates.

### 1.4 The whole run set reproduces

I re-executed five of the twenty-seven recorded commands — all three arms, all
three field sizes, including the 289-second largest cell — with the committed
module, into a scratch directory. `raw-result.json` is **identical** on
deterministic content in all five, and `certificates.json` is identical in full,
certificate for certificate. That simultaneously establishes seed integrity, that
the committed module is the executed module (which no manifest hash records), and
that nothing was hand-edited after the fact.

### 1.5 The anti-tautology rule genuinely held

The literals `0.3`, `0.6`, `0.2`, `1.5` appear **nowhere** in the 1,816-line
module. `sympy` appears ten times and not once inside `membership_query` or
anything it calls. The counter is three integers incremented inside a
hand-written GF(p) polynomial layer, reset per query. Every gate quantity is in
`raw-result.json`, not only in `stdout`. This is the exact opposite of the
EXP-GGM-001 failure that REV-20260727-002 demolished, and it was clearly built
in response to it.

### 1.6 The producer flagged its own weakest point

`analysis.md` caveat 1 says, in the producer's own words, that `beta_ops` is a
property of the declared query algorithm and that the red team's `Ω(q^{3/2})`
prior assumed an eliminant of degree `~q` which is not what was measured — and
labels it "the single most important thing for the Validator to attack."
Section 6 says outright that "a reader who reads `deg_u` as the backward-state
size would conclude that CTRL-POS shows no collapse, which is false." Section 5.2
says the measured abort speedup is essentially zero and why. An artifact that
names its own three most attackable points is not an artifact trying to get away
with something.

**Summary of the case FOR.** The main-arm `beta_deg` is an exact count, taken
under an instrument with a passing one-variable-different positive control and a
passing negative control, reproducing byte-for-byte, robust to every cut, with
no threshold visible to the measuring code and no wall-clock anywhere near the
counted path.

---

## Part 2 — The strongest case AGAINST

### 2.1 The experiment is not named after the thing it measured

The title is *"Subresultant-PRS backward-state degree meter."* The cost-bearing
path contains almost no subresultant PRS. `membership_query` loops over all `L³`
triples `(v3,v4,v5)`, computes two small resultants per triple, and evaluates the
resulting degree-8 factor at every forward value. `prs_remainder_degrees` — the
actual PRS — is invoked on the **first four** polynomial pairs per query
(`--prs-sample 4`) purely to record a remainder-degree sequence, and contributes
a constant, negligible share of the operation count.

So the experiment did not test subresultant PRS as a device for avoiding the
eliminant. It tested a brute-force enumeration over `V³`. That is a legitimate
membership query, and the run set is an honest measurement of it, but it is not
the object RT-1476-SUBRES-A1 is about.

### 2.2 The `beta_ops` gate could not have failed. Here is the derivation.

`membership_query` performs `L³` iterations. Each iteration computes at most two
resultants of polynomials whose degrees are bounded by 4 in the eliminated
variable and 2 in `u` — **bounded independently of `q`** — and then evaluates a
degree-8 polynomial at every element of the forward state. Therefore

```
ops_per_query  ≤  L³ · (c1 + c2·|F|)      with c1, c2 absolute constants.
```

I measured `|F| = L²` **exactly** on the main arm at all three sizes: 16, 81,
784. So

```
ops_per_query = O(L⁵) = O(q)     for any curve, any factor base, any q,
```

hence `beta_ops ≤ 1 + o(1) < 3/2`, **forced before any curve was sampled**.

The numbers confirm the model. Fitting `c1, c2` from the two *larger* sizes only
gives `ops = L³·(5428.5 + 15.9142·|F|)`, which predicts the smallest cell — held
out of the fit — to within 1.5% (363,723 predicted vs 369,134 measured). The
rising pairwise slopes are the crossover between the two terms becoming visible:

| pair | main `beta_ops` |
|---|---|
| p=1009 → 65521 | 0.6165 |
| p=1009 → 16769023 | 0.7158 |
| p=65521 → 16769023 | **0.7908** |

Monotone, and heading for 1.0, not settling at 0.72.

Three consequences, each of which a reader could get wrong:

1. **`beta_ops = 0.7197` is not an exponent.** It is a point on a crossover
   between `q^{3/5}` and `q^1`, which is why dropping the largest prime moves it
   to 0.6165 and dropping the smallest moves it to 0.7908 — a 0.174 swing, five
   times the `beta_deg` instability.
2. **Success criterion S2 ("`beta_ops < 3/2`") is met and carries zero
   information.** A gate that returns the same answer on every possible execution
   is precisely what REV-20260727-002 destroyed EXP-GGM-001 for. There the
   operands were two string literals in one source file. Here the threshold sits
   at 3/2 while the measured quantity is bounded above by 1 by the structure of a
   loop. The mechanism is different; the epistemic content is the same: nothing.
3. **The red team's prior was not tested.** `Ω(q^{3/2})` was a claim about
   subresultant PRS on a degree-`~q` eliminant. This measurement is of a
   different algorithm on a degree-`8q^{3/5}` object. It neither confirms nor
   refutes; it does not address.

The Executor's caveat 1 gets this right in substance — the eliminant is smaller
than the red team assumed, so the prior doesn't apply — but stops one step short.
The stronger statement is that the counted cost function is bounded by `O(q)`
*by the structure of the loop*, independently of the eliminant's degree at all.

### 2.3 One of the two quantities called `beta_deg` fails its own positive control

The specification defines `beta_deg` over **two** quantities:
`backward_state_support_size` *and*, separately, `deg_u_backward_eliminant`.
INVALID-4 then says "CTRL-POS does not report `beta_deg < 0.3`" without saying
which. They disagree:

| arm | support exponent | `deg_u` exponent |
|---|---|---|
| main | 0.5985 | 0.6009 |
| **posctl** | **0.2034** | **0.6056** |
| negctl | 0.6055 | 0.6004 |

`deg_u` is `8L³` exactly — 512, 5832, 175616 at `L = 4, 9, 28` — on **every
arm**, because the module computes it as `deg_sum`, the sum over `L³` triples of
each triple's degree-8 resultant. It is a count of non-degenerate triples times
eight. It is a function of `L` alone. Fitting an exponent to it recovers
`3 × (1/5) = 0.6` by arithmetic and could not have returned anything else.

On the positive control, where the reachable set has 169 elements, `deg_u`
reports 175,616 — an overstatement by a factor of **1039**. Read as a state-size
meter, `deg_u` fails INVALID-4 outright.

The consequence is not that the run set is invalid. It is that:

- success criterion S1's clause *"and, where available, corroborated by
  `deg_u_backward_eliminant`"* is **structurally unavailable**, not merely unmet;
- H-RT1476-001's second prediction (`deg_u` exponent below 0.3) is **untestable**
  by this instrument, not tested and failed;
- the `deg_u` exponent 0.6009 may not be cited in either direction.

### 2.4 The positive control proves less than "the meter is calibrated"

`V_pos = {x([i]P)}` makes the reachable index set an interval of `6L+1` integers.
So *any* correct implementation of "count the distinct `u` reachable over `V³`"
**must** return `6L+1`, and `6L+1` with `L = round(q^{1/5})` **must** fit to
0.2034. The value is arithmetically forced.

What the control genuinely excludes is a real and non-empty bug class — a support
routine that returns `|V|³`, or a constant multiple of it, or anything
insensitive to the structure of `V`. That is exactly the bug that would have
manufactured a false 0.6 on the main arm, so excluding it is worth having.

But `backward_state_support_size` is *defined* as the exact cardinality of the
reachable set and *computed* by exhaustion. A quantity computed exactly has no
sensitivity to calibrate. The only thing a control can add is a correctness
check, and that is what this one is. "The meter demonstrably resolves a planted
factor-`q^{0.4}` collapse" is true but flattering. The accurate statement is:
*the enumerator is not blind to the structure of `V`, and returns the true count
on an input whose true count is independently known.*

And the same control, applied to the other quantity carrying the `beta_deg`
name, fails. That is the informative half of CTRL-POS, and it is the half a
reader is most likely to miss.

### 2.5 The red-team amendment was honoured and is inert

`ops_success`, `ops_all` and `ops_failure` on the main arm give `beta_ops` =
0.7197 / 0.7195 / 0.7192. They agree to 0.0005. Per cell, the
success/failure ratio is 1.0000 at both larger sizes.

The reason is in the source: `membership_query` scans all `L³` triples
unconditionally with no early exit. A successful query and a failing query do the
same work by construction. The amendment — *fit on successes only, because early
abort helps only the non-relation fraction* — was correctly implemented on the
correct (certified, group-law) success set, and **could not have changed the
answer**, because there is no abort to exclude. Its protective function was never
exercised. That is not a fault in the implementation; it is a statement that the
single adversarial improvement the frozen contract ever received did nothing
here.

### 2.6 Three points, both slope sequences turning, and the smallest anchor is degenerate

`log q` spans 6.90 to 16.63, a factor of 2.4, on three points. Both pairwise-slope
sequences turn upward (`beta_deg`: 0.5790 → 0.6119; `beta_ops`: 0.6165 → 0.7908).
At `L = 4` the factor base has four elements and, by my count, **24% of that
size's certificates contain a proper sub-multiset of summands summing to the
identity** — i.e. the "5-term relation" is effectively shorter — against 0.9% at
the largest size, and all 43 certificates in the run set that contain the target's
own `x` among the summands are at `p = 1009`. The cell that anchors the low end
of every fit is the one where constants and degeneracies dominate.

### 2.7 The main-arm result confirms an elementary count rather than discovering an exponent

`support/L³` = 1.3573, 1.3507, 1.3353 → **4/3**. That is not an empirical
constant. The backward leg reaches `8L³` signed triples; the chain sum is
symmetric in the three factor-base points, so ordered triples collapse by
`3! = 6`; hence `8L³/6 = (4/3)L³` distinct `u`, and `beta_deg = 3/5` exactly.

This does not weaken the *test* — H-RT1476-001 asserted the count was wrong by a
factor of `q^{0.3}`, and it is not — but it bounds sharply what nine toy cells
and 1,797 seconds of compute added over one paragraph of arithmetic.

---

## Part 3 — Which one I could not break

**I could not break the case FOR, restricted to the support series.**

I tried three ways.

1. *Could the enumerator overcount?* It cannot. It builds a set and reports
   `len`. Over-reporting would require the group law to produce points that are
   not reachable, and the group law is verified 3,191 times against two other
   implementations. Under-reporting would show up on CTRL-POS, and does not.
2. *Could the main arm's 0.5985 be an artifact of the sample?* Nine cells, three
   independently sampled curves per size, per-seed spread 0.011, leave-one-prime-out
   spread 0.033, and the value sits on top of a closed-form prediction of 3/5. No.
3. *Could the fit be the wrong functional form?* Yes in general — three points
   cannot establish a power law, and the specification and H-RT1476-001 both say
   so — but it does not matter here, because the *conclusion drawn* is "not below
   0.3", and the raw ratio `support/L³` is within 2% of the generic constant at
   every single size independently of any fit at all.

**I did break the case FOR, as applied to `beta_ops` and to `deg_u`.**
`beta_ops`'s gate could not have failed (§2.2); `deg_u`'s exponent could not have
been anything but 0.6 (§2.3). Both are stated as measured outcomes in the run
package; neither is an outcome in any meaningful sense.

So the honest split is:

| series | survives adversarial reading? |
|---|---|
| main `beta_deg` on `backward_state_support_size` | **yes** |
| CTRL-POS / CTRL-NEG on the support series | **yes**, as a correctness check |
| `beta_deg` on `deg_u` | **no** — demonstrated-blind instrument |
| `beta_ops` on any subset | **no** — gate arithmetically unreachable |
| posctl `beta_ops` = 0.6223 | **no** — fitted across cells where INVALID-1 fires |

---

## Part 4 — The one check a third party can run to decide between them

**On paper, no computer, five minutes.**

> Count the backward leg. Over the x-line factor base `V` of size `L`, the
> backward 3-sum reaches the points `R ∓ P3 ∓ P4 ∓ P5` with `x(Pi) ∈ V`. That is
> `2³ · L³ = 8L³` signed triples. The sum is symmetric in the three summands, so
> each unordered triple is counted `3! = 6` times. If no further coincidence
> occurs, the number of distinct `u = x(·)` is `8L³/6 = (4/3)L³`.
>
> Then: with `L = round(q^{1/5})`, that is `(4/3)·q^{3/5}`, i.e.
> **`beta_deg = 3/5` exactly.**

Now compare against the committed raw files, which need only division:

| `p` | `L` | measured mean support | `support / L³` |
|---|---|---|---|
| 1009 | 4 | 86.87 | 1.3573 |
| 65521 | 9 | 984.68 | 1.3507 |
| 16769023 | 28 | 29312.43 | 1.3353 |

against `4/3 = 1.3333`.

**How to read the outcome.**

- If the paper count is right — and I could not fault it — then the main-arm
  measurement is a *confirmation* of an elementary count, the collapse
  H-RT1476-001 posits is absent for the elementary reason that there is nothing
  in the architecture to produce it, and no scaling study is needed to know that
  three toy sizes will keep reproducing `4/3`.
- If the paper count is wrong, the measurement is the more interesting object and
  the discrepancy between 1.3353 and the true constant is where to look.

The same third party can settle the `beta_ops` question just as cheaply:

> Read `membership_query`. Count the loop: `L³` iterations, each doing `O(1)`
> field work on polynomials of `q`-independent degree plus one evaluation per
> forward value. Read `|F|` out of any `raw-result.json` (`gate_values.forward_state_size`:
> 16, 81, 784) and observe `|F| = L²`. Then `ops = O(L⁵) = O(q)`, so
> `beta_ops ≤ 1`, so the pre-registered threshold of `3/2` could never have been
> crossed.

If that reading holds — and I confirmed it numerically to 1.5% on a held-out
cell — then **no experiment in this family can test the 3/2 gate**, and a
successor must first state, before execution, an upper bound on its query's cost
so the reachability of its own threshold can be checked in advance.

---

## Coda

The single most important thing not to conclude from this run set: **that
`beta_ops = 0.72 < 1.5` is a favourable signal.** It is not a signal at all. It
is the arithmetic of a loop that was chosen before any curve was sampled, and it
would have come out below 1.5 on a curve where the hypothesis was true, on a
curve where it was false, and on no curve at all.

The one thing that *is* a real measurement — `beta_deg = 0.5985` on an exact
enumeration, with a passing positive control and a matching closed-form count —
is adverse to H-RT1476-001 on the tested scope, and its scope is nine curves over
fields of at most 24 bits.

Neither of those statements is evidence about ECDLP hardness, and a validated run
set is not a validated conclusion.
