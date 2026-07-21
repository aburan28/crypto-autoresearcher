# Idea Generation — Research Director — 2026-07-19 batch8 (report 16 / internal batch14)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Target:** a non-generic single-target prime-field ECDLP algorithm whose *complete* cost beats Pollard-rho `O(sqrt(n))`. Toy correctness, a new coordinate system, a relation certificate, faster preprocessing, or a solver swap alone is **not** a breakthrough.
**Scope:** generated toy curves, public benchmark instances, synthetic data only. No wallets, production keys, or unauthorized systems.

**Verdict up front:** the mechanism space is saturated. This is the **16th** idea report (internal batch14). Fifteen prior reports span ~60 distinct mechanism lanes and essentially every lower-bound / representation technology family with an obvious hook. Batch14's honest contribution is **not** a new crossing candidate — it is **two barrier technologies absent from all 15 prior reports**, each of which (i) attacks the surviving RT-1472 supply gate at a deeper root than any prior supply barrier and (ii) **prices an unpriced assumption** that two earlier candidates (batch5 `MATUNION-A2` matroid-union, batch11 `LORENTZIAN-LOGCONCAVE-C2`) silently relied on:

1. **Analytic-number-theory sieve inequalities + the Selberg parity problem** — the large sieve L² inequality, Selberg Λ² weights, and Bombieri–Vinogradov average equidistribution as *supply ceilings* on the two-large-prime pair support, culminating in the **parity-problem barrier**: no sieve of this family can detect the sign/parity structure a `delta>1/4` enrichment requires.
2. **Markov-chain mixing-time lower bounds** (conductance / spectral-independence failure) — the *mixing-time barrier*: the sampler-based enrichment route that `MATUNION-A2` and `LORENTZIAN-LOGCONCAVE-C2` both assume is fast is provably slow-mixing on a long-range-correlated relation graph.

Representation/high-risk arms (positive geometry, survey-propagation/1RSB, determinantal, prismatic, Katz–Sarnak) are included per the four-group requirement; each is a scoped negative or reject-tier with a near-certain named kill. **No rho crossing is claimed. RT-1472 and RT-1476 remain open.**

---

## 1. Inputs reviewed and machine-readable inventory

### 1.1 Files read this run

