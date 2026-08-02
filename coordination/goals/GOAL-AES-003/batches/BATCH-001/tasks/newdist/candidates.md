# Candidate distinguishers for reduced-round AES-128 that are not the measured objects

Session role: Idea Generator. Scratchpad only. **Nothing here is a claim about AES
security, a distinguisher that exists, a key recovery, a speedup, or a barrier
statement.** No ledger record is written, no hypothesis status is changed, no
compute was run this session. Machine-readable companion: `candidates.yaml`
(same directory).

---

## 0. Epistemic preamble — read before using anything below

**0.1 No parser was available.** This subagent session has no `Bash` and no
code-execution tool, so `candidates.yaml` **could not be run through a YAML
parser**. Three prior passes shipped unparseable YAML; I could not verify mine
by execution and I will not claim I did. What I did instead is write in the most
conservative YAML subset available: every scalar single-quoted, no scalar
containing an apostrophe, a newline, or a block indicator; no block scalars, no
anchors, no aliases, no flow collections, no tabs. The specific defect that
broke `rr78/candidate_report.yaml` — a block sequence followed by a mapping key
at the same indentation — does not occur here because no node in the file is
both. **Treat "parses" as unverified until someone with a parser runs it.**

**0.2 No literature.** No primary source is reachable. No `WebSearch` was run.
Every recalled fact carries an `unverified-from-memory` tag and a recall
confidence, and **no recalled figure is used either to promote or to dismiss any
candidate** — dismissing from recollection is the same fabrication as promoting
from it, and is additionally premature closure.

**0.3 Zero compute.** Every quantity marked *derived* below is an algebraic
statement I worked out in-session from the pinned AES structure and which is
exhaustively re-checkable on this machine in seconds. Every quantity marked
*measured* is measured in a cited prior record of this repository, never here.
No gate outcome is reported, predicted-as-observed, or implied.

**0.4 The two failure modes I am steering between.** Overclaiming, and the
withdrawn-closure shape: a density measure reading 0.4995 on a random function
against 0.4996 on AES. Every candidate below therefore states, explicitly,
whether it has a **deterministic** statistic (no detection floor) or a
**statistical** one (floor stated in bits, on the same line as any null it
reports).

---

## 1. What the campaign has measured, and what "structurally new" has to mean

Two shapes, both cited rather than recalled:

| measured object | depth | shape |
|---|---|---|
| 1-byte delta-set balance | 3 | one-directional, degree-bounded |
| full-diagonal 2^32 integral | **exact through 4, dead at 5** | one-directional, degree-bounded |
| per-cell key influence bias | null from 4 | one-directional |
| mixed-space pair count mod 8 | null at 4,5,6 at 1 trial/arm, **producer declined to call it refuted** | counting residue |
| yoyo word-exchange orbit | **12–17× at 5, dead at 6** | adaptive two-directional |

The yoyo's own measured properties are the sharpest constraint on what a new
object must avoid: strictly all-or-nothing (graded ratios 0.9999 / 0.9998 /
0.9951 at 1/2/3 zero bytes), and **iteration provably cannot amplify it because
the A-step is an exact involution**. Any quartet-shaped candidate I propose must
say why that argument does not transfer to it, or it is the yoyo again.

---

## 2. The derivations this session actually produced

All in the pinned convention (final round drops MixColumns; `SR(x)[t][c] =
x[t][(c+t) mod 4]`; `CW[j]` = inverse-SR diagonal = the SR-image of column `j`;
`CW[0] = {0,13,10,7}`, which matches the yoyo6 pre-registration's definition —
a deliberate cross-check, since getting `CW` wrong once produced a false null
upstream).

Write `Delta_i` for the state difference after `i` **full** rounds.

**D1.** ShiftRows carries the diagonal space `D_0` onto column space `C_0`, so a
plaintext *difference* in `D_0` gives `Delta_1` supported inside column 0.
This needs only the **difference** to lie in `D_0` — **not** that the text set
is a full coset. Everything below therefore survives restriction to an
arbitrary **subset** of a diagonal coset. *This is why the gates are cheap, and
it is exactly why the `A5` sub-coset defect that broke `gate-rr78` cannot apply
here:* `A5` is about the image subspace of the text **set**; these statements
are about **differences**.

**D2.** Every MixColumns entry is nonzero, so `MC` of a weight-1 column vector
has weight exactly 4 and lies on the `GF(2^8)`-line spanned by the corresponding
MixColumns column.

