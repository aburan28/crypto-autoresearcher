# Research-Director Idea Generation — 2026-07-17

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Mission:** propose *mechanism-new*, falsifiable directions whose *complete* cost could
eventually beat the single-target Pollard-rho `0.886·sqrt(n)` baseline for ECDLP over
**ordinary prime fields**. Toy correctness, a new coordinate system, a relation
certificate, faster preprocessing, or a solver swap is explicitly **not** a breakthrough.

This is an autonomous scheduled run (no user present). Choices are noted inline.

---

## 0. Review scope and inventory census

**Sources read (all four required, plus derived corpus):**

1. `research_ledger.md` (2.6 MB, 2248 lines; sections: open-frontier, active hypotheses,
   negative results, positive signals, baselines, literature map, graph-index frontier,
   negative controls, P1436/P1437 continuation).
2. `ecdlp_index_calculus_state/research_ledger.md` (648 lines; ECFG functional-graph track
   + direct-source packet track).
3. `research/non_generic_transfer_search_20260610.md` (390 lines; the transfer/decomposition
   channel search + PO-001..006 appendix).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` (10 primary entries).
5. Referenced corpus: 1070 files in `research/` (PO_transfer 177 files, ISO_* atlas, PAPER_*,
   p14xx barrier/theorem notes), sampled by highest-numbered contracts, all `*_theorem.md`,
   `*_result.md`, `*barrier*` notes, and the negative-controls tables.

**Census (machine-readable count):**

- **Distinct negative IDs: 638** (`NR-001 .. NR-1477`, prefix-collapsed 555 numeric):
  ECFG-NR 502 (span 303..1477, none below 303), TRANSFER-NR 53, ISO-AR-NR 56,
  ISO-SP/RM/CW-NR 3, SHA1-N 9, core `NR-` 13, ECFG-IR 2.
- **Active hypotheses ≈ 427:** ECFG-H 382 (H303..H687), ISO-AR/SP 33, TRANSFER-H 8, SHA1-H 4.
- **Positive signals ≈ 968:** ECFG-P 864 (..P1470), TRANSFER-P 64 (PO9..PO95), ISO-AR-POS 36,
  plus ECFG-RT/MX restricted-model rows, SHA1-P 4.
- **ID families covered:** ECFG (Evans functional graph + coordinate index-calculus — the
  dominant lane), TRANSFER/PO (cover/Prym/Jacobian correspondence), ISO-AR/ISO-SP
  (oriented-CM isogeny + self-pairing recovery), SHA-1 seed-bounty (off-topic to ECDLP),
  and the bare `NR-` core.

**Bottom line from the inventory (load-bearing):** *No ledger entry demonstrates a
complete-cost single-target speedup over Pollard rho on prime-field ECDLP.* Every empirical
"below rho" is amortized-many-target and/or setup-uncharged. The only rho-beating paths on
record are two **conditional restricted-model targets that remain unrealized** (ECFG-RT-1472,
ECFG-RT-1476).

---

## 1. Fingerprint inventory by mechanism family (compressed)

`F(entry) = (object, ops, hidden-structure, discarded, retained, relation-primitive,
compression-primitive, rank-mechanism, descent-mechanism, dominant-cost-exponent)`.

| Fam | Object | Structure exploited | Relation / compression primitive | Rank mechanism | Descent | Dominant cost | Outcome / scoped boundary |
|---|---|---|---|---|---|---|---|
| **M1 ECFG coordinate IC** | `E/F_p`, points as graph nodes, `B≈n^(1/5)` | recursive `S1=F,S2=F+F,S3=S2+F` five-term `A+C=R`; coord bases `interval_x`, `x_residue_mod4`, rational-map, `x^L=1` subgroup, autos | pair-compiler, shared-x buckets, CRT/product trees, preimage DAG | weighted factor-log matrix, sparse full-rank | one-factor online descent | membership / public generator cost; rank-poor cheap bases | **TOY, no single-target win.** Explicit-join = `B^3=n^0.6`; held-out end-to-end `22..66× rho`. |
| **M2 large-prime graph** | 1-LP residual / 2-LP endpoint graph | occupancy of residual columns; endpoint-incidence cycles | pair table, signless nullity | graph cycle rank | LP-log propagation | 1-LP exponent `(1+β)/2=0.6` at `β=1/5`; 2-LP setup `Θ(L²)` | **RT-1472:** 2-LP crosses `1/2` only if advice enrichment `δ>1/4`; explicit decks give `δ≤1/4`. |
| **M3 implicit membership backend** | m-ary Semaev-style pair/five-term membership | `x^L=1` sparse subgroup S3, char buckets, CM orbit, serial-S3 state, resultants | implicit predicate eval | sparse full-rank (target) | shared backend | query exponent `alpha` | **RT-1476:** backend with `alpha<3/2` (m=5) / `alpha<1` (m≥4), setup `≤L²`, random support, sparse full-rank → conditionally beats rho. **All tried backends miss it** (serial-S3 `L^1.675`, resultants dense `4L²`, buckets/orbits no concentration). |
| **M4 cover/Prym/Jacobian transfer** | genus-2/3 covers `X→E`, Prym `J(X)`, `Z[π]`-lattices | hidden E-isotypic block, C3/deck projectors, norm labels `z^d=h(P)` | source principal-divisor / ternary constant-sum relations, LP closure | C3-module kernels, integral Rosati Gram | calibrated logs → signed-point lookup | Prym-block certification + cover setup | **RESTRICTED THMs (PO-032/034/038/093/095):** deck/Prym maps **scalar-or-zero** on visible E-factor; best real recovery `~3376× rho`. **OPEN:** a native genus-2 correspondence engine that does **not** pull back to the x-line Semaev relation. |
| **M5 oriented-CM isogeny + self-pairing** | oriented `O_K=Z[π]`, ascending volcano, `θ(8,8)`, Kani | target-free oriented-kernel construction, `ℓ+1` lift-class bound | — | — | — | torsion-field degree | **OBSERVATION/RESTR-THM, TOY.** Isogeny-**finding**/vectorization primitive; does **not** attack rho; same-field class preserves order/trace/anomalous/supersingular/embedding/CM-field. |
| **M6 ECFG public selectors** (IC-state) | Evans graph `k→x(kB)` | depth-to-cycle, component size, indegree as public leaf selectors | frozen selector gates route relation leaves | selected-leaf event yield vs uniform | shift-and-lookup | full graph build = N edges | **NEGATIVE chain (ECFG-N001..061):** every frozen selector wins post-hoc, fails prospective validation; reverse index amortized-only. |

**Standing barriers / restricted theorems (the frontier constraints my candidates must respect):**

- **B-Dreg:** degree-of-regularity **conservation** (Yokoyama-2020-consistent,
  `PAPER_prime_field_ecdlp_resistance_map.md`): naive Semaev/Gröbner, coordinate
  reparametrization, scalar Weil-restriction/abelian-surface (NR-022), crossbred `m=3`,
  and multi-target rho all fail to lower the exploitable solving degree over `F_p`.
- **B-trace-fiber (PO-005):** for a group hom `τ:H→G`, full kernel fibers multiply successes
  and trials equally → trace-fiber multiplicity is *no* relation-probability or rank gain.
- **B-permutation (TRANSFER-NR-001, ISO-CW-NR-001):** an isogeny-transported factor base
  preserves multiplicities → measure-preserving correspondence ⇒ no rank gain.
- **B-preproc (Corrigan-Gibbs/Kogan; CHW SGGM):** generic frontier `S·T² = Ω̃(εq)`;
  structured success `≤ Õ(S·T²/q + δ·T)`. Fixed-curve online wins sit on this frontier once
  advice, bandwidth, success prob, and supported target count are charged.
- **B-explicit-edge (P1434):** explicit terminal source-edge coordinate circuits admit **no**
  compressed exact promoting rule (234/234 cells). **Loophole left explicitly open:**
  *generative / sketch-based witness recovery* (non-explicit membership).
- **B-n=1 collapse (Gaudry/Diem):** Weil-restriction subexponential IC needs a proper base
  field (`n≥2`); prime-field `n=1` has nothing to restrict → Semaev degree blows up.
  Any candidate must survive this collapse or bypass polynomial-system solving entirely.

---

## 2. Known-closed / control-only territory (negative controls)

A candidate is a **duplicate** unless it breaks one of these measured obstructions with a
*new mathematical operation*:

1. Ordinary same-field isogeny invariants (order/trace/CM class-invariant) — TRANSFER-NR-001/044, ISO-CW-NR-001.
2. Scalar Weil pullback / level-2 theta / Kummer-line charts (Dreg-preserving) — TRANSFER-NR-005/010/030/045/046, NR-022.
3. Explicit two-large-prime advice graphs — ECFG-NR-1471; RT-1472 (`δ>1/4` needed).
4. Joint factor / large-prime block-Krylov (Wiedemann/Lanczos) solving — TRANSFER-NR-042, NR-033/036.
5. Pair-residual character buckets — ECFG-NR-1475.
6. Non-invariant CM endpoint decks — ECFG-NR-1474.
7. Materialized serial-S3 backward-state polynomials (dense, `L^1.675`) — ECFG-NR-1477.
8. Dense composed resultants (degree `4L²`, zero held-out prediction) — ECFG-MX-1478.
9. Source selectors / post-hoc scheduling without an honest hit generator — ECFG-NR-303/304/305/347/348/1382; whole ECFG-N001..061 chain.
10. Relation validity without relation-derived ECDLP recovery (rowspace export) — ECFG-NR-418/420/424/425/427/428.
11. Preprocessing wins that lose to rho on offline/memory/advice/target count — ECFG-NR-1406/1433, TRANSFER-NR-037/041.
12. Twist / extension-field channels (adjacent invalid-curve, not original subgroup) — `ISO_GOAL_FOUND_p224_twist`.

A large share of high-numbered ECFG-NR (1439–1465), all SHA1-N, and the ISO-AR "V-chain"
are **instrumentation/provenance/containment** negatives — *not* mathematical dead-ends and
must not be mined as evidence against any mechanism.

---

## 3. Twelve candidates

Notation: `q≈n` prime subgroup order; `B≈n^(1/5)` factor base; `L≈B`; rho `≈0.886·n^(1/2)`;
IC total `≈ B·(cost/relation) + B²(sparse LA) + descent`, with `B²=n^(2/5)<n^(1/2)` so the
sparse-LA stage is *not* the binding constraint — the **relation/membership stage** is.
The named open gate is **RT-1476**: a complete m-ary membership backend with query exponent
below the stated boundary, `≤L²` setup, random-like support, and sparse full-rank.

### Group A — conservative extensions

---

## Candidate: A1 — Polyhedral (BKK / mixed-volume) output-sensitive point decomposition

### One-sentence mechanism
Exploit the **Newton-polytope / mixed-volume (BKK) structure** of the m-point prime-field
decomposition system to enumerate its `F_p`-roots by **polyhedral homotopy** with path-count
`= mixed volume` rather than the dense Bézout/Dreg bound, reducing the per-relation membership
cost `C` below the RT-1476 `L^(3/2)` backend boundary.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (literature agent: no tropical/Newton-polytope/BKK analysis of Semaev
membership found; EC-application gap is the reduction step, machinery mature elsewhere).

### Semantic fingerprint
- object: m-point (`m=4,5`) EC decomposition system over `F_p`, `B≈n^(1/5)`.
- ops: public curve arithmetic, symmetric-function evaluation.
- hidden structure: sparsity pattern (support/Newton polytope) of `S_m` and the recursive
  `S3` five-term system.
- discarded: dense-degree accounting; keeps only the polytope.
- retained: exact monomial support → mixed volume.
- relation primitive: five-term `A+C=R` membership.
- compression primitive: polyhedral homotopy path pruning (mixed volume ≪ Bézout iff polytope thin).
- rank mechanism: unchanged weighted factor-log matrix (sparse full-rank target).
- descent: standard one-factor online descent.
- dominant cost exponent: mixed-volume growth in `log q` — **the object of measurement**.

### Nearest ledger entries
1. **B-Dreg / resistance-map** — both bound decomposition-solve cost, but Dreg measures Gröbner
   *solving degree*; mixed volume measures *solution count / homotopy path count*. A system can
   have high Dreg yet low mixed volume (thin polytope). **Distinction: different complexity
   invariant, never measured in the ledger.**
2. **ECFG-MX-1478 (dense resultants, `4L²`)** — resultants materialize the dense elimination
   ideal; polyhedral homotopy never forms it. **Distinction: sparse solver vs dense elimination.**
3. **ECFG-NR-1477 (serial-S3 state, `L^1.675`)** — that measures dense *state polynomials*;
   A1 measures the *root variety's polytope*. **Distinction: variety geometry vs state density.**
4. **P1416 exact five-term control (`B^3=n^0.6`)** — same relation shape; A1 changes only the
   root-enumeration subroutine. **Distinction: enumeration algorithm, not relation definition.**
5. **RT-1476** — A1 is a *concrete instantiation attempt* of the open membership backend, not a
   new gate. **Distinction: A1 supplies a candidate backend; RT-1476 is the acceptance test.**

### Nearest literature
Semaev 2004; Gaudry 2009; Kousidis–Wiemers 2015 (first-fall degree of `S_m`);
Faugère–Huot–Joux–Renault–Vitse 2014 (symmetrized `S_m`). Gap: none analyze the *Newton
polytope / mixed volume* of `S_m`; the standard degree bound is treated as tight but never
checked against BKK.

### Target family
Random ordinary prime-order short-Weierstrass `E/F_p`, `p` prime, `n=#E` prime, `j∉{0,1728}`.
Excluded: anomalous, supersingular, small embedding degree, CM by small discriminant.

