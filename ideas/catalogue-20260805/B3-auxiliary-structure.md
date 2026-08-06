# B3 — Auxiliary structure: what disclosure costs an isogeny/DL assumption

Catalogue slice B3, 2026-08-05. Idea Generator session. **This file is a
catalogue of research ideas only.** No ledger record, no `IDEA-*.yaml`, no ID
was minted. Nothing here is an approved experiment, and nothing here changes a
hypothesis status.

Anchors: `KN-OPEN-015` (which auxiliary data is fatal?), `KN-OPEN-024` (rank-1
quaternion PIP), `KN-OPEN-013` (endomorphism-ring hardness), `KN-TECH-026`
(Kani embeddings), `KN-TECH-027` (CSIDH), `KN-TECH-028` (Deuring/SQIsign),
`KN-TECH-050` / `KN-TECH-057` / `KN-TECH-058` (matched baselines),
`EV-SSI-004`, `EV-SSI-006`, `GOAL-SSI-001`, `GOAL-SQISIGN-001`,
`GOAL-SQISIGN-002`, `docs/inventor-protocol.md` §§1–5, §8.

---

## 0. Session frame (inventor-protocol §1: object-first, families off-limits)

### Established families in this slice — declared OFF-LIMITS as the primary lens

| Family | Tracked object | Status in corpus |
|---|---|---|
| **F1** SIDH break | images of a *known basis* of `E_0[N]` under secret `φ` of *known* degree `d`, `N > d` | CLOSED case study. Provable poly-time (`KN-TECH-026`, `KN-LIT-065/067`). Not a target. |
| **F2** GPST adaptive | oracle responses to malformed torsion inputs | Closed; needs an interactive static-key oracle (`KN-LIT-076`). |
| **F3** Petit unbalanced | same object as F1 in overstretched degree regimes | Closed precursor (`KN-LIT-077`). |
| **F4** oriented/CM weakness | an explicit endomorphism generating an orientation | Scoped-closed on this program's own attempt (`IDEA-20260725-002` / `EV-SSI-004`): material only with *independently published* poly-bounded `α` **and** certified orbit membership. |
| **F5** SQIsign transcript | Fiat–Shamir transcript `SQI-FS-T0` | CLOSED negative (`IDEA-20260725-003` / `EV-SSI-006`). Any transcript idea below must say how it differs, or it duplicates a closed record. |

**No idea in this catalogue proposes a torsion-image attack on CGL, CSIDH, or
SQIsign.** Those schemes publish no torsion images, F1's necessary conditions
fail on them (`EV-SSI-006`), and re-running that check is the fatigue report
`docs/inventor-protocol.md` §4 forbids.

### What is actually open, and what this slice generates against

`KN-OPEN-015` is explicit: *"the dividing line is now understood for the
specific attack, but a general characterization of which auxiliary data is
fatal is not settled."* The generative target is therefore **not** another
attack. It is a **decidable screen**: an object you can run against a scheme's
published interface and obtain `SAFE` / `UNDECIDED (here is exactly why)` /
`FATAL (here is the named reduction target)`.

### Candidate tracked objects, scored (§1 three axes)

Objects, not ideas. Each is a candidate for *the thing the screen follows*.

| # | Candidate tracked object | New or repackaging | One-step propagation definable/measurable? | Survives until |
|---|---|---|---|---|
| O1 | the secret isogeny `φ` itself | repackaging of F1 | yes | dissolves immediately without images — this is F1 |
| O2 | **residual set `S(Σ)`** = secrets consistent with published surface `Σ` | information-theoretic reframing; unverified whether written down for isogenies | yes: `S(Σ∘Σ')` from `S(Σ)`, `S(Σ')` | survives all schemes; **collapses to size 1 on CSIDH too**, so alone it false-alarms |
| O3 | **the constraint rank on the degree matrix** the disclosure imposes, modulo the masking group | plausibly new as a *screen scalar*; unverified | yes: ranks add under composition, mask dims add | survives the whole disclosure lattice; dissolves when the mask is instance-dependent |
| O4 | **specifiability of a Kani kernel** (the graph `{(P, φP)}`) | reframes `KN-TECH-026`'s applicability limit as an object | yes: kernel generators compose | survives raising embedding dimension `g` — which is exactly the claim |
| O5 | **orientation fragment** (what part of `End` is pinned: discriminant / char-poly / explicit map) | adjacent to F4 but F4 tracks the *explicit map*; the fragment lattice is the new part | yes | dissolves at the certified-orbit-membership gate `EV-SSI-004` flagged |
| O6 | **charged provenance of every "given"** in a reduction (computable / hypothesised / oracle-supplied) | methodological; the failure mode is already named `REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END` | yes | survives arbitrarily; it is an audit, not a mathematical object |
| O7 | revealed degree alone, no points | known channel (fixed-degree search, `KN-LIT-132`) but its *exponent as a screen threshold* is not stated in this corpus | yes (degrees multiply) | survives everywhere; the question is whether it moves an exponent |

O2–O7 are the objects the eight ideas below are built on. O1 is off-limits.

### Lossy-projection test (§2), applied once, up front

`Σ ↦ S(Σ)` **is** lossy: it forgets which curve, which basis, which encoding,
and retains only the fibre. It propagates: composing disclosures intersects
residual sets. It is therefore admissible as a tracked object — *and* it is not
sufficient, because `|S| = 1` for CSIDH (the class-group action is free, so
`[a]E_0` determines `a`) and CSIDH is not broken. **That failure is the
substance of this slice, not a defect in it:** it proves that *pinning the
secret* and *handing over the secret* are different, and the screen must be
two-stage. Stage A is entropy; Stage B is whether the disclosure supplies a
system that some *named, published* poly-time procedure solves.

