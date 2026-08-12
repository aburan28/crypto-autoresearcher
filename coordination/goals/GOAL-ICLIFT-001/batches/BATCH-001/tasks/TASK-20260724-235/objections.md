# TASK-20260724-235 — Red-team objections to the EXP-XEDN-002 interpretation

Independent red team. Target: `EXP-XEDN-002` as committed in snapshot
`9f9186c65257aa30458c56d435bc6289e6aaeed7` (receipt
`coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/archives/TASK-20260724-231/snapshot-receipt.json`,
`parent_sha 68e375f`, sha recorded in `.../BATCH-001/dispatch_queue.json`).
Verified `git diff 9f9186c -- experiments/EXP-XEDN-002 experiments/EXP-XEDN-001`
is empty, so the artifacts read here are the committed ones. The other
reviewers' task directories (TASK-20260724-232/233/234) are untracked in the
working tree and were deliberately **not** read: they are not durable evidence
and reading them would compromise independence.

**Attack surface.** Not arithmetic. An independent validator has already
re-derived and brute-forced the closed form, and I reproduced its central
combinatorial input myself as a by-product of probe 1 (§2: `Q(p) = 152, 738,
5450` at `p = 5, 7, 11`, by brute-force enumeration with an independent
`gcd(y, y')` squarefreeness test). The attack is **model error**: whether the
frozen family, slot shape, predicate, measure, and multi-section threshold
formalise anything that the xedni idea needs.

**Probes.** Four throwaway numerical probes were run under `/tmp/rt235`
(scratch, no run records, no evidence status, nothing committed). They import
`experiments/EXP-XEDN-001/xedni_sections.py` read-only and modify nothing.
Their code is reproduced or fully specified below so every number is
recomputable.

---

## 1. Summary of position

`conclusion_requires_narrowing`.

The measured quantity is exact and its verdict against H-XEDN-001 **as literally
written** is correct: `alpha = 3`, so `alpha < 1/2` is false. That part cannot be
overturned. But three of the eight things the Coordinator would be closing are
not what was measured:

| what a closure would suggest | what was actually measured |
|---|---|
| the function-field xedni lift is rare | a **uniform-measure per-slot** square density; the **constructed** measure gives success rate 1.0000 (probe 3) |
| candidate B2's surface family is closed | a family every member of which is `j = 0` and iso-trivial — exactly B2's excluded class |
| `P[>= 9 sections]` is far below `p^-1` and falling | true in the **monic** convention; in the **free-`x`** convention already in the run record it is `7.89e-3 -> 8.82e-3` (rising) with the gap to `p^-1` closing (§4) |

The iso-triviality finding **is fatal** to reading this as a closure of candidate
B2. It is **not** fatal to the exponent: I derived and verified that the
non-isotrivial general rational elliptic surface family gives the same
`alpha = 3` (§2). So the honest disposition is a real but narrow negative result
with two named formalisation defects, not a closure of the route.

---

## 2. RT-2 probe: does `a(t) != 0` change the exponent? (No — derived and verified)

The sharpest form of the iso-triviality objection would be "the exponent is an
artifact of `j = 0`". I tested it rather than asserting it.

**Family.** `y^2 = x^3 + a(t) x + b(t)` over `F_p`, `deg a <= 4`, `deg b = 6`
exactly, slot = monic quadratic `x`, predicate = the frozen `is_square_poly`.
This is the *general* rational elliptic surface shape, with `j` non-constant for
`a != 0`.

**Derivation.** Fix `a` and `x`. `f := x^3 + a x + b` and `b |-> f` is a
translation bijection, so for fixed `(a, x)` the hit count is the number of `f`
that are nonzero squares with squarefree root, subject to `deg b = 6` exactly.
With `x` monic of degree 2 and `deg a <= 4`, `[t^6](x^3 + a x) = 1 + a_4`, so the
condition is `[t^6] f != v` with `v := 1 + a_4`. Writing `f = y^2` with `y != 0`
squarefree, `[t^6] f = y_3^2`, and with `M_2 = p^2 - p`, `M_3 = p^3 - p^2`:

