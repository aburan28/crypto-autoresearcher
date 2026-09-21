# Red-team of the GOAL-AES-002 full-round closure

Timebox: start `2026-08-01T19:53:24Z`, hard halt start+1800 s. All measurements below
were taken inside that window on this machine, gcc 13.3.0 `-O3 -maes -msse4.1`, 4 cores.
Sources are in this directory: `sbox_eq.c`, `infl_bias.c`, `mixture.c`, `mixture2.c`,
`ks_standalone.c`, `ks_verify.c`, `ks_zero.c`.

**Nothing here asserts anything about AES security. No impossibility claim is made. No
ledger state was changed and nothing was committed.**

**Literature status: NO primary source was consulted, no WebSearch was run.** Every recalled
fact below is tagged `UNVERIFIED-FROM-MEMORY` with a recall confidence, and — per
DEC-20260731-019 ruling 3 — no recalled figure is used to promote *or* to dismiss anything.
Where I needed a fact about AES I derived it and checked it against the CPU (the S-box was
rebuilt from the GF(2^8) definition and matched `AESENCLAST` on all 256 inputs; the key
schedule was rebuilt from the word recurrence and matched `aeskeygenassist` on all 11 round
keys).

---

## 0. Bottom line

**All four closures survive as conclusions. Two of them are overstated as written, one is
measurably off by a round, and the search itself has a real hole.**

- Closure 1 (O-3 / MITM): conclusion stands; **the argument has a genuine hole** — the
  set-amortized (sieve) escape from O-3's premise was named by pass 2 and then answered
  with an argument (D-3) that only covers *exact MITM factorization*. Sieves are not MITM
  factorizations. This is the largest gap I found.
- Closure 2 (depth wall): the *measurement* is sound; the **generalization from it is not**.
  One property was measured and the verdict sentence in
  `influence_support_receipt.json` reads it as closing "the structural classes" (plural).
  I measured a second, from-scratch-derived structural property to r=10; it came back at
  a matched null, so the conclusion is *supported* — but by my measurement, not by theirs.
- Closure 3 (algebraic): the soft input is now hard — I **derived 39 as the exact number of
  independent quadratic equations per AES S-box**, so `M = 7800` is measured, not recalled.
  But the **semi-regularity assumption is worse than the receipt admits**, and the verdict
  sentence reads past its own `not_established` entry.
- Closure 4 (influence support): **measurably overstated by one round.** The density
  statistic reports the object dead at r=3. A finer statistic on the same object is 43.8
  standard deviations from null at r=3 and only reaches null at r=4.

**Classes neither pass considered:** TMTO, multi-target, weak-key classes, key schedule as a
standalone object, single-key slide/self-similarity, and set-amortized (non-MITM)
elimination. I adjudicate each below. **None of them beats exhaustive key search when
everything is charged**, and for four of them the arithmetic that shows this is a few lines
that neither pass wrote down. The sixth — set-amortized elimination — is *not* adjudicable
from the existing record and is the live gap.

---

## 1. Findings, ranked by severity

### F-1 (HIGH). O-3's escape hatch is a set-amortized test, and D-3 does not close it.

O-3 bounds any class that "pays >= 1 S-box per **enumerated candidate**". Pass 2 correctly
identified that premise `(P-b)` as breakable and then closed it with derivation D-3 — which
proves only that **no exact MITM factorization** exists at 10/12/14 rounds. That is a
different statement.

The user's question is the right one: the S-box is not obviously the right atom, and the
test need not be per-candidate. A procedure that spends `c` S-boxes to eliminate a
*structured set* of `2^t` candidates pays `c/2^t` S-boxes per candidate. O-3's ceiling of
`2^kappa / N_S` is derived from the assumption `c/2^t >= 1`, i.e. `t = 0`. Nothing in O-3,
D-3, O-7, or O-8 bounds `t`.

Pass 1 asserted the escape "moves the attack into class A under O-1/O-2". **That is an
assertion, not a derivation, and it is the load-bearing step.** A set-eliminating sieve need
not be a statistical distinguisher of the data path at all — it can be a *deterministic*
consistency test on a structured key set (an affine coset, a coset of a key-schedule
subspace, a set closed under some group action) whose cost is sublinear in the set size
because intermediate work is shared. That is not class A and it is not the biclique.

