# Idea Generation — ECDLP over ordinary prime fields — 2026-07-19 batch5 (report 11 / batch 11)

Research Director empirical-cryptanalysis run. Target: a non-generic single-target
algorithm whose **complete** cost beats Pollard-rho `~0.886*sqrt(n)` group ops.
Toy correctness, a new coordinate system, a relation certificate, faster
preprocessing, or a solver swap alone is **not** a breakthrough.

Authorized scope only: generated toy curves, public benchmark instances,
synthetic data. No wallets/keys/accounts.

---

## 0. Input review and machine-readable inventory

### 0.1 Files read this run

1. `/Volumes/Volume/git/autolab/research_ledger.md` (2478 lines; committed frontier ~P1486; gate rows ECFG-RT-1472, ECFG-RT-1476).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (720 lines; frontier P1509–P1513, plus NR-1500..1508).
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (with PO-transfer-001..006 closeouts).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json` (113 lines).
5. All 12 prior idea-generation reports `research/idea_generation_2026071{7,8,9}*.md` via the running anti-dup catalogue in memory `ecdlp-idea-generation-reports`.

### 0.2 Entries reviewed and ID families covered

- **Main ledger** `ECFG-*`: gate rows RT-1472, RT-1476; committed frontier through P1486; ~1470 numbered `P####` fingerprints scanned.
- **IC-state ledger** `ECFG-NR-1500..1508` + `ECFG-P1509..P1513` (+ R-suffixed refinements P1510-R1, P1511-R1, P1511-R2, P1512-R1). This is the live index-calculus frontier.
- **Report P-IDs** through **ECFG-P1597** (batch10). This report proposes **ECFG-P1598..P1609**.
- **Transfer program**: PO-transfer-001..006, NR-1500..1508 (Prym/trace-zero/cover lane, closed or cost-negative).
- Prior-report mechanism lanes: **~60 distinct lanes across 11 reports** (memory catalogue). Barrier technologies already spent: border/slice/asymptotic-spectrum rank, communication lifting + NOF, VC, approximate degree + probabilistic polynomials, Shearer/Lang-Weil/container/matroid-union entropy & supply, p-adic Adolphson-Sperber + Ax-Katz, Nullstellensatz-degree + PolyCalc/IPS + combinatorial-NSS, τ-conjecture-roots, arithmetic-circuit-complexity (shifted partials, Nisan noncommutative-ABP width, Barvinok), GCT occurrence + GKZ D-module holonomic rank, restriction/Kakeya, matching-vector codes, Elekes-Szabó, fine-grained OV/3SUM, rigidity, Delsarte-LP, sign-rank/γ2, syzygy/Betti, SOS/Lasserre, apolarity/catalecticant, Coppersmith lattice, elusive functions, depth-reduction chasm, algebraic natural proofs.

### 0.3 The only two live rho-crossing surfaces (unchanged since batch4)

Both are **conditional, unrealized** theorems in `research_ledger.md`:

- **RT-1472** (2-large-prime enrichment): exact cost exponent `max(2*ell, 1-ell, 1+1/5-2*ell)`, minimized at `ell=1/3` giving `2/3`. Crossing requires an enrichment `delta>1/4` at `L=q^{1/5}`; the honest summation graph is a.a.s. subcritical (`delta=0`). **Meter target: delta.**
- **RT-1476** (m=5 membership backend): optimum `ell=1/m`, total `(1+alpha)/m`; m=5 crosses rho iff query exponent `alpha<3/2`. **Meter target: alpha.**

### 0.4 The IC-state frontier chain, restated as one obstruction

The P1509–P1513 chain is one story:
- **P1510-R1**: an exact **per-target** truncated marked-resultant compiler exists — `O(r^2 + r*M(r)*log r)` work, `O(r^2)` state — a genuine output-sensitive summation-polynomial FFE primitive.
- **P1511-R1/R2**: every route to share/batch it across the `Theta(r)` relation rows re-materializes a **product-circuit input of degree `r^3`** (`r^3` provenance leaves); favorable degree-`r` gcd output does **not** remove the cubic input floor. Leaf-count / rho ratio is `sqrt(r)`. Batching = `Theta(r^3)=Theta(q^{3/5})` — above rho.
- **P1512-R1**: the scalar-**linear** source-labelled Chow/Tate atomizer carries the **full canonical-multiset cycle payload** `L=binom(2r+4,5)=Omega(r^5)`; standard determinant control `deg(det M) <= dim(M)` forces a degree-`r^3` batch object to cubic matrix dimension. **Closed.** The **single** surviving representational escape is a **target-specialized NONLINEAR circuit** that computes the shared object below `r^3` without materializing the `r^2` leaves per target.
- **P1513**: the shared bivariate input circuit `H(U,W)` is exactly **quadratic** (`r^2` leaves), but both explicit norms `N_T=Res_U(T,H)`, `N_F=Res_U(F,H)` remain **cubic**. Open theorem gate: an output-sensitive common-norm recurrence below `r^{5/2}`.

**Consolidated batch11 α-restatement (sharpening batch10):** *Is there a representation of the shared five-point common-norm whose complexity is governed by a functional other than the commutative determinant degree — one not capped by `deg(det)<=dim` — that evaluates `Theta(r)` rows in `o(r^3)`?* Every prior barrier metered the commutative-determinant / eliminant-degree functional. Batch11 imports functionals that are provably **decoupled** from it: **local decodability** (query lower bound), **noncommutative inner rank** (operator scaling, not degree-capped), **analytic/partition rank** (bias, not slice rank), **low-degree detectability** (RT-1472 δ), **Berezin/Pfaffian** (fermionic exact evaluation), and **information/space** cost (direct-sum, pebbling).

### 0.5 Claim discipline

Nothing below is a break. Every candidate is a scoped, falsifiable meter or barrier on RT-1472/RT-1476. Toy evidence, heuristics, and restricted models are labelled. A failed candidate is a scoped negative result, never evidence that prime-field ECDLP cannot be improved.

---

# GROUP A — Conservative extensions of known work

## Candidate: LDC-LOCAL-DECODABILITY-A1  *(conservative winner)*

### One-sentence mechanism
Exploit the fact that the m=5 membership backend is a **local source-reconstruction code** — it must recover a hidden deck/source index from few evaluations of the marked-resultant codeword — to lower-bound its query exponent `alpha` (subproblem P = RT-1476 backend) below the naive `sqrt` count only if the code evades the LDC length/query tradeoff (baseline B = rho via `alpha<3/2`).

### Status
HYPOTHESIS (as an exact α-meter). The underlying LDC lower bounds are THEOREMS.

### Novelty classification
LITERATURE-ADJACENT (coding-theory lane exists; the LDC *lower-bound* theorem is unused).

### Semantic fingerprint F(C)
- algebraic object: the P1510 marked-resultant codeword `c: [q]->F_q` indexed by evaluation point, message = the `O(r)` source keys;
- available public operations: evaluate `c` at chosen points (each = one P1510 local form), compare/decode;
- hidden structure exploited: **smoothness/locality** of the reconstruction map (few queries per recovered key);
- information discarded: global codeword; only queried positions;
- information retained: `q`-ary local views at `alpha`-many points;
- relation-generation primitive: local decoding queries;
- compression primitive: none — this is a **lower-bound** meter;
- rank mechanism: n/a (query-complexity, not matrix rank);
- descent mechanism: same local decoder reused per target;
- dominant cost exponent: `alpha` = queries per recovered source key.

### Nearest ledger entries
1. **LISTDECODE-B2 (batch7)** — used Guruswami-Sudan list decoding as a relation *generator* (upper bound via decoding radius). LDC-A1 is the **dual**: a *lower* bound on local decodability. Distinction: opposite direction of the coding theorem; batch7 asked "can I decode nearby codewords"; A1 asks "how many queries must any local decoder make".
2. **MATCHING-VECTOR-B1 (batch9)** — matching-vector *codes* as a membership object; near-certain kill because prime `n` forbids composite-modulus gain. A1 uses **general** LDC length/query bounds (Kerenidis-de Wolf 2-query exponential; Katz-Trevisan smooth-code), not MV construction. Distinction: MV was a construction; A1 is an impossibility meter.
3. **DELSARTE-LP-A2 (batch8)** — coding-LP supply ceiling on the 2-large-prime code (δ side). A1 is on the **α** side and uses locality, not distance-distribution LP. Distinction: different gate, different theorem.
4. **VCDIM-D3 (batch7)** — Sauer-Shelah relation-diversity ceiling. VC bounds *shattering*; LDC bounds *local recovery*. Distinct combinatorial quantity.
5. **P1511-R2** — product-circuit semijoin cubic input. A1 asks whether *any* backend (not just the product circuit) can be a short local code; it is the model-independent lower-bound complement to P1511-R2's representation-specific negative.

Exact distinction: no prior entry treats the backend as a locally-decodable code and imports the **length-vs-query** LDC tradeoff.

