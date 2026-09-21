# A4 — ECDLP transfers and bridges: catalogue of 11 research ideas

Slice: isogeny/cover transfer, MOV/embedding-degree and anomalous cases, Weil
descent, elliptic-curve trapdoors, lattice/HNP relevance to the **plain** ECDLP,
multi-target and preprocessing regimes.
Anchors: `KN-OPEN-011`, `KN-OPEN-012`, `KN-OPEN-018`.
Author: idea-generator. Date: 2026-08-05. Status: **catalogue only** — no ledger
record, no ID minted, no hypothesis status touched, no work assigned.

---

## 0. Standing conventions for this catalogue

**Baseline.** Matched Pollard rho at `0.886·sqrt(N)` charged group operations
(corpus convention, rho-with-negation), and matched BSGS at `2·ceil(sqrt(N))`.
Every cost below is stated against those two.

**Two frontier rows cited as UNVERIFIED RECOLLECTIONS.** This corpus does not
hold a transcribed primary source for either. Neither may be used as a decision
threshold until a `KN-LIT` entry transcribes the exact statement and constant.
- **MT-REC.** Kuhn–Struik (SAC 2001), multi-target rho for `L` targets in **one**
  group at total `~sqrt(L·N)`. Existence/venue confirmed by web search recorded
  in `IDEA-20260802-007.novelty_screen`; **the constant and the exact regime are
  not transcribed here.**
- **PP-REC.** Corrigan-Gibbs–Kogan (EUROCRYPT 2018), generic DLP-with-preprocessing
  lower bound `S·T² = Ω(εN)`. Same status: existence confirmed in that same
  screen; statement not transcribed.

**Classical facts this catalogue leans on, and their verification status.**
- **TATE.** Tate's isogeny theorem over finite fields: `E`, `E'/F_q` are
  `F_q`-isogenous **iff** `#E(F_q) = #E'(F_q)`. Textbook; **not transcribed into
  this corpus**. It is load-bearing for A4-1/A4-6/A4-11 and a `KN-LIT` transcription
  is owed before any of those becomes a ledger record.
- **ISO-COST.** Ordinary-curve isogeny path finding at `Õ(p^{1/4})` low storage
  (GHS random walk; `KN-LIT-317` reports Galbraith 2011 improving it ~14x at 160
  bits). Corpus status `confidence: reported`, bulk-seeded; constant not transcribed.
- **ENDO-COST.** Computing `End(E)` for ordinary `E/F_p` in subexponential
  `L_p(1/2)` under GRH + heuristics (`KN-LIT-309` Bisson; `KN-LIT-3063`). Corpus
  status `reported`; exponent not transcribed. Load-bearing for A4-11.
- **COVER-COST.** Genus-`g` Jacobian index calculus over `F_q` at `Õ(q^{2-2/g})`;
  `Õ(q)` for prime-order curves over `F_{q³}` via an `(ℓ,ℓ,ℓ)`-isogeny from the
  Weil restriction (`KN-LIT-742`, Tian 2020, `citation_verified: read`).
  Load-bearing for A4-4.

**SageMath is unavailable and uninstallable in this environment.** Every idea
below is specified Sage-free: `F_p` arithmetic in pure Python integers, Vélu's
formulas for small `ℓ`, division polynomials by recurrence, group order by
BSGS/Mestre at toy sizes (`p ≤ 2^32`), Hasse-interval search. Where a step would
normally be a Sage one-liner, the fallback is named in the idea.

**Novelty.** Not adjudicable in this session. Nothing below is claimed new and
nothing is dismissed as known. `novelty_status` for the catalogue as a whole:
`unverified` (corpus grepped: `knowledge/`, `ledger/proposals/`,
`ledger/evidence/`, `ledger/decisions/`; no web literature search performed).

**Live state built on, not rediscovered.**
`H-IT-001` / `EXP-IT-001` is ACTIVE and has failed three times on **controls**,
never on mathematics: `EV-IT-001` (crash — infrastructure, never evidence),
`EV-IT-002` (mechanically clean; planted control passed only under an unamended
`C_special_MOV` substitution applied outside its FIX-4 scope, to an
embedding-degree-1 endpoint; null gate never run; empty edge ledger),
`DEC-20260803-004` / BATCH-046 (inconclusive; transfer-gate interpretation VOID).
Two named defects are **off-limits as fixes**: an embedding-degree-1 endpoint is
not a transfer demonstration, and `C_special_MOV` may not be recalibrated without
a field-DLP-inclusive cost.

---

## 1. Object enumeration before ideas (inventor protocol §1)

**Established families in this slice, declared off-limits as the primary lens:**
(a) *path in an `F_p`-isogeny graph to a member of a named weak family* — this is
`H-IT-001`'s object, live and repeatedly uncontrolled; (b) *GHS/cover Weil descent
over `F_{q^n}`* — heavily mined and structurally absent over prime fields;
(c) *short vector in an HNP lattice from leaked nonce bits* — the leakage model,
excluded from the plain problem by `KN-OPEN-011` / `KN-OPEN-018`.

**Candidate objects enumerated, scored `new-or-repackaged / testable / survival
depth`:**

| # | Tracked object | New? | One-step propagation definable? | Survives until |
|---|---|---|---|---|
| O1 | the pair `(p, N)` — the isogeny-class label | repackaging of a classical invariant, **but never used as a lens here** | yes, trivially: constant under `F_p`-isogeny (TATE) | never dissolves; that is the point (A4-1) |
| O2 | the multiset of prime degrees of a transfer path | adaptation | yes, per Vélu step | dissolves when the path leaves one volcano level |
| O3 | the conductor `f = [O_K : End(E)]` (vertical position) | adaptation | yes: `f → ℓ^{±1}f` per vertical step | dissolves at `f = 1` / at the crater |
| O4 | the embedding-degree divisor `k = ord_N(p)` | repackaging of O1 | yes: constant (function of O1) | never (A4-1, A4-5) |
| O5 | a truncated `p`-adic elliptic logarithm of a lifted point | genuinely different lens here | yes: `λ([m]P) = m·λ(P)` in the formal group | dissolves at the lift-ambiguity subgroup (A4-3) |
| O6 | base-field-shrinkage exponent `e(n,g)` of a cover transfer | adaptation | yes, symbolically | dissolves at `n = 1` (A4-4) |
| O7 | a **batch** of `L` targets carried across an isogeny class to one hub curve | adaptation of index-calculus amortization to the isogeny orbit | yes: transport by an evaluated isogeny | dissolves when endomorphism rings differ (A4-6, A4-7) |
| O8 | the preprocessed advice string for the isogeny graph, size `S` | adaptation | yes: table lookup + short walk | bounded by PP-REC only if it is advice about the **group** (A4-7) |
| O9 | the archimedean/integer *size* of an `x`-coordinate lift | genuinely different lens here | **no** — see A4-10's lossy-projection verdict | dissolves at the first group operation (A4-9, A4-10) |
| O10 | a weakness *predicate*, classified by what it factors through | methodological, not an attack object | yes | never (A4-11) |

**The load-bearing observation of this catalogue.** Objects O1 and O4 are
*perfectly non-lossy in the wrong direction*: the special-family predicates the
`H-IT-001` lane hunts (anomalous `N = p`; low embedding degree `k = ord_N(p)`;
supersingular) all **factor through `(p, N)`**, which by TATE is **constant on the
`F_p`-isogeny class**. So the object "path in the `F_p`-isogeny graph" carries
*zero* information about those predicates. Applying the lossy-projection test
(§2 of the protocol) to the composite map `walk → (p,N) → predicate`: the walk is
discarded entirely and the predicate is retained unchanged — the projection is not
lossy at all, it is *constant*. A constant projection is not a new object; it is
the absence of one. **This is the algebraic reason every planted control in the
`H-IT-001` lane has had to cheat**, and it retrodicts the exact recorded defect:
`EV-IT-002` O-5 records that the recovered path was "a 1-hop edge between two
special curves." Walking from a special curve by an `F_p`-isogeny *must* land on
another special curve. That is not a bug in the harness; it is TATE.