What makes this a hole rather than a candidate: the program *already has the instrument*.
GATE 1 measured `rho_min = 0.77` (154 of 200 S-boxes recomputed) for **the biclique-style
coset**. That is one coset family. The measurement was never repeated for any other
structured set, and the number that decides O-3's fate is exactly `min` over set families of
(work per set) / (set size).

**Cheapest falsification gate (this is my single recommended next experiment; see §5).**

### F-2 (HIGH). Closure 4 is measurably off by one round — and the mechanism generalizes.

`influence_support_receipt.json` reports density `0.4996` at r=3 against a `0.5` null and
concludes "the object is dead at round 3 of a 10-round cipher". The receipt's own
`not_established` says a saturated support "does not preclude finer structure inside it".
That caveat is correct and it is not a caveat — it is the result.

The density statistic has **no power by construction**. Any function whose every output bit
is a balanced function of the key bits has expected support density exactly 1/2. The
measurement could not have come out otherwise past round 2, so a value of 1/2 is a
*controlled null being read as a closure*.

I measured the obvious refinement — for every (key bit *i*, ciphertext bit *j*), the
probability over random (K,P) that flipping key bit *i* flips ciphertext bit *j*, against a
null in which the second encryption uses an independent random key (`infl_bias.c`):

| rounds | mode | samples | ever-set density | chi^2 dev from null (in sd) | max &#124;z&#124; |
|---|---|---|---|---|---|
| 3 | flip | 2^18 | 1.0000 | **+43.84 sd** | 5.18 |
| 4 | flip | 2^18 | 1.0000 | -0.06 sd | 4.29 |
| 4 | flip | 2^20 | 1.0000 | -0.92 sd | 3.71 |
| 5 | flip | 2^20 | 1.0000 | -0.74 sd | 3.80 |
| 6 | flip | 2^20 | 1.0000 | +0.06 sd | 3.85 |
| 6 | **null** | 2^20 | 1.0000 | +0.10 sd | 3.89 |
| 10 | flip | 2^18 | 1.0000 | -0.50 sd | 3.62 |
| 10 | **null** | 2^18 | 1.0000 | -1.96 sd | 4.13 |

The object is **alive at round 3 at 43.8 sd** and reaches the null at round 4. The
published closure declared it dead exactly one round early, because the coarser statistic
saturated one round before the finer one did. Note also that the ever-set density here is
`1.0000`, not `0.4996` — the receipt's statistic is per-trial density; mine is the union
over 2^18 trials. Both are consistent; both are powerless.

Severity is HIGH not because one round changes the verdict (it does not: 4 of 10 is still
6 rounds short) but because **the mechanism is general**. A coarse projection of an object
reports death earlier than the object dies. Every "dead at round k" in this campaign was
measured through some projection, and none of them was accompanied by a
finer-statistic control. That is a systematic, correlated blind spot of exactly the kind
the task predicted.

**Honest limit of my own probe.** With 2^20 samples the per-cell sd is `4.9e-4`, so this
bounds any single key-bit-to-ciphertext-bit correlation only below about `2^-8.8`, and any
uniform per-cell bias below about `2^-13.5`. O-8 says a usable filter must be within about
`2^-40` of deterministic. **My probe cannot see the regime that matters, and neither can
theirs.** Saying "at the null" here means "at the null of an instrument 30 bits too blunt".
That limitation is absent from `influence_support_receipt.json`.

### F-3 (HIGH). The depth wall is one property, and the verdict sentence promotes it to a class.

`depth_wall_receipt.json` is careful: its `not_established` says "This measures ONE property
... and proves nothing about what other objects might reach". `influence_support_receipt.json`
then writes: *"the structural classes by the measured depth wall (integral dead at round 5)"*.
Plural classes, from one property. That promotion is the overstatement.

Two further problems inside the depth-wall receipt itself:

