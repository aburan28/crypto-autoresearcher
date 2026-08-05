# C1 — GOAL-SSIQ-001 idea catalogue: the smoothness / table-construction side of the exponent budget

Slice: levers on the factors governing **smoothness probability**, **modular-polynomial
evaluation**, **table-construction cost**, and the **Dickman/CEP-type distributional
inputs** of the archived p^{1/3+o(1)} supersingular isogeny algorithm
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, cited by line below).
Companion agent C2 owns the search / collision / memory side. This catalogue does not
propose, cost, or evaluate a change to the claw-finding mechanism, to the van
Oorschot–Wiener curve, or to how the two lists are compared.

**Nothing here claims p^{1/4}, an exponent below 1/3, a break, or a completion.**
Every ceiling stated below is `toy` or `medium`. Every idea is a proposal, not a result.
Novelty is not adjudicable in this session: no idea below is claimed new, and no idea
below is dismissed as known.

---

## 0. Frame

### 0.1 Off-limits as the primary lens this session

Declared before enumeration, per `docs/inventor-protocol.md` §1:

- **OL-1. Generic claw finding / meet-in-the-middle over the two keyed lists.** C2's slice.
- **OL-2. The van Oorschot–Wiener memory tradeoff** (paper L39). Lever L5; recorded for
  honesty in GOAL-SSIQ-001, not prioritised, and not this slice.
- **OL-3. Re-deriving GOAL-P13-001's per-entry cost measurement.** EV-PEC-2e67ff and
  EV-PEC-857664 are **inputs** here, cited, never re-derived and never restated as this
  goal's own evidence (GOAL-SSIQ-001 `related_goals_note`).
- **OL-4. Minkowski/Hermite-type bounds on the degree lattice.** Lever L1 is
  CLOSED-IN-SCOPE at derivation tier (BATCH-001 D1); its obstruction field was a
  category error twice over and that is already corrected in the goal record.

### 0.2 The tracked object of this catalogue, and the lossy-projection test

**Tracked object (TO-MULT).** The *multiplicative type* of the target degree: the map

    (E, φ_min : E → E^{(p)})  ↦  the multiset of prime factors of deg(φ_min),

together with the divisor lattice it generates.

