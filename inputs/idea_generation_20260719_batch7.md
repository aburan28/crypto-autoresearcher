# Idea Generation — Research Director — 2026-07-19 batch7 (report 15 / internal batch13)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Target:** a non-generic single-target prime-field ECDLP algorithm whose *complete* cost beats Pollard-rho `O(sqrt(n))`. Toy correctness, a new coordinate system, a relation certificate, faster preprocessing, or a solver swap alone is **not** a breakthrough.
**Scope:** generated toy curves, public benchmark instances, synthetic data only. No wallets, production keys, or unauthorized systems.

**Verdict up front:** the mechanism space is saturated. This is the **15th** idea report (internal batch13). Fourteen prior reports span ~60 distinct mechanism lanes and every lower-bound/representation technology family that had an obvious hook. Batch13 imports three families that are genuinely absent from all 14 prior reports — **Boolean sensitivity/certificate query measures (post-Huang)**, **Fulton–MacPherson excess/Segre refined intersection**, and **Borodin–Cook multi-output time-space tradeoffs** — plus adjacent proof-complexity and analytic supply meters. As in batches 5–12, every attack-side candidate is a **scoped negative / lane closure with a near-certain named kill**, and the higher-EV work is the **barrier arm** (group D), each of whose thresholds would formally *close* one of the two live gates. **No rho crossing is claimed. RT-1472 and RT-1476 remain open.**

---

## 1. Inputs reviewed and machine-readable inventory

### 1.1 Files read this run

- `/Volumes/Volume/git/autolab/research_ledger.md` (2.95 MB; ECFG-P frontier `P1486`, RT/NR chain through the `P147x` two-large-prime gate block and the ISO-IKD oriented-ideal Kani rows through `ISO-RT-IKD-014`).
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (IC-state frontier `P1509–P1513`).
- `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (transfer census — same-field isogeny/trace-zero/Weil-descent negatives).
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json` (10 core Semaev/index-calculus primary sources).
- All 14 prior `research/idea_generation_2026071[7-9]*.md` reports (anti-duplication catalogue).

### 1.2 Inventory summary (families and outcomes)

- **Ledger IDs reviewed:** the full `ECFG-P` / `ECFG-NR` / `ECFG-RT` / `ECFG-MX` / `ISO-*-IKD` families in the two ledgers, plus report-proposed `ECFG-P` IDs `P1487–P1621` from reports 1–14. ID families covered: `ECFG-P`, `ECFG-NR`, `ECFG-RT`, `ECFG-MX`, `ISO-{NR,OBS,RT}-{ONK,IKD}`, `IDEA-0xx/1xx`, `RQ`, `H`, `EV`, `DEC`.
- **The only two live rho-crossing surfaces (both unrealized conditional theorems):**
  - **RT-1472** — an explicit hash-like two-large-prime graph at `B=n^{1/5}` has cost exponent `max(2ell, 1-ell, 1+1/5-2ell)`, minimized at `ell=1/3` giving exponent `2/3`; crossing rho requires pair-support **enrichment `delta>1/4`**. Every explicit-advice/character-bucket/CM-orbit enrichment attempt (`P1471–P1475`) measured `delta ≈ 0`.
  - **RT-1476** — a complete five-term implicit membership backend with **query exponent `alpha<3/2`** (setup `≤L^2`, random-like support, sparse full-rank relations) would conditionally beat rho; `m≤3` impossible, `m=4` needs `alpha<1`, `m=5` needs `alpha<3/2`. At `m=5, alpha=1` relation and linear algebra are `q^{2/5}`, descent `q^{1/5}`.
- **IC-state frontier `P1509–P1513`:** P1509 exact local Hasse-jet source section (positive, verifier `Theta(r^3)`); P1510-R1 **independently verified global marked-resultant compiler** (`O(r^2)` state, output-sensitive FFE) — but repeating it for `Theta(r)` rows is `Theta(r^3)=q^{3/5}`; P1511-R2 closed the product-circuit gcd/subresultant/Hasse semijoin (`r^3` input leaves); **P1512-R1 closed the source-labelled scalar-linear Chow/Tate/determinant-of-cohomology atomizer at `Omega(r^5)`** via `deg(det M) ≤ dim`, leaving **only the target-specialized nonlinear-circuit exception**; P1513 is the **open** shared-bivariate common-norm theorem gate (input circuit quadratic, both explicit norms still cubic).
- **Negative-control territory (closed unless a candidate breaks the measured obstruction):** ordinary same-field isogeny invariants; scalar Weil pullback; explicit two-large-prime advice graphs; joint factor/large-prime Krylov; pair-residual character buckets; non-invariant CM endpoint decks; materialized serial-S3 backward states; dense composed resultants; source selectors without an honest hit generator; relation validity without ECDLP recovery; preprocessing wins whose offline/memory/advice/target-count cost loses to rho.

### 1.3 Anti-duplication catalogue (technology families already consumed, reports 1–14)

Tensor/border/slice rank; communication (Raz–McKenzie/GPW lifting, 5-party NOF/BNS, discrepancy/corruption, direct-sum info, sign-rank, `gamma_2`); VC/Sauer–Shelah; approximate degree/dual polynomial; probabilistic polynomials; entropy (Shearer); matroid union; Delsarte-LP; hypergraph containers; sum-product/additive energy; PFR; Kruskal–Katona shadow; Bollobás set-pairs; sunflower-free; p-adic (Ax–Katz, Adolphson–Sperber, Newton polygon); Lang–Weil/Deligne count; l-adic Betti/Milnor–Thom; Nullstellensatz (refutation **and** feasibility certificate); Polynomial-Calculus/IPS; SOS/Lasserre/Positivstellensatz; Sherali–Adams LP hierarchy; tau-conjecture/Shub–Smale; arithmetic-circuit LBs (shifted partials, Nisan nc-ABP, GCT occurrence, elusive functions, depth-reduction chasm, algebraic natural proofs, Valiant rigidity, Raz multilinear, block-Hankel); noncommutative rank/operator scaling; immanant interpolation; matchgate/Holant/Cohn–Umans; GKZ D-module; Newton–Okounkov; cluster algebras; quaternion/Brandt; LDC/LDLR; proof-space (red-blue) pebbling; cell-probe chronogram; quantum adversary/span program; fine-grained OV/3SUM/hyperclique; Lorentzian/log-concave; delta-matroid; Schubert structure constants; method of multiplicities; restriction/Kakeya; Coppersmith lattice; Barvinok interpolation; Moser entropy compression; dequantized sampling; persistent homology; RKHS; free probability; Fourier–Mukai; arboreal Galois; Mahler/automatic; formal group/Coleman; ACFA/difference; Dynamical Mordell–Lang; Picard–Fuchs; Ronkin/amoeba; elliptic nets; Croot–Sisask; Elekes–Szabó; sandpile/critical group; o-minimal Pila–Wilkie; matching-vector codes; Berezin–Pfaffian; Ore/skew resultant.

**Batch13 must be new against all of the above.** The three organizing families below appear nowhere in it.

---

## 2. Organizing theme for batch13

Every degree-based or circuit-degree-based meter is **capped by the degree of the membership object** (`deg(det M) ≤ dim` is exactly what closed P1512-R1). Batch13 imports meters that are *decoupled from ambient polynomial/circuit degree in a way none of the prior families were*:

1. **Boolean decision-structure measures** — sensitivity `s(f)`, block sensitivity `bs(f)`, certificate complexity `C(f)`, deterministic decision-tree depth `D(f)`. Post-Huang (2019) these satisfy `bs(f) ≤ s(f)^4` and `deg(f) ≤ s(f)^{...}`, a *combinatorial* chain distinct from approximate degree (batch8), LDC length-vs-query (batch11), and query→communication lifting (batch7). They measure the *number of pivotal source coordinates*, not the eliminant degree.
2. **Fulton–MacPherson excess/Segre refined intersection** — the 5-point membership variety is a **non-transverse** intersection (the whole reason the linear Chow atomizer bottomed out at `Omega(r^5)`: the excess is discarded). The refined class is the **Segre class of the excess normal bundle**, not the ordinary intersection product. This is the sharpest untried attack on the P1512-R1 nonlinear exception, because P1512's `deg(det)` bound is a statement about the *ordinary* class.
3. **Borodin–Cook multi-output time-space tradeoffs** — the batch relation-generation stage is a *multi-output* function (emit `Theta(r)` source rows). Borodin–Cook `TS=Omega(n^2)`-style bounds are the classic tool for exactly this shape and are distinct from the static proof-space pebbling (batch11 D1) and the dynamic cell-probe chronogram (batch12 D1).

Supporting imports: Cutting-Planes/Lovász–Schrijver proof complexity (the missing rung below SOS/SA/PolyCalc), Arakelov arithmetic-intersection height (a *global* supply meter over all places), Temperley–Lieb/Hecke diagrammatics, Håstad random restriction, spectrahedral shadows, and seeded extractors/condensers.

At least six candidates (A1, A2, A3, B1, B2, C1, C3, D1, D2, D3) begin **outside the ledger's algebraic-geometry/index-calculus vocabulary**.

---

## 3. Candidates

Ledger IDs `ECFG-P1622 … ECFG-P1633`.

---

## Candidate: SENSITIVITY-BLOCK-A1  (ECFG-P1622)

### One-sentence mechanism
Exploit the *combinatorial decision structure* of the `m=5` membership predicate — its sensitivity `s`, block sensitivity `bs`, and certificate complexity `C` — to lower-bound (or, in the favorable branch, upper-bound) the query cost `alpha` of any decision-tree backend, below the `L^{1.5}` RT-1476 boundary.