**D3.** If `Delta_0 ∈ D_0` is nonzero, `Delta_1` is supported in column 0 with
weight `w ≥ 1`, and **`Delta_2` has exactly `w` FULLY active columns** —
SubBytes preserves support, ShiftRows sends the `w` active bytes of column 0
into `w` distinct columns one byte each, and D2 then fills each of them.

**D4.** Column `j` of `Delta_3` is zero iff the four bytes of `Delta_2` at
positions `(t, (j+t) mod 4)`, `t = 0..3`, are all zero. Those four positions lie
in **four distinct columns** of `Delta_2`. By D3 at least one column of
`Delta_2` is fully active. **Hence no column of `Delta_3` is zero.**

**D5.** The `r`-round ciphertext difference is zero on `CW[j]` iff column `j` of
the difference entering the final SubBytes is zero — SubBytes is bytewise
bijective, so it preserves the zero set of a difference *exactly*, and ShiftRows
carries column `j` onto `CW[j]`. **At `r = 4` that difference is `Delta_3`, so
by D4 the event is impossible** for every pair whose plaintext difference lies
in `D_0`.

**D6 — the ladder.** The *same* statistic at `r = 3` is "column `j` of `Delta_2`
is zero", which holds whenever `w < 4`, i.e. very often; at `r = 2` it is
"column `j` of `Delta_1` is zero", which holds for **every** `j ≠ 0` and every
pair. So one statistic reads **saturating at r=2 → huge excess at r=3 → exactly
zero at r=4 → generic at r=5**. That four-point ladder is the instrument, and
it carries its own positive controls in the same code path.

**D7 — the set form (a subspace-trail object that is not the integral).** Let
`y` be the four bytes of the round-1 column-0 state. Column `c` of the round-2
state depends on **exactly one byte of `y`**, because ShiftRows puts one
nonconstant byte into each column and MixColumns acts within a column. So the
round-2 image of a diagonal coset is a **product set** of four 256-element
column sets — and this product structure **survives SubBytes and MixColumns**
(both columnwise) and dies only at ShiftRows. This is precisely the
"coset-to-coset map with structure surviving SubBytes" the directive asks about;
its measurable shadow is "the `CW[j]` projection at `r = 3` takes at most 256
distinct values", which is one readout of the same gate.

**D8 — key schedule.** Let `sigma(state)` = XOR of the four columns. Then
`sigma∘SR = sigma`, `sigma∘MC = MC∘sigma`, `sigma(x+k) = sigma(x)+sigma(k)`.
Only SubBytes breaks it. And expanding the three linear recurrences inside one
AES-128 round key gives **`sigma(RK_i) = W_{4i-3} ⊕ W_{4i-1} = RK_{i-1}[1] ⊕
RK_{i-1}[3]`** — a cross-round schedule constraint on a 32-bit projection that
three of the four layers commute with.

**D9 / D10 — the quartet side.** A ciphertext shift `nabla` in the `CW[0]` space
propagates backward deterministically for **exactly two rounds** (column 0, then
`D_0`; a third round applies `MC^{-1}` to a `D_0`-supported difference, which
has one byte per column and therefore fills every column). Consequently at
`r = 2`, with plaintext difference in `D_0` and shift in `CW[0]`-space,
`P3⊕P1 ∈ D_0` and `P4⊕P2 ∈ D_0`, so **`P3⊕P4 = (P3⊕P1)⊕(P1⊕P2)⊕(P2⊕P4) ∈ D_0`
with probability exactly 1**. That is an exact positive control the boomerang
instrument would otherwise lack.

**D11 — the key-schedule obstruction, stated because it is load-bearing.** For a
*fixed* key the cipher is one permutation and AddRoundKey is a translation. The
key schedule constrains the map *key → round-key tuple*, and a fixed-key
distinguisher cannot query that map: any single-key statistic is invariant under
replacing the schedule by any other round-key tuple realising the same
permutation. The lane is not empty — what it *can* test is a property whose
probability under the real schedule differs from its probability under
independent round keys, **measured across keys** — but that becomes a PRP claim
only through an explicit two-step chain (see CAND-ND-4).

---

## 3. The five candidates, ranked

Ranking is by (a) probability of surviving past `r = 5`, (b) cost of the
cheapest discriminating gate — with cheap-and-decisive ranked first, per the
directive.

### Rank 1 — CAND-ND-1: projection-multiplicity ladder

