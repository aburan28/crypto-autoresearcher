# PREREG-1 — BATCH-4ed139 FROZEN PRE-REGISTRATION

    goal      GOAL-MLKEM-005
    batch     BATCH-4ed139
    task      TASK-20260812-34b86c (Coordinator, pre-registration only)
    notarized by  TASK-20260812-1ed548 (snapshot archive, runs alone, before any measuring task)
    authority DEC-20260812-7c4a1e (AM-17) applying AM-16 of DEC-20260809-afe29b
              and AM-10..AM-14 of DEC-20260808-05b684
    claim tier TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring task
of BATCH-4ed139 may be dispatched until this file is committed by
TASK-20260812-1ed548 and that commit contains **zero** producer artifacts. That
is the split-producer notarization pattern, retained unchanged; it has now worked
four times and has been verified in both directions by four independent sessions.

---

## 0. WHY THE ORDERING IS NOT CEREMONY

The three-way termination clause of section 7 decides what this goal does next.
If it is written **after** the numbers are seen, the batch can only assert an
outcome it chose after seeing them, and six consecutive instrument batches would
be followed by a seventh chosen the same way. Freezing it here, before any
measurement exists, is the entire reason this task runs and is archived alone.

Equally binding in the other direction: nothing in section 7 may be re-read,
re-weighted or "clarified" after the run. A branch that turns out inconvenient is
still the branch that fired.

---

## 1. WHAT IS BEING BUILT AND WHY

### 1.1 The object

`G-VAR2` — the replacement dispersion criterion AM-16(a) specifies, extended by
AM-17(b), (c) and (d). It is an **instrument**, not a proposition about a
lattice. Nothing in this batch bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.

### 1.2 The defect it must not inherit

AM-16(d) validates G-VAR2 against one fixture, `probe_nullroute.py`, whose six
arithmetic routes all live inside family **F0**. Wave 2's `probe_gvar_family.py`
shows that one line of change to the family (**F1**) gives both `rdet` and
`X_null` genuinely large between-basis dispersion while they still read **zero
entries of A**. A criterion scaled on between-basis dispersion alone would admit
them there. So G-VAR2 as specified inherits exactly the defect RT-R1 names, and
**its own fixture cannot detect it**. Neither review wave could see this: wave 1
wrote AM-16 without F1, wave 2 built F1 without ever reading AM-16.

### 1.3 The consequence carried into the criterion

AM-17(c): the separator both fixtures point at is dispersion **on the fibre of
the family over the observable's own declared arguments**. AM-17(d): every
dispersion criterion in this goal must **declare the family it is evaluated on as
part of the criterion**, because the verdict is a joint property of
(observable, arithmetic route, family) and the family has been an undeclared free
parameter exactly as the route was.

---

## 2. FROZEN OBJECTS

### 2.1 Constants

    q          = 3329
    N_BASES    = 8            (basis index i = 0..7)
    tau_rel    = 0.10         (carried unchanged, prereg 1.5 of BATCH-9e3584)
    s_X        = 1.0          (carried unchanged, prereg 1.4 of BATCH-9e3584)
    tau_var    = 1e-3         (NEW, frozen here; see 3.4)

### 2.2 Lattices and grids (carried verbatim from BATCH-9e3584 prereg 1.2/1.3)

    L1 (100,30)  L2 (100,70)  L4 (140,40)  L5 (140,100)
    L7 (20,6)    L8 (20,14)   L9 (30,9)    L10 (30,21)
    L11 (40,12)  L12 (40,28)

    beta grid   d=100: 15,30,35,50,65    d=140: 20,40,45,70,95
                d=20 : 5,10,15           d=30 : 7,15,22    d=40: 10,20,30
    mirrored pairs  (L1,L2) (L4,L5) (L7,L8) (L9,L10) (L11,L12)
    REL1 pair       d=100:(15,65) d=140:(20,95) d=20:(5,15) d=30:(7,22) d=40:(10,30)

38 scored cells per family (10 lattices x their beta grids).

