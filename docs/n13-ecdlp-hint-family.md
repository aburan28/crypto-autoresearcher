# An n^{1/3} ECDLP algorithm, theorized

**From Koblitz–Menezes §3.2 to a hint family, and to the three experiments
that would falsify it cheaply.**

---

## 0. Status, and what this is not

This is a **speculative design note**, written 2026-09-20 in response to a
direct user request to theorize Koblitz and Menezes's §3.2 question into an
algorithm. It is analysis, not evidence.

- It records **no** run, measurement, timing, or statistic. Nothing here is
  cited as evidence by anything, and it asserts no claim tier
  (`docs/claims-and-verification.md`).
- It changes **no** hypothesis status and approves **no** experiment. Turning
  §10 into ledger records is a separate Coordinator act via `/propose-ideas`
  and `/design-experiment`.
- It makes **no** claim about what any intelligence agency does or does not
  know. Koblitz and Menezes's §3.2 is a speculation *about a possibility*, and
  it is treated here strictly as a well-posed mathematical question: *what
  would such an algorithm have to look like?* The answer below is largely a
  set of **constraints and no-go arguments**, which is the useful part.
- Two of the four routes in §8 are argued dead in a paragraph each. Under
  `docs/inventor-protocol.md` that is a success condition, not a failure: a
  cheap pre-compute falsification that kills a branch before it is funded.

## 1. The source question

Koblitz and Menezes, *A Riddle Wrapped in an Enigma* (ePrint 2015/1018), §3.2:

> Does the NSA have an n^{1/3}-algorithm for finding elliptic curve discrete
> logs? … at Asiacrypt 2013 Bernstein and Lange presented an n^{1/3}-algorithm.
> However, it needed a tremendous amount of precomputation, taking time n^{2/3}.
> So from a practical standpoint, as Bernstein and Lange pointed out, it is
> worthless. However, it is conceivable that [one could find] a similar
> algorithm that requires far less precomputation.

The last sentence is the whole problem, and it is sharper than it looks. The
n^{1/3} is not the hard part — it is already achieved. **The hard part is
`far less precomputation`,** and §§2–6 below show that this single phrase
forces the algorithm into one very specific shape.

Corpus pointers: `knowledge/literature/KN-LIT-5230.md` (Bernstein–Lange,
*Non-uniform cracks in the concrete: the power of free precomputation*),
`knowledge/literature/KN-LIT-013.md` (Corrigan-Gibbs–Kogan, *The
Discrete-Logarithm Problem with Preprocessing*, 2018).

## 2. The known algorithm, and its exact cost identity

Let `E/F_p` have prime order `n ≈ p`, generator `g`. Write `S` for advice
entries stored, `T` for online group operations, `P` for precomputation
operations.

The Mihalcik / Lee–Cheon–Hong / Bernstein–Lange construction:

1. **Precomputation.** Run pseudorandom walks from known-log starting points,
   `P` steps in total. They cover a *trail set* `C ⊆ ⟨g⟩` with `|C| ≈ P`.
   Store only the `S` distinguished endpoints, each with its known log.
2. **Online.** Walk from `h·g^a` (offset `a` known). Each step lands in `C`
   with probability `|C|/n`. Once inside `C`, the walk is deterministic and
   runs to a stored endpoint, whose log is known, yielding `log_g h`.

Success after `T` steps is `≈ T·P/n`, so `Θ(1)` success requires

> **`P · T = n`**,  and with mean trail length `≈ T`,  `S ≈ P/T`, hence
> **`S · T² = n`**.

Corrigan-Gibbs and Kogan proved `ST² = Ω(n)` is also a **lower bound in the
generic group model**, so the online tradeoff is tight and nothing about it
can be improved. The balanced point `S = T = n^{1/3}`, `P = n^{2/3}` is where
the "n^{1/3}-algorithm" phrase comes from.

The identity to keep is the *first* one, `P·T = n`, because it is the one
Koblitz and Menezes's question asks you to break.

## 3. The P-256 audit: why the known family is worthless here

`n ≈ 2^256`.

