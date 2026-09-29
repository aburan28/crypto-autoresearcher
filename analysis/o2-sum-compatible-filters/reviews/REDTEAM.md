# Red Team pass on the (O2) line — `RT-20260803-be45a8`

Independent adversarial review of the (O2) sum-compatible-filter closure for
`GOAL-ECDLP-001`.

**Snapshot reviewed:** `HEAD = 198c410a5` (clean tree for `analysis/` and
`knowledge/`). Documents: `analysis/o2-sum-compatible-filters/*` and
`knowledge/findings/KN-FIND-ffe1df.md`, with `KN-LIT-7639` and `KN-LIT-f6de4b`.

**Claim attacked.** *"No cheaply computable filter `h : E(F_p) → [M]` can be
sum-compatible often enough to drive a Wagner k-tree, for every F1 filter family
except the SHA null. Therefore the `j=2` four-tree at exponent `0.4167` — the last
exponent-moving configuration — is closed, and this route cannot beat Pollard
rho's `1/2`."*

**Verdict in one line.** The line contains three correct unconditional theorems
(Theorem 1, Theorem A as an inequality, Theorem C) and one genuine conditional
closure — but the headline is **not supported**, because the chain bounds a
*bucket-averaged* agreement rate `δ` while a Wagner level is paid at the
*single-bucket* rate `max_{c,d} π_c ≥ δ`. Bounding a lower bound on the
attacker's gain is not a barrier. Repairing that step with the machinery the line
actually has costs back exactly the factor `M` the composition removed, which
returns closure to `M ≤ p^{1/4}` and **reopens `j = 2`**.

Status of this document: **exploratory review**, `certificate.kind: none`. No
ledger record, hypothesis status, or other file is created or modified. Nothing
here is committed.

---

## 0. What I ran

Four scripts, whole-group exact enumeration in dlog coordinates, reusing the
line's own curve code (`fourier_obstruction.py`), ~6 minutes total. They live in
this session's scratchpad and are reproduced verbatim in §7 so any reviewer can
re-run them; they are **not** archived artifacts and nothing here is offered as
an evidence record.

| # | question | answer |
|---|---|---|
| RT-1 | does the closure statistic behave the same when `M` is tied to `p^{1/3}` instead of held at 4/16? | the fitted slope moves from `−0.52` to `−0.04`; the fit is noise-dominated (per-curve constant varies 18×) |
| RT-2 | is `T_t` really `M`-independent, as the additive completion needs? | **yes** — `T_max·√N ≈ 0.50` flat over `M = 4 … 256`; the completion's *conclusion* holds even though its stated *reason* is false |
| RT-3 | is family J (popcount/digit sums) inside the class the additive completion defines? | **no** — 9438 intervals per level set, `L¹ = 7.6·log p`, and `max_{t≠0}|T_t| = 0.395 = 101/√N`, a **counterexample to the theorem as stated** |
| RT-4 | does the tree's freedom to pick the target bucket beat the bound the line proves? | logically **yes** (`max_c π_c ≥ δ` always, and the available bound on it costs `M²`); empirically the excess sits at the null level at every measurable `(p,M)` |

---

## 1. Ranked vulnerabilities

### V1 — CRITICAL. The closure bounds `δ`; a Wagner level is paid at `max_{c,d} π_c`. Bounding a lower bound is not a barrier.

`O2_derivation_attempt.md` Lemma 5 is the *only* bridge from the character-sum
theorems to an attack cost. It says: cost `= L²q_c`, hits `= L²q_cπ_c`, speedup
`= M·π_c`, and then — this is the load-bearing sentence —

> *"Since `Σ_c q_c = 1` and `Σ_c q_cπ_c = δ(h,f)`, **if the `π_c` are equal** then
> `π = δ` and the speedup is exactly `M·δ`."*

Every later document bounds `δ` and nothing bounds `max_c π_c`. But `δ` is by
construction the `q_c`-weighted **average** of the `π_c`, so

```
        max_{c,d} π_c(d)   >=   delta        for every h, always.
```

The tree fixes **one** target bucket `c` and one offset `d` — that is precisely
what makes the surviving list shrink by `M` and makes the level recurse — and the
attacker chooses `(c,d)` **after** seeing `h`. So the theorems control a quantity
that lower-bounds the attacker's rate. That is a quantifier-order defect of the
kind `agents/red-team.md` §2 asks for: the construction silently chooses the
witness (the bucket) before the adversary does.

**The repair costs the factor the composition removed.** Expanding the
single-bucket rate honestly, with `1[h(P)+h(Q) ≡ s] = (1/M)Σ_t e(t(·−s)/M)`,

```
   eps_c(d) = Pr[ h(P+Q)=c  AND  h(P)+h(Q) = c-d ]
            = (1/M^2) sum_{t,u} e(...) * E[ g_t(P) g_t(Q) g_u(P+Q) ]
           <= 1/M^2 + max_{(t,u) != (0,0)} |That_{t,t,u}|,
   pi_c    ~ M * eps_c    <=  1/M + M * Lambda_W,
   speedup  = M * pi_c    <=  1  +  M^2 * Lambda_W .
```

All `M²` coefficients here have modulus 1, so there is no `ℓ²` saving — this is
**the same Cauchy–Schwarz step, in the same place, that both derivations
independently identified as the `M²` barrier**. With `Λ_W = O(D p^{-1/2})` that is
`p^{o(1)}` only for `M ≤ p^{1/4−o(1)}`. Wagner's `j = 2` needs `M ≈ p^{1/3}`.

**So the `M²` barrier was never bypassed.** `O2_composition_closure.md` §3.3
appears to escape it by switching from the level-set statistic to the
phase-encoded one — but that switch is legitimate only for the *bucket-averaged*
rate, which is not the rate a tree is charged. The composition's own summary of
its contribution, *"the single factor `M` is the entire difference between closing
`j=2` and not"*, is exactly right, and the factor comes back through the bucket.