1. **A recalled figure is used to dismiss.** `depth_wall_summary` reads "Even granting the
   classical 2-3 round key-guessing extension, that reaches roughly 6-7 of 10." The
   "classical 2-3 round extension" is unverified-from-memory, is not tagged as such in that
   sentence, and it is doing dismissive work — the exact symmetric-prohibition violation
   DEC-20260731-019 ruling 3 was written to prevent. Same in the first receipt block: "the
   partial-sum technique is what classically extends such a distinguisher by roughly one
   round". Both should be tagged or deleted; the conclusion does not need them.
2. **`integral_depth_probe.c` has a printf defect** — line 42 evaluates
   `(unsigned long long)argv[2]?strtoull(argv[2],0,10):1`, which casts the *pointer* to
   `unsigned long long` and uses it as the condition, and the file calls `atoi`/`strtoull`
   with no `<stdlib.h>`. The printed seed is correct only by accident (when `argc<=2`,
   `argv[2]` is the NULL terminator). The accumulator values are unaffected. It is a
   provenance defect in a receipt-grade artifact, not a result defect.

**Properties whose survival depth was never measured here, all cheap on 4 cores with
AES-NI** (I measured the third):

- the **un-projected delta-set statistic** — the per-byte value *histogram* over the
  delta-set, not its XOR. (For an exactly-uniform histogram this is strictly stronger than
  balance and is therefore already excluded by the r=5 result; the *near*-uniform / chi^2
  version is not, and is 53 s per sweep.)
- **truncated-differential survival**: probability that a diagonal input difference gives a
  zero byte after r rounds, against the 2^-8 null. Minutes.
- **backward (decryption-direction) integral depth.** 53 s per sweep. Never run.
- **mixture / exchange quadruples** (measured, see F-6).
- **key-schedule-conditioned differential probability** — pass 2's own "open direction
  ii-sharpened", never run and cheap at r=2,3,4.
- **integral depth for AES-192/256**, which have different key schedules. Never run; the
  receipt's conclusion is stated for all three key sizes from AES-128 measurements only.

### F-4 (MEDIUM-HIGH). Closure 3: `M=7800` is now derived, but semi-regularity is a worse assumption than the receipt says.

I computed the exact number of independent GF(2) equations satisfied by the AES S-box, with
the S-box built from the field definition and cross-checked against `AESENCLAST`
(`sbox_eq.c`):

```
SBOX_SELFCHECK aesenclast_mismatches=0  S(00)=63 S(01)=7c S(53)=ed
DEG2_ALL       monomials=137  rank=98   independent_equations=39
DEG2_BIAFFINE  monomials=81   rank=58   independent_equations=23
DEG3_ALL       monomials=697  rank=226  independent_equations=471
NULL_RANDBIJ_DEG2 monomials=137 rank=137 independent_equations=0
```

- **39 is exactly right and is no longer a recollection.** `M = 200 x 39 = 7800` for
  AES-128 is now derived. I re-ran the receipt's Hilbert-series computation independently
  and reproduced its whole sensitivity table (`d_reg` 62/45/37/33/26 at
  `M` = 4000/6000/7800/9000/12000, costs `2^859.1 / 2^671.6 / 2^575.9 / 2^525.9 / 2^434.3`).
  The receipt's arithmetic is correct.
- **The null-object control is decisive and was never run:** a uniformly random 8-bit
  bijection satisfies **zero** quadratic equations. The AES S-box satisfies 39. The system
  is structurally special by a wide margin — which is the attacker-favourable direction and
  is exactly why the semi-regular reference is the wrong reference.

**The attack on semi-regularity, in the attacker's favour, that neither pass made.** Every
one of the 39 quadrics per S-box involves only 16 bits (8 input, 8 output). As a quadratic
form in the `N = 1408` variables of the full system, each generator therefore has **rank at
most 16 out of 1408**. Introduce fresh variables for the S-box inputs and the quadratic
generators become **variable-disjoint across the 200 blocks**, with all coupling carried by
*linear* equations. A semi-regular sequence has nothing remotely like this. The Hilbert
series `(1+z)^N/(1+z^2)^M` is the series of a system AES demonstrably is not, so
`2^434..2^859` is **a reference point, not a bound in either direction** — the receipt says
this in `not_established` and then its `verdict` line says "The algebraic lane does NOT
reach exhaustive key search". Those two sentences are inconsistent; the `not_established`
one is the correct one.