### Status
HYPOTHESIS (meter); the barrier direction is D1.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Nisan–Szegedy 1992; Huang 2019; Kenyon–Kutin; Ambainis–Vihrovs) — no application to Semaev membership found.

### Semantic fingerprint F(C)
- algebraic object: the Boolean membership function `f_B: (source-index tuple) -> {0,1}` deciding whether five factor-base points sum to the target;
- available public operations: query one source coordinate (a factor-base membership bit) at unit cost;
- hidden structure exploited: pivotal-coordinate concentration (few sensitive blocks per accepting input);
- information discarded: the field values / eliminant degree;
- information retained: which coordinates flip the decision;
- relation-generation primitive: decision tree emitting a certificate = a source row;
- compression primitive: certificate complexity `C(f)` as row-witness size;
- rank mechanism: n/a (this is a query meter, not a rank meter);
- descent mechanism: same decision tree reused for target descent;
- dominant cost exponent: `alpha = log_L D(f)`, with `D(f) ≤ C(f)^2 ≤ (bs·s)^2 ≤ s^{10}` (Huang chain).

### Nearest ledger entries
1. **APPROXDEG-D1 (batch8, P156x)** — approximate degree `deg~(f)`. Distinction: `deg~` bounds *bounded-error polynomial* degree; `s/bs/C` are *exact* combinatorial measures with a different relation chain (`deg~ ≤ ... ` is separate from `D ≤ C^2`). A function can have small `bs` but large `deg~` region-wise.
2. **LDC-LOCAL-DECODABILITY-A1 (batch11, P159x)** — length-vs-query LDC bound. Distinction: LDC measures *decodability under corruption*; sensitivity measures *pivotality under a single flip* — dual regimes.
3. **LIFTING-D1 (batch7, P155x)** — query→communication lifting. Distinction: lifting transfers a *query* bound into a *communication* bound; A1 stays inside the query world and uses the sensitivity certificate chain directly.
4. **RIGIDITY-A1 (batch8)** — matrix rigidity of the P1510 eval matrix. Distinction: rigidity is a linear-algebraic robustness measure; sensitivity is a Boolean pivotality measure — no shared inequality.
5. **P1477-R2 density** — backward-state coefficient density. Distinction: density is an algebraic sparsity count, not a decision-tree measure.

### Nearest literature
- Nisan, Szegedy, *On the degree of Boolean functions as real polynomials* (1994): `deg(f) ≤ bs(f)^2` and the sensitivity conjecture statement.
- Huang, *Induced subgraphs of hypercubes and a proof of the Sensitivity Conjecture* (Annals 2019): `bs(f) ≤ s(f)^4`, closing the polynomial-relatedness chain.
- Kenyon–Kutin; Ambainis–Vihrovs (upper bounds on `bs` in terms of `s`).
- Gap: all of this is defined for `f:{0,1}^N -> {0,1}`; the Semaev backend queries **`F_p`-valued** source coordinates, so the bit-model translation to the `L^alpha` field-op cost model is exactly the open question A1 must resolve.

### Target family
Ordinary prime-field `E/F_p`, prime group order `n=q`, `q≈L^5`, `L=q^{1/5}`, generic `j∉{0,1728}`, no CM, no small embedding degree, no rational 2- or 3-torsion structure that trivializes the predicate. Excluded: supersingular, anomalous, low-embedding-degree, and Weil-restricted composite-field curves.

### Full algorithmic path
1. **Factor base:** the P1473 sparse subgroup-x deck of size `L` (public, deterministic).
2. **Relation generation:** encode `m=5` membership as `f_B` over the `5·L` source-presence bits; run a decision tree; each accepting leaf certificate is a candidate five-source relation.
3. **Witness extraction & verification:** the certificate names five sources; the P1510-R1 compiler re-verifies the marked resultant exactly (independent).
4. **Relation probability:** `min(1, L^5/q) = Theta(1)` at `q≈L^5` (the RT-1476 support model).
5. **Matrix:** `Theta(L)` rows, sparse, linear algebra `L^2` (not binding).
6. **Factor-log calibration:** standard once relations are full-rank.
7. **Descent:** same decision tree on the target row.
8. **Offline/online:** decision tree is target-blind ⇒ offline; certificate emission is online.
9. **Memory/parallelism:** tree depth `D(f)` per query; embarrassingly parallel over rows.

No stage missing.

### Cost model
Query cost per row `= L^{alpha}`, `alpha = log_L D(f)`. **Favorable branch:** if `f_B` has `bs(f)=O(polylog L)` (few pivotal blocks), then `D(f) ≤ bs^2·s ≤ polylog`, giving `alpha→0` and total `q^{2/5}` — a crossing. **Realistic branch:** a random-like membership predicate on `Theta(log q)` relevant bits has `bs(f)=Theta(log q)` and `D(f)=Theta(log q)` **bits**, i.e. `Theta(1)` field elements' worth — but the field-op to answer one bit query is itself the cubic P1510 evaluation, so `alpha` collapses back to the P1511-R2 `Theta(r^3)` input floor. Compare: rho `q^{1/2}`, BSGS `q^{1/2}`, nearest IC baseline (per-target P1510) `q^{3/5}`.

### Why the existing negative results do not already kill it
P1512-R1 and P1511-R2 are statements about **degree** and **product-circuit input size**; a low-`bs` function can have high degree, so the sensitivity chain is not entailed by `deg(det) ≤ dim`. The new operation is measuring **pivotality** rather than degree — a measure P1512's `Omega(r^5)` proof never touches.

### Likely fatal obstruction
The bit-model `D(f)` does not charge the **field cost of answering one query**; a single membership bit for a random-like predicate already costs the cubic P1510 evaluation, so a small `D(f)` buys nothing in the `L^alpha`-field-op currency. Near-certain kill ⇒ inconclusive, not barrier.

### Minimal falsifying experiment
Toy sizes `L∈{8,16,32}` (three), ordinary prime-order curves at `q≈L^5`; per size measure exact `s(f_B), bs(f_B), C(f_B)` on the true subgroup deck, plus a **positive control** (a planted low-sensitivity `f` with a known short tree), a **negative control** (random-x deck), and randomized seeds `×5`. Instrument the *field-op cost of one query* alongside `D(f)`.

### Quantitative promotion gate
Require measured `alpha = log_L (queries × field-op-per-query) < 3/2` with a **decreasing** trend across the three sizes and leave-one-out max `< 3/2`. Correctness of certificates alone is explicitly *not* the gate.

### Proof track
Theorem to prove: `bs(f_B) = O(polylog L)` for the elliptic membership predicate ⇒ (via Huang) `D(f_B)=polylog` ⇒ `alpha→0`. Requires showing few pivotal source blocks per accepting five-tuple.

### Disproof track
Exhibit an elliptic family where a single source flip changes membership for `Theta(L)` disjoint blocks ⇒ `bs=Theta(L)` ⇒ `alpha ≥ 1` in field ops ⇒ no crossing. (Expected outcome.)

### Reproduction artifact
Contract `experiment_contract_p1622_sensitivity_block_membership_meter.md`; impl `tasks/ecdlp_index_calculus/p1622_sensitivity_block_meter.py`; result `p1622_sensitivity_block_meter.json`; audit `p1622_audit.py`; ledger `ECFG-P1622`.

---

## Candidate: CERTIFICATE-DUAL-A2  (ECFG-P1623)

### One-sentence mechanism
Exploit certificate complexity `C(f_B)` as an exact *witness-size* meter for the five-source relation, decoupling row-witness cost from eliminant degree.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (certificate/nondeterministic decision-tree complexity). Distinct from the **algebraic** Nullstellensatz feasibility certificate (batch9 A1), which measures certificate *degree×height*, not Boolean certificate *size*.

### Semantic fingerprint F(C)
object: membership function `f_B`; operations: source-bit queries; hidden structure: minimal accepting certificate; discarded: field arithmetic; retained: the minimal source set forcing acceptance; relation primitive: nondeterministic tree; compression: `C_1(f)` = 1-certificate size; rank: n/a; descent: certificate re-solve on target; cost exponent: `alpha = log_L C_1(f_B)`.

### Nearest ledger entries
NULLSTELLENSATZ-CERT-A1 (batch9, algebraic certificate degree); SENSITIVITY-BLOCK-A1 (this batch, `C ≥ bs`); LDC-A1 (batch11, query vs length); BENORTIWARI-A1 (batch7, sparse-interp witness opening); P1511-R1 FD-width (join-witness size). Distinction from each: `C_1(f)` is the *Boolean* minimal-certificate size; the others measure algebraic degree, decodability, interpolation support, or join width — none equals `C_1`.

### Nearest literature
Buhrman–de Wolf survey *Complexity measures and decision tree complexity* (2002): `D(f) ≤ C_0(f)·C_1(f)`, `bs(f) ≤ C(f) ≤ bs(f)^2`. Gap: no elliptic instantiation; the `F_p`-cost-per-query problem is shared with A1.

### Target family
As A1.

### Full algorithmic path
1. factor base = P1473 deck; 2. relation gen = enumerate minimal 1-certificates; 3. witness = the certificate's source set, verified by P1510-R1; 4. probability `Theta(1)`; 5. `Theta(L)` sparse rows, LA `L^2`; 6. standard calibration; 7. descent by re-certifying the target; 8. certificate table offline, emission online; 9. `C_1(f)` memory per row. No stage missing.

### Cost model
`alpha=log_L C_1(f_B)`. Favorable: `C_1=polylog` ⇒ crossing. Realistic: `C_1=Theta(log q)` bits but each bit is a cubic field evaluation ⇒ same collapse as A1. Compare rho `q^{1/2}`, IC baseline `q^{3/5}`.