**What would have to be true for the claim to survive.** Either (a) a proof that
`max_{c,d} π_c(d) ≤ δ + o(1/M)` for the covered classes — i.e. that no bucket is
anomalously accurate — or (b) a direct bound on the single-bucket rate that beats
`1 + M²Λ_W`. Neither exists in the line. Note (a) is a *level-set* statement, so
it is Theorem B territory, where the factor `M` is exactly what is not known to be
removable (`O2_fourier_obstruction.md` §3: *"It is not known to be tight"*).

**Measured, and reported against my own objection (RT-4).** At every parameter I
can enumerate exactly, `M·max_{c,d}π_c` is indistinguishable from the null's:

```
h                    p       M    M*delta   M*max_pi  ratio     (null: M*max_pi)
A: floor(Mx/p)    8219     20    1.01083    1.16191   1.15      1.10733
A: floor(Mx/p)   65539     40    1.00231    1.08409   1.08      1.08207
I: x mod M       65539     40    1.00299    1.08398   1.08      1.08207
P2: dlog-int     65539     40   20.00031   20.01225   1.00     (positive control)
```

The best-bucket excess is ~8% at `p = 65539, M = 40`, it is the **same for the
SHA null**, and it decays in `p` (1.15 → 1.08). So V1 is a **hole in the proof,
not a demonstrated attack**, and the narrowest valid statement is: *the `j = 2`
closure is unproved, not refuted.* That is still fatal to a record whose title
says "closed".

### V2 — HIGH. The cost clause is not merely unproven; proving it is equivalent to the goal — and the quantifier the algorithm needs is missing from the coverage table.

`KN-FIND-ffe1df` "What is NOT established" item 2 is honest and correct: the
dlog-interval pullback reaches `eps ≈ 1/2` at arbitrarily large `M` on every
prime-order group, so only a *definitional* restriction excludes it. Two things
that the record does not say and should:

1. **The gap is not closable in principle by this program.** Theorem A converts
   "no cheap sum-compatible filter" into "no cheap `h` correlating `≥ 3/M ≈ 3p^{-1/3}`
   with a dlog character" (`O2_fourier_obstruction.md` §7.2 says this). A cheap `h`
   with that property *is* a sub-rho DLP algorithm, by the very tree the line is
   excluding. So "cheap ⊆ algebraic class" is not a lemma awaiting proof; it is
   the conclusion assumed. The line should say so in those words. Note also that
   the converse hardness statement does **not** follow from any standard
   assumption: an `p^{-1/3}`-advantage distinguisher is far too weak for a
   Boneh–Venkatesan / hidden-number-problem style reduction, so "DLP is hard"
   does not imply the cost clause either.
2. **The quantifier order is wrong for a single-target problem.**
   `O2_derivation_attempt.md` §7.6 item 5 lists as *uncovered*: *"Non-uniform /
   adaptive `h`, `h` depending on the target"*. `KN-FIND-ffe1df`'s coverage table
   has **no such row**, and its headline quantifies "no cheaply computable filter
   `h`". ECDLP is posed with `Q` in hand before `h` is chosen, so the relevant
   object is `h_Q(·)` — e.g. `h_Q(P) = (⌊M x(P)/p⌋ + ⌊M x(P−Q)/p⌋) mod M`, which
   is one extra group operation and sits outside every class considered. Likewise
   the cost clause is stated per evaluation and never amortized, although one tree
   run performs `≈ p^{1/3}` evaluations, so any precomputation up to `p^{1/3}`
   is free per call. Neither is refuted; neither is addressed.

Also unaddressed and worth naming, because it is the closest object where a
"filter-like" idea *does* move the exponent: over `F_{q^n}` with prime group
order, Gaudry/Diem index calculus beats rho, and every ingredient of this line
(Weil bounds at genus 1, prime `N`, `p ≫ g²`) transfers verbatim. The line must
therefore *not* be read as constraining sub-rho list-merging attacks in general —
the successful technique in that neighbourhood is a factor-base decomposition
test, not a sum-compatible filter. The **nearby-object control is missing** and
its absence is what lets the title generalise past the theorem.

### V3 — HIGH. The composition identifies two different objects, and in the wrong direction. The document that performs the headline closure does not prove it.

`O2_composition_closure.md` §1.1 asserts:

> *"`Λ` and `max_{ψ≠1}|T̂_ψ|` are **the same object reached two ways** … This is
> the hinge of the composition."*

They are not the same object. `[F]`'s `Λ = max_{t≠0} max_ξ |ĝ_t(ξ)|` is a
**linear** Fourier coefficient against a **dlog** character; `[D]`'s `T̂_ψ` is a
**trilinear** form over the **filter-alphabet** characters. The only relation is
`|T̂_ψ| ≤ Λ` — one direction. The composition then substitutes an upper bound on
`T̂` into the slot where Theorem A needs `Λ`, which is invalid.

`O2_additive_completion.md` §1 states the non-identity explicitly —
*"Dlog characters are **not** algebraic functions on `E`, so Weil cannot bound `Λ`
directly"* — and silently repairs the chain by re-deriving `(A′)` in terms of
`T_t`. It does not record that this invalidates the composition document as
written, and the multiplicative closure (families C–G, the headline) was never
repaired. `KN-FIND-ffe1df` states Theorem A in the repaired `T_t` form while
citing the composition, so the corpus carries both versions.

The repair is one line (`eps = (1/M)Σ_t e(−td/M)T_t ⟹ eps ≤ 1/M + max_{t≠0}|T_t|`)
and the conclusion survives it. But an unrepaired hinge in the one document that
closes `j = 2` is not a bookkeeping matter, and the two quantities are numerically
far apart (§V5).

### V4 — HIGH. Family J is not closed. Here is the counterexample.

`O2_additive_completion.md` §2.1 defines the covered class as filters whose level
sets are *"a union of `O(1)` intervals of `[0,p)`"*, then §2.2 asserts

> *"`g_t(P) = e(t·h(P)/M)` is a function of `x(P)` alone, **supported on `O(1)`
> intervals**, so … `Σ_α |c_α^{(t)}| = O(log p)`."*

`g_t` is not supported on `O(1)` intervals — each *level set* is, but `g_t` takes
`M` values on `M` pieces, so the generic bound is `O(M log p)` per factor and
`O(M³(log p)³ p^{-1/2})` for `|T_t|`, which is vacuous at `M = p^{1/3}`. The class
also self-contradicts: §2.1 lists *"popcount thresholds"* as inside the class,
while §5.4 admits *"Family J's popcount at large `M` should be checked against
this"*. That check was never run. `KN-FIND-ffe1df` lists A, B, I, **J** as closed.

