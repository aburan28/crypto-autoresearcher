# Idea Generation — ECDLP over ordinary prime fields — 2026-07-18 batch6

Research Director, empirical cryptanalysis laboratory.
Scope: generated toy curves, public benchmark instances, synthetic data only. No
wallets, production keys, accounts, or unauthorized systems.

Primary target: a non-generic algorithm whose **complete** cost beats the
single-target Pollard-rho `0.886*sqrt(n)` baseline. Toy correctness, a new
coordinate system, a relation certificate, faster preprocessing, or a solver swap
alone is not a breakthrough.

---

## 0. Required-input review and machine-readable inventory

Reviewed in full before proposing:

1. `/Volumes/Volume/git/autolab/research_ledger.md` (2478 lines: ~140 open-frontier
   bullets; active hypotheses `SHA1-H001..H004`; the two conditional rho-crossing
   gates `ECFG-RT-1472`, `ECFG-RT-1476`; ~120 `PO96*` correspondence/Prym frontier
   entries; the low-term relation-collector and source-scheduling lanes).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md`
   (720 lines: `ECFG-001..043` functional-graph selector hypotheses — almost all
   NEGATIVE/OBSERVATION; `ECFG-NR-1506..1508`; and the active IC frontier
   `ECFG-P1509..P1513` implementing `IDEA-049/052/058/068/115/117`).
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md`
   (`PO-transfer-001..006`: same-field isogeny closed; twist positive control;
   scalar-Weil diagnostic-only; bielliptic/trielliptic cofiber negatives).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json`
   (10 primary sources: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013;
   FHJRV 2014 symmetrized; Kousidis–Wiemers 2015 first-fall-degree; Karabina 2015;
   Amadori–Pintore–Sala 2017 prime-field; McGuire–Mueller 2017 Gröbner-free;
   Trimoska–Ionica–Dequen 2020 SAT).
5. Current experiment contracts (`p1497..p1501`, `p1510..p1513`), negative-result
   tables (`ECFG-*`, `PO96*`, `PO-transfer-*`), open-frontier questions, and the
   literature maps embedded in (1) and (2).
6. All seven prior idea reports (the anti-duplication corpus):
   `idea_generation_20260717.md`, `..._20260717_batch2.md`, `..._20260718.md`,
   `..._20260718_batch2.md`, `..._20260718_batch3.md`, `..._20260718_batch4.md`,
   `..._20260718_batch5.md`.

**Entries reviewed:** the two ledgers plus the transfer doc contribute on the order
of **900+ distinct record IDs**; the seven prior reports contribute **84 catalogued
candidates** (12 per report × 7). **ID families covered:** `RQ-*`, `IDEA-*`
(incl. `IDEA-049/052/058/068/115/117`), `H-*`, `EXP-*`, `RUN-*`, `EV-*`, `DEC-*`,
`TASK-*`, `KN-*`, the `P-series` (`P1385..P1537`), the `PO-series` (`PO36..PO96AB-R1-F5`
and `PO-transfer-001..006`), the `ECFG-series` (`ECFG-001..043`, `ECFG-NR-1506..1508`,
`ECFG-P1509..P1513`), the `RT-series` (`RT-1471/1472/1476`), the `F5-series`
(`F5D0..F5F7`), and `SHA1-H001..H004`.

### Extracted dimensions (condensed inventory of the exploited-structure axes)

| Axis | Values already occupied in the ledger + 7 reports |
|---|---|
| mechanism | Semaev/summation membership; point-decomposition IC; large-prime/graph enrichment; correspondence/Prym/Jacobian transfer; functional-graph (ECFG) selectors; source-scheduled low-term relation collectors; endomorphism/CM transfer; scalar-Weil/Kummer/theta charts |
| representation | short-Weierstrass x-line; Kummer/theta (level 2, 3); split genus-2/3 covers; trace-zero/Weil restriction; canonical/Serre–Tate lift; Cartier–Manin/crystalline; formal group; tensor-train/border-rank; SOS/apolarity/syzygy; Mahler/automatic; Fourier–Mukai kernel; arboreal tree; matroid/graphon |
| exploited structure | order/trace invariants; addition-law algebra; torsion/level structure; isogeny-class geometry; class-group/CM; graph cycle-space/homology/matroid; additive-combinatorial energy; spectral gap |
| relation-generation | Gröbner/resultant/SAT/crossbred; symmetrized Semaev; rational-map/cover factor base; two/three-large-prime; native cover divisors; source-scheduled row emission |
| compression | negation; symmetrization; large-prime graphs; landmark/cycle ECFG index; border-rank/tensor-train; SOS certificate |
| linear-algebra object | sparse GF(p) relation matrix (`n^{2/5}` at m=5, **not binding**); cycle-incidence; Hom/Fitting module; determinant-of-cohomology |
| target descent | Semaev individual-log; cover push-forward; ECFG reverse index; correspondence label return; descent-tree (batch5 DESCENT-EXP meter) |
| dominant cost | membership/relation-generation query exponent (the binding stage); enrichment `delta`; per-target compiler `Theta(r^3)`; MITM memory |
| outcome | overwhelmingly NEGATIVE / SCOPED-NEGATIVE / OBSERVATION; positives are toy-correctness or amortized-many-target, never single-target complete-cost sub-rho |
| scoped negative boundary | "not a Shoup break"; "generated-fixture boundary"; "amortized not single-target"; "setup-uncharged" |

### The only two live rho-crossing surfaces (unchanged since batch5)

Both are open, unrealized **conditional** theorems; every ledger "below rho" is
amortized-many-target or setup-uncharged. The sparse-LA stage (`n^{2/5}`) is **not**
binding — the **relation/membership-generation** stage is.

- **RT-1472** (`ECFG-RT-1472`): an explicit/honest 2-large-prime summation graph at
  `B=n^{1/5}` needs cycle-space enrichment `delta > 1/4` to push the exponent
  `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)` below `1/2`. Prior meters (3-LP homology, graphic-matroid
  cycle basis, effective-resistance, matroid-union, correlated-peeling) all failed to
  demonstrate `delta > 1/4`.
- **RT-1476** (`ECFG-RT-1476`): a five-term (`m=5`) implicit-membership backend with
  query exponent `alpha < 3/2`, setup `<= L^2`, random-like support, sparse full-rank
  relations. Exact optimum `ell=1/(m+1-alpha)`; `m<=3` impossible, `m=4` needs
  `alpha<1`, `m=5` needs `alpha<3/2`. Strong prior `beta -> 3/2` for the backward-3-sum
  eliminant degree (`P1512-R1`: scalar-linear Chow atomizer closed at `Omega(r^5)`;
  only the **target-specialized nonlinear-circuit exception** survives).

### Meta-finding carried from batch5 (now reconfirmed at batch6)

The **mechanism vocabulary is saturated**: seven reports span ~48 distinct mechanism
lanes and all six task-brief search seeds (Hasse-jet, tropical/Newton-polytope,
output-sensitive incidence, transfer-operator, path-algebra, tensor-network) are
exhausted. batch6 therefore continues the batch4/batch5 discipline: candidates are
drawn from lanes **outside** the ledger vocabulary, weighted toward (a) **exact
measurement primitives** that sharpen the two live gates and (b) **barriers of a
structurally new type** (fine-grained conditional hardness, Deligne/Lang–Weil
point-counting, algebraic-complexity root bounds) that no prior barrier used — every
prior barrier was algebraic (border-rank, slice-rank, Chow-atomizer, class-function,
arboreal-maximality). **No break is claimed. All results are scoped negatives, exact
meters, or barriers.**

---

## 1. Twelve candidates

Groups: **A** conservative extensions · **B** representation changes · **C** high-risk
speculative · **D** negative-theory / barrier. At least six begin outside the ledger's
dominant vocabulary (marked ⊗). Semantic fingerprint `F(C) = (algebraic object,
public operations, hidden structure, info discarded, info retained, relation-gen
primitive, compression primitive, rank mechanism, descent mechanism, dominant cost
exponent)`.

---

## Candidate: BAURSTRASSEN-A1 — Reverse-mode (Baur–Strassen) co-extraction of all m membership witnesses

### One-sentence mechanism
Exploit the fact that reverse-mode differentiation (Baur–Strassen) computes **all**
partial derivatives of one arithmetic circuit at `O(1)×` the circuit's evaluation cost,
to co-extract the m source-witness coordinates of a five-point membership from a single
eliminant evaluation, reducing the witness-extraction cost of subproblem P (stage-3
opening in the RT-1476 backend) below the per-witness re-solve baseline B.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (Baur–Strassen is textbook algebraic complexity; its application as
a **simultaneous Semaev-witness opener** is ledger-absent, but it targets a stage the
ledger already shows is **not** the binding one).

### Semantic fingerprint
(algebraic object: the arithmetic circuit computing the m=5 eliminant `S3`/backward-sum;
public ops: field ×,+, reverse-mode adjoint pass; hidden structure: shared subexpressions
across the m witness coordinates; info discarded: eliminant value once roots are known;
info retained: full gradient = witness tuple; relation-gen primitive: eliminant root +
gradient read-off; compression primitive: subexpression sharing; rank mechanism: unchanged
sparse GF(p) matrix; descent: same Semaev individual-log; dominant cost: **still the
eliminant degree**, unchanged by witness co-extraction).

### Nearest ledger entries
1. `RT-1476-SUBRES-A1` (batch2) — measures the eliminant *degree* `beta`; BS measures the
   *witness-opening* cost given the eliminant, an orthogonal stage.
2. `POWERPROJ-A1` (batch5) — transposed power-projection meters solution *count*; BS meters
   *coordinate recovery*.
3. `ECFG-P1509` Hasse-jet source section — extracts source labels from leading-form ratios;
   BS extracts them from the adjoint circuit. Distinction: BS is target-blind and needs no
   per-endpoint code factoring.
4. `ECFG-P1511-R1` FD-width join — recovers intermediate points after indices fixed; BS
   recovers them by differentiation, not by join planning.
5. `A3` many-target amortization (batch2) — amortizes setup; BS is per-target.

### Nearest literature
Baur & Strassen, "The complexity of partial derivatives" (1983): all first partials at
`<=3×` eval. Kaltofen–Villard transposition/Tellegen principle. **Gap:** none of these
bound the *eliminant degree*, which the ledger (`P1512-R1`) already fixes at `Omega(r^5)`
for scalar-linear atomizers; BS cannot lower a degree it only differentiates.

### Target family
Ordinary `E/F_p`, prime order `n | #E(F_p)`, non-anomalous, non-supersingular, embedding
degree large. Excluded: `j in {0,1728}`, CM by small discriminant, singular reductions.

