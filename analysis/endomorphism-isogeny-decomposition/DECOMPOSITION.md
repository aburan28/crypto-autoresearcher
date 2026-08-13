# Prime-field ECDLP: a resource-labelled subproblem decomposition centred on endomorphisms, isogenous curves, and j-invariant structure

- Campaign: `GOAL-ENDO-001`
- Opening batch: `BATCH-cb71b5`
- Authority: Coordinator (this document creates no evidence and moves no hypothesis status)
- Date: 2026-08-07
- Parent question: `RQ-ECDLP-002` (`GOAL-ECDLP-001`)

## 0. What this document is and is not

This is a **decomposition**, not a result. It partitions prime-field ECDLP into
subproblems, states for each one the exact non-generic resource it must consume,
the cost functional it targets, and the cheapest measurement that could kill it.
Nothing here asserts that any lane works. Several lanes are opened specifically
because the program's own standing conclusions predict they will fail, and a
clean failure with a named obstruction is the deliverable in those cases
(`docs/inventor-protocol.md`, closure standard).

Every claim below that is not a citation is either (a) an elementary
verifiable fact, marked **[fact]**, or (b) a conjecture/expectation to be
tested, marked **[open]**. No claim is made about crypto-scale behaviour.

## 1. Setting and notation

`p > 3` prime, `E/F_p` an elliptic curve, `t = p + 1 - #E(F_p)` its trace,
`G = <P> ⊆ E(F_p)` of prime order `N`, `Q = [k]P`. Recover `k`.

Write `D = t^2 - 4p < 0` for the Frobenius discriminant (ordinary case),
`K = Q(sqrt(D))`, `O_K` its maximal order. By Deuring/Waterhouse,
`Z[pi] ⊆ End_{F_p}(E) ⊆ O_K`, and `End_{F_p}(E)` is an order `O` of conductor
`f_E | f`, where `D = D_0 f^2` and `D_0` is the fundamental discriminant.

## 2. Layer 0 — the admissibility filter every lane must pass

Shoup's bound gives `Omega(sqrt(N))` for generic algorithms. This program has
already closed two natural augmentations at exponent 1/2:

- **Incidence oracle** and **endomorphism-image oracle** are GGM-simulable, hence
  closed (`KN-FIND-b7e091`, `EV-GGM-79e710`, `DEC-20260804-3b4258`).
- `H-ENDO-001` states the reason in the sharpest possible form: `G` has **prime**
  order, so `End(G) ≅ Z/N` and **every** endomorphism of `E` acts on `G` as
  multiplication by a scalar `lambda in Z/N`. Adding `r` endomorphisms to the
  witness lattice adds coordinates but **no new congruence**; the index stays
  exactly `N`, the meet-in-the-middle exponent stays `1/2`, and the constant
  doubles per endomorphism.

**Consequence — the admissibility filter.** A lane is *inadmissible on its face*
if the only thing it does with `phi` is apply it to points of `G`. Any lane
in this campaign must therefore name a resource that is **not** a group-operation
output. The resource taxonomy used to label every lane:

| Resource | What it is | Why it escapes the GGM |
|---|---|---|
| **R1** | `x`-coordinates as *field elements* (index calculus, Semaev) | the oracle returns field data, not group elements |
| **R2** | the curve *equation* `(a,b)` / model | changes polynomial systems, not the group |
| **R3** | `End(E)` as a *ring* (ideals, norms, class group) | ring structure is invisible to `G` |
| **R4** | the *isogeny graph* / class-group action | acts on curves, not on points |
| **R5** | `ell`-torsion for `ell != N`, as a Galois module | outside `G` entirely |
| **R6** | lifts to `Z_p` / char 0 | a different group |
| **R7** | pairings into `F_{p^k}` | a different group |
| **R8** | multi-instance / preprocessing structure | changes the model, not the group |

A lane that cannot name its resource is closed before it costs anything. This is
the cheapest audit in the campaign and it is applied to every idea generated.

## 3. Layer 1 — the transport theorem, and why "isogenous curves" is a real axis

**[fact] T1 (transport).** Let `phi: E -> E'` be an `F_p`-isogeny of degree `d`
with `gcd(d, N) = 1`. Then `phi` restricted to `G` is an injective group
homomorphism, `phi(Q) = [k] phi(P)`, and `phi(P)` has order `N`. So the
instance `(E, P, Q, k)` maps to `(E', phi(P), phi(Q), k)` **with the same `k`**.