Measured (`p = 65539, N = 65287`, exact whole-group enumeration):

```
          filter   #intervals/level   L1(g_t)  L1/log p        Tmax  Tmax*sqrtN    M*Tmax
  A: floor(Mu/p)                  1      8.023     0.723  2.0041e-03      0.5121   0.03206
     B: mid bits                 65      9.939     0.896  1.9234e-03      0.4915   0.03077
     J: digitsum               4457     47.992     4.327  9.5915e-05      0.0245   0.00153
     J: popcount               9438     83.811     7.557  3.9479e-01    100.8730   6.31657   (M=16)
```

`max_{t≠0}|T_t| = 0.395` for popcount — **101 times the `p^{-1/2}` scale** every
other filter sits at — so the claimed `Λ = O(p^{-1/2+o(1)})` is false for a family
the record marks closed, and the naive gain bound is `7.3`, not `1+o(1)`.

**Narrowest valid conclusion, against my own objection.** The excess is entirely
the `ξ = 0` (marginal) Fourier term: removing it gives `T = 7.6e-5`
(`T·√N = 0.02`, *below* the SHA null), and `GAP = eps − δ_const = −0.18 < 0`. So
popcount is **not** an attack; it is a counterexample to the theorem *as stated*,
and it identifies the missing hypothesis — the balance / non-redundancy condition
that `[D]`'s Theorem 3 carries as **(H6)** and that the additive completion
dropped. Family J closes after adding a hypothesis, not after new mathematics.
Until it is added, the coverage row is unsupported.

Note this is the **third** time in this line that an unsubtracted `δ_const` floor
has driven a headline number (F1's `1.101×` lift; the `(★)`-ceiling comparison in
`O2_quasigroup_scaling.md`, see V10; and now this).

### V5 — HIGH. The reported decay statistic is not the one the theorem consumes, and it hides a `p^{1/2}` separation from the null.

`interval_decay.py` and `scaling.py` report `Λ`; `(A′)` consumes `max_{t≠0}|T_t|`,
and `O2_additive_completion.md` §1 says so while still reporting `Λ`
(*"`Λ ≥ |T_t|`, so these are conservative"*). The two behave completely
differently. At `p = 65539, M = 16`:

```
                Lambda (published)      Tmax (what (A') consumes)     Tmax * sqrt(N)
A: floor(Mx/p)        0.01622                   2.0041e-03                 0.512
H: sha(x) null        0.01619                   5.8385e-05                 0.015
                 --> "indistinguishable"   --> 34x apart, and growing
```

Fitted over the published ladder: `α(T_max) = −0.52` for the interval filter,
`−1.20` for the SHA null. That is the textbook picture — an algebraic filter sits
at the Weil scale `p^{-1/2}`, a random function at `p^{-1}` — and it means the
line's central empirical claim, *"the curve filter is **indistinguishable from the
null**"* (`O2_fourier_obstruction.md` §6) and *"the algebraic filters land on the
null side"* (`O2_derivation_attempt.md` §8.3), is an artifact of choosing a
statistic dominated by the extreme-value noise of `MN` dlog-Fourier coefficients.
The closure still survives numerically (`0.5·M/√N = 0.5p^{-1/6} → 0`), but the
"controlled null" evidence the line advertises does not say what it is said to say.

**The advertised null control also calibrates the wrong end.** `P2: dlog-int`
returns `Λ = 0.90032` (and `0.99359` at `M=16`) *identical to five decimals at
every `p`* — it is flat by algebraic identity, not by measurement. It demonstrates
that the instrument can see a **maximal** signal; it never demonstrates that the
instrument can resolve a **marginal** one at the `M·T ≈ 1` boundary where the
closure is actually decided. That calibration is the missing control (§3, C2).

### V6 — MEDIUM-HIGH. "Wagner uses the group law" is asserted, and the combining-rule taxonomy is incomplete in three ways.

`O2_composition_closure.md` §3.3 argues that Wagner merges on *"a quotient
homomorphism, so its combining rule is the group law"*. Over `(Z/2)^n` that is
true because a quotient exists. On a prime-order `E(F_p)` **no quotient exists**,
which is the whole content of Theorem 1 — so the analogy pins nothing, and the
choice of `f` is free subject only to bucket-indexability. Three consequences:

1. `O2_quasigroup_gap.md` §1 gets this right: the operative class is
   **quasigroups**, not affine maps. That class is closed only in the **exact**
   case (Theorem C). So the headline `j=2` row rests on the affine branch, which
   is not the branch a tree with a non-homomorphic `h` can use. The coverage table
   records this honestly one row up ("closed exactly; unrealized approximately")
   and the `j`-table beneath it then prints `j=2: closed` unqualified.
2. **Set-valued rules are omitted entirely.** The only filter in the whole line
   that works — Proposition 2's dlog interval — uses an `O(1)`-valued rule
   (`"corrected by at most one carry"`), and Wagner-over-`Z/N` uses the same. The
   taxonomy affine / quasigroup / arbitrary has no row for
   `f : [M]² → {subsets of size s}`. For affine branches this is harmless (`s`
   cancels: gain `≤ 1 + MΛ`); for quasigroup or arbitrary branches it inherits the
   open case. It should be stated, not omitted.
3. **Only level 1 is analysed.** `O2_fourier_obstruction.md` §7 limit 4 flags it:
   *"Wagner's later levels operate on lists already filtered at earlier levels …
   the theorem applies verbatim to level 1 and needs restating for levels ≥ 2."*
   The composition, both quasigroup documents and `KN-FIND-ffe1df` all drop the
   caveat, and the `j = 3, 4` rows that the record marks closed apply the filter
   to conditioned lists.

### V7 — MEDIUM. Family D is not closed, and the finding record contradicts the literature record it cites.