| operating point | `S` (entries) | `T` (online) | `P` (precomp) |
|---|---|---|---|
| balanced `n^{1/3}` | `2^85.3` | `2^85.3` | `2^170.7` |
| 1 PB table (`2^45` entries) | `2^45` | `2^105.5` | `2^150.5` |
| Pollard rho (no table) | `O(1)` | `2^128` | `0` |

Two independent walls, either of which alone is fatal:

- **Storage.** `2^85.3` entries at ≥32 bytes is `≈1.6 × 10^27` bytes. Global
  installed storage is on the order of `10^23` bytes. The balanced table is
  roughly **four orders of magnitude larger than all storage ever
  manufactured.** The online-optimal point is not merely expensive; it is not
  a physical object.
- **Precomputation, and it is structural, not incidental.** From `P·T = n`:

  > `T < √n  ⟺  P > √n`.

  **Preprocessing of this kind can never lower total cost below the rho
  bound.** It only *relocates* cost off the online path. For a single target
  — and P-256 is one curve with one target at a time — the relocation buys
  nothing. That is exactly Bernstein and Lange's own "worthless," now stated
  as an identity rather than an observation.

## 4. What must therefore be true

Take the two walls seriously and the design space collapses:

- The storage wall makes **`S = O(polylog n)`** the only physically realizable
  regime — no table at all.
- The `P·T = n` identity makes a large `P` *useless* for a single target rather
  than impossible: by §3 it never lowers total cost, so a preprocessing-based
  algorithm worth having must have **`P = O(polylog n)`**.
- The requirement is still **`T ≈ n^{1/3}`**.

**This is a design argument, not a theorem** (corrected 2026-09-20; see §13).
In particular it does **not** follow from Corrigan-Gibbs–Kogan: their model
gives the preprocessor unbounded power and charges only `(S, T)`, so in that
model `P` is not a resource at all and nothing forces it small. §12 S1 names
the model in which the corresponding theorem does hold.

So the object being speculated about is not a better *table*. With `S` and `P`
both degenerate, the advice stops being data and becomes a **decision
procedure**: something that can recognize a useful point, and invert it, from
the point's coordinates alone, with no memory of ever having seen it.

That is a single, nameable mathematical object.

## 5. The object, and the algorithm

> **Definition (hint family).** An **`(α, c)`-hint family** for `(E/F_p, g)` is
> a triple `(D, χ, ω)`:
> - `D ⊆ ⟨g⟩` with `|D| ≥ n^α`  — *density*;
> - `χ : E(F_p) → {0,1}` deciding `Q ∈ D` in time `c` from the affine
>   coordinates of `Q`  — *recognizability*;
> - `ω : D → Z/nZ` with `g^{ω(Q)} = Q`, computable in time `c` from the
>   coordinates of `Q`  — *invertibility*.

```
HINTWALK(h ; hint family (D, χ, ω) of density n^{α-1})
 1  a ←$ Z/nZ ;  X ← h · g^a                  # X = g^{x+a}, offset a known
 2  loop:
 3      if χ(X):  return ω(X) − a  mod n      # done
 4      s ← step(X)                           # r-adding walk, s known
 5      X ← X · g^s ;  a ← a + s  mod n
 6      every L steps: a ←$ Z/nZ ; X ← h·g^a  # escape short cycles
```

**Cost.** Each step lands in `D` with probability `|D|/n = n^{α-1}`, so the
expected iteration count is `n^{1-α}`.

> **`HINTWALK` runs in `n^{1-α}·(c + O(1))` group operations, with `O(1)`
> storage and zero precomputation.**
>
> At `α = 2/3` that is **`n^{1/3}` online, no table, no preprocessing** —
> strictly stronger than Bernstein–Lange, and exactly the object §3.2
> speculates about.

The tradeoff is continuous and the exponent is a dial: `α = 1/2` gives
`n^{1/2}` (rho, no gain), `α = 2/3` gives `n^{1/3}`, `α = 3/4` gives `n^{1/4}`.
The algorithm is trivial. **Everything hard has been pushed into the existence
of `(D, χ, ω)`, which is the point of writing it this way.**