A projection that loses nothing is a change of coordinates. Checked per-idea
below where a new object is introduced.

### Hard environment constraints (bind every idea)

- **Primary sources (eprint/arxiv) are unreachable.** `downloads/` does not
  exist in this worktree, so the local PDFs cited by `KN-LIT-2182`
  (Castryck, *A polynomial time attack on instances of M-SIDH and FESTA*),
  `KN-LIT-4829` (M-SIDH/MD-SIDH) and `KN-LIT-3867` (FESTA) are **not
  available**; those three entries are title-level only, with no extracted
  abstract. Every use of them below is flagged and given a fallback.
- **SageMath is unavailable and uninstallable.** Python 3 + `sympy` is the
  compute surface (`requirements-agent.txt`). Toy supersingular arithmetic
  over `F_{p^2}` via the modular polynomial `Φ_2` and hand-rolled field
  arithmetic is feasible at `p ≈ 2^12–2^20` (≈ `p/12` vertices). **Genus-2 /
  Richelot arithmetic is NOT assumed available**; every idea below that would
  otherwise need it is reformulated to test an *existence predicate* or a
  *brute-force ground truth*, never to execute a higher-dimensional isogeny.
- Consequence: no idea here is crypto-tier. Ceilings are `toy`, `control`, or
  `derivation`. Stated per idea.

### Scope statement binding all eight ideas

**No deployed or candidate scheme is claimed broken or weakened by anything in
this file.** CGL, CSIDH, SQIsign (all versions), M-SIDH, MD-SIDH and FESTA are
treated as *calibration targets for an instrument*, not as attack targets.
Where a threshold is derived (B3-7), it is stated as a function of parameters
and explicitly not evaluated at any real parameter set. SIDH/SIKE appear only
as a known-positive control.

---

## 1. The ideas

### B3-1. Two-stage disclosure screen: residual entropy × named-constructor, with an explicit UNDECIDED verdict

**Claim.** A scheme's published interface can be classified by a two-stage
decision procedure that (A) measures the residual set `S(Σ)` of secrets
consistent with the published surface `Σ`, and (B) asks whether `Σ` determines
an instance of a problem this corpus records as poly-time or subexponentially
solvable *by a named, cited procedure*. Verdict = `SAFE` if Stage A leaves
superpolynomial residual entropy; `FATAL` only if Stage A collapses **and**
Stage B names a constructor; `UNDECIDED` otherwise. The screen reproduces
`FATAL` for SIDH, `SAFE` for CGL, and — crucially — `UNDECIDED`, not `FATAL`,
for CSIDH, whose secret is information-theoretically pinned by `[a]E_0`.
Falsifiable version: **no single-stage screen can separate SIDH from CSIDH.**

**Mechanism.** Stage A is the residual-set object O2. Stage B is a lookup
against a *frozen, cited* table of solvable-problem shapes: (i) "find an
isogeny with known degree matrix between known abelian varieties given a
specifiable kernel" (`KN-TECH-026`, `KN-LIT-065/067`); (ii) "find a smooth-norm
ideal in a known maximal order" (KLPT, `KN-TECH-028`); (iii) "abelian hidden
shift" (`KN-TECH-027`, Kuperberg); (iv) "PIP in `M_g(O)`, `g ≥ 2`"
(`KN-LIT-7641`, `KN-OPEN-024`). Stage B fires only when a *named row* matches;
"looks structured" is not a match. The dividing line `KN-OPEN-015` says is
unsettled is exactly the Stage-A→Stage-B implication, and this idea's content
is that the implication is false in general, with CSIDH as the witness.
*Lossy-projection check:* Stage A's projection `Σ ↦ S(Σ)` forgets the encoding
and retains the fibre, and fibres intersect under composed disclosure —
admissible. Stage B is not a projection but a table lookup, and is deliberately
not claimed to be an object.

**Minimal discriminating test.** Toy scale, pure Python. Build a supersingular
2-isogeny graph over `F_{p^2}`, `p ∈ {2^11, 2^13, 2^15}` (`Φ_2` roots; no Sage).
For each of five miniature schemes (CGL walk; CSIDH-like free action on an
`F_p`-rational orbit; SQIsign-like public-degree response; SIDH-like with
published basis images; SIDH-like with images *withheld*), enumerate the full
secret space by brute force, compute `|S(Σ)|` exactly, and record which Stage-B
rows match. Two outcomes discriminate: (a) `|S|` separates CGL from SIDH but
*not* CSIDH from SIDH ⇒ the two-stage structure is necessary, as claimed;
(b) `|S|` separates all three ⇒ a one-stage entropy screen suffices and the
claim is false.

**Null object / control.** Same measurement with `Σ` replaced by a *random*
surface of identical shape: point images sampled uniformly from `E_1[N]`
without any generating isogeny, degrees sampled independently of the walk. The
residual set must be **empty or maximal**, never intermediate. An intermediate
value on the null means `|S|` is measuring the toy graph's size, not the
disclosure.

**Falsifier (reachable).** (i) `|S(Σ)| = 1` for the CGL rung at all three `p`
⇒ Stage A is a scale artifact and has no content at toy scale — the screen
loses Stage A entirely. (ii) The CSIDH rung yields `|S| > 1` ⇒ the claimed
false-alarm witness is wrong and the motivating asymmetry evaporates.
(iii) Stage B matches a named row on the CGL rung ⇒ the table is over-broad and
the screen is over-sensitive.

**Cost.** Implementation medium (graph builder + five scheme mock-ups +
brute-force fibre enumeration; ~600–900 lines, no external deps beyond `sympy`).
Compute low (`≤ 1` CPU-hour at `p ≤ 2^15`; `|V| ≈ p/12 ≈ 2730`).

