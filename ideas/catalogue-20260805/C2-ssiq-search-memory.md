# C2 — SEARCH / COLLISION / MEMORY catalogue for GOAL-SSIQ-001

Slice: the van Oorschot–Wiener (vOW) curve and its interpolation range, batched
evaluation, parallelisation, time–memory tradeoffs, the collision-search
structure itself, and quantum variants of the search stage. Companion agent C1
owns the smoothness / table-construction side; smoothness distributions,
Heuristic 1, Ψ(X,B), and the choice of B *as a smoothness question* are not
touched here except where they enter a memory or search cost.

Deliverable class: a **decided lever map**, not an algorithm. Nothing in this
file claims p^{1/4}, a break, a completion, or novelty. Every idea is written so
that a negative outcome is a usable result.

## 0. Reading conventions used throughout

**MEASURED vs MODELED.** Every number is tagged. `MEASURED` = a committed run
datum with its record ID. `MODELED-COMMITTED` = arithmetic inside a committed
cost model, which per DEC-20260802-48c72c carries **no claim tier**.
`MODELED-HERE` = arithmetic performed in this catalogue from committed inputs,
shown so it can be checked or refuted; it is a *prediction of an audit*, never a
finding.

**Two different "L4" exist and the collision is real.** GOAL-P13-001's run
assumption **L4** is *batched evaluation of modular polynomials*; GOAL-SSIQ-001's
lever **L4** is *descent to the F_p-rational subgraph*. This catalogue writes
**L4-BATCH** and **L4-DESCENT** and never bare "L4". Downstream records should
adopt the same disambiguation or state which they mean.

**Standing constraints inherited, not re-litigated.**
- `gamma_B = 0.8100336227` is a **transient** of the unimproved shared reduction
  (MA-5, DEC-20260802-48c72c adjudication C). **The bracket's low end is the
  optimistic one.** No idea here treats a low end as conservative.
- `gamma_A` and `gamma_B` are **not independent estimates** (MA-8).
- Charging at `ell = B_opt` overstates the entry-weighted cost by **0.60–1.00
  bits** (assumption L2, RT3-C1); every margin quoted from BATCH-003 is that
  pessimistic, and the correction shifts the whole table uniformly.
- **SP-9 binds:** C-NULL's measured 2^12.26–2^12.32 multiplications per 2-isogeny
  step at p ≈ 2^40 may **never** be cited as a Delfs–Galbraith per-step cost. It
  is cited below only as *this pipeline's own null-object step cost*.
- `alpha = 1` carries the **MECHANISM-INCONSISTENT** label (SP-10).
- Primary sources beyond `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` are
  **unreachable** and SageMath is **unavailable**. Every idea below states its
  fallback or is marked blocked.

**Committed anchors used repeatedly** (all at SQIsign NIST-I, log2 p ≈ 256):

| quantity | value | provenance |
|---|---|---|
| `log2 T_full` | 108.73088958800618 | MODELED-COMMITTED, RUN-WESOVOW-001 via EV-PEC-857664 OBS-M |
| `log2 M` (table entries) | 93.28 | MODELED-COMMITTED, EXP-WESOVOW-001 via DEC-20260802-48c72c gate_3 |
| `log2 B_opt` | 14.2 | MODELED-COMMITTED, RUN-WESOVOW-001 |
| `log2 T_DG` | 128 = log2(p)/2 | control C2 PASS, EXP-WESOVOW-001 |
| implied `1/P0` | 15.45 bits | MODELED-HERE = 108.73 − 93.28 |
| corrected overhead span | 21.1147 … 25.9193 bits | MODELED-COMMITTED, EV-PEC-857664 OBS-M (18 readings) |
| margin span at w = 2^30 | [8.3498, 13.1544] bits | MODELED-COMMITTED, OBS-M |
| L4-BATCH removable term | 11.502 (S-B) / 13.247 (S-A) bits | MODELED-COMMITTED, OBS-L; 48–59 % of total |
| null-object step cost | 4914.45–5118.83 mults (2^12.26–2^12.32) at p ≈ 2^40 | MEASURED, RUN-PEC-49c773-a; SP-9 attached |

Paper locators used below, all in `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`:
line **39** (vOW tradeoff √(N³/w) = p^{1/2+o(1)}/w^{1/2}, N = p^{1/3+o(1)},
"memory cost is essentially as high as the complexity", "parallelizes
perfectly"); line **41** (n processors: p^{1/2+o(1)}/(w^{1/2}·n); quantum pointer
to [29] Jaques–Schanck, "quantum computation may only be advantageous to reduce
the amount of memory, with the same time complexity"); line **43** (optimistic
assumptions); line **53** (the [24,26] p^{−1/2} adjacency event); line **133**
(Lemma 3.2 size bound); line **147** (Algorithm 1 step 6 — entries are sequences
of curves, only codomains needed); line **156** (Lemma 3.3 + the footnote naming
**batched evaluation of modular polynomials** as the likely fastest population
route — this footnote is the origin of L4-BATCH); lines **167–175** (Algorithm 2:
X ← B^{1/2}(p/2)^{1/6}, one table keyed by codomain, the Frobenius lookup at
line 171); lines **177–185** (the degree split, deg η ≤ X); line **191**
(Remark 1 — multiple small isogenies E → E^{(p)}, any one smooth suffices);
lines **210–218** (u = √log(p/2), Ψ(X,B) = p^{1/6+o(1)}, per-attempt
p^{1/3+o(1)}); line **230** (§4.1 cost model: M = Ψ(X,B)X, one F_{p^2}-operation
per entry, memory ≈ M, time ≈ M/P0); lines **234–238** (the five concrete pairs).

---

# The twelve ideas

---

### C2-1. Endpoint audit of the van Oorschot–Wiener interpolation: is the committed T(w) anchored at w = M or at w = 1, and does the NIST-I sign survive the answer?

**Which factor** — F7 (the collision mechanism) and the memory axis w. It enters
the exponent not at all and the *concrete comparison* completely: T(w) is the
single function through which every margin, crossover and threat statement in
this programme is expressed. An anchoring error in T(w) is an additive
`0.5·log2 M` = **46.64 bits** (MODELED-HERE, from committed `log2 M` = 93.28) at
NIST-I — larger than the entire measured-overhead programme (21–26 bits), the
whole disputed margin (8.35–13.15 bits), L4-BATCH (11.50–13.25), L2 (0.60–1.00),
A-3 (1.01) and every irreproducibility band (2.23 / 3.51) **combined**.

**Claim** — Three mutually inconsistent formulas for the same object are
currently on the record, and at most one can be right:
(a) `experiments/EXP-WESOVOW-001/cost_model.py` line 270 computes
`log2Tw = log2Tfull − 0.5·min(log2w, log2M) + overhead`, i.e. **T(w) = T_full /
√(min(w,M))**;
(b) `RUN-WESOVOW-001/execution_report.yaml` line 53 reports control C4 as
"PASS (by construction)" while stating the formula **T(w) = T_full·min(1,√(M/w))**,
which for every w ≤ M equals T_full and therefore is *not* what (a) computes;
(c) the frozen contract's own controls C3 and C4
(`EXP-WESOVOW-001/specification.yaml` lines 145–149) require
"T(w) must equal T_full for w ≥ M" and "At w = M, vOW time must equal T_full
exactly", which formula (a) violates by exactly `0.5·log2 M`.
The claim is that the vOW-consistent form is
**T(w) = T_full·√(M/w) for w ≤ M**, because vOW solves a claw of set size N in
√(N³/w), which at w = N returns N — the full-memory cost — so the numerator of
the interpolation is `M^{3/2}/P0 = p^{1/2+o(1)}` and **not** `T_full = M/P0 =
p^{1/3+o(1)}`. Substituting the p^{1/3+o(1)} number into a formula whose
numerator is p^{1/2+o(1)} is a nameable, checkable mechanism, and it is the
hypothesis this audit tests.

**Mechanism** — Under (a), memory is a *bonus*: T falls below T_full as w rises
from 1. Under the vOW-consistent form, memory is a *requirement*: T rises above
T_full as w falls below M. The two agree only at w = M under form (b) and
nowhere under form (a). The audit recomputes the entire committed table under all
three forms plus a fourth, purely local control: the naive
**unbalanced-split streaming bound**, obtained by splitting the degree as
X₁·X₂ = B·D with lists of size X₁² and X₂², storing the small list and streaming
the large one, which gives `T = M²/w` at memory `w = X₁²` and is achievable
without any vOW machinery. Since `M²/w ÷ (M^{3/2}/w^{1/2}) = √(M/w) ≥ 1`, the
streaming curve must lie **above** the vOW curve everywhere, and any model
placing T(w) below `M^{3/2}/w^{1/2}` is claiming to beat vOW without saying how.
Form (a) does exactly that.