## 6. The generic no-go — a hint family is a certificate of non-genericity

Apply Corrigan-Gibbs–Kogan to `HINTWALK` itself. A hint family of size `O(1)`
to describe is `O(1)` bits of advice, so `S = O(polylog)` and the lower bound
gives `T = Ω(√(n/S)) = Ω(n^{1/2 - o(1)})`.

> **No `(2/3, polylog)` hint family exists for a generic group.** In the
> generic group model there are no coordinates for `χ` and `ω` to read.

This is not an obstruction to the program; it is the program's *specification*.
It says the non-genericity of `E(F_p)` is not a side condition of such an
algorithm — it is the entire content of it. Equivalently:

> **Exhibiting a `(2/3, polylog)` hint family is exactly exhibiting a
> quantitative failure of the generic-group model for `E(F_p)`,** and any
> algorithm meeting §3.2's specification is an index-calculus-type algorithm
> in disguise, whether or not it is presented as one.

That reframing is worth more than the algorithm. It converts an open-ended
"is there a better attack" into a measurable question about the curve
(§10, Experiment A).

## 7. The duality: why `P·T = n` is forced, and where the escape would be

Two subsets of `⟨g⟩` of size exactly `n^{2/3}` are available for free. For
P-256, `n^{2/3} = 2^170.7`:

- **`D_x` = `{Q : x(Q) < p^{2/3}}`** — "the x-coordinate has its top 85 bits
  zero."
  `χ` is a single comparison. ✔ dense ✔ recognizable ✘ **no known `ω`**.
- **`D_w` = `{g^k : k has low Hamming weight}`** (weight `w` with
  `C(256,w) ≈ 2^170`, i.e. `w ≈ 34`).
  `ω` is free — you generated `k` yourself. ✔ dense ✔ invertible
  ✘ **no known `χ`**: deciding membership is itself a discrete-log problem.

> **The duality.** Every natural candidate set is recognizable-but-not-
> invertible, or invertible-but-not-recognizable. A hint family needs one set
> that is **natively both**.

This also *re-derives* `P·T = n` and shows it is not an artifact of the walk
construction. Bernstein–Lange's precomputation is precisely the operation
"enumerate an invertible set and filter it down to a recognizable one":
generate points of known log (`D_w`-like), keep those satisfying the
distinguished-point predicate (`D_x`-like). The cost of that filtering is the
size of the invertible set you must enumerate, `n/T`. Hence `P ≥ n/T`, for
*any* construction of this shape.

> **So there is exactly one escape.** Not a cheaper filter — a set that is
> dense, recognizable, and invertible **without being filtered into
> existence.** Every route in §8 is an attempt to produce one.

And the reduction becomes a single sentence, which is the most useful
sentence in this note:

> **Given `Q ∈ E(F_p)` promised to satisfy `x(Q) < p^{2/3}`, can `log_g Q` be
> computed in time `≪ p^{1/3}`?**
>
> An affirmative answer yields an `n^{1/3}`, zero-storage, zero-precomputation
> ECDLP algorithm by §5. This is *not* circular: the input carries a promise,
> the budget is `n^{1/3}` rather than `O(1)`, and by §6 the solver is
> permitted — in fact required — to read coordinates.

## 8. Four routes to `ω`, and their ceilings

### Route 1 — index calculus with a small-x factor base. **Open; already the program's front line.**

Relax `ω` to allow a per-curve preprocessing that computes logs of a factor
base `F = {Q : x(Q) < B}` and a descent rewriting any `Q ∈ D_x` over `F`.
This is the Logjam shape: pay once per modulus, then individual logs are cheap
— and note that for `F_p^*` this is not speculation but deployed reality.

The bottleneck is unchanged from where it has always been: relation search
requires solving Semaev's summation polynomial `S_{m+1}(x_1,…,x_m, x(R)) = 0`
with every `x_i` confined to `[0,B)`. Over prime fields there is no Weil
restriction to turn that confinement into algebraic structure; `x_i < B` is a
*size* condition, and Gröbner methods do not see size conditions. The tools
that do see them (lattice reduction, Coppersmith) face a system whose
dimension grows faster than the gain.

