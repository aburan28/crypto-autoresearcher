# Idea Generation — 2026-07-18 batch5 (Research Director)

Mechanism-new candidates vs the full ledger **and** all six prior idea reports
(`20260717`, `20260717_batch2`, `20260718`, `20260718_batch2`, `20260718_batch3`,
`20260718_batch4`). This is the **seventh** report; batch4 already declared the six
task-brief search seeds exhausted and went outside them (P1514–P1525). Batch5 targets
the **two live rho-crossing gates** and the **one surviving representation frontier**
identified by the prior reports, using measurement primitives and objects that are
absent from every prior candidate.

Authorized scope: generated toy curves, public benchmark instances, synthetic data
only. No wallets/keys/accounts.

---

## 0. Input review and machine-readable inventory

### Sources read
- `/Volumes/Volume/git/autolab/research_ledger.md` (2,478 lines): frontier questions
  (§Open frontier), 560 `H-*` hypotheses, 731 `NR-*` negative results, 8,497 `P####`
  positive-signal IDs, 7 `RT-*` conditional rho-crossing theorems, baselines, literature
  map, negative controls.
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (720
  lines): IC-state frontier **P1509–P1513** (IDEA-068 Hasse-jet source-section chain;
  marked-resultant / DB-join lower bounds; scalar-linear Chow atomizer closed at
  `Ω(r^5)` = P1512-R1, **only the nonlinear-circuit exception open**).
- `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (389
  lines) + the PO-transfer-001..006 closeouts: same-field isogeny closed; scalar
  Weil/Kummer diagnostic-only; twist = positive control (adjacent, not a subgroup
  break); fixed-degree unramified affine cofiber multiplicity closed; next open =
  cyclic-cover norm label with a *measured label-conditioned factorization advantage*.
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json`
  (10 entries: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013; FHJRV 2014
  symmetrized; Kousidis–Wiemers 2015 first-fall; Karabina 2015; Amadori–Pintore–Sala
  2017; McGuire–Müller 2017 Gröbner-free; Trimoska–Ionica–Dequen 2020 SAT).
- All six prior idea reports (72 candidate blocks).

### ID families covered
`RQ-*, IDEA-*, H-* (560), NR-* (731), P#### (≤P1486 committed; P1509–P1513 IC-state;
P1514–P1525 proposed in batch4), PO*/PO96* transfer series, RT-1471..1486, EV-*, DEC-*,
MX-1478`. Prior-report proposal IDs span `A1/A2/A3, B1..B4, C1..C3, D1..D3` in six
reports plus the batch4 named lane `SOS/APOLARITY/CORRELATED/GENJAC/SYZYGY/SIGNRANK/
GROWTH/PILA/SANDPILE/SOS-LB/SLICE-RANK/LINLABEL` (P1514–P1525).

### The only two live rho-crossing surfaces (verbatim from the ledger)
- **RT-1472** — two-large-prime graph at `B=n^{1/5}`: exact cost exponent
  `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)`, min `2/3` at `ℓ=1/3`; **crossing rho requires explicit
  advice enrichment `δ>1/4`**, else an implicit deck needs setup `o(L)` and query
  `o(√L)`.
- **RT-1476** — m-ary implicit membership backend: `ℓ=1/(m+1−α)`, total `2/(m+1−α)`
  for `α≤1`; `m≤3` has no sub-rho `α`, `m=4` needs `α<1`, **`m=5` needs `α<3/2`**. At
  `m=5, α=1`: relations and sparse LA are `q^{2/5}`, descent `q^{1/5}`.

**Load-bearing fact (confirmed against the ledger):** the sparse-linear-algebra stage
(`n^{2/5}`) is **not** binding. The binding stages are (i) **relation/membership
generation** (RT-1476 α, RT-1472 δ) and (ii) an almost-always-unmetered
**individual-log descent** exponent. Every prior "below rho" is amortized-many-target
or setup-uncharged. The surviving *representation* frontier is
**LINLABEL-UNIFIED-D3** (batch4/P1525): all `F_p`-**linear** target labels have marginal
rank `o(B)` or compiler cost `Ω(r^5)`; **only genuinely nonlinear labels can escape.**

### Anti-duplication catalogue (60+ consumed mechanism lanes, do not re-propose)
Report1: BKK/mixed-volume; EDS/elliptic-net smoothness; incidence-reporting backend;
nilpotent-jet/dual-number; tensor-train/separator-rank; tropical/p-adic valuation
descent; noncommutative CM quiver/groupoid; Lattès transfer-operator; Xedni
height-lattice. Report2: 3-LP hypergraph homology; NFS two-sided coincidence;
transposed Kedlaya–Umans amortization; Kani-torsion RM genus-2; Serre–Tate canonical
lift; Riemann-bilinear theta; representation-technique MITM; p-curvature holonomy;
character-sum bias. Report3: sparse-interpolation Prony/Ben-Or–Tiwari; Sidon/B_h
design; list-decoding Guruswami–Sudan; Cartier–Manin; discrete-Fourier dual-group;
Semaev border rank; approximate-homomorphism Bogolyubov–Ruzsa; Kloosterman importance
sampling; CM ideal-factorization class group. Report4: subresultant-PRS α-meter;
graphic-matroid cycle basis; many-target amortization; modular/Hecke; Drinfeld module;
Ritt/Dickson decomposition; non-backtracking isogeny walk; Pink–Zilber; Coleman–Gross
height pairing. Report5: displacement/Toeplitz-Bézoutian; effective-resistance
sparsifier; composed-resultant power-sum Prony-pencil; Heisenberg/theta Schrödinger–Weil;
Weil–Châtelet m-descent; Berkovich skeleton; holographic/matchgate; higher-order-Fourier
nilsequence; orthogonal-lattice Nguyen–Stern; sum-product energy ceiling; finite-field
collapse; Cai–Lu Holant. Report6 (batch4): SOS/Lasserre; apolarity/Waring atomizer;
correlated-peel Wormald DE 2-core; generalized-Jacobian modulus; syzygy/Betti resolution;
sign-rank/γ2; growth SL2; Pila–Wilkie o-minimal; sandpile critical group; SOS-LB;
slice-rank; linlabel-unified.

**Batch5 avoids every lane above.** New primitives introduced here: transposed
**power projection** (dual of modular composition), **matroid union / Nash-Williams
tree-packing**, **descent-tree branching-exponent** metering, **Mahler/automatic-sequence**
representation, **Fourier–Mukai** nonlinear kernel labels, **motivic/arc-space**
measure, **arboreal Galois** iterated-monodromy, **Cohen–Lenstra** volcano bias, **free
probability**, and the **asymptotic spectrum of tensors** (Strassen) barrier.

---

## 1. Candidates

Fingerprint tuple `F(C) = (algebraic object, public operations, hidden structure,
info discarded, info retained, relation-gen primitive, compression primitive, rank
mechanism, descent mechanism, dominant cost exponent)`.

---

## Candidate: POWERPROJ-A1 — Transposed power-projection membership α-meter (RT-1476)

### One-sentence mechanism
Exploit the **trace/dual side** of the backward-3-sum quotient algebra: certify implicit
five-point membership by matching the target's **Newton power-sum signature** computed
via Bostan–Schost **power projection** (the transpose of modular composition), reducing
the membership-query exponent `α` toward the `α<3/2` that RT-1476 proves beats rho —
without ever materializing the eliminant.

### Status
HYPOTHESIS (α is measurable; the theorem it feeds, RT-1476, is proven).