- `/Volumes/Volume/git/autolab/research_ledger.md` (2.95 MB; `ECFG-P` frontier `P1486`, RT/NR chain through the `P147x` two-large-prime gate block, `ECFG-RT-1472/1476/1485` verbatim).
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (IC-state frontier `P1509–P1513`).
- `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (transfer census — same-field isogeny / trace-zero / Weil-descent negatives).
- `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json` (core Semaev / index-calculus primary sources).
- All 15 prior `research/idea_generation_2026071[7-9]*.md` reports (anti-duplication catalogue), plus targeted `grep` of every batch14 candidate family name against those reports.

### 1.2 Inventory summary (families and outcomes)

- **Ledger IDs reviewed:** the full `ECFG-P` / `ECFG-NR` / `ECFG-RT` / `ECFG-MX` / `ISO-{NR,OBS,RT}-{ONK,IKD}` families in the two ledgers, plus report-proposed `ECFG-P` IDs `P1487–P1633` from reports 1–15. ID-family counts (main ledger): `P` 7565, `ECFG-P` 956, `PO` 583, `H` 552, `RT` 7, `MX` 1. IC-state frontier `P1509–P1513`. ID families covered: `ECFG-P`, `ECFG-NR`, `ECFG-RT`, `ECFG-MX`, `ISO-*-IKD/ONK`, `IDEA-0xx/1xx`, `RQ`, `H`, `EV`, `DEC`, `TASK`, `KN`, `PO`.
- **The only two live rho-crossing surfaces (both unrealized conditional theorems, quoted verbatim from the ledgers):**
  - **RT-1472** — an explicit hash-like two-large-prime graph at `B=n^{1/5}` has cost exponent `max(2ell, 1-ell, 1+1/5-2ell)`, minimized at `ell=1/3` giving exponent `2/3`; crossing rho requires pair-support **enrichment `delta>1/4`**. Every explicit-advice / character-bucket / CM-orbit enrichment attempt (`P1471–P1475`) measured `delta ≈ 0`.
  - **RT-1476** — a complete five-term implicit membership backend with **query exponent `alpha<3/2`** (setup `≤L^2`, random-like support, sparse full-rank relations) would conditionally beat rho; `m≤3` impossible, `m=4` needs `alpha<1`, `m=5` needs `alpha<3/2`. At `m=5, alpha=1`, relation and linear algebra are `q^{2/5}`, descent `q^{1/5}`.
- **IC-state frontier `P1509–P1513`:** P1509 exact local Hasse-jet source section (positive, verifier `Theta(r^3)`); P1510-R1 verified global marked-resultant compiler (`O(r^2)` state) but `Theta(r)`-row repeat is `Theta(r^3)=q^{3/5}`; P1511-R2 closed the product-circuit gcd/subresultant/Hasse semijoin (`r^3` input leaves); **P1512-R1 closed the source-labelled scalar-linear Chow/Tate/determinant atomizer at `Omega(r^5)`** via `deg(det M) ≤ dim`, leaving **only the target-specialized nonlinear-circuit exception**; **P1513 open** shared-bivariate common-norm (input circuit quadratic, both explicit norms cubic).
- **Negative-control territory (closed unless a candidate breaks the measured obstruction):** ordinary same-field isogeny invariants; scalar Weil pullback; explicit two-large-prime advice graphs; joint factor/large-prime Krylov; pair-residual character buckets; non-invariant CM endpoint decks; materialized serial-S3 backward states; dense composed resultants; source selectors without an honest hit generator; relation validity without ECDLP recovery; preprocessing wins whose offline/memory/advice/target-count cost loses to rho; **crystalline / Cartier–Manin / p-curvature / canonical-lift spectral invariants** (batch2 D2 theorem-grade order-only barrier — a class function of Frobenius, no per-target leakage for prime order); **Kloosterman / elliptic character-sum bias** (batch2 C3, Deligne equidistribution kill).

### 1.3 Anti-duplication catalogue (technology families already consumed, reports 1–15)

Tensor/border/slice/analytic rank; communication (Raz–McKenzie/GPW lifting, 5-party NOF/BNS, discrepancy/corruption, direct-sum info, sign-rank, `gamma_2`); VC/Sauer–Shelah; approximate degree/dual polynomial; probabilistic polynomials; entropy (Shearer); matroid union; Delsarte-LP; hypergraph containers; sum-product/additive energy; PFR; Kruskal–Katona shadow; Bollobás set-pairs; sunflower-free; p-adic (Ax–Katz, Adolphson–Sperber, Newton polygon, **Frobenius-slope of Semaev**); Lang–Weil/Deligne count; l-adic Betti/Milnor–Thom; Nullstellensatz (refutation + feasibility); Polynomial-Calculus/IPS; SOS/Lasserre/Positivstellensatz; Sherali–Adams; Cutting-Planes/Lovász–Schrijver; tau-conjecture/Shub–Smale; arithmetic-circuit LBs (shifted partials, Nisan nc-ABP, GCT occurrence, elusive functions, depth-reduction chasm, algebraic natural proofs, Valiant rigidity, Raz multilinear, block-Hankel); noncommutative rank/operator scaling; immanant interpolation; matchgate/Holant/Cohn–Umans; GKZ D-module; Newton–Okounkov; cluster algebras; quaternion/Brandt; LDC/LDLR; proof-space (red-blue) pebbling; cell-probe chronogram; quantum adversary/span program; fine-grained OV/3SUM/hyperclique; **Lorentzian/log-concave sampling (Anari–Oveis-Gharan)**; delta-matroid; Schubert structure constants; method of multiplicities; restriction/Kakeya; Coppersmith lattice; Barvinok interpolation; Moser entropy compression; dequantized sampling; persistent homology; RKHS/Peter–Weyl; free probability; Fourier–Mukai; arboreal Galois; Mahler/automatic; formal group/Coleman; **crystalline/Cartier–Manin/Monsky–Washnitzer/Kedlaya (closed order-only barrier)**; ACFA/difference; Dynamical Mordell–Lang; Picard–Fuchs; Ronkin/amoeba; elliptic nets; Croot–Sisask; Elekes–Szabó; sandpile/critical group; o-minimal Pila–Wilkie; matching-vector codes; Berezin–Pfaffian; Ore/skew resultant; sensitivity/certificate/block-sensitivity (Huang chain); Fulton–MacPherson excess/Segre; Borodin–Cook multi-output time-space; Arakelov height; Temperley–Lieb/Hecke; Håstad random restriction; spectrahedral shadow; extractor/condenser; **Kloosterman/character-sum bias oracle (closed, Deligne)**.

**Batch14 must be new against all of the above.** The organizing families below appear nowhere in it (`grep`-verified: `large sieve` 0, `Selberg sieve` 0, `circle method` 0, `parity problem` 0, `spectral independence` 0, `Glauber` 0, `survey propagation` 0, `positive geometry` 0, `amplituhedron` 0, `Helton-Vinnikov` 0, `prismatic` 0, `Katz-Sarnak` 0 prior hits).

---

## 2. Organizing theme for batch14

Every prior **supply** barrier for RT-1472 bounds the *size or count* of the honest pair support: Lang–Weil (point count of a variety), Shearer (entropy submodularity), Delsarte-LP (code size), matroid union / Bollobás / Kruskal–Katona (combinatorial extremal size), Ax–Katz (p-adic solution count), container (independent-set count). None asks the two questions batch14 asks:

1. **What can any *sieve* certify about the pair support?** The two-large-prime enrichment is exactly a sieve problem: count residue classes (pairs) surviving a set of congruence/inclusion conditions. Analytic number theory has *sharp* tools for this — the **large sieve L² inequality**, **Selberg Λ² upper-bound weights**, and **Bombieri–Vinogradov average equidistribution** — and one *fundamental obstruction*, the **Selberg parity problem**: a sieve cannot distinguish an even from an odd number of prime factors, i.e. it cannot see the *sign* structure. RT-1472 needs `delta>1/4` of *signed* enrichment. This is a structurally new supply ceiling and a structurally new barrier.
2. **Is the enrichment *sampler* actually fast?** Two prior candidates — `MATUNION-A2` (matroid-union basis sampling) and `LORENTZIAN-LOGCONCAVE-C2` (Anari–Oveis-Gharan log-concave sampler) — assumed that *if* the support has the right algebraic structure, a poly-time Markov chain produces enriched relations. Neither priced the **mixing time**. Batch14 imports **conductance / spectral-independence lower bounds**: if the relation Glauber chain has small conductance (long-range correlation), it mixes in `exp(Omega(L^c))` steps and the "certified enrichment" is never realized in sub-rho time. This is the first Markov-chain barrier in the program.

Both roots close the *same* gate (RT-1472) that has resisted 15 reports, and they close it against *entire method arms* rather than single decks. The representation and high-risk arms (positive geometry, survey propagation, determinantal, prismatic, Katz–Sarnak) are the four-group scaffolding; all are scoped negatives.

At least six candidates (A1, A2, A3, C1, D1, D2, D3) begin **outside** the ledger's algebraic-geometry / index-calculus vocabulary.

---

## 3. Candidates

Ledger IDs `ECFG-P1634 … ECFG-P1645`.

---

## Candidate: LARGE-SIEVE-SUPPLY  (ECFG-P1634)  ★ conservative winner

### One-sentence mechanism
Exploit the **large sieve L² inequality** as an exact upper ceiling on the two-large-prime pair-support enrichment `delta` — bounding, over all residue moduli simultaneously, how concentrated an honest pair support on `E(F_p)` can be, to decide whether `delta>1/4` is even arithmetically available (subproblem P = RT-1472 supply).

### Status
HYPOTHESIS (supply meter); barrier direction is D1 (asymptotic) and D3 (parity root).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Montgomery 1971 *The analytic principle of the large sieve*; Bombieri; Selberg) — no application to elliptic factor-base / two-large-prime supply found.

### Semantic fingerprint F(C)
- algebraic object: the multiset of two-large-prime pairs `{(F_i,F_j)}` whose partial sum lands in the residue-class deck, viewed as a subset of `Z/qZ` (equivalently residues over the large-prime moduli);
- available public operations: count pairs in arithmetic progressions / residue classes; take Fourier/character transforms over the moduli;
- hidden structure exploited: whether the pair support is *more concentrated* in some residue classes than equidistribution allows (the enrichment `delta`);
- information discarded: the exact group-law structure of each pair (only its residue footprint is retained);
- information retained: residue-class occupancy across all moduli up to `Q`;
- relation-generation primitive: n/a (supply meter — feeds the P1471–P1475 collectors);
- compression primitive: the large-sieve "dual" bound `sum over moduli` of squared occupancy deviations;
- rank mechanism: n/a;
- descent mechanism: n/a;
- dominant cost exponent: the certified `delta` ceiling from `Delta = Q^2 + N` (large-sieve constant) vs `Theta(L^2)` support.

### Nearest ledger entries
1. **DELSARTE-LP-A2 (batch8, P156x)** — coding LP supply ceiling on the two-large-prime *code*. Distinction: Delsarte-LP optimizes a *single* linear program over one code's distance distribution; the large sieve is an **L² inequality over a whole family of moduli at once** (`sum_q sum_a |S(q,a) - mean|^2 ≤ (N+Q^2)|coeffs|^2`). A support can pass every single-modulus LP and still be forced to equidistribute by the joint large-sieve bound.
2. **SHEARER-D3 (batch8)** — entropy submodularity. Distinction: Shearer bounds support *size* by marginal entropies; large sieve bounds support *concentration* by residue-class variance — a different functional (variance vs entropy).
3. **LANGWEIL-SUPPLY-D2 (batch6)** — Deligne/Lang–Weil point count. Distinction: Lang–Weil counts `F_p`-points of one variety; large sieve bounds occupancy deviation across `Q` residue systems — a dual/analytic bound, not a geometric count.
4. **CONTAINER-CEILING-A3 (batch9)** — hypergraph container independent-set count. Distinction: containers bound the *number* of sparse configurations; large sieve bounds their *arithmetic concentration*.
5. **ENERGY-D1 (batch3)** — additive-energy relation-supply ceiling. Distinction: additive energy is a single fourth-moment count; the large sieve is a second-moment inequality quantified over all moduli — incomparable functionals.

### Nearest literature
- Montgomery, *The analytic principle of the large sieve* (Bull. AMS 1978): `sum_{q≤Q} sum_{a mod q}^* |S(a/q)|^2 ≤ (N + Q^2) sum |a_n|^2`.
- Bombieri, *Le grand crible dans la théorie analytique des nombres* (1974). Selberg, *Collected Papers* (large sieve chapter).
- Claim / assumption / gap: the classical large sieve is stated for integer sequences over `Z`; the elliptic instantiation must map the pair support onto the residue systems of the large-prime moduli and verify the L² inequality transfers with the same constant `N+Q^2`. Whether the *elliptic* pair support saturates or falls short of the large-sieve ceiling is the open measurement.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck as in `P1471–P1475`, `B=n^{1/5}`, large primes `L=q^{1/5}`. Excluded: supersingular, anomalous, low-embedding-degree, CM curves with unusually structured residue footprints (there the sieve ceiling may be non-generic — flag separately).

### Full algorithmic path (supply-meter form)
1. **Factor base:** the `P1471` explicit two-large-prime deck of `Theta(L^2)` candidate pairs.
2. **Relation generation:** n/a — this is a supply ceiling, not a generator; its output feeds the `P1473` costed preflight.
3. **Witness extraction & verification:** n/a.
4. **Relation probability:** the large-sieve bound converts to a maximum enrichment `delta_max` = certified excess occupancy over equidistribution.
5. **Matrix:** n/a.
6. **Factor-log calibration:** n/a.
7. **Descent:** n/a.
8. **Offline/online:** entirely offline — a one-time arithmetic ceiling on the deck.
9. **Memory/parallelism:** `O(Q)` residue counters; embarrassingly parallel over moduli.

**INCOMPLETE on stages 2–7 by design** (a supply ceiling, complete for the RT-1472 supply question, INCOMPLETE for descent).

### Cost model
Outputs a `delta` ceiling, not a backend. Large-sieve inequality with `N=Theta(L^2)` support and moduli up to `Q=Theta(L)` gives deviation bound `≤ (L^2 + L^2)·(mean)`, i.e. occupancy deviations `O(sqrt(N+Q^2)) = O(L)` against a mean of `Theta(L^2/L)=Theta(L)` per class — so relative enrichment `delta = O(1/sqrt(L)) → 0`. Compare: RT-1472 needs `delta>1/4` to beat exponent `2/3`; rho `q^{1/2}`.

### Why the existing negative results do not already kill it
`P1471–P1475` measured `delta≈0` on *specific* explicit decks (character buckets, CM orbits, hash). The large sieve is the first tool that bounds `delta` **uniformly over all residue-structured decks at once**, converting per-deck negatives into a family-wide ceiling. The new operation is the **joint L² inequality over the modulus family**, absent from every prior single-place supply meter.

### Likely fatal obstruction
The large-sieve constant `N+Q^2` is *tight* only when the sequence is genuinely equidistributed; for the elliptic support the ceiling may be *loose* (over-estimate `delta_max`), giving an inconclusive upper bound rather than a barrier — precisely the failure mode of `KRUSKAL-KATONA-SHADOW-A1` (batch12). Then it neither crosses nor closes.

### Minimal falsifying experiment
Toy sizes `L∈{8,16,32}` (three), ordinary prime-order `E/F_p` at `q≈L^3`; per size compute the exact residue-class occupancy of the true two-large-prime deck across moduli up to `Q=L`, evaluate the large-sieve L² deviation, and extract measured `delta`. **Positive control** = a synthetically enriched deck engineered with `delta=1/2` (must show large L² deviation). **Negative control** = the equidistributed hash deck (must show `delta≈0`). Randomized curve seeds `×5`; ordinary prime-order controls throughout.

### Quantitative promotion gate
Require measured `delta > 1/4` with an **increasing** trend across the three sizes and leave-one-out min `> 1/4`; otherwise the run is a **barrier** (`delta_max ≤ 1/4` unconditionally over the residue family = D1). Correctness of the occupancy count alone is *not* the gate.

### Proof track
Theorem: for the honest elliptic two-large-prime support the large-sieve inequality yields `delta_max = O(L^{-1/2})`, hence `delta ≤ 1/4` for all `L ≥ L_0` (this is D1).

### Disproof track
Exhibit an ordinary prime-order curve whose pair support saturates a residue class with `delta>1/4` surviving the large-sieve bound — a single toy measurement of `delta>1/4` with increasing trend narrows the barrier.

### Reproduction artifact
Contract `experiment_contract_p1634_large_sieve_supply_ceiling.md`; impl `tasks/ecdlp_index_calculus/p1634_large_sieve_supply.py`; result `p1634_large_sieve_supply.json`; audit `p1634_audit.py`; ledger `ECFG-P1634`.

---

## Candidate: SELBERG-LAMBDA-CEILING  (ECFG-P1635)

### One-sentence mechanism
Exploit **Selberg's Λ² upper-bound sieve** weights on the two-large-prime pair support to get a self-optimizing `delta`-ceiling that is tighter than the single-modulus Delsarte-LP.

### Status
HYPOTHESIS (supply meter; asymptotic partner D3 parity barrier).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Selberg 1947 upper-bound sieve; Halberstam–Richert *Sieve Methods*). Distinct from DELSARTE-LP-A2 (batch8) and LARGE-SIEVE-SUPPLY-A1 (this batch).

### Semantic fingerprint F(C)
object: pair support as a sifted set; operations: apply divisor-supported weights `(sum_{d|n} lambda_d)^2 ≥ [n survives]`; hidden structure: the optimal quadratic-form minimum over divisor weights; discarded: exact residues, only divisibility retained; retained: divisor-closed weight profile; relation primitive: n/a; compression: the Selberg quadratic-form minimum `1/sum 1/g(d)`; rank: n/a; descent: n/a; cost exponent: `delta`-ceiling from the sieve dimension `kappa`.

### Nearest ledger entries
LARGE-SIEVE-SUPPLY-A1 (this batch — L² Fourier vs Λ² divisor optimization); DELSARTE-LP-A2 (batch8 — code LP vs Selberg quadratic form); CONTAINER-CEILING-A3 (batch9); MATUNION-A2 (batch5); SHEARER-D3 (batch8). Distinction: the Selberg sieve is a **quadratic-programming optimum over divisor-supported weights**, a different optimization object from the large-sieve L² inequality, the coding LP, the container count, matroid independence, or entropy.

### Nearest literature
Selberg, *On an elementary method in the theory of primes* (1947); Halberstam–Richert, *Sieve Methods* (1974), Ch. 3–5. Gap: no elliptic pair-support instantiation; the effective sieve dimension `kappa` of the elliptic support is unmeasured.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck.

### Full algorithmic path (supply-meter form)
1. factor base = `P1471` deck; 2. set up the Selberg Λ² weights over large-prime divisors; 3. solve the quadratic-form minimum for the sifted-set upper bound; 4. convert to `delta_max`; 5–9 supply-meter only (**INCOMPLETE for descent by design**).

### Cost model
Outputs `delta_max = O((log L)^{kappa}/L^{...})`; the Selberg dimension `kappa` of the elliptic support governs sharpness. Compare RT-1472 threshold `delta>1/4`.

### Why the existing negative results do not already kill it
Delsarte-LP is a single-code bound; the Selberg sieve optimizes divisor weights that see multiplicative structure across all large primes — a strictly different (and classically sharper for sieve problems) optimum.

### Likely fatal obstruction
The Selberg **parity problem** (D3): the Λ² sieve cannot break sign parity, so its `delta` ceiling is blind to exactly the signed enrichment RT-1472 needs — the bound is honest but cannot certify `delta>1/4` even if it existed, and cannot rule it out below the parity floor ⇒ inconclusive at the boundary.

### Minimal falsifying experiment
`L∈{8,16,32}`; compute the Selberg quadratic-form minimum on true vs random decks; positive control = a divisor-structured enriched deck; negative control = equidistributed hash deck; `×5` seeds; report measured sieve dimension `kappa`.

### Quantitative promotion gate
`delta>1/4` certified with increasing trend, else barrier `delta ≤ 1/4` modulo the parity floor.

### Proof track
Selberg upper bound `delta_max ≤ 1/4` for the elliptic support at sieve dimension `kappa`.

### Disproof track
A deck whose divisor structure produces `delta>1/4` past the parity floor.

### Reproduction artifact
`experiment_contract_p1635_selberg_lambda_ceiling.md`; `p1635_selberg_lambda.py`; `p1635_selberg_lambda.json`; `p1635_audit.py`; `ECFG-P1635`.

---

## Candidate: BOMBIERI-VINOGRADOV-AVERAGE  (ECFG-P1636)

### One-sentence mechanism
Exploit a **Bombieri–Vinogradov-type average-over-moduli equidistribution** statement to measure whether, *on average over the large-prime moduli*, the pair support enriches — the "average GRH" flavor of the RT-1472 supply question.

### Status
HYPOTHESIS (supply meter).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Bombieri 1965; Vinogradov 1965; Bombieri–Friedlander–Iwaniec). Distinct from all single-place meters and from A1/A2 (which are worst-case-over-moduli, not average).

### Semantic fingerprint F(C)
object: pair-support occupancy error `E(q,a)` per modulus; operations: average `sum_{q≤Q} max_a |E(q,a)|`; hidden structure: whether occupancy errors cancel on average (BV) or concentrate; discarded: worst single modulus; retained: the modulus-averaged error; relation primitive: n/a; compression: BV bound `≪ N/(log N)^A`; rank: n/a; descent: n/a; cost exponent: average `delta`.

### Nearest ledger entries
LARGE-SIEVE-SUPPLY-A1 (this batch, worst-case L² vs average error); SELBERG-LAMBDA-CEILING-A2 (this batch); EXPLICIT-FORMULA-C3 (batch6, single Weil density); ADOLPHSPERBER-A2 (batch7, single p-adic slope); LANGWEIL-SUPPLY-D2 (batch6). Distinction: BV is an **average-over-moduli** statement (using the large sieve as its engine but delivering a mean-error bound), distinct from every worst-case or single-place meter.

### Nearest literature
Bombieri, *On the large sieve* (1965); Bombieri–Friedlander–Iwaniec, *Primes in arithmetic progressions to large moduli* (1986). Gap: no elliptic-support BV analog; whether occupancy errors average out for the elliptic pair support is open.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck.

### Full algorithmic path (supply-meter form)
1. factor base = `P1471` deck; 2. compute per-modulus occupancy error; 3. average over moduli up to `Q=L^{1/2}` (BV range); 4. extract average `delta`; 5–9 supply-meter only (**INCOMPLETE for descent by design**).

### Cost model
Average `delta` from BV error `≪ N/(log N)^A`; average enrichment `→0`. Compare RT-1472 `delta>1/4`.

### Why the existing negative results do not already kill it
No prior meter averages over the modulus family; a support could enrich at one modulus (passing/failing a single-place meter) yet vanish on average (BV) — the average is the honest input to an *amortized-over-moduli* collector, which no prior candidate priced.

### Likely fatal obstruction
BV forces the average error small, so average `delta→0`; and a *single* enriched modulus (if it existed) is exactly a `P1475` character-bucket, already measured `delta≈0`. Near-certain reproduces the P1475 negative.

### Minimal falsifying experiment
`L∈{8,16,32}`; compute modulus-averaged occupancy error on true vs random decks; positive control = a single-modulus enriched deck; negative control = hash deck; `×5` seeds.

### Quantitative promotion gate
average `delta>1/4` with increasing trend, else barrier.

### Proof track
BV analog `⇒` average `delta = O((log L)^{-A})`.

### Disproof track
A deck with average `delta>1/4`.

### Reproduction artifact
`experiment_contract_p1636_bombieri_vinogradov_average.md`; `p1636_bv_average.py`; `p1636_bv_average.json`; `p1636_audit.py`; `ECFG-P1636`.

---

## Candidate: POSITIVE-GEOMETRY-CANONICAL-FORM  (ECFG-P1637)  ★ representation winner

### One-sentence mechanism
Represent the set of `Theta(r^5)` five-point membership cells as the boundary strata of a **positive geometry**, whose single **canonical form** (a rational differential form with prescribed poles on exactly the relation loci) is a *non-materializing* compact object — testing whether the amplituhedron-style collapse of a huge cell sum into one canonical form gives a sub-`L^{1.5}` membership/relation generator that the ordinary `Omega(r^5)` cycle provably cannot.

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (documented search: Arkani-Hamed–Bai–Lam *Positive Geometries and Canonical Forms* 2017; Arkani-Hamed–Trnka amplituhedron 2013; Lam surveys — **no discrete-log / Semaev / index-calculus application found**). LEDGER-NEW.

### Semantic fingerprint F(C)
- algebraic object: a candidate positive geometry `(X, X_{≥0})` on (a compactification of) `E^5` whose positive part's boundary strata are the five signed diagonal-sum relation loci, and its canonical form `Omega(X_{≥0})`;
- available public operations: residue/triangulation recursion on the canonical form (the defining property `Res Omega = Omega of the boundary`);
- hidden structure exploited: **triangulation independence** — the canonical form is independent of how the region is triangulated, so a sum over `Theta(r^5)` cells equals one form of potentially far smaller description;
- information discarded: the interior of each cell (only the pole structure on relation loci is retained);
- information retained: the residue/pole data = the relation witnesses;
- relation-generation primitive: read source rows off the poles of `Omega` (each simple pole = one relation locus);
- compression primitive: the canonical form's description length vs `binom(2r+4,5)` cells;
- rank mechanism: n/a (form-degree, not matrix rank);
- descent mechanism: residue of `Omega` along the target-point locus;
- dominant cost exponent: description complexity of `Omega` in `r`.

### Nearest ledger entries
1. **SEGRE-EXCESS-B1 (batch13, P1625)** — Fulton excess/Segre refined intersection. **Exact distinction:** Segre computes the *excess intersection class* (a Chow-group element) via blow-up; the canonical form is a *differential form* whose poles encode the boundary — an intersection-theory object vs a residue/pole object. Segre measures excess multiplicity; the canonical form measures triangulation-invariant pole structure. Different invariants (Chow class vs meromorphic form).
2. **GKZ-DMODULE-B2 (batch8)** — holonomic rank = normalized volume. Distinction: GKZ's `D`-module counts solution branches by mixed volume of the Newton polytope; the canonical form is the *unique* top form with the boundary residue property — not a `D`-module solution count.
3. **NEWTON-OKOUNKOV-B3 (batch9)** — graded valuation filtration. Distinction: Okounkov bodies filter sections; positive geometry organizes *boundary strata + their residues*. Incomparable.
4. **P1512-R1** (scalar-linear Chow atomizer `Omega(r^5)`). Distinction: P1512-R1 bounds the *ordinary* determinant-of-cohomology cycle by `deg(det M) ≤ dim`; the canonical form is **not a determinant** — it is a triangulation-invariant residue form, precisely the "nonlinear-circuit exception" P1512-R1 leaves open, because its description complexity is governed by the number of *facets*, not by `dim M`.
5. **IMMANANT-INTERPOLATION-B2 (batch12)** — character-weighted determinant. Distinction: immanants interpolate `det↔perm`; the canonical form is not a matrix functional at all.

### Nearest literature
- Arkani-Hamed, Bai, Lam, *Positive Geometries and Canonical Forms* (JHEP 2017) — canonical form, triangulation independence, residue recursion.
- Arkani-Hamed, Trnka, *The Amplituhedron* (JHEP 2014) — a sum over many BCFW cells equals one canonical form.
- Lam, *An invitation to positive geometries* (2022).
- Claim / assumption / gap: positive geometries live over **`R` with a positivity structure** (the "positive part" `X_{≥0}`); a finite field `F_p` has **no order/positivity**, so whether any `F_p`-rational analog of the canonical form and its residue recursion exists is the crux. Recent "binary geometries" / p-adic amplitude work is suggestive but unproven for this locus — hence CONJECTURE, not HYPOTHESIS.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`, `E^5` with the five signed diagonal-sum conditions; exclude curves where the relation loci fail to form a normal-crossings boundary (there the residue recursion breaks — flag separately).

