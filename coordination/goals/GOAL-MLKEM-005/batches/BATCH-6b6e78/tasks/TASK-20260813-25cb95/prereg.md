# PREREG-2 — BATCH-6b6e78 FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-6b6e78
    task        TASK-20260813-25cb95 (Coordinator, pre-registration only)
    notarized by TASK-20260813-502381 (snapshot archive, runs alone, before any
                measuring task)
    authority   DEC-20260812-781961 (AM-18), applying AM-17 of DEC-20260812-7c4a1e,
                AM-15/AM-16 of DEC-20260809-afe29b and AM-10..AM-14 of
                DEC-20260808-05b684
    claim tier  TOY, UNCONDITIONALLY

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is a
superseding record under a new identifier, never an edit here. No measuring task
of BATCH-6b6e78 may be dispatched until this file is committed by
TASK-20260813-502381 and that commit contains **zero** producer artifacts. That
is the split-producer notarization pattern, retained unchanged; it has now worked
five times and has been verified in both directions by independent sessions each
time.

---

## 0. WHY §1 COMES FIRST, AND WHY IT IS NOT CEREMONY

`AM-18(a)` is a **stopping condition, not a repair**: no further dispersion
criterion may be specified in this goal until "non-constant on the fibre" is a
**numbered assumption with an explicit falsification condition at finite
precision**. The assumption in force until now — *non-constant on the fibre in
IEEE-754 float64 ≡ non-constant on the fibre* — has never been numbered and is
**measured false** at 38 of 38 cells for `rdet` under three of six declared
routes (attributed to `DEC-20260812-781961`, the `BATCH-4ed139` lead's own
`R2-OUT-5`, and both `BATCH-4ed139` reviews independently).

If the assumption is written **after** a replacement clause is chosen, it will be
written to fit the clause, and this batch will have reproduced the exact failure
`AM-18(a)` exists to stop. So §1 is the numbered assumption, it comes before
every other substantive section of this document, and:

> **THIS PRE-REGISTRATION SPECIFIES NO REPLACEMENT DISPERSION CRITERION, NO
> REPLACEMENT FIBRE CLAUSE, NO GATE AND NO THRESHOLD, ANYWHERE IN ITS TEXT.**
> §3 specifies a **DIAGNOSTIC MEASUREMENT** whose only job is to score the
> falsifiers of §1. The one place an `ADMIT`/`REFUSE` verdict appears at all is
> §4, which **re-executes the already-frozen, already-adjudicated `G-VAR2` code
> path of `BATCH-4ed139`** under an added route — a re-execution of a frozen
> criterion, not the specification of a new one.

Equally binding in the other direction: nothing in §7 may be re-read, re-weighted
or "clarified" after the run. A branch that turns out inconvenient is still the
branch that fired. And §7.5 supplies the bar that `PREREG-1` 7.3's FORBIDS list
lacked (Red Team `O-3`): **premature closure and unbounded repair are the same
failure mode in two directions**, and this document bars both by name.

**THIS IS THE SEVENTH CONSECUTIVE INSTRUMENT BATCH OF THIS GOAL** (six as of
`BATCH-4ed139`, attributed to `DEC-20260812-781961`), and `C3` — the goal's
actual science criterion — has still not been entered. That cost is real, it is
recorded here rather than in a later apology, and it is paid because `AM-8` makes
the gate binding over every candidate observable in this goal.

---

## 1. A-1 — THE NUMBERED ASSUMPTION, AND ITS FALSIFICATION CONDITION

### 1.0 The three objects §1 needs, and nothing more

Only three definitions are required before the assumption can be stated. None of
them is a criterion: none maps to a verdict and none carries a threshold.

* **Fibre family of a candidate `X`, written `fib(X)`.** A family of `N_BASES`
  bases indexed by `i` that holds **every** declared nuisance argument of `X`
  fixed across `i` while the free content of `A` varies. It is **per candidate**,
  built from that candidate's **own** declared nuisance set (§2.4). This is
  `AM-18(c)` and it is the point of obligation (d).
* **Relative fibre dispersion.** For candidate `X`, route `r`, working precision
  `p`, cell `c`:

      x_i        = X^{r,p}(B_i, beta),  i = 0..N_BASES-1,  B_i in fib(X)
      s_c        = sd over i, ddof = 1
      m_c        = mean over i
      rho(X,r,p,c) = s_c / |m_c|          (undefined and reported as such if m_c == 0)

  `rho` is a **statistic**. It has no threshold, decides nothing, and is not a
  criterion.
* **Exact route.** A declared route that evaluates `X` on `fib(X)` in **exact
  arithmetic** — integer, rational, or fixed-point to a certified error bound
  strictly below the smallest fibre difference it must resolve — and terminates
  within a declared time cap.

### 1.1 A-1 — STATEMENT

> **A-1 (THE FINITE-PRECISION FIBRE ASSUMPTION).**
>
> **"`X` is non-constant on the fibre" MEANS: `X` is non-constant on `fib(X)` in
> EXACT ARITHMETIC.** Evaluation at a finite working precision is an
> **ESTIMATOR** of that property and is **never its definition**.
>
> **A-1 is the assumption that this estimator is USABLE**, and it has exactly
> three components. Each is stated over the **in-scope declared candidates of
> §2.4** and over the **declared routes and precisions of §2.5–2.6**, and each
> carries its own falsifier.
>
> **A-1.1 (DECIDABILITY).** For **every** in-scope declared candidate there is a
> declared **exact route** on `fib(X)` that terminates within the declared cap,
> so that "exactly constant on the fibre" is **DECIDABLE** for it and not merely
> definable.
>
> **A-1.2 (CONSISTENCY / DIRECTION).** For every candidate that A-1.1 **certifies
> exactly constant** on its own fibre, the finite-precision relative fibre
> dispersion is strictly decreasing in the working precision and vanishes in the
> limit: `rho(X,r,binary32,c) > rho(X,r,binary64,c)` at every covered cell and
> route, and `rho` under the exact route is exactly `0`.
>
> **A-1.3 (INVARIANCE).** For every candidate that A-1.1 **certifies exactly
> non-constant** on its own fibre, `rho` is invariant under a change of working
> precision within a declared factor of **2**:
> `1/2 <= rho(X,r,binary32,c) / rho(X,r,binary64,c) <= 2` at every covered cell
> and route, and `rho(X,r,p,c) > 0` at both declared precisions.

### 1.2 FALSIFICATION CONDITION — explicit, and each part independently sufficient

**A-1 IS FALSIFIED if any one of the following is measured at any covered cell,
route or candidate.** Every one of them is a **direction, an existence or an
order comparison**. Only `FC-3a` carries a numeric constant, and §1.4 states that
constant's basis and its honest consequence.

    FC-1   (A-1.1)  No declared exact route exists, is defined, or terminates
                    within the declared cap for some in-scope declared candidate.
                    Reported PER CANDIDATE CLASS. If it fires for SOME but not
                    ALL classes, A-1.1 is false as stated and T-A1-FALSIFIED
                    fires with the scope named. If it fires for EVERY class, §7.2
                    applies instead.

    FC-2a  (A-1.2)  Some candidate certified exactly constant has
                    rho(binary32) <= rho(binary64) at a covered cell and route
                    that is NOT `precision_degenerate` under §1.3.
                    DIRECTION ONLY. NO THRESHOLD.

    FC-2b  (A-1.2)  Some candidate certified exactly constant has rho > 0 under
                    the EXACT route. EXISTENCE ONLY. NO THRESHOLD.

    FC-3a  (A-1.3)  Some candidate certified exactly NON-constant has
                    rho(binary32) / rho(binary64) outside [1/2, 2] at a covered
                    cell and route.

    FC-3b  (A-1.3)  Some candidate certified exactly NON-constant has rho == 0
                    exactly at either declared precision at a covered cell and
                    route — the float evaluation has destroyed real fibre
                    content. EXISTENCE ONLY. NO THRESHOLD.