### 2.3 Families — DECLARED AS PART OF THE CRITERION (AM-17(d))

    F0  (frozen)  B_i = [[I_k, A_i], [0, q I_{d-k}]]
                  A_i = default_rng([1,d,k,i]).integers(0,q,size=(k,d-k))
                  |det B_i| = q^(d-k), CONSTANT in i BY CONSTRUCTION

    F1  (nearby)  B_i = [[I_k, A_i], [0, diag(m_i)]]
                  m_i[0] = q + i, m_i[j>0] = q; A_i IDENTICAL to F0
                  |det B_i| = (q+i) q^(d-k-1), VARIES in i

    F0|fib        B_i = [[I_k, A'_i], [0, q I_{d-k}]]
                  A'_i = default_rng([2,d,k,i]).integers(0,q,size=(k,d-k))
                  |det B_i| = q^(d-k), CONSTANT in i

    F1|fib        B_i = [[I_k, A'_i], [0, diag(m)]] with m[0] = q + 3, m[j>0] = q
                  HELD FIXED ACROSS i; A'_i as in F0|fib
                  |det B_i| = (q+3) q^(d-k-1), CONSTANT in i

F0 and F1 are carried verbatim from the two committed fixtures. `F0|fib` and
`F1|fib` are **new draws** (seed prefix 2, not 1) so that a fibre family is never
a relabelling of a scored family. Replication (AM-10): every fibre count is
additionally computed on two further fibre families with seed prefixes 3 and 4,
and reported per family with its dispersion.

### 2.4 Candidate observables and their DECLARED ARGUMENT SETS

The declared argument set is part of the criterion and is declared **here**, by
the Coordinator, before any measurement. Introducing or re-declaring a candidate
observable is a Coordinator and Idea Generator act; a producer may not change a
declared argument set, and a reviewer who believes one is dishonest reports that
as a finding rather than silently rescoring.

| candidate | definition | declared arguments | nuisance args held fixed on the fibre |
|---|---|---|---|
| `X_null` | (beta/d)(1/d) log abs(det B) | d, k, beta, q, abs(det B) | abs(det B) |
| `rdet` | exp(log abs(det B) / d) | d, abs(det B) | abs(det B) |
| `V_evade` | X_null + 1e-9 * A[0,0]/q | d, k, beta, q, abs(det B), A[0,0] | abs(det B), A[0,0] |
| `X_lambda` | X_null + lambda * A[0,0]/q | d, k, beta, q, abs(det B), A[0,0] | abs(det B), A[0,0] |
| `lam1n` | as committed in BATCH-9e3584 | d, k, q, GSO profile (+ beta if any) | d, k, beta, q, abs(det B) |
| `hkz` | as committed in BATCH-9e3584 | d, k, beta, q, HKZ-reduced GSO profile | d, k, beta, q, abs(det B) |
| `rawtail` | as committed in BATCH-9e3584 | d, k, beta, q, raw GSO profile | d, k, beta, q, abs(det B) |
| `X_gso_k` | (1/k) * sum_{j=1..k} log norm(b*_j) of the RAW basis | d, k, q, raw GSO profile — **no beta** | d, k, beta, q, abs(det B) |

`X_gso_k` is introduced **here, by the Coordinator**, as rider (ii)'s
false-refusal control (section 8.2). The wave-2 Red Team correctly declined to
introduce a candidate observable; that act belongs to this record.

### 2.5 Declared arithmetic routes (AM-16(b))

For `X_null`, `rdet`, `V_evade`, `X_lambda` — all six routes of the committed
`probe_nullroute.py`, carried verbatim, with the route recorded beside every
value:

    R0  closed form            (d-k)*log q
    R1  slogdet(B)
    R2  QR of B^T              sum_j log abs(R_jj)
    R3  slogdet(U B)           U a fixed unimodular re-presentation, seed [424242,d]
    R4  0.5 * slogdet(B B^T)
    R5  slogdet(B H)           H a fixed ambient isometry, seed [313131,d]

In F1 and in the fibre families the same six routes apply, with `log abs(det B)`
read from the actual matrix rather than from the F0 closed form. R0 in a family
whose determinant is not q^(d-k) is defined as the exact closed form of **that**
family's determinant, `sum_j log m_j`, and is labelled `R0_closed_form_of_family`.

For `lam1n`, `hkz`, `rawtail`:

    RC  committed per-basis values read from BATCH-9e3584
        tasks/TASK-20260809-cda2f6/results_relvar.json, pinned by sha256 in the
        run manifest, never edited
    RD  recomputation through the FROZEN HKZ pipeline at d <= 40 only
        (L7, L8, L9, L10, L11, L12), fpylll pinned at 0.6.4

For `X_gso_k` (rider ii):

    RQ  QR of B^T,                     log abs(R_jj), j = 1..k
    RG  Cholesky of the Gram B B^T,    log of the diagonal, j = 1..k

**No new reduction beyond the frozen HKZ pipeline, and nothing
reduction-dependent above d = 40.** At d in {100, 140} the reduction-dependent
candidates are available through RC only; that is a declared coverage limit, not
a result (section 7.4).

---

## 3. G-VAR2 — THE FROZEN CRITERION

G-VAR2 is a **conjunction of two clauses**, evaluated per candidate, per route,
per family, per cell, and **reported as a per-cell profile**. AM-16(c) is in
force: the all-cells reduction is withdrawn and no admissibility verdict on a
candidate observable may be reported as an all-cells Boolean.

### 3.1 VAR-S — scaled between-basis dispersion (AM-16(a))

For candidate X, route r, family F, cell c = (lattice with (d,k), beta):

    x_{c,i}   = X^{r,F}(B_i, beta),  i = 0..7
    s_c       = sd over i, ddof = 1
    m_c       = mean over i
    R_{d,k}   = max_{c' at this (d,k)} m_{c'}  -  min_{c' at this (d,k)} m_{c'}
                (the candidate's OWN between-cell range at fixed (d,k),
                 taken over that lattice's beta grid)
    D_c       = s_c / R_{d,k}

    VAR-S(c)  =  ADMIT   if D_c >= tau_var
                 REFUSE  if D_c <  tau_var
                 scale_degenerate  if R_{d,k} == 0 exactly   (see 3.2)

Also reported at every cell, always: `s_c`, `m_c`, `max - min` over i, the
`bit_identical` flag (the old G-VAR statistic, for continuity), `R_{d,k}`, `D_c`,
the route label, the family label and the declared argument set.

### 3.2 THE DEGENERATE-SCALE RULE — frozen here, with both readings named

**A specification hole in AM-16(a), found by writing this pre-registration and
recorded as such rather than repaired silently.** `rdet = exp(log abs(det B)/d)`
**takes no beta argument**, so at fixed (d,k) it is constant across the beta grid
and `R_{d,k} = 0` **exactly, by its definition**. AM-16(a)'s scale is undefined
for every beta-free candidate. Two readings are available and they disagree:

* **naive reading**: `D_c = s_c / 0 = +inf` for `s_c > 0`, so VAR-S **ADMITS**
  `rdet` in F1 — and the F1 fixture then fails.
* **frozen reading (BINDING)**: `R_{d,k} == 0` means the candidate has no scale
  of its own; `VAR-S` is **UNDEFINED** and is recorded as `scale_degenerate` —
  **not a pass and not a fail**. At such cells the G-VAR2 verdict is decided by
  VAR-F alone.

The frozen reading is binding. The producer must **additionally report the naive
reading's verdict beside it at every scale_degenerate cell**, so the choice is
auditable and a successor can re-decide it against the numbers rather than
against this paragraph.

This rule is **not** a disguised refusal rule, and the batch's own numbers will
show it: under it, `rdet` is refused at scale_degenerate cells (constant on the
fibre) while `X_gso_k` — also beta-free, therefore also scale_degenerate — is
**admitted** (non-constant on the fibre). If both were refused, the rule would be
doing the refusing and VAR-F would be decorative; that is a defect a reviewer
should look for and it is named here in advance.

Which candidates are scale_degenerate is otherwise a **measured** outcome and is
not asserted here for anything but `rdet`, whose beta-freeness is definitional.

### 3.3 VAR-F — the fibre clause (AM-17(c))

For candidate X, route r, family F:

Let `F|fib` be the fibre sub-family of section 2.3 holding X's declared nuisance
arguments **fixed across the basis index** while the free content A varies.

    VAR-F(c)  =  PASS   if X is NON-CONSTANT across F|fib at cell c
                 FAIL   if X is CONSTANT across F|fib at cell c

Non-constancy is measured by the same statistic and the same threshold:
`s_c^{fib} / R_{d,k}^{fib} >= tau_var`, with the identical `scale_degenerate`
handling — except that at a `scale_degenerate` fibre cell, non-constancy is
decided by `s_c^{fib} > 0` under the **bit-identity** test carried verbatim from
the producer's own `bit_identical()`. Both statistics are reported at every fibre
cell.

Reported per fibre cell: `s_c^{fib}`, `bit_identical`, the number of distinct
IEEE-754 values over the 8 bases, and the fibre family's seed prefix.

### 3.4 G-VAR2 and the threshold

    G-VAR2 ADMITS X at cell c through route r on family F
      iff  VAR-S(c) == ADMIT  or  VAR-S(c) == scale_degenerate
      AND  VAR-F(c) == PASS
    otherwise G-VAR2 REFUSES at c.

`tau_var = 1e-3` is **frozen here, before the run**, and its basis is stated
plainly because it matters: it is **calibrated on committed numbers**, namely the
escaping routes' between-basis float sd of 1.20e-13 (R2) and 5.44e-14 (R5)
against a between-cell range of order 1, V_evade's 3.91e-10, and `hkz`'s
committed between-basis sd of 0.023888 at L7 beta 5. Any threshold in
(1e-9, 1e-2) separates those three on the committed numbers; 1e-3 sits about 1.4
orders below `hkz`'s own value and about 7 orders above V_evade's.

**The honest consequence, declared in advance**: because the threshold is
calibrated on F0's committed numbers, the F0 fixture is a **weak** test of the
calibration and a **strong** test of the operationalization's *structure* — of
the fibre clause, the degenerate-scale rule and the route quantification, none of
which the calibration determines. **F1 is the test the calibration cannot pass by
construction**, which is why AM-17(b) requires it and why section 7 branches on
it.

### 3.5 What G-VAR2 is NOT, stated before any result

* It is **not** an admissibility gate. It is one clause of the AM-4/AM-8 gate.
* Passing it carries **no** claim that an observable carries lattice information.
* It moves a free parameter; it does not remove one. The family was undeclared
  and is now declared; the arithmetic route was undeclared and is now declared;
  the **declared argument set** is now the free parameter, and it is declared,
  auditable and attackable rather than hidden. **That is the whole of what the
  fibre clause buys.** A reviewer should attack exactly there.

---

## 4. THE TWO FIXTURES AND THEIR DECLARED TARGET BEHAVIOUR

Both fixtures are **committed files** and their target behaviour is declared
**in advance** — in `probe_nullroute.py`'s own committed output for F0, and in
AM-17(b) for F1.

### 4.1 Fixture F0 — `probe_nullroute.py`

    reviews/TASK-20260809-444fe7/probes/probe_nullroute.py
    reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.json

**TARGET BEHAVIOUR (declared in advance):**

* all six routes R0..R5 to `X_null`  → **REFUSED** by G-VAR2
* all six routes R0..R5 to `rdet`    → **REFUSED** by G-VAR2
* `lam1n`, `hkz`, `rawtail`          → **ADMITTED** by G-VAR2

**F0 PASSES** iff every one of the three lines holds at **every scored cell that
is covered**, with coverage reported per candidate and per route.

### 4.2 Fixture F1 — `probe_gvar_family.py`

    reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.py
    reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.json

**TARGET BEHAVIOUR (declared in advance, AM-17(b)):**

* `X_null` → **REFUSED** in F1
* `rdet`   → **REFUSED** in F1

`lam1n`, `hkz` and `rawtail` are **NOT SCORED IN F1** and no target behaviour is
declared for them there: `probe_gvar_family.py` runs no reduction and F1's
reduced bases do not exist. Their absence from F1 is a declared scope limit and
is never reported as a failure.

**F1 PASSES** iff both lines hold at **every** one of the 38 scored cells, for
**every** declared route.

### 4.3 The reproduction consistency check

`X_null` computed **definitionally through the matrix** must reproduce the
notarized BATCH-9e3584 prereg 2.6 table at 38 of 38 cells in F0 to 6 decimals,
or the F0/F1 contrast is an implementation contrast rather than a family
contrast. Labelled a **CONSISTENCY CHECK** under AM-15(a); it is reported and it
does not count as a prediction.

---

## 5. THE V_evade PREDICTION

`V_evade(B, beta) = X_null(B, beta) + 1e-9 * A[0,0] / q` — the wave-2 Validator's
O-2 construction, carried verbatim.

**P-V1, restated from DEC-20260812-7c4a1e and NOT re-derived here:** on the
committed numbers V_evade carries a between-basis float sd of 3.91e-10 against a
between-cell range of order 1, so **VAR-S alone REFUSES V_evade** — i.e. O-2
defeats G-VAR as frozen but does **not** defeat its replacement, while RT-R1's F1
defeats both.

    P-V1 is adjudicated on VAR-S ALONE, at every scored cell of F0, through at
    least two declared routes. That is the object AM-16(a) specifies and the
    object the decision predicted; the full G-VAR2 verdict on V_evade is reported
    separately and is not P-V1.

**FALSIFIER:** VAR-S admits V_evade at **any** scored cell (`D_c >= tau_var`).

**IF FALSIFIED:** the scaled operationalization is defeated by a 1e-10
perturbation and **AM-16(a) needs its own replacement, not merely the fibre
extension**. Reported as such. No lane closes on this alone.

**CLASSIFICATION, declared in advance under AM-15(a):** P-V1's falsifier is
empty conditional on reproducing a reviewer's committed measurement (3.91e-10),
so **P-V1 IS A CONSISTENCY CHECK** and does not count toward this batch's
empirical content. It is still run and still reported exactly as
DEC-20260812-7c4a1e requires; classifying it does not excuse it.

---

## 6. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 6.1 The graded MUST-PASS guard (AM-16(e))

`X_lambda = X_null + lambda * A[0,0]/q` over the frozen grid

    lambda in {0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1}

`lambda = 0` is `X_null` itself; `lambda = 1e-9` is `V_evade`. The producer
reports, per cell, the **crossing amplitude** `lambda*` — the least grid value at
which VAR-S flips from REFUSE to ADMIT — and the full profile. This measures
**resolution**, not merely non-deadness, which is exactly what AM-16(e) requires
and what a binary guard cannot give.

**P-G1 (MUST-PASS, could-not-PASS live):** the guard crosses somewhere in the
grid at a majority of scored cells.

**R2-OUT-V (VOID row):** if the guard does **not** cross anywhere in the grid,
VAR-S is dead at this scale and **every G-VAR2 verdict in this batch is VOID**,
both fixtures included. The batch then reports an instrument defect and nothing
else. This row is live and is not a straw man.

### 6.2 could-not-FIRE — the criterion could never refuse anything

Would hold if `tau_var` were 0, or if `D_c >= tau_var` everywhere by
construction. **We are not in it, and it is measured rather than asserted**:
`X_null` in F0 has `s_c = 0` exactly at all 38 cells on the committed numbers, so
`D_c = 0 < tau_var`. The producer reports the measured `s_c` distribution rather
than citing this sentence.

### 6.3 could-not-PASS — the criterion could never admit anything

Would hold if `tau_var` were above every real candidate's dispersion. **We are
not in it**: `hkz`'s committed between-basis sd is 0.023888 at L7 beta 5, giving
`D ~ 2.4e-2 >> 1e-3`. Measured and reported, not asserted. The graded guard of
6.1 is the second, stronger instance of the same control.

### 6.4 could-not-fail on the FIBRE clause specifically

* could-not-FAIL: if every fibre family happened to hold X constant for every
  candidate, VAR-F would refuse everything and the clause would be a constant.
  **Live check:** `X_gso_k`, `lam1n`, `hkz` and `rawtail` read the GSO profile,
  which varies with A on the fibre; the producer must exhibit at least one
  candidate that VAR-F **passes** or report the clause as degenerate.
* could-not-PASS: if a fibre family failed to hold the nuisance argument fixed,
  VAR-F would pass everything. **Guarded:** the producer asserts and prints, per
  fibre family and per lattice, that `abs(det B_i)` is **bit-identical across all
  8 bases** (F0|fib: `q^(d-k)`; F1|fib: `(q+3) q^(d-k-1)`). If that assertion
  fails anywhere the run is an instrument failure and claims nothing.

### 6.5 AM-16(f)

Not applicable: this batch estimates no standard error and applies no variance
decomposition. Declared N/A with its reason rather than omitted.

---

## 7. THE TERMINATION CLAUSE — THREE BRANCHES, FROZEN BEFORE THE RUN

Exactly one of T-PASS, T-F1FAIL, T-F0FAIL fires, determined by the F0 and F1
fixture verdicts of section 4 and gated by section 6.1's VOID row. Section 7.4 is
the infrastructure branch and is **not** a fourth science branch.

**Precedence, frozen:** R2-OUT-V (VOID) dominates everything. F0's verdict is
evaluated before F1's. If F0 fails, T-F0FAIL fires **whatever F1 does**.

### 7.1 T-PASS — G-VAR2 passes BOTH F0 and F1

**FIRES WHEN:** F0 PASSES at full coverage and F1 PASSES at all 38 cells for all
declared routes, and the guard crossed.

**LICENSES:** the gate is usable and **C3 proceeds behind a validated
instrument**. A successor batch may score candidate observables through G-VAR2
and report admissibility verdicts, each scoped to the declared families, the
declared routes and the declared argument sets, and each carrying its per-cell
profile.

**FORBIDS:**
* any claim that G-VAR2 is validated beyond the two fixtures, the two families,
  the declared routes and the declared argument sets;
* any transport of any number here to ML-KEM parameters, to beta = 606, to
  d = 1420, or to any FIPS 203 parameter set, by extrapolation, analogy or any
  other route;
* any retro-validation of BATCH-9e3584's or BATCH-cbe023's verdicts — a validated
  instrument does not revalidate results scored under its predecessor;
* any statement that the gate's **REFUSAL SIDE** is now tested. C-2(b) stands:
  the refusal side is untested and its false-refusal rate is unmeasured. Rider
  (ii) bears on that and the fixtures do not;
* closing, pausing or completing GOAL-MLKEM-005.

### 7.2 T-F1FAIL — passes F0, fails F1

**FIRES WHEN:** F0 PASSES and F1 FAILS at one or more cells or routes.

**MEANS:** the scaled operationalization is confirmed **FAMILY-CONDITIONAL**.

**LICENSES:** **THE ADMISSIBILITY-GATE LANE CLOSES**, with its named obstruction
stated exactly: *a dispersion criterion cannot separate "reads the instance" from
"reads a nuisance parameter" without a fibre condition.* The goal proceeds
**DIRECTLY TO C3**, with every candidate declared **PRESENTATION-DEPENDENT** and
every C3 verdict scoped accordingly — rather than a **SEVENTH** consecutive gate
repair. The closure records, as docs/inventor-protocol.md section 4 and CLAUDE.md
rule 9 require: its evidence, its budget, its test boundary, its remaining
uncertainty, and a concrete successor or revisit condition.

**FORBIDS:**
* a seventh consecutive gate repair;
* **closing, pausing or completing GOAL-MLKEM-005.** Closing the
  admissibility-gate LANE retires the **LANE**, never the goal. A lane closure
  with a named obstruction is listed in this goal's `non_terminal_conditions` and
  may not be cited in a decision that closes, pauses or completes it;
* any claim that the gate is "broken in general". It is broken **between F0 and
  F1**, which is two families, one probe, one run;
* any claim about ML-KEM, any parameter set, any attack cost or any cost model.

### 7.3 T-F0FAIL — fails F0

**FIRES WHEN:** F0 FAILS at one or more covered cells or routes — whatever F1
does.

**MEANS:** **AM-16(a) itself needs replacing, and that is reported as such.**

**LICENSES:** a decision recording that the AM-16(a) operationalization does not
reproduce its own declared target behaviour on the fixture it was written
against. Specifying a replacement is a Coordinator act in the successor decision,
not a producer act here.

**FORBIDS:**
* proceeding to C3 behind G-VAR2;
* treating the F1 result as informative. If the instrument fails at its own
  reference point, its behaviour elsewhere is uninterpretable;
* presenting an F0 failure as evidence about any lattice, any observable's
  admissibility, or any proposition in this goal. It is an instrument outcome;
* reading a failure **caused by a missing dependency, a timeout or a crash** as
  an F0 failure at all. That is INFRASTRUCTURE SIGNAL (AGENTS.md rule 5) and
  forces section 7.4 instead;
* closing, pausing or completing GOAL-MLKEM-005.

### 7.4 T-PARTIAL — the infrastructure branch, declared so it cannot be narrated into a science branch

**FIRES WHEN:** any declared cell, route or candidate is **uncovered** —
fpylll absent, a timeout, a crash, or the declared d <= 40 reduction bound.

**RULE:** the **determinant-only half of F0** (the six routes to `X_null` and to
`rdet`) requires **no reduction at all** and is fully scorable on any host; its
verdict is binding regardless. The `lam1n` / `hkz` / `rawtail` ADMITTED half is
reported at its **actual coverage**, cell by cell and route by route.

**CONSEQUENCE:** the branch that fires is reported with the suffix `-PARTIAL`
(`T-PASS-PARTIAL`, `T-F1FAIL-PARTIAL`). **T-PASS-PARTIAL does NOT license C3 to
proceed behind the instrument**: a partially validated instrument is not a
validated one, and the missing coverage becomes the next action. T-F1FAIL is
unaffected by partial coverage of the ADMITTED half, because F1's target
behaviour names only `X_null` and `rdet`, both reduction-free.

**A missing dependency is never a negative mathematical result, and no branch of
section 7 may be reached through one.**

---

## 8. THE THREE RIDERS — PRE-REGISTERED, BEHIND THE LEAD, STRUCTURALLY GATED

All three `depends_on` the lead's snapshot archive TASK-20260812-b581a8 so they
**cannot displace the lead**. None of them may be reported before the lead's own
outcome rows.

### 8.1 Rider (i) — the C-1 resolving tabulation (TASK-20260812-78a6e3)

Tabulate the **19 G-REL2** and **10 G-REL1** `X_null` criterion values out of the
committed `results_relvar.json` under **ALL THREE** declared readings — legacy
`i = 0`, count of passing bases, mean over 8 — and publish the **multiset with
the reading beside each**, plus per reading: the min, the max, the ratio of each
value to `tau_rel = 0.10`, and the count of entries below 6x.

**P-C1:** at least one declared reading reproduces exactly one of the two
conflicting counts — wave 1's "15 of the 19 G-REL2 cells below 6x" or wave 2's
"two of 29 entries below 6x". **FALSIFIER:** no reading reproduces either.

**BINDING:** until the Coordinator rules on this tabulation in the batch
decision, **NEITHER COUNT IS CITABLE**. The corrected range **4.87x to 31.03x**
is agreed, two-wave replicated and binding, and is unaffected. "A factor of 6 to
31" is FALSE and is not citable anywhere. The rider resolves a **citation
block**; it does not declare either validator wrong beyond what the numbers show.

Seconds of Python on a committed file, pinned by sha256. No reduction, no fpylll,
no basis rebuild. `results_relvar.json` is immutable and is **not edited**.

### 8.2 Rider (ii) — the false-refusal control (TASK-20260812-4b8ede)

`X_gso_k(B) = (1/k) * sum_{j=1..k} log norm(b*_j)` over the **RAW** basis, in the
frozen row order, through routes RQ and RG (section 2.5).

* **Informative by construction:** it reads the leading k Gram-Schmidt norms,
  which depend on the entries of A.
* **Structurally refused:** it takes **no beta argument**, so at fixed (d,k) it
  is constant across the beta grid and `rho = 0` exactly at G-REL1 — it fails
  REL-1 **by algebra**, exactly as `rdet` and `lam1n` do.

**P-FR1:** `X_gso_k` is REFUSED by G-REL1 and ADMITTED by G-VAR2 (scale_degenerate
on VAR-S, PASS on VAR-F). **FALSIFIER:** either half failing.

**WHAT IT ESTABLISHES AND WHAT IT DOES NOT, frozen in advance:** it is **ONE
CONSTRUCTED INSTANCE**, n = 1. It narrows C-2(b) from "the refusal side is
untested in either direction" to "the refusal side has one constructed instance
of a false refusal". **IT DOES NOT MEASURE A FALSE-REFUSAL RATE** and no rate may
be reported, estimated or implied from it.

Minutes of numpy, one QR and one Cholesky per basis, no reduction, all 10
lattices.

### 8.3 Rider (iii) — the fpylll-equipped L7/L8 replication (TASK-20260812-0e930c)

Install fpylll pinned at **0.6.4** and re-measure the **L7/L8 arm**: the 8 frozen
bases at d = 20, the frozen beta grid {5, 10, 15}, HKZ through the frozen
pipeline, reproducing the committed per-basis `hkz` and `lam1n` values of
`results_relvar.json` and reporting the max absolute deviation.

**P-L1:** the re-measurement reproduces the committed values to 6 decimals.
**FALSIFIER:** max absolute deviation above 1e-6.

**MANDATORY FRAMING, FROZEN:** this **RESTORES THE COVERAGE WAVE 2 LOST** and is
**NEVER** to be presented as resolving a doubt, there being none to resolve.
fpylll's absence in both wave-2 sessions is **INFRASTRUCTURE SIGNAL** and was
never evidence against `lam1n`, `hkz`, the 48 reductions or their reported max
violation of 0.0. AM-9 is in force: **fpylll's k counts the q-scaled rows, NOT
the identity block.**

**If the install fails:** INFRASTRUCTURE SIGNAL. Report it, emit the artifacts
declaring the failure, claim nothing, and do not report a deviation that was
never measured.

---

## 9. PREDICTION REGISTER (AM-15(a) and AM-15(c))

**All eight items below were OPEN at the moment of notarization. None of them had
been evaluated by anyone when this text was frozen.**

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-F0 | G-VAR2 refuses all six routes to `X_null` and all six to `rdet` on F0, and admits `lam1n`/`hkz`/`rawtail` on F0, at every covered cell | any listed refusal that is an admission, or any listed admission that is a refusal, at any covered cell | PREDICTION | OPEN |
| P-F1 | G-VAR2 refuses `X_null` and `rdet` on F1 at all 38 cells, all routes | any admission at any cell or route | PREDICTION | OPEN |
| P-FR1 | `X_gso_k` is refused by G-REL1 and admitted by G-VAR2 | either half failing | PREDICTION (n = 1 instance) | OPEN |
| P-C1 | some declared reading reproduces exactly one of the two conflicting sub-6x counts | no reading reproduces either | PREDICTION | OPEN |
| P-L1 | the fpylll re-measurement reproduces committed L7/L8 `hkz` and `lam1n` to 6 dp | max abs deviation above 1e-6 | PREDICTION | OPEN |
| P-G1 | the graded guard crosses within the lambda grid at a majority of cells | no crossing anywhere | MUST-PASS GUARD | OPEN |
| P-V1 | VAR-S alone refuses `V_evade` at every scored F0 cell | VAR-S admits it at any cell | CONSISTENCY CHECK (AM-15(a)) | OPEN |
| P-R26 | definitional `X_null` reproduces the notarized prereg 2.6 table at 38/38 to 6 dp | any cell disagreeing | CONSISTENCY CHECK (AM-15(a)) | OPEN |

**Empirical content of this batch: FIVE predictions** (P-F0, P-F1, P-FR1, P-C1,
P-L1). **TWO consistency checks** (P-V1, P-R26) — reported, valuable, and **not**
counted. **ONE must-pass guard** (P-G1). A count of predictions is a function of
the governing amendment set, not of the artifacts alone (C-5); this register is
that function, evaluated here and frozen.

---

## 10. OUTCOME ROWS

| row | what it records |
|---|---|
| R2-OUT-1 | the F0 fixture verdict — PASS / FAIL / PARTIAL — with the full per-cell profile and per-route coverage |
| R2-OUT-2 | the F1 fixture verdict — PASS / FAIL — with the full per-cell profile |
| R2-OUT-3 | P-V1: VAR-S on `V_evade` — HOLDS / FALSIFIED, labelled a consistency check |
| R2-OUT-4 | the graded guard's crossing-amplitude profile, per cell |
| R2-OUT-5 | the scale-degenerate disclosure: how many cells, per candidate, with the naive reading's verdict beside the frozen reading's |
| R2-OUT-V | **VOID**: the guard did not cross anywhere in the grid, so every G-VAR2 verdict in this batch is void |
| R2-OUT-6 | rider (i): the three-reading multiset and the C-1 adjudication input |
| R2-OUT-7 | rider (ii): P-FR1, one constructed false-refusal instance, n = 1 |
| R2-OUT-8 | rider (iii): the L7/L8 replication, or the declared infrastructure outcome |

The termination branch of section 7 is read off R2-OUT-1 and R2-OUT-2 under
R2-OUT-V's precedence, and **nowhere else**.

---

## 11. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

* **AM-10 through AM-14** of DEC-20260808-05b684 and their binding carries.
* **AM-15 and AM-16** of DEC-20260809-afe29b, AM-16 as extended by AM-17,
  including that AM-13's consistency-check clause binds **every** section and
  that a non-citation carry binds **at the point of QUOTATION**, never at the
  point of occurrence.
* **AM-17** of DEC-20260812-7c4a1e.
* **AM-3 IS NOT RETIRED.** Its power remains undemonstrated rather than disproved
  and its 0.096 family-wise false-failure bound stands.
* **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT** and its Section C verdict and
  detection floors remain **VOID IN BOTH DIRECTIONS**.
* **AM4-OBS-1 is cited ONLY through `knowledge/findings/KN-FIND-f38a89.md`.**
* **AM-9:** fpylll's k counts the q-scaled rows, **NOT** the identity block.
* **THE G-VAR REFUSAL IS CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY F0.**
* The **split-producer notarization pattern** is retained unchanged.
* The **receipt-with-`commit_sha: null`-inside-its-own-commit** archive pattern is
  **MANDATORY**.
* Every run emits durable `command.txt`, `stdout.log` and `stderr.log`, with **no
  path inside a folded YAML scalar**.
* `knowledge/INDEX.md` must **NOT** be written, regenerated or staged: it is
  generated and `.gitignore`d.
* **CLAIM TIER STAYS TOY.**

### 11.1 NOT CITABLE ANYWHERE IN THIS BATCH

* "a factor of 6 to 31" — **the citable range is 4.87x to 31.03x**;
* "no admissibility claim is reportable in either direction" — replaced by the
  three-part decomposition of DEC-20260812-7c4a1e C-2: (a) the gate's PASS side
  is uninformative **on the frozen family F0**; (b) the gate's REFUSAL side is
  untested and its false-refusal rate unmeasured; (c) no admissibility claim
  about any candidate is made by either wave;
* the **"genuinely cross-platform"** reading of the L7/L8 agreement — the citable
  form is a **PORTABILITY** result across three textually distinct
  implementations with fpylll pinned at 0.6.4;
* **both sub-6x counts**, pending rider (i);
* "the null fires more often than the real arm" **as a general statement**
  (2 of 8 wave-2 replicates fire less often than the committed real count of
  29 of 48, against the exact-null benchmark of 47 of 48);
* "G-VAR cannot be tuned into or out of firing" — **FALSE**;
* "three predictions of actual empirical content" — the official count for
  BATCH-9e3584 Section R remains **ONE**;
* the blanket "Residuals are 0 identically" — cite **per transform**: 0.0 for
  `X_null` under all transforms and for `rdet` under T2 and T3; **3.865e-12** for
  `rdet` under T1;
* "the obstruction is relocated";
* "CONSISTENT", in either direction;
* **"29 of 48" without the exact-null benchmark of 47 of 48 in the same
  sentence**;
* the 3.91% floor without its **NEGATIVE-VARIANCE-COMPONENT** qualifier; the
  non-degenerate figure is **10.83%**.

---

## 12. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** q = 3329; d in {20, 30, 40, 100, 140}; the frozen k and beta grids;
8 bases per lattice per family; four declared families; six declared arithmetic
routes for determinant-only candidates and two for every other; no reduction
beyond the frozen HKZ pipeline and none above d = 40. **Every conclusion is
scoped to exactly that and transports nowhere.**

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** AGENTS.md **rule 12 is
UNMET AND UNWAIVED** in this goal and is not waived here. Two review waves over
BATCH-9e3584 were two independent sessions on **one model**, not two models, and
they do not touch rule 12. Every producer and reviewer of this batch records
`model_verified: false` with its reason. Two knowledge promotions remain owed
from GOAL-MLKEM-003 and cannot be executed without a second backend.

**PD-4 IS OPEN.** Review artifacts, and in this batch the three riders' artifacts,
sit uncommitted across a dispatch window. The named fix is unchanged: a
`tools/research_dispatch.py` change verifying an already-committed source by hash.

**WHAT THIS BATCH CANNOT DO, stated so no reader has to infer it.** It cannot say
anything about ML-KEM, about any FIPS 203 parameter set, about any attack cost or
about any cost model. It cannot measure a false-refusal **rate**. It cannot
establish that any observable carries lattice information. It cannot revalidate
BATCH-9e3584 or BATCH-cbe023. It cannot close, pause or complete GOAL-MLKEM-005.

---

## 13. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no git
command, no probe, no `allocate_id`, and computed no hash. Every number quoted
here is **attributed** to the review, decision or committed artifact that
measured it, and none is claimed as this session's own measurement. In
particular: 3.91e-10, 1.20e-13, 5.44e-14, 0.023888, 4.87x, 31.03x, 0.486626,
3.865e-12, 29 of 48, 47 of 48 and 38 of 38 are all carried, not measured here.

`prereg_sha256.txt` is therefore **generated and committed by TASK-20260812-1ed548**,
by a session that has a shell, and is that task's own declared artifact. It is
**not** invented here.

**END OF FROZEN TEXT.**