- `KN-LIT-7639` states in its own words: *"family D (cubic, quartic, octic residue
  characters, `k = 3,4,8`) is **not covered by this entry**"*. Theorem 3 step 4
  needs multiplicative Weil/Bombieri at order `k > 2` on a genus-1 curve, which is
  untraced. `KN-FIND-ffe1df`'s coverage table lists **D as closed**.
- `KN-LIT-f6de4b` (committed at `HEAD`, cited in `KN-FIND-ffe1df`'s Artifacts
  section) records that **(H1′) is materially *less* well attested than (H1)**,
  that the Encyclopedia entry is the genus-0 case, and that the Artin–Schreier
  criterion the §2.3 lemma uses is *"NOT verified from any source"*. It also
  records that the correction to `O2_additive_completion.md` §5.1 is **owed and
  not applied**, so that document still asserts the opposite at `HEAD`.
- `KN-FIND-ffe1df` item 3 still reads *"(H1′) the additive case is **better
  attested** but has **no `KN-LIT` entry yet** — one is owed"*, 85 lines below the
  Artifacts section that links `KN-LIT-f6de4b`. The finding record contradicts, in
  one file, the literature record it cites, with no supersession.

Net: every closure row in the table is conditional on a curve-level character-sum
statement that has not been traced to a primary source in either the
multiplicative `k>2` case or the additive case.

### V8 — MEDIUM. The `α ≈ −0.44` extrapolation is under-powered, and needs no unmodelled effect to explain.

Three separate problems with the decay evidence:

1. **Wrong regime.** Every published fit holds `M ∈ {4,16}` and varies `p`. The
   claim is about `M ≈ p^{1/3}`. Tying `M = round(N^{1/3})` moves the fitted slope
   of the closure-relevant quantity `M·T_max` from `−0.523` (fixed `M=16`) to
   `−0.040` — because the exponent is `1/3 + α(T_max)`, not `α(T_max)`.
2. **Under-powered.** One curve per `p`, eight points. Measured spread of the
   per-curve constant `T_max·√N` across the ladder: `0.033` (the `p ≈ 16417`
   curve) to `0.63` — an **18–20× spread**, against a total trend of `2.24×` for a
   genuine `p^{-1/6}` effect over the same `125×` range in `p`. The design cannot
   resolve `α` to better than roughly `±0.15`, and the margin that separates
   "closed" from "gain grows like `p^{1/6}` per level" is `±0.167`. **My own
   `−0.04` fit above is therefore not evidence of non-decay either** — it is
   evidence that the instrument, as configured, cannot decide.
3. **`α ≈ −0.44` needs no explanation.** `O2_additive_completion.md` §4 attributes
   the shortfall to a `log p` completion loss. But `Λ` is by construction a maximum
   over `~MN` coefficients, whose extreme-value model (`scaling.py`'s own model,
   `Λ ~ √(log(MN)/N)`) is a *curve*, not a power law: fitting a power law to it
   over two decades necessarily returns a slope shallower than `−0.5`. The SHA
   null returns `−0.452` for exactly this reason, and the document says so. So at
   least three explanations fit equally well and the data selects none of them.
   The honest statement is the one the document already contains — *"the
   measurement distinguishes decaying from flat; it does not resolve logarithms"* —
   which is weaker than what the coverage table then does with it.

Under `AGENTS.md` rule 7, none of this is crypto-scale validation; `N ≤ 65539` is
`~70` orders of magnitude from a 256-bit prime and the record says so.

### V9 — MEDIUM. The "two independent derivations hit the same `M²` barrier" argument is a shared-method artifact, and the corpus contradicts it.

`O2_composition_closure.md` §1.2: *"Independently derived, same place, same size.
That is strong evidence the loss is real for adversarial `f`, not an artifact of
either write-up."* Three objections:

1. Both applied **the same textbook step** — Cauchy–Schwarz over `M` objects in a
   trilinear form — so agreement is evidence of a shared method, not of tightness.
   That is what a correlated blind spot looks like.
2. `O2_quasigroup_scaling.md` §3 then measures the exact worst case over **all**
   `f` at `~160×` below the `(★)` ceiling and concludes *"the `M` loss is a proof
   artifact here, not a phenomenon"*. Both statements stand uncorrected in the
   same directory, three files apart.
3. Both sessions resolved to `claude-opus-5`, which every document discloses; and
   the composition itself notes that `[D]` had already written the group-law
   improvement in a §7.2 parenthetical, so the two derivations were not
   content-disjoint either. `AGENTS.md` rule 12 requires `review-breakthrough` at
   `max` on an independently resolved model for a closure claim;
   `KN-FIND-ffe1df` states *"Independent review has **not** been performed: no
   Validator or Red Team pass exists on any of these documents."* A record whose
   title asserts a closure and whose body says it is unreviewed is, by this
   repository's own rules, at best `unverified`.

V1 supplies the reconciliation the corpus is missing: **both derivations were
right that `M²` is the barrier, and the composition escaped it only by changing
the quantity being bounded.**

### V10 — LOW-MEDIUM. The line's own mandatory control is not applied in its most recent measurement.

`O2_derivation_attempt.md` §12 control 2 makes it standing policy: *"`δ_const`
must always be reported and subtracted."* `quasigroup_scaling.py` reports
`(eps − 1/M)/Λ` and contains no `δ_const` anywhere, so the `"~160× below the (★)
ceiling"` figure quoted in `KN-FIND-ffe1df` item 1 is computed on the statistic
`[D]` declared wrong. The error direction favours the program's own conclusion
(subtracting `δ_const` would make the excess smaller), so this is a discipline
finding, not a falsification — but the same statistic error is what the line was
created to correct in F1.

### V11 — LOW. The retired configuration's own Pareto row was never written down.

The `j=2` four-tree is asserted to be "the last exponent-moving configuration" at
`0.4167`, but neither its memory (`≈ p^{1/3}`, from the level-1 list size) nor its
linear algebra (`≈ N^{2β} = p^{1/6}` for `β = 2^j/(m(j+1)) = 1/12`) appears
anywhere, and the derivation of `(2^j+m)/(m(j+1))` in `[D]` §7.4 charges only
relation collection. Separately, the exponent table assumes a *perfect* filter
(`δ ≈ 1`, so speedup `= M`), while `[D]` §5's amendment (iv) sets the attack bar at
`δ ≥ M^{-1+Ω(1)}`, which yields a different and un-tabulated exponent — the record
should say which bar it clears.

