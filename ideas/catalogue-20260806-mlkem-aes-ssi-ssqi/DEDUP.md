# DEDUP — catalogue 2026-08-06 (ML-KEM / AES / SSI / SSQI), 120 entries over 12 slices

Screener pass over `M1 M2 M3 A1 A2 A3 S1 S2 S3 Q1 Q2 Q3` (10 entries each, 120 total),
against the prior catalogue `ideas/catalogue-20260805/` (102 entries, INDEX + 9 slice
files + SCREENING) and against `ledger/hypotheses/`, `ledger/proposals/`.

**Nothing here is a ledger record.** No identifier is minted, no status changed. Every
verdict below is advisory to the Coordinator.

## 0. Structural facts that shape both tables

1. **The prior catalogue covers ECDLP / SSI / SSQI only.** Its slices are A1–A4
   (ECDLP index calculus, solving degree, representations, transfers), B1–B3 (SSI),
   C1–C2 (SSQI). So the twelve new slices split cleanly by collision exposure:
   - `M1 M2 M3` (ML-KEM) and `A1 A2 A3` (AES) have **no** prior-catalogue counterpart.
     Their only prior art is the ledger (`H-MLKEM-*`, `H-AES-*`, `EV-*`, `MEAS-*`,
     `CAND-*`, `KN-*`). Note the *name collision*: prior-catalogue `A1..A4` are ECDLP,
     new `A1..A3` are AES. They are unrelated.
   - `S1 S2 S3` sit directly on prior `B1 B2 B3`, and `Q1 Q2 Q3` sit directly on prior
     `C1 C2`. **Every prior-art collision in Table 2 with a `B*`/`C*` id lives here.**
2. **The 2026-08-05 catalogue was never executed.** Its own SCREENING records zero
   unanimous survivors, seven entries refuted by all three lenses (`A3-4 A3-5 A4-10
   B1-1 B1-6 B2-7 C2-7`) and two contested (`B3-6 C2-1`). Several new Q-slice entries
   nevertheless cite prior-catalogue entries as if they had produced data — see §3,
   *phantom prior art*. This is a systemic defect, not a per-entry one.
3. **Four A1 algebraic facts are already discharged in-session** (DDT/BCT/LAT class
   collapse, MixColumns weight transitions). They are re-derivable in seconds and carry
   no evidence strength. `A1-1`, `A1-2`, `A1-3` must be re-scoped to their *undischarged*
   halves before costing; their "Prediction (i)" rows are retrodictions of work already
   done in the same document that proposes them.

---

## 1. CROSS-SLICE DUPLICATES AMONG THE NEW ENTRIES

A twelve-way fan-out produced **26 near-duplicate pairs**. Rows marked ⚑ are the ones a
Coordinator must act on before batching; the rest are sequencing constraints.