**Object.** The multiset of fibre sizes of `x ↦ CW[j](E_K^r(x))` on a text set
whose pairwise differences lie in `D_0`. What is tracked is a **set partition**,
not a difference, not a support pattern, not a degree, not an integral sum.

**Not an excluded shape.** Not the integral (that tracks one XOR aggregate over
a full 2^32 delta-set; this tracks the whole collision partition and is decisive
on 2^20 texts). Not degree-bounded (D4 is a support/branch-number statement with
no degree ingredient). Not the yoyo (one direction, no oracle, no exchange). Not
the mod-8 residue — and D1 shows the `A5` defect that broke that gate cannot
apply.

**Depth and what stops it.** Deterministic through `r = 4`; predicted dead at
`r = 5`, because there the event needs four specified bytes of `Delta_3` to
vanish, each column of `Delta_3` is `MC` of a *full-weight* vector, and branch
number 5 permits a full-weight input to give a weight-1 output. The D4
obstruction expires exactly one round later.

**Deterministic statistic: YES.** Collision count on `CW[j]` is *exactly 0* at
`r = 4`. At `N = 2^20` a random permutation gives ≈ 2^7 = 128 collisions per
`j`; observing exactly 0 has null probability `exp(-128) = 2^-184.7` per
`(j, key, trial)`. The `r = 3` arm reads ≈ 2^31 against the same 2^7 null — a
ratio of ≈ 2^24. **No detection floor.**

**Gate (runs here).** 2^20 texts, encrypt at `r ∈ {2,3,4,5,6,10}`, extract
`CW[j]` as a `uint32`, sort, report distinct-value count + fibre histogram +
collision count computed two ways. ≈ 2^24 encryptions total, **well under one
second of AES work**, < 100 MB, no solver, no numpy (a `uint32` sort is stdlib).

**Controls.** Matched PRP at identical data; `r = 10` decay; **two sibling
nulls** that isolate the named property — replace `D_0` by a non-diagonal 4-byte
set (D1 fails, so the zero must not survive), and replace `CW[j]` by a non-SR-
diagonal 4-byte set (D5 fails, likewise); independent-round-key arm;
random-plaintext arm.

**Delta vs. this program's own reference.** REF-C's full-diagonal integral is
2^32 data at depth 4. This is **2^20 data at depth 4**, with a strictly stronger
(set-level, deterministic) readout: **12 bits of data at equal depth**, pending
measurement. It does **not** beat REF-C on depth.

### Rank 2 — CAND-ND-2: r=5 truncated-differential collision ratio, prediction frozen first

**Object.** The count of pairs colliding on `CW[j]` at `r = 5`, plus the
plaintext-difference profile of the colliding pairs.

**Mechanism.** At `r = 5` the event needs four specified bytes of `Delta_3` to
vanish (one per column, at row `c−j` in column `c`). By D2/D3, `Delta_2` is
*rigid*: with a one-active-byte plaintext difference, every column of `Delta_2`
is a nonzero scalar multiple of a fixed MixColumns column — four scalars are the
only freedom. So the four vanishing conditions are **not** four independent
`2^-8` events; they are four linear conditions on SubBytes output differences
constrained by that rigidity and by the AES DDT (a 0/2/4-valued row
distribution). Prediction: the count is off the generic `2^-32` by a relative
factor `R ≠ 1`.

**The design feature that matters.** `R` is **computed before the cipher is
touched**, from the mechanism alone (sample the rigid `Delta_2`, push through one
SubBytes and one MixColumns, count) — 10^9 samples, seconds in C — and **frozen
with a digest**. Then the AES measurement can agree with `R`, disagree with both
`R` and 1, or agree with 1. All three are pre-registered and distinct readings.
This is what a statistical candidate has to do to be admissible after the
0.4995/0.4996 incident.

**Deterministic statistic: NO** — stated first, not buried. Relative resolution
`4/sqrt(mean)` at mean ≈ 2^31 per `j` is ≈ **2^-14.4 per j, 2^-15.4 pooled**; a
predicted 2^-8 effect sits ~8 bits above the floor.

**Gate.** Full 2^32 coset, `r ∈ {4,5,6,10}`, 4 GB bucketed counter — `gate-rr78`
already measured this shape at **≈150 s/arm**, so the figure is a measured
memory-bound number and not an extrapolation from compute throughput. ≈ 20 min
for the grid. CAND-ND-1's `r = 4` zero runs inside the same code path as the
positive control.

### Rank 3 — CAND-ND-3: truncated boomerang quartet, 96-bit return event