**Status: genuinely open, no algorithm beating box-exhaustion is known.** This
is where the program already works — areas `DREG`, `SDEG`, `SIG`, `MONO`,
`RELN`, `ICEX`, `ICLIFT`, `SEMBIN`, `ICPERF`. The contribution of this note to
Route 1 is only the reframing: *those areas are the search for `ω`,* and §5
tells you the exponent any success there would purchase.

### Route 2 — lifting to a global object (xedni). **Dead, and instructively so.**

Give `E` a height filtration by lifting points to a curve over `Q`, where the
canonical height orders points and small-height points satisfy relations.
Silverman's xedni calculus did exactly this; Jacobson, Koblitz, Silverman,
Stein and Teske showed it is no better than brute force.

State the failure in §7's vocabulary and it becomes predictive rather than
anecdotal: **reduction mod `p` is a lossy projection that destroys height.**
Nothing in the mod-`p` coordinates of `Q` distinguishes a reduction of a
small-height global point from any other point, and the expected number of
bounded-height lifts of a random `Q` is `O(1)`. So global points give a set
that is invertible but **not recognizable** — the `D_w` side of the duality,
reached by a longer road. Route 2 is not a new idea that failed; it is §7's
right-hand column.

### Route 3 — generic search plus endomorphisms. **Blocked by the missing coordinates-to-exponent dictionary.**

GLV/GLS and Q-curve decompositions write the scalar over a rank-`d` lattice
with short vectors of norm `n^{1/d}`, which looks like it should shorten the
search. It does not, and the reason generalizes:

It is tempting to argue that Wagner's k-tree attains `2^{b/3}` on 4-sums only
because `b`-bit strings admit a **homomorphic** projection onto their low
`b/3` bits, and that `⟨g⟩`, having prime order, admits no nontrivial
homomorphism onto anything smaller — so there is no partial match to merge on.

**That argument is wrong** (corrected 2026-09-20; see §13). Wagner's algorithm
runs on modular k-SUM in `Z_N` for arbitrary `N`, primes included. The merge
matches on an *interval* of representatives rather than on a subgroup, and
interval membership is not a homomorphism — it is a set-valued rule with
bounded branching (a single `−N` correction). **A merge consumes bounded
branching, not a homomorphism.** Prime order forbids nothing here.

The real obstruction is the one §7 and §12 S3 already name. A k-tree merge
needs its partial-match predicate computable **from the data the algorithm
actually holds**. In k-SUM over `Z_N` that data is the summands themselves, so
the interval test is free. In DLP the intermediate objects are *group
elements*, the target `log_g h` is unknown, and the filtration that would
support partial matching lives in the exponent — precisely what cannot be read
off a point. The family is blocked by the missing coordinates-to-exponent
dictionary, not by prime order.

What survives: any algorithm restricted to forming group elements and testing
equality is under Shoup's `√n`, improved by at most `√|Aut|`
(Gallant–Lambert–Vanstone; Duursma–Gaudry–Morain) — a constant. What does
**not** survive is the claim that this is a one-line kill of the whole
generalized-birthday-on-a-curve family. The live question is quantitative —
how much branching a coordinate projection may carry before the merge stops
paying — and it belongs to `RQ-ECDLP-160d89`.

It also yields a sanity check that the §5–§7 framework is not vacuous. On a
`j = 0` curve the automorphism acts as `(x,y) ↦ (βx, y)`, so `D_x` is not
preserved but `⋃_i β^i·[0,B)` is: three intervals instead of one — a factor-3
density gain, i.e. the known `√3`-ish speedup of rho on `j = 0` curves, and
nothing more. The framework reproduces the known constant and does not
hallucinate an exponent.

### Route 4 — the isogeny class as free representation multiplicity. **Dead by its own arithmetic, and the argument is reusable.**

This is the one genuinely non-generic resource the curve has that §8's other
routes do not use, and it deserved a real look.