### Full algorithmic path
1. **Factor base:** `P1473` deck of `L` source x-coordinates.
2. **Relation generation:** construct the candidate positive geometry on `E^5`; compute its canonical form `Omega` via residue recursion (never enumerating all `binom(2r+4,5)` cells); read relation loci off the simple poles.
3. **Witness extraction & verification:** each pole names a five-source relation; re-verify with the P1510-R1 marked-resultant compiler (independent, exact).
4. **Relation probability:** number of `F_p`-rational poles ≈ `min(1, L^5/q)` in the RT-1476 model.
5. **Matrix:** `Theta(L)` sparse rows; LA `L^2`.
6. **Factor-log calibration:** standard.
7. **Descent:** residue of `Omega` along the target locus.
8. **Offline/online:** the geometry and `Omega`'s structure are target-blind (offline); per-target residue is online.
9. **Memory/parallelism:** `Omega` stored by its pole data (`O(#facets)`); parallel over residues.

No stage missing (contingent on the `F_p` canonical form existing — else INCOMPLETE at stage 2).

### Cost model
Setup: residue recursion, `poly(r)` *if* the `F_p` canonical form exists with `O(r^c)` poles. Per-target: residue extraction `= (#poles)·polylog`. **If** `#poles = O(r^{1.5-eps})` the RT-1476 row query exponent falls below `3/2` — a crossing. Compare: ordinary cycle `binom(2r+4,5)=Theta(r^5)` (P1512-R1 floor), rho `q^{1/2}=r^{2.5}`, IC baseline `q^{3/5}=r^3`.

