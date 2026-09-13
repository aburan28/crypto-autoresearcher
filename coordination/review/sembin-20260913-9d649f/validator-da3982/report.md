# Validator report — REVIEW-SEMBIN-20260913-9d649f

- **Task**: TASK-20260913-da3982, validator, `review-adversarial` at `xhigh`.
- **Joints owned**: J1 (Semaev's memory model) and J4 (the exponential-versus-polynomial
  mechanism of CLAIM B), plus the four `proves_too_much` objects.
- **Joints NOT owned and NOT read**: J2, J3, J5, J6 (TASK-20260913-cf9d98).
- **Blindness respected**: nothing under `coordination/review/sembin-20260913-9d649f/red-team-cf9d98/`
  or `.../blind-rederivation-ec11c4/` was read. Neither directory was listed or opened.
- **No whole-claim verdict is offered.** I can see two of six joints. A verdict on
  CLAIM A or CLAIM B from this report would be an opinion formed from a third of the
  evidence; the Coordinator composes.

My own working scripts are under `scratch/`: `j1_memory_model.py`, `j4_mechanism.py`,
`proves_too_much.py`, with their JSON output beside them. Every number quoted below is
reproducible by running them.

---

## J1 — Semaev's memory model

**The joint.** That peak memory of the chained-S₃ algorithm at (n, m) is
max(relation store, Gröbner working set), the store at 2^⌈n/m⌉ rows of (mk + 2n) bits and
the working set from the degree-4 Macaulay width of the chained system — dense reading
width² bits, sparse reading width bits. If this accounting is wrong, every crossover in
CLAIM A is wrong.

### (a) What the frozen text says is stored, and whether Galbraith's objection was answered

The paper gives **no memory model at all**. Section 3 defines the chain and its
decomposition step; Section 4.3 states eq. (11) and the yield; Section 4.5.2 costs
*time* as n^{4ω} under a block-structured Gröbner approach it does not implement
("We think the same approach is applicable"). No section states a working-set size, a
matrix layout, or a bit count for a stored relation. This absence is the whole reason
KN-OPEN-86e7e1 exists.

Both of the record's readings therefore come from **outside** the paper, and both come
from the same place: the recorded ePrint/ellipticnews exchange in KN-LIT-e77232, one from
each disputant. Galbraith's objection is the width² count; Semaev's answer is the sparse
estimate (nm)⁴/24 × n³/m. The plan's attack (a) asks whether that objection "was answered
with a count this record should be using instead" — it was, and **the record already uses
it**: `semaev_sparse` *is* Semaev's answer, and it is the reading that produces the 375
crossover and the +11.52 bits at n = 409.

I read KN-LIT-e77232 (an internal record, `provenance: internal`). I did **not** open the
blog thread itself, so my attribution of the two formulas to Galbraith and to Semaev is
relayed through that record and inherits its `retrieved` provenance, not a fresh reading.

The relation store is textually grounded: a relation is m factor-base indices of k bits
each plus the (u, v) pair at 2n bits, giving 2^k rows of (mk + 2n) bits, i.e.
log₂ = k + log₂(mk + 2n). At n = 409, m = 11: 38 + log₂(1236) = **48.27 bits**, which is
the record's figure.

### (b) Is the dense width² reading defensible, or a straw reading?

**I disagree with the Coordinator's prior. The dense reading is defensible, and it is not
a straw.** Four reasons, in increasing order of weight:

1. It is not offered as a best estimate. The manifest's `overestimating_factors_semaev`
   already says "the dense reading charges width² bits, which no implementation would use
   if the matrix is as sparse as Semaev claims." The record labels it an upper bound on
   its face.
2. It is one of the two positions of record in the dispute the run exists to adjudicate.
   Dropping it would leave the record reporting only the *defendant's* own memory estimate.