**A-1 HOLDS in this batch iff none of `FC-1`, `FC-2a`, `FC-2b`, `FC-3a`, `FC-3b`
fires at full declared coverage.** "Holds" means **survived its first test at
this scale** and never "is true": see §7.4's FORBIDS list.

### 1.3 THE `precision_degenerate` RULE — a specification hole, frozen here with both readings named

Found by writing this pre-registration and recorded as such rather than repaired
silently, exactly as `PREREG-1` 3.2 did for the degenerate-scale hole.

`A-1.2` asks for a **strict** decrease of `rho` with precision. At a cell where
`rho(binary64) == 0` **exactly** — which is the measured behaviour of `rdet`
through `R1` and, by construction, of every route that never touches the matrix
(`R0`) — the strict inequality is either vacuous or trivially satisfied depending
on how `rho(binary32)` lands. Two readings are available and they disagree:

* **strict reading:** `rho(binary32) > 0 == rho(binary64)` satisfies `A-1.2`;
  `rho(binary32) == rho(binary64) == 0` **falsifies** it, because nothing
  decreased.
* **frozen reading (BINDING):** a cell with `rho(binary64) == 0` exactly is
  `precision_degenerate`. It is **EXEMPT** from `FC-2a` — not a falsification and
  not a confirmation — and it is reported as such. `FC-2b` still binds there.

The frozen reading is binding. **The producer must additionally report the strict
reading's verdict beside it at every `precision_degenerate` cell** (outcome row
`R3-OUT-7`), so the choice is auditable and a successor can re-decide it against
the numbers rather than against this paragraph. Which cells are
`precision_degenerate` is otherwise a **measured** outcome and is asserted here
only for `R0`, whose independence from the matrix is definitional.

### 1.4 THE ONE CONSTANT IN THE FALSIFIER, ITS BASIS AND ITS HONEST CONSEQUENCE

`FC-3a`'s window `[1/2, 2]` is the only calibrated quantity in §1, and its basis
is stated plainly because it matters.

It is a **coarse, round constant chosen to sit far from both classes in both
directions** on the already-committed numbers, which are **carried and
attributed, never measured here**: the `BATCH-4ed139` Red Team's
`probe_precision_null` reports a `binary32/binary64` relative-dispersion ratio of
`0.9999991` to `1.0000001` for the real object `X_gso_k`, and `1.4e6` to `5.9e8`
(median `5.5e7`) for the null object `rdet`, against `eps32/eps64 = 5.369e8`. The
factor `2` therefore sits roughly **six orders from one class and six orders from
the other**, and **no value between `1.000001` and `7e5` would change any
archived verdict.** It is not fitted to a boundary.

**THE HONEST CONSEQUENCE, DECLARED IN ADVANCE.** Because both classes' archived
ratios are already known, `A-1.3` is a **WEAK** test of the constant and a
**STRONG** test of the **CLASSIFICATION** — of whether `A-1.1`'s exact route
assigns candidates to the classes whose ratios then confirm them, and of whether
the assignment survives on candidates whose ratios are **not** archived
(`X_hash`, `X_parfree`, `V_evade`, `X_lambda`). This is the same discipline
`PREREG-1` 3.4 applied to `tau_var`, and it is stated for the same reason.

### 1.5 WHAT A-1 REPLACES, AND WHAT IT IS NOT

**What it replaces.** The unnumbered assumption *non-constant in IEEE-754 float64
≡ non-constant*, measured false. A-1 differs in **one structural respect**: the
float evaluation is demoted from **definition** to **estimator**, and the
definition is moved onto a route whose very existence is itself an assumption
(`A-1.1`) with its own falsifier. An assumption that cannot fail where it is
weakest is not an improvement on an unnumbered one.

**What it is not.** A-1 is **not** a criterion, **not** a gate, **not** a
threshold, **not** a repair and **not** a claim about any lattice. It does not
say that a precision-invariant observable carries lattice information — §5's
`P-HASH` exists precisely to measure how false that reading would be. It closes
nothing and forbids no direction of inquiry.

**`AM-18(a)` after this batch.** If A-1 survives, a successor **may** build a
replacement clause on it — subject in full to §7.5's repair bar, and carrying
A-1's scope with it. If A-1 is falsified, the successor's first act is a
**successor assumption**, not a criterion. Either way `AM-18(a)`'s stopping
condition is discharged **by numbering an assumption and exposing it to a
falsifier**, and never by asserting one.

---

## 2. FROZEN OBJECTS

### 2.1 Constants

    q          = 3329
    N_BASES    = 8            (basis index i = 0..7)
    tau_var    = 1e-3         (carried unchanged from PREREG-1 2.1; used ONLY
                               inside the re-executed BATCH-4ed139 code path of
                               §4, never as a criterion of this batch)
    W          = 2            (the FC-3a window factor; basis in §1.4)
    K_grid     = the K-interval computation of §3.5 is SOLVED, not gridded

### 2.2 Lattices and grids (carried verbatim from PREREG-1 2.2)

    L1 (100,30)  L2 (100,70)  L4 (140,40)  L5 (140,100)
    L7 (20,6)    L8 (20,14)   L9 (30,9)    L10 (30,21)
    L11 (40,12)  L12 (40,28)

    beta grid   d=100: 15,30,35,50,65    d=140: 20,40,45,70,95
                d=20 : 5,10,15           d=30 : 7,15,22    d=40: 10,20,30

38 scored cells per family (10 lattices x their beta grids).

### 2.3 Families and fibre families

    F0  (frozen, carried)   B_i = [[I_k, A_i], [0, q I_{d-k}]]
                            A_i = default_rng([1,d,k,i]).integers(0,q,size=(k,d-k))
                            |det B_i| = q^(d-k), CONSTANT in i BY CONSTRUCTION

    fib_s2  base fibre draw  A'_i = default_rng([2,d,k,i]).integers(0,q,size=(k,d-k)),
                             modulus block q I_{d-k} held fixed across i
    fib_s3, fib_s4           the same at seed prefixes 3 and 4 (AM-10 replication)

**THE FIBRE FAMILY IS PER CANDIDATE (`AM-18(c)`, obligation (d)).** `fib_s2`,
`fib_s3` and `fib_s4` are **draws**, not fibre families. A candidate's fibre
family is obtained from a draw by **pinning every declared nuisance argument of
that candidate across `i`**, per §2.4. Two pinnings are used and both are frozen:

    PIN-DET     |det B_i| is bit-identical across i.  Satisfied by every draw
                above by construction (modulus block fixed): |det B_i| = q^(d-k).
    PIN-A00     A'_i[0,0] is additionally set to A'_0[0,0] for every i, leaving
                every other entry of A' untouched and |det B_i| untouched.
                Construction carried from the BATCH-4ed139 Red Team's
                probes/probe_argset.py section Q2 (family `F0|fib_dec`), which
                BUILT AND RAN it; it is declared here as the fibre family of every
                candidate whose declared nuisance set contains A[0,0].

`F1` is **NOT USED IN THIS BATCH**. `PREREG-1` 7.3's FORBIDS list suspends the
interpretive weight of the `F1` result and `DEC-20260812-781961` adopts that
unamended; re-scoring it here would be reading a suspended number. Its absence is
a **declared scope limit**, not a result.

### 2.4 In-scope candidates, DECLARED ARGUMENT SETS, and their per-candidate fibre

Introducing or re-declaring a candidate observable is a **Coordinator act** and it
is done here, before any measurement. A producer may not change a declared
argument set; a reviewer who believes one is dishonest reports that as a finding
rather than silently rescoring.