### Novelty classification
LITERATURE-ADJACENT (power projection is classical; its use as a *membership certifier*
for Semaev backward-state is new, and it measures a **different quantity** from
batch4/A1's subresultant-degree meter).

### Semantic fingerprint
- object: quotient algebra `A = F_p[u]/I`, `I = ⟨S3(x1,x2,u)⟩ ∩ backward S4(u,x3,x4,x5)`.
- public ops: field ops; the linear map "multiply-by-target-coordinate" `M_t` on `A`.
- hidden structure: **membership is decided by the power-sum vector `(Tr(M_t^i))_{i<r}`
  with `r = dim A` bounded by Bézout / RT-1485 fiber count**, not by eliminant degree.
- discarded: the eliminant polynomial (never formed).
- retained: `O(r)` power sums / traces (a *dual* object).
- relation-gen primitive: for each backward tuple, apply power projection `ℓ∘M_t^i`
  (Shoup transposition principle) at cost `O(M(d) log d)` per projection.
- compression primitive: **transposition principle** — compute linear forms of roots,
  not the roots' symmetric functions.
- rank mechanism: `Θ(L)` sparse rows over `Z/n` (unchanged; not binding).
- descent: same power-projection backend on `T+[r]P` (see A3 for its exponent).
- dominant cost exponent: `α := log_L(#power sums needed to certify) · (proj cost exp)`.

### Nearest ledger / report entries
1. **batch2/A1 subresultant-PRS** (RT-1476-SUBRES): measures the **degree of the first
   nonzero subresultant** (a *primal* remainder-sequence quantity). POWERPROJ measures the
   **number of independent traces to disambiguate membership** (a *dual* quantity bounded
   by the solution count, not the solution spread). Sharp distinction: an ideal can have
   a high-degree eliminant yet `O(1)` solutions — subresultant sees `β≈1`, power projection
   can still see `α=O(1)`. This is why the subresultant negative would **not** kill it.
2. **batch2/A3 transposed Kedlaya–Umans**: KU is *forward* fast evaluation; power
   projection is its literal transpose (dual). KU bounds evaluation; power projection
   bounds *linear forms of roots* — a different cost quantity.
3. **RT-1476 / P1477**: the theorem and its "non-materializing backward representation
   with exponent <1.5" request; POWERPROJ is a concrete, falsifiable instantiation.
4. **RT-1485** (Kummer companion, constant fibers `≤4`, support `D(D+2)/4`): direct
   evidence the solution count `r` is small — exactly the quantity power projection is
   sensitive to. This is the strongest prior that `α` could be `O(1)`.
5. **batch3/A3 composed-resultant power-sum Prony-pencil**: uses power sums of a
   *C-finite recurrence* oracle to reconstruct a common root by Prony; POWERPROJ uses
   power sums of the *quotient-algebra multiplication operator* as a membership *decision*
   — different source of the power sums (multiplication trace vs recurrence), different
   output (yes/no membership vs root value).

### Nearest literature
Bostan–Salvy–Schost (power projection / fast modular composition, 2003–08); Shoup
(transposition principle, 1994/1999); von zur Gathen–Gerhard (Newton's identities);
Kedlaya–Umans 2011. None applies power projection to Semaev/point-decomposition
membership. Gap: no primary source measures the trace-side query exponent for the m=5
prime-field backward state. *(literature note appended below)*

### Target family
Ordinary prime-field `E/F_p`, prime order `n`, `j∉{0,1728}`, non-anomalous, large
embedding degree. Excluded: binary/extension, singular/supersingular/anomalous, CM
special orders.

### Full algorithmic path
1. Factor base `L=q^ℓ` on the line (RT-1476 model). 2. Forward `S3(x1,x2,u)` root table;
build `A` and `M_t` for each backward triple. 3. Witness: matching power-sum signature
⇒ shared `u`; verify full `S5=0` by O(1) evaluation. 4. Relation prob `min(1,L^5/q)`.
5. `Θ(L)` sparse rows, density `O(1/L)`. 6. Standard IC calibration. 7. Descent: same
backend (metered by A3). 8. Offline: forward table + LA per curve; online: descent per
target. 9. Memory: forward table `O(L^2)` (streamable with distinguished-`u`); power
projections embarrassingly parallel.

### Cost model
RT-1476: total `2/(m+1−α)`; m=5 sub-rho iff `α<3/2`. If certifying membership needs
`r_eff = Θ(q^{β'})` traces at `O(M(d)log d)` each, `α ≈ β' + o(1)`. **Falsifiable
prediction:** if `r_eff = O(1)` (constant solution count, as RT-1485 hints for the
companion state), `α→1` and m=5 lands at total exponent `2/5 < 1/2` **for relations and
LA** — but only if descent (A3) also stays `≤q^{1/5}`. Compare vs rho `0.886 q^{1/2}`,
BSGS `q^{1/2}`, Gaudry–Diem prime-field IC (no sub-rho known).

### Why existing negatives do not already kill it
Closed control: "dense composed resultants" and "materialized serial-S3 backward
states." Power projection forms **neither** the eliminant nor the backward state; it
reads a dual trace stream whose length is governed by the **solution count**, a quantity
the subresultant meter is blind to. New operation = Shoup transposition of
multiplication-by-target.

### Likely fatal obstruction
The multiplication operator `M_t` on the *generic* backward algebra has degree `Θ(q)`
(Bézout), so even the *dual* stream may need `Θ(q)` traces ⇒ `α≥1` and no window unless
the RT-1485 fiber-collapse is generic rather than Kummer-special. Second risk: computing
`M_t` itself may cost `Θ(deg)` field ops, hiding the exponent in setup.

### Minimal falsifying experiment
Toy `p∈{1009, 65521, 16769023}`, ordinary prime-order curves, 3 seeds each. Build the
serial-S3 split; for random backward triples, compute `dim A` and the **number of power
sums needed to separate a member from a non-member** as a function of `q`. Positive
control: a curve with known constant fibers (Kummer-companion fixture from RT-1485).
Negative control: a random dense trivariate system of equal total degree (expect
`r_eff=Θ(q)`). Fit `β' = d log(r_eff)/d log q`.

### Quantitative promotion gate
`β' < 0.3` across all three sizes, flat/declining, **and** A3's descent exponent
`≤1/5` ⇒ promote to a costed collector. `β' ≥ 0.3` ⇒ scoped NEGATIVE closing the
trace-side backend for RT-1476 (complements the subresultant negative).

### Proof track
Theorem: *the backward-3-sum quotient algebra `A` has `dim_{F_p} A = O(q^{β'})` with
`β'<3/10`, and its multiplication-by-target operator is certifiable by `O(dim A)` power
projections.* Would follow from a mixed-volume / RT-1485-style fiber-count bound on the
solution set (mixed volume as **analysis**, not as the BKK **algorithm**).

### Disproof track
Exhibit an ordinary family where `dim A = Θ(q)` (generic Bézout) with no fiber collapse
⇒ `β'=1`.

### Reproduction artifact
Contract `research/EXP_POWERPROJ_A1_contract.md`; impl
`experiments/ecdlp_prime_field/powerproj_alpha_meter.sage`; result
`powerproj_alpha.json`; audit `powerproj_audit.py`; ledger **P1526 / RT-1476-POWERPROJ-A1**.

---

## Candidate: MATUNION-A2 — Nash-Williams matroid-union large-prime enrichment (RT-1472)

### One-sentence mechanism
Exploit **two independent** two-large-prime advice graphs by taking their **matroid
union**: Nash-Williams tree-packing predicts the combined spanning-forest count, which
can exceed either graph's own subcritical cycle rank and reach enrichment `δ>1/4`.

### Status
HYPOTHESIS.

### Novelty classification
POSSIBLY NOVEL (matroid union / Nash-Williams is classical, but a literature check found
**no prior** applying matroid-union / tree-packing to large-prime relation enrichment;
existing 2-LP combination is birthday/2-core/cycle-counting based, not base-packing based).
Caveat: the yield claim needs a model linking packing number to relation count.

### Semantic fingerprint
- object: two graphs `G1, G2` (large primes = vertices; partial relations = edges) from
  two disjoint factor-base halves / two coordinate charts; matroid `M = M(G1)∨M(G2)`.
- public ops: partial-relation generation with ≤2 large primes on each chart; graph algs.
- hidden structure: **cross-graph cycles** — a base of `M(G1)∨M(G2)` can pack more
  independent relations than `rank M(G1)+rank M(G2)` bounded separately would suggest.
- discarded: edges not on any packed forest.
- retained: a Nash-Williams-optimal forest packing spanning the joint relation lattice.
- relation-gen primitive: two-large-prime birthday on each chart.
- compression primitive: **matroid union rank** via Nash-Williams
  `min_{X} (|E\X| + Σ_i rank_i(X))`.
- rank mechanism: joint packing number = effective relation count = `δ`.
- descent: special-q on a target large prime.
- dominant cost exponent: RT-1472 `max(2ℓ,1−ℓ,1+1/5−2ℓ)`, improved iff `δ>1/4`.

### Nearest ledger / report entries
1. **batch2/A2 graphic-matroid cycle basis** (single graph): capped by its own 2-core;
   MATUNION is the **union of two matroids**, a strictly larger object whose rank is
   given by Nash-Williams, not by one cycle space.
2. **batch2/A1 3-LP hypergraph homology**: simplicial homology of one 3-uniform
   hypergraph; MATUNION is two 2-uniform graphs combined — different chain complex.
3. **batch3/A2 effective-resistance sparsifier**: *reduces* edges preserving cuts;
   MATUNION *combines* two edge sets to add cross relations — opposite direction.
4. **batch4/A3 correlated-peel Wormald DE 2-core**: measures the 2-core threshold of
   *one dependent* sum-graph; MATUNION asks whether *two* graphs' union crosses the
   threshold even when each alone is subcritical.
5. **report2/A2 NFS two-sided**: two factor bases giving *coincidence* relations (a
   relation is a pair matched on both sides); MATUNION uses two graphs for *forest
   packing*, not two-sided coincidence — different use of "two sides."

### Nearest literature
Nash-Williams 1961 (forest packing); Edmonds (matroid union); Fouque–Joux–et al. and
Cavallar (large-prime variations in NFS/index calculus). No source applies matroid
union to LP enrichment. *(literature note appended.)*

### Target family
As RT-1472: `B=n^{1/5}`, ordinary prime-field prime-order.

### Full algorithmic path
1. Two factor-base charts, each `Θ(L^2)` pair-advice. 2. Generate ≤2-LP partials per
   chart. 3. Witness: a packed forest edge = a certified partial; a fundamental cycle =
   a full relation. 4. Relation prob per chart as RT-1472. 5. `Θ(L)` sparse rows.
   6. Standard calibration. 7. Special-q descent. 8. Offline packing; online descent.
   9. Memory `Θ(L^2)` advice (both charts), streamable.

### Cost model
RT-1472 exponent improves iff the union packing yields `δ>1/4` **at the same advice
budget** `Θ(L^2)`. **Falsifiable:** measure `δ = log_L(#independent relations) − log_L(L)`
for one graph vs the union. Compare vs rho / RT-1472 baseline `2/3`.

### Why existing negatives do not already kill it
The measured obstruction (batch2/A2, batch4/A3) is that a **single** honest summation
graph is a.a.s. **subcritical** (`δ=0`). Matroid union is the one operation that can
lift two subcritical structures above threshold **if they are independent**. New
operation = Nash-Williams packing across two charts.

### Likely fatal obstruction (→ D2)
The two charts share the **same curve addition law**, so `G1, G2` are **not
independent**: `rank(M(G1)∨M(G2)) − rank M(G1) = o(|V|)`, leaving `δ≤1/4`. This is
exactly the barrier D2 is designed to prove.

### Minimal falsifying experiment
Toy `p∈{1009, 65521, 16769023}`; build two disjoint-chart LP graphs (3 seeds); compute
single-graph cycle rank and the Nash-Williams union packing number; fit `δ`. Positive
control: two *artificially independent* random graphs (should show union lift). Negative
control: two charts of the *same* curve (expect no lift — the D2 prediction).

### Quantitative promotion gate
Honest two-chart union `δ>1/4` on all three sizes ⇒ promote. `δ≤1/4` (or lift only for
the artificial-independence control) ⇒ scoped NEGATIVE feeding D2.

### Proof / disproof track
Proof (positive): a two-chart construction with certified matroid independence and
union rank `> (5/4)L`. Disproof (→D2): independence deficiency
`corank(M(G1)∧M(G2)) = ω(L)` forcing `δ≤1/4`.

### Reproduction artifact
Contract `research/EXP_MATUNION_A2_contract.md`; impl
`experiments/ecdlp_prime_field/matunion_delta_meter.sage`; result `matunion_delta.json`;
audit `matunion_audit.py`; ledger **P1527 / RT-1472-MATUNION-A2**.

---

## Candidate: DESCENT-EXP-A3 — Individual-log descent-tree branching-exponent meter

### One-sentence mechanism
Exploit the fact that **every prior "below rho" left the individual-log descent
unmetered**: directly measure the descent-tree **branching exponent** `γ_desc` of the
m=5 membership backend, and check `γ_desc ≤ 1/5` so that descent does not silently
dominate the RT-1476/RT-1472 relation win.

### Status
HYPOTHESIS (γ_desc is a measurable exponent).

### Novelty classification
LEDGER-NEW (the descent stage is stage 7 in every prior candidate but is *metered*
nowhere; all prior meters measure relation-generation or enrichment).

### Semantic fingerprint
- object: the special-q descent tree of a target `T=[r]P` under repeated m=5
  decomposition into smaller-norm points.
- public ops: the membership backend (POWERPROJ / subresultant); norm bookkeeping.
- hidden structure: **descent-tree branching factor and depth** — the true online cost.
- discarded: none (this is an accounting instrument).
- retained: per-level node count and smoothness-yield.
- relation-gen primitive: reuse of the chosen backend, applied to descent nodes.
- compression primitive: none (measurement).
- rank mechanism: n/a.
- descent mechanism: **the object of measurement**.
- dominant cost exponent: `γ_desc := log_q(total descent nodes)`.

### Nearest ledger / report entries
1. **RT-1476** — asserts "same backend for descent," cost `q^{1/5}`, but does **not**
   measure the branching that produces it; A3 supplies the missing meter.
2. **batch2/A3 many-target amortization** — measures the offline/online crossover for
   *relations*, not the *descent tree* of a single target.
3. **PO67/PO68 ledger entries** — repeatedly note "late rank arrival limits reductions"
   and "target descent" as the unresolved cost; A3 turns that into an exponent.
4. **PO-transfer "blind descent" gates** — verify *correctness* of descent, never its
   *exponent*.
5. **batch4 winners' contracts** — all assume descent `≤ relations`; A3 tests that
   assumption, on which every winner silently depends.

### Nearest literature
Enge–Gaudry (descent/individual log in IC); Diem (descent trees for EC IC); Joux–Vitse
(descent cost). These give asymptotic descent bounds but no toy-scale *measured* m=5
exponent. *(literature note appended.)*

### Target family
As RT-1476 (ordinary prime-order, m=5 line model).

### Full algorithmic path
Instruments stages 6–7 of *another* candidate (POWERPROJ default): 1–5 supplied by the
host backend; 6 calibration; 7 **descent tree fully expanded and counted** per target;
8 online cost = descent nodes × backend query; 9 memory = active frontier.

### Cost model
Total online exponent `= max(relation exponent, γ_desc + α)`. A candidate that wins on
relations but has `γ_desc + α > 1/2` does **not** beat rho single-target. **Falsifiable:**
measure `γ_desc` for the m=5 backend; sub-rho requires `γ_desc + α ≤ 1/2` with the
relation stage already `≤2/5`.

### Why existing negatives do not already kill it
No prior artifact metered descent; this is a genuine unfilled accounting slot, not a
re-run. New operation = full descent-tree expansion and node-count fitting.

### Likely fatal obstruction
Descent may branch as `q^{1/5}` per level over `O(log q)` levels but with a **constant
>1 per-node re-decomposition failure rate**, inflating `γ_desc` past `1/5` and revealing
that the RT-1476 "descent `q^{1/5}`" is optimistic.

### Minimal falsifying experiment
Toy `p∈{1009, 65521, 16769023}`; run the m=5 backend descent on 30 random targets each;
count nodes per level; fit `γ_desc`. Positive control: a factor base engineered for
high smoothness (low branching). Negative control: an undersized factor base (expect
`γ_desc→1/2`, i.e. descent ≈ exhaustive).

### Quantitative promotion gate
`γ_desc ≤ 1/5` with the host backend at `α≤1` ⇒ the descent half of RT-1476 is
honestly clear. `γ_desc + α > 1/2` ⇒ scoped NEGATIVE: relation wins do not close the
single-target gap.

### Proof / disproof track
Proof: a smoothness-probability bound giving descent depth `O(log q)` and per-level
branching `q^{1/5}`. Disproof: a measured `γ_desc>1/5` on ordinary curves.

### Reproduction artifact
Contract `research/EXP_DESCENT_EXP_A3_contract.md`; impl
`experiments/ecdlp_prime_field/descent_exponent_meter.sage`; result
`descent_exponent.json`; audit `descent_audit.py`; ledger **P1528 / DESCENT-EXP-A3**.

---

## Candidate: MAHLER-B1 — Automatic-sequence / Mahler-equation representation of x([k]P)

### One-sentence mechanism
Represent the scalar-indexed sequence `k ↦ x([k]P)` (an elliptic divisibility sequence)
by a **Mahler functional equation / finite-automaton (k-automatic) structure** and read
`k` from low automaton state-complexity rather than from the group order.

### Status
HYPOTHESIS (near-certain negative — see obstruction; kept for the barrier it sharpens).

### Novelty classification
POSSIBLY NOVEL (representation); **distinct** from EDS-smoothness (report1/A2, which uses
EDS terms as *relation values*) and from Drinfeld/function-field transport (batch2/B2).

### Semantic fingerprint
- object: the EDS `(W_k)` and the x-sequence `x([k]P)=φ_k/ψ_k^2` as a formal power/Mahler
  series.
- public ops: EDS recurrence; base-b digit maps.
- hidden structure (*hypothesised*): a Mahler relation
  `Σ_i a_i(z) f(z^{b^i}) = 0` encoding `k`.
- discarded: the group-order coordinate.
- retained: automaton state / Mahler coefficient stream.
- relation-gen primitive: automaton transition following the base-b digits of `k`.
- compression primitive: finite-state automaton (if it exists).
- rank mechanism: n/a (a representation probe).
- descent: read `k` digit-by-digit from the automaton.
- dominant cost exponent: `polylog(q)` **if** the sequence is automatic.

### Nearest ledger / report entries
1. **report1/A2 EDS-smoothness**: uses EDS terms for *smooth relations*; MAHLER asks a
   *structural* question (is the sequence automatic?) — orthogonal use.
2. **batch2/B2 Drinfeld**: function-field *module* transport; MAHLER is a *functional-
   equation / automatic-sequence* structure, not a Drinfeld module.
3. **RT-1485 Kummer state**: a *finite* companion state; MAHLER is an *infinite*
   sequence structure.
4. **PO96V cyclic-lift cocycle**: carry/cocycle recovery has "full q-valued cocycles";
   MAHLER would need the opposite (finite state) — direct tension.
5. **batch1/B1 nilpotent jet**: first-order local lift; MAHLER is a global
   digit-recursive structure.

### Nearest literature
Ward (EDS); Shipsey, Stange (elliptic nets); Adamczewski–Bell (Mahler functions,
transcendence); Allouche–Shallit (automatic sequences). Known: EDS satisfy nonlinear
recurrences and their generating functions are generally **not** automatic (would
contradict transcendence/aperiodicity results). *(literature note appended — this is the
crux.)*

### Target family
Ordinary prime-field prime-order; excluded singular/anomalous.

### Full algorithmic path
1. Compute EDS terms `W_1..W_T`. 2. Test for a Mahler relation of bounded order/degree by
   linear algebra over `F_p(z)`. 3. Witness: a nonzero Mahler operator annihilating the
   series. 4–6 n/a. 7. If found, read `k` from automaton state. 8/9: polylog if found.

### Cost model
If automatic with state-complexity `s(q)=polylog(q)`, the DLP is `polylog(q)` —
exponent `0`. **Falsifiable prediction:** no bounded-order Mahler relation exists
(state-complexity grows polynomially in `q`), giving exponent `≥1/2` and a scoped
negative. Compare vs rho.

### Why existing negatives do not already kill it
No prior artifact tested the automatic/Mahler structure of the x-sequence; EDS were used
only for smoothness. New operation = Mahler-operator search over `F_p(z)`.

### Likely fatal obstruction
EDS are provably **not eventually periodic / not automatic** in characteristic 0
(transcendence of associated series); over `F_p` the sequence is periodic with period
`Θ(n)`, so any automaton has `Θ(n)=Θ(q)` states ⇒ no compression, exponent `≥1/2`. This
is the near-certain kill.

### Minimal falsifying experiment
Toy `p∈{101, 1009, 65521}`; compute the x-sequence period and the **minimal Mahler
operator order/degree** and the minimal DFAO state count; fit state-complexity vs `q`.
Positive control: a genuinely automatic sequence (Thue–Morse) — should give bounded
state. Negative control: a random periodic sequence of period `n` (expect `Θ(n)` states).

### Quantitative promotion gate
Minimal automaton state count `= polylog(q)` across sizes ⇒ promote (would be a break).
`= q^{Ω(1)}` ⇒ scoped NEGATIVE: the x-sequence carries no sub-linear automatic
structure (a clean representation barrier).

### Proof / disproof track
Proof (kill): EDS over `F_p` have automaton state-complexity `Θ(n)`. Disproof (break):
a bounded-order Mahler operator whose automaton reads `k` in `polylog(q)`.

### Reproduction artifact
Contract `research/EXP_MAHLER_B1_contract.md`; impl
`experiments/ecdlp_prime_field/mahler_state_complexity.sage`; result
`mahler_state.json`; audit `mahler_audit.py`; ledger **P1529 / MAHLER-B1**.

---

## Candidate: FOURIERMUKAI-B2 — Fourier–Mukai nonlinear kernel label (nonlinear-frontier attack) *(REPRESENTATION WINNER)*

### One-sentence mechanism
Exploit the **Fourier–Mukai autoequivalence** `Φ_P: D^b(E)→D^b(Ê)` with Poincaré kernel:
a point `P` maps to the degree-0 line bundle `O(P−O)`, so a **bilinear/nonlinear label**
of the transfer correspondence — the FM kernel evaluated on `(source, target)` — is a
genuinely nonlinear target functional that could **escape the LINLABEL-UNIFIED-D3
barrier**, the ledger's one surviving representation frontier.

### Status
HYPOTHESIS (targets the exact open loophole; collapse risk is explicit).

### Novelty classification
POSSIBLY NOVEL for this application (FM transform classical; its use to build a
**nonlinear factor-base label** for prime-field ECDLP is new and directly aimed at the
P1525 frontier).

### Semantic fingerprint
- object: `E`, its dual `Ê≅E`, and the Poincaré line bundle `𝒫` on `E×Ê` (the FM
  kernel).
- public ops: line-bundle arithmetic on `E` (Weil pairing / theta functions realize `𝒫`
  on torsion).
- hidden structure: the FM kernel is **bilinear** in `(source, target)` — precisely the
  non-`F_p`-linear label class the D3 barrier leaves open.
- discarded: `F_p`-linear endpoint functionals (known bounded-rank).
- retained: the bilinear pairing value `⟨e_source, e_target⟩_𝒫`.
- relation-gen primitive: for factor-base points `F_i` and target-derived points,
  evaluate the FM/Poincaré pairing to a **nonlinear** feature and seek rank-productive
  coincidences.
- compression primitive: the FM transform (derived pushforward of `𝒫`).
- rank mechanism: whether the nonlinear-label incidence matrix reaches `B−1`.
- descent: pairing-consistent special-q.
- dominant cost exponent: TBD — first obligation is a **rank-vs-control** measurement.

### Nearest ledger / report entries
1. **LINLABEL-UNIFIED-D3 / P1525**: the barrier stating **only nonlinear labels escape**;
   FM is a *specific constructible* nonlinear label — the intended positive probe of the
   loophole D3 isolates. Distinction: prior escapes (APOLARITY, GENJAC) use
   Waring/generalized-Jacobian labels; FM uses a **derived-category / Poincaré-kernel**
   label — a different nonlinear object.
2. **PO96D scalar Weil pullback (closed)**: `F_p`-linear label `q2−[k]φ·q1`, all worse.
   FM is explicitly **non-linear**, so the PO96D negative does not cover it.
3. **MOV/pairing (order-only barrier)**: the Weil pairing gives an order-`n` character
   DLP; FM must be shown to yield a **factor-base rank** signal, not merely a pairing —
   this is the crux and the collapse risk.
4. **batch2/B3 Riemann-bilinear theta**: uses level-≥3 theta for *low-degree membership*;
   FM uses the Poincaré kernel for a *nonlinear label*, not a membership relation.
5. **PO96AB nonlinear projector requests**: the ledger repeatedly asks for a
   "uniform scalar-blind nonlinear projector on a corresponding Jacobian/torus"; FM is a
   concrete candidate for that object.

### Nearest literature
Mukai 1981 (Fourier functor on abelian varieties); Atiyah (bundles on E); Polishchuk
(abelian varieties, theta, FM). No source uses FM as an ECDLP relation label.
*(literature note appended.)*

### Target family
Ordinary prime-field prime-order, `j∉{0,1728}`; the dual `Ê` and `𝒫` are `F_p`-rational.
Excluded: supersingular, CM special orders.

### Full algorithmic path
1. Factor base `{F_i}` and their FM images `O(F_i−O)`. 2. Relations: seek factor-base
   subsets whose FM-pairing pattern against target-derived points is rank-productive.
   3. Witness: exact Poincaré-pairing / theta evaluation (verifiable). 4. Relation prob:
   **the object of measurement**. 5. Rank vs matched controls. 6. Calibration if rank
   survives. 7. Descent. 8/9 charged only after the rank gate.

### Cost model
No exponent until the rank gate passes. **Falsifiable first gate:** does the FM-nonlinear
incidence matrix have rank `≥B−1` **and** exceed matched linear-label and random controls?
If it collapses to the Weil pairing (order-`n` character) it is a **known** order-based
channel (no rank gain), and is killed. Compare vs rho only after a rank-positive result.

### Why existing negatives do not already kill it
Every closed transfer negative (PO96D, scalar Weil, MOV) is either `F_p`-linear or
order-based. FM is a **bilinear (nonlinear) non-order label** — exactly the class
LINLABEL-UNIFIED-D3 declares unbarriered. New operation = Poincaré-kernel FM evaluation
as a factor-base feature.

### Likely fatal obstruction
FM on `E` is governed by the same theta/Weil-pairing structure, so the nonlinear label
almost surely **collapses to the Weil pairing**, giving an order-`n` character DLP with no
factor-base rank — the MOV boundary. Resolving this either produces the first escaping
nonlinear label **or extends D3 to cover FM kernels** (both advance the frontier).

### Minimal falsifying experiment
Toy `p∈{271, 499, 787}` (the ledger's PO96 fixtures, for direct comparability); build the
FM/Poincaré label incidence for a `B≈q^{1/5}` factor base; compute rank vs (a) matched
`F_p`-linear label control, (b) random-label control, (c) the Weil-pairing-only control.
Positive control: a construction where a nonlinear label is known rank-productive
(APOLARITY fixture). Negative control: the linear PO96D label (expect bounded rank).

### Quantitative promotion gate
FM-label rank `≥B−1` **strictly above** all three controls on all three fixtures, AND not
reducible to the Weil pairing ⇒ promote (first escaping nonlinear label). Any of: rank
`o(B)`, control-matched, or Weil-pairing-reducible ⇒ scoped NEGATIVE extending
LINLABEL-UNIFIED-D3 to FM kernels.

### Proof / disproof track
Proof (escape): the FM-label incidence has generic rank `B−1` and is not a character of
the order-`n` group. Disproof (barrier extension): the FM kernel on `E` factors through
the Weil pairing ⇒ order-only ⇒ bounded factor-base rank.

### Reproduction artifact
Contract `research/EXP_FOURIERMUKAI_B2_contract.md`; impl
`experiments/ecdlp_isogeny/fourier_mukai_label_rank.sage`; result `fm_label_rank.json`;
audit `fm_audit.py`; ledger **P1530 / FOURIERMUKAI-B2**.

---

## Candidate: MOTIVIC-B3 — Arc-space / motivic-measure representation of membership

### One-sentence mechanism
Represent five-point membership as a **motivic volume of the arc space** of the Semaev
variety (Denef–Loeser), asking whether the motivic measure of the decomposition locus is
computable in sub-`√q` work.

### Status
HYPOTHESIS (likely vacuous over finite fields; kept as a representation/barrier probe).

### Novelty classification
POSSIBLY NOVEL; **distinct** from the first-order jet lift (report1/B1) — arc spaces are
*infinite*-jet, and motivic integration is a *measure*, not a derivative.

### Semantic fingerprint
- object: arc space `L(V)` of the Semaev variety `V={S5=0}`; motivic measure `μ`.
- public ops: point counting; Igusa/motivic zeta computation.
- hidden structure: `μ(decomposition locus)` as a rationally-computable invariant.
- discarded: individual solutions.
- retained: the motivic/Igusa zeta function coefficients.
- relation-gen primitive: motivic volume ⇒ *count* of decompositions.
- compression primitive: rationality of the motivic zeta function.
- rank mechanism: n/a (a counting/representation probe).
- descent: none direct.
- dominant cost exponent: `polylog(q)` if the motivic measure is cheaply computable.

### Nearest ledger / report entries
1. **report1/B1 nilpotent jet (first order)**: motivic uses *all* orders (arcs) — a
   strictly larger object.
2. **batch4/PILA-WILKIE-C2**: o-minimal *counting* of the lifted variety (char-0
   artifact risk); motivic is an *algebraic-geometric measure*, same "counting not
   solving" concern but a different object.
3. **report1/A1 BKK mixed volume**: a Newton-polytope *count*; motivic is an arc-space
   measure — different invariant.
4. **report3/B4 Semaev border rank**: an algebraic-complexity invariant of the tensor;
   motivic is a measure of the variety.
5. **P1509 Hasse-jet source-section**: exact local positive, no global compiler; motivic
   is the "global measure" analogue — likely inheriting the same no-global-compiler wall.

### Nearest literature
Denef–Loeser (motivic integration, arc spaces); Igusa (local zeta functions). No ECDLP
application. *(literature note appended.)*

### Target family
Ordinary prime-field prime-order.

### Full algorithmic path
1. Form `V={S5=0}`. 2. Compute the (truncated) motivic/Igusa zeta of the decomposition
   locus. 3. Extract the point-count of decompositions from the zeta. 4. If sub-`√q`
   *and solution-locating*, use to seed relations; else representation-only.

### Cost model
A *count* of decompositions is not a *solve*. **Falsifiable:** the motivic measure gives
`#solutions` but not their coordinates in sub-`√q`; exponent `≥1/2` for actual recovery.
Compare vs rho.

### Why existing negatives do not already kill it
Arc-space / motivic measure was never computed here; first-order jets were. New operation
= truncated motivic-zeta computation of the decomposition locus.

### Likely fatal obstruction
Motivic integration is a **char-0 / generic** invariant; over `F_p` it degenerates to
point-counting (Weil), which gives a *count*, not a *witness*. Locating a decomposition
still costs `Ω(√q)`. Near-certain representation-only negative.

### Minimal falsifying experiment
Toy `p∈{101, 1009, 65521}`; compute the decomposition count via (a) direct enumeration
and (b) a truncated Igusa/motivic zeta; check whether the zeta yields witnesses or only
counts, and its computation cost exponent. Positive control: a variety with a known
cheap motivic measure. Negative control: a random dense hypersurface (expect count-only).

### Quantitative promotion gate
Motivic zeta yields **located** decompositions in sub-`√q` ⇒ promote. Count-only or
`≥√q` ⇒ scoped NEGATIVE (representation carries no witness advantage).

### Proof / disproof track
Proof (kill): motivic measure over `F_p` = Weil point-count ⇒ no witness in sub-`√q`.
Disproof (break): a motivic-zeta evaluation that locates a decomposition in `polylog(q)`.

### Reproduction artifact
Contract `research/EXP_MOTIVIC_B3_contract.md`; impl
`experiments/ecdlp_prime_field/motivic_measure_probe.sage`; result `motivic_probe.json`;
audit `motivic_audit.py`; ledger **P1531 / MOTIVIC-B3**.

---

## Candidate: ARBOREAL-C1 — Arboreal Galois / iterated-preimage-tree invariant *(HIGH-RISK WINNER)*

### One-sentence mechanism
Exploit the **arboreal Galois representation** (profinite iterated monodromy) of the
Lattès/multiplication map's preimage tree: test whether a spectral or statistical
invariant of the tree image leaks the scalar `k` in `T=[k]P` in sub-`√q` work.

### Status
HYPOTHESIS (high-risk; likely killed generically by arboreal-image maximality — D3).

### Novelty classification
POSSIBLY NOVEL; **distinct** from the single-map transfer operator (report1/C2 Ruelle
spectrum), Ritt decomposition (batch2/B3), and isogeny-walk (batch2/C1) — the arboreal
representation is the *profinite iterated-monodromy group of the whole preimage tree*, a
new object.

### Semantic fingerprint
- object: the rooted preimage tree `T_∞` of the multiplication/Lattès map `L_m` on `E`,
  with Galois action `ρ: Gal → Aut(T_∞)`.
- public ops: division polynomials; Frobenius on preimages.
- hidden structure: (*hypothesised*) a Frobenius-conjugacy or spectral invariant of the
  tree image correlated with `k`.
- discarded: the group order.
- retained: the arboreal image / a tree invariant.
- relation-gen primitive: Frobenius acting on level-`ℓ` preimages of the target.
- compression primitive: the finite tree image at bounded level (if non-maximal).
- rank mechanism: n/a (leakage probe).
- descent: read `k` from tree invariants if leakage exists.
- dominant cost exponent: `polylog(q)` **iff** the image is non-maximal and `k`-correlated.

### Nearest ledger / report entries
1. **report1/C2 Lattès transfer operator**: the Ruelle operator of *one* map; ARBOREAL
   uses the *iterated preimage tree* (all levels) and its Galois image — a different,
   profinite object.
2. **batch2/B3 Ritt decomposition**: functional *decomposition* of `f_m`; ARBOREAL is the
   *dynamical iterated monodromy*, not a decomposition.
3. **batch2/C1 non-backtracking isogeny walk**: a walk on the *isogeny* graph; ARBOREAL
   walks the *preimage* tree of a self-map on one curve.
4. **PO96Z Kummer functional-graph**: notes "functional-graph conjugates" with maximal
   degree; ARBOREAL asks the *Galois* (not geometric) structure of the same tree — direct
   tension, and PO96Z's maximality hint foreshadows the D3 kill.
5. **RT-1485 Kummer state**: a level-1 companion state; ARBOREAL is the full profinite
   tower.

### Nearest literature
Odoni (arboreal representations); R. Jones (surveys; generic maximality of arboreal
image); Pink (profinite iterated monodromy of Lattès maps); **Serre (open-image theorem)**.
Crux (from the literature check): for an elliptic curve the multiplication-by-`m` preimage
tree **is the `m`-adic Tate-module tower**, whose Galois image is generically `GL_2` (Serre
open image / arboreal maximality for Lattès). So ARBOREAL is a *Tate-tower leakage* question
in tree language; the maximality barrier is exactly Serre's theorem, and it predicts **no
`k`-signal**. The novel content is the framing (a tree-invariant mutual-information probe)
and the exact toy verifier, not a new object beyond the Tate tower.

### Target family
Ordinary prime-field prime-order, `j∉{0,1728}` (Lattès genericity).

### Full algorithmic path
1. Build division-polynomial preimage tree to bounded level `ℓ`. 2. Compute the Frobenius
   action / arboreal image at level `ℓ`. 3. Witness: a tree invariant that separates `k`
   values. 4–6 n/a. 7. If separating, binary-search `k` via tree invariants.
   8/9 polylog if leakage exists.

### Cost model
If the arboreal image is non-maximal with a `k`-correlated invariant computable at level
`ℓ=polylog(q)`, DLP is `polylog(q)`. **Falsifiable prediction:** the image is maximal
(full `Aut(T_ℓ)`) with no `k`-correlation ⇒ exponent `≥1/2`. Compare vs rho.

### Why existing negatives do not already kill it
No prior artifact computed the *Galois* image of the preimage tree; PO96Z only noted
geometric functional-graph conjugacy. New operation = arboreal-image computation and a
Frobenius-conjugacy leakage test.

### Likely fatal obstruction (→ D3)
Generic **maximality of the arboreal image** = **Serre's open-image theorem** on the
`m`-adic Tate tower: for ordinary non-CM `E`, the image is generically `GL_2(Z_m)`, so the
tree is effectively a full-torsor and carries **no** scalar-`k` information beyond
Pohlig–Hellman. Near-certain kill; the small non-maximal cases are CM/special (excluded).

### Minimal falsifying experiment
Toy `p∈{101, 1009, 65521}`; build the level-`ℓ` preimage tree (ℓ=1..4) on ordinary
prime-order curves; compute the arboreal image size vs `|Aut(T_ℓ)|` and test any tree
invariant against known `k` (mutual-information probe). Positive control: a CM curve with
known small arboreal image. Negative control: a random ordinary curve (expect maximal
image, zero mutual information).

### Quantitative promotion gate
Non-maximal image with measurable `k`-mutual-information `>0` scaling favorably ⇒ promote.
Maximal image / zero mutual information across sizes ⇒ scoped NEGATIVE feeding D3.

### Proof / disproof track
Proof (kill): arboreal image maximal ⇒ tree invariants independent of `k`. Disproof
(break): an ordinary family with non-maximal `k`-correlated image.

### Reproduction artifact
Contract `research/EXP_ARBOREAL_C1_contract.md`; impl
`experiments/ecdlp_prime_field/arboreal_image_leakage.sage`; result
`arboreal_leakage.json`; audit `arboreal_audit.py`; ledger **P1532 / ARBOREAL-C1**.

---

## Candidate: COHENLENSTRA-C2 — Cohen–Lenstra volcano class-group bias relation predictor

### One-sentence mechanism
Exploit the **Cohen–Lenstra statistical distribution** of `Cl(End(E'))` across
isogeny-volcano neighbors of `E` to *predict* which neighbor yields a smoother / denser
relation supply, biasing the CM index-calculus factor base before construction.

### Status
HYPOTHESIS (high-risk; likely constant-factor only).

### Novelty classification
POSSIBLY NOVEL; **distinct** from CM ideal-factorization IC (report3/C3, which fixes *one*
endomorphism ring's class group as the factor base) — C2 uses the *distribution across
many rings* as a *predictor*.

### Semantic fingerprint
- object: the volcano of `ℓ`-isogenous curves and their class groups `Cl(O_i)`.
- public ops: isogeny steps; class-group structure computation on small `O_i`.
- hidden structure: Cohen–Lenstra bias in `Cl(O_i)` `p`-ranks predicting relation density.
- discarded: neighbors with unfavorable class-group statistics.
- retained: the best-statistics neighbor's class group as factor base.
- relation-gen primitive: CM ideal factorization on the selected neighbor.
- compression primitive: none (a selection heuristic).
- rank mechanism: relation-matrix rank on the selected class group.
- descent: CM descent on the selected neighbor.
- dominant cost exponent: subexponential (class-group IC) at best — **not** a `<1/2`
  polynomial exponent.

### Nearest ledger / report entries
1. **report3/C3 CM ideal-factorization IC**: fixed single class group; C2 *selects* among
   neighbors by distribution. 2. **batch2/C1 isogeny walk**: walks for *collisions*; C2
   walks for *class-group statistics*. 3. **PO75/PO76 volcano census**: exact horizontal
   family classification (no repeated native factor); C2 adds a *statistical* selection
   layer. 4. **batch4/GROWTH-SL2-C1**: growth in the isogeny/Kummer group; C2 is a
   number-theoretic class-group statistic, not a growth argument. 5. **non_generic_transfer
   same-field isogeny closed**: order/trace invariant in class — C2 must show the class
   *group structure* (not order) varies usefully across the volcano.

### Nearest literature
Cohen–Lenstra (class-group heuristics); Kohel (volcano/endomorphism rings); Bisson–Sutherland
(endomorphism-ring computation); Enge (class-group IC subexponentiality). No source uses
Cohen–Lenstra bias as an IC factor-base predictor. *(literature note appended.)*

### Target family
Ordinary prime-field prime-order with computable small-conductor endomorphism rings on
the volcano.

### Full algorithmic path
1. Walk the ℓ-volcano to depth `d`; 2. compute `Cl(O_i)` structure; 3. select the
   neighbor with the most favorable Cohen–Lenstra statistics; 4. run CM ideal-factorization
   IC there; 5–9 as report3/C3.

### Cost model
Best case = class-group IC subexponential `L_q(1/2)` — **already worse than rho's
`q^{1/2}` for the class-group DLP transfer, and the CM transfer itself is order-based**.
**Falsifiable:** measure whether *any* selection produces a *polynomial* relation-density
gain (exponent), not a constant. Compare vs rho.

### Why existing negatives do not already kill it
The same-field isogeny closure is *order/trace* based; C2 uses *class-group structure*
variation, not order. New operation = Cohen–Lenstra-biased neighbor selection.

### Likely fatal obstruction
Cohen–Lenstra bias is a **constant-factor distributional** statement; it cannot change an
exponent. And the CM transfer is order-based (invariant in the isogeny class), so the
target subgroup is not solved. Near-certain constant-only / order-based negative.

### Minimal falsifying experiment
Toy `p∈{1009, 65521, 16769023}`; enumerate volcano neighbors to depth 3; compute
`Cl(O_i)` and relation density; test whether best-neighbor density scales as a *better
exponent* than the base. Positive control: an artificially imbalanced class-group family.
Negative control: the base curve (expect no exponent change).

### Quantitative promotion gate
Best-neighbor relation-density **exponent** strictly better than base across sizes AND a
subgroup-solving (not order-only) descent ⇒ promote. Constant-only or order-only ⇒ scoped
NEGATIVE.

### Proof / disproof track
Proof: an exponent-level density gap across the volcano. Disproof: Cohen–Lenstra bias is
`O(1)` multiplicative and CM transfer is order-based ⇒ no exponent change.

### Reproduction artifact
Contract `research/EXP_COHENLENSTRA_C2_contract.md`; impl
`experiments/ecdlp_isogeny/cohen_lenstra_volcano_bias.sage`; result `cl_volcano.json`;
audit `cl_audit.py`; ledger **P1533 / COHENLENSTRA-C2**.

---

## Candidate: FREEPROB-C3 — Free-probability spectral sketch of the membership operator

### One-sentence mechanism
Model the S3/S5 point-decomposition membership operator as a **structured random matrix**
and use **free probability** (asymptotic freeness) to predict a spectral outlier/gap that
would enable a sub-`√q` **low-rank sketch** of membership.

### Status
HYPOTHESIS (high-risk; likely killed — the operator is deterministic-algebraic).

### Novelty classification
POSSIBLY NOVEL; **distinct** from sign-rank/γ2 (batch4/B3, a communication-complexity
norm) and border rank (report3/B4, algebraic rank) — free probability is an *asymptotic
spectral-distribution* tool.

### Semantic fingerprint
- object: the membership incidence operator `M` (rows = factor-base tuples, cols =
  targets), viewed as a structured random matrix ensemble.
- public ops: matrix–vector products with `M` (via the backend).
- hidden structure: (*hypothesised*) an outlier eigenvalue / spectral gap concentrating
  membership into a low-rank subspace.
- discarded: the bulk spectrum.
- retained: the top-`r` singular subspace (a sketch).
- relation-gen primitive: project the target onto the top-`r` sketch to test membership.
- compression primitive: **low-rank spectral sketch** predicted by free convolution.
- rank mechanism: sketch rank `r` vs `B`.
- descent: sketch-consistent special-q.
- dominant cost exponent: `sketch-apply` exponent if `r=o(B)`.

### Nearest ledger / report entries
1. **report3/B4 / D3 Semaev border rank**: algebraic rank of the *tensor*; FREEPROB
   targets the *spectral* distribution of the *matrix* — different rank notion (and any
   low-rank sketch reduces to border rank, the collapse risk).
2. **batch4/B3 sign-rank γ2**: a norm from communication complexity; FREEPROB is
   spectral/analytic.
3. **batch3/A2 effective-resistance sparsifier**: a *combinatorial* spectral sparsifier;
   FREEPROB is a *random-matrix* spectral predictor.
4. **PO92/PO93 rank censuses**: exact finite-module ranks with "no map-span surplus";
   FREEPROB would need a spectral outlier those exact censuses did **not** see — direct
   tension.
5. **batch4/SLICE-RANK-1-D2**: slice rank vacuous in rank-1 cyclic `E(F_p)`; FREEPROB
   faces the same "deterministic algebraic object, universality inapplicable" wall.

### Nearest literature
Voiculescu (free probability); Bai–Silverstein (spectra of large random matrices);
Tao–Vu (universality). No ECDLP/IC application. *(literature note appended.)*

### Target family
Ordinary prime-field prime-order.

### Full algorithmic path
1. Build `M` for a `B≈q^{1/5}` factor base. 2. Compute its singular spectrum; compare to
   the free-convolution prediction. 3. If a top-`r` (r=o(B)) sketch reproduces membership,
   use it as the backend. 4–9 charged only if the sketch is faithful.

### Cost model
A faithful `r=o(B)` sketch would drop membership below the dense query — but this is
exactly a **border-rank** statement (closed) unless the sketch is *spectrally* (not
algebraically) cheap. **Falsifiable:** measure the singular spectrum; predict whether an
outlier exists. Compare vs rho and vs the border-rank baseline.

### Why existing negatives do not already kill it
The border-rank negative is *algebraic*; FREEPROB tests a *spectral* outlier that could,
in principle, be cheaper to apply. New operation = free-convolution spectral prediction +
sketch faithfulness test.

### Likely fatal obstruction
`M` is **deterministic and algebraic** (Semaev structure), so random-matrix universality
does **not** apply; its spectrum is rigid, and any faithful low-rank sketch is a border-rank
witness (closed at the wall). The PO92/PO93 exact ranks already show no surplus. Near-certain
kill.

### Minimal falsifying experiment
Toy `p∈{1009, 65521}`; build `M` (B up to `q^{1/5}`); compute the exact singular spectrum;
compare to the Marchenko–Pastur/free-convolution prediction; test a top-`r` sketch's
membership fidelity. Positive control: a genuinely random ±1 matrix (universality holds).
Negative control: the Semaev `M` (expect rigid, no outlier / no faithful sketch).

### Quantitative promotion gate
A stable spectral outlier giving a faithful `r=o(B)` sketch **not** reducible to border
rank ⇒ promote. Rigid spectrum / border-rank-equivalent / no outlier ⇒ scoped NEGATIVE
feeding D1.

### Proof / disproof track
Proof: a spectral outlier + sub-border-rank sketch application. Disproof: the Semaev
operator's spectrum is rigid (no universality) and any low-rank sketch = border rank.

### Reproduction artifact
Contract `research/EXP_FREEPROB_C3_contract.md`; impl
`experiments/ecdlp_prime_field/freeprob_spectral_sketch.sage`; result `freeprob.json`;
audit `freeprob_audit.py`; ledger **P1534 / FREEPROB-C3**.

---

## Candidate: ASYMPSPEC-D1 — Asymptotic-spectrum-of-tensors barrier for bilinear membership *(BARRIER — pairs B4-report3, C3, POWERPROJ)*

### One-sentence mechanism
Strengthen the border-rank barrier (report3/D3) using **Strassen's asymptotic spectrum**
(quantum and support functionals): bound **every degeneration / bilinear algorithm** for
the Semaev membership operator, not one fixed decomposition, closing the whole bilinear
lane below the exponent needed.

### Status
OPEN (barrier candidate).

### Novelty classification
LEDGER-NEW barrier object (border rank bounds *one* decomposition; the asymptotic
spectrum bounds *all* degenerations simultaneously via the universal spectral points).

### Semantic fingerprint
Object = the Semaev summation tensor `T_m`; mechanism = the value of `T_m` under every
monotone spectral point (quantum functional `F^t`, support functional `ζ^θ`) lower-bounds
asymptotic (border) rank of any bilinear membership algorithm; loophole = **non-bilinear**
backends (POWERPROJ trace-side, subresultant) not covered.

### Nearest ledger / report entries
1. **report3/D3 Semaev transform-sparsity / border-rank LB**: bounds one decomposition;
   ASYMPSPEC bounds the *asymptotic rank* over all degenerations. 2. **batch4/SLICE-RANK-1-D2**:
   slice rank (one spectral point); ASYMPSPEC uses the *whole spectrum* (slice rank is a
   special case). 3. **batch1/B2 tensor-train**: an *upper*-bound backend; D1 is the matching
   *lower* bound. 4. **report3/B4 border rank**: the quantity D1 lower-bounds universally.
   5. **POWERPROJ-A1 / batch2-A1**: the *non-bilinear* escapes D1 explicitly leaves open —
   D1's value is to show bilinear cannot win, focusing effort on the trace/elimination side.

### Nearest literature
Strassen (asymptotic spectrum of tensors, 1986–91); Christandl–Vrana–Zuiddam (quantum
functionals, 2018); Zuiddam (support functionals / asymptotic spectrum duality). No ECDLP
application. *(literature note appended.)*

### Target family / path / cost
Applies to any bilinear membership algorithm for `m∈{3,4,5}`. Proof: evaluate a spectral
point (e.g. the quantum functional) on `T_m`; if `> q^{1/2·(m+1−α)^{-1}·…}` (the
RT-1476-implied threshold), no bilinear backend crosses rho. Cost model: a barrier — it
asserts the *bilinear* lane is closed, redirecting to trace/elimination backends.

### Why existing negatives do not already establish it
D3/report3 and SLICE-RANK-1 are *single* spectral points; the asymptotic spectrum is the
*supremum* over all monotone points and gives the *tight* asymptotic-rank obstruction —
a strictly stronger, reusable barrier.

### Likely fatal obstruction (to the barrier)
The relevant spectral point may be *small* on `T_m` (the tensor could have low asymptotic
rank), which would be a *positive* result (a fast bilinear backend) rather than a barrier —
the intended falsification.

### Minimal falsifying experiment
Toy `m∈{3,4,5}`; compute the support/quantum functionals of the concrete Semaev tensor
`T_m` at small `q`; check whether they exceed the RT-1476 threshold. Positive control: the
matrix-multiplication tensor (known spectral values). Negative control: a low-rank tensor
(small functionals).

### Quantitative promotion gate
A spectral point of `T_m` provably exceeds the RT-1476 bilinear threshold for all `m≤5`
⇒ bilinear lane closed. A small spectral value ⇒ a *positive* backend lead instead.

### Proof / disproof track
Proof: `F^t(T_m) ≥ threshold`. Disproof: `F^t(T_m) < threshold` (a fast bilinear
membership algorithm).

### Reproduction artifact
Note `research/asympspec_barrier.md`; impl
`experiments/ecdlp_prime_field/asympspec_functionals.sage`; result `asympspec.json`;
ledger **P1535 / ASYMPSPEC-D1**.

---

## Candidate: MATUNION-INDEP-D2 — Two-graph independence barrier (pairs MATUNION-A2)

### One-sentence mechanism
Prove that the two honest large-prime graphs share the **same curve addition law** and are
therefore **not independent matroids**: their union rank exceeds a single graph's by
`o(|V|)`, so matroid-union enrichment cannot reach `δ>1/4`.

### Status
OPEN (barrier candidate).

### Novelty classification
LEDGER-NEW barrier (closes the matroid-union enrichment lane A2 opens).

### Semantic fingerprint
Object = two summation graphs `G1, G2` and their intersection matroid; mechanism = shared
arithmetic ⇒ high matroid intersection ⇒ small union-rank surplus; loophole = a
genuinely independent second structure (which the honest curve does not provide).

### Nearest ledger / report entries
1. **MATUNION-A2** — the candidate this closes. 2. **RT-1472** — the exponent that stays
   `2/3` if `δ≤1/4`. 3. **batch2/A2 cycle basis** — single-graph subcriticality, the
   input fact. 4. **batch4/CORRELATED-PEEL-A3** — the *dependent* sum-graph 2-core result,
   evidence that honest graphs are correlated. 5. **report2/D2 addition-law scrambling LB**
   — the addition law resists structured relation reuse; D2 is the matroid analogue.

### Nearest literature
Nash-Williams/Edmonds (matroid union rank); index-calculus large-prime dependence
(Cavallar). *(literature note appended.)*

### Target family / path / cost
Any two honest LP graphs from one curve. Proof: bound the matroid intersection
`rank(M(G1)∧M(G2)) = |V| − o(|V|)` via the shared addition-law incidence ⇒ union surplus
`o(|V|)` ⇒ `δ≤1/4`. Cost model: a barrier.

### Why existing negatives do not already establish it
Prior results show *single*-graph subcriticality; D2 is the first statement about the
*joint* matroid of two honest charts.

### Likely fatal obstruction (to the barrier)
A construction of two provably low-intersection charts (e.g. from disjoint torsion
structures) with union surplus `Ω(|V|)` — the A2 positive escape.

### Minimal falsifying experiment
Toy `p∈{1009, 65521}`; compute `rank(M(G1)∧M(G2))` for two same-curve charts vs two
independent random graphs; confirm same-curve intersection `≈|V|` (barrier) vs random
`≪|V|`.

### Quantitative promotion gate
Same-curve union surplus `o(|V|)` (`δ≤1/4`) across sizes ⇒ barrier holds. Surplus
`Ω(|V|)` ⇒ A2 reopens.

### Proof / disproof track
Proof: shared-addition-law incidence forces high matroid intersection. Disproof: a
low-intersection two-chart construction.

### Reproduction artifact
Note `research/matunion_indep_barrier.md`; impl
`experiments/ecdlp_prime_field/matunion_independence.sage`; result `matunion_indep.json`;
ledger **P1536 / MATUNION-INDEP-D2**.

---

## Candidate: ARBOREAL-MAX-D3 — Arboreal-image maximality barrier (pairs ARBOREAL-C1)

### One-sentence mechanism
Invoke **generic maximality of the arboreal Galois image** (Jones/Odoni) for ordinary
non-CM `E`: the iterated-preimage tree is a full `Aut(T_∞)`-torsor, so tree invariants
carry **no** scalar-`k` information beyond Pohlig–Hellman on the order.

### Status
OPEN (barrier candidate).

### Novelty classification
LEDGER-NEW barrier (imports arboreal-maximality into the ECDLP leakage setting; closes
ARBOREAL-C1 generically).

### Semantic fingerprint
Object = the arboreal image `ρ(Gal) ≤ Aut(T_∞)`; mechanism = maximality ⇒ uniform
distribution over tree automorphisms ⇒ zero `k`-mutual-information; loophole =
non-maximal (CM/special, excluded) images.

### Nearest ledger / report entries
1. **ARBOREAL-C1** — the candidate this closes. 2. **PO96Z functional-graph maximality**
   — the geometric analogue already observed. 3. **report1/D2 correspondence-permutation
   no-gain** — a permutation no-leakage barrier; D3 is its dynamical-tree version.
   4. **batch4/GROWTH-SL2 abelian-collapse** — group-theoretic no-leakage; D3 is the
   arboreal analogue. 5. **RT-1485** — the level-1 state maximality hint.

### Nearest literature
Odoni 1985; R. Jones (arboreal surveys, generic maximality); Pink (Lattès iterated
monodromy); **Serre (open-image theorem)** — the preimage tree is the `m`-adic Tate tower,
so maximality is Serre's theorem directly.

### Target family / path / cost
Ordinary non-CM prime-field `E`. Proof: for generic `E`, `ρ(Gal)=Aut(T_∞)` ⇒ any
`Gal`-invariant tree statistic is `k`-independent ⇒ leakage 0. Cost model: barrier.

### Why existing negatives do not already establish it
The ledger's maximality observations are *geometric* (functional-graph); D3 is the
*Galois*-image statement, which is what actually governs computable leakage.

### Likely fatal obstruction (to the barrier)
A non-maximal ordinary family (rare, likely CM/special) with a `k`-correlated invariant —
the ARBOREAL-C1 positive escape.

### Minimal falsifying experiment
Toy `p∈{101, 1009, 65521}`; compute level-`ℓ` arboreal image size vs `|Aut(T_ℓ)|` on
ordinary curves; confirm maximality and zero `k`-mutual-information. Positive control: a CM
curve (small image). Negative control: random ordinary (maximal).

### Quantitative promotion gate
Maximal image + zero mutual information across sizes ⇒ barrier holds. Non-maximal +
positive MI ⇒ C1 reopens.

### Proof / disproof track
Proof: generic arboreal maximality ⇒ no leakage. Disproof: a non-maximal `k`-correlated
ordinary family.

### Reproduction artifact
Note `research/arboreal_max_barrier.md`; impl
`experiments/ecdlp_prime_field/arboreal_maximality.sage`; result `arboreal_max.json`;
ledger **P1537 / ARBOREAL-MAX-D3**.

---

## 2. Ranking

Scores 0–5: **D** distance from prior ledger/report mechanisms; **V** exact-verifier
plausibility; **E** chance of changing an *exponent* (not a constant); **P** complete-path
coverage; **F** toy-scale falsifiability; **L** literature-novelty confidence; **R** *low*
hidden-preprocessing/memory risk. Reject if `D<3`, no complete descent path, no rho
comparison, or no precise distinction from the closest entry.

| Cand | Group | D | V | E | P | F | L | R | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **POWERPROJ-A1** | A | 3 | 5 | 4 | 5 | 5 | 3 | 4 | **29** | **WINNER (conservative)** |
| MATUNION-A2 | A | 4 | 5 | 3 | 4 | 5 | 3 | 4 | 28 | keep |
| DESCENT-EXP-A3 | A | 4 | 5 | 3 | 4 | 5 | 3 | 5 | 29 | keep (fills the descent-accounting gap) |
| MAHLER-B1 | B | 4 | 4 | 3 | 3 | 5 | 4 | 4 | 27 | keep (near-certain negative) |
| **FOURIERMUKAI-B2** | B | 4 | 4 | 4 | 4 | 4 | 4 | 3 | **27** | **WINNER (representation)** |
| MOTIVIC-B3 | B | 4 | 3 | 2 | 3 | 3 | 4 | 3 | 22 | keep (weak; likely count-only) |
| **ARBOREAL-C1** | C | 5 | 4 | 3 | 4 | 4 | 4 | 4 | **28** | **WINNER (high-risk)** |
| COHENLENSTRA-C2 | C | 3 | 4 | 2 | 4 | 4 | 4 | 3 | 24 | keep (constant-only risk) |
| FREEPROB-C3 | C | 4 | 3 | 2 | 3 | 4 | 4 | 3 | 23 | keep (universality-inapplicable risk) |
| ASYMPSPEC-D1 | D | 4 | 4 | — | 4 | 4 | 4 | 4 | 24 | barrier |
| MATUNION-INDEP-D2 | D | 4 | 5 | — | 4 | 5 | 3 | 5 | 26 | barrier |
| ARBOREAL-MAX-D3 | D | 5 | 4 | — | 4 | 4 | 4 | 4 | 25 | barrier |

All twelve satisfy `D≥3`, carry a complete (if speculative) descent path, compare to rho,
and give a precise mathematical distinction from their nearest entry. **Rejected as
duplicates during generation** (not tabled): a half-GCD backend (= subresultant PRS,
batch2/A1); an LSH/sketch prefilter (= post-hoc feature control); a Wormald DE 2-core meter
(= batch4/A3); a p-adic-Hodge translation coordinate (= crystalline/Serre–Tate, batch2/B2 +
report3/B2). **Winners:** POWERPROJ-A1 (conservative — a new *dual-side* measurement on
the single most load-bearing gate RT-1476), FOURIERMUKAI-B2 (representation — the one
candidate aimed squarely at the surviving nonlinear-label frontier P1525), ARBOREAL-C1
(high-risk — the cleanest genuinely-new object with an exact toy verifier).

---

## 3. Experiment contracts (three winners) + first command

### 3.1 POWERPROJ-A1

```yaml
id: EXP-POWERPROJ-001                 # ledger P1526 / RT-1476-POWERPROJ-A1
hypothesis: >
  The backward-3-sum quotient algebra A has dim_{F_p} A = O(q^{beta'}) with beta' < 3/10,
  and membership is certifiable by O(dim A) Bostan–Schost power projections, giving
  membership-query exponent alpha < 3/2 and, via RT-1476, a sub-rho single-target
  RELATION+LA stage (2/5) — pending DESCENT-EXP-A3 confirming descent <= q^{1/5}.
null_hypothesis: >
  dim A = Theta(q) (generic Bezout, no RT-1485-style fiber collapse off the Kummer
  companion), so alpha >= 1 with no sub-rho window at m=5; the trace-side backend is no
  cheaper than the subresultant backend already measured.
target_family: ordinary prime-order E/F_p, j != 0,1728, non-anomalous, large embedding degree
sizes: {p: [1009, 65521, 16769023]}   # three toy sizes, q ~ L^5
seeds: [20260718, 20260719, 20260720]
factor_base: L = q^{1/5} x-coordinates on the line (RT-1476 model)
primitive: Shoup transposition principle / Bostan–Schost power projection of M_t on A
measure: r_eff(q) = #power sums to separate member from non-member; beta' = dlog r_eff/dlog q
positive_control: RT-1485 Kummer-companion fixture (known constant fibers <= 4)
negative_control: random dense trivariate system of equal total degree (expect r_eff=Theta(q))
promotion_gate: beta' < 0.3 on all three sizes AND DESCENT-EXP-A3 gives gamma_desc <= 1/5
falsification: beta' >= 0.3 on any size -> scoped NEGATIVE closing the trace-side m=5 backend
verifier: independent recompute of dim A, M_t traces, and full S5=0 on every accepted witness
inference: {requested_policy: <handoff>, resolved_model: <manifest>, fallback_used: <bool>}
```
First command:
```bash
sage experiments/ecdlp_prime_field/powerproj_alpha_meter.sage \
  --sizes 1009,65521,16769023 --seeds 20260718,20260719,20260720 \
  --ell 0.2 --out experiments/ecdlp_prime_field/powerproj_alpha.json
```

### 3.2 FOURIERMUKAI-B2

```yaml
id: EXP-FOURIERMUKAI-001              # ledger P1530 / FOURIERMUKAI-B2
hypothesis: >
  The Fourier–Mukai / Poincaré-kernel bilinear target label on E yields a factor-base
  incidence matrix of rank >= B-1 that strictly exceeds matched F_p-linear-label,
  random-label, and Weil-pairing-only controls — i.e. the first NONLINEAR label to escape
  the LINLABEL-UNIFIED-D3 (P1525) barrier.
null_hypothesis: >
  The FM label factors through the Weil pairing (order-n character), giving no factor-base
  rank surplus (MOV boundary) or bounded rank o(B); it extends D3 rather than escaping it.
target_family: ordinary prime-order E/F_p, j != 0,1728, F_p-rational dual and Poincaré bundle
sizes: {p: [271, 499, 787]}           # PO96 fixtures for direct ledger comparability
seeds: [20260718, 20260719, 20260720]
factor_base: B ~ q^{1/5} points; FM images O(F_i - O)
primitive: exact Poincaré/theta pairing evaluation as a nonlinear factor-base feature
measure: rank of the FM-label incidence vs (a) F_p-linear PO96D label, (b) random label,
         (c) Weil-pairing-only label; plus a reducibility test to the Weil pairing
positive_control: an APOLARITY/Waring nonlinear label known rank-productive on the fixture
negative_control: the linear PO96D label q2-[k]phi*q1 (expect bounded rank)
promotion_gate: FM rank >= B-1 strictly above all three controls on all three fixtures AND
                not Weil-pairing-reducible
falsification: rank o(B), control-matched, or Weil-reducible -> scoped NEGATIVE extending
               LINLABEL-UNIFIED-D3 to Fourier–Mukai kernels
verifier: independent recompute of every Poincaré-pairing value and every reported rank
inference: {requested_policy: <handoff>, resolved_model: <manifest>, fallback_used: <bool>}
```
First command:
```bash
sage experiments/ecdlp_isogeny/fourier_mukai_label_rank.sage \
  --fixtures 271,499,787 --seeds 20260718,20260719,20260720 \
  --ell 0.2 --controls linear,random,weilpairing \
  --out experiments/ecdlp_isogeny/fm_label_rank.json
```

### 3.3 ARBOREAL-C1

```yaml
id: EXP-ARBOREAL-001                  # ledger P1532 / ARBOREAL-C1
hypothesis: >
  For some ordinary prime-order E/F_p the level-ell arboreal Galois image of the
  multiplication/Lattes preimage tree is NON-maximal and carries a tree invariant with
  positive mutual information about the scalar k, enabling sub-sqrt(q) recovery.
null_hypothesis: >
  The arboreal image is maximal (= Aut(T_ell)) with zero k-mutual-information (Jones/Odoni
  genericity), so no tree invariant leaks k beyond Pohlig–Hellman -> exponent >= 1/2.
target_family: ordinary non-CM prime-order E/F_p, j != 0,1728
sizes: {p: [101, 1009, 65521]}
seeds: [20260718, 20260719, 20260720]
levels: {ell: [1, 2, 3, 4]}
primitive: division-polynomial preimage tree; Frobenius/arboreal image; MI(tree invariant; k)
measure: |rho(Gal)| / |Aut(T_ell)| and mutual information I(invariant; k) vs q
positive_control: a CM curve with known small arboreal image
negative_control: random ordinary curve (expect maximal image, zero MI)
promotion_gate: non-maximal image AND I(invariant;k) > 0 with favorable scaling on all sizes
falsification: maximal image / zero MI across sizes -> scoped NEGATIVE feeding ARBOREAL-MAX-D3
verifier: independent recompute of image order and MI on every fixture
inference: {requested_policy: <handoff>, resolved_model: <manifest>, fallback_used: <bool>}
```
First command:
```bash
sage experiments/ecdlp_prime_field/arboreal_image_leakage.sage \
  --sizes 101,1009,65521 --levels 1,2,3,4 --seeds 20260718,20260719,20260720 \
  --out experiments/ecdlp_prime_field/arboreal_leakage.json
```

---

## 4. Red-team: are the three winners disguised repetitions or cost-negative?

**POWERPROJ-A1 — "this is just batch2/A1 subresultant with different words."**
Rebuttal: the *measured quantity differs*. Subresultant PRS reads the **degree** of the
first nonzero subresultant (β, primal, sensitive to solution *spread*); power projection
reads the **number of independent traces** to certify membership (β', dual, sensitive to
solution *count*). RT-1485's constant fibers bound the *count*, not the *degree*, so the two
meters can disagree, and the subresultant negative does **not** imply the power-projection
negative. **But** the honest cost risk is real: if `dim A = Θ(q)` generically, the dual
stream is also `Θ(q)` and `α≥1`; and building `M_t` may itself cost `Θ(deg)`, hiding the
exponent in setup — the experiment must charge `M_t` construction. Verdict: **not a
duplicate; genuine cost risk, explicitly metered.** Winner survives as a sharper meter on
the binding gate, not a claimed break.

**FOURIERMUKAI-B2 — "FM on E is the Weil pairing; this is MOV, an order-only closed
channel."** Rebuttal: that is precisely the **stated likely obstruction and the null
hypothesis**. The candidate is not asserting a break; it is the **one constructible probe
of the exact loophole** LINLABEL-UNIFIED-D3 leaves open (nonlinear labels), against the
ledger's own PO96 fixtures with a Weil-pairing-reducibility control built into the design.
If it collapses, it **extends the barrier** (a genuine ledger advance); if it does not, it
is the first escaping nonlinear label. Cost honesty: no exponent is claimed before the rank
gate; the contract charges nothing until rank `≥B−1` above controls is demonstrated.
Verdict: **not cost-negative by construction — it is gated on a rank pre-flight** and
advances the frontier in either outcome. Residual risk: FM-label evaluation cost itself
must be charged (theta/pairing evaluation is `polylog`, acceptable).

**ARBOREAL-C1 — "isogeny/functional-graph maximality is already in the ledger (PO96Z);
this is a renamed no-gain."** Rebuttal: PO96Z observed **geometric** functional-graph
conjugacy; ARBOREAL computes the **Galois image** of the preimage tree, which is the object
that actually governs *computable* leakage — a different quantity that PO96Z did not
measure. The near-certain negative (arboreal maximality, D3) is acknowledged up front, and
the candidate's value is a **clean, exactly-verifiable** mutual-information probe that
converts a geometric hint into a Galois-theoretic barrier. Cost honesty: the tree is built
to bounded level `ℓ=polylog`, so the probe is cheap; no break is claimed, only a
leakage-or-barrier dichotomy. Verdict: **not a rename; a distinct object with a decisive
toy verifier**, most likely resolving into the ARBOREAL-MAX-D3 barrier.

**Cross-cutting red-team.** All three winners share the program's structural honesty
requirement: (i) POWERPROJ's relation/LA win is **conditional on DESCENT-EXP-A3** — no
single-target sub-rho claim is admissible until `γ_desc ≤ 1/5` is separately measured;
(ii) FOURIERMUKAI and ARBOREAL are **gated on pre-flight rank / mutual-information** and
claim nothing before it; (iii) every witness is independently re-verified. None is presented
as a break. The batch5 thesis is deliberately modest and matches the saturated state of the
ledger: after six reports the *mechanism* space is essentially mined, so the highest-value
moves are (a) a **new dual-side meter** on the single binding gate (RT-1476), (b) the **one
constructible probe** of the surviving nonlinear-label frontier (P1525), and (c) three
**barriers** (ASYMPSPEC-D1, MATUNION-INDEP-D2, ARBOREAL-MAX-D3) that would convert the most
likely negatives into reusable impossibility statements.

---

## 4b. Literature-verification addendum (primary-source check)

An independent primary-source pass resolved the six load-bearing novelty claims. Net:
**Seeds 4/5/6 (MATUNION, ASYMPSPEC, FREEPROB) have no identifiable prior application**
(NOVELTY-UNVERIFIED = plausibly novel, unconfirmed); **Seed 1 (POWERPROJ)** is a narrow,
likely-novel recombination; **Seeds 2/3 (MAHLER, ARBOREAL)** face **known theorems that
argue against feasibility** — retained precisely as sharp negatives / barriers.

- **POWERPROJ-A1.** Power projection / transposition principle: Shoup 1994/1999;
  Bostan–Salvy–Schost; Kaltofen–Shoup 1998; Kedlaya–Umans 2011. **Key finding:** power
  projection is *already used in ECDLP index calculus* — but for the **Frobenius /
  linear-algebra step** (Kaltofen–Shoup automorphism projection on subfield/Koblitz
  curves), **not** as a root-membership test. Eliminant-avoiding resultant over `F_q`
  exists (arXiv 2302.08891) but is not framed as a power-sum signature match. The **narrow
  gap** (membership via Newton power-sum signature of the backward-3-sum ideal without
  materializing the eliminant) is not found — label **LITERATURE-ADJACENT** stands, with
  the distinction now sharpened: prior EC use is the LA step, not membership.
- **MAHLER-B1.** Lauter–Stange (EDS↔ECDLP equivalence, eprint 2008/099, 2008/444); Ward;
  Stange; Christol; Adamczewski–Bell. **Effective barrier, not mere absence:** over `F_p`
  the `x([k]P)` sequence is (eventually) periodic with period tied to `ord(P)`, so its
  automaton state-complexity is `Ω(ord P)=Ω(q)` — automatic only trivially; Christol ties
  non-trivial automaticity to algebraic power series, and recurrence value-sets are
  non-automatic except trivially. Confirms the near-certain kill.
- **ARBOREAL-C1 / -MAX-D3.** Odoni; Jones; Pink; **Serre open-image**. The preimage tree
  is the `m`-adic Tate tower; generic image `GL_2` ⇒ no `k`-leakage. Confirms D3 = Serre.
- **MATUNION-A2 / -INDEP-D2.** Nash-Williams 1961; Edmonds (matroid union); Kaiser
  (tree-packing, arXiv 0911.2809); large-prime cycle IC (Lenstra–Manasse;
  Gaudry–Thomé–Nagao). **NOVELTY-UNVERIFIED — no prior found** for matroid-union
  enrichment; genuinely open, modulo the packing→relation-count model (which D2 predicts
  fails via shared arithmetic).
- **ASYMPSPEC-D1.** Strassen 1988; Christandl–Vrana–Zuiddam (arXiv 1709.07851); support ≡
  quantum functionals. **NOVELTY-UNVERIFIED — no ECDLP/IC application.** Speculative:
  requires casting Semaev as a tensor *family* with a defined degeneration order before the
  spectral points bite.
- **FREEPROB-C3.** Voiculescu; free-additive-convolution universality; structured-matrix
  concentration (arXiv 2601.08111). **NOVELTY-UNVERIFIED — no prior.** Real modeling
  obstacle (strengthens the stated kill): IC relation matrices are sparse, structured, and
  solved *exactly over `F_ℓ`*; RMT universality assumes rotationally-invariant real/complex
  ensembles, so its hypotheses fail and "low-rank sketch of membership over `F_ℓ`" has no
  obvious meaning. Premise needs justification before pursuit — **lowest-priority keep.**
- **MOTIVIC-B3 / COHENLENSTRA-C2.** Not separately re-verified beyond the standard
  Denef–Loeser / Cohen–Lenstra / Kohel references cited inline; both carry explicit
  count-only / constant-only obstructions and are retained as weak probes.

**Effect on ranking:** unchanged winners. MATUNION-A2 rises in literature-novelty
confidence (L: 3→4) but its `E`/exponent risk (shared-arithmetic non-independence, D2) is
unchanged; POWERPROJ-A1 and ARBOREAL-C1 keep their scores with sharper distinctions;
FREEPROB-C3 is confirmed weakest.

## 5. Claim discipline

Everything above is CONJECTURE/HYPOTHESIS/OPEN. No relation, rank, exponent, or ECDLP
recovery is claimed. Toy-scale evidence, when produced, will be scoped to the tested curves,
parameters, backend, and budget, and will never be presented as crypto-scale. A failed
winner is a **scoped negative result** (e.g. "the trace-side m=5 backward-state backend has
`β'≥0.3` on `p∈{1009,65521,16769023}`"), not evidence that prime-field ECDLP cannot be
improved. The two live conditional theorems RT-1472 (`δ>1/4`) and RT-1476 (`α<3/2`) remain
**open and unrealized**; batch5 supplies sharper meters and candidate barriers for them, not
a crossing.

*Ledger IDs proposed (uncommitted): P1526–P1537. This report is an uncommitted file; do not
commit unless asked.*