**Cheapest experiment that would show AES's true `d_reg` far below semi-regular.** Build a
scaled-down AES-shaped system (small S-box, 2-4 rounds, `N ~ 20-40` GF(2) variables) and a
*random* quadratic system with the identical `(N, M)` — the null object — and measure the
degree at which the Macaulay matrix first falls, by GF(2) rank, at increasing round counts.
This is feasible here: a degree-4 Macaulay matrix at `N=24` is ~13k x 13k bits, seconds to
minutes in C with the bitset elimination already written in `sbox_eq.c`.
**State the discriminator in advance:** the parameter that must destroy any apparent
advantage is *round count*. If the structured system's first-fall degree sits below the
random null's and the **gap widens with rounds**, the closure is wrong. If the gap is flat
or narrows, the closure is supported and the semi-regular reference is vindicated for the
right reason. A flat gap is the artifact tell, per `docs/inventor-protocol.md` §3.
The program's one prior structured-vs-random `d_reg` measurement (a different family) found
the structured degree *higher*; that is a prior, not a result about AES.

### F-5 (MEDIUM-HIGH). The key schedule as a standalone object was never treated — and it does not saturate.

Neither pass treated the key schedule as an object in its own right. Pass 1 reached it only
through `sigma(K)` (LP-1, rejected as non-lossy) and the key-masked linear approximation
(LP-2); pass 2 only through D-6 (Rcon and MixColumns functionals). No one measured it.

I did (`ks_standalone.c`, then re-verified with the CPU's own `aeskeygenassist` schedule in
`ks_zero.c`, 200 000 random keys per round). Result, **AES-128**:

| round | master-bit -> round-key-bit support density | cells never flipping |
|---|---|---|
| 1 | 0.0820 | 0.9180 |
| 2 | 0.3242 | 0.6758 |
| 3 | 0.5137 | 0.4863 |
| 4 | 0.7090 | 0.2910 |
| **5..10** | **0.781250 (exactly, every round)** | **3584 / 16384 = 0.218750** |

**The AES-128 key-schedule influence support never saturates.** 3584 of the 16384
(master-key-bit, round-key-bit) pairs flip in **zero** of 200 000 random keys at every round
from 5 to 10, and the never-flipping sets are whole bytes. AES-192 saturates at 0.8750,
AES-256 at 0.781250, both permanently. Contrast the *ciphertext* influence matrix, which is
at full density and unbiased from round 4 (F-2) — the data path saturates, the key schedule
never does.

Two honest qualifications, both load-bearing:

1. **This is not an attack and does not reduce key entropy.** The AES-128 key schedule is
   invertible from any single round key, so a sparse influence pattern is a statement about
   coordinates, not about information. It is exactly the shape LP-1 correctly rejected.
2. **My own symbolic dependency closure was wrong and I am reporting that.** A naive
   transitive-closure computation (`ks_verify.c`, and the Python closure) says support
   reaches 1.0 at round 5, because OR-propagation cannot represent XOR cancellation. The
   sampled measurement on the CPU's own schedule is the correct one. Anyone re-deriving
   this by dependency-graph reasoning will get the wrong answer, which may be precisely why
   both passes' diffusion arguments (D-3's "full key-and-state dependence in two rounds")
   read as obviously true.

Related, and also unmeasured by both passes: **no repeated round key occurred in 200 000
random schedules for any of AES-128/192/256** (null expectation ~1e-31). That is the
single-key slide/self-similarity precondition and it is now measured rather than asserted
from Rcon.

**What this does to D-3.** It does not refute it. D-3's conclusion survives, but by a much
simpler route than the one stated: for AES-128 round key 0 *is* the master key and for
AES-256 round keys 0-1 *are* the master key, so no nontrivial key partition can leave the
forward-eligible round keys independent of `K_2`. The stated argument (two-round full
dependence) is a claim about the data path that was never measured and whose key-schedule
analogue is *false at the bit level*. The closure should be rewritten on the trivial ground,
which is airtight, rather than on the diffusion ground, which is not checked.

### F-6 (MEDIUM). I built a second structural property, found a signal at r=5 where the integral is dead, red-teamed my own measurement, and it collapsed to a controlled null.