### Full algorithmic path
1. factor base `B = {P : x(P) in [0,L)}`, `L=q^{1/5}`; 2. relation gen: draw random
`R=aP+bQ`, form the m=5 membership circuit, evaluate + one reverse pass to test membership
and read witnesses simultaneously; 3. witness verify: independent EC re-addition of the
opened tuple; 4. relation prob: unchanged from RT-1476 (`min(1,L^m/q)`); 5. matrix `Theta(L)`
rows, density `Theta(m)`, GF(p); 6. factor-log calibration standard; 7. descent: same
backend on the target row; 8. offline: circuit synthesis once; online: eval+adjoint per
attempt; 9. memory `Theta(circuit size)`, embarrassingly parallel over attempts.

### Cost model
Per attempt `c_eval + c_adjoint = O(1)*deg_circuit` field ops. Because `deg_circuit`
inherits the eliminant degree, total exponent = RT-1476's, **unchanged**: BS removes a
constant `m` factor on witness opening, not the degree exponent. vs rho `1/2`; vs BSGS
`1/2`; vs RT-1476 skeleton: identical exponent, `<= m×` constant improvement.

### Why the existing negative results do not already kill it
It avoids the per-witness re-solve that a naive backend pays; the new operation is the
adjoint pass. But it does **not** avoid the `Omega(r^5)`/`beta->3/2` degree obstruction.

### Likely fatal obstruction
The binding cost is eliminant *degree*, not witness *opening*; BS is a constant-factor win
on the wrong stage. Almost certainly cannot cross `alpha=3/2`.

### Minimal falsifying experiment
Toy `p in {1009, 4099, 40009}`, seeds `s=1..5`, ordinary prime-order controls; positive
control = a curve where witnesses are known; negative control = random non-membership
circuits. Measure `(c_eval+c_adjoint)/c_eval` and confirm it is `Theta(1)` while the
degree exponent is unchanged.

### Quantitative promotion gate
Reject unless the **measured total membership exponent** (degree × opening) drops below
`3/2` in `L=q^{1/5}` on `>=3` sizes. Correctness/constant-factor wins do not promote.

### Proof track
Theorem: reverse-mode opening of the m=5 eliminant circuit is `O(1)×` its evaluation and
returns the unique source tuple on the successful-membership locus.

### Disproof track
Measure eliminant degree growth (already `beta->3/2`); if opening is `Theta(1)` but degree
unchanged, the exponent is untouched — kills the promotion claim.

### Reproduction artifact
contract `experiment_contract_p1538_baur_strassen_witness_opener.md`; impl
`tasks/ecdlp_index_calculus/p1538_bs_witness_opener.py`; result
`p1538_bs_witness_opener.json`; audit `p1538_bs_witness_opener_audit.json`; ledger
`ECFG-P1538`.

---

## Candidate: HDX-COBOUNDARY-A2 ⊗ — Coboundary-expansion δ-meter for the m-uniform relation hypergraph (RT-1472)

### One-sentence mechanism
Exploit the **cosystolic/coboundary expansion** constant `lambda` of the m-uniform
**relation hypergraph** (whose faces are membership-valid tuples) to lower-bound the
independent-cycle yield `delta` of subproblem P (2-large-prime enrichment) below the
naive random-graph estimate, targeting `delta > 1/4`.

### Status
HYPOTHESIS

### Novelty classification
NOVELTY-UNVERIFIED (high-dimensional-expander/coboundary expansion has **not** appeared;
distinct from the report2 3-LP *simplicial homology* meter, which computed `H_1` of a
**fixed** 3-large-prime complex, and from the batch3 effective-resistance and batch5
matroid-union meters, which are 1-dimensional graph invariants).

### Semantic fingerprint
(object: m-uniform relation hypergraph / simplicial complex on the factor base; public ops:
face enumeration via membership, coboundary map `delta_1`; hidden structure: higher
isoperimetry of the valid-tuple complex; discarded: individual face identities; retained:
`Z_2`/`F_p` coboundary norm ratio; relation-gen: cocycle = independent relation batch;
compression: cosystole basis; rank mechanism: cosystolic expansion `lambda` lower-bounds
usable rank; descent: standard; dominant cost exponent: `delta` via `lambda`).

### Nearest ledger entries
1. report2 `A1` 3-LP hypergraph homology — fixed complex, `H_1` dimension count; HDX gives a
   *quantitative expansion constant*, not a Betti number.
2. batch5 `MATUNION-A2` matroid-union — 1-dim graphic-matroid packing; HDX is the m-dim
   analogue and does not assume graphic structure.
3. batch3 `EFFRES-A2` effective-resistance sparsifier — spectral 1-dim; HDX is topological
   m-dim.
4. batch2 `RT-1472-CYCLEMAT-A2` cycle-basis — graph cycle space; HDX cocycle space is a
   strict generalization.
5. `ECFG-RT-1472` gate itself — HDX is a candidate `delta`-lower-bound generator for it.

### Nearest literature
Lubotzky–Kaufman, Evra–Kaufman (cosystolic expansion of Ramanujan complexes);
Kaufman–Oppenheim (local-spectral → global expansion). **Gap:** these bound expansion of
*designed* complexes (buildings, coset geometries); no result computes the coboundary
constant of an **arithmetically-defined Semaev relation complex**, and none connects it to
a large-prime `delta` for ECDLP.

### Target family
Ordinary prime-order `E/F_p`; `B=q^{1/5}`; excluded special-torsion / CM curves where the
relation complex degenerates.

### Full algorithmic path
1. factor base `B`; 2. relations = m-faces (membership-valid tuples) built by Semaev test;
3. witness verify by EC re-addition; 4. relation prob unchanged; 5. cocycle space over
`F_p`, `dim = delta*|edges|`; 6. calibration standard; 7. descent standard; 8. offline:
complex construction; online: cocycle solve; 9. memory `Theta(#faces)`.

### Cost model
`delta` is set by `lambda`; if `lambda` bounded below by a positive constant on the honest
complex, `delta = Theta(1)` may exceed `1/4`. Setup `= #m-faces = Theta(L^m/q * binom(...))`.
Compare exponent `max(2ℓ,1−ℓ,1+1/5−2ℓ)` under measured `delta` vs rho `1/2`.

### Why the existing negative results do not already kill it
Prior δ meters were 1-dimensional (graph cycle space, resistance, matroid). Coboundary
expansion is a genuinely higher-dimensional isoperimetric quantity; the D2 two-graph
independence barrier (batch5) is a statement about **two** 1-dim graphs, not about the
m-dim complex's cosystole.

### Likely fatal obstruction
Arithmetically-defined complexes over `F_p` are almost surely **not** expanders
(coboundary constant `-> 0` with size), so `delta` collapses to the random-graph value
`0`. See barrier LANGWEIL-SUPPLY-D2 below.

### Minimal falsifying experiment
Toy `p in {1009, 4099, 40009}`, seeds `1..5`; build the m=3 and m=4 relation complexes
exactly (exhaustive at toy scale); measure `lambda` (smallest nonzero coboundary singular
value) and `delta`. Positive control: a designed expander complex of matched size.
Negative control: Erdős–Rényi random m-uniform hypergraph of matched density.

### Quantitative promotion gate
Reject unless measured `delta` exceeds `1/4` **and** `lambda` is bounded away from 0 as the
toy size grows across `>=3` sizes with the exponent trend crossing `1/2`.

### Proof track
Theorem: the honest Semaev relation complex has cosystolic expansion `>= lambda_0 > 0`,
implying `delta >= f(lambda_0) > 1/4`.

### Disproof track
Measure `lambda -> 0` (near-certain) → `delta = 0`; kills the enrichment hope and *confirms*
LANGWEIL-SUPPLY-D2.

### Reproduction artifact
contract `experiment_contract_p1539_hdx_coboundary_delta_meter.md`; impl
`tasks/ecdlp_index_calculus/p1539_hdx_coboundary_delta.py`; result JSON + audit; ledger
`ECFG-P1539`.

---

## Candidate: LANGWEIL-METER-A3 ⊗ — Exact Deligne/Lang–Weil relation-supply meter for the Semaev variety

### One-sentence mechanism
Exploit **Deligne/Lang–Weil point-count bounds** on the m-th Semaev hypersurface to replace
the heuristic smoothness/occupancy estimate of the relation-probability stage with an
**exact** `F_p`-point count `|V_m(F_p)| = p^{m-2} + O(p^{m-2-1/2})`, pinning the true
relation-supply exponent and its error bar for both live gates.

### Status
HYPOTHESIS (measurement primitive)

