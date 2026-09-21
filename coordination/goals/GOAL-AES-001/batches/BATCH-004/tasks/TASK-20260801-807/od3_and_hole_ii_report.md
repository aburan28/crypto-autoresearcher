# OD-3 (set-valued objects) and D-705-5 hole (ii) (the restricted state quantifier)

TASK-20260801-807 — GOAL-AES-001 — BATCH-004 — executor

**Provenance pointer (protocol-amendment-GOAL-AES-001-004 Part B).** This is a
PROSE REPORT and takes the manifest-pointer form: the covering machine-readable
manifest is `od3_results.json` in this same directory, which carries the
first-class `inference` block and the `artifact_provenance` list (path, kind,
SHA-256, comment-block stanza flag, coverage flag) for all four declared
artifacts of this task, including this file.

**Scope and claim tier, stated before anything else.** Everything below is a
derivation plus a toy-scale computation in a **scaled-down GF(2^4) analogue**
about the algebra of AES components. It is **not** a cryptanalytic result, **not**
a distinguisher, **not** a barrier statement, and it asserts **nothing** about AES
at any round count or about deployed AES. No closure is proposed, no
`reject_scoped` is proposed, no evidence strength is assigned, no ledger record
is created, nothing is promoted to knowledge, and no official state changes.

**On PROP-701-I.** `PROP-701-I` is **not established** — KN-FIND-017 declines to
assert it and instructs readers not to cite it as established, and its
falsification gate still fails to isolate the ingredient it names (V-804-1).
Nothing here is built on PROP-701-I being **true**. Group (b) reasons about its
**proof**: what the Step 1 / Step 2 / Step 3 machinery does when hypothesis (H2)'s
"for EVERY state `s`" is weakened. Wherever the distinction could matter, this
report says which of the two it is doing.

**Out of scope this batch.** D-705-5 hole (i), word-position-dependent families,
is deliberately not attempted; it is deferred to BATCH-005 by the task card.

**Supersession.** This file supersedes nothing. All four artifacts are new. No
BATCH-001, BATCH-002 or BATCH-003 artifact was modified, re-run into or deleted.
`od1_gate701c_v2.py` and `verify_derivation.py` were read only; the field
arithmetic and the `(lambda,k)`-graph strong-connectivity computation were
re-implemented from scratch in `od3_quantifier.py` so that agreement, where the
two overlap, is an independent check and not a shared assumption.

---

## 0. Pre-registration — written BEFORE any code and BEFORE any measurement

This section is a **verbatim reproduction** of the `pre_registered_predictions`
block of `prescreen_od3.json`, which was written to disk **before** any line of
`od3_quantifier.py` existed and **before** anything was executed. Its SHA-256 at
freeze is recorded in `od3_results.json` under `prescreen.sha256_at_freeze`. The
pre-registration ordering therefore rests on a **committed digest**, not on a
file mtime — the direct response to defect V-804-2. (One correction is recorded:
the first draft carried a *guessed* `written_at_utc`, replaced by the measured
clock value before any code was written; the superseded digest and the reason are
recorded inside the file and as DEV-807-1 in the manifest. Nothing else changed.)

Analogue: GF(2^4), modulus `x^4+x+1`, MixColumns-shaped circulant first row
`(02,03,01,01)`, 4 words × 4 rows. Same analogue as GATE-701-C v2.

- **P_b1** — coordinate-subspace cosets (this class contains every delta-set and
  every fixed-byte set): reach size of `u_k` is exactly 1 or exactly `|F| = 16`,
  no intermediate value, and it is `|F|` exactly when at least one of the three
  pre-MixColumns coordinates other than the fixed one is free.
- **P_b2** — single-active-byte delta-set: sweep totally broken, reach 1 for every `k`.
- **P_b3** — classical 4-active-byte one-diagonal delta-set: sweep **full** with
  maximal free-coordinate count 3 for the one output word index of that diagonal,
  and reach 1 for the other three output word indices.
- **P_b4** — fixed-byte sets with at most three bytes fixed: sweep full wherever
  Step 1 is admissible.
- **P_b5** — over an exhaustive enumeration of all `2^16 = 65536` coordinate-active
  patterns, the number admitting the **full unrestricted argument** (some input
  word `p` with all 12 positions outside word `p` active and at least one inside)
  is **exactly 57** (`= 4*15 - 3`).