### Why the existing negative results do not already kill it
Same as A1: `C_1` is degree-free; P1512-R1/P1511-R2 do not bound it.

### Likely fatal obstruction
`C_1(f_B) ≥ 5` trivially, and each certificate bit costs a P1510 cubic evaluation; certificate *size* small but certificate *verification* cubic ⇒ no field-op win.

### Minimal falsifying experiment
`L∈{8,16,32}`; measure exact `C_0,C_1` on true vs random decks; positive control = short-certificate planted function; negative control = random-x; `×5` seeds.

### Quantitative promotion gate
`alpha<3/2` including per-query field cost, decreasing trend, LOO max `<3/2`.

### Proof track
`C_1(f_B)=O(polylog L)`.

### Disproof track
`C_1(f_B)=Theta(log q)` with cubic per-bit cost ⇒ collapse.

### Reproduction artifact
`experiment_contract_p1623_certificate_dual_meter.md`; `p1623_certificate_dual.py`; `p1623_certificate_dual.json`; `p1623_audit.py`; `ECFG-P1623`.

---

## Candidate: CUTTING-PLANES-A3  (ECFG-P1624)

### One-sentence mechanism
Exploit Cutting-Planes / Lovász–Schrijver semialgebraic proof size of the *infeasibility* of a low-support two-large-prime enrichment as an RT-1472 `delta`-ceiling meter — the missing proof-complexity rung below SOS (batch4) and Sherali–Adams (batch12).

### Status
HYPOTHESIS (meter/barrier hybrid; asymptotic partner D2).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Chvátal–Gomory; Cook–Coullard–Turán; Lovász–Schrijver). Distinct from SOS-LB-D1 (batch4, degree), SHERALI-ADAMS (batch12, LP hierarchy levels), POLYCALC-D2 (batch7, Nullstellensatz degree).

### Semantic fingerprint F(C)
object: the integer program "does a `delta>1/4` enriched pair-support exist"; operations: Chvátal–Gomory rounding cuts; hidden structure: integrality gap of the pair-occupancy polytope; discarded: real relaxation slack; retained: rounded lattice constraints; relation primitive: n/a (supply meter); compression: cut-count; rank: Chvátal rank; descent: n/a; cost exponent: `delta`-ceiling from the LS rank.

### Nearest ledger entries
SOS-LB-D1 (batch4); SHERALI-ADAMS-RANK-BARRIER-D2 (batch12); DELSARTE-LP-A2 (batch8); MATUNION-INDEP-D2 (batch5); CONTAINER-CEILING-A3 (batch9). Distinction: CP/LS uses **integer rounding rank** (Chvátal rank), a measure none of the SDP/LP-hierarchy/coding/matroid supply meters use.

### Nearest literature
Chvátal, *Edmonds polytopes and a hierarchy of combinatorial problems* (1973); Lovász–Schrijver, *Cones of matrices and set-functions* (1991); Grigoriev–Hirsch–Pasechnik CP lower bounds. Gap: no elliptic pair-support instantiation.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck as in P1471–P1475.

### Full algorithmic path (supply-meter form)
1. factor base = P1471 explicit two-large-prime deck; 2. write the pair-occupancy IP; 3. compute CP/LS rank of the `delta>1/4` cut; 4–9. supply-meter only — bound the achievable `delta` and feed P1473+ collectors. **INCOMPLETE on stages 5–7 by design** (it is a supply ceiling, not a full backend) — labelled INCOMPLETE for descent, complete for the RT-1472 supply question.

### Cost model
Not a backend; outputs a `delta` ceiling. If Chvátal rank forces `delta ≤ 1/4`, this *is* the RT-1472 closure. Compare: RT-1472 needs `delta>1/4` to beat exponent `2/3`.

### Why the existing negative results do not already kill it
SOS/SA are relaxation-degree/level measures; CP integer rank is incomparable — an LP with low SA rank can have high Chvátal rank and vice versa.

### Likely fatal obstruction
The honest two-large-prime polytope may have **Chvátal rank 1** (occupancy constraints already integral) ⇒ CP proves nothing ⇒ inconclusive.

### Minimal falsifying experiment
`L∈{8,16,32}`; compute exact CP/LS rank of the enrichment cut on true vs random decks; positive control = a planted high-Chvátal-rank instance; negative control = the equidistributed hash deck.

### Quantitative promotion gate (barrier form)
CP/LS rank ⇒ `delta ≤ 1/4` unconditionally in the CP model ⇒ closes RT-1472 for explicit advice.

### Proof track
Show the pair-occupancy IP has Chvátal rank `≥ 2` with the rounded constraint forcing `delta ≤ 1/4`.

### Disproof track
Exhibit a rank-1 integral formulation ⇒ meter vacuous.

### Reproduction artifact
`experiment_contract_p1624_cutting_planes_delta_ceiling.md`; `p1624_cutting_planes.py`; `p1624_cutting_planes.json`; `p1624_audit.py`; `ECFG-P1624`.

---

## Candidate: SEGRE-EXCESS-B1  (ECFG-P1625)  ★ representation winner

### One-sentence mechanism
Exploit the **non-transversality** of the five-point membership intersection: represent the relation as a Fulton–MacPherson *refined* intersection whose class is the **Segre class of the excess normal bundle**, capturing exactly the excess information the scalar-linear Chow atomizer (P1512-R1) discarded — and test whether the Segre class admits an output-sensitive `<L^{1.5}` evaluation the ordinary class provably cannot.

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (documented search: Fulton *Intersection Theory* 1998; Aluffi Segre-class computations; recent regularly-embedded-component Segre formulas — **no discrete-log / Semaev application found**). LEDGER-NEW.