```
2 Q_v = [v != 0] * (p-1)(1 + p + M_2)  +  (#{y_3 != 0 : y_3^2 != v}) * M_3
      = (p-1)(p^3 - 2p^2 + 1)   if v is a nonzero square   (the frozen v = 1 case)
      = (p-1)(p^3 + 1)          if v is a non-residue
      = p^2 (p-1)^2 / 1 ... i.e. 2Q_0 = (p-1) M_3   if v = 0 .
```

Summing over the `p` values of `a_4` collapses neatly:

```
sum_{v in F_p} 2 Q_v = (p-1)^2 (p^3 + 1)                          [verified exactly]
P_slot^{deg a <= 4}(p) = sum_v Q_v / ((p-1) p^7)
                       = (p-1)(p^3 + 1) / (2 p^7)
                       = (1 - 1/p)(1 + p^-3) / (2 p^3) .
```

**Limiting exponent `alpha = 3` exactly, constant `1/2`** — identical asymptotics
to the frozen `a = 0` family, and numerically identical to the `a = 0` free-`x`
formula of `derivation.md` §1.7 (checked as exact rationals at all eight sizes).

**Verification (probe 1).**

* `Q_v` closed form vs brute-force enumeration over every `y` of degree `<= 3`
  with an independent `gcd(y, y')` squarefreeness test: exact agreement for all
  `v` at `p = 5, 7, 11` (21 cases). At `v = 1` this reproduces the frozen
  family's `Q(p) = 152, 738, 5450` — an independent confirmation of arm A's
  combinatorial core.
* `sum_v Q_v = (p-1)^2(p^3+1)/2` exact at `p = 5, 7, 11, 13, 101`.
* **Exhaustive complete-`b`-marginals with the frozen predicate and `a != 0`.**
  For a fixed `a` of degree 4 and `x = t^2 + 2t + 3`, every one of the
  `(p-1)p^6` values of `b` was classified by `is_square_poly`, at `p = 5`
  (62,500 each) and `p = 7` (705,894 each), for one `a` in each of the three
  `v`-classes:

  ```
  p=5 a4=0 (v=QR ) frozen hits=152   Q_v closed=152   OK
  p=5 a4=1 (v=NQR) frozen hits=252   Q_v closed=252   OK
  p=5 a4=4 (v=0  ) frozen hits=200   Q_v closed=200   OK
  p=7 a4=0 (v=QR ) frozen hits=738   Q_v closed=738   OK
  p=7 a4=2 (v=NQR) frozen hits=1032  Q_v closed=1032  OK
  p=7 a4=6 (v=0  ) frozen hits=882   Q_v closed=882   OK
  ```

**Exact `alpha_eff`, non-isotrivial family vs frozen family:**

| pair | `deg a <= 4` | frozen `a = 0` |
|---|---|---|
| 101 -> 211 | 2.992943 | 2.985781 |
| 211 -> 431 | 2.996601 | 2.993178 |
| 431 -> 809 | 2.998275 | 2.996544 |

**Consequences.**

1. De-isotrivialising the family does **not** rescue `alpha < 1/2`. Anyone
   objecting "you measured the wrong family, so the exponent is unknown" is
   wrong about the exponent.
2. This is a **fourth** exact confirmation of Lemma D2's marked counting
   heuristic, in the configuration that matters most (`A = 4, B = 6, d = 2,
   e = 3`: `c_slot = max(6,6,6,6) - 3 = 3`), beyond the three in
   `derivation.md` §2.3.
3. It is a **red-team probe, not a run record.** The Coordinator may not record
   the broader family as measured evidence. What it licenses is a cheap
   successor contract, and a warning that the iso-triviality defect is a defect
   of *representativeness*, not of the number.