- **P_b6** — GF(2)-affine but not F-affine state sets: **intermediate** reach sizes
  strictly between 1 and 16 do occur; 2, 4 and 8 will all be observed.
- **P_b7** — the closure forces `pi` constant for exactly the P_b5 patterns and no
  others among the named family.
- **P_b8 (positive control)** — `A` = all 16 active forces constancy for **every**
  seed; if not, the implementation is wrong and every group (b) reading is VOID.
- **P_b9 (null_1)** — identity matrix: constancy not forced for any single-coordinate seed.
- **P_b10 (null_2)** — invertible circulant with a zero entry: constancy not forced
  for at least some seeds.
- **P_b11 (null_3, isolation)** — invertible circulant, all entries nonzero,
  `(lambda,k)` graph **not** strongly connected: constancy not forced. If it instead
  behaves like the target, the statistic discriminates without isolating, exactly
  the V-804-1 failure mode, and that is reported as a failure of isolation.
- **P_a1** — coupling witness: XOR sum survives; word multiset, support size and
  F-affine rank all broken.
- **P_a2** — the group (a) enumeration terminates in `NO_ADMISSIBLE_MEMBER`.

---

## 1. The mandatory pre-screen, and what it killed

Frozen in `prescreen_od3.json` before any derivation and before any compute.
Threshold and language identical to TASK-20260801-806: **PURSUE iff the interface
constant `n` is `<= about 7`**, otherwise `IN_SCOPE_VACUOUS`; the screen is on the
argument's iteration count over interfaces **however the iteration is packaged**.

One distinction was recorded **in the frozen file, before any work**, because it
would look like a dodge if constructed afterwards: PROP-701-I's Step 3 traverses
the `(lambda,k)` graph, but for a **round-independent** `pi` every traversal step
happens **at the same single interface with the same `pi`** — the graph walk is over
the invariance group, not over interfaces. Its interface constant is `n = 1`.
Proposition 801-1's constant is `2 + 2n* = 32` only because **its** `pi` is
layer-dependent, so each graph step must be paid for with two fresh interfaces.
Hole (ii) and OD-3 both keep round-independence.

| id | statement (abbreviated) | spreads through the graph / `G^2` | `n` | verdict |
|---|---|---|---|---|
| CAND-B1 | reach of `u_k` under a restricted state set | **no** — a single row-`k` linear functional, one interface | 1 | **PURSUE** |
| CAND-B2 | fixpoint of Steps 1–3 under a restricted state set | yes | **1** (round-independent `pi`) | **PURSUE** |
| CAND-B3 | layer-dependent family + restricted domain, closed after `N` interfaces | yes | **≥ 32** | `IN_SCOPE_VACUOUS` |
| CAND-B4 | iterate the restricted closure **across** interfaces, tracking domain growth | yes | **no upper bound exhibited** | `IN_SCOPE_VACUOUS` |
| CAND-A1 | set-valued (H2) coupling witness | **no** — ShiftRows cross-word coupling, one interface | 1 | **PURSUE** |
| CAND-A2 | lift `pi` to sets and re-run Steps 1–3 | yes | 1 | **PURSUE** |
| CAND-A3 | set-valued analogue of Proposition 801-1 | yes | **≥ 32** | `IN_SCOPE_VACUOUS` |

**Killed: 3 of 7** — CAND-B3 (`n ≥ 32`), CAND-B4 (no upper bound on `n` could be
exhibited), CAND-A3 (`n ≥ 32`). **None of the three was pursued.** No derivation of
CAND-B3, CAND-B4 or CAND-A3 is attempted anywhere in this package; CAND-B4 is
carried forward as a named residual (§4.4) rather than as work. This is the gate
BATCH-003 lacked when Proposition 801-1 was proved before it was screened.

---

## 2. Group (b): D-705-5 hole (ii), the restricted state quantifier

### 2.1 What is being computed, and where in the proof it bites

`PROP-701-I`'s (H2) demands deterministic propagation for **every** state `s`. Its
proof consumes that quantifier at a named place, quoted from the BATCH-002 text:

> As `u` ranges over `U_i`, its `k`-th coordinate `u_k` ranges over ALL of `F`,
> because `u_k = sum_l M[k][l] y_l + (k_j)_k` with `y_i` fixed, `y_l` free for
> `l != i`, and `M[k][l] != 0`. Taking the union over those values of `u_k`, the
> constraint disappears.