**Baseline comparison, stated correctly and in the finding's favour.** Pollard rho
is `p^{1/2}` time, `O(1)` memory; parallel collision search trades processors, not
memory, for time, so memory buys an ECDLP attacker essentially nothing here and
there is no van Oorschot–Wiener interpolation that dominates `0.4167`. BSGS is
`p^{1/2}` time and `p^{1/2}` memory, dominated. No published algorithm beats
`p^{1/2}` on a prime field with prime group order. So the excluded configuration
**would** have been a genuine frontier row at `(time p^{0.4167}, memory p^{1/3})`,
and closing it is worth real effort — which is exactly why it must not be recorded
as closed before V1 is discharged. `sota_delta = 0` and `dominated_by:
inapplicable` are the right entries for a barrier result and I do not contest them.

---

## 2. The single cheapest falsification experiment

**RT-EXP-1 — the bucket-gain ladder.** One script, ~10 minutes, attacks V1
directly and picks up V4/V5/V8 for free.

| item | specification |
|---|---|
| primes | `p ∈ {523, 1033, 2063, 4111, 8219, 16417, 32779, 65539}` (the line's own ladder) |
| curves | the **first 3 distinct prime-order curves** per `p`, not the first 1 — this is the fix for V8 and is the only change that costs anything |
| alphabet | `M = round(N^{1/3})` ∈ `{8,10,13,16,20,25,32,40}`, **and** a fixed-`M = 16` arm for continuity with the published tables |
| filters | the 7 in `interval_decay.py`; **plus** `popcount mod M`, `digitsum mod M` (V4); **plus** `x([2]P) mod M` and `(x(P)+x([2]P)) mod M` (degree grows, `Δ` no longer `p^{o(1)}`); **plus** the target-dependent `h_Q(P) = (⌊M x(P)/p⌋ + ⌊M x(P−Q)/p⌋) mod M` for 3 random `Q` (V2) |
| nulls | SHA-256 null; uniform random `h`; `P2` dlog-interval positive control |
| **calibration control (new, and the point)** | a **planted** filter `h_θ(P) = ⌊M·dlog(P)/N⌋` with probability `θ`, uniform otherwise, at `θ = p^{-1/9}` so the planted coupling is `T ≈ θ³ = p^{-1/3}` and `M·T ≈ 1` — exactly the closure boundary. If the instrument does not recover this at its designed value, no null result from it means anything |
| primary statistic | `G := M · max_{c,d} π_c(d)` over buckets with `q_c ≥ 1/M²` — the tree's actual per-level gain (V1) |
| secondary | `M·δ`; `M·max_{t≠0}|T_t|` with the `ξ=0` term removed (the `δ_const`-free form, V5/V10); `Λ` for continuity |
| readout | log-log fit of `G − 1` vs `p` with a bootstrap CI over the 3 curves per `p` |

**Falsification criteria, pre-registered.**

- The headline **fails** if any cheap family's 95% CI on `α(G−1)` excludes `≤ 0`
  while the matched nulls decay — i.e. the tree's per-level gain does not die.
- The headline is **not supported either way** if the CI straddles 0 by more than
  `±0.167`; that is the "the instrument cannot decide" outcome, and on my
  single-curve run it is the outcome I got (`α = −0.04`, spread 18×).
- The closure's empirical support is **established at toy scale** only if the CIs
  exclude `≥ 0` for every covered family *and* the planted control is recovered at
  `M·T ≈ 1`.

I ran the `M`-fixed, single-curve, two-prime version of the primary statistic
already (§0, RT-4): the best-bucket excess is real (`8%` at `p=65539, M=40`) and
is matched by the null. That is the controlled-null outcome, and it is why V1 is
graded "unproved" and not "refuted".

---

## 3. Required controls before any promotion

- **C1 — bound `max_{c,d} π_c`, or state the closure as conditional on
  `max_c π_c = δ(1+o(1))` as a numbered heuristic** with a falsification condition.
  This is the whole of V1 and nothing else in the list matters until it is done.
- **C2 — a planted-signal calibration at the decision boundary** (RT-EXP-1). The
  existing `P2` control is flat by identity and calibrates only the maximal-signal
  end; a null result from an instrument never shown to resolve `M·T ≈ 1` is not a
  null result.
- **C3 — replicate curves per `p`.** One curve per `p` with an 18× constant spread
  cannot support any fitted exponent (V8).
- **C4 — re-report every decay table on the `ξ=0`-free `T_t`**, not on `Λ` (V5),
  and subtract `δ_const` everywhere the line's own §12 control requires (V10).
- **C5 — the nearby-object control**: apply the argument verbatim to `E(F_{q^n})`
  with prime group order and state explicitly why it does not contradict
  Gaudry/Diem. Whatever ingredient blocks it is the ingredient that bounds the
  scope of the conclusion (V2).
- **C6 — add the balance/non-redundancy hypothesis to the additive completion**
  and re-derive its `L¹` bound per family instead of from the false "`O(1)`
  intervals" premise (V4); recheck family J and mid-bit windows against it.
- **C7 — `review-breakthrough` at `max` on a resolved model distinct from
  `claude-opus-5`** before any closure language, per `AGENTS.md` rule 12 and the
  record's own admission.

---

## 4. Verdict on `KN-FIND-ffe1df`'s scope statement

**Overreaching — but unevenly, and the overreach is concentrated in the title,
the coverage table and the closing "redirect search" sentence, not in the
caveats.**

*Honest, and unusually so.* "What is NOT established" items 1, 2, 4 and 5 are
correct and stated against interest; item 2 (the cost clause is not a theorem)
names the limitation that would most tempt a program to bury it. The "Independence
of the derivations" section discloses the single-backend resolution. The
provenance note records a sequential-ID violation against interest. The
frontmatter (`confidence: reported`, `proof_status: derivation`, `proof_refs: []`)
and the frontmatter note (naming the absent `EV-*/DEC-*` chain as *"a real gap"*)
are exemplary.

*Overreaching, on six specific counts.*

1. **The title claims what V1 says is unproved.** "…the Wagner k-tree route … is
   closed" rests on `δ`, and a tree is paid at `max_{c,d} π_c ≥ δ`. Under the
   line's own machinery the single-bucket rate reinstates `M²`, which closes only
   to `p^{1/4}` and leaves `j=2` open. This alone is disqualifying for the word
   "closed".
2. **"for every F1 filter family except the null" is false as stated.** Family D
   (`k = 3,4,8`) is untraced by the record's own literature entry; family J is
   outside the class its supporting theorem defines and violates that theorem's
   conclusion by a factor of 101 at `p = 65539`.
3. **The `j`-table prints "closed" where the coverage table two lines above prints
   "unrealized approximately."** A tree can only use a quasigroup `f`; Theorem C
   closes quasigroups only exactly. The unqualified `j=2: closed` row is stronger
   than the row it sits under.
4. **Item 3 contradicts `KN-LIT-f6de4b`**, which the same file links 85 lines
   earlier, and which corrects (H1′) *downward*. An immutable knowledge record
   should not carry both.
5. **"No such filter exists in any algebraically structured family"** silently
   drops the uniform-independent-`P,Q`, target-independent, level-1-only,
   no-precomputation quantifiers that every underlying theorem carries.
6. **"effort should move off the sum-compatible-filter lane entirely"** is forward
   guidance derived from a closure that is not established. Per
   `docs/inventor-protocol.md` §4 a closure needs a named obstruction, an argument
   and forward guidance naming what remains open — the obstruction and the
   guidance are present, the argument has the V1 hole, and a redirection issued on
   an unproved closure is precisely the premature-closure failure mode the protocol
   treats as symmetric with overclaiming.

**Recommended disposition.** Retitle to what is proved, keep the record, and let
the caveats keep their present strength. `status`/`confidence` should not exceed
`unverified` until C1 and C7 are discharged. The result is genuinely valuable —
Theorem 1, Theorem C and the fibred Weil architecture are real contributions, and
Theorem C in particular is four lines that kill the entire exact quasigroup class
— but it is a **conditional, class-restricted, level-1, bucket-averaged** barrier,
not a closure of the lane.

---

## 5. Narrowest supported statement

> Let `E/F_p` have `#E(F_p) = N` prime. **(i)** *(unconditional)* Every exactly
> sum-compatible `h : E(F_p) → [M]`, `M < N`, into any quasigroup `([M],f)` is
> constant — Theorem 1 and Theorem C, no restriction on `h`, no character-sum
> input. **(ii)** *(conditional)* For `h` either a non-redundant multiplicative
> character filter of complexity `(k,r,Δ)` with `Δ = p^{o(1)}` and `k = 2`, or a
> balanced filter whose level sets are `O(1)` intervals or arithmetic progressions
> in `x(P)`; for `P,Q` independent and uniform; for `h` chosen independently of the
> target; and for an **affine** combining rule `f` — the **bucket-averaged**
> agreement satisfies `eps ≤ 1/M + O(Δ·p^{-1/2+o(1)})`, so the bucket-averaged
> per-level gain is `p^{o(1)}` for `M ≤ p^{1/2-o(1)}`. This is conditional on (H1)
> and (H1′), both untraced at the curve level, and on (H3).
>
> Everything else is measurement or unaddressed: the **single-bucket** rate a tree
> is actually charged; approximate quasigroup rules; `O(1)`-valued rules; levels
> `≥ 2`; multiplicative order `k > 2` (family D); filters whose level sets are
> `p^{Ω(1)}` intervals (family J); target-dependent, precomputed, or amortized `h`;
> and all cheap `h` outside those two classes, which Proposition 2 shows no
> group-theoretic argument can ever reach.

---

## 6. Report record

```yaml
red_team_report:
  id: RT-20260803-be45a8
  task_id: null                      # dispatched conversationally; no TASK-* envelope was supplied
  claim_under_review: >-
    KN-FIND-ffe1df: no cheap sum-compatible filter on E(F_p); the j=2 Wagner
    four-tree at exponent 0.4167 is closed and this route cannot beat rho's 1/2.
  snapshot_reviewed: 198c410a5
  objections:
    - id: V1
      severity: critical
      summary: >-
        The closure bounds delta, the q_c-weighted AVERAGE agreement over buckets.
        A Wagner level fixes one bucket c and offset d, chosen after seeing h, and
        is paid at max_{c,d} pi_c(d) >= delta. Bounding a lower bound on the
        attacker's rate is not a barrier. Bounding the single-bucket rate with the
        line's own machinery gives speedup <= 1 + M^2 * Lambda_W, i.e. closure only
        to M <= p^{1/4}, which does NOT cover j=2 (M = p^{1/3}). The M^2 barrier both
        derivations found was never bypassed; the composition escaped it by changing
        the quantity bounded.
      status: proof hole, not a demonstrated attack (measured excess sits at the null)
    - id: V2
      severity: high
      summary: >-
        The cost clause is definitional AND equivalent in strength to the goal (a
        cheap h with the required dlog-character correlation IS a sub-rho DLP
        algorithm; no standard hardness assumption implies it, since a p^{-1/3}
        advantage is far below any HNP-style reduction). Target-dependent h and
        precomputation amortized over the ~p^{1/3} evaluations of one run are
        listed as uncovered in [D] 7.6 item 5 and absent from the coverage table.
        No nearby-object control against E(F_{q^n}), where Gaudry/Diem does beat rho.
    - id: V3
      severity: high
      summary: >-
        O2_composition_closure.md 1.1 identifies [F]'s Lambda (linear, dlog-character)
        with [D]'s max_psi |That_psi| (trilinear, alphabet characters). They are not
        the same object and the only relation, |That| <= Lambda, runs the wrong way
        for the substitution performed. O2_additive_completion.md 1 states the
        non-identity explicitly and repairs the chain for the additive families only;
        the multiplicative headline closure was never repaired.
    - id: V4
      severity: high
      summary: >-
        Family J counterexample, measured. The additive completion's class is
        "O(1) intervals per level set" and its L1 bound is justified by the false
        claim that g_t (not its level sets) is supported on O(1) intervals. popcount
        mod 16 at p=65539 has 9438 intervals/level, L1 = 7.6 log p, and
        max_{t!=0}|T_t| = 0.395 = 101/sqrt(N), against the claimed O(p^{-1/2+o(1)}).
        The excess is entirely the xi=0 marginal term (balanced T = 7.6e-5,
        GAP = -0.18), so it is a counterexample to the theorem as stated, not an
        attack; the missing hypothesis is [D]'s (H6).
    - id: V5
      severity: high
      summary: >-
        The published statistic Lambda is not the one (A') consumes. On T_t the
        algebraic filters sit at the Weil scale (T*sqrt(N) ~ 0.51, alpha = -0.52)
        and the SHA null at 1/p (alpha = -1.20) - a 34x separation at p=65539 that
        Lambda reports as "indistinguishable". The advertised P2 null control is flat
        by algebraic identity and calibrates only the maximal-signal end.
    - id: V6
      severity: medium-high
      summary: >-
        "Wagner merges on a quotient homomorphism" is asserted; on prime-order
        E(F_p) no quotient exists. The operative class is quasigroups (closed only
        exactly). O(1)-valued combining rules - what Proposition 2's own filter and
        Wagner-over-Z/N use - have no row in the taxonomy. Levels >= 2 are
        unanalysed; [F] 7 limit 4 flags it and every later document drops it.
    - id: V7
      severity: medium
      summary: >-
        Family D (k=3,4,8) is listed closed while KN-LIT-7639 states it is not
        covered. (H1') is "largely untraced" per KN-LIT-f6de4b, including the
        Artin-Schreier criterion the 2.3 lemma uses, and the owed correction to
        O2_additive_completion.md 5.1 is not applied at HEAD. KN-FIND-ffe1df item 3
        still repeats the "better attested / no KN-LIT entry" claim that
        KN-LIT-f6de4b, linked in the same file, retracts.
    - id: V8
      severity: medium
      summary: >-
        Decay evidence is fitted at fixed M while the claim is about M ~ p^{1/3};
        tying M = round(N^{1/3}) moves alpha(M*Tmax) from -0.523 to -0.040. One curve
        per p, with the per-curve constant T*sqrt(N) spanning 0.033..0.63 (18x)
        against a 2.24x trend, cannot resolve alpha to better than ~ +/-0.15 against
        a +/-0.167 decision margin. alpha ~ -0.44 needs no unmodelled effect: Lambda
        is an extreme-value maximum whose own model is a curve, not a power law.
    - id: V9
      severity: medium
      summary: >-
        "Two independent derivations hit the same M^2 barrier" is a shared-method
        artifact (same Cauchy-Schwarz step, same trilinear form, same backend
        claude-opus-5, partially overlapping content). O2_quasigroup_scaling.md 3
        then calls the same loss "a proof artifact, not a phenomenon" and both
        statements stand uncorrected. AGENTS rule 12 review is admitted absent.
    - id: V10
      severity: low-medium
      summary: >-
        [D] 12 control 2 makes subtracting delta_const mandatory; quasigroup_scaling.py
        contains no delta_const, so the "~160x below the (star) ceiling" figure cited
        in KN-FIND-ffe1df is computed on the statistic [D] declared wrong. Error
        direction favours the program's own conclusion.
    - id: V11
      severity: low
      summary: >-
        The retired j=2 configuration's memory (p^{1/3}) and linear algebra (p^{1/6})
        were never costed, and the 0.4167 exponent assumes a perfect filter while
        [D] 5 sets the bar at delta >= M^{-1+Omega(1)}; the record does not say which
        bar it clears.
  required_controls:
    - "C1 bound max_{c,d} pi_c, or state the closure conditional on max_c pi_c = delta(1+o(1)) as a numbered heuristic with a falsification condition"
    - "C2 planted-signal calibration at the M*T ~ 1 decision boundary (theta = p^{-1/9} dlog-interval mixture)"
    - "C3 >= 3 prime-order curves per p on the whole ladder"
    - "C4 re-report every decay table on the xi=0-free T_t rather than on Lambda; subtract delta_const everywhere"
    - "C5 nearby-object control: apply the argument verbatim over F_{q^n} and state why it does not contradict Gaudry/Diem"
    - "C6 add the balance/non-redundancy hypothesis to the additive completion and re-derive its L1 bound per family; recheck J and mid-bit windows"
    - "C7 review-breakthrough at max on a resolved model distinct from claude-opus-5 before any closure language"
  counterexample_or_mutation: >-
    Family J: h = popcount(x(P)) mod 16 on the prime-order curve at p = 65539,
    N = 65287. 9438 maximal intervals per level set (the additive completion's class
    admits O(1)); L1 completion norm 83.81 = 7.56 log p (the interval filters give
    0.72 log p); max_{t != 0}|T_t| = 3.9479e-01 = 100.87/sqrt(N), against a claimed
    O(p^{-1/2+o(1)}); naive per-level gain bound 1 + M*Tmax = 7.32. Narrowest reading:
    the excess is the xi=0 marginal term (balanced Tmax = 7.60e-05, T*sqrt(N) = 0.02,
    below the SHA null; GAP = eps - delta_const = -0.18), so it refutes the theorem as
    stated and identifies the missing hypothesis, and it is not an attack.
  baseline_comparison: >-
    Pollard rho p^{1/2} time / O(1) memory; BSGS p^{1/2} / p^{1/2}, dominated;
    parallel collision search trades processors not memory, so no van Oorschot-Wiener
    interpolation dominates the excluded configuration; no published algorithm beats
    p^{1/2} on a prime field with prime group order. The j=2 four-tree would therefore
    have occupied a genuine frontier row at (time p^{0.4167}, memory p^{1/3}), which is
    why closing it is worth the effort and why it must not be recorded as closed
    before V1 is discharged. sota_delta = 0 and dominated_by = inapplicable are correct
    for a barrier result and are not contested.
  heuristic_challenges:
    - "The load-bearing assumption is unnumbered and unstated: Lemma 5's 'if the pi_c are equal'. It is neither a heuristic with a falsification condition nor a lemma."
    - "'cheap implies algebraic' is a definition presented as a limitation; the record should state that no standard assumption implies it and that proving it implies the goal."
    - "Delta ~ Theta~(N^{-1/2}) for arbitrary h was measured for two families and extrapolated; [F]'s correction notice fixes the headline but the extrapolation persists as the empirical support for the coverage table."
    - "(H1) k>2 on curves and (H1') at curve level are untraced to any primary source; both gate coverage rows marked closed."
  cost_model_challenges:
    - "Per-level gain is charged at M*delta (bucket average) where the algorithm is charged M*max_c pi_c (single bucket): V1."
    - "Levels >= 2 operate on conditioned lists and are not covered by any theorem in the line."
    - "The excluded attack's memory (p^{1/3}) and linear algebra (p^{2*beta} = p^{1/6}) never appear in the exponent derivation."
    - "The exponent table assumes delta ~ 1 (perfect filter) while the stated attack bar is delta >= M^{-1+Omega(1)}; the intermediate exponents are never tabulated."
    - "Filter evaluation cost is charged per call and never amortized over the ~p^{1/3} calls of one tree run, so any p^{1/3}-sized precomputation is free and unmodelled."
  reduction_and_scope_challenges:
    - "Coverage table lists family D closed; KN-LIT-7639 states in its own words that it is not covered."
    - "Coverage table lists family J closed; the supporting document's class excludes it and V4 gives a counterexample."
    - "KN-FIND-ffe1df item 3 contradicts KN-LIT-f6de4b, which it cites in the same file."
    - "The title generalises from 'sum-compatible-filter k-tree' to 'this route cannot beat rho'; the nearby object E(F_{q^n}), where Gaudry/Diem beats rho with a factor-base decomposition test rather than a sum-compatible filter, shows how much the generalisation costs."
    - "'h depending on the target' is listed as uncovered in [D] 7.6 item 5 and has no row in the finding's coverage table, although ECDLP is single-target and h may be chosen after seeing Q."
  proof_architecture_challenges:
    - "Quantifier-order: the theorems fix the bucket before the adversary; the adversary picks (c,d) after seeing h (V1)."
    - "Observation-fiber: Lambda is the observation and it does not separate the algebraic filters from the null, while T_t does by a factor of 34 at p=65539 - the reported invariant is lossy exactly where the conclusion is drawn (V5)."
    - "Method ceiling: the largest claim the single-bucket resource measure supports under ideal tuning is M <= p^{1/4}, which does not reach the p^{1/3} headline."
    - "Nearby object: no control against E(F_{q^n}) with prime group order, where the desired conclusion is false."
    - "Boundary/strictness: the P2 positive control is flat by algebraic identity and calibrates only the maximal-signal end, so the instrument was never shown to resolve the regime in which the closure is decided."
  narrowest_supported_statement: see section 5
  next_concrete_action: >-
    Run RT-EXP-1 (section 2): the bucket-gain ladder. Primary statistic
    G = M * max_{c,d} pi_c(d) over buckets with q_c >= 1/M^2, at M = round(N^{1/3}),
    3 prime-order curves per p over p in {523,1033,2063,4111,8219,16417,32779,65539},
    against the SHA/random nulls and a planted dlog-interval mixture at theta = p^{-1/9}
    calibrated to sit at the M*T ~ 1 decision boundary. Refutation if any cheap family's
    95% CI on alpha(G-1) excludes <= 0 while the nulls decay; "instrument cannot decide"
    if the CI straddles 0 by more than +/-0.167. ~10 minutes of compute. Until it and C1
    are done, KN-FIND-ffe1df should not carry closure language.
  artifact_paths:
    - analysis/o2-sum-compatible-filters/reviews/REDTEAM.md
```

---

## 7. Reproducing the four measurements

All four ran against the line's own `fourier_obstruction.py` helpers (curve
search, `dlog_table`), on the same ladder, exact whole-group enumeration, no
sampling. Scratch scripts, not archived artifacts; the definitions below are
complete enough to re-implement in a few lines each.