| candidate | definition | declared arguments | nuisance held fixed on ITS OWN fibre | fibre family | expected exact class |
|---|---|---|---|---|---|
| `X_null` | `(beta/d)(1/d) log abs(det B)` | d, k, beta, q, abs(det B) | abs(det B) | PIN-DET | CONSTANT |
| `rdet` | `exp(log abs(det B) / d)` | d, abs(det B) | abs(det B) | PIN-DET | CONSTANT |
| `X_parfree` | `log abs(det B) / (d*k)` | d, k, abs(det B) | abs(det B) | PIN-DET | CONSTANT |
| `V_evade` | `X_null + 1e-9 * A[0,0]/q` | d, k, beta, q, abs(det B), A[0,0] | abs(det B), **A[0,0]** | PIN-DET + PIN-A00 | CONSTANT |
| `X_lambda` | `X_null + lambda * A[0,0]/q`, lambda over the §2.7 grid | d, k, beta, q, abs(det B), A[0,0], lambda | abs(det B), **A[0,0]** | PIN-DET + PIN-A00 | CONSTANT |
| `X_gso_k` | `(1/k) * sum_{j=1..k} log norm(b*_j)` of the RAW basis | d, k, q, raw GSO profile | abs(det B) | PIN-DET | NON-CONSTANT |
| `X_hash` | `X_null + c * H(B)`, `H` per §2.8, `c` over the §2.7 amplitude grid | d, k, beta, q, abs(det B), **every entry of A** | abs(det B) | PIN-DET | NON-CONSTANT |

`X_parfree` is introduced **here, by the Coordinator**, and it is the
`BATCH-4ed139` Validator's blind null `N2` (its `CC-6`), which no producer scored
and which reproduces the `rdet` admission exactly. The Validator correctly did not
add it to the candidate list; that act belongs to this record and the credit
belongs there.

`X_hash` is introduced **here, by the Coordinator**, and is the `BATCH-4ed139` Red
Team's `RC-6` / `probe_argset.py` section Q3 construction, declared as a candidate.

**"Expected exact class" IS AN EXPECTATION AND NEVER A FINDING.** The class of
every candidate is **CERTIFIED BY THE EXACT ROUTE AT RUN TIME** (`A-1.1`,
`R3-OUT-1`). If a certification contradicts the expectation in this table, **the
CERTIFICATION BINDS**, the disagreement is reported as a finding of this batch,
and the falsifiers of §1.2 are evaluated against the certified class and never
against this column.

Note, stated in advance because it is the whole content of obligation (d): on its
**own** fibre `V_evade` and `X_lambda` are expected **constant**, because both
their declared nuisance arguments are pinned there. Under `BATCH-4ed139`'s
candidate-**independent** fibre they were not, which is Validator `F-2` and Red
Team `O-1`, and it flipped `X_lambda`'s full `G-VAR2` verdict at 38 of 38 cells
for `lambda` in `{1e-1, 1}` and at 22 of 38 for `lambda = 1e-2` under all six
routes (attributed, and **post-hoc there, pre-registered here**).

### 2.5 OUT OF SCOPE, DECLARED BEFORE THE RUN WITH ITS REASON

`lam1n`, `hkz` and `rawtail` are **OUT OF SCOPE for A-1 in this batch** and no
`A-1` verdict is reported for them in either direction. The reason is declared
now rather than discovered later: this batch permits **no new reduction of any
kind and nothing reduction-dependent above d = 40**, their committed values
(route `RC`) exist at one working precision only, and a two-precision evaluation
of them would require re-running the reduction. **THE CONSEQUENCE IS A REAL LIMIT
ON WHAT THIS BATCH CAN CONCLUDE AND IS STATED AS ONE:** `A-1`'s scope excludes
every reduction-dependent observable in this goal, so a successor may not cite
`A-1` — held or falsified — about them. Their exclusion is a scope limit and is
**never** an `FC-1` firing.

### 2.6 Declared routes and declared working precisions

For `X_null`, `rdet`, `X_parfree`, `V_evade`, `X_lambda`, `X_hash` — the six
routes of the committed `probe_nullroute.py`, carried verbatim through the
committed `measure_gvar2.py`, with the route recorded beside every value:

    R0  closed form            (d-k)*log q          (never touches the matrix)
    R1  slogdet(B)
    R2  QR of B^T              sum_j log abs(R_jj)
    R3  slogdet(U B)           U a fixed unimodular re-presentation, seed [424242,d]
    R4  0.5 * slogdet(B B^T)
    R5  slogdet(B H)           H a fixed ambient isometry, seed [313131,d]

    R6_exact   log abs(det B) from the EXACT INTEGER determinant through
               `decimal` at 60 significant digits.  THE EXACT ROUTE for every
               determinant-only candidate.  ALREADY BUILT, ALREADY RUN AND
               ARCHIVED at
               coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/
               TASK-20260812-696cd4/probes/probe_precision_null.py, cost 0.4 s
               (attributed to that report).

For `X_gso_k`:

    RQ  QR of B^T,                     log abs(R_jj), j = 1..k     (carried)
    RG  Cholesky of the Gram B B^T,    log of the diagonal, j = 1..k (carried)
    R7_exact_gram   THE EXACT ROUTE, derived in §2.9.

**Declared working precisions: `binary32` and `binary64`** (numpy `float32`,
`float64`). `float32` is a **knob used to move machine epsilon and nothing else**;
it is not a claim about any deployment, and that framing is carried verbatim from
the archived probe. `R6_exact` and `R7_exact_gram` are **precision-free** and are
not working precisions.

### 2.7 Frozen grids for the two parameterised candidates

    lambda in {0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1}   (X_lambda; carried from PREREG-1 6.1)
    c      in {1e-9, 1e-3, 1e-2, 1e-1}                                    (X_hash; carried from Red Team RC-6)

### 2.8 `H(B)` — frozen so it is reproducible to the bit

    H(B) = int(sha256(payload).hexdigest(), 16) / 2**256   in [0, 1)
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))

`B` is the **exact integer** basis matrix. `H` reads **every entry of `A`** and
carries **no lattice information whatever**; that is the entire point of the
object and it is `AM-18(e)`'s null-object calibration.

### 2.9 `R7_exact_gram` — the exact route for `X_gso_k`, DERIVED HERE

**This derivation is the Coordinator's own, is elementary, and is stated so it can
be checked rather than believed.** For the raw basis rows `b_1..b_k` with
Gram–Schmidt vectors `b*_j`,

    prod_{j=1..k} norm(b*_j)^2 = det Gram(b_1..b_k) = det G_k

so

    X_gso_k = (1/k) * sum_{j=1..k} log norm(b*_j) = (1/(2k)) * log det G_k .

For the frozen families, row `i <= k` of `B` is `[e_i | A_i]`, hence

    G_k = I_k + A A^T ,

an **integer** matrix. `det G_k` is therefore an exact integer, and

    R7_exact_gram :  X_gso_k = (1/(2k)) * log det(I_k + A A^T),

with `det` computed by exact integer arithmetic (fraction-free Bareiss, or
multi-modular with a Hadamard bound) and the logarithm taken through `decimal` at
60 significant digits. **No float representation of the Gram determinant is read
anywhere.**

**COVERAGE, DECLARED IN ADVANCE.** `R7_exact_gram` is **MANDATORY at d <= 40**
(`L7`–`L12`, `k <= 28`, where the exact determinant is milliseconds) and
**BEST-EFFORT at d in {100, 140}** under a **declared cap of 45 s per lattice**;
a lattice that exceeds the cap is reported `UNCOVERED` and forces the `-PARTIAL`
suffix of §7.6. It is **not** an `FC-1` firing unless it exceeds the cap at
`d <= 40` as well.