**Minimal discriminating test** — Zero new compute; arithmetic on committed
numbers. (i) Evaluate all four curves at w ∈ {2^20, 2^25, 2^30, 2^35, 2^40, 2^50,
2^60, 2^80, M} for all five field sizes and all eighteen measured-gamma readings.
(ii) Run the frozen contract's own controls C3/C4 as *executable assertions*
against each form and report pass/fail per form. (iii) Report the crossover
memory `w*` at which each form's T(w) meets 2^{log2 p/2}. (iv) Re-derive the
committed `Base margin at zero overhead 34.2691` under each form and state which
form reproduces it (form (a) does, by construction — that is the known-answer
gate for the audit's arithmetic, not a validation of the form).

**Null object / control** — (1) **Endpoint control**: evaluate every form at
w = M; a form that does not return exactly T_full there is falsified against the
frozen contract's own C4 regardless of anything else. (2) **Ordering control**:
the streaming curve `M²/w` must lie above the vOW curve at every w; a model
violating that ordering is claiming an unstated improvement. (3) **Absurdity
control**: at w = 2^80 form (a) returns T = 2^68.7 at NIST-I (MODELED-HERE from
committed inputs), i.e. fewer operations than the 2^93.28 table entries the same
model says the algorithm must handle at full memory; any form producing
T(w) < T(M) for w < M is internally inconsistent.

**Falsifier** (reachable) — The audit is falsified if form (a) can be derived
from a *stated, documented* alternative model — e.g. w measured in a different
unit than M, or `T_full` intended as a per-attempt rather than total cost — that
simultaneously satisfies C3, C4 and the streaming-ordering control. If such a
derivation exists, the committed margins stand unchanged and this idea's
pre-registered arithmetic below is simply wrong.

**Pre-registered arithmetic (MODELED-HERE, can fail)** — At NIST-I under the
vOW-consistent form: margin at w = 2^30 and zero overhead
= 128 − (108.73089 + 0.5·(93.28 − 30)) = **−12.37 bits** (against the committed
**+34.2691**); with the committed overhead span 21.11–25.92 it becomes **−33.5 to
−38.3 bits**; at w = M the margin is 19.269 − overhead = **−6.65 to −1.85 bits**;
the zero-overhead crossover memory is `log2 w* = 93.28 − 2·(128 − 108.73089)`
= **54.74**, and for any overhead above 19.27 bits **no crossover exists at any
w ≤ M**. At NIST-III the same correction subtracts 0.5·(138.6 − 30) = 54.3 bits
from the committed +49.1-bit speedup at w = 2^30. **If this arithmetic holds, the
sign of the NIST-I comparison inverts and the "NIST-III/V retain comfortable
margins" position becomes memory-conditional rather than unconditional.** If it
does not hold, the committed position is confirmed on a stronger basis than it
currently rests on. Either outcome is worth the hour.

**Cost** — implementation: **very low** (≈100 lines of arithmetic reusing
`cost_model.py`'s Dickman grid unchanged). compute: **none** (< 1 minute).

**Ceiling** — Model substitution; **no claim tier** (DEC-20260802-48c72c). It can
change *which* modelled statements are citable and in which direction; it cannot
measure anything. Memory is the free axis and is reported at every point.

**Kills-it-early** — Reading `cost_model.py` line 270 beside
`specification.yaml` line 149 and `execution_report.yaml` line 53. If those three
agree on inspection, the idea is dead in ten minutes and costs nothing.

**Method ceiling** — *Strongest statement it could ever support:* "the committed
(time, memory) frontier for the p^{1/3+o(1)} method is off by `0.5·log2 M` at
every w < M, and the corrected frontier places the method's advantage over
Delfs–Galbraith only at memory within `2·(log2 T_DG − log2 T_full − overhead)`
bits of M." That is a statement about **this programme's cost model**, never about
the paper's theorem, which is asymptotic and untouched. *Nearest obstruction:* the
vOW result itself is cited, not verified, in this corpus (EV-WESO-001 records
"van Oorschot-Wiener [43] verified" at the level of the paper's use of it); the
constant 2.5 and the validity range of √(N³/w) in w are **not transcribed** and the
primary source is unreachable — so the audit must emit the curve in the form
`T(w) = κ·M^{3/2}/(w^{1/2}P0)` with κ unpinned, and report the *ratio* and the
*sign* (which are κ-independent for κ ≥ 1) as primary, the absolute locus as
secondary. *Nearby-object control:* apply the identical audit to the streaming
curve `M²/w`, whose derivation is entirely local and needs no external citation;
a form that fails the ordering test against it fails without any bibliography.
*Cheap pre-compute falsification:* evaluate every candidate form at w = M and
compare to T_full. One line, decides the anchoring question outright.

**Relation to prior records** — This is a **successor to and a precondition
for** IDEA-20260803-48e258, which computes the crossover locus p*(w) using
`margin(w) = 128 − (108.73089 − 0.5·log2 w + overhead_bits)` — i.e. form (a).
That proposal's known-answer gate (reproduce the committed margin band) would
*pass* under a wrong anchor, because it reproduces the same formula. This audit
supplies the one control that gate cannot contain. It does not duplicate p*(w)
and does not displace it; it fixes the function p*(w) is a level set of.

---

### C2-2. Charge the vOW step function: a fresh random sample is not an amortised table entry, and L4-BATCH does not survive the change of regime

**Which factor** — F7 (collision mechanism) × the per-entry cost law measured in
BATCH-003. It enters the *slope and the endpoints* of the tradeoff curve, not the
exponent. The unit mismatch is worth **13.5–16 bits** at NIST-I (MODELED-HERE),
concentrated entirely at the low-memory end.

**Claim** — The committed interpolation charges one vOW step at the same unit as
one table entry. These are different objects. (i) In Algorithm 1 (line 147) each
new entry is produced by **one** ℓ-isogeny step extending an existing entry —
amortised cost, one root-finding per ℓ+1 entries. (ii) A vOW step must produce an
**independent, seed-determined** element of L(E,X,B): sample a B-smooth degree
d ≤ X, then walk **Ω(d)** ℓ-steps from E. Nothing is amortised. So the vOW step
costs Ω(d) root-findings, not one. (iii) Worse, the batching gain of L4-BATCH is
an amortisation across *many entries sharing one ℓ*, which the table has by
construction and an isolated vOW sample has not. **Therefore the 11.50–13.25 bits
L4-BATCH removes from the high-memory endpoint are not removable at the
low-memory endpoint** — the two ends of the curve must be charged with different
per-step laws.

**Mechanism** — Let n_ψ = Ω(deg ψ) be the number of prime factors of the half
degree. With `log2 X` = 49.6 and `log2 B_opt` = 14.2 (MODELED-HERE from the
committed B_opt via X = B^{1/2}(p/2)^{1/6}), a smooth d ≤ X has u = log X/log B ≈
3.49 (this reproduces the committed "w moves only from 3.49 to 5.40" of RT3-C1 —
an independent consistency check on the arithmetic), so n_ψ is at least u ≈ 3.5
and typically larger because smooth numbers carry many small factors. Charging
n_ψ ∈ [4, 7] gives **2.0–2.8 bits**; adding the non-amortisable L4-BATCH term
gives **13.5–16.0 bits** of extra cost per vOW step relative to a table entry.
Direction: **against** the attack, and only at low w — it steepens the curve
exactly where the campaign has been quoting its margins.

**Minimal discriminating test** — Zero compute for the arithmetic; one bounded
toy measurement for n_ψ. (i) At toy p ∈ {2^20, 2^30, 2^40} and B ∈ {50, 100, 215},
enumerate B-smooth d ≤ X exactly and record the distribution of Ω(d) weighted by
d and by entry count — the same exact-enumeration machinery RT3-C1 already used
at (X,B) = (10^7,100) and (10^8,215), which gives a known-answer gate (it must
reproduce RT3-C1's Δ = 0.598 and 0.625 bits when asked for that statistic).
(ii) Recompute the tradeoff curve with a **two-law** charge: table-entry law at
w = M, vOW-step law at w < M, interpolating in log w. (iii) Report the size of
the resulting kink.

**Null object / control** — (1) **Unit control**: recompute with n_ψ = 1 and the
L4-BATCH gain applied at both ends; this reproduces the committed curve exactly
and is the known-answer gate. (2) **Direction control**: the correction must be
zero at w = M by construction; a two-law charge that moves the *high*-memory
endpoint has been implemented wrongly. (3) **Distribution null**: draw Ω(d) for
uniformly random d ≤ X (not smooth); the smooth distribution must be shifted
upward, and if it is not, the smoothness structure is not driving n_ψ and the
charge should be recomputed from the unrestricted distribution.

**Falsifier** (reachable) — If a vOW step function can be defined whose cost is
one root-finding — e.g. by walking the *previous* sample by one ℓ-step instead of
resampling — then n_ψ = 1 and the correction collapses to the L4-BATCH term
alone. **This is a serious and specific escape route and the test must look for
it**: a one-step vOW walk is a walk on the isogeny graph, not on L(E,X,B), so the
resulting collisions are graph collisions and no longer encode the degree
constraint deg ψ ≤ X. Whether the constraint can be maintained under a one-step
update is exactly the falsifier, and the answer decides the idea.

**Cost** — implementation: **low** (exact smooth enumeration already exists in
the corpus's RT3-C1 derivation). compute: **minutes** at (10^7, 100) and
(10^8, 215) scale; pure Python.

**Ceiling** — `toy` for the Ω(d) distribution (enumeration at X ≤ 10^8);
model substitution with **no claim tier** for the corrected curve. The measured
input it leans on (γ ∈ {0.8100336227, 0.9328644281}, non-independent, MA-8) is
`medium`. Memory position: the correction is **zero at w = M and maximal at
w → poly**, so it acts only on the interpolation, never on the paper's own claim.

**Kills-it-early** — If the one-step vOW update above is admissible (checkable at
the whiteboard against Algorithm 2's degree constraint at lines 167–181), the
n_ψ half of the idea dies immediately and only the L4-BATCH-asymmetry half
survives.

**Method ceiling** — *Strongest statement it could ever support:* "the two
endpoints of the interpolation are charged in incommensurable units, and the
low-memory end is understated by n_ψ·(per-step) + the L4-BATCH gain, i.e. by
13.5–16 bits at NIST-I." *Nearest obstruction:* the same asymmetry may apply to
the **baseline**. A Delfs–Galbraith walk step is also a single small-ℓ step and is
also unbatched — but SP-9 forbids using this corpus's C-NULL step measurement as a
DG cost, and the DG baseline constant k has been named necessary in three
consecutive red-team reports and executed in none. So the *absolute* corrected
crossover is not obtainable without k; only the *relative* statement about the
attack's own two endpoints is. That limitation must be printed on the output.
*Nearby-object control:* apply the identical two-law charge to a hypothetical
attack whose entries are independent by construction (no chain amortisation); the
correction must vanish there, because the amortisation it prices does not exist.
*Cheap pre-compute falsification:* read Algorithm 1 line 147 and Algorithm 2 lines
167–175 and check whether the table's entries are chained. They are ("sequences
of elliptic curves"), which is what makes the amortisation real.

---

### C2-3. Golden-claw multiplicity R: the tradeoff curve has never been charged for the fact that there are many correct answers

**Which factor** — F7 (collision mechanism), on the vOW branch only. Contributes
p^{o(1)}: it cannot move the exponent, and it can move the low-memory concrete
cost by an amount **of the same order as the entire disputed margin**.

**Claim** — The claw being searched for is not unique, and the committed model
treats it as if it were. Two independent sources of multiplicity: (i) **split
multiplicity** — Lemma 3.4's proof (lines 177–185) picks *one* prefix split of
deg φ, but *every* divisor d of D = deg φ with d ≤ X and D/d ≤ X yields a valid
(ψ, χ) pair and a distinct middle curve; (ii) **Remark 1 multiplicity** (line 191)
— there are generally several small isogenies E → E^{(p)} and any one being smooth
suffices. Source (ii) is a smoothness question and belongs to C1; **source (i) is
a pure search-structure question and is charged here.** vOW's cost for a golden
collision when there are c of them is not √(N³/w); the claim is that charging it
correctly moves the low-memory end by log2 R or 0.5·log2 R bits, and the audit
decides which.

**Mechanism** — D = (p/2)^{1/3} so `log2 D` = 85 at NIST-I; the admissible
divisors lie in the window [D/X, X] of multiplicative width exactly
X²/D = B_opt = 2^14.2. Divisors of a smooth D are roughly log-uniform, so
**R ≈ τ(D)·log B/log D = τ(D)/u** with u ≈ 5.99 (MODELED-HERE; note
log D = 2 log X − log B = 99.2 − 14.2 = 85 reproduces the committed geometry
exactly). For a squarefree-ish D with Ω(D) ∈ [8,14], τ(D) ≈ 2^Ω and
**R ≈ 2^5.4 … 2^11.4** (MODELED-HERE, wide on purpose — R is the quantity to be
measured, not asserted). R is p^{o(1)} by construction, because Ω(D) ≤ log D/log 2
and the operative bound is Ω(D) ≈ u·(small constant); **this is the method
ceiling and it is exact: R can never carry an exponent.**

**Minimal discriminating test** — A synthetic vOW simulation, no isogenies
required. Build a random function f on a space of size N ∈ {2^18, 2^20, 2^22}
with c ∈ {1, 2, 4, 16, 64, 256} planted golden collisions, run distinguished-point
vOW at memory w ∈ {2^8, 2^10, 2^12}, and measure expected function evaluations to
the first golden collision. Fit the exponent β in `T ∝ √(N³/w)·c^{−β}` and decide
between **β = 1** and **β = 1/2** — the two candidate scalings — or report a third
value. Separately, measure R at toy scale by exact factorisation of the true
minimal degree at small p (falls back to exact enumeration of smooth D in the
window if isogeny-side data is unavailable).

**Null object / control** — (1) **c = 1 arm** must reproduce the standard
single-golden-collision behaviour and the published constant (≈2.5·√(N³/w)); if
it does not, the simulator is wrong and nothing else in the run is readable. This
is the known-answer gate. (2) **Random-function null**: the same simulation on a
function with *no* planted golden collision must run to the budget without
success; a "success" there is an instrumentation bug. (3) **Scaling null**: vary N
at fixed c and confirm the 3/2 exponent in N before reading any c-exponent.

**Falsifier** (reachable) — β measured at or below 0.1 (multiplicity does not
help vOW at all) falsifies the idea and *closes* a route: it would mean the
low-memory end cannot be improved by multiplicity and the campaign's curve needs
no R correction. β ≈ 1 with R ≈ 2^8 would mean the committed low-memory rows are
**8 bits pessimistic**, which is inside the disputed margin and would have to be
carried in the opposite direction from C2-1 and C2-2 — an honest, inconvenient
outcome that must be reported with the same weight.

**Cost** — implementation: **medium** (a correct distinguished-point vOW
simulator is the only real work; ≈300 lines). compute: **low**, ≤ 2 CPU-hours,
pure Python, N ≤ 2^22.

**Ceiling** — `toy` (N ≤ 2^22 synthetic; no isogenies). The extrapolation from a
synthetic random function to the real key map is **exactly** what C2-10 tests, and
this idea may not be read as validated at crypto scale under any circumstance
(AGENTS.md rule 7).

**Kills-it-early** — If the corrected anchor of C2-1 shows no crossover exists at
any w ≤ M, an 8-bit improvement to the low-memory end changes no ordering and the
idea drops in priority (it does not become wrong).

**Method ceiling** — *Strongest statement it could ever support:* "the vOW branch
is cheaper than modelled by c^{β} where c = R = p^{o(1)}; the exponent 1/2 of the
low-memory endpoint is unchanged." *Nearest obstruction:* R ≤ τ(D) and
Ω(D) = O(log D/log 2) with the operative value ≈ u = √log(p/2) up to a constant,
so log R = O(√log p) — **superpolynomially small in p and therefore permanently
inside o(1)**. No amount of multiplicity moves 1/2 or 1/3. *Nearby-object
control:* run the same simulation on a claw with c golden collisions that are
*correlated* (e.g. all sharing a coordinate), which is closer to the real case
where the R middle curves all come from one φ; if β differs between independent
and correlated plantings, the independent-planting number may not be transferred.
*Cheap pre-compute falsification:* compute the divisor-window width X²/D and check
it equals B; if it does not, the R model is misderived before a line is run.

---

### C2-4. Track the Frobenius orbit, not the curve: the search is a self-claw under an involution, and the quotient graph is the honest state space

**Which factor** — F7 (collision mechanism) and the memory constant. Exponent
movement: **none, and provably so** — see the method ceiling. The reason it earns
a slot is that it is the enabling condition for C2-5 and it changes what a
"distinguished point" can be.

**Claim** — Algorithm 2 (lines 169–175) builds **one** table and looks up
`(E′)^{(p)}`. So the object is not a two-list claw; it is a **collision under the
graph automorphism σ: j ↦ j^p** inside a single list. Three consequences follow
that no record in this corpus currently states: (i) the key space may be quotiented
by σ, halving memory (a canonical form `min(j, j^p)` in any fixed ordering);
(ii) a distinguished-point predicate for vOW **must be σ-stable** or half the
golden collisions are invisible to it; (iii) the fixed-point locus of σ is exactly
the F_p-rational subgraph of size ≈ p^{1/2}, which is where L4-DESCENT lives — so
the quotient object is the shared boundary between this catalogue's slice and
lever L4-DESCENT, and the two must not be developed with incompatible key
conventions.

**Lossy-projection test (§2 of the inventor protocol, applied before any
experiment)** — Projection: `(E′, ψ) ↦ {j(E′), j(E′)^p}`. **What is discarded:**
the witness ψ entirely, and *which* of the two representatives is held.
**Is the loss compatible with the operations?** Yes: σ is an automorphism of the
ℓ-isogeny graph for every ℓ (the ℓ-neighbours of j^p are the p-th powers of the
ℓ-neighbours of j, since Φ_ℓ has coefficients in F_p), so the orbit of the
neighbours is a function of the neighbour-set of the orbit. The retained part
propagates deterministically under every operation Algorithm 1 performs.
**Is it genuinely lossy?** Yes, 1 bit per key plus the whole witness — and unlike
the (Δ, Π) counterexample of `KN-LIT-7595`, the discarded representative is **not**
recoverable from the orbit without computing a p-th power, which is exactly the
operation the algorithm is trying to avoid needing. Verdict: **passes the test as
a genuine projection, at a loss of one bit** — which is also the honest statement
of its ceiling.

**Mechanism** — |G/σ| = (|G| + #fix)/2 ≈ p/24 + p^{1/2}/2. Storing canonical
orbit representatives halves M (1.0 bit). More importantly, a σ-stable predicate P
(e.g. P depends only on the unordered pair {j, j^p}, or on Tr(j) = j + j^p and
N(j) = j^{1+p}, both of which lie in F_p) is satisfied by E′ **iff** it is
satisfied by (E′)^{(p)} — so filtering the table on P costs the *hit probability*
once, not twice. Under a non-σ-stable filter of density f the claw survives with
probability f², under a σ-stable one with probability f. That factor is what makes
C2-5 admissible at all.

**Minimal discriminating test** — (i) Verify σ-equivariance computationally at
toy scale: at p ∈ {2^20, 2^30} sample j, compute the ℓ-neighbour set of j and of
j^p for ℓ ∈ {2,3,5,7}, and check set equality after p-th powering — a pure
identity check with a definite answer. (ii) Measure the fixed-point density and
confirm it is ≈ p^{1/2}/(p/12). (iii) Measure the *actual* memory saving on a
built toy table (canonical-form dedup) and confirm it is 1.0 bit and not more
(more would indicate a collision bug).

**Null object / control** — (1) **Non-equivariant control**: repeat (i) with a
random field automorphism-like permutation of j-values that is *not* Frobenius;
set equality must fail. If it does not fail, the test has no power. (2) **Dedup
control**: the canonical-form table and the raw table must return the *same claw*;
a differing answer is a canonicalisation bug, not a finding.

**Falsifier** (reachable) — Set equality failing in (i) at any ℓ falsifies
σ-equivariance and kills the entire idea and C2-5 with it. (It is expected to
hold — Φ_ℓ ∈ Z[X,Y] — which is why the test is cheap and is run first.)

**Cost** — implementation: **low**. compute: **minutes** at p ≤ 2^30 with
ℓ ≤ 7, where Φ_ℓ is small enough to embed rather than fetch. **Fallback stated:**
the BATCH-003 modular-polynomial fetch route (47/47 HTTP 200, RUN-PEC-49c773-a) may
not be reachable now; ℓ ≤ 7 needs no network.

**Ceiling** — `toy`. Memory claim: **exactly 1.0 bit**, and the idea says so
rather than presenting a constant as a gain. Position on the vOW curve: unchanged
in shape; M and w both shift by 1 bit, so the curve translates and no crossover
moves by more than 0.5 bit.

**Kills-it-early** — Test (i) at ℓ = 2 alone, five minutes.

**Method ceiling** — *Strongest statement it could ever support:* "the state space
is G/σ, memory halves, and σ-stable predicates are the only admissible filters and
distinguished-point functions." *Nearest obstruction:* |G/σ| = |G|/2 + O(p^{1/2}),
so **no quotient by this involution can move any exponent** — the group has order
2 and that is a theorem, not an estimate. Any exponent gain would have to come
from a larger group acting on the key space, and none is known here; naming that
is the forward guidance. *Nearby-object control:* the same construction on the
2-isogeny graph *without* the Frobenius pairing (i.e. an ordinary collision search
with no involution) must show **zero** memory saving; if the implementation reports
a saving there, it is deduplicating something else. *Cheap pre-compute
falsification:* Φ_ℓ ∈ Z[X,Y] ⇒ σ-equivariance, one line of algebra; if this fails,
so does every downstream idea that uses it.

---

### C2-5. A σ-stable, per-step-prunable filter: spend the golden-claw multiplicity R to shrink both time and memory, and find out whether pruning survives the prefix-build cost

**Which factor** — F3 (list cardinality) as it is *consumed by the search*, not as
it is *built* — the restriction is a search-structure choice, and its exchange rate
is a collision-search question. Contribution is bounded by log2 R = p^{o(1)}
(≈5–11 bits at NIST-I, MODELED-HERE via C2-3). It **cannot** move the exponent and
the idea says so in its first line.

**Claim** — Lever L2's stated obstruction is that every natural restriction divides
the list and the hit probability by the same factor (1:1), and the BATCH-001
correction found the *generic* rate is e = 2δ, i.e. **worse** than 1:1. Both
readings assume **one** target. There are R of them (C2-3). Under a filter of
density f applied to the key space: the list (and the memory) shrink by f; the
claw survives if **any** of the R middle curves passes, i.e. with probability
≈ 1 − (1−f)^R ≈ min(1, fR); and if the filter is σ-stable (C2-4) the cost is paid
once, not twice. So the exchange rate is **free down to f = 1/R** and 1:1 (or
worse) below it. The claim is that this is the only known mechanism that makes
L2's exchange rate better than break-even, that its size is exactly R, and that it
is therefore an o(1) lever whose honest value is concrete bits, not an exponent.

**Mechanism** — Filter candidates that are σ-stable by construction: the low bits
of Tr(j) = j + j^p ∈ F_p; the low bits of N(j) = j^{1+p} ∈ F_p; membership of
Tr(j) in a prescribed residue class. Each is computable from the key alone at
O(1) F_{p^2}-operations. The claw condition at line 171 requires both E′ and
(E′)^{(p)} in the table; a σ-stable filter keeps both or neither.

**The obstruction that decides the idea** — Algorithm 1 builds entries by
**extension**: an entry of degree d is reached through a chain of prefixes. A
filter applied only to the *final* key prunes only the last layer and saves
nothing in time — memory yes, time no. For a time saving the predicate must be
**per-step prunable**: there must be a predicate P_k on depth-k prefixes with
P_k ⊇ P_{k+1}-preimages, so that a subtree can be discarded before it is built.
`Tr(j) mod 2^t` has no such structure — it is a hash of the endpoint, uncorrelated
with prefixes. **So the honest statement is: the filter buys memory for free and
buys time only if a prunable σ-stable predicate exists, and none is currently
known.** That is the idea's real content and its real test.

**Minimal discriminating test** — Toy scale, exact. (i) Build the full table
L(E,X,B) at toy p (log2 p ∈ [20, 40]) with small B, locate all R claws by exhaustive
matching, and **measure** the empirical survival probability of at least one claw
under σ-stable filters of density f ∈ {1/2, 1/4, …, 2^{-14}}, against the modelled
min(1, fR). (ii) Measure list shrinkage (must be exactly f) and memory shrinkage.
(iii) Measure *time* under (a) final-layer filtering and (b) a per-step prunable
predicate if any candidate is found — reporting the two separately and never
netting them.

**Null object / control** — (1) **Non-σ-stable filter arm**: the identical
experiment with a filter that depends on j rather than on {j, j^p}. The survival
probability must fall as f² (or min(1, f²R)); if it does not, the σ-stability
mechanism is not what is producing the effect and the whole story is misattributed.
This is the discriminating null and it is cheap. (2) **R = 1 arm**: restrict to
instances whose minimal degree admits exactly one admissible split; survival must
then be f and the free-shrinkage window must vanish. (3) **Time control**: assert
that final-layer filtering leaves the build time unchanged — a measured time saving
there is a bug.

**Falsifier** (reachable) — Survival probability falling as f (not min(1,fR)) in
the σ-stable arm falsifies the multiplicity mechanism outright and closes the
lever's only known escape from break-even. Equally, a per-step prunable σ-stable
predicate found to exist would *promote* the lever from memory-only to time-and-
memory — which is the outcome worth hunting.

**Cost** — implementation: **medium**. compute: **low–medium**, ≤ 4 CPU-hours at
log2 p ≤ 40 with B ≤ 100, pure Python. **Depends on C2-4 test (i) passing.**

**Ceiling** — `toy`, hard. Memory statement: memory falls by f *by construction*;
time falls by f **only** under the unresolved pruning condition, and no row may
report a time gain without it. Position on the vOW curve: shrinking M by f moves
the whole curve; under the corrected anchor of C2-1 that is worth 0.5·log2(1/f)
bits at fixed w, which must be reported.

**Kills-it-early** — The prefix-build argument above is a whiteboard argument; if
no σ-stable per-step prunable predicate can be exhibited in an hour of algebra,
the time half of the idea is closed before any code is written and only the memory
half proceeds.

**Method ceiling** — *Strongest statement it could ever support:* "list and memory
shrink by R = p^{o(1)} at no loss in success probability, and time shrinks by the
same factor iff a per-step prunable σ-stable predicate exists." *Nearest
obstruction:* R = τ(D)/u with log R = O(√log p) — permanently o(1) (C2-3's
ceiling). Additionally, the generic exchange rate e = 2δ recorded in the BATCH-001
lever correction is the *baseline* this must beat, and it is beaten only inside the
window f ≥ 1/R. *Nearby-object control:* apply the identical filter to a claw
problem with a **single** solution and confirm the free-shrinkage window is absent;
a filter that appears free there is measuring something other than multiplicity.
*Cheap pre-compute falsification:* count the divisors of a toy D in [D/X, X] and
compare to τ(D)/u; if R is not what the model says, the exchange rate is not
either.

---

### C2-6. Charge the machine, not the RAM: the p^{1/3} memory advantage under area–time, bisection-bandwidth and 3-D layout accounting

**Which factor** — the memory axis itself, and F7's realisability. It does not
move the F_{p^2}-operation exponent; it decides whether that exponent is the right
thing to compare. This is the memory-is-first-class idea of the catalogue.

**Claim** — The comparison "2^106.5 operations at 2^92.5 memory versus 2^128
operations at negligible memory" (paper lines 234–238) is stated in a
unit-cost-RAM model, in which a random access to a 2^92.5-entry table costs the
same as a field multiplication. Under a physically-charged model the ranking can
change, and the direction is computable in closed form. In a 2-D layout of M cells
the side is M^{1/2}, the bisection width is M^{1/2}, and routing M random accesses
across it takes Θ(M^{1/2}) time, so **AT = M·M^{1/2} = M^{3/2} = p^{1/2+o(1)}** —
**exactly the Delfs–Galbraith AT cost**, i.e. the exponent advantage vanishes in
2-D AT. In 3-D the bisection area is M^{2/3}, routing takes M^{1/3}, and
**AT = M^{4/3} = p^{4/9+o(1)} ≈ p^{0.444}**, which *beats* p^{1/2}. Under AT² in
2-D, **AT² = M² = p^{2/3}** against DG's p, so the advantage returns. The claim is
that the ranking is **metric-dependent**, that this is currently unstated anywhere
in the corpus, and that the paper's "parallelizes perfectly" (line 39) is a
statement about arithmetic and not about the table's access pattern.

**Mechanism** — Standard bisection-bandwidth accounting, applied to the two
endpoints separately: (i) full-memory endpoint — M random lookups against M cells;
(ii) vOW endpoint — distinguished-point search is *designed* for low communication
(w-entry shared table, one access per ~1/θ steps), so its AT cost degrades far more
gracefully. The audit's real output is that the two endpoints of the same
interpolation curve have **different sensitivities to the cost model**, which means
the interpolation itself is model-dependent and cannot be quoted without naming
the model.

**Minimal discriminating test** — Zero compute. Produce the five-field-size table
under four metrics — RAM-time, 2-D AT, 3-D AT, 2-D AT² — for (a) the full-memory
endpoint, (b) the vOW endpoint at w ∈ {2^30, 2^40, 2^50}, (c) Delfs–Galbraith —
using the corrected anchor from C2-1 and the committed overhead span. Report which
metric reverses which comparison.

**Null object / control** — (1) **Metric-consistency control**: under RAM-time the
table must reproduce the committed numbers exactly; a discrepancy means the metric
machinery is wrong before any physical claim is read. (2) **Baseline symmetry
control**: DG must be charged in the *same* metric, including its own memory
(negligible but not zero) and its own parallel communication (none). A metric
applied only to the attack is not a comparison. (3) **Degenerate-metric control**:
setting the wire cost to zero must return the RAM-model table exactly.

**Falsifier** (reachable) — If the p^{1/3} endpoint remains strictly ahead of DG
under *every* one of the four metrics at every field size, the "RAM-model artifact"
hypothesis is falsified and the memory advantage is robust — a strengthening of the
attack's position obtained at zero cost. If it loses under 2-D AT and wins under
AT², that is the honest and most likely outcome, and it converts the current scalar
comparison into a metric-indexed one.

**Cost** — implementation: **very low**. compute: **none**.

**Ceiling** — Model substitution, **no claim tier**. Explicitly *not* a physical
measurement: the AT model assumes free 2-D wires, uniform cell cost, and no memory
hierarchy, and it ignores that a real 2^92.5-entry store does not exist. Those
idealisations are stated on the output, not in a footnote.

**Kills-it-early** — The four exponent identities above (M^{3/2}, M^{4/3}, M²) are
one line each; if they do not reproduce p^{1/2}, p^{4/9}, p^{2/3} at M = p^{1/3},
the framing is wrong before any table is built.

**Method ceiling** — *Strongest statement it could ever support:* "the
p^{1/3+o(1)} result's advantage over p^{1/2} is metric-dependent: it is a tie in
2-D AT, a gain in 3-D AT and in AT², and a gain in unit-cost RAM." It can never
show the algorithm is *wrong* or *slower in operations*. *Nearest obstruction:*
the AT model is itself a bound-free idealisation and its use as a security metric
is contested in the literature; the corpus cannot verify that literature (sources
unreachable), so the audit must present the metrics as *arithmetic under stated
assumptions*, never as an accepted security accounting. *Nearby-object control:*
apply the same four metrics to an algorithm whose memory is genuinely negligible
(DG); the metric spread there must be small, and if it is not, the metric
implementation is charging something spurious. *Cheap pre-compute falsification:*
check that the 2-D AT cost of DG is p^{1/2}·O(1); if the machinery returns
something else for the *easy* case it cannot be trusted on the hard one.

---

### C2-7. Make L4-BATCH decidable without building the attack: an isolated batching microbenchmark with a known-answer gate at batch size 1

**Which factor** — the per-entry cost law, whose ℓ-dependent part
γ·log2(B_opt) = **11.502 bits (S-B) / 13.247 bits (S-A)** is 48–59 % of the
21.233–25.223-bit corrected overhead and is **the single largest residual term in
the cost model** (MODELED-COMMITTED, EV-PEC-857664 OBS-L). It is exponent-free — it
lives entirely in the o(1) — and it is nonetheless the largest untested number in
the campaign.

**Claim** — L4-BATCH is currently an **identifiability collision**: two
incompatible worlds — "batched multipoint evaluation reaches Õ(log p) per entry"
and "batching stalls at ℓ^δ for some δ > 0" — produce the *same* observable,
because the observable is a margin band computed from an unbatched implementation
plus a scenario flag. The claim is that the collision is breakable by a
**microbenchmark of the batching kernel alone**, without implementing the attack,
without a table of 2^93 entries, and without touching the smoothness side.

**Mechanism** — OBS-L's argument (a *review-side derivation*, SP-5: citable as a
review finding, never as run evidence) is that Algorithm 1 specialises Φ_ℓ at
N ≈ M/ℓ ≫ ℓ arguments per ℓ, and that multipoint evaluation of the ℓ+2 coefficient
polynomials at N arguments costs Õ(ℓ² + Nℓ), i.e. **Õ(1) per entry once N ≫ ℓ**,
with root-finding batching to Õ(log p) per entry. That argument has a *measurable*
signature: amortised per-entry cost as a function of batch size N must fall like
ℓ/N + const and **plateau** at a constant once N ≫ ℓ. If it instead plateaus at
c·ℓ^δ, the argument is wrong and L4-BATCH is partly unavailable. The experiment
measures the plateau.

**Minimal discriminating test** — Implement only the kernel: (i) multipoint
evaluation of the ℓ+2 coefficient polynomials of Φ_ℓ at N points in F_{p^2}, and
(ii) batched root-finding of the resulting N polynomials. Count F_{p^2}
multiplications per entry for ℓ ∈ {11, 23, 53, 101, 151, 211} (the C-SEED /
extension grid already used) and N/ℓ ∈ {1, 2, 4, …, 256}, at p = 1099511627563 (the
committed BATCH-003 prime, so the unit and the field match exactly). Fit the
plateau level and its ℓ-exponent δ_batched. Report δ_batched with the same
estimator, windows and pairing rule the frozen contract EXP-PEC-49c773 used, so the
numbers are commensurable with the committed γ.

**Null object / control** — (1) **Known-answer gate at N = ℓ+1 (no batching)**:
the measurement must reproduce the committed unbatched law within its published
bands, i.e. γ ∈ {0.8100336227, 0.9328644281} paired with its own intercept under
the binding pairing rule. A microbenchmark that cannot reproduce the number it is
generalising is void — this is the same gate IDEA-20260803-48e258 imposes on the
crossover machinery, applied here. (2) **Structure-free null**: run the identical
kernel on *random* polynomial families of the same degrees. The batching argument
is structure-free, so the null must show the **same** plateau; if the real Φ_ℓ
plateaus lower, something structural (not batching) is being measured, and if it
plateaus higher, the modular polynomial's coefficient growth is the cost and must
be charged separately. (3) **Decay control (inventor protocol §3)**: the amortised
cost must *decay* as N/ℓ increases and then flatten. A quantity that does not decay
when the parameter that should destroy it increases is the canonical artifact tell,
and here it would mean the batching is not happening at all.

**Falsifier** (reachable) — δ_batched ≥ 0.4 at the plateau falsifies "Õ(1) per
entry" and re-prices L4-BATCH at less than half its assumed value, narrowing the
committed [8.3498, 22.2927] span from the top. δ_batched ≤ 0.05 with a plateau at
O(log p) confirms it and moves the *whole* 11.5–13.25 bits into the attack's
favour, which is the outcome most adverse to the programme's current position and
must be reported with equal weight.

**Cost** — implementation: **medium–high** (multipoint evaluation and batched root
finding in pure Python; SageMath unavailable, stated). compute: **medium**, ≤ 6
CPU-hours at ℓ ≤ 211 and N/ℓ ≤ 256. **Fallback if Φ_ℓ cannot be fetched:** run the
kernel on the structure-free null family alone and report **only** the batching
exponent, marking the Φ_ℓ arm UNRUN under AGENTS.md rule 5 — the batching claim is
structure-free, so the null arm alone still decides δ_batched, with the modular-
polynomial-specific constants missing and declared missing.

**Ceiling** — `medium` at most (field bits = 2·40 = 80, per
docs/claims-and-verification.md, matching EV-PEC-857664's own derivation), and only
for the per-entry cost law at ℓ ≤ 211. **Never** crypto-scale: B_opt = 2^14.2 is
6.48 unmeasured octaves above ℓ = 211 (assumption L1), and that gap is the reason
this measurement cannot settle the attack, only the kernel.

**Kills-it-early** — The known-answer gate at N = ℓ+1. If the kernel cannot
reproduce the committed unbatched per-entry counts, stop.

**Method ceiling** — *Strongest statement it could ever support:* "batched
multipoint evaluation of Φ_ℓ achieves amortised per-entry cost c·ℓ^{δ_batched} at
p ≈ 2^40 for ℓ ≤ 211 and N/ℓ ≤ 256." *Nearest obstruction:* L1's 6.48 octaves — the
plateau at ℓ = 211 says nothing rigorous about ℓ = 2^14.2, and the method ceiling
recorded in CORR-4 (γ = exponent(M) − 1 ≤ 1 for this pipeline) bounds the *unbatched*
law only. A second obstruction: batching requires a working set, which is C2-8, and
a plateau measured with unlimited memory is not a plateau the attack can use.
*Nearby-object control:* the structure-free null family is exactly this control and
it is built into the design rather than added afterwards. *Cheap pre-compute
falsification:* check that Õ(ℓ² + Nℓ)/(N) → Õ(ℓ²/N + ℓ) per *batch* and hence
Õ(ℓ/N + 1) per *entry* — if the algebra does not give a plateau, the experiment has
nothing to find and should not be run.

---

### C2-8. The batching gain is a function of memory: L4-BATCH's 11.5–13.25 bits are not carriable along the vOW curve, and the working-set requirement is computable

**Which factor** — L4-BATCH × the memory axis w. Exponent contribution: none. What
it decides is whether the campaign's practice of carrying L4-BATCH as a
**w-independent two-valued scenario** (as IDEA-20260803-48e258 does, and correctly
for its purpose) is admissible once the curve is corrected.

**Claim** — Batched evaluation buys its Õ(1) per entry by holding N ≫ ℓ arguments
for one ℓ simultaneously. In table-build mode that is free: the table *is* the
working set. In vOW mode there is no table — points are generated independently —
so batching requires running many chains concurrently and grouping them by their
current ℓ. With π(B_opt) ≈ 2^{14.2}/ln(2^{14.2}) ≈ 1915 ≈ 2^10.9 distinct primes
and a batch requirement of N ≫ ℓ = 2^14.2, the concurrent-chain buffer is
**≈ 2^25–2^27 entries** (MODELED-HERE). Therefore: **below w ≈ 2^25 the L4-BATCH
gain is unavailable in vOW mode; above it, w must be partitioned between the
batching buffer and the distinguished-point store**, and the effective vOW memory
is w − buffer, not w. At the campaign's headline point w = 2^30, the buffer eats
2^25–2^27 of it, which is 0.05–0.17 bits of √w — small — but at w = 2^25 it eats
all of it.

**Mechanism** — Emit the **surface** g(w) = batching gain in bits as a function of
available memory, with three regimes: w < buffer (gain 0), buffer ≤ w < M (gain
present, memory partitioned), w ≥ M (full table, gain full). Then recompute the
tradeoff curve with g(w) applied rather than a constant.

**Minimal discriminating test** — Zero compute for the surface (arithmetic on
π(B_opt), the N ≫ ℓ threshold from C2-7, and the committed w grid). One bounded
measurement to pin the threshold: reuse C2-7's microbenchmark and record the
**smallest N/ℓ** at which the plateau is reached within 0.1 bits — that number, not
an assumed "≫", sets the buffer.

**Null object / control** — (1) **Regime control**: at w ≥ M the surface must
return exactly the committed constant gain (11.502 / 13.247 bits); a surface that
disagrees at the endpoint is misimplemented. (2) **Monotonicity control**: g(w)
must be non-decreasing in w; a non-monotone surface indicates the partition
accounting is double-counting. (3) **Zero-buffer null**: setting the buffer to 0
must return the current w-independent treatment exactly, isolating how much of the
change is due to the buffer.

**Falsifier** (reachable) — If the measured plateau threshold is N/ℓ ≈ 2 rather
than ≫ 1, the buffer collapses to ≈ 2^12 and the surface is flat over the entire
plotted range — the current w-independent treatment is then vindicated and the idea
is closed with a mechanism. If the threshold is N/ℓ ≥ 64, the buffer is ≈ 2^30 and
**L4-BATCH is unavailable at every memory budget the campaign has ever quoted**,
which would remove 11.5–13.25 bits from the attack's side at exactly the point
where its margin is disputed.

**Cost** — implementation: **low** given C2-7. compute: **none** beyond C2-7.

**Ceiling** — Model substitution, **no claim tier**; the threshold input is `medium`
at ℓ ≤ 211 and inherits L1's 6.48-octave gap. Memory is the independent variable,
which is the point.

**Kills-it-early** — π(B_opt)·ℓ arithmetic; if the buffer comes out below 2^20 the
idea is uninteresting in ten minutes.

**Method ceiling** — *Strongest statement it could ever support:* "the batching
gain is a step function of memory with a computable threshold, so it may not be
carried as a constant across the tradeoff curve." *Nearest obstruction:* a smarter
batching schedule may reduce the buffer — e.g. batching *across attempts* rather
than across chains (this is lever A7, cross-attempt amortisation, which BATCH-001
minted for exactly this kind of composition and which is invisible at the source's
parameters). Any buffer bound here is therefore an **upper** bound on the
requirement under one schedule, not a lower bound over all schedules, and must be
labelled that way. *Nearby-object control:* compute the same surface for an
algorithm with no ℓ-loop (a single-ℓ walk); its buffer must be ≈ ℓ, not π(B)·ℓ, and
if the machinery does not show that it is not modelling the ℓ-multiplexing.
*Cheap pre-compute falsification:* if π(B_opt)·ℓ ≪ any w of interest, the whole
idea is inert; check first.

---

### C2-9. Position the quantum search stage honestly: charge qubits, depth, queries and QRAM for claw finding and for quantum vOW, and state which cost model (if any) leaves the exponent below 1/3

**Which factor** — F7 (collision mechanism) under a quantum model. This is the
**only** place in this catalogue where an exponent below 1/3 appears at all, and it
appears in a *query* model, which is not a cost model. Every sentence below is
written to prevent that distinction from being lost.

**Claim** — Three positions must be computed and reported together, and none is an
algorithm proposed here:
(i) **Quantum claw finding on the new claw.** Claw finding between two sets of size
N has a quantum walk algorithm of Õ(N^{2/3}) *queries* with Õ(N^{2/3}) quantum
memory. With N = p^{1/3+o(1)} this is **p^{2/9+o(1)} = p^{0.2222…} queries at
p^{2/9} QRAM**. It is stated here only as a *positioning*, and specifically: it is
a query count under a free-QRAM assumption, the corpus cannot verify the source
(primary sources unreachable), and the paper's own pointer (line 41, [29]
Jaques–Schanck) says the opposite conclusion holds under RAM-model costing —
"quantum computation may only be advantageous to reduce the amount of memory, with
the same time complexity".
(ii) **Grover over the adjacency event.** The classical [24,26] method (line 53)
draws random walks until E′ is adjacent to E′^{(p)}, an event of probability
O(p^{−1/2}); Grover over the walk seeds gives **p^{1/4+o(1)} queries at polynomial
quantum memory**. This derivation is elementary and needs no citation — it is
stated here in-house precisely so the comparison does not rest on a reference the
corpus cannot fetch. (A published quantum Õ(p^{1/4}) algorithm for this problem is
*recollected* but **not verified in this corpus and must not be cited** until
retrieved; the in-house derivation stands on its own.)
(iii) **Grover over the re-randomisation loop is worthless and this must be said
once, in writing.** P0^{−1} = p^{o(1)} (factor F4), so √(P0^{−1}) = p^{o(1)}: no
exponent exists there to recover. Any future proposal claiming a quantum gain from
"fewer attempts" is refuted at the whiteboard by the same argument that refutes the
classical version.

**Mechanism** — Compute all three positions in **three** costings, at all five
field sizes: (a) query model with free QRAM; (b) unit-cost-RAM quantum circuit
model with QRAM charged as Õ(√M) depth per access (the Jaques–Schanck-style
objection, reconstructed in-house rather than cited); (c) depth×width (DW) with an
explicit qubit count. Report, for each, the *exponent* and the *concrete* qubits,
circuit depth, T-depth surrogate (counted as F_{p^2}-multiplications requiring
reversible implementation), and the QRAM size — never a bare "quantum speedup".

**Minimal discriminating test** — Zero compute. The deliverable is a 3 (positions)
× 3 (costings) × 5 (field sizes) table with the exponent and the four resource
figures per cell, plus one sentence per cell naming which of the three positions
dominates there. The discrimination is: **does any costing other than the free-QRAM
query model leave a quantum exponent strictly below 1/3?** If no, the quantum lane
is closed for exponent purposes with a mechanism (QRAM access depth), which is a
first-class negative. If yes, that cell is named and becomes a hypothesis.

**Null object / control** — (1) **Classical-limit control**: setting the quantum
speedup to 1 must return the classical table exactly. (2) **Resource-consistency
control**: the qubit count for position (i) must equal the classical memory
exponent 2/9·log2 p; a table where quantum memory is smaller than the algorithm's
own working set is misaccounted. (3) **Baseline symmetry**: Delfs–Galbraith must be
charged in the same three costings, including its Grover variant; charging quantum
resources only to the new method is not a comparison.

**Falsifier** (reachable) — The idea's central assertion — that at least one
non-query costing preserves an exponent below 1/3 — is falsified if all of (b) and
(c) push every position to ≥ 1/3, or if position (ii)'s p^{1/4} dominates position
(i)'s p^{2/9} in every realistic costing (which would say the *old* method
quantises better than the new one, an inversion worth knowing).

**Cost** — implementation: **low**. compute: **none**.

**Ceiling** — Model substitution, **no claim tier**, and additionally: **no
quantum resource estimate here is validated against any quantum literature**, since
primary sources are unreachable. Positions (i) and the RAM-model objection are
carried as **UNVERIFIED-RELAYED** and must be marked so in every downstream use;
only position (ii)'s derivation and position (iii)'s refutation are self-contained.
Nothing here claims p^{1/4} for the F_{p^2} problem, and position (ii)'s p^{1/4} is
a **quantum query count for the classical p^{1/2} method**, which is a different
object from the goal's classical target and may not be conflated with it.

**Kills-it-early** — Position (iii)'s one-line refutation is already established
(factor F4 carries exponent 0); if a proposal's quantum content reduces to it, stop
there.

**Method ceiling** — *Strongest statement it could ever support:* "under free-QRAM
query accounting the search stage admits exponent 2/9; under every costing that
charges QRAM access by distance, it does not." *Nearest obstruction:* the quantum
query lower bound for claw finding on N-sets is Ω(N^{2/3}), so **2/9 is the floor
of this method** and no tuning reaches below it — a hard, statable ceiling for the
whole quantum-claw lane. *Nearby-object control:* apply the same three costings to
Grover on an *unstructured* p^{1/2}-density search (position (ii)); if the costing
machinery does not reproduce the textbook p^{1/4} there, it is not trustworthy on
the harder case. *Cheap pre-compute falsification:* check that position (i)'s QRAM
size p^{2/9} exceeds any plausible physical memory at NIST-I (2^56.9 quantum
words); if the resource is absurd, the exponent is a mathematical curiosity and
must be presented as one.

---

### C2-10. Does the generic tradeoff bound even apply here? A null-object control on the key map's randomness, deciding whether a below-vOW point is a structural question or a lower-bound question

**Which factor** — F7 and the tradeoff curve (lever L5). No exponent is claimed;
the idea decides **which kind of argument** could ever close or open L5.

**Claim** — L5 asks for a point strictly below √(N³/w). The vOW curve is optimal
for *unstructured* claw finding; escaping it requires structure in the map
`entry ↦ key`, i.e. `(smooth degree d, cyclic-kernel index) ↦ j(codomain)`. The
claim is that this map's deviation from a random function is **measurable at toy
scale**, and that the measurement decides whether L5 is a structure question (open,
with a named place to look) or a lower-bound question (closed against generic
methods, with forward guidance naming what remains).

**Mechanism** — Measure, at toy p, statistics of the key map that a random function
of the same size would fix: (i) the collision profile (number of keys with
multiplicity k, against the Poisson prediction for a random map of the same
domain/range sizes); (ii) the distribution of keys over σ-orbits (against uniform);
(iii) the auto-correlation between a key and the key of its ℓ-neighbour, for ℓ
inside and outside B; (iv) the distribution over the F_p-locus, which is where the
map is *known* to be non-uniform (the fixed points of σ) and therefore serves as a
positive control that the instrument can detect non-randomness at all.

**Minimal discriminating test** — Build L(E,X,B) exhaustively at log2 p ∈ [20, 40]
with small B, compute all four statistics with bootstrap intervals, and compare
against (a) a random function on the same sized sets and (b) a random *bijection*.
Report each statistic as a signed deviation in σ-units.

**Null object / control** — (1) **Random-function null** and (2)
**random-bijection null**, both of the same shape, run through the identical
measurement code — this is the inventor protocol §3 requirement applied literally.
(3) **Positive control**: the F_p-locus statistic, which *must* show a detectable
deviation; if the instrument cannot see the one non-uniformity that is known to
exist, it has no power and none of its nulls mean anything. (4) **Decay control**:
any detected excess must **decay** as B (hence the mixing of the walks producing
the keys) increases; an excess that is constant in B is the canonical artifact
tell recorded in `KN-TECH-056`.

**Falsifier** (reachable) — Every statistic within 2σ of both nulls, with the
positive control firing, is a **scoped closure**: at the tested scale the key map
is indistinguishable from random by these four statistics, so a below-vOW point
cannot be built on them, and the remaining routes are named (algebraic relations
among Φ_ℓ evaluations; the quaternion-side lattice representation of C2-12;
multi-instance amortisation A5/A7). Any statistic outside both nulls **and**
decaying in B is a structural signal and becomes the seed of an L5 hypothesis.

**Cost** — implementation: **medium**. compute: **low–medium**, ≤ 3 CPU-hours,
pure Python, ℓ ≤ 7 to avoid the Φ_ℓ fetch dependency (fallback stated).

**Ceiling** — `toy`, absolutely. Four statistics at log2 p ≤ 40 close four
statistics at log2 p ≤ 40, and AGENTS.md rule 6 scopes the negative to exactly
that. This idea's value is that it produces a **closure with a mechanism** rather
than a fatigue report, which is what the inventor protocol §4 requires and what
this programme's standing saturation claims currently lack.

**Kills-it-early** — The positive control. If the F_p-locus deviation is not
detected, the instrument is dead and the run stops before the nulls are read.

**Method ceiling** — *Strongest statement it could ever support:* "the key map is
statistically indistinguishable from a random map with respect to collision
profile, orbit distribution, neighbour correlation and locus occupancy, at
log2 p ≤ 40 and B ≤ 100." *Nearest obstruction:* statistical indistinguishability is
**not** algebraic structurelessness — the map is defined by polynomial identities
(Φ_ℓ) and a sieve could exploit an identity that no moment statistic sees. That
gap is the honest limit and it is the forward guidance: the surviving route is
algebraic, not statistical. *Nearby-object control:* run the identical statistics on
the **2-isogeny graph walk without the smooth-degree constraint**, whose mixing is
well studied; the statistics must look random there too, and if they do not, the
instrument is measuring the walk rather than the constraint. *Cheap pre-compute
falsification:* count |L(E,X,B)| against Lemma 3.2's bound (line 133) at toy scale;
if the realised cardinality does not sit in the predicted range, the object being
measured is not the object of the theorem.

---

### C2-11. Re-optimise B under a memory budget: a fourth tradeoff curve that the committed model never computes, and the only cheap candidate for a point below vOW

**Which factor** — F3 (list cardinality) *through* the memory constraint, and the
tradeoff curve itself. This is lever **L5** done as arithmetic rather than as an
aspiration. It cannot move the p^{1/3} exponent at full memory; it can change the
*shape* of the curve between the endpoints, which is exactly what L5 asks for.

**Claim** — The committed model optimises B for **time at full memory**, then
applies vOW to the resulting fixed (M, T_full). That is not the best the algorithm
can do at memory w. A memory-constrained attacker should re-optimise:
`T(w) = min over B of [ M(B)/P0(B) if M(B) ≤ w, else the vOW cost at (M(B), w) ]`.
Since M(B) ≈ B·(p/2)^{1/3}·ρ(u) falls with B while P0(B)^{−1} rises
superpolynomially, there is a genuine optimisation with a computable optimum, and
the claim is that the resulting curve lies **on or below** the vOW-on-fixed-B
curve everywhere, strictly below somewhere, and that "somewhere" has never been
located.

**Mechanism** — `cost_for_B` and `optimize_B` already exist in
`experiments/EXP-WESOVOW-001/cost_model.py` (lines 162–188) with a validated
Dickman grid (ρ(2) reproduced against 1 − ln 2). The change is to add a memory
constraint to the objective and re-run the same grid. Nothing new is modelled; the
existing model is asked a question it was never asked.

**Minimal discriminating test** — Zero new compute. For each field size and each
w ∈ {2^20 … 2^90}, sweep log2 B over the committed grid, evaluate both branches,
take the min, and emit the resulting frontier alongside (i) the corrected vOW curve
from C2-1, (ii) the streaming curve M²/w, (iii) Delfs–Galbraith. Report where the
re-optimised curve is strictly below vOW-on-fixed-B and by how many bits.

**Null object / control** — (1) **Endpoint control**: at w ≥ M(B_opt) the
re-optimised curve must return exactly the committed T_full — the constraint is
inactive there. (2) **Monotonicity control**: T(w) must be non-increasing in w.
(3) **Dominance control**: the re-optimised curve must never be *above* the
fixed-B vOW curve, since fixed-B is one of the options in the min; a violation is
an implementation error. (4) **Grid-boundary control**: report whether the optimal
B at each w sits at a grid boundary, which would mean the optimum is outside the
committed grid and the answer is truncated rather than optimal.

**Falsifier** (reachable) — If the re-optimised curve coincides with the fixed-B
vOW curve to within 0.1 bits at every w, the lever is **closed by computation**:
re-optimisation buys nothing, and L5 must look elsewhere (forward guidance: the
remaining routes are structural, i.e. C2-10 and C2-12, not parametric). If it is
strictly below by several bits over a wide w range, that is a genuine improvement
of the *tradeoff* — never of the time exponent — and it must be reported with both
its memory and its position relative to the corrected anchor.

**Cost** — implementation: **very low** (a constrained objective around existing
functions). compute: **none** (< 1 minute).

**Ceiling** — Model substitution, **no claim tier**. Any improvement found is a
p^{o(1)}-level rearrangement inside a model whose overhead is disputed by 21–26
bits and whose anchor is under audit by C2-1; it must be re-emitted after C2-1
concludes, and it is meaningless if the anchor is wrong.

**Kills-it-early** — One evaluation at w = M: if the constrained optimum equals the
unconstrained one there (it must), and the two curves are already visually identical
at w = 2^40, the idea is a five-minute closure.

**Method ceiling** — *Strongest statement it could ever support:* "at memory w the
best choice of B gives time T*(w), which is below the fixed-B vOW interpolation by
Δ(w) bits; the exponents at both endpoints are unchanged." *Nearest obstruction:*
M(B) ≥ (p/2)^{1/3}·B·ρ(u) means the p^{1/3} floor in M is not removable by choosing
B — lowering B lowers the list but raises P0^{−1} superpolynomially, and the product
is what the model already optimises. So the achievable Δ(w) is bounded by the
curvature of that product, which is o(1)-scale. *Nearby-object control:* run the
same constrained optimisation on a problem where the memory-time product is known
to be flat (a pure birthday search); Δ must be 0 there, and a non-zero Δ means the
optimiser is exploiting the grid rather than the problem. *Cheap pre-compute
falsification:* check that the unconstrained optimum reproduces the committed
`log2 B_opt` = 14.2; if it does not, the objective has been changed rather than
constrained.

---

### C2-12. Non-materialised claw search: state exactly what would have to be computable from j(E) alone for the search to cost less than M, and run the predictor test that decides it

**Which factor** — F3 as consumed by F7: the assertion `time ≥ |L|` holds only if
the list must be enumerated. This is lever **L3** with its unstated prerequisite
**A3** (non-materialised representation) made explicit, and it is the **only**
exponent-carrying idea on the search side of this catalogue.

**Claim** — Every search-side exponent below 1/3 requires that the claw be located
without enumerating a p^{1/3}-size structure. That requires a predicate or
predictor, computable from j(E) alone in time o(M), that concentrates the true
middle key into a set of size M^{1−δ}. The claim is (a) that this is the exact and
only requirement — everything else is packaging — and (b) that its existence is
**testable at toy scale by a predictor test with a null object**, cheaply, before
any algorithm is designed.

**Mechanism, including the circularity that must be named up front** — The
quaternion side offers exactly such a representation: the trace-zero rank-3
sublattice of Hom(E, E^{(p)}) with discriminant p/4 (the object BATCH-001's D1
established, replacing the goal record's Minkowski category error), on which finding
the minimal degree is a rank-3 shortest-vector problem — polynomial. **The
circularity is that constructing that lattice requires End(E), which is
polynomial-time equivalent to the problem itself** (the reduction network at
paper line 127). So the non-materialised route lives or dies on whether *partial*
lattice information is obtainable from j(E) at cost o(M). That is the question, and
it is not answered by asserting the lattice exists.

**Minimal discriminating test — the predictor test** — At toy p, for many instances
E: (i) compute the true claw and record its middle key j(E′); (ii) evaluate a
**pre-declared, finite** predictor family on j(E) alone — the F_p-rationality flag,
Tr(j) and N(j), the roots of Φ_m(j(E), y) for m ≤ m_max, and the same for j(E)^p;
(iii) measure whether any predictor's output set contains j(E′) more often than a
uniform random set of the same size. Report the concentration factor with bootstrap
intervals.

**Null object / control** — (1) **Random-target null**: replace j(E′) with a
uniformly random supersingular j and re-run; the concentration factor must be 1.
(2) **Random-predictor null**: replace the predictor family with random sets of the
same sizes; must give 1. (3) **Positive control**: use a predictor that *does*
contain the answer by construction (e.g. the full ℓ-neighbourhood at depth equal to
the true degree's factor count) and confirm the instrument reports a large
concentration; without this the nulls have no power. (4) **Cost control**: every
predictor must be timed, and any predictor whose evaluation cost is not o(M) at toy
scale is disqualified *before* its concentration is read — otherwise the test
rewards predictors that are secretly doing the search.

**Falsifier** (reachable) — Concentration factor within 2σ of 1 for every declared
predictor, with the positive control firing, closes the family: **the declared
predictor family carries no o(M)-computable information about the middle key at the
tested scale**, and lever L3/A3 must be pursued through a different family (forward
guidance: multi-instance/amortised A5-A7, or local/p-adic invariants, neither of
which is in this family). A concentration factor significantly above 1 with a
disqualifying cost is *not* a positive result and must be reported as a cost
failure, not a signal.

**Cost** — implementation: **medium–high**. compute: **medium**, ≤ 6 CPU-hours at
log2 p ≤ 32, ℓ ≤ 7 and m_max ≤ 13 (fallback to embedded small Φ_m if fetch fails).

**Ceiling** — `toy`. A closure here closes a *declared finite family at toy scale*
and nothing more; per AGENTS.md rule 6 it may not be restated as "no predictor
exists". This is precisely the discipline the inventor protocol §4 demands and the
reason the family is declared before the run rather than after.

**Kills-it-early** — The cost control. If every candidate predictor costs Ω(M) at
toy scale, the family is empty and the run is not worth starting.

**Method ceiling** — *Strongest statement it could ever support:* "for the declared
family, no o(M)-computable predictor concentrates the middle key, so a sub-M search
built on that family is impossible; a sub-M search must therefore obtain lattice
information not computable from j(E) by these means." *Nearest obstruction:* the
reduction network (line 127) — any o(M) procedure returning substantial information
about End(E) would itself be a sub-M solution to EndRing, so the predictor test is,
in effect, hunting for a partial break; a *negative* is therefore the expected and
still-useful outcome, and a *positive* would demand immediate independent review at
the highest available tier before any further work. *Nearby-object control:* run the
identical test on a curve where the answer is known to be predictable — e.g. an E
**on** the F_p locus, where the minimal degree is 1 and the middle key is E itself —
and confirm the instrument reports maximal concentration. A method that cannot
distinguish the F_p case from the generic case has not identified the load-bearing
structure. *Cheap pre-compute falsification:* write the claim with explicit
quantifier order — `∃ predictor P, ∀ E: j(E′) ∈ P(j(E))` versus
`∀ E, ∃ predictor P_E` — and check that no proposed construction lets P depend on
E in a way the uniform statement forbids. The lattice route fails this check
visibly, which is why the circularity is stated in the mechanism rather than
discovered later.

---

# Batches

Four bounded batches. At most **three** concurrent non-archive tasks. Write scopes
are disjoint (one task directory per batch, no shared ledger or experiment file is
edited by any producer). Sequencing is set by one dependency only: **S1 fixes the
function every other cost statement is expressed in**, so S1 runs alone first.

### BATCH-S1 — "Fix the curve before anything is charged against it"
- **Objective.** Determine whether the committed tradeoff function T(w) is anchored
  at w = M or at w = 1, correct it if it is not, and re-emit every (time, memory)
  comparison — including the NIST-I and NIST-III signs — under the corrected
  anchor, the two-law step charge, the multiplicity charge, and the streaming and
  re-optimisation control curves.
- **Ideas.** C2-1, C2-2 (arithmetic half), C2-3 (arithmetic half), C2-11.
- **Grouping rationale.** All four are arithmetic over committed numbers and all
  four write the same object: the (T, w) frontier. Splitting them would produce
  four incompatible frontiers. C2-1 is logically prior to the other three, which is
  why they share a task rather than run concurrently.
- **Budget.** 1 task, ≤ 3 wall-clock hours, **zero** new compute. Deliverable: a
  four-curve × five-field-size × eighteen-gamma-reading table plus a pass/fail
  report on controls C3/C4 per candidate form.
- **What it decides.** Whether the campaign's positive NIST-I margin at w = 2^30
  survives; whether any crossover with Delfs–Galbraith exists at any w ≤ M; whether
  "NIST-III/V retain comfortable margins" is unconditional or memory-conditional;
  and whether re-optimising B under a memory budget buys anything (lever L5, by
  computation).

### BATCH-S2 — "The largest untested term"
- **Objective.** Break the L4-BATCH identifiability collision by measuring the
  batching kernel in isolation, and determine whether the resulting gain is
  carriable along the tradeoff curve or only at full memory.
- **Ideas.** C2-7, C2-8.
- **Grouping rationale.** C2-8 consumes exactly one number produced by C2-7 (the
  smallest N/ℓ at which the plateau is reached). Running them apart would either
  duplicate the microbenchmark or leave the buffer threshold assumed.
- **Budget.** 1 task, ≤ 8 wall-clock hours, ≤ 6 CPU-hours, pure Python, ceiling
  `medium` and only at ℓ ≤ 211 / p ≈ 2^40.
- **What it decides.** The exponent δ_batched of the batched per-entry law and
  hence how much of the 11.50–13.25-bit L4-BATCH term is real; and the memory
  threshold below which none of it is available.

### BATCH-S3 — "Objects for the collision structure"
- **Objective.** Establish whether the search stage has any exploitable structure
  beyond the generic claw: verify the Frobenius quotient, price the multiplicity
  filter, test the key map against null objects, and test the middle-key predictor
  family.
- **Ideas.** C2-4, C2-5, C2-10, C2-12 (plus C2-3's toy multiplicity measurement,
  which shares the same toy table build).
- **Grouping rationale.** All four build or consume the **same toy object** —
  an exhaustively enumerated L(E,X,B) at log2 p ≤ 40 with its claws located — and
  all four share the same null-object harness. Building that object once is the
  batch's main cost; splitting the batch would build it three times. C2-4's
  σ-equivariance check gates C2-5 and runs first inside the task.
- **Budget.** 1 task, ≤ 10 wall-clock hours, ≤ 12 CPU-hours, ceiling `toy`
  throughout, hard. Fallback recorded: ℓ ≤ 7 with embedded Φ_ℓ if the modular-
  polynomial fetch route is unavailable.
- **What it decides.** Whether the σ-quotient is real (1 bit of memory and the
  admissibility of σ-stable filters); whether multiplicity buys a better-than-
  break-even exchange rate in L2; whether the key map is distinguishable from
  random by four declared statistics; and whether any declared o(M)-computable
  predictor concentrates the middle key — the last being the only exponent-carrying
  question in this catalogue.

### BATCH-S4 — "Charging the machine"
- **Objective.** Report the whole comparison under cost models other than unit-cost
  RAM: area–time in 2-D and 3-D, AT², bisection-bandwidth-limited parallel time,
  and three quantum costings with qubits, depth, queries and QRAM charged
  explicitly.
- **Ideas.** C2-6, C2-9.
- **Grouping rationale.** Both are pure re-costings of the *same* frontier under
  *different* metrics, both consume S1's corrected anchor and nothing else, and both
  produce the same shaped table. Neither touches any measurement.
- **Budget.** 1 task, ≤ 3 wall-clock hours, **zero** compute. Depends on S1.
- **What it decides.** Whether the p^{1/3} memory advantage is a RAM-model artifact
  (2-D AT tie), survives in other metrics (3-D AT, AT²), and whether any quantum
  costing other than the free-QRAM query model leaves an exponent below 1/3 — with
  the 2/9 query-model floor stated as a ceiling, never as a claim.

**Concurrency plan.** S1 alone → then S2, S3, S4 concurrently (three tasks, the
declared maximum). S4 is gated on S1's corrected anchor; S2 and S3 are not gated on
anything and could start earlier if the anchor question is answered by inspection
in the first ten minutes (C2-1's kills-it-early).

---

# Honest accounting (docs/inventor-protocol.md §5)

**Objects considered.** (1) The keyed table L(E,X,B) with the codomain j-invariant
as the tracked object — the incumbent, and **declared off-limits as the primary
lens** for this session per §1. (2) The **σ-orbit** {j, j^p} under the Frobenius
automorphism — passes the lossy-projection test (C2-4), loses one bit and the
witness, propagates deterministically because Φ_ℓ ∈ Z[X,Y]. (3) The **divisor
window** of the minimal degree, i.e. the golden-claw multiplicity R — lossy (keeps
a count and a window, discards the curves), propagates under extension by one
prime. (4) The **batching working set** — a resource object, not an algebraic one;
it does not pass the lossy-projection test and is not offered as a new attack
object, only as a cost-model dimension. (5) The **(T, w, metric)** frontier itself
treated as the object of study, which is what C2-1, C2-6, C2-9 and C2-11 track.
(6) The **middle-key predictor** as a projection of the instance (C2-12) — declared
finite in advance so the test can fail.

**Enumeration status.** Per `KN-OPEN-019`, this program has **no** written
object-enumeration for the ECDLP or for this problem. The six objects above are a
**sketch, not a taxonomy**, and no record may treat "not in this list" as "not a
route." No lane is declared closed by this session.

**`dominated_by`.** For C2-1, C2-2, C2-3, C2-6, C2-7, C2-8, C2-9, C2-10, C2-12:
**"n/a (no result claimed)"** — these are audits, measurements and controls, and
none proposes an attack. For C2-4: dominated by the incumbent table search on every
axis except memory, where it is ahead by exactly 1.0 bit; that is a constant and is
reported as one. For C2-5 and C2-11: **unresolved pending computation**, and the
frontier rows checked in reaching that statement are (i) Delfs–Galbraith
p^{1/2}·(log p)^{O(1)} time at polynomial memory; (ii) Wesolowski p^{1/3+o(1)} time
and memory, heuristic-conditional, above a superpolynomial o(1); (iii) the
vOW interpolation √(N³/w) between them, whose anchor is exactly what C2-1 audits;
(iv) the quantum rows of C2-9 (elementary Grover p^{1/4} in queries; a relayed and
**unverified** claw-finding p^{2/9} in queries at p^{2/9} QRAM). C2-5's candidate
gain is R = p^{o(1)} and therefore lies **inside** row (ii) rather than beside it;
C2-11's candidate lies on or below row (iii) by a margin that has not been computed.
No `null` is written anywhere in this file.

**`sota_delta`.** Zero on every attack axis — nothing here is faster, smaller or
cheaper than any row above, and no idea claims to be. The *assessment* delta, if
BATCH-S1 returns as its pre-registered arithmetic predicts, is a **sign inversion**
of the programme's headline NIST-I comparison at w = 2^30 (from +8.35…+13.15 bits
in favour of the attack to roughly −33…−38 bits against it) obtained at zero
compute; and if it returns the other way, the committed position gains a control it
currently lacks. The *measurement* delta available from BATCH-S2 is the first
number of any kind on the term that carries 48–59 % of the corrected overhead.

**Enumerated closures produced by this session.** None. This catalogue closes
nothing; it designs the tests that could. Two closure-shaped statements are
*prepared* with their mechanisms already named, so a later session does not have to
invent them: (a) C2-4's ceiling — the Frobenius group has order 2, so this quotient
can never move an exponent, and a larger group acting on the key space would be
needed; (b) C2-3's ceiling — log R = O(√log p), so multiplicity is permanently
inside o(1). Both are stated as ceilings on *methods*, not as claims that any
direction is impossible.

**Open directions for the next session.** (i) Lever **A7** (cross-attempt
amortisation) interacts with C2-8's buffer and with C2-2's step charge and is not
costed here. (ii) The **DG baseline constant k** remains unquantified after four
batches and blocks every *absolute* crossover statement; it is named blocking in
C2-2 and in IDEA-20260803-48e258, and the fetch is still unexecuted. (iii) The
vOW constant (≈2.5) and the **validity range in w** of √(N³/w) are untranscribed
and unreachable; C2-1 works around them by emitting ratios, but the absolute locus
stays UNRUN until they are obtained. (iv) The **[35] reduction cascade** carries no
exponent anywhere in the record (defect GD-1 of the goal record); every search-side
result here is about **OneEnd**, and its transfer to Isogeny is uncosted.
(v) **L4-DESCENT** (the F_p-locus lever) meets this slice at C2-4's fixed-point
stratum, and the two must agree on a key convention before either builds anything.