The words "`y_l` free for `l != i`" are exactly the full quantifier. Restricting the
propagation requirement to a structured subset `S` of states restricts which `y`
are achievable, so the question is finite and computable: **as `y` ranges over the
achievable set with `y_i` fixed, how much of `F` does `u_k` reach?**

Geometry used throughout, stated in PROP-701-I's own convention and generalised
from its `p = 1` to an arbitrary input word: with ShiftRows offsets `(0,1,2,3)`,
the pre-MixColumns vector of output word `j` is `y^(j)_l = w_{(j+l) mod 4}[l]`, so
input word `p` contributes exactly one coordinate to output word `j`, at row
`i = (p-j) mod 4`, equivalently `j = (p-i) mod 4`. For a state set in which each of
the 16 positions is either free or fixed, define

`J_p(i) = { l != i : state position (l, (j+l) mod 4) is free }`, `j = (p-i) mod 4`.

These are precisely the coordinates the proof calls free.

**This is reasoning about the PROOF, not about the proposition.** Nothing in §2
claims that any object does or does not propagate; it computes what the machinery
delivers when its hypothesis is weakened.

### 2.2 Measured: how much of `F` the sweep reaches

Exhaustive over **all `2^16 = 65536` coordinate-active patterns**, over all input
words `p`, all rows `i`, and all `k` — 2 097 152 admissible configurations. The
reach sets themselves are obtained by **explicit enumeration** of `y` for every
`(i, J)` shape (the exhaustive pass then looks the enumerated value up; the
enumeration is the computation, the lookup is deduplication of identical
enumerations). Constants and round key were **checked, not assumed, to be
irrelevant to reach sizes**: re-running every shape with seeded nonzero fixed bytes
and a seeded nonzero round key gives identical sizes (`seed 80720260801`).

| reading | measured |
|---|---|
| distinct reach sizes over all 2 097 152 configurations | **{1, 16}** — no intermediate value ever occurs |
| histogram | `1: 262144` (12.5 %), `16: 1835008` (87.5 %) |
| patterns with Step 1 admissible at all | 65535 of 65536 (all but the empty pattern) |
| patterns admitting the full unrestricted argument | **57** |

- **P_b1: agrees.** The dichotomy is exact and the mechanism is one line: a single
  free coordinate `y_l` already sweeps `F`, because `M[k][l] != 0` and `M[k][l]·F = F`.
  There is no partial coverage. `reach_k = F` iff `J_p(i) != {}`.
- **P_b5: agrees exactly, 57.**
- **P_b2: agrees.** Single-active-byte delta-sets read reach 1 for every `k`, in
  every admissible configuration, for both tested positions. The mechanism: the
  collision difference `Delta` must be supported on the **active rows of the
  collision word**, so the one active byte is forced to be both the collision
  coordinate and the only free coordinate, leaving `J = {}`.
- **P_b4: agrees.** The 15-active fixed-byte set is full everywhere.
- **P_b3: PARTIAL — discrepancy recorded, not reconciled.** The classical
  4-active-byte one-diagonal delta-set does read a **full** sweep with the maximal
  `|J| = 3`, for the one output word index of that diagonal, as predicted. The
  predicted "reach 1 for the other three output word indices" is **not observed**:
  those configurations do not exist at all, because `Delta` cannot be supported on
  a frozen row of the collision word. The prediction named the right conclusion
  through the wrong mechanism, and is left as written.

**Named-family readings (sweep):** full sweep everywhere for `A_full`, the
2-active-bytes-on-one-diagonal set, the 4-active-byte one-diagonal delta-set, the
8-active-byte two-diagonal set, the 15-active fixed-byte set, the 12-active
word-1-frozen set, and the 13-active minimal pattern. Reach 1 everywhere for both
single-active-byte delta-sets, the 2-active-bytes-in-one-word set, the
4-active-byte one-word set and the 4-active-byte one-row set.

### 2.3 Measured: sets that are GF(2)-affine but not F-affine

The `{1, 16}` dichotomy is a fact about **F-linear** structure. For a state set that
is a GF(2)-subspace, `u_k` is a GF(2)-linear image of a GF(2)-affine slice, so the
reach is a GF(2)-subspace of `F` and intermediate sizes are possible.

- First design (uniform random GF(2)-subspace, dims 2–12, 40 samples each,
  `seed 807042026`): **0 admissible instances** — a uniform subspace of dimension
  `<= 12` inside the 64-dimensional state space essentially never contains a nonzero
  vector supported on a single word, so no Step-1 pair exists. Reported, and the
  design change is recorded as DEV-807-2; no prediction was altered.