### Semantic fingerprint F(C)
- algebraic object: the excess-intersection cycle of the five diagonal-sum conditions on `E^5`, and its Segre class `s(Z,E^5)` where `Z` is the (higher-than-expected-dimension) excess locus;
- available public operations: Chern/Segre-class arithmetic on the blow-up of the excess locus;
- hidden structure: the **excess normal bundle** `N` measuring how far the five conditions are from transverse — this is the precise carrier of the "nonlinear-circuit exception" left open by P1512-R1;
- information discarded: nothing (Segre retains the excess that the ordinary product drops);
- information retained: excess multiplicity per component;
- relation-generation primitive: read source rows off the residual/Segre decomposition (Fulton's residual intersection formula);
- compression primitive: the Segre class is supported on the excess locus, potentially far smaller than the full `binom(2r+4,5)` cycle;
- rank mechanism: refined class degree vs `Omega(r^5)`;
- descent mechanism: residual intersection of the target with the factor-base cycle;
- dominant cost exponent: `deg s(Z,E^5)` in `r`.

### Nearest ledger entries
1. **P1512-R1** (source-labelled scalar-linear Chow/Tate atomizer, `Omega(r^5)`). **Exact distinction:** P1512-R1's `3m ≥ sum_R nu_R = binom(2r+4,5)` bound is a statement about the **ordinary** intersection class / `deg(det M) ≤ dim`. The Segre/excess class is a **different cycle** (Fulton Ch. 6–9): it is supported on the *excess* locus and its degree is governed by the excess bundle rank, not by `dim M`. If the excess bundle has rank `< 5`, the Segre degree can be sub-`r^5`. This is the one representation P1512-R1 explicitly leaves open ("target-specialized nonlinear-circuit exception").
2. **SYZYGY-REGULARITY-B2 (batch4)** — minimal free resolution/Betti table. Distinction: Betti numbers measure the *resolution* of the factor-base ideal; the Segre class measures the *excess of an intersection* — different invariants (Betti is `Tor`, Segre is a Chow class).
3. **GKZ-DMODULE-B2 (batch8)** — holonomic rank = normalized volume. Distinction: GKZ counts branches by mixed volume of the *Newton polytope*; Segre counts by excess multiplicity of the *intersection* — the polytope is transverse-toric, the Segre is refined-non-transverse.
4. **APOLARITY-ATOMIZER-A2 (batch4)** — Waring/catalecticant nonlinear compiler. Distinction: apolarity is a symmetric-tensor decomposition; Segre is an intersection-theoretic class — no shared operation.
5. **NEWTON-OKOUNKOV-B3 (batch9)** — graded descent filtration. Distinction: Okounkov bodies are a valuation filtration on sections; Segre is a Chow-class degree — incomparable.

### Nearest literature
- Fulton, *Intersection Theory* (2nd ed. 1998), Ch. 6 (excess intersection), Ch. 9 (residual intersection formula), Ch. 4 (Segre classes).
- Aluffi, *Computing characteristic classes / Segre classes of subschemes of toric varieties* (2015+): algorithmic Segre-class computation via blow-ups — the concrete evaluation route.
- *Segre classes of schemes with regularly embedded components* (2025): Segre = polynomial in Chern classes of normal bundles when components meet transversely — the boundary case B1 must avoid.
- Claim/assumption/gap: these give **general-position** Segre-class algorithms; the elliptic five-point locus's excess-bundle rank over `F_p` is unmeasured, and whether the Segre support is sub-`r^5` is exactly the open question.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`, `E^5` with the five signed diagonal-sum conditions `A2/A3`; exclude curves where the five conditions are generically transverse (there Segre = ordinary, no gain) — the hypothesis needs *genuine* excess.

### Full algorithmic path
1. **Factor base:** P1473 deck of `L` source x-coordinates on `E`.
2. **Relation generation:** form the excess locus `Z` of the five diagonal-sum conditions in `E^5`; blow up along `Z`; the exceptional divisor's Segre class decomposes into residual components each carrying a source tuple (Fulton residual formula).
3. **Witness extraction & verification:** each residual component names a five-source relation; re-verify with the P1510-R1 marked-resultant compiler (independent, exact).
4. **Relation probability:** governed by the number of Segre residual components with `F_p`-rational support ≈ `min(1, L^5/q)` in the RT-1476 model.
5. **Matrix:** `Theta(L)` rows, sparse; LA `L^2`.
6. **Factor-log calibration:** standard.
7. **Descent:** residual intersection of the target point with the factor-base cycle.
8. **Offline/online:** blow-up and Segre-class *structure* is target-blind (offline); residual extraction per target is online.
9. **Memory/parallelism:** Segre class stored on the excess locus (`O(|Z|)` memory); parallel over components.

No stage missing.

### Cost model
Setup: one blow-up + Chern-class arithmetic on `Z`, `poly(r)`. Per-target: evaluate residual components, cost `= deg s(Z,E^5)·polylog`. **If** excess-bundle rank `< 5` so that `deg s(Z,E^5)=O(r^{5-c})` for `c≥1`, then per-row query is `q^{(5-c)/5·(1/1)}`; the RT-1476 crossing needs the effective row query exponent `< 3/2` in `L`, i.e. Segre degree `< L^{1.5}=r^{1.5}`. Compare: ordinary class `binom(2r+4,5)=Theta(r^5)` (P1512-R1 floor), rho `q^{1/2}=r^{2.5}`, IC baseline `q^{3/5}=r^3`.

### Why the existing negative results do not already kill it
P1512-R1 proves `Omega(r^5)` **for the ordinary intersection class** via `deg(det M) ≤ dim`. The Segre class of the excess bundle is provably a *different* cycle (Fulton Ch. 6): its degree is not bounded by `dim M`, it is bounded by the excess-bundle rank. P1512-R1's proof never constructs the excess bundle — it sums local multiplicities `nu_R` of the *ordinary* class. The new mathematical operation is **blowing up the non-transverse locus and reading the residual/Segre decomposition** — an operation absent from every prior atomizer.

### Likely fatal obstruction
The excess normal bundle of the five diagonal-sum conditions almost certainly has **rank equal to the codimension defect = `Theta(r)`** (each source contributes one excess direction), so `deg s(Z,E^5) = Theta(r^5)` and the Segre class reproduces the P1512-R1 floor exactly — the excess is "large" precisely because the payload cycle has length `binom(2r+4,5)`. Near-certain kill.

### Minimal falsifying experiment
Toy sizes `r∈{4,6,8}` (three), ordinary prime-order curves `q≈r^5`; compute the **exact** excess-bundle rank and `deg s(Z,E^5)` via an explicit blow-up (Sage/Macaulay2) on each; **positive control** = a synthetic intersection engineered to have excess rank 1 (Segre degree `O(r)`, must recover a short backend); **negative control** = a generically transverse five-condition system (Segre = ordinary, must reproduce `r^5`); randomized coefficient seeds `×5`; ordinary prime-order control curves throughout.

### Quantitative promotion gate
Require measured `deg s(Z,E^5) = O(r^{beta})` with `beta < 1.5` and a **decreasing** `log_r(deg Segre)` trend across the three sizes, LOO max `< 1.5`. Correctness of the residual decomposition alone is *not* the gate — the Segre *degree exponent* must fall below `3/2`.

### Proof track
Theorem: the excess normal bundle `N_{Z/E^5}` of the five signed diagonal-sum conditions has rank `≤ c` independent of `r`, hence `deg s(Z,E^5)=O(r^{c})` with `c<1.5`. (This would be the representation-changing breakthrough.)

### Disproof track
Prove `rank N_{Z/E^5} = Theta(r)` (each source is an independent excess direction) ⇒ `deg s(Z,E^5)=Theta(r^5)` ⇒ Segre reproduces P1512-R1. (Expected.) A single toy measurement of excess rank on `r=4,6,8` scaling as `Theta(r)` disproves it.

### Reproduction artifact
Contract `experiment_contract_p1625_segre_excess_atomizer.md`; impl `tasks/ecdlp_index_calculus/p1625_segre_excess_atomizer.py`; result `p1625_segre_excess_atomizer.json`; audit `p1625_audit.py`; ledger `ECFG-P1625`.

---

## Candidate: ARAKELOV-HEIGHT-B2  (ECFG-P1626)

### One-sentence mechanism
Exploit the *global* Arakelov / Bost–Gillet–Soulé arithmetic-intersection height of the factor-base sections as an RT-1472 `delta`-supply meter combining all archimedean and non-archimedean places at once.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Bost–Gillet–Soulé; Faltings; Zhang equidistribution). Distinct from all prior supply meters, which live at a **single** place (Lang–Weil count = one prime; Adolphson–Sperber/Ax–Katz = p-adic; Shearer = archimedean entropy). Arakelov combines them globally.

### Semantic fingerprint F(C)
object: arithmetic self-intersection number `hat{deg}` of the factor-base divisor on the arithmetic surface; operations: arithmetic intersection at all places; hidden structure: global height concentration of the two-large-prime pairs; discarded: none (global); retained: per-place local heights; relation primitive: n/a; compression: height defect vs equidistribution; rank: n/a; descent: n/a; cost exponent: `delta` from height concentration.

### Nearest ledger entries
LANGWEIL-SUPPLY-D2 (batch6, single-prime count); ADOLPHSPERBER-A2 (batch7, p-adic valuation); SHEARER-D3 (batch8, entropy); EXPLICIT-FORMULA-C3 (batch6, Weil explicit formula); AX-KATZ-BARRIER-D3 (batch9). Distinction: those are single-place; Arakelov is the global arithmetic-intersection combination — a strictly different invariant.

### Nearest literature
Bost–Gillet–Soulé, *Heights of projective varieties and positive Green forms* (1994); Zhang, *Equidistribution of small points* (1998); Bilu equidistribution. Gap: no factor-base-supply instantiation; the concentration question is open.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck.

### Full algorithmic path (supply meter)
1. factor base = P1471 deck; 2. compute the arithmetic-intersection height of the pair-support divisor; 3. compare to the equidistribution baseline; 4–9. supply-meter only (INCOMPLETE for descent by design — a `delta` ceiling).

### Cost model
Outputs `delta` from the height defect. Height equidistribution (Szpiro–Ullmo–Zhang) predicts `delta→0` on average.

### Why the existing negative results do not already kill it
Single-place meters cannot see cross-place cancellation; Arakelov can. A globally-concentrated support undetected at each single place is the only escape hatch this meter probes.

### Likely fatal obstruction
Height equidistribution forces the honest support to equidistribute ⇒ `delta→0` ⇒ reproduces the P1475 character-bucket negative (`delta≈0`).

### Minimal falsifying experiment
`L∈{8,16,32}`; compute arithmetic heights of true vs random decks; positive control = a planted height-concentrated divisor; negative control = equidistributed hash deck; `×5` seeds.

### Quantitative promotion gate
`delta>1/4` measured, increasing trend — else barrier `delta ≤ 1/4`.

### Proof track
Height concentration bound `delta>1/4` for the elliptic pair support.

### Disproof track
Zhang equidistribution ⇒ `delta→0`.

### Reproduction artifact
`experiment_contract_p1626_arakelov_height_supply.md`; `p1626_arakelov_height.py`; `p1626_arakelov_height.json`; `p1626_audit.py`; `ECFG-P1626`.

---

## Candidate: HECKE-TL-B3  (ECFG-P1627)

### One-sentence mechanism
Exploit a Temperley–Lieb / Hecke-algebra **planar-diagram** contraction of the symmetrized Semaev 5-tensor that never materializes the full tensor, seeking a diagram-rank collapse below `L^{1.5}`.

### Status
HYPOTHESIS. **INCOMPLETE** (descent path depends on a planarity lemma not yet established).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Temperley–Lieb; Jones; Hecke algebras of type A). Distinct from Cohn–Umans (batch6, group-algebra triple product), Holant/matchgate (batch3), immanant (batch12), GKZ (batch8).

### Semantic fingerprint F(C)
object: symmetrized Semaev `S5` as a planar tensor network; operations: TL diagram composition; hidden structure: planar contractibility; discarded: non-planar crossings; retained: planar diagram basis; relation primitive: diagram evaluation; compression: TL rank (Catalan-bounded); rank: TL cell-module dimension; descent: contract target leg; cost exponent: TL rank in `L`.

### Nearest ledger entries
COHNUMANS-B1 (batch6); HOLANT-C1 (batch3); IMMANANT-INTERPOLATION-B2 (batch12); GKZ-DMODULE-B2 (batch8); SCHURPLETHYSM-B3 (batch7). Distinction: TL is the *planar* subcategory — a genuinely different diagram algebra with Catalan-dimensional cell modules, not the full symmetric/matchgate/hypergeometric structure.