A4-1 turns this into a falsifiable audit rather than an assertion. A4-2, A4-3 and
A4-11 are the three lanes that survive it. A4-6 is the lane that *uses* it.

---

## 2. The eleven ideas

### A4-1. Class-invariance audit of the transfer-target predicate: is the `H-IT-001` weak-endpoint search searching a constant function?
**Claim** — For `E/F_p` with prime-order subgroup `G` of order `N`, every predicate
in `EXP-IT-001`'s `special_families` list (`anomalous_N_eq_p`,
`low_embedding_degree_MOV`, and supersingularity) is a function of `(p, N)` alone,
hence by TATE is **constant on the `F_p`-isogeny class of `E`**. Consequence, stated
as a point prediction with a number: for **100%** of `F_p`-rational isogeny walks of
any length, with any degree coprime to `N`, `special(E_start) = special(E_end)`; the
minimal path length to a *different* value of the predicate is `∞`, not large.
Therefore `R_xfer ≥ 1` on generic curves is true **by construction, not by
measurement**, and the third family (`subfield_Weil_descent_friendly`) is vacuous
over a prime field because `F_p` has no proper subfield.
**Mechanism** — TATE: `F_q`-isogenous ⟺ equal group order. `#E'(F_p) = #E(F_p) = h·N`,
so `N` and `p` are class invariants; `k = ord_N(p)` is a function of `(N,p)`;
`N = p` is a function of `(N,p)`; ordinary/supersingular is a function of the trace
`t = p+1-#E`. The `H-IT-001` search therefore evaluates a constant over its whole
search space. The one escape the argument does **not** close: isogenies not defined
over `F_p` (which change the rational point count), and predicates that do not
factor through `(p,N)` — see A4-11's partition.
**Minimal discriminating test** — Zero-compute core plus a cheap empirical audit.
(i) Write the factorization `walk → (p,N) → predicate` symbolically for each of the
three families; state the quantifier order explicitly (`∀ p ∀ E ∀ φ over F_p`).
(ii) Sage-free empirical check at `p ∈ {2^20…2^24}`: sample 200 curves, compute
`#E` by BSGS in the Hasse interval, bucket by order, and for each bucket with `≥2`
members verify that `anomalous` and `k = ord_N(p)` are constant within the bucket
**and** that an explicit small-`ℓ` Vélu walk from any bucket member stays in its
bucket. Report the number of bucket-crossing walks.
**Null object / control** — Two. (a) **Non-isogenous null**: pairs of curves with
*different* orders; the predicate must be free to differ, and it must be observed
to differ in at least some pairs — otherwise the audit has no resolving power and
is measuring nothing. (b) **Broken-arithmetic null**: run the identical bucketing
on a deliberately corrupted `#E` routine (off-by-one in the Hasse search); the
audit must then report bucket-crossings, proving the instrument can see a crossing
when one exists.
**Falsifier (reachable)** — Any single observed `F_p`-rational, `N`-coprime isogeny
whose endpoints differ in any of the three predicates. Also falsified if control
(b) fails to produce crossings, which would mean the audit cannot detect a crossing
and is uninformative in either direction.
**Cost** — impl **low** (BSGS point count + Vélu for `ℓ ≤ 19`, ~300 lines pure
Python); compute **low** (< 1 CPU-hour).
**Ceiling** — This is a **closure with a named obstruction**, not an attack. It
moves no exponent. What it can achieve: retire the `EXP-IT-001` weak-endpoint
search as *structurally* unable to return a positive over `F_p`, replacing three
inconclusive batches of instrument repair with an argument. What it cannot achieve:
it says nothing about non-`F_p`-rational isogenies, nothing about predicates outside
the three named families, and **nothing about whether the ECDLP is hard**. Scope,
affected vs safe: it *widens* the safe set — no prime-field curve can be walked into
anomalousness or low `k` — and affects no deployed parameter.
**Kills-it-early** — If the empirical audit finds even one bucket-crossing walk,
either TATE is being misapplied (most likely: the harness's edge relation is not
`F_p`-rational isogeny, e.g. it uses modular-polynomial roots over `F_{p^2}`) or the
point counter is wrong. Either finding is decision-relevant and must be routed to a
correction, not absorbed.

---

### A4-2. Synthetic marked-set transfer harness: the only positive control the prime-field transfer lane can honestly have, with a density-swept decay prediction
**Claim** — A transfer harness can be given a **valid** positive control by marking
a random set `S` of `j`-invariants of density `ρ` (marked in `j`-space, therefore
*not* a class invariant, therefore genuinely reachable by a walk) and pairing it
with a *modelled* special solver charged at `c_smart·log2(p)` — the honest
anomalous/Smart cost, which is a strict **upper bound on the benefit** any real
`O(log p)` special family could confer. Under this harness: (i) the planted walk
starts at a marked `j` and is **forced to terminate at an unmarked `j`**, so the
instance on which the DLP is posed is non-special and the recovery certificate is a
**real Vélu pullback** `log_E(Q) = deg-scaled log_{E'}(φ(Q))` verified as `[k]P = Q`
on `E`; (ii) the measured recovery rate `r(ρ)` **decays** as `ρ → 0`, tracking the
sparse-set hitting-time prediction to within a pre-registered KS threshold.
**Mechanism** — A4-1 shows the real families cannot be walked to over `F_p`; so
either the lane has no positive control at all, or the marked set is synthetic. A
synthetic mark separates the two things the harness must do — *find a short path to
a sparse target* and *pull a log back through an evaluated isogeny* — from the
question of whether any real family sits at the target. The density sweep supplies
the reachable negative: a signal that does **not** decay when the parameter meant to
destroy it (falling `ρ`) increases is the canonical artifact tell
(`docs/inventor-protocol.md` §3.1).
**Minimal discriminating test** — Sage-free. At `p ≈ 2^20`, build the `ℓ = 2,3`
volcano by modular-polynomial root-finding over `F_p` (Cantor–Zassenhaus, pure
Python), persist a **raw edge ledger** (`(j_from, j_to, ℓ)` rows, non-empty, hashed).
Mark `S` at `ρ ∈ {2^-4, 2^-6, 2^-8, 2^-10}`, 30 planted instances per `ρ`. Plant by
walking `h` hops from a marked `j` and **rejecting any endpoint that is marked**.
Solve by BFS/MITM from the instance; on hitting `S`, call the modelled solver, then
**evaluate the composed Vélu isogeny on `Q`** and verify `[k]P = Q` on the original
curve. Report `r(ρ)`, `R_xfer`, and the charged ledger.
**Null object / control** — Three, all live, none skippable.
(a) **Null-plant**: instances with `ρ = 0` (no marks). Recovery must be `0/30` and
`R_xfer` must be reported as *unbounded*, not `0.0`. This is the gate never run in
`EV-IT-002`/`EV-IT-008`.
(b) **Shuffled-edge null**: identical pipeline on a random permutation of the edge
ledger preserving degree sequence. Recovery must collapse to the random-hit rate;
if it does not, the "path" is packaging arithmetic.
(c) **Certificate null**: replace the Vélu pullback with the direct BSGS solve that
`EV-IT-002` O-5 caught. The harness must **reject** this run as non-discriminating;
a harness that accepts it is void.
**What a passing control would NOT establish** — Explicitly: not that any real weak
family is reachable over `F_p` (A4-1 says the three named ones are not); not that
`ρ` of that magnitude occurs in nature; not that `c_smart·log2(p)` is the right cost
for anything but the anomalous family; and not one bit about crypto-scale, since the
graph diameter at 20 bits is not the diameter at 256.
**Falsifier (reachable)** — `r(ρ)` flat across the sweep (artifact); or null (a)
returning any recovery; or null (b) matching the real arm; or the pullback
certificate disagreeing with an independent BSGS solve on the *planted* instances.
**Cost** — impl **medium** (modular polynomial `Φ_2`, `Φ_3` hard-coded; Vélu for
`ℓ ∈ {2,3}`; ~800 lines); compute **low** (< 4 CPU-hours).
**Ceiling** — Instrument calibration only; **moves no exponent, not even a
constant**. Its value is that it is the cheapest object that converts the
`H-IT-001` lane from "harness void, three batches running" into either a
demonstrably capable instrument or a documented incapacity.
**Kills-it-early** — If, before any run, the shuffled-edge null cannot be
constructed while preserving the degree sequence (volcano degree sequences are
rigid at `ℓ=2`), control (b) is unavailable and the harness has no structure-
destruction gate; say so and use `ℓ = 3` or abandon.