**Ceiling.** `toy` for every measured number; `derivation` for the two-stage
claim itself. The strongest thing this can certify is: *at the tested toy
parameters, entropy alone does not separate a broken scheme from an unbroken
one.* It certifies nothing about crypto-scale entropy and asserts no attack.

**Kills-it-early.** Before writing the graph builder: check by hand whether the
CSIDH class-group action on the toy `F_p`-rational orbit is actually free at
the chosen `p`. If the toy orbit has a nontrivial stabiliser, `|S| > 1` for
trivial reasons and the whole calibration is confounded — pick `p` first.

---

### B3-2. The disclosure-projection lattice: which lossy views of the torsion channel still propagate, and the rank-minus-mask accounting

**Claim.** The torsion-image channel admits a linearly ordered family of lossy
projections — `C0` nothing ⊂ `C1` degree only ⊂ `C2` Weil-pairing values only ⊂
`C3` `x`-coordinates only ⊂ `C4` images up to one *common* scalar ⊂ `C5` images
up to *independent* scalars ⊂ `C6` images up to a secret `2×2` matrix ⊂ `C7`
full images. Claim: **every one of `C1`–`C7` is composition-compatible**, so
compositionality is *not* the safety criterion; safety is governed instead by
the scalar `r(C) − m(C)` = (number of independent constraints the channel
imposes on the degree matrix) − (dimension of the masking group). Predicted
direction: residual-orbit size at toy scale is monotone decreasing in
`r(C) − m(C)`, with a sharp change of regime where it crosses zero.

**Mechanism.** Object O3. `C1`: degrees multiply under composition. `C2`:
`e(φP, φQ) = e(P,Q)^{deg φ}` so the pairing channel is exactly `deg φ mod N` —
one constraint, and it composes multiplicatively. `C3`: `x`-only forgets the
sign, and `[-1]` is central, so `±` is discarded *compatibly* with composition
— a genuine lossy projection that still propagates deterministically. `C4`/`C5`:
scalars compose multiplicatively. `C6`: matrices compose. So each rung passes
the §2 lossy-projection test and none is a mere change of coordinates. The
content is that passing the test does **not** imply attackability: the mask
group eats constraints, and `r − m` is the bookkeeping.
*Lossy-projection check:* explicitly performed per rung above; `C7 → C7` is the
identity and is recorded as the degenerate (non-)projection.

**Minimal discriminating test.** Toy scale, no genus-2 arithmetic. For a fixed
toy `(E_0, E_1, N, d)` with a known secret `φ`, enumerate *all* degree-`d`
isogenies `E_0 → E_1` by brute force in the toy graph. For each channel `C0`–`C7`,
compute the size of the subset consistent with the published view. Compare the
measured `log |orbit|` against the predicted `r(C) − m(C)` ordering. **Two
outcomes:** monotone agreement ⇒ the lattice is a genuine safety ordering and
`r − m` is a usable screen scalar; a non-monotonicity (some coarser channel
leaves a *smaller* orbit than a finer one) ⇒ the accounting is wrong and the
lattice is not linearly ordered, which is itself a publishable characterisation
correction.

**Null object / control.** Replace `φ` by a random isomorphism `E_0[N] → E_1[N]`
not induced by any isogeny of degree `d`. Every channel must then give orbit
size 0 (inconsistent) — if a channel gives a nonzero orbit on the null, that
channel's consistency predicate is vacuous and it must be removed from the
lattice before any conclusion is drawn.

**Falsifier (reachable).** Measured orbit sizes fail the predicted monotone
ordering at two or more of three toy parameter sets ⇒ `r − m` rejected as the
screen scalar. Also reachable: `C2` (pairing-only) leaves an orbit *smaller*
than `C1` by more than the single `deg` constraint predicts ⇒ the pairing
channel carries more than the degree, contradicting the mechanism.

**Cost.** Implementation medium (reuses B3-1's graph builder; adds per-channel
consistency predicates). Compute low-medium (brute-force degree-`d` isogeny
enumeration; keep `d ≤ 2^7` and `N ≤ 2^7` so the enumeration stays under
`10^7` operations).

**Ceiling.** `toy`. The strongest certifiable claim is an ordering of channels
*at the tested toy parameters*. It cannot establish that `C4` (common-scalar
masking) is safe at any real parameter set, and explicitly does not: the
corpus's M-SIDH/FESTA entries (`KN-LIT-4829`, `KN-LIT-2182`, `KN-LIT-3867`) are
**title-level only with no extracted abstract and no reachable PDF**, so the
literature verdict on `C4`/`C6` cannot be used as ground truth here.

**Kills-it-early.** Write out `r(C)` and `m(C)` symbolically for all eight rungs
on paper first (~30 minutes, zero compute). If two distinct rungs already have
the same `r − m` *and* are known to differ in hardness, the scalar is
insufficient before a single line of code is written.

---

### B3-3. The torsion-to-degree ratio ρ as the screen's continuous dial, and where its phase boundary actually sits

**Claim.** The F1 family's applicability is governed, to first order, by the
single scalar `ρ = log N / log d` (accessible torsion order vs secret degree),
with the known necessary condition `N > d` i.e. `ρ > 1`. Claim to test:
**the integer existence predicate for a valid degree matrix agrees with
brute-force ground-truth recoverability at the same `ρ`**, i.e. `ρ` is not
merely a necessary condition but locates the actual boundary. Direction:
measured recoverability rate rises from ≈0 to ≈1 across a window in `ρ` whose
location matches the predicate to within the toy graph's resolution.