**P-GRAM (CONSISTENCY CHECK).** `R7_exact_gram` must reproduce the committed `RQ`
and `RG` float64 values of `X_gso_k` to `1e-10` absolute at every basis and
lattice where both are computed. **If it does not, the derivation above is wrong,
`R7_exact_gram` is reported as UNAVAILABLE for `X_gso_k` — which fires `FC-1` —
and the disagreement is reported as a finding. It is never patched.**

---

## 3. THE DIAGNOSTIC MEASUREMENT — WHAT IS COMPUTED, AND NOTHING ELSE

**No gate. No threshold. No `ADMIT`/`REFUSE` produced by this section.** It
computes exactly the quantities §1's falsifiers consume, plus the two reported
diagnostics of §3.5–3.6.

### 3.1 Obligation (d) — the per-candidate fibre family and the guard that guards

For **every** in-scope candidate and **every** fibre draw (`fib_s2`, `fib_s3`,
`fib_s4`):

1. Build `fib(X)` from that candidate's **own** declared nuisance set per §2.4.
2. **ASSERT AND PRINT, per candidate, per fibre family and per lattice, WHICH
   DECLARED ARGUMENTS WERE VERIFIED CONSTANT ACROSS THE BASIS INDEX** — the whole
   declared nuisance set, not `abs(det B)` alone. `abs(det B_i)` is compared by
   **exact integer** equality; `A[0,0]` by integer equality; any further declared
   nuisance argument by the comparison declared beside it here.
3. The printout is outcome row `R3-OUT-4` and is a **first-class deliverable**:
   a run that computes it and does not print it per candidate has not discharged
   obligation (d).

**This is the must-pass guard `P-G2` of §6.1.** If any declared nuisance argument
of any scored candidate is **not** constant across `i` on that candidate's own
fibre family, `R3-OUT-V` fires: every fibre-constancy quantity in this batch is
**VOID**, the batch reports an instrument defect, and it reports nothing else.

### 3.2 Obligation (c) — every VAR-F-like constancy clause at TWO working precisions

For every in-scope candidate, every declared route of §2.6 and every covered cell,
compute at **both** `binary32` and `binary64`:

    s_c^fib, m_c^fib, rho = s_c^fib / |m_c^fib|,
    the `bit_identical` flag (carried verbatim from the committed
      measure_gvar2.py `bit_identical()`),
    the number of distinct IEEE-754 values over the 8 bases,
    THE COMMITTED VAR-F VERDICT of PREREG-1 3.3 evaluated at THAT precision,
    the fibre family label and seed prefix,
    and the ratio  rho(binary32) / rho(binary64) .

Report, per candidate and per route: **whether the committed `VAR-F` verdict
CHANGES between the two precisions**. `AM-18(b)`: *a clause whose verdict changes
with precision is reading a REPRESENTATION rather than an observable, and must be
reported as such.* That sentence is to appear in the report against every clause
whose verdict changes, in the report's own words, cell-counted.

### 3.3 `A-1.1` — the exact-route certification

For every in-scope candidate, evaluate `X` on `fib(X)` through its exact route
(`R6_exact` or `R7_exact_gram`) and record:

    exact route used, wall clock, whether it terminated within the declared cap,
    the exact fibre values over the 8 bases,
    CERTIFIED CLASS = CONSTANT if all 8 exact values are equal, NON-CONSTANT
      otherwise, UNCERTIFIED if the route did not terminate or is undefined,
    rho under the exact route (0 for CONSTANT by construction; reported anyway).

This is `R3-OUT-1`. **The certified class, not §2.4's expectation, is what §1.2's
falsifiers are evaluated against.**

### 3.4 `A-1.2` and `A-1.3` — scoring the falsifiers

Evaluate `FC-2a`, `FC-2b`, `FC-3a` and `FC-3b` exactly as §1.2 states them, over
the certified classes of §3.3, with the `precision_degenerate` rule of §1.3
applied as frozen and both readings reported at every such cell (`R3-OUT-7`).
Report per falsifier: fired / did not fire, the count of cells at which it fired,
and the extreme cell with its numbers. This is `R3-OUT-2`.

### 3.5 `P-SEP` — the precision-relative-scale feasibility measurement

`KN-FIND-9d44b4` §4 records — and this batch does not restate as new — that the
only shape nobody in this campaign has tried is **a scale declared relative to the
working precision rather than to the observable**. This section **measures whether
such a scale can exist on the declared candidates**. It **specifies no criterion**
and proposes no threshold; it computes an interval and reports whether it is
empty.

For each declared precision `p` with unit roundoff `u_p`, and each route `r`,
**solve** rather than grid:

    K_min(r,p) = max over CERTIFIED-CONSTANT candidates and covered cells of  rho / u_p
    K_max(r,p) = min over CERTIFIED-NON-CONSTANT candidates and covered cells of  rho / u_p
    admissible K-interval at (r,p) = ( K_min(r,p), K_max(r,p) )   -- EMPTY if K_min >= K_max

Report: the interval per `(route, precision)`; the intersection **over precisions**
at fixed route; the intersection **over routes and precisions** jointly; and
whether each is empty. This is `R3-OUT-5`.

**P-SEP (PREDICTION):** the joint intersection over both declared precisions is
**EMPTY** — no single precision-relative constant `K`, independent of route and of
precision, separates the two certified classes at both precisions.
**FALSIFIER:** the producer exhibits a non-empty joint intersection.
**BASIS FOR STATING IT IN THIS DIRECTION, DERIVED AND ATTRIBUTED, NOT MEASURED
HERE:** at `binary32` the archived null-object relative fibre dispersion reaches
`2.95e-01` (`rdet|R4`, Red Team `O-8`) while the archived real-object relative
dispersion stays at `5.71e-04` to `1.09e-02` and does not move with precision, so
the two classes' archived ranges **invert** between the precisions and no
constant multiple of `u_p` can sit between them at both. **The producer computes
the intervals and reports them rather than taking this paragraph's word**, and the
per-route intersections are reported separately because a per-route `K` is a
weaker and genuinely open possibility.

### 3.6 `AM-18(e)` — the null-object calibration at declared amplitudes

`X_hash` is scored through the identical code path at every declared amplitude
`c in {1e-9, 1e-3, 1e-2, 1e-1}`, on **all three** fibre draws (`AM-10`
replication), with dispersion reported per draw. This is `R3-OUT-6`.

**It is reported as a RE-EXECUTION AND EXTENSION of an archived construction and
never as a new finding.** That `X_hash` is admitted at 38 of 38 cells at the top
amplitude by the `BATCH-4ed139` code path is **archived, `n = 1`, and attributed**
to the Red Team's `probe_argset.py` section Q3 and to `KN-FIND-9d44b4` §6 item 5.
What is new here is only its behaviour **across precisions and on the
per-candidate fibre**, which nobody has measured.

---

## 4. OBLIGATION (b) — RE-SCORING F0's REFUSAL HALF WITH `R6_exact` ADDED

The `BATCH-4ed139` frozen verdict is **immutable and is not rescored**: `F0`
FAILED, the branch was `T-F0FAIL` reported as `T-F0FAIL-PARTIAL`, and
`DEC-20260812-781961` closed it. **This section adds a route and computes this
batch's own answer**, so that the successor's record answers the question rather
than inheriting that decision's answer, exactly as the goal's `next_action`
requires.

**SCOPE: `F0`'s REFUSAL HALF ONLY** — the `X_null` and `rdet` lines of `PREREG-1`
4.1, both determinant-only, requiring **no reduction at all** and fully scorable
on any host. The `lam1n`/`hkz`/`rawtail` ADMITTED half is **not in scope** (§2.5).