**Lossy?** Yes, and the loss is large and structured. The projection collapses every
isogeny of a given degree to one point. Its fibre over a degree d, for a fixed domain E,
has ≈ d·∏_{ℓ|d}(1+1/ℓ) elements (paper L133, Lemma 3.2; L230, "the number of isogenies
of degree d is at least d"). That fibre size **is** exponent-budget factor F3 — the
quadratic factor that makes memory equal time. So the discarded data is precisely the
data C2's slice tracks, and the retained data is precisely this slice's.

**Compatible with the target's operations?** Yes. deg is multiplicative under
composition, so TO-MULT propagates deterministically along Algorithm 1's extension steps
(paper L137–L152): appending an ℓ-isogeny adjoins ℓ to the multiset, with no dependence
on which ℓ-isogeny. Algorithm 2's decision procedure — list by (degree, smoothness),
split at a divisor ≤ X (L167, L177–L185) — **factors entirely through TO-MULT**.

**Not a change of coordinates.** From the multiset one cannot recover E, φ, or the
codomain; the fibre is exponentially large. Contrast the `KN-LIT-7595` worked
counterexample (Δ, Π), where the pair was recoverable and nothing was gained.

**Consequence used repeatedly below.** Because the algorithm's *correctness* condition
lives entirely in TO-MULT while its *cost* lives partly in the fibre, the smoothness lane
and the collision lane are genuinely different lanes, and a lever that moves TO-MULT's
hit probability without touching the fibre is not a repackaging of a C2 lever.

### 0.3 The one exponent fact that bounds this entire slice

From the paper's own assembly (L210–L218) and BATCH-001's re-derivation:

    X = (B·D)^{1/2}  exactly   (L167),   so   M ≈ X^2 = B·D,   D = (p/2)^{1/3} (L81)
    time ≈ M / P0,   P0 = u^{-u(1+o(1))},   u = log(p/2)/(3 log B)   (L69, L187)

With B = p^{o(1)}, the total time exponent equals the **Theorem 1.5 degree exponent** and
nothing else. Therefore:

> **CEILING-SLICE (stated once, binds every idea below).** No lever on smoothness
> probability, on Ψ(X,B), on modular-polynomial evaluation, or on table-construction cost
> can move the time exponent below 1/3 while B = p^{o(1)} and D = p^{1/3}. Factor F4
> carries exponent 0 (goal record, confirmed and strengthened in BATCH-001), and F5/F7/F8
> carry exponent 0. What this slice *can* move is (i) the **shape of the o(1)** — the
> paper's own headline caveat, "a superpolynomial overhead hiding in the o(1) exponent"
> (L13, L39) — and (ii) the **charged concrete cost**. Ideas C1-5 and C1-3 are the only
> two below that touch an exponent at all, and both do so through D, not through
> smoothness, and both are audited to a **negative** ceiling.

Stating this up front is the point of the goal, not a hedge. Two of the thirteen ideas
below are ceiling arguments whose expected verdict is CLOSED; a failed audit is a useful
result (`docs/inventor-protocol.md` §8).

### 0.4 What is already measured and must not be redone

- Section 4.1's one-F_{p^2}-operation-per-entry convention (L230) is **REFUTED in the
  attack's disfavour** at the tested scale: 1843.5 to 94023.4 counted multiplications per
  entry over 2 ≤ ℓ ≤ 211 at p ~ 2^40; seam-free exponents γ_A = 0.9328644281 (schoolbook),
  γ_B = γ_{S-MIN} = 0.8100336227 (Karatsuba); ℓ-independent structural prefactor 2^8.92
  (EV-PEC-2e67ff OBS-C/OBS-D; EV-PEC-857664 OBS-G). **Medium tier.** Not redone here.
- `c` is citable **only** as the bracket [1.327077, 1.576444] at NIST-I, never as a number
  (DEC-20260802-48c72c). Every cost line below obeys this.
- Pre-registered falsifier **FC-4 (MECHANISM-INCONSISTENT) FIRED**, driven by ℓ ∈ {3,5}
  (EV-PEC-857664 OBS-K). A post-hoc ℓ-restriction cannot lift it. Every cost-model idea
  below carries FC-4 on its face.
- The correct phrasing is binding: "the fitted per-entry cost curve, **evaluated at
  ℓ = B_opt**, is 21.2 to 25.2 bits above Section 4.1's convention" — never "the measured
  prefactor is 2^9.73" (EV-PEC-857664 CORR-3).
- IDEA-20260803-48e258 owns the crossover curve p*(w). C1-2, C1-11 and C1-12 below are
  marked **successors** to it and do not duplicate it: that record holds the cost law
  fixed and varies (p, w); these vary **B** and the **per-entry cost model**.

---

## 1. The thirteen ideas

### C1-1. Divisor-in-window split: replace the worst-case greedy bound X = (BD)^{1/2} by X = λ·D^{1/2}

**Which factor** — F2 (split exponent) and, through it, F3 (list cardinality). X enters
the exponent budget as M ≈ X^2 = B·D (L167, L177–L185). The factor B in M comes *only*
from the worst-case greedy split, not from smoothness. Removing it removes a factor B
from both time and memory and changes the shape of the o(1).

**Claim** — Lemma 3.4's proof (L177–L185) bounds deg η ≤ ℓ_{k+1}·D/X ≤ B·D/X by charging
the *largest possible* prime at the greedy boundary, and then sets X = (BD)^{1/2} so that
this worst case still fits. For a **typical** B-smooth integer n ≈ D the divisors of n are
far denser near √n than one per multiplicative factor B. Replacing the universally
quantified split condition by the existentially quantified divisor condition —
*deg φ has a divisor in [deg φ / X, X]* — permits X = λ·D^{1/2} with λ a slowly growing
(conjecturally O(1) to (log p)^{O(1)}) factor, at the cost of a success-probability factor
q = Pr[divisor in window]. Predicted effect at NIST-I under the paper's own §4.1 model:
M falls from ≈ 2^{94.1} to ≈ 2^{80}–2^{83}, time from ≈ 2^{106.5} to ≈ 2^{91}–2^{93},
i.e. **9–14 bits of memory and 13–15 bits of time, with the exponent unchanged at 1/3.**

**Mechanism** — Correctness lemma is restated with a strictly weaker hypothesis:
*if deg φ is B-smooth **and** has a divisor a with deg φ/X ≤ a ≤ X, then Algorithm 2
returns φ.* Cyclicity is unaffected: for a cyclic isogeny of degree n every divisor a | n
gives a unique factorization φ = η∘ψ with deg ψ = a and both factors cyclic (paper L177,
minimality ⟹ cyclic kernel). The multiplicative-window density is the classical
Erdős multiplication-table / Ford quantity H(x,y,z): for a dyadic window,
H(x,y,2y)/x ≍ (log y)^{-δ}(log log y)^{-3/2} with δ = 1 − (1+log log 2)/log 2 ≈ 0.086.
For **B-smooth** n the divisor set is denser still, because a B-smooth n ≤ D has ≈ u
prime factors near B and ≈ 2^{ω(n)} divisors whose logarithms concentrate near
(log n)/2 with spread ≈ (√ω/2)·log B; the expected number of divisors in a window of
log-width 2 log λ is ≈ 2^{ω}·2 log λ / √(2π V), which **grows** with u. So q improves as
p grows, which is the opposite of the direction that would kill the idea.

**Minimal discriminating test** — Pure integer arithmetic, no isogeny and no curve.
(1) For D ∈ {2^{40}, 2^{48}, 2^{56}} and B on a ladder bracketing D^{1/u} for u ∈ {3,4,6,8},
enumerate or sample B-smooth n ∈ [D/2, D], and measure q(λ) = Pr[n has a divisor in
[n/(λ√D), λ√D]] for λ ∈ {1, 2^{1/4}, 2^{1/2}, 2, 4, √B}. (2) Recompute the paper's §4.1
row arithmetic at NIST-I/III/V with X' = λ√D substituted for X = (BD)^{1/2}, reporting
M, P0·q, time and **peak memory** side by side with the unmodified rows, under (a) the
paper's 1-op-per-entry convention and (b) the committed measured per-entry law charged at
ℓ = B_opt with `c` carried as the bracket only. (3) Re-optimize B jointly with λ.

**Null object / control** — (i) **Matched uniform-integer null**: identical q measurement
on uniform integers in [D/2, D] with no smoothness condition. If q_smooth ≈ q_uniform the
"smooth numbers have denser divisors" mechanism is not doing the work claimed for it, and
the effect is the generic Ford density, which is a *weaker* but still usable basis —
report which. (ii) **λ = √B recovers the paper exactly**: a known-answer gate. At λ = √B
the measured q must be 1.000 at every sampled n; anything else falsifies the instrument,
not the idea. (iii) **Decay tell**: q(λ) must increase monotonically in λ and decrease as
u increases at fixed λ. A q that does not move with λ is the canonical artifact signature.

**Falsifier (reachable)** — F1-a: q(λ) ≤ (λ-dependent threshold pre-registered from the
Ford exponent) at every λ with λ^2 ≤ B^{1/2}, i.e. the window must be nearly as wide as
the paper's to give constant hit rate — the lever then buys < 2 bits and is CLOSED as a
concrete lever. F1-b: q decreases in u, so the gain shrinks as p grows and the asymptotic
o(1)-shape claim fails. F1-c: the re-costed table under the measured per-entry law is not
better than the unmodified table at any (λ, B), i.e. the B-re-optimisation the idea forces
is charged away. F1-d (structural, kills it at the whiteboard): a counterexample showing
the restated correctness lemma is false — e.g. a divisor a of deg φ in the window whose
induced ψ is not in L(E, X', B) for a reason other than degree.

**Cost** — implementation: low (≈150 lines of pure Python: smooth-number enumeration,
divisor enumeration, window test). compute: minutes to ~1 CPU-hour. No SageMath, no
network, no modular polynomials.

**Ceiling** — `medium` at best for the arithmetic; the NIST-scale rows are a **model
substitution carrying no claim tier**, exactly as EV-PEC-857664 OBS-M requires.

**Kills-it-early** — Enumerate all B-smooth n in one decade at D = 2^{40}, B = 2^{7},
count those with a divisor in the dyadic window around √n. If that fraction is below ~0.05
the whole idea is a ≤2-bit lever and drops to the bottom of the ranking. Ten minutes.

**Method ceiling** — *What would have to be true:* that for the specific integer
deg φ_min the divisor-window density is Θ(1) (or (log p)^{-O(1)}) at λ = p^{o(1)}.
*Strongest statement this lever could ever support:* time and memory
p^{1/3}·(log p)^{O(1)}·ρ(u/2)/ρ(u) — i.e. **removal of the superpolynomial o(1)** if and
only if B can simultaneously be raised to p^{Θ(1)} (that is C1-2, and it is a separate and
harder condition). It can **never** move the exponent below 1/3: M ≥ X^2 ≥ D = p^{1/3}
because the two lists must jointly cover a degree-D isogeny, and λ ≥ 1.
*Nearest known obstruction:* Ford's theorem gives only a (log y)^{-0.086}(log log y)^{-3/2}
density for **uniform** integers at a dyadic window — a log-power, not a constant — so the
Θ(1) claim rests on the smooth-number strengthening, which is a heuristic about the
concentration function of log-divisors of smooth integers and is not supplied by CEP.
*Nearby-object control:* apply the identical measurement to uniform integers (control (i)
above). A method that cannot distinguish "smooth n" from "uniform n" on this statistic has
not identified the load-bearing structure and the claim must retreat to the Ford density.
*Cheap pre-compute falsification:* control (ii), the λ = √B known-answer gate, plus the
whiteboard check that q ≤ 1 makes the total ≥ D·ρ(u/2)/ρ(u) ≥ D — so the lever cannot be
argued past p^{1/3} even in the ideal limit.

---

### C1-2. The self-consistent smoothness bound: solve B* = (M(B*))^{1/4} from per-prime modular-polynomial amortisation

**Which factor** — F5 (the smoothness parameter B) and F3 (list cardinality) jointly. B
does not carry an exponent, but it sets Ψ(X,B), P0, X, and hence the whole o(1). The
paper fixes B = e^{(1/3)√log(p/2)} in the proof (L193) and notes at L200 that "in practice,
one may instead precompute an optimal choice of B minimizing the total expected cost". The
committed value log2 B_opt = 14.2 (RUN-WESOVOW-001) is a **numerical** optimum whose
governing constraint has never been written down.

**Claim** — The true constraint on B is not the u^{-u} balance alone but a **per-prime
affordability condition**: a prime ℓ is admissible in the listable set only if the cost of
its modular polynomial, amortised over the entries that use it, is within the per-entry
budget. Under the precompute-and-amortise model this gives ℓ^4 ≲ M and hence the fixed
point B* = M(B*)^{1/4}; under the per-specialisation model it gives a per-entry cost
Θ̃(ℓ), a completely different optimum, and a much smaller B*. **The two models disagree by
6+ octaves in B*, and the exponent budget currently records neither.** Prediction: under
(precompute, idealised 1-op-per-entry) B* ≈ 2^{20}–2^{21} at NIST-I with u ≈ 4.3 and
P0^{-1} ≈ 2^{8.3}; under (per-specialisation, idealised) B* falls back toward the
committed 2^{14.2}; under the **measured** per-entry law B* falls further.

**Mechanism** — Entries whose degree is divisible by ℓ are a ≈ 1/ℓ fraction of M, so
Φ_ℓ's Θ̃(ℓ^3) construction cost amortises to ℓ^4/M per entry; requiring ≤ 1 gives
ℓ ≤ M^{1/4}. Its Θ̃(ℓ^2) storage is ≤ M^{1/2} ≪ M, so storage is not the binding
constraint *relative to a table this program already calls astronomical* — a statement
that must be made in relative terms only. Algorithm 1's outer loop is `for ℓ ≤ B` (L143),
so exactly one Φ_ℓ is live at a time, which is what makes the amortisation legitimate.

**Minimal discriminating test** — Zero compute beyond arithmetic on committed constants.
(1) Write the fixed-point equation under each of the two Φ models and each of the two cost
laws (§4.1 convention; measured law with `c` as the bracket only), giving four (B*, M, P0,
time, peak memory) rows at each of log2 p ∈ {256, 384, 512, 576, 768}. (2) Known-answer
gate: the (per-specialisation, §4.1-convention) cell must reproduce the committed
log2 B_opt = 14.2 and the paper's five rows (L234–L238) to within the 2.2309-bit NIST-I
irreproducibility band inherited from RUN-WESOVOW-001. A machinery that cannot reproduce
the point it generalises is void. (3) Report d(log2 time)/d(log2 B) at each cell so the
sensitivity, not just the optimum, is visible.

**Null object / control** — **Null-baseline control**: recompute every cell with the
Φ-amortisation constraint **removed** (B unbounded above). The optimum must then be driven
only by the u^{-u} balance and must move materially; if it barely moves, the amortisation
constraint is not doing the work claimed for it and the idea is re-described as a
restatement of the existing numerical optimisation. **Adversarial-corner check**: evaluate
at the corner of the `c` bracket and the γ readings most favourable to the attack and
report that corner explicitly.

**Falsifier (reachable)** — F2-a: the known-answer gate fails, machinery void.
F2-b: B* under every model lies within 1 octave of the committed 2^{14.2}, so the fixed
point is a re-derivation of a number already committed and the idea is a bookkeeping
note, not a lever. F2-c: under the measured per-entry law the total is **monotone
decreasing in B down to the smallest admissible B**, i.e. there is no interior optimum and
the whole framing is wrong. F2-d: the ℓ^4 ≲ M derivation is contradicted because entries
are not uniformly distributed over ℓ in the way the 1/ℓ density assumes (this is exactly
the RT3-C1 entry-weighting effect, already priced at 0.60–1.00 bits **pro-attack**, and it
must be carried signed, not absorbed).

**Cost** — implementation: low (arithmetic + a root-finder for the fixed point).
compute: none. Successor to IDEA-20260803-48e258 on the B axis; that record's fitted-window
guard and undefined-segment discipline are inherited verbatim.

**Ceiling** — No claim tier. Every row is a **model substitution** under the committed
assumption set, exactly as EV-PEC-857664 OBS-M declares.

**Kills-it-early** — Evaluate the two Φ models at NIST-I on the back of an envelope: if
M^{1/4} at M ≈ 2^{92.5} (the paper's own memory row) gives B* ≈ 2^{23} but the measured
per-entry law at ℓ = 2^{23} charges > 25 bits, the idea reduces to "the Φ model decides
everything", which is C1-11, and C1-2 should be folded into it rather than run separately.

**Method ceiling** — *What would have to be true:* that per-prime amortisation, not the
smoothness balance, is the binding constraint on B, and that the per-entry cost at the
resulting B* is Θ̃(1). *Strongest ever supportable:* a closed-form B*(p) and a closed-form
o(1) for the incumbent — **not an exponent**, and this must be said on the face of every
deliverable. *Nearest obstruction:* the identifiability limit already committed in
EV-PEC-2e67ff `boundaries` — "the experiment cannot discriminate between per-entry cost
laws that agree over ℓ ≤ 211 and diverge at ℓ ~ 2^{14}" — and C1-2 makes the relevant ℓ
*larger*, so it widens rather than narrows that gap. That is a real cost of the idea and
it is stated here rather than discovered later. *Nearby-object control:* apply the same
fixed-point derivation to the C-NULL object of the committed runs, whose per-entry cost is
O(1) in ℓ by construction; the derivation must return "no constraint on B", and if it
returns a finite B* the derivation is manufacturing one. *Cheap pre-compute falsification:*
the known-answer gate (2).

---

### C1-3. Remark 1 multiplicity, priced against the Siegel–Rogers short-vector count

**Which factor** — F4 (inverse success probability) at its interface with F1. Remark 1
(L191) records that "there are generally multiple small (non-cyclic) isogenies E → E^{(p)},
and it is sufficient for any one of them to be smooth", observed experimentally by Panny,
and states that the phenomenon "is absorbed in the hidden term of the asymptotic
complexity". Nobody in this program has checked what it is worth or whether the absorption
is correct.

**Claim** — The number of isogenies E → E^{(p)} of degree ≤ T is, on the Siegel–Rogers
heuristic for the governing rank-3 trace-zero lattice of discriminant p/4 (BATCH-001's
corrected object), N(T) ≈ κ·T^{3/2}/p^{1/2}, so N(D) = Θ(1) at D = (p/2)^{1/3} — consistent
with Theorem 1.5 (L81) — and N(p^{1/3+ε}) ≈ p^{3ε/2}. Therefore the multiplicity lever is
**exponent-neutral at best and negative in practice**: raising the degree threshold to
p^{1/3+ε} multiplies the table by p^{ε} (since M ≈ B·T) while multiplying P0 by at most
min(N, 1/P0) = p^{o(1)}, because P0^{-1} is already p^{o(1)}. Expected verdict: **CLOSED
as an exponent lever, OPEN as an o(1) lever worth an explicitly computed number of bits.**

**Mechanism** — Two competing readings, and the idea exists to separate them.
*Reading A (independent):* the N(T) degrees are multiplicatively independent for
smoothness purposes, so P0(T) ≈ 1 − (1 − ρ(u_T))^{N(T)} ≈ N(T)·ρ(u_T), and Remark 1 is
worth log2 N(T) bits.
*Reading B (dependent):* the degrees are values of one ternary form at nearby lattice
points, subject to shared congruence conditions and shared small-prime structure, so the
smoothness events are strongly positively correlated and Remark 1 is worth far less than
log2 N. Reading B is not speculative: EV-WESO-001 already records "one constant-factor
signed bias against smoothness identified (ramified small primes demote L(1,χ) Euler
factors)" from TASK-20260724-P13-HEUR.

**Minimal discriminating test** — Fold into C1-7's sampler (shared instrument, separate
falsifier). For each sampled maximal order, LLL/enumerate **all** lattice vectors of norm
≤ κ·D rather than only the shortest, record the vector of norms, and measure (a) the
empirical N(T) curve against κT^{3/2}p^{-1/2}, (b) the empirical
Pr[at least one of the N norms is B-smooth] against both Reading A and Reading B
predictions, (c) the pairwise correlation of the smoothness indicators.

**Null object / control** — **Random-lattice null**: identical enumeration and smoothness
measurement on random positive-definite ternary forms of discriminant p/4 (not arising
from any quaternion order). Reading A is the null's own prediction, so agreement with the
null is *evidence for* A and disagreement is the structural signal for B. This is the same
null the goal record already pre-registered for REC-1 and it is reused rather than
reinvented. **Artifact tell**: N(T) must scale as T^{3/2}; a measured exponent of 2 is
either the α = 2 alternative the goal record names, or an enumeration bug, and the two are
separated by running the identical enumerator on the random-form null.

**Falsifier (reachable)** — F3-a: N(T) exponent measured ≠ 3/2 on **both** arms →
instrument failure, no disposition. F3-b: measured exponent = 3/2 on the null and ≈ 2 on
the Deuring arm → the Deuring lattices are not Siegel-equidistributed, which is a genuine
structural finding and independently **reopens** L1's second disjunct at exactly 1/4 per
the goal record's pre-committed reversion. F3-c: Reading A confirmed and log2 N(D) < 1 →
Remark 1 is worth under a bit and the paper's absorption is vindicated; lever CLOSED with
a number. F3-d: Reading B confirmed → the correlation is a named, measured structural
property of the target distribution and it *weakens* the incumbent's P0, i.e. it moves
against the attack.

**Cost** — implementation: medium (shares C1-7's sampler; adds a rank-3 short-vector
enumerator, ~120 lines of pure Python: Cholesky + Fincke–Pohst, on 3×3 Gram matrices with
entries ~p). compute: ≤ 2 CPU-hours on top of C1-7.

**Ceiling** — `medium`, and only as a statement about the sampled distribution at the
sampled p. Never crypto-scale isogeny evidence: no isogeny is computed anywhere.

**Kills-it-early** — Compute κ·D^{3/2}/p^{1/2} symbolically at D = (p/2)^{1/3}. If it is
below 2, Reading A's ceiling is < 1 bit and the lever is closed before any sampling.

**Method ceiling** — *What would have to be true:* that multiplicity gains more than the
threshold-raising costs. *Strongest ever supportable:* total = M/P0 with M ≈ B·T and
P0 ≈ N(T)ρ(u_T); differentiating, the optimum in T sits at the point where
d log N/d log T = 1, i.e. 3/2 = 1 — **never satisfied**, so the optimum is at the smallest
admissible T and raising T is strictly bad. That is a one-line closure with a named
mechanism, and it is the expected outcome. *Nearest obstruction:* the count exponent 3/2
is the rank divided by two for a rank-3 form; changing it requires changing the rank, which
is lever N5, not this one. *Nearby-object control:* the random-form null. *Cheap
pre-compute falsification:* the derivative argument above, executable at the whiteboard.

---

### C1-4. Is the CEP/Dickman model's local-density correction for the ternary form constant, or u-dependent?

**Which factor** — F4 (P0) through the distributional input of Heuristic 1 (L69), and
therefore every margin row identically.

**Claim** — Heuristic 1 asks that deg φ_min "has the smoothness probability that one would
expect for a random integer of its size" (L83), justified by composing Theorem 1.5 (L81)
with Theorem 1.4 (CEP, L77). But deg φ_min is not a random integer: it is the **value of a
positive-definite ternary quadratic form of discriminant p/4 at its shortest vector**.
Values of a ternary form satisfy local conditions at primes dividing 2·disc, and their
smoothness law carries an Euler-product correction with local densities δ_ℓ. The claim to
be decided: **the correction is a constant factor C(p) independent of u (harmless: absorbed
into the o(1) with a computable number of bits), or it is u-dependent (not harmless: it
changes the shape of the tail exactly where Heuristic 1 is used).**

**Mechanism** — For each small prime ℓ, the density of form-values divisible by ℓ^k differs
from ℓ^{-k} by a factor determined by the local representation density of the form over
Z_ℓ. If those factors are ℓ-wise bounded and the deviation from 1 is summable, the
resulting change to Pr[B-smooth] is a bounded multiplicative constant, uniformly in u.
If instead the small primes are systematically **demoted** (the L(1,χ) Euler-factor effect
already identified in EV-WESO-001), then B-smooth values — which are built out of small
primes and need *many* of them — are penalised in proportion to how many small primes they
require, i.e. **in proportion to u**, and the correction is C^{u} rather than C.
Those two are distinguishable at the whiteboard by writing the Euler product and at the
bench by measuring the smooth fraction across a u-ladder.

**Minimal discriminating test** — Two arms, both cheap.
*Arm 1 (zero compute):* write Pr[form-value is B-smooth] as ρ(u)·∏_{ℓ≤B}(local factor),
identify whether the product's logarithm is Θ(1) or Θ(u) in the regime u ≈ 4–13, and state
the sign. *Arm 2 (rides C1-7's sample):* measure the ratio R(u) = p̂(u)/ρ(u) at every rung
of a pre-registered B-ladder and fit log R against u. The discriminator is the **slope**:
slope ≈ 0 ⟹ constant correction; slope ≠ 0 ⟹ u-dependent, and its sign says which way.

**Null object / control** — **Matched uniform-integer arm at the same size and the same
sample count**, run through the identical trial-division pipeline. Its R(u) measures the
finite-size error of the ρ reference itself, so any Semaev-style conflation of "departure
from the asymptotic reference" with "departure specific to the form" is impossible by
construction. This is the ABS-REL discipline of H-LPF-001 (`absolute_versus_relative`
clause), reused verbatim rather than re-invented; if the uniform arm leaves the
pre-registered band at a rung, **limb B is not decidable at that rung by this apparatus**
and is reported as such. Second control: a **random ternary form of the same
discriminant**, which shares the "value of a ternary form" structure but not the Deuring
provenance; a departure present on both is a ternary-form effect, a departure present only
on the Deuring arm is a Deuring effect.

**Falsifier (reachable)** — F4-a: fitted slope of log R against u indistinguishable from
zero at the pre-registered resolution across ≥4 rungs at ≥2 primes → the correction is
constant, the lever is CLOSED as an o(1)-shape question and survives only as a bit count.
F4-b: slope significantly negative → the target is **rougher** than uniform, P0 is
overstated, and the incumbent's cost is understated: a finding **against the attack** and
a direct weakening of Heuristic 1 at the tested scale. F4-c: slope significantly positive
→ the target is **smoother** than uniform, P0 is understated, and the incumbent's cost is
overstated: a finding **for the attack**. F4-d: the uniform arm itself fails its band →
apparatus statement only, no disposition either way.

**Cost** — implementation: low if it rides C1-7 (a fit and a ladder); the Euler-product arm
is paper-only. compute: none beyond C1-7.

**Ceiling** — `medium`. A departure measured at one p is a statement about that p; the
u-dependence claim needs at least two primes to be a claim about u at all.

**Kills-it-early** — Write the local factor at ℓ = 2 and ℓ = 3 for the standard maximal
order at p ≡ 3 mod 4. If both are 1 + O(1/ℓ) with no systematic sign, the Θ(u) branch has
no mechanism and Arm 2 is a confirmation exercise rather than a discriminator.

**Method ceiling** — *What would have to be true:* that the deviation from the uniform-integer
smoothness law is large enough to matter at the operating u. *Strongest ever supportable:*
a signed, quantified correction to P0 of the form ρ(u)·C or ρ(u)·C^{u} — which changes the
o(1) and every margin row identically, and **never the exponent** (F4 carries exponent 0).
*Nearest obstruction:* CEP (L77) is a theorem about integers below X; there is no
correspondingly uniform theorem for values of a ternary form at a shortest vector, so the
absolute limb can only ever be tested against ρ, never proved. *Nearby-object control:*
the random-ternary-form arm, which is the closest object where the Deuring structure is
absent but the ternary structure is present. *Cheap pre-compute falsification:* the ℓ = 2, 3
local factors.

---

### C1-5. The threshold–smoothness exchange curve T(θ) = θ + g(θ) − s(θ)

**Which factor** — F1 and F4 jointly. This is the only place in this slice where an
exponent can move, and the audit's expected verdict is that it moves the wrong way.

**Claim** — Generalise the algorithm to accept only curves whose minimal degree satisfies
δ_E ≤ p^{θ} for θ ≤ 1/3, re-randomising until one is found (L193, L202). Then
total time exponent = θ + g(θ) − s(θ), where g(θ) = −log_p Pr[δ_E ≤ p^{θ}] and s(θ) ≥ 0 is
the exponent-scale credit from the *improved smoothness* of a smaller target (u = θ log p /
log B falls with θ, so ρ(u) rises). **s(θ) = 0 identically whenever B = p^{o(1)}**, because
ρ(u) is p^{o(1)} for every u = Θ(√log p): the smoothness credit is real, is worth bits, and
is worth **no exponent**. Prediction: with the Siegel/BATCH-001 value g(1/4) = 1/8,
T(1/4) = 3/8 > 1/3 = T(1/3); the lever is CLOSED unless g's exponent α is 2 rather than
3/2, in which case g(1/4) = 0 and T(1/4) = 1/4 exactly — the goal record's own
pre-committed reversion condition.

**Mechanism** — #{E : δ_E ≤ T} = c·T^{α}·p^{β}; anchored at T = 1 by the p^{1/2} size of
the F_p locus (β = 1/2) and at θ = 1/3 by Theorem 1.5 (the fit must go vacuous there).
α = 3/2 is the Siegel–Rogers/volume prediction for a rank-3 lattice; α = 2 is the
ingredient-(c) failure mode named in the goal record's next_action. This idea is the
**smoothness-side successor** to REC-1 and explicitly does not duplicate it: REC-1 measures
the *size* distribution only, and the exchange curve additionally needs s(θ) and the
conditional smoothness law at lowered θ, which REC-1's design cannot produce.

**Minimal discriminating test** — Zero compute. (1) Write T(θ) = θ + g(θ) with
g(θ) = max(0, 1/2 − αθ) under α ∈ {3/2, 2} and both anchors enforced, and tabulate T over
θ ∈ [1/5, 1/3]. (2) Add s(θ) explicitly and prove s ≡ 0 for B = p^{o(1)}, then compute the
**bit-scale** (not exponent-scale) smoothness credit at NIST-I for θ ∈ {1/4, 0.28, 0.30}
and report it beside the exponent cost, so that the two are never confused again.
(3) State the exact numeric condition on α at which T(1/4) = 1/3, and hence what REC-1's
measurement would have to return to reopen the lever.

**Null object / control** — **Degenerate-θ control**: at θ = 1/3 the machinery must return
T = 1/3 exactly and s = 0; at θ = 1 it must return T = 1 (the trivial all-curves case with
g = 0). Both are free known-answer gates. **Sign control**: the smoothness credit s must be
non-negative and must vanish in the exponent for every B = p^{o(1)}; if the arithmetic
returns a positive exponent-scale s, the accounting has confused an o(1) with an exponent,
which is exactly the error the goal record says is "refuted at the whiteboard".

**Falsifier (reachable)** — F5-a: T(θ) ≥ 1/3 for all θ < 1/3 under both α values →
the lever is CLOSED with a mechanism (the density exponent α is never large enough to pay
for the threshold reduction). F5-b: T(θ) < 1/3 for some θ under α = 2 → the lever is OPEN
and the deciding measurement is REC-1's α, already scheduled; this catalogue then routes to
it rather than duplicating it. F5-c: s(θ) is found to carry an exponent → either B is not
p^{o(1)} in the variant being costed (in which case say so and re-cost), or the arithmetic
is wrong.

**Cost** — implementation: none. compute: none. Half an hour of algebra plus a table.

**Ceiling** — No claim tier: this is an arithmetic identity plus two anchored fits, and the
α input is owned by REC-1, whose own data is **SUB-TOY** (log2 p ≤ 18) and
falsification-only by the goal record's explicit instruction. Nothing here may be cited as
support for α; only as a refutation if α disagrees.

**Kills-it-early** — Evaluate T(1/4) under α = 3/2: 1/4 + 1/8 = 3/8. One line. If the
reader accepts α = 3/2, the lever is closed before anything else is done.

**Method ceiling** — *What would have to be true:* α ≥ 2, i.e. the Deuring lattices carry
short vectors more often than Siegel equidistribution predicts. *Strongest ever
supportable:* T(1/4) = 1/4 **at α = 2 exactly, and never below**, because g ≥ 0 always and
θ = 1/4 is the target. So this lever's ceiling *meets* the goal's target and does not beat
it — that is worth saying plainly. *Nearest obstruction:* for a rank-3 positive-definite
form the number of vectors of norm ≤ T is (4π/3)T^{3/2}/√det + O(T), and at T = p^{1/4} the
main term is p^{-1/8} ≪ 1, so the regime is entirely fluctuation-governed; α = 2 requires
the *family* of Deuring lattices to be non-Siegel, not any single lattice to be unusual.
*Nearby-object control:* the random-ternary-form arm of C1-3, which is Siegel by
construction; if the fitted α agrees there and on the Deuring arm, α = 3/2 stands and the
lever closes. *Cheap pre-compute falsification:* the T(1/4) = 3/8 line above.

---

### C1-6. Factorisation-shape-restricted listable families: compute the exchange rate from Dickman/CEP instead of measuring it

**Which factor** — F3 (list cardinality). This is lever L2 / A4 rendered in the smoothness
idiom, and it is proposed **because** the goal record's correction says the generic
exchange rate is e = 2δ, i.e. worse than the 1:1 the original obstruction field assumed,
with both nulls (independent, aligned) pre-computed.

**Claim** — Restricting the listable degree set to a factorisation *shape* class F —
squarefree degrees; degrees with exactly k prime factors; degrees all of whose prime
factors lie in a dyadic band [B/2, B]; degrees with a prescribed Ω or ω — shrinks the list
by a factor computable in closed form from Dickman/CEP-type asymptotics, and shrinks the
hit probability by a factor computable from the same asymptotics. **The exchange rate for
every such shape class is therefore decidable at the whiteboard, not by measurement**, and
the decisive question is whether the *target's* shape distribution is biased toward F
relative to a uniform smooth integer. Prediction: exchange rate ≥ 1 (no gain) for every
shape class defined purely multiplicatively, with the single possible exception of classes
favoured by the ternary form's local densities (C1-4's mechanism).

**Mechanism** — For a uniform B-smooth n ≤ D the number of prime factors is
asymptotically Poisson–Dickman; the density of the shape class and the density of the hit
set are governed by the *same* law, so restricting to a p^{-δ} fraction of the list costs a
p^{-δ} fraction of the hit probability unless the target's law differs from the list's law.
This is the exact content of "the exchange rate is the whole question": here it is
computed rather than asserted, and the only route to e < 1 is a **measured** shape bias in
the target, which is C1-4's Euler-product correction seen from the other side.

**Minimal discriminating test** — (1) For each of five shape classes, write the list-side
count (Σ_{d ∈ F, d ≤ X} d) and the hit-side probability (Pr[deg φ ∈ F | deg φ B-smooth])
under the uniform-integer model, and tabulate the exchange rate at NIST-I parameters.
(2) On C1-7's sample, measure the empirical shape distribution of deg φ_min and compare to
the uniform-smooth-integer prediction, class by class. The discriminator is whether any
class shows a bias exceeding its own list-shrinkage.

**Null object / control** — **Aligned and independent nulls, both pre-computed** (carried
from the goal record's A4 correction): independent gives worse than 1/3; aligned gives
exact break-even at 1/3 for every δ. A measured class must beat *aligned* to be a lever at
all, and any reported gain that lands between the two nulls is reported as within-null.
**Matched-uniform shape arm** from C1-4 supplies the reference distribution.

**Falsifier (reachable)** — F6-a: every class's exchange rate ≥ 1 in the closed-form
computation → CLOSED with a mechanism and a forward-guidance list (what remains: classes
defined by *non-multiplicative* data, e.g. congruence classes of the represented value,
which is C1-4's territory). F6-b: some class has computed exchange rate < 1 but the
measured target bias is inside the aligned null → the gain is a modelling artifact.
F6-c: some class has exchange rate < 1 **and** the measured bias exceeds the aligned null →
a genuine restricted-family lever, to be costed against the per-entry cost of enumerating
that class (which may itself eat the gain, and must be charged).

**Cost** — implementation: low (closed-form sums + a shape histogram on C1-7's sample).
compute: minutes.

**Ceiling** — `medium` for the measured shape histogram; the closed-form arm carries no
tier and is a derivation.

**Kills-it-early** — Squarefree degrees: the list shrinks by 1/ζ(2)·(smooth correction) and
the hit probability shrinks by essentially the same factor. If the two agree to within the
computation's own precision, the archetype of the whole class is break-even and the
remaining classes need a specific reason to differ.

**Method ceiling** — *What would have to be true:* the target's factorisation shape is
biased toward some cheaply-enumerable class. *Strongest ever supportable:* a constant-factor
(bit-scale) reduction in M at fixed P0 — **never an exponent**, because any class of
relative density p^{-δ} that is hit with probability p^{-δ'} contributes exponent
δ' − δ ≥ 0 unless the bias exponent is strictly positive, and a multiplicatively-defined
class cannot have a p-power bias for an integer that CEP models as uniform. *Nearest
obstruction:* the aligned null gives exact break-even at 1/3 for every δ — already computed
in BATCH-001 — so any claimed gain must be shown to beat break-even, not merely to be
positive. *Nearby-object control:* the same shape measurement on uniform integers of the
same size (C1-4's null). *Cheap pre-compute falsification:* the squarefree archetype above.

---

*(Ideas C1-7 through C1-13 and the batch plan continue below.)*