3. Structurally width² does overcharge — and I quantified it. The degree-4 Macaulay matrix
   of the chained system is far from square: with n(t−1) equations and N variables, rows
   sit **15.3 to 20.7 bits below** columns across n = 163…571 (at n = 409:
   log₂ rows = 24.00, log₂ cols = 43.42). An honest rows × cols dense accounting is
   therefore 19.4 bits cheaper than width² at n = 409. That is a real criticism of width²
   *as an estimate of the matrix*.
4. But the only memory measurements of this object that exist **refute rows × cols as an
   upper bound and do not refute width²**. Tables 1–2 of the frozen source carry 34 MAGMA
   memory measurements (27 non-trivial). Against them:

   | accounting | (model − measured peak), bits | upper-bounds every row? |
   |---|---|---|
   | record dense, width² | −1.66 … +6.99 | almost (fails 1 row by 1.7 bits) |
   | record sparse, Semaev's estimate | −5.62 … +0.73 | no |
   | rows × cols dense | −7.62 … **−0.17** | **no — fails all 27** |

   Measured peak memory lies **between the record's two readings in 21 of 27** non-trivial
   rows. Real F4 consumes more than a bare rows × cols matrix, which is what one would
   expect of a solver rather than a matrix. So width² survives contact with data that
   rows × cols does not.

The load-bearing caveat, which cuts against me and which I therefore state plainly: this
depends on reading the Tables 1–2 MB column as a **peak**, and `tables.yaml`'s own
`transcription_limits` says it is the **total over 100 systems**. I computed both and
picked neither. Under the total reading every model over-predicts (dense by up to 13.6
bits) and rows × cols becomes an upper bound too, so the discrimination above disappears.
The recurring exact 32.1 MB on six unrelated easy rows is the signature of a process
floor and hence of a peak, which is why I regard the peak reading as the more likely one —
but this is an inference, not a resolution, and it is a **contradiction between two
sources that I report rather than settle**.

### (c) The variable count N

**Re-derived independently, and the record is exactly right.** Two different sections of
the frozen text give the same count and both reproduce 2790, 4099, 6286:

- Section 4.5.1: x₁…x_t in the k-dimensional F₂-subspace V give tk Boolean variables;
  u₁…u_{t−2} in F_{2^n} give (t−2)n. So N = n(t−2) + kt.
- Section 4.2, at t = m: N = (m−2)n + km.

At (310,10), (409,11), (571,12) with k = ⌈n/m⌉ = 31, 38, 48 both give **2790, 4099, 6286**.
Agreement is exact, and these are the right counts for a t = m chain.

**A plan defect, reported because it will otherwise be charged to the code.** The plan
states N as `m*k + 2n` — in the J1 joint text (with an ellipsis) and, more consequentially,
without an ellipsis in the `blind_rederivation.parameters` block that TASK-20260913-ec11c4
is instructed to work from. `m*k + 2n` is **not** the variable count; it is the *relation
row width*, which the record uses for the store and `memory_charged_cost.py` names as such
at lines 23 and 627. The two differ by a factor of three in N and about **7 bits in
Macaulay width** at every FIPS cell:

| cell | N (record, correct) | N (plan's formula) | log₂ width | log₂ width, plan's N |
|---|---|---|---|---|
| 310, 10 | 2790 | 930 | 41.20 | 34.86 |
| 409, 11 | 4099 | 1236 | 43.42 | 36.50 |
| 571, 12 | 6286 | 1718 | 45.89 | 38.40 |

A re-derivation that follows the plan's parameters faithfully will get a crossover
**below** 375 and the disagreement will localise to one of the two implementations, when
its actual cause is the plan's parameter statement. Recognising that signature in advance
is worth more than discovering it afterwards. (The plan's sparse description, "one field
element per nonzero", is also not the record's `semaev_sparse`, which is Semaev's
(nm)⁴/24 × n³/m.)

### (d) MAX rather than SUM

**Defensible, and immaterial.** The working set dominates the relation store at every FIPS
cell under both of the record's readings — at n = 409, 86.84 (dense) or 66.53 (sparse)
against 48.27 — so max and sum differ by **0.0 to 0.0005 bits**. Even under the sparsest
accounting I could construct (nonzeros with a column index, 50.64 bits at n = 409, only
2.4 bits above the store) the gap is 0.26 bits. The phase-overlap question the plan raises
is real, is disclosed in the manifest's `overestimating_factors_semaev`, and cannot move
any crossover. Nothing here needs resolving.

### J1 findings

- **F1 (disagreement with the prior).** The dense width² reading is defensible as a
  disclosed upper bound and is not a straw. The 435 crossover and the n = 409 flip do not
  fall. Note the plan's stated consequence — "only the 375 survives, which would REMOVE
  the n = 409 flip" — is what my finding *avoids*, so this is the opposite of the outcome
  the Coordinator expected.
- **F2 (limitation, direction: record understates Semaev).** CLAIM A calls the swing one
  "between two defensible storage readings", but the family of defensible accountings is
  wider than two and is asymmetric about zero. At n = 409 under (time × memory):
  record dense **−8.79**, rows × cols dense **+10.62**, record sparse **+11.52**,
  nonzeros-with-index sparse **+21.96**. Three of four put Semaev ahead; the one that does
  not is the loosest upper bound the record itself labels overestimating. Crossovers span
  **344 to 435**, not 375 to 435. "Straddling zero between two defensible readings" is
  true but selective, and the selection is *unfavourable* to Semaev.
- **F3 (validation gap).** The frozen source carries 34 memory measurements of this exact
  object and the record's memory model is never compared against any of them. They are the
  only such measurements at any scale. The comparison is cheap, it is the natural control
  for a memory model, and it happens to *support* the record's bracketing.
- **F4 (unvalidated extrapolation, undisclosed).** The gap between the record's two
  readings widens with N: about 7 bits at N ≈ 50, where the measurements are, and 19–21
  bits at N = 2790…6286, where the claims are. The record does not disclose that its
  bracket widens with the parameter, so a reader cannot tell that the 46.6-bit swing at
  n = 409 is mostly an extrapolation of a gap last observed at a seventieth of the scale.
- **F5 (Assumption 1, already disclosed).** All of the above is at degree bound 4.
  Section 4.4 says d_F4 generally exceeds 4 when k > ⌈n/m⌉, and KN-LIT-e77232 records
  Kosters reaching degree 5 at n = 45. The record discloses this and tables the cost
  (+19.4 bits at degree 5 at n = 409). I add only that the single real-world anchor in the
  corpus — 126 GB at n = 45 — was at degree **5**, so it cannot test a D = 4 model, and I
  did not use it as one.

### Does the declared breaking artifact fire?

J1's breaking artifact is "a memory accounting derived from the frozen text that differs
from the record's by more than 5 bits at any FIPS label". My rows × cols accounting differs
from the record's dense by **19.4 bits at n = 409**, so the trigger is met on its face and
I report it rather than argue it away. My own reading of it, for the Coordinator to weigh:
this is a *third accounting* alongside a disclosed upper bound and a disclosed lower one,
not a correction of a mis-stated quantity — and the Tables 1–2 data, under the peak
reading, refutes it as an upper bound while sustaining width². The second limb, "a
demonstration that the dense reading has no textual basis, which retires the 435
crossover", does **not** fire: neither reading has a basis in the paper, both have one in
the recorded dispute, and retiring width² would leave only the defendant's own estimate.

### Verdict — J1: **holds**

The accounting is right where it is checkable: N is exact, the store is textually grounded,
max-versus-sum is immaterial, and the dense reading is a legitimate disclosed upper bound
rather than a straw. It holds **with F2, F3 and F4 recorded as limitations** — the reported
range is narrower than the defensible family and selected unfavourably to Semaev, the
model was never checked against the 34 measurements in its own frozen source, and the
bracket's widening with N is undisclosed. None of these makes a crossover wrong; all three
bear on how CLAIM A should be *stated*.

---

## J4 — the exponential-versus-polynomial mechanism

**The joint.** That under eq. (11), P = 1 − exp(−2^{tk−n}/t!), shortening the chain from
t = m to t < m costs yield exponentially in n while every available solving-cost saving is
polynomial in n, so no t < m can pay.

### (a) Yield-loss scaling, re-derived, and the regime boundary

Write A(t) = 2^{tk−n}/t!. Then

    A(t−1)/A(t) = 2^{−k} · t,

so in the regime A ≪ 1, where eq. (11) linearises to P ≈ A, **one unit of t costs exactly
k − log₂ t bits of yield**. Cumulatively from m down to t that is (m−t)k − log₂(m!/t!),
which at k ≈ n/m is ≈ **n(1 − t/m)** — linear in n *in the exponent*, i.e. exponential in
n. This is the record's characterisation and it is correct. I derived it from eq. (11) as
stated in Section 4.3 without reading the implementation, then checked it numerically:
the analytic k − log₂ t matches the exact eq. (11) difference to 1e−6 at nearly every step
and to **0.346 bits in the worst case over the whole swept range**.

The regime boundary is where A ≳ 1 and P saturates, at which point shortening is free.
Since k = ⌈n/m⌉ gives mk − n ≤ m − 1 while log₂(m!) > m − 1 for m ≥ 4, A < 1 **already at
t = m**, and falls by a further factor 2^{−k}·t per unit of t. Sweeping every
(n, m, t) with n ∈ [250, 600], m ∈ [2, 20], 2 ≤ t ≤ m:

- **saturated cells (log₂ A ≥ 0): 0.**
- maximum log₂ A over the entire range: **−1.0 exactly**, attained at (n, m, t) = (250, 2, 2)
  and at every even n with m = t = 2.

So **no (n, m, t) in the swept range sits in the regime where the argument's premise
fails.** The closest approach is within 1 bit, at the m = 2 corner, where A = 1/2 and
P ≈ 0.39 — and that is precisely where the linear yield law is least accurate, which is
the source of the 0.346-bit worst-case error above. It does not matter: m = 2 is never
optimal (m\* is 9–12 at these n). The premise holds throughout, and the record's
"exponential" is earned rather than asserted.

### (b) "2–3 bits per unit of t", against both readings — and is any reading exponential in (m − t)?

Verified against both, and the figure is right **but mis-stated**. At t = m, per unit of t:

| reading | saving at t = m | maximum over t | at n = 409 |
|---|---|---|---|
| `macaulay4` | 2.26–2.59 bits | **31–32 bits** (at t = 3→2) | 2.26 at t = m |
| `f4_std` | 2.04 bits | **12 bits** (at t = 3→2) | 2.04 at t = m |
| `block_n4w` | **0** | 0 | identically t-independent |

So "2–3 bits per unit of t" is the **local derivative at t = m for m ≈ 10–12**, not a bound
over the range of t. Ten to fifteen times that is available near t = 2. The record's
phrasing invites a reader to treat it as uniform, and it is not.

**No reading is exponential in (m − t)**, which is the question that decides the joint. I
checked the increments directly at n = 409, m = 20: the per-unit saving as t decreases runs
42.4, 11.3, 6.8, 4.9, 3.8, 3.1, 2.6, 2.3, 2.0, … — **decreasing, not increasing**. The
cumulative saving grows like log(m − t), so the cost *ratio* is polynomial in (m − t).
An exponential saving would need increasing increments. None of the three readings has
them, and `block_n4w` has none at all. The declared breaking artifact — "a solving-cost
reading, drawn from the frozen text, under which the saving is exponential in (m − t)" —
does **not** fire.

**One disclosure the record owes.** Under `block_n4w`, the record's own headline reading
for the memory-charged run, the solving cost does not depend on t *at all*. Under that one
reading t\* = m\* is trivially forced by the yield term alone, and CLAIM B carries no
information. The non-trivial content lives entirely in `macaulay4` and `f4_std`, where the
t-dependence is real and the exponential-beats-polynomial trade is genuinely resolved.
CLAIM B says the result holds "under all three solving-cost readings", which is true and
slightly flatters itself: one of the three cannot fail.

### (c) Reconciling Semaev's "drops dramatically" with "2–3 bits"

**Reconciled, and they are consistent.** Section 3 step 3's "drops dramatically" and the
record's "2–3 bits" describe different points of the same curve, and Tables 1–2 let me
check which. The measured solving-time drops per unit of t, read off the frozen tables:

| n, m | step | measured drop | `macaulay4` predicts | `f4_std` predicts |
|---|---|---|---|---|
| 19, 3 | t=3→2 | 13.87 bits | 18.74 | 12.00 |
| 21, 3 | t=3→2 | 13.78 bits | 19.20 | 12.00 |
| 15, 4 | t=3→2 | 8.52 bits | 20.34 | 12.00 |
| 16, 4 | t=4→3 | 8.33 bits | 9.42 | 7.02 |
| 15, 5 | t=5→4 | 3.75 bits | 6.22 | 4.98 |

Measured drops span **3.75 to 13.87 bits** and are bracketed by the two model readings.
Every measured point has m ≤ 5 and reaches t = 2 — the far end of the curve, where the
per-unit saving is large under the models too. "Dramatically" is Semaev describing t well
below m at small m; "2–3 bits" is the derivative at t = m for cryptographic m. Both are
correct. The reconciliation is that **the record quoted a derivative as though it were a
range**, and the measurements confirm the derivative is not the range.

### (d) Does the optimizer genuinely vary t?

**Yes, established four independent ways.** A bug that ignored t would produce t\* = m\*
everywhere and pass the run's own known-false control, so this needed positive evidence,
not absence of failure.

1. **Independent optimizer.** I wrote one from the published formulas without importing
   `joint_balance.py`. It reproduces t\* = m\* at every n ∈ [250, 600] under all three
   readings, and its m\* under `macaulay4` (7, 7, 9, 10 at n = 283, 310, 409, 571) matches
   `jb.optimize` exactly.
2. **No-yield null.** Deleting the yield term moves t\* from m to **2** at every n. If t
   were ignored, nothing could move it.
3. **Targeted probe.** Charging 400 bits for every t except one target returns **exactly
   that target** — t = 2, 3, 5, 7 all recovered, 19 distinct t evaluated per solve.
4. **Object 4** (below): under a cost where shortening pays, t\* moves from m\* to 2, a
   swing of 28 links, at a threshold that matches the yield law 5/5.

The declared breaking artifact "a demonstration that the optimizer does not genuinely
sweep t" does not fire. t\* = m\* is a result, not a fixed point of the code.

### J4 findings

- **F6 (published number is wrong; direction: understates the record's own case).** CLAIM B
  and the manifest state yield loss as "25 to 28 bits per unit of t at the FIPS labels".
  Re-deriving k − log₂ t at the manifest's own m\* (283:9, 310:10, 409:11, 571:12) gives
  **28.27, 27.68, 33.72, 44.00** — a range of **27.7 to 44.0 bits**, not 25 to 28. The
  published range covers only the two smallest FIPS labels and understates n = 571 by
  16 bits. Cause: `exponential_vs_polynomial_argument()` hardcodes `m = 10` regardless of
  m\*, and the quoted range is taken over a subset of its rows. The error runs *against*
  the record's own conclusion — a larger yield loss makes t = m more strongly optimal — so
  it is conservative, but it is a wrong number in a headline mechanism statement.
- **F7 (published field is inverted).** `raw-result.json`'s `mechanism.per_n[*].best_t_by_net`
  reports **3, 3, 2, 2**. Those are the t at which shortening is *worst* (net cost 139 to
  370 bits) reported as best; the correct answer is t = 10 (net 0). Cause: an argmax/argmin
  sign error, `min(per_t, key=lambda r: r["net…"] * -1)`. The sibling field name
  `net_bits_negative_is_worse` is also inverted — its values are positive-is-worse — and
  the manifest's "The net is negative at every t < m" inherits that. The *substance* is
  right (shortening is a net loss at every t < m; I confirmed this independently); the
  published sign convention contradicts it. As it stands, `raw-result.json` carries
  `best_t_by_net: 2` directly beside `consequence: t = m is optimal`, so a reader meets a
  self-contradiction in one object.
- **F8 (presentational).** "2–3 bits per unit of t" is the derivative at t = m, not a bound
  over t; the true maximum is 31–32 bits (`macaulay4`) or 12 (`f4_std`). See (b) and (c).
- **F9 (disclosure).** Under `block_n4w` the solving cost is t-independent, so t\* = m\* is
  vacuous under that reading. "Under all three readings" should say so.

Per AGENTS.md, **an implementation defect is never a mathematical conclusion**: F6 and F7
are defects in *summary and reporting* code. I checked that they do not propagate.
`optimize()`, `crossover()` and `stage_costs()` are independent of
`exponential_vs_polynomial_argument()`; my own from-scratch optimizer agrees with
`jb.optimize` on m\* and t\* at every n and every reading; and the crossovers (302, 367,
408) and t\* = m\* table do not consume the defective function. The mechanism is sound and
its published quantification is not.

### Verdict — J4: **holds**

Every load-bearing step of the mechanism survives independent re-derivation. The yield loss
is exponential in n at k − log₂ t bits per unit of t; no cell in the swept range reaches the
saturation regime that would break the premise (max log₂ A = −1.0, zero saturated cells);
no solving-cost reading in the frozen text is exponential in (m − t), all having *decreasing*
per-unit increments; Semaev's "dramatically" and the record's "2–3 bits" are reconciled by
the measured drops in Tables 1–2; and the optimizer demonstrably sweeps t. None of the three
declared breaking artifacts fires. It holds **with F6 and F7 recorded as published-number
defects requiring correction, and F8 and F9 as scope statements the claim owes** — and, as
the Coordinator's prior anticipated, the honest statement is scoped to "under the published
yield law".

---

## Proves-too-much objects

All four executed; full detail and per-cell numbers in `proves-too-much.json`.
**No object failed.** All four returned the answer that refutes their known-false
statement.

| # | object | required | observed | met? |
|---|---|---|---|---|
| 1 | n = 163 | Semaev loses under every metric and both storage readings | loses in **all 8** cells, by 42.4 to 73.9 bits; loses at every printed Table 3 n < 300 | yes |
| 2 | eq. (4), unchained S_{m+1} | catastrophically worse | worse by **1957 to 5977 bits**, re-derived independently from Section 2's degree 2^{m−2}-per-variable statement | yes |
| 3 | free-yield null, P ≡ 1 | crossover must move **DOWN** | **every** cell moves down: 435→339, 375→265, 303→250 (×2); margin at n = 409 improves for Semaev in all four | yes |
| 4 | solving cost exponential in (m − t) | t\* must come in **below** m\* | t\* drops below m\* at some n at 10 bits/link and at **every** n at 20 bits/link, moving from m\* to 2 | yes |

Objects 3 and 4 were not run by the producer in this form and are the two that matter.

**Object 3.** I deleted exactly the factor 1/P = m!·2^{n−mk} from stage 1 — the two terms
log₂(m!) + (n − mk) — and nothing else. Crossovers moved down in all four (metric, storage)
cells, by 53 to 110 in n, and the n = 409 margin improved for Semaev in each. I also
reproduced the shifts (435→339, 375→265) in my own implementation. **The sign convention is
not inverted.** This is the one failure mode no amount of agreement between the producer's
two implementations could have caught, since both share the convention, so it is worth
stating that it was checked and passed.

**Object 4, with a correction to my own work.** My first pass implemented the plan's object
with the wrong sign — charging c·(m−t) as a *penalty* for shortening rather than a reward —
and consequently could not move t\* below m\* at any rate, which would have read as the
object failing. The plan's object is a model in which "shortening the chain MUST pay", so
the saving is exponential in (m − t). Corrected, the object goes through. I ran both signs
and report both: under the penalty sign t\* stays pinned at m\* at every rate to 120 bits,
as it must. **The failure was mine, not the producer's optimizer's**, and it is recorded in
`proves-too-much.json` rather than quietly fixed.

The threshold is the object's real payoff. At 10 bits/link, t\* flips at n = 250 and 300 but
not at 409, 500, 571 — and that exact pattern is predicted by the yield loss per unit of t
at the m the patched optimizer lands on (n/30 − 1 = 7.3, 9.0, 12.6, 15.7, 18.0 bits, flip
iff below 10): **5/5 match**. The optimizer is trading precisely the two quantities the
mechanism says it should, at the rate J4 derives independently. I repeated the object under
`macaulay4`, where the solving cost genuinely depends on t, with the same outcome.

One caveat, stated because it limits what object 4 shows: under the patched cost the
optimizer runs m to the m_hi = 30 grid boundary and takes t = 2, so t\* < m\* is reached at
a **corner in m** rather than an interior optimum. That is a property of a deliberately
unphysical cost, not of the record. The object asks only whether t can move at all, and it
moves by 28 links.

**On object 2's discriminating power.** It passes by 1957 to 5977 bits. A control that
passes by two thousand bits cannot detect a cost model that is wrong by fifty, so it
confirms almost nothing beyond that the machinery has the right *sign* on the paper's
central contribution. I record this because the manifest counts it among six passing
controls and it does not carry a sixth of the weight. (D1 in the manifest already records
that eq. (4) is a substitute for the specified prime-field control, and that the
prime-field control remains owed; my point is narrower and about power, not substitution.)

---

## What I re-derived myself, and what I took on trust

**Re-derived independently** (from the frozen text and the published formulas, not from the
producer's implementation):

- N = 2790, 4099, 6286, from two different sections, both agreeing.
- The relation store, k + log₂(mk + 2n) = 48.27 bits at n = 409.
- Macaulay rows and columns separately, hence the rows/cols ratio (−15.3 to −20.7 bits) and
  a rows × cols accounting.
- Three memory accountings the record does not offer, and their crossovers (376, 344).
- The Tables 1–2 empirical comparison — 27 non-trivial rows, three accountings, both
  readings of the MB column. The record does not contain this comparison.
- eq. (11)'s yield-loss law k − log₂ t, analytically and numerically, and the regime
  boundary (max log₂ A = −1.0 over the full sweep).
- Per-unit and cumulative solving savings under all three readings, and the increment
  sequence establishing log(m − t) growth.
- The measured solving-time drops in Tables 1–2 (3.75–13.87 bits).
- A complete optimizer over (m, t), agreeing with `jb.optimize` on m\* and t\* at every n
  under all three readings.
- The correct value of the manifest's yield-loss range (27.7–44.0, not 25–28).
- Objects 1–4, and objects 2 and 3 twice — once through the producer's machinery and once
  through my own.

**Taken on trust** (checked for consistency, not re-derived):

- The 36/36 Table 3 reproduction and the 302 baseline crossover. J5 owns the fit; I did not
  re-fit c.
- The baseline side entirely — 0.886·2^{n/2}, store_log2 = 30, 3n bits per point. That is
  J2's, and every crossover I quote inherits whatever is true of it.
- The matched-null attribution (share = 0) and the ceiling-discrepancy table.
- Digests, environment capture, and determinism claims. I did not re-execute the runs from
  scratch, so `artifact-digests.json` is unverified by me.
- Semaev's Assumption 1 at every costed (n, m), and Assumption 2, which no verdict here
  touches.
- That Galbraith authored the width² count and Semaev the sparse estimate — relayed through
  KN-LIT-e77232; I did not open the blog thread.

## Limits of this report

I own two of six joints and offer no verdict on either claim. Everything above is
conditional on the baseline charging (J2) and on the metric set (J3) being sound, and both
are somebody else's. My J1 verdict turns on a reading of the Tables 1–2 memory column that
the frozen source's own transcription note contradicts; I computed both readings and picked
neither, and a Coordinator who resolves that ambiguity the other way should expect F1 to
weaken to `inconclusive`. Confirming an accounting is not evidence that the algorithm
works, and nothing here bears on the security of any curve in either direction.