An `ℓ`-isogeny `φ : E → E'` is a group homomorphism; `n` is prime and `ℓ ≪ n`,
so `φ` restricts to an **isomorphism** `⟨g⟩ → ⟨φ(g)⟩` and
`log_{φ(g)} φ(h) = log_g h`. The instance is invariant across the isogeny
class while the coordinates change completely, and small-`ℓ` steps cost
`Õ(ℓ)`. For ordinary `E` the class holds `h(O) ≈ √p ≈ n^{1/2}` curves. So
`HINTWALK` could walk in two directions — along `⟨g⟩`, and across the graph —
over `≈ n^{3/2}` distinct `(curve, point)` encodings of one instance.

**It buys nothing, and here is why.** A budget of `T` steps visits `T` pairs,
whichever direction each step moves. Success needs the invertible set to have
density `≥ 1/T` *in whatever space you are sampling*. Enlarging the space from
`n` pairs to `n^{3/2}` pairs enlarges numerator and denominator together:

> **Representation multiplicity is not a resource unless it changes density.**

The corollary needs restating; the version first written here was wrong
(corrected 2026-09-20; see §13). Locating a "special" curve inside the class
does **not** cost `√p / #special` — `j`-invariants are read for free, so
location costs nothing. The correct obstruction is stronger, and is an
*invariance* statement rather than a density one: **every exploitable
specialness is a class invariant.** All curves in an ordinary isogeny class
share the Frobenius order, hence the endomorphism algebra, hence `|Aut| = 2`
unless the discriminant is `−3` or `−4`, hence the group order and the
embedding degree. The extra automorphisms behind the `j = 0` factor-3 gain are
a property of the *class*, decided at zero cost from the starting curve, and
absent from a random curve's class; walking the graph cannot manufacture them.
What genuinely varies within a class is the `j`-invariant and the curve model,
and whether either changes a charged stage cost is a measurement, not a
corollary.

Transfer is pointless in both directions regardless: an online point on any `E'`
can be pulled back to `E` through the chain at polylog cost, so **the class
offers no new instances, only new coordinates, and you may as well stay on
`E`.**

This also disposes of a tempting accounting claim — that Bernstein–Lange
preprocessing is a *class-level* cost amortizable over `h(O)` curves. It is
not usable amortization: the stored distinguished points push through `φ` with
their logs intact, but the distinguished-point *predicate* is defined on
coordinates and does not transfer, so the trail structure is lost and the
online cost degrades from `n/(ST)` to `n/S`. Pulling back to `E` recovers it
and returns you to one curve. There is only ever one curve.

## 9. Two cautions

- **The two `1/3`s are unrelated.** The `1/3` in `L[1/3]` (NFS, subexponential)
  and the `1/3` in `n^{1/3}` (polynomial, this note) are different exponents in
  different scales. Route 1's Logjam analogy is an analogy of *shape* —
  per-modulus precomputation then cheap individual logs — not of exponent. Do
  not let the numeral do argumentative work.
- **`T = n^{1/3}` is still `2^85` for P-256.** Even total success here leaves
  P-256 standing: `2^85` operations is beyond reach, and the practical
  consequence would be a **security-margin** result (P-256 at ~85 bits rather
  than ~128), not a break. This is the honest framing for any deliverable, and
  it is what `docs/target-result-profile.md` asks for: an exponent-moving
  result on a central hard problem, stated conditionally, costed honestly, and
  **not** dressed up as a break.

## 10. Cheapest falsification first

Under `docs/inventor-protocol.md` these are pre-compute falsification checks,
ordered by cost. A failed audit is a useful result. None of them is approved;
they are candidates for `/propose-ideas` → `/design-experiment`.

### Experiment A — measure the non-genericity of `E(F_p)` directly

§6 says a hint family *is* a quantitative failure of the generic-group model.
That is measurable at toy scale, cheaply, and it is decisive in one direction.

- **Object.** Toy ordinary prime-field curves, `n ≈ 2^20 … 2^32`, full
  enumeration of `⟨g⟩` with known logs.