### Novelty classification
LEDGER-NEW as an **exact cohomological meter** (the ledger's occupancy `P1471/P1472` were
**empirical hit counts** with observed/expected ratios `0.829/0.884`; no entry computes the
Weil-bounded point count of the variety itself).

### Semantic fingerprint
(object: Semaev hypersurface `V_m subset A^m` cut by `S_m=0`; public ops: point counting,
zeta/Weil bound, singular-locus test; hidden structure: `l`-adic cohomology dimensions of
`V_m`; discarded: individual points; retained: exact count + variance; relation-gen: the
supply this feeds is unchanged; compression: none; rank mechanism: supply → expected rank;
descent: standard; dominant cost exponent: sharpens the *supply* side, not the query side).

### Nearest ledger entries
1. `ECFG-RT-1472` occupancy exponent boundary (`P1472`) — empirical hit ratio; A3 is the exact
   count.
2. batch3 `ENERGY-D1` additive-energy ceiling — bounds low-weight relation supply by
   sum-product; A3 bounds it by point-counting (independent method).
3. `P1471` occupancy — empirical; A3 exact.
4. batch2 `RT-1476-SUBRES-A1` — query side; A3 is supply side.
5. Kousidis–Wiemers first-fall-degree — bounds solving degree; A3 bounds relation supply.

### Nearest literature
Lang–Weil (1954) point-count bound; Deligne Weil II; Rojas/Cafure–Matera explicit
`F_p`-variety point-count bounds. FHJRV 2014 symmetrized Semaev. **Gap:** explicit
Lang–Weil constants for the *symmetrized* m=5 Semaev variety, and whether the error term
`O(p^{m-2-1/2})` is large enough to change the supply exponent, are uncomputed.

### Target family
Ordinary prime-order `E/F_p`; all m in {3,4,5}; exclude `V_m` singular-dominated toy primes.

### Full algorithmic path
Measurement-only for supply, then plugged into the existing RT-1472/RT-1476 skeleton:
1. build `V_m`; 2. exact toy point-count + smooth-locus count; 3. compare to `p^{m-2}`;
4. relation prob = smooth-point-density → exact supply exponent; 5–7 inherited from the
skeleton; 8. offline: none; 9. memory negligible.

### Cost model
Toy-exact counting `O(p^{m-1})` (toy only); the deliverable is the *exponent constant*
feeding rho comparison, not a runnable attack. Compares the **corrected** supply exponent
against the heuristic one used in RT-1472/RT-1476.

### Why the existing negative results do not already kill it
It is not itself an attack; it removes the heuristic-smoothness assumption that every prior
"below rho" supply estimate silently used — potentially *tightening* the barriers.

### Likely fatal obstruction
The count almost certainly matches the heuristic to leading order (`p^{m-2}`), so it
**confirms** rather than breaks — value is in closing an assumption, not crossing `1/2`.

### Minimal falsifying experiment
Toy `p in {101,211,431,809,1601,4099}`, seeds `1..5`; exact count `|V_m(F_p)|` and smooth
locus for m=3,4,5; compare to `p^{m-2}` and to empirical occupancy `P1471`. Positive control:
a variety with known extra cohomology (elevated count). Negative control: a smooth complete
intersection with predicted count.

### Quantitative promotion gate
This is a **barrier-grade meter**: "promotion" = a *measured* supply exponent that changes
the RT-1472/RT-1476 optimum by a computable amount. If the corrected exponent still forbids
`delta>1/4` / `alpha<3/2`, record as a tightened barrier (LANGWEIL-SUPPLY-D2).

### Proof track
Theorem: `|V_m^{smooth}(F_p)| = c_m p^{m-2}(1+O(p^{-1/2}))` with explicit `c_m`, fixing the
supply exponent.

### Disproof track
An anomalously large count on a curve family would signal exploitable extra structure — a
positive lead worth escalating.

### Reproduction artifact
contract `experiment_contract_p1540_langweil_supply_meter.md`; impl
`tasks/ecdlp_index_calculus/p1540_langweil_supply.py`; result + audit; ledger `ECFG-P1540`.

---

## Candidate: COHNUMANS-B1 ⊗ — Group-algebra (triple-product-property) convolution embedding of m-point decomposition

### One-sentence mechanism
Exploit a **Cohn–Umans triple-product-property (TPP) embedding** of the elliptic
addition/decomposition relation into a finite group algebra, so that testing all m-point
decompositions of a target becomes a single **group-algebra convolution** evaluated by
FFT, reducing membership-query cost C of subproblem P below the resultant/Gröbner backend B.

### Status
CONJECTURE

### Novelty classification
NOVELTY-UNVERIFIED (Cohn–Umans TPP embedding has **not** appeared; distinct from
report3 `B4` Semaev **border-rank**, which is a *lower bound* on the fixed decomposition
tensor — this is an *upper-bound construction* via a different algebra; distinct from
report1 `B2` tensor-train, which contracts the fixed tensor rather than re-embedding it).

### Semantic fingerprint
(object: group algebra `F_p[G]` with a TPP triple `(S,T,U)` encoding decomposition; public
ops: convolution/FFT in `F_p[G]`, character transform; hidden structure: the decomposition
tensor's embeddability as a sub-permutation of group multiplication; discarded: geometric
coordinates; retained: convolution support = valid decompositions; relation-gen: read
nonzero convolution coefficients; compression: character-basis diagonalization; rank
mechanism: standard sparse GF(p); descent: convolution against the target; dominant cost:
`|G|` and TPP capacity vs the m-point count).

### Nearest ledger entries
1. report3 `B4` Semaev border-rank — lower bound on the SAME tensor; B1 seeks a construction
   in a different algebra.
2. report1 `B2` tensor-train contraction — contracts the fixed Semaev operator; B1 replaces
   the operator by a group convolution.
3. batch3 `C1` holographic/matchgate — matchgate tensor contraction; B1 is a group-algebra
   embedding, a different reduction target.
4. `ECFG-P1510-R1` marked-resultant compiler — output-sensitive resultant FFE; B1 is a
   *non-resultant* backend.
5. batch2 `A3` transposed Kedlaya–Umans — modular composition; B1 is group convolution, not
   polynomial composition.

### Nearest literature
Cohn–Umans (2003) group-theoretic matrix multiplication; Cohn–Kleinberg–Szegedy–Umans (2005)
TPP constructions. **Gap:** no TPP embedding is known for a *nonlinear* elliptic
decomposition tensor; the addition law is not a bilinear map on a vector space, so the
embedding target is unclear — the core risk.

### Target family
Ordinary prime-order `E/F_p`; m in {4,5}; exclude curves with automorphisms that collapse the
would-be TPP triple.

### Full algorithmic path
1. factor base `B`; 2. relation gen: encode `B` and the target into `F_p[G]`; a single
convolution enumerates candidate decompositions; 3. witness verify by EC re-addition;
4. relation prob per convolution support; 5. sparse GF(p) matrix; 6. calibration standard;
7. descent: convolve target against `B`; 8. offline: group + character tables; online:
FFT per target; 9. memory `Theta(|G|)`.

### Cost model
If a TPP triple of capacity `>= (#m-tuples)` embeds in `|G| = q^{gamma}`, convolution costs
`O(|G| log|G|) = O(q^{gamma} polylog)`. Sub-rho requires `gamma < 1/2` at m=5 — the whole
gamble. vs rho `1/2`; vs Semaev-Gröbner backend (superlinear in `L`).

### Why the existing negative results do not already kill it
Border-rank lower bounds (report3 B4, batch5 ASYMPSPEC-D1) constrain the *bilinear* tensor;
a group-algebra embedding is a different computational model whose cost is `|G|`, not tensor
rank. The `Omega(r^5)` Chow-atomizer negative is for *scalar-linear* determinantal atomizers.

### Likely fatal obstruction
The elliptic decomposition relation is genuinely **nonbilinear**; there is likely **no**
TPP triple embedding it, and any `|G|` large enough to host the m-tuple count will have
`gamma >= 1/2` (see CIRCUIT-TAU-D3). Near-certain collapse.

### Minimal falsifying experiment
Toy `p in {101,211,431}`, m=4; attempt to construct a TPP triple for the exact decomposition
relation; measure realized capacity vs `#m-tuples` and `gamma`. Positive control: matrix-mult
TPP of matched size (known to embed). Negative control: a random nonbilinear tensor (expected
non-embeddable).

### Quantitative promotion gate
Reject unless a TPP embedding exists with `gamma < 1/2` and the measured convolution exponent
crosses `1/2` on `>=3` sizes. Existence of *any* embedding at `gamma>=1/2` is a scoped
negative.

### Proof track
Theorem: there is a group `G`, `|G|=q^{gamma}`, `gamma<1/2`, and a TPP triple realizing the
m=5 elliptic decomposition tensor.

### Disproof track
Capacity lower bound: any group hosting `Theta(q)` decompositions needs `|G|=Omega(q)`,
forcing `gamma>=1`; a counting argument likely closes this immediately.

### Reproduction artifact
contract `experiment_contract_p1541_cohn_umans_tpp_backend.md`; impl
`tasks/ecdlp_index_calculus/p1541_cohn_umans_tpp.py`; result + audit; ledger `ECFG-P1541`.

---

## Candidate: PICARDFUCHS-B2 ⊗ — Gauss–Manin / holonomic constructive descent

### One-sentence mechanism
Exploit the **Picard–Fuchs / Gauss–Manin connection** of the family of Semaev fibers over
the target parameter to represent the individual-logarithm descent as **analytic
continuation of a flat holonomic section**, replacing per-target re-solving with a
`D`-finite recurrence of bounded order.

### Status
CONJECTURE