**[fact] T2 (class-wide vulnerability).** ECDLP difficulty is therefore constant
across an `F_p`-isogeny class *up to transport cost*. If **any** curve in the
class admits a cheaper attack, every curve in the class does.

**[fact] T3 (the invariance test is decisive both ways).** If an attack-cost
functional `C(E)` is provably constant on the isogeny class, this axis is closed
*for that functional* — with a named obstruction, which is a legitimate closure.
If `C` varies, the campaign gets a target: `min_{E' ~ E} C(E')`.

**[fact] T4 (what varies and what does not).** Fixing the class fixes `t`, hence
fixes `p`, `N`, `#E(F_p)`, the embedding degree, the CM field `K`, and `D`.
Fixing `t` therefore also fixes whether `j = 0` or `j = 1728` occurs anywhere in
the class (`j = 0` requires `D_0 = -3`, `j = 1728` requires `D_0 = -4`) and fixes
the maximal automorphism group available. **You cannot walk to a `j = 0` curve
from a curve whose class does not already contain one.** What *does* vary within
a class: the `j`-invariant itself, the isomorphism class of `(a, b)`, the
endomorphism-ring level in each `ell`-volcano, `h(End(E))`, and the number of
`F_p`-rational `ell`-isogenies at each level.

**[open] T5 (the reachability gate — the crux of the whole campaign).**
The crater of the `ell`-volcano is a Cayley graph of `Cl(O)` and, under GRH, is
a rapid mixer. So a **uniformly random** curve in the class is reachable in
`O(log p)` isogeny steps: *cheap*. But reaching a **specified** curve is the
vectorization problem underlying CSIDH: *hard*, `~sqrt(h) ~ p^{1/4}` classically
at best. Hence the decomposition's central dichotomy:

> A cost-minimising curve in the isogeny class is useful **only if goodness is
> (i) common enough to hit by random walking, or (ii) detectable by a *local*
> test evaluable at each step of a walk.** Goodness that is only identifiable by
> a global address is unreachable, and the lane dies on cost even if the
> variance is large.

T5 is stated here so that every lane in this campaign carries reachability as a
mandatory second gate, and no lane may report a variance result as an attack.

## 4. Layer 2 — the fourteen subproblem lanes

Each lane names: the resource (R1–R8), the invariant exploited, the cost
functional targeted, the decisive cheap test, and the prior obstruction it must
get past. `RQ` ids are the campaign's research questions.

### L1 — Isogeny-class invariance of attack-cost functionals · `RQ-ICINV-475b5e`
- **Resource** R1, R2, R4. **Invariant** the class (`t` fixed), varying `(a,b)`, `j`.
- **Functional** Semaev/Gröbner solving degree, first-fall degree, relation
  yield, factor-base decomposition probability, Macaulay rank profile.
- **Decisive test** enumerate a whole toy isogeny class; measure `C(E)` on every
  curve in it; compare within-class variance against between-class variance and
  against a matched random-curve null of the same `p`. Zero within-class variance
  closes the axis for that `C`, with an obstruction, which is a result.
- **Obstruction to beat** none yet; this lane produces the obstruction or the target.
- **This is the campaign's gating lane.** L2, L3, L11 are conditional on it.

### L2 — Volcano level and endomorphism-ring depth · `RQ-VOLC-f6253b`
- **Resource** R3, R4. **Invariant** `End(E)` conductor, varying inside the class.
- **Functional** does depth change *anything* measurable — relation yield,
  solving degree, walk mixing, torsion splitting?
- **Decisive test** build the `ell`-volcano for small `ell | f`, classify each
  curve's level by counting rational `ell`-isogenies, and stratify every L1
  measurement by level.
- **Obstruction to beat** on `G` the level is invisible (all `phi` are scalars),
  so any effect must be routed through R1/R2/R5.

### L3 — j-invariant special values and CM discriminant size · `RQ-JINV-8fc13a`
- **Resource** R2, R3. **Invariant** `j = 0`, `j = 1728`, small `|D_0|`, small
  height `j`, `j` a root of a low-degree Hilbert class polynomial.
- **Functional** everything in L1, plus the automorphism-quotient rho constant.
- **Decisive test** compare curves with `|D_0| in {3,4,7,8,11,...}` against
  generic-`D_0` curves at matched `p` and matched `N`; and, separately, check
  whether small-`|D_0|` classes are *distinguishable* by any cost functional at
  all beyond the known `sqrt(|Aut|)` constant.