**THE THREE READINGS ARE FROZEN HERE, ALL THREE ARE REPORTED, AND NO ONE OF THEM
MAY BE CITED WITHOUT NAMING ITS ROUTE SET IN THE SAME SENTENCE.** This is the
`C-1` lesson applied in advance: a verdict is a joint function of its route set,
and a citation that names fewer axes than the verdict has is under-determined.

    V6   verdict over the SIX float routes {R0..R5}       -- the frozen PREREG-1
         4.1 reading, recomputed here
    V7   verdict over the SEVEN routes {R0..R5, R6_exact} -- every route must hold
    VX   verdict over the EXACT route ALONE {R6_exact}    -- the reading Red Team
         RC-1's conditional is about

**P-F0Xa (CONSISTENCY CHECK, AM-15(a)):** `V6 = FAIL`, reproducing `BATCH-4ed139`.
Its falsifier is empty conditional on reproducing a committed measurement, so it
is classified as a consistency check and does **not** count toward this batch's
empirical content. It is still run and still reported.

**P-F0Xb (PREDICTION):** `V7 = FAIL` and `VX = PASS` on the refusal half at 38 of
38 cells. **FALSIFIER:** either disagreeing at any covered cell.

**WHAT `VX = PASS` WOULD AND WOULD NOT LICENSE, FROZEN BEFORE THE RUN.** It would
license exactly the statement Red Team `RC-1` frames: that the `F0` refusal
failure is localised to the **float representation** consumed by `PREREG-1` 3.3's
fallback, and **not** to `AM-16(a)`. It would license **nothing** about any
lattice, about any observable's admissibility, about `F1`, about any prior
batch's verdict, or about the gate. And it does **not** validate any criterion:
`G-VAR2` remains the instrument `DEC-20260812-781961` records as not governing
anything in this goal.

---

## 5. PREDICTION REGISTER (`AM-15(a)` and `AM-15(c)`)

**All ten items below were OPEN at the moment of notarization. None of them had
been evaluated by anyone when this text was frozen.**

| id | statement | falsifier | class | open at notarization |
|---|---|---|---|---|
| P-A11 | an exact route exists and terminates within the declared cap for every in-scope candidate (mandatory at d <= 40) | FC-1 | PREDICTION | OPEN |
| P-A12a | `X_null` and `rdet`: `rho(f32) > rho(f64)` at every non-degenerate covered cell, `rho(exact) = 0` | FC-2a / FC-2b | CONSISTENCY CHECK — the f32/f64 ratios and the exact-route result are archived (Red Team `probe_precision_null`) | OPEN |
| P-A12b | `X_parfree`, `V_evade`, `X_lambda` (every lambda): same, on their **own** fibre | FC-2a / FC-2b | PREDICTION — no archived measurement exists on the per-candidate fibre | OPEN |
| P-A13a | `X_gso_k`: `rho(f32)/rho(f64)` in `[1/2, 2]` and `rho > 0` at both precisions | FC-3a / FC-3b | CONSISTENCY CHECK — archived at `0.9999991`..`1.0000001` | OPEN |
| P-HASH | `X_hash`: `rho(f32)/rho(f64)` in `[1/2, 2]` and `rho > 0`, at every declared amplitude and fibre draw | FC-3a / FC-3b | PREDICTION | OPEN |
| P-SEP | the joint `K`-interval over both precisions is EMPTY | a non-empty joint intersection | PREDICTION | OPEN |
| P-F0Xa | `V6 = FAIL` | `V6 != FAIL` | CONSISTENCY CHECK | OPEN |
| P-F0Xb | `V7 = FAIL` and `VX = PASS` at 38/38 | either disagreeing at any cell | PREDICTION | OPEN |
| P-GRAM | `R7_exact_gram` reproduces committed `RQ`/`RG` `X_gso_k` to `1e-10` | any disagreement above `1e-10` | CONSISTENCY CHECK | OPEN |
| P-G2 | every declared nuisance argument of every scored candidate is constant across `i` on that candidate's own fibre family | any declared argument varying anywhere | MUST-PASS GUARD | OPEN |

**Empirical content of this batch: FIVE predictions** (`P-A11`, `P-A12b`,
`P-HASH`, `P-SEP`, `P-F0Xb`). **FOUR consistency checks** (`P-A12a`, `P-A13a`,
`P-F0Xa`, `P-GRAM`) — reported, valuable, and **not** counted. **ONE must-pass
guard** (`P-G2`). A count of predictions is a function of the governing amendment
set, not of the artifacts alone; this register is that function, evaluated here
and frozen.

**`P-HASH` IS THE SHARPEST NEW TEST IN THIS BATCH AND ITS CONSEQUENCE IS FROZEN
BEFORE THE RUN.** `X_hash` reads every entry of `A` and carries **no lattice
information whatever**. If `P-HASH` holds, then **precision-invariance of the
fibre dispersion is NECESSARY BUT NOT SUFFICIENT for "reads the instance"**, and
`A-1` — even if it survives every falsifier — buys **strictly less** than a
separator. **`P-HASH` holding CANNOT falsify `A-1`** (`X_hash` is certified
non-constant, so `A-1.3` predicts exactly this) and **may not be reported as
falsifying it**; what it bounds is `A-1`'s usable content, and that bound is to be
stated in the same paragraph as any statement that `A-1` held.

---

## 6. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN

### 6.1 The MUST-PASS guard `P-G2`, and `AM-18(d)`'s published reachability

**GUARD.** §3.1: every declared nuisance argument of every scored candidate is
constant across the basis index on that candidate's own fibre family.

**VOID ROW `R3-OUT-V`:** if it fails anywhere, every fibre-constancy quantity in
this batch is **VOID**; the batch reports the instrument defect and nothing else.

**ANALYTIC REACHABILITY OF THE VOID ROW, PUBLISHED HERE BEFORE THE RUN AS
`AM-18(d)` REQUIRES — and this is the clause `O-6` was written to force.** The
row is **reachable, and its reachability is DEMONSTRATED rather than merely
argued**: under `BATCH-4ed139`'s candidate-**independent** fibre construction the
`A[0,0]` row would have fired at **10 of 10 lattices in every one of the six
fibre families**, for both `V_evade` and `X_lambda` (attributed to Validator `F-2`
and Red Team `O-1`; example values recorded there, `F0|fib_s2` at `L1`:
`791, 895, 1188, 1315, 1620, 2122, 2284, 2918`).

**AND THE HONEST OTHER HALF, STATED IN THE SAME PLACE.** Under **this** batch's
`PIN-A00` construction the row is reachable **only through an implementation
error**, because the pinning is by construction. **Its non-firing is therefore
evidence about the IMPLEMENTATION and about nothing else, and it may NOT be cited
as a control, as a validation of the fibre clause, or as evidence about any
object.** That sentence is frozen here so no later reader has to reconstruct it.

**NO OTHER MUST-PASS GUARD IS DECLARED, AND THE REASON IS RECORDED.** The obvious
candidate — "the instrument can resolve real fibre variation at all", i.e.
`X_gso_k`'s `rho` exceeding `u_64` — has a VOID row **unreachable by roughly
twelve orders of magnitude** on the archived numbers (`5.71e-04` against
`u_64 = 2.22e-16`). `AM-18(d)` permits running such a guard while barring its
citation; this pre-registration declines to run it, because `O-6` is this goal's
recorded cost of one straw-man guard and a second would be worse than none. The
margin is reported as a **diagnostic** in `R3-OUT-2` and is cited as a
measurement, never as a control.

### 6.2 could-not-FALSIFY — `A-1` could never fail

Would hold if every declared candidate fell into a single certified class, or if
no exact route existed at all, or if every falsifier carried a window wide enough
to swallow both classes. **WE ARE NOT IN IT, AND IT IS MEASURED RATHER THAN
ASSERTED:**

* **both classes are populated by construction**: five candidates expected
  `CONSTANT` (`X_null`, `rdet`, `X_parfree`, `V_evade`, `X_lambda`) and two
  expected `NON-CONSTANT` (`X_gso_k`, `X_hash`) — and the producer reports the
  **certified** class counts, not this sentence;