### Novelty classification
NOVELTY-UNVERIFIED (Gauss–Manin/Picard–Fuchs as a **constructive descent representation**
is ledger-absent; distinct from batch2 `C2` p-curvature/arithmetic-holonomy, which used the
mod-p reduction of such a connection as a *barrier* (order-only), not as a descent engine;
distinct from report1 `C2` Lattès transfer-operator spectral, which is a dynamical operator,
not a flat connection).

### Semantic fingerprint
(object: Gauss–Manin connection on `H^1` of the Semaev fiber family; public ops: connection
matrix apply, holonomic recurrence step; hidden structure: `D`-finiteness of the
membership-count-vs-target function; discarded: geometric fiber; retained: flat section /
recurrence coefficients; relation-gen: continuation gives decompositions along a path;
compression: bounded connection rank; rank mechanism: standard; descent: analytic
continuation; dominant cost: connection rank × path length).

### Nearest ledger entries
1. batch2 `C2` p-curvature — same connection, used as an order-only **barrier**; B2 is
   constructive.
2. batch2 `C3` Coleman–Gross p-adic height — p-adic pairing lattice; B2 is a
   characteristic-p flat section.
3. report1 `C2` Lattès transfer-operator — dynamical spectrum; B2 is de Rham cohomology.
4. batch3 `A3` composed-resultant power-sum (`C`-finite recurrence) — 1-var C-finite; B2 is a
   multivariate `D`-finite connection.
5. `ECFG-P1513` shared bivariate common-norm — a resultant identity; B2 is a differential one.

### Nearest literature
Katz, "Nilpotent connections and the monodromy theorem"; Bostan–Chyzak–van der Hoeven
creative-telescoping for holonomic functions. **Gap:** in characteristic `p` the Gauss–Manin
connection has p-curvature obstructions (Grothendieck–Katz); whether a *usable* horizontal
section exists mod p for the Semaev family is exactly the open question, and p-curvature
(batch2 C2) suggests it generically does **not**.

### Target family
Ordinary `E/F_p`, prime order; exclude curves where the Semaev family degenerates
(supersingular, `j in {0,1728}`).

### Full algorithmic path
1. factor base `B`; 2. relation gen: compute the connection, continue a flat section from a
known fiber to the target fiber, read decompositions; 3. verify by EC re-addition; 4. prob
per continuation; 5. sparse matrix standard; 6–7 standard/continuation descent; 8. offline:
connection matrix; online: recurrence steps; 9. memory `Theta(rank)`.

### Cost model
If connection rank `= r_0 = O(1)` and path length `polylog`, descent is `polylog(q)` per
target — but p-curvature generically forces the horizontal-section computation back to
`Omega(q)` work. Sub-rho requires a bounded-order **mod-p** recurrence — the gamble.

### Why the existing negative results do not already kill it
p-curvature (batch2 C2) was framed as an order-only *barrier* on a linear representation; B2
asks the constructive question the barrier leaves open — whether a specific flat section is
computable despite generic non-triviality.

### Likely fatal obstruction
Grothendieck–Katz p-curvature: mod p, the Gauss–Manin connection generically has no nonzero
horizontal section, so continuation costs `Omega(q)`; B2 likely reproduces batch2 C2's
barrier.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; compute the Semaev-family connection, its
p-curvature, and attempt a flat section. Positive control: a `D`-finite family with trivial
p-curvature (section exists). Negative control: a generic family (nonzero p-curvature).

### Quantitative promotion gate
Reject unless a bounded-order mod-p recurrence gives per-target descent `polylog(q)` with the
*total* exponent (setup included) crossing `1/2` on `>=3` sizes.

### Proof track
Theorem: the m=5 Semaev-family Gauss–Manin connection has zero p-curvature (equivalently a
full set of mod-p horizontal sections) on a positive-density curve family.

### Disproof track
Compute nonzero p-curvature on the generic family (near-certain) → continuation is `Omega(q)`;
reproduces the batch2 C2 barrier.

### Reproduction artifact
contract `experiment_contract_p1542_gauss_manin_descent.md`; impl
`tasks/ecdlp_index_calculus/p1542_gauss_manin_descent.py`; result + audit; ledger
`ECFG-P1542`.

---

## Candidate: GRAPHON-CUTNORM-B3 ⊗ — Graph-limit (cut-norm) representation of the honest summation graph

### One-sentence mechanism
Exploit the **graphon / cut-norm limit** of the honest 2-large-prime summation graph to
compute its giant-2-core threshold — hence `delta` — directly from a homomorphism-density
functional, rather than by simulating a peeling process.

### Status
HYPOTHESIS

### Novelty classification
NOVELTY-UNVERIFIED, and I flag an **honest overlap** with batch4 `CORRELATED-PEEL-A3`
(Wormald differential-equation peeling of the *dependent* sum-graph). Distinction: A3 tracks a
**specific** peeling trajectory (a lower bound realized by one process); the graphon/cut-norm
functional gives the **threshold itself** as an analytic invariant of the limit object,
independent of any process. If the graphon converges to a rank-1 / constant kernel, `delta`
is pinned exactly.

### Semantic fingerprint
(object: graphon `W: [0,1]^2 -> [0,1]` = limit of the summation graph; public ops:
homomorphism density, cut-norm; hidden structure: the limit kernel's spectrum; discarded:
finite-graph fluctuations; retained: threshold functional; relation-gen: cycle space of the
finite approximant; compression: low-rank kernel; rank mechanism: 2-core → `delta`; descent:
standard; dominant cost: `delta` from the kernel).

### Nearest ledger entries
1. batch4 `CORRELATED-PEEL-A3` — process vs threshold (see distinction above).
2. batch2 `RT-1472-CYCLEMAT-A2` cycle basis — finite combinatorics; B3 is the limit.
3. batch3 `EFFRES-A2` effective resistance — spectral finite; B3 is spectral-of-the-limit.
4. batch5 `MATUNION-A2` matroid union — packing; B3 is density.
5. `ECFG-RT-1472` — B3 is a `delta`-threshold generator for it.

### Nearest literature
Lovász "Large Networks and Graph Limits"; Bollobás–Riordan random-graph 2-core thresholds;
Borgs–Chayes–Lovász cut-norm. **Gap:** the summation graph is **not** exchangeable
(edges are arithmetically correlated), so standard graphon convergence may fail — the
central risk, shared with A3's independence assumption.

### Target family
Ordinary prime-order `E/F_p`; `B=q^{1/5}`; exclude degenerate-torsion families.

### Full algorithmic path
As RT-1472 skeleton with `delta` supplied by the cut-norm threshold; 1. factor base; 2.
relations = summation edges; 3. verify; 4. prob; 5. cycle space `dim = delta|E|`; 6–7
standard; 8/9 negligible offline / `Theta(|E|)` memory.

### Cost model
`delta` from the limit kernel; if the kernel is (near) constant, `delta = 0` at density below
the giant-2-core threshold; sub-rho needs `delta>1/4`. Compare exponent
`max(2ℓ,1−ℓ,1+1/5−2ℓ)` vs rho `1/2`.

### Why the existing negative results do not already kill it
It is a **threshold** method, not a process realization; the batch5 D2 two-graph independence
barrier is about two graphs, not the cut-norm of one honest graph's limit.

### Likely fatal obstruction
Arithmetic edge-correlation likely makes the summation graph converge to a **constant
sub-critical** kernel → `delta=0` (again LANGWEIL-SUPPLY-D2).

### Minimal falsifying experiment
Toy `p` up to exhaustive `binom` counts; build the exact summation graph at `L=q^{1/5}`;
estimate the cut-norm-closest low-rank kernel and its 2-core threshold; compare to the
observed 2-core. Positive control: an Erdős–Rényi graph above threshold. Negative control:
a sub-critical random graph.

### Quantitative promotion gate
Reject unless the measured 2-core `delta` exceeds `1/4` and the exponent trend crosses `1/2`
on `>=3` sizes.

### Proof track
Theorem: the honest `L=q^{1/5}` summation graph is above its giant-2-core threshold with
`delta>1/4`.

### Disproof track
Measure sub-critical `delta=0` (near-certain) → confirms the enrichment gap and D2.

### Reproduction artifact
contract `experiment_contract_p1543_graphon_cutnorm_delta.md`; impl
`tasks/ecdlp_index_calculus/p1543_graphon_cutnorm_delta.py`; result + audit; ledger
`ECFG-P1543`.

---

## Candidate: DML-ORBIT-C1 ⊗ — Dynamical Mordell–Lang orbit-intersection framing

### One-sentence mechanism
Exploit **Dynamical Mordell–Lang (DML)** structure of the additive orbit `O(P)={[k]P}`
under the translation map `+P`, viewing ECDLP as "find the return time `k` at which the
orbit meets the factor-base subvariety `X`," so that DML's arithmetic constraints on
`{k : [k]P in X}` could expose a sub-`sqrt(n)` return-time shortcut.

### Status
OPEN

### Novelty classification
NOVELTY-UNVERIFIED (DML/orbit-intersection framing has **not** appeared; distinct from
report1 `C2` and batch2 `C1` dynamical **isogeny/Lattès** work, which act on the isogeny
graph, not the additive translation orbit; distinct from batch5 `ARBOREAL-C1`, which is
about the **preimage** tree of a self-map, not the forward additive orbit).

### Semantic fingerprint
(object: additive orbit under `+P` and a target subvariety `X`; public ops: EC addition,
subvariety membership; hidden structure: DML `p`-adic-analytic parametrization of return
times; discarded: intermediate orbit points; retained: return-time set structure;
relation-gen: return times = relations; compression: analytic return-time arc; rank
mechanism: standard; descent: solve return time; dominant cost: cost of locating a return
time).