---

## 3. RT-5 probe: the measure is the wrong side of xedni

`P_lift` is defined against the **uniform** measure on the family. Xedni does
not sample surfaces; it **constructs** one through prescribed points
(`KN-LIT-020`: "lifts several points from `E(F_p)` ... and chooses a curve
`E/Q` through them"). `derivation.md` §2.6 case 6 concedes this in one line
("On a structured subfamily the lift probability can be `1` by construction");
the concession is much larger than the line makes it look.

**Probe 3a.** For a target `Y^2 = X^3 + B_0` over `F_p` and any point
`(X_0, Y_0)` on it, take `x := t^2 + t + X_0` and `y := c t^3 + Y_0` with
`c^2 != 1`, then `b := y^2 - x^3`. Then `deg b = 6` exactly (so the surface is
**inside** the frozen census family), `b(0) = Y_0^2 - X_0^3 = B_0` (so the fibre
at `t_0 = 0` **is** the target curve), and `(x, y)` is a section through the
prescribed point. Attempted for every `(B_0, point)` pair:

```
p=  5: attempted=25     successes=25     failures=0   rate=1.0000
p=  7: attempted=49     successes=49     failures=0   rate=1.0000
p= 11: attempted=121    successes=121    failures=0   rate=1.0000
p= 13: attempted=169    successes=169    failures=0   rate=1.0000
p=101: attempted=10201  successes=10201  failures=0   rate=1.0000
```

against `P_lift(101) = 4.756857e-07`. The two numbers are 6.3 orders of
magnitude apart and both are exactly right: they are answers to different
questions.

**Probe 3b.** Exact count of frozen-family configurations
`(b, S_1..S_m)` with `deg b = 6`, `b(0) = B_0`, and `m` sections through `m`
distinct prescribed points of the fibre at `t_0 = 0`, divided by the number of
prescribed point tuples (mean per prescription):

| convention | `m` | `p = 5` | `p = 7` | `p = 11` |
|---|---|---|---|---|
| monic | 1 | 374 | 1713 | 11978 |
| monic | 2 | 17.2 | 200.9 | 168.4 |
| monic | 3 | 0 | 62.45 | 5.236 |
| free `x` | 1 | 2496 | 14394 | — |
| free `x` | 2 | 430.4 | 14430 | — |
| free `x` | 3 | 134.4 | 29460 | — |

For `m = 1` the count is **exactly `p^3(p-2)`** per prescription (375, 1715,
11979, minus exactly `p` configurations for the single prescribed point with
`Y_0 = 0`, where `y = 0` is excluded), i.e. `Theta(p^4)` and **growing**, while
`P_lift = Theta(p^-3)` and shrinking. For `m = 2, 3` the counts stay in the
hundreds-to-tens-of-thousands at `p = 7, 11` and oscillate with `p mod 3`
(see §4), so no exponent is determined at these sizes — but they are nowhere
near zero.

**Consequence.** A closure of the uniform-measure question licenses nothing
about the constructed-measure question. Every recorded sentence must say
"uniform-measure per-slot", never "the lift is rare".

---

## 4. RT-3: the free-`x` `P[>= 9]` numbers already in the run record

`runs/RUN-XEDN-002-C/raw-result.json` contains a `free_x_frozen_semantics`
histogram that `analysis.md` §4 and `execution-report.yaml` never report at
`s = 9`. Recomputed from that file:

| convention | `p` | `P[>= 9 slots]` | `p^-1` | ratio | `P[>= 9 points]` | ratio |
|---|---|---|---|---|---|---|
| monic | 5 | 0 | 0.200000 | 0 | 0 | 0 |
| monic | 7 | 0 | 0.142857 | 0 | 1.289145e-04 | 0.0009 |
| monic | 11 | 0 | 0.090909 | 0 | 0 | 0 |
| monic | 13 | 1.346645e-06 | 0.076923 | 0.0000 | 5.588578e-05 | 0.0007 |
| **free `x`** | 5 | 0 | 0.200000 | 0 | 0 | 0 |
| **free `x`** | **7** | **7.893536e-03** | 0.142857 | **0.0553** | **1.304020e-02** | **0.0913** |
| **free `x`** | 11 | 0 | 0.090909 | 0 | 0 | 0 |
| **free `x`** | **13** | **8.815141e-03** | 0.076923 | **0.1146** | **1.375464e-02** | **0.1788** |

(`510588 / 57921708 = 8.815141e-03`; `5572 / 705894 = 7.893536e-03`.)

Three things follow.

1. `analysis.md`'s "at `p = 13` it is smaller by a factor of `5.7e4`" is a
   **monic-convention** statement. In the free-`x` convention — which
   `derivation.md` §2.4 itself identifies as the natural integral-section shape
   of a rational elliptic surface (`c_surf = 0`) — the factor is **8.7**.
2. The free-`x` value **increases** with `p` (`7.89e-3 -> 8.82e-3`) while `p^-1`
   decreases, so the ratio to `p^-1` **doubles** (0.055 -> 0.115). If it stayed
   near `9e-3`, it would cross `p^-1` around `p ~ 113` — i.e. below three of
   the four contracted sizes. Two data points do not make a trend, which is
   exactly the point: the criterion's verdict is undetermined in this
   convention.
3. Everything per-surface oscillates with `p mod 3`. The event is identically
   zero at `p = 5, 11` (`p = 2 mod 3`, no `mu_3`) and positive at `p = 7, 13`
   (`p = 1 mod 3`). Only **two sizes per residue class** were computed, and only
   **one** of the four contracted sizes (`211`) is `1 mod 3`. No decay statement
   about any per-surface quantity is supported. The executor reports the
   oscillation for `P[>= 1]` (`derivation.md` §3 observation 3) but not for
   `s = 9`.

---

## 5. RT-4 probes: distinct is not independent, and `s >= r+1` is neither
necessary nor sufficient

`s >= 9` comes from `r <= 8` (Shioda–Tate) plus "a relation needs `s >= r + 1`".
Both halves are shakier than the record suggests. The bound `r <= 8` is
**correct** for this family — for squarefree `b` of degree 6 the discriminant is
`-432 b^2`, giving six type-II fibres, all irreducible, with a smooth fibre at
infinity, so `sum_v (m_v - 1) = 0` and `rho = r + 2` with `rho = 10`, hence
`r = 8` *geometrically and generically*. That is worth stating plainly: the
frozen family is the **maximal-rank** case, the opposite of candidate B2's
"rank-1 elliptic surface" mechanism. What fails is the inference from `s`.

**Probe 2a — a surface with 4 counted slots has infinitely many sections.**
In-family surface at `p = 13`: `x* = t^2 + 2t + 3`, `y* = 2t^3 + t + 1`,
`b = y*^2 - x*^3 = [0, 0, 3, 12, 9, 7, 3]` (`deg b = 6`, `b_6 = 3`). The frozen
predicate finds 4 monic slots and 15 free-`x` slots. Computing multiples with
the group law over `F_13(t)`:

```
 1S : deg num(x) =   2, deg den(x) =   0   (counted by the census)
 2S : deg num(x) =   8, deg den(x) =   6   (not counted)
 3S : deg num(x) =  18, deg den(x) =  14   (not counted)
 ...
12S : deg num(x) = 288, deg den(x) = 284   (not counted)
```

`deg num x(nS) = 2n^2` exactly for `n = 1..12`, all distinct, none torsion. Once
the rank is `>= 1`, `E(F_p(t))` contains **infinitely many** distinct sections.
So `P[>= 9 distinct sections]` as measured is a statement about one bounded
height window, not about the group; and the measured `P[>= 1 free-x section]`
of `0.353 / 0.395` at `p = 5, 11` is already a lower bound on `P[rank >= 1]`,
hence on `P[>= 9 distinct sections in E(F_p(t))]` — a constant, not `p^-1`.

**Probe 2b/4 — the sections that *are* counted are dependent, with a
tautological relation.** For `p = 1 mod 3` the `j = 0` curve has the order-3
automorphism `w : (x, y) |-> (zeta x, y)`, and `1 + w + w^2 = 0` in `End`. On
the probe surface all 15 free-`x` sections fall into **5 `mu_3` orbits of size
3**, and every orbit sums to the zero section (verified by the group law):

```
orbit 0: size 3  leading x-coeffs [0, 0, 0]  sum = O
orbit 1: size 3  leading x-coeffs [1, 3, 9]  sum = O
orbit 2: size 3  leading x-coeffs [1, 3, 9]  sum = O
orbit 3: size 3  leading x-coeffs [1, 3, 9]  sum = O
orbit 4: size 3  leading x-coeffs [1, 3, 9]  sum = O
```

and only the leading-coefficient-1 member of each orbit is visible to the monic
slot definition (the monic census sees 4 of these 15). The relation
`S + wS + w^2 S = O` specialises to `P + wP + w^2 P = O`, which holds at
**every** point of **every** smooth `j = 0` fibre — checked exhaustively on
4,788 affine points at `p = 7, 13, 31, 61` (all smooth fibre classes, zero
exceptions). It is a tautology and carries no discrete-log information.

Among the 5 orbit representatives an exhaustive `{-1, 0, +1}` search finds
exactly one further relation (up to sign): `R_1 + R_3 + R_4 = O`. So on a
surface the free-`x` convention credits with 15 sections, the rank of the span
is at most 4 and **every** relation found has coefficients in `{-1, 0, +1}`.

**Probe 2a, again, from the other side — the pigeonhole relation can be
vacuous.** Among `{S, 2S, ..., 9S}` the guaranteed dependence is
`2S + (-2S) = O` (verified `= O`), a relation whose specialisation says
`2P = 2 * P`. Conversely, if a surface's rational sections span rank 2, three
sections already force a relation; `s >= 9` is a *sufficient* condition for
guaranteed dependence, not a necessary one for existence. Treating the failure
of a sufficient condition as closure is a logic error.

**Consequence.** The monic number understates the distinct-section count, the
free-`x` number overstates the independent-section count, and the attack-relevant
quantity — the rank and the relation coefficients — was not computed at all
(`execution-report.yaml`: "No Mordell-Weil rank, height pairing, or torsion
computation was performed"). Candidate B2 names the height-pairing Gram matrix
as its central object ("information retained: the height-pairing Gram matrix
(exact lattice)"). The experiment measured everything except it.

---

## 6. RT-6: a verified off-by-one in `derivation.md` §2.5

`derivation.md` §2.5 charges `2 + m` conditions for the prescribed
configuration — `a(t_0) = A_0`, `b(t_0) = B_0`, and one per section — and
concludes

```
dim <= dim_a + B - 1 - m - sum_i c_surf,i .
```

For the **`a`-absent** family there is no `a(t_0) = A_0` condition, so only
`1 + m` conditions exist and the correct count is one larger. Recounting from
scratch: `7` parameters for `b`, `(delta + e + 1)` per section, `7` equations per
section, `1 + m` prescriptions:

```
monic x (delta = 2):  dim = 7 + 6m - 7m - 1 - m = 6 - 2m
free  x (delta = 3):  dim = 7 + 7m - 7m - 1 - m = 6 -  m
```

Probe 3b confirms both at `m = 1` by **exact count**: the monic mean per
prescription is exactly `p^3(p - 2)` (measured 374, 1713, 11978 at
`p = 5, 7, 11`), i.e. `dim = 4`, where §2.5's formula gives `3`; the free-`x`
mean is `~0.8 p^5`, i.e. `dim = 5`, where the formula gives `4`.

Effect on the stated conclusion: the threshold "the `c_surf = 0` abundance is
destroyed once `m > dim_a + B - 1` ... at `m >= 6` for the frozen `a = 0`,
`B = 6` family" should read `m >= 7` in the free-`x` convention (and `m >= 4`
in the monic one). The error is in the direction that makes the obstruction look
*stronger* than the count supports. The `m = 9` sign is unchanged
(`dim = 6 - 9 = -3 < 0`), and the full rational elliptic count (`dim = 10 - m`,
so `dim <= 1` at `m = 9`) is correct as written. So the qualitative statement
survives; the quoted threshold must not be recorded as-is.

Separately, §2.5's count is a **transversality-free** parameter count.
`dim <= 1` at `m = 9` on the full family is consistent with an empty variety and
with a positive-dimensional one; the executor is right that it does not exclude
the classical construction, and it equally does not establish that the
construction exists. Neither direction may be recorded.

---

## 7. RT-7: `alpha = 3` is not the JKSST prediction

`H-XEDN-001` states: "The competing classical prediction, inherited from the
Jacobson-Koblitz-Silverman-Stein-Teske analysis of xedni and from the naive
square-density heuristic recorded in the harness, is alpha = 3."

The ledger's own record of JKSST says something different.
`knowledge/literature/KN-LIT-021.md`: "The failure is driven by an absolute
bound on the size of the coefficients of any relation the lifted points can
satisfy". `ideas/artifacts/ECDLP-IDEA-005/p1543_global_lift_torsion_defect_gate.md`
("Xedni fixed-arity control"): "Random finite points have such a relation with
probability `O(1/p)=O(1/N)`". And `research_directions_20260718.md` line 428:
"JKSST 2000: `P_lift -> 0` like `(log p)^{-Theta(1)}` or worse".

`alpha = 3` is the **naive square-density parameter count** (7 sextic
coefficients minus 4 cubic ones), stated as such in `H-XEDN-001`'s own
`mechanism` field. Confirming `alpha = 3` confirms that count. It is a different
quantity (per-slot square density vs probability of a usable dependence), in a
different measure (uniform vs constructed), by a different mechanism (parameter
codimension vs coefficient bound). Recording "the exact census confirms the
classical JKSST prediction" would misattribute the literature and would
double-count `KN-LIT-021` as new internal evidence.

---

## 8. RT-10: what would actually have to be true, and where the real obstruction is

Concretely, a function-field xedni relation source needs all of:

1. a surface in the family whose fibre at some `t_0` is the target curve, with
   `m` sections specialising to the prescribed points — **probability 1 for
   `m = 1`, abundant for `m = 2, 3`** (probe 3);
2. a relation `sum n_i S_i = O` in `E(F_p(t))` among those sections —
   **guaranteed once `m >= 9`** by `r <= 8`;
3. relation coefficients `n_i` large enough to express a *random* discrete log,
   i.e. `|n_i|` growing with `p`;
4. a cost model for finding the configuration in (1) and the relation in (2).

The census measures none of these. It measures the uniform-measure per-slot
density, which appears in none of them.

And (3) is where the route dies, for a reason this experiment cannot see. On
this family with squarefree `b` of degree 6 the fibration has six irreducible
type-II fibres and a smooth fibre at infinity, so with Shioda's height formula
`h(P) = 2*chi + 2(P.O) - sum_v contr_v` and `chi = 1`, `contr_v = 0`,
`(P.O) = 0` for an integral section, **every section of the frozen shape has
height exactly 2** — it is a *root* of the Mordell–Weil lattice, which for a
rational elliptic surface with all fibres irreducible is `E_8`. Numerical
support from the probes: `deg num x(nS) = 2n^2` exactly for `n = 1..12`
(consistent with `h(nS) = n^2 h(S)`, `h(S) = 2`); the observed maximum free-`x`
slots per surface across `RUN-XEDN-002-C` are `4, 36, 4, 63`, all at most
`120 = 240/2`, and `E_8` has exactly 240 roots; and the `mu_3` orbit relation
`<S, wS> = 1 - (S . wS) = 1 - 2 = -1` is exactly the root configuration whose
three members sum to zero, as verified by the group law.

Relations among `E_8` roots have **absolutely bounded** coefficients — every
relation found on the probe surface has coefficients in `{-1, 0, +1}`. A
specialised relation `sum n_i P_i = O` with `|n_i| <= C` for an absolute `C` can
express only `O(C^2)` of the `~p` possible discrete logs, giving success
probability `O(1/p)`. That is precisely the `KN-LIT-021` / `ECFG-P1543-R1`
`C_0/p` obstruction — and in this setting it needs **no Lang height conjecture**,
because the height bound is a geometric fact about rational elliptic surfaces
rather than a conjectural diophantine one. Escaping it requires sections of
height growing with `p`, i.e. exactly the class the frozen degree shape excludes,
and whose search cost `derivation.md` §2.6 case 8 lists as unmodelled.

**Status of this paragraph:** red-team argument, not experiment output. Its
literature inputs (Shioda height formula; `rho = 10` for a rational elliptic
surface; `E_8` as the Mordell–Weil lattice when all fibres are irreducible) were
used without re-derivation. It must not enter the ledger without its own
independent audit. It is offered because it identifies where a decisive theorem
lives, and because it shows the `p^-3` census is measuring the non-binding
obstruction.

---

## 9. Smaller objections

**RT-8 — arm B coverage.** Full-space frozen-predicate exhaustion was achieved
at `p = 5, 7` only; `p = 11, 13` have complete `b`-marginals for 12 and 6
listed `x` (9.92% and 3.55% of slots). The executor states this in
`analysis.md` §3, `execution-report.yaml` DEV-1, and boundary 8, and mitigates
it with arm C's independent full-space fibering. Sound. No recorded sentence may
say "the frozen predicate was exhaustively validated at `p in {5,7,11,13}`".

**RT-9 — no in-population positive control.** DEV-4: the only planted-recovery
control has `deg b = 5` and therefore lies **outside** the census family, so no
positive control exercises the actual population. This is cheap to fix — probe 2
built an in-family planted surface in three lines (`x* = t^2 + 2t + 3`,
`y* = 2t^3 + t + 1`, `b = [0,0,3,12,9,7,3]`, `deg b = 6`, section recovered by
the frozen predicate, 4 monic slots) — and any successor contract should carry
one.

**RT-11 — the predicate.** Squarefreeness and the `y = 0` exclusion move only
constants (`x1.2303` at `p = 5`, `x1.0100` at `p = 101`; `O(p^-4)`), and I found
no reading of squarefreeness that changes the exponent. The predicate-level
model error is elsewhere: `is_square_poly(x^3 + b)` tests only **integral**
sections at a **prescribed** `x`. For non-integral sections (`x = u/w^2`,
`y = v/w^3`) the correct test is `v^2 = u^3 + b w^6`, and under the reading "this
surface has a section" the answer is `Theta(1)` — at least `0.353` at `p = 5`
and `0.395` at `p = 11` from the free-`x` histogram — not `Theta(p^-3)`. The
quantifier over `x`, not the square test, is what carries the exponent.

**RT-12 — a prior recorded reading that this result falsifies.**
`research_directions_20260718.md` §9.3 records, from the `p = 101` smoke's
0-of-5760: "the xedni rarity obstruction is already visible at toy scale,
consistent with JKSST 2000". Control 3 now shows the expected count was
`0.002740` and `P(observe 0) = 0.997264`: the smoke had essentially zero power
and that reading was unsupported. This is a genuine correction the census earns,
and it should be recorded as a new record rather than left standing.

**RT-13 — model policy.** The handoff requests `review-xhigh`
(GPT-5.6 Sol, `xhigh`). This Claude-family harness cannot resolve it
(`CLAUDE.md` model policy note), and `fallback_allowed: true`. My resolved model
is `claude-opus-5-thinking-max`, verified from the runtime rather than assumed —
the **same** resolved model the executor recorded in `execution-report.yaml`.
`independent_session_required: true` is satisfied (separate session, separate
agent, did not originate the claim), but the "independent `review-xhigh`
session" clause of AGENTS.md rule 12 is met only in the session sense, not the
model sense. That limitation should travel with the decision record.

---

## 10. Baseline comparison

`EXP-XEDN-002` makes no cost claim and no attack claim, and every run sets
`certificate.kind: none`, so there is nothing to compare against a baseline —
which is itself the point worth recording. For the regime candidate B2 targets
(prime-field ECDLP, `n ~ p`), the standing baselines are Pollard rho at
`~0.886 sqrt(n)` group operations with negligible memory, BSGS at `~2 sqrt(n)`
operations with `~sqrt(n)` memory, and, as the specialized baseline B2 itself
names, summation-polynomial / Semaev-style index calculus for the relation
generation step it proposed to undercut with `O(poly(r) log^2 p)` per relation.
Nothing in `EXP-XEDN-002` establishes any stage of that path: no relation is
produced, no rank is computed, no source recovery or target descent is attempted,
and no memory or wall-clock model for a lifting attack is stated. The correct
baseline sentence is that the route has **no cost path at all** at this point,
not that it is slower than rho.

---

## 11. Falsification routes (what would reopen this)

1. **Relation-coefficient growth (cheapest; see the report's
   `cheapest_falsifying_control`).** On the surfaces arm C already flags as
   section-rich, compute the Shioda height Gram matrix of the observed free-`x`
   sections (`<P,P> = 2`; `<P,Q> = 1 - (P.Q)` for integral sections on this
   family), extract a `Z`-basis of the relation lattice, and report
   `max |coefficient|` of the minimal relation at `p in {7, 13, 19, 31}`. If it
   grows with `p`, the relation-source route reopens and the closure must be
   withdrawn. If it stays bounded — as it does on my probe surface, where every
   relation has coefficients in `{-1, 0, +1}` — the route is closed for the
   coefficient-bound reason and the `p^-3` census is beside the point either
   way. Cost: gcds of degree-`<=3` polynomials plus exact linear algebra on
   `<= 9 x 9` rational matrices, for a few hundred surfaces.
2. **Free-`x` `P[>= 9]` trend at `p = 1 mod 3`.** Extend arm C's free-`x`
   histogram to `p = 19` and `p = 31`. If `P[>= 9]` stays near `9e-3` while
   `p^-1` falls, clause (ii) of the falsification criterion fails in the natural
   convention and the multi-section closure must be withdrawn.
3. **Constructed-measure census.** Replace the uniform surface measure with the
   xedni measure: for random target instances, count surfaces with the fibre at
   `t_0` prescribed and `m` sections through prescribed points, for
   `m = 2..9`, in the full rational elliptic family (`deg a <= 4`). Probe 3
   shows this is nonempty and large for small `m`; the `m` at which it empties
   is the quantity that decides the route and it is currently unmeasured.
4. **Higher-height sections.** Census sections with `deg x <= 4, 6` (heights 4,
   6, ...) and measure both abundance and relation-coefficient size. This is the
   only class that could escape the coefficient bound, and it is exactly what the
   frozen degree shape excludes.
5. **Non-isotrivial family, properly contracted.** The probe of §2 says the
   exponent will be 3 again; running it as a real experiment would let the
   closure be recorded for the family B2 actually named, instead of the one it
   excluded.
