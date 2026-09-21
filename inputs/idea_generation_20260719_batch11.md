# ECDLP Idea Generation — 2026-07-19 batch11 (report #19 / "batch17")

Role: Research Director, empirical cryptanalysis lab. Target: a non-generic
prime-field ordinary-curve ECDLP algorithm whose **complete** cost beats the
Pollard-rho `~0.886*sqrt(n)` single-target baseline. Toy correctness, a new
coordinate system, a relation certificate, faster preprocessing, or a solver
improvement alone is NOT a breakthrough.

Authorized scope: generated toy curves, public benchmark instances, synthetic
data only. No wallets/keys/accounts.

---

## 0. Input review and machine-readable ledger inventory

Reviewed in full (not sampled):

- `research_ledger.md` (main): true numeric frontier **P1486**, `ECFG-P` frontier
  **P1470**, 1244 distinct `P####` IDs. ID families present: `P`, `ECFG-P`,
  `ECFG-NR`, `ECFG-MX`, `ECFG-RT`, `PO`, `RT-`, `RQ-`, `IDEA-`, `EXP-`, `EV-`,
  `DEC-`.
- `ecdlp_index_calculus_state/research_ledger.md`: frontier **P1509–P1513**
  (P1512-R1 closed, P1513 open); families `ECFG-P####-R#`, `ECFG-NR`, `ECFG-MX`.
- `research/non_generic_transfer_search_20260610.md`: transfer/decomposition
  channel search; same-field isogeny transfer = NEGATIVE/model-bound; genuinely
  new Jacobian/correspondence relation engines not factoring through the scalar
  x-line = OPEN.
- `ecdlp_index_calculus_state/research_sources/bibliography.json`: 90 entries.
- **All 18 prior idea reports** `idea_generation_2026071{7,8,9}*.md` (report IDs
  through `ECFG-P1669`) and their anti-duplication catalogue (memory index
  `ecdlp-idea-generation-reports.md`).

**Entries reviewed:** the full committed ledgers (main frontier P1486 / ECFG-P1470;
IC-state P1509–P1513) plus 18 report files carrying proposed IDs to P1669.
**ID families covered:** P, ECFG-P, ECFG-NR, ECFG-MX, ECFG-RT, PO, RT, RQ, IDEA,
EXP, EV, DEC, and the report-local `ECFG-P15xx/16xx`.

### The two — and only two — live rho-crossing surfaces (verified from ledger text)

- **RT-1472 / `ECFG-RT-1472`** (OPEN): explicit hash-like **two-large-prime graph**
  at `B=n^(1/5)`. Exact cost exponent `max(2*ell, 1-ell, 1+1/5-2*ell)`, minimized
  at `ell=1/3` giving `2/3`. Explicit advice must reach enrichment **`delta>1/4`**
  to cross rho; pair advice/support `Theta(L^2)`, `Theta(L+B)` edges. P1471 hit
  ratio 0.829/0.884, energy ratio 1.0.
- **RT-1476 / `ECFG-RT-1476`** (OPEN): complete **five-term implicit membership
  backend** with query exponent **`alpha<3/2`**, setup `<=L^2`, random-like
  support, `Theta(L)` rows, sparse LA `L^2`. Optimum `ell=1/(m+1-alpha)`,
  total `2/(m+1-alpha)`; `m<=3` impossible, `m=4` needs `alpha<1`, `m=5` needs
  `alpha<3/2`.
- IC-state supporting facts: **P1510** per-target compiler positive (`r^2`
  pair-resultant leaves/target); **P1511-R2** closed (product-circuit gcd/subres/
  Hasse semijoin, input degree `r^3`, leaf/rho ratio `sqrt(r)`); **P1512-R1**
  closed (scalar-linear Chow atomizer `Omega(r^5)` via `deg(det M)<=dim`, only a
  **target-specialized NONLINEAR-circuit exception** preserved); **P1513** OPEN
  (shared bivariate common-norm: input quadratic, both norms cubic).

### Saturation statement (report #19)

Eighteen prior reports each imported a fresh lower-bound / representation
technology family and each concluded: winners are near-certain **scoped
negatives**, the **barrier arm is higher-EV**, and **RT-1472 / RT-1476 remain
open**. The mechanism space around the two gates is saturated. This report does
not claim a break. Its honest value is (a) importing three technology families
absent from all 18 reports and the ledger, and (b) two barrier candidates whose
thresholds, if they bite, each **close a live gate**.

### Technology families imported this run (grep-verified 0 prior-report hits)

1. **Parameterized / kernelization lower bounds** — OR-cross-composition,
   distillation, no-poly-kernel under `coNP/poly` (Bodlaender–Downey–Fellows–
   Hermelin 2009; Fortnow–Santhanam 2008; Bodlaender–Jansen–Kratsch 2014). This
   is the exact formal question behind RT-1476: "can the `L^5`-support membership
   instance be **compressed** to a small backend?" — no prior report used
   instance-compression complexity.
2. **Ergodic-theory multiple recurrence** — Furstenberg 1977 ergodic proof of
   Szemerédi, Furstenberg–Katznelson density recurrence, as an RT-1472 `delta`
   supply ceiling. Distinct from the analytic-NT arm (batch14 large sieve, batch15
   circle method) and the additive-energy arm (batch3 ENERGY).
3. **Metric embedding / NNS cell-probe via metric expansion** — Panigrahy–Talwar–
   Wieder (FOCS 2010, robust expansion), Andoni–Indyk–Pătrașcu lopsided set
   disjointness, Ribe-program nonembeddability (Bourgain, Matoušek). A **static**
   data-structure lower bound driven by **metric expansion**, distinct from batch15
   round-elimination (asymmetric communication), batch12 cell-probe chronogram
   (dynamic), batch13 Borodin–Cook (time-space).

Supporting (also absent from prior reports): **resolution/width proof complexity**
(Ben-Sasson–Wigderson) — prior proof-complexity barriers were all *degree/rank*
(PolyCalc, SOS, Sherali–Adams, cutting-planes) or *space* (pebbling); **width** is a
new axis. And **BBD decomposition theorem / perverse sheaves** for the
representation arm.

Six or more candidates below begin outside the ledger's dominant algebraic-
geometry / index-calculus vocabulary (in fact all twelve do). The six task-brief
search seeds (Hasse-jet, tropical, incidence, transfer-operator, path-algebra,
tensor-net) were exhausted by batch4 and are not re-proposed.

Proposed IDs this run: **ECFG-P1670 .. ECFG-P1681**.

---

# GROUP A — Conservative extensions of known work

## Candidate: KERNELIZATION-COMPRESSION-A1  (P1670) — CONSERVATIVE WINNER

### One-sentence mechanism
Exploit **instance-compression complexity** (OR-cross-composition) to decide
whether the five-term membership instance with `L^5` support can be kernelized to
a backend of size `o(L^2)` — the exact object RT-1476 requires — reducing the
membership-query exponent `alpha` below `3/2`, versus the strong prior that no
poly kernel exists.

### Status
HYPOTHESIS (meter); its near-certain resolution is a NEGATIVE CONTROL.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (kernelization lower bounds are standard, but
never applied to Semaev m-ary membership compression).

### Semantic fingerprint F(C)
- algebraic object: the P1510 per-target compiler instance (`r^2` marked
  pair-resultant leaves; five-point membership predicate).
- available public operations: field arithmetic, resultants, the P1510 grammar.
- hidden structure exploited: whether membership is *compressible* — a small
  self-reduction kernel — not whether it is *solvable*.
- information discarded: per-target coefficient values (kept only the kernel size).
- information retained: instance-size-vs-parameter growth under OR-composition.
- relation-generation primitive: N/A (this is a meter on the backend, not a
  generator).
- compression primitive: **kernelization / distillation** (the object under test).
- rank mechanism: N/A.
- descent mechanism: same backend reused for individual-log descent (RT-1476
  assumption).