### Nearest ledger entries
1. report1 `C2` Lattès transfer-operator — isogeny dynamics; C1 is translation dynamics.
2. batch5 `ARBOREAL-C1` iterated-preimage tree — backward orbit; C1 is forward.
3. batch2 `C1` non-backtracking isogeny walk — isogeny-graph walk; C1 is the additive orbit.
4. `ECFG-001` direct Evans `k->x(kB)` functional graph (NEGATIVE) — C1 reframes it as an
   orbit-intersection with DML constraints rather than a preimage search.
5. batch3 `C2` nilsequence predictor — additive-combinatorial; C1 is arithmetic-dynamical.

### Nearest literature
Bell–Ghioca–Tucker "The Dynamical Mordell–Lang Conjecture"; Denis, Ghioca–Tucker. **Gap:**
DML says `{k : f^k(x) in X}` is a finite union of arithmetic progressions for *étale* maps
in char 0; over `F_p` translation-by-`P` is periodic with period `n`, so the return set is a
single AP of period `n` — which is exactly the BSGS/rho structure, giving no shortcut. This
is the near-certain collapse.

### Target family
Ordinary prime-order `E/F_p`; `X` = short-x factor base.

### Full algorithmic path
1. factor base `X`; 2. relation gen: orbit points hitting `X`; 3. verify; 4. prob = `|X|/n`;
5. standard; 6–7 return-time solve; 8/9 standard.

### Cost model
If the return-time set had exploitable sub-AP structure, locating a hit could beat
`sqrt(n)`; DML over `F_p` gives a full-period AP, so cost `= Theta(n/|X|)` — **not** sub-rho.
vs rho `1/2`.

### Why the existing negative results do not already kill it
It is a genuinely different framing (forward additive orbit + DML) from every prior dynamical
candidate; the `ECFG-001` negative was for direct preimage inversion, not orbit-intersection.

### Likely fatal obstruction
Char-`p` periodicity collapses DML to a single period-`n` AP = BSGS; no shortcut. Almost
certain.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; enumerate `{k : [k]P in X}` and test for any
sub-AP / `p`-adic-arc structure beyond the trivial period. Positive control: a char-0 étale
map with nontrivial DML AP union. Negative control: random subset (no structure).

### Quantitative promotion gate
Reject unless the return-time set has structure enabling a hit-location exponent `<1/2` on
`>=3` sizes. Trivial-period observation is a scoped negative.

### Proof track
Theorem: `{k : [k]P in X}` admits a `p`-adic-analytic description finer than the period-`n`
AP, exploitable for return-time search.

### Disproof track
Show the set is exactly a period-`n` AP (near-certain) → collapses to BSGS.

### Reproduction artifact
contract `experiment_contract_p1544_dml_orbit_intersection.md`; impl
`tasks/ecdlp_index_calculus/p1544_dml_orbit.py`; result + audit; ledger `ECFG-P1544`.

---

## Candidate: BOOTSTRAP-SPECTRAL-C2 ⊗ — SDP/conformal-bootstrap spectral-gap bound on the addition-transfer operator

### One-sentence mechanism
Exploit **semidefinite (conformal-bootstrap-style) relaxation** to certify a spectral-gap
bound on the `+P` addition-transfer operator, converting a certified gap into a mixing/
collision-rate bound that could shrink the rho constant — or, as a barrier, prove the gap is
too small to change the exponent.

### Status
HEURISTIC

### Novelty classification
NOVELTY-UNVERIFIED (SDP/bootstrap spectral certification is new vocabulary; distinct from
report1 `C2` transfer-operator spectral *estimation* and batch2 `C1` Ramanujan isogeny walk
— those posit a gap; C2 *certifies* one via SDP hierarchies).

### Semantic fingerprint
(object: `+P` transfer/Koopman operator on `F_p`-functions; public ops: SDP moment
hierarchy; hidden structure: operator spectrum; discarded: eigenvectors; retained: certified
gap bound; relation-gen: none new; compression: SDP certificate; rank mechanism: n/a; descent:
n/a; dominant cost: rho *constant*, not exponent).

### Nearest ledger entries
1. report1 `C2` Lattès transfer-operator — estimation; C2 is certification.
2. batch2 `C1` isogeny expander walk — assumes Ramanujan gap; C2 proves/bounds it.
3. batch4 `SIGNRANK-GAMMA2-B3` — SDP-flavored `gamma_2` norm; C2 is an SDP spectral bound on a
   different operator.
4. batch3 `EFFRES-A2` — spectral sparsifier; C2 is the operator's own spectrum.
5. `ECFG-RT-1476` — C2 does not attack it (constant-only).

### Nearest literature
Poland–Rychkov–Vichi conformal-bootstrap SDP; Lasserre/moment–SOS hierarchies (batch4
touched SOS for *membership*, not for operator spectra). **Gap:** no bootstrap has been
applied to a group-translation Koopman operator over `F_p`; and spectral gaps generically
change only the *constant*.

### Target family
Ordinary prime-order `E/F_p`.

### Full algorithmic path
Diagnostic only: 1. build the operator; 2. SDP-certify a gap; 3. translate to a
collision-rate constant. No new relation/descent stage — **INCOMPLETE** as a full attack path
(labeled below).

### Cost model
Best case: improves the rho *constant* `0.886`; cannot change the `1/2` exponent. vs rho:
constant-only.

### Why the existing negative results do not already kill it
It is a certification method not previously tried; but ranking will penalize it heavily for
constant-only impact.

### Likely fatal obstruction
Spectral gaps move constants, not exponents; **INCOMPLETE** (no target-descent stage).

### Minimal falsifying experiment
Toy `p in {1009,4099}`, seeds `1..5`; SDP-certify the gap and show the implied speedup is a
constant factor. Positive control: a known-gap operator. Negative control: an operator with
no gap.

### Quantitative promotion gate
Reject (structurally): cannot cross `1/2`. Retained only for barrier value.

### Proof track / Disproof track
Prove the certified gap implies only a constant-factor collision-rate change → barrier.

### Reproduction artifact
`experiment_contract_p1545_bootstrap_spectral.md`; impl `p1545_bootstrap_spectral.py`; ledger
`ECFG-P1545`. **Flagged INCOMPLETE (no descent stage).**

---

## Candidate: EXPLICIT-FORMULA-C3 ⊗ — Weil explicit-formula relation-density predictor

### One-sentence mechanism
Exploit the **Weil explicit formula** relating the zeros of the curve's `L`-function (i.e.
`#E(F_{p^k})` data) to the fine distribution of factor-base-relevant residue classes, to
predict relation-rich regions of the factor base before Semaev evaluation.

### Status
HEURISTIC

### Novelty classification
NOVELTY-UNVERIFIED (explicit-formula prediction is ledger-absent; distinct from batch3 `C2`
higher-order-Fourier/nilsequence prediction — that is additive-combinatorial; C3 is
`L`-function/spectral; distinct from batch5 `COHENLENSTRA-C2` class-group bias — that is
statistical over curves, C3 is within one curve).

### Semantic fingerprint
(object: curve `L`-function zeros / point-count spectrum; public ops: point counts, Fourier
over residues; hidden structure: zero distribution → residue bias; discarded: individual
relations; retained: predicted density map; relation-gen: bias-guided sampling; compression:
none; rank mechanism: standard; descent: standard; dominant cost: whether bias beats uniform
by more than a constant).

### Nearest ledger entries
1. batch3 `C2` nilsequence predictor — additive; C3 is spectral/`L`-function.
2. report3 `C2` Kloosterman importance sampling — exponential-sum bias; C3 is explicit-formula
   bias (related but the source of bias differs: Kloosterman sums vs `L`-zeros).
3. `ECFG-014` RHS graph enrichment — empirical selector; C3 is analytic.
4. batch5 `COHENLENSTRA-C2` — across-curve statistics; C3 within a curve.
5. `P1449` ancestry-permutation invariance — C3 must beat a permutation null.

### Nearest literature
Weil explicit formula; Sarnak–Katz zeros-of-`L`-functions; Iwaniec–Kowalski. **Gap:** the
explicit formula controls *averaged* point distributions; extracting a residue bias strong
enough to beat uniform relation-sampling by more than a constant is unestablished, and
Sato–Tate averaging suggests the bias washes out.

### Target family
Ordinary prime-order `E/F_p`.

### Full algorithmic path
1. factor base; 2. relation gen: sample residues by predicted density; 3–7 standard; 8/9
standard.

### Cost model
Best case: a constant-factor relation-yield improvement; crossing `1/2` requires the bias to
be exponentially concentrated, which Sato–Tate forbids on average. vs rho: likely
constant-only.

### Why the existing negative results do not already kill it
The `L`-function bias source is distinct from the empirical ECFG selectors (all NEGATIVE) and
from Kloosterman sampling; it is analytically grounded.

### Likely fatal obstruction
Sato–Tate equidistribution → the predicted bias is `O(p^{-1/2})`, a constant-order effect on
yield.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; compute the explicit-formula density map and
measure relation-yield lift vs a uniform sampler and vs an ancestry-permutation null
(per `P1449`). Positive control: a planted-bias residue set. Negative control: uniform.

### Quantitative promotion gate
Reject unless the yield lift is super-constant (changes the sampling exponent) on `>=3` sizes
against both uniform and permutation nulls.

### Proof track
Theorem: the explicit-formula residue bias concentrates relations by a super-constant factor.

### Disproof track
Sato–Tate bound shows `O(p^{-1/2})` bias → constant-only; scoped negative.

### Reproduction artifact
`experiment_contract_p1546_explicit_formula_density.md`; impl
`p1546_explicit_formula_density.py`; ledger `ECFG-P1546`.

---