**Mechanism.** Object O3 restricted to the unmasked channel `C7`. The
embedding needs an isogeny diamond whose degrees sum correctly (`d + (N−d) = N`
in the basic case), which is a pure integer condition — cheap to evaluate, no
abelian-variety arithmetic. Ground truth is separate and independent: in the
toy graph, enumerate all degree-`d` isogenies `E_0 → E_1` and check whether the
published `N`-torsion images single one out. Agreement of a cheap predicate
with expensive ground truth is what makes `ρ` a *screen dial* rather than a
restatement of Kani's hypothesis.

**Minimal discriminating test.** Grid over `(N, d)` with `ρ ∈ [0.6, 2.0]` in
~10 steps, at 2–3 toy primes. For each cell: (i) evaluate the integer existence
predicate; (ii) measure the fraction of random secrets uniquely pinned by the
published images. Plot both against `ρ`. **Three outcomes, all informative:**
predicate and ground truth co-locate ⇒ `ρ` is the dial; predicate fires below
the ground-truth boundary ⇒ `ρ` is necessary but loose, and the screen must
report `UNDECIDED` in the gap (a *useful* result: it sizes the gap); ground
truth fires below the predicate ⇒ the predicate is not necessary and
`KN-TECH-026`'s stated requirement is incomplete as this program has recorded
it.

**Null object / control.** Published images drawn from a random
`GL_2(Z/N)`-element applied to a basis of `E_1[N]`, with no generating isogeny.
The recoverability rate must be ≈0 across the whole `ρ` grid. **A recoverability
rate that does not fall as `ρ` decreases is the canonical artifact tell**
(`docs/inventor-protocol.md` §3): it means the toy graph is small enough that
uniqueness comes from graph size, not from the disclosure.

**Falsifier (reachable).** The null control shows a recoverability rate within
2σ of the live measurement at any `ρ` ⇒ the measurement is graph-size-bound and
the experiment is void at that parameter set. Also: no transition anywhere in
`ρ ∈ [0.6, 2.0]` ⇒ `ρ` is not a dial at toy scale.

**Cost.** Implementation medium (needs a degree-`d` isogeny enumerator and
`N`-torsion basis handling in pure Python; the torsion arithmetic is the fiddly
part). Compute medium (`~10` grid cells × `~10^2` random secrets ×
enumeration; budget `≤ 4` CPU-hours, hard cap).

**Ceiling.** `toy`. Explicitly cannot certify the boundary at crypto scale, and
cannot certify anything about masked channels (that is B3-2). Cannot execute a
Kani embedding — only its existence predicate and an independent ground truth.

**Kills-it-early.** At the smallest toy prime, check whether *any* `ρ < 1` cell
shows nonzero recoverability. If the whole grid is 0 or the whole grid is 1,
the toy scale has no dynamic range and larger `p` is required before any
gridding is worth running.

---

### B3-4. Embedding dimension controls existence of a splitting, not knowability of a kernel: converting `KN-TECH-026`'s applicability limit into a named obstruction