- Second design (same seed, one basis vector forced to be supported on the
  collision word, which is exactly the condition Step 1 needs): **240 admissible
  instances**, reach-size histogram **`{1: 192, 2: 145, 4: 134, 8: 161, 16: 328}`**.

**P_b6: agrees.** Intermediate reach sizes 2, 4 and 8 all occur. This is the one
place where the answer to "how much of `F` does `u_k` reach" is genuinely a
spectrum rather than a dichotomy, and it identifies the structural feature that
produces the spectrum: **not the size of `S`, but whether `S` is F-linear.**

### 2.4 Measured: what the whole Step 1 / Step 2 / Step 3 machinery does

The sweep is one step. The decisive question is what the fixpoint of the machinery
delivers under the restriction. The engine tracks, for each translation `t`, the
set `W_t ⊆ F^4` of `w` for which the machinery has established `pi(w) = pi(w+t)`,
and applies the restricted Step 1 uniformly (Step 2 is that rule applied to a pair
the rule itself produced; Step 3 is its transitive closure). Constancy counts as
**forced** when the GF(2)-span of `{ t : W_t = F^4 }` is all of `F^4` — PROP-701-I's
own Step 3 route. Because the rule fires per `(t, a)` pair, `closure(X ∪ Y) =
closure(X) ∪ closure(Y)`, so it suffices to run single seeds `(p, i, lambda)`; the
binding case for a proposition that must handle **every** collision is the weakest
single seed. All admissible seeds were run for every named set (15–225 per set).

| job | seeds | constancy forced | every seed? |
|---|---|---|---|
| **positive control**, target matrix, `A` = all 16 | 60 | 60 | **yes** |
| `p`-symmetry check, target, `A` = all 16 | 4 | 4 | yes |
| **null_1** identity `(1,0,0,0)`, 60 SCCs of size 1 | 60 | 0 | no |
| **null_2** `(0,1,1,1)`, invertible, one zero entry, 15 SCCs of size 4 | 60 | 0 | no |
| **null_3** `(1,1,1,6)`, invertible, **all entries nonzero**, 5 SCCs of size 12 | 60 | 0 | no |
| delta-set, 1 active byte (r0w0) | 15 | 0 | no |
| delta-set, 1 active byte (r1w2) | 15 | 0 | no |
| delta-set, 2 active bytes, same word | 30 | 0 | no |
| delta-set, 2 active bytes, same diagonal | 30 | 0 | no |
| delta-set, 4 active bytes, one diagonal | 60 | 0 | no |
| delta-set, 4 active bytes, one word | 60 | 0 | no |
| delta-set, 4 active bytes, one row | 60 | 0 | no |
| delta-set, 8 active bytes, two diagonals | 120 | 0 | no |
| fixed-byte set, **one** byte fixed (15 active) | 225 | **225** | **yes** |
| fixed-byte set, word 1 entirely fixed (12 active) | 180 | 0 | no |
| minimal "full-argument" pattern, 12 off-word-1 + 1 (13 active) | 195 | 0 | no |

**P_b8: agrees — VOID-A does not fire.** The positive control reproduces
PROP-701-I's own conclusion for every seed, so the implementation is not obviously
wrong and the readings are not void.

**P_b9, P_b10, P_b11: all agree.** All three nulls read 0/60 against the target's
60/60. In particular **null_3 isolates**: it has all entries nonzero and is
invertible, and differs from the target only in that its `(lambda,k)` graph is not
strongly connected (5 SCCs of size 12, recomputed here from scratch), and the
statistic separates it from the target. null_2 and null_3 are **siblings** that
negate the two named ingredients — "every entry of `M` nonzero" and "strong
connectivity" — **separately**, which null_1 negates together. This statistic
therefore does **not** repeat the V-804-1 failure mode on this ingredient: it
discriminates **and** it isolates, on the one ingredient V-804-1 showed
GATE-701-C v2 does not isolate. Two limits on that, stated rather than buried:
(i) it is a different instrument answering a different question, so it does not
repair GATE-701-C v2 and nothing here discharges V-804-1; (ii) isolation is
demonstrated for strong connectivity and for the nonzero-entries condition, not
for every ingredient of the proof.