**Object.** The return difference `P3⊕P4` of a quartet from a plaintext
difference in `D_0` and a **fixed ciphertext shift** `nabla ∈ CW[0]`-space.

**Why it is not the yoyo, structurally.** The yoyo A-step *exchanges words*
between the two ciphertexts, which preserves the pair XOR difference exactly —
that is what makes it a value-orbit object at fixed difference, and its A-step
is an **exact involution**, which is why iteration provably cannot amplify it.
The boomerang **shifts both ciphertexts by the same `nabla`**, changing values
*and* the quartet configuration; the shift is not an involution in that sense,
so **the yoyo no-amplification argument does not transfer**, and whether
iteration amplifies is open here rather than closed. That is the single most
interesting property of this candidate and the only route to `r = 6` I can name.

**Depth.** Derived exactly at `r = 2` (D10, probability 1 — the positive
control). **I have not derived `r = 3,4,5,6` and I decline to guess them.** The
named difficulty is that the two backward-propagated junction differences must
coincide, and after three mixing layers every difference byte depends on every
other, so no support-based coincidence argument exists. That is a difficulty,
**not** an obstruction argument; its honest status is `unverified`.

**Statistic.** The `r = 2` arm is deterministic. For `r ≥ 3`, the 96-bit return
event has null mean `2^-66` at 2^30 quartets, so **a single hit is decisive** —
effectively no detection floor even though it is not a theorem. **Graded readout
is built in** precisely because the yoyo turned out all-or-nothing: full 17-bin
zero-byte histogram, plus 8-byte (null `2^-64`) and 12-byte (null `2^-32`)
support events; at 2^36 quartets the `2^-32` event has null mean 16.

**Gate.** Tier 1: 2^30 quartets × (2 enc + 2 dec) = 2^32 ops ≈ **15–30 s** per
round count, negligible memory. Tier 2 (graded): 2^36 quartets ≈ 1000 s.
Rare-event resolution 3/N → **28.6 bits** at tier 1, against a 96-bit null: 67
bits of headroom.

**Implementation risk, named.** The decryption path needs the equivalent inverse
key schedule, and this campaign has already produced a false null from a wrong
inverse-side convention. The `r = 2` determinism control and an explicit
decrypt-of-encrypt round-trip at every `r` are the guards, and they must pass
before anything else is read.

### Rank 4 — CAND-ND-4: key-schedule σ-object, real schedule vs. independent round keys

**Object.** The 32-bit `sigma` projection (D8) tracked jointly with the
cross-round constraint `sigma(RK_i) = RK_{i-1}[1] ⊕ RK_{i-1}[3]`. Under
independent round keys the per-round `sigma`-translations are independent
uniform; under the real schedule they lie in a proper subvariety.

**Lossy-projection test: PASSES with a stated defect.** 128→32 bits, compatible
with ShiftRows (exactly), MixColumns (conjugation) and AddRoundKey
(translation) — **but not with SubBytes**, so `sigma` does not propagate
deterministically across even one full round. It fails the strict reading of the
test at one layer out of four. It is ranked fourth for exactly that reason and
retained only because the lane is genuinely untested here.

**The two-step chain, which is the whole methodological content.** Step 1:
real-schedule vs. independent-round-key at round `r`. Step 2:
independent-round-key vs. **PRP** at the same `r`, same statistic, same data. A
step-1 gap is a PRP distinguisher **only if** step 2 shows independent-round-key
is itself at the PRP null at that `r`; otherwise the gap is generic AES
structure with no key-schedule content. Reporting step 1 alone would be exactly
the laundering RQ-AES-003 R5 forbids.

**Honest resolution.** 2^12 keys resolves a shift of ≈ `2^-4` across-key sigma —
**blunt**. A null here means only "below 2^-4 across-key sigma", which is a weak
bound and must be written in the same sentence as the number. `sota_delta: 0
bits`; **dominated by REF-C on every axis**, stated plainly.

**Gate.** 2^12 keys × 2^16 texts × 5 round counts × 4 arms ≈ 2^32.3 encryptions,
≈ 30 s, < 1 GB. Key schedules are **charged, not amortised** (the experiment
varies the key). Quantile comparison implemented by hand — no numpy — which is
where a silent bug would live.

### Rank 5 — CAND-ND-5: differential-linear, proposed *with* an untestable-here declaration