Reported in full because the collapse is the finding.

**Derivation, from scratch, no literature.** Let `p1, p2` agree outside the ShiftRows
diagonal `D = {0,5,10,15}` and differ inside it. For a proper nonempty `T` subset of `D`,
let `p3 = p1` with bytes `T` taken from `p2`, and `p4 = p2` with bytes `T` taken from `p1`.
At every byte position `{p3,p4} = {p1,p2}` as a multiset, so `S(p3_i)+S(p4_i) =
S(p1_i)+S(p2_i)` everywhere; SubBytes is bytewise and ShiftRows-MixColumns-AddRoundKey is
GF(2)-affine, so **the state difference after one full round is identical for the pair
`(p1,p2)` and for the pair `(p3,p4)`, while the absolute states differ.** A mixture
quadruple is two pairs launched with the same round-1 difference from different values.
`mixture.c` TEST0 verifies this on the machine: **HOLDS, 2000/2000 quadruples, every run.**
This structural fact is not in either pass's enumeration.

Readout: `A` = "the two ciphertexts of pair 1 agree in at least one byte", `B` = same for
pair 2; test `P[A&B]` against `P[A]P[B]`.

First run (2^24 quadruples): r=4 ratio 1.0354 `z=8.81`, r=5 ratio 1.0306 `z=7.61`, nulls
`z=0.50` and `z=0.22`. **A signal at round 5, where the integral is dead.** It was also
nearly flat between r=4 and r=5 — the artifact tell. I computed the degeneracy directly:
when the diagonal bytes of `p1,p2` coincide on all of `T`, the mixture pair *is* the
original pair, giving a round-independent perfect correlation with probability `1.12e-3`
and an excess of `6.4e-5` — **about half of the observed `1.3e-4`**.

Second run with a guard requiring all four diagonal bytes to differ (`mixture2.c`, 2^25
quadruples):

| rounds | mixture | matched null |
|---|---|---|
| 4 | ratio 1.0121, z=4.20 | ratio 1.0178, **z=6.17** |
| 5 | ratio 1.0118, z=4.11 | ratio 1.0153, **z=5.31** |
| 6 | ratio 1.0182, z=6.31 | — |
| 10 | ratio 1.0091, z=3.15 | ratio 1.0147, **z=5.11** |

The residual excess is present **equally in the null**, is **flat from r=4 to r=10**, and the
mixture arm is never above the null arm. Its source (shared key within a quadruple, or my
xorshift64 PRNG) is unidentified and I did not chase it. **Conclusion: no mixture-specific
effect detected at r=4,5,6,10 against a matched null.** That is a controlled null, not a
finding, and it *supports* the depth-wall conclusion — via a property the depth-wall
measurement never touched.

**What I must not do here is convert my failed readout into a closure.** The object is
verified to exist; only one lossy readout of it (byte-collision co-occurrence) was tested.
A different readout — the r=2/r=3 "identical difference" survival probability, or the joint
difference distribution rather than a collision indicator — is untested. Calling the object
dead on this evidence would be exactly the fatigue report this red team is meant to police.

### F-7 (MEDIUM). Four classes neither pass enumerated. None beats exhaustive search once everything is charged.

`TMTO` / `Hellman` / `rainbow` / `Biryukov` appear **zero times** in either candidate report,
either companion document, or the baseline map. `weak key`/`weak keys` appear zero times as
an attack class (twice as a caveat about sampling). `slide attack` appears zero times.
Multi-target appears once, declared out of frontier in one clause of `baseline_map.md`.

**(a) Time-memory(-data) tradeoffs.** In scope as single-key full-round attacks. Verdict:
**cannot beat the reference once precomputation is charged, and the direction of the
inequality is safe.** Building any table over the key space applies the target function to
`2^128` points, so precomputation alone equals the worst-case reference and exceeds the
`2^127` expected-case reference. Charging the inverse success probability (table coverage is
below 1) only raises the total. And the reference has `O(1)` memory while a TMTO does not,
so on the Pareto frontier the TMTO is dominated on **memory** as well as on total time. This
requires no literature: it follows from "the table must be built".
The van-Oorschot-Wiener-style interpolation back to the baseline is the honest framing —
TMTO relocates cost along the memory axis, it does not move the exponent — and it should be
in the record. Recall that block-cipher TMTOs are classically described as amortizing over
*many* targets is `UNVERIFIED-FROM-MEMORY, recall MEDIUM`, and is used for neither promotion
nor dismissal; the arithmetic above stands without it.