### Nearest literature
Temperley–Lieb (1971); Jones (1983); Graham–Lehrer cellular algebras. Gap: no Semaev instantiation; planarity of the 5-point relation unverified.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`.

### Full algorithmic path
1. factor base = P1473 deck; 2. build `S5` as a tensor network; 3. **INCOMPLETE** — needs a lemma that the network is planar/TL-representable; 4–9 contingent.

### Cost model
If planar, TL rank ≤ Catalan`(5)`-bounded per contraction ⇒ possible `alpha` collapse. Realistic: the 5-point relation is non-planar ⇒ no TL reduction.

### Why the existing negative results do not already kill it
The matchgate/Holant closure (batch3 HOLDICH-D3) is about *planar-Boolean-signature* holographic reductions; TL cell-module rank is a distinct decomposition of the *symmetric-group* action.

### Likely fatal obstruction
The symmetrized 5-tensor is **non-planar** (five mutually-summed points force crossings) ⇒ TL basis does not span ⇒ no rank collapse.

### Minimal falsifying experiment
`L∈{8,16,32}`; test planarity and measure TL cell-module rank of `S5`; positive control = a planar 3-point sub-relation; negative control = random 5-tensor; `×5` seeds.

### Quantitative promotion gate
TL contraction cost exponent `< 3/2`, decreasing trend.

### Proof track
`S5` is TL-representable with `O(polylog L)` rank.

### Disproof track
Exhibit a forced crossing ⇒ non-planar ⇒ vacuous.

### Reproduction artifact
`experiment_contract_p1627_hecke_tl_contraction.md`; `p1627_hecke_tl.py`; `p1627_hecke_tl.json`; `p1627_audit.py`; `ECFG-P1627`.

---

## Candidate: RANDOM-RESTRICTION-C1  (ECFG-P1628)  ★ high-risk winner

### One-sentence mechanism
Exploit Håstad random restriction / switching-lemma shrinkage: test whether the `m=5` membership function collapses to a small decision tree under a random restriction of the source coordinates, yielding a sub-`L^{1.5}` **average-case** membership backend over a `1-o(1)` fraction of targets.

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (documented search: Håstad switching lemma; Furst–Saxe–Sipser; Rossman shrinkage — **no application to elliptic membership** found). LEDGER-NEW.

### Semantic fingerprint F(C)
- algebraic object: the membership DNF/CNF `f_B` over source-presence literals, subjected to a random restriction `rho` fixing a `p`-fraction of source coordinates;
- available public operations: fix a random subset of factor-base memberships (a partial relation), evaluate the residual predicate;
- hidden structure: **shrinkage** — whether the restricted `f_B|_rho` has small decision-tree depth with high probability;
- information discarded: the unrestricted (worst-case) targets;
- information retained: the `1-o(1)` fraction where the tree shrinks;
- relation-generation primitive: the shrunken decision tree emits source rows for restricted targets;
- compression primitive: switching-lemma tree depth after restriction;
- rank mechanism: n/a (query meter);
- descent mechanism: restrict-then-solve on the target;
- dominant cost exponent: expected restricted tree depth `E_rho[D(f_B|_rho)]` in `L`.

### Nearest ledger entries
1. **PROBABILISTIC-POLY-C3 (batch8)** — probabilistic polynomials. Distinction: prob-poly randomizes the *polynomial*; random restriction randomizes the *input assignment* and exploits shrinkage — different randomization axis.
2. **DEQUANTIZED-SAMPLING-C1 (batch10)** — sample-and-query stable rank. Distinction: dequantized sampling is a linear-algebraic sketch; random restriction is a Boolean simplification.
3. **CORRELATED-PEEL-A3 (batch4)** — Wormald DE 2-core peeling. Distinction: peeling removes low-degree *graph* vertices; restriction fixes *function* variables — different objects.
4. **MOSER-ENTROPY-COMPRESSION-C3 (batch10)** — constructive entropy compression. Distinction: Moser bounds a *randomized-algorithm* runtime; switching bounds *residual circuit depth*.
5. **APPROXDEG-D1 (batch8)** — approximate degree. Distinction: switching-lemma tree depth ≠ approximate degree (a shallow-after-restriction function can have high `deg~`).

### Nearest literature
- Håstad, *Almost optimal lower bounds for small depth circuits* (1986) — the switching lemma.
- Furst–Saxe–Sipser (1984); Rossman, *shrinkage of De Morgan formulas* (2019). Gap: switching lemmas require **bounded-depth Boolean** structure; whether elliptic membership over `F_p` arithmetic has any AC0-shallow representation is the open question — almost certainly it does not, which is why this is high-risk.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`; **average-case over public random targets** (this is an average-case, not worst-case, candidate — stated explicitly).

### Full algorithmic path
1. **Factor base:** P1473 deck of `L` sources.
2. **Relation generation:** draw a random restriction `rho` fixing a `p`-fraction of source-presence bits (a partial relation prefix); evaluate the residual membership predicate `f_B|_rho`; if it shrinks to a shallow tree, enumerate its leaves as source rows.
3. **Witness extraction & verification:** each leaf certificate re-verified by P1510-R1.
4. **Relation probability:** the fraction of targets on which shrinkage occurs; the gate needs `1-o(1)`.
5. **Matrix:** `Theta(L)` sparse rows; LA `L^2`.
6. **Factor-log calibration:** standard on the shrunken fraction; worst-case targets fall back to rho descent.
7. **Descent:** restrict-then-solve the target.
8. **Offline/online:** the restriction distribution is target-blind (offline); per-target residual evaluation is online.
9. **Memory/parallelism:** one tree per restriction; parallel over restrictions.

No stage missing.

### Cost model
Per row: `E_rho[2^{D(f_B|_rho)}]` field-evaluations. Switching-lemma bound (if it applied): `Pr[D(f_B|_rho) > t] ≤ (5 p L)^t`, giving expected depth `O(1)` for suitable `p` — a crossing at `q^{2/5}`. **Realistic:** `f_B` over `F_p` arithmetic has no bounded-depth Boolean form; the residual predicate stays high-degree ⇒ no shrinkage ⇒ per-row cost stays at the P1511-R2 cubic input `Theta(r^3)`. Compare rho `q^{1/2}`, IC baseline `q^{3/5}`.

### Why the existing negative results do not already kill it
Every prior degree/rank/circuit closure is **worst-case**; none measures average-case shrinkage under random restriction. The new operation — **randomly fixing a partial relation and measuring residual tree depth** — is untried, and average-case is a genuinely different regime (a `1-o(1)`-fraction backend plus rho fallback is still a valid single-target speedup if the fraction is large enough).

### Likely fatal obstruction
The switching lemma is a theorem about **AC0 / bounded-depth Boolean circuits**. Elliptic membership is an `F_p`-arithmetic predicate of degree `Theta(L)`; it has no shallow Boolean representation, so restriction does not shrink it — the residual predicate is as hard as the original. Near-certain kill.

### Minimal falsifying experiment
Toy sizes `L∈{8,16,32}` (three), ordinary prime-order curves `q≈L^5`; for each, sample random restrictions `rho` at several rates `p`, measure the **empirical** residual decision-tree depth distribution of `f_B|_rho`; **positive control** = a synthetic shallow-DNF membership proxy (must shrink); **negative control** = random-`F_p` predicate (must not shrink); randomized seeds `×5`; report the fraction of targets with `D(f_B|_rho) ≤ (1/2)log_2 L`.

### Quantitative promotion gate
Require: (i) a `1-o(1)` fraction of targets with residual depth giving per-row exponent `alpha<3/2`, **and** (ii) a **decreasing** `alpha` trend across the three sizes. Correctness of the shrunken-fraction relations alone is *not* the gate; the *fraction* and *exponent* together must beat the rho-fallback blend.

### Proof track
Theorem: `f_B` admits a depth-`d` bounded-fan-in representation with `d=O(1)` after restriction rate `p=Theta(1/L)`, so `E_rho[D(f_B|_rho)]=polylog L`. (Would require an AC0-type representation of elliptic membership — the crux.)

### Disproof track
Prove `f_B|_rho` retains degree `Theta(L)` for all restrictions of rate `o(1)` (elliptic membership has no low-depth Boolean form) ⇒ no shrinkage. A single toy measurement showing flat residual-depth across `p` disproves it.

### Reproduction artifact
Contract `experiment_contract_p1628_random_restriction_shrinkage.md`; impl `tasks/ecdlp_index_calculus/p1628_random_restriction.py`; result `p1628_random_restriction.json`; audit `p1628_audit.py`; ledger `ECFG-P1628`.

---

## Candidate: SPECTRAHEDRAL-SHADOW-C2  (ECFG-P1629)

### One-sentence mechanism
Represent five-point membership feasibility as a projected spectrahedron (spectrahedral shadow) and test whether Helton–Nie projected-SDP structure gives a sub-`L^{1.5}` feasibility oracle.

### Status
CONJECTURE. **Reject-tier risk** (no `F_p` continuum for SDP).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Helton–Nie; Scheiderer spectrahedral-shadow theory). Distinct from SOS-LASSERRE-A1 (batch4, moment certificate) and BOOTSTRAP-SPECTRAL-C2 (batch6, SDP gap).

### Semantic fingerprint F(C)
object: membership feasibility as a projected LMI; operations: SDP projection; hidden structure: spectrahedral-shadow lifting number; discarded: exact `F_p` arithmetic (SDP is real/complex); retained: convex relaxation feasibility; relation primitive: SDP feasibility → candidate row; compression: shadow lift dimension; rank: SDP matrix rank; descent: target feasibility; cost exponent: lift dimension.

### Nearest ledger entries
SOS-LASSERRE-A1 (batch4); BOOTSTRAP-SPECTRAL-C2 (batch6); BEREZIN-PFAFFIAN-COMMONNORM-C1 (batch11); LORENTZIAN-LOGCONCAVE-C2 (batch11); SHERALI-ADAMS-PSEUDODIST-B1 (batch12). Distinction: spectrahedral *shadow* lift dimension is a projection-complexity measure distinct from SOS degree, spectral gap, Pfaffian, or LP pseudo-distribution.