- **Obstruction to beat** `KN-TECH-018`: the automorphism discount is a constant
  `<= sqrt(6)`, never an exponent. Any claim here must exceed that or be labelled
  as baseline calibration.

### L4 — phi-equivariant relation collection · `RQ-EQIC-8cb959`
- **Resource** R1, R2, R3. **Invariant** a `phi`-stable factor base.
- **Functional** summation-polynomial degree, system size, solving degree,
  relations per unit time.
- **Decisive test** `phi`-orbit factor bases versus size-matched random factor
  bases on the *same* curve — the only comparison that isolates equivariance from
  factor-base size.
- **Obstruction to beat** `H-STR-002` is `weakened` (`DEC-20260727-009`) and its
  replication obligation `DEFER-BATCH009-001` is **open**. This lane must not
  re-assert `H-STR-002`; it may only test mechanisms the weaken did not touch,
  and must say which.

### L5 — phi-equivariant sparse linear algebra · `RQ-EQLA-0d3f40`
- **Resource** R1, R3. **Invariant** the relation matrix as a `Z[phi]`-module.
- **Functional** cost of the linear-algebra stage: displacement rank, block
  structure, Wiedemann/Lanczos iteration count.
- **Decisive test** measure displacement rank and block-circulant structure of
  relation matrices from `phi`-stable bases against random-permutation nulls.
- **Obstruction to beat** `EV-STR-001` recorded the failure of the earlier
  arithmetic-progression variant; the null control is mandatory and blocking.

### L6 — endomorphism-accelerated walks · `RQ-EWALK-8fa147`
- **Resource** R3 only — so this lane is **on the wrong side of the admissibility
  filter by construction** and is opened to measure the ceiling precisely.
- **Functional** rho step count on `E / Aut`, fruitless-cycle rate, GLV-split walks.
- **Decisive test** measured speedup versus the predicted `sqrt(|Aut|)`; any
  excess is either an instrument artifact or the one interesting event in the lane.
- **Obstruction to beat** Shoup + `KN-FIND-b7e091`. Expected outcome: constant
  factor only. Recorded as baseline calibration.

### L7 — torsion at `ell != N` as a Galois/End module · `RQ-TORS-8c7b79`
- **Resource** R5. **Invariant** `E[ell]` as a `Gal x End` module; division
  polynomial factorisation patterns; Elkies/Atkin prime behaviour.
- **Functional** does any `ell`-torsion statistic correlate with `k`, or with the
  cost of any stage? Does the Elkies/Atkin split pattern of the class carry
  usable structure?
- **Decisive test** the correlation must be measured against a null where `k` is
  resampled with the curve fixed — the canonical artifact control.
- **Obstruction to beat** `k` is information about a point, not about the curve;
  any curve-only statistic is `k`-independent by construction. The lane's real
  question is whether *point*-dependent torsion data is publicly computable.

### L8 — pairings and embedding degree under CM structure · `RQ-PAIR-21313f`
- **Resource** R7. **Invariant** embedding degree `k_emb`, distortion maps,
  self-pairings on CM curves.
- **Functional** cost of transfer to `F_{p^{k_emb}}` plus index calculus there.
- **Decisive test** `k_emb` is class-determined and generically `~N`; the lane is
  a *scoping* lane — which CM families have small `k_emb`, and is any standard
  curve near them?
- **Obstruction to beat** MOV/Frey-Rück is classical; nothing here is novel unless
  a CM-specific self-pairing computable without a second independent point exists.

### L9 — canonical lifts and CM lifting · `RQ-CANL-63098f`
- **Resource** R6, R3. **Invariant** Serre-Tate canonical lift; CM points;
  Hilbert class polynomial; heights on the lifted curve.
- **Functional** the Xedni-style question, re-asked with CM constraints:
  does the CM structure of the canonical lift constrain the lifted points enough
  to make height/regulator arguments bite?
- **Decisive test** measure the canonical height growth of lifted points against
  the Silverman-Xedni failure mechanism, which is *quantified*, not vague.
- **Obstruction to beat** Jacobson-Koblitz-Silverman-Stein-Teske: Xedni fails
  because lifted points have height `~N`. Any lane variant must state how CM
  changes that specific quantity or it is closed on arrival.

### L10 — class group action and ideal structure · `RQ-CLGP-b99df5`
- **Resource** R3, R4. **Invariant** `Cl(O)` acting simply transitively on the crater.
- **Functional** is there any *reduction* between the `Cl(O)`-vectorization
  problem and ECDLP on the same class, in either direction?