* **four of the five falsifiers carry no numeric constant at all** (`FC-1`,
  `FC-2a`, `FC-2b`, `FC-3b`): they are existence, direction and order tests;
* `FC-3a`'s window is `[1/2, 2]`, six orders from each archived class (§1.4).

### 6.3 could-not-HOLD — `A-1` could never survive

Would hold if some falsifier fired by construction before any measurement. **The
one live instance is named and frozen rather than left to be discovered**: at a
cell where `rho(binary64) == 0` exactly, `FC-2a`'s strict decrease is vacuous, and
under the strict reading `A-1.2` would be falsified at every `R0` cell **by the
definition of `R0`**, which never touches the matrix. §1.3's `precision_degenerate`
rule exempts exactly those cells, binds as the frozen reading, and requires the
strict reading to be printed beside it at every one of them. **A reviewer should
attack exactly there**, and `R3-OUT-7` exists to make that cheap.

### 6.4 could-not-fail on the FIBRE clause specifically

* **could-not-FAIL:** if every fibre family happened to hold every candidate
  constant, the certified-`NON-CONSTANT` class would be empty and `A-1.3` would be
  vacuous. **Live check:** `X_gso_k` and `X_hash` read the free content of `A`;
  the producer must exhibit at least one candidate certified `NON-CONSTANT` by the
  exact route or report the classification as degenerate.
* **could-not-PASS:** if a fibre family failed to hold a declared nuisance
  argument fixed, every constancy verdict computed on it would be about the wrong
  object. **Guarded by `P-G2`**, and that guard now ranges over the **whole
  declared nuisance set**, which is precisely the `AM-18(c)` repair and precisely
  what `BATCH-4ed139`'s guard did not do.

### 6.5 `AM-16(f)`

Not applicable: this batch estimates no standard error and applies no variance
decomposition. Declared N/A with its reason rather than omitted.

---

## 7. THE TERMINATION CLAUSE — FROZEN BEFORE THE RUN

Exactly one of `T-VOID`, `T-UNSTATABLE`, `T-A1-FALSIFIED`, `T-A1-HELD` fires.
§7.6 is the infrastructure/coverage branch and is **not** a fifth science branch.

**PRECEDENCE, FROZEN:** `R3-OUT-V` (`T-VOID`) dominates everything. Then
`T-UNSTATABLE`. Then `T-A1-FALSIFIED`. `T-A1-HELD` fires only if none of the
first three does, at full declared coverage.

**The branch is read off `R3-OUT-1` and `R3-OUT-2` under `R3-OUT-V`'s precedence,
and NOWHERE ELSE.**

### 7.1 `T-VOID` — the must-pass guard failed

**FIRES WHEN:** any declared nuisance argument of any scored candidate is not
constant across `i` on that candidate's own fibre family (§3.1).

**MEANS:** the fibre families do not instantiate the declaration, so no
fibre-constancy quantity in this batch is about the object it names.

**LICENSES:** a decision recording an **instrument failure** and specifying the
repair. Nothing else.

**FORBIDS:** reporting any `A-1` verdict in either direction; reporting `V6`,
`V7` or `VX`; treating any number in this batch as evidence about any object;
closing, pausing or completing `GOAL-MLKEM-005`.

### 7.2 `T-UNSTATABLE` — the assumption cannot be stated in a form its own falsifier could reach

**FIRES WHEN:** `A-1.1`'s exact route is unavailable, undefined, or
non-terminating within the declared cap for **EVERY** in-scope candidate class —
both the determinant-only class **and** the raw-GSO class. Out-of-scope
candidates (§2.5) do **not** count toward this branch in either direction.

**MEANS:** "non-constant on the fibre" cannot be given a finite-precision meaning
whose own falsifier the declared instrument can reach.

**LICENSES:** **CLOSING THE ADMISSIBILITY-GATE LANE**, with that as its named
obstruction, and proceeding to `C3` with every candidate declared
**PRESENTATION-DEPENDENT** and every `C3` verdict scoped accordingly. The closure
requires **its own committed Coordinator decision** carrying, as
`docs/inventor-protocol.md` §4 and `CLAUDE.md` rule 9 require: its evidence, its
budget, its test boundary, its remaining uncertainty, and a concrete successor or
revisit condition.

**FORBIDS:**
* **closing, pausing or completing `GOAL-MLKEM-005`.** Closing the
  admissibility-gate LANE retires the **LANE**, never the goal. A lane closure
  with a named obstruction is in this goal's `non_terminal_conditions` and may not
  be cited in a decision that closes, pauses or completes it;
* treating a **class-scoped** decidability failure as this branch — that is
  `T-A1-FALSIFIED` with the scope named (§7.3);
* treating the **declared** out-of-scope status of the reduction-dependent
  candidates (§2.5) as a decidability failure of any kind;
* any claim about any lattice, any parameter set, any attack cost or any cost
  model.

**REACHABILITY OF THIS BRANCH, PUBLISHED BEFORE THE RUN AND STATED AGAINST
ITSELF.** The determinant-only exact route `R6_exact` is **already built, already
run and archived**, at a cost of `0.4 s` (attributed). **This branch therefore
CANNOT fire on that class**, and can fire at all only if `R7_exact_gram` **also**
fails, at every lattice including `d <= 40`, where §2.9's derivation says it is
milliseconds of integer arithmetic. **THIS BRANCH IS THEREFORE NEARLY FORECLOSED
BY AN ARCHIVED ARTIFACT, AND ITS NON-FIRING IS NOT EVIDENCE THAT THE ASSUMPTION IS
WELL-FOUNDED.** That is the `O-6` discipline applied to a branch instead of a
guard, and it is written here so that no successor can cite this branch's silence.

### 7.3 `T-A1-FALSIFIED` — a falsifier fired

**FIRES WHEN:** any of `FC-1` (for some but not all classes), `FC-2a`, `FC-2b`,
`FC-3a`, `FC-3b` fires at any covered cell, route or candidate.

**MEANS:** `A-1` as stated is **false** at the declared precisions, routes,
families and candidates. It does **not** mean that no finite-precision meaning
exists; it means this one does not survive.

**LICENSES:** a decision recording exactly **which sub-clause failed, at which
cells and routes, and for which certified class**, and the specification of a
**SUCCESSOR ASSUMPTION** — not a criterion — subject in full to §7.5.

**FORBIDS:**
* specifying **any** dispersion criterion, fibre clause or gate resting on `A-1`;
* proceeding to `C3` behind any gate;
* presenting the falsification as evidence about any lattice, any observable's
  admissibility, or any proposition in this goal — **it is an instrument
  outcome**;
* reading a failure **caused by a missing dependency, a timeout, a crash or the
  declared `R7` cap at `d > 40`** as a falsifier at all: that is INFRASTRUCTURE
  SIGNAL (`AGENTS.md` rule 5) and forces §7.6 instead;
* closing, pausing or completing `GOAL-MLKEM-005`.

### 7.4 `T-A1-HELD` — no falsifier fired at full declared coverage

**FIRES WHEN:** none of `FC-1`, `FC-2a`, `FC-2b`, `FC-3a`, `FC-3b` fires, at full
declared coverage, and the guard passed.

**MEANS:** `A-1` **survived its first test at this scale**. It does **not** mean
`A-1` is true.

**LICENSES:** a successor **may** specify a replacement fibre clause **built on
`A-1`** — subject in full to §7.5's repair bar — and must carry `A-1`'s scope
(§8) with it at the point of quotation.

**FORBIDS:**
* any claim that the admissibility gate is repaired, validated or usable;
* any claim that a precision-invariant observable **carries lattice information**
  — `P-HASH` bounds exactly that, and if `P-HASH` holds, the bound is stated in
  the same paragraph as any statement that `A-1` held;