### Full algorithmic path
1. **Factor-base construction:** `interval_x` / rational-map base, size `B≈n^(1/5)`. (`O(B)` group ops.)
2. **Relation generation:** for a public shift `R`, form the five-term `S3` system; compute its
   support → Newton polytope; run polyhedral homotopy over `F_p` (or `\bar F_p` with rational
   recovery), tracking mixed-volume-many paths.
3. **Witness extraction/verification:** each recovered root replays exact EC additions `A+C=R`
   with `A∈S2, C∈S3`; verify group-law identity and factor indices.
4. **Relation probability:** `≈ K·B^5/q = Θ(B)` supply per `K=Θ(B)` shifts (P1438).
5. **Matrix:** `Θ(B)×B`, density `O(1/B)`, target sparse full-rank (`t≥B−1`).
6. **Factor-log calibration:** standard.
7. **Descent:** one-factor online descent per target.
8. **Offline/online:** polytope/homotopy start-system is curve-independent and precomputable
   (offline); path tracking is online.
9. **Memory/parallel:** homotopy paths are embarrassingly parallel, `O(mixed-vol)` memory.

### Cost model
Per-relation cost `= mixed-volume(S_m-system) · (path-tracking cost)`. Naive dense bound gives
`≈ (2^(m-2))^(m-1)` per shift → dominates. **Promotion requires** empirically-measured mixed
volume growing so that total relation-gen `= B·MV(B)` yields exponent `<1/2` in `n`, i.e.
`MV(B) < B^(3/2)` (the RT-1476 boundary), ideally `MV(B)=poly(m)·B^(o(1))`. Compare: rho
`n^0.5`; explicit-join IC `n^0.6`; A1 target `<n^0.5`.

### Why existing negatives do not kill it
Avoids **B-Dreg** (mixed volume ⊥ solving degree), avoids **MX-1478/NR-1477** (never forms
resultant or dense state). New operation: **polyhedral homotopy path enumeration keyed on the
`S_m` support polytope.**

### Likely fatal obstruction
Semaev polynomials are *symmetric and near-dense* in their arguments; the Newton polytope is
likely close to the full simplex, so `MV ≈ Bézout` and there is no gain. (This is exactly what
the experiment measures.)

### Minimal falsifying experiment
Compute (in Sage / `phcpy` / `msolve`) the exact mixed volume of the `m=4,5` `S3` five-term
system for `E/F_p` at three sizes `p≈2^20,2^24,2^28`, seeds `20260717..20260722`, vs the dense
Bézout count; positive control = a deliberately *thin* toy system (should show `MV≪Bézout`);
negative control = a random dense system of matched degree (should show `MV≈Bézout`). Fit
`log MV / log B`.

### Quantitative promotion gate
Measured `MV(B)` fits exponent `<3/2` in `B` (equivalently relation-gen exponent `<1/2` in `n`)
across all three sizes, **and** the recovered relations reach sparse rank `t≥B−1`. Correctness
alone is *not* the gate.

### Proof track
Theorem to establish: `MV(S_m^(F_p)-system) = O(B^(3/2−ε))`. Would follow from a structural
sparsity theorem on `S_m` (a nontrivial face of its Newton polytope dominating).

### Disproof track
Show `MV = Θ(Bézout)` (dense polytope) at all three sizes ⇒ narrow to "polyhedral structure
gives no sub-Bézout handle for symmetric `S_m`," a reusable negative refining B-Dreg.

### Reproduction artifact
- contract: `research/experiment_contract_a1_polyhedral_decomposition_20260717.md`
- impl: `experiments/ecdlp_prime_field/a1_mixed_volume_semaev.sage`
- result: `.../a1_mixed_volume_result.json`
- audit: `.../a1_mixed_volume_verify.sage`
- ledger id: `POLY-A1`

---

## Candidate: A2 — Elliptic-net / EDS-smoothness relation channel

### One-sentence mechanism
Exploit the **bilinear elliptic-net (Stange) / elliptic-divisibility-sequence recurrence** so
that a factor base of "EDS-smooth" points yields relations from the **net's integer/`F_p`
division-value factorization** rather than the group-law Semaev relation.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (xedni-calculus lineage is known-failed; elliptic nets are known
(Stange 2007); their use as an IC *factor-base smoothness* channel over `F_p` is not in the
ledger and not standard).

### Semantic fingerprint
- object: elliptic net `W: Z^k → F_p` attached to `(E, P_1..P_k)`.
- ops: net recurrence (bilinear Somos-type), public evaluation.
- hidden structure: multiplicative/divisibility structure of net values.
- discarded: group-law composition; keeps net-value factorization pattern.
- retained: which "primes"/factor-columns divide net values (smoothness).
- relation primitive: net-value multiplicative relation among factor-base indices.
- compression primitive: shared subterms in the net recurrence lattice.
- rank mechanism: exponent matrix of net-value factorizations.
- descent: net-value log relation for the target index.
- dominant cost exponent: net-value smoothness probability — the object of measurement.

### Nearest ledger entries
1. **M4 cover/Prym norm-factorization `z^d=h(P)` (PO-007 target)** — both use a
   *factorization* of an auxiliary value; EDS uses the *net's own* division values, not a cover
   norm. **Distinction: intrinsic net recurrence vs external cover norm.**