- dominant cost exponent: `alpha` (query exponent of the compressed backend).

### Nearest ledger entries (5)
1. **P1476 / ECFG-RT-1476** — defines `alpha`. A1 is a *complexity-theoretic*
   meter on whether the required compressed backend can exist at all; RT-1476
   only *optimizes over ell assuming* the backend exists. Distinction: existence
   vs parameter-optimization.
2. **P1477-R2** (materialized serial-S3 does not beat `L^1.5`) — measured a
   *specific* construction dense. A1 asks whether *any* poly-size kernel exists —
   a class statement, not one construction.
3. **P1479** (no exact `<=L^(1/2)` public linear feature space) — a *linear*
   compression negative. A1 is *nonlinear/arbitrary* instance compression.
4. batch7 **VCDIM-D3** / batch13 **SENSITIVITY-BLOCK-A1** — combinatorial query
   meters (shatter function, `s/bs/C/D`). Distinction: A1 measures instance
   *compressibility* (kernel bit-length), a different resource axis than query
   count.
5. batch11 **LDC-LOCAL-DECODABILITY-A1** — length-vs-query LDC bound. Distinction:
   LDC bounds a *code*; kernelization bounds a *self-reduction*; the composition
   machinery (Fortnow–Santhanam distillation) is disjoint.

### Nearest literature
- Bodlaender, Downey, Fellows, Hermelin, *On problems without polynomial kernels*,
  JCSS 2009 — OR-composition ⇒ no poly kernel unless `coNP ⊆ NP/poly`.
- Fortnow, Santhanam, STOC 2008 — distillation ⇒ `PH` collapse.
- Bodlaender, Jansen, Kratsch, *Kernelization Lower Bounds by Cross-Composition*,
  SIAM J. Discrete Math. 2014.
- **Gap:** the framework requires an **NP-hard seed** that OR-composes into the
  parameterized problem. Fixed-field five-term membership is in **P** (P1476 gives
  explicit `L^{alpha}` solvers with `alpha<=3/2`), so no NP-hard seed exists — the
  framework may be *vacuous* for the single-instance problem.

### Target family
Ordinary `E/F_p`, prime group order `n`, `p` large, non-CM generic; parameter
`k=5` (membership arity), `L=q^{ell}`. Excluded: CM/`j∈{0,1728}`, supersingular,
non-prime order, small embedding degree.

### Full algorithmic path
1. **factor-base construction:** subgroup-x deck of size `L` (as P1473/P1477).
2. **relation generation:** five-point membership queries via the P1510 compiler.
3. **witness extraction/verification:** exact source-tuple recovery + independent
   re-check (claim tier: relation certificate).
4. **relation probability:** support `min(1, L^5/q)` (RT-1476 model).
5. **matrix dims/density/rank:** `Theta(L)` rows, sparse, `L^2` LA (unchanged).
6. **factor-log calibration:** standard.
7. **individual log / descent:** same backend (RT-1476 assumption).
8. **offline/online separation:** the *kernel* is the offline object; A1 measures
   its size growth.
9. **memory/parallelism:** kernel bit-length = memory; parallel over targets.

Meter itself (not a full solver): construct the parameterized problem
`5-MEMBERSHIP(L)` and test whether the amortized **many-target** version admits an
OR-cross-composition from a plausibly hard seed (e.g. multivariate root-counting
mod p at bounded degree), which would imply **no poly kernel** ⇒ any backend must
touch `Omega(L^2)` support ⇒ `alpha>=3/2`. Complete meter path; the *solver* it
gates is exactly RT-1476's backend.

### Cost model
Meter cost: build `t` composed instances, size `poly(L)*t`; a poly kernel would
compress to `poly(L)`; distillation test is `O(t)` reductions. Against baselines:
this does not itself solve ECDLP; it decides whether the RT-1476 backend that
would give total `q^{2/5}` (vs rho `q^{1/2}`) can exist. If the kernel lower bound
holds ⇒ `alpha>=3/2` ⇒ RT-1476 closed for the compression class ⇒ no crossing.

### Why the existing negative results do not already kill it
P1477-R2 and P1479 killed *specific* (materialized serial-S3, linear-feature)
compressions. A1 asks the *class* question — no poly kernel of **any** form — via
a complexity-theoretic obstruction none of those measured. New operation:
OR-composition / distillation, absent from the ledger.

### Likely fatal obstruction
**Near-certain vacuity:** single-instance five-term membership is in P, so the
composition framework has no NP-hard seed to compose. The honest outcome is
"kernelization framework does not apply to a poly-time predicate" — which
*names and closes the "just kernelize the membership instance" hope* but does not
itself produce an `alpha` bound. Escape hatch: apply it to the **amortized
many-target** decision problem (arguably the real IC setting), where a
`#P`/counting seed may compose — but that likely reprices rho rather than beating
it.

### Minimal falsifying experiment
Toy `q ≈ L^5` at `L∈{4,8,16}`, ordinary prime-order controls, 3 seeds each.
Positive control: a problem WITH a known poly kernel (`k`-Vertex-Cover) to
validate the harness. Negative control: a problem WITHOUT (`k`-Path) to confirm
the distillation detector fires. Measure: does `5-MEMBERSHIP` admit an
OR-composition (seed hardness present) or is it detected in-P (framework vacuous)?

### Quantitative promotion gate
Promotion requires a **proven no-poly-kernel result** for the amortized
`5-MEMBERSHIP` implying **`alpha>=3/2` is unavoidable** (a barrier, negative for
crossing) OR, to advance a *positive* crossing, a construction of a poly kernel of
size `o(L^2)` with a measured backend `alpha<3/2` on `L∈{4,8,16,32}` with LOO
slope `<3/2`. Correctness of the kernel harness alone is not the gate.

### Proof track
Theorem: `5-MEMBERSHIP`(amortized) OR-cross-composes from `d`-Root-Counting mod p
⇒ no poly kernel unless `coNP ⊆ NP/poly` ⇒ any correct backend materializes
`Omega(L^2)` bits ⇒ `alpha>=3/2`.

### Disproof track
Exhibit a poly kernel: a self-reduction compressing the `L^5`-support instance to
`o(L^2)` bits with exact recovery — which would directly threaten RT-1476.

### Reproduction artifact
Contract `experiment_contract_p1670_kernelization_membership_compression.md`;
impl `p1670_cross_composition_membership_meter.py`; result
`p1670_result.json`; audit `p1670_audit.py`; ledger `ECFG-P1670`.

---

## Candidate: ERGODIC-RECURRENCE-A2  (P1671)

### One-sentence mechanism
Exploit **Furstenberg multiple-recurrence density** of the honest two-large-prime
support set to bound the RT-1472 enrichment `delta`: if the support has only the
random recurrence density, `delta -> 1/4` and no crossing.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (ergodic Szemerédi is classical; never applied as
a δ-supply meter here).

### Semantic fingerprint F(C)
object: the 2-LP occupancy set on `Theta(L^2)` pairs; ops: additive shifts on the
subgroup deck; hidden structure: multiple-recurrence density along the group law;
discarded: pair identities (kept density only); retained: recurrence density
exponent; relation-gen primitive: honest summation-graph edges; compression: none;
rank mechanism: cycle-rank of the enriched graph; descent: N/A (supply meter);
dominant exponent: `delta`.

### Nearest ledger entries (5)
1. **P1472 / RT-1472** — defines `delta`. A2 is a recurrence-density meter on the
   same object.
2. batch4 **CORRELATED-PEEL-A3** (Wormald DE 2-core) — measures 2-core threshold
   via differential equations; A2 measures *ergodic recurrence density*, a
   different quantity (average along orbits, not peeling dynamics).
3. batch14 **LARGE-SIEVE-SUPPLY-A1** — `L^2` dual inequality over the modulus
   family; A2 is a recurrence average, not a sieve inequality.