---

### A4-3. The `p`-adic lift-ambiguity meter: does the Smart/SSSA channel carry a measurable number of bits about `k` when `N ≠ p`?
**Claim** — Define, for a lift `P̃ ∈ E(Q_p)` of `P` to precision `p^3` and the
formal-group logarithm `λ`, the observable `μ(P,Q) = λ([N]Q̃)/λ([N]P̃) mod p`. For
`N = p` this equals `k` exactly (SSSA). The claim to test: for `N ≠ p` the empirical
**mutual information** `I(μ ; k)` is `0.00 ± σ_null` bits, where `σ_null` is the
measured positive bias of the same estimator on independently resampled `k` — i.e.
the channel is *exactly* closed, with a named obstruction (the lift-ambiguity
subgroup `[N]·ker(red) = N·pZ_p` covers all of `Z/N` when `gcd(N,p) = 1`), and there
is **no near-anomalous regime**: the advantage is a step function of `[N = p]`, not
a decay in `|N − p|/p`.
**Mechanism** — The tracked object is O5, a *truncated* `p`-adic elliptic logarithm:
a genuinely lossy projection (it discards the point and retains a residue) whose
one-step propagation is exactly `λ([m]P) = m λ(P)`, deterministic in the formal
group. That is what makes it testable. The question is at which point the retained
part stops determining `k`. The interpolating family — sample curves at controlled
`|N − p|` including `N = p`, `N = p ± 1`, `N = p ± small`, and random `N` — turns a
folklore boundary into a measured one.
**Minimal discriminating test** — Sage-free: Hensel-lift `P` to `Z/p^3` on the short
Weierstrass model (pure Python), compute `λ` from the standard formal-group series
truncated at the same precision. `p ≈ 2^20`, 5 bands of `|N−p|`, 2000 instances per
band, fresh random lift per instance. Estimate `I(μ ; k)` with a bias-corrected
(Miller–Madow) estimator, binned to `2^6` bins, and report both `I` and the
estimator's null bias.
**Null object / control** — (a) **Resampled-`k` null**: identical pipeline with `k`
drawn independently of `Q`; gives `σ_null`, the estimator's floor. (b) **Anomalous
positive control**: the `N = p` band **must** return `I ≈ log2(N)` bits and recover
`k` exactly on 2000/2000 — if it does not, the `p`-adic implementation is broken and
every other band is uninterpretable. (c) **Lift-randomization control**: 20 distinct
random lifts of the *same* `P`; `μ` must be observed to vary over the full range for
`N ≠ p` (that variation *is* the obstruction) and to be invariant for `N = p`.
**Falsifier (reachable)** — `I(μ;k) > σ_null + 3σ` in any `N ≠ p` band, replicated
at a second `p`, surviving control (c). That outcome is a **partial-information
channel on the plain ECDLP** and would be the single highest-value result in this
catalogue. The opposite outcome is a scoped closure with a named obstruction.
**Cost** — impl **low-medium** (~400 lines); compute **low** (< 2 CPU-hours).
**Ceiling** — Negative outcome: closes the "near-anomalous" family with an argument
rather than a tally, and bounds the trapdoor lane (a designer cannot hide a partial
`p`-adic channel). Positive outcome: even `1` bit per instance would be an
information channel outside the generic group model and would change the program's
picture; but `I` bits per instance reduce rho only to `0.886·sqrt(N/2^I)`, so a
small `I` moves a **constant**, not an exponent — say so plainly before running.
Scope: affects all prime-field curves symmetrically; no special family.
**Kills-it-early** — Control (b) failing at `N = p`. Also: if the lift-ambiguity
argument can be written down as a one-line proof that `μ` is uniform on `Z/N`
independent of `k` (it plausibly can), the experiment is unnecessary and the
argument alone is the deliverable — **attempt the proof first, it costs nothing**.

---

### A4-4. The base-field-shrinkage identity: a symbolic exponent audit forcing every cover/descent transfer to `≥ 1/2` at extension degree `n = 1`
**Claim** — For a transfer of the ECDLP on `E/F_{q^n}` (group order `N ≈ q^n`) into
a genus-`g` Jacobian over `F_q` solved by index calculus at `Õ(q^{2-2/g})`, the
achieved exponent in `N` is `e(n,g) = (2 − 2/g)/n`. This identity (i) **reproduces**
the two published points in the corpus — `n=3, g=3` gives `e = 4/9`… and with
Tian's `Õ(q)` for prime-order `F_{q³}` curves gives `e = 1/3` (`KN-LIT-742`) — and
(ii) forces `e(1,g) = 2 − 2/g ≥ 1` for all `g ≥ 2`, i.e. **strictly worse than rho's
`1/2` at `n = 1` by a factor `N^{1/2}` or more**. The advantage of the entire cover
family is therefore a function of extension degree alone, and prime fields have
`n = 1`.
**Mechanism** — The cover attack wins because the *base field shrinks* while the
group size does not; the genus-`g` Jacobian over `F_q` has ~`q^g` elements and
index calculus costs `q^{2-2/g}`, sublinear in the group size only because `q ≪ q^n`.
Over `F_p` there is no proper subfield to shrink into, so `g` must rise with no
compensating fall in `q`, and every `g > 1` is a strict loss. The tracked object is
O6 — the exponent as a two-variable symbolic expression, which is a lossy projection
of the whole attack (it discards the construction and retains only its cost scaling)
and propagates compositionally under chaining transfers.
**Minimal discriminating test** — Purely symbolic, zero compute. (1) State `e(n,g)`.
(2) **Baseline reproduction audit** (`docs/inventor-protocol.md` §8.1): instantiate
at the corpus's recorded points — `KN-LIT-742` (`n=3`, prime order, `Õ(q)`),
`KN-LIT-090`/`KN-LIT-449`/`KN-LIT-386` (GHS odd characteristic, weak-cover classes),
`KN-LIT-3197` (cover-and-decomposition) — and check each reported exponent is
recovered **symbolically**, not by curve-shape resemblance. (3) Enumerate every
degree of freedom that could break the identity: composite `n`, non-`(2,…,2)`
coverings, decomposition-with-cover hybrids, transfers into abelian varieties that
are not Jacobians, and transfers whose index calculus is not the `q^{2-2/g}` variety.
(4) For each, state whether it can produce `e < 1/2` at `n = 1` and why.
**Null object / control** — **Nearby-object control** (§8.4): apply the identity to
the *closest object where the hoped-for conclusion fails* — the `n = 3` prime-order
case, where the transfer genuinely wins. A method that cannot distinguish `n = 1`
from `n = 3` has not identified the load-bearing structure. The identity must
predict "win" at `n=3` and "loss" at `n=1` from the same formula, or it is a
tautology dressed as an audit.
**Falsifier (reachable)** — Any recorded cover/descent/decomposition result whose
published exponent the identity fails to reproduce (identity wrong), **or** any
construction achieving `e < 1/2` at `n = 1` (conclusion wrong). Both are
decision-relevant; the second would be a breakthrough.
**Cost** — impl **low** (a symbolic derivation and a table); compute **zero**.
**Ceiling** — A closure over the cover/descent family **for prime fields only**,
with forward guidance naming exactly what remains open (transfers into non-Jacobian
abelian varieties; index-calculus variants not of the `q^{2-2/g}` form; `n=1`
transfers whose target is not a curve at all). Affected vs safe: cover attacks
affect `F_{q^n}`, `n ≥ 3` curves and **no prime-field curve**; this is a
scope-clarification result, not an attack. It moves no exponent.
**Kills-it-early** — Step (2). If the identity does not reproduce `KN-LIT-742`'s
`Õ(q)` symbolically, stop: the model of the cover cost is wrong and the `n=1`
conclusion inherits that error.

