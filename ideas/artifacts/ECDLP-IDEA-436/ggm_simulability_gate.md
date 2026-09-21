# ECDLP-IDEA-436 — GGM-simulability gate memo for the coordinate-valuation-profile functional family

- Task: `TASK-20260831-c7c3ef` (goal `GOAL-ECDLP-001`, proposal namespace
  `B71-IDEA436-GGM-SIMULABILITY-GATE-20260831-c7c3ef`)
- Role: idea-generator. Requested policy `research-deep`, reasoning effort `high`.
- Runs: 0. Experiments: 0. Implementations: 0. No code was written or executed;
  no `p`-adic arithmetic was implemented or timed.
- Evidence tier: **derivation, zero-run, single-session, not independently
  reviewed**. Nothing in this memo is an experimental result, an attack, a
  speedup, a breakthrough, or a status change. Status changes are the
  Coordinator's authority alone.

## 0. Verdict

**`scoped_rejection_simulable`.**

ECDLP-IDEA-436's own primary named family

```
inv_{j,r}(k) = v_p( x([k]Ŝ) - x([j]Ŝ) ),  truncated at precision r
```

is **generic-group-model simulable with `O(1)` overhead — one group inversion
and two equality tests per query — in the *strictest* Shoup GGM (opaque
labels), independently of `r`, `p` and `n`.** The reason is not that a generic
oracle can perform `p`-adic arithmetic (it cannot). The reason is that under
ECDLP-IDEA-436's own stated hypotheses this particular functional *takes only
two values*, and the predicate separating them is exactly the group-theoretic
predicate `[k]S = ±[j]S`. The valuation and the precision `r` are inert.

Consequently the family is closed at exponent `1/2` by `KN-TECH-005` /
Shoup's generic lower bound, by the same closure mechanism as `KN-FIND-002`'s
jet oracle and `KN-FIND-b7e091`'s endomorphism oracle — and, unlike those two,
**without needing the structured-GGM weakening that `KN-FIND-002` discloses in
its own scope block.** This closure is therefore strictly stronger than the
one ECDLP-IDEA-436 anticipated it would have to clear.

The recommendation to the Coordinator is **scoped rejection of ECDLP-IDEA-436
as written**, per that record's own gate language ("**The GGM-simulability
check is a gate, not a step**: if the functional family is simulable, this
record is rejected without running anything") and its own disproof track
("Prove the family is GGM-simulable").

The rejection is **scoped**, and §7 states exactly what it does not cover: the
record's secondary disjunct — "*or a fixed statistic of the precision-`r`
coordinate digits of `[k]Ŝ`*" — is closed only **relatively** (structured GGM,
zero group-operation overhead, no advantage over an adversary that already
holds `F_p` coordinates), and §6.4 gives the nearby object (anomalous curves,
Smart/Satoh–Araki/Semaev) on which a relative closure of that kind is
demonstrably *not* upgradable to an absolute one. That residue stays open.

## 1. What is being gated, exactly

### 1.1 The frozen setting (from ECDLP-IDEA-436, Assumptions 1–2)

`E/F_p` ordinary with good reduction, `p >= 3`; `S ∈ E(F_p)` of order `n` with
`gcd(n, p) = 1`; `E/Q_p` the good-reduction lift with a Weierstrass model whose
coefficients lie in `Z_p`; `Ŝ ∈ E(Q_p)` the unique point of order `n` reducing
to `S`. The lift is target-uniform and scalar-blind: `Ŝ` is a deterministic
Hensel function of `S` alone (`KN-TECH-73630e`, quoted in §2.1).

### 1.2 The two disjuncts of the family

ECDLP-IDEA-436 states its family as one primary form plus one hedge. They have
different answers and must be gated separately.

- **D1 (primary, named):** `inv_{j,r}(k) = v_p( x([k]Ŝ) - x([j]Ŝ) )` truncated
  at precision `r`. Truncation convention: report `min(v_p(·), r)`, with the
  cap value `r` standing for "valuation at least `r`, including the exactly-zero
  difference". Degenerate arguments (`k ≡ 0` or `j ≡ 0 mod n`, where `[k]Ŝ = Ô`
  and `x` is undefined) need a stated convention; §5.3 shows the verdict is
  independent of which convention is chosen.