2. **B-trace-fiber (PO-005)** — EDS is not a group hom fiber. **Distinction: bilinear net, not a
   homomorphism kernel.**
3. **M1 five-term relations** — both build an exponent matrix; A2's columns are net-value
   prime divisors, not EC factor-base indices. **Distinction: what a "column" is.**
4. **B-n=1 collapse** — A2 does not solve a Semaev system, so the `n=1` degree blow-up does not
   directly apply; the analogous obstruction is net-value smoothness probability.
5. **Xedni (Silverman 1998, not in ledger)** — A2's closest external precedent and its warning.

### Nearest literature
Stange 2007 (elliptic nets); Ward 1948 / Silverman EDS; Silverman 1998 xedni-calculus;
Jacobson–Koblitz–Silverman–Stein–Teske 2000 (xedni fails: lifted points force full-rank
lattice / large height). Gap: nobody has tested EDS-value *smoothness* (over `F_p`, not a lift)
as a relation source.

### Target family
Random ordinary prime-order `E/F_p`. Excluded specials as A1.

### Full algorithmic path
1. factor base: points `P_i` with EDS values `W(P_i)` smooth over a chosen prime/column set.
2. relations: multiplicative dependencies among `W(mP_i+nP_j)` via the net recurrence.
3. witness/verify: replay net recurrence, verify value factorization.
4. relation probability: `Prob(W(·) is S-smooth)` — **measured**.
5. matrix: exponent matrix over the smoothness-prime columns.
6. calibration: solve for point "logs" via net-value log relations.
7. descent: express target via a smooth net value.
8. offline/online: net start-values offline; per-target online.
9. memory/parallel: net evaluation parallel; `O(B)` memory.

### Cost model
Per-relation `= (1/Prob(smooth)) · (net-eval cost)`. Over `F_p`, `W(P)∈F_p` so "smoothness" is
of a **field element**, not an integer — the standard obstruction (finite field has no size
hierarchy). Gain only if a *structured* subset of net values factors in a low-degree
`F_p[x]`-column sense. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Not a cover norm (≠ PO-007), not a group-hom fiber (≠ PO-005), not a Semaev system (≠ B-Dreg).
New operation: **net-value column factorization as the relation.**

### Likely fatal obstruction
Over `F_p` there is no smoothness hierarchy for field elements; this is the same wall that sinks
xedni. Any gain must come from an *integer/`p`-adic* lift, reintroducing the xedni height
obstruction.

### Minimal falsifying experiment
Evaluate EDS/net values for a `B≈n^(1/5)` base at `p≈2^20,2^24,2^28`; measure the fraction with
a chosen low-degree/column-structured factorization vs a random-`F_p`-element control; positive
control = a curve with engineered rational torsion (structured values); negative control =
random field elements. Fit relation-yield exponent.

### Quantitative promotion gate
Structured-smoothness relation yield produces sparse full-rank `t≥B−1` with total exponent
`<1/2`, beating the random-element control by a growing margin across three sizes.

### Proof track
Theorem: a positive-density subset of net values admits a shared low-degree factor column
(would give a real factor base). Requires a distribution theorem on EDS values mod `p`.

### Disproof track
Net-value factorization is indistinguishable from random `F_p` elements at all sizes ⇒ reusable
negative: "EDS smoothness gives no `F_p` factor base," precisely locating the xedni wall.

### Reproduction artifact
- contract: `research/experiment_contract_a2_eds_smoothness_20260717.md`
- impl: `experiments/ecdlp_prime_field/a2_elliptic_net_smoothness.sage`
- result/audit: `.../a2_eds_result.json`, `.../a2_eds_verify.sage`
- ledger id: `EDS-A2`

---

## Candidate: A3 — Output-sensitive incidence-reporting membership backend

### One-sentence mechanism
Exploit a **finite-field polynomial-partitioning / semialgebraic range-reporting data
structure** to *list* (not count) the factor-base pair-sums that land in the base in time
`O(output + B^(1/2+o(1)))`, directly instantiating the P1434 "generative/sketch-based witness
recovery" loophole and the RT-1476 backend.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT to the ledger's own incidence *counting* barrier (Ahmadi–Shparlinski
sum-product, P1447), but the *reporting data structure* (algorithmic, output-sensitive) is a
distinct object; POSSIBLY NOVEL as an EC application (Stevens–de Zeeuw machinery unused here).

### Semantic fingerprint
- object: point set `= {x(F_i)}` and query surface `= {R − F_j}` over `F_p`.
- ops: EC arithmetic, polynomial partitioning of `F_p^2`.
- hidden structure: incidence sparsity between pair-sums and the base.
- discarded: full pair enumeration `B²`.
- retained: only the incident pairs (output-sensitive).
- relation primitive: `A+C=R` pair membership.
- compression primitive: partitioning-polynomial cell decomposition (data structure).
- rank mechanism: unchanged sparse factor-log matrix.
- descent: standard.
- dominant cost exponent: query exponent `alpha` of the reporting DS — object of measurement.

### Nearest ledger entries
1. **P1447 sum-product/incidence theorem target** — the ledger has the *counting/energy bound*
   as a **barrier**; A3 is a *reporting algorithm*. **Distinction: report < count-then-filter.**
2. **P1434 explicit-edge lower bound** — A3 lives in the *generative/sketch* regime P1434
   explicitly leaves open. **Distinction: A3 targets the named loophole.**
3. **RT-1476** — A3 is a concrete backend candidate. **Distinction: candidate vs gate.**
4. **ECFG-NR-1477 serial-S3** — A3 does not materialize state; it partitions space.
5. **M1 shared-x buckets** — buckets are hashing; A3 is a geometric cell DS. **Distinction:
   algebraic-geometric partition vs hash bucket.**

### Nearest literature
Stevens–de Zeeuw 2023 (finite-field point-line incidence); polynomial method / Guth–Katz;
Ahmadi–Shparlinski (`|x(F)+x(F)|·|x(F+F)|`). Gap: no output-sensitive *reporting* DS built for
Semaev pair membership; incidence bounds are for lines/low-degree, not the `S_3` curve family.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. factor base `B≈n^(1/5)`; build a partitioning polynomial `g` of degree `D` decomposing `F_p^2`
   into cells each meeting few base points.
2. relation gen: for query `R`, locate the `O(1)`-few cells the surface `A+C=R` crosses; report
   incident pairs from those cells only.
3. witness/verify: replay `A+C=R`.
4. relation probability: unchanged `Θ(B)` supply.
5. matrix: `Θ(B)×B` sparse full-rank target.
6–9: standard calibration/descent/offline-online/parallel; DS build is offline per curve.

### Cost model
Query `= O(#incident + D + crossed-cell scan)`. Beats birthday only if `#cells crossed · cell
size` gives query exponent `alpha<1` (RT-1476 `m≥4` boundary). Build `≤L²`. Compare explicit
join `B^3` per full pass; A3 targets `B^(1+alpha)` with `alpha<1` ⇒ `<B²`.

### Why existing negatives do not kill it
Attacks the P1434 generative loophole with an algorithmic (not explicit-edge) witness generator;
avoids MX-1478 (no resultant) and NR-1477 (no state polynomials). New operation:
**semialgebraic cell reporting over `F_p^2`.**

### Likely fatal obstruction
Finite-field incidence bounds are weakest exactly in the `|P|≈q^(1/2)` regime; the partitioning
polynomial's cell-crossing count may force `alpha≥1`, collapsing to birthday cost — the
Ahmadi–Shparlinski wall the ledger already fears.

### Minimal falsifying experiment
Build a degree-`D` partitioning DS for the `B≈n^(1/5)` base at `p≈2^20,2^24,2^28`; measure
average pairs reported and cells crossed per query vs a full-scan control; positive control =
a base with planted low-incidence structure; negative control = random base. Fit query exponent
`alpha` vs `log B`.

### Quantitative promotion gate
Measured `alpha<1` (or `<3/2` in the `m=5` five-term instantiation) with `≤L²` build and sparse
full-rank relations, stable across three sizes.

### Proof track
Theorem: an `F_p` polynomial-partition of the base achieves query exponent `alpha<1`. Requires a
reporting analogue of Stevens–de Zeeuw for the `S_3` curve family.

### Disproof track
Measured `alpha≥1` at all sizes ⇒ reusable negative strengthening P1447: "output-sensitive
reporting does not beat birthday for `S_3` pair membership at `B=q^(1/5)`."

### Reproduction artifact
- contract: `research/experiment_contract_a3_incidence_reporting_20260717.md`
- impl: `experiments/ecdlp_prime_field/a3_partition_reporting.sage`
- result/audit: `.../a3_report_result.json`, `.../a3_report_verify.sage`
- ledger id: `INC-A3`

### Group B — representation changes

---

## Candidate: B1 — Nilpotent jet / dual-number lift relation filter

### One-sentence mechanism
Exploit the **non-reduced ring `F_p[ε]/(ε^k)`** (jets/arcs of `E`) so that Hasse-derivative
*tangent relations* act as an `O(1)`-cost membership **pre-filter**, cutting the failed-attempt
factor in relation generation below the group-law-only test.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (dual-number EC arithmetic exists for *constructive* crypto, not for
decomposition; no jet/arc lift of the Semaev relation found).

### Semantic fingerprint
- object: `E(F_p[ε]/(ε^k))`, extension of `E(F_p)` by `Lie(E)⊗(ε…)` (unipotent, **not** an AV).
- ops: jet arithmetic (group law over the nil-ring).
- hidden structure: tangent/derivative constraints coupling a decomposition to its
  infinitesimal neighbours.