---

### A4-5. Field-DLP-inclusive MOV/Frey-Rück cost oracle, frozen and calibrated against published DLP records
**Claim** — A hash-frozen cost function `C_MOV(p, N) = C_pairing(p,k) + C_fieldDLP(p^k)`,
with `k = ord_N(p)` computed **exactly** (not modelled) and `C_fieldDLP` an explicit
`L_{p^k}(1/3, c)` / FFS expression, (i) reproduces the published cost of at least
**three** recorded finite-field DLP computations to within a stated factor, and
(ii) returns, for random prime-order `E/F_p`, a value exceeding `0.886·sqrt(N)` by a
factor of at least `2^{40}` at 256-bit `p` — because for random `N`, `k = ord_N(p)`
is `Θ(N)` with overwhelming probability, so `F_{p^k}` is astronomically large.
This is the **named-defect repair**: `EV-IT-002` O-4 and `DEC-20260803-004` both
record that `C_special_MOV = ceil(k·log2 p)` charges only the Miller loop and omits
the dominant field DLP, and the same defect class (`RT-130-O4`) has now recurred
three times.
**Mechanism** — MOV/Frey-Rück maps `G` into `F_{p^k}^*`. The attack's cost is
pairing evaluation **plus** a DLP in `F_{p^k}^*`. `k = ord_N(p)` is a class
invariant (A4-1), so no isogeny and no base change reduces it: base-changing to
`F_{p^m}` divides `k` by `gcd(k,m)`, and at `m = k` gives embedding degree 1 — over
the *same* field `F_{p^k}`, at the *same* field-DLP cost. That is precisely why an
embedding-degree-1 endpoint is not a transfer demonstration, and the oracle makes
that non-negotiable by construction rather than by policy.
**Minimal discriminating test** — Sage-free: `ord_N(p)` by factoring `N−1` at toy
sizes / by exact order computation; the `L(1/3)` expression is arithmetic. (1) Freeze
the formula and its constants in a hashed spec **before** looking at any calibration
point. (2) Calibrate: predict the cost of three published field-DLP records
(transcribed into `KN-LIT` first — none is transcribed today) and report the ratio
predicted/actual. (3) Emit `C_MOV` for the `EXP-IT-001` toy parameter sets and for
P-256/secp256k1, alongside matched rho. (4) Re-score `EV-IT-002`'s planted control
under the frozen oracle and report the resulting `R_xfer` as a **superseding
recomputation**, never as an edit.
**Null object / control** — (a) **Pairing-friendly positive control**: a BN/BLS-shaped
toy curve with `k = 12`, where `C_MOV` must come out **below** matched rho — if the
oracle cannot see the real MOV win where one exists, it is void. (b) **Random-curve
null**: 100 random prime-order toy curves; `C_MOV/matched_rho` must exceed 1 on
100/100. (c) **Formula-substitution tripwire**: a unit test asserting that
`ceil(k·log2 p)` is *not* an admissible `C_special_MOV` value, so the exact
substitution that voided `EV-IT-002` cannot recur silently.
**Falsifier (reachable)** — Calibration ratio outside the stated band on any of the
three records (oracle wrong, decision-relevant); or control (a) failing (oracle
blind to a real win); or any random toy curve returning `C_MOV < matched_rho`
(either the oracle or `ord_N(p)` is wrong).
**Cost** — impl **low-medium**; compute **low** (< 1 CPU-hour). The real cost is the
literature transcription of three DLP records, which is owed regardless.
**Ceiling** — Infrastructure. **Moves no exponent and claims no mathematics.** Its
justification is that the same cost-model inversion has voided three batches, and a
frozen oracle with a measured calibration is the only thing that stops a fourth.
Affected vs safe: it *narrows* claimed impact — the MOV route affects only curves
with genuinely small `k` (pairing-friendly, by design), and no random prime-field
curve.
**Kills-it-early** — If no finite-field DLP record can be transcribed from primary
sources in this environment, the oracle is uncalibrated; ship it as
`uncalibrated`, forbid its use as a decision threshold, and say so — do **not**
calibrate against a remembered figure.

---