**Claim.** `KN-TECH-026` records, without argument, that "without the torsion
images the embedding cannot be built." This idea proposes the argument, in the
form `docs/inventor-protocol.md` §4 requires: **a named obstruction.** Proposed
obstruction: *raising the embedding dimension `g` increases the guaranteed
existence of a reducible/splitting structure (Robert's dim-4/8 result) but does
not increase the specifiability of the isogeny kernel, which is generated by
graph elements `(P, φ(P))` and therefore requires point images at rank 2 in the
`N`-torsion.* Existence and knowability are governed by different quantifiers,
and `g` moves only the first. Falsifiable form: **for every `g`, the kernel
generators of the embedding depend on `φ`'s action on `E_0[N]` and are not
determined by `(E_0, E_1, deg φ)` alone.**

**Mechanism.** Object O4. This is the §8 *quantifier-order audit* used
constructively: the true statement is `∀ instance ∃ g ∃ splitting`, while the
attack needs `∀ instance ∃ g ∃ splitting *computable from published data*`. The
proposal is that the second existential cannot be pushed inside, and that the
witness necessarily depends on data the survivor schemes never publish.
*Lossy-projection check:* the tracked object is `ker ⊂ (E_0 × E_1)[N]`
projected to "is this subgroup specifiable from `Σ`". That projection forgets
the subgroup itself and retains a boolean, and the boolean composes (a
specifiable kernel composed with a specifiable kernel is specifiable) — lossy
and propagating, hence admissible.

**Minimal discriminating test.** No compute in the main line. (1) Write the
kernel-generator dependency explicitly for `g = 2` and for the dim-4/8 case as
recorded in `KN-TECH-026`/`KN-LIT-067`, marking every step as *derived here* or
*relayed unread* (the primary papers are unreachable — this is the binding
limitation and must be stated, not hidden). (2) **Nearby-object control, which
is the discriminating part:** the closest object where the conclusion should
fail is a scheme publishing a *single* point image `φ(P)` for one point of
order `N`, not a full basis. Ask whether any `g` makes that sufficient. If yes,
the "full basis" requirement is *parametric* and the obstruction is weaker than
stated — a real boundary result. If no, the obstruction is *structural* at rank
2 and the screen gains a crisp rule: **rank of published torsion action is the
invariant, not the number of published points.** (3) Toy confirmation only:
verify at `p ≈ 2^13` that a single published image leaves an orbit of size > 1
while a full basis leaves size 1.

**Null object / control.** Run the identical dependency analysis on SIDH, where
the conclusion is known to fail (the embedding *is* buildable). If the analysis
does not distinguish SIDH from CGL, it has not identified the load-bearing
structure and the obstruction is not named — it is asserted.

**Falsifier (reachable).** (i) The single-image nearby object turns out to be
sufficient at some `g` ⇒ the rank-2 obstruction is false and the boundary moves.
(ii) A construction is exhibited whose kernel is specifiable from
`(E_0, E_1, deg φ)` alone ⇒ obstruction fails outright. (iii) The analysis
cannot be completed without reading `KN-LIT-067` in full ⇒ the deliverable is
`blocked`, recorded as such, and **not** downgraded to a plausibility argument.

**Cost.** Implementation low (toy confirmation reuses B3-1's builder). Compute
low (`≤ 0.5` CPU-hour). Analysis effort high — this is the hardest *thinking*
item in the slice and the one most exposed to the unreachable-source constraint.

**Ceiling.** `derivation`, scoped to the embedding constructions as this corpus
records them. **It cannot certify that no future embedding exists**; the honest
strongest claim is "for embeddings of the recorded shape, `g` does not supply
kernel knowability," plus forward guidance naming what remains open (embeddings
whose kernel is specified by something other than a graph of `φ`; embeddings
seeded by orientation data rather than point images — which is B3-5's lane).

**Kills-it-early.** One paragraph, zero compute: write the `g = 2` kernel
generators as a formula and check whether `φ`'s action appears. If it does not,
the obstruction is already false and the idea dies in an hour.

---

### B3-5. Minimal orientation fragment: how much of an orientation must leak before an exponent moves — and the cost of certifying orbit membership

**Claim.** Orientation disclosure is not binary. Order the fragments:
`F0` nothing; `F1` the discriminant `Δ` of an orientation known to exist;
`F2` `F1` + *certified* class-group orbit membership; `F3` the characteristic
polynomial of a generating endomorphism; `F4` the explicit endomorphism as an
evaluable map. Claim: **`F1` alone moves no exponent against the `KN-TECH-057`
matched baselines, and `F2`'s advantage is cancelled once the certification
cost is charged rather than assumed** — leaving `F4` (which no survivor
publishes) as the only fatal fragment. Direction: charged cost of exploiting
`F1`/`F2` ≥ `min(VW p^{1/2} at F_{p^2}, DG p^{1/3} at F_p)`; strict inequality
is the interesting case.

**Mechanism.** Object O5. `EV-SSI-004` closed `IDEA-20260725-002` with two
named residuals: *"naturality of independently published poly-bounded `α` on
path-finding instances"* and *"class-number heuristics unextracted"*, and
recorded that missing orbit membership **fails closed** with
`REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END`. **This idea differs from that
closed record in the quantifier**: `IDEA-20260725-002` asked whether a *given*
`α` (≈ `F4` + `F2`) beats the baseline and answered "in a regime"; this asks for
the *minimal* fragment, and specifically forces the certification cost that the
earlier record left as an unresolved confound to be *charged inside the
comparison*. That is a successor to a flagged confound, not a re-run.

**Minimal discriminating test.** Derivation, zero curve compute. For each of
`F1`–`F4`, write the best attack the corpus can name that consumes exactly that
fragment and no more, then charge: (a) the search cost, (b) the cost of
certifying orbit membership (`F2`) rather than receiving it, (c) memory under
the Wiener 3D model as `KN-TECH-057` does. Compare exponents to the matched
baselines. **Discriminating outcomes:** an exponent strictly below the matched
baseline at some fragment ⇒ that fragment is fatal and the screen gains a hard
rule; all fragments ≥ baseline once certification is charged ⇒ orientation
disclosure short of `F4` is *safe*, which is a clean `SAFE` verdict for the
survivors and exactly the "screen can return a negative" property.

**Null object / control.** The uncharged variant: run the identical derivation
*without* charging orbit certification. If the two derivations give the same
exponent, then certification was never load-bearing and `EV-SSI-004`'s
fail-closed disposition was over-cautious — a correction worth recording. If
they differ, the size of the difference *is* the result.

**Falsifier (reachable).** `F1` (bare discriminant) is shown to move an
exponent ⇒ claim false, and a much larger fraction of the design space is
implicated than currently believed. Conversely: the certification cost is
unbounded / not expressible ⇒ the comparison is ill-posed and must be recorded
as `UNDECIDED`, not as a `SAFE` verdict.

**Cost.** Implementation low (no code). Compute none. Effort medium-high;
depends on class-number heuristics that `EV-SSI-004` records as *unextracted* —
if they cannot be extracted from the corpus, the `F2` row is `blocked` and must
be reported as blocked.

**Ceiling.** `derivation`, conditional on the `KN-TECH-057` baselines (which are
themselves partly conditional: the `F_p` VW figure assumes unproven subgraph
mixing). Cannot claim anything about CSIDH's or SQIsign's real parameters.

**Kills-it-early.** Check first whether `F1` even determines a finite candidate
set: if the number of curves with a given orientation discriminant is
super-polynomial in `log p` for the relevant `Δ` range, `F1` is trivially safe
and only `F2`–`F4` need analysis — collapsing the work by half.

---

### B3-6. Turn the screen on this program: charged-provenance audit of its own transfer, cover, and advice directions

**Claim.** This program's transfer/cover/self-reduction directions are subject
to the same screen, and the screen has a definite verdict on each. Every
"given" in a proposed reduction falls into exactly one of three classes:
**(a)** publicly computable from the instance (no disclosure, no charge);
**(b)** a *hypothesis on the instance* — only some curves admit it (charge as a
restricted-instance claim, never as a general result); **(c)** oracle-supplied
(an uncharged-oracle disclosure — the failure mode `EV-SSI-004` already names).
Claim: at least one live program direction currently sits in (c) without
saying so; and the audit's *acquittal* of the rest is equally a result.

**Mechanism.** Object O6. Audit targets, all internal: `EXP-ISADV-001`
(planted-advice transfer across isogenous curves — advice is *planted*, hence
class (c) by construction, which makes it the **positive control**); the
cover/transfer lane (`KN-TECH-033`, Weil-descent / GHS / trace-zero / Prym
material); `RQ-JMV-001`'s isogeny-expander random self-reduction (the reduction
*supplies* a walk — is the walk computable, hypothesised, or given?); and any
proposal assuming a known orientation, cover map, or endomorphism as input.
*Lossy-projection check:* not applicable — this is an audit protocol, not a
tracked mathematical object, and is recorded as such rather than dressed up as
one.

**Minimal discriminating test.** Read each target's own record and classify its
"givens" into (a)/(b)/(c) with a one-line justification and a citation to the
record. The test discriminates because it has a **mandatory positive control**:
`EXP-ISADV-001` plants its advice explicitly, so the audit *must* classify it
(c). An audit that returns (a)/(b) for everything including the planted-advice
experiment is untested instrumentation and its output is void.

**Null object / control.** Positive control as above (`EXP-ISADV-001`, must
return (c)). Negative control: a direction whose inputs are unambiguously
public — e.g. a cost-model derivation like `EXP-WESOVOW-001` that consumes only
published parameters — which must return (a). Both controls must resolve
correctly before any indictment is recorded.

**Falsifier (reachable).** The audit fails either control ⇒ the classification
rubric is not discriminating and no verdict may be reported. Separately: the
audit finds *no* (c) among the live directions ⇒ the claim's second clause is
false and the program is acquitted on this axis — a valid, complete, and
non-embarrassing outcome that should be recorded as such rather than pushed
until something fires.

**Cost.** Implementation none. Compute none. Effort low (a reading and
classification pass). This is the cheapest item in the slice.

**Ceiling.** `control`. It produces no mathematics. Its value is that a
disclosure screen that has only ever been pointed outward has never been tested
on data whose ground truth this program controls.

**Kills-it-early.** Classify `EXP-ISADV-001` first. If the rubric cannot
cleanly return (c) on an experiment that literally plants the advice, the rubric
is broken and the audit stops there.

---

### B3-7. Is degree disclosure asymptotically free? A full-cost exponent for the revealed-degree-only channel

**Claim.** Publishing the exact degree `d` of a secret isogeny, with **no**
point images, is a nonzero auxiliary channel, and its effect is expressible as
a threshold. Claim to derive: under the Wiener 3D full-cost model of
`KN-TECH-057`, fixed-degree search costs `≈ d^{1/2}` at polynomial memory
(memory-free collision search over the `≈ σ(d)` degree-`d` isogenies) and
`≈ d^{2/3}` for a table-based meet-in-the-middle after the wiring penalty.
Writing `δ = log d / log p`, the channel is **not free** whenever
`d^{1/2} < min(baseline)`; against `DG p^{1/3}` (`F_p`) that is `δ < 2/3`, and
against `VW p^{1/2}` (`F_{p^2}`) that is `δ < 1`. Direction: the exponent is
`min(δ/2, baseline exponent)`, strictly below baseline on an explicit interval.

**Mechanism.** Object O7. Degrees compose multiplicatively and the channel is
maximally lossy (it retains one integer), so it passes §2 trivially — and that
is the point: it is the *coarsest* channel that still propagates, hence the
natural floor of B3-2's lattice. The corpus records that memory-free
fixed-degree algorithms beat MITM over a range of the degree parameter
(`KN-LIT-132`, via `KN-TECH-050`) but records **no exponent**, and
`KN-TECH-050` states plainly that it is "insufficient to state what the matched
baseline costs." **Fallback for the unreachable-source constraint:** derive the
fixed-degree exponents here, in the Wiener model, from the algorithm structure —
do not relay `KN-LIT-132`'s numbers, which this corpus has never read.

**Minimal discriminating test.** Analytic derivation with a small toy sanity
check. (1) Count degree-`d` isogenies from a fixed curve (`≈ σ(d)`), state the
enumeration cost per isogeny, and derive step count and full cost for both the
memory-free and the table variant, charging the `S^{1/3}` wiring term exactly as
`KN-TECH-057` does. (2) Produce the exponent-vs-`δ` chart with the crossover
points marked. (3) Toy sanity check at `p ≈ 2^13`: measure the actual number of
degree-`d` isogenies between random supersingular curves for several `d` and
confirm it tracks `σ(d)` / the expected count — if it does not, the counting
premise of the derivation is wrong at the very scale where it can be checked.

**Null object / control.** The `δ ≥ 1` regime is the built-in control: for
`d ≥ p` the derived cost must *not* beat the generic baseline. A derivation
that shows degree disclosure helping at every `δ` has an error, because at
`δ ≫ 1` there is no information in the degree.

**Falsifier (reachable).** Once the per-isogeny enumeration cost and the cost of
*verifying* a candidate are charged, the fixed-degree cost is `≥ min(baseline)`
for all `δ` in range ⇒ **degree disclosure is asymptotically free**, the claim
is false, and the screen gains a `SAFE` rule for every scheme that publishes
response degrees. That negative is the more likely outcome and is fully
usable.

**Cost.** Implementation low (chart + toy counter). Compute low
(`≤ 1` CPU-hour).

**Ceiling.** `derivation`. **Explicit scope limit: no parameter set of any
scheme is evaluated.** The threshold is stated as a function of `δ`. SQIsign
publishes response-isogeny degrees, but this program has read no Round-3
specification (`GOAL-SQISIGN-002` next_action), so **no claim whatever is made
about SQIsign's `δ`**, and the derivation must state that gap rather than fill
it with a guess. Inherits `KN-TECH-057`'s conditionality (the `F_p` VW figure
assumes unproven mixing).