## Candidate: FINEGRAINED-OV-D1 ⊗ — Fine-grained conditional lower bound on m-point membership (barrier; pairs COHNUMANS-B1, BAURSTRASSEN-A1)

### One-sentence mechanism
Reduce **Orthogonal-Vectors / 3SUM** instances to the m-point Semaev membership query, so
that a backend with `alpha < 3/2` at `m=5` would refute the OV/3SUM fine-grained conjectures
— establishing a *conditional* obstruction of a kind no prior barrier used.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL as a **barrier type**: every prior barrier in the ledger and seven reports is
**algebraic** (border-rank D3-report3/ASYMPSPEC-D1, slice-rank D2-batch4, Chow-atomizer
`P1512-R1`, class-function D1-report3, arboreal-maximality D3-batch5). A fine-grained
conditional-hardness reduction is structurally new. Documented search below.

### Semantic fingerprint
(object: the membership decision problem itself; public ops: reduction gadget; hidden
structure: OV/3SUM embedding into decomposition search; discarded: nothing; retained: the
conditional bound; relation-gen: n/a; compression: n/a; rank mechanism: n/a; descent: n/a;
dominant cost exponent: lower-bounds `alpha`).

### Nearest ledger entries
1. `P1512-R1` Chow-atomizer `Omega(r^5)` — algebraic determinantal lower bound; D1 is
   fine-grained/model-independent.
2. batch4 `SLICE-RANK-1-D2` — slice-rank vacuity; D1 is reduction-based.
3. report3 `D3` Semaev transform-sparsity — algebraic; D1 is fine-grained.
4. batch5 `ASYMPSPEC-D1` asymptotic-spectrum — bilinear-complexity; D1 is problem-reduction.
5. `ECFG-RT-1476` — D1 directly bounds its `alpha`.

### Nearest literature
Williams "Hardness of easy problems" (OV, SETH); Vassilevska Williams 3SUM/APSP surveys;
Björklund–Kaski fine-grained algebraic reductions. **Gap:** no fine-grained reduction is known
*into or out of* elliptic point-decomposition; the gadget (embedding OV vectors as factor-base
constraints) is unconstructed — the core research obligation.

### Target family
The m-point decomposition decision problem for ordinary prime-order `E/F_p`.

### Full algorithmic path (as a barrier)
1. take an OV/3SUM instance; 2. build a factor base and target encoding the instance; 3. show a
sub-`3/2` backend solves OV/3SUM below its conjectured bound. No relation/descent stage —
this is a lower bound.

### Cost model
If the reduction is tight, `alpha >= 3/2 - o(1)` conditionally, closing RT-1476. Compares the
*conditional* lower bound against the RT-1476 requirement.

### Why the existing negative results do not already kill it
It is a new proof technique that could *close* RT-1476 unconditionally-modulo-OV, which the
algebraic barriers only did for restricted (scalar-linear) atomizers.

### Likely fatal obstruction
The reduction may not be tight (constant-factor slack) or may not exist — elliptic
decomposition may be *easier* than OV, in which case D1 gives nothing.

### Minimal falsifying experiment
Construct the OV→membership gadget at toy scale `p in {101,211,431}`; verify the reduction
preserves instance size within the needed exponent. Positive control: a known OV-hard problem
(e.g., closest-pair) reduction. Negative control: a problem OV does *not* reduce to.

### Quantitative promotion gate
Promote (as a barrier) if the reduction forces `alpha >= 3/2 - o(1)` under OV/3SUM; else record
the slack as the residual loophole.

### Proof track
Theorem: OV on `d`-dim vectors reduces to m=5 membership with parameter blow-up small enough
that `alpha<3/2` refutes OV.

### Disproof track
Exhibit a membership backend faster than any OV algorithm at matched size → the reduction is
not tight; D1 fails and the loophole stays open.

### Reproduction artifact
`experiment_contract_p1547_finegrained_ov_barrier.md`; impl `p1547_finegrained_ov.py`; ledger
`ECFG-P1547`.

---

## Candidate: LANGWEIL-SUPPLY-D2 ⊗ — Deligne/Lang–Weil supply barrier (pairs HDX-A2, GRAPHON-B3, LANGWEIL-METER-A3)

### One-sentence mechanism
Use the **exact Lang–Weil point count** of the honest 2-large-prime summation graph's
cycle-space generating variety to prove the enrichment `delta` is pinned below `1/4` (or `=0`)
for the honest graph, closing the RT-1472 enrichment hope by a cohomological supply bound.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL as a barrier: uses Deligne/Weil point-counting (not additive-combinatorial
energy, batch3 `ENERGY-D1`) to bound `delta`. Complements LANGWEIL-METER-A3 (the meter) as its
negative-theory partner.

### Semantic fingerprint
(object: cycle-generating subvariety of the summation graph; public ops: point count, Weil
bound; hidden structure: cohomology of the honest graph's relation variety; discarded: none;
retained: `delta` upper bound; relation-gen: n/a; compression: n/a; rank mechanism:
supply → `delta`; descent: n/a; dominant cost exponent: bounds `delta`).

### Nearest ledger entries
1. batch3 `ENERGY-D1` additive-energy ceiling — sum-product; D2 is point-counting (independent).
2. batch5 `MATUNION-INDEP-D2` two-graph independence — combinatorial; D2 is cohomological.
3. `P1472` occupancy boundary — empirical; D2 is a proven bound.
4. batch2 `D2` amortization lower bound — preprocessing; D2 is supply.
5. `ECFG-RT-1472` — D2 directly bounds its `delta`.

### Nearest literature
Lang–Weil; Cafure–Matera explicit `F_p` bounds; Fouvry–Katz sums over varieties. **Gap:** the
precise cohomology of the *summation-relation* variety and its induced `delta` bound are
uncomputed.

### Target family
Ordinary prime-order `E/F_p`; `B=q^{1/5}`.

### Full algorithmic path (barrier)
1. exact count the cycle-generating variety; 2. bound independent cycles; 3. conclude
`delta <= delta_max`. Compare `delta_max` to `1/4`.

### Cost model
If `delta_max <= 1/4`, RT-1472 closes for the honest graph. vs rho: proves no crossing.

### Why the existing negative results do not already kill it
It supplies the *proof* that prior empirical/combinatorial meters only observed.

### Likely fatal obstruction
The Weil error term may be too weak to separate `delta` from `1/4` at toy scale; the bound may
be non-tight.

### Minimal falsifying experiment
Toy `p in {101,211,431,809,1601,4099}`; exact-count the cycle variety, compute `delta_max`,
compare to observed 2-core `delta` (feeds HDX-A2, GRAPHON-B3). Positive/negative controls as
in A3.

### Quantitative promotion gate
Promote as barrier if `delta_max <= 1/4` provably across `>=3` sizes with a size-monotone
trend; else record the gap.

### Proof track
Theorem: `delta(honest summation graph) <= 1/4 - c` for some `c>0`.

### Disproof track
A curve family with `delta > 1/4` (would be a *positive* lead for RT-1472).

### Reproduction artifact
`experiment_contract_p1548_langweil_supply_barrier.md`; impl `p1548_langweil_supply_barrier.py`;
ledger `ECFG-P1548`.

---

## Candidate: CIRCUIT-TAU-D3 ⊗ — Algebraic-complexity root/τ barrier (pairs COHNUMANS-B1, BAURSTRASSEN-A1, P1510 compiler)

### One-sentence mechanism
Apply **τ-conjecture-style / Shub–Smale root bounds** (a small arithmetic circuit for the
eliminant has few real/`F_p` roots) to bound the number of decompositions any sub-`3/2`-cost
membership circuit can report, closing the "small circuit ⇒ cheap membership" hope that
COHNUMANS-B1, BAURSTRASSEN-A1, and the `P1510` marked-resultant compiler all rely on.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL as a barrier: uses algebraic-complexity **root-counting** (τ-conjecture,
Shub–Smale, Baur–Strassen degree bounds), not tensor rank or determinantal degree. Distinct
from `P1512-R1` (determinant-degree ≥ cycle length) and from all border-rank barriers.

### Semantic fingerprint
(object: arithmetic circuit for the eliminant / membership; public ops: circuit size/depth,
root count; hidden structure: circuit-size vs root-count tradeoff; discarded: none; retained:
the lower bound; relation-gen: n/a; compression: n/a; rank mechanism: n/a; descent: n/a;
dominant cost exponent: lower-bounds membership via circuit size).

### Nearest ledger entries
1. `P1512-R1` Chow-atomizer `Omega(r^5)` — determinant degree; D3 is circuit-size vs roots.
2. `P1511-R2` factorized-semijoin cubic-input floor — product-circuit degree; D3 is a general
   circuit root bound.
3. report3 `D3` transform-sparsity — sparsity; D3 is τ/root-count.
4. batch4 `SOS-LB-D1` — SOS-degree lower bound; D3 is circuit-size.
5. `ECFG-P1510-R1` compiler — D3 bounds what any such compiler can output cheaply.

### Nearest literature
Shub–Smale τ-conjecture; Bürgisser "On defining integers…"; Koiran real-τ / sum-of-products.
**Gap:** τ-type bounds are notoriously open (imply `P≠NP`-adjacent separations); a *conditional*
version tied to the Semaev eliminant is the realistic deliverable.

### Target family
The m=5 eliminant circuit for ordinary prime-order `E/F_p`.

### Full algorithmic path (barrier)
1. bound the eliminant's `F_p`-root count from below (`Theta(q)` decompositions needed);
2. invoke a root-vs-size bound; 3. conclude circuit size `Omega(q^{1/2})` → `alpha>=3/2`.