### A4-6. Isogeny-class batching: turning `L` targets on `L` distinct curves from `L·N^{1/2}` into `L·N^{1/4} + (L·N)^{1/2}`, with a mathematically guaranteed null
**Claim** — Let `E_1,…,E_L /F_p` be **distinct** curves with `#E_i(F_p) = h·N`, each
holding one ECDLP target. By TATE they are pairwise `F_p`-isogenous. Computing
`L−1` explicit isogenies to a hub curve at ISO-COST `Õ(p^{1/4})` each and evaluating
them on the targets converts `L` independent single-target problems into **one**
`L`-target problem in one group, solvable at MT-REC `~sqrt(L·N)`. Total
`≈ L·c₁·N^{1/4} + c₂·sqrt(L·N)` against a baseline of `L·0.886·sqrt(N)` (rho does
**not** amortize across distinct groups; MT-REC's `sqrt(L·N)` is **not** the baseline
here and must not be quoted as one). Amortized per-target cost at `L = N^{1/2}`:
`Θ(N^{1/4})` versus `Θ(N^{1/2})` — an **amortized-exponent move from 1/2 to 1/4** in
the multi-instance regime, conditional on ISO-COST.
**Mechanism** — The tracked object is O7, a *batch* carried across a symmetry orbit.
The isogeny class is the orbit of the class-group action; one expensive structure
(the path to the hub) is reused by every target that lands in the same orbit. This
is structurally the same amortization `KN-OPEN-026` identifies in the 2026 lattice
hybrid results — one expensive preprocessing shared across symmetry-derived
instances — and is the concrete place where `KN-OPEN-012`'s "does the program's
structure-exploitation experience transfer" question has a **prime-field ECDLP**
instance rather than an analogy. **It exploits the representation** (`j`-invariants,
Vélu), so the generic-group bound does not forbid it: merging `L` groups into one is
not a generic operation.
**Minimal discriminating test** — Sage-free. At `p ≈ 2^20…2^24`: (1) generate a
class with `≥ 64` members by walking `ℓ = 2,3` from a seed and recording `j`; (2) for
`L ∈ {2, 8, 32, 64}`, plant one target per curve; (3) find paths to a hub by
bidirectional MITM over the persisted edge ledger; (4) **evaluate** the composed
isogeny on each target (Vélu, degree-coprime to `N`), verify `[k]P_i = Q_i` on the
original `E_i` after solving in the hub; (5) charge every step in the shared
charged-unit ledger and plot total cost against `L·0.886·sqrt(N)` and against
`sqrt(L·N)`; (6) fit the isogeny-cost exponent across the three `p` sizes and
report it against the predicted `1/4` **with the fit's confidence interval, refusing
the fit if three points cannot support it** (they cannot — report as unfitted).
**Null object / control** — Three, and note that the first is *guaranteed correct by
theorem*, which is what makes this control cheap:
(a) **Non-isogenous null (guaranteed)**: pairs with different group orders. By TATE
no `F_p`-isogeny exists, so the path search **must** terminate in failure and must
report failure explicitly — not a censored `0`. Any "path" found is a harness bug.
(b) **Shuffled-edge null**: permuted edge ledger; path recovery must collapse.
(c) **Planted positive**: pairs constructed by a known `h`-hop walk; the search must
recover a path of length `≤ h` and the pullback certificate must verify.
**What a passing control would NOT establish** — Not the `N^{1/4}` scaling (three
toy sizes cannot fit an exponent, and the record must say `unfitted`); not that
deployments present `L` targets on `L` distinct isogenous curves (they generally do
not — this is a well-defined regime, not an observed one); not any single-target
improvement whatsoever.
**Falsifier (reachable)** — Measured total cost `≥ L·0.886·sqrt(N)` at every tested
`L` (the batching gains nothing in scope); or control (a) returning a path (harness
void); or the pullback certificate failing on planted pairs; or the endomorphism-ring
descent step (curves in one class with **different** `End`) dominating and pushing
per-target cost above `sqrt(N)` — a confounder that must be measured, not assumed
away.
**Cost** — impl **medium-high** (reuses A4-2's edge ledger and Vélu; adds MITM and
multi-target rho); compute **medium** (< 24 CPU-hours).
**Ceiling** — **Amortized multi-target only.** It moves an exponent `1/2 → 1/4` in
the per-target amortized cost for `L ≤ N^{1/2}` and moves **nothing** at `L = 1`.
Rests entirely on ISO-COST, which is `reported` in this corpus and untranscribed;
if the true ordinary-isogeny cost is `L_p(1/2)` rather than `p^{1/4}` for the
same-`End` case plus descent, the gain shrinks or vanishes. Affected vs safe: no
deployed single-target parameter set is affected.
**Kills-it-early** — Before any run: check whether the `L` curves in the sampled
class share an endomorphism ring. If they do not, the descent step is the real cost
and must be costed first; if descent is `L_p(1/2)` it may already exceed `sqrt(N)`
at toy sizes, which would kill the idea for **one line of arithmetic**.

---

### A4-7. The isogeny-class preprocessing table: an `(S,T)` frontier that the generic `S·T² = Ω(εN)` bound does not obviously govern
**Claim** — Preprocessing that is advice about the **isogeny graph** (a table of `S`
distinguished `j`-invariants with their paths to a hub) is not advice about the
**group**, so PP-REC's generic bound `S·T² = Ω(εN)` does not directly apply to it.
Concrete claim: an `S`-entry table reduces the online transfer time from
`Õ(p^{1/4})` to `Õ(p^{1/4}/S)` for `S ≤ p^{1/4}` (distinguished-point / kangaroo
accounting), while the **composed** attack — table plus online multi-target rho —
must still be scored against PP-REC for the full ECDLP-with-preprocessing task. The
discriminating question: does the composed `(S, T)` point land **below** `S·T² = εN`,
and if so is that (a) a real non-generic advantage from representation exploitation,
or (b) an accounting error, or (c) evidence that PP-REC as remembered is not the
statement that applies?
**Mechanism** — O8. The advice is about the class-group orbit structure, which is a
representation-level object invisible to a generic algorithm. This is the same
lever as A4-6 with time traded for space, and it is the natural place to test
whether the isogeny-class amortization is bounded by the group-theoretic frontier or
sits outside it. **Every one of the three outcomes above is informative**, which is
what makes this a discriminator rather than a fishing trip.
**Minimal discriminating test** — Sage-free, and it should **not** be attempted
before PP-REC is transcribed from the primary source: the whole test is a comparison
against a threshold this corpus does not currently hold. Then: at `p ≈ 2^20`, build
tables at `S ∈ {2^4, 2^6, 2^8, 2^10}` over the persisted edge ledger, measure online
transfer time `T_iso(S)`, compose with matched multi-target rho, and plot the
resulting `(S, T_total)` against the transcribed frontier. Report the exponent of
`T_iso(S)` in `S`.
**Null object / control** — (a) **Random-table null**: a table of `S` random `j`
values with fabricated paths; online time must **not** improve, and if it does the
improvement is packaging. (b) **Group-advice control**: an `S`-entry table of actual
discrete logs in the hub group — this **is** governed by PP-REC and must be measured
to sit on or above the frontier, calibrating the instrument against the bound it is
supposed to test. (c) **Table-size sweep as decay check**: `T_iso` must fall
monotonically with `S`; a flat curve is the artifact tell.
**Falsifier (reachable)** — Control (b) landing **below** the frontier (instrument
or transcription wrong, decision-relevant either way); or `T_iso(S)` flat in `S`
(table does nothing); or the composed point sitting above `L·sqrt(N)`, i.e. the
whole scheme is dominated by doing nothing.
**Cost** — impl **medium** (extends A4-6); compute **low-medium** (< 8 CPU-hours),
**plus** the blocking literature transcription of PP-REC.
**Ceiling** — Multi-target/preprocessing regime only; **no single-target exponent
move**. Best case it exhibits a concrete `(S,T)` point for a *composite* task that
the generic bound does not cover, which is a scope result about the bound, not an
attack on the ECDLP. Worst case it is dominated by A4-6's tableless version.
**Kills-it-early** — If PP-REC cannot be transcribed, this idea has no threshold and
should not run; downgrade it to "measure `T_iso(S)` and report", which is a
component of A4-6, not a separate result.

---