### Why the existing negative results do not already kill it
P1512-R1 bounds the *determinant-of-cohomology* class by `dim M`; the canonical form is a triangulation-invariant residue object whose complexity is `#facets`, not `dim M`, and P1512's proof never constructs it. The new operation is **residue recursion on a boundary stratification** — absent from every prior atomizer (which all build a determinant, resultant, or intersection product).

### Likely fatal obstruction
**No `F_p` positivity:** positive geometries are defined by a positive part `X_{≥0}`, which requires an ordered field. Over `F_p` there is no canonical form in the Arkani-Hamed–Bai–Lam sense; any naive residue recursion on the relation loci is just the ordinary `Omega(r^5)` sum in disguise, reproducing the P1512-R1 floor. Near-certain kill — but it kills a **named, never-tested representation** by exhibiting the missing structure.

### Minimal falsifying experiment
Toy sizes `r∈{4,6,8}` (three), ordinary prime-order `q≈r^5`; attempt to construct an `F_p`-rational canonical form for the five-condition boundary and count its poles; **positive control** = a genuine positive geometry over `Q` (a cyclic polytope / associahedron) whose canonical form has `O(r)` poles (must compress); **negative control** = a random five-condition system with no boundary structure (must give `Theta(r^5)` poles); randomized seeds `×5`; ordinary prime-order controls throughout.

### Quantitative promotion gate
Require an `F_p`-rational canonical form with `#poles = O(r^{beta})`, `beta<1.5`, and a **decreasing** `log_r(#poles)` trend; LOO max `<1.5`. Existence of a residue recursion alone is *not* the gate — the pole count exponent must fall below `3/2`.

### Proof track
Theorem: the five signed diagonal-sum loci on `E^5` bound an `F_p`-rational positive geometry whose canonical form has `O(r^{c})` poles, `c<1.5`. (This would be the representation breakthrough — and would first require an `F_p` theory of canonical forms.)

### Disproof track
Prove no `F_p`-rational canonical form exists for a non-orderable field, or measure `#poles=Theta(r^5)` on `r=4,6,8` (expected). A single such measurement kills it.

### Reproduction artifact
Contract `experiment_contract_p1637_positive_geometry_canonical_form.md`; impl `tasks/ecdlp_index_calculus/p1637_positive_geometry.py`; result `p1637_positive_geometry.json`; audit `p1637_audit.py`; ledger `ECFG-P1637`.

---

## Candidate: HELTON-VINNIKOV-DETERMINANTAL  (ECFG-P1638)

### One-sentence mechanism
Represent the five-point membership hypersurface as an **exact `F_p` determinantal (definite/hyperbolic) linear-matrix representation** `f = det(A_0 + sum x_i A_i)`, testing whether a definite representation has size below the polynomial degree.

### Status
CONJECTURE. **Reject-tier risk** (size = degree ⇒ reproduces P1512-R1 floor).

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Helton–Vinnikov 2007 determinantal representations; hyperbolic polynomials / Lax conjecture). Distinct from SPECTRAHEDRAL-SHADOW-C2 (batch13 — real SDP, no `F_p`) and LORENTZIAN-LOGCONCAVE-C2 (batch11 — log-concave cone).

### Semantic fingerprint F(C)
object: membership polynomial as `det` of a linear pencil; operations: pencil arithmetic over `F_p`; hidden structure: definite/hyperbolic determinantal representability; discarded: nothing (exact over `F_p`); retained: the pencil; relation primitive: pencil eigen-locus = relation; compression: pencil size `s`; rank: pencil rank; descent: target pencil; cost exponent: `s = deg f`.

### Nearest ledger entries
SPECTRAHEDRAL-SHADOW-C2 (batch13); LORENTZIAN-LOGCONCAVE-C2 (batch11); P1512-R1 (`deg(det M)≤dim`); IMMANANT-INTERPOLATION-B2 (batch12); NONCOMMUTATIVE-RANK-OPSCALING-B2 (batch11). Distinction: a *definite hyperbolic* determinantal representation over `F_p` (exact, unlike the real SDP shadow) — but its size `s` equals `deg f`, colliding head-on with P1512-R1.

### Nearest literature
Helton–Vinnikov, *Linear matrix inequality representation of sets* (CPAM 2007); Vinnikov, *LMI representations of plane curves* (2012). Gap: over `F_p` there is no hyperbolicity cone; whether a *smaller-than-degree* determinantal representation exists is exactly the P1512-blocked question.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`.

### Full algorithmic path
1. factor base = `P1473` deck; 2. seek a size-`s` `F_p` determinantal representation of the membership polynomial; 3–9 contingent: if `s<deg`, extract relations from the pencil eigen-locus; **reject-risk** because `s ≥ deg` for a single determinant.

### Cost model
If `s = o(deg)`, membership query drops; realistic `s = deg = Theta(L)` ⇒ reproduces P1512-R1 `Omega(r^5)`. Compare rho `q^{1/2}`.

### Why the existing negative results do not already kill it
Spectrahedral shadow needs `R`; a determinantal representation is exact over `F_p`. The (thin) hope is a *sum-of-few-determinants* representation smaller than one degree-`s` determinant.

### Likely fatal obstruction
`deg(det(pencil)) = size(pencil)`, so a single determinantal representation cannot beat degree — exactly P1512-R1. Reject-tier unless a genuinely sub-degree *sum-of-determinants* (nonlinear-circuit) form is exhibited, which returns to the open exception without new leverage.

### Minimal falsifying experiment
`L∈{8,16,32}`; search for `F_p` determinantal representations of size `<deg`; positive control = a curve/plane sextic with a known small representation; negative control = a generic high-degree form; `×5` seeds.

### Quantitative promotion gate
`s = O(L^{beta})`, `beta<1.5`, decreasing trend — else reject.

### Proof track
Sub-degree definite representation exists over `F_p`.

### Disproof track
`s ≥ deg` (expected, = P1512-R1).

### Reproduction artifact
`experiment_contract_p1638_helton_vinnikov_determinantal.md`; `p1638_helton_vinnikov.py`; `p1638_helton_vinnikov.json`; `p1638_audit.py`; `ECFG-P1638`.

---

## Candidate: PRISMATIC-DELTA-RING  (ECFG-P1639)

### One-sentence mechanism
Represent the arithmetic of `x([k]P)` (and the membership recurrence) via **prismatic cohomology / `delta`-ring** structure (Bhatt–Scholze), whose Frobenius-lift `delta`-operator interpolates crystalline, de Rham, and étale cohomology, seeking a `delta`-structured non-materializing recurrence.

### Status
CONJECTURE. **Reject-tier risk** (collapses to the closed crystalline order-only barrier).

### Novelty classification
LEDGER-NEW as a *named technology* (prismatic cohomology, 2019+, absent from all prior reports); but the mechanism is shadowed by a **closed** lane (batch2 D2 crystalline order-only barrier). Honest label: **NOVELTY-UNVERIFIED / likely-dominated**.

### Semantic fingerprint F(C)
object: the prismatic cohomology `H^*_{prism}(E/A)` over a prism `(A,I)` with its `delta`-ring Frobenius lift; operations: `delta`-operator / Frobenius-lift arithmetic; hidden structure: the `delta`-ring lift of the `[k]`-recurrence; discarded: the ambient degree (replaced by `delta`-weight); retained: prismatic Frobenius data; relation primitive: `delta`-structured recurrence for `x([k]P)`; compression: `delta`-recurrence length; rank: prismatic Frobenius rank; descent: specialize at the target; cost exponent: `delta`-recurrence complexity in `L`.

### Nearest ledger entries
**batch2 D2 crystalline/Cartier–Manin order-only barrier (CLOSED)** — prismatic specializes to crystalline at the crystalline prism, inheriting the "class function of Frobenius ⇒ order-only, no per-target leakage for prime `n`" theorem; FORMALGROUP-B1 (batch8, Coleman log — a de Rham specialization); MAHLER-B1 (batch5, automatic recurrence); ELLNET-C2 (batch7, elliptic-net recurrence); PICARDFUCHS-B2 (batch6, Gauss–Manin). Distinction: prismatic is the universal deformation of all p-adic cohomologies; but every specialization relevant to `E/F_p` lands in an already-closed lane.

### Nearest literature
Bhatt–Scholze, *Prisms and prismatic cohomology* (Annals 2022); Bhatt–Lurie, *Absolute prismatic cohomology* (2022). Gap: prismatic cohomology is a *point-counting / comparison* technology (like crystalline via Kedlaya); no per-target DLP-leakage route is known, and the crystalline specialization is provably order-only here.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5`, ordinary (so the prism has the Serre–Tate canonical lift).

### Full algorithmic path
1. factor base = `P1473` deck; 2. build the prismatic `delta`-recurrence for `x([k]P)`; 3. **reject-risk** — the recurrence's per-target content collapses to Frobenius-class (order-only) data by batch2 D2; 4–9 contingent.

### Cost model
If a `delta`-recurrence of length `o(ord P)` carried target-specific data, membership could drop; realistic: crystalline specialization ⇒ order-only ⇒ no leakage ⇒ reproduces the closed barrier.

### Why the existing negative results do not already kill it
Prismatic is strictly richer than crystalline (it remembers the Hodge–Tate and étale specializations too); the *only* untested hope is that the mixed prismatic data escapes the crystalline class function — almost certainly it does not for prime-order `n`.

### Likely fatal obstruction
batch2 D2: any Frobenius-class p-adic invariant of `E/F_p` is order-only for prime `n`. Prismatic cohomology's `E/F_p` fiber is such an invariant ⇒ reject-tier.