* any retro-validation of `BATCH-4ed139`, `BATCH-9e3584`, `BATCH-cbe023` or
  `BATCH-a44d08`, or of any verdict scored under any predecessor instrument;
* proceeding to `C3` behind a criterion that does not yet exist;
* any transport of any number here to ML-KEM parameters, to `beta = 606`, to
  `d = 1420`, or to any FIPS 203 parameter set, by extrapolation, analogy or any
  other route;
* closing, pausing or completing `GOAL-MLKEM-005`.

### 7.5 THE REPAIR BAR — what makes a further gate repair ILLEGITIMATE

**This section exists because `PREREG-1` 7.3's FORBIDS list, unlike 7.2's,
contained no bar on a seventh consecutive gate repair, and 7.3 is the branch that
fired (Red Team `O-3`).** It binds every branch of §7 and every successor of this
batch.

A further dispersion criterion, fibre clause or gate repair in `GOAL-MLKEM-005` is
**ILLEGITIMATE** unless **all six** of the following hold, each demonstrable from
committed artifacts:

1. **It rests on a NUMBERED assumption that precedes it textually**, with a
   falsification condition **reachable by the instrument that will score it** —
   and the reachability is published **before** the run (`AM-18(a)`, `AM-18(d)`).
2. **Its threshold, if it has one, is not calibrated on the same committed
   numbers it will be validated against.** `PREREG-1` 3.4 declared that weakness
   honestly; a successor that repeats it without declaring it is illegitimate.
3. **It is accompanied by a null-object calibration at declared amplitudes**
   (`AM-18(e)`), scored through the identical code path.
4. **It NAMES IN ADVANCE the class of objects it CANNOT separate, and EXHIBITS
   ONE.** Every criterion in this goal has been defeated by an object built after
   it was frozen; a criterion that cannot name its own blind spot has not been
   thought about.
5. **It states, in the same sentence as the proposal, the count of consecutive
   instrument batches to date** — seven as of this batch — so the cost is visible
   at the point of decision and not in a later apology.
6. **It states why the alternative is worse, on the record.** The alternative is
   proceeding to `C3` with candidates declared presentation-dependent. **This
   requirement is a decision-hygiene requirement and is NOT a licence to take that
   alternative**: `T-F1FAIL` did not fire in `BATCH-4ed139`, `PREREG-1` 7.3
   independently forbids proceeding to `C3` behind `G-VAR2`, and adopting the
   consequence of a branch that did not fire remains forbidden.

**AND ONE ABSOLUTE BAR:** **NO EIGHTH CONSECUTIVE GATE REPAIR MAY BE DISPATCHED
IN THIS GOAL** without a committed Coordinator decision that first records, with
evidence, why the `C3` lane cannot be entered instead. **Symmetry, stated so this
clause cannot be misused:** premature closure is a failure mode symmetric with
overclaiming, this bar is **not** a licence to close the lane, to close the goal,
or to declare the problem saturated, and a count of failed criteria is a fatigue
report rather than a finding (`docs/inventor-protocol.md`).

### 7.6 `T-PARTIAL` — the infrastructure/coverage branch, declared so it cannot be narrated into a science branch

**FIRES WHEN:** any declared cell, route or candidate is **uncovered** — a
timeout, a crash, a missing dependency, or the declared `R7_exact_gram` cap at
`d in {100, 140}`.

**RULE:** the **determinant-only** work of this batch requires **no reduction at
all** and is fully scorable on any host; its results are binding regardless. The
`X_gso_k` exact-route half is reported at its **actual coverage**, lattice by
lattice.

**CONSEQUENCE:** the branch that fires is reported with the suffix `-PARTIAL`, and
**all four are enumerated here** so no successor has to apply a general rule to a
list that omits its case — a latitude `DEC-20260812-781961` recorded against
`PREREG-1` 7.4 and asked a successor to close:

    T-VOID-PARTIAL   T-UNSTATABLE-PARTIAL   T-A1-FALSIFIED-PARTIAL   T-A1-HELD-PARTIAL

**`T-A1-HELD-PARTIAL` DOES NOT LICENSE A SUCCESSOR CRITERION.** A partially tested
assumption is not a tested one, and the missing coverage becomes the next action.

**A missing dependency, a timeout or a crash is never a negative mathematical
result, and no branch of §7 may be reached through one.**

---

## 8. OUTCOME ROWS

| row | what it records |
|---|---|
| `R3-OUT-1` | `A-1.1`: the exact-route certification per candidate — route, wall clock, termination, exact fibre values, CERTIFIED CLASS, coverage per lattice |
| `R3-OUT-2` | `A-1.2`/`A-1.3`: the two-precision table — `rho(f32)`, `rho(f64)`, the ratio, the committed `VAR-F` verdict at each precision and whether it changed, per candidate, route and cell; and each falsifier fired / not fired with its cell count |
| `R3-OUT-3` | obligation (b): the `F0` refusal half under the three frozen readings `V6`, `V7`, `VX`, per candidate, route and cell, with coverage |
| `R3-OUT-4` | obligation (d): per candidate, per fibre family and per lattice, **WHICH DECLARED ARGUMENTS WERE VERIFIED CONSTANT** across the basis index |
| `R3-OUT-V` | **VOID**: a declared nuisance argument was not constant on a candidate's own fibre, so every fibre-constancy quantity in this batch is void |
| `R3-OUT-5` | `P-SEP`: the admissible `K`-intervals per route and precision, and the intersections |
| `R3-OUT-6` | `AM-18(e)`: `X_hash` at every declared amplitude on all three fibre draws, with dispersion |
| `R3-OUT-7` | the `precision_degenerate` disclosure: which cells, per candidate and route, with the **strict** reading's verdict beside the **frozen** one |
| `R3-OUT-8` | `P-GRAM`: `R7_exact_gram` against committed `RQ`/`RG`, max absolute deviation |

---

## 9. WHAT IS ALREADY PROMOTED AND IS **NOT** THIS BATCH'S FINDING

`knowledge/findings/KN-FIND-9d44b4.md` is **promoted, in the corpus, and binding**.
**Nothing in the following list may be restated as a new result of
`BATCH-6b6e78`**, by any producer or reviewer:

* that a fibre-constancy test evaluated on floating-point values cannot separate
  "reads the instance" from "reads a nuisance parameter";
* that the `F0` failure is a **float-representation effect** tracking machine
  epsilon over seven to nine orders;
* that `G-VAR2` **REFUSES `rdet` at 38/38 under `R6_exact`** and `F0`'s declared
  target for `rdet` is met once the float representation is removed;
* that the admission is **threshold-independent across sixteen decades** of
  `tau_var`, bit-identity at a `scale_degenerate` cell having no threshold at all;
* that the defect belongs to the **clause** and not to `rdet`, shown by a blind
  null the producers never scored;
* that the **declared argument set is decorative** in the `BATCH-4ed139`
  implementation;
* that the obstruction is **two-sided**: evaluated exactly, the clause needs a
  scale, and a scale is a threshold.

**WHAT THIS BATCH TESTS INSTEAD — what follows from all of that:** whether the
replacement meaning can be **numbered and falsified** (`A-1`, §1); whether the
exact route exists for the one candidate that reads the instance (`R7_exact_gram`,
§2.9 — **new, and derived here**); whether the per-candidate fibre repairs the
guard (§3.1); whether a **precision-relative** scale can exist at all (`P-SEP`,
§3.5 — the shape `KN-FIND-9d44b4` §4 records as untried); whether
precision-invariance is **sufficient** for reading the instance (`P-HASH`, §5 —
predicted **no**); and this batch's **own** answer on `V6`/`V7`/`VX` (§4).

---

## 10. BINDING CARRIES — IN FORCE, NOT RE-LITIGATED