4. batch15 **SINGULAR-SERIES-A1** — circle-method `𝔖`; A2 is the ergodic
   (not analytic) side of the same density question.
5. batch3 **ENERGY-D1** (additive energy) — second-moment count; A2 is a
   recurrence density along shifts, higher-order.

### Nearest literature
- Furstenberg, *Ergodic behavior of diagonal measures and a theorem of Szemerédi*,
  J. Analyse Math. 1977. Furstenberg–Katznelson density Hales–Jewett.
- **Gap:** ergodic recurrence gives **qualitative** positive density (there exist
  many patterns) but not the **quantitative** `delta>1/4` vs `<=1/4` boundary; the
  correspondence principle loses the exact exponent.

### Target family
As A1. Excluded: special CM decks where the orbit is a single short AP.

### Full algorithmic path
1. deck of size `L`; 2. honest 2-LP edges from group-law sums; 3. witness =
one-witness cycle, verified; 4. edge probability random-like `L^{-3}` per pair;
5. graph `Theta(L)` rows sparse; 6. calibrate cycle-rank vs targets; 7. N/A;
8. offline = recurrence-density estimate; 9. memory `Theta(L^2)` pairs.
Meter: estimate the multiple-recurrence density of the support and compare to the
random baseline `1/4`.

### Cost model
Meter `Theta(L^2)` to enumerate pairs at toy scale; asymptotic claim symbolic. If
`delta=1/4` (random) ⇒ RT-1472 not crossed. Compare: crossing needs `delta>1/4`;
rho exponent `1/2`, IC-with-enrichment `2/3 - (something)` only if `delta>1/4`.

### Why the existing negative results do not already kill it
The analytic-NT arm (batch14/15) bounded `delta` via inequalities and the circle
method; ergodic recurrence is the *dynamical* dual and could, in principle,
detect structured excess those inequalities average away. New operation:
Furstenberg correspondence, absent from the ledger.

### Likely fatal obstruction
Qualitative-not-quantitative: Szemerédi-type density does not resolve `1/4 ± o(1)`.

### Minimal falsifying experiment
`L∈{16,32,64}`, 3 seeds, ordinary prime-order; positive control = a planted
structured deck with known excess density; negative control = random-x deck.
Measure recurrence density vs `1/4`.

### Quantitative promotion gate
A **proven** `delta<=1/4` unconditional over recurrence-countable support
(→ barrier D1) OR a measured structured-deck `delta>1/4` with LOO-stable slope.

### Proof track
Furstenberg–Katznelson ⇒ honest support density = random baseline ⇒ `delta<=1/4`.

### Disproof track
A curve family whose 2-LP support has recurrence density strictly `>1/4`.

### Reproduction artifact
`experiment_contract_p1671_ergodic_recurrence_supply.md`;
`p1671_recurrence_density_meter.py`; `p1671_result.json`; `p1671_audit.py`;
ledger `ECFG-P1671`.

---

## Candidate: RESOLUTION-WIDTH-A3  (P1672)

### One-sentence mechanism
Exploit the **resolution width–size relation** (Ben-Sasson–Wigderson) on the CNF
encoding of "2-LP graph has enrichment `delta>1/4`" — if refuting the *absence* of
enrichment needs width `Omega(L)`, no small resolution certificate exists, so the
enrichment is not efficiently certifiable and `delta<=1/4` in the resolution class.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT.

### Semantic fingerprint F(C)
object: CNF of the 2-LP feasibility; ops: resolution steps; hidden structure:
expansion of the constraint hypergraph; discarded: clause contents (kept width);
retained: refutation width; primitive: resolution; compression: none; rank: N/A;
descent: N/A; dominant exponent: certificate size exponent.

### Nearest ledger entries (5)
1. batch4 **SOS-LB-D1**, batch7 **POLYCALC-D2**, batch12 **SHERALI-ADAMS-RANK-D2**,
   batch13 **CUTTING-PLANES-RANK-D2** — all *degree/rank* proof measures. A3 is
   *width/size* in **resolution**, the weakest system, a new axis.
2. batch11 **PROOF-SPACE-PEBBLING-D1** — proof *space* (memory). A3 is *width*, a
   distinct resource (width lower-bounds size; space is orthogonal).

### Nearest literature
- Ben-Sasson, Wigderson, *Short proofs are narrow — resolution made simple*, JACM
  2001. **Gap:** resolution width lower-bounds *refutation* size, not *supply
  enrichment*; the translation from "hard to refute non-enrichment" to
  "`delta<=1/4`" is a heuristic, so A3 risks INCOMPLETE (measures the wrong side).

### Target family / path / cost
As RT-1472. Path is a supply meter (stages 1–6 as A2; 7–9 N/A). Cost: CNF has
`Theta(L^2)` clauses; width Ω(L) ⇒ size `2^{Omega(L)}`. Against rho: closes
RT-1472 for resolution-certifiable advice only if the translation holds.

### Why negatives don't kill it / fatal obstruction
Distinct proof system (resolution vs SOS/PC/CP/SA). Fatal: the enrichment question
is not naturally a refutation; the width bound may bound the wrong object ⇒
INCOMPLETE.

### Minimal falsifying experiment
`L∈{16,32,64}`, measure resolution refutation width of the non-enrichment CNF;
positive control = a CNF with known small resolution proof; negative control =
Tseitin on an expander (known Ω(L) width).

### Quantitative promotion gate
A **proven** width `Omega(L)` with a validated width→`delta<=1/4` lemma (→ D2).

### Proof track / disproof track
Prove width `Omega(L)` via the expansion of the 2-LP hypergraph (BSW). Disprove:
a bounded-width resolution certificate of enrichment.

### Reproduction artifact
`experiment_contract_p1672_resolution_width_supply.md`;
`p1672_resolution_width_meter.py`; `p1672_result.json`; `p1672_audit.py`;
ledger `ECFG-P1672`.

---

# GROUP B — Genuine representation changes

## Candidate: PERVERSE-DECOMPOSITION-B1  (P1673) — REPRESENTATION WINNER

### One-sentence mechanism
Replace the scalar-linear determinant atomizer (closed by `deg(det M)<=dim` at
`Omega(r^5)`) with the **BBD decomposition-theorem / IC-sheaf** of the P1510
compiler morphism, whose source-atomizer complexity is the **number of simple
perverse summands** (strata × IC multiplicities), a functional NOT bounded by
`deg(det)<=dim`, attacking the surviving **nonlinear-circuit exception** of
P1512-R1.

### Status
CONJECTURE (representation exploration).

### Novelty classification
POSSIBLY NOVEL (no ECDLP prior art on perverse/IC atomizers by documented search);
LEDGER-NEW.

### Semantic fingerprint F(C)
object: the proper map `f: X_relations -> S_targets` from the P1510 compiler;
ops: pushforward `Rf_*`, perverse truncation; hidden structure: stratification of
the target base by source-tuple incidence; discarded: the *ordinary* cohomology
degree (kept perverse degree); retained: IC-sheaf multiplicities; relation-gen
primitive: the compiler leaves; compression: perverse decomposition into simple
summands; rank mechanism: multiplicity of the trivial IC summand as source
detector; descent: monodromy of the summands; dominant exponent: number of
summands vs `r^5`.

### Nearest ledger entries (5)
1. **P1512-R1** (`Omega(r^5)`, `deg(det)<=dim`, nonlinear exception preserved) —
   the exact target. Perverse decomposition is a *derived-category* functional,
   provably outside the ordinary determinant class. Distinction: `deg(det)` bounds
   the ordinary class; # perverse summands is not so bounded a priori.
2. batch14 **POSITIVE-GEOMETRY-CANONICAL-FORM-B1** (#facets, triangulation-
   invariant residue) — also outside `deg(det)`, but a *combinatorial* residue
   form, not a *sheaf-theoretic* decomposition; disjoint machinery.