### Cost model
If a size-`s` circuit has `<= poly(s)` roots but the backend must report `Theta(q^{...})`
decompositions, then `s = Omega(...)`, bounding `alpha`. vs rho: proves no crossing for the
circuit model.

### Why the existing negative results do not already kill it
It targets the **circuit** model (COHNUMANS, BAURSTRASSEN, P1510 all live there), which the
determinantal `P1512-R1` barrier does not fully cover.

### Likely fatal obstruction
Unconditional τ bounds are open; the barrier is likely only **conditional**, and the
root-count lower bound for the specific eliminant may be hard to establish.

### Minimal falsifying experiment
Toy `p in {101,211,431}`, m=4,5; measure eliminant `F_p`-root counts vs circuit size across
sizes; test the size-vs-roots trend. Positive control: a low-τ polynomial (few roots).
Negative control: a dense high-root polynomial.

### Quantitative promotion gate
Promote as barrier if the measured root-vs-size trend forces membership circuit size
`Omega(q^{1/2})` (`alpha>=3/2`) on `>=3` sizes.

### Proof track
Theorem (conditional on τ): any circuit reporting `Theta(q^{c})` decompositions has size
`Omega(q^{c'})` with `c' >= ...` closing `alpha<3/2`.

### Disproof track
A small circuit reporting many decompositions (would refute the τ-type premise and *open* a
backend).

### Reproduction artifact
`experiment_contract_p1549_circuit_tau_barrier.md`; impl `p1549_circuit_tau_barrier.py`;
ledger `ECFG-P1549`.

---

## 2. Ranking

Scores 0–5 on: (S1) distance from prior ledger mechanisms; (S2) plausibility of an exact
verifier; (S3) chance of changing an **exponent** not a constant; (S4) complete-path
coverage; (S5) falsifiability at toy scale; (S6) literature-novelty confidence; (S7)
**freedom from** hidden preprocessing/memory cost (higher = safer).

| Cand | S1 | S2 | S3 | S4 | S5 | S6 | S7 | Verdict |
|---|--:|--:|--:|--:|--:|--:|--:|---|
| BAURSTRASSEN-A1 | 3 | 5 | 1 | 5 | 5 | 3 | 5 | **keep** (conservative pool; low S3) |
| HDX-COBOUNDARY-A2 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **CONSERVATIVE WINNER** |
| LANGWEIL-METER-A3 | 4 | 5 | 2 | 3 | 5 | 4 | 5 | keep (meter; feeds D2) |
| COHNUMANS-B1 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | **REPRESENTATION WINNER** |
| PICARDFUCHS-B2 | 4 | 3 | 3 | 4 | 3 | 4 | 3 | keep (likely reproduces batch2 C2) |
| GRAPHON-CUTNORM-B3 | 3 | 4 | 3 | 4 | 4 | 3 | 4 | keep (overlap w/ batch4 A3) |
| DML-ORBIT-C1 | 4 | 5 | 3 | 4 | 5 | 4 | 4 | **HIGH-RISK WINNER** |
| BOOTSTRAP-SPECTRAL-C2 | 4 | 3 | 0 | 1 | 3 | 4 | 3 | **REJECT** (constant-only, INCOMPLETE) |
| EXPLICIT-FORMULA-C3 | 3 | 3 | 1 | 4 | 4 | 3 | 4 | reject-tier (constant-only) |
| FINEGRAINED-OV-D1 | 5 | 3 | 4 | 4 | 3 | 5 | 5 | **keep** (best barrier) |
| LANGWEIL-SUPPLY-D2 | 4 | 5 | 4 | 4 | 5 | 4 | 5 | **keep** (barrier; pairs A2/A3/B3) |
| CIRCUIT-TAU-D3 | 4 | 3 | 4 | 4 | 3 | 4 | 5 | keep (conditional barrier) |

**Rejections** (semantic-novelty < 3, or no route to descent, or no rho comparison, or
constant-only): **BOOTSTRAP-SPECTRAL-C2** (S3=0, INCOMPLETE path, constant-only) and
**EXPLICIT-FORMULA-C3** (constant-only by Sato–Tate; retained only as a documented
scoped-negative expectation). All others clear semantic novelty ≥ 3, have a complete
route to target descent (via the RT-1472/RT-1476 skeletons) or are explicit barriers with a
rho comparison, and give a precise distinction from the closest ledger entry.

**Selected winners:**
1. Conservative: **HDX-COBOUNDARY-A2** — attacks the live RT-1472 `delta` gate with a
   genuinely higher-dimensional (cosystolic) isoperimetric invariant, exactly measurable at
   toy scale, complete path via the RT-1472 skeleton.
2. Representation-changing: **COHNUMANS-B1** — replaces the polynomial-system backend with a
   group-algebra convolution; the one construction that could, in principle, dodge the
   determinantal `Omega(r^5)` payload because its cost is `|G|`, not tensor rank.
3. High-risk: **DML-ORBIT-C1** — a clean, ECDLP-native reframing (forward additive orbit +
   Dynamical Mordell–Lang) with an exact toy verifier and a sharp, almost-certainly-negative
   prediction (period-`n` AP ⇒ BSGS).

---

## 3. Winner experiment contracts + first commands

### 3.1 Contract — HDX-COBOUNDARY-A2 (`ECFG-P1539`)

```yaml
id: ECFG-P1539
title: Coboundary-expansion delta-meter for the m-uniform Semaev relation complex (RT-1472)
status: PREREGISTERED / REVIEW REQUIRED
hypothesis: >
  The honest m-uniform relation complex (faces = membership-valid tuples over the
  short-x factor base) has cosystolic/coboundary expansion lambda bounded away from 0,
  implying an independent-cycle enrichment delta > 1/4 at L = q^{1/5}, hence a sub-rho
  RT-1472 crossing.
null_hypothesis: >
  lambda -> 0 with size and the honest complex is sub-critical, delta = 0 (confirming
  LANGWEIL-SUPPLY-D2). This is the strong prior.
target_family: ordinary prime-order E/F_p, non-CM, j != 0,1728, non-supersingular.
sizes: p in {1009, 4099, 40009}  # exhaustive m=3,4 complexes; sampled m=5
seeds: {1,2,3,4,5}
parameters:
  L: floor(p^{1/5})
  m: [3, 4]        # 5 sampled only
  field_of_coeffs: [GF(2), GF(p)]
factor_base: {x(P) in [0, L)}, negation-reduced
relation_shape: m-face = membership-valid m-tuple summing to O (or to target for descent)
metrics:
  - lambda: smallest nonzero singular value of the coboundary map delta_1 (both GF(2), GF(p))
  - delta: dim(cocycle space)/|edges|
  - exponent: max(2*ell, 1-ell, 1+1/5-2*ell) under measured delta
  - baseline: rho exponent 1/2
positive_control: a designed Ramanujan/coset complex of matched size (lambda bounded below)
negative_control: Erdos-Renyi m-uniform hypergraph of matched density (lambda -> 0)
success_criterion: >
  delta > 1/4 AND lambda bounded away from 0 across all 3 sizes AND the exponent trend
  crosses 1/2. Correctness of the complex alone does NOT promote.
falsification_criterion: >
  lambda -> 0 (near-certain) => delta collapses to sub-critical; record scoped negative
  and route to LANGWEIL-SUPPLY-D2 as a proven supply barrier.
claim_discipline: >
  Toy-scale, exact-enumeration evidence. No single-target complete-cost sub-rho claim is
  made; a positive would be a delta-meter observation requiring an honest full-graph run.
independent_audit: recompute lambda and delta from a frozen face list; 5 mutation classes.
artifacts:
  contract: experiment_contract_p1539_hdx_coboundary_delta_meter.md
  impl: tasks/ecdlp_index_calculus/p1539_hdx_coboundary_delta.py
  result: p1539_hdx_coboundary_delta.json
  audit: p1539_hdx_coboundary_delta_audit.json
```

**First executable command** (Sage/Python preflight — enumerate the exact m=3 relation
complex on the smallest toy curve and report its coboundary spectrum; no attack, pure meter):

```bash
sage -python tasks/ecdlp_index_calculus/p1539_hdx_coboundary_delta.py \
  --prime 1009 --m 3 --L auto --coeff-field GF2 --coeff-field GFp \
  --seed 1 --exhaustive --emit p1539_hdx_coboundary_delta.json
```

### 3.2 Contract — COHNUMANS-B1 (`ECFG-P1541`)

```yaml
id: ECFG-P1541
title: Cohn-Umans triple-product-property convolution backend for m-point decomposition
status: PREREGISTERED / REVIEW REQUIRED
hypothesis: >
  There exists a finite group G with |G| = q^{gamma}, gamma < 1/2, and a TPP triple
  (S,T,U) that realizes the exact m=5 elliptic decomposition tensor, so that testing all
  decompositions of a target is one F_p[G] convolution of cost O(q^{gamma} polylog q),
  giving membership query exponent alpha < 3/2.
null_hypothesis: >
  The decomposition relation is nonbilinear and admits no TPP embedding, or any embedding
  needs |G| = Omega(q) (gamma >= 1), reproducing the rho baseline (see CIRCUIT-TAU-D3).
target_family: ordinary prime-order E/F_p; m in {4,5}; no extra automorphisms.
sizes: p in {101, 211, 431}   # exact TPP construction feasible only at toy scale
seeds: {1,2,3,4,5}
parameters: {m: [4,5], group_family: [abelian, Heisenberg-mod-p, S_n-wreath]}
factor_base: {x(P) in [0,L)}, L = floor(p^{1/5})
relation_shape: nonzero convolution coefficients = valid decompositions (EC-reverified)
metrics:
  - gamma: log_q |G| for the smallest embedding found
  - capacity: realized TPP capacity vs #m-tuples
  - convolution_exponent: measured FFT cost exponent in q
  - baseline: rho 1/2 ; Semaev-Grobner backend superlinear-in-L
positive_control: matrix-multiplication TPP of matched size (must embed)
negative_control: a random nonbilinear tensor of matched shape (must fail to embed)
success_criterion: a TPP embedding with gamma < 1/2 AND convolution_exponent < 1/2 across
  all 3 sizes; any embedding at gamma >= 1/2 is a scoped negative.
falsification_criterion: no embedding, or capacity < #m-tuples, or gamma >= 1/2.
claim_discipline: >
  Correctness of the convolution reproducing decompositions is necessary but NOT a
  performance claim; only a measured gamma < 1/2 with a crossing exponent promotes.
independent_audit: reconstruct all decompositions directly by EC addition; 6 mutations.
artifacts:
  contract: experiment_contract_p1541_cohn_umans_tpp_backend.md
  impl: tasks/ecdlp_index_calculus/p1541_cohn_umans_tpp.py
  result: p1541_cohn_umans_tpp.json
  audit: p1541_cohn_umans_tpp_audit.json
```