**P_b7: DISAGREES, in both directions. Reported as a discrepancy and not
reconciled.** The pre-registered criterion (full sweep ⇒ constancy forced) is
**wrong**, and it is left as written:

- The **13-active** pattern `A` = (all 12 positions outside word 1) + one position
  in word 1 **is** a P_b5 pattern, has a full sweep everywhere, and forces
  constancy for **0 of 195** seeds.
- The **15-active** fixed-byte set (only `(row 0, word 0)` fixed) is **not** a P_b5
  pattern and forces constancy for **225 of 225** seeds.

### 2.5 What the restriction actually does to Step 2 — the answer

**Step 2's sweep is not the binding constraint.** This is the substantive finding
and it contradicts the report of TASK-20260801-801 §5 on one point, which is
recorded as a contradiction rather than smoothed over. That report states of hole
(ii): *"Both Step 1's hyperplane construction and Step 2's sweep of `u_k` over all
of `F` consume the full quantifier, so the proof does not survive the restriction
even partially."* On the second clause, as measured in this analogue:

1. **The sweep survives almost everywhere.** `u_k` reaches all of `F` in 87.5 % of
   admissible configurations, and it does so as soon as **one single** other
   coordinate of the relevant diagonal is free. It does not need "all of `F`" worth
   of state freedom; it needs one free byte in the right place. The full quantifier
   is far more than Step 2's sweep consumes.
2. **But a full sweep does not give Step 2's conclusion.** Step 2 concludes
   `pi(w) = pi(w + v_k m_k)` for **all** `w in F^4`. Under a restriction that leaves
   `|J| < 3`, the union over `u_k in F` gives invariance only on the `M`-image of a
   coordinate subspace of F-dimension `1 + |J_p(k)|` — a strictly smaller set, even
   though the sweep of `u_k` itself was complete. The two things the proof does in
   one sentence — sweeping `u_k`, and freeing the remaining coordinates — come
   apart under restriction, and only the first is cheap.
3. **The binding constraint is the re-application, not the sweep.** The measured
   contrast between the 13-active pattern (fails) and the 15-active pattern
   (succeeds) locates it. Step 2 re-applies Step 1 to the pair `(u, u+v)` placed at
   an input word, and `v = Delta_i m_i` has **all four coordinates nonzero**
   (that is exactly what PROP-701-I uses claim C9 for). A translation with all four
   coordinates nonzero is realisable as a difference at input word `p` **only if all
   four rows of word `p` are free**. In the 13-active pattern word 1 has one free
   row, so the re-application must move to another word, where a frozen position
   costs a free coordinate and the closure stalls at translations that are never
   global. In the 15-active pattern three words are entirely free, and the closure
   completes for every seed.
4. **So the load-bearing use of the full quantifier is at the re-application, and
   the honest reading of the measurement is: what Step 2 needs from the quantifier
   is that some input word be entirely free.** This is a description of the
   measured behaviour of the named family — **it is not proved and is not claimed as
   a theorem**, and it is not exhaustively characterised (§4.4).

**Which `S` break Step 2's sweep, as measured (analogue).**
- **Break it completely (reach 1):** every state set in which the only free bytes of
  the relevant diagonal is the collision coordinate itself. Concretely: all
  single-active-byte delta-sets; all sets whose active bytes lie in one word; all
  sets whose active bytes lie in one row. 12.5 % of admissible configurations.
- **Do not break it (reach = all of `F`):** every set with at least one further free
  byte on the relevant diagonal, including the classical 4-active-byte one-diagonal
  delta-set, the 8-active two-diagonal set, and every fixed-byte set with at least
  one free byte in the right place. 87.5 % of configurations.
- **Partially break it (reach 2, 4 or 8):** state sets that are GF(2)-affine but not
  F-affine. This is the only family in which the sweep degrades gradually.

**Which `S` break the machinery as a whole, as measured (analogue).** All of them
except the 15-active fixed-byte set and the unrestricted set: **every delta-set
tested, at every active-byte count from 1 to 8, and both 12- and 13-active
patterns, leaves the closure short of forcing constancy.**

---

## 3. Group (a): OD-3, set-valued objects

### 3.1 Novelty screen, run before any effort

Every candidate was screened **before** any effort against integral/square balance,
Demirci–Şelçuk MITM multisets, division property, impossible differential,
boomerang/retracing and biclique. Every family attribution is
**unverified-from-memory** with a recall confidence recorded in
`prescreen_od3.json`; no primary source is reachable in this environment, so the
strongest form any of these verdicts takes is "matches a family recalled from
memory", and none says "known to be known".