**Kills-it-early.** Ten minutes: write the number of degree-`d` isogenies and
the cost of testing one. If testing a candidate already costs more than the
generic baseline divided by `σ(d)`, the channel is free and the derivation is
finished before it starts.

---

### B3-8. Calibration ladder and observation-collision hunt: the screen is untested instrumentation until it is scored on graded ground truth

**Claim.** A disclosure screen that has only ever returned "does not apply" on
survivors is untested instrumentation (`docs/inventor-protocol.md` §3;
`GOAL-SQISIGN-002` makes the same demand for its single audit). Claim: the
screen of B3-1 can be scored on a **graded ladder** of seven synthetic toy
schemes with pre-registered intended verdicts, and its errors are informative —
`R0` CGL (`SAFE`); `R1` CGL + published walk length (`SAFE`/`UNDECIDED`);
`R2` free class-group action (`UNDECIDED` — the false-alarm rung);
`R3` public-degree response, no images (`SAFE`/`UNDECIDED`);
`R4` common-scalar-masked images (**intended verdict UNKNOWN**, see below);
`R5` unbalanced published basis images (`FATAL`); `R6` balanced published basis
images (`FATAL`). Second claim: **hunt for an observation collision** — two
surfaces `Σ ≠ Σ'` with the identical screen observable and different
brute-force ground-truth recoverability. A collision falsifies the screen's
identifiability directly.