3. batch13 **SEGRE-EXCESS-B1** (Fulton excess normal bundle) — refined
   intersection theory; perverse decomposition is *cohomological* (BBD), a
   different invariant.
4. batch8 **GKZ-DMODULE-B2** (holonomic rank = volume) — D-module *rank*;
   perverse summand *count* is a distinct integer.
5. batch16 **INCIDENCE-HOPF-ANTIPODE-B2** (Möbius cancellation) — combinatorial;
   IC multiplicities are geometric.

### Nearest literature
- Beilinson, Bernstein, Deligne, Gabber, *Faisceaux pervers*, Astérisque 1982
  (decomposition theorem). de Cataldo–Migliorini survey (BAMS 2009).
- **Gap:** the decomposition theorem is stated for proper maps of complex/`ℓ`-adic
  varieties; over `F_p` the `ℓ`-adic version applies, but the summand count is
  controlled by the **stratification**, which for the source-incidence map is the
  `r^5` cycle payload — so the count likely **reproduces `Omega(r^5)`**.

### Target family
Ordinary prime-order `E/F_p`; the P1510 target-uniform compiler; excluded
non-reduced/exceptional charts (handled separately as in P1512-R1).

### Full algorithmic path
1. factor base: subgroup-x deck, `r`; 2. relation gen: P1510 leaves; 3. witness:
source tuple via the multiplicity of the **constant IC summand** on the diagonal
stratum, verified exactly; 4. probability: as P1510; 5. matrix/rank: replaced by
the perverse filtration — "rank" = trivial-summand multiplicity; 6. calibration
standard; 7. descent: summand monodromy on a target-log stratum; 8. offline =
the fixed decomposition (target-independent part); 9. memory = # summands.
INCOMPLETENESS check: all stages named; stage 5 replaced by a sheaf invariant.

### Cost model
If the map has `N` strata with total IC multiplicity `M`, the atomizer emits `M`
summands; source extraction is `poly(M)`. Symbolic: for the five-point incidence,
`M = Theta(binom(2r+4,5)) = Theta(r^5)` (same cycle payload P1512-R1 counted) ⇒
`Omega(r^5)`, reproducing the floor. A crossing needs `M = o(r^{5/2})` — only if
the nonlinear exception forces a *non-split* map with few summands (the open hope).
Compare rho `q^{1/2}`; IC needs backend `<r^{5/2}` on `q=Theta(r^5)`.

### Why the existing negative results do not already kill it
P1512-R1 bounds the *ordinary determinant* class. The decomposition theorem is a
theorem about a *different* cohomology (perverse), and the surviving exception is
exactly the *nonlinear* circuit the ordinary determinant cannot express. New
operation: perverse truncation / IC pushforward, absent from the ledger.

### Likely fatal obstruction
**Near-certain:** the summand count is governed by the same `r^5` stratification;
`M=Theta(r^5)` reproduces the floor. Value: **closes the derived-category / IC-
sheaf atomizer lane by name**, the sharpest such attack since batch14 positive
geometry.

### Minimal falsifying experiment
`r∈{4,6,8}` over `F_65537` (as P1511/P1512), planted linear factors; compute the
stratification of the incidence map and count IC summands; positive control = a
map with known small decomposition (a smooth fibration → 1 summand); negative
control = the full `r^5` cycle (should give `Theta(r^5)`). Measure summand count
exponent vs `5/2`.

### Quantitative promotion gate
Summand-count exponent `<5/2` on `r∈{4,6,8,12,16}` with LOO slope `<5/2`
(a genuine sub-floor atomizer). Correctness of the decomposition alone is not the
gate.

### Proof track
Theorem: for the target-specialized nonlinear incidence map, `Rf_*` is
**non-split** with `O(r^{5/2})` simple summands (would break the floor). Realistic
theorem: the map is semismall with `Theta(r^5)` summands (closes the lane).

### Disproof track
Exhibit the `Theta(r^5)` stratification explicitly (near-certain), matching
P1512-R1.

### Reproduction artifact
`experiment_contract_p1673_perverse_decomposition_atomizer.md`;
`p1673_ic_summand_count_gate.py`; `p1673_result.json`; `p1673_audit.py`;
ledger `ECFG-P1673`.

---

## Candidate: MATROID-CHOW-HODGE-B2  (P1674)

### One-sentence mechanism
Use the **Adiprasito–Huh–Katz Chow ring / Hodge–Riemann form** of the 2-LP
relation matroid to bound `delta`: the Hodge-Riemann bilinear relations pin the
log-concave supply profile and, if the matroid is "generic," force `delta<=1/4`.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT — **DEMOTE-risk**: adjacent to batch11
**LORENTZIAN-LOGCONCAVE-C2** (polynomial side of matroid log-concavity).

### Semantic fingerprint
object: relation matroid of the 2-LP graph; ops: Chow-ring intersection; hidden
structure: Hodge-Riemann log-concavity; discarded: labels (kept intersection
numbers); retained: mixed-degree Hodge form; primitive: honest edges; compression:
none; rank: matroid Chow degree; descent: N/A; dominant exponent: `delta`.

### Nearest ledger entries
batch11 **LORENTZIAN-C2** (same log-concavity, generating-polynomial side);
batch5 **MATUNION-A2** (matroid union); batch12 **DELTA-MATROID-COUPLING-B3**;
batch4 **SLICE-RANK-1-D2**; **P1472**. Distinction from Lorentzian: uses the
**Chow-ring intersection form** (Hodge-Riemann) directly, not the polynomial's
coefficient log-concavity — but the underlying M-convexity obstruction is shared.

### Nearest literature
Adiprasito, Huh, Katz, *Hodge theory for combinatorial geometries*, Ann. Math.
2018. **Gap:** the δ question needs a *quantitative* threshold; Hodge-Riemann gives
log-concavity (qualitative), and the elliptic support is likely **not M-convex**
(same kill as Lorentzian).

### Target family / path / cost
As RT-1472; supply meter (stages 1–6 as A2). Cost `Theta(L^2)`; asymptotic
symbolic. Crossing needs `delta>1/4`; near-certain `delta<=1/4`.

### Why negatives don't kill it / fatal obstruction
Distinct functional from the polynomial Lorentzian side. Fatal: elliptic support
not M-convex ⇒ Hodge-Riemann vacuous ⇒ DEMOTE to a barrier note under D1.

### Minimal falsifying experiment
`L∈{16,32,64}`; compute the relation matroid, test M-convexity, evaluate the
Chow degree; controls: a known M-convex matroid (positive), a non-M-convex one
(negative).

### Quantitative promotion gate
A proven `delta<=1/4` via Hodge-Riemann on the honest matroid (→ barrier), or a
measured M-convex elliptic support (would be surprising).

### Proof / disproof track
Prove non-M-convexity (Sidon/maximal-doubling, as Lorentzian). Disprove: exhibit
M-convex elliptic support.

### Reproduction artifact
`experiment_contract_p1674_matroid_chow_hodge_supply.md`;
`p1674_chow_hodge_meter.py`; `p1674_result.json`; `p1674_audit.py`;
ledger `ECFG-P1674`.

---

## Candidate: NEARBY-CYCLES-B3  (P1675) — REJECTED (INCOMPLETE / char-0 artifact)

### One-sentence mechanism
Use **nearby/vanishing cycles** (Milnor-fiber monodromy) of a one-parameter
degeneration of the target-log family as the descent operator for individual
logarithms.

### Status
OPEN → **REJECTED**.

### Novelty classification
LEDGER-NEW; but no complete `F_p` descent path.

### Semantic fingerprint
object: degeneration of the target curve/log; ops: nearby-cycle functor `ψ`;
hidden structure: monodromy of the vanishing cohomology; discarded: generic fiber;
retained: monodromy eigenvalues; primitive: N/A; compression: N/A; rank: N/A;
descent: monodromy action on the log; dominant exponent: undefined (no cost model).