- **Decisive test** an explicit attempted reduction with quantifier order stated;
  a failed reduction with a named obstruction is the expected and useful outcome.
- **Obstruction to beat** the two problems live on different objects (curves vs.
  points). A reduction must produce the bridge map explicitly.

### L11 — curve models and representation change · `RQ-MODEL-e61cb2`
- **Resource** R1, R2. **Invariant** Weierstrass / Montgomery / Edwards /
  Hessian / Jacobi-quartic / theta / Kummer models of the *same* curve.
- **Functional** summation-polynomial degree and solving degree as a function of
  the model — a strictly finer question than L1, because the model changes with
  the curve fixed.
- **Decisive test** same curve, same points, same factor base, five models,
  identical measurement.
- **Obstruction to beat** Diem's and Gaudry's degree bounds are model-agnostic in
  their asymptotic form; the lane targets constants and small-`m` behaviour and
  must not claim an exponent.

### L12 — the generic-group boundary for structured curves · `RQ-GGMB-6eaabc`
- **Resource** none — this lane *audits* resources. **Invariant** simulability.
- **Functional** for each oracle a lane proposes, is it GGM-simulable?
- **Decisive test** an explicit simulator, or an explicit proof that none exists.
- **Purpose** this is the campaign's internal falsifier: it extends
  `KN-FIND-b7e091` to the *new* oracle classes the other lanes invent, and it is
  cheaper than running any of them.

### L13 — multi-target and preprocessing inside one isogeny class · `RQ-MTGT-2cabee`
- **Resource** R8, R4. **Invariant** many targets share one class and one `N`.
- **Functional** amortised cost per target; whether preprocessing on *one* curve
  in the class transfers to the others by transport (T1).
- **Decisive test** does a table built on `E` retain value on `E'` after
  transport, or does transport destroy it? This is a sharp, cheap question.
- **Obstruction to beat** Bernstein-Lange / Mihailescu preprocessing bounds and
  the AT^2 lower bounds; any claim must be charged in the full-cost model.

### L14 — instrumentation, null objects, certificates · `RQ-INSTR-f8faa0`
- **Resource** none. **Purpose** every measured quantity in L1–L13 needs a null
  object of the same shape and a decay test (`docs/inventor-protocol.md`,
  "controls before belief"), plus a certificate re-verified independently of the
  solver (`docs/claims-and-verification.md`).
- **Decisive test** the instrument must fail to detect a signal in a matched
  random object, and must detect a *planted* signal — both directions.
- **Purpose** this lane is what makes the others' negatives citable.

## 5. What this decomposition predicts, stated before any measurement

Recorded here so it cannot be tuned afterwards:

1. **L1 is expected to show small but non-zero within-class variance** in the
   Gröbner-basis proxies, dominated by instance noise, and **zero** variance in
   relation *yield* (which depends on `N` and factor-base size only). **[open]**
2. **L2 is expected to show no effect** stratified by volcano level. **[open]**
3. **L6 is expected to reproduce `sqrt(|Aut|)` and nothing more.** **[open]**
4. **L12 is expected to close several of the oracles L4/L5/L7 invent**, cheaply,
   before they are run. This is the intended use of the lane. **[open]**
5. **The campaign's most likely genuine deliverable is a negative with a named
   obstruction in L1** — "the cost functionals this program measures are
   isogeny-class invariants" — which, if it holds, is a *stronger* and more
   citable statement than the fatigue-report closures the inventor protocol
   forbids.

If instead L1 shows large, structured within-class variance that survives its
null, the campaign's centre of gravity moves to the reachability gate T5, and
the next question is whether goodness is locally detectable.

## 6. Scope and honesty statement

Everything in this campaign runs at **toy scale** (`p` up to ~32 bits) unless a
later contract says otherwise, and every resulting evidence record is capped at
`claim_tier: toy`. No lane here is claimed to threaten any deployed curve. The
transport theorem T1 is elementary and is the only mathematical claim this
document asserts without qualification; T5 rests on GRH-conditional rapid mixing
of the class-group Cayley graph and is cited, not proved, here.

`dominated_by`: as an attack, every lane in this campaign is currently dominated
by parallel Pollard rho with distinguished points at `0.886 sqrt(N)` group
operations and `O(1)` memory (`KN-TECH-001`, `KN-TECH-006`), and by the
automorphism-discounted variant on CM curves (`KN-TECH-018`). `sota_delta`:
zero. No lane has produced any speedup and none is claimed.