### Nearest literature
Helton–Nie, *Semidefinite representation of convex sets* (2009); Scheiderer, *Spectrahedral shadows* (2018). Gap: SDP is inherently real; no exact `F_p` transfer — the reject-risk.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`.

### Full algorithmic path
1. factor base = P1473 deck; 2. write membership as an LMI feasibility; 3. project to a spectrahedral shadow; 4–9 **INCOMPLETE/reject-risk**: no exact-`F_p` recovery from a real SDP feasibility certificate.

### Cost model
If a low-lift shadow existed, feasibility oracle sub-`L^{1.5}`. Realistic: SDP gives a real-number relaxation with no exact `F_p` relation recovery ⇒ no valid ECDLP relation.

### Why the existing negative results do not already kill it
Spectrahedral-shadow lift is not SOS degree (batch4) nor spectral gap (batch6) — a genuinely different convex-geometry measure.

### Likely fatal obstruction
No `F_p` continuum: SDP feasibility over `R`/`C` does not certify an exact finite-field relation. Reject-tier unless an exact rounding is exhibited.

### Minimal falsifying experiment
`L∈{8,16,32}`; test whether any spectrahedral shadow of the membership LMI rounds to an exact `F_p` relation; positive control = a rational-feasible planted instance; negative control = random LMI; `×5` seeds.

### Quantitative promotion gate
Exact `F_p` relation recovery from a sub-`L^{1.5}` shadow oracle — else reject.

### Proof track
Exact-rounding theorem from real shadow to `F_p` relation.

### Disproof track
No-`F_p`-continuum obstruction (expected).

### Reproduction artifact
`experiment_contract_p1629_spectrahedral_shadow.md`; `p1629_spectrahedral_shadow.py`; `p1629_spectrahedral_shadow.json`; `p1629_audit.py`; `ECFG-P1629`.

---

## Candidate: EXTRACTOR-CONDENSER-C3  (ECFG-P1630)

### One-sentence mechanism
Model the two-large-prime pair-support as a min-entropy source and test whether a seeded extractor/condenser certifies `delta>1/4` concentration — or, in the barrier direction, its impossibility.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Nisan–Zuckerman; Guruswami–Umans–Vadhan condensers). Distinct from LDLR-DELTA-METER-A3 (batch11, detectability).

### Semantic fingerprint F(C)
object: pair-support as a `k`-source; operations: seeded extraction; hidden structure: min-entropy deficiency; discarded: source structure below the entropy floor; retained: extractable randomness; relation primitive: n/a; compression: condenser output length; rank: n/a; descent: n/a; cost exponent: `delta` from entropy concentration.

### Nearest ledger entries
LDLR-DELTA-METER-A3 (batch11); SHEARER-D3 (batch8); DELSARTE-LP-A2 (batch8); ENERGY-D1 (batch3); MOSER-ENTROPY-COMPRESSION-C3 (batch10). Distinction: extractor/condenser output length is a randomness-extraction measure distinct from likelihood-ratio detectability, entropy submodularity, coding LP, additive energy, or algorithmic entropy compression.

### Nearest literature
Nisan–Zuckerman (1996); Guruswami–Umans–Vadhan (2009). Gap: extractors certify *extractable randomness*, not *rank-exploitable concentration* — the likely failure mode.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck.

### Full algorithmic path (supply meter)
1. factor base = P1471 deck; 2. estimate min-entropy of the pair-support; 3. apply a condenser and measure concentration; 4–9 supply-meter only (INCOMPLETE for descent).

### Cost model
Outputs `delta` from concentration. Realistic: extraction certifies detectability, not the graph-cycle rank RT-1472 needs (same failure as LDLR-A3).

### Why the existing negative results do not already kill it
Condenser output length is not the LDLR likelihood ratio; it is a distinct randomness measure that could in principle see structured concentration.

### Likely fatal obstruction
Detection ≠ rank-exploitation: even a certified low-entropy support need not give the graph cycles/rank RT-1472 requires (P1471 measured cycle surplus 0 despite structure).

### Minimal falsifying experiment
`L∈{8,16,32}`; extractor/condenser on true vs random decks; positive control = a planted low-entropy support; negative control = uniform deck; `×5` seeds.

### Quantitative promotion gate
`delta>1/4` with *rank-exploitable* cycles (not just detectability), increasing trend.

### Proof track
Concentration ⇒ cycle-rank surplus.

### Disproof track
Detection-only (expected).

### Reproduction artifact
`experiment_contract_p1630_extractor_condenser_supply.md`; `p1630_extractor_condenser.py`; `p1630_extractor_condenser.json`; `p1630_audit.py`; `ECFG-P1630`.

---

## Candidate: SENSITIVITY-DEGREE-BARRIER-D1  (ECFG-P1631)

### One-sentence mechanism
Use Huang's theorem (`s(f) ≥ sqrt(deg f)`) contrapositively: if the `m=5` membership function has degree `Theta(L)`, then `s(f_B) ≥ sqrt(L)`, forcing decision-tree depth `D(f_B) ≥ s(f_B) ≥ sqrt(L)` and hence query exponent `alpha ≥ 1/2` in *bit* queries — and, in the field-op model, an `alpha ≥ 3/2` floor for RT-1476 in the decision-tree class.

### Status
HYPOTHESIS (barrier; asymptotic partner of A1).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Huang 2019; Nisan–Szegedy). Distinct from all batch10 circuit barriers (algebraic degree) and batch8 approx-degree.

### Semantic fingerprint F(C)
object: `f_B` and its real degree `deg(f_B)`; operations: the `s ≥ sqrt(deg)` inequality; hidden structure: high real degree forces high sensitivity forces deep trees; discarded: n/a; retained: the degree→sensitivity→depth chain; relation primitive: n/a; compression: n/a; rank: n/a; descent: same tree; cost exponent: `alpha` floor.

### Nearest ledger entries
APPROXDEG-D1 (batch8); SHIFTED-PARTIALS-A1 (batch10); NISAN-NC-RANK-A2 (batch10); RAZ-MULTILINEAR-FORMULA-D3 (batch11); SENSITIVITY-BLOCK-A1 (this batch). Distinction: D1 uses the **exact** Huang `s ≥ sqrt(deg)` bound, not approximate degree, not shifted partials, not nc-ABP width, not multilinear formula rank.

### Nearest literature
Huang (Annals 2019); Nisan–Szegedy (1994) `deg ≤ bs^2`. Gap: elliptic membership degree `Theta(L)` is expected but not proven; the bit-to-field-op translation must be pinned.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`.

### Full algorithmic path (barrier)
1. establish `deg(f_B)=Theta(L)`; 2. apply Huang `s ≥ sqrt(deg)`; 3. conclude `D ≥ sqrt(L)` bits; 4. translate to the field-op model to reach `alpha ≥ 3/2`. Barrier, not backend.

### Cost model
If it bites: `alpha ≥ 3/2` in the decision-tree class ⇒ **closes RT-1476** for any decision-tree/certificate backend (the class A1/A2/C1 live in).

### Why the existing negative results do not already kill it
No prior barrier uses the sensitivity–degree inequality; approx-degree (batch8) gives a *lower* bound of a different flavor and does not entail the `sqrt(deg)` sensitivity floor.

### Likely fatal obstruction
The bit-query lower bound `D ≥ sqrt(L)` is in the **wrong currency**: RT-1476's `alpha` counts `L`-sized field operations, and `sqrt(L)` bit-queries could in principle be `O(1)` field ops ⇒ the translation may only give `alpha ≥ 1/2·(1/5)`... i.e. the barrier may land *below* `3/2` and be inconclusive.

### Minimal falsifying experiment
`L∈{8,16,32}`; measure exact `deg(f_B)` and `s(f_B)`, confirm `s ≥ sqrt(deg)`; positive control = a low-degree function (small `s`); negative control = full-degree membership; `×5` seeds.

### Quantitative promotion gate (barrier)
Demonstrate the field-op translation yields `alpha ≥ 3/2` ⇒ closes RT-1476 in the decision-tree model.

### Proof track
`deg(f_B)=Theta(L)` ⇒ (Huang) `D(f_B) ≥ sqrt(L)` ⇒ field-op `alpha ≥ 3/2`.

### Disproof track
Show the translation only gives `alpha < 3/2` ⇒ inconclusive.

### Reproduction artifact
`experiment_contract_p1631_sensitivity_degree_barrier.md`; `p1631_sensitivity_degree_barrier.py`; `p1631_sensitivity_degree_barrier.json`; `p1631_audit.py`; `ECFG-P1631`.

---

## Candidate: CUTTING-PLANES-RANK-BARRIER-D2  (ECFG-P1632)

### One-sentence mechanism
A Chvátal-rank / Lovász–Schrijver rank lower bound on the two-large-prime enrichment polytope forces `delta ≤ 1/4` unconditionally in the CP proof model — the asymptotic partner of A3.

### Status
HYPOTHESIS (barrier).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Chvátal; Grigoriev–Hirsch–Pasechnik CP lower bounds). Distinct from SHERALI-ADAMS-RANK-BARRIER-D2 (batch12), SOS-LB-D1 (batch4), MATUNION-INDEP-D2 (batch5).

### Semantic fingerprint F(C)
object: pair-occupancy IP; operations: Chvátal rank; hidden structure: integer-rounding depth; discarded: LP slack; retained: rounded cuts; relation primitive: n/a; compression: n/a; rank: Chvátal/LS rank; descent: n/a; cost exponent: `delta` ceiling.

### Nearest ledger entries
SHERALI-ADAMS-RANK-BARRIER-D2 (batch12); SOS-LB-D1 (batch4); MATUNION-INDEP-D2 (batch5); LANGWEIL-SUPPLY-D2 (batch6); AX-KATZ-BARRIER-D3 (batch9). Distinction: Chvátal integer rank ≠ SA level ≠ SOS degree ≠ matroid independence ≠ point-count ≠ p-adic congruence.