- discarded: none of the base data.
- retained: base relation **plus** `k−1` Hasse-derivative equations.
- relation primitive: `A+C=R` lifted to jets → derivative relations in the same logs.
- compression primitive: derivative relations as a cheap rejection filter.
- rank mechanism: base weighted factor-log matrix (tangent part is additive/linear — see D1).
- descent: standard.
- dominant cost exponent: filter selectivity — object of measurement.

### Nearest ledger entries
1. **NR-022 scalar Weil restriction / abelian surface** — Weil restriction over `F_{p^2}` gives
   a *separable* AV; the jet lift over `F_p[ε]` gives a *unipotent* (`G_a`) extension.
   **Distinction: nilpotent non-reduced base vs separable field extension** — B-Dreg's proof
   assumes the latter.
2. **B-Dreg** — established for coordinate/Weil reparametrization; **untested for nilpotent
   lifts** (the tangent equations are not Galois conjugates).
3. **M1 five-term relations** — B1 keeps the relation, adds a derivative filter. **Distinction:
   pre-filter, not new columns.**
4. **B-trace-fiber (PO-005)** — jet fiber is additive, not a group-hom kernel of order `n`.
5. **M5 self-pairing** — uses `p`-torsion pairings on dual numbers (arXiv:math/0703906) for
   *pairing* theory, not decomposition. **Distinction: relation filtering vs pairing.**

### Nearest literature
Dual-number EC arithmetic; "Weil pairing on `p`-torsion over dual numbers"
(arXiv:math/0703906); Hasse-derivative theory. Gap: no decomposition/relation use.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. factor base `B≈n^(1/5)`, each point lifted to a chosen jet.
2. relation gen: candidate `A+C=R`; test base membership **and** the `k−1` tangent equations;
   accept only if all hold.
3. witness/verify: replay base + jet arithmetic.
4. relation probability: base supply `Θ(B)`, but with a smaller failed-attempt constant.
5. matrix: base sparse full-rank (tangent adds no log-rank — see D1).
6–9: standard.

### Cost model
Relation-gen cost `= (attempts) · (jet-test cost)`. The jet test is `O(k)` field ops. **Net win
only if** the tangent filter multiplies the *acceptance rate* by a factor that lowers the
attempt exponent — i.e. tangent constraints are *correlated* with base membership. If tangent
equations are independent noise, they only add constant overhead. Compare `n^0.6` explicit join.

### Why existing negatives do not kill it
Nilpotent (`G_a`) lift ≠ separable Weil restriction (NR-022) ≠ Galois-conjugate split, so B-Dreg
does not directly apply. New operation: **Hasse-derivative tangent constraints as a membership
pre-filter.**

### Likely fatal obstruction
`E(F_p[ε]) ≅ E(F_p) ⋉ Lie(E)`; the `ε`-part is an `F_p`-vector space with *trivial* (linear)
DLP, so tangent relations are **linear** and likely *independent* of base membership → filter
selectivity `≈1`, no gain (this is exactly D1, the paired refuter).

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`, generate candidate `A+C=R` triples; measure `P(tangent equations hold |
base holds)` vs `P(tangent hold)` (correlation); positive control = a jet construction with
engineered correlation; negative control = random tangent vectors. If conditional ≫ marginal,
the filter is real.

### Quantitative promotion gate
Tangent filter lowers the *measured relation-gen exponent* (not just constant) across three
sizes, keeping sparse full-rank — i.e. attempt-count exponent drops toward `<1/2` in `n`.

### Proof track
Theorem: tangent constraints are conditionally dependent on base membership (nonzero mutual
information). Would require the jet decomposition of `S_m` to couple `ε`-order terms to roots.

### Disproof track (see D1)
Prove independence ⇒ B1 gives only constant-factor gain; reusable negative "nilpotent lifts add
no relation rank."

### Reproduction artifact
- contract: `research/experiment_contract_b1_jet_filter_20260717.md`
- impl: `experiments/ecdlp_prime_field/b1_dual_number_filter.sage`
- result/audit: `.../b1_jet_result.json`, `.../b1_jet_verify.sage`
- ledger id: `JET-B1`

---

## Candidate: B2 — Tensor-train / separator-rank contraction of the S3 membership operator  *(REPRESENTATION WINNER)*

### One-sentence mechanism
Represent the recursive `S3` five-term membership as a **tensor network** over the pair-sum
chain and contract it with a **tensor-train / low-separator-rank** order, answering membership in
`O(L·r)` where `r =` the SVD separator rank across the `S2|S3` cut — plausibly `≪ L^(1/2)` even
though the serial state *polynomials* are dense (ECFG-NR-1477).

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL as an EC/Semaev application (treewidth/tensor-train contraction mature in #SAT /
quantum simulation; never applied to Semaev). Distinct from NR-1477/MX-1478 which measured
*density*, not *rank*.

### Semantic fingerprint
- object: interaction hypergraph of the `S1→S2→S3` relation, as a tensor network.
- ops: EC arithmetic to build local tensors; SVD/contraction.
- hidden structure: the **separator rank** (Schmidt rank) across the pair-sum cut.
- discarded: the full resultant / Macaulay matrix.
- retained: low-rank cores of the contraction.
- relation primitive: `A+C=R` membership as a network contraction value.
- compression primitive: tensor-train truncation at bond dimension `r`.
- rank mechanism: separator rank `r` **is** the object; sparse factor-log matrix downstream.
- descent: same backend.
- dominant cost exponent: `log r / log L` — object of measurement.

### Nearest ledger entries
1. **ECFG-NR-1477 (serial-S3 state, dense `L^1.675`)** — measured *number of nonzero monomials*
   in the state polynomial. **Distinction: B2 measures matrix/Schmidt RANK of the transfer
   operator; a dense operator can be low-rank.** This is the crux distinction.
2. **ECFG-MX-1478 (dense resultants `4L²`)** — B2 never forms the resultant. **Distinction:
   contraction order vs elimination.**
3. **RT-1476** — B2 is a concrete backend candidate: if `r=L^(alpha)` with `alpha<1`, it meets
   the `m≥4` gate. **Distinction: candidate vs gate.**
4. **M1 shared-x buckets / CRT trees** — those share *subterms*; B2 exploits *low-rank* cross-cut
   structure. **Distinction: sparsity vs rank.**
5. **B-Dreg** — Dreg bounds Gröbner solving; B2 bypasses Gröbner via contraction. **Distinction:
   different solving paradigm.**

### Nearest literature
Markov–Shi 2005 (contraction ↔ treewidth); tensor-train/MPS; weighted model counting via graph
decompositions (arXiv:1908.04381). Gap: Semaev interaction-graph treewidth and transfer-operator
separator rank never measured.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. factor base `B≈n^(1/5)`; build local tensors for each `+F` step (`S1→S2→S3`).
2. relation gen: contract the network for a query `R`; nonzero contraction ⇒ membership; recover
   the witness from the argmax path.
3. witness/verify: replay `A+C=R`.
4. relation probability: `Θ(B)` supply.
5. matrix: sparse full-rank target.
6–9: standard; the network topology is curve-independent (offline), tensors are per-curve.

### Cost model
Contraction `= O(L · r²)` per query with bond dimension `r`. **Promotion iff** `r = O(L^(alpha))`,
`alpha<1` ⇒ query `<L²`, total relation-gen `<n^(1/2)`. Setup builds `r`-truncated cores `≤L²`.
Compare NR-1477 `L^1.675`; B2 wins iff separator rank ≪ state support.

### Why existing negatives do not kill it
NR-1477 ruled out the *dense materialized state*; B2 measures a **different quantity (rank)** and
never materializes the state — a dense-but-low-rank operator contracts cheaply. New operation:
**SVD/tensor-train truncation of the pair-sum transfer operator.**

### Likely fatal obstruction
The transfer operator may be **full-rank** across the `S2|S3` cut (generic EC addition mixes all
coordinates), giving `r=Θ(L)` and query `Θ(L²)` — no gain. (This is exactly D3, the paired
lower-bound track.)

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`, `L≈n^(1/5)`, build the `S2|S3` transfer matrix and compute its numerical
`F_p`-rank / singular-value profile; positive control = a deliberately separable toy operator
(low rank); negative control = a random full-rank operator; fit `log r / log L`.

### Quantitative promotion gate
Measured separator rank `r=L^(alpha)` with `alpha<1` across all three sizes, **and** a working
`r`-truncated contraction recovers ≥ `B−1` sparse-independent relations and blind targets.

### Proof track
Theorem: the `S2|S3` transfer operator has separator rank `O(L^(1−ε))`. Would follow from a
low-treewidth / low-Schmidt-rank structure of EC addition on the chain.

### Disproof track (see D3)
Prove `r=Ω(L^(1/2+c))` ⇒ close the tensor-train loophole; reusable rank lower bound
strengthening NR-1477 from density to rank.

### Reproduction artifact
- contract: `research/experiment_contract_b2_tensor_train_membership_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2_tt_separator_rank.sage`
- result/audit: `.../b2_tt_result.json`, `.../b2_tt_verify.sage`
- ledger id: `TT-B2`

---

## Candidate: B3 — Tropical / p-adic-lift valuation descent on the Semaev variety

### One-sentence mechanism
**Lift `E` to `Z_p`** and use the `p`-adic **valuation stratification (tropicalization)** of the
Semaev variety to guide a valuation-first root search, so that decomposition roots are found by
tracking a low-dimensional tropical skeleton rather than the dense variety.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL, with a stated obstacle: `F_p` has no valuation, so a `Z_p`/function-field lift is
mandatory and itself unaddressed in the ledger.