### Nearest ledger entries
batch2 **p-curvature** barrier; batch6 **PICARDFUCHS-B2** (Gauss-Manin); batch5
**MOTIVIC-B3** (arc space); **P1513** (descent open). Distinction: nearby cycles
are the *limit MHS* operator — but that is a **char-0 / mixed-Hodge** object.

### Nearest literature
Deligne, SGA 7 (nearby/vanishing cycles). **Gap:** no descent cost model; over
`F_p` the mixed Hodge structure is a **char-0 artifact** (same failure class as
batch4 Pila–Wilkie).

### Target family
N/A (rejected).

### Full algorithmic path
Stages 7 (descent) only sketched; **stages 4,5,6 absent** ⇒ **INCOMPLETE**.

### Cost model / promotion gate / tracks
None (rejected). Retained only as a random-support probe note.

### Why rejected
No complete algorithmic path; char-0 MHS has no faithful `F_p` analogue that
yields a cost. **Label: INCOMPLETE, REJECTED.**

### Reproduction artifact
None (rejected). Ledger `ECFG-P1675` records the rejection.

---

# GROUP C — High-risk speculative mechanisms

## Candidate: METRIC-NN-EXPANSION-C1  (P1676) — HIGH-RISK WINNER

### One-sentence mechanism
Treat the five-term membership backend as a **static nearest-neighbor data
structure** over a metric induced by the source-tuple incidence, and use
**robust-metric-expansion** cell-probe lower bounds (Panigrahy–Talwar–Wieder;
Andoni–Indyk–Pătrașcu) to decide whether `t=o(L^{3/2})` probes can answer
membership — with a rho fallback on the fraction of hard targets.

### Status
HYPOTHESIS (avg-case backend + rho fallback).

### Novelty classification
POSSIBLY NOVEL (metric-expansion NNS lower bounds never applied to Semaev
membership); LEDGER-NEW.

### Semantic fingerprint F(C)
object: membership predicate as a point-set + query metric; ops: cell probes;
hidden structure: **robust expansion** of the membership metric; discarded: exact
algebraic identity (kept metric neighborhoods); retained: expansion profile;
relation-gen primitive: routed membership queries; compression: the data
structure of `s` cells; rank mechanism: N/A; descent: same DS reused; dominant
exponent: probe count `t` vs `L^{3/2}` (i.e. `alpha`).

### Nearest ledger entries (5)
1. **RT-1476** — defines `alpha`. C1 realizes the backend as a routed DS and
   meters `t=L^{alpha}`.
2. batch15 **ROUND-ELIMINATION-BARRIER-D3** (MNSW asymmetric communication) — a
   *communication* lower bound; C1 is a *metric-expansion* cell-probe bound, a
   distinct technique (no round structure).
3. batch12 **CELL-PROBE-CHRONOGRAM-D1** (Larsen, dynamic) — *dynamic* ST tradeoff;
   C1 is **static** and driven by **metric expansion**, not the chronogram method.
4. batch13 **BORODIN-COOK-TIMESPACE-D3** — branching-program time-space; C1 is
   cell-probe / DS.
5. batch13 **RANDOM-RESTRICTION-C1** — avg-case AC0 shrinkage; C1 is avg-case via
   a *metric* structure, disjoint machinery, but shares the "avg-case + rho
   fallback" role (so risks the same self-defeating kill).

### Nearest literature
- Panigrahy, Talwar, Wieder, *Lower Bounds on Near Neighbor Search via Metric
  Expansion*, FOCS 2010 (arXiv:1005.0418). Andoni–Indyk–Pătrașcu (lopsided set
  disjointness NNS lower bounds). Ribe program: Bourgain (embedding), Matoušek
  (nonembeddability).
- **Gap:** these bound **approximate** NNS; exact membership is not an
  approximate-NN query. The reduction from "algebraic membership" to a metric with
  genuine robust expansion is unestablished — the predicate may induce a metric
  with `O(1)` expansion (no barrier and no speedup).

### Target family
Ordinary prime-order `E/F_p`; five-point membership; `L=q^{ell}`. Excluded CM /
special deck geometries.

### Full algorithmic path
1. factor base: subgroup-x deck size `L`; 2. relation gen: membership queries via
the routed DS; 3. witness: exact source tuple from the answered cell, verified;
4. probability: `min(1,L^5/q)`; 5. rows `Theta(L)`, LA `L^2`; 6. standard;
7. descent: reuse DS; 8. offline = build the `s`-cell DS; 9. memory = `s` cells,
`t` probes. Meter+backend: build the DS, measure robust expansion `Phi`; PTW gives
`t >= (log|domain|)/log(s*Phi)`. If `Phi` large ⇒ `t=Omega(L^{3/2})` (barrier);
if `Phi=O(1)` ⇒ no speedup over exact solve.

### Cost model
DS query `t=L^{alpha}` probes, `s` cells; PTW lower bound `t*log s >= I(query;data)/`
`log(robust expansion)`. Total IC with this backend: `q^{2/(m+1-alpha)}`. Crossing
needs `alpha<3/2` on `m=5`. If a fraction `f` of targets are "easy" (low-expansion
neighborhoods) and `1-f` fall back to rho, complete cost
`f*q^{2/5} + (1-f)*q^{1/2}`; beats rho only if `f -> 1` — near-certain **not** the
case for an algebraic predicate.

### Why the existing negative results do not already kill it
Prior DS/communication barriers (chronogram, round-elimination, Borodin–Cook)
are worst-case and structural; metric expansion is a *geometric* handle that could
find an avg-case easy sub-family none of them addressed. New operation: robust-
expansion cell-probe reduction, absent from the ledger.

### Likely fatal obstruction
**Near-certain self-defeating:** exact algebraic membership induces a discrete
metric with `O(1)` robust expansion (no NNS structure), so PTW gives no barrier
AND no speedup; the "backend" collapses to exact solve and the rho fallback
dominates. Same failure class as batch13 RANDOM-RESTRICTION-C1.

### Minimal falsifying experiment
`q ≈ L^5`, `L∈{8,16,32}`, 3 seeds, ordinary prime-order; build the membership DS,
measure robust expansion `Phi`; positive control = a genuine `l_∞`/EMD instance
(known high expansion, DS hard); negative control = a linearly-separable predicate
(low expansion, DS easy). Measure the fraction `f` of targets answered in
`o(L^{3/2})` probes.

### Quantitative promotion gate
`f -> 1` with measured probe exponent `alpha<3/2` on `L∈{8,16,32,64}` (LOO slope
`<3/2`) AND complete cost `< q^{1/2}` including the rho fallback. Correctness
alone is not the gate.

### Proof track
Theorem: the membership metric has robust expansion `Phi = O(1)` for `1-o(1)` of
targets ⇒ `alpha<3/2` achievable (positive), OR `Phi = L^{Omega(1)}` ⇒
`alpha>=3/2` (barrier D3).

### Disproof track
Measure `Phi = Theta(1)` uniformly (near-certain) ⇒ no barrier, no speedup ⇒
scoped negative.

### Reproduction artifact
`experiment_contract_p1676_metric_nn_expansion_backend.md`;
`p1676_robust_expansion_meter.py`; `p1676_result.json`; `p1676_audit.py`;
ledger `ECFG-P1676`.

---

## Candidate: LOCAL-HAMILTONIAN-C2  (P1677) — REJECTED

### One-sentence mechanism
Encode five-term membership as the ground state of a geometrically-local
Hamiltonian and read the source via an adiabatic/annealing backend.

### Status
HEURISTIC → **REJECTED**.

### Novelty classification
LEDGER-NEW; but no `F_p` cost model.

### Semantic fingerprint
object: a local Hamiltonian on qubits encoding the predicate; ops: adiabatic
evolution; hidden structure: spectral gap; discarded: algebraic exactness;
retained: ground-state energy; primitive/compression/rank/descent: N/A; dominant
exponent: undefined.