**Mechanism.** This is `docs/inventor-protocol.md` §8 audits 2 and 4 executed as
an experiment rather than filled in as a form. The ladder supplies the method
ceiling (what the screen can certify) and the nearby-object controls (adjacent
rungs with opposite intended verdicts). The collision hunt supplies the
identifiability falsifier. **Differentiation from `GOAL-SQISIGN-002`:** that
goal requires *one* weakened null variant that must make *its* audit fire; this
is a graded calibration curve scoring a *general* screen across seven rungs,
including a rung whose correct answer is instance-dependent. The two do not
overlap in write scope and neither substitutes for the other.

**Minimal discriminating test.** Implement the seven rungs at `p ≈ 2^13`, run
B3-1's screen on each, and record verdict vs intended verdict as a confusion
table. Then, for a fixed rung, enumerate surfaces exhaustively at a very small
`p` and search for two with equal observable and unequal recoverability.

**Null object / control.** `R0` and `R6` are the two mandatory poles: the screen
**must not** fire on `R0` and **must** fire on `R6`. Failure at either pole
voids every other rung. Additionally, each rung is run against a random-surface
version of itself (as in B3-1) so that "fires" is distinguished from "fires on
anything of that shape."

**Falsifier (reachable).** (i) Screen fires on `R0`–`R3` ⇒ over-sensitive,
useless as a screen, and the `SAFE` verdict is unreachable. (ii) Screen fails to
fire on `R5`/`R6` ⇒ under-sensitive, and the `FATAL` verdict is unreachable.
(iii) A collision is found ⇒ the observable is not identifying and needs an
additional separating condition, which is then the deliverable.