**The honest claim is a negative testability claim plus a calibration.** Data
for a correlation `c` is ≈ `c^-2`; the envelope caps a task at ≈ 2^38 queries,
so the smallest resolvable correlation is ≈ **2^-19**. A differential-linear
hybrid with a probability-1 truncated head (D1) and an `r−1`-round linear tail
has correlation at most the square of the tail correlation, which the wide-trail
active-S-box count puts far below 2^-19 at `r ≥ 5`.

**Both ingredients are computed, not recalled.** The S-box maximum linear
correlation (exhaustive 2^16 LAT enumeration) and the MixColumns branch number
(exhaustive) are **stage 0 of the gate**, which converts my recollections
(recall confidence MEDIUM, tagged `unverified-from-memory`) into measurements
before either is quoted.

**So `r ≥ 5` arms are declared UNTESTABLE-HERE in advance and are not run**,
because a null there would carry no information — this is the 0.4995/0.4996
failure shape, and the correct handling is an explicit out-of-scope-for-execution
record rather than a reported null. What *is* run: `r = 2,3,4` at 2^32 pairs
(resolution 2^-16) as a calibration of the accounting. A measured `r = 4`
correlation **above** the stage-0 ceiling would falsify the ceiling and be the
interesting outcome. `sota_delta`: 0 at best, negative on depth; **dominated by
REF-C**.

---

## 4. The single cheapest decisive gate

**CAND-ND-1 at `N = 2^20`.** Encrypt 2^20 texts whose pairwise differences lie
in `D_0`, at `r ∈ {2,3,4,5,6,10}`, project to `CW[j]` as a `uint32`, sort, count
collisions. **≈ 2^24 encryptions, well under one second of AES work, < 100 MB,
stdlib only.**

It is the cheapest *valid* discriminator for four independent reasons:

1. **It is deterministic.** Exactly 0 at `r = 4` against a Poisson mean of 128.
   Null tail `2^-184.7` per `(j, key)`. No sample-size argument, no sigma, no
   detection floor — the property the campaign has learned to prize.
2. **It carries its own positive controls in the same code path.** The `r = 2`
   saturation and the `r = 3` ≈2^24 excess are predicted by the same derivation.
   A statistic with no power *cannot* masquerade as a closure here: if those two
   arms do not fire, the instrument is void and nothing about `r = 4,5,6` may be
   reported.
3. **It has two sibling nulls that negate the *named* property**, not a merely
   sufficient hypothesis — swap `D_0` for a column (kills D1), swap `CW[j]` for a
   non-SR-diagonal set (kills D5). That is the KN-FIND-018 rule-6 discipline,
   which V-804-1 has left undischarged for three batches.
4. **Its `r = 5` and `r = 6` arms are free.** One extra AESENC each. A negative
   there is a real, pre-registered negative; a positive would be the highest-value
   outcome in the envelope.

It also has a real chance of *failing*: if any `r = 4` collision appears, D1–D6
are wrong and the candidate is withdrawn outright rather than repaired.

---

## 5. Honest read: does any named object plausibly survive past r = 5?

**My honest position is: probably not — for the deterministic objects, and I
can argue why; and I do not know for the quartet object, where I decline to
guess.** Stated as a difficulty with forward guidance, explicitly **not** as a
closure, because the closure standard is not met.

The argument, which is an argument and not a theorem:

1. Every deterministic structure I could construct this session bottoms out in
   two rounds of forward reach and two of backward reach (D1–D5, D9). That is
   the branch-number-free part of the wide-trail structure and it is worth
   exactly 4 rounds.
2. Every projection I constructed dies at one of exactly two places. The
   **algebraic** ones (projective/collinearity classes of a column difference)
   die at the **affine layer `L` inside SubBytes** — not at the inversion; that
   is KN-FIND-017 Fact 2, internal and verified, and it is a correction to the
   obvious wrong reason. The **support-based** ones (zero columns, zero patterns,
   product-set structure) die at the **third MixColumns**, where branch-number
   saturation makes every difference byte depend on every other.
3. I could not construct a projection that survives both, and to reach `r = 6`
   one must. **That is a report about this session's search, not a theorem about
   AES**, and under `docs/inventor-protocol.md` §4 its honest status is
   `unverified`. It is not a closure and must not be cited as one.

Three things keep the question genuinely open, and they are the forward guidance:

- **CAND-ND-3's iteration question.** The yoyo cannot be amplified *because its
  A-step is an exact involution*. The boomerang shift is not, so that argument
  does not transfer. Whether iterating a quartet shift amplifies is the one
  mechanism I can name that might buy a round, and it is unmeasured.