**(b) Multi-target / multi-key.** **Out of scope as a single-key break** (the success
criterion changes), and it does not help anyway: exhaustive search against `m` targets costs
`2^128` evaluations *total* — one pass over the key space, testing each trial key against a
hash table of the `m` ciphertexts at `O(1)` amortized cost — i.e. `2^(128 - log2 m)` per key.
**The reference amortizes over multiple targets exactly as well as any TMTO does.**
`baseline_map.md`'s one-clause dismissal ("changes the problem, not the cipher") reaches the
right answer without this arithmetic; the arithmetic is what makes it a closure.

**(c) Weak-key classes of nonzero density.** In scope. Verdict: **cannot move the expected
total below the reference unless the gain applies to a constant fraction of keys**, because
total cost is per-attempt cost times inverse success probability. Explicitly, for density
`2^-d` and an in-class gain of `g` bits, `E[total] = 2^-d * 2^(128-d-g) + (1 - 2^-d) * 2^128`:

| density | in-class gain | E[total] | reference |
|---|---|---|---|
| 2^-8 | 8 bits | 2^127.9944 | 2^128 |
| 2^-32 | 32 bits | 2^128.0000 | 2^128 |
| 2^-64 | 64 bits | 2^128.0000 | 2^128 |
| 2^-1 | 1 bit | 2^127.3219 | 2^128 |

Only a class of *constant* density moves anything, and then only by its own gain. Neither
pass wrote these four lines. Note the sharp consequence for pass 1's CAND-FR-2 caveat: its
own record says "a weak-key class of density below 2^-30 is INVISIBLE to this experiment" —
correct, and now also **irrelevant**, since a class that thin cannot beat the reference even
if it exists.

**(d) Key schedule as a standalone object.** In scope. Measured for the first time in this
program — see F-5. It does not beat the reference: the AES-128 schedule is a bijection from
any round key back to the master key, so its coordinate sparsity carries no entropy loss.
Also measured: no repeated round key in 200 000 schedules per key size, which is the
single-key slide precondition.

**(e) Single-key slide / self-similarity.** In scope, zero mentions in either pass, closed by
(d)'s measurement plus the elementary fact that the round constants differ per round.

**(f) Nonlinear invariants as distinct from invariant subspaces.** `baseline_map.md` lists
them in one table cell with invariant subspaces and one shared verdict. They are different
objects (a preserved *function* versus a preserved *set*), and for a single-key attack a
nonlinear invariant generically requires a weak-key class — which (c) now closes on cost
grounds regardless of whether one exists. Naming it because the deduplication register
merged two objects into one row and neither pass noticed.

---

## 2. Where the closures are weakest

Ranked, weakest first.

1. **The step "batch elimination moves the attack into class A"** (pass 1, O-3 forward
   guidance). Unproved, load-bearing, and the only thing standing between O-3 and a
   sublinear-per-candidate sieve. D-3 does not cover it.
2. **Every "dead at round k" in the campaign.** Each was measured through one projection
   with no finer-statistic control. F-2 shows the error is at least one round in the one
   case I could check.
3. **`d_reg` semi-regularity.** Now demonstrably the wrong model class (rank-16 forms,
   block-disjoint generators, a null bijection with 0 quadrics against AES's 39), with no
   measurement of the real thing at any scale.
4. **Instrument resolution.** Both my bias probe and the published influence probe are
   ~30 bits too blunt to see the bias regime O-8 says matters. "At the null" is being read
   as "no structure" when it means "below this instrument's floor".
5. **AES-192 and AES-256** carry conclusions measured only on AES-128 (integral depth,
   partly the algebraic lane). Their key schedules differ, as F-5 shows quantitatively.

---

## 3. Things the record gets right and should keep

- `dominated_by` in pass 2 is filled with the mandated string rather than `null`, with an
  explicit axis-by-axis check against the one adjudicable reference. That is correct
  practice under AGENTS rule 5 and it is rare.
- Both passes state "no fifth/fourth class" as a statement about the search, not the
  problem, and pass 2 found a fourth class after pass 1 implicitly closed at three. That is
  the anti-premature-closure discipline working.
- Pass 2's correction of O-5 (`2^704` was a category error; Groebner/XL is `C(N,d)^omega`,
  not `2^cN`) is right, and I reproduced its binomials exactly.