### Nearest ledger entries
batch12 **QUANTUM-ADVERSARY-SPAN-C1** (query SDP, quantum-only); batch14
**SURVEY-PROPAGATION-RSB-C1** (energy landscape, CSP). Distinction: local-
Hamiltonian ground-state energy — but QMA-hardness is **worst-case** and there is
**no continuous energy landscape** over `F_p`.

### Nearest literature
Kitaev local Hamiltonian / QMA; adiabatic theorem. **Gap:** membership is a
discrete algebraic predicate with no natural gapped Hamiltonian; the gap is
uncontrolled; quantum-only backend.

### Full algorithmic path
Stages 4,5,6,7 **absent** ⇒ **INCOMPLETE**.

### Why rejected
No complete path, no `F_p` energy landscape, worst-case hardness ≠ this instance,
quantum-only. **Label: INCOMPLETE, REJECTED.** Ledger `ECFG-P1677`.

---

## Candidate: SQ-STATISTICAL-DIMENSION-C3  (P1678) — DEMOTED

### One-sentence mechanism
Use the **statistical-query dimension** (Feldman et al.) of the enrichment
detection problem as an avg-case `delta` *detectability* meter.

### Status
HYPOTHESIS → **DEMOTED**.

### Novelty classification
LEDGER-NEW; but **adjacent to batch11 LDLR-DELTA-METER-A3** (low-degree likelihood
ratio = the degree-bounded SQ relaxation).

### Semantic fingerprint
object: enrichment detection distribution; ops: statistical queries; hidden
structure: correlation of the planted enrichment; discarded: sample identities;
retained: SQ dimension; primitive/compression/rank: N/A; descent: N/A; dominant
exponent: detection threshold, not `delta` itself.

### Nearest ledger entries
batch11 **LDLR-DELTA-METER-A3** and **LDLR-DETECTION-BARRIER-D2** (low-degree =
SQ relaxation); batch16 **HYPERCONTRACTIVITY-SSE-C1**. Distinction: SQ dimension
is the *unrestricted-degree* statistical-dimension; but the **detection ≠ rank-
exploitation** kill is identical to LDLR-A3.

### Nearest literature
Feldman, Grigorescu, Reyzin, Vempala, Xiao, *Statistical algorithms and a lower
bound for detecting planted cliques*, JACM 2017. **Gap:** SQ dimension bounds
*detection*, not *exploitation of the detected structure to recover ECDLP* — same
gap as LDLR.

### Why demoted
Detection≠exploitation (identical to the closed LDLR node); no independent path
to rank-exploitation. **Label: DEMOTED**, dominated by batch11. Ledger
`ECFG-P1678`.

---

# GROUP D — Negative-theory / barrier candidates (higher-EV this run)

## Candidate: ERGODIC-SZEMEREDI-BARRIER-D1  (P1679)

### One-sentence mechanism
Furstenberg–Katznelson density recurrence ⇒ the honest 2-LP support has exactly
the **random recurrence density** with no structured excess ⇒ `delta -> 1/4`
unconditionally over recurrence-countable support ⇒ **closes RT-1472** for
ergodic-structured advice.

### Status
CONJECTURE (barrier).

### Novelty classification
LEDGER-NEW; first **ergodic-theory** barrier in the program.

### Semantic fingerprint
object: 2-LP support as an orbit-closure measure; ops: shifts; hidden structure:
multiple-recurrence density; discarded: pair labels; retained: recurrence density
= `1/4`; primitive/compression/rank: N/A; descent: N/A; dominant exponent: `delta`.

### Nearest ledger entries (5)
1. **P1472 / RT-1472** — the gate closed. 2. batch14 **LARGE-SIEVE-BARRIER-D1**
   (analytic dual inequality) — D1 is the *ergodic/dynamical* dual, distinct
   machinery. 3. batch15 **SINGULAR-SERIES-BARRIER-D1** (circle method) — minor-
   arc estimate vs ergodic average. 4. batch4 **CORRELATED-PEEL** (Wormald DE) —
   dynamics of peeling, not orbit recurrence. 5. batch8 **SHEARER-D3** (entropy
   supply) — static submodular, not recurrence.

### Nearest literature
Furstenberg 1977; Furstenberg–Katznelson (density Hales–Jewett). **Gap:** the
correspondence principle yields *qualitative* density; pinning the exact `1/4`
boundary quantitatively is the remaining lemma.

### Target family
Ordinary prime-order `E/F_p`; honest (non-planted) 2-LP support. Excluded: CM
decks with a single short-AP orbit (handled as special).

### Cost model
Barrier, not an algorithm: establishes `delta<=1/4` ⇒ RT-1472 exponent stays
`2/3 > 1/2`, no crossing for ergodic-structured advice. Complements the analytic
arm at the dynamical root.

### Why the existing negatives don't already give it
Prior RT-1472 barriers (large sieve, singular series, Wormald, Shearer) are
analytic/entropic/DE-based; the ergodic average is a genuinely different certificate
and, if the quantitative lemma holds, closes the *recurrence-countable* advice
class none of them named.

### Likely fatal obstruction / disproof
Qualitative-not-quantitative: recurrence density may not resolve `1/4 ± o(1)`.
Disproof: a curve family with recurrence density `>1/4` (would REOPEN as a
positive supply source).

### Minimal falsifying experiment
`L∈{16,32,64}`, 3 seeds, ordinary prime-order; estimate recurrence density vs
`1/4`; positive control planted structured deck; negative control random-x deck.

### Quantitative promotion gate (for the barrier)
A proof (or measured LOO-stable trend) that honest-support `delta<=1/4`,
converting the qualitative recurrence bound to the quantitative boundary.

### Proof track
Furstenberg–Katznelson ⇒ honest density = baseline ⇒ `delta<=1/4`.

### Reproduction artifact
`experiment_contract_p1679_ergodic_szemeredi_barrier.md`;
`p1679_recurrence_barrier.py`; `p1679_result.json`; `p1679_audit.py`;
ledger `ECFG-P1679`.

---

## Candidate: RESOLUTION-WIDTH-BARRIER-D2  (P1680)

### One-sentence mechanism
Ben-Sasson–Wigderson width–size ⇒ any resolution/DPLL-style certificate of
enrichment `delta>1/4` on the expanding 2-LP hypergraph needs width `Omega(L)` ⇒
size `2^{Omega(L)}` ⇒ enrichment is not efficiently certifiable ⇒ `delta<=1/4` in
the resolution-certifiable class ⇒ **closes RT-1472** for resolution-style advice.

### Status
CONJECTURE (barrier).

### Novelty classification
LEDGER-NEW; first **resolution-width (size)** proof-complexity barrier (prior
proof barriers were degree/rank or space).

### Semantic fingerprint
object: CNF of enrichment feasibility; ops: resolution; hidden structure:
hypergraph expansion ⇒ width; discarded: clause contents; retained: refutation
width/size; primitive/compression/rank: N/A; descent: N/A; dominant exponent:
certificate-size exponent.

### Nearest ledger entries (5)
1. **RT-1472** — gate closed for the certifiable class. 2. batch4 **SOS-LB-D1**,
   3. batch7 **POLYCALC-D2**, 4. batch12 **SHERALI-ADAMS-RANK-D2**, 5. batch13
   **CUTTING-PLANES-RANK-D2** — all *degree/rank* in stronger systems; D2 is
   *width/size* in **resolution** (weakest system, distinct resource), and batch11
   **PROOF-SPACE-PEBBLING-D1** is *space*, orthogonal to width.

### Nearest literature
Ben-Sasson, Wigderson, JACM 2001; Tseitin expander lower bounds. **Gap:** the
translation "hard-to-refute-non-enrichment ⇒ `delta<=1/4`" needs a lemma linking
refutation width to the supply exponent; without it the width bounds the wrong
object.