### Semantic fingerprint
- object: Semaev variety over `Q_p`; tropical skeleton over `R`.
- ops: `p`-adic lift of curve + point arithmetic.
- hidden structure: valuation strata of decomposition roots.
- discarded: `F_p` field structure (moves to `Q_p`).
- retained: `p`-adic valuations / tropical combinatorics.
- relation primitive: `A+C=R` via valuation-guided lift.
- compression primitive: tropical skeleton (piecewise-linear) vs full variety.
- rank mechanism: standard factor-log matrix after descent to `F_p`.
- descent: Hensel/Newton from tropical strata.
- dominant cost exponent: skeleton size / lift-precision cost — object of measurement.

### Nearest ledger entries
1. **B-n=1 collapse** — B3 tries to bypass the collapse by adding a *valuation* the prime field
   lacks. **Distinction: works in a ring with a valuation (`Z_p`), not `F_p`.**
2. **A1 (BKK polytopes)** — both are polyhedral; A1 stays over `F_p` counting mixed volume, B3
   moves to `Q_p` tracking valuations. **Distinction: field of work and what the polytope buys.**
3. **Xedni / lift attacks** — B3 is a lift attack; distinct in using tropical (not height-minimizing)
   guidance. **Distinction: valuation combinatorics vs height reduction.**
4. **B-Dreg** — B3 changes the ring, so Dreg-conservation (proved over `F_p`) does not directly bind.
5. **NR-022 Weil restriction** — B3 lifts, not restricts. **Distinction: char-0 lift vs `F_p`-split.**

### Nearest literature
Maclagan–Sturmfels (tropical geometry); tropical DLP (arXiv:2101.02781, unrelated semiring
crypto). Gap: no tropicalization of Semaev; the `F_p`→`Q_p` lift step is the open crux.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. lift `(E, F_i, R)` to `Z_p` at precision `π`.
2. relation gen: tropicalize the Semaev relation; enumerate tropical solutions (skeleton
   vertices); Hensel-lift and reduce mod `p` to recover `F_p` decompositions.
3. witness/verify: replay `A+C=R` over `F_p`.
4. relation probability: `Θ(B)` supply if lift succeeds.
5. matrix: sparse full-rank target.
6–9: lift precision is the memory/time driver.

### Cost model
Cost `= (#tropical strata) · (Hensel-lift cost at precision π)`. Beats rho only if strata count is
`poly` and precision `π=O(log q)` suffices. The likely blow-up: lifting `F_p` points to `Z_p`
needs `π≈log q` and the number of lifts is exponential unless the tropical skeleton is thin.

### Why existing negatives do not kill it
Moves off `F_p`, so B-Dreg / NR-022 (both `F_p`-bound) do not directly apply. New operation:
**valuation-stratified root lifting.**

### Likely fatal obstruction
The xedni wall: generic `F_p` points lift to a full-rank height lattice; the tropical skeleton is
then as large as the variety, and precision cost dominates. Tropicalization gives no thin skeleton
for a `0`-dimensional generic fiber.

### Minimal falsifying experiment
For toy `p≈2^12,2^16,2^20` (smaller — lift is expensive), lift the `m=4` Semaev system to `Z_p`,
compute the tropical variety / skeleton size vs the naive root count; positive control = a system
with engineered valuation structure; negative control = random lift. Fit skeleton-size exponent.

### Quantitative promotion gate
Tropical skeleton size `= O(B^(1/2−ε))` (sub-birthday) with `O(log q)` precision, across three
sizes, yielding sparse full-rank relations.

### Proof track
Theorem: the Semaev tropical variety has `O(B^(1/2−ε))` skeleton vertices for generic ordinary `E`.

### Disproof track
Skeleton size `≈` full root count ⇒ reusable negative "tropicalization gives no thin skeleton for
Semaev; lift attacks stay xedni-bound."

### Reproduction artifact
- contract: `research/experiment_contract_b3_tropical_lift_20260717.md`
- impl: `experiments/ecdlp_prime_field/b3_tropical_semaev.sage`
- result/audit: `.../b3_tropical_result.json`, `.../b3_tropical_verify.sage`
- ledger id: `TROP-B3`

### Group C — high-risk speculative

---

## Candidate: C1 — Noncommutative CM-correspondence relation composition (quiver/groupoid)  *(HIGH-RISK WINNER)*

### One-sentence mechanism
Use the **class-group action groupoid** on the horizontal CM isogeny orbit as a **path/quiver
algebra**, and test whether *composing* several class-group correspondences produces a relation
operator that is **not a measure-preserving permutation** of the factor base (i.e. that
increases relation rank), unlike a single isogeny walk.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT for isogeny transfer itself (known, ruled out for P-256: NR-033/T-ISO-4);
POSSIBLY NOVEL for the specific *quiver/path-algebra composition of correspondences into a
single relation* (no precedent found).

### Semantic fingerprint
- object: CM orbit under `Cl(O)` action, as a groupoid/quiver of `ℓ`-isogeny correspondences.
- ops: horizontal isogeny evaluation, Hecke-style adjacency.
- hidden structure: noncommutative composition of correspondences.
- discarded: single-walk destination.
- retained: composed correspondence operator on the factor base.
- relation primitive: factor-base image under a composed correspondence.
- compression primitive: path-algebra relations (if non-permutation).
- rank mechanism: rank of the composed-correspondence incidence matrix — object of measurement.
- descent: isogeny-transfer descent (known poly-cost per edge).
- dominant cost exponent: composition depth vs rank gain — object of measurement.

### Nearest ledger entries
1. **M5 ISO-AR (56 entries) / oriented CM** — extensive single-walk / self-pairing work.
   **Distinction: C1 composes *many* correspondences via a path algebra to seek rank, not a
   destination.**
2. **B-permutation (TRANSFER-NR-001, ISO-CW-NR-001)** — a single correspondence permutes the
   base. **Distinction: C1 asks whether *composition* escapes permutation** (the explicit test).
3. **B-trace-fiber (PO-005)** — permutation/fiber no-gain. C1's disproof track is D2 (generalizing
   this).
4. **`ISO_cost_weighted_atlas` / `ISO_isogeny_rational_map_atlas`** — map inventories.
   **Distinction: C1 is an algebra of compositions, not an atlas of maps.**
5. **NR-033 / T-ISO-4 (no weak isogenous curve for P-256)** — closes *destination* weakness;
   C1 seeks *rank* structure, not a weak destination. **Distinction: rank vs weakness.**

### Nearest literature
Mestre graph method (isogeny graph = Hecke operator); "Spectral Theory of Isogeny Graphs"
(arXiv:2308.13913); Deuring/quaternion (supersingular). Gap: ordinary volcanoes are sparse; no
path-algebra *relation composition* formalism exists.

### Target family
Ordinary prime-order `E/F_p` with **navigable class group** (moderate discriminant, several small
split Elkies primes). Excluded: `conductor=1` flat volcanoes with trivial navigability (e.g.
P-256 per memory) — those are the negative control, not the target.

### Full algorithmic path
1. factor base = a set of CM-orbit representatives reachable by small-`ℓ` horizontal isogenies.
2. relation gen: compose `d` correspondences `T_{ℓ_1}∘…∘T_{ℓ_d}`; record the induced map on the
   factor base; extract relations from its incidence pattern.
3. witness/verify: replay each isogeny; verify the composed image.
4. relation probability: depends on non-permutation fraction — **measured**.
5. matrix: rank of the composed-correspondence incidence matrix vs a permutation null.
6–9: descent via isogeny transfer (poly per edge); memory = orbit size.

### Cost model
Cost `= (composition depth d) · (isogeny-eval cost) · (orbit size)`. Rank gain per composition
must exceed the permutation baseline (rank = 1 per permutation). Beats rho only if a `poly(log q)`
composition yields `Ω(B)` independent relations. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Single-walk permutation results (NR-001, PO-005) are about *one* correspondence; C1 tests the
*composition algebra*. New operation: **noncommutative composition of class-group correspondences.**

### Likely fatal obstruction
The class-group action is **free and transitive** (torsor) ⇒ every composition is again a single
permutation (group element), so the composed operator is *still* a permutation and D2 applies:
no rank gain. C1's whole bet is that the *incidence* (not the action) carries extra structure.

### Minimal falsifying experiment
For toy ordinary curves with navigable `Cl(O)` at `p≈2^16,2^20,2^24`, compute the rank of
depth-`d` composed-correspondence incidence matrices vs a random-permutation null and a
single-walk control; `d=1,2,3`; positive control = a deliberately non-free groupoid (composite
order structure); negative control = free-transitive torsor (should give permutation).

### Quantitative promotion gate
Composed-correspondence rank exceeds the permutation null by a factor growing with `d` and with
size, yielding `Ω(B)` independent relations at `poly(log q)` depth — rank gain, not constant.

### Proof track
Theorem: some composition of class-group correspondences on the factor base has incidence rank
`>1` (non-permutation). Would need a genuinely groupoid (non-torsor) structure.

### Disproof track (see D2)
Prove every composition is a permutation (torsor) ⇒ no rank gain; reusable
correspondence-permutation no-gain theorem generalizing PO-005/NR-001.

### Reproduction artifact
- contract: `research/experiment_contract_c1_correspondence_composition_20260717.md`
- impl: `experiments/ecdlp_isogeny/c1_quiver_composition.sage`
- result/audit: `.../c1_quiver_result.json`, `.../c1_quiver_verify.sage`
- ledger id: `QUIV-C1`