- **CAND-ND-2's `R`.** If the r=5 collision ratio is real and *larger* than the
  ~2^-8 my mechanism sketch suggests, the value-level dependence is stronger
  than the support-level argument in (2) sees, and (2) is wrong about where
  things die.
- **The mod-8 residue was never actually refuted.** Its own producer declined to
  call it refuted: the 2^24 design broke the subspace algebra at round 2 for
  reasons unrelated to depth, and the surviving arms ran **1 trial each**. A
  deterministic residue at 1 trial has null probability 1/8. That lane is open
  at a resolution of 3 bits, which is nearly no resolution at all.

**What I would not do is declare `r = 6` impossible.** CAND-ND-1 and CAND-ND-3
test it at essentially zero and low marginal cost respectively, which is a better
answer than an opinion.

---

## 6. Honest accounting (inventor-protocol §5)

- **Objects considered:** 5 proposed; 6 enumerated and dropped *before* any
  experiment (255-byte delta-set sequence — not lossy; full quartet ciphertext
  difference — not lossy; projective column class — folded into CAND-ND-1/2
  rather than re-parameterised; column-product structure D7 — folded into
  CAND-ND-1; mixture/exchange quadruple — **deliberately not proposed**, it is a
  measured object of this program and another readout of it would be the
  re-parameterisation the directive rules non-responsive; invariant-subspace /
  weak-key objects — measure-zero key class, incompatible with a
  randomly-drawn-key PRP-controlled distinguisher).
- **Compute run:** zero.
- **`dominated_by`:** *unresolvable in this environment: no primary source
  reachable; every recalled frontier row is unverified-from-memory.* Against the
  three adjudicable references: CAND-ND-1 is dominated by REF-C on **no** axis
  (matched on depth 4, better by 12 bits on data). CAND-ND-2 and CAND-ND-3 match
  REF-C's depth-5 row conditionally on their gates. **CAND-ND-4 and CAND-ND-5
  are dominated by REF-C on every axis**, and that is stated rather than
  softened. Per-candidate rows are in the YAML and are deliberately not
  collapsed into one summary row, because collapsing hides that split.
- **`sota_delta`:** this session produces **no attack, no distinguisher, no
  measurement**. Its quantitative content is five derivations: (i) a
  deterministic 4-round property at 2^20 data against REF-C's measured 2^32 at
  the same depth — a **claimed 12-bit data delta pending the gate**; (ii) an
  exact `r = 2` quartet determinism giving the boomerang a positive control;
  (iii) a cross-round key-schedule relation on a layer-commuting 32-bit
  projection; (iv) a named obstruction for the fixed-key key-schedule route;
  (v) an explicit untestable-here declaration for differential-linear at
  `r ≥ 5` with its resolution argument attached.
- **Closures enumerated: none at the §4 standard.** One *difficulty* is named
  without an obstruction argument (§5 above) and is recorded `unverified`. One
  partial closure is offered — the **fixed-key-query route** into the key-schedule
  lane (D11) has a named obstruction, an argument, and forward guidance (the
  across-key measurement remains open; related-key and known-key models remain
  admissible as objects of study and can never satisfy a completion criterion).
  The *lane* is not closed.
- **`DEFERRED_UNBOUNDED`** (a fact about this session, kept out of any count of
  rulings): the `r = 3,4,5,6` return probabilities of CAND-ND-3; and whether any
  object reaches `r = 6` — I could neither construct one nor exclude one.
- **Open directions:** the decryption-direction mirror of CAND-ND-1 (never run
  here in any form, same milliseconds, a direction asymmetry would be a genuine
  surprise); iteration of the boomerang quartet; the mod-8 residue at more than
  1 trial per arm and on a design that does not break the algebra at round 2;
  AES-192/256 depth, currently carried over from AES-128 without measurement.

---

## 7. Non-claims — read before citing

- No claim about AES security of any kind, at any round count. No distinguisher
  exists here, none is asserted to exist, none was measured.
- No impossibility claim, no barrier statement, no lane closed. `r = 6` is
  recorded `unverified`, not answered.
- No evidence strength assigned, no hypothesis status changed, no ledger record
  written, nothing committed.
- No literature figure used to promote **or** to dismiss. No citation implying a
  source was read appears anywhere.
- Every gate is a **proposal**. No gate outcome is reported,
  predicted-as-observed, or implied.
- Toy tier throughout, however any gate returns.