### Minimal falsifying experiment
`L∈{8,16,32}`; compute the prismatic `delta`-recurrence and test for per-target (non-order) leakage on ordinary prime-order curves; positive control = a composite-order toy with known leakage; negative control = prime-order (must show order-only); `×5` seeds.

### Quantitative promotion gate
Measured per-target leakage exponent giving `alpha<3/2` — else reject (= batch2 D2).

### Proof track
Prismatic data carries per-target DLP leakage escaping the Frobenius class function (would contradict batch2 D2 — very unlikely).

### Disproof track
Order-only collapse on prime-order fixtures (expected).

### Reproduction artifact
`experiment_contract_p1639_prismatic_delta_ring.md`; `p1639_prismatic_delta.py`; `p1639_prismatic_delta.json`; `p1639_audit.py`; `ECFG-P1639`.

---

## Candidate: SURVEY-PROPAGATION-RSB  (ECFG-P1640)  ★ high-risk winner

### One-sentence mechanism
Treat five-point relation-finding as a random constraint-satisfaction problem and run **survey propagation / 1-step replica-symmetry-breaking (1RSB) cavity** analysis to locate enriched relation *clusters* below the equidistribution barrier, exploiting the statistical-physics geometry of the solution space (subproblem P = RT-1472 δ / RT-1476 relation supply).

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (documented search: Mézard–Parisi–Zecchina *Analytic and Algorithmic Solution of Random Satisfiability* 2002; Mézard–Montanari *Information, Physics, and Computation* 2009 — **no application to elliptic-curve index calculus / Semaev relation CSP found**). LEDGER-NEW.

### Semantic fingerprint F(C)
- algebraic object: the factor graph of the five-point relation CSP — variables = source-presence indicators, constraints = the `Theta(L)` membership equations;
- available public operations: message passing (belief/survey propagation) on the factor graph;
- hidden structure exploited: **clustering of the solution space** — whether enriched relations concentrate in a few 1RSB clusters (a state a uniform sampler misses);
- information discarded: the exact field values (only the constraint-graph combinatorics retained);
- information retained: cluster membership marginals (surveys);
- relation-generation primitive: decimate variables by their surveys to fix a cluster, then read off relations;
- compression primitive: the survey fixed point (a distribution over messages) vs enumerating relations;
- rank mechanism: n/a;
- descent mechanism: add the target constraint to the factor graph and re-run SP;
- dominant cost exponent: SP convergence time × decimation depth in `L`.

### Nearest ledger entries
1. **CORRELATED-PEEL-A3 (batch4)** — Wormald differential-equation 2-core peeling of the sum graph. **Exact distinction:** peeling is a *degree-based* combinatorial process (remove low-degree vertices) analyzed by an ODE; survey propagation is a *cavity/message-passing* analysis of the *clustered* solution geometry (1RSB), a strictly richer statistical-physics object (peeling = replica-symmetric / BP regime; SP = 1RSB).
2. **LORENTZIAN-LOGCONCAVE-C2 (batch11)** — log-concave sampler. Distinction: Lorentzian sampling assumes a single well-connected (replica-symmetric) measure; SP explicitly targets the *broken* (clustered) phase where uniform sampling fails.
3. **MATUNION-A2 (batch5)** — matroid-union basis sampling. Distinction: matroid union is an algebraic-independence structure; SP is a probabilistic message-passing analysis of clustering — different objects.
4. **HDX-COBOUNDARY-A2 (batch6)** — cosystolic expansion of the relation complex. Distinction: HDX measures topological expansion; SP measures solution-space clustering — orthogonal.
5. **ENERGY-D1 (batch3)** — additive-energy supply ceiling. Distinction: energy is a moment count; SP is a cluster-geometry analysis.