---

## Candidate: C2 — Lattès transfer-operator spectral descent

### One-sentence mechanism
Treat the degree-`ℓ²` **Lattès map `x∘[ℓ]`** on the `x`-line as an arithmetic-dynamical system,
build its **transfer (Perron–Frobenius) operator**, and search for a spectral coordinate in which
individual-log descent linearizes.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL but currently **underspecified** (literature agent): spectral Frobenius data
(SEA) computes *order*, not logs; no bridge to relation generation exists.

### Semantic fingerprint
- object: Lattès map `φ_ℓ = x∘[ℓ]` on `P^1(F_p)`; its transfer operator.
- ops: rational-map iteration, spectral decomposition.
- hidden structure: eigenfunctions of the transfer operator.
- discarded: group-law composition.
- retained: spectral/dynamical invariants.
- relation primitive: (speculative) spectral coordinate linearizing `[k]`.
- compression primitive: eigenbasis truncation.
- rank mechanism: unclear — object of investigation.
- descent: (speculative) spectral inversion of `[k]`.
- dominant cost exponent: undefined until formalized.

### Nearest ledger entries
1. **M6 ECFG functional graph** — the Evans graph *is* the dynamical system of `k→x(kB)`; C2 is
   its operator-theoretic (spectral) counterpart. **Distinction: transfer operator of the
   Lattès map vs combinatorial graph statistics.**
2. **M5 self-pairing / Frobenius** — Frobenius eigenvalues give order (char poly). **Distinction:
   C2 targets the `[ℓ]`-dynamics operator, not Frobenius.**
3. **B-preproc** — any spectral precompute must beat `S·T²=Ω̃(εq)`.
4. **RT-1476** — C2 is not a membership backend; different lane.
5. **ECFG-N001 (direct graph inversion negative)** — C2 must avoid re-deriving this.

### Nearest literature
Ruelle transfer operators / dynamical zeta functions (conceptual); SEA (Frobenius spectrum →
order). Gap: no cryptanalytic transfer-operator construction; a "spectral relation" for DLP is
undefined.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path (INCOMPLETE — flagged)
1. build transfer operator of `φ_ℓ` on a sampled `F_p` support.
2. spectral decomposition; search for a coordinate linearizing `[k]`.
3. **Stages 3–9 undefined:** no witness extraction, relation shape, rank mechanism, or descent is
   yet specified. **This candidate is INCOMPLETE and is retained only as a negative-theory seed
   (see D-note) / long-shot.**

### Cost model
Undefined (no relation shape). Cannot yet compare to rho — a rejection criterion.

### Why existing negatives do not kill it
It is orthogonal to all measured lanes, but that is because it is not yet an algorithm.

### Likely fatal obstruction
Transfer-operator eigenvalues of a Lattès map are governed by the same Frobenius/`[ℓ]`
characteristic data that already only yields *order*, not per-target logs. Almost certainly no
descent exists.

### Minimal falsifying experiment
Formalize (Theory Agent): does any eigenfunction of the `φ_ℓ` transfer operator encode a
*target-dependent* quantity (a log), or only class functions of the char poly? If only the
latter, close it.

### Quantitative promotion gate
Not eligible for promotion until a complete relation/descent path is specified. **Rejected at
ranking** on incompleteness; kept as a formalization target.

### Proof/disproof track
Disproof: prove all transfer-operator spectral invariants are class functions of Frobenius
(order-determined) ⇒ no per-target information — a clean barrier.

### Reproduction artifact
- note: `research/c2_transfer_operator_formalization_20260717.md`
- ledger id: `SPEC-C2`

---

## Candidate: C3 — Xedni-2.0: near-orthogonal global height-lattice relation lift

### One-sentence mechanism
Revisit lifting factor-base points to a global object (number field / `Z`) so that a **global
linear dependence in Mordell–Weil** projects to an `F_p` relation, using **modern lattice
reduction (LLL/BKZ) to engineer a near-orthogonal, low-height lift** that beats the original
xedni height obstruction.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (xedni is known-failed; Jacobson–Koblitz–Silverman–Stein–Teske 2000 proved
the failure mode). Included as a high-risk *precise-refutation* candidate.

### Semantic fingerprint
- object: global lift of `(E, F_i)` to a number field; Mordell–Weil lattice.
- ops: point lifting, height computation, lattice reduction.
- hidden structure: low-height global relations.
- discarded: `F_p` structure (lift to char 0).
- retained: MW linear dependencies.
- relation primitive: global `Σ a_i F_i = O` reduced mod `p`.
- compression primitive: LLL/BKZ height reduction.
- rank mechanism: MW-lattice rank.
- descent: global relation for the target.
- dominant cost exponent: lift height vs number of points — the known wall.

### Nearest ledger entries
1. **A2 EDS / B3 tropical** — all three are lift attacks. **Distinction: C3 minimizes height via
   lattice reduction; B3 uses valuation strata; A2 uses net-value factorization.**
2. **B-n=1 collapse** — C3 bypasses Semaev entirely (no polynomial system).
3. **NR-022 Weil restriction** — restriction, not lift. **Distinction: char-0 global object.**
4. **B-preproc** — lift precompute must beat the generic frontier.
5. **M4 transfer** — transfers within char `p`; C3 leaves char `p`. **Distinction: global lift.**

### Nearest literature
Silverman 1998 (xedni); Jacobson–Koblitz–Silverman–Stein–Teske 2000 (xedni fails: forcing many
points through a fixed lift makes the MW lattice full-rank / heights too large). Gap: whether
modern BKZ + a cleverer lift-point selection changes the *rank-vs-height* tradeoff (the paper
predicts no).

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. select factor-base points; lift `E` and points to a number field with controlled conductor.
2. relation gen: search for low-height MW dependencies via LLL/BKZ; reduce mod `p`.
3. witness/verify: reduce global relation to `F_p`, replay.
4. relation probability: governed by lift-height distribution.
5. matrix: MW exponent matrix.
6–9: descent via global relation; memory = lift precision.

### Cost model
The xedni wall: to force `s` points onto one lift, the lift's height grows so the search cost is
`≥ exp(height) ≫ n^(1/2)`. C3 bets BKZ changes the constant/exponent; the 2000 paper says it does
not. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Not in the ledger at all (xedni absent); the char-0 lift is orthogonal to every `F_p`-bound
negative. New operation: **lattice-reduced low-height global lift.**

### Likely fatal obstruction
Proven (2000): the number of lift conditions equals the MW rank needed, forcing height `≥` a bound
that makes the search super-`sqrt(n)`. BKZ does not change this asymptotically.

### Minimal falsifying experiment
For toy `p≈2^12,2^16`, attempt LLL/BKZ-guided lifts of a small point set; measure achieved
height vs number of simultaneously-lifted points; positive control = a curve of high rank with
small-height generators; negative control = generic curve. Fit height-vs-points curve against the
JKSST bound.

### Quantitative promotion gate
Achieved lift height grows *sub*-linearly enough that relation-search cost fits exponent `<1/2` —
i.e. a measured violation of the JKSST height bound. (Expected to fail; a clean refutation is the
value.)

### Proof track
Would require disproving the JKSST height lower bound — very unlikely.

### Disproof track
Reproduce the JKSST height blow-up at toy scale ⇒ reusable, ledger-absent negative closing the
xedni lane in this repo's accounting.

### Reproduction artifact
- contract: `research/experiment_contract_c3_xedni2_20260717.md`
- impl: `experiments/ecdlp_prime_field/c3_height_lift.sage`
- result/audit: `.../c3_xedni_result.json`, `.../c3_xedni_verify.sage`
- ledger id: `XEDNI-C3`

### Group D — negative-theory candidates (expose a loophole or barrier)

---

## Candidate: D1 — Nilpotent-lift no-rank-gain theorem

### One-sentence mechanism
Prove that relations in `E(F_p[ε]/(ε^k))` split as `(base F_p relation) ⊕ (additive tangent
relation)` with the tangent part carrying **zero discrete-log rank**, exactly bounding what jet
lifts (B1) can add.

### Status
HYPOTHESIS (provable-looking)

### Novelty classification
LEDGER-NEW (no nilpotent-lift analysis in the ledger; B-Dreg covers only separable lifts).

### Semantic fingerprint
object: `E(F_p[ε])`; ops: jet arithmetic; structure: the split `E(F_p)⋉Lie(E)`; discarded: none;
retained: the log-rank of each factor; relation primitive: jet relation; compression: n/a; rank
mechanism: **the theorem's object**; descent: n/a; cost exponent: n/a (a barrier).

### Nearest ledger entries
B-trace-fiber (PO-005, multiplicities), NR-022 (Weil restriction), B-Dreg, B1 (its partner),
`proofs_Dreg_conservation_weil_invariance.md`. Distinction: **nilpotent/unipotent base** vs
separable — none of these treat a non-reduced ring.

### Nearest literature
Structure of `E(R)` for `R` local Artinian (Lie-algebra extension); Greenberg functor. Gap: no
cryptanalytic statement.

### Target family
All ordinary prime-order `E/F_p`.

### Full algorithmic path
Theory only: (1) exhibit the exact sequence `0→Lie(E)⊗εF_p[ε]/(ε^k)→E(F_p[ε^k])→E(F_p)→0`;
(2) show the kernel is an `F_p`-vector space (trivial DLP); (3) conclude tangent relations impose
`F_p`-linear constraints on tangent coordinates, contributing **no rank** to the order-`n`
log-relation matrix. Verify on toy curves by explicit rank comparison.