**Cost.** Implementation medium (seven rungs on B3-1's builder). Compute
low-medium (`≤ 2` CPU-hours; the exhaustive collision hunt must be capped at a
very small `p` with a hard budget).

**Ceiling.** `toy` / `control`. **`R4` cannot be scored.** Its intended verdict
would have to come from `KN-LIT-2182` / `KN-LIT-4829`, which are title-level
entries with no extracted abstract and whose local PDFs are absent from this
worktree; primary sources are unreachable. `R4` is therefore recorded as
`INTENDED-VERDICT-UNKNOWN` and **excluded from the score**, with the exclusion
stated in the deliverable. Filling `R4` from memory would be a fabricated
citation.

**Kills-it-early.** Build `R0` and `R6` only, and run the screen on both. If the
two poles are not separated, the ladder is pointless and B3-1 needs redesign
before the middle rungs are written.

---

## 2. Honest accounting (`docs/inventor-protocol.md` §5)

- **Objects studied.** O2 residual set; O3 constraint-rank-minus-mask-dimension;
  O4 Kani-kernel specifiability; O5 orientation fragment; O6 charged provenance
  of a reduction's givens; O7 revealed degree. O1 (the secret isogeny) declared
  off-limits.
- **Depth of verified structure.** **None.** Nothing in this file has been
  computed, derived to completion, or tested. Every item is a proposal. The
  lossy-projection checks in §0 and per idea are algebraic observations made
  here and are the only content not requiring future work; they are recorded at
  the tier "argued in this document, not independently reviewed."
- **`dominated_by`.** `n/a (no result claimed)`. No idea in this file claims an
  attack, a cost, or an exponent improvement over any row of the frontier. The
  one exponent-facing item, **B3-7, is dominated by construction**: its own most
  likely outcome is that the revealed-degree channel does not beat
  `min(VW p^{1/2} F_{p^2}, DG p^{1/3} F_p, Wesolowski p^{1/3+o(1)} heuristic)`
  as recorded in `KN-TECH-057` / `KN-TECH-058`, and it is proposed *because* a
  negative there is a usable screen rule. Frontier rows checked for that
  comparison: MITM `p^{2/3}` full cost, DG `p^{1/3}` full cost, VW `p^{1/2}`
  (`F_{p^2}`) and `p^{1/4}` (`F_p`, conditional on mixing), Wesolowski
  `p^{1/3+o(1)}` time *and* memory above a superpolynomial `o(1)`.
- **`sota_delta`.** Zero on every attack axis (time, memory, data/queries): no
  algorithm is proposed. The intended delta is **instrumental** — converting
  `KN-OPEN-015`'s "general characterization is not settled" into a screen with a
  three-valued verdict and a stated false-alarm mode, and converting
  `KN-TECH-026`'s one-sentence applicability limit into a named obstruction
  (B3-4). Neither is a complexity result and neither should be scored as one.
- **Enumerated closures (§4 standard) — none claimed here.** This session
  closes nothing. It *relies on* two existing closures (`EV-SSI-004`,
  `EV-SSI-006`) and proposes successors to both flagged residuals rather than
  re-running them (B3-5 for the orientation confound; B3-1/B3-8 for the "audit
  that only ever returns does-not-apply" gap). The saturation of the
  auxiliary-structure lane is **not** asserted: `KN-OPEN-019` records that this
  program has no object enumeration, and §0's object table is a **sketch, not a
  taxonomy**.
- **Open directions for the next session.** (1) Disclosure channels that are
  *not* projections of the torsion channel at all — orientation-seeded
  embeddings (the class B3-4's forward guidance names as remaining open).
  (2) Whether `KN-OPEN-024`'s rank-1-vs-rank-`g` gap is itself an
  auxiliary-structure statement: `M_g(O) = End(E^g)`, so "does `E^g` give away
  more than `E`" is a disclosure question in the same family as this slice, and
  the screen of B3-1 has no rung for it. (3) Interactive/adaptive disclosure
  (F2's lane), which every idea here excludes by treating `Σ` as static.
- **Novelty.** `unverified` for all eight. The corpus was searched
  (`knowledge/`, `ledger/proposals/`, `ledger/evidence/`); web and primary
  sources were **not** reachable. No idea here is claimed new, and none is
  dismissed as known.

---

## Batches

Three bounded batches, run in order. At most **3 concurrent non-archive tasks**;
write scopes are disjoint (one task directory per idea, no shared ledger edits).
Batch B is gated on Batch A's poles separating (B3-8 kill-early), because
measuring a boundary with an uncalibrated instrument produces a number with no
referent. Batch C is gated on Batch B only for B3-5's baseline inputs; B3-6 has
no dependency and may be pulled forward into any spare slot.

### Batch A — "Is the instrument real, and is the cheapest channel already priced?"

- **Ideas:** B3-1, B3-8, B3-7.
- **Grouping rationale:** B3-1 defines the screen and B3-8 is the only thing
  that makes B3-1's output meaningful — they must not be separated, or the
  program acquires a screen it has never scored. B3-7 is included because it is
  fully independent (an analytic cost derivation needing none of the screen
  machinery), fills the third slot without contention, and its likely negative
  supplies a `SAFE` rule the screen can consume in Batch B.
- **Budget:** implementation medium; compute `≤ 4` CPU-hours total, hard cap;
  `p ≤ 2^15`; no genus-2 arithmetic; no network.
- **Decides:** whether a two-stage screen with a reachable `SAFE` verdict exists
  and separates the mandatory poles `R0`/`R6`; whether its observable is
  identifiable (collision hunt); and whether revealed-degree disclosure is
  asymptotically free or has a threshold in `δ = log d / log p`.
- **Stop rule:** if the `R0`/`R6` poles do not separate, Batch B does not launch.

### Batch B — "Where is the safe/fatal boundary, and is it structural or parametric?"

- **Ideas:** B3-2, B3-3, B3-4.
- **Grouping rationale:** the three named dials of the disclosure geometry —
  channel coarseness (`r − m`), torsion-to-degree ratio (`ρ`), and embedding
  dimension (`g`) — measured against one shared toy graph builder and one shared
  brute-force ground truth. Splitting them would duplicate the expensive
  enumerator three times. B3-4 is the theory item and carries the batch's real
  value: it is the only one that can produce a §4-standard named obstruction.
- **Budget:** implementation medium-high; compute `≤ 8` CPU-hours total, hard
  cap; hard limits `d ≤ 2^7`, `N ≤ 2^7`, `p ≤ 2^15`. Any timeout is an
  infrastructure outcome, never negative mathematical evidence.
- **Decides:** whether the disclosure channels are linearly ordered by
  `r − m`; where the `ρ` phase boundary actually sits versus the existence
  predicate, and how wide the `UNDECIDED` gap between them is; and whether
  "no images ⇒ no embedding at any `g`" is a structural obstruction at torsion
  rank 2 or merely a parametric statement about full bases.
- **Stop rule:** if the B3-3 null control matches the live measurement within
  2σ, the toy scale has no dynamic range — record that and stop rather than
  regrid.

### Batch C — "What does the calibrated screen indict, including at home?"

- **Ideas:** B3-5, B3-6.
- **Grouping rationale:** both are application passes with zero curve compute
  and disjoint targets — B3-5 points the screen at orientation fragments
  (external), B3-6 points it at this program's own transfer, cover, and advice
  directions (internal). Pairing them means the same rubric is exercised on
  external and internal ground truth in one batch, which is the cheapest test of
  whether the rubric is target-independent. Two tasks, leaving one slot free
  deliberately: `AGENTS.md` dispatch guidance is not to fill capacity merely
  because a slot exists.
- **Budget:** implementation none; compute none; reading and derivation only.
- **Decides:** the minimal orientation fragment that moves an exponent once
  orbit-membership certification is charged (successor to `EV-SSI-004`'s flagged
  confound, not a re-run); and whether any live program direction is currently
  resting on an uncharged-oracle disclosure — with an acquittal recorded as a
  full result if none is.
- **Stop rule:** B3-6 halts immediately if the rubric cannot return class (c) on
  `EXP-ISADV-001`, whose advice is planted by construction.