**First executable command** (attempt the m=4 TPP embedding on the smallest toy curve and
report realized capacity vs required, and gamma — a construction-existence preflight, not an
attack):

```bash
sage -python tasks/ecdlp_index_calculus/p1541_cohn_umans_tpp.py \
  --prime 101 --m 4 --group-family abelian --group-family heisenberg \
  --seed 1 --report-capacity --emit p1541_cohn_umans_tpp.json
```

### 3.3 Contract — DML-ORBIT-C1 (`ECFG-P1544`)

```yaml
id: ECFG-P1544
title: Dynamical Mordell-Lang orbit-intersection structure of the additive ECDLP orbit
status: PREREGISTERED / REVIEW REQUIRED
hypothesis: >
  The return-time set R = {k : [k]P in X} for the short-x factor base X has arithmetic
  structure finer than the trivial period-n arithmetic progression, exploitable to locate
  a hit with exponent < 1/2.
null_hypothesis: >
  Over F_p, translation-by-P is periodic with period n, so R is a single period-n AP =
  the BSGS/rho structure; no shortcut. Strong prior.
target_family: ordinary prime-order E/F_p.
sizes: p in {1009, 4099, 40009}
seeds: {1,2,3,4,5}
parameters: {X: short-x factor base of size L = floor(p^{1/5}); also L = floor(sqrt(p)) control}
relation_shape: k with [k]P in X (a return time = a relation)
metrics:
  - R_structure: decomposition of R into APs / p-adic arcs beyond the trivial period
  - hit_location_exponent: measured cost to find one k in R vs n/|X|
  - baseline: rho 1/2 ; BSGS n/|X|
positive_control: a char-0 etale self-map with a nontrivial DML AP-union (structure present)
negative_control: a random subset of Z/n of matched size (no structure)
success_criterion: R has sub-AP structure enabling hit_location_exponent < 1/2 on all 3 sizes.
falsification_criterion: R is exactly a period-n AP (near-certain) => collapses to BSGS.
claim_discipline: A trivial-period observation is a scoped negative, NOT evidence that
  prime-field ECDLP is unimprovable.
independent_audit: recompute R by brute force at toy scale; verify AP-period equals n.
artifacts:
  contract: experiment_contract_p1544_dml_orbit_intersection.md
  impl: tasks/ecdlp_index_calculus/p1544_dml_orbit.py
  result: p1544_dml_orbit.json
  audit: p1544_dml_orbit_audit.json
```

**First executable command** (enumerate the return-time set on the smallest toy curve and
test whether its period is exactly `n` — the null — versus any finer arithmetic structure):

```bash
sage -python tasks/ecdlp_index_calculus/p1544_dml_orbit.py \
  --prime 1009 --factor-base short-x --L auto --seed 1 \
  --test-ap-structure --emit p1544_dml_orbit.json
```

---

## 4. Red-team — are the three winners disguised repetitions or cost-negative?

**Charge against HDX-COBOUNDARY-A2 (conservative winner).**
- *Disguised repetition?* It is the m-dimensional generalization of a lane the ledger has
  hit five times (3-LP homology, cycle-basis, effective-resistance, matroid-union,
  correlated-peeling). The **mechanism** (coboundary/cosystolic expansion) is new, but the
  **target quantity** (`delta`) and the **failure mode** are identical to all five priors.
  Risk: this is a new *name* for the same `delta`-hunt.
- *Cost-negative?* Near-certain. Arithmetically-defined complexes over `F_p` are generically
  **not** expanders; `lambda -> 0` forces `delta = 0`, exactly what LANGWEIL-SUPPLY-D2
  predicts and what all five prior meters observed. The likely outcome is a **scoped
  negative that upgrades to a barrier** (D2), not a crossing. **Verdict: probably
  cost-negative; retained because the exact coboundary meter *proves* what prior meters only
  observed, and a positive would be a genuine RT-1472 lead.**

**Charge against COHNUMANS-B1 (representation winner).**
- *Disguised repetition?* The ledger already has a Semaev **border-rank** lower bound (report3
  B4) and an asymptotic-spectrum barrier (batch5 ASYMPSPEC-D1). B1 is the dual *upper-bound*
  construction, so it is not a repetition — but it lives in the **same tensor/bilinear-complexity
  universe** those barriers police.
- *Cost-negative?* Very likely. The elliptic decomposition relation is **nonbilinear**;
  Cohn–Umans TPP embeds *bilinear* maps (matrix multiplication). There is no reason a
  nonbilinear decomposition tensor embeds in a group algebra at all, and a **counting
  argument** (hosting `Theta(q)` decompositions needs `|G| = Omega(q)`, so `gamma >= 1`)
  likely closes it before any FFT speedup — this is exactly **CIRCUIT-TAU-D3**'s charge.
  **Verdict: probably cost-negative via a capacity/counting bound; retained because it is the
  only candidate whose cost model (`|G|`) is orthogonal to the determinantal `Omega(r^5)`
  payload, so a positive would escape the strongest existing barrier.**

**Charge against DML-ORBIT-C1 (high-risk winner).**
- *Disguised repetition?* It reframes the `ECFG-001` direct-functional-graph negative and is
  operationally close to BSGS. The **framing** (forward additive orbit + DML) is new, but the
  **object** (the orbit `{[k]P}`) is the most-studied object in the whole program.
- *Cost-negative?* Essentially certain. Over `F_p`, `+P` is periodic with period `n`, so DML's
  "finite union of arithmetic progressions" degenerates to a **single period-`n` AP** — which
  is exactly the structure BSGS already exploits, giving cost `Theta(n/|X|)`, not sub-rho.
  DML's power is a char-0 / étale phenomenon; the char-`p` periodic case is its trivial
  boundary. **Verdict: cost-negative with near-certainty; retained only because the exact toy
  verifier cleanly *closes* the orbit-intersection framing as a scoped negative, preventing a
  future report from re-proposing it.**

**Cross-cutting red-team conclusion.**
All three winners are, on the strong prior, **scoped negatives or barriers-in-waiting**, and
each is paired with the exact barrier that most likely kills it (A2↔D2, B1↔D3, C1↔its own
periodicity lemma). This is consistent with the batch4/batch5/batch6 meta-finding: **the
mechanism space is saturated; the residual value is in exact meters and structurally-new
barriers, not in a rho crossing.** No break is claimed. Every positive control is a toy
correctness/structure check; every "below rho" in the reviewed corpus remains
amortized-many-target or setup-uncharged. A failed candidate here is a scoped negative result,
**not** evidence that prime-field ECDLP cannot be improved.

---

## 5. Claim discipline

- **Correctness ≠ performance.** Reproducing decompositions (B1), enumerating a relation
  complex (A2), or a return-time set (C1) is necessary but never a speedup claim.
- **Candidate relation ≠ verified ECDLP recovery.** No candidate here recovers a scalar below
  rho; the winners are meters/constructions gated on a *measured exponent crossing 1/2*.
- **Toy-scale, heuristic, restricted-model labels** are attached to every quantitative claim.
- **Barriers D1/D2/D3 are conditional or toy-verified**, not unconditional impossibility
  theorems; D1 and D3 rest on OV/3SUM and τ-type conjectures respectively.
- A failed candidate is a **scoped negative result**. It narrows the search; it does not close
  prime-field ECDLP improvement.

**Novelty ledger for batch6:** BAURSTRASSEN-A1 LITERATURE-ADJACENT · HDX-COBOUNDARY-A2
NOVELTY-UNVERIFIED · LANGWEIL-METER-A3 LEDGER-NEW(meter) · COHNUMANS-B1 NOVELTY-UNVERIFIED ·
PICARDFUCHS-B2 NOVELTY-UNVERIFIED · GRAPHON-CUTNORM-B3 NOVELTY-UNVERIFIED · DML-ORBIT-C1
NOVELTY-UNVERIFIED · BOOTSTRAP-SPECTRAL-C2 NOVELTY-UNVERIFIED(rejected) · EXPLICIT-FORMULA-C3
NOVELTY-UNVERIFIED(reject-tier) · FINEGRAINED-OV-D1 POSSIBLY-NOVEL(barrier type) ·
LANGWEIL-SUPPLY-D2 POSSIBLY-NOVEL(barrier type) · CIRCUIT-TAU-D3 POSSIBLY-NOVEL(barrier type).

The two live rho-crossing gates **RT-1472** (`delta>1/4`) and **RT-1476** (`alpha<3/2` at
m=5) remain **open**; batch6 adds three exact meters and three structurally-new barriers
aimed squarely at them, and rejects two constant-only speculatives.
```