| id | object | verdict | family |
|---|---|---|---|
| OBJ-807-1 | coordinate-wise XOR sum over the set | REDISCOVERY | integral / square balance (explicitly off-limits) |
| OBJ-807-2 | multiset of one byte over the set | REDISCOVERY | DS-MITM multiset (explicitly off-limits) |
| OBJ-807-3 | multiset of the full 32-bit **word** over the set | REDISCOVERY | DS-MITM multiset at word granularity — widening the observed unit changes the statistic's granularity, not the family |
| OBJ-807-4 | support size `|{word_j(s)}|` | REDISCOVERY | integral / square (the `A` and `C` properties **are** cardinality statements) |
| OBJ-807-5 | F-affine rank of the set | REDISCOVERY | subspace trails (for a coset, the carrier dimension — the object OBJ-701-2 already records as a probable rediscovery) |
| OBJ-807-6 | difference set of the set | REDISCOVERY | differential / subspace trail |
| OBJ-807-7 | Walsh/Fourier support of the set indicator | REDISCOVERY | linear cryptanalysis (masks) |
| OBJ-807-8 | ANF/monomial support of the set indicator | REDISCOVERY | division property |

**Outcome: `NO_ADMISSIBLE_MEMBER`.** Eight candidates enumerated, eight in a named
family, zero admissible. **P_a2 agrees.** No member was invented to have something
to report. OBJ-807-5 is worth singling out because it **passes** the specific
warning OD-3 carries — it is neither a coordinate-wise sum nor a single-byte
multiset — and still fails the wider screen; the OD-3 warning is necessary but not
sufficient as a filter.

### 3.2 Which of Steps 1, 2, 3 survive, break, or are undefined — and the exact
point of departure

- **Step 1 — BREAKS, and this is the exact point of departure.** The sentence that
  fails is *"All four input `pi`-values are the same for `S` and `S'`, so the
  hypothesis forces the two outputs to have equal `pi`."* For a single-state `pi`
  the four input values determine what the hypothesis constrains. For a set-valued
  `pi` the four input values are **marginals** — one object per word, computed from
  the set — and equality of marginals does not determine the set. ShiftRows makes
  each pre-MixColumns vector collect one byte from **each** of the four input words,
  so the output object depends on the **joint** content of the set across words,
  which a per-word set object does not record. The set-valued analogue of (H2) is
  therefore strictly weaker than it looks, and Step 1's forcing step is simply not
  available.
- **Step 2 — UNDEFINED in general, SURVIVES for the translation-equivariant
  sub-class.** Step 2 presupposes Step 1's output, an invariance of `pi` on `F^4`;
  for a set-valued object the domain is the power set of `F^4` and "invariance
  under a translation" is a different statement. Where the object commutes with
  translations — that is, where `pi(S + v)` is determined by `pi(S)` and `v` — the
  sweep argument of §2 goes through verbatim, because it is a statement about `M`
  and about which coordinates are free, and neither mentions `pi`.
- **Step 3 — SURVIVES verbatim.** It is pure group theory on translations plus the
  strong connectivity of the `(lambda,k)` graph. Once a global invariance exists it
  is indifferent to what kind of object was invariant.

So the departure is **entirely in Step 1**, at the marginal-versus-joint gap. This
also disposes of CAND-A2 (lift `pi` to sets and re-run): the lift changes nothing
in Steps 2–3 and destroys Step 1.

### 3.3 The coupling witness — measured

Executed, not argued. Two state sets are built with **identical per-word
marginals** and different cross-word coupling (`S = {s, s'}`; `T` swaps word 0
between them). Any object that is a function of the four marginals must agree on
both; any object that separates them therefore cannot satisfy the set-valued
analogue of (H2) at a single interface. 200 seeded trials (`seed 807032026`) × 4
output words; all 200 trials had identical per-word marginals by construction.

| object | separations / 800 | reading |
|---|---|---|
| coordinate-wise XOR sum (OBJ-807-1) | **0** | never separated — survives this obstruction |
| multiset of the output word (OBJ-807-3) | **745** | broken |
| multiset of output byte, row 0 (OBJ-807-2) | **700** | broken |
| support size (OBJ-807-4) | **0** | not broken by this witness |
| F-affine rank (OBJ-807-5) | **0** | not broken by this witness |

