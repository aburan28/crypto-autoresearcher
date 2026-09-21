# C1 — GOAL-SSIQ-001 idea catalogue: the smoothness / table-construction side of the exponent budget

Slice: levers on **smoothness probability**, **modular-polynomial evaluation**,
**table-construction cost**, and the **Dickman/CEP-type distributional inputs** of the
archived p^{1/3+o(1)} algorithm (`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, cited by
line `L<n>`). C2 owns search / collision / memory; nothing here proposes a change to claw
finding, to list comparison, or to the van Oorschot–Wiener curve.

**No idea below claims p^{1/4}, an exponent under 1/3, a break, or a completion.** Ceilings
are `toy` or `medium`. Novelty is not adjudicable in this session: nothing is claimed new
and nothing is dismissed as known.

## 0. Frame

### 0.1 Off-limits as the primary lens

- **OL-1** Generic claw finding / meet-in-the-middle over the two keyed lists — C2's slice.
- **OL-2** vOW memory tradeoff (L39). Lever L5: recorded for honesty, not prioritised.
- **OL-3** Re-deriving GOAL-P13-001's per-entry cost measurement. EV-PEC-2e67ff and
  EV-PEC-857664 are **inputs**, cited, never re-derived (GOAL-SSIQ-001 `related_goals_note`).
- **OL-4** Minkowski/Hermite bounds on the degree lattice — L1 is CLOSED-IN-SCOPE (D1), and
  its obstruction field was already corrected as a category error twice over.

### 0.2 Tracked object and the lossy-projection test

**TO-MULT.** The *multiplicative type* of the target degree:
`(E, φ_min : E → E^{(p)}) ↦ multiset of prime factors of deg(φ_min)`, plus its divisor lattice.

- **Lossy?** Yes, and structurally so. It collapses every isogeny of a given degree to one
  point; the fibre over degree d from a fixed E has ≈ d·∏_{ℓ|d}(1+1/ℓ) elements (L133; L230
  "the number of isogenies of degree d is at least d"). **That fibre size is exactly factor
  F3** — the quadratic factor that makes memory equal time. The discarded data is precisely
  what C2 tracks; the retained data is precisely this slice's.
- **Compatible with the target's operations?** Yes. deg is multiplicative under composition,
  so TO-MULT propagates deterministically along Algorithm 1's extension steps (L137–L152):
  appending an ℓ-isogeny adjoins ℓ, independent of *which* ℓ-isogeny. Algorithm 2's decision
  procedure — list by (degree, smoothness), split at a divisor ≤ X (L167, L177–L185) —
  factors entirely through TO-MULT.
- **Not a change of coordinates.** E, φ and the codomain are unrecoverable from the multiset;
  the fibre is exponentially large. Contrast `KN-LIT-7595`'s (Δ, Π), where the pair was
  recoverable and nothing was gained.
- **Consequence used throughout.** Correctness lives entirely in TO-MULT while cost lives
  partly in the fibre, so a lever moving TO-MULT's hit probability without touching the fibre
  is not a repackaging of a C2 lever.

### 0.3 The one fact that bounds this whole slice

From the paper's assembly (L210–L218) and BATCH-001's re-derivation:
`X = (B·D)^{1/2}` exactly (L167) ⟹ `M ≈ X² = B·D`, `D = (p/2)^{1/3}` (L81);
`time ≈ M/P0`, `P0 = u^{−u(1+o(1))}`, `u = log(p/2)/(3 log B)` (L69, L187).

> **CEILING-SLICE (binds every idea below).** With B = p^{o(1)} and D = p^{1/3}, no lever on
> smoothness probability, on Ψ(X,B), on modular-polynomial evaluation, or on table cost can
> move the time exponent below 1/3. F4 carries exponent 0 (confirmed and strengthened in
> BATCH-001); F5/F7/F8 carry exponent 0. What this slice *can* move is (i) **the shape of the
> o(1)** — the paper's own headline caveat, a "superpolynomial overhead hiding in the o(1)"
> (L13, L39) — and (ii) **charged concrete cost**. Only C1-3 and C1-5 touch an exponent, both
> through D rather than smoothness, and both are audited to a **negative** ceiling.

Stating this first is the goal's purpose, not a hedge: two of the thirteen are ceiling
arguments whose expected verdict is CLOSED, and a failed audit is a useful result
(`docs/inventor-protocol.md` §8).

### 0.4 Committed state that must not be redone

- §4.1's one-op-per-entry convention (L230) is **REFUTED in the attack's disfavour** at the
  tested scale: 1843.5–94023.4 counted multiplications per entry over 2 ≤ ℓ ≤ 211 at
  p ~ 2^40; seam-free γ_A = 0.9328644281, γ_B = γ_{S-MIN} = 0.8100336227; ℓ-independent
  structural prefactor 2^8.92 (EV-PEC-2e67ff OBS-C/D; EV-PEC-857664 OBS-G). **Medium tier.**
- `c` is citable **only** as the bracket [1.327077, 1.576444] at NIST-I, never as a number
  (DEC-20260802-48c72c).
- **FC-4 (MECHANISM-INCONSISTENT) FIRED**, driven by ℓ ∈ {3,5} (EV-PEC-857664 OBS-K); a
  post-hoc ℓ-restriction cannot lift it. Every cost-model idea below carries it.
- Binding phrasing: "the fitted per-entry cost curve, **evaluated at ℓ = B_opt**, is 21.2 to
  25.2 bits above §4.1's convention" — never "the measured prefactor is 2^9.73" (CORR-3).
- IDEA-20260803-48e258 owns the crossover curve p*(w). C1-2, C1-11, C1-12 are marked
  **successors**: that record fixes the cost law and varies (p, w); these vary **B** and the
  **per-entry cost model**.

---

## 1. The thirteen ideas

### C1-1. Divisor-in-window split: replace the worst-case greedy bound X = (BD)^{1/2} by X = λ·D^{1/2}

**Which factor** — F2 (split exponent) and through it F3. X enters as M ≈ X² = B·D (L167,
L177–L185). The factor B in M comes **only** from the worst-case greedy split, not from
smoothness; removing it removes a factor B from time *and* memory and changes the o(1)'s shape.

**Claim** — Lemma 3.4's proof bounds deg η ≤ ℓ_{k+1}·D/X ≤ B·D/X by charging the largest
possible prime at the greedy boundary, then sets X = (BD)^{1/2} so the worst case fits. For a
**typical** B-smooth n ≈ D, divisors near √n are far denser than one per multiplicative factor
B. Replacing the universally quantified split by the existentially quantified condition —
*deg φ has a divisor in [deg φ/X, X]* — permits X = λ·D^{1/2} with λ conjecturally O(1) to
(log p)^{O(1)}, at the cost of a success factor q = Pr[divisor in window]. Predicted at
NIST-I under the paper's own §4.1 model: M falls 2^{94.1} → ≈2^{80}–2^{83}, time 2^{106.5} →
≈2^{91}–2^{93}: **9–14 bits memory, 13–15 bits time, exponent unchanged at 1/3.**

**Mechanism** — Restated correctness lemma, strictly weaker hypothesis: *if deg φ is B-smooth
**and** has a divisor a with deg φ/X ≤ a ≤ X, Algorithm 2 returns φ.* Cyclicity is unaffected:
for cyclic φ of degree n every divisor a | n gives a unique φ = η∘ψ with deg ψ = a, both
cyclic (L177, minimality ⟹ cyclic kernel). The window density is the classical
Erdős multiplication-table / Ford quantity: for a dyadic window,
H(x,y,2y)/x ≍ (log y)^{−δ}(log log y)^{−3/2}, δ = 1 − (1+log log 2)/log 2 ≈ 0.086. For
**B-smooth** n the divisor set is denser: n ≤ D has ≈ u prime factors near B and ≈ 2^{ω}
divisors whose logarithms concentrate near (log n)/2 with spread ≈ (√ω/2)·log B, so the
expected divisor count in a log-window 2 log λ is ≈ 2^{ω}·2 log λ/√(2πV) and **grows with u** —
the opposite of the direction that would kill the idea. The X-tightening axis is already live
in the source: L87 credits Basso with "a tighter choice of X ... (replacing B with √B)".

**Minimal discriminating test** — Pure integer arithmetic; no curve, no isogeny.
(1) For D ∈ {2^40, 2^48, 2^56} and B bracketing D^{1/u}, u ∈ {3,4,6,8}, enumerate/sample
B-smooth n ∈ [D/2, D] and measure q(λ) = Pr[n has a divisor in [n/(λ√D), λ√D]] for
λ ∈ {1, 2^{1/4}, 2^{1/2}, 2, 4, √B}. (2) Recompute §4.1's rows at NIST-I/III/V with X' = λ√D,
reporting M, P0·q, time and **peak memory** beside the unmodified rows, under (a) the 1-op
convention and (b) the committed measured law charged at ℓ = B_opt with `c` as bracket only.
(3) Re-optimise B jointly with λ.

**Null object / control** — (i) **Matched uniform-integer null**: identical q on uniform
integers in [D/2, D]. If q_smooth ≈ q_uniform, the "smooth numbers have denser divisors"
mechanism is not doing the claimed work and the claim retreats to the generic Ford density —
report which. (ii) **λ = √B known-answer gate**: q must be exactly 1.000 at every sampled n;
anything else falsifies the instrument, not the idea. (iii) **Decay tell**: q must increase
monotonically in λ and decrease as u increases at fixed λ; a q that does not move with λ is
the canonical artifact signature.

**Falsifier (reachable)** — F1-a q(λ) below its pre-registered Ford-derived threshold for all
λ with λ² ≤ B^{1/2} → lever buys < 2 bits, CLOSED as a concrete lever. F1-b q **decreases** in
u → the gain shrinks as p grows and the o(1)-shape claim fails. F1-c the re-costed table under
the measured law is not better at any (λ,B) → charged away. F1-d a counterexample to the
restated correctness lemma (a window divisor whose induced ψ is absent from L(E,X',B) for a
reason other than degree) → killed at the whiteboard.

**Cost** — impl: low (~150 lines pure Python: smooth enumeration, divisor enumeration, window
test). compute: minutes to ~1 CPU-hour. No SageMath, no network, no modular polynomials.

**Ceiling** — `medium` at best for the arithmetic; the NIST rows are a **model substitution
carrying no claim tier** (EV-PEC-857664 OBS-M discipline).

**Kills-it-early** — Enumerate all B-smooth n in one decade at D = 2^40, B = 2^7; count those
with a divisor in the dyadic window at √n. Below ≈0.05 the idea is a ≤2-bit lever. Ten minutes.

**Method ceiling** — *Would have to be true:* the divisor-window density for the specific
integer deg φ_min is Θ(1) (or (log p)^{−O(1)}) at λ = p^{o(1)}. *Strongest ever supportable:*
time and memory p^{1/3}(log p)^{O(1)}·ρ(u/2)/ρ(u) — **removal of the superpolynomial o(1)**,
but only if B can simultaneously reach p^{Θ(1)} (that is C1-2, separate and harder). It can
**never** move the exponent: M ≥ X² ≥ D = p^{1/3} since the two lists must jointly cover a
degree-D isogeny and λ ≥ 1. *Nearest obstruction:* Ford gives only a
(log y)^{−0.086}(log log y)^{−3/2} density for **uniform** integers at a dyadic window — a
log-power, not a constant — so Θ(1) rests on a smooth-number strengthening about the
concentration function of log-divisors of smooth integers, which CEP does not supply.
*Nearby-object control:* the uniform-integer arm; a method that cannot separate "smooth n"
from "uniform n" on this statistic has not found the load-bearing structure. *Cheap
pre-compute falsification:* the λ = √B gate, plus the whiteboard bound q ≤ 1 ⟹ total ≥ D.

---

### C1-2. The self-consistent smoothness bound: solve B* = M(B*)^{1/4} from per-prime Φ_ℓ amortisation

**Which factor** — F5 (B) and F3 jointly. B carries no exponent but sets Ψ(X,B), P0, X and the
whole o(1). The proof fixes B = e^{(1/3)√log(p/2)} (L193); L200 notes "in practice, one may
instead precompute an optimal choice of B minimizing the total expected cost". The committed
log2 B_opt = 14.2 (RUN-WESOVOW-001) is a **numerical** optimum whose governing constraint has
never been written down.

**Claim** — The binding constraint on B is a **per-prime affordability condition**, not the
u^{−u} balance alone: ℓ is admissible only if its modular polynomial's cost, amortised over
the entries using it, fits the per-entry budget. Precompute-and-amortise ⟹ ℓ⁴ ≲ M ⟹ the fixed
point B* = M(B*)^{1/4}; per-specialisation ⟹ per-entry Θ̃(ℓ) and a much smaller B*.
**The two models disagree by 6+ octaves in B* and the exponent budget records neither.**
Prediction: (precompute, idealised) B* ≈ 2^{20}–2^{21} at NIST-I with u ≈ 4.3, P0^{−1} ≈ 2^{8.3};
(per-specialisation, idealised) B* falls back toward 2^{14.2}; under the **measured** law, lower.

**Mechanism** — Entries divisible by ℓ are a ≈1/ℓ fraction of M, so Φ_ℓ's Θ̃(ℓ³) construction
amortises to ℓ⁴/M per entry; ≤ 1 gives ℓ ≤ M^{1/4}. Its Θ̃(ℓ²) storage is ≤ M^{1/2} ≪ M, so
storage is not binding **relative to a table this program already calls astronomical** — a
statement admissible only in relative terms. Algorithm 1's outer loop is `for ℓ ≤ B` (L143),
so exactly one Φ_ℓ is live at a time, which is what legitimises the amortisation.

**Minimal discriminating test** — Zero compute beyond arithmetic on committed constants.
(1) Write the fixed point under each Φ model × each cost law (§4.1 convention; measured law
with `c` as bracket only), giving four (B*, M, P0, time, peak memory) rows at log2 p ∈
{256, 384, 512, 576, 768}. (2) **Known-answer gate**: the (per-specialisation, §4.1) cell must
reproduce log2 B_opt = 14.2 and the five published rows (L234–L238) within the 2.2309-bit
NIST-I irreproducibility band. Machinery that cannot reproduce the point it generalises is
void. (3) Report d(log2 time)/d(log2 B) at each cell so sensitivity, not just the optimum, is
visible.

**Null object / control** — **Null-baseline**: recompute every cell with the amortisation
constraint removed (B unbounded above). The optimum must move materially; if it barely moves,
the constraint is not doing the claimed work and the idea is re-described as a restatement of
the existing numerical optimisation. **Adversarial corner**: evaluate at the corner of the `c`
bracket and γ readings most favourable to the attack, reported explicitly.

**Falsifier (reachable)** — F2-a known-answer gate fails → void. F2-b B* under every model
within one octave of 2^{14.2} → bookkeeping note, not a lever. F2-c under the measured law the
total is monotone decreasing in B down to the smallest admissible B → no interior optimum, the
framing is wrong. F2-d the 1/ℓ entry density is contradicted — this is exactly RT3-C1's
entry-weighting effect, already priced at 0.60–1.00 bits **pro-attack**, and it must be carried
signed, never absorbed.

**Cost** — impl: low (arithmetic + a fixed-point root-finder). compute: none. Successor to
IDEA-20260803-48e258 on the B axis; that record's fitted-window guard and undefined-segment
discipline are inherited verbatim.

**Ceiling** — No claim tier. Every row is a **model substitution** under the committed
assumption set (EV-PEC-857664 OBS-M).

**Kills-it-early** — Envelope check at NIST-I: if M^{1/4} at M ≈ 2^{92.5} gives B* ≈ 2^{23} but
the measured law at ℓ = 2^{23} charges > 25 bits, the idea reduces to "the Φ model decides
everything" (= C1-11) and should be folded into it rather than run separately.

**Method ceiling** — *Would have to be true:* per-prime amortisation, not the smoothness
balance, binds B, and per-entry cost at B* is Θ̃(1). *Strongest ever supportable:* closed forms
for B*(p) and for the incumbent's o(1) — **not an exponent**, and that must appear on the face
of the deliverable. *Nearest obstruction:* the committed identifiability limit — "the
experiment cannot discriminate between per-entry cost laws that agree over ℓ ≤ 211 and diverge
at ℓ ~ 2^{14}" (EV-PEC-2e67ff `boundaries`) — and C1-2 makes the relevant ℓ **larger**, so it
widens that gap. Stated here rather than discovered later. *Nearby-object control:* apply the
same derivation to the committed C-NULL object, whose per-entry cost is O(1) in ℓ by
construction; it must return "no constraint on B", and a finite B* there means the derivation
manufactures one. *Cheap pre-compute falsification:* the known-answer gate.

---

### C1-3. Remark 1 multiplicity, priced against the Siegel–Rogers short-vector count

**Which factor** — F4 at its interface with F1. Remark 1 (L191) records that there are
"generally multiple small (non-cyclic) isogenies E → E^{(p)}", that any one being smooth
suffices, that Panny observed it, and that it "is absorbed in the hidden term". Nobody here has
checked what it is worth or whether the absorption is right.

**Claim** — On the Siegel–Rogers heuristic for the governing rank-3 trace-zero lattice of
discriminant p/4 (BATCH-001's corrected object), the count of isogenies of degree ≤ T is
N(T) ≈ κ·T^{3/2}/p^{1/2}: N(D) = Θ(1) at D = (p/2)^{1/3}, consistent with Theorem 1.5 (L81),
and N(p^{1/3+ε}) ≈ p^{3ε/2}. So multiplicity is **exponent-neutral at best and negative in
practice** — raising the threshold to p^{1/3+ε} multiplies M ≈ B·T by p^{ε} while multiplying
P0 by at most p^{o(1)}, since P0^{−1} is already p^{o(1)}. Expected verdict: **CLOSED as an
exponent lever, OPEN as an o(1) lever worth an explicitly computed number of bits.**

**Mechanism** — Two readings, and the idea exists to separate them. *A (independent):* the
N(T) degrees are multiplicatively independent, P0(T) ≈ N(T)·ρ(u_T), Remark 1 worth log2 N bits.
*B (dependent):* they are values of one ternary form at nearby lattice points under shared
congruence conditions, so smoothness events are positively correlated and Remark 1 is worth far
less. B is not speculative: EV-WESO-001 already records "one constant-factor signed bias
against smoothness identified (ramified small primes demote L(1,χ) Euler factors)".

**Minimal discriminating test** — Rides C1-7's sampler. Per sampled order, enumerate **all**
vectors of norm ≤ κ·D rather than only the shortest; record the norm vector; measure (a) N(T)
against κT^{3/2}p^{−1/2}, (b) Pr[at least one norm B-smooth] against both readings, (c) pairwise
correlation of the smoothness indicators.

**Null object / control** — **Random-lattice null**: identical enumeration and smoothness
measurement on random positive-definite ternary forms of discriminant p/4 with no quaternion
provenance. Reading A is the null's own prediction, so agreement with the null supports A and
disagreement is the structural signal for B. This is the null the goal record already
pre-registered for REC-1, reused not reinvented. **Artifact tell**: N(T) must scale as T^{3/2};
a measured 2 is either the α = 2 alternative the goal record names or an enumerator bug, and the
two separate on the null arm.

**Falsifier (reachable)** — F3-a exponent ≠ 3/2 on **both** arms → instrument failure, no
disposition. F3-b 3/2 on the null and ≈2 on the Deuring arm → Deuring lattices are not
Siegel-equidistributed; a genuine structural finding that independently **reopens L1's second
disjunct at exactly 1/4** per the goal record's pre-committed reversion. F3-c Reading A and
log2 N(D) < 1 → Remark 1 is worth under a bit, absorption vindicated, lever CLOSED with a
number. F3-d Reading B → a measured correlation that **weakens** the incumbent's P0, i.e. moves
against the attack.

**Cost** — impl: medium (shares C1-7's sampler; adds ~120 lines of rank-3 Fincke–Pohst on 3×3
Gram matrices with entries ~p). compute: ≤2 CPU-hours on top of C1-7.

**Ceiling** — `medium`, and only about the sampled distribution at the sampled p. Never
crypto-scale isogeny evidence: no isogeny is computed anywhere.

**Kills-it-early** — Evaluate κ·D^{3/2}/p^{1/2} at D = (p/2)^{1/3}. If below 2, Reading A's
ceiling is < 1 bit and the lever closes before any sampling.

**Method ceiling** — *Would have to be true:* multiplicity gains more than threshold-raising
costs. *Strongest ever supportable:* with M ≈ B·T and P0 ≈ N(T)ρ(u_T), the optimum in T sits
where d log N/d log T = 1, i.e. 3/2 = 1 — **never satisfied** — so the optimum is at the
smallest admissible T and raising T is strictly bad. A one-line closure with a named mechanism,
and the expected outcome. *Nearest obstruction:* the exponent 3/2 is rank/2 for a rank-3 form;
changing it means changing the rank, which is lever N5, not this one. *Nearby-object control:*
the random-form null. *Cheap pre-compute falsification:* the derivative argument above.

---

### C1-4. Is the CEP/Dickman model's local-density correction for the ternary form constant, or u-dependent?

**Which factor** — F4, through Heuristic 1's distributional input (L69), and therefore every
margin row identically.

**Claim** — Heuristic 1 asks that deg φ_min "has the smoothness probability that one would
expect for a random integer of its size" (L83), justified by composing Theorem 1.5 (L81) with
Theorem 1.4 (CEP, L77). But deg φ_min is the **value of a positive-definite ternary quadratic
form of discriminant p/4 at its shortest vector**, not a random integer; such values obey local
conditions at primes dividing 2·disc and their smoothness law carries an Euler-product
correction with local densities δ_ℓ. To decide: **is the correction a constant C(p), independent
of u (harmless — absorbed into the o(1) with a computable bit count), or u-dependent (not
harmless — it reshapes the tail exactly where Heuristic 1 is used)?**

**Mechanism** — If the local factors deviate from 1 summably, the change to Pr[B-smooth] is a
bounded constant uniform in u. If small primes are systematically **demoted** (the L(1,χ)
Euler-factor effect already identified in EV-WESO-001), then B-smooth values — which are built
from many small primes — are penalised in proportion to how many they need, i.e. **in
proportion to u**, giving C^{u} rather than C. The two are separable at the whiteboard by
writing the Euler product and at the bench by a u-ladder.

**Minimal discriminating test** — *Arm 1 (zero compute):* write Pr[form-value B-smooth] as
ρ(u)·∏_{ℓ≤B}(local factor); determine whether the product's logarithm is Θ(1) or Θ(u) at
u ≈ 4–13, and state the sign. *Arm 2 (rides C1-7):* measure R(u) = p̂(u)/ρ(u) at every rung of
a pre-registered B-ladder and fit log R against u. **The discriminator is the slope**: ≈0 ⟹
constant; ≠0 ⟹ u-dependent, sign says which way.

**Null object / control** — **Matched uniform-integer arm** at the same size and count through
the identical pipeline, so the finite-size error of the ρ reference is measured rather than
assumed; this is H-LPF-001's ABS-REL clause inherited verbatim, and if the uniform arm leaves
its band at a rung then **the absolute limb is not decidable at that rung by this apparatus**.
**Random-ternary-form arm** of the same discriminant: a departure on both is a ternary-form
effect; a departure only on the Deuring arm is a Deuring effect.

**Falsifier (reachable)** — F4-a slope indistinguishable from zero across ≥4 rungs at ≥2 primes
→ correction is constant; CLOSED as an o(1)-shape question, survives only as a bit count.
F4-b slope significantly negative → target **rougher** than uniform, P0 overstated, incumbent
cost understated: **against the attack**. F4-c slope significantly positive → target
**smoother**, P0 understated: **for the attack**. F4-d the uniform arm fails its own band →
apparatus statement only, no disposition.

**Cost** — impl: low if it rides C1-7 (a fit and a ladder); Arm 1 is paper-only. compute: none
beyond C1-7.

**Ceiling** — `medium`. A departure at one p is a statement about that p; a u-dependence claim
needs ≥2 primes to be a claim about u at all.

**Kills-it-early** — Write the local factor at ℓ = 2 and ℓ = 3 for the standard maximal order at
p ≡ 3 mod 4. If both are 1 + O(1/ℓ) with no systematic sign, the Θ(u) branch has no mechanism
and Arm 2 is a confirmation exercise, not a discriminator.

**Method ceiling** — *Would have to be true:* the deviation from the uniform-integer law is
large enough to matter at the operating u. *Strongest ever supportable:* a signed, quantified
correction ρ(u)·C or ρ(u)·C^{u} — which moves the o(1) and every margin row identically and
**never the exponent** (F4 carries exponent 0). *Nearest obstruction:* CEP (L77) is a theorem
about integers below X; there is no correspondingly uniform theorem for values of a ternary
form at a shortest vector, so the absolute limb can be tested against ρ but never proved.
*Nearby-object control:* the random-ternary-form arm — the closest object with the ternary
structure but without the Deuring structure. *Cheap pre-compute falsification:* the ℓ = 2, 3
local factors.

---

### C1-5. The threshold–smoothness exchange curve T(θ) = θ + g(θ) − s(θ)

**Which factor** — F1 and F4 jointly. The only place in this slice where an exponent can move,
and the audit's expected verdict is that it moves the wrong way.

**Claim** — Accept only curves with δ_E ≤ p^{θ}, θ ≤ 1/3, re-randomising until one is found
(L193, L202). Then total time exponent = θ + g(θ) − s(θ), with g(θ) = −log_p Pr[δ_E ≤ p^{θ}]
and s(θ) ≥ 0 the credit from the improved smoothness of a smaller target (u = θ log p/log B
falls with θ, so ρ(u) rises). **s(θ) ≡ 0 in the exponent whenever B = p^{o(1)}**: the smoothness
credit is real, is worth bits, and is worth **no exponent**. Prediction: with BATCH-001/Siegel
g(1/4) = 1/8, T(1/4) = 3/8 > 1/3 = T(1/3) — CLOSED, unless the density exponent α is 2 rather
than 3/2, in which case g(1/4) = 0 and T(1/4) = 1/4 exactly, which is the goal record's own
pre-committed reversion condition.

**Mechanism** — #{E : δ_E ≤ T} = c·T^{α}·p^{β}, anchored at T = 1 by the p^{1/2} F_p-locus size
(β = 1/2) and at θ = 1/3 by Theorem 1.5 (the fit must go vacuous there). α = 3/2 is the
Siegel–Rogers/volume prediction for rank 3; α = 2 is the ingredient-(c) failure mode the goal
record names. This is the **smoothness-side successor** to REC-1 and does not duplicate it:
REC-1 measures the size distribution only, while the exchange curve additionally needs s(θ) and
the conditional smoothness law at lowered θ, which REC-1's design cannot produce.

**Minimal discriminating test** — Zero compute. (1) Tabulate T(θ) = θ + max(0, 1/2 − αθ) over
θ ∈ [1/5, 1/3] for α ∈ {3/2, 2} with both anchors enforced. (2) Add s(θ) explicitly, prove
s ≡ 0 in the exponent for B = p^{o(1)}, then compute the **bit-scale** smoothness credit at
NIST-I for θ ∈ {1/4, 0.28, 0.30} beside the exponent cost, so the two are never confused again.
(3) State the exact numeric condition on α at which T(1/4) = 1/3, i.e. what REC-1 would have to
return to reopen the lever.

**Null object / control** — **Degenerate-θ gates**: at θ = 1/3 the machinery must return
T = 1/3 and s = 0; at θ = 1 it must return T = 1. Both free. **Sign control**: s must be
non-negative and must vanish in the exponent for every B = p^{o(1)}; a positive exponent-scale s
means the accounting has confused an o(1) with an exponent — the error the goal record calls
"refuted at the whiteboard".

**Falsifier (reachable)** — F5-a T(θ) ≥ 1/3 for all θ < 1/3 under both α → CLOSED with a
mechanism. F5-b T(θ) < 1/3 for some θ under α = 2 → OPEN, and the deciding measurement is
REC-1's α, already scheduled; this catalogue routes to it rather than duplicating it.
F5-c s(θ) found to carry an exponent → either B is not p^{o(1)} in the variant being costed (say
so and re-cost) or the arithmetic is wrong.

**Cost** — impl: none. compute: none. Half an hour of algebra plus a table.

**Ceiling** — No claim tier: an arithmetic identity plus two anchored fits. The α input is
REC-1's, whose data is **SUB-TOY** (log2 p ≤ 18) and falsification-only by the goal record's
explicit instruction; nothing here may cite it as support for α, only as refutation if it
disagrees.

**Kills-it-early** — Evaluate T(1/4) under α = 3/2: 1/4 + 1/8 = 3/8. One line, and if α = 3/2 is
accepted the lever is closed before anything else is done.

**Method ceiling** — *Would have to be true:* α ≥ 2, i.e. Deuring lattices carry short vectors
more often than Siegel equidistribution predicts. *Strongest ever supportable:* T(1/4) = 1/4 at
α = 2 exactly and **never below**, since g ≥ 0 always — so this lever's ceiling *meets* the
goal's target and does not beat it, which is worth saying plainly. *Nearest obstruction:* for a
rank-3 positive-definite form the count of vectors of norm ≤ T is (4π/3)T^{3/2}/√det + O(T), and
at T = p^{1/4} the main term is p^{−1/8} ≪ 1, so the regime is entirely fluctuation-governed;
α = 2 requires the **family** to be non-Siegel, not any single lattice to be unusual.
*Nearby-object control:* the random-ternary-form arm of C1-3, Siegel by construction; agreement
of fitted α on both arms closes the lever. *Cheap pre-compute falsification:* the T(1/4) = 3/8
line.

---

### C1-6. Factorisation-shape-restricted listable families: compute the exchange rate from Dickman/CEP rather than measuring it

**Which factor** — F3. Lever L2 / A4 in the smoothness idiom, proposed **because** the goal
record's correction says the generic exchange rate is e = 2δ — worse than the 1:1 the original
obstruction field assumed — with both nulls (independent, aligned) pre-computed.

**Claim** — Restricting the listable degree set to a factorisation *shape* class F — squarefree;
exactly k prime factors; all prime factors in a dyadic band [B/2, B]; prescribed Ω or ω —
shrinks the list by a factor computable in closed form from Dickman/CEP-type asymptotics and
shrinks the hit probability by a factor computable from the same asymptotics. **Every such
exchange rate is therefore decidable at the whiteboard, not by measurement**, and the only
decisive question is whether the *target's* shape distribution is biased toward F relative to a
uniform smooth integer. Prediction: exchange rate ≥ 1 for every purely multiplicatively defined
shape, with the sole possible exception of classes favoured by the ternary form's local
densities (C1-4's mechanism seen from the other side).

**Mechanism** — For a uniform B-smooth n ≤ D the prime-factor count is asymptotically
Poisson–Dickman, and the density of the shape class and the density of the hit set are governed
by the **same** law, so restricting to a p^{−δ} fraction of the list costs a p^{−δ} fraction of
the hit probability unless the target's law differs from the list's law. That is the exact
content of "the exchange rate is the whole question", here computed rather than asserted.

**Minimal discriminating test** — (1) For five shape classes write the list-side count
(Σ_{d ∈ F, d ≤ X} d) and the hit-side probability (Pr[deg φ ∈ F | deg φ B-smooth]) under the
uniform-integer model, tabulating the exchange rate at NIST-I parameters. (2) On C1-7's sample,
measure the empirical shape distribution of deg φ_min class by class against the
uniform-smooth-integer prediction. Discriminator: does any class show a bias exceeding its own
list-shrinkage?

**Null object / control** — **Aligned and independent nulls, both pre-computed** (carried from
the goal record's A4 correction): independent gives worse than 1/3, aligned gives exact
break-even at 1/3 for every δ. A class must beat **aligned** to be a lever at all; any reported
gain between the two nulls is reported as within-null. **Matched-uniform shape arm** from C1-4
supplies the reference distribution.

**Falsifier (reachable)** — F6-a every class's exchange rate ≥ 1 in closed form → CLOSED with a
mechanism plus forward guidance (what remains: classes defined by **non-multiplicative** data,
e.g. congruence classes of the represented value — C1-4's territory). F6-b some class computes
< 1 but the measured target bias is inside the aligned null → modelling artifact. F6-c a class
computes < 1 **and** the measured bias exceeds the aligned null → a genuine restricted-family
lever, to be charged against the per-entry cost of enumerating that class, which may itself eat
the gain.

**Cost** — impl: low (closed-form sums + a shape histogram on C1-7's sample). compute: minutes.

**Ceiling** — `medium` for the measured histogram; the closed-form arm carries no tier and is a
derivation.

**Kills-it-early** — Squarefree degrees: list shrinks by ≈1/ζ(2) with a smooth correction, hit
probability shrinks by essentially the same factor. If the two agree within the computation's
own precision, the archetype of the whole class is break-even and the rest need a specific
reason to differ.

**Method ceiling** — *Would have to be true:* the target's factorisation shape is biased toward
a cheaply enumerable class. *Strongest ever supportable:* a constant-factor (bit-scale)
reduction in M at fixed P0 — **never an exponent**, because a class of relative density p^{−δ}
hit with probability p^{−δ'} contributes exponent δ' − δ ≥ 0 unless the bias exponent is
strictly positive, and a multiplicatively defined class cannot carry a p-power bias for an
integer CEP models as uniform. *Nearest obstruction:* the aligned null's exact break-even at
1/3 for every δ, already computed in BATCH-001; a claimed gain must beat break-even, not merely
be positive. *Nearby-object control:* the same shape measurement on uniform integers of the same
size. *Cheap pre-compute falsification:* the squarefree archetype.

---

### C1-7. Crypto-scale tail validation of Heuristic 1 by trial-division smoothness — no SageMath, no factoring

**Which factor** — F4 (P0). Heuristic 1 (L69) multiplies **every** margin row identically and
has never been paired with a validation experiment across three batches
(DEC-20260802-48c72c: "NC-3 and NC-6 remain unrun since BATCH-001").
`docs/target-result-profile.md` A7/C12 requires the pairing. This is GOAL-SSIQ-001's own need,
not GOAL-P13-001's: **C1-1's restated correctness condition, C1-3's multiplicity reading,
C1-4's Euler correction and C1-5's s(θ) all consume the same distribution**, and none can be
decided without it.

**The heuristic, stated exactly, with quantifiers** — *Let p be prime and E/F_{p²} a **uniformly
random** supersingular elliptic curve. The degree of the **smallest** isogeny φ : E → E^{(p)} is
B-smooth with probability **at least** u^{−u(1+o(1))}, u = log(p/2)/(3 log B), **uniformly as
p → ∞ for (log p)^ε < u < (log p)^{1−ε} at a fixed ε*** (L69).
*Distribution concerned:* the law of P(deg φ_min), the largest prime factor of the minimal
degree, under the uniform measure on supersingular curves over F_{p²}.
*Theoretical prediction and source:* ρ(u), Dickman–de Bruijn, via Theorem 1.4
(Canfield–Erdős–Pomerance, L77) composed with Theorem 1.5 (Aubry–Oyono–Vincent, L81), exactly as
the paper composes them (L83); Figures 1–2 use u = log(p/2)/(3x), x = log of the largest prime
factor (L254).
*What is NOT covered, and must be said:* Heuristic 1 is a **lower bound with a (1+o(1)) in the
exponent of u**. Agreement with ρ(u) at finite u neither proves nor disproves the
"≥ u^{−u(1+o(1))}" form, because ρ(u) = exp(−u(log u + log log u − 1 + o(1))) differs from
u^{−u} by e^{u(1−log log u+o(1))} — a factor ≈2 at u ≈ 13 and ≈1/70 at u ≈ 25, i.e. **the two
references cross sign as p grows**. Every deliverable must state which reference it used.

**Claim** — The tail at the *operating point* is measurable at **cryptographic parameters** in
pure Python at 10–100× the paper's sample resolution, because deciding B-smoothness for
B ≈ 2^{14}–2^{21} needs only **trial division by the ≈1200–150000 primes below B plus a cofactor
test**, never a factorisation. The paper's route (L244–L248) factors the norm to record its
largest prime factor and so needs SageMath and a factoring engine; the **tail** statement needs
neither. Prediction: at NIST-I the smooth fraction at u ≈ 6 is ≈2·10^{−4}, so 10^6 samples yield
≈200 events and 10^7 yield ≈2000, against the paper's ≈1 event at its own tail check (L250) —
precisely the "zero sample resolution" objection RT-H1 has carried since July.

**Mechanism** — The Deuring correspondence used exactly as the paper uses it (L244): sample a
random maximal order O in B_{p,∞}, form the unique two-sided ideal P of reduced norm p, take the
shortest vector of (P, Nrd/p); its norm is the minimal degree. All of it is integer lattice
arithmetic — HNF, Gram matrices, LLL, Fincke–Pohst — implementable without SageMath. Then trial
division of an ≈2^{83} integer (NIST-I) by primes < B, with the cofactor tested for
1 / prime / prime-power. **Sample size justified from the smallest probability to be resolved:**
to resolve rate q at relative precision r needs n ≈ 1/(q r²); at q = 2·10^{−4}, r = 0.2,
n = 1.25·10^5 per rung; a five-rung ladder plus a matched null doubles it; 10^6 primary samples
give r ≤ 0.07 at the operating rung and ≈20 events two rungs into the tail.
**Tail consistency checks, pre-registered:** (i) reproduce the paper's own two — smoothest of
100k at p = 5·2^{248}−1 is 12589-smooth vs ρ(u) ≈ 1/69232, and smoothest of 10k at
p = 27·2^{500}−1 is e^{23}-smooth vs ρ(u) ≈ 1/3312 (L250–L252) — as a known-answer gate on the
sampler; (ii) the observed minimum-B over the whole sample must match the ρ-predicted quantile
at that sample size with a two-sided Clopper–Pearson interval; (iii) the smooth fraction must
**decay** across the B-ladder like ρ — the canonical artifact tell.

**Minimal discriminating test** — One run. (1) Sampler + gate (i). (2) 10^6 samples at
p = 5·2^{248}−1 and 10^5 at p = 27·2^{500}−1, both SQIsign primes so the paper's numbers compare
directly. (3) Five-rung B-ladder bracketing B_opt, with p̂(u) read against ρ(u) on an
**absolute** band and against a matched-uniform arm on a **measured order-statistic** band, the
two limbs read and reported separately and never conflated (H-LPF-001's ABS-REL clause,
inherited). (4) Report the table against **both** references, ρ(u) and u^{−u}, with the crossing
point marked.

**Null object / control** — (a) **Matched uniform-integer arm** on [D/2, D] through the
identical pipeline at identical n and ladder, measuring the finite-size error of the ρ reference
so a form-specific departure is separable from a reference error. (b) **Apparatus-identity
control**: products of two random integers below √D, derivably smoother — a pre-registered point
prediction that **can fail**, and whose failure is apparatus failure, not evidence. (c) the
decay tell. (d) **Sampler control C1-8 is a precondition**, run in the same batch.

**Falsifier (reachable)** — F7-a p̂/ρ outside the pre-registered band at ≥2 rungs at **both**
primes in the **same** direction while the uniform arm is inside → Heuristic 1's tail
**weakened at the tested parameters**, direction stated (smoother = pro-attack, rougher =
anti-attack; opposite consequences, never reported as one outcome). F7-b decay tell fires →
apparatus falsified, no disposition. F7-c gate (i) fails → sampler falsified, the run decides
nothing about the heuristic (AGENTS.md rule 5). F7-d the trial-division shortcut is shown to
change the measured quantity (cofactor test misclassifies prime powers above the pre-registered
rate) → instrument defect, repair and re-run.

**Cost** — impl: **medium-high**, ≈400–700 lines of pure Python (maximal-order arithmetic, ideal
HNF, the two-sided ideal of norm p, shortest vector, trial-division sieve). compute: 4–12
CPU-hours for 10^6 samples; **peak memory < 2 GB** — the sample stream is processed online, with
only per-rung counters and a reservoir of extreme samples retained. No network. **SageMath is
unavailable and is not required**; if the sampler cannot be validated, that is C1-8's verdict,
reported as a feasibility outcome and **never** as evidence about Heuristic 1.

**Ceiling** — **`medium`, declared deliberately and not derived from field bit size.**
Crypto-scale *parameters* do not by themselves raise the tier: no isogeny is computed, the
sampler's fidelity is itself under test, and one unreplicated run is `preliminary` by the same
logic that caps EV-PEC-857664. A favourable outcome is `replicate`, never `support`, and never a
discharge of the conditional qualifier — `docs/claims-and-verification.md` is explicit that only
an unconditional proof removes it and that experimental validation at any scale does not.

**Kills-it-early** — Build only the sampler and run the paper's two published tail checks
(L250–L252) at 10^4 samples. If they do not reproduce, stop: everything downstream measures the
sampler, not the heuristic.

**Method ceiling** — *Would have to be true:* the Deuring-side shortest-vector norm is samplable
uniformly, and B-smoothness is decidable without factorisation at the operating B. Both are
checked, neither assumed. *Strongest ever supportable:* a distributional statement about **the
tested primes at the tested sample sizes**; the asymptotic statement stays conditional forever.
*Nearest obstruction:* Heuristic 1's uniformity range is a **p → ∞** statement, and two primes
is not one and cannot become one. *Nearby-object control:* the matched uniform-integer arm — a
pipeline that cannot separate the ternary-form arm from the uniform arm has not measured what it
claims. *Cheap pre-compute falsification:* the known-answer gate on the paper's two published
tail checks.

---

### C1-8. Sampler fidelity for the Deuring-side oracle: is "uniformly random up to conjugation" actually uniform?

**Which factor** — The instrument under F4. Every number in §4.2 and every number C1-7 would
produce is conditioned on sampler uniformity. EV-WESO-001 records the standing objection that
"the walk-based quaternion sampler is unvalidated"; it has never been tested.

**Claim** — The standard route to "a uniformly random maximal order up to conjugation" is a
random walk in the quaternion ideal graph, whose stationary distribution is **not** uniform on
isomorphism classes: it is weighted by 1/#Aut (Eichler mass-formula weights), with extra bias at
j = 0 and j = 1728 and a walk-length-dependent bias toward the start. To decide: **at the walk
lengths used, is the residual bias below the resolution of the smoothness measurement, or large
enough to move p̂(u) at the tail?** The tail is where it matters most, because fewest classes
contribute there.

**Mechanism** — Two explanations for any C1-7 departure. *S (sampler):* a mis-weighted sampling
measure. *D (distribution):* a genuine property of the target's smoothness law. They separate
because S is **p-independent in shape** — the 1/#Aut weights are supported on O(1) exceptional
classes and the walk bias decays geometrically in length — while D is not.

**Minimal discriminating test** — Toy scale, exhaustive, therefore decisive **about the
instrument**. (1) At p ≈ 2^{10}–2^{16}, p ≡ 3 mod 4, the supersingular set has ≈ p/12 classes and
is exhaustively enumerable: enumerate it, compute exact mass-formula weights, run the production
sampler at walk lengths n ∈ {n₀/4, n₀/2, n₀, 2n₀} with n₀ the length C1-7 would use, and measure
total-variation distance from (a) uniform on classes and (b) mass-weighted uniform. (2) Measure
the **induced** bias on the smoothness statistic: recompute p̂(u) under the sampler's empirical
measure and under exact uniform, reporting the difference in bits. (3) Fit TV decay in n and
extrapolate, marking the extrapolation as such.

**Null object / control** — **Exact-enumeration control**: at toy p the true answer is
computable, so the null here is ground truth rather than a surrogate. **Walk-length monotonicity
tell**: TV must decrease geometrically in n; a TV that does not decay as n increases indicts the
enumerator or the walk, not the mixing theory. **Starting-point control**: ≥3 distinct starts
including j = 1728, all converging to the same measure.

**Falsifier (reachable)** — F8-a TV at n₀ above threshold **and** induced bias above the C1-7
band → **C1-7's numbers are not admissible as stated** and must be re-run at longer walks or
with importance reweighting; a result about the instrument that blocks rather than contaminates
the heuristic finding. F8-b TV below threshold and induced bias below the band at every toy p →
explanation S is bounded **at toy scale**, and C1-7 reports with that bound attached, never as a
crypto-scale statement about the sampler. F8-c TV does not decay in n → instrument failure.

**Cost** — impl: medium (supersingular-locus enumerator via 2-isogeny closure from j = 1728,
plus the mass formula). compute: < 1 CPU-hour. Reuses C1-7's sampler, which is why the two must
share a batch.

**Ceiling** — `toy`, unambiguously and by construction: exhaustive enumeration exists only at
toy p. **A toy-scale sampler bound does not validate the sampler at 2^{248}**, and C1-7's record
must carry that gap explicitly rather than inherit a false discharge.

**Kills-it-early** — At the smallest toy p, sample 10^4 times and χ²-test the class histogram
against the mass-formula weights. If it fails there, no longer walk fixes a systematically wrong
measure and the sampler must be redesigned before C1-7 is worth building.

**Method ceiling** — *Would have to be true:* a toy-scale mixing bound transfers to crypto-scale
walks. *Strongest ever supportable:* a **toy-scale** bound plus a cited mixing-time argument —
the paper cites Pizer and the more explicit [6, Lemma 14] for n = O(log p) (L193) — so the
transfer is by citation, not by this experiment, and must be labelled so. *Nearest obstruction:*
the exhaustive enumeration that makes the test decisive is exactly what is unavailable at the
scale where the answer matters; a structural ceiling on the control, not a budget limit.
*Nearby-object control:* a random regular graph of the same degree and size, where mixing is
known; measured TV decay must match it, and materially slower mixing on the Deuring graph makes
the cited bound the thing to re-examine. *Cheap pre-compute falsification:* the χ² check.

---

### C1-9. The joint law of (size, smoothness): is the minimal degree's smoothness conditionally independent of its size?

**Which factor** — F1 × F4. The input C1-5 needs and that no scheduled measurement produces:
REC-1 measures the **size** distribution of δ_E; §4.2 measures the **smoothness** distribution;
nothing measures the **joint**.

**Claim** — T(θ) = θ + g(θ) − s(θ) is valid only if
Pr[B-smooth | δ_E ≈ p^{θ}] = ρ(θ log p/log B), i.e. if, conditioned on size, the minimal degree
follows the uniform-integer law **for that size**. Two live mechanisms with opposite consequences:
*(M-indep)* conditional independence, so lowering the threshold buys exactly the size-driven
credit and nothing more, and C1-5's s(θ) is correctly computed; *(M-corr)* short vectors are
systematically **smoother** than their size predicts — plausible because a lattice with an
unusually short vector often carries extra structure (small-discriminant order, CM-like
configuration, repeated small factor in the represented value) — in which case s(θ) is
understated and the exchange curve shifts in the attack's favour at lowered thresholds.

**Minimal discriminating test** — Rides C1-7's sample at no extra sampling cost. Bin by
log(δ_E)/log p into ≥6 bins spanning the observed range; within each bin measure p̂(u_bin)
against ρ(u_bin) computed **at that bin's own size**. Discriminator: is R(u_bin) = p̂/ρ flat
across bins (M-indep) or trending (M-corr), and with what sign?

**Null object / control** — **Matched-size uniform-integer arm** per bin, so the bin-wise
finite-size error of ρ is measured rather than assumed. **Random-ternary-form arm** (shared with
C1-3/C1-4): a trend present there too is a ternary-form effect, not a Deuring effect.
**Bin-count tell**: small-δ bins are rare by construction (Pr[δ_E ≤ p^{θ}] ≈ p^{3θ/2−1/2}), so
each bin carries its exact Clopper–Pearson interval and bins below a pre-registered count are
**recorded and not read** — H-LPF-001's underpowered-rung discipline, inherited.

**Falsifier (reachable)** — F9-a R flat within intervals at both primes → M-indep; C1-5's s(θ)
stands and the joint question is CLOSED at the tested parameters. F9-b R trends upward toward
small δ → M-corr; the exchange curve must be recomputed and C1-5's closure weakens. F9-c R
trends downward → short vectors are rougher; the curve worsens and C1-5's closure strengthens.
F9-d the same trend on the random-form arm → it belongs to C1-4, not here.

**Cost** — impl: low (binning + per-bin statistics on C1-7's stream). compute: none beyond
C1-7. **Requires C1-7 to retain δ_E per sample, which must be specified before the run.**

**Ceiling** — `medium`, per-bin only. The small-δ bins are the fewest-sample bins, so the
interesting end is the underpowered end; that is a stated design limitation, not a later
disappointment.

**Kills-it-early** — Compute the expected count in the smallest bin at n = 10^6 against the
observed δ_E range. If the bin at θ ≈ 0.30 carries under ≈30 samples, the design has no power
where C1-5 needs it; say so in advance and either raise n or restrict the claim to powered bins.

**Method ceiling** — *Would have to be true:* a size-conditioned smoothness departure exists and
is large enough to move an exponent-scale quantity. *Strongest ever supportable:* a **bit-scale**
correction to s(θ); s(θ) stays exponent-zero for any B = p^{o(1)} regardless of outcome
(CEILING-SLICE), so this idea can never by itself reopen C1-5 — it can only reapportion the gap
between T(θ) and 1/3 between smoothness and density. *Nearest obstruction:* the bins where
M-corr would matter most (θ near 1/4) have probability p^{−1/8} ≈ 2^{−32} at NIST-I —
**unreachable at any sample size this program can run** — so the measurement is intrinsically
confined near θ ≈ 1/3 and extrapolation toward 1/4 is forbidden, not merely cautioned.
*Nearby-object control:* the random-ternary-form arm. *Cheap pre-compute falsification:* the
bin-count arithmetic, which decides the design's power before a sample is drawn.

---

### C1-10. The o(1) ledger: an exact, signed accounting of every o(1) and polylog in the chain

**Which factor** — All of F1–F8 at once. `DEC-20260802-48c72c` gate_3 records the gap in terms:
"What is missing is the o(1) characterization for the paper's own asymptotic, which this
programme has not produced." The source discloses a **superpolynomial** overhead "much larger
than the previous (log p)^{O(1)} cofactor" (L13, L39) but does not characterise it.

**Claim** — Every suppressed term can be written down, signed, and evaluated at
log2 p ∈ {256, 384, 512, 576, 768}; their sum is the honest gap between the asymptotic statement
and any concrete number. Enumerated with locators: (i) **Lemma 3.2's log X + 2** (L133), kept in
the upper bound, dropped in §4.1's lower bound (L230) — understates M; (ii) **CEP's
u^{−u(1+o(1))}** (L77), the o(1) multiplying u so the error is u^{±o(1)·u} — two-sided;
(iii) **Heuristic 1's own (1+o(1))** (L69) at a **different** u than (ii), so the two do **not**
cancel in Ψ(X,B)/P0 — the single most-overlooked item, and what makes the ρ-versus-u^{−u}
reference choice load-bearing (C1-7); (iv) **Lemma 3.3's B^{O(1)} and (B + log p)^{O(1)}**
(L154, L156) with the footnote explicitly declining to fix the exponent — understates time,
magnitude set by the Φ model (C1-11); (v) **X^{1+o(1)}** (L154); (vi) **walk length O(log p)**
(L193) — understates per-attempt cost, small; (vii) **§4.1's "≥ d" for the true cyclic count
d·∏(1+1/ℓ)** (L230) — understates M; (viii) **the Σ_{d smooth ≤ X} d ≈ X·Ψ(X,B) identity**,
whose true value is X·Ψ(X,B) − ∫₀^X Ψ(t,B)dt, a bounded constant factor below 1 — overstates M.

**Mechanism** — The source names two directions of error itself: "a rough underestimation of the
size of the table and the cost of its generation" and "we are assuming here that the bound of
Lemma 3.5 is tight: the above numbers may be overestimating the factor 1/P0 (see Remark 1)"
(L240). The ledger makes the two **separately quantified and not netted**, the same discipline
EV-PEC-857664's `unit_and_conventions` imposes on the measured side. A term that cannot be
bounded is UNDEFINED and drawn as a gap, never estimated.

**Minimal discriminating test** — Zero compute. (1) Eight rows × five field sizes, each cell a
value or UNDEFINED, with a sign and a locator. (2) Sum the bounded terms; report the residual as
an interval, not a number. (3) **Known-answer gate**: every term at its §4.1 convention must
reproduce the five published rows (L234–L238) within the committed 2.2309-bit NIST-I band.
(4) State explicitly which terms IDEA-20260803-48e258's crossover curve treats as constants over
its plotted range — that record names this "the largest modelling gap", and this ledger is the
object that closes it.

**Null object / control** — the convention-recovery gate (3); a **sign-consistency control** —
the known-sign terms applied together must move the rows in the direction the source itself
predicts (table understated, 1/P0 possibly overstated), and if they do not there is a sign
error; a **superpolynomiality check** — the dominant term must be superpolynomial in log p since
L39 asserts it is, and a ledger whose largest term is polylog contradicts the source.

**Falsifier (reachable)** — F10-a gate fails → ledger void. F10-b summed bounded terms below
polylog scale at every field size → contradicts L39, a term is missing. F10-c more than half the
cells UNDEFINED → the ledger is an inventory of ignorance, reported as exactly that (still
useful: it names what to measure). F10-d (ii)/(iii) shown to cancel after all → the largest
conceptual item drops out and the ledger simplifies.

**Cost** — impl: none. compute: none. Half a day of careful reading against line locators.
**Highest information-per-cost item in the catalogue.**

**Ceiling** — No claim tier: a derivation over an external source's own statements. It asserts
nothing about the attack's true cost and everything about what the published asymptotic fixes.

**Kills-it-early** — Write (ii) and (iii) and check whether the two u's coincide. They do not:
u = log(p/2)/(3 log B) for Heuristic 1 (L69) versus w = log X/log B = 1/2 + (1/2)√log(p/2) for
CEP (L214). One line settles the ledger's central item either way.

**Method ceiling** — *Would have to be true:* every suppressed term is identifiable from the
frozen text. *Strongest ever supportable:* a **characterisation of the incumbent's o(1)**, which
bounds what any concrete-cost statement about this algorithm can mean — and therefore bounds
C1-1, C1-2, C1-11 and C1-12's deliverables too. It is not an improvement to the algorithm and
must never be presented as one. *Nearest obstruction:* Lemma 3.3's B^{O(1)} is deliberately
unfixed by the source ("We do not presently investigate the best possible exponent O(1)", L156
footnote), so one cell is UNDEFINED by construction until C1-11 decides the Φ model.
*Nearby-object control:* apply the identical ledger to the previous-best p^{1/2}(log p)^{O(1)}
algorithm (L25); its cofactor is polylog by construction, so the ledger must return polylog
there. A ledger returning superpolynomial for both has not identified the load-bearing structure.
*Cheap pre-compute falsification:* the two-u check.

---

### C1-11. The Φ_ℓ evaluation-model fork: precompute-and-amortise versus per-specialisation, and which one the exponent budget must adopt

**Which factor** — F7/F8 (collision mechanism feed and per-step arithmetic) and, through them,
F5 (B). Lemma 3.3 charges "Computing the polynomial Φ_ℓ(j(E'), x) ∈ F_{p²}[x] and finding its
ℓ + 1 roots ... time (B + log p)^{O(1)}" (L156) and explicitly declines to fix the exponent.

**Claim** — Two models are consistent with the frozen text and they give **opposite** verdicts on
how large B may be. *Model P (precompute-and-amortise):* build Φ_ℓ mod p once at Θ̃(ℓ³) with
Θ̃(ℓ²) storage, amortise over the ≈M/ℓ entries that use it ⟹ ℓ ≤ M^{1/4}, per-entry Θ̃(1).
*Model S (per-specialisation):* evaluate Φ_ℓ at a single j without materialising it ⟹ per-entry
Θ̃(ℓ)/(ℓ+1)·(root-finding) and a per-entry cost rising with ℓ. Under P, C1-2's fixed point
permits B* ≈ 2^{20}; under S it does not. **The record has never adjudicated between them**, and
the relevant external source has been named as necessary in three consecutive red-team reports
and fetched in none (EV-PEC-857664 OBS-L: "FLAGGED, UNVERIFIED, AND RELIED ON BY NOTHING").

**Mechanism** — The committed instrument computes roots as gcd(x^{p²} − x, f) via `poly_powmod`,
so per-entry ≈ 4 log2(p)·M(ℓ)/(ℓ+1) and γ = exponent(M) − 1 ≤ 1 — the **method ceiling already
committed** in EV-PEC-857664 CORR-4, which is why the c = 2 scenario died by ceiling rather than
by measurement. That ceiling is a statement about **this pipeline**, and Model P sits outside it
by moving the ℓ-dependence into a one-time precomputation. Both models therefore live inside the
same L156 licence, and only a measurement or a citation separates them.

**Minimal discriminating test** — Primary sources are unreachable, so the test is a **measurement
fallback**, not a fetch. (1) Implement both models at toy ℓ (ℓ ≤ 211, where committed Φ_ℓ files
already exist and are hash-bound) and measure counted-F_{p²}-multiplications per entry as a
function of the number of distinct j's evaluated per ℓ. The discriminator is the **crossover in
N**: Model P's per-entry cost falls as 1/N, Model S's is flat in N. (2) Fit both and report the
N at which P overtakes S, then compare to the algorithm's actual N ≈ M/ℓ. (3) Re-run C1-2's
fixed point under each fitted model. **FC-4 is carried on every output** and the ℓ ∈ {3,5}
diagnosis is attached.

**Null object / control** — **C-NULL-shaped control** reused: an object whose per-entry cost is
O(1) in ℓ by construction must show **no** N-dependence under either model; N-dependence there is
an instrument artifact. **Known-answer gate**: at N = 1 the two models must agree to within the
measurement's own precision, since a single specialisation is a single specialisation either way.
**Non-netting rule**: excluded costs (Φ storage and I/O, coefficient reduction, hashing, table
access) remain excluded **in the attack's favour**, so the measured exponent stays simultaneously
a lower bound with respect to them; the two directions are not netted.

**Falsifier (reachable)** — F11-a the crossover N exceeds M/ℓ at the operating point → Model S
governs, B* stays near 2^{14.2}, and C1-1's gain is not compounded by C1-2. F11-b the crossover
is far below M/ℓ → Model P governs and C1-2's B* ≈ 2^{20} branch is live. F11-c neither model
fits the measured N-dependence → both are wrong and the L156 licence hides a third behaviour;
that is the most informative outcome and it names the next measurement. F11-d the C-NULL control
shows N-dependence → instrument artifact, no disposition.

**Cost** — impl: medium (~200 lines reusing the committed harness and its counters). compute:
~1 CPU-hour, ℓ ≤ 211 only. **Blocked component, declared:** the external
modular-polynomial-evaluation literature is unreachable this session; the fallback above is a
measurement, and any claim about the published asymptotic of that literature is recorded as
UNVERIFIED and relied on by nothing (the discipline EV-PEC-857664 OBS-L already set).

**Ceiling** — `medium`, scoped to ℓ ≤ 211 at p ~ 2^40 and to this implementation family. The
extrapolation to ℓ ≈ B_opt is **not** licensed by this test and is C1-12's subject.

**Kills-it-early** — At ℓ = 211, measure per-entry cost at N = 1 and N = 1000. If the ratio is
within noise of 1, Model P's amortisation is not realisable in this harness and the fork
collapses to S for anything this program can build.

**Method ceiling** — *Would have to be true:* the amortisation is realisable and the algorithm's
N is on the right side of the crossover. *Strongest ever supportable:* a **bit-scale**
determination of the per-entry law and hence of B* — never an exponent (F7, F8 carry exponent 0).
*Nearest obstruction:* the committed identifiability limit, that laws agreeing over ℓ ≤ 211 can
diverge at ℓ ~ 2^{14}; this test measures the **N-axis**, not the ℓ-axis, which is precisely why
it can discriminate where an ℓ-extrapolation cannot — and it still says nothing about the ℓ-axis.
*Nearby-object control:* the C-NULL object. *Cheap pre-compute falsification:* the N = 1
agreement gate.

---

### C1-12. The unreachable-ℓ bracket: per-entry cost at the operating ℓ is not measurable by the committed route, so report the bracket width as a function of B

**Which factor** — F5/F8 as they enter the concrete cost. Successor to IDEA-20260803-48e258 on
the B axis: that record varies (p, w) at fixed cost law; this one asks how wide the cost law's
bracket is at the ℓ the algorithm actually uses, and how that width grows if C1-1/C1-2 raise B.

**Claim** — The committed measurement reaches ℓ ≤ 211 while the operating point is ℓ ≈ B_opt
= 2^{14.2}, about 6.5 octaves beyond the top of the measured range (EV-PEC-2e67ff `boundaries`).
Direct measurement at the operating ℓ is **infeasible by the committed route**: Φ_ℓ has
≈ ℓ²/2 coefficients, and the committed acquisition already hit its 67108864-byte per-ℓ cap at
ℓ ≥ 223 (EV-PEC-857664, deviation D-2 with all seven tail ℓ returning curl exit 63). Therefore
the exponent budget must carry the per-entry cost as a **model with a declared bracket**, and the
honest deliverable is **the bracket's width as a function of B**, which C1-1 and C1-2 both
*widen* by pushing B upward. Prediction: bracket width grows ≈ |γ_A − γ_B|·log2 B = 0.1228·log2 B
bits from the γ span alone, i.e. ≈1.74 bits at B = 2^{14.2} and ≈2.46 bits at B = 2^{20}, before
the L4/batched-evaluation ambiguity (48–59 per cent of a 21.2–25.2-bit total) is added.

**Mechanism** — Three independent width sources, kept separate and not netted: (a) the measured
γ span across seam-free fits, whose two endpoints are **non-independent estimates** (gamma_A and
gamma_B share the split structure — EV-PEC-857664 OBS-F's binding consequence) and whose spread
is therefore not a confidence interval; (b) the α (p-scaling) question, worth
log2(256/40)·(α − 1) bits, on which **FC-4 fired** and stands; (c) the L4 batched-evaluation
term, unimplemented and dominant. Optimistic assumptions and their bias directions are declared:
the measured γ from an unoptimised implementation is an **upper** bound on the achievable
per-entry exponent (anti-attack by construction), while the excluded costs are excluded **in the
attack's favour** (so the same γ is a **lower** bound with respect to them).

**Minimal discriminating test** — Zero compute. (1) Emit width(B) over log2 B ∈ [10, 24] with the
three sources decomposed and signed, `c` used only as the bracket [1.327077, 1.576444], and the
RT3-C1 charging-point correction (0.60–1.00 bits **pro-attack**) applied and signed rather than
absorbed. (2) Mark every B outside the fitted window as **UNDEFINED**, drawn as a gap, per
IDEA-20260803-48e258's fitted-window guard. (3) Report **peak memory** beside time at each B,
since M moves with B and memory is first-class here. (4) Known-answer gate: at B = 2^{14.2} the
machinery must reproduce the committed eighteen-reading span [8.3498, 13.1544] bits.

**Null object / control** — **Null-baseline**: recompute width(B) with the corrected overhead
replaced by §4.1's one-op convention; the width must collapse, and if it barely moves the
corrected overhead is not driving the result. **Instrument-response control**: width(B) must be
monotone increasing in B; a flat or non-monotone width means the B-dependence is not wired in.

**Falsifier (reachable)** — F12-a width(B) is flat in B → the bracket is B-independent and
C1-1/C1-2 cost nothing in uncertainty, which strengthens them. F12-b width(B) at B = 2^{20}
exceeds the entire gain C1-1 claims → the compounded C1-1 + C1-2 route buys a number smaller than
its own uncertainty and must be reported as inconclusive by construction, not defended.
F12-c the known-answer gate fails → machinery void.

**Cost** — impl: low. compute: none.

**Ceiling** — No claim tier: a model substitution under the committed assumption set, with FC-4
attached and the non-independence of γ_A/γ_B stated on the face of every output.

**Kills-it-early** — Compute 0.1228·log2 B at B = 2^{20} and compare to C1-1's claimed 13–15 bit
gain. If the width already exceeds the gain, the whole compounded route is uncertainty-limited
and should be ranked accordingly before anything is built.

**Method ceiling** — *Would have to be true:* the per-entry law's form is stable across the
6.5–10 unmeasured octaves. *Strongest ever supportable:* **a width, not a value** — this idea can
never determine the per-entry cost, only bound how much any determination could mean. That is the
point, and it is the honest counterweight to C1-1 and C1-2. *Nearest obstruction:* the committed
identifiability limit is structural, not budgetary — Φ_ℓ files at the operating ℓ do not fit in
the acquisition budget or in memory — so no amount of precision inside ℓ ≤ 211 removes it.
*Nearby-object control:* the C-NULL object, whose width must be ≈0 in B by construction; a
non-zero B-dependence there is manufactured. *Cheap pre-compute falsification:* the
0.1228·log2 B arithmetic above.

---

### C1-13. The listable-set optimisation as one object: cost(R)/hit(R), with its free closures and the single distributional input that decides it

**Which factor** — F2, F3, F5 jointly; the object-first framing of this whole slice, and the
record that keeps its closures from being re-tread.

**Claim** — Every idea in this catalogue is a choice of **listable set** R ⊆ [1, X] with
cost(R) = Σ_{d ∈ R} d + Σ_{ℓ used} cost(Φ_ℓ) and hit(R) = Pr[deg φ = ab with a, b ∈ R], and the
algorithm's total is cost(R)/hit(R). Stating the optimisation once yields **three free closures**
and isolates exactly one open distributional input. (i) **Symmetry:** splitting the two lists
asymmetrically (X₁ ≠ X₂ with X₁X₂ ≥ D) minimises X₁² + X₂² at X₁ = X₂ by AM-GM, so asymmetric
splits strictly lose — closed, one line. (ii) **One-large-prime domination:** if the per-prime
affordability condition is ℓ⁴ ≲ M (C1-2, Model P), it applies to **every** prime, so a semismooth
"one large prime up to L" family is dominated by uniform smoothness at B = M^{1/4}; the
Bach–Peralta σ(u, v) two-parameter density is therefore **not** the right generalisation here —
closed, with a mechanism. (iii) **Threshold monotonicity:** raising the degree threshold T costs
p^{ε} in cost(R) and gains at most p^{o(1)} in hit(R) (C1-3), so T is at its minimum — closed.
**What remains open after all three:** the *window* freedom (C1-1) and the *shape* freedom
(C1-6), and both reduce to one question — **does the target's multiplicative law differ from the
uniform-integer law, and in which direction** — which is C1-4/C1-7/C1-9's measurement.

**Mechanism** — The three closures are consequences of the TO-MULT projection: because
correctness factors through TO-MULT, any R is a subset of the divisor-lattice's degree axis, and
the cost/hit ratio is a functional on subsets of [1, X]. That functional's structure — convex in
the symmetric direction, monotone in the threshold, dominated in the semismooth direction — is
what makes the closures cheap. Nothing here is a statement about isogenies; it is a statement
about the projection, which is why it is free.

**Minimal discriminating test** — Zero compute. (1) Write the functional, prove the three
closures, and record each with its mechanism at the `docs/inventor-protocol.md` §4 standard
(named obstruction + argument + forward guidance), not as a screening count. (2) Verify each
closure against a nearby object where it must **fail**: asymmetry must win when the two lists
have different per-entry costs (so the closure is scoped to equal-cost lists); semismooth must win
when the affordability condition is per-*use* rather than per-prime (so the closure is scoped to
Model P); threshold monotonicity must fail when α ≥ 2 (so the closure is scoped to α = 3/2). A
closure that cannot be made to fail on any nearby object is not identifying real structure.
(3) Emit the forward-guidance list of what remains.

**Null object / control** — **Nearby-object controls are the test** (step 2). Additionally, a
**degenerate-R control**: R = {1} must give hit = 0 and R = [1, X] with X ≥ D must give hit = 1;
a functional returning anything else is misdefined.

**Falsifier (reachable)** — F13-a any of the three closures fails its own scoping check → it was
stated too broadly and must be narrowed, which is a correction of exactly the kind BATCH-001
found in four of five obstruction fields. F13-b a fourth freedom is exhibited that is neither
window nor shape nor threshold → the enumeration is incomplete and says so, and the
completeness disclaimer applies as it did to L1–L5. F13-c the semismooth closure fails because
the affordability condition is per-use → C1-2's Model P is wrong and the fork of C1-11 is
already decided against it.

**Cost** — impl: none. compute: none. **Do this first**: it is free and it can retire work.

**Ceiling** — No claim tier. These are statements about a cost functional, not about the
supersingular isogeny problem, and none of them is evidence about hardness, any parameter set, or
whether a p^{1/4} algorithm exists.

**Kills-it-early** — The AM-GM line. If asymmetric splits are already known to lose, closure (i)
is a restatement and the idea's value rests on (ii) and (iii).

**Method ceiling** — *Would have to be true:* the cost/hit functional captures the whole design
space of this slice. *Strongest ever supportable:* a **scoped completeness statement** — "within
the TO-MULT projection and under the stated affordability model, the only remaining freedoms are
window and shape" — which is a statement about the search, explicitly **not** about the problem,
and whose honest status is exactly what `docs/inventor-protocol.md` §4 demands of any closure.
*Nearest obstruction:* the projection itself. Anything that does not factor through TO-MULT — the
fibre structure, the collision mechanism, oriented or higher-dimensional targets (N5) — is
invisible to this functional, so a "completeness" claim here can never be a completeness claim
for the goal. *Nearby-object control:* step (2)'s three scoping failures. *Cheap pre-compute
falsification:* the degenerate-R control.

---

## Batches

Three concurrent non-archive tasks maximum, disjoint write scopes, one archive task per batch.
Batches are ordered so that free work can retire expensive work.

### Batch S1 — "Whiteboard ceilings before any compute"
- **Objective.** Decide, at zero compute, which smoothness/table levers are exponent-carrying and
  which are o(1), and retire what can be retired for free.
- **Ideas.** C1-13, C1-5, C1-3 (whiteboard arm only), C1-10.
- **Grouping rationale.** All four are pure derivations over the frozen text and committed
  numbers; each has a one-line kills-it-early check; and three of them can *close* routes that
  S3/S4 would otherwise pay to explore. C1-13's closures scope C1-5's and C1-3's audits, and
  C1-10 supplies the o(1) frame every later cost statement needs.
- **Budget.** Zero compute. 3 concurrent tasks: T1 producer (C1-13 + C1-5), T2 producer
  (C1-3 whiteboard + C1-10), T3 red team on both. Plus one archive task.
- **Decides.** Whether the threshold lever is CLOSED at α = 3/2; whether Remark 1's multiplicity
  is worth under a bit; whether asymmetric, semismooth and raised-threshold families are closed
  with mechanisms; and what the incumbent's o(1) actually contains.

### Batch S2 — "The owed heuristic pairing, at crypto parameters"
- **Objective.** Produce this program's first crypto-parameter smoothness measurement and pair
  the conditional result with the heuristic it rests on.
- **Ideas.** C1-7 (primary), C1-8 (blocking precondition), C1-9 (rides the same stream).
- **Grouping rationale.** One instrument, three falsifiers. C1-8 must gate C1-7 in the same batch
  or C1-7's numbers are uninterpretable; C1-9 costs nothing extra but must be specified before the
  run because it requires δ_E to be retained per sample.
- **Budget.** 4–12 CPU-hours, peak memory < 2 GB, one authorised run, maximum_runs 1.
  3 concurrent tasks: executor, validator, red team. Plus one archive task.
- **Decides.** Whether Heuristic 1's tail is consistent with ρ(u) at the operating point at 10–100×
  the source's resolution; whether the sampler is fit for purpose at toy scale; and whether size
  and smoothness are conditionally independent.

### Batch S3 — "Charged table cost and the smoothness bound"
- **Objective.** Fix B* and the per-entry model, and decide whether C1-1's structural gain
  survives being charged.
- **Ideas.** C1-1 (arithmetic + toy divisor-window measurement), C1-2, C1-12.
- **Grouping rationale.** C1-1 produces a gain, C1-2 compounds it or does not, C1-12 measures the
  uncertainty both create. Running the gain without its bracket is precisely the failure the
  campaign's own record warns about; running them together makes the comparison decidable.
- **Budget.** ≤2 CPU-hours (C1-1's integer arithmetic only), zero for the rest. 3 concurrent
  tasks: producer (C1-1), producer (C1-2 + C1-12), validator. Plus one archive task.
- **Decides.** Whether X can be tightened from (BD)^{1/2} to λ·D^{1/2}; what B* is under each
  model; and whether the resulting bracket exceeds the claimed gain.

### Batch S4 — "Distributional structure of the target integer"
- **Objective.** Decide whether the target's smoothness law departs from the uniform-integer model
  in a u-dependent way, and whether any shape restriction beats break-even.
- **Ideas.** C1-4, C1-6, C1-11.
- **Grouping rationale.** C1-4 and C1-6 are the two halves of the same question — does the target's
  multiplicative law differ from uniform, and can any listable family exploit it — and both read
  S2's committed sample rather than generating one. C1-11 joins them because it is the last
  unresolved input to C1-2 and because its blocked source makes it a measurement task rather than a
  fetch, so it belongs with the other bench work.
- **Budget.** ~1 CPU-hour (C1-11 at ℓ ≤ 211). 3 concurrent tasks: producer (C1-4 + C1-6),
  producer (C1-11), red team. Plus one archive task.
- **Decides.** Whether the Euler-product correction is constant or u-dependent and with what sign;
  whether any factorisation-shape family beats the aligned null; and which Φ evaluation model the
  exponent budget must adopt.

**Dependencies.** S1 → S3 (C1-13's closures scope C1-2's framing; C1-10 frames C1-12).
S2 → S4 (C1-4, C1-6, C1-9 read S2's sample). S4/C1-11 → S3/C1-2 if S3 is re-run.
No idea in S3 or S4 may be dispatched before S1's red team returns.

---

## Honest accounting (`docs/inventor-protocol.md` §5)

- **Object studied.** TO-MULT — the multiplicative type of the minimal degree deg φ_min, and the
  cost/hit functional on listable sets that it induces (§0.2, C1-13). The lossy-projection test is
  applied and passed in §0.2: the fibre discarded is exactly factor F3, the retained data
  propagates deterministically under composition because deg is multiplicative, and the original
  object is not recoverable.
- **Depth of verified structure.** None. **This is an ideation deliverable and contains zero
  executed measurements, zero runs and zero evidence.** Every number in it is either (a) quoted
  from a committed record with its identifier, (b) read from the frozen source with a line locator,
  or (c) an explicitly labelled prediction that the corresponding minimal test would confirm or
  refute. The predictions in C1-1, C1-2 and C1-3 are the load-bearing ones and none has been tested.
- **`dominated_by`.** For every idea in this catalogue: **the archived p^{1/3+o(1)} algorithm
  itself**, on every axis. Checked against each row of the frontier the goal record names:
  unconditional p^{1/2}(log p)^{O(1)} at polynomial memory — not dominated by anything here, and
  not beaten by anything here; heuristic-conditional p^{1/3+o(1)} time **and** memory — dominates
  every idea here on time exponent (all are 1/3 or worse) and on memory exponent; the
  vOW interpolation √(N³/w) — untouched, since no idea here changes N's exponent or moves along the
  curve; the F_p-restricted Õ(p^{1/4}) figure — not a baseline for this problem, contested in this
  corpus (KN-TECH-058 RC4), and cited by nothing here. `null` is **not** claimed anywhere.
- **`sota_delta`.** **Zero on every exponent axis. No idea in this catalogue reduces the time
  exponent below 1/3, and CEILING-SLICE (§0.3) explains why none can while B = p^{o(1)} and
  D = p^{1/3}.** The claimed deltas are: C1-1, up to 13–15 bits of modelled time and 9–14 bits of
  modelled memory at NIST-I with the exponent unchanged, and a possible change to the o(1)'s
  *shape* if compounded with C1-2 — untested; C1-2, a closed-form B* and o(1) where the record
  currently holds a numerical optimum with no stated constraint; C1-3 and C1-5, expected **negative**
  results (closures with mechanisms); C1-7, the first crypto-parameter tail resolution of the
  heuristic that multiplies every margin row, at 10–100× the source's sample resolution;
  C1-10 and C1-12, characterisations of what is *not* known, which reduce no cost at all.
- **Enumerated closures (each with mechanism, at the §4 standard).** (i) **Asymmetric split loses**
  — AM-GM on X₁² + X₂² at fixed X₁X₂; scoped to equal-cost lists, and it fails when the two lists
  have different per-entry costs. (ii) **Semismooth / one-large-prime is dominated** — the per-prime
  affordability condition ℓ⁴ ≲ M applies to every prime, so uniform smoothness at B = M^{1/4}
  dominates any Bach–Peralta σ(u,v) family; scoped to Model P, and it fails if affordability is
  per-use. (iii) **Raising the degree threshold loses** — the optimum needs d log N/d log T = 1
  while the Siegel count gives 3/2; scoped to rank 3, and it fails for a rank change (lever N5).
  (iv) **Smoothness cannot recover an exponent** — F4 carries exponent 0, so any s(θ) credit is
  bits, never exponent; this is the whiteboard refutation the goal record already names, restated
  with its scope. **Forward guidance:** what remains open inside this slice is the *window* freedom
  (C1-1) and the *shape* freedom (C1-6), both of which reduce to one measurable question — whether
  the target's multiplicative law departs from the uniform-integer law and in which direction. What
  remains open **outside** this slice and is invisible to TO-MULT: the fibre structure and the
  collision mechanism (C2), oriented / prescribed-torsion / higher-dimensional targets (N5), and
  cross-attempt amortisation (A7).
- **Open directions for the next session.** (1) Whether C1-1 and C1-2 compound, which is the only
  route in this slice to changing the o(1)'s *shape* rather than its constant. (2) Whether C1-7's
  measurement can be extended to a third prime, since two primes cannot support a statement about
  u-dependence as p → ∞. (3) The N5 scoping pass, which C1-3's and C1-5's ceilings both explicitly
  exclude. (4) Whether the TO-MULT enumeration is complete — recorded as **unverified**, because
  this program still has no written object enumeration (`KN-OPEN-019`), and any completeness reading
  of C1-13 is a sketch, not a taxonomy.
- **Not claimed anywhere in this document.** No exponent below 1/3; no p^{1/4}; no break; no
  completion; no security-parameter action; no statement about CSIDH, (qt-)Pegasis, or torsion-based
  constructions, which the source's own scope excludes and which no record here may widen.