### Nearest literature
Chvátal (1973); Lovász–Schrijver (1991); Grigoriev–Hirsch–Pasechnik (2002). Gap: elliptic pair-polytope rank unmeasured.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`.

### Full algorithmic path (barrier)
1. write the enrichment IP; 2. bound its Chvátal/LS rank; 3. conclude `delta ≤ 1/4`. Barrier.

### Cost model
If it bites: `delta ≤ 1/4` ⇒ **closes RT-1472** for explicit advice.

### Why the existing negative results do not already kill it
Chvátal integer rank is incomparable to SA/SOS relaxation measures; a rank-1 SA polytope can have high Chvátal rank.

### Likely fatal obstruction
The honest polytope may already be integral (Chvátal rank 1) ⇒ no bound ⇒ inconclusive.

### Minimal falsifying experiment
`L∈{8,16,32}`; compute Chvátal rank on true vs random decks; positive control = high-rank planted instance; negative control = integral hash deck; `×5` seeds.

### Quantitative promotion gate (barrier)
Chvátal rank ⇒ `delta ≤ 1/4` ⇒ closes RT-1472.

### Proof track
Rank `≥ 2` with the rounded cut forcing `delta ≤ 1/4`.

### Disproof track
Rank-1 integral formulation ⇒ vacuous.

### Reproduction artifact
`experiment_contract_p1632_cutting_planes_rank_barrier.md`; `p1632_cutting_planes_rank.py`; `p1632_cutting_planes_rank.json`; `p1632_audit.py`; `ECFG-P1632`.

---

## Candidate: BORODIN-COOK-TIMESPACE-D3  (ECFG-P1633)

### One-sentence mechanism
Apply the Borodin–Cook multi-output time-space tradeoff to the batch relation-generation stage (a multi-output function emitting `Theta(r)` source rows), forcing `T·S = Omega(r^{c})` and hence a setup×query product above rho for any branching-program backend.

### Status
HYPOTHESIS (barrier).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Borodin–Cook 1982; Beame–Saks–Sun–Vee 2003). Distinct from CELL-PROBE-CHRONOGRAM-D1 (batch12, dynamic cell-probe) and PROOF-SPACE-PEBBLING-D1 (batch11, static proof space).

### Semantic fingerprint F(C)
object: the multi-output relation generator `G: targets -> Theta(r) source rows`; operations: R-way branching-program steps; hidden structure: output-set incompressibility; discarded: n/a; retained: the `T·S` product; relation primitive: n/a (barrier on the generator); compression: n/a; rank: n/a; descent: same generator on the target; cost exponent: `T·S` floor.

### Nearest ledger entries
CELL-PROBE-CHRONOGRAM-D1 (batch12); PROOF-SPACE-PEBBLING-D1 (batch11); ELUSIVE-FUNCTIONS-D1 (batch10); DEPTH-REDUCTION-CHASM-D2 (batch10); RIGIDITY-A1 (batch8). Distinction: Borodin–Cook is the classic **computational** multi-output `T·S` method (probabilistic, same bound for randomized/deterministic BPs); it is neither the dynamic cell-probe update model (batch12) nor static proof/red-blue pebbling space (batch11) nor a circuit-image elusiveness bound.

### Nearest literature
Borodin–Cook, *A time-space tradeoff for sorting on a general sequential model* (1982) — `TS=Omega(n^2)`; Beame–Saks–Sun–Vee, *Time-space tradeoff lower bounds for randomized computation* (2003); recent multi-output separations (arXiv 2306.15817, 2023). Gap: the Borodin–Cook "many outputs, each with few consistent inputs" hypothesis must be verified for the elliptic relation generator.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`.

### Full algorithmic path (barrier)
1. model the relation generator as a multi-output branching program; 2. verify the Borodin–Cook output-embedding hypothesis (each output row has few consistent input assignments); 3. conclude `T·S = Omega(r^{c})`; 4. compare `T·S` to the rho budget. Barrier.

### Cost model
If it bites: `T·S = Omega(r^c)`; with the RT-1476 sparse-LA `S=Theta(r^2)` state, `T ≥ Omega(r^{c-2})`; the crossing needs total `< q^{1/2}=r^{2.5}`, so `c ≥ 4.5` would **close RT-1476** for branching-program backends.

### Why the existing negative results do not already kill it
Borodin–Cook is a *computational* (not proof-space, not cell-probe-update) tradeoff, and it is the natural tool for the *multi-output* shape of relation generation that no prior barrier addressed — the chronogram/pebbling barriers target single-output or dynamic structures.

### Likely fatal obstruction
The Borodin–Cook embedding hypothesis may fail: if each source row is consistent with **many** target inputs (high fan-in), the `T·S` bound degrades to `Omega(r)` and lands below rho ⇒ inconclusive.

### Minimal falsifying experiment
`L∈{8,16,32}`; measure the output-embedding parameter (consistent inputs per output row) of the relation generator; positive control = a sorting-like generator with the tight embedding; negative control = a high-fan-in generator; `×5` seeds.

### Quantitative promotion gate (barrier)
`T·S = Omega(r^{4.5})` ⇒ closes RT-1476 for branching-program backends.

### Proof track
Verify the Borodin–Cook embedding ⇒ `T·S=Omega(r^{4.5})`.

### Disproof track
High fan-in ⇒ weak bound ⇒ inconclusive.

### Reproduction artifact
`experiment_contract_p1633_borodin_cook_timespace.md`; `p1633_borodin_cook_timespace.py`; `p1633_borodin_cook_timespace.json`; `p1633_audit.py`; `ECFG-P1633`.

---

## 4. Ranking

Scores (0–5) on: (D) distance from prior ledger mechanisms; (V) plausibility of an exact verifier; (X) chance of moving an exponent not a constant; (P) complete-path coverage; (F) toy-scale falsifiability; (L) literature-novelty confidence; (R) hidden-preprocessing/memory risk (higher = safer).

| ID | Cand | D | V | X | P | F | L | R | notes |
|---|---|---|---|---|---|---|---|---|---|
| P1622 | SENSITIVITY-BLOCK-A1 | 4 | 5 | 3 | 5 | 5 | 4 | 4 | conservative winner |
| P1623 | CERTIFICATE-DUAL-A2 | 3 | 5 | 3 | 5 | 5 | 4 | 4 | near-dup of A1 chain |
| P1624 | CUTTING-PLANES-A3 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | INCOMPLETE descent (meter) |
| P1625 | SEGRE-EXCESS-B1 | 5 | 5 | 4 | 5 | 4 | 5 | 3 | representation winner |
| P1626 | ARAKELOV-HEIGHT-B2 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | supply meter |
| P1627 | HECKE-TL-B3 | 4 | 3 | 3 | 2 | 4 | 4 | 3 | INCOMPLETE (planarity) |
| P1628 | RANDOM-RESTRICTION-C1 | 5 | 4 | 4 | 5 | 4 | 5 | 3 | high-risk winner |
| P1629 | SPECTRAHEDRAL-SHADOW-C2 | 4 | 2 | 3 | 2 | 3 | 4 | 2 | reject-risk (no F_p continuum) |
| P1630 | EXTRACTOR-CONDENSER-C3 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | supply meter |
| P1631 | SENSITIVITY-DEGREE-BARRIER-D1 | 4 | 4 | 4 | 4 | 5 | 4 | 5 | closes RT-1476 (DT class) |
| P1632 | CUTTING-PLANES-RANK-BARRIER-D2 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | closes RT-1472 (CP model) |
| P1633 | BORODIN-COOK-TIMESPACE-D3 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | closes RT-1476 (BP class) |

**Rejections under the discipline (novelty <3, or no complete descent route, or no rho comparison, or no precise ledger distinction):**
- **SPECTRAHEDRAL-SHADOW-C2 (P1629): REJECTED** — verifier plausibility 2, no exact `F_p` recovery route (no-continuum), descent INCOMPLETE. Retained only as a "does any shadow round to `F_p`" probe.
- **CERTIFICATE-DUAL-A2 (P1623): DEMOTED** — distance 3, essentially the `C ≥ bs` node of the same A1 chain; kept as a sub-measure of A1, not an independent lane.
- **HECKE-TL-B3 (P1627): INCOMPLETE** — descent contingent on an unproven planarity lemma; retained as a Phase-0 planarity probe only.

All other candidates pass the gate (novelty ≥3, complete or explicitly-scoped-meter path, explicit rho comparison, precise ledger distinction).

### Selected winners

1. **Best conservative:** SENSITIVITY-BLOCK-A1 (P1622).
2. **Best representation-changing:** SEGRE-EXCESS-B1 (P1625).
3. **Best high-risk:** RANDOM-RESTRICTION-C1 (P1628).

---

## 5. Experiment contracts + first executable commands (three winners)

### Contract — EXP-P1622 (SENSITIVITY-BLOCK-A1)
- **Hypothesis:** the elliptic `m=5` membership predicate `f_B` has block sensitivity `bs(f_B)=O(polylog L)`, so a decision-tree backend achieves per-row query exponent `alpha<3/2` *including per-query field cost*.
- **Frozen protocol:** ordinary prime-order curves at `L∈{8,16,32}`, `q≈L^5`; compute exact `s, bs, C_0, C_1, D` of `f_B` on the true subgroup deck; instrument the field-op cost of one membership query via the P1510-R1 compiler; positive control = planted low-`bs` proxy; negative control = random-x deck; 5 seeds each.
- **Promotion gate:** `alpha = log_L(queries × field-op-per-query) < 3/2`, decreasing across `{8,16,32}`, LOO max `< 3/2`.
- **Deliverables:** contract md, `p1622_sensitivity_block_meter.py`, result+note JSON, independent audit rejecting ≥5 mutations.
- **Expected outcome (pre-registered):** near-certain kill — `bs=Theta(log q)` bits, each bit a cubic field evaluation ⇒ `alpha` collapses to the P1511-R2 `r^3` floor. Scoped negative, not a lower bound against non-decision-tree backends.