```python
# the statistic (A') actually consumes, per t != 0, from the dlog-indexed h
g    = np.exp(2j*np.pi*t*hv/M);  gh = np.fft.fft(g)/N
T_t  = np.sum(np.conj(gh) * gh * gh)          # = E[g(P)g(Q)conj(g(P+Q))]
T_bal= np.sum(np.conj(gh[1:]) * gh[1:] * gh[1:])   # xi=0 (marginal) term removed
Lam  = np.abs(gh).max()                       # the published statistic

# the single-bucket rate (V1), exact, via  J[s,c] = #{(i,j): h(i)+h(j)=s, h(i+j)=c}
Fg   = np.fft.fft(np.exp(2j*np.pi*np.outer(range(M),hv)/M), axis=1)
conv = np.fft.ifft(Fg*Fg, axis=1)             # conv[t,m] = sum_i g_t(i)g_t(m-i)
D    = conv @ W.T                             # W[c] = indicator(h == c)
J    = (np.exp(-2j*np.pi*np.outer(range(M),range(M))/M).T @ D).real / M / N**2
# eps_c(d) = J[(c-d)%M, c];  q_c(d) = sum_a n_a n_{c-d-a};  pi = eps/q;  G = M*max pi

# the completion norm the additive argument needs (V4)
L1 = np.abs(np.fft.fft(np.exp(2j*np.pi*t*H/M))/p).sum()   # H = filter on F_p, not on E
```

Environment: Python 3, numpy, macOS arm64; deterministic apart from SHA-256 used
as a fixed function. Every count is an exact enumeration over all `N²` pairs via
FFT in dlog coordinates, matching the line's own method.

---

## Inference

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11). CONSEQUENCE
    STATED PLAINLY: this red-team pass resolves to the SAME backend as every
    document it reviews. Under AGENTS.md rule 12 a closure claim requires
    review-breakthrough at max on an independently resolved model, and this session
    is NOT that. It therefore discharges nothing; C7 remains owed in full, and the
    objections above should be read as a checklist for that review rather than as a
    substitute for it. The measurements in section 0 are independent of the model in
    a way the arguments are not: they are exact enumerations that any reviewer can
    re-run from the definitions in section 7.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this session.
    The identifier is unverified configuration.
```