- **D2 (hedge):** any fixed statistic `T` of the precision-`r` coordinate
  digits of `[k]Ŝ` — e.g. the `r`-th `p`-adic digit of `x([k]Ŝ)`, a digit-sum,
  a `p`-adic distance to a fixed subvariety.

### 1.3 The precise question (dispatch constraint 3, verbatim scope)

Is the map `(E, S, j, k, r) -> inv_{j,r}(k)` computable using only generic
group operations (group law, inversion, equality test, random group-element
sampling) and **no** coordinate-level or `p`-adic-arithmetic access beyond what
a generic group oracle exposes?

The dispatch card is right that this is not obvious: a `p`-adic valuation of a
coordinate difference is prima facie *not* a generic-group-computable quantity,
because coordinates and valuations are structure the oracle does not expose.
The gate is decided below not by asserting that a generic oracle can compute
valuations, but by computing what the valuation *equals*.

## 2. The formalization fork, stated before the argument

Simulability is meaningless until the oracle interface is pinned down. Three
choices are genuinely open in the source records and this memo does not pick a
convenient one; it answers on each branch and reports where the branches agree.

### 2.1 Fork A — which model of "generic group"

- **A-strict (Shoup GGM).** Group elements are random opaque labels
  `σ: Z/nZ -> {0,1}^ℓ`; the algorithm has the group operation, inversion, and
  equality on labels, and nothing else. `KN-TECH-005` (`kb`) states the bound
  this model carries: "*Any generic DLP algorithm needs Omega(sqrt(p)) group
  operations (Shoup, KN-LIT-011; precursor Nechaev 1994).*"
- **A-structured (structured GGM).** The curve equation and the affine
  coordinates of every handled point are public. This is the model
  `KN-FIND-002` actually used, and it discloses the consequence itself:
  "*The classification uses the **structured GGM** (curve equation is public),
  not the strictest Shoup GGM (opaque labels). Under the strictest GGM, jet and
  endomorphism would be NON-SIMULABLE because they require coordinate access.*"
  (`KN-FIND-002`, "Scope and limitations", `internal`.)

`KN-FIND-b7e091` evaluates in a model closer to A-strict for the jet oracle —
"*Oracle A (first-jet): non-simulable but privately computable (requires k)*" —
while agreeing with `KN-FIND-002` on the endomorphism oracle, which it
simulates *group-theoretically*: "*For prime-order prime-field curves with
End_{F_p}(E) = Z, every phi = [m], so phi(Q) = [m]Q is computable in m group
operations from Q alone.*" (`internal`.) The two records are not in conflict;
they are evaluated on different branches of Fork A, and §6 uses that fact as
the proves-too-much control.

**Open formalization question OFQ-1.** Neither record states a single canonical
model for this program. This memo therefore answers on **both** branches and
reports the answer only where they agree (D1) or where they differ (D2). It
does not adjudicate which branch is this program's canonical GGM; that remains
open and is flagged as forward guidance in §10.

### 2.2 Fork B — is the oracle over the lift or over the reduction

- **B-reduction.** The generic group is `⟨S⟩ ⊆ E(F_p)`; the oracle handles are
  labels for elements of `⟨S⟩`, and `inv` is an *augmentation* the adversary may
  query on a handle.
- **B-lift.** The generic group is `⟨Ŝ⟩ ⊆ E(Q_p)`; handles label elements of
  `⟨Ŝ⟩`.