**P_a1: PARTIAL — discrepancy recorded, not reconciled.** The XOR-sum half is
confirmed exactly and is the point: the object the witness cannot touch is the
**additive** one, which is the integral family, which is off-limits. The support-size
and F-affine-rank halves were predicted broken and were **not** broken. The cause is
a limitation of the witness design, found after measurement: it uses 2-element
sets, on which support size is 2 and affine rank is 1 for both sets generically, so
the witness has no power against those two objects. The prediction is left as
written; a supplementary larger-set computation was **not** run (budget), and is
named as a residual (§4.4).

An object **not** separated by the witness is **not** thereby shown to propagate; it
merely survives this one obstruction. That is stated in the artifact itself.

---

## 4. Outcomes at the closure standard

Both outcomes are negative or null. Each is stated with a named obstruction, an
argument, and forward guidance — not as a count of things tried.

### 4.1 OD-3

**Outcome: `NO_ADMISSIBLE_MEMBER`, with an obstruction.**

- **Named obstruction: the marginal/joint gap at Step 1.** ShiftRows couples the
  four input words into every output word, so a per-word set-valued object records
  marginals while the interface acts on the joint. The set-valued analogue of (H2)
  can only constrain objects that are insensitive to the coupling — and the
  canonical such object, measured to be exactly the one the coupling witness cannot
  separate, is the **additive** one, i.e. the integral family, which is off-limits.
- **Argument:** §3.2 (which step departs and where) plus §3.3 (the measured witness).
- **Forward guidance:** a set-valued candidate that is **not** a function of the
  per-word marginals is not an OD-3 object at all — it is a multi-word object and
  belongs to **OD-2**, whose bookkeeping is the thing that would have to be redone.
  The productive move from here is OD-2, not further OD-3 enumeration. This is
  guidance, not a ruling; the disposition of OD-3 belongs to the Coordinator.

### 4.2 Hole (ii)

**Outcome: the hole is narrowed, and narrowed in an unexpected direction.**

- The **named place** where the proof was said to consume the quantifier — Step 2's
  sweep of `u_k` over all of `F` — **is not where the restriction bites.** The sweep
  survives for 87.5 % of admissible configurations and needs only one free byte in
  the right place. To that extent hole (ii) **closes**: the claim that Step 2's sweep
  consumes the full quantifier is, in this analogue, too strong.
- **The hole is nevertheless real, and its location has moved.** The restriction
  bites at **Step 2's re-application of Step 1**, which needs a translation with all
  four coordinates nonzero to be realisable as a difference at some input word, and
  therefore needs some input word to be **entirely free**. Measured: every delta-set
  tested (1, 2, 4 and 8 active bytes), the word-1-frozen 12-active set and the
  13-active minimal pattern all leave the closure short of forcing constancy; only
  the 15-active fixed-byte set and the unrestricted set complete it.
- **Where the residual now lives, named.** Objects required to propagate only on a
  state set in which **no input word is entirely free** — which includes every
  delta-set of the shapes tested — are untouched by the machinery. That family is
  large, and it contains exactly the delta-sets of the integral and DS-MITM
  families, which are off-limits to this campaign for independent reasons. So the
  residual is real but its most prominent inhabitants are already excluded.
- **Forward guidance:** the sharp question this hands to the next batch is whether
  the "some input word entirely free" condition is necessary as well as sufficient.
  That is decidable by exhaustive computation over all `2^16` active patterns in the
  same analogue and was not affordable here (§4.4).

### 4.3 The analogue is an analogue

Every reading above is in **GF(2^4)**. Stated explicitly: **these readings are not
evidence about GF(2^8), and they are certainly not about AES.** The transfer
argument, given rather than assumed, differs by reading:

- **Transfers by a field-independent argument:** the `{1, |F|}` dichotomy and the
  criterion `reach_k = F` iff `J_p(i) != {}`. The mechanism is `M[k][l] != 0` and
  `M[k][l]·F = F`, which holds in any field. Only the value 16 changes, to 256.
- **Transfers by a counting argument, with arithmetic to redo:** the count 57 and
  the 12.5 % / 87.5 % split. They depend only on the 16-position ShiftRows
  incidence structure and not on the field, so the same numbers should arise over
  GF(2^8) — but this was **not** computed, and is not asserted as measured.