### Nearest literature
- Mézard, Parisi, Zecchina, *Analytic and Algorithmic Solution of Random Satisfiability Problems* (Science 2002) — survey propagation.
- Mézard, Montanari, *Information, Physics, and Computation* (OUP 2009), Ch. 19–22 — 1RSB cavity, clustering, condensation.
- Krzakała et al., *Gibbs states and the set of solutions of random CSPs* (PNAS 2007) — the clustered phase.
- Claim / assumption / gap: SP is proven effective on **random, locally-tree-like** factor graphs with independent constraints. The elliptic membership CSP has *deterministic, algebraically-dependent* constraints (the group law couples all five points), so the cavity independence assumption is violated — whether SP even converges, let alone finds enriched clusters, is the open (high-risk) question.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^5` (for the m=5 relation CSP) and `q≈L^3` (for the two-large-prime pair CSP); **average-case over the relation ensemble** (stated explicitly — SP is an average-case tool).

### Full algorithmic path
1. **Factor base:** `P1473` deck of `L` sources.
2. **Relation generation:** build the relation factor graph; run survey propagation to a fixed point; decimate high-survey variables to enter a cluster; enumerate the cluster's relations.
3. **Witness extraction & verification:** each decimated assignment names a five-source relation; re-verify with P1510-R1 (independent, exact).
4. **Relation probability:** governed by the number/size of 1RSB clusters with `F_p`-rational solutions.
5. **Matrix:** `Theta(L)` sparse rows; LA `L^2`.
6. **Factor-log calibration:** standard on the cluster's relations.
7. **Descent:** add the target constraint, re-run SP.
8. **Offline/online:** the factor-graph structure is target-blind (offline); per-target SP is online.
9. **Memory/parallelism:** `O(#edges)` messages; parallel over factor-graph regions.

No stage missing (contingent on SP convergence — else INCOMPLETE at stage 2).

### Cost model
Per relation batch: `T_SP · D_decim` field evaluations, `T_SP` = SP convergence time, `D_decim` = decimation depth. **If** the elliptic CSP has a favorable 1RSB structure with `T_SP=polylog`, enriched clusters yield `delta>1/4` or `alpha<3/2` — a crossing. **Realistic:** the algebraically-dependent constraints make the factor graph far from locally-tree-like; SP either fails to converge or its surveys reproduce the uniform (equidistribution) marginals, giving `delta≈0` and no query win — the per-relation cost collapses to the P1511-R2 cubic floor. Compare rho `q^{1/2}`, IC baseline `q^{3/5}`.

### Why the existing negative results do not already kill it
Every prior supply/relation analysis is either worst-case (degree/rank/count) or replica-symmetric (peeling, log-concave sampling); none analyzes the **clustered (1RSB) phase**. The new operation — **survey propagation to find and decimate into a solution cluster** — is untried, and the clustered phase is genuinely where a uniform sampler and a moment count are both blind.

### Likely fatal obstruction
The elliptic membership constraints are **deterministic and fully coupled** (the group law is not a random sparse constraint); the cavity/1RSB formalism requires approximate conditional independence of distant variables, which fails, so SP converges to the trivial uniform fixed point (surveys = marginals = equidistribution) ⇒ no cluster enrichment ⇒ `delta≈0`. Near-certain kill.

### Minimal falsifying experiment
Toy sizes `L∈{8,16,32}` (three), ordinary prime-order `q≈L^5`; build the relation factor graph, run SP, measure convergence and the survey-vs-uniform marginal deviation; **positive control** = a synthetic random 5-XORSAT-like relation ensemble with a planted clustered phase (SP must find clusters); **negative control** = a genuinely equidistributed relation ensemble (SP must return uniform); randomized seeds `×5`; report the measured enrichment `delta` and convergence time.

### Quantitative promotion gate
Require (i) SP convergence with survey marginals deviating from uniform, yielding measured `delta>1/4` (or per-relation `alpha<3/2`), **and** (ii) a **strengthening** trend across the three sizes. SP convergence alone is *not* the gate; the enrichment exponent must cross.

### Proof track
Theorem: the elliptic five-point relation CSP has a 1RSB clustered phase with survey marginals bounded away from uniform by `>1/4`. (Would be a genuine statistical-physics-of-ECDLP result.)

### Disproof track
Prove the coupled algebraic constraints force SP to the uniform fixed point (surveys ≡ marginals) ⇒ no clustering. A single toy showing survey ≡ uniform across sizes disproves it.

### Reproduction artifact
Contract `experiment_contract_p1640_survey_propagation_rsb.md`; impl `tasks/ecdlp_index_calculus/p1640_survey_propagation.py`; result `p1640_survey_propagation.json`; audit `p1640_audit.py`; ledger `ECFG-P1640`.

---

## Candidate: SPECTRAL-INDEPENDENCE-SAMPLER  (ECFG-P1641)

### One-sentence mechanism
Use **spectral independence** (bounded pairwise-influence spectral radius, Anari–Liu–Oveis-Gharan) of the two-large-prime relation distribution to certify rapid Glauber mixing and sample enriched relations in poly time (subproblem P = RT-1472 δ).

### Status
HYPOTHESIS. **Demoted — ADJACENT to batch11 LORENTZIAN-LOGCONCAVE-C2** (same "poly-time sampler certifies enrichment" role); its real value is the *barrier* direction D2.

### Novelty classification
LEDGER-NEW as a *named technology* (spectral independence, 2020) but **LITERATURE-ADJACENT in mechanism** to LORENTZIAN-LOGCONCAVE-C2 (batch11) and MATUNION-A2 (batch5) — the sampler-certifies-enrichment role is consumed.

### Semantic fingerprint F(C)
object: the relation distribution `mu` on the pair support; operations: Glauber (Gibbs) single-site updates; hidden structure: the influence-matrix spectral radius; discarded: global algebraic structure; retained: pairwise correlations; relation primitive: MCMC-sampled relation; compression: mixing time; rank: influence-matrix eigenvalue; descent: condition on the target; cost exponent: mixing-time exponent.

### Nearest ledger entries
LORENTZIAN-LOGCONCAVE-C2 (batch11 — log-concave ⇒ mixing); MATUNION-A2 (batch5 — matroid basis sampling); HDX-COBOUNDARY-A2 (batch6 — spectral expansion); CORRELATED-PEEL-A3 (batch4); SHEARER-D3 (batch8). Distinction: spectral independence is a *strictly weaker sufficient condition* for mixing than log-concavity (it applies to non-log-concave `mu`), but the **role is identical** to LORENTZIAN-C2 — hence ADJACENT, not a winner.

### Nearest literature
Anari, Liu, Oveis-Gharan, *Spectral Independence in High-Dimensional Expanders and Applications to the Hardcore Model* (2020); Chen–Liu–Vigoda, *Rapid mixing via spectral independence* (2021). Gap: no elliptic instantiation; the influence matrix of the elliptic pair distribution is unmeasured.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck.

### Full algorithmic path
1. factor base = `P1471` deck; 2. define `mu` on the pair support; 3. estimate the influence-matrix spectral radius; 4. if `<1`, run Glauber to sample enriched relations; 5. `Theta(L)` rows, LA `L^2`; 6–9 standard. **Contingent on bounded spectral radius** — else the sampler is slow (= D2).

### Cost model
If spectrally independent, mixing time `L·polylog` ⇒ poly-time enrichment sampler; realistic: the elliptic pair distribution has long-range algebraic correlations ⇒ influence radius `≥1` ⇒ `exp(Omega(L^c))` mixing (= D2). Compare RT-1472 `delta>1/4`.

### Why the existing negative results do not already kill it
Log-concavity (batch11) is sufficient but not necessary for mixing; spectral independence covers non-log-concave measures the Lorentzian test rejected — a slightly wider sufficient condition.

### Likely fatal obstruction
Same as batch11 C2: the honest elliptic support is not nicely correlated; the influence matrix has spectral radius `≥1` (long-range dependence), so Glauber is slow-mixing and no enrichment is sampled — the mixing-time lower bound is exactly D2.

### Minimal falsifying experiment
`L∈{8,16,32}`; estimate the influence-matrix spectral radius and measure empirical Glauber mixing on true vs random decks; positive control = a spectrally-independent planted distribution; negative control = a long-range-correlated deck; `×5` seeds.

### Quantitative promotion gate
Bounded spectral radius `<1` with poly mixing **and** measured `delta>1/4` — else barrier (= D2).

### Proof track
Bounded influence spectral radius for the elliptic pair distribution.

### Disproof track
Spectral radius `≥1` (expected) ⇒ slow mixing (= D2).

### Reproduction artifact
`experiment_contract_p1641_spectral_independence_sampler.md`; `p1641_spectral_independence.py`; `p1641_spectral_independence.json`; `p1641_audit.py`; `ECFG-P1641`.

---

## Candidate: KATZ-SARNAK-SYMMETRY  (ECFG-P1642)

### One-sentence mechanism
Measure the **Katz–Sarnak random-matrix symmetry type** (low-lying-zero statistics) of the family of L-functions attached to the membership curves as a δ-bias detector for the two-large-prime support.

### Status
HYPOTHESIS. **Reject-tier risk** (Deligne equidistribution ⇒ no exploitable bias — same obstruction as the closed Kloosterman lane).

### Novelty classification
LEDGER-NEW as a *named technology* (Katz–Sarnak family symmetry) but the *obstruction* (Deligne/Sato–Tate equidistribution) is the **settled kill** shared with the closed character-sum lane (batch2 C3) and EXPLICIT-FORMULA-C3 (batch6).

### Semantic fingerprint F(C)
object: the family of L-functions / zeta functions of the membership curves; operations: compute low-lying-zero one-level density; hidden structure: monodromy symmetry type (U/O/Sp); discarded: individual curve arithmetic; retained: family-averaged zero statistics; relation primitive: n/a; compression: symmetry-type parameter; rank: n/a; descent: n/a; cost exponent: δ from any density bias.

### Nearest ledger entries
EXPLICIT-FORMULA-C3 (batch6 — single Weil explicit formula); LANGWEIL-SUPPLY-D2 (batch6); batch2 C3 (character-sum bias, CLOSED); ELL-ADIC-BETTI-MILNOR-THOM-C2 (batch12); ARAKELOV-HEIGHT-B2 (batch13). Distinction: Katz–Sarnak measures the *family* monodromy symmetry (a global average), distinct from a single explicit formula or point count — but subject to the same equidistribution kill.

### Nearest literature
Katz–Sarnak, *Random Matrices, Frobenius Eigenvalues, and Monodromy* (AMS 1999); Katz–Sarnak, *Zeroes of zeta functions and symmetry* (BAMS 1999). Gap: family symmetry gives *statistical* not *per-target* information; no DLP-leakage route.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, membership-curve family.

### Full algorithmic path
1. factor base = `P1471` deck; 2. compute low-lying-zero density of the membership-curve family; 3. test for symmetry-type bias; 4–9 **reject-risk** — symmetry is a family average, not a per-target δ.

### Cost model
If a symmetry bias produced δ, enrichment follows; realistic: equidistribution ⇒ symmetry type is the generic one ⇒ δ→0.

### Why the existing negative results do not already kill it
Katz–Sarnak family symmetry is a global statistic no single-place meter computes; the (thin) hope is a non-generic symmetry type carrying support bias.

### Likely fatal obstruction
Deligne equidistribution / generic big monodromy ⇒ generic symmetry type ⇒ no support bias ⇒ δ→0. Reject-tier (= closed character-sum obstruction).

### Minimal falsifying experiment
`L∈{8,16,32}`; compute low-lying-zero density on true vs random families; positive control = a family with engineered non-generic monodromy; negative control = generic family; `×5` seeds.

### Quantitative promotion gate
δ>1/4 from a symmetry bias — else reject.

### Proof track
Non-generic symmetry type with support bias `>1/4`.

### Disproof track
Generic symmetry (expected).

### Reproduction artifact
`experiment_contract_p1642_katz_sarnak_symmetry.md`; `p1642_katz_sarnak.py`; `p1642_katz_sarnak.json`; `p1642_audit.py`; `ECFG-P1642`.

---

## Candidate: LARGE-SIEVE-BARRIER  (ECFG-P1643)  ▲ barrier (RT-1472)

### One-sentence mechanism
Prove that the **large sieve L² inequality** forces the honest two-large-prime pair support to have enrichment `delta ≤ 1/4` unconditionally over the residue-structured family — closing RT-1472 for all AP/residue-structured advice.

### Status
HYPOTHESIS → target THEOREM (barrier). Asymptotic partner of A1.

### Novelty classification
LEDGER-NEW; the first **analytic-number-theory dual-inequality** barrier in the program. Distinct from LANGWEIL-SUPPLY-D2 (batch6, point count), SHEARER-D3 (batch8, entropy), AX-KATZ-BARRIER-D3 (batch9, p-adic congruence), CONTAINER-CEILING (batch9), MATUNION-INDEP-D2 (batch5).

### Semantic fingerprint F(C)
object: the pair-support occupancy vector across residue moduli; operations: the large-sieve L² bound `sum_{q≤Q} sum_a^* |S(a/q)|^2 ≤ (N+Q^2)||a||^2`; hidden structure: the maximal residue concentration compatible with the inequality; discarded: group law; retained: occupancy variance; relation primitive: n/a; compression: the sieve constant; rank: n/a; descent: n/a; cost exponent: `delta_max` ceiling.

### Nearest ledger entries
LARGE-SIEVE-SUPPLY-A1 (this batch, meter form); DELSARTE-LP-A2 (batch8); SHEARER-D3 (batch8); LANGWEIL-SUPPLY-D2 (batch6); AX-KATZ-BARRIER-D3 (batch9). Distinction: a **uniform L² inequality over the whole modulus family** vs any single-place / single-code / entropy / p-adic bound.

### Nearest literature
Montgomery (1978); Bombieri (1974); Iwaniec–Kowalski, *Analytic Number Theory* (2004), Ch. 7 (large sieve). Gap: elliptic-support transfer of the sieve constant.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck; residue-structured / AP-structured advice.

### Full algorithmic path (barrier form)
1. factor base = `P1471` deck; 2. write the occupancy vector across moduli `q≤Q=Theta(L)`; 3. apply the large-sieve inequality; 4. derive `delta_max = O(L^{-1/2}) ≤ 1/4` for `L≥L_0`. **Barrier — no descent (n/a).**

### Cost model
Not a backend. If proven, `delta ≤ 1/4` closes RT-1472 for residue-structured decks (the only explicit advice family measured so far). Compare RT-1472 threshold `delta>1/4`.

### Why the existing negative results do not already kill it
It *is* a strengthening: it converts the per-deck `P1471–P1475` negatives into a family-wide impossibility over all residue-structured advice via one inequality.

### Likely fatal obstruction (to the barrier)
The large-sieve bound is *loose* for the elliptic support (the sequence is not maximally equidistributed), leaving a gap in `[delta_max, 1/4]` — inconclusive rather than a clean closure. Also: it only covers *residue-structured* advice; a non-arithmetic (geometric) enrichment escapes (but no such enrichment is known and P1512-style geometric routes are separately closed).

### Minimal falsifying experiment
`L∈{8,16,32,64}` (four); compute the exact large-sieve deviation and `delta_max` on true decks; positive control = an enriched deck (must exceed the bound if bound is tight); negative control = hash deck; `×5` seeds; report `delta_max` trend and whether it provably `≤1/4`.

### Quantitative promotion gate (barrier)
Proven `delta_max ≤ 1/4` for all `L≥L_0` over residue-structured advice ⇒ **closes RT-1472** for explicit advice.

### Proof track
`delta_max = O(L^{-1/2})` from the large-sieve inequality with `N=Theta(L^2)`, `Q=Theta(L)`.

### Disproof track
A residue-structured deck with `delta>1/4` surviving the sieve bound (would narrow/kill the barrier).

### Reproduction artifact
`experiment_contract_p1643_large_sieve_barrier.md`; `p1643_large_sieve_barrier.py`; `p1643_large_sieve_barrier.json`; `p1643_audit.py`; `ECFG-P1643`.

---

## Candidate: MIXING-TIME-BARRIER  (ECFG-P1644)  ▲ barrier (sampler route)

### One-sentence mechanism
Prove a **conductance / spectral-independence-failure lower bound** on the two-large-prime relation Glauber chain, showing it mixes in `exp(Omega(L^c))` steps — closing the *entire sampler-based enrichment route* (batch5 MATUNION-A2, batch11 LORENTZIAN-LOGCONCAVE-C2, this batch's C2) that every such candidate silently assumed was fast.

### Status
HYPOTHESIS → target THEOREM (barrier). Partner of C1/C2.

### Novelty classification
LEDGER-NEW; the first **Markov-chain mixing-time** barrier in the program. Distinct from HDX-COBOUNDARY-A2 (batch6, *static* topological expansion), PROOF-SPACE-PEBBLING-D1 (batch11), CELL-PROBE-CHRONOGRAM-D1 (batch12) — those are static / cell-probe / proof-space bounds; this is a *temporal* mixing bound on a sampling dynamics.

### Semantic fingerprint F(C)
object: the Glauber/Gibbs chain on the relation distribution `mu`; operations: bound the conductance `Phi(mu)` / the influence-matrix spectral radius; hidden structure: a bottleneck set (small conductance cut) or a large influence eigenvalue; discarded: n/a; retained: the spectral gap; relation primitive: n/a; compression: mixing-time lower bound `≥ 1/Phi`; rank: influence eigenvalue; descent: n/a; cost exponent: mixing-time exponent `c`.

### Nearest ledger entries
LORENTZIAN-LOGCONCAVE-C2 (batch11 — assumed fast mixing); MATUNION-A2 (batch5 — assumed poly sampling); SPECTRAL-INDEPENDENCE-SAMPLER-C2 (this batch); HDX-COBOUNDARY-A2 (batch6). Distinction: prior "mixing" appearances *assumed* rapid mixing as a sufficient condition; this barrier *disproves* it via a conductance bottleneck — the dual, unmet obligation.

### Nearest literature
Jerrum–Sinclair, *Conductance and the rapid mixing property* (1989); Levin–Peres, *Markov Chains and Mixing Times* (2017), Ch. 7 (bottleneck ratio); Anari–Liu–Oveis-Gharan (2020) and its converse (spectral-independence failure ⇒ slow mixing, e.g. hardcore-model non-uniqueness). Gap: no elliptic-relation-chain conductance computation.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3` (pair chain) and `q≈L^5` (relation chain), honest decks.

### Full algorithmic path (barrier form)
1. factor base = `P1471`/`P1473` deck; 2. define the Glauber chain on `mu`; 3. exhibit a low-conductance cut (or an influence-matrix eigenvalue `≥1`); 4. conclude mixing time `≥ exp(Omega(L^c))`. **Barrier — no descent (n/a).**

### Cost model
Not a backend. If proven, no sampler-based enrichment runs in sub-rho time ⇒ closes the `MATUNION`/`LORENTZIAN`/`SPECTRAL-INDEP` arm. Compare: those candidates need poly `L` mixing to certify `delta>1/4`.

### Why the existing negative results do not already kill it
No prior barrier touches sampling *dynamics*; batch5/batch11 candidates were left "open pending a mixing-time analysis" — this barrier supplies exactly that missing analysis, converting three open sampler candidates into a closed arm.

### Likely fatal obstruction (to the barrier)
The elliptic relation chain *does* mix rapidly (bounded conductance), in which case the barrier fails and C1/C2 revive — but the strong prior (long-range algebraic correlation, non-uniqueness-like coupling) is that it does not. A single measured spectral gap bounded below would kill the barrier.

### Minimal falsifying experiment
`L∈{8,16,32}`; empirically estimate the conductance / spectral gap of the relation Glauber chain and its mixing time on true vs random decks; positive control = a rapidly-mixing planted chain (barrier must *not* fire); negative control = a bottlenecked chain (barrier must fire); `×5` seeds; report the mixing-time exponent trend.

### Quantitative promotion gate (barrier)
Proven mixing time `≥ exp(Omega(L^c))`, `c>0` ⇒ **closes the sampler route** for the elliptic relation chain.

### Proof track
A conductance bottleneck `Phi = exp(-Omega(L^c))` (or influence spectral radius `≥1+Omega(1)`) for the honest elliptic relation distribution.

### Disproof track
A bounded-below spectral gap ⇒ rapid mixing ⇒ C1/C2 revive.

### Reproduction artifact
`experiment_contract_p1644_mixing_time_barrier.md`; `p1644_mixing_time_barrier.py`; `p1644_mixing_time_barrier.json`; `p1644_audit.py`; `ECFG-P1644`.

---

## Candidate: SIEVE-PARITY-BARRIER  (ECFG-P1645)  ▲ barrier (RT-1472, root)

### One-sentence mechanism
Invoke the **Selberg parity problem** — the fundamental obstruction that no sieve of the large / Selberg / Bombieri–Vinogradov family can distinguish an even from an odd number of prime factors — to prove that *no sieve-based enrichment* can certify the *signed* concentration `delta>1/4` that RT-1472 requires, closing the entire sieve-enrichment arm (A1/A2/A3) at its root.

### Status
CONJECTURE → target THEOREM (deepest barrier). Root partner of A1/A2/A3.

### Novelty classification
POSSIBLY NOVEL (documented search: Selberg's parity principle; Bombieri's *asymptotic sieve*; Friedlander–Iwaniec *asymptotic sieve for primes* 1998 — **no application to elliptic pair-support enrichment / RT-1472 found**). LEDGER-NEW.

### Semantic fingerprint F(C)
object: the class of sieve weights (large / Selberg Λ² / BV) applied to the pair support; operations: any sieve-weighted count; hidden structure: the *parity* (sign) of the pair-sum contribution, which the sieve cannot access; discarded: **the sign/parity structure** — this is the whole point; retained: the unsigned sifted count; relation primitive: n/a; compression: the parity-blind sieve bound; rank: n/a; descent: n/a; cost exponent: the parity floor on certifiable `delta`.

### Nearest ledger entries
LARGE-SIEVE-SUPPLY-A1 / SELBERG-LAMBDA-CEILING-A2 / BOMBIERI-VINOGRADOV-AVERAGE-A3 (this batch — the arm it closes); DELSARTE-LP-A2 (batch8); RT-1472 (the gate). Distinction: the parity problem is a **structural impossibility for the whole sieve family**, not a numerical ceiling for one deck — it says the sieve *cannot even see* the signed enrichment, a strictly stronger and different statement than any prior size/count ceiling.

### Nearest literature
Selberg, *Collected Papers* (parity principle); Bombieri, *The asymptotic sieve* (1976); Friedlander–Iwaniec, *The polynomial `X^2+Y^4` captures its primes* / *Asymptotic sieve for primes* (Annals 1998) — the modern statement and the conditions to *break* parity (a bilinear/Type-II input). Gap: whether the elliptic pair support supplies the bilinear "Type-II" information needed to break parity is open — almost certainly not for the honest deck.

### Target family
Ordinary prime-order `E/F_p`, `q≈L^3`, two-large-prime deck; all sieve-based enrichment methods.

### Full algorithmic path (barrier form)
1. factor base = `P1471` deck; 2. formalize the pair-enrichment as a sieve problem; 3. show it lacks the Type-II bilinear input; 4. conclude by the parity principle that no sieve certifies `delta>1/4`. **Barrier — no descent (n/a).**

### Cost model
Not a backend. If established, the sieve arm (A1/A2/A3) cannot cross RT-1472 *even in principle* — a root closure stronger than the numerical D1 ceiling. Compare RT-1472 `delta>1/4`.

### Why the existing negative results do not already kill it
Prior supply barriers bound *size*; the parity problem bounds *detectability of sign* — RT-1472's `delta` is defined via a signed (character-weighted) enrichment, exactly the quantity parity forbids a sieve to see. This is the precise reason the whole analytic-supply arm is doomed, not merely bounded.

### Likely fatal obstruction (to the barrier)
If the elliptic pair support secretly carries a **bilinear / Type-II** structure (a Friedlander–Iwaniec-style input), parity *can* be broken and the barrier fails — but constructing such bilinear structure honestly is itself an open enrichment (and if it existed, it would be the crossing, not a failure). Also: the parity barrier constrains sieves, not *all* enrichment (a purely geometric route is outside its scope — but those are separately closed).

### Minimal falsifying experiment
`L∈{8,16,32}`; test whether any sieve weighting of the pair support recovers the *signed* enrichment (compare a parity-sensitive statistic to the sieve's parity-blind estimate); positive control = a synthetic support with injected Type-II bilinear structure (parity breakable — barrier must *not* fire); negative control = the honest deck (barrier must fire); `×5` seeds.

### Quantitative promotion gate (barrier)
Established parity obstruction: no sieve certifies `delta>1/4` on the honest deck ⇒ **closes the sieve-enrichment arm** for RT-1472.

### Proof track
Show the honest elliptic pair support has no Type-II bilinear input ⇒ the parity principle forbids sieve detection of signed `delta>1/4`.

### Disproof track
Exhibit a Type-II bilinear structure in the honest deck breaking parity (would revive A1/A2/A3 — and be a crossing candidate in its own right).

### Reproduction artifact
`experiment_contract_p1645_sieve_parity_barrier.md`; `p1645_sieve_parity.py`; `p1645_sieve_parity.json`; `p1645_audit.py`; `ECFG-P1645`.

---

## 4. Ranking

Scores 0–5 on: (D) distance from prior ledger mechanisms; (V) plausibility of an exact verifier; (X) chance of changing an exponent not a constant; (P) complete-path coverage; (F) falsifiability at toy scale; (L) literature-novelty confidence; (R) freedom from hidden preprocessing/memory cost. Reject if semantic novelty (D) `<3`, or no complete route to descent, or no rho comparison, or no precise distinction from the closest ledger entry.

| ID | Candidate | D | V | X | P | F | L | R | Verdict |
|----|-----------|---|---|---|---|---|---|---|---------|
| P1634 | LARGE-SIEVE-SUPPLY | 4 | 5 | 3 | 4* | 5 | 4 | 4 | **KEEP — conservative winner** |
| P1635 | SELBERG-LAMBDA-CEILING | 4 | 5 | 2 | 4* | 5 | 4 | 4 | KEEP (meter) |
| P1636 | BOMBIERI-VINOGRADOV-AVERAGE | 3 | 4 | 2 | 4* | 4 | 3 | 4 | KEEP (meter) |
| P1637 | POSITIVE-GEOMETRY-CANONICAL-FORM | 5 | 3 | 4 | 4 | 4 | 5 | 3 | **KEEP — representation winner** |
| P1638 | HELTON-VINNIKOV-DETERMINANTAL | 3 | 4 | 2 | 3 | 4 | 3 | 3 | KEEP (lane-closure, reject-risk) |
| P1639 | PRISMATIC-DELTA-RING | 3 | 2 | 2 | 3 | 3 | 3 | 3 | **DEMOTED** (dominated by closed batch2 D2) |
| P1640 | SURVEY-PROPAGATION-RSB | 5 | 3 | 4 | 4 | 4 | 5 | 3 | **KEEP — high-risk winner** |
| P1641 | SPECTRAL-INDEPENDENCE-SAMPLER | 3 | 3 | 3 | 4 | 4 | 2 | 3 | **DEMOTED** (ADJACENT to batch11 C2; value = D2) |
| P1642 | KATZ-SARNAK-SYMMETRY | 3 | 2 | 2 | 3 | 4 | 3 | 4 | KEEP (reject-risk) |
| P1643 | LARGE-SIEVE-BARRIER | 4 | 5 | 5† | 4 | 5 | 4 | 5 | **KEEP — barrier, higher-EV** |
| P1644 | MIXING-TIME-BARRIER | 5 | 5 | 5† | 4 | 4 | 5 | 5 | **KEEP — barrier, higher-EV** |
| P1645 | SIEVE-PARITY-BARRIER | 5 | 4 | 5† | 4 | 4 | 5 | 5 | **KEEP — barrier, deepest, higher-EV** |

`*` supply meters are INCOMPLETE for descent **by design** (they output a `delta` ceiling that feeds the P1473 collector); this is disclosed, not a hidden gap. `†` for barriers, X = "chance of formally closing a live gate", not of crossing.

**Selected winners:**
1. **Conservative:** `LARGE-SIEVE-SUPPLY (P1634)` — the sharpest supply meter yet on RT-1472; converts per-deck negatives to a family-wide ceiling via one L² inequality; near-certain `delta→0` ⇒ promotes to D1.
2. **Representation:** `POSITIVE-GEOMETRY-CANONICAL-FORM (P1637)` — the first non-determinantal, triangulation-invariant residue representation of the r^5 relation cells; the sharpest untried attack on the P1512-R1 nonlinear exception since batch13 Segre/excess, because its complexity is `#facets` not `dim M`; near-certain kill = no `F_p` positivity, which *closes the positive-geometry lane by name*.
3. **High-risk:** `SURVEY-PROPAGATION-RSB (P1640)` — the first statistical-physics (1RSB clustered-phase) analysis of the ECDLP relation CSP; genuinely new regime (uniform samplers and moment counts are both blind to clustering); near-certain kill = coupled algebraic constraints force the uniform fixed point.

**The three barriers (D1/D2/D3) are higher-EV than the winners**, each closing a live gate or method arm with a technology no prior barrier used:
- `LARGE-SIEVE-BARRIER (P1643)` → `delta ≤ 1/4` unconditionally over residue-structured advice ⇒ closes RT-1472 for explicit advice.
- `MIXING-TIME-BARRIER (P1644)` → `exp(Omega(L^c))` Glauber mixing ⇒ closes the sampler-based enrichment arm (retroactively prices batch5 MATUNION-A2 and batch11 LORENTZIAN-C2).
- `SIEVE-PARITY-BARRIER (P1645)` → the Selberg parity principle ⇒ *no* sieve certifies signed `delta>1/4` ⇒ closes the entire analytic-supply arm at its root (deepest of the three).

---

## 5. Experiment contracts and first commands (three winners)

### 5.1 `LARGE-SIEVE-SUPPLY (P1634)` — conservative winner

**Contract `experiment_contract_p1634_large_sieve_supply_ceiling.md`:**
- **Hypothesis:** the honest two-large-prime pair support on ordinary prime-order `E/F_p` has large-sieve-certified enrichment `delta_max = O(L^{-1/2}) ≤ 1/4`.
- **Design:** `L∈{8,16,32}`, `q≈L^3`; per size, build the `P1471` deck, compute residue-class occupancy across moduli `q≤Q=L`, evaluate the large-sieve L² deviation, extract `delta`; positive control = engineered `delta=1/2` deck; negative control = equidistributed hash deck; `×5` curve seeds; ordinary prime-order controls.
- **Promotion gate:** `delta>1/4` with increasing trend and LOO-min `>1/4` ⇒ crossing candidate; else emit the D1 barrier record.
- **Immutability / claim tier:** result JSON + independent audit re-count; claim tier = "measured `delta` ceiling on the tested decks/sizes", no crypto-scale extrapolation.

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1634_large_sieve_supply.py \
  --sizes 8,16,32 --q-exp 3 --moduli-max-exp 1 \
  --decks true,hash,enriched --seeds 5 \
  --out results/p1634_large_sieve_supply.json && \
python3 tasks/ecdlp_index_calculus/p1634_audit.py results/p1634_large_sieve_supply.json
```

### 5.2 `POSITIVE-GEOMETRY-CANONICAL-FORM (P1637)` — representation winner

**Contract `experiment_contract_p1637_positive_geometry_canonical_form.md`:**
- **Hypothesis:** the five signed diagonal-sum loci on `E^5` bound an `F_p`-rational positive geometry whose canonical form has `O(r^{beta})` poles, `beta<1.5`.
- **Design:** `r∈{4,6,8}`, `q≈r^5`; attempt an `F_p` canonical-form construction, count poles; positive control = a cyclic polytope / associahedron over `Q` with `O(r)` poles; negative control = a structureless five-condition system with `Theta(r^5)` poles; `×5` coefficient seeds; ordinary prime-order controls.
- **Promotion gate:** `F_p`-rational canonical form with `#poles=O(r^{beta})`, `beta<1.5`, decreasing `log_r(#poles)` trend, LOO-max `<1.5`.
- **Immutability / claim tier:** each pole's relation re-verified independently by the P1510-R1 compiler; claim tier = "pole-count exponent on the tested sizes", no extrapolation.

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1637_positive_geometry.py \
  --sizes 4,6,8 --q-exp 5 --construct-canonical-form \
  --controls cyclic_polytope,structureless --seeds 5 \
  --out results/p1637_positive_geometry.json && \
python3 tasks/ecdlp_index_calculus/p1637_audit.py results/p1637_positive_geometry.json
```

### 5.3 `SURVEY-PROPAGATION-RSB (P1640)` — high-risk winner

**Contract `experiment_contract_p1640_survey_propagation_rsb.md`:**
- **Hypothesis:** the elliptic five-point relation CSP has a 1RSB clustered phase with survey marginals `>1/4` from uniform, yielding enriched relations.
- **Design:** `L∈{8,16,32}`, `q≈L^5`; build the relation factor graph, run survey propagation, measure convergence and survey-vs-uniform deviation; positive control = a planted-cluster 5-XORSAT ensemble; negative control = an equidistributed relation ensemble; `×5` seeds; ordinary prime-order controls.
- **Promotion gate:** SP convergence with measured `delta>1/4` (or per-relation `alpha<3/2`) **and** a strengthening trend across sizes.
- **Immutability / claim tier:** each decimated relation re-verified by P1510-R1; claim tier = "measured cluster enrichment on the tested sizes"; SP non-convergence or survey≡uniform is recorded as a scoped negative, **not** as evidence against ECDLP improvability.

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1640_survey_propagation.py \
  --sizes 8,16,32 --q-exp 5 --sp-max-iter 1000 --decimate \
  --ensembles true,planted_cluster,equidistributed --seeds 5 \
  --out results/p1640_survey_propagation.json && \
python3 tasks/ecdlp_index_calculus/p1640_audit.py results/p1640_survey_propagation.json
```

---

## 6. Red team — are the three winners disguised repetitions or cost-negative?

**Charge 1 — LARGE-SIEVE-SUPPLY (P1634) is a relabeled Delsarte-LP / Lang–Weil supply meter (batch8/batch6).**
Partly conceded on *role* (it is a δ-supply ceiling, the same slot). But the *operation* is genuinely different: Delsarte-LP is a single linear program over one code's distance distribution; Lang–Weil is a point count of one variety; the large sieve is an **L² inequality quantified over the entire modulus family simultaneously**. A support can pass every single-modulus LP and still be forced to equidistribute by the joint bound. Verdict: **mechanism-distinct, but honestly a scoped tightening, not a crossing** — near-certain `delta→0` ⇒ it promotes to the D1 barrier. Cost-negative as a crossing; net-positive as a barrier.

**Charge 2 — POSITIVE-GEOMETRY (P1637) is Segre/excess (batch13) or GKZ (batch8) in new clothes, and dies to the same `Omega(r^5)` floor.**
Rejected on identity: the canonical form is a *meromorphic differential form* defined by boundary-residue recursion and triangulation-independence; Segre is a *Chow-group class* from a blow-up; GKZ is a `D`-module *solution count*. No shared operation. **But** the red team's cost charge lands: the near-certain kill is that `F_p` has no positivity, so no canonical form exists and any naive residue recursion reproduces the ordinary `Omega(r^5)` sum. Verdict: **mechanism-distinct; near-certain cost-negative** (kills the positive-geometry lane *by name* — a scoped negative, the intended outcome).

**Charge 3 — SURVEY-PROPAGATION (P1640) is CORRELATED-PEEL (batch4) or the Lorentzian sampler (batch11) rebranded.**
Rejected on regime: peeling is the *replica-symmetric* (BP) 2-core process; the Lorentzian sampler assumes a *single well-connected* measure; SP explicitly analyzes the **1RSB clustered phase** where both are blind. Genuinely new statistical-physics object. **But** the cost charge lands: the elliptic constraints are deterministic and fully coupled, violating the cavity independence assumption, so SP near-certainly converges to the uniform fixed point ⇒ `delta≈0`. Verdict: **mechanism-distinct; near-certain cost-negative** (records the cavity-independence failure as the scoped kill).

**Meta-charge — the whole batch is another saturation reconfirmation.**
Conceded, and stated up front. The honest value is **not** in the three attack-winners (all near-certain scoped negatives) but in the **three barriers**: LARGE-SIEVE-BARRIER and SIEVE-PARITY-BARRIER together close the analytic-supply arm for RT-1472 (numerically and at the parity root), and MIXING-TIME-BARRIER prices the sampler assumption that batch5 MATUNION-A2 and batch11 LORENTZIAN-C2 both left unmet. These are the first analytic-number-theory and Markov-chain barriers in the program, and each threshold formally closes a live gate or method arm. **No rho crossing is claimed. RT-1472 and RT-1476 remain open.**

---

## 7. Claim discipline

Every candidate above is a **conjecture / hypothesis / heuristic** at **toy scale**; none is a verified ECDLP recovery, none is crypto-scale, and none claims a completed rho crossing. Supply meters output a `delta` *ceiling*, not a backend. Barriers are *targets for proof*, not established theorems, until an executor produces the measured/proven artifact and an independent validator + red-team accept the Coordinator's snapshot. A failed candidate is a **scoped negative result** bounded to its tested curves, parameters, sizes, and solver — **not** evidence that prime-field ECDLP cannot be improved. IDs `ECFG-P1634…P1645` are **report-proposed** and become official only through the Coordinator's ledger commit and the dispatcher's post-commit verifier.