**Open formalization question OFQ-2 (resolved for this gate, not in general).**
By `KN-TECH-73630e` the reduction `red : ⟨Ŝ⟩ -> ⟨S⟩` is a group isomorphism of
cyclic groups of order `n`, so the two branches present *isomorphic* generic
groups and any oracle defined on one transports canonically to the other. Fork
B therefore does not affect this memo's verdict. It would matter for a
functional defined on a *larger* subgroup of `E(Q_p)` than the prime-to-`p`
torsion — in particular anything touching the formal group `Ê(pZ_p)` — which
ECDLP-IDEA-436 explicitly excludes ("*no map into the formal group is
taken*"). Recorded so that a later proposal touching `Ê(pZ_p)` does not inherit
this memo's resolution of Fork B by default.

### 2.3 Fork C — what "overhead" is counted

Group-operation count, following `KN-TECH-005` and `KN-FIND-002`'s `C = 1` /
`C = 0` bookkeeping. Local bit-work (Hensel lifting, `p`-adic arithmetic at
precision `r`) is *not* a group operation and is reported separately, because
the Shoup bound is a group-operation bound. §5.4 states why that accounting
convention is exactly where a relative closure can hide a real attack, and
§6.4 exhibits the object where it does.

## 3. Two lemmas

Both are textbook; neither is this memo's contribution. They are stated because
the collapse in §4 is their composition.

**Lemma 1 (integral reduction of prime-to-`p` torsion).** For `k ≢ 0 mod n`,
`x([k]Ŝ) ∈ Z_p` and `x([k]Ŝ) mod p = x([k]S)`.

*Derivation.* `Ê(pZ_p)`, the kernel of reduction, is a pro-`p` group and hence
torsion-free away from `p` (`KN-TECH-73630e`, `internal`, which attributes this
to Silverman's formal-group/good-reduction chapters). `[k]Ŝ` has order dividing
`n` with `gcd(n,p) = 1`, so `[k]Ŝ ∉ Ê(pZ_p)` unless `[k]Ŝ = Ô`. A point of
`E(Q_p)` outside the kernel of reduction has non-negative valuation coordinates
on an integral model and reduces coordinatewise to its image in `E(F_p)`, which
is `[k]S` by definition of the canonical lift. ∎

**Lemma 2 (the `x`-map has exactly the `±` fibres, on both sides).** On a
Weierstrass model, `x(-P) = x(P)` identically, and `x(P) = x(P')` implies
`P' = ±P`. Hence over `F_p`, `x([k]S) = x([j]S) ⟺ k ≡ ±j mod n`; and over
`Q_p`, `x([k]Ŝ) = x([j]Ŝ) ⟺ [k]Ŝ = ±[j]Ŝ ⟺ k ≡ ±j mod n`, the last
equivalence because `red : ⟨Ŝ⟩ -> ⟨S⟩` is a group isomorphism
(`KN-TECH-73630e`) and negation is a group automorphism, so the canonical lift
commutes with it: `σ(-P) = -σ(P)`. ∎

Lemma 2's first clause — that `x` does not separate `P` from `-P` — is the
property Koblitz and Menezes are reported to single out as the non-generic
feature of elliptic curves, in *Another Look at Generic Groups*
(eprint.iacr.org/2006/230). That is a **`retrieved` citation at web-search
snippet level only**: the direct fetch of the PDF failed to yield extractable
text and no passage of that paper was read (§11 and the source-novelty audit).
The fact itself is elementary and textbook and the lemma does not rest on that
citation; the citation is a pointer for a reviewer.

## 4. Proposition (the collapse): D1 is two-valued and its separating predicate is group-theoretic

**Proposition.** Under the frozen setting of §1.1, for all `j, k` with
`k, j ≢ 0 mod n`:

```
v_p( x([k]Ŝ) - x([j]Ŝ) )  =  0        if  k ≢ ±j  (mod n),
                          =  +∞       if  k ≡ ±j  (mod n).
```

There is **no** `j, k, E, p, n` for which the valuation takes a finite value
`≥ 1`.

*Proof.* Two cases.

- Suppose `k ≢ ±j mod n`. By Lemma 2, `x([k]S) ≠ x([j]S)` in `F_p`. By Lemma 1
  both `x([k]Ŝ)` and `x([j]Ŝ)` lie in `Z_p` and reduce to `x([k]S)` and
  `x([j]S)` respectively. Distinct residues mod `p` force
  `v_p(x([k]Ŝ) - x([j]Ŝ)) = 0`.
- Suppose `k ≡ ±j mod n`. By Lemma 2 applied over `Q_p`,
  `x([k]Ŝ) = x([j]Ŝ)` **exactly** in `Q_p`, so the difference is the zero
  element and its valuation is `+∞`.

The two cases are exhaustive and the dichotomy is complete, so no intermediate
value is attained. ∎

**Corollary 4.1 (precision is inert).** For every `r ≥ 1`,
`inv_{j,r}(k) = 0` when `k ≢ ±j` and `= r` (the truncation cap) when
`k ≡ ±j`. The profile at precision `r` carries exactly the information of the
profile at `r = 1`, for every `r`. ECDLP-IDEA-436's precision-growth exponent
`rho_r` is therefore `0`, not `≥ 1/2`.

**Corollary 4.2 (information content).** `inv_{j,r}(·)` has image of size 2, so
one query returns at most **1 bit**, and for a fixed `j` and uniformly random
`k` that bit is `1` with probability `2/n` — i.e. its Shannon content is
`H(2/n) = O((log n)/n)` bits per query. The "profile" is the indicator of the
`±j` fibre and nothing else.

**Corollary 4.3 (what the family actually is).** The functional family D1 *is*
the `x`-line equality predicate on `⟨S⟩`, i.e. equality in the quotient
`⟨S⟩/{±1}`. That quotient is available in `E(F_p)` for free and is precisely
the structure Pollard rho already exploits via the negation map. The `p`-adic
lift, the coordinates, the valuation and the precision schedule contribute
nothing to it.

## 5. The simulator, and the overhead

### 5.1 Strict-GGM simulator for D1 (branch A-strict)

Let `A` be the queried handle (the adversary's handle for `[k]S`, or
equivalently for `[k]Ŝ` under Fork B) and `B` the reference handle for `[j]S`.

```
Sim(A, B, r):
  1. if EQ(A, B):        return r            # cap value
  2. B' <- INV(B)                            # 1 group operation
  3. if EQ(A, B'):       return r            # cap value
  4. return 0
```

Correctness is Proposition 4 read as a table: the returned value equals
`inv_{j,r}(k)` on every input. Cost: **1 group operation (inversion) and 2
equality tests**, independent of `r`, `n`, `p`, and of the coordinates. No
coordinate access, no Hensel lifting, no `p`-adic arithmetic, no field
arithmetic of any kind is performed by the simulator. Overhead constant
`C = 1` in `KN-FIND-002`'s bookkeeping.

If the family is queried as a *profile vector* over a reference set `J`
(`inv_{j,r}(k)` for all `j ∈ J`), the same simulator runs `|J|` times: `|J|`
group operations and `2|J|` equality tests, still `O(1)` per emitted value.

### 5.2 Structured-GGM simulator for D1 (branch A-structured)

Also simulable, by two independent routes: the strict simulator of §5.1 works
verbatim, and additionally a coordinate-level simulator may Hensel-lift `A` and
`B` to precision `r` locally (0 group operations, `Õ(r log p)` bit-work) and
compute the valuation directly. Both return the same value by Proposition 4.
The strict route is the one that carries the closure, because it is the one
valid in the model where Shoup's theorem holds.

### 5.3 Degenerate arguments

If `k ≡ 0 mod n` then `[k]Ŝ = Ô` and `x` is undefined; the family must fix a
convention (return a sentinel, or exclude). Whatever convention is fixed, the
simulator detects the case with one further equality test against the identity
handle, which the GGM provides in both branches. The overhead stays `O(1)` and
the verdict is unchanged. This is recorded because the frozen family in
ECDLP-IDEA-436 does not state the convention, and a reviewer should not have to
infer it.

### 5.4 D2 (the digit-statistic hedge) — the honest dichotomy

D2 does **not** collapse. `T` applied to the precision-`r` digits of `x([k]Ŝ)`
is in general a genuine coordinate function taking many values (Proposition 4
is specific to a *difference of two `x`-coordinates*; it says nothing about a
single point's digits). So:

- **Branch A-structured:** `[k]Ŝ = σ([k]S)` is a deterministic function of the
  `F_p`-point `[k]S` (`KN-TECH-73630e`: "*`Ŝ` is a deterministic function of
  `S`, computable to any precision from `E(F_p)` data alone by Hensel lifting
  plus the order condition*"). A simulator holding the coordinates of `[k]S`
  Hensel-lifts to precision `r` and applies `T`. Cost: **0 group operations**
  plus `Õ(r log p)` local bit-work. Simulable, by the *same mechanism* as
  `KN-FIND-002`'s jet oracle, whose simulator likewise "*computes P+Q (1 group
  operation) and then evaluates the rational function*" of public coordinates.
- **Branch A-strict:** `T` is not a function of the opaque label, so it is not
  simulable — exactly as `KN-FIND-002`'s own scope note predicts for jet and
  endomorphism, and as `KN-FIND-b7e091` records for the first-jet oracle. But
  in that branch no party can compute `T` either: it is outside the model, not
  an advantage inside it.

**The dichotomy:** *in every model in which D2 is publicly computable at all,
it is simulable with `O(1)` group-operation overhead; in the model in which it
is not simulable, it is not computable.* That is a **relative** closure — "no
advantage over an adversary that already holds `F_p` coordinates" — and §6.4
shows why a relative closure of this shape may not be promoted to an absolute
exponent-`1/2` statement. The accounting convention of Fork C is where the gap
lives: local bit-work is uncounted, and an attack that does all its damage in
local bit-work (which is exactly what the anomalous-curve transfer is) is
invisible to a group-operation-counted simulability argument.

## 6. Mandatory control — the proves-too-much check

The argument style used above is two moves. Both are run against objects whose
correct verdict is already recorded, and against one object where the desired
conclusion is **known false**.

- **M1 (determinism reduction).** If the oracle output is a deterministic
  function of objects the adversary already holds in the model (handles plus
  public curve data), it is simulable at the cost of evaluating that function
  locally.
- **M2 (predicate collapse).** If that deterministic function further factors
  through group-theoretic predicates (equality, inversion, group law), the
  simulation lifts from A-structured to A-strict.

### 6.1 Jet oracle (`KN-FIND-002` records: SIMULABLE, `C = 1`, structured GGM)

- M1: dual-number data at `(P, Q)` is a rational function of the coordinates of
  `P`, `Q`, `P+Q` and the public curve parameters. Simulator: 1 group operation
  plus local rational-function evaluation. **Verdict: simulable, `C = 1`,
  A-structured.**
- M2: the derivative values separate points that stand in identical
  group-theoretic relations, so no collapse. **Verdict: not A-strict simulable.**

Recorded verdicts: `KN-FIND-002` — "*Jet oracle (C=1) ... The generic simulator
computes P+Q (1 group operation) and then evaluates the rational function.*"
`KN-FIND-002` scope — "*Under the strictest GGM, jet and endomorphism would be
NON-SIMULABLE.*" `KN-FIND-b7e091` — "*Oracle A (first-jet): non-simulable but
privately computable (requires k).*"
**Reproduced on both branches, including the apparent tension between the two
records, which the argument correctly localises to Fork A rather than to an
error in either record.** ✔

### 6.2 Endomorphism oracle (`KN-FIND-002`: `C = 0`; `KN-FIND-b7e091`: `m` group ops)

- M1: `φ` is a public deterministic map on coordinates; simulator evaluates
  locally with **0 group operations**. Matches `KN-FIND-002`'s `C = 0`. ✔
- M2: for prime-order prime-field curves `End_{F_p}(E) = Z`, so `φ = [m]` and
  `φ(Q) = [m]Q` is a pure group computation: collapse succeeds, **`m` group
  operations, A-strict**. Matches `KN-FIND-b7e091` exactly. ✔

### 6.3 The anti-triviality half of the control — objects the argument must *fail* to close

An argument that closed everything would be worthless. Run on the two oracles
`KN-FIND-002` explicitly declines to close at `1/2`:

- **Elliptic-net oracle.** M1 applies but the deterministic function is
  evaluated *through* the group: `W(a,b)` needs `O(log a + log b) = O(log N)`
  group operations. Non-constant overhead ⇒ **not closed by the
  constant-overhead bound.** Matches `KN-FIND-002`'s "*SIMULABLE with
  non-constant overhead (NOT closed at 1/2)*". ✔
- **Incidence oracle.** M1 gives `O(B^m)` group operations, `B` growing with
  problem size ⇒ **not closed by the constant-overhead bound.** Matches
  `KN-FIND-002`. ✔ (`KN-FIND-b7e091` separately closes an incidence oracle at
  `O(m)` per query under a different, narrower oracle definition — reporting
  both rather than picking one, per the retrieval policy on contradictory
  sources. The disagreement does not bear on this gate.)

The argument therefore discriminates: it closes 2 of 4 recorded oracles at
`O(1)` and declines to close the other 2, reproducing the recorded split 4/4.

### 6.4 Nearby-object control — and it FIRES, on M1

Take the object where the desired conclusion is **known false**: an anomalous
curve, `#E(F_p) = p`, with the Semaev / Satoh–Araki / Smart additive-transfer
map `ψ` (`KN-TECH-033`, `kb`: "*there is an explicit isomorphism from that
group onto the additive group `(F_p, +)` ... the ECDLP is linear time*";
"*the p-adic version (KN-LIT-088) is additionally the one place where lifting to
characteristic zero is known to pay*"). ECDLP-IDEA-436 itself names this case as
its positive control.

- **M1 applied to `ψ`:** `ψ(P)` is a deterministic, publicly computable function
  of the coordinates of `P` and the public curve data (the lift choice is
  `p`-ambiguous but `ψ` is independent of it). So M1 declares `ψ`
  **A-structured simulable with 0 group operations** — and if "A-structured
  simulable with `O(1)` overhead" were allowed to imply "closed at exponent
  `1/2`", M1 would prove that ECDLP on anomalous curves needs `Ω(√p)` group
  operations. That is **false**: it is solved in `O(log p)` field operations.
  **M1 alone proves too much and is broken as a closure rule.**
- **M2 applied to `ψ`:** does `ψ` factor through group operations and equality
  tests? No — `ψ` is a nontrivial homomorphism onto `(F_p,+)` whose evaluation
  from handles alone would make DLP generically easy, contradicting Shoup. M2
  correctly **does not fire**. ✔

**Repair, and where the memo's weight rests.** The exponent-`1/2` closure of D1
in §0 rests on **M2 only** — strict-GGM simulability, where Shoup's theorem
actually holds. M1 is used only for D2 in §5.4, and its conclusion there is
correspondingly weakened to a *relative* closure with the anomalous curve
standing as the explicit witness that relative ≠ absolute. This is also exactly
the caveat `KN-FIND-002` records against itself, and the caveat `KN-LIT-7606`
(The Structured Generic-Group Model, Corrigan-Gibbs–Henzinger–Wu, `kb`) makes
into a quantity: that corpus entry notes "*A plain-GGM simulability argument
cannot close a candidate for real elliptic curves*" and that the paper's
`δ`-fraction parameter "*is what makes 'how non-generic is this attack' a
quantity rather than a binary*".

**Control outcome: the argument reproduces every recorded verdict (4/4 oracles,
both Fork-A branches), and the known-false object breaks the weak move M1 while
leaving the strong move M2 intact. The D1 verdict is carried by M2 and survives
the control. The D2 statement is carried by M1 and is therefore reported at the
weaker, relative tier.**

## 7. Lossy-projection test (inventor protocol §2)

The tracked object of ECDLP-IDEA-436 is the `p`-adic valuation profile of
coordinate differences along `⟨Ŝ⟩`.

- **Is it lossy?** Yes, maximally: by Corollary 4.2 it retains 1 bit and
  discards everything else about `[k]Ŝ`.
- **Is what it discards discarded compatibly with the target's operations?**
  Yes — the retained bit is `[k]S = ±[j]S`, a `{±1}`-equivariant predicate, so
  it propagates deterministically under the group action.
- **Is it therefore a new object?** **No.** The test has two failure modes, not
  one. A projection that loses *nothing* is a change of coordinates
  (`KN-LIT-7595`'s `(Δ, Π)` example, via `docs/inventor-protocol.md` §2,
  `internal`). The failure here is the mirror image: the projection loses a
  great deal, but its *image* factors through `⟨S⟩/{±1}`, an object already
  available for free in `E(F_p)` and already exploited by the negation map in
  Pollard rho. The `p`-adic apparatus is a longer road to an object that was
  never lifted out of reach. Recording this mirror failure mode — **lossy, but
  landing inside an already-available quotient** — is the transferable part of
  this memo.

## 8. Pareto honesty and cost accounting

- `dominated_by`: **Pollard rho with the negation map on the `x`-line**, at
  `n^{1/2+o(1)}` time and `O(1)` memory. Frontier rows checked: rho
  (`n^{1/2}` time, `O(1)` memory), BSGS (`n^{1/2}` time, `n^{1/2}` memory),
  and the generic preprocessing tradeoff `S·T² = Ω̃(n)` (Corrigan-Gibbs–Kogan).
  All three are read off `KN-TECH-005` (`kb`, opened in full), which states the
  bound, the matching of BSGS and rho to it, and the preprocessing tradeoff;
  `KN-TECH-001` is cited *inside* that record and was **not** opened here. D1
  supplies no query/data axis on which it is incomparable: by Corollary 4.2
  each query yields ≤ 1 bit, and the optimal use of the `±`-fibre indicator
  against adaptively chosen references *is* an `x`-line collision search, i.e.
  rho. So D1 is dominated on every axis and matched on none.
- `sota_delta`: **time exponent `+0`, memory exponent `+0`, query exponent
  `+0`.** Not merely "no exponent gain": no constant-factor gain either, since
  the `√2`-type saving from the negation map is already realized inside rho
  (`recalled`, standard folklore; not load-bearing on the verdict, which rests
  on the exponent).
- `target_complexity` in ECDLP-IDEA-436's own notation: the record required
  `lambda, mu <= 0.45` for promotion. Corollary 4.1 gives `rho_r = 0`
  (precision is free — the opposite of the record's expected fatal obstruction),
  but Corollary 4.2 gives reciprocal informative-query density `N^delta` with
  `delta = 1` for a fixed reference and `delta = 1/2` under adaptive
  references, so `lambda = max(a, delta + q, ell, u + q) >= 1/2`. The record's
  own promotion gate fails, by a *different* term than the record predicted.
- Hidden overhead: none is hidden in the simulator; `O(1)` here is literally
  one inversion and two equality tests, not an `o(1)` exponent.

## 9. What this memo does not claim

1. **No usefulness claim, in either direction.** Per dispatch constraint 5 and
   `KN-TECH-73630e`, the lift is information-theoretically empty for
   group-theoretic invariants; non-simulability would not have implied
   usefulness, and simulability here does not add any new hardness claim about
   ECDLP. The verdict is about one functional family, not about ECDLP.
2. **No closure of `KN-OPEN-3417fc`.** That open problem asks about *any*
   computable non-group-theoretic coordinate/valuation invariant. This memo
   closes one named family (D1) unconditionally and one hedge (D2) relatively.
   The open problem stands.
3. **No closure of face F2** (`KN-TECH-06bb4e`) beyond what
   `KN-TECH-73630e` already recorded.
4. **No experimental content.** Zero runs. Proposition 4 is a derivation
   produced in this single session and has not been independently re-derived,
   machine-checked, or reviewed. Its two ingredient lemmas are textbook and are
   corroborated by `KN-TECH-73630e` (`internal`) and by a bounded web search
   (`retrieved`, AI-synthesized search summary, §11 and the source-novelty
   audit); the *composition* is this session's own step and its honest label is
   `adaptation`, not a new theorem.
5. **No status change.** The recommendation in §0 is a recommendation. Changing
   ECDLP-IDEA-436's `State` field, or any hypothesis status, is the
   Coordinator's authority alone, and ECDLP-IDEA-436's own record is frozen and
   was not edited by this task.
6. **No Fork-A adjudication.** OFQ-1 (§2.1) is left open on purpose.
7. **No claim that any direction is impossible.** §10 names what remains.

## 10. Open formalization questions and forward guidance

The closure standard (`docs/inventor-protocol.md` §4) requires a named
obstruction, an argument, and forward guidance naming what remains open.

**Named obstruction (derivation tier, zero runs).**
*Quantity:* size of the image of `inv_{j,r}` on `⟨Ŝ⟩`, and the group-operation
overhead of its GGM simulation.
*Value:* image size exactly **2** for every `r ≥ 1`, `p ≥ 3`, `n` coprime to
`p`; simulation overhead exactly **1 inversion + 2 equality tests**.
*Error bars:* none — this is a derivation over the stated hypotheses, not a
measurement; no runs are cited because none exist, and this is disclosed rather
than dressed as a measured obstruction.
*Scope:* `E/F_p` with good reduction, `p ≥ 3`, `gcd(n, p) = 1`, Weierstrass
model, canonical order-`n` lift, D1 as written. Outside any of these — bad or
additive reduction, `p = 2`, a non-Weierstrass model where the `x`-map does not
have `±` fibres, a point whose order is divisible by `p`, or a functional on
`Ê(pZ_p)` — Proposition 4 does not apply.

**`resource_check` — which theory wants this measurement.** Examined: **yes**,
and one taker was found. The degeneracy is *hypothesis-shaped* in the bad- and
additive-reduction regime. A bounded web search (see the source-novelty audit)
surfaced *Recovering Kodaira types from ℓ-torsion on elliptic curves*
(arXiv:2607.02678, `retrieved`, **abstract level only**), which "*endows `E[ℓ]`
with a distance function that records the `p`-adic distances between the
`x`-coordinates of the points*" and shows this determines the Kodaira type. That
is the *same tracked object* as ECDLP-IDEA-436's, and it is informative exactly
where this memo's Lemma 1 fails — the fetched abstract concerns "*potentially
good and multiplicative reduction*" and Kodaira types, i.e. **bad** reduction.
The abstract does **not** state that the good-reduction case is degenerate; that
is this memo's own derivation, and the adjacency is offered as corroborating
context, not as support. Reading: the object is not empty in general, it is
empty precisely under ECDLP-IDEA-436's own good-reduction hypothesis — the
hypothesis the ECDLP setting cannot drop, since bad reduction is not the
cryptographic case.

**Forward guidance — classes that remain open after this memo.**

1. **OFQ-1: this program's canonical GGM branch.** `KN-FIND-002` and
   `KN-FIND-b7e091` evaluate on different Fork-A branches. Until one is
   declared canonical (or `KN-LIT-7606`'s `δ`-parameterised model is adopted,
   which would replace the binary with a quantity), every "closed at exponent
   1/2" in this program's corpus carries an unstated model parameter. Cheap,
   zero-compute, and it would re-scope two existing findings.
2. **The D2 residue.** A digit statistic of a *single* lifted point does not
   collapse and is closed only relatively. The specific sub-question that would
   settle it: is there a statistic `T` and a precision schedule `r(n)` such that
   `T(σ(·))` is a nonconstant *homomorphism-like* map `⟨S⟩ -> (small target)`?
   `KN-TECH-033` shows the answer is yes exactly when the curve supplies a
   global structural coincidence (`#E(F_p) = p`), and that record's own framing
   is the right bar: "*representations win exactly when the curve supplies a
   global structural coincidence,*" and "*a proposal must name its
   coincidence*". A D2 proposal that cannot name its coincidence for an
   ordinary curve is not ready for a gate.
3. **Coordinate differences of *three or more* points.** Proposition 4 uses the
   `±` fibre structure of a *pairwise* `x`-difference. A functional built from
   `v_p` of a determinant, resultant, or division-polynomial value at several
   lifted points is not covered by the collapse and is not gated here. Whether
   it collapses by a similar route is open and is the closest untried neighbour.
4. **Non-Weierstrass models.** Lemma 2 is model-dependent. On a model whose
   distinguished coordinate does not have `±` fibres, the collapse argument does
   not run as written. Whether an equivalent collapse holds is open.
5. **`KN-OPEN-019`.** This memo used an object-first framing without the
   ECDLP object enumeration that `KN-OPEN-019` calls for; the family-to-object
   mapping in §7 is a sketch, not a taxonomy, exactly as
   `docs/inventor-protocol.md` §1 requires it to be labelled.

## 11. Source ledger for this memo

Full provenance labelling is in the companion `source-novelty-audit.yaml`.
Summary: `KN-FIND-002`, `KN-FIND-b7e091`, `KN-TECH-73630e`, `KN-TECH-06bb4e`,
`KN-TECH-005`, `KN-TECH-009`, `KN-TECH-033`, `KN-OPEN-005`, `KN-OPEN-3417fc`,
`KN-LIT-6935a1`, `KN-LIT-7606` were **opened and read in full in this task**
(`internal` / `kb`) and every quotation above is verbatim from the opened file,
with markdown emphasis markers dropped and the source's `Ŝ` typography kept.
arXiv:2607.02678 was fetched at abstract level (`retrieved`). One fetch
(eprint.iacr.org/2006/230, Koblitz–Menezes, *Another Look at Generic Groups*)
**failed** to yield extractable text and is cited only at web-search-snippet
level, for a fact that is independently textbook and not load-bearing.
`KN-LIT-7595` is cited via `docs/inventor-protocol.md` §2, which was opened;
the underlying corpus entry was not opened separately.
`experiments/EXP-GGM-001/*` was **not** opened: it lies outside this task's
declared `read_scope`, so the baseline reproduction in §6 is against
`KN-FIND-002`'s and `KN-FIND-b7e091`'s stated arguments and recorded verdicts
rather than against the simulability-test implementation. Disclosed as a
limitation, not as a claim about that implementation.