* **`AM-10` through `AM-14`** of `DEC-20260808-05b684` and their binding carries,
  including that `AM-13`'s consistency-check clause binds **every** section.
* **`AM-15` and `AM-16`** of `DEC-20260809-afe29b`; **`AM-17`** of
  `DEC-20260812-7c4a1e`; **`AM-18`** of `DEC-20260812-781961`, all in force. A
  non-citation carry binds **at the point of QUOTATION**, never at the point of
  occurrence.
* **`AM-3` IS NOT RETIRED.** Its power remains undemonstrated rather than
  disproved and its `0.096` family-wise false-failure bound stands.
* **`BATCH-a44d08` IS NOT RESCORED IN ANY RESPECT** and its Section C verdict and
  detection floors remain **VOID IN BOTH DIRECTIONS**. `BATCH-9e3584`,
  `BATCH-cbe023` and `BATCH-4ed139` are **NOT REVALIDATED**.
* **`AM4-OBS-1` is cited ONLY through `knowledge/findings/KN-FIND-f38a89.md`.**
* **`AM-9`:** fpylll's `k` counts the q-scaled rows, **NOT** the identity block.
* **THE `G-VAR` REFUSAL IS CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY `F0`.**
* The **split-producer notarization pattern** is retained unchanged.
* The **receipt-with-`commit_sha: null`-inside-its-own-commit** archive pattern is
  **MANDATORY**.
* Every run emits durable `command.txt`, `stdout.log` and `stderr.log`, with **no
  path inside a folded YAML scalar**, and **lists every path it wrote** in its
  report.
* `knowledge/INDEX.md` must **NOT** be written, regenerated or staged: it is
  generated and `.gitignore`d.
* **`AGENTS.md` rule 12 is UNMET AND UNWAIVED.** Two reviews are two **SESSIONS**
  on **ONE MODEL** and **ONE HOST** — never model-level and never environmental
  corroboration. Two knowledge promotions remain owed from `GOAL-MLKEM-003` and
  cannot be executed without a second backend.
* **`PD-4` IS OPEN.** Each review's own report and probes sit uncommitted across a
  dispatch window and are the sole carriers of their own evidence until the ledger
  archive commits them. The named fix is unchanged: a
  `tools/research_dispatch.py` change verifying an already-committed source by
  hash.
* **CLAIM TIER STAYS TOY.**

### 10.1 NOT CITABLE ANYWHERE IN THIS BATCH

* **"a factor of 6 to 31"** — the citable range is **4.87x to 31.03x**, and any
  quotation of a span names its normalization (the same 29 entries span `5.71x` to
  `37.50x` under `absX`);
* **BOTH sub-6x counts** — neither *"15 of the 19 `G-REL2` cells below 6x"* nor
  *"two of 29 entries below 6x"* is citable, and **"wave 2's count corresponds to a
  5.71x threshold" is NOT citable as THE explanation**, at least two incompatible
  accounts reproducing it and naming the same two entries;
* **ANY sub-threshold count in this goal must name ALL FOUR AXES in the same
  sentence** — reading, normalization, boundary rule, threshold — **plus its
  summation algorithm**. A count naming fewer is under-determined and is not
  citable;
* the **"genuinely cross-platform"** reading of the `L7`/`L8` agreement — the
  citable form is a **PORTABILITY** result across three textually distinct
  implementations with fpylll pinned at `0.6.4`;
* **"the guard crossed, so `VAR-S` is alive at this scale"** as a live control, and
  the grid crossing amplitude is citable **only as an UPPER BOUND**;
* rider (ii)'s **`G-VAR2` half** as evidence about the world (its `G-REL1` half is
  citable);
* every number computed under an alternative `A[0,0]`-pinned fibre **in
  `BATCH-4ed139`**, or at any `tau_var` other than the frozen `1e-3` there, is
  **POST-HOC** and citable only as a sensitivity analysis of that batch. **This
  batch pre-registers the `A[0,0]`-pinned fibre in advance (§2.3 `PIN-A00`), so
  ITS OWN numbers are not post-hoc — and that distinction must be stated at the
  point of quotation, never assumed;**
* **"no admissibility claim is reportable in either direction"** — replaced by
  `DEC-20260812-7c4a1e` `C-2`'s three-part decomposition, whose part (b) is
  narrowed by `DEC-20260812-781961` to **ONE CONSTRUCTED INSTANCE with no rate**;
* **"the null fires more often than the real arm"** as a general statement;
* **"`G-VAR` cannot be tuned into or out of firing"** — FALSE;
* **"three predictions of actual empirical content"** — the official count for
  `BATCH-9e3584` Section R remains **ONE**;
* the blanket **"Residuals are 0 identically"** — cited **per transform**;
* **"the obstruction is relocated"**; **"CONSISTENT"** in either direction;
* **"29 of 48" without the exact-null benchmark of 47 of 48 in the same
  sentence**;
* the `3.91%` floor without its **NEGATIVE-VARIANCE-COMPONENT** qualifier; the
  non-degenerate figure is **10.83%**.

---

## 11. SCOPE, INDEPENDENCE AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; `d in {20, 30, 40, 100, 140}`; the frozen `k` and `beta`
grids; 8 bases per lattice per fibre family; one scored family `F0` and three
fibre draws; six float routes plus one exact route for determinant-only
candidates, two float routes plus one exact route for `X_gso_k`; two working
precisions, `binary32` and `binary64`; **no reduction of any kind** and nothing
reduction-dependent above `d = 40`. **Every conclusion is scoped to exactly that
and transports nowhere.**

**`A-1`'s OWN SCOPE, CARRIED AT EVERY QUOTATION.** `A-1` is stated over the
in-scope candidates of §2.4 only. **It says nothing about any reduction-dependent
observable** (§2.5), which is the half of this goal's candidate list that matters
for `C3`.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` **rule 12 is
UNMET AND UNWAIVED** in this goal and is not waived here. Every producer and
reviewer of this batch records `model_verified: false` with its reason, and
records its host and stack, so that environmental correlation is visible rather
than assumed away.

**WHAT THIS BATCH CANNOT DO, stated so no reader has to infer it.** It cannot say
anything about ML-KEM, about any FIPS 203 parameter set, about any attack cost or
about any cost model. It cannot establish that any observable carries lattice
information — and if `P-HASH` holds it measures how far precision-invariance is
from that. It cannot measure a false-refusal rate. It cannot validate, repair or
license any gate. It cannot revalidate any prior batch. **It cannot close, pause
or complete `GOAL-MLKEM-005`.**

---

## 12. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no git
command, no probe, no `allocate_id`, and computed no hash. **Every number quoted
here is attributed to the review, decision or committed artifact that measured
it**, and none is claimed as this session's own measurement. In particular:
`38 of 38`, `0.4 s`, `1.4e6`, `5.9e8`, `5.5e7`, `5.369e8`, `0.9999991`,
`1.0000001`, `2.64e-9`, `5.71e-04`, `1.09e-02`, `2.95e-01`, `71.3`, `7.1316e-02`,
`15 of 38`, `22 of 38`, `10 of 10`, the eight `A'[0,0]` values at `L1`, and the
sixteen-decade `tau_var` result are all **carried, not measured here**.

**The one thing this session did produce itself is a DERIVATION, §2.9**, that
`X_gso_k = (1/(2k)) log det(I_k + A A^T)` on the frozen families. It is elementary,
it is stated in full so a reader can check it in a minute, and it is **subject to
`P-GRAM`**: if it disagrees with the committed `RQ`/`RG` values above `1e-10`, the
derivation is wrong, the route is reported UNAVAILABLE, and that is a finding of
this batch rather than something to patch.

`prereg_sha256.txt` is therefore **generated and committed by
TASK-20260813-502381**, by a session that has a shell, and is that task's own
declared artifact.

**END OF FROZEN TEXT.**