- `algebraic_lane_receipt.json` computing **both** the optimistic proxy and the standard
  Hilbert criterion and reporting the disagreement (`~330` bits) rather than picking one.
- The receipts' `not_established` blocks are unusually honest. The failure is that the
  `verdict` and `finding` fields repeatedly read past them.

---

## 4. What I did not do

- No `WebSearch`, no primary source, no literature figure used in either direction.
- I did not re-run the 2^32 integral sweep; I accept `depth_wall_receipt.json`'s R4/R5
  accumulators as reported and attack the generalization, not the numbers.
- I did not build the toy structured-vs-random `d_reg` instrument (F-4). It is the second
  cheapest open gate and did not fit the timebox.
- I did not identify the source of the ~1.5% common-mode excess in the mixture estimator
  (F-6). It is present in the null and flat in rounds, so it does not affect the conclusion,
  but it is an unexplained artifact in my own instrument and I am flagging it.
- I asserted nothing about AES security and made no impossibility claim.

---

## 5. The single cheapest experiment that could still overturn the conclusion

**Measure the minimum per-candidate S-box cost over structured key SETS, not over the
biclique coset alone.**

GATE 1 measured `rho_min = 0.77` for one coset family and that number is what makes O-3
bite (7.27 bits above the ceiling). O-3's ceiling is `2^kappa / N_S` *only under* "one S-box
per candidate". The quantity that actually decides the class is

```
    mu  =  min over structured key-set families F  of   (S-boxes to test the whole set F) / |F|
```

O-3 assumes `mu >= 1`. GATE 1 measured `mu ~ 0.77` for one `F`. **Nobody measured any other
`F`.**

Concrete protocol, ~30 minutes on this machine, AES-NI, no new dependency:

1. Enumerate structured key-set families reachable here: affine cosets of the master key of
   dimension `d = 8..24`; cosets of the *last-round-key* subspace pulled back through the
   inverted key schedule; cosets of the key-schedule-sparsity subspace that F-5 exposes
   (the 3584 permanently-independent cells define a natural non-obvious coordinate split);
   and sets closed under the diagonal byte-swap that F-6's mixture derivation verified.
2. For each family and each `d`, instrument a reduced-round AES to count **distinct
   intermediate byte values** across the set at each of the 200 S-box positions. Shared
   values are shared work; `mu(F,d) = (sum of distinct counts) / (200 * 2^d)`.
3. **Pre-register the discriminator.** `mu` must *increase toward 1* as `d` grows, because
   full diffusion should destroy sharing. A `mu` that **stays flat or falls as `d` grows** is
   either a real sublinear set test — which breaks O-3 outright — or an artifact.
4. **Null-object control, mandatory.** Run the identical count against a random 128-bit
   permutation family of the same shape (e.g. an independent-round-key AES, which has the
   same wiring and no key schedule). If AES's `mu` curve matches the null's, that is a
   controlled null and O-3's premise is confirmed *by measurement* for the first time.

Outcome either way is a real result. If `mu` falls below `1/N_S = 1/200` for any family at
any `d`, the O-3 ceiling is void and the enumerative class is reopened. If `mu -> 1` on every
family and matches the null, O-3 stops being a counting argument with an unproved forward
clause and becomes a measured obstruction — which is what a closure is supposed to be under
`docs/inventor-protocol.md` §4.

Second cheapest, if the first is run and returns a null: the structured-vs-random `d_reg`
first-fall experiment of F-4, with round count as the pre-registered discriminator.

---

## 6. Elapsed

Start `2026-08-01T19:53:24Z`. All measurement complete by `2026-08-01T20:07:02Z`
(818 s elapsed). Report written inside the 1800 s budget. Measured elapsed is reported
honestly and no result was extrapolated past what was run.