### A4-8. Multi-target MOV: one `F_{p^k}` precomputation amortized across `L` targets, and where that moves the affected/safe boundary for small-`k` curves
**Claim** — For curves with genuinely small embedding degree `k` (pairing-friendly
by construction: BN, BLS, MNT — **not** random prime-field curves, whose
`k = ord_N(p)` is `Θ(N)` by A4-1/A4-5), MOV maps `L` targets into **one** field
`F_{p^k}` whose index-calculus cost splits into a large one-off precomputation
(sieving + linear algebra) and a much cheaper per-target individual-log descent.
Claim: the measured break-even `L*` at which
`C_precomp(p^k) + L·C_indlog(p^k) < L·0.886·sqrt(N)` is **finite and small** (`L* ≤ 2^6`
at toy scale), so the multi-target regime shifts the affected/safe boundary for
small-`k` curves **without touching any random prime-field curve**. This is the
"precomputation vs individual-log separation" pattern `GOAL-ECTD-001`'s completion
criteria already name in the hidden-SNFS sense.
**Mechanism** — Amortization of the expensive half across derived instances, again
(the same shape as A4-6, A4-7, and `KN-OPEN-026`'s lattice mechanism). The tracked
object is the shared factor-base log table in `F_{p^k}^*`.
**Minimal discriminating test** — Sage-free and genuinely small: pick `p^k` with
`p ≈ 2^{10}`, `k ∈ {2,3,6}` so `p^k ≈ 2^{20…60}`; implement a plain index calculus
in `F_{p^k}^*` with a small factor base (pure Python), measure `C_precomp` and the
distribution of `C_indlog` over `L ∈ {1,4,16,64}` targets, and plot amortized
per-target cost against matched rho on the curve and against MT-REC `sqrt(L·N)`.
Charge everything in the shared charged-unit ledger, and report **both**
amortization conventions (once-charged and per-attempt), since the convention is
exactly what produced this campaign's 116.5x false signal.
**Null object / control** — (a) **Large-`k` null**: the identical pipeline on a
random prime-field curve where `k = ord_N(p)` is large — the pipeline must report
`C_MOV` as infeasible (via A4-5's oracle) and must **not** produce a number that
could be mistaken for a win. (b) **Precomputation-reuse tripwire**: run `L` targets
with the factor-base table deliberately rebuilt per target; the ledger must flag the
amortization mismatch. (c) **Certificate control**: every claimed log verified as
`[k]P = Q` on the curve, not in the field.
**What a passing control would NOT establish** — Nothing about random prime-field
curves; nothing about single-target cost; and nothing crypto-scale, since a
`2^{60}` field is not a `2^{3072}` field and NFS's asymptotics do not appear at toy
sizes — the toy measurement fits the *shape* of the split, not the exponent.
**Falsifier (reachable)** — Amortized per-target cost `≥ 0.886·sqrt(N)` at every
tested `L` (no multi-target MOV advantage in scope); or null (a) producing a
finite win (oracle or accounting broken); or the individual-log cost failing to
separate from the precomputation cost (no split, so nothing to amortize).
**Cost** — impl **medium** (small-field index calculus, ~600 lines); compute **low**
(< 4 CPU-hours).
**Ceiling** — **Special-curve result; does not generalize.** It moves the
per-target constant (and, at large `L`, the amortized exponent) for a family that is
already known to be pairing-friendly *by design*. Affected: BN/BLS/MNT-style curves
used in a batched setting. Safe: every random prime-field curve, every standard
NIST/SEC prime curve. It is included because the affected/safe boundary is the thing
this program must state correctly, and because it supplies a **real** transfer with
a **real** win for the harness of A4-2 to be validated against.
**Kills-it-early** — If `C_precomp` at the chosen toy `p^k` is not measurably larger
than `C_indlog` (small fields do not exhibit the split), the toy scale cannot show
the mechanism at all; report that and stop rather than reporting a ratio.

---

### A4-9. Scoped closure attempt for lattice bridges to the plain ECDLP: the GGM bound is information-theoretic in the query count, so any bridge must exploit the representation — plus the enumeration of which representation channels exist
**Claim** — Two parts. (i) **Closure attempt**: any ECDLP algorithm whose access to
the group is `q` group-operation/equality queries followed by *arbitrary unbounded
computation on the transcript* succeeds with probability `O(q²/N)`. Lattice
reduction is arbitrary computation on the transcript. Therefore **no lattice bridge
that is group-respecting can beat `sqrt(N)`**, regardless of how clever the basis
is, and the failure is not about BKZ's quality — it is that the transcript contains
no more information. (ii) **Forward guidance**: any live bridge must therefore use
the **representation**, and this idea enumerates the channels — (C1) integer lifts
of `x`-coordinates; (C2) coefficients of division polynomials; (C3) Weierstrass
coefficients and the `j`-invariant; (C4) archimedean/`p`-adic lifts and canonical
heights; (C5) the `(p, N)` class label; (C6) the modular-polynomial/isogeny
structure — with a verdict per channel from the **lossy-projection test**, which
costs no compute.
**Mechanism** — `KN-OPEN-018` names exactly this as the cheaper of the two closing
moves ("simulable in the generic group model … in the style of the program's
existing GGM-simulability screens"). It has never been attempted here. The content
is not the bound (which is classical) but the **precise statement of what it does
and does not forbid**: it forbids group-respecting bridges outright, and it forbids
nothing about representation-exploiting ones — which is why the enumeration is the
deliverable, not the theorem.
**Minimal discriminating test** — Zero compute. Write the reduction: an adversary
`A` that builds a lattice from `q` queries and runs BKZ ⟹ a generic adversary `A'`
making `q` queries with the same success probability. State the **quantifier order**
explicitly (`∀ N ∀ A ∃ simulator` versus `∃ simulator ∀ A`) and check that the
simulator is not permitted to depend on the instance in a way the uniform conclusion
forbids. Then, for each of C1–C6, state (a) what the projection discards, (b) whether
the discarded part is discarded *compatibly with the group law*, and (c) the
resulting verdict `not-a-projection / lossy-but-non-propagating / lossy-and-propagating`.
**Null object / control** — **Nearby-object control** (§8.4): apply the same argument
to the HNP-with-leakage setting, where lattices demonstrably *do* win. The argument
must **fail there** — and the reason it fails must be exhibited (leakage supplies
information outside the group-query transcript). An argument that also "proves" HNP
impossible has not identified the load-bearing structure and is void.
**Falsifier (reachable)** — The nearby-object control failing (argument proves too
much); or the quantifier-order check revealing the simulator must depend on the
instance; or any enumerated channel receiving verdict `lossy-and-propagating`,
which would identify a live bridge candidate rather than closing the lane.
**Cost** — impl **low** (a written argument and a six-row table); compute **zero**.
**Ceiling** — A **scoped** closure of the group-respecting half of `KN-OPEN-018`,
with the representation-exploiting half explicitly left open and enumerated. It is
not an impossibility theorem for lattice/ECDLP bridges and must never be recorded as
one. It moves no exponent. **It must state, in its own text, that nonce-leakage
results do not transfer to the plain problem** — `KN-OPEN-011`'s boundary — and that
the asymmetry `KN-OPEN-018` flags (lattices attack *implementations* superbly and the
*mathematical problem* not at all) is preserved, not weakened, by this result.
**Kills-it-early** — The nearby-object control. Run it first; it is one paragraph.

---

### A4-10. Representation-lattice null screen: do `x`-coordinate and division-polynomial lattices carry any `k`-correlated short vector, measured against a random-relabelling null?
**Claim** — The concrete measurement backing A4-9(ii), and its predicted answer.
Build, for a target `(P, Q)` with `Q = [k]P`, lattices from (L1) the integer lifts
`x(P), x(2P), …, x(mP)` in `[0,p)`, (L2) the same for `Q + iP`, and (L3) coefficients
of division polynomials `ψ_i(P)`. Claim: the shortest vector's correlation with `k`
— measured as recovery rate of any of the top/bottom `log2(N)/4` bits of `k` — is
**statistically indistinguishable from a random-relabelling null**, at all tested
`m ≤ 64` and both toy sizes. Predicted mechanism of failure, stated **before** the
run: channel C1's projection (integer size of `x`) is genuinely lossy, but what it
discards is **not discarded compatibly with the group law** — the addition formulae
are rational maps whose effect on integer size is pseudorandom — so the retained
part does **not** propagate deterministically, and the lossy-projection test rejects
the object *a priori*.
**Mechanism** — O9. This idea exists to make that `a priori` verdict *falsifiable*
rather than asserted, which is the difference between a controlled null and an
opinion. Both outcomes are recorded: a null is `KN-OPEN-018` evidence at the
"one concrete family screened with a control" tier; a signal is a live bridge.
**Minimal discriminating test** — Sage-free: pure-Python LLL (Nguyen–Stehlé style
integer LLL, ~200 lines, adequate at dimension `≤ 64`). `p ≈ 2^20` and `2^24`,
200 instances each, `m ∈ {8,16,32,64}`, three lattice families, report bit-recovery
rate with exact binomial intervals.
**Null object / control** — (a) **Random-relabelling null**: replace the curve group
by `Z/N` with a random bijective relabelling into `[0,p)`, build the identical
lattices from the labels; this is the null object of the same shape and its recovery
rate is the floor. (b) **Planted-positive control**: an HNP instance with 8 leaked
nonce bits, where LLL **must** recover `k` — if it does not, the LLL implementation
is broken and every null is uninterpretable. **This control is in the leakage model
and is used only to certify the solver; its success establishes nothing whatever
about the plain problem** (`KN-OPEN-011`). (c) **Dimension sweep as decay check**:
any apparent signal must vary with `m`; a signal flat in `m` is an artifact.
**Falsifier (reachable)** — Recovery rate exceeding null (a) by `> 3σ` at any
`(m, family)`, replicated at both `p` and surviving (c) — that is a
representation channel on the plain ECDLP. Conversely control (b) failing kills the
run outright as an infrastructure failure, never as mathematical evidence
(`AGENTS.md` rule 5).
**Cost** — impl **medium** (integer LLL is the bulk); compute **low** (< 3 CPU-hours).
**Ceiling** — Negative outcome moves nothing and claims nothing beyond "three
concrete lattice families screened with a null at toy scale" — deliberately narrow,
and it must **not** be written up as "lattices do not bear on the ECDLP." Positive
outcome, even at a few bits, is a constant-factor reduction (`sqrt(N/2^b)`), **not**
an exponent move, unless `b` grows with `log N` — which the sweep would show.
**Kills-it-early** — Control (b). If planted HNP with 8 leaked bits does not solve,
stop and fix LLL. Also: the lossy-projection verdict is written **before** the run
and pre-registered; if it says `not-a-projection` for a family (i.e. the lattice is
invertibly recoverable from `(P,Q)`), that family is a change of coordinates and is
dropped without measurement.

---

### A4-11. Trapdoor endpoint public-detectability partition: which weakness predicates can be hidden at all, and the `L_p(1/2)` barrier against hiding one in the endomorphism ring
**Claim** — Partition every candidate trapdoor weakness predicate `W(E)` by what it
factors through, and each cell carries a different and *checkable* detection cost:
- **Cell A — `W` factors through `(p, N)`** (anomalous, embedding degree,
  supersingularity, smooth order). Detection is `O(poly log p)` from the **public**
  curve. **No trapdoor is possible**: the weakness is a public label. This is A4-1
  restated as a design statement and it removes four families from
  `GOAL-ECTD-001`'s space *by argument*, upgrading them from "deprioritized" to
  "publicly detectable."
- **Cell B — `W` factors through `End(E)`** (conductor size, discriminant
  smoothness; the `IDEA-20260731-017` vertical-conductor lane). Detection costs
  ENDO-COST `L_p(1/2)` under GRH+heuristics. Since `L_p(1/2) = o(p^{1/2})`,
  **public detection is asymptotically cheaper than matched rho** — which
  **violates `GOAL-ECTD-001`'s own requirement** that public detection remain at
  least rho-hard. Claim: Cell B is a **barrier**, not a lane, unless the detector's
  concrete crossover is above the target parameter size.
- **Cell C — `W` factors through `j` and nothing coarser.** Detection requires
  search; this is the only cell where a Teske-style trapdoor can survive, and it is
  the cell A4-2's synthetic marked set models.
**Mechanism** — O10. The tracked object is the predicate's factorization, and the
propagation rule is: coarser factorization ⟹ cheaper public detection ⟹ weaker
trapdoor. This is the cheapest possible triage of an entire campaign's endpoint
space and it costs no compute.
**Minimal discriminating test** — (1) Enumerate every endpoint family named in
`GOAL-ECTD-001` and `IDEA-20260731-016/017/018` and assign each to A, B or C with the
factorization written out. (2) For Cell B, **transcribe** ENDO-COST from
`KN-LIT-309` / `KN-LIT-3063` primary sources — this is blocking and is not done
today — and compute the concrete crossover `p*` where `L_p(1/2)` overtakes
`0.886·sqrt(p)`. (3) Sage-free toy check of Cell A: for 200 random toy curves,
confirm that every Cell-A predicate is computable from `(p, N)` in `< 10^4` charged
units, i.e. that a public detector really is cheap.
**Null object / control** — (a) **Cell-C control**: a synthetic `j`-marked predicate
(A4-2's) must land in Cell C, and the partition must **not** be able to detect it
from `(p,N)` or `End(E)` — if the partition assigns everything to Cell A, it has no
resolving power. (b) **Detector-cost control**: run the Cell-A detector on curves
where the predicate is *false* and confirm it returns false at the same cost (no
asymmetric early exit masquerading as detection).
**Falsifier (reachable)** — A predicate exhibited that is **not** a function of
`(p,N)` yet is checkable in `poly(log p)` from the public curve — that collapses
Cell C into Cell A and closes the trapdoor lane far harder than this partition does.
Or: a Cell-B predicate with a genuine ECDLP advantage **and** a concrete crossover
`p*` above 256 bits — that would make Cell B a live lane again at deployed sizes,
which is the outcome that would *rescue* `IDEA-20260731-017`.
**Cost** — impl **low** (a written partition plus a 200-curve check); compute
**zero to low**. Blocking dependency: the ENDO-COST transcription.
**Ceiling** — A **barrier/triage result** for `GOAL-ECTD-001`, not an ECDLP result.
It moves no exponent. Affected vs safe: it constrains what a *designer* can hide; it
says nothing about the hardness of any deployed curve, and a curve is not made weak
by being in Cell A — Cell A curves are simply *visibly* weak or visibly not.
**Kills-it-early** — Step (2). If ENDO-COST cannot be transcribed, Cell B's barrier
is unquantified and must be recorded as **conjectural**, not as a barrier; the
partition still stands for Cells A and C.

---

## 3. Honest accounting (`docs/inventor-protocol.md` §5)

**Objects considered.** O1–O10 above, of which O1/O4 (the class label) is the one
whose examination produced the catalogue's load-bearing observation; O5 (`p`-adic
truncated logarithm) and O7 (batch across a symmetry orbit) are the two with a
reachable positive; O9 (integer size of a coordinate) is expected to fail the
lossy-projection test and is proposed for measurement anyway, with the failure
pre-registered.

**Depth of verified structure.** Zero. **No experiment in this catalogue has been
run.** Nothing here is verified at any tier. The class-invariance observation
(§1) is an application of a textbook theorem that **this corpus has not
transcribed**; it is `unverified` until TATE is transcribed and A4-1's audit runs.

**`dominated_by`.** Checked against every frontier row this corpus holds, per idea:
- A4-1, A4-4, A4-9, A4-11: `n/a (no algorithmic result claimed)` — closure/triage
  arguments occupying no point on any cost frontier.
- A4-2, A4-5, A4-7(degraded), A4-10: `n/a (no result claimed)` — instrument and
  measurement work.
- A4-3: **dominated by Pollard rho at `0.886·sqrt(N)`** on the expected (null)
  outcome; on a positive outcome with `I` bits it would sit at `0.886·sqrt(N/2^I)`,
  still dominated for any constant `I`.
- A4-6: **not dominated a priori in the `L`-target, `L`-distinct-curve regime** —
  the relevant frontier rows are `L·0.886·sqrt(N)` (independent rho, the correct
  baseline) and MT-REC `sqrt(L·N)` (which applies to one group and is **not** the
  baseline here). It **is** dominated at `L = 1` by rho. Conditional on ISO-COST,
  which is untranscribed.
- A4-7: dominated by A4-6's tableless version unless `T_iso(S)` falls with `S`;
  additionally must be scored against PP-REC, untranscribed.
- A4-8: dominated by rho at `L = 1`; not dominated a priori for large `L` **on
  small-`k` curves only**; dominated by rho on every random prime-field curve.
No row was left as an unchecked `null`.

**`sota_delta`, quantitative.**
- Single-target prime-field ECDLP: **zero on every axis.** No idea in this
  catalogue claims a single-target improvement over `0.886·sqrt(N)`.
- Multi-target (A4-6): claimed amortized per-target `Θ(N^{1/4})` versus
  `Θ(N^{1/2})` for `L ≤ N^{1/2}`, i.e. an amortized-exponent delta of `−1/4`,
  **conditional on ISO-COST and unmeasured**. Memory: `Õ(1)` for the low-storage
  isogeny walk plus MT-REC's rho memory; data/queries: `L` targets.
- Instrument delta (A4-2 + A4-5): from a transfer lane with **zero** valid positive
  controls across three batches and a cost model that inverted three times, to a
  harness with a density-swept decay prediction, a live null gate, a persisted edge
  ledger, and a frozen field-DLP-inclusive cost oracle with a measured calibration.

**Enumerated closures, with mechanisms (each at the §4 standard, each *proposed*
and none yet established).**
1. **Prime-field weak-endpoint transfer.** Obstruction: TATE ⟹ `(p,N)` is an
   `F_p`-isogeny-class invariant ⟹ the anomalous, embedding-degree and
   supersingular predicates are constant on the class ⟹ the search evaluates a
   constant. Forward guidance: non-`F_p`-rational isogenies; predicates in Cell C of
   A4-11; base-change constructions (which A4-5 shows do not reduce the MOV field).
2. **Cover/Weil-descent transfer at `n = 1`.** Obstruction: the win is
   `e(n,g) = (2−2/g)/n`, a function of base-field shrinkage; `n = 1` forces
   `e ≥ 1 > 1/2`. Forward guidance: non-Jacobian targets; index calculus outside the
   `q^{2−2/g}` form; transfers whose target is not a curve.
3. **Group-respecting lattice bridges.** Obstruction: the GGM bound is
   information-theoretic in the query count; unbounded offline computation on the
   transcript, lattice reduction included, adds nothing. Forward guidance: channels
   C1–C6, of which C1/C2 are screened by A4-10 and C4/C6 are untouched.
4. **Trapdoors with a Cell-A weakness.** Obstruction: the predicate is a public
   function of `(p,N)`. Forward guidance: Cell C only; Cell B pending the ENDO-COST
   transcription.
**None of these is a claim that a direction is impossible.** Each is scoped, each
names what remains open, and each has a reachable falsifier above.

**Premature-closure check.** This session declined to generate nothing. Four of the
eleven ideas are closure arguments; the other seven are constructive, and two
(A4-3, A4-6) have positive outcomes that would be substantial. The catalogue's
saturation posture is `unverified`, per `KN-OPEN-019`: this program still has no
written object enumeration for the ECDLP, so §1's table is a **sketch, not a
taxonomy**, and no closure here rests on it being complete.

**Open directions for the next session.** (i) Non-`F_p`-rational isogeny transfers —
untouched by A4-1 and by this catalogue entirely. (ii) `KN-OPEN-012`'s reverse
direction: whether A4-6/A4-7's orbit-amortization has a lattice counterpart, which
`KN-OPEN-026` frames and nobody here has attempted. (iii) Representation channels
C4 (archimedean/`p`-adic lifts, canonical heights) and C6 (modular-polynomial
structure), enumerated in A4-9 and screened by nothing. (iv) The four literature
transcriptions this catalogue is blocked on: TATE, MT-REC, PP-REC, ENDO-COST.

---

## 4. Batches

Three bounded batches. At most **3 concurrent non-archive tasks** per batch;
write scopes are disjoint at the task-directory level, and no task writes to
`ledger/`, `experiments/EXP-IT-001/`, or any existing knowledge entry.

### Batch A4-B1 — "Does the transfer premise survive?" (zero-compute algebraic audits)
**Ideas**: A4-1, A4-4, A4-11.
**Objective**: Determine, before any further compute is spent on the `H-IT-001`
lane, whether the prime-field weak-endpoint transfer premise, the cover-descent
premise, and the trapdoor-endpoint premise are structurally live or structurally
constant.
**Grouping rationale**: All three are symbolic factorization arguments over the same
object (a weakness predicate and what it factors through); all three are zero- to
low-compute; all three are prerequisites for spending anything on B2 or B3; none
shares code with the others, so their write scopes are trivially disjoint.
**Budget**: 3 concurrent tasks, ~2 CPU-hours total, no runs beyond A4-1's 200-curve
bucketing check. Blocking literature transcriptions: TATE (A4-1), ENDO-COST (A4-11).
**Decides**: whether `EXP-IT-001`'s weak-endpoint search can return a positive over
`F_p` at all (A4-1); whether any cover transfer can reach `e < 1/2` at `n=1`
(A4-4); which cells of the trapdoor space remain (A4-11). A **negative** batch here
is the expected and useful outcome and would redirect, not close, `GOAL-ECTD-001`
and `H-IT-001`.

### Batch A4-B2 — "A transfer harness with a reachable negative" (instrument repair)
**Ideas**: A4-2, A4-3, A4-5.
**Objective**: Produce, for the first time in this lane, a positive control that can
honestly pass, a null gate that actually runs, a persisted raw edge ledger, and a
frozen field-DLP-inclusive special-solver cost — plus one measurement (A4-3) whose
positive outcome would be independently valuable.
**Grouping rationale**: A4-2 and A4-5 are the two named-defect repairs from
`EV-IT-002`/`DEC-20260803-004` and must be frozen together (the harness and its cost
oracle); A4-3 is independent code but shares the same toy-`F_p` arithmetic layer and
is the batch's one shot at a reachable positive. Disjoint write scopes: harness,
oracle, `p`-adic meter.
**Budget**: 3 concurrent tasks, ~8 CPU-hours, `p ≤ 2^24`, toy claim ceiling
throughout. Depends on A4-B1 (A4-1's verdict determines whether A4-2's *synthetic*
marking is the only honest option, which is the assumption A4-2 is built on).
**Decides**: whether a transfer instrument in this program can be certified at all,
and whether the `p`-adic channel is exactly closed for `N ≠ p`. Explicitly does
**not** decide anything about `H-IT-001`'s mathematical claim.

### Batch A4-B3 — "The only exponent-moving lane here, and the lattice bridge screen"
**Ideas**: A4-6 + A4-7 (one task, shared code), A4-8 (one task), A4-9 + A4-10 (one
task).
**Objective**: Measure the isogeny-class batching gain against the correct
multi-target baselines; measure the multi-target MOV split on small-`k` curves and
state the affected/safe boundary; and attempt the `KN-OPEN-018` scoped closure with
its concrete null screen.
**Grouping rationale**: A4-6/A4-7 are the same instrument at two points on a
time–memory tradeoff and must share an edge ledger. A4-8 is a disjoint codebase
(small-field index calculus) and disjoint scope (special curves only). A4-9/A4-10 are
argument-plus-measurement on the same object and share the LLL implementation.
**Budget**: 3 concurrent tasks, ~35 CPU-hours, `p ≤ 2^24` / `p^k ≤ 2^60`. Blocking
literature transcriptions: MT-REC and PP-REC (A4-6/A4-7 cannot be scored without
them), ISO-COST (A4-6's whole exponent claim is conditional on it).
**Decides**: whether the amortized `1/2 → 1/4` multi-target claim survives its first
measurement and its guaranteed-negative null; whether multi-target MOV shifts the
affected/safe boundary for pairing-friendly curves; and whether the
group-respecting half of `KN-OPEN-018` closes with the leakage-model asymmetry
intact.

---

## 5. What this document is not

It mints no identifier, writes no `IDEA-*.yaml`, creates no hypothesis, approves no
experiment, and changes no status. It asserts no experimental outcome — **no idea
below has been run** — and it cites no source it has not read in this repository.
Four external facts it leans on (TATE, MT-REC, PP-REC, ENDO-COST, ISO-COST,
COVER-COST) are labelled with their verification status at §0 and are blocking
dependencies wherever they carry a threshold.