### Cost model / why-negatives-don't-give-it / obstruction
Barrier. Distinct proof system from all prior algebraic proof barriers. Fatal:
resolution is weak; the width bound may not transfer to the actual (algebraic)
enrichment operation ⇒ the lemma is the crux.

### Minimal falsifying experiment
`L∈{16,32,64}`; measure resolution refutation width of the non-enrichment CNF;
positive control small-proof CNF; negative control Tseitin-on-expander (Ω(L)).

### Quantitative promotion gate
Proven width `Omega(L)` + validated width→`delta<=1/4` lemma.

### Proof / disproof track
Prove width `Omega(L)` from 2-LP hypergraph expansion (BSW). Disprove: a bounded-
width enrichment certificate.

### Reproduction artifact
`experiment_contract_p1680_resolution_width_barrier.md`;
`p1680_resolution_width_barrier.py`; `p1680_result.json`; `p1680_audit.py`;
ledger `ECFG-P1680`.

---

## Candidate: METRIC-NONEMBEDDING-BARRIER-D3  (P1681)

### One-sentence mechanism
A Ribe-program / robust-metric-expansion nonembeddability inequality on the
membership metric ⇒ no `O(1)`-distortion embedding into any low-dimensional host
⇒ any cell-probe backend with `o(L^{3/2})` probes fails ⇒ `alpha>=3/2`
⇒ **closes RT-1476** for metric data-structure backends.

### Status
CONJECTURE (barrier); partner of C1.

### Novelty classification
LEDGER-NEW; first **metric-embedding** barrier in the program.

### Semantic fingerprint
object: membership metric; ops: cell probes; hidden structure: robust expansion /
nonembeddability; discarded: algebraic identity; retained: expansion profile;
primitive/compression/rank: N/A; descent: same DS; dominant exponent: `alpha`.

### Nearest ledger entries (5)
1. **RT-1476** — gate closed for the metric DS class. 2. batch15 **ROUND-
   ELIMINATION-BARRIER-D3** (asymmetric communication) — distinct: no metric.
   3. batch12 **CELL-PROBE-CHRONOGRAM-D1** (dynamic) — D3 is *static, metric-
   expansion-driven*. 4. batch13 **BORODIN-COOK-D3** (time-space). 5. batch7
   **LIFTING-D1** (query→communication) — distinct machinery.