- **Measure.** Mutual information between `log_g Q` and efficiently computable
  coordinate statistics of `Q`: bit patterns and leading-zero counts of `x`,
  `x mod` small primes, Hamming weight of `x`, Legendre symbols of `x + c`,
  and any learned low-degree function of the coordinate bits.
- **Null object (mandatory).** A random relabelling of the same cyclic group —
  which is literally a generic group — at matched `n`.
- **Symmetries that must be quotiented out first, or they will be
  "discovered".** `x(−Q) = x(Q)` (the standard `±` folding behind rho's `√2`);
  the `β`-orbit structure on `j = 0` and `j = 1728` curves (§8, Route 3).
- **Prediction if ECDLP behaves generically.** MI indistinguishable from null
  at every `n`, with no growth in `n`. **Any statistic whose MI grows with `n`
  is the crack,** and §5 converts a density-`n^{α-1}` signal directly into a
  `T = n^{1-α}` algorithm.
- **Why it is worth running even though it will probably return null.** It is
  `O(n)` at toy scale, it returns a *number over a stated scope* rather than a
  verdict, and that number is the reusable content (`obstruction` /
  `resource_check` in `templates/research-records.md`). It also bounds how much
  of §8 Route 1's difficulty is intrinsic.

### Experiment B — the promised-input DLP, measured as a curve

Fix the §7 reduction and measure it as a function of the promise, rather than
arguing about it: for a toy curve, sample `Q` with `x(Q) < p^{β}` for
`β ∈ {1, 0.9, …, 0.5}`, and measure the *best achievable* cost of `log_g Q`
under each solver the program already has (rho baseline, small-x factor-base
index calculus from the `ICPERF` library).

- **What it decides.** Whether the promise `x(Q) < p^{2/3}` is worth *anything*
  — whether the measured cost curve bends at all as `β` falls. A flat curve is
  a clean negative that retires §7's reduction as a practical route while
  leaving the framing intact.
- **Charge the promise honestly.** Sampling `Q` with small `x` is free
  (pick `x`, solve for `y`), so there is no hidden cost to launder.

### Experiment C — the isogeny-density control

§8 Route 4 is argued dead on paper. Density arguments made on paper are
exactly the kind that hide a factor, so the control is cheap insurance: on a
toy curve with a small isogeny class, pool coordinate statistics across the
whole class and re-run Experiment A's MI measurement on the pooled
`(curve, point)` space against the same null.

- **Prediction from §8.** Zero MI beyond null, at every `ℓ` and every class
  size — the class adds encodings, not information.
- **Value if confirmed.** The density argument becomes a measured obstruction
  with a scope, reusable against every future "more representations" proposal,
  of which this program will see many.

## 11. What would count as progress

Ordered by strength, and none of it is claimed here:

1. **Experiment A returns a statistic with `n`-growing MI.** Highest value in
   the note; converts directly into an exponent by §5.
2. **Experiment B's cost curve bends with `β`.** Evidence that the small-x
   promise is a real resource; feeds Route 1 directly.
3. **A measured obstruction from A, B or C.** The expected outcome, and still
   worth the budget: recorded as a *quantity over a stated scope*, it prices
   the `n^{1/3}` question for every future reranking instead of leaving it as
   folklore.
4. **§6 and §7 written up as they stand.** The reduction of §3.2 to
   "dense + recognizable + invertible", the proof that the generic model
   forbids it, and the duality argument that forces `P·T = n` for every
   filter-based construction, are stateable results about *what such an
   algorithm must be*. They claim nothing about whether it exists.

## 12. Open statements

- **S1.** *(restated 2026-09-20; see §13.)* As first posed — "is `P·T = Ω(n)`
  provable in the generic group model?" — the question is malformed, because
  it names no preprocessing model. In Corrigan-Gibbs–Kogan's **non-uniform**
  model the preprocessor is unbounded and `P` is not charged at all, so
  `P·T = Ω(n)` is **false** there. The well-posed form is: **in a
  query-bounded preprocessing model**, where phase 1 makes at most `P` group
  queries, is `P·T = Ω(n)`? That version looks provable by a lazy-sampling
  argument and would make §4's collapse rigorous. Naming the model is not a
  technicality: §4's design argument and this theorem live in different
  models, and any record in this lane must say which one it means.
- **S2.** Is there any subset of `E(F_p)` of density `n^{-1/3}` that is
  natively both recognizable and invertible — §7's escape — or is the duality
  itself provable?
- **S3.** *(restated 2026-09-20; see §13.)* As first posed — "does prime-order
  `E(F_p)` admit *any* group-compatible size function?" — this has a trivial
  affirmative answer and is the wrong question: the word metric with respect
  to any generating set `S` is group-compatible, so such a function always
  exists. The sharp form is about **descent**, not existence: is there a
  generating set `S` and an efficiently computable map sending `Q` to a short
  `S`-word for `Q`, beating the meet-in-the-middle cost `|S|^{L/2}`? Counting
  kills the *search* route for every generating set at once — non-negligible
  density of elements of word length `≤ L` forces `|S|^L ≈ n`, hence `n^{1/2}`,
  with no design freedom. So index calculus does **not** work in `F_p^*`
  because a size function exists there; the same count gives `n^{1/2}` there
  too. It works because `Z` carries an **algebraic** descent — integer
  factorization — that bypasses search entirely. S3 therefore reduces to: *is
  there an algebraic descent on `E(F_p)`?*, which routes into `KN-OPEN-020`'s
  three open classes and into §8 Route 1.

---

## 13. Corrections, 2026-09-20

This note was merged in #1293 and then adversarially reviewed during ideation
against `RQ-ECDLP-bc7a54`. The review found four defects. They are corrected
in place above, each marked at the point of correction, and recorded here so
the change is visible rather than silent. **Three of the four are errors in
arguments this note asserted; every affected conclusion survives, but two of
them survive for different reasons than the ones originally given, and one
"one-line kill" is downgraded to an open quantitative question.**

1. **§8 Route 3 — the homomorphism ceiling was an invalid argument.** Wagner's
   k-tree runs on modular k-SUM in `Z_N` for arbitrary `N`, primes included,
   matching on intervals rather than subgroups; a merge consumes bounded
   branching, not a homomorphism. Prime order forbids nothing. The conclusion
   (no generalized-birthday speedup on a curve) still holds, but because the
   partial-match predicate must be computable from the data held — group
   elements — while the filtration lives in the unreadable exponent. The
   claim that this kills the family "in one line" is withdrawn; the live
   question is how much branching a coordinate projection may carry, and it
   belongs to `RQ-ECDLP-160d89`.

2. **§12 S1 was malformed.** It asked for `P·T = Ω(n)` "in the generic group
   model" without naming a preprocessing model. In the non-uniform model of
   `KN-LIT-013` the preprocessor is unbounded and `P` is uncharged, so the
   statement is false there. Restated for a query-bounded model.

3. **§4 overstated a design argument as a theorem.** "The two walls force
   `S = P = O(polylog)`" does not follow from `KN-LIT-013`. Large `P` is
   *useless* for a single target, by §3 — not impossible. Note that
   `RQ-ECDLP-bc7a54`'s `motivation` reproduces the original inference; as an
   immutable ledger record it is not edited here, and correcting it is a
   separate Coordinator act under AGENTS.md rule 2 (corrections supersede,
   never overwrite).

4. **§8 Route 4's corollary was wrong.** Locating a "special" curve does not
   cost `√p / #special`, because `j`-invariants are free to read. Replaced by
   the stronger and correct statement that every exploitable specialness is a
   *class invariant*. The density no-go itself — *representation multiplicity
   is not a resource unless it changes density* — is unaffected.

One further caution, not a correction but a scoping limit on §10 Experiment B:
enumerating the promise class `{Q : x(Q) < p^β}` is free but yields **points,
not logs**, so a `β`-sweep run without naming which mechanism it tests —
additive structure in the log-image, or Route 1 relation yield — will produce
a flat curve and a null that discriminates nothing. If run, it should be run
as the Route 1 arm against the `ICPERF` instrument.