### Nearest literature
- Kerenidis & de Wolf, "Exponential lower bound for 2-query LDCs via a quantum argument" (`quant-ph/0208062`): 2 classical queries ⇒ codeword length `2^{Omega(n)}`.
- Katz & Trevisan (STOC'00): smooth codes / `q`-query decoders have `m >= n^{1+1/(q-1)}`-type length bounds; the smoothness-to-LDC reduction.
- Alrabiah-Guruswami-Kothari-Manohar (near-cubic 3-query LDC LB from CSP refutation, `2308.15403`).
- Gap: LDC bounds are stated for **worst-case all-index** recovery over small alphabets; the backend needs only the `O(r)` *actual* source keys over a `q`-ary alphabet (partial/average decoding), where the bounds weaken. Closing the gap = proving a **partial-LDC** length-query bound in the `q`-ary regime.

### Target family
Ordinary prime-field `E/F_p`, prime order `n`, `q=Theta(r^5)`, `m=5`. Excludes supersingular, anomalous, small-embedding-degree, and any curve where `E[k]` structure leaks (`gcd` conditions per NR-1501).

### Full algorithmic path
1. **factor base**: the `2r`-element signed deck (P1510 sources) as the message symbols.
2. **relation generation**: not generated — A1 is a lower-bound meter over any generator.
3. **witness extraction/verification**: each query returns a verified local P1510 leading form + factor pair (already exact in P1509).
4. **relation probability**: n/a (meter).
5. **matrix dims/density/rank**: n/a.
6. **factor-log calibration**: n/a.
7. **individual log / descent**: the same local decoder is the descent backend; the meter bounds its per-target query cost.
8. **offline/online**: codeword = offline P1510 compile (`O(r^2)` per target); online = `alpha` queries.
9. **memory/parallelism**: `O(r^2)` codeword slots; queries embarrassingly parallel.

Complete (all stages accounted; stages 2–6 are "n/a — lower-bound meter", not missing).

### Cost model
If the partial-`q`-ary LDC bound gives per-key query `alpha >= 3/2`, then `(1+alpha)/m >= (1+3/2)/5 = 1/2` — **exactly rho**, and any `alpha>=3/2` is rho-lost. Crossing requires `alpha<3/2`, i.e., a local decoder reading `<r^{3/2}` codeword positions per source key. vs rho `q^{1/2}`; vs BSGS `q^{1/2}` memory; vs nearest IC baseline P1510 per-target `q^{2/5}` build + `q^{3/5}` batch.

### Why existing negatives do not already kill it
P1511-R2/P1512-R1 close *specific representations* (product circuit, linear Chow). A1 is representation-**independent**: it asks whether the backend can be ANY short local code, catching nonlinear-circuit escapes that dodge `deg(det)<=dim`. The new operation is the **query-counting reduction** (LDC/smooth-code argument), never applied here.

### Likely fatal obstruction
LDC lower bounds are strongest for `O(1)` queries; at `alpha=Theta(sqrt(r))` queries the exponential length bound degrades to polynomial, so A1 likely yields `alpha >= const` (an obstruction below `3/2`) — **inconclusive**, not a barrier. It would still *rule in/out* the sub-`3/2` regime numerically.

### Minimal falsifying experiment
Toy sizes `r in {4,8,16}` (`q ~ r^5`, primes `~1024, 32771, 1048583`), seeds `{20260719..20260723}`. Build P1510 codewords; empirically measure the minimum #queries a best-effort local decoder needs to recover each planted source key. Positive control: a random `q`-ary code (should need `Omega(r^2)` queries). Negative control: a Reed-Solomon codeword of the same length (decodable in `deg+1` queries). Ordinary prime-order controls throughout.

### Quantitative promotion gate
Measured per-key query exponent `alpha_hat` fit across the three sizes crosses `3/2` **downward** with a certified partial-LDC theorem that forbids `alpha>=3/2`. Correctness of decoding alone is NOT the gate.

### Proof track
Theorem: any `q`-ary local decoder recovering an unknown weight-`O(r)` source vector from a length-`O(r^2)` P1510-type codeword uses `alpha=Omega(1)` queries with a constant `>=3/2` — via a smooth-code / quantum-1-query reduction adapted to partial recovery.

### Disproof track
Exhibit a P1510-derived codeword + explicit `o(r^{3/2})`-query decoder recovering all `O(r)` keys on a toy cell — that *is* the sub-rho backend (report immediately).

### Reproduction artifact
- contract `ecdlp_index_calculus_state/experiment_contract_p1598_ldc_local_decodability_alpha_meter.md`
- impl `tasks/ecdlp_index_calculus/p1598_ldc_local_decodability.py`
- result `p1598_ldc_local_decodability.json`
- audit `p1598_ldc_local_decodability_audit.py`
- ledger `ECFG-P1598`.

---

## Candidate: DIRECTSUM-INFO-A2

### One-sentence mechanism
Exploit **information-complexity direct-sum additivity** to prove that solving the `Theta(r)` membership rows of one campaign costs `Omega(r)` times the single-row information cost (subproblem P = the RT-1476 *batching* step), so batching cannot beat `r*r^2=r^3` unless single-row membership carries information `o(r^2)`.

### Status
HYPOTHESIS.

### Novelty classification
POSSIBLY NOVEL (documented search: info-complexity direct-sum unused on ECDLP; communication-lifting batch7 is a single-instance query→comm reduction, not a batching direct-sum).

### Semantic fingerprint F(C)
- algebraic object: the membership relation as a two-party (source-holder / evaluator) function;
- available public operations: exchange partial evaluations of the marked resultant;
- hidden structure exploited: **statelessness of shared sub-circuits** vs per-row novelty;
- information discarded: correlations across rows (the object of study);
- information retained: internal information cost per row;
- relation-generation primitive: none (meter on batching);
- compression primitive: the shared quadratic P1513 input (the potential savings);
- rank mechanism: n/a;
- descent mechanism: same;
- dominant cost exponent: batching exponent `beta_batch` in `q`.

### Nearest ledger entries
1. **LIFTING-D1 (batch7)** — query-to-communication lifting on a single membership instance's `alpha`. A2 is **direct-sum across instances**: a different theorem (Braverman-Rao-type internal-information additivity), targeting `beta_batch` not single-`alpha`.
2. **NOF-COMM-D2 (batch8)** — 5-party number-on-forehead cube norm on one query. A2 is 2-party internal info summed over `r` queries. Distinct axis (batching, not arity).
3. **P1511-R1 (FD-width)** — worst-case-optimal join batching; found cubic. A2 is the info-theoretic *lower* bound explaining why every join plan is cubic. Complement, not dup.
4. **P1513** — shared bivariate common-norm (the one batching hope with sublinear shared input). A2 predicts the exact info floor P1513 must beat.
5. **MATUNION-A2 (batch5)** — matroid-union independence for the δ graph; A2 is information additivity for the α batch. Different gate/tool.

Distinction: no prior entry uses **internal information cost + direct-sum** as the batching floor.

### Nearest literature
- Braverman-Rao, "Information equals amortized communication" (IEEE-IT 2014).
- Bar-Yossef-Jayram-Kumar-Sivakumar information-cost direct-sum.
- Gap: arithmetic/algebraic work is not communication; info cost lower-bounds communication, and the shared P1513 quadratic input may let the `r` rows share information (breaking naive additivity). Closing = an info-complexity model that charges shared symbolic sub-circuits honestly.

### Target family
As A1.

### Full algorithmic path
1. factor base = deck; 2. n/a (meter); 3. verified per-row; 4–6. n/a; 7. descent = one more row (same bound); 8. offline shared-circuit build vs online per-row info; 9. `O(r^2)` shared state.
Complete (meter).

### Cost model
If single-row internal info `= Omega(r^2)` and rows are info-independent, batching `= Omega(r^3)=Omega(q^{3/5})` (rho-lost). Crossing needs single-row info `o(r^2)` OR super-additive sharing driving `beta_batch<5/2`. vs rho `q^{1/2}`.

### Why existing negatives do not already kill it
P1511 closes *algorithmic* batching; A2 asks the *information-theoretic* question — whether ANY batching (including an unknown nonlinear circuit) can share information across rows. New operation: direct-sum decomposition of the campaign.

### Likely fatal obstruction
Info cost is a communication bound; the compiler is not communication-bounded, and the shared quadratic input (P1513) may allow super-additive sharing the model cannot see — giving a vacuous `Omega(r)` (not `Omega(r^2)`) floor.

### Minimal falsifying experiment
`r in {4,8,16}`; empirically estimate internal info of single-row membership under a product source distribution; test additivity vs an `r`-fold batch with the shared P1513 input present/absent. Positive control: `r` truly independent DLPs (must be additive). Negative control: `r` identical rows (info collapses). Seeds `{20260719..}`.

### Quantitative promotion gate
Estimated `beta_batch` fit crosses `5/2` downward, i.e., measured batch info scales `< r^{2.5}` with a certified super-additivity mechanism. Additivity alone (`r^3`) is a barrier, not a crossing.

### Proof track
Theorem: internal information of one m=5 membership solve is `Omega(r^2 log q)`, and the `Theta(r)`-row campaign direct-sums to `Omega(r^3 log q)` even with the shared quadratic input.

### Disproof track
Measured strong sub-additivity from shared-circuit reuse driving batch info `o(r^3)` — promotes to a batching-savings lead.

### Reproduction artifact
contract `..._p1599_directsum_info_batching_floor.md`; impl `p1599_directsum_info_batching.py`; result/audit JSON; ledger `ECFG-P1599`.

---

## Candidate: LDLR-DELTA-METER-A3

### One-sentence mechanism
Exploit the **low-degree likelihood ratio** as the exact predictor of whether any cheap (degree-`D`, cost `q^{O(D)}`) statistic can *detect* the 2-large-prime enrichment versus the honest random summation graph (subproblem P = RT-1472 δ), so `delta>1/4` is achievable only if the enrichment is low-degree-detectable below degree `q^{1/4}`.

### Status
HYPOTHESIS (meter); LDLR predictions are conjecturally tight, proven in many planted models.

### Novelty classification
POSSIBLY NOVEL (LDLR unused on ECDLP; distinct from all supply meters).

### Semantic fingerprint F(C)
- algebraic object: distribution pair (enriched vs honest 2-LP graph);
- available public operations: evaluate degree-`D` polynomial statistics of the graph/pair data;
- hidden structure exploited: planted 2-large-prime correlation;
- information discarded: high-degree correlations;
- information retained: degree-`<=D` moments;
- relation-generation primitive: none (detection meter);
- compression primitive: none;
- rank mechanism: `||L^{<=D}||_2` (LDLR norm), not matrix rank;
- descent mechanism: n/a;
- dominant cost exponent: `delta` via the detectability degree threshold.

### Nearest ledger entries
1. **DELSARTE-LP-A2 (batch8)** — coding-LP *supply* ceiling on the 2-LP code. A3 meters *detectability*, not supply. Distinct: LP-distance vs likelihood-ratio norm.
2. **SHEARER-D3 (batch8)** / **container/matroid** — entropy/supply ceilings. A3 is a distinguishing threshold, not a counting bound.
3. **RT-1472-CYCLEMAT-A2** — graphic-matroid cycle-basis enrichment. A3 predicts whether the enrichment is even *detectable* by cheap statistics (necessary for δ>1/4).
4. **ENERGY-D1 (batch3)** — additive-energy relation-supply ceiling. A3 is detection, not energy.
5. **SOS-LB-D1 (batch4)** — SOS pseudo-calibration. LDLR is the low-degree shadow of SOS; A3 is the cheaper, sharper prediction on the *specific* enrichment.

Distinction: no prior entry uses **detection/distinguishing complexity** as the δ meter.

### Nearest literature
- Kunisky-Wein-Bandeira, "Notes on computational hardness of hypothesis testing: predictions using the low-degree likelihood ratio."
- Hopkins-Steurer (FOCS'17), sharp low-degree detection at the KS threshold.
- Gap: LDLR predicts detection, not the *rank/exploitability* of the detected structure; δ>1/4 needs relations (rank), not just detection.

### Target family
Ordinary prime-field, `L=q^{1/5}`, honest vs 2-LP-enriched summation graph.

### Full algorithmic path
1. factor base = `L`-smooth relation edges; 2. n/a (meter); 3. n/a; 4. detection advantage = LDLR norm; 5. n/a; 6. n/a; 7. n/a; 8. offline moment computation; 9. `q^{O(D)}` statistic memory.
Complete (meter).

### Cost model
`delta>1/4` at `ell=1/3` requires detectability at degree `D=o(q^{1/4})` with LDLR norm diverging. If `||L^{<=D}||_2=O(1)` for `D` up to `q^{1/4}`, no cheap statistic detects enrichment ⇒ δ≤1/4. vs rho exponent `2/3`.

### Why existing negatives do not already kill it
Supply meters (Shearer/Delsarte/energy) bound how *many* relations exist; A3 bounds whether the *enriching structure* is cheaply *findable* — an orthogonal necessary condition never metered.

### Likely fatal obstruction
Enrichment may be low-degree-detectable (LDLR diverges) yet still not convertible into `delta>1/4` rank — a positive-but-cost-negative signal (detection ≠ exploitation).

### Minimal falsifying experiment
`r in {4,8,16}`; compute the empirical degree-`{1,2,3}` LDLR norm for enriched vs honest 2-LP graphs. Positive control: a strongly planted dense-subgraph (LDLR must diverge). Negative control: honest random graph (LDLR ≈ 1). Seeds `{20260719..}`.

### Quantitative promotion gate
LDLR norm grows with `q` at the degree needed for `delta>1/4` **and** a paired rank-realization test converts detection to `delta>1/4` relations. Detection alone is not the gate.

### Proof track
Compute the degree-`D` LDLR for the enriched-vs-honest model; show divergence below `D=q^{1/4}` ⟺ enrichment δ.

### Disproof track (this doubles as barrier D2 below)
Bounded LDLR up to `q^{1/4}` ⇒ δ≤1/4 in the low-degree model — closes RT-1472 for all cheap detectors.

### Reproduction artifact
contract `..._p1600_ldlr_delta_detectability_meter.md`; impl `p1600_ldlr_delta_meter.py`; result/audit; ledger `ECFG-P1600`.

---

# GROUP B — Genuine representation changes

## Candidate: ANALYTIC-RANK-BIAS-B1

### One-sentence mechanism
Represent m=5 membership by the **analytic rank** (`-log_q` of the bias / Gowers-`U`) of the symmetrized Semaev summation tensor instead of its border/slice rank, so that a low-analytic-rank tensor admits a **biased** membership sampler that beats the `r^{3/2}` query floor (subproblem P = RT-1476 α; baseline B = rho).

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW (slice rank was batch4 SLICE-RANK-1, rank-1 vacuous; analytic/partition rank distinct and unused).

### Semantic fingerprint F(C)
- algebraic object: the 5-tensor `T` of the symmetrized Semaev relation over `F_p`;
- available public operations: evaluate additive characters `psi(T(x))`;
- hidden structure exploited: **bias** `E_x psi(T(x))` (nontrivial ⇒ low analytic rank);
- information discarded: exact membership; kept: biased/character-weighted membership;
- information retained: Fourier-analytic mass;
- relation-generation primitive: importance-sampling toward the biased support;
- compression primitive: partition-rank decomposition (Lovett: partition ≈ analytic rank);
- rank mechanism: **analytic rank** `a(T)`;
- descent mechanism: same biased sampler per target;
- dominant cost exponent: `alpha` via `a(T)`.

### Nearest ledger entries
1. **SLICE-RANK-1-D2 (batch4)** — Croot-Lev-Pach slice rank; vacuous at rank 1 in cyclic `E(F_p)`. Analytic rank is a *different* functional (bias-based), not slice rank. Distinction: bias vs slice decomposition; the equivalence is only up to constants over large fields (2102.10509), and the *value* here is the open question.
2. **BORDER-B4 / ASYMPSPEC-D1 (batch3/5)** — border rank / asymptotic spectrum. Analytic rank is not multiplicative-spectrum; distinct meter.
3. **GKZ-DMODULE-B2 (batch8)** — holonomic rank = normalized volume (branch count). Analytic rank measures bias, not volume. Distinct.
4. **PROBABILISTIC-POLY-C3 (batch8)** — probabilistic degree. Analytic rank is deterministic bias, not randomized degree. Distinct.
5. **P1508 (quadratic phase)** — Walsh/phase rank 29 toy identity, scalar-label. B1 measures the full quintic tensor's analytic rank over real curve coordinates, not the manufactured scalar predicate.

Distinction: no prior entry uses **bias/analytic rank** of the summation tensor.

### Nearest literature
- Gowers-Wolf; Lovett "The analytic rank of tensors and its applications" (`1806.09179`); Bhowmick-Lovett; Cohen-Moshkovitz partition≈analytic (`2102.10509`); "Bias implies low rank for quartic polynomials" (`1902.10632`).
- Gap: these bound partition-vs-analytic rank *of a given tensor*; they do not compute the analytic rank of the Semaev tensor, which is the crux.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`; exclude tensors with imposed CM/character symmetry that inflate bias artificially.

### Full algorithmic path
1. factor base = deck; 2. biased sampler draws `x` with `psi(T(x))`-weight, retains membership hits; 3. verify each hit exactly; 4. relation prob ≈ `q^{-a(T)/...}`; 5. `Theta(r)` rows, sparse; 6. standard; 7. same sampler for descent; 8. offline character tables, online sampling; 9. `O(r^2)`.
Complete.

### Cost model
If `a(T)=o(r)` (biased), the sampler finds a relation in `q^{a(T)/5}`-ish cost, potentially `alpha<3/2`. If `a(T)=Theta(r)` (max bias-free), sampler cost `= q^{Theta(1)}` per row, rho-lost. vs rho `q^{1/2}`.

### Why existing negatives do not already kill it
Slice-rank vacuity (P1512/batch4) is about the *linear* Chow atomizer; analytic rank is a nonlinear bias functional and is exactly the kind of **nonlinear-circuit exception** P1512-R1 left open (a biased evaluator is not a determinant).

### Likely fatal obstruction
P1512 engineered the incidence to carry a **rank-`Theta(r)` cycle payload** ⇒ the tensor is bias-free ⇒ `a(T)=Theta(r)` ⇒ maximal, no cheap sampler. Near-certain kill; but *measuring* `a(T)` on toy cells is itself a first-time datum.

### Minimal falsifying experiment
`r in {4,8,16}`; compute empirical bias `E psi(T(x))` and estimate `a(T)` via partition-rank search. Positive control: a planted low-partition-rank tensor (biased). Negative control: a random 5-tensor (bias `~q^{-r}`). Ordinary prime-order curves; seeds `{20260719..}`.

### Quantitative promotion gate
Fitted `a(T)/r` trends **below** a constant that yields `alpha<3/2` across the three sizes. Any `a(T)=Theta(r)` is a barrier datum.

### Proof track
Theorem: the symmetrized Semaev 5-tensor has analytic rank `Theta(r)` (bias `q^{-Theta(r)}`) ⇒ no low-degree biased sampler ⇒ `alpha>=3/2`.

### Disproof track
A toy family with measured `a(T)=o(r)` and a working biased sampler beating `r^{3/2}` queries.

### Reproduction artifact
contract `..._p1601_analytic_rank_bias_membership.md`; impl `p1601_analytic_rank_bias.py`; result/audit; ledger `ECFG-P1601`.

---

## Candidate: NONCOMMUTATIVE-RANK-OPSCALING-B2  *(representation winner)*

### One-sentence mechanism
Represent the batched five-point incidence as a **linear matrix over the free skew field** and compute its **noncommutative (inner) rank via operator scaling** — a functional NOT capped by `deg(det)<=dim` — so that if `nc-rank = o(r^{5/2})` while commutative rank is `Omega(r^5)`, operator scaling recovers source atoms in `poly(nc-dim)` time (subproblem P = the RT-1476 backend; baseline B = rho).

### Status
HYPOTHESIS.

### Novelty classification
POSSIBLY NOVEL (documented search: operator scaling / nc-rank unused on ECDLP; distinct from Nisan noncommutative-ABP *width lower bound* batch10, which was a barrier, not this constructive rank algorithm).

### Semantic fingerprint F(C)
- algebraic object: a linear matrix `M = sum_k A_k x_k` with source markers `x_k` treated as **noncommuting**;
- available public operations: operator scaling / Gurvits' algorithm (Sinkhorn-type completely-positive scaling);
- hidden structure exploited: **inner rank over the free skew field** ≠ commutative rank;
- information discarded: commutative specializations;
- information retained: the noncommutative rank shrinkage of the incidence pencil;
- relation-generation primitive: null-space / shrunk-subspace certificate from the scaling limit;
- compression primitive: nc-rank deficiency (Cohn-Reutenauer inner rank);
- rank mechanism: **noncommutative rank** (operator scaling, deterministic poly-time; works in positive characteristic per Ivanyos-Qiao-Subrahmanyam);
- descent mechanism: same nc-rank certificate per target;
- dominant cost exponent: `beta_nc` in `r`.

### Nearest ledger entries
1. **P1512-R1** — scalar-**linear** Chow atomizer, closed at `Omega(r^5)` via `deg(det M)<=dim(M)` on the **commutative** determinant. B2 replaces the commutative determinant with the **noncommutative** inner rank, for which `deg(det)<=dim` does NOT hold — this is the precise **target-specialized nonlinear-circuit exception** P1512-R1 preserved, instantiated by operator scaling (a non-Gröbner, non-determinant iterative process).
2. **NISAN-NC-RANK-A2 (batch10)** — noncommutative-ABP *width* = Nisan-Hankel rank, a **lower bound** on a fixed ordering. B2 is a **constructive rank-computation algorithm** over the free skew field, not an ordered-ABP width bound. Distinct object (inner rank vs Hankel rank) and distinct direction (algorithm vs LB).
3. **DEQUANTIZED-SAMPLING-C1 (batch10)** — stable-rank sampler. nc-rank is an exact algebraic rank, not a spectral sample. Distinct.
4. **RIGIDITY-A1 (batch8)** — Valiant rigidity of the eval matrix (commutative). B2 is noncommutative. Distinct functional.
5. **P1511-R2 (product circuit)** — commutative product-circuit input cubic. nc-rank may collapse the pencil the commutative product cannot.

Exact distinction: B2 is the only candidate that computes a rank functional **provably decoupled** from the determinant degree that gated P1512.

### Nearest literature
- Garg-Gurvits-Oliveira-Wigderson, "Operator scaling: theory and applications" (`1511.03730`, FOCM).
- Ivanyos-Qiao-Subrahmanyam, "Non-commutative Edmonds' problem and matrix semi-invariants" (deterministic poly-time nc-rank, **positive characteristic**).
- Hamada-Hirai (nc-rank via CAT(0) convex optimization); Cohn-Reutenauer inner rank.
- Gap: these solve nc-rank *of a given linear matrix*; whether the Semaev incidence pencil, presented noncommutatively, has nc-rank `o(r^{5/2})` is open. For **shift/cyclic** pencils commutative rank = nc-rank (Edmonds is easy), which is the risk.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`. Excludes any pencil that is provably commutative (single-variable or diagonalizable), where nc = commutative.

### Full algorithmic path
1. factor base = deck ⇒ marker variables `x_k`; 2. build linear pencil `M(x)` of the signed five-source incidence; 3. run operator scaling to get nc-rank + shrunk subspace = source certificate, verify exactly; 4. relation prob = nc-rank deficiency probability; 5. pencil dim `= nc-dim`, sparse; 6. standard; 7. same scaling per target; 8. offline pencil build, online scaling; 9. `poly(nc-dim)` memory.
Complete.

### Cost model
If `nc-rank = Theta(r^5)` (= commutative), B2 = P1512 (rho-lost, `Omega(r^5)`). If the noncommutative presentation shrinks the payload to `nc-dim=o(r^{5/2})`, operator scaling runs in `poly(r^{5/2})` and per-target atomization is sub-rho. vs rho `q^{1/2}=r^{5/2}`; vs P1510 batch `r^3`.

### Why existing negatives do not already kill it
P1512-R1's proof is `deg(det M)<=dim(M)` for the **commutative** determinant. Amitsur's theory shows the noncommutative determinant obeys **different** degree bounds; the `Omega(r^5)` cycle-payload argument uses commutative multiplicativity that fails over the free skew field. New operation: operator scaling / nc-rank, which no prior entry used.

### Likely fatal obstruction
The P1512 cycle payload is a **cyclic/shift-structured** pencil, and for such pencils the Edmonds problem is easy with nc-rank = commutative rank ⇒ same `Omega(r^5)`. The nc gain requires genuine noncommutativity in the marker algebra, which the abelian curve group may forbid (same collapse family as MAHLER/ACFA).

### Minimal falsifying experiment
`r in {4,8,16}`; build the incidence pencil; compute nc-rank via operator scaling (Gurvits) AND commutative rank; compare. Positive control: a Fullness/Edmonds pencil with known nc-rank < commutative rank (e.g., a `2x2` skew example blown up). Negative control: a diagonal pencil (nc = commutative). Ordinary prime-order; seeds `{20260719..}`.

### Quantitative promotion gate
Measured `nc-rank / commutative-rank` trends **below 1** with a fitted `beta_nc<5/2` across the three sizes. nc = commutative on all cells is a scoped barrier datum (closes the nonlinear-rank exception).

### Proof track
Theorem: the noncommutatively-presented Semaev incidence pencil has `nc-rank = o(r^{5/2})` ⇒ operator scaling atomizes below rho. (Or its negation as a barrier.)

### Disproof track
Prove the pencil is FL-decomposable/shift-structured ⇒ nc-rank = commutative rank = `Omega(r^5)` on all cells.

### Reproduction artifact
contract `..._p1602_noncommutative_rank_opscaling_atomizer.md`; impl `p1602_nc_rank_opscaling.py`; result/audit; ledger `ECFG-P1602`.

---

## Candidate: SCHUBERT-STRUCTURE-CONSTANT-B3

### One-sentence mechanism
Represent the five-point membership count as a **Schubert intersection number** (Littlewood-Richardson structure constant) in a Grassmannian of the point-spans, so an output-sensitive geometric-LR / puzzle rule counts complete incidences without materializing the `r^2` pair-resultant leaves (subproblem P = P1513 shared common-norm).

### Status
HEURISTIC.

### Novelty classification
NOVELTY-UNVERIFIED (Schubert calculus unused; adjacency to GKZ toric/syzygy needs closer literature coverage).

### Semantic fingerprint F(C)
- algebraic object: Schubert classes of the linear spans of the five deck points in a Grassmannian `Gr(k,V)`;
- available public operations: LR / puzzle intersection counts;
- hidden structure exploited: **cohomology-ring sparsity** of the intersection;
- information discarded: explicit resultant leaves;
- information retained: intersection multiplicities;
- relation-generation primitive: nonzero structure constants = incidences;
- compression primitive: puzzle/honeycomb rule (output-sensitive LR);
- rank mechanism: n/a (enumerative);
- descent mechanism: same per target;
- dominant cost exponent: incidence-count exponent.

### Nearest ledger entries
1. **GKZ-DMODULE-B2 (batch8)** — holonomic rank = normalized volume = branch count (toric). Schubert is Grassmannian cohomology, not toric volume. Distinction: LR structure constants vs BKK mixed volume.
2. **SYZYGY-REGULARITY-B2 (batch4)** — Betti table of the factor-base ideal. Schubert is intersection theory on a homogeneous space, not free-resolution ranks. Distinct.
3. **APOLARITY-ATOMIZER-A2 (batch4)** — Waring/catalecticant. Distinct (apolarity vs Schubert).
4. **P1513** — shared bivariate common-norm; B3 is a candidate *representation* of exactly that count.
5. **NEWTON-OKOUNKOV-B3 (batch9)** — graded descent filtration (Okounkov body). Related to Schubert via flag degenerations but distinct enumerative object; flagged for overlap.

Distinction: no prior entry uses Grassmannian **structure constants**; risk of adjacency with Newton-Okounkov must be closed in Phase 0.

### Nearest literature
- Vakil's geometric Littlewood-Richardson rule; Knutson-Tao puzzles; positivity/effective LR computation.
- Gap: whether the five-point elliptic incidence is a genuine Schubert problem (linear-span condition) or a nonlinear condition that only *looks* like one — likely the latter, which would collapse B3 to a resultant.

### Target family
Ordinary prime-field, `m=5`. Excludes degenerate collinear decks.

### Full algorithmic path
1. factor base = deck spans; 2. LR count of complete incidences; 3. verify each realized incidence exactly; 4. incidence prob = nonzero-structure-constant density; 5. `Theta(r)` rows sparse; 6. standard; 7. same; 8. offline cohomology setup; 9. output-sensitive memory.
Status: **INCOMPLETE-risk** — stage 2 relies on the elliptic condition being a linear-span/Schubert condition, unproven. Label INCOMPLETE until Phase 0 lemma.

### Cost model
If the count is a sparse LR problem, output-sensitive count `~ #incidences * polylog`, potentially `o(r^3)`. If the elliptic condition is nonlinear (generic), it is not Schubert and reduces to a resultant `r^3`. vs rho `r^{5/2}`.

### Why existing negatives do not already kill it
GKZ (toric) and syzygy (free-resolution) meter *different* invariants; the enumerative Schubert count is a nonlinear-circuit-style object not covered by `deg(det)<=dim`.

### Likely fatal obstruction
The elliptic five-point sum condition is genuinely nonlinear (cubic curve, not a linear subspace incidence), so it is **not** a Schubert problem and the LR representation does not apply — collapsing to the standard resultant.

### Minimal falsifying experiment
`r in {4,8}`; test whether the incidence count equals an LR structure constant on toy decks. Positive control: a genuine linear-span incidence (must match LR). Negative control: the elliptic condition (expected mismatch = kill). Seeds `{20260719..}`.

### Quantitative promotion gate
A proven Schubert reformulation **and** an output-sensitive count trending `o(r^3)`. Mismatch on the elliptic control is a clean scoped negative.

### Proof track
Lemma: the five-point elliptic sum-to-`O` condition is (or is not) equivalent to a linear Schubert incidence in some `Gr(k,V)`.

### Disproof track
Show the condition is irreducibly cubic ⇒ no Schubert lift (the expected outcome).

### Reproduction artifact
contract `..._p1603_schubert_structure_constant_incidence.md`; impl `p1603_schubert_structure_constant.py`; result/audit; ledger `ECFG-P1603`.

---

# GROUP C — High-risk speculative mechanisms

## Candidate: BEREZIN-PFAFFIAN-COMMONNORM-C1  *(high-risk winner)*

### One-sentence mechanism
Represent the shared five-point common-norm (P1513) as a **fermionic Berezin integral** over anticommuting (Grassmann) variables, so the `r`-fold pair-coupling collapses to a **Pfaffian** of an `r x r` skew matrix computable in `O(r^2 M(r))` rather than the `r^3` product-circuit (subproblem P = P1513 open common-norm; baseline B = rho `r^{5/2}`).

### Status
HEURISTIC / high-risk.

### Novelty classification
NOVELTY-UNVERIFIED (Berezin/Grassmann integration unused; matchgate P1504 is the Boolean *signature* shadow, not the integral over the actual marked-resultant).

### Semantic fingerprint F(C)
- algebraic object: Grassmann-algebra generating integral of the `r^2`-leaf coupling;
- available public operations: Berezin integration = Pfaffian evaluation;
- hidden structure exploited: **antisymmetry** of the pair-coupling ⇒ Pfaffian shortcut;
- information discarded: full product expansion (`r^3` monomials);
- information retained: the Pfaffian of the coupling matrix;
- relation-generation primitive: Pfaffian roots = common-norm roots;
- compression primitive: Gaussian fermionic integral (quadratic-form ⇒ Pfaffian);
- rank mechanism: Pfaffian (`sqrt(det)` of skew part);
- descent mechanism: same per target;
- dominant cost exponent: Pfaffian cost `~2` in `r`.

### Nearest ledger entries
1. **P1504 (matchgate obstruction)** — arity-8 Boolean tensor has **zero** matchgate bases over shared GL2. C1 does NOT booleanize; it integrates the actual `F_p`-valued marked resultant fermionically, whose coupling is a **continuous** skew matrix, not a Boolean signature. Distinction: Berezin integral of the real object vs matchgate Boolean signature; P1504 closed the latter only.
2. **P1513** — shared bivariate common-norm, open; C1 is a candidate exact evaluator for it.
3. **HOLANT-C1 (batch3)** — holographic/matchgate counting + Cai-Lu dichotomy. Same Boolean-signature caveat; C1 is the integral, not the Holant reduction.
4. **P1512-R1** — commutative determinant capped; a Pfaffian is `sqrt(det)` of a *skew* matrix, a nonlinear-circuit object not `deg(det)<=dim`-capped.
5. **CLUSTER-MUTATION-B3 (batch8)** — Somos/EDS recurrence; distinct (no fermionic integral).

Distinction: no prior entry evaluates the common-norm via a **Berezin/Pfaffian** representation of the actual resultant.

### Nearest literature
- Berezin, "The Method of Second Quantization"; Valiant matchgates/Pfaffian circuits; Cai-Choudhary Pfaffian circuits.
- Gap: Pfaffian evaluation is fast only if the coupling matrix is genuinely **skew and the integrand is Gaussian (quadratic in Grassmann variables)**; the marked resultant is higher-degree, so the reduction is not automatic.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`; exclude char 2 (Pfaffian sign issues).

### Full algorithmic path
1. factor base = deck; 2. assemble the `r x r` Grassmann coupling from P1513 pair leaves; 3. Pfaffian = common-norm; verify roots exactly; 4. relation prob = root density; 5. `Theta(r)` rows sparse; 6. standard; 7. same; 8. offline coupling build, online Pfaffian; 9. `O(r^2)`.
Complete (modulo the Gaussian-reduction lemma; flagged).

### Cost model
If the coupling is skew + Gaussian, Pfaffian `= O(r^2 M(r))` per target, batch `= O(r^3 ... )` — need the Pfaffian to also **share** across targets (P1513 shared input) for `o(r^{5/2})`. Best case matches the P1513 target: sub-`r^{5/2}` common-norm. vs rho `r^{5/2}`.

### Why existing negatives do not already kill it
P1504 closed matchgate *bases* for a Boolean tensor; C1 uses the fermionic integral of the real resultant, a distinct object. P1512's `deg(det)<=dim` does not bound a Pfaffian (`sqrt(det)` of skew).

### Likely fatal obstruction
The marked resultant is **not quadratic** in the Grassmann variables ⇒ the Berezin integral is not a plain Pfaffian but a higher fermionic moment (= permanent-like / still `r^3`). Near-certain: fermionic Gaussianity fails, reproducing the cubic floor.

### Minimal falsifying experiment
`r in {4,8,16}`; attempt to write the P1513 common-norm as a Pfaffian of an explicit skew coupling; measure evaluation cost vs the `r^3` product. Positive control: a genuine matchgate-realizable count (Pfaffian exact). Negative control: a permanent (no Pfaffian shortcut). Seeds `{20260719..}`.

### Quantitative promotion gate
Pfaffian evaluation of the true common-norm trends `o(r^{5/2})` across sizes **with** shared-input reuse. Any higher-moment blowup to `r^3` is a scoped negative.

### Proof track
Lemma: the P1513 pair-coupling is skew and the integrand is fermionic-Gaussian ⇒ common-norm = Pfaffian.

### Disproof track
Show the integrand has fermionic degree > 2 ⇒ no Pfaffian collapse (expected).

### Reproduction artifact
contract `..._p1604_berezin_pfaffian_common_norm.md`; impl `p1604_berezin_pfaffian.py`; result/audit; ledger `ECFG-P1604`.

---

## Candidate: LORENTZIAN-LOGCONCAVE-C2

### One-sentence mechanism
Represent the relation-supply generating polynomial of the 2-large-prime graph as a **Lorentzian / completely-log-concave polynomial**, so if it is Lorentzian its supports obey Mason-type log-concavity and an Anari-Oveis-Gharan-style sampler produces enriched relations in poly time, certifying `delta>1/4` (subproblem P = RT-1472 δ).

### Status
HEURISTIC / high-risk.

### Novelty classification
POSSIBLY NOVEL (Lorentzian polynomials / log-concavity unused on ECDLP).

### Semantic fingerprint F(C)
- algebraic object: the multivariate generating polynomial `g_G(x)` of the enriched relation set;
- available public operations: evaluate `g_G` and its Hessian signature;
- hidden structure exploited: **log-concavity / M-convexity** of the relation support;
- information discarded: non-log-concave correlations;
- information retained: the Lorentzian cone membership;
- relation-generation primitive: log-concave sampling (down-up walk);
- compression primitive: the M-convex support;
- rank mechanism: Hessian signature (one positive eigenvalue);
- descent mechanism: n/a;
- dominant cost exponent: `delta` via mixing time.

### Nearest ledger entries
1. **MATUNION-A2 (batch5)** — matroid union for the δ graph. Lorentzian polynomials generalize matroid basis-generating polynomials (log-concavity), but C2 asks whether the *enriched* support is M-convex, a stronger structural claim. Distinction: matroid-union independence vs Lorentzian cone membership + sampling.
2. **CORRELATED-PEEL-A3 (batch4)** — Wormald 2-core threshold of the dependent sum-graph. C2 is log-concavity of the generating polynomial, not a differential-equation core threshold. Distinct.
3. **GRAPHON-CUTNORM-B3 (batch6)** — cut-norm δ-threshold. Distinct (analytic vs log-concave).
4. **SHEARER-D3 / container** — entropy ceilings. Log-concavity is a positive sampling tool, opposite direction.
5. **RT-1472-CYCLEMAT-A2** — cycle-basis enrichment; C2 tests whether that enrichment's polynomial is samplable.

Distinction: no prior entry uses **Lorentzian/log-concave** structure.

### Nearest literature
- Brändén-Huh, "Lorentzian polynomials" (Annals 2020); Anari-Liu-Oveis Gharan-Vinzant log-concave sampling; Adiprasito-Huh-Katz Hodge theory for matroids.
- Gap: elliptic incidence supports are not matroids in general; whether `g_G` is Lorentzian is the open crux.

### Target family
Ordinary prime-field, `L=q^{1/5}`, enriched 2-LP graph.

### Full algorithmic path
1. factor base = `L`-smooth edges; 2. sample relations via down-up walk if Lorentzian; verify; 3. exact; 4. relation prob = stationary mass; 5. `Theta(L+B)` edges; 6. standard; 7. n/a; 8. offline polynomial assembly; 9. walk memory.
Complete (modulo Lorentzian lemma).

### Cost model
If `g_G` Lorentzian, sampling mixes in poly time and enrichment `delta>1/4` is realizable at `ell=1/3`; else no gain. vs rho `2/3`.

### Why existing negatives do not already kill it
Supply/entropy meters bound counts; C2 asks whether the enriched support is *efficiently samplable* — a constructive property none tested.

### Likely fatal obstruction
The honest 2-LP relation support is **not** M-convex (elliptic incidences violate exchange), so `g_G` is not Lorentzian and log-concave sampling does not apply — the Sidon-like maximal-doubling kill (cf. PFR-DICHOTOMY-C2, batch9).

### Minimal falsifying experiment
`r in {4,8,16}`; test Lorentzian-ness (Hessian one-positive-eigenvalue on the support) of `g_G`. Positive control: a matroid basis polynomial (Lorentzian). Negative control: a non-M-convex support. Seeds `{20260719..}`.

### Quantitative promotion gate
`g_G` certified Lorentzian **and** the sampler yields `delta>1/4` across sizes. Non-Lorentzian is a scoped negative.

### Proof track
Lemma: `g_G` is (not) Lorentzian for the enriched 2-LP support.

### Disproof track
Exhibit an exchange-property violation ⇒ not Lorentzian (expected).

### Reproduction artifact
contract `..._p1605_lorentzian_logconcave_enrichment.md`; impl `p1605_lorentzian_logconcave.py`; result/audit; ledger `ECFG-P1605`.

---

## Candidate: ORE-SKEW-RESULTANT-C3

### One-sentence mechanism
Represent five-point membership in the **Ore skew-polynomial ring** `F_p{F}` of linearized (additive) polynomials, where the skew-Euclidean algorithm computes a **skew resultant** in quasi-linear degree cost, potentially replacing the `r^3` commutative resultant (subproblem P = RT-1476 backend).

### Status
HEURISTIC / high-risk (near-certain collapse kill).

### Novelty classification
LEDGER-NEW (Ore/skew-polynomial resultant unused; distinct from Nisan noncommutative *width* batch10 and formal-group Coleman batch8).

### Semantic fingerprint F(C)
- algebraic object: linearized polynomials as elements of `F_p{F}`, `F=`Frobenius;
- available public operations: skew addition, skew multiplication, skew (left/right) Euclid;
- hidden structure exploited: **skew-Euclidean quasi-linear GCD** in degree;
- information discarded: commutative monomial structure;
- information retained: skew degree;
- relation-generation primitive: skew resultant = common skew factor;
- compression primitive: skew Euclid (degree, not `r^3` leaves);
- rank mechanism: n/a;
- descent mechanism: same;
- dominant cost exponent: skew-GCD cost.

### Nearest ledger entries
1. **NISAN-NC-RANK-A2 (batch10)** — noncommutative-ABP width LB (Hankel rank). C3 is a *constructive skew-Euclid algorithm* in `F_p{F}`, not a width bound. Distinct.
2. **FORMALGROUP-B1 (batch8)** — Honda formal-group/Coleman log; killed by `gcd(p,n)=1`. C3 is skew-polynomial (Frobenius) arithmetic, a different linearization; but it shares the collapse-risk family.
3. **MAHLER-B1 (batch5)** — automatic-sequence/Mahler rep; killed by `F_p` periodicity. C3 has the same Frobenius-triviality risk.
4. **B2 (nc-rank)** — also noncommutative but B2 uses free-skew-field rank (marker variables); C3 uses the Frobenius Ore ring (field automorphism). Different noncommutativity source.
5. **P1511-R2** — commutative product cubic; C3 asks if a skew resultant avoids it.

Distinction: no prior entry uses the **Ore/skew-polynomial (linearized-polynomial) resultant**.

### Nearest literature
- Ore, "Theory of non-commutative polynomials" (1933); skew-Euclid / resultants over `F_q{F}`; Wu-Feng linearized-polynomial factorization.
- Gap: over `F_p`, Frobenius `F=` identity on scalars, so `F_p{F}` largely commutes with constants and the skew ring degenerates.

### Target family
Ordinary prime-field, `m=5`; excludes extension-field presentations where Frobenius acts nontrivially (those change the object, cf. transfer program).

### Full algorithmic path
1. factor base = deck as linearized-polynomial roots; 2. skew resultant = common factor; verify; 3. exact; 4. root density; 5. `Theta(r)` rows; 6. standard; 7. same; 8. offline skew setup; 9. degree-bounded memory.
Complete.

### Cost model
If a genuine skew resultant applies, GCD cost `~ M(degree) log` = quasi-linear in `r`, far below `r^3`. But over `F_p` the skew ring collapses ⇒ commutative resultant ⇒ `r^3`. vs rho `r^{5/2}`.

### Why existing negatives do not already kill it
It is the untried Ore linearization; distinct from Coleman/Mahler/Honda even though it shares their collapse-risk.

### Likely fatal obstruction
Frobenius `= id` on `F_p` ⇒ `F_p{F}` is not genuinely skew over the constant field ⇒ the skew resultant reduces to the ordinary resultant. Near-certain kill (same as MAHLER/ACFA/FORMALGROUP collapses).

### Minimal falsifying experiment
`r in {4,8}`; attempt a skew-resultant membership on `F_p` and on `F_{p^e}` (control where `F` is nontrivial). Positive control: `F_{p^e}` skew ring (nontrivial GCD gain). Negative control: `F_p` (expected collapse). Seeds `{20260719..}`.

### Quantitative promotion gate
Over prime-field `F_p`, skew-GCD cost trends below `r^{5/2}` **without** changing the object. Collapse on `F_p` is a scoped negative that also names the lane closed.

### Proof track
Lemma: over `F_p`, the linearized five-point membership skew resultant equals the commutative resultant (or not).

### Disproof track
Show the skew ring degenerates over `F_p` ⇒ no gain (expected).

### Reproduction artifact
contract `..._p1606_ore_skew_resultant_membership.md`; impl `p1606_ore_skew_resultant.py`; result/audit; ledger `ECFG-P1606`.

---

# GROUP D — Negative-theory / barrier candidates

*Each imports a lower-bound technology no prior barrier used; each threshold CLOSES a live gate if it bites.*

## Candidate: PROOF-SPACE-PEBBLING-D1

### One-sentence mechanism
Import **proof-complexity space / pebbling** lower bounds: the P1510 compiler claims `O(r^2)` state, and a pebbling / space lower bound on the m=5 membership refutation forces any backend computing all `Theta(r)` rows to obey a space-time tradeoff `ST=Omega(r^4)`, forbidding the `o(r^{5/2})` total with `O(r^2)` space (closes RT-1476 batching).

### Status
CONJECTURE (barrier).

### Novelty classification
LEDGER-NEW (proof-complexity SPACE / pebbling unused; all prior proof-complexity barriers were DEGREE: PolyCalc/IPS/NSS).

### Semantic fingerprint F(C)
- algebraic object: the membership refutation DAG;
- available public operations: pebble placement (space) over derivation steps;
- hidden structure exploited: **pebbling number / space-time tradeoff** of the DAG;
- information discarded/retained: n/a (space meter);
- relation-generation primitive: n/a;
- compression primitive: none (lower bound);
- rank mechanism: n/a;
- descent mechanism: n/a;
- dominant cost exponent: space-time product.

### Nearest ledger entries
POLYCALC-D2 (batch7, degree), COMBINATORIAL-NSS-D2 (batch9, degree), SOS-LB-D1 (batch4, degree), APPROXDEG-D1 (batch8, degree), LIFTING-D1 (batch7, communication). All bound **degree or communication**; D1 bounds **space** (Ben-Sasson-Nordström pebbling), an orthogonal resource. The P1510 `O(r^2)` STATE claim is the exact object space complexity targets.

### Nearest literature
- Ben-Sasson-Nordström, "Understanding space in proof complexity" (space-time tradeoffs); Alwen-Serbinenko pebbling.
- Gap: proof-complexity space is for CNF/polynomial refutations; the P1510 compiler is a straight-line arithmetic circuit, so the space bound must be adapted to circuit pebbling (Hopcroft-Paul-Valiant / red-blue pebbling).

### Target family / path / cost / gate
Ordinary prime-field, `m=5`. Barrier form: pebbling number of the batched-membership circuit `= Omega(r^2)` ⇒ `ST >= Omega(r^4)` ⇒ with `S=O(r^2)`, `T=Omega(r^2)` per target, `Omega(r^3)` batch ⇒ rho-lost. Promotion gate: measured red-blue pebbling number trends `Omega(r^2)` on toy circuits. Proof track: the batched-membership DAG has pebbling number `Omega(r^2)`. Disproof: a `o(r^2)`-space linear-time backend (= the sub-rho algorithm).

### Reproduction artifact
contract `..._p1607_proof_space_pebbling_barrier.md`; impl `p1607_proof_space_pebbling.py`; result/audit; ledger `ECFG-P1607`.

---

## Candidate: LDLR-DETECTION-BARRIER-D2

### One-sentence mechanism
Import the **low-degree likelihood ratio barrier** (asymptotic partner of A3): if the degree-`D` LDLR of the enriched-vs-honest 2-LP graph is `O(1)` for all `D` up to `q^{1/4}`, then no statistic computable in `q^{o(1/4)}` distinguishes the enrichment, so `delta<=1/4` unconditionally in the low-degree model (closes RT-1472 for all cheap enrichment detectors).

### Status
CONJECTURE (barrier).

### Novelty classification
POSSIBLY NOVEL (LDLR-as-barrier unused; distinct from Shearer/Delsarte/container/VC supply barriers).

### Semantic fingerprint
As A3 but in the impossibility direction: bounded LDLR norm ⇒ detection lower bound ⇒ δ ceiling.

### Nearest ledger entries
DELSARTE-LP-A2 (batch8), SHEARER-D3 (batch8), VCDIM-D3 (batch7), ENERGY-D1 (batch3), CONTAINER-CEILING-A3 (batch9) — all **supply/count** ceilings. D2 is a **detection** ceiling (can the enrichment even be found cheaply), a necessary condition for δ that no supply barrier captures. Pairs with A3 like batch8 APPROXDEG↔PROB-POLY.

### Nearest literature
Kunisky-Wein-Bandeira; Hopkins-Steurer; Bandeira-Kunisky-Wein low-degree hardness. Gap: LDLR predicts detection hardness; converting to an unconditional δ ceiling needs the low-degree model to be the right cost model for the enrichment search.

### Target / gate
Ordinary prime-field, `L=q^{1/5}`. Barrier bites if `||L^{<=D}||_2=O(1)` up to `D=q^{1/4}` ⇒ δ≤1/4. Promotion gate: empirical LDLR norm flat across sizes at the relevant degree. Proof: bound the degree-`D` LDLR for the enriched model. Disproof: LDLR diverges (⇒ A3 crossing candidate).

### Reproduction artifact
contract `..._p1608_ldlr_detection_barrier.md`; impl `p1608_ldlr_detection_barrier.py`; result/audit; ledger `ECFG-P1608`.

---

## Candidate: RAZ-MULTILINEAR-FORMULA-D3

### One-sentence mechanism
Import **Raz's min-partition-rank multilinear formula lower bound**: the marked resultant is multilinear in the `2r` source-marker variables, and the rank of its partial-derivative matrix under a **random balanced partition** lower-bounds any multilinear-formula backend to super-polynomial size, so no small **multilinear** circuit shares the object across `Theta(r)` targets below `r^3` (closes the multilinear sub-case of the P1512-R1 nonlinear exception).

### Status
CONJECTURE (barrier).

### Novelty classification
LEDGER-NEW (Raz random-partition rank distinct from batch10 shifted-partials depth-4 and Nisan fixed-order ABP width).

### Semantic fingerprint
- algebraic object: partial-derivative matrix `M_f^{Y,Z}` under a random partition of the `2r` markers;
- hidden structure exploited: **min-partition rank** (rank high under most balanced partitions);
- rank mechanism: rank of `M_f^{Y,Z}` (not shifted-partial dimension, not Hankel);
- dominant cost exponent: multilinear formula size floor.

### Nearest ledger entries
1. **SHIFTED-PARTIALS-A1 (batch10)** — shifted-partial-derivative dimension `Gamma` (depth-4, **fixed** partition). Raz uses a **random** partition and bounds general (unbounded-depth) multilinear formulas. Distinct partition model and circuit class.
2. **NISAN-NC-RANK-A2 (batch10)** — Nisan-Hankel coefficient rank on a **fixed** variable order (noncommutative ABP). Raz min-partition rank is over random *commutative* multilinear partitions. Distinct.
3. **RIGIDITY-A1 (batch8)** — Valiant rigidity of a fixed matrix. Distinct (rigidity vs partition rank).
4. **P1512-R1** — closes scalar-linear Chow; D3 closes the **multilinear-formula** sub-case of the surviving nonlinear exception.
5. **DEPTH-REDUCTION-CHASM-D2 (batch10)** — promotes depth-4 floors to general circuits. D3 is directly a general multilinear-formula bound; complementary, distinct object.

### Nearest literature
Raz, "Multi-linear formulas for permanent and determinant are of super-polynomial size" (JACM); Raz-Yehudayoff; the min-partition-rank survey (unbalancing sets, `1708.02037`). Gap: the marked resultant's multilinearity in markers must be verified; if it is only *set*-multilinear in a way that admits low min-partition rank, the bound is weak.

### Target / gate
Ordinary prime-field, `m=5`. Barrier bites if measured min-partition rank of `M_f^{Y,Z}` `= 2^{Omega(r)}` (or the appropriate `r^{omega(1)}`) on toy cells ⇒ no small multilinear formula ⇒ multilinear batching stays `>= r^3`. Promotion gate: rank fit high across sizes and partitions. Proof: min-partition rank `= Omega(...)`. Disproof: rank collapses under a natural partition ⇒ multilinear-formula escape (⇒ representation crossing candidate).

### Reproduction artifact
contract `..._p1609_raz_multilinear_partition_rank_barrier.md`; impl `p1609_raz_multilinear_partition_rank.py`; result/audit; ledger `ECFG-P1609`.

---

# RANKING

Scores 0–5 on: (1) distance from prior ledger mechanisms, (2) plausibility of an exact verifier, (3) chance of changing an exponent (not a constant), (4) complete-path coverage, (5) falsifiability at toy scale, (6) literature-novelty confidence, (7) low risk of hidden preprocessing/memory cost. Reject if semantic novelty <3, no complete route to descent, no rho comparison, or no precise distinction from the closest ledger entry.

| Cand | (1) | (2) | (3) | (4) | (5) | (6) | (7) | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A1 LDC** | 4 | 5 | 3 | 5 | 5 | 4 | 4 | 30 | **conservative winner** |
| A2 DIRECTSUM | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 28 | keep |
| A3 LDLR-meter | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 28 | keep (pairs D2) |
| B1 ANALYTIC-RANK | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 29 | keep |
| **B2 NC-RANK** | 5 | 5 | 4 | 5 | 4 | 5 | 4 | 32 | **representation winner** |
| B3 SCHUBERT | 4 | 3 | 3 | 2 | 3 | 3 | 3 | 21 | keep (INCOMPLETE — Phase 0 lemma) |
| **C1 BEREZIN-PFAFFIAN** | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 28 | **high-risk winner** |
| C2 LORENTZIAN | 5 | 4 | 3 | 4 | 4 | 4 | 3 | 27 | keep |
| C3 ORE-SKEW | 4 | 4 | 2 | 5 | 4 | 4 | 4 | 27 | keep (near-certain collapse) |
| **D1 PROOF-SPACE** | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 30 | keep (high-EV barrier) |
| **D2 LDLR-BARRIER** | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 30 | keep (high-EV barrier) |
| **D3 RAZ-MULTILINEAR** | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 31 | keep (high-EV barrier) |

No candidate scores novelty <3; none rejected outright. B3 is retained but flagged INCOMPLETE pending its Phase-0 Schubert-equivalence lemma.

**Selected winners:**
1. **Conservative:** LDC-LOCAL-DECODABILITY-A1 (ECFG-P1598).
2. **Representation:** NONCOMMUTATIVE-RANK-OPSCALING-B2 (ECFG-P1602).
3. **High-risk:** BEREZIN-PFAFFIAN-COMMONNORM-C1 (ECFG-P1604).

The three **D barriers are higher expected-value than the winners** (as in batches 6–10): each threshold, if reached, CLOSES a live gate (D1→RT-1476 batching space-time; D2→RT-1472 δ detectability; D3→RT-1476 multilinear exception). The winners are the sharpest *attack* probes but each carries a near-certain scoped-negative kill.

---

# WINNER CONTRACTS + FIRST COMMANDS

## Contract 1 — ECFG-P1598 LDC local-decodability α-meter (conservative)

```yaml
id: ECFG-P1598
title: LDC local-decodability lower bound as an exact RT-1476 alpha meter
hypothesis: >
  Any q-ary local decoder recovering the O(r) source keys of a campaign from a
  length-O(r^2) P1510 marked-resultant codeword uses per-key query exponent
  alpha >= 3/2, so the m=5 membership backend cannot cross rho via a short local code.
null_hypothesis: >
  A P1510-derived codeword admits an o(r^{3/2})-query decoder recovering all keys.
model: restricted; q-ary partial locally-decodable code; message = weight-O(r) source vector.
target_family: ordinary prime-field E/F_p, prime order, m=5, q=Theta(r^5); excludes supersingular/anomalous/small-embedding-degree.
sizes: r in {4,8,16}; p ~ {1024-bit-safe toy primes near r^5} = {1031, 32771, 1048583}.
seeds: [20260719,20260720,20260721,20260722,20260723]
metrics:
  - per_key_query_count alpha_hat (primary)
  - codeword length / r^2 (must stabilize)
  - decode success rate (correctness gate, NOT promotion gate)
positive_control: random q-ary code (expect Omega(r^2) queries).
negative_control: Reed-Solomon codeword (expect deg+1 queries).
success_criterion: fitted alpha_hat crosses 3/2 downward across sizes WITH a partial-LDC theorem forbidding alpha>=3/2.
falsification: alpha_hat >= 3/2 stable (barrier datum, RT-1476 closed for short local codes).
verifier: independent q-ary decoder replay + query-count audit + mutation rejections.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1598_ldc_local_decodability_alpha_meter.md
  impl: tasks/ecdlp_index_calculus/p1598_ldc_local_decodability.py
  result: p1598_ldc_local_decodability.json
  audit: p1598_ldc_local_decodability_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1598_ldc_local_decodability.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --emit p1598_ldc_local_decodability.json
```

## Contract 2 — ECFG-P1602 noncommutative-rank operator-scaling atomizer (representation)

```yaml
id: ECFG-P1602
title: Noncommutative inner rank via operator scaling on the five-point incidence pencil
hypothesis: >
  Presented noncommutatively, the Semaev five-source incidence pencil M(x)=sum A_k x_k has
  nc-rank o(r^{5/2}) while commutative rank is Omega(r^5); operator scaling then atomizes
  sources in poly(nc-dim), below rho.
null_hypothesis: >
  The pencil is shift/cyclic-structured, nc-rank = commutative rank = Omega(r^5).
model: linear matrix over the free skew field; deterministic nc-rank (Ivanyos-Qiao-Subrahmanyam, positive char).
target_family: ordinary prime-field, m=5, q=Theta(r^5); excludes provably-commutative pencils.
sizes: r in {4,8,16}; toy primes as P1598.
seeds: [20260719..20260723]
metrics:
  - nc_rank, commutative_rank, ratio (primary)
  - fitted beta_nc in r
  - operator-scaling iteration count / cost
positive_control: a Fuglede-Kadison/Edmonds pencil with nc-rank < commutative rank.
negative_control: diagonal pencil (nc = commutative).
success_criterion: ratio < 1 with fitted beta_nc < 5/2 across sizes.
falsification: nc = commutative on all cells (scoped negative; closes nonlinear-rank exception for this pencil).
verifier: independent nc-rank recomputation (algebraic + scaling) + commutative rank + mutations.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1602_noncommutative_rank_opscaling_atomizer.md
  impl: tasks/ecdlp_index_calculus/p1602_nc_rank_opscaling.py
  result: p1602_nc_rank_opscaling.json
  audit: p1602_nc_rank_opscaling_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1602_nc_rank_opscaling.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --compare-commutative --emit p1602_nc_rank_opscaling.json
```

## Contract 3 — ECFG-P1604 Berezin-Pfaffian common-norm (high-risk)

```yaml
id: ECFG-P1604
title: Berezin/Grassmann Pfaffian representation of the P1513 shared common-norm
hypothesis: >
  The P1513 pair-coupling H(U,W) is fermionic-Gaussian, so the shared common-norm equals a
  Pfaffian of an r x r skew coupling computable (with shared-input reuse) in o(r^{5/2}).
null_hypothesis: >
  The integrand has fermionic degree > 2; the Berezin integral is a higher moment reproducing r^3.
model: Grassmann-algebra Berezin integration; Pfaffian evaluation; char != 2.
target_family: ordinary prime-field, m=5, q=Theta(r^5); excludes char 2.
sizes: r in {4,8,16}; toy primes as P1598.
seeds: [20260719..20260723]
metrics:
  - fermionic degree of the integrand (primary; must be 2 for the shortcut)
  - Pfaffian evaluation cost vs r^3 product cost
  - fitted common-norm exponent with/without shared-input reuse
positive_control: a matchgate-realizable count (Pfaffian exact).
negative_control: a permanent (no Pfaffian shortcut).
success_criterion: integrand fermionic-degree 2 AND common-norm cost o(r^{5/2}) with shared reuse.
falsification: fermionic degree > 2 (scoped negative; P1513 cubic floor preserved).
verifier: independent Pfaffian recomputation + exact common-norm cross-check on P1510 transcript + mutations.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1604_berezin_pfaffian_common_norm.md
  impl: tasks/ecdlp_index_calculus/p1604_berezin_pfaffian.py
  result: p1604_berezin_pfaffian.json
  audit: p1604_berezin_pfaffian_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1604_berezin_pfaffian.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --emit p1604_berezin_pfaffian.json
```

---

# RED-TEAM: are the three winners disguised repetitions or cost-negative?

**A1 (LDC) — disguised repetition?** Nearest prior is LISTDECODE-B2 (batch7). Verdict: **not a repetition** — batch7 used list decoding as a *generator* (upper bound via decoding radius); A1 imports the *lower-bound* length-query LDC theorem, opposite direction, unused. **Cost-negative risk: HIGH.** The honest fatal obstruction is that LDC bounds degrade from exponential to polynomial once queries reach `Theta(sqrt r)`, so A1 most likely yields `alpha=Omega(1)` with a constant **below** `3/2` — an inconclusive obstruction, not a barrier, and certainly not a crossing. It is a *meter that most likely tightens the α accounting without moving the exponent.* Retained because even a sub-`3/2` obstruction with a certified partial-LDC theorem is new ledger data on RT-1476.

**B2 (nc-rank) — disguised repetition?** Nearest is P1512-R1 (commutative Chow, `deg(det)<=dim`) and NISAN-A2 (batch10, ordered-ABP width LB). Verdict: **not a repetition** — B2 computes the *free-skew-field inner rank* by operator scaling, a functional provably not capped by `deg(det)<=dim` and distinct from a Hankel-width lower bound. This is the sharpest instantiation of the surviving P1512-R1 nonlinear exception. **Cost-negative risk: HIGH but not certain.** The near-certain kill is that the P1512 cycle payload is a **cyclic/shift-structured** pencil, and for such pencils Edmonds is easy with nc-rank = commutative rank = `Omega(r^5)`. The nc gain needs genuine noncommutativity in the marker algebra, which the abelian curve group likely forbids (the MAHLER/ACFA/FORMALGROUP collapse family). If it collapses, B2 is a scoped negative that **closes the nonlinear-rank exception by name** — high value either way.

**C1 (Berezin-Pfaffian) — disguised repetition?** Nearest is P1504 (matchgate obstruction) and HOLANT-C1 (batch3). Verdict: **not a repetition** — P1504/HOLANT closed matchgate *Boolean signatures*; C1 integrates the actual `F_p`-valued marked resultant fermionically. But **the danger is real**: if the Berezin reduction ends up requiring the integrand to be matchgate-realizable, C1 collapses *into* P1504's closed lane. **Cost-negative risk: VERY HIGH.** The near-certain obstruction is that the marked resultant is **not quadratic** in the Grassmann variables, so the Berezin integral is a higher fermionic moment (permanent-like), reproducing the `r^3` floor. C1 is the one untried exact-evaluation route for the still-open P1513 gate, but it most likely reduces to "fermionic Gaussianity fails."

**Global red-team verdict.** All three winners are **scoped tightenings / lane-closures / high-variance probes, not crossings.** Each has a named, near-certain kill that (if realized) converts it into a scoped negative closing a specific escape hatch on RT-1476/RT-1472. The **three D barriers (D1 proof-space, D2 LDLR, D3 Raz-multilinear) are higher expected value**: each imports a lower-bound technology no prior barrier used and each threshold, if reached, closes a live gate unconditionally in its model. Consistent with batches 6–10, the mechanism space is saturated (12 reports, ~60 lanes); the marginal value this batch is (a) importing six functionals **provably decoupled from the commutative-determinant degree** that gated the entire P151x chain, and (b) the barrier arm.

**No break is claimed. RT-1472 and RT-1476 remain open.** Every result above is toy-scale, model-bounded, and scoped to the tested curves/parameters/solver/budget. A failed candidate is a scoped negative result, not evidence that prime-field ECDLP cannot be improved.

---

## Sources (external literature grounding)

- Kerenidis & de Wolf, exponential 2-query LDC lower bound via a quantum argument: [arXiv quant-ph/0208062](https://arxiv.org/pdf/quant-ph/0208062); near-cubic 3-query LDC LB: [arXiv 2308.15403](https://arxiv.org/pdf/2308.15403).
- Garg-Gurvits-Oliveira-Wigderson, operator scaling: [arXiv 1511.03730](https://arxiv.org/pdf/1511.03730); Ivanyos-Qiao-Subrahmanyam, non-commutative Edmonds' / nc-rank (positive characteristic): [Springer](https://link.springer.com/article/10.1007/s00037-016-0143-x); nc-rank via CAT(0): [SIAM AG](https://epubs.siam.org/doi/10.1137/20M138836X).
- Kunisky-Wein-Bandeira, low-degree likelihood ratio hardness predictions: [Springer](https://link.springer.com/chapter/10.1007/978-3-030-97127-4_1); Hopkins-Steurer low-degree detection at KS threshold (FOCS'17).
- Lovett, analytic rank of tensors: [arXiv 1806.09179](https://arxiv.org/abs/1806.09179); partition ≈ analytic rank over large fields: [arXiv 2102.10509](https://arxiv.org/abs/2102.10509); bias implies low rank for quartics: [arXiv 1902.10632](https://arxiv.org/pdf/1902.10632).
- Raz, super-polynomial multilinear formula lower bounds (min-partition rank / random-partition partial-derivative matrix); survey/unbalancing sets: [arXiv 1708.02037](https://arxiv.org/pdf/1708.02037).
- Brändén-Huh, Lorentzian polynomials (Annals 2020); Anari-Liu-Oveis Gharan-Vinzant log-concave sampling.
- Ben-Sasson-Nordström, space in proof complexity (space-time tradeoffs).
- Ore, theory of non-commutative polynomials (1933); skew-polynomial resultants over F_q{F}.