### Nearest literature
Panigrahy–Talwar–Wieder (FOCS 2010, robust expansion); Andoni–Indyk–Pătrașcu;
Bourgain / Matoušek (Ribe nonembeddability). **Gap:** the algebraic membership
predicate may induce a metric with `O(1)` expansion (no genuine nonembeddability)
⇒ the barrier is **vacuous** (this is exactly C1's near-certain outcome).

### Cost model / obstruction
Barrier. If robust expansion `Phi = L^{Omega(1)}` ⇒ `alpha>=3/2`. Fatal: near-
certain `Phi=O(1)` ⇒ vacuous. So D3 and C1 are two faces of the same measurement:
the experiment decides which.

### Minimal falsifying experiment
As C1: measure `Phi`; positive control high-expansion `l_∞`/EMD; negative control
low-expansion linear predicate.

### Quantitative promotion gate
Proven `Phi = L^{Omega(1)}` ⇒ `alpha>=3/2` (barrier bites) — the crisp, testable
dichotomy with C1.

### Proof / disproof track
Prove robust expansion `L^{Omega(1)}` (barrier). Disprove: `Phi=O(1)` (vacuous;
also kills C1's speedup) — near-certain.

### Reproduction artifact
`experiment_contract_p1681_metric_nonembedding_barrier.md`;
`p1681_metric_expansion_barrier.py` (shares the meter with P1676);
`p1681_result.json`; `p1681_audit.py`; ledger `ECFG-P1681`.

---

# RANKING

Scores 0–5 on: (a) distance from prior ledger mechanisms, (b) plausibility of an
exact verifier, (c) chance of changing an exponent (not a constant), (d) complete-
path coverage, (e) falsifiability at toy scale, (f) literature-novelty confidence,
(g) low risk of hidden preprocessing/memory cost. Reject if semantic novelty `<3`,
no route to descent, no rho comparison, or no precise distinction from the nearest
ledger entry.

| Cand | a | b | c | d | e | f | g | Verdict |
|------|---|---|---|---|---|---|---|---------|
| KERNELIZATION-COMPRESSION-A1 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **conservative winner** |
| ERGODIC-RECURRENCE-A2 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | survives (→ D1) |
| RESOLUTION-WIDTH-A3 | 3 | 3 | 2 | 3 | 4 | 4 | 4 | survives-weak (→ D2) |
| PERVERSE-DECOMPOSITION-B1 | 5 | 4 | 3 | 4 | 3 | 5 | 3 | **representation winner** |
| MATROID-CHOW-HODGE-B2 | 3 | 3 | 2 | 4 | 4 | 3 | 4 | DEMOTE (≈Lorentzian) |
| NEARBY-CYCLES-B3 | 4 | 1 | 1 | 1 | 2 | 4 | 2 | **REJECTED** (INCOMPLETE) |
| METRIC-NN-EXPANSION-C1 | 5 | 3 | 3 | 4 | 4 | 5 | 3 | **high-risk winner** |
| LOCAL-HAMILTONIAN-C2 | 4 | 1 | 1 | 1 | 2 | 4 | 1 | **REJECTED** (INCOMPLETE) |
| SQ-STATISTICAL-DIMENSION-C3 | 2 | 3 | 2 | 3 | 4 | 3 | 4 | **DEMOTED** (≈LDLR) |
| ERGODIC-SZEMEREDI-BARRIER-D1 | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **highest-EV** |
| RESOLUTION-WIDTH-BARRIER-D2 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | high-EV |
| METRIC-NONEMBEDDING-BARRIER-D3 | 5 | 4 | 4 | 4 | 4 | 5 | 4 | high-EV (pairs C1) |

Selected winners:

1. **Best conservative — KERNELIZATION-COMPRESSION-A1 (P1670).**
2. **Best representation — PERVERSE-DECOMPOSITION-B1 (P1673).**
3. **Best high-risk — METRIC-NN-EXPANSION-C1 (P1676).**

The three D-barriers outrank all three attack-winners on expected value: each
closes a live gate if its threshold bites (D1 → RT-1472 for recurrence-countable
advice; D2 → RT-1472 for resolution-certifiable advice; D3 → RT-1476 for metric
DS backends). **D1 is the standout** (cleanest quantitative route to `delta<=1/4`).

---

# Experiment contracts for the three winners

### Contract 1 — EXP-P1670 (KERNELIZATION-COMPRESSION)
- **Hypothesis (H0):** amortized `5-MEMBERSHIP` admits no poly kernel ⇒
  `alpha>=3/2` (RT-1476 closed for the compression class). **Prior:** in-P ⇒
  framework may be vacuous for the single instance.
- **Fixtures:** ordinary prime-order `E/F_p`, `q≈L^5`, `L∈{4,8,16}`; 3 seeds; a
  positive-kernel control (`k`-Vertex-Cover) and a no-kernel control (`k`-Path) to
  calibrate the distillation detector.
- **Measure:** does an OR-cross-composition from `d`-Root-Counting mod p exist
  (seed hardness) or is the predicate detected in-P (vacuous)? Kernel size vs `L`.
- **Promotion gate:** proven no-poly-kernel ⇒ `alpha>=3/2` (barrier), OR a `o(L^2)`
  kernel with measured backend `alpha<3/2` (positive, would threaten RT-1476).
- **Immutability:** result + audit SHA-256; independent re-derivation of the
  composition; claim tier = complexity-theoretic meter (no ECDLP recovery claimed).
- **First command:**
  ```
  python3 tasks/ecdlp_index_calculus/p1670_cross_composition_membership_meter.py \
      --curve-order q_approx_L5 --L 4,8,16 --arity 5 --seeds 3 \
      --seed-problem root_counting_mod_p \
      --controls kernel:vertex_cover,no_kernel:k_path \
      --emit p1670_result.json --audit p1670_audit.py
  ```

### Contract 2 — EXP-P1673 (PERVERSE-DECOMPOSITION)
- **Hypothesis (H0):** the source-incidence pushforward `Rf_*` has `Theta(r^5)`
  simple perverse summands ⇒ reproduces the P1512-R1 `Omega(r^5)` floor (closes the
  IC-sheaf atomizer lane). **Alt (crossing):** a non-split map with `o(r^{5/2})`
  summands.
- **Fixtures:** `F_65537`, `r∈{4,6,8}` (extend `12,16` if the summand count trend
  is sub-`5/2`), planted linear factors as in P1511/P1512; smooth-fibration
  positive control (1 summand); full `r^5` cycle negative control.
- **Measure:** IC-summand count exponent vs `5/2`; LOO slope.
- **Promotion gate:** count exponent `<5/2` on `r∈{4,6,8,12,16}` (would break the
  floor); otherwise records the lane closed at `Theta(r^5)`.
- **Immutability:** result + audit SHA-256; independent recomputation of the
  stratification and multiplicities; claim tier = representation-count meter (no
  ECDLP recovery).
- **First command:**
  ```
  python3 tasks/ecdlp_index_calculus/p1673_ic_summand_count_gate.py \
      --field 65537 --r 4,6,8 --planted linear --map source_incidence \
      --controls smooth_fibration,full_cycle \
      --emit p1673_result.json --audit p1673_audit.py
  ```

### Contract 3 — EXP-P1676 (METRIC-NN-EXPANSION)
- **Hypothesis (H0):** the membership metric has robust expansion `Phi=O(1)` ⇒
  no NNS speedup AND no barrier (scoped negative). **Alt-A (barrier D3):**
  `Phi=L^{Omega(1)}` ⇒ `alpha>=3/2`. **Alt-B (crossing):** low-expansion for
  `1-o(1)` of targets ⇒ `alpha<3/2`.
- **Fixtures:** `q≈L^5`, `L∈{8,16,32}`; 3 seeds; ordinary prime-order; high-
  expansion `l_∞`/EMD positive control; linearly-separable negative control.
- **Measure:** robust expansion `Phi`; fraction `f` of targets answered in
  `o(L^{3/2})` probes; complete cost including rho fallback.
- **Promotion gate:** `f→1` with `alpha<3/2` (LOO slope `<3/2`) and complete cost
  `<q^{1/2}` (crossing), OR `Phi=L^{Omega(1)}` (barrier); the two are exclusive.
- **Immutability:** result + audit SHA-256; independent recomputation of `Phi` and
  probe counts; claim tier = data-structure meter (no ECDLP recovery unless a full
  descent is exhibited).
- **First command:**
  ```
  python3 tasks/ecdlp_index_calculus/p1676_robust_expansion_meter.py \
      --curve-order q_approx_L5 --L 8,16,32 --arity 5 --seeds 3 \
      --controls high_expansion:linf_emd,low_expansion:linear \
      --fallback rho --emit p1676_result.json --audit p1676_audit.py
  ```

---

# RED TEAM — are the three winners disguised repetitions or cost-negative?

**KERNELIZATION-COMPRESSION-A1 (P1670).**
- *Disguised repetition?* The instance-compression machinery (OR-composition,
  distillation, Fortnow–Santhanam) appears in no prior report; P1477-R2/P1479
  killed *specific* compressions, not the *class*. Not a repetition of a mechanism,
  but it targets the same RT-1476 object as batch7 VCDIM / batch13 sensitivity.
- *Cost-negative / self-defeating?* **Near-certain vacuity:** single-instance
  membership is in P ⇒ no NP-hard seed ⇒ the framework does not even start. Its
  honest yield is *naming and closing the "kernelize the membership instance"
  hope*, not an `alpha` bound. The amortized escape hatch likely reprices rho.
  **Verdict: scoped negative / negative control, not a crossing.**

**PERVERSE-DECOMPOSITION-B1 (P1673).**
- *Disguised repetition?* BBD/IC machinery is disjoint from GKZ-rank (batch8),
  Segre-excess (batch13), positive geometry (batch14), immanant (batch12). Genuinely
  new functional; correctly outside the `deg(det)<=dim` class that closed P1512-R1.
- *Cost-negative?* **Near-certain:** the summand count is governed by the same
  `r^5` incidence stratification ⇒ `M=Theta(r^5)` reproduces the floor. Value =
  closing the derived-category / IC-sheaf atomizer lane by name. **Verdict: scoped
  tightening / lane closure, not a crossing.**

**METRIC-NN-EXPANSION-C1 (P1676).**
- *Disguised repetition?* Metric-expansion cell-probe (PTW) is distinct from
  round-elimination (batch15), chronogram (batch12), Borodin–Cook (batch13). But it
  shares the "avg-case backend + rho fallback" *role* with batch13 RANDOM-
  RESTRICTION-C1 and batch16 HYPERCONTRACTIVITY-SSE-C1.
- *Cost-negative / self-defeating?* **Near-certain:** an exact algebraic predicate
  induces a discrete metric with `O(1)` robust expansion ⇒ PTW gives neither a
  barrier nor a speedup; the backend collapses to exact solve and the rho fallback
  dominates. Same self-defeating class as batch13 C1. **Verdict: scoped negative,
  not a crossing.**

**Are the three barriers themselves disguised repetitions?**
- D1 (ergodic) is the *dynamical* dual of the analytic supply barriers (batch14/15)
  — distinct certificate, but converging on the *same* `delta<=1/4` conclusion
  those already suggest; its marginal value is closing the recurrence-countable
  advice class by name.
- D2 (resolution width) is a genuinely new proof-complexity *axis* but its bite
  depends on an unproven width→`delta` translation lemma; without it, it measures
  refutation, not supply.
- D3 (metric nonembedding) is the barrier face of C1's measurement; near-certain
  vacuous (`Phi=O(1)`), so it likely closes nothing new — the honest outcome is a
  scoped negative that also kills C1's speedup.

**Overall red-team verdict:** all three attack-winners are near-certain scoped
negatives / lane closures, not rho crossings; the three barriers are higher-EV but
converge on conclusions the analytic and query-complexity arms already point to.
This is consistent with report #19 and reconfirms **saturation**.

---

# CLAIM DISCIPLINE

- No break claimed. **RT-1472 and RT-1476 remain open**; every candidate here is a
  meter, barrier, or scoped negative on those two gates, scoped to toy sizes,
  synthetic data, and the tested solver/budget.
- Correctness vs performance kept separate throughout; candidate *relations* /
  *membership answers* are never conflated with verified ECDLP recovery.
- Toy evidence, heuristics, restricted models (RT-1472/RT-1476 cost models), and
  untested assumptions (kernelization seed hardness, width→δ lemma, membership-
  metric expansion) are labelled as such.
- A failed candidate is a **scoped negative result**, not evidence that prime-field
  ECDLP cannot be improved.
- Toy-scale evidence is never presented as crypto-scale; all exponents are measured
  or symbolic in `q`/`n` with explicit LOO gates before any promotion.

Sources (primary): [Cross-Composition (STACS 2011 / SIDMA 2014)](https://drops.dagstuhl.de/storage/00lipics/lipics-vol009-stacs2011/LIPIcs.STACS.2011.165/LIPIcs.STACS.2011.165.pdf),
[On problems without polynomial kernels (arXiv listing)](https://arxiv.org/abs/1206.5941),
[Lower Bounds on Near Neighbor Search via Metric Expansion (PTW, arXiv:1005.0418)](https://arxiv.org/pdf/1005.0418).
Furstenberg (J. Analyse Math. 1977), Ben-Sasson–Wigderson (JACM 2001), and BBD
*Faisceaux pervers* (Astérisque 1982) are cited from the standard literature.