- **Does NOT transfer without recomputation:** everything in §2.4. The closure
  fixpoint depends on the `(lambda,k)` graph, which over GF(2^8) has 1020 nodes and
  measured diameter 30, against 60 nodes here. The **positive control**, the three
  **nulls** and the constancy verdicts are readings about this analogue only.
- **Does not transfer at all:** anything about AES. Nothing here touches SubBytes,
  key schedule, round counts or any cipher.

### 4.4 Residuals, named

1. **CAND-B4** (killed by the pre-screen, `n` unbounded): iterating the restricted
   closure across successive interfaces while tracking domain growth. Untouched by
   design; it is the multi-interface form of hole (ii).
2. **No exhaustive characterisation.** The constancy verdict was computed for 11
   named sets, not for all `2^16` patterns. The "some input word entirely free"
   reading is a **description of the measured family**, not a proved criterion.
3. **No surviving-partition certificates for the restricted target cases.** The
   a-priori certificate budget of 6 was consumed by the first failing job in job
   order (null_1). The budget was **not** raised afterwards, because raising a cap
   after seeing which cases consumed it is outcome-directed.
4. **The group (a) witness has no power against support size or F-affine rank**, as
   measured; a larger-set witness was not run.
5. **Hole (i)** (word-position-dependent families) is untouched and deferred to
   BATCH-005, by the task card.
6. **`PROP-701-I` remains not established**, and nothing here changes that.
7. **Contradiction with a committed record, recorded as such.** TASK-20260801-801
   §5 states the proof "does not survive the restriction even partially" and names
   Step 2's sweep as one of two reasons. §2.5 measures the sweep clause to be too
   strong in this analogue. The BATCH-003 record **stands as written**; this is a new
   record that supersedes nothing and edits nothing, and the disagreement is a
   matter for the independent review in TASK-20260801-809.

---

## 5. Promotion gates

**NOT ENGAGED.** No cost statement and no asymptotic statement is made anywhere in
this package — no attack, no distinguisher, no complexity figure, no exponent, no
`sota_delta`, no bit-margin, no literature comparison. Gates (1)–(3) are therefore
recorded as `not_engaged` in `od3_results.json`. Gate (4), independent review plus
a red-team pass, is recorded as **REQUIRED AND NOT PERFORMED BY THIS TASK** for the
whole package regardless: TASK-20260801-809 and TASK-20260801-810 are its named
holders. **No promotion is requested and no gate is asserted satisfied.**

---

## 6. Execution record

Order of events: (1) binding records read; (2) **`prescreen_od3.json` written to
disk and its SHA-256 taken**, before any code and before any execution;
(3) `od3_quantifier.py` written; (4) phases executed; (5) `od3_results.json`;
(6) this report. Exact commands, exit statuses, timings, tool versions, git commit
`3e6b8b735ab9c98724fb69cc03f14cf46137343e`, dirty-tree state, all seeds, every
check that did not run with its reason, and all four deviations are in
`od3_results.json`.

**Determinism.** `--phase sweep` and `--phase closure` use **no random source at
all**; they are exhaustive enumerations in a fixed order and re-execute
byte-identically apart from `wall_clock_seconds`. `--phase gf2` and `--phase od3`
use `random.Random(seed)` with the seeds recorded (`807042026`, `807032026`) and
one further seed for the constants check (`80720260801`).

**Runs, including the one that failed.** Five runs. Run 4 (`--phase closure
--closure-max-seconds 150`) was **killed at 120 s by the invoking shell's
tool-level timeout** — not by the phase's own cap and not by any mathematical
condition. That is **infrastructure signal**, produced no output, and is reported as
a run rather than omitted. Run 5 repeated it with a lower internal cap and
completed with `capped = false` and an empty `not_run` list.

**Budget.** Declared 1200 s wall clock, 4 GB, 8 runs — a binding stop condition.
Measured compute across all five runs is ~254 s (including run 4's 120 s), and
peak memory is far under the cap (the largest structures are 61 bitmasks of 8 KB).
**The declared budget was exceeded in session elapsed time, in authoring rather
than in compute.** That is recorded here and as DEV-807-4 rather than concealed,
and its consequences are the residuals 2, 3 and 4 of §4.4 — the work that was
dropped rather than done, named.

**Instrument work.** None, of any kind. No mutation-control work, no harness
repair, no escape enumeration, no GATE-601-A, no `reject_scoped`. No BLOCKER arose.

**No official state changed.** No ledger record, no hypothesis status, no evidence
strength, no knowledge promotion, no closure, no `reject_scoped`.