| # | pair | shared tracked object | resolution (one line) |
|---|---|---|---|
| ⚑1 | **M1-5** ∥ **M3-2** | counted (never timed) instrumentation of one `bgj1`/`g6k` sieve over `d ∈ [50,80]`, feeding one memory-charged cost exponent | **MERGE.** Same patch, same seeds, same dimension ladder, same declared motivation (the dead `EV-MLKEM-d8f627/4a9cfe` timing confound); `γ` (pairs-per-vector) and `ρ` (hop locality) are two readouts of one instrumented run, and running them apart pays the g6k build twice. |
| ⚑2 | **M2-1** ∥ **M2-6** | the left-tail order statistic of a per-key functional over the *victim's* key generator, capped by the same `s·√(2 ln N)` law | **MERGE.** Identical instrument (exact convolution → order statistic → ceiling law → norm-ratio→`Δβ` conversion); only the functional changes (`δ(sk)` vs `‖(s,e)‖²`). One entry with two functionals; the ceiling is the finding either way. |
| ⚑3 | **A1-1** ∥ **A1-3** | the exact 255-term sum over `TO-TORUS` classes across one super-box, no search | **MERGE.** Same enumeration engine with `DDT` swapped for the trace-form `LAT`; the differential maximiser and the linear-hull coherence factor come out of one loop. Keep both predictions, one implementation. |
| ⚑4 | **A1-10** ∥ **A3-2** | the value-averaged 16-bit byte-activity abstraction of the AES round function and its gap from reality | **MERGE.** A1-10 evolves the *mass* `π_r` under `Σ_SR ∘ C^{⊗4}`; A3-2 evolves the *support* `R_A(r)` and measures realizability `φ_A(r)`. Support is the zero-set of the mass. One exhaustive `C` build plus one `2^30`-pair sampling run yields `π_r`, `R_A(r)`, `φ_A(r)` and `r*`. |
| ⚑5 | **A1-7** ∥ **A3-6** | the across-key overdispersion index `Var_K(N)/E_K(N)` of a distinguisher count | **MERGE.** A1-7 reads it as hull evidence, A3-6 as the reason a rate excess has weak per-instance ROC. Same draws, same counts, same code path. Measure once, report both readings — and note A3-6's overdispersion, if real, *invalidates the Poisson LLR* A3-5 wants to compute. |
| ⚑6 | **A2-4** ∥ **A2-9** | `TO-COMB`: whether a mode's output combiner transmits a set-aggregate death round | **MERGE.** A2-9 (GHASH power weighting) is literally class (ii) of A2-4's combiner taxonomy — the predicted *breaker* of A2-4's affine-preservation identity. One taxonomy, one sweep budget, the weighted case as its negative arm. |
| ⚑7 | **A3-3** ∥ **A3-10** | "every construction in this repository is dominated by the definitional reference" | **MERGE (and PICK A3-10's arm).** Both are expected-CLOSED domination entries against `REF-A`. A3-10 costs one 60-s exclusion-rate measurement plus instrumentation; A3-3 costs twelve full `attack6n`/brute-force runs to draw a curve through a committed `DOMINATED` point whose sign it predicts will not change. Fold A3-3's `h ∈ {12..15}` window into A3-10 as one row. |
| ⚑8 | **Q2-10** ∥ **Q3-9** | the exchange rate of a restriction on `L(E,X,B)` against the same two pre-computed nulls (aligned / independent), on the same four toy primes, both aimed at levers **L2 / A4** | **MERGE.** Q3-9's channel decomposition (degree-measurable vs codomain-measurable) is a *classification of* Q2-10's walk-choice family. One pre-registered restriction battery, reporting per restriction both the channel index and the measured exponent `e`. Running both re-closes L2/A4 twice with two different arguments. |
| ⚑9 | **Q2-5** ∥ **Q3-8** | a pre-declared closed battery of cheap functions of `j(E)` (`Tr(j)`, `N(j)`, roots of `Φ_ℓ`, `F_p`-rationality) evaluated exhaustively on the same toy supersingular graphs, both with expected verdict CLOSED | **MERGE.** Q2-5 reads the battery as a proximity sketch (`ρ_LSH`), Q3-8 as a δ-level stratum (mutual information vs permutation null). Identical enumeration, identical battery members, identical expected outcome. Two readouts of one build. |
| ⚑10 | **S2-6** ∥ **S2-8** | `TO-CHARGE`: signature-typing the pinned CSIDH cost derivation to find which resources are charged in which column | **MERGE.** Both are zero-compute "strike the coefficient, keep the type" audits of the same equations (4.1 / 3.5). S2-6's row is the setup/class-group-presentation cost, S2-8's row is the `4D` lookup term. One audit table, two rows. |
| ⚑11 | **S3-2** ∥ **S3-4** | one published byte-level field of a SQIsign signature, its derived null law, and a two-sample across-key test on the same toy signer at `p ∈ {2^11,2^13,2^15}` | **MERGE.** `n_bt` and `hint_pk` differ only in which byte is read; the toy signer, the enumeration of the supersingular set, the χ²/two-sample machinery and the key ladder are shared verbatim. |
| ⚑12 | **S3-2** ∥ **S3-8** | same as #11, with `M_chl mod 2^k` as the field | **MERGE into #11.** S3-8's own minimal test says it "reuses S3-2's toy signer". Three fields, one battery, one pre-registered support derivation per field at Stage 0. |
| 13 | **M1-3** ∥ **M3-5** | the exact CBD law's entropy used to price an attacker's search / query budget | **SEQUENCE M1-3 first.** M1-3 computes `H`, `H_{1/2}`, `log2|supp|` exactly and argues Shannon is the *wrong* exponent for guessing; M3-5 then uses Shannon `H(s)` legitimately (a mutual-information floor, not a guessing bound). Running M3-5 first invites the exact confusion M1-3 exists to name. |
| 14 | **M3-1** ∥ **M3-4** | the 3-D physical memory charge `α = 1/3` applied to a declared live-set | **SEQUENCE M3-1 first.** M3-4's `Δ = (1/3)·log2(max(...))` *is* M3-1's result assumed. M3-1 carries the known-answer gate (reproduce `H-MLKEM-b1300f`'s 199.8/299.7/437.1 at `α=1`); M3-4 has none of its own. |
| 15 | **M3-1** ∥ **Q2-2** | "one memory number is not a cost": physically charging storage rather than counting cells | **COMPLEMENTARY-PAIR, one shared derivation.** M3-1 (lattice, `α = 1/D`) and Q2-2 (isogeny, `w_fast` vs `S_total`) are the same physical argument in two domains. Write the `D`-dimensional charge once (M3-1 has the gate) and have Q2-2 cite it rather than re-derive. |
| 16 | **M1-5/M1-6** ∥ **M1-6** ⟶ **M3-2** | see #1; M1-6 (`ρ = P_warm/P_cold`) is a third readout of the same patched sieve | **SEQUENCE inside the merged instrument (#1).** Different protocol (warm/cold restart of the adjacent block), same binary and counters. Do not build a second instrumented g6k. |
| 17 | **M2-8** ∥ **M3-8** | the accept/reject branch structure of decapsulation, probed by mutation plus an implicit-vs-explicit-rejection ablation | **COMPLEMENTARY-PAIR (paper-side vs measured-side).** M2-8 enumerates the *mathematical* fibres of the specified map at toy parameters; M3-8 measures a *build's* two-bit `(a,r)` signature over `dk` byte indices at real parameters. Pair them: M2-8 predicts which rows must flip, M3-8 is where the flip is observable. |
| 18 | **M2-8** ∥ **M3-7** | implicit rejection as the object | **SEQUENCE M2-8 first.** M3-7's influence-set difference `A \ B` is only interpretable once the accept/reject fibre rows are named; M2-8 is toy-scale and cheap, M3-7 needs a taint engine. |
| 19 | **M2-5** ∥ **M2-10** | the FIPS 203 wire-object census (encoding fibres, byte lengths, `{800,1184,1568}` × `{768,1088,1568}`) | **COMPLEMENTARY-PAIR, shared census.** M2-5 counts the encoding fibre of one object, M2-10 the length coincidences across all of them. Build the census table once; both entries read it. |
| 20 | **A2-6** ∥ **A3-4** | an exact DP / layered BFS over a ≤`2^16` byte-activity state space returning a minimum active-S-box count | **COMPLEMENTARY-PAIR, one implementation.** A2-6 runs it on the key schedule, A3-4 on the data path (as a *known optimum* for a search-honesty control). A2-6 itself names the `2^32` joint automaton as the boundary — these two are its two halves. Share the transition-relation code. |
| 21 | **A2-1** ∥ **A2-2** | the GF(2)-linear structure of the σ-relaxed key schedule, computed by one elimination on `[A_K | A_σ]` | **SEQUENCE A2-1 first.** A2-2 builds `Z_pred` *from* A2-1's `A_K`, `A_σ`. One program emits both the annihilator dimension (960/1216/1248) and the permanent-zero incidence set. |
| 22 | **A2-6** ∥ **A2-8** ∥ **A2-10** | the key-schedule difference-activity automaton | **SEQUENCE A2-6 first.** A2-8 supplies the per-step active count the automaton consumes; A2-10 explicitly extends the automaton with DM/MP boundary conditions. Neither is standalone. |
| 23 | **A1-3** ∥ **A3-7** | `hull / best-single-characteristic` as a measured ratio at `r = 2,3,4` with an exact `r = 1` (or identity-S-box) gate | **COMPLEMENTARY-PAIR (linear vs differential), one DP engine.** A1-3's `F` is the *linear*-hull coherence factor; A3-7's `κ` is the *differential* clustering factor. Same per-column DP over the same tables, same gate structure, same consumer (open problem O-1). Do not build two. |
| 24 | **Q1-2** ∥ **Q1-8** | `P0`, the success probability of the incumbent, as a lattice integral at threshold `X² = B·D` | **COMPLEMENTARY-PAIR (paper-side vs measured-side).** Q1-8's own text says it "decides Q1-2". Q1-2 derives the `19.73`-bit undiscounted bound; Q1-8 measures where in `[1, 2^19.73]` the ratio `R` actually sits. Neither is interpretable alone; run in one batch. |
| 25 | **Q1-3** ∥ **Q1-9** | `TO-LPF` (the largest-prime-factor law of an entry's degree) converted into bits of per-entry cost overhead, both capping **L4-BATCH** | **SEQUENCE Q1-3 first.** Q1-9's "charge at `ℓ = B_opt`" step needs Q1-3's entry-weighted law (`E[log P(d)/log B] = 0.9026`) to be established, and both deliver a cap on the same removable fraction — reported apart they will be double-counted into the overhead ledger. |
| 26 | **Q1-5** ∥ **Q3-5** | lever **A7** (cross-attempt amortisation), same toy graphs, both with expected verdict CLOSED-with-a-number | **COMPLEMENTARY-PAIR, must be reported jointly.** Q1-5 closes the *smoothness-correlation* route to A7 (does `1/P0` multiply or add), Q3-5 closes the *pooled-table-validity* route (birthday yield, crossover `k* = P0·p^{1/3}`). Two independent closures of one lever; filed separately they will read as two findings. |
| 27 | **Q3-1** ∥ **Q3-2** | self-closing vertex maps `τ` on `G_ℓ(p)` | **SEQUENCE Q3-1 first — it can empty Q3-2.** If `Aut(G_ℓ) ∩ Aut(G_3) ∩ Aut(G_5) = ⟨σ⟩`, Q3-2's family `T = {τ_1..τ_k}` has `k = 1` and its whole exchange-rate surface is vacuous. Q3-1 is ~150 lines of Python; Q3-2 is a two-parameter surface plus a lookup program. |
| 28 | **Q2-6** ∥ **S2-7** | a budget-allocation vector under a width/parallelism cap, with the crossover as the deliverable | **COMPLEMENTARY-PAIR.** Q2-6 (claw on the `p^{1/3}` table, `W* = p^{1/6}`) and S2-7 (classical presearch vs collimation sieve, corner solution moving under a width cap) are the same instrument on two problems. Share the cap-and-crossover template; keep both. |
| 29 | **Q2-8** ∥ **Q2-5 / Q2-9 / Q2-10 / Q3-8** | the coverage ratio `ρ = 12M/p` of every toy table in the SSQI slices | **SEQUENCE Q2-8 first.** Q2-8 is a meta-entry classifying which toy statistics are `ρ`-stable; every other toy measurement in Q2/Q3 is inadmissible for extrapolation until it has passed. It is the cheapest gate in the two slices. |
| 30 | **S1-1** ∥ **S1-3** | the `p^{2/3}` local-information threshold, same three toy primes, same instrument, both predicting `α = 2/3 ± 0.05` | **COMPLEMENTARY-PAIR, pre-register jointly.** S1-3's own text says it reaches "the same threshold as S1-1, arrived at by a different route" (ball census vs CM-incidence rigidity). That agreement is the value — but only if both predictions are frozen before either runs, otherwise the second is a re-report of the first. |

**Sequencing constraints that are not duplicates but bind the batch plan:** `S1-1 → S1-7`
(S1-7's `m_D(E)` is read off S1-1's census); `S1-2 → S1-8` (S1-8 measures the sensitivity
horizon of S1-2's filter list and cross-checks its `c = 1/2`); `S2-3 → S2-9` (S2-3's `A` is
S2-9's weight); `S2-5 → S2-7` (S2-7 consumes S2-5's width law); `S3-2 → S3-7` (S3-7 runs in
S3-2's two arms); `Q1-1 → Q1-4` (Q1-4 uses Q1-1's normal-form machinery); `A3-6 → A3-5`
(a Poisson LLR is not computable if `Var/Mean ≠ 1`); `M3-5 → H-MLKEM-008` (M3-5 decides in
advance whether the factor-2 the approved hypothesis chases is even available).

---

## 2. COLLISIONS WITH PRIOR ART

Verdicts: `duplicate_drop` / `successor_keep` (extends it — how is stated) /
`adjacent_keep` (shares a topic, different tracked object).

### 2a. The high-risk rows — where this program is closest to rediscovering itself

| new | prior | verdict | why |
|---|---|---|---|
| **Q2-3** | `H-SSI-8ff06b` (committed hypothesis: the sign of the goal's central comparison is set by cost functional and *parallelism regime*; item (iv) reverses the AT verdict **under unbounded parallelism**) | **successor_keep** | Q2-3 attacks exactly 8ff06b(iv)'s premise: it derives the validity range in `n` of the `T(w,n) = p^{1/2+o(1)}/(w^{1/2}n)` formula 8ff06b reads verbatim, and emits a wall-clock floor (`2^{56}–2^{71}` steps at NIST-I) that no processor count beats. That is a genuine extension — **but Q2-3 does not cite 8ff06b at all** (it cites C2-6/C2-8). It must be re-filed against 8ff06b or it will read as an independent discovery of the same regime dependence. |
| **Q2-6** | `H-SSI-8ff06b` (ii)/(iii) — a `p^{1/6}` gap between the poly-memory and `p^{1/3}` endpoints; and prior **C2-9** | **successor_keep** | The `p^{1/6}` exponent is already in the corpus from the same tradeoff curve; Q2-6's `W* = p^{1/6}` is a *different* comparison (quantum vs classical parallel at equal total budget) that happens to land on the same number. Keep — but the coincidence must be stated, not presented as a new constant. Separately: Q2-6's known-answer gate demands that "at `n = 1` every cell reproduce C2-9's committed table exactly" — **C2-9 has no committed table** (see §3). Q2-6 must produce it, which makes Q2-6 a *replacement* for C2-9 rather than an extension. |
| **S1-5** | `IDEA-20260806-bcbcf5` (minted today: eigenvalues are Hecke eigenvalues, carry **zero bits about any individual curve**, and the eigenvector-coordinate access cost forces the spectral lane's budget) | **successor_keep** | S1-5 supplies the two numbers bcbcf5 asserts qualitatively: the identification number `k(p)` (predicted 1–2, flat in `p`) and the per-coordinate access cost, whose product is `Θ(p^{2/3})`. But S1-5 declares its nearest neighbour as BATCH-046's MSI direction and **never mentions bcbcf5**, which is the same lane minted in the same week. Re-file as bcbcf5's measured successor. |
| **Q3-6** | the L4 chain `H-SSIQ-18dc91 / 9e2c71 / 137200 / 36e970` with `EV-SSIQ-f3ce32`, `EV-SSIQ-028c9f` | **successor_keep** | Q3-6's headline at `ℓ = 2` is a **retrodiction of a trapped fraction the campaign has already measured**, and the entry says so. It survives only on (P-b): the forced `0.865 ± 0.05` at `ℓ = 3` and `0.954 ± 0.04` at `ℓ = 5`, a new arm on graphs that do not exist yet. The `ℓ = 2` row must be labelled a consistency check with **zero evidence strength**, never a result. |
| **Q3-7** | `IDEA-20260805-250e50` / `H-SSIQ-90e07b` (`E(θ,s,γ) = (1/2 − 3θ/2)_+ + max(γ, θ−s)`, with `E(1/4,0,1/4) = 3/8` recorded) | **successor_keep** | The constant `3/8` is already committed. Q3-7's new content is the four-condition certificate `(k, r, β, u)` — memory- and family-aware where 250e50 is memory-blind and family-blind by its own record — and the identification that "enlarge the family" and "exploit the tail" reach 3/8 by two routes. The 3/8 must be cited to 250e50, not re-derived as a discovery. |
| **S3-9** | `H-SQISIGN-c0488f` (pre-registered threshold on publishing `M_sk mod 2^k`) | **successor_keep** | S3-9 predicts it will *reproduce* c0488f's independently pre-registered `k = e_rsp` threshold. The new content is the rank ledger itself: `rank(R_q) − U_q = −1` **uniformly in `q`**, i.e. zero bits about `d` at every signature count. The reproduction is a known-answer gate; it is not the finding, and must not be scored as one. |
| **S1-2** | `IDEA-20260806-e4c719` (minted today: `exponent = c·log_p(det)/(2·rank)` — "one formula that returns 1/3, 1/2 and 1/4 exactly") | **adjacent_keep** | Two different one-parameter identities that both retrodict the corpus's `1/3`, `1/2`, `1/4` anchors, minted a day apart, both framed as "one number decides the whole family". The parameters genuinely differ (S1-2's `c` is the membership-test cost exponent in a neighbour-query model; e4c719's `c` is the degree-count exponent of the ambient morphism category). Keep both — but S1-2 must state the distinction explicitly or a reader will take them for the same theorem. |
| **M1-8** | `EV-MLKEM-004` / `H-MLKEM-001` (exact CBD convolution under **FIPS compression and rounding semantics**) | **successor_keep (with obligation)** | The `Compress`/`Decompress` fibre structure for `d_u ∈ {10,11}` is inside the committed instrument. M1-8's genuinely new step is *conditioning on the ciphertext* — partitioning coordinates into noise classes and recomputing the uSVP block size under M0/M1/M2. It must **read** the committed census, not recompute it, or the entry's first deliverable is a rediscovery. |
| **M1-9** | `H-MLKEM-fef5ae` (arms (M) ML-KEM-shaped negacyclic module lattices vs (N) unstructured, at matched determinant `q^{d/2}`) and `IDEA-20260805-522b48/530869` (ring-deleted matched null) | **adjacent_keep (with obligation)** | The matched-null *construction* is committed twice already. M1-9's new object is reduction **dynamics** (`t*`, lag-`n` autocorrelation) rather than a lattice-point census or a gain audit, and its expected verdict is that neither observable fires. Keep — but reuse fef5ae's instance generator; building a third matched null is the rediscovery. |

### 2b. Genuine successors

| new | prior | verdict | why |
|---|---|---|---|
| **S1-1**, **S1-2** | **B1-9** (cost curve for a per-vertex terminal filter, `C(M)` left as a free function) | successor_keep | S1-1 computes the entropy of the *maximal* local statistic, bounding every menu item at once; S1-2 converts B1-9's free `C(M)` into the single exponent `c` in `1/(2(2−c))`, with a lower bound on `c` from ball geometry and two committed retrodiction anchors. B1-9 could only ever speak about its hand-listed menu. |
| **S2-5** | **B2-7** (refuted by all three screening lenses for re-assembling equations Eq. 4.1 already assembles) | successor_keep | S2-5 does not assemble the published equations at all: it computes peak liveness `Θ(d·log #Cl)` and critical path from the recursion's dependency DAG. That is precisely the escape from B2-7's refutation, and it is stated. |
| **S2-9** | **B2-7** | successor_keep **(contested)** | S2-9 moves the argmin `(d*, δ*)` under a per-query weight `A` and delivers a threshold list, which B2-7 cannot express. **But** grid-minimising `total(d,δ;A)` assembled "from committed locators only" is uncomfortably close to the move that got B2-7 refuted. S2-9 must carry its escape argument explicitly or it re-inherits the refutation. |
| **S2-2** | **B2-8** (reconstruct the leading constant `c` in `2^{c√log N}`) | successor_keep | S2-2 takes `c` as an interval rather than pinning it, and computes the locus where a *competing polynomial sample budget* overtakes the sieve — a comparison B2-8 could not have made, since the competing route entered the corpus on 2026-08-06. It also repairs B2-8's `log p` vs `log N` variable defect. |
| **S2-8** | **B2-6** (Wiener-3D wiring clock on QRACM) | successor_keep | S2-8 asks whether the pinned `4D` charge *already is* an access charge, which is strictly upstream of adding a latency clock and changes B2-6's predicted magnitude. Sequence S2-8 before B2-6 if B2-6 ever runs. |
| **S3-5** | **B3-1** (two-stage disclosure screen) | successor_keep | S3-5 shows Stage A and Stage B have different invariance properties under information-preserving re-encoding, so B3-1's three-valued verdict is not a function of `Σ` alone — a well-definedness defect in B3-1's input object, plus the cost-annotated closure as the repair. |
| **S3-7** | `IDEA-20260805-18a4d4` (secret connecting ideal cancels; a whole family of pairwise statistics dead before measurement) | successor_keep | S3-7 asks whether the cancellation identity covers the *second* published curve `E_aux`, where the ideal is not of the form `conj(I_τ)·(…)`, and converts 18a4d4's proven-dead response arm into the negative control that makes the `E_aux` reading interpretable. |
| **S3-8** | `IDEA-20260805-c4ae3d` / `H-SQISIGN-c0488f` | successor_keep | Discharges a normalisation obligation c4ae3d's own hypothesis records as undischarged, on the *published* `M_chl` rather than the withheld `M_sk`. |
| **S3-10** | `IDEA-20260805-18a4d4`'s forward guidance ("surviving information must live in representative-sensitive functionals") | successor_keep | S3-10 supplies the count that closes the representative-insensitive lane: `H(d | E_pk) ≤ 3` bits at every parameter set. |
| **Q1-2** | **C1-3** (Remark-1 multiplicity priced against a Siegel–Rogers short-vector count) | successor_keep | Q1-2 shows C1-3 **double-charges**: the threshold `X² = B·D` is already bought by a table built to `X`, so the marginal cost of the multiplicity in `[D, X²]` is not `M ≈ B·T`. It refutes a prior entry's charging rather than repeating it. |
| **Q1-1** | **C1-2** (declared) and **C1-10** (the `o(1)` ledger — *not* declared) | successor_keep | Q1-1 supplies the saddle-point normal form and the 15.19-bit NIST-I gap between `B_opt` and the paper's fixed `B`. C1-10 is the *container* for exactly this accounting; Q1-1 (with Q1-3, Q1-9, Q1-2) is C1-10 executed with numbers. File Q1-1 as C1-10's first line item, not as an independent ledger. |
| **Q2-7** | **C2-1** (streaming `M²/w` as an *ordering control*, contested by screening) + **C2-2** (two-law step charge) | successor_keep | Q2-7's content is the composition: the control C2-1 introduced only to catch cheaters is a legitimate algorithm once charged at C2-2's cheap step law, with a crossover at `w ≈ 2^{61}–2^{66}` nobody computed. It must be filed as depending on both and must not re-derive either. |
| **Q2-2** | **C2-6** (charge the machine, not the RAM) | successor_keep | Q2-2 changes the frontier's **dimension** (fast memory vs total storage as two resources) where C2-6 changes its metric. C2-6 cannot express an external-memory branch. |
| **Q3-5** | goal lever **A7** | successor_keep | A7 is the statement of a lever with no result; Q3-5 supplies the validity proof for cross-attempt matches and the crossover `k* = P0·p^{1/3}`, turning the goal record's qualitative note into a number. |
| **M3-1** | `H-MLKEM-b1300f` / `IDEA-20260805-cdc87d` (sweeps `α ∈ [0,1]`, declares the physical→`α` mapping its "weakest link") | successor_keep | M3-1 supplies that mapping (`α = 1/D`, physically capped at 1/3) and consequently **refutes** b1300f's P3 rather than extending it. Its known-answer gate reproduces b1300f's own 199.8/299.7/437.1 at `α = 1`. |
| **M3-4** | `EV-MLKEM-020` (borrowed, uncalibrated `0.2075·β` memory literal) | successor_keep | Charges the three structures the dual attack declares in the estimator's own output (`2^{c_Mβ}` sieve, `N` stored vectors, `q^{k_fft}` accumulator), one of which the borrowed literal does not describe at all. |
| **M1-5** | `EV-MLKEM-020` | successor_keep | Supplies exactly the calibration half that 020's own `what_does_not_survive_scrutiny` says it lacks — counted, emulation-invariant, and therefore immune to the confound that killed the previous sieve lane. |
| **M1-4** | `IDEA-20260805-2b94fe` (exact per-coordinate log-likelihood scoring) | successor_keep | M1-4 is the *ceiling on* 2b94fe: it prices the maximum possible value of the substitution (`< 0.3` core-SVP bits) before anyone implements it, with the expected verdict that 2b94fe should not be run. A screening entry on prior art — cheap and legitimate. |
| **M3-5** | `H-MLKEM-008` (approved: soft-oracle leakage budget, Cortex-M4, "within 2×") | successor_keep | Computes the channel-capacity floor that decides *in advance* whether the factor of two is even available, and needs no device — which matters because the device does not exist in this environment. |
| **M2-3** | `EV-MLKEM-d146a5` (deployment census, `M = 1` for SSH/IKEv2) | successor_keep **(half)** | The `H(Δβ)` measurement is new and the failure-hint-accumulation mechanism is new. Part (a) — re-reading the committed `census.json` for a `Q` column — carries **no new evidence** and must be labelled a re-read. |
| **A2-1** | closure **LP-1** (`(K,σ)` is not a lossy re-coordinatisation of `K`) | successor_keep | A2-1's annihilator exists *because of* the relaxation LP-1 declined to make; it is lossy in the required direction and yields a count (960 / 1216 / 1248) LP-1 has no way to produce. |
| **A2-2** | `MEAS-RT-D` / **NC-4** (density `0.78125`, symbolic derivation retracted as wrong in the unsafe direction) | successor_keep | A2-2 predicts the **incidence set** from GF(2) algebra containing no S-box, and adds the random-S-box and random-Rcon substitution arms that decide whether the pattern is about AES or about wiring — a question a density cannot answer. |
| **A2-8** | **NC-5** + `MEAS-RT-D` (within-schedule round-key repetition, `0/200000`) | successor_keep | Derives the **cross-key** shift defect exactly (`(01 ⊕ x^s) ‖ 00 ‖ 00 ‖ 00`, key-independent, slide window exactly 1) where NC-5 sampled a within-schedule event and asserted a reason. |
| **A1-8** | `MEAS-RT-C` (mixture-exchange byte-collision ratio 1.012–1.018, **present equally in its own null at every round 4–10**) | successor_keep | Changes the readout from a ratio to a 14-bit agreement-pattern word with a probability-one known-answer gate at `r = 1`, i.e. it repairs the exact defect MEAS-RT-C's own scope note records. |
| **A3-1** | `H-AES-d6405d` / `sq_null.c mode_compare6` (naive-vs-partial-sums ratio at one table size) | successor_keep | Tracks the *ratio of the two ratios* as a function of working-set size and pre-registers a **sign change** — a statement one table size cannot make. |
| **A3-6** | `EV-AES-9794e1` OBS-B6-1 / `EV-AES-a47618` (yoyo rate ratio 13.5–15.6× at r5) | successor_keep | Replaces an aggregate rate ratio with the operating curve of a per-instance decision rule plus the arms' overdispersion — neither exposable by a ratio of means. |
| **A3-8** | `EV-AES-005` OBS-5 (`25.66 s` certified `r=5` recovery; re-executed on a second key) | successor_keep | Those records establish existence and reproducibility; A3-8 tracks the cost **distribution** over 64 instances and asks whether the committed single-run margin has an unstated `±`. |

### 2c. Adjacent — same topic, different tracked object (keep, no action)

`M1-1` ∥ `IDEA-20260805-f7c912` (segment-boundary integers vs the scalar `δ_0`) ·
`M1-2` ∥ `GOAL-MLKEM-005` (randomise the **basis**, not the target; convexity cap does not apply) ·
`M1-3`, `M2-4`, `M3-6` ∥ `EV-MLKEM-004` (guessing exponent / conditional geometry / conditional observability vs a failure marginal) ·
`M1-6` ∥ `H-MLKEM-fef5ae` (a ratio across adjacent blocks vs a census at one block) ·
`M1-7` ∥ `GOAL-MLKEM-004` / `EV-MLKEM-da9e3b` (scores no candidate; certifies a lift) ·
`M1-10` ∥ `EV-MLKEM-2cd08b` (an `r×c` interaction test vs a nested-ablation localisation) ·
`M2-1` ∥ `H-MLKEM-dc51f5` / `IDEA-20260805-1d76e9` (per-key DFR vs public-key norm shortfall — note dc51f5 proves `ek` is exactly uniform, which is *why* M2-1/M2-6 move the selector off `ek`) ·
`M2-2` ∥ `KN-TECH-048` · `M2-5`, `M3-9` ∥ `H-MLKEM-d9062d` / `IDEA-20260805-3c957e` ·
`M2-7` ∥ `IDEA-20260805-a102ec` · `M2-8`, `M3-7`, `M3-10` ∥ `EV-MLKEM-006` / `EV-MLKEM-007` ·
`M2-9` ∥ `EV-MLKEM-d146a5` · `M2-10` ∥ `EV-MLKEM-021` · `M3-3` ∥ `EV-MLKEM-020` (quantum coordinates 020 does not have) ·
`M3-8` ∥ `KN-FIND-001` / `EV-MLKEM-005` ·
`A1-1` ∥ `MEAS-RT-A` · `A1-2` ∥ `CAND-ND-3` · `A1-3` ∥ `CAND-ND-5` · `A1-4` ∥ class-D `D4` ·
`A1-5` ∥ derivation `D-6(2)` and Proposition 806-1 / `H-AES-0e5fa1` (0e5fa1's `Φ` is SubBytes-free; A1-5's is not) ·
`A1-6`, `A1-10`, `A3-2` ∥ `CAND-RR78-D` (a three-way fan-out on one prior candidate — see Table 1 #4) ·
`A1-7` ∥ `CAND-ND-2` (second moment across keys vs first moment at fixed key) · `A1-9` ∥ `KN-FIND-028` Fact 2 ·
`A2-3` ∥ `CAND-ND-4` · `A2-4`, `A2-5` ∥ `MEAS-GOAL-AES-002-002` / REF-C (used correctly, as a gate) ·
`A2-6` ∥ `H-AES-b02749` · `A2-7` ∥ `H-AES-8c2d07` · `A2-9` ∥ `H-AES-ecf3ad` · `A2-10` ∥ Proposition 806-1 ·
`A3-4`, `A3-9` ∥ `KN-FIND-029` / `EV-AES-acddd0` · `A3-5` ∥ RQ-AES-003 R6 · `A3-7` ∥ open problem O-1 ·
`A3-10` ∥ `MEAS-GOAL-AES-002-005` / NC-1 ·
`S1-3` ∥ `IDEA-20260804-84328c` · `S1-4` ∥ `IDEA-20260805-d66193` / `H-SSI-bdc41f` ·
`S1-6` ∥ `KN-TECH-057`, `B1-7` · `S1-7` ∥ `IDEA-20260806-bcbcf5` · `S1-8` ∥ `B3-8` ·
`S1-9` ∥ `IDEA-20260806-d5a34e` · `S1-10` ∥ `IDEA-20260806-a3ef00`, and **also** `IDEA-20260806-62ba9d` (undeclared: 62ba9d is a *reduction resource ledger* and S1-10 measures the Type⟶Marked reduction cost — different reduction pair, same accounting move) ·
`S2-1`, `S2-6` ∥ `B2-4` (O9 / O2) · `S2-3` ∥ `B2-9` · `S2-4` ∥ `IDEA-20260806-9c2f80` · `S2-7` ∥ `B1-5`→`C2-9` · `S2-10` ∥ `B2-10` ·
`S3-1` ∥ `IDEA-20260805-244f78` · `S3-2` ∥ `IDEA-20260805-2a669e` · `S3-3` ∥ `IDEA-20260801-020` ·
`S3-4` ∥ `IDEA-20260805-c4ae3d` (marginal vs conditional — a clean, real distinction) · `S3-6` ∥ `B3-2` ·
`Q1-4` ∥ `research/P13-HEUR-001` route (b) and `IDEA-20260806-b60c35` · `Q1-5` ∥ ANOM-1 / `EV-SSIQ-0fc992` ·
`Q1-6` ∥ lever L3 · `Q1-7`, `Q2-5` ∥ `C2-12` · `Q1-8` ∥ `C1-7` · `Q1-10` ∥ `C1-1` ·
`Q2-1` ∥ `C1-1` (asymmetric vs symmetric shrink — real) · `Q2-4` ∥ `C2-4` (bits per entry vs entries; the two compose) ·
`Q2-8` ∥ `C2-10` · `Q2-9` ∥ `IDEA-20260805-250e50` · `Q3-1` ∥ `C2-4` · `Q3-3` ∥ `C1-9` ·
`Q3-4` ∥ `IDEA-20260805-062bee` · `Q3-8` ∥ `C2-12` · `Q3-9` ∥ `C1-6` · `Q3-10` ∥ `C1-13`.

**No `duplicate_drop`.** Every entry examined has at least one falsifiable component
absent from its nearest prior neighbour. Four rows (Q3-6, Q3-7, S3-9, M2-3) survive only
after an explicitly labelled retrodiction/re-read component is stripped of evidence
strength, and three (Q2-3, S1-5, S1-2) survive only after being re-filed against the prior
art they failed to declare.

---

## 3. Systemic defect: phantom prior art

Several Q-slice entries cite 2026-08-05 **catalogue** entries as though they had produced
data. They have not: the prior catalogue mints no identifier, and its own SCREENING records
zero unanimous survivors, seven entries refuted by all three lenses and two contested.

- `Q2-6` known-answer gate: "at `n = 1` every cell must reproduce **C2-9's committed
  table** exactly". No such table exists.
- `Q1-2` minimal test: "recompute the integral with the **measured `q` from C1-1's
  design**". C1-1 has not run; there is no measured `q`.
- `Q1-10` minimal test: "shared with **C1-1's sample** so no new data is generated". Same.
- `Q2-8` prediction: classifies "**C2-10's collision profile**" and "**C2-5's survival
  probability**" as `ρ`-unstable. Neither has been measured.
- `Q1-9` deliverable: "emit the capped **L4-BATCH** removable fraction" — L4-BATCH's
  11.50–13.25 bits are a modelled bracket, not a measurement.

Each of these must be rewritten either as "produce X, then gate on it" or as an explicit
dependency on an unexecuted proposal. Left as written, they will read in the ledger as
gates against evidence that does not exist — which is the same failure mode as
rediscovering a committed result, with the sign flipped.

Two further honesty notes carried out of §0:

- `A1-1` / `A1-2` / `A1-3` must be re-scoped so that the in-session algebraic facts
  (255-class DDT/BCT/LAT collapse, boomerang uniformity 6 at `0xbc`/`0xbd`, `max|W| = 32`,
  MixColumns 1020/1020 and 6120/390150) are inputs with **no evidence strength**, not
  predictions. Their falsifiable content is the super-box enumeration (A1-1/A1-3, merged)
  and the 4-round boomerang measurement (A1-2).
- The `√(2 ln N)` best-of-`N` ceiling now appears in four places (`M1-2` basis seeds,
  `M2-1` key DFR, `M2-6` keygen seeds, prior `GOAL-MLKEM-005` ciphertexts). Derive it
  once, in one place, and let the three surviving measurements cite it.

---

## 4. Net distinct count

| | |
|---|---|
| entries generated | **120** |
| pairwise merges resolved (Table 1 rows ⚑1–⚑12; ⚑11+⚑12 is one three-way merge, −2) | **−12** |
| entries dropped as prior-art duplicates | **0** |
| **net distinct ideas** | **108** |

Of the 108: **12** carry an explicit "must be re-filed / re-scoped before costing" flag
(Q2-3, Q2-6, S1-5, S1-2, Q3-6, Q3-7, S3-9, M2-3, M1-8, M1-9, A1-1/A1-3 merged, A1-2), and
**5** carry a phantom-prior-art repair (Q1-2, Q1-9, Q1-10, Q2-6, Q2-8).

Coupled pairs that must be run in one batch: (Q1-2, Q1-8), (Q1-5, Q3-5), (S1-1, S1-3),
(M2-8, M3-8), (A1-3, A3-7), (M2-5, M2-10), (A2-6, A3-4), (Q2-6, S2-7), (M3-1, Q2-2).

Hard sequencing constraints: `Q2-8` before every SSQI toy statistic · `Q3-1` before `Q3-2`
· `M3-1` before `M3-4` · `M1-3` before `M3-5` · `A2-1` before `A2-2` · `A2-6` before `A2-8`
and `A2-10` · `A3-6` before `A3-5` · `S2-3` before `S2-9` · `S2-5` before `S2-7` ·
`S1-1` before `S1-7` · `S1-2` before `S1-8` · `S3-2` before `S3-7` · `Q1-1` before `Q1-4` ·
`Q1-3` before `Q1-9` · `M2-8` before `M3-7` · `M3-5` before any execution of `H-MLKEM-008`.