**First command:**
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1622_sensitivity_block_meter.py \
  --sizes 8,16,32 --qexp 5 --seeds 5 \
  --deck subgroup_x --controls random_x,planted_lowbs \
  --measure s,bs,C0,C1,D --charge-field-op-per-query \
  --out results/p1622_sensitivity_block_meter.json
```

### Contract — EXP-P1625 (SEGRE-EXCESS-B1)
- **Hypothesis:** the excess normal bundle `N_{Z/E^5}` of the five signed diagonal-sum conditions has rank `≤ c` (constant), so `deg s(Z,E^5)=O(r^{c})` with `c<1.5` — a refined-intersection atomizer below the P1512-R1 ordinary-class floor `Omega(r^5)`.
- **Frozen protocol:** ordinary prime-order curves at `r∈{4,6,8}`, `q≈r^5`; explicit blow-up of the excess locus (Sage/Macaulay2); compute exact excess-bundle rank and `deg s(Z,E^5)`; positive control = engineered excess-rank-1 intersection (must give Segre degree `O(r)`); negative control = generically transverse five-condition system (must reproduce ordinary `r^5`); re-verify every extracted residual source row with the P1510-R1 compiler; 5 coefficient seeds.
- **Promotion gate:** `deg s(Z,E^5)=O(r^{beta})`, `beta<1.5`, decreasing `log_r` trend across `{4,6,8}`, LOO max `<1.5`. Residual-decomposition *correctness* is explicitly **not** the gate — the Segre *degree exponent* must fall below `3/2`.
- **Deliverables:** contract md, `p1625_segre_excess_atomizer.py`, result+note JSON, independent audit reconstructing the Segre class and rejecting ≥5 mutations.
- **Expected outcome (pre-registered):** near-certain kill — excess-bundle rank `=Theta(r)` (one excess direction per source) ⇒ `deg s(Z,E^5)=Theta(r^5)`, reproducing P1512-R1. Scoped negative that would *close the excess/Segre representation of the nonlinear-circuit exception by name*.

**First command:**
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1625_segre_excess_atomizer.py \
  --sizes 4,6,8 --qexp 5 --seeds 5 \
  --excess-locus five_diagonal_sum --blowup explicit \
  --measure excess_bundle_rank,segre_degree \
  --controls transverse_five_condition,planted_excess_rank1 \
  --verify-rows p1510r1_compiler \
  --out results/p1625_segre_excess_atomizer.json
```

### Contract — EXP-P1628 (RANDOM-RESTRICTION-C1)
- **Hypothesis:** under a random restriction of the source coordinates at rate `p`, `f_B|_rho` shrinks to a shallow decision tree on a `1-o(1)` fraction of targets, giving an average-case backend with per-row exponent `alpha<3/2` (worst-case targets fall back to rho descent).
- **Frozen protocol:** ordinary prime-order curves at `L∈{8,16,32}`, `q≈L^5`, average-case over public random targets; sample random restrictions at rates `p∈{1/L, 2/L, 4/L}`; measure the empirical residual decision-tree-depth distribution of `f_B|_rho`; positive control = shallow-DNF membership proxy (must shrink); negative control = random-`F_p` predicate (must not); 5 seeds; report the fraction of targets with `D(f_B|_rho) ≤ (1/2)log_2 L`.
- **Promotion gate:** a `1-o(1)` target fraction with per-row `alpha<3/2` **and** decreasing `alpha` across `{8,16,32}`, such that the shrunken-fraction + rho-fallback blend beats `q^{1/2}`.
- **Deliverables:** contract md, `p1628_random_restriction.py`, result+note JSON, independent audit rejecting ≥5 mutations.
- **Expected outcome (pre-registered):** near-certain kill — elliptic membership has no bounded-depth Boolean form, so the switching lemma does not apply and `f_B|_rho` stays degree-`Theta(L)`; no shrinkage. Scoped negative confined to the decision-tree/AC0 model; explicitly not a bound against algebraic backends.

**First command:**
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1628_random_restriction.py \
  --sizes 8,16,32 --qexp 5 --seeds 5 --avg-case-targets public_random \
  --restrict-rates 0.125,0.0625,0.03125 \
  --measure residual_tree_depth_distribution,shrunk_fraction \
  --controls shallow_dnf_proxy,random_fp_predicate \
  --out results/p1628_random_restriction.json
```

---

## 6. Red-team — are the three winners disguised repetitions or cost-negative?

**Adversarial thesis:** each winner is either (a) a renamed prior lane, or (b) cost-negative by a floor already measured in the ledger.

- **SENSITIVITY-BLOCK-A1 (P1622).** *Disguised-repetition charge:* it is APPROXDEG-D1 (batch8) with different vocabulary. **Rebuttal:** `bs/s/C/D` are exact combinatorial measures with the Huang chain `D ≤ C^2 ≤ (bs·s)^2`; approximate degree is a bounded-error polynomial measure — a function can be shallow-after-certificate yet high-`deg~`. Distinct meter. *Cost-negative charge (the decisive one):* the bit-query count `D(f_B)` ignores the field-op cost of answering one query, which is the cubic P1510 evaluation; so even `D=O(1)` buys nothing in the `L^alpha` currency. **Verdict: cost-negative by the P1511-R2 `r^3` input floor with near-certainty.** A scoped negative, correctly labelled. Not a crossing.
- **SEGRE-EXCESS-B1 (P1625).** *Disguised-repetition charge:* it is P1512-R1 re-run, since the excess is the same cycle. **Rebuttal:** the Segre class of the excess bundle is provably a *different* cycle from the ordinary intersection class P1512-R1 bounded (Fulton Ch. 6 vs the ordinary product); P1512-R1's `deg(det M) ≤ dim` argument does not construct the excess bundle at all. The distinction is mathematical, not terminological. *Cost-negative charge (the decisive one):* the excess-bundle rank is almost certainly `Theta(r)` (one excess direction per source), so `deg s(Z,E^5)=Theta(r^5)` reproduces the P1512-R1 floor exactly. **Verdict: near-certain cost-negative, reproducing `Omega(r^5)`** — but it *closes the excess/Segre representation of the nonlinear-circuit exception by name*, which is genuine ledger value. Not a crossing.
- **RANDOM-RESTRICTION-C1 (P1628).** *Disguised-repetition charge:* it is PROBABILISTIC-POLY-C3 (batch8) or DEQUANTIZED-SAMPLING-C1 (batch10). **Rebuttal:** those randomize the *polynomial* / take a *linear-algebraic sketch*; random restriction randomizes the *input assignment* and exploits Boolean shrinkage — a different randomization axis and a different (average-case) regime. *Cost-negative charge (the decisive one):* the switching lemma requires bounded-depth Boolean structure; elliptic membership is an `F_p`-arithmetic predicate of degree `Theta(L)` with no AC0-shallow form, so no shrinkage occurs and the residual predicate is as hard as the original. **Verdict: near-certain cost-negative (no shrinkage), scoped to the decision-tree/AC0 model.** Not a crossing.

**Red-team summary.** All three winners are **scoped tightenings / lane closures with near-certain named kills**, exactly as in batches 5–12 — none is a rho crossing. The three **barriers (D1/D2/D3)** are the higher-EV work: each imports a lower-bound technology no prior barrier used, and each threshold, if reached, *formally closes a live gate* (D1 → RT-1476 in the decision-tree class; D2 → RT-1472 in the CP model; D3 → RT-1476 in the branching-program class). The most honest reading of report 15 is the same as reports 7–14: **the mechanism space is saturated, the marginal candidate is a scoped negative, and the barrier arm should be prioritized to formally close RT-1472/RT-1476 rather than to keep proposing attack lanes.**

---

## 7. Claim discipline

Everything above is **CONJECTURE/HYPOTHESIS/OPEN**. No candidate has been implemented or run in this report; all cost claims are symbolic and all "near-certain kills" are pre-registered predictions, not measurements. Correctness of any relation certificate is explicitly distinguished from verified ECDLP recovery, and toy-scale evidence would never be presented as crypto-scale. A failed candidate is a **scoped negative result**, not evidence that prime-field ECDLP is unimprovable. **No rho crossing is claimed. RT-1472 and RT-1476 remain open.**

**Reports reviewed:** 14 (idea_generation 20260717 … 20260719_batch6). **This report:** 15 (batch13). **Ledger IDs proposed:** ECFG-P1622 … ECFG-P1633. **ID families covered in inventory:** ECFG-{P,NR,RT,MX}, ISO-{NR,OBS,RT}-{ONK,IKD}, IDEA, RQ, H, EV, DEC.

Sources: [Huang sensitivity conjecture / ECCC 2020-002](https://eccc.weizmann.ac.il/report/2020/002/download/), [block sensitivity vs sensitivity (arXiv 1306.4466)](https://arxiv.org/pdf/1306.4466), [Fulton Intersection Theory / Segre classes (arXiv 2109.05061)](https://arxiv.org/pdf/2109.05061), [Segre classes with regularly embedded components (arXiv 2511.06799)](https://arxiv.org/pdf/2511.06799), [Borodin–Cook multi-output time-space (arXiv 2306.15817)](https://arxiv.org/html/2306.15817), [Beame branching-program time-space](https://homes.cs.washington.edu/~beame/papers/focsbranch.pdf).