### Cost model
n/a (barrier). Consequence: B1 can only be a *filter* (constant-factor), never a rank source.

### Why existing negatives do not kill it
It is a new theorem, not a repeat; complements B1.

### Likely fatal obstruction
The tangent constraints *might* correlate with base membership (giving B1 a real filter even if no
rank) — the theorem must carefully separate "no rank" from "no filtering," which are different.

### Minimal falsifying experiment
Toy `p≈2^12,2^16,2^20`: compute the rank of the log-relation matrix with and without jet-tangent
rows; the theorem predicts identical rank. A rank increase would falsify it (and vindicate B1).

### Quantitative promotion gate
Theorem proved + toy rank-equality confirmed at three sizes ⇒ closes the jet-rank loophole
(scoped negative); a rank increase ⇒ promotes B1 instead.

### Proof track
The exact-sequence argument above.

### Disproof track
A toy curve where jet rows raise rank.

### Reproduction artifact
- proof note: `research/d1_nilpotent_lift_theorem_20260717.md`
- impl: `experiments/ecdlp_prime_field/d1_jet_rank_check.sage`
- ledger id: `NILP-D1`

---

## Candidate: D2 — Correspondence-permutation no-gain theorem

### One-sentence mechanism
Prove that any finite algebraic correspondence acting on the factor base by a
**measure-preserving permutation** multiplies successes and trials equally (no
relation-probability or rank gain), unifying PO-005, TRANSFER-NR-001, ISO-CW-NR-001, and
delimiting exactly which correspondences (non-permutation / rank-increasing) could escape.

### Status
HYPOTHESIS (partly proved in special cases; generalize)

### Novelty classification
LEDGER-NEW as a *unified* theorem (the special cases exist; the general statement + escape
condition does not).

### Semantic fingerprint
object: algebraic correspondence `Γ⊂E×E'` on factor bases; structure: permutation vs non-
permutation; retained: the incidence-rank criterion; rank mechanism: **the theorem's object**;
cost exponent: n/a.

### Nearest ledger entries
PO-005 (trace-fiber), TRANSFER-NR-001 / ISO-CW-NR-001 (multiplicity preservation),
PO-032/034/038 (scalar/zero maps), C1 (its partner). Distinction: **a single criterion (incidence
non-permutation)** subsuming all, plus the *escape condition* C1 tests.

### Nearest literature
Diem/Gaudry IC (rank needs genuine relations); Howe gluing/degree bounds. Gap: no
permutation/rank dichotomy theorem for EC factor-base correspondences.

### Target family
Ordinary prime-order `E/F_p` and its correspondences.

### Full algorithmic path
Theory: (1) define the correspondence-induced bipartite incidence on `(F, F')`; (2) show that if
the induced map is a bijection preserving the counting measure, the relation matrix is a
row/column permutation of the original (rank-preserving); (3) state the escape condition:
strictly positive-dimensional or many-to-one incidence with `rank>1` per correspondence. Verify on
toy isogeny/cover correspondences.

### Cost model
n/a (barrier). Consequence: any transfer candidate must exhibit a *non-permutation* incidence to
have a chance — a concrete promotion filter for M4/C1.

### Why existing negatives do not kill it
New unifying theorem.

### Likely fatal obstruction
The interesting correspondences (Prym maps) are exactly the ones the theorem would flag as
scalar/zero (PO-038) — so the escape set may be empty for ordinary prime-field curves; the
theorem should determine whether it is.

### Minimal falsifying experiment
Toy: for a bank of isogeny/cover/Prym correspondences, classify each as permutation vs non-
permutation and correlate with measured rank gain; the theorem predicts rank gain iff non-
permutation.

### Quantitative promotion gate
Theorem proved + toy classification matches (rank gain iff non-permutation) ⇒ a reusable
promotion filter; discovery of a non-permutation ordinary-curve correspondence with rank gain ⇒
promotes that correspondence (and C1).

### Proof track
Measure-preserving-bijection ⇒ permutation-matrix argument.

### Disproof track
A measure-preserving correspondence that nonetheless raises rank (would refine the hypothesis).

### Reproduction artifact
- proof note: `research/d2_correspondence_permutation_theorem_20260717.md`
- impl: `experiments/ecdlp_isogeny/d2_correspondence_rank_classify.sage`
- ledger id: `PERM-D2`

---

## Candidate: D3 — Separator-rank lower bound for S3 membership

### One-sentence mechanism
Prove the `S2|S3` pair-sum transfer operator has **separator (Schmidt) rank
`r = Ω(L^(1/2+c))`**, upgrading NR-1477's *density* observation to a *rank* lower bound and thereby
closing the tensor-train loophole (B2) — or find the sub-`L^(1/2)` rank that opens it.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (NR-1477 measured support/density; rank is a strictly stronger, unmeasured quantity).

### Semantic fingerprint
object: `S2|S3` transfer matrix; structure: its singular-value profile; retained: separator rank;
rank mechanism: **the theorem's object**; cost exponent: `log r/log L`.

### Nearest ledger entries
ECFG-NR-1477 (dense state), ECFG-MX-1478 (dense resultant), RT-1476 (the gate), B2 (its partner).
Distinction: **rank vs density** — the load-bearing separation.

### Nearest literature
Communication-complexity / matrix-rigidity lower bounds; treewidth lower bounds. Gap: no rank
bound for the EC pair-sum operator.

### Target family
Ordinary prime-order `E/F_p`, `L≈n^(1/5)`.

### Full algorithmic path
Theory + measurement: (1) construct the `S2|S3` transfer matrix; (2) prove a rank lower bound via
a rigidity/incidence argument (e.g. a large full-rank submatrix from EC-addition
non-degeneracy); (3) confirm numerically at three sizes. If the bound is `<L^(1/2)`, B2 promotes.

### Cost model
n/a (barrier), but decides B2: `r≥L^(1/2+c)` ⇒ tensor-train query `≥L^(1+2c)`, no gain.

### Why existing negatives do not kill it
Strengthens NR-1477 to a new (rank) quantity.

### Likely fatal obstruction
Proving a *tight* rank bound may be as hard as the algorithm; the fallback is the numerical
measurement (which B2 already runs), so D3's marginal value is the *proof*, not the measurement.

### Minimal falsifying experiment
Numerically compute the singular-value profile / `F_p`-rank of the `S2|S3` operator at
`p≈2^20,2^24,2^28`; a proof attempt runs in parallel. Rank `≈L` ⇒ closes B2; rank `≪L^(1/2)` ⇒
opens it.

### Quantitative promotion gate
A proved `Ω(L^(1/2+c))` bound (closes B2 / part of RT-1476 backend space) **or** measured
`r=o(L^(1/2))` (opens B2). Either is a definitive result.

### Proof track
Rigidity/full-rank-submatrix argument from EC-addition genericity.

### Disproof track
A low-rank factorization of the operator (opens B2).

### Reproduction artifact
- proof note: `research/d3_separator_rank_bound_20260717.md`
- impl: `experiments/ecdlp_prime_field/d3_s3_rank_profile.sage`
- ledger id: `RANK-D3`

---

## 4. Ranking

Scores 0–5 on: **N** distance from prior ledger mechanisms; **V** plausibility of an exact
verifier; **X** chance of changing an *exponent* (not a constant); **P** complete-path coverage;
**F** falsifiability at toy scale; **L** literature-novelty confidence; **R⁻** *low* hidden
preprocessing/memory risk (5 = low risk). Reject if N<3, or no complete route to target descent,
or no quantitative rho comparison, or no precise distinction from the closest ledger entry.

| Cand | N | V | X | P | F | L | R⁻ | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A1** polyhedral/BKK | 4 | 5 | 4 | 5 | 5 | 4 | 4 | **31** | **KEEP — conservative winner** |
| A2 EDS smoothness | 4 | 4 | 3 | 4 | 4 | 3 | 3 | 25 | keep |
| A3 incidence reporting | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 25 | keep |
| B1 jet filter | 4 | 5 | 2 | 4 | 5 | 4 | 4 | 28 | keep (paired with D1) |
| **B2** tensor-train rank | 4 | 5 | 4 | 4 | 5 | 4 | 4 | **30** | **KEEP — representation winner** |
| B3 tropical/p-adic lift | 4 | 3 | 3 | 3 | 3 | 4 | 2 | 22 | keep (weak) |
| **C1** quiver composition | 4 | 4 | 4 | 3 | 4 | 3 | 3 | **25** | **KEEP — high-risk winner** |
| C2 transfer operator | 4 | 2 | 2 | 1 | 2 | 4 | 3 | 18 | **REJECT — INCOMPLETE path (no relation/descent)** |
| C3 xedni-2.0 | 3 | 4 | 2 | 4 | 3 | 2 | 2 | 20 | keep (refutation value only) |
| D1 nilpotent no-gain | 4 | 5 | — | 5 | 5 | 4 | 5 | (barrier) | KEEP |
| D2 permutation no-gain | 5 | 5 | — | 5 | 4 | 4 | 5 | (barrier) | KEEP |
| D3 separator-rank bound | 4 | 5 | — | 5 | 5 | 4 | 5 | (barrier) | KEEP |

*(D-candidates are barriers; X "exponent change" is N/A — scored on decisiveness instead.)*

**Rejected:** C2 (incomplete algorithmic path — no relation shape, rank mechanism, or descent;
retained only as a Theory-Agent formalization/negative seed).

**Winners:**
1. **Conservative — A1** (polyhedral/BKK output-sensitive decomposition).
2. **Representation — B2** (tensor-train separator-rank S3 membership backend).
3. **High-risk — C1** (noncommutative CM-correspondence composition).

All three (i) are outside the dominant ledger vocabulary, (ii) have an exact toy verifier,
(iii) come with a paired disproof/barrier track (A1↔B-Dreg refinement; B2↔D3; C1↔D2), and
(iv) target a *measured exponent that could cross 1/2* — not correctness.

---

## 5. Winner experiment contracts + first executable command

### Experiment Contract: A1 — polyhedral mixed-volume decomposition

- **Hypothesis:** the `m∈{4,5}` prime-field decomposition system at `B≈n^(1/5)` has mixed volume
  `MV(B)=O(B^(3/2−ε))`, giving output-sensitive relation-gen exponent `<1/2` in `n`.
- **Null:** `MV(B)=Θ(Bézout)` (dense polytope), no sub-birthday handle.
- **Parameters:** random ordinary prime-order `E/F_p`, `p≈2^20,2^24,2^28`; seeds
  `20260717..20260722`; `m=4,5`; `B=ceil(n^(1/5))`.
- **Metrics:** mixed volume, Bézout bound, polyhedral-homotopy path count, roots found, relations,
  sparse rank, group/field ops, wall-clock, memory.
- **Positive control:** an engineered thin-polytope toy system (`MV≪Bézout`).
- **Negative control:** a random dense system of matched degree (`MV≈Bézout`).
- **Success:** `log MV/log B < 3/2` across all three sizes **and** sparse rank `t≥B−1`.
- **Falsification:** `MV≈Bézout` at every size.
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/a1_mixed_volume_semaev.sage \
    --sizes 20,24,28 --m 4,5 --seeds 20260717-20260722 \
    --out experiments/ecdlp_prime_field/a1_mixed_volume_result.json
  ```
- **First executable command (smallest slice, do this first):**
  ```bash
  sage experiments/ecdlp_prime_field/a1_mixed_volume_semaev.sage \
    --sizes 20 --m 4 --seeds 20260717 --stage mixed_volume_only \
    --out experiments/ecdlp_prime_field/a1_smallest_probe.json
  ```

### Experiment Contract: B2 — tensor-train separator rank of S3 membership

- **Hypothesis:** the `S2|S3` pair-sum transfer operator has separator rank `r=O(L^(1−ε))`, so
  tensor-train contraction answers membership in `o(L²)` and instantiates the RT-1476 backend.
- **Null:** `r=Θ(L)` (full-rank operator), contraction `Θ(L²)`, no gain (D3).
- **Parameters:** random ordinary prime-order `E/F_p`, `p≈2^20,2^24,2^28`; `L=ceil(n^(1/5))`;
  seeds `20260717..20260722`.
- **Metrics:** `F_p`-rank and singular-value profile of the transfer matrix; truncation error at
  bond dims `L^(1/3),L^(1/2),L^(2/3)`; relations recovered; blind targets; ops; memory.
- **Positive control:** a separable toy operator (low rank).
- **Negative control:** a random full-rank operator.
- **Success:** `log r/log L < 1` at all sizes **and** an `r`-truncated contraction recovers
  `≥B−1` independent relations and blind targets.
- **Falsification:** `r=Θ(L)` at every size (→ feed D3 the numerics for the lower-bound proof).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/b2_tt_separator_rank.sage \
    --sizes 20,24,28 --seeds 20260717-20260722 \
    --out experiments/ecdlp_prime_field/b2_tt_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/b2_tt_separator_rank.sage \
    --sizes 20 --seeds 20260717 --stage rank_profile_only \
    --out experiments/ecdlp_prime_field/b2_smallest_probe.json
  ```

### Experiment Contract: C1 — CM-correspondence composition rank

- **Hypothesis:** some `poly(log q)`-depth composition of class-group correspondences on the
  factor base is **non-permutation** with incidence rank `>1`, yielding `Ω(B)` independent
  relations after full charging.
- **Null:** the `Cl(O)` action is a free-transitive torsor ⇒ every composition is a permutation
  ⇒ rank gain `=0` (D2).
- **Parameters:** toy ordinary curves with navigable `Cl(O)` (moderate discriminant, several small
  split primes), `p≈2^16,2^20,2^24`; composition depths `d=1,2,3`; seeds `20260717..`.
- **Metrics:** incidence-matrix rank vs random-permutation null and single-walk control; relations;
  isogeny-eval ops; orbit memory; descent cost.
- **Positive control:** a deliberately non-free groupoid (composite structure) — should show
  `rank>1`.
- **Negative control:** a free-transitive torsor — should show permutation.
- **Success:** composed rank exceeds the permutation null by a factor growing with `d` and size,
  giving `Ω(B)` independent relations at `poly(log q)` depth.
- **Falsification:** every composition is a permutation (matches D2) at all sizes.
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_isogeny/c1_quiver_composition.sage \
    --sizes 16,20,24 --depth 1,2,3 --seeds 20260717-20260720 \
    --out experiments/ecdlp_isogeny/c1_quiver_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_isogeny/c1_quiver_composition.sage \
    --sizes 16 --depth 1,2 --seeds 20260717 --stage rank_vs_permutation_null \
    --out experiments/ecdlp_isogeny/c1_smallest_probe.json
  ```

---

## 6. Red team — are the three winners disguised repetitions or cost-negative?

**A1 (polyhedral/BKK).**
- *Disguised repeat of MX-1478 (dense resultants)?* No: MX-1478 forms the resultant; polyhedral
  homotopy never does. But **risk:** if `MV≈Bézout` (near-certain for symmetric near-dense `S_m`),
  A1 collapses to the same dense cost — so A1 is *most likely a negative result*, valuable as a
  BKK-refinement of B-Dreg. **Cost-negative risk:** high — polyhedral homotopy has large
  path-tracking constants; even with small `MV`, `F_p` root recovery via char-0 homotopy adds
  precision cost the exponent analysis hides. **Verdict:** genuinely new *measurement*, likely
  negative; keep because the mixed volume of `S_m` is a load-bearing number nobody has computed.

**B2 (tensor-train separator rank).**
- *Disguised repeat of NR-1477 (serial-S3 dense state)?* This is the sharpest challenge. NR-1477
  found the state *polynomials* dense (`L^1.675` monomials). If "dense support" ⇒ "high rank" for
  this operator, B2 is a repeat. **The bet is precisely that support ≫ rank.** For generic EC
  addition, coordinates mix fully, which usually implies *full* rank — so **the null (D3, `r=Θ(L)`)
  is the favorite.** **Cost-negative risk:** even at `r=L^(2/3)`, contraction `L·r²=L^(7/3)>L²` —
  so B2 needs `r<L^(1/2)`, a strong requirement. **Verdict:** distinct quantity (rank vs density),
  decisive either way (opens the RT-1476 backend or, via D3, closes it), but the honest prior is
  that it closes it.

**C1 (CM-correspondence composition).**
- *Disguised repeat of ISO-AR / NR-033?* ISO-AR sought weak *destinations*; C1 seeks *rank* from
  *composition* — a different target. **But** the class-group action is a torsor, and the near-
  certain outcome (D2) is that every composition is a permutation ⇒ zero rank gain. **Cost-negative
  risk:** even if a non-permutation appeared, navigable `Cl(O)` requires moderate discriminant —
  deployed curves (P-256) are `conductor=1` flat volcanoes where the whole construction is trivial
  (the negative control), so any positive would be toy-structural and may not transfer. **Verdict:**
  honestly the weakest of the three on upside; its value is that D2 (a clean unifying no-gain
  theorem) is *worth proving regardless*, and C1 is the experiment that either proves D2 empirically
  or finds its one exception.

**Cross-cutting red-team conclusion.** All three winners are **most likely negative results**, but
each is (a) mechanism-distinct from every inventoried entry by a *named new operation*, (b)
equipped with an exact toy verifier, and (c) attached to a paired barrier theorem (A1→BKK
refinement of B-Dreg; B2→D3 rank bound; C1→D2 permutation theorem) so that a negative outcome
still *advances the barrier map* rather than merely failing. That is the correct posture: the
lab's frontier is now defined by two precise conditional theorems (RT-1472, RT-1476), and these
candidates are the sharpest available probes of whether the RT-1476 membership backend and the M4
correspondence channel can be realized or must be closed.

---

## 7. Claim discipline

- Every candidate above is `HYPOTHESIS`/`CONJECTURE` — **no** performance claim is made.
- "Relations" ≠ "ECDLP recovery": every contract requires relation-derived blind target descent
  under full charging, not relation validity alone.
- All evidence targeted is `TOY` / `MODEL-BOUND`; novelty verdicts are search-bounded
  (`POSSIBLY NOVEL` = "no equivalent found in this ledger + one literature pass," not certified).
- A failed candidate is a **scoped negative result**, not evidence that prime-field ECDLP cannot
  be improved. The correct ending remains: strongest scoped result + what it does not rule out +
  the next concrete probe.

## 8. Next three pushes (Research-Director decision)

1. **Conservative:** run A1's smallest probe (mixed volume of the `m=4` `S3` system, one 20-bit
   curve) — one cheap number that either motivates or closes the polyhedral lane.
2. **Representation:** run B2's `rank_profile_only` slice in parallel — the `S2|S3` singular-value
   profile directly decides RT-1476 backend feasibility and feeds D3.
3. **High-risk / barrier:** commission D2 (correspondence-permutation theorem) from the Theory
   Agent regardless of C1's outcome — it is the highest-leverage *barrier* and turns the entire M4
   transfer program into a checkable filter.
