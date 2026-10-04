# TASK-20260913-f6652f — review-breakthrough (max) of RUN-SEMBIN-251fd3: joints B1, B2, proves_too_much

Review round `REVIEW-SEMBIN-20260913-251fd3`, plan `coordination/review/sembin-20260913-251fd3/review-plan.yaml`.
Reviewed object: `experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/` (snapshot TASK-20260913-a10007, commit a2cdafc67 — verified present and identical to HEAD for the run package: `git diff --stat a2cdafc67 HEAD -- experiments/EXP-SEMBIN-db9bc3` is empty), hypothesis `H-SEMBIN-4a80f3`.
Role: validator-breakthrough, independent session, attempt 2 (attempt 1 was cut by an infrastructure stop before writing anything; an earlier incarnation of attempt 2 was also cut after writing scratch scripts under `scratch/`, which this session re-read line by line, corrected in one place — a key-name mismatch against `known-false-dF5.json`, see §4 — and re-ran; nothing in this report is taken from that incarnation's outputs without re-execution here).
Inference: requested_policy `review-breakthrough`, resolved model `claude-fable-5-1-thinking-max`, reasoning effort `max`, model_verified false, fallback_used false.

**Standing constraints honoured.** No sibling report read (`TASK-20260913-3b91d0/`, `TASK-20260913-7fb774/`, `coordination/bus/` untouched). No degree measured or asserted (IMP-SEMBIN-ENGINE). No statement about any curve's security in either direction. Verdicts are per joint; no whole-claim verdict is offered. Every number below marked **recomputed** was produced by my own code under `scratch/` (`b1_recompute.py`, `b1_extras.py`, `b2_exponent.py` import nothing from the producer's `code/`); every number marked **producer** is read off the run package; the proves-too-much object (§3) imports the producer's `code/nagao_cost.py` by the plan's own instruction and says so. Script runs this session: 10 of the 20 allowed (9 for the review proper; the tenth ran `tools/check_review_independence.py` against the plan and this task's `attestation.yaml` alone, to confirm the attestation is machine-readable — it reports no problem naming this task, and its only findings are the sibling attestations this session deliberately did not pass to it); peak memory well under 2 GB (log2-domain arithmetic only).

STATUS: FINAL.

## 0. Summary of verdicts

- **B1 — holds**, for the 39 flag entries at n = 571 that survive the coherent (dense-width²) memory reading; **breaks** for the other 81 of the 120 cells — every n = 409 cell and 42 n = 571 cells — which exist only under the frozen-width pairing, an accounting no algorithm has. The survivors are a genuine property of the charged model as stated: reproduced from the definitions to 1.2e-13 bits, not erasable by unit conversion (which deepens them), not erasable by any omitted attack-side term I can bound (all ≥ 124 bits below the charged time), and not erasable by any *coherent* memory reading of Lemma 2 (dense width² is the most pessimistic one, §1.1). They are, however, entirely inside the constants the model does not quantify: one degree of first-fall-degree slack (52–67 bits T×M) erases every survivor, and an absorbed Lemma-2 constant of 2^{10.6} erases the ω = 2.807 headline. The Coordinator's prior on B1 is confirmed on its main point (frozen width is the weak joint) and **sharpened in one direction it did not anticipate**: dense width² is not merely "the honest reading", it is the *ceiling* of the coherent readings, so no memory model can rescue P3 at n = 571 — only the constants and the grant can (§1.1, §4).
- **B2 — holds.** Under bound B, 2^{C_0} = Θ(n/log n), #Fb = Θ(n²/log² n), N = Θ(n²/log n), decompose cost Θ(n^{8ω+2}/(log n)^{4ω+2}); polynomial; trigger (b) correctly did not fire. The Coordinator's prior on the *text* is **partly overturned**: Section 7 and Algorithm 2 do settle the reading more than the prior allows — the v_i are fixed by disjointness alone and Nagao's explicit remedy for empty cosets is "choose suitable constant C_0", not "choose suitable v_i" — so the fixed-coset reading is the text's own and the searched-coset reading is a repair. Under that repair the selection cost is within one bit of building Fb and both bounds dissolve. A third reading (over-provision m by a constant factor, §2.2) leaves only bound A binding. **C1 is reading-dependent** (§2.3). Nothing in ARM C contradicts a published result (§2.4).
- **proves_too_much — passed.** The producer's charging at n = 571 reports `nagao_ahead = false` at m = 2 (min margin +396.6 bits) and m = 3 (min +172.3) under every metric × memory reading × monomial reading. Removing T6 entirely still leaves m = 2 above vOW under every metric (min +78.1) and m = 3 above vOW under every memory-charging metric (§3).

## 1. Joint B1 — the escalation flag

### 1.0 What was recomputed, and how

`scratch/b1_recompute.py` re-implements T1–T6, the four metrics and the vOW Pareto minimum from the *statements* in H-SEMBIN-4a80f3 (mechanism, heuristic_assumptions), cost-surface.json `vow_baseline`/`column_definitions` and CORR-20260913-53739b's yield convention, with its own log-space binomial for the Jensen deficit (lgamma, not the producer's numpy cumulative table). It then reads the producer's JSON only to compare. **Recomputed** results:

- 3,840 producer values (T1…T6, time, and every `margins` entry at committed ω) reproduce with worst |Δ| = 1.2e-13 bits (at n = 409, C_0 = 10, ω = 2.376, loose, T4).
- Flag counts from my own filter over my own cells: 242 memory-charging-metric flags, 180 with committed ω, **120 with committed ω and bound-B-satisfying C_0** — identical to the producer's 242 / 180 / 120; the producer's JSON flag list has 242 entries.
- ARM C bounds from my own code: A = 4 at every label; B = 5 / 6 / 6 / 6 / 7 at n = 163 / 233 / 283 / 409 / 571 — identical to `c0-lower-bound.json` `headline_p2`.
- ARM K's d_F 4 → 5 time rise, computed from the definitions at every surviving cell, equals `known-false-dF5.json` `observed_time_rise_bits` to 0 bits at all 57 rows.

So the arithmetic is not in question anywhere below; the question is what it means.

### B1(1) The memory reading — argument

**What Lemma 2 charges.** Nagao's Assumption 1 (paper l. 416–417): "*Degree of the polynomial appears in the Gröbner basis computation (by F4 algorithm) of {f_1, ..., f_M} is ≤ d_F.*" From it (l. 419–424): "*the number of the monomial appears in the Gröbner basis computation is ≤ O(N^{d_F}) So, we have the following; Lemma 2. The complexity of Gröbner basis computation (by F4 algorithm) of {f_1, ..., f_M} is ≤ O(N^{d_F w}), where w ∼ 2.7 is the linear algebra constant.*" With D := #monomials of degree ≤ d_F, one solve is charged D^ω. That is the cost of dense linear algebra with exponent ω on a matrix whose row count is Θ(D) as well as its column count — the run's T1 + T2 = ω · log2 D (binomial reading D = C(N+4,4), loose reading D = N⁴).

**What memory that time charge implies.** Every dense elimination with exponent ω < 3 is a fast-matrix-multiplication method operating on explicit blocks; its working set is Θ(rows × cols). For the Θ(D)-row matrix that D^ω presupposes, that is Θ(D²) field elements. The frozen-width figure D is the size of one row, or of the column-index set: it is the memory of a monomial ordering, not of a linear-algebra step. **There is no algorithm with time D^ω, ω ∈ {2.376, 2.807, 3.0}, and memory Θ(D).** The producer's frozen pairing therefore takes its time from one algorithm and its memory from none.

**Is there an implicit/structured representation that gets width-scale memory at the SAME ω?** No, and I state this as a claim I could not refute rather than a theorem. The methods that achieve memory near the width are the black-box/iterative solvers (Wiedemann 1986, Lanczos, block Wiedemann — provenance **recalled**, pointers only): memory Θ(nnz) = Θ(D · rw) with rw the row weight, but time Θ(D · nnz) = Θ(D² · rw) — a different cost model, exponent 2 in D times the row weight, not D^ω. They also return a kernel vector or a solution of Ax = b, not the reduced rows F4's degree-fall mechanism needs; pairing them with Lemma 2 models a one-shot linearisation (XL-type) at whatever degree XL needs, and equating that degree with d_F is a stronger grant than Assumption 1 — a degree question this review may not adjudicate (IMP-SEMBIN-ENGINE).

**The coherent family, and why dense width² is its ceiling (recomputed, `b1_extras.py`).** A Lemma-2 elimination on an r × D matrix, 1 ≤ r ≤ D, costs time r^{ω−1}·D and memory r·D, so T × M = r^ω · D² · 2^{T3+T4} — **monotone increasing in r**. The producer's time charge D^ω is the r = D member; its coherent memory is D². Any *cheaper* coherent member (fewer rows) lowers time and memory together and **deepens** the flag. At (n = 571, C_0 = 8, ω = 2.807, binomial):

| coherent member | log2 r | time | memory | T×M | T×M margin vs vOW |
|---|---|---|---|---|---|
| r = D (dense width², the producer's time charge) | 56.6 | 173.2 | 113.3 | 286.5 | **−10.6** |
| r = N(N+1) (one Macaulay step of N cubics × N+1 multipliers) — NOT ADOPTED | 30.6 | 126.1 | 87.3 | 213.4 | −83.7 |
| r = 1 (what "memory D" would coherently pair with: time D, not D^ω) | 0 | 70.8 | 56.6 | 127.5 | −169.6 |
| producer's frozen pairing (time from r = D, memory from r = 1) — incoherent | — | 173.2 | 56.6 | 229.9 | −67.3 |

At n = 409 the same table gives +52.0 (r = D) and −15.7 (r = N(N+1)): the one-step reading would *restore* the n = 409 flags. I do not adopt it, and neither may the run: asserting r = N(N+1) asserts that the F4 computation terminates in a single degree-4 Macaulay step, which is a statement about the solving degree and the shape of the computation that this program cannot make (IMP-SEMBIN-ENGINE), and which Lemma 2 does not make (it gives only the upper bound D^ω). What the table establishes is the direction: **within the charged model as stated (time = D^ω), the only coherent memory is D²; and among all coherent readings of Lemma 2, D² is the one least favourable to Nagao.** The surviving dense flags are therefore a *floor* on how far below vOW the coherent charged model sits at n = 571, not a residue that a better memory model could remove.

**Conclusion of B1(1).** The frozen-width reading is indefensible as the memory of the D^ω time charge — the Coordinator's prior on the weak joint is **confirmed** — and dense width² is not just defensible but maximal among coherent readings, which the prior did not say and which cuts against the hope, expressed in its `what_would_change_my_mind`, that "a defect in the charging erases the n = 571 flags under the dense reading too": no memory-model defect can, because there is no more pessimistic coherent memory. Under the dense reading (**recomputed**, identical to **producer**): no n = 409 flag survives (minimum dense T×M margin at n = 409 across committed ω and bound-B C_0: **+18.2 bits**, at ω = 2.376, C_0 = 16, binomial); at n = 571, 39 flag entries survive.

**Surviving-flag list under each memory reading (the 120-cell set; recomputed; `scratch/b1_tables.md`).**

*Frozen width — 81 entries (every one an artifact of the incoherent pairing):*
n = 409: ω = 2.376 at C_0 ∈ {6, 8, 10, 12, 16}, both readings, T×M and AT (20 entries); ω = 2.807 at C_0 ∈ {8, 10, 12, 16}, binomial only, T×M and AT (8); ω = 3.0 at C_0 = 16, binomial, T×M and AT (2). — 30 entries.
n = 571: ω = 2.376 at C_0 ∈ {8, 10, 12, 16}, both readings, T×M and AT (16) plus equal-rate at C_0 ∈ {10, 12, 16} binomial (3); ω = 2.807 at C_0 ∈ {8, 10, 12, 16}, both readings, T×M and AT (16); ω = 3.0 at C_0 ∈ {8, 10, 12, 16}, both readings, T×M and AT (16). — 51 entries.

*Dense width² — 39 entries, all at n = 571:*
- ω = 2.376: C_0 ∈ {8, 10, 12, 16}, binomial and loose, T×M and AT — 16 entries; equal-rate at C_0 ∈ {10, 12, 16}, binomial — 3 entries (margins −1.1, −2.0, −2.5 bits).
- ω = 2.807: C_0 = 8 binomial (T×M, AT); C_0 ∈ {10, 12, 16} binomial and loose (T×M, AT) — 14 entries.
- ω = 3.0: C_0 ∈ {10, 12, 16}, binomial only (T×M, AT) — 6 entries. (C_0 = 8: +0.3, not a flag; the dense ω = 3.0 T×M margin by C_0 is +48.0, +42.1, +23.5, +7.1, **+0.3**, −4.3, −8.2, −13.1 at C_0 = 2 … 16.)

AT and T×M coincide at every cell because the run charges both as 6nW against time × memory; that identical treatment is joint N2's, not mine, and I take it as declared.

### B1(2) The absorbed constant — erasing-constant table

Lemma 2's O(N^{d_F ω}) has no measured constant; Proposition 5's d_F ≤ 4 is stated with "*The situation is the same as the Semaev's case. So, we omit the proof*" (footnote 6, l. 844). For each dense survivor (T×M; AT identical), the constant in bits that erases it, beside ARM K's d_F 4 → 5 rise computed from the definitions (**recomputed**; time rise equals `known-false-dF5.json` exactly). "Inside?" asks whether the erasing constant is smaller than one degree of slack.

| ω | C_0 | reading | margin | erasing constant (bits) | d_F 4→5 time rise | memory rise (dense) | T×M rise | inside one degree? | fraction of one degree |
|---|---|---|---|---|---|---|---|---|---|
| 2.376 | 8 | binomial | −35.0 | 35.0 | 30.9 | 26.0 | 56.8 | yes | 0.62 |
| 2.376 | 8 | loose | −24.1 | 24.1 | 36.4 | 26.0 | 62.3 | yes | 0.39 |
| 2.376 | 10 | binomial | −38.9 | 38.9 | 30.1 | 25.3 | 55.4 | yes | 0.70 |
| 2.376 | 10 | loose | −28.0 | 28.0 | 35.6 | 25.3 | 61.0 | yes | 0.46 |
| 2.376 | 12 | binomial | −42.0 | 42.0 | 29.4 | 24.8 | 54.2 | yes | 0.78 |
| 2.376 | 12 | loose | −31.1 | 31.1 | 35.0 | 24.8 | 59.7 | yes | 0.52 |
| 2.376 | 16 | binomial | −45.9 | 45.9 | 28.4 | 23.9 | 52.4 | yes | 0.88 |
| 2.376 | 16 | loose | −35.0 | 35.0 | 33.9 | 23.9 | 57.9 | yes | 0.60 |
| 2.807 | 8 | binomial | **−10.6** | 10.6 | 36.4 | 26.0 | 62.4 | yes | 0.17 |
| 2.807 | 10 | binomial | −15.0 | 15.0 | 35.6 | 25.3 | 60.9 | yes | 0.25 |
| 2.807 | 10 | loose | −2.1 | 2.1 | 42.1 | 25.3 | 67.4 | yes | 0.03 |
| 2.807 | 12 | binomial | −18.6 | 18.6 | 34.8 | 24.8 | 59.6 | yes | 0.31 |
| 2.807 | 12 | loose | −5.8 | 5.8 | 41.3 | 24.8 | 66.1 | yes | 0.09 |
| 2.807 | 16 | binomial | −23.2 | 23.2 | 33.6 | 23.9 | 57.5 | yes | 0.40 |
| 2.807 | 16 | loose | −10.4 | 10.4 | 40.1 | 23.9 | 64.0 | yes | 0.16 |
| 3.0 | 10 | binomial | −4.3 | 4.3 | 38.0 | 25.3 | 63.3 | yes | 0.07 |
| 3.0 | 12 | binomial | −8.2 | 8.2 | 37.2 | 24.8 | 62.0 | yes | 0.13 |
| 3.0 | 16 | binomial | −13.1 | 13.1 | 35.9 | 23.9 | 59.8 | yes | 0.22 |

Equal-rate survivors (ω = 2.376, binomial, dense = frozen since time > memory there): −1.1 / −2.0 / −2.5 bits at C_0 = 10 / 12 / 16, against a d_F 4→5 rise of the max(time, memory) of 30.1 / 29.4 / 28.4 bits — fractions 0.04–0.09.

**Reading.** Every surviving margin is inside one degree of first-fall-degree slack: the largest (45.9 bits, ω = 2.376, C_0 = 16) is 0.88 of one degree; the ω = 2.807 headline is 0.17 of one degree and is erased by an absorbed constant of 2^{10.6} ≈ 1,550 in Lemma 2's O(·) — a factor that F4's iteration count times a Strassen-type leading constant could plausibly supply or exceed, and that nothing in the run bounds. The ω = 3.0 survivors (4.3–13.1 bits) are of the same character. The ω = 2.376 survivors need 2^{24}–2^{46}, which no absorbed *linear-algebra* constant of an implemented method reaches — but ω = 2.376 is the Coppersmith–Winograd exponent, whose algorithm is galactic and whose constant is not known to lie below 2^{35} for any implementation (provenance **recalled**, pointer only); those cells cost a theorem's exponent, not an algorithm anyone runs (the prior said this and I confirm it). For the record, under the *frozen* pairing 19 of the 24 n = 571 T×M rows have erasing constants **outside** one degree of slack (fractions up to 2.44): that is exactly why the memory reading is load-bearing and why the producer's escalation headline read as robust before the pairing was examined.

### B1(3) The grant — which first-fall-degree assumption the charging needs

The charging needs the **strong** version. Precisely: the run charges one solve at D^ω with D = #monomials of degree ≤ d_F = 4 (Prop. 5, p = 2). That figure is Lemma 2's, and Lemma 2 is derived from Assumption 1 as quoted above — that *the degree of every polynomial appearing in the F4 computation is ≤ d_F*. That is the statement "the solving degree of the Gröbner computation equals (is bounded by) the first fall degree". Proposition 5 by itself ("*First fall degree of EQS4(m,R) is bounded by 4 (p = 2)*", l. 719–729) is only a statement about the degree at which the first non-trivial degree fall occurs; it bounds nothing about the degrees F4 subsequently reaches, and it is stated with its proof omitted. A weaker grant — "d_F ≤ 4 and the solving degree is some d_solve ≥ d_F" — gives a charge of C(N + d_solve, d_solve)^ω, which at d_solve = 5 is the ARM K rise in the table above (52–67 bits T×M), erasing every survivor. So the flags stand or fall with the strong grant, and the strong grant is the published point of contention for Weil-descent systems. Pointers, all **recalled** and none read by any agent in this program as far as this review knows: Petit–Quisquater (ASIACRYPT 2012) introduce the first-fall-degree heuristic for these systems; Kosters–Yeo (2015, "Notes on summation polynomials") report evidence that the degree of regularity/solving degree of Semaev-type Weil-descent systems grows beyond the first fall degree; Galbraith–Gaudry (2016 survey) discuss the gap. These are where a Coordinator should look; they support nothing here. Nagao's own text (l. 426–428) warns of a different confusion — the "FAKE first fall degree" reduced mod field equations (Definition 6) — and the run's T1 counts monomials of degree ≤ 4 without field-equation reduction, which is the true-d_F reading; the difference between C(N+4,4) and the squarefree count Σ_{d≤4} C(N,d) at N = 40541 is 0.0004 bits (**recomputed**, `O12` in `b1_recompute.json`), so that choice is immaterial. **This review measures and asserts no degree**; it records only that the surviving flags are conditional on Assumption 1 in its strong form and vanish one degree above it.

### B1(4) Omitted terms — bounds at n = 571, C_0 = 8 (m = 72, N = 40541), bits

Reference: charged time 173.2 (ω = 2.807, binomial), charged T×M dense 286.5, T5 dense 113.3, T5 frozen 56.6. **Recomputed**, `b1_recompute.json` `omitted_terms_n571_C0_8`; pessimistic (schoolbook n² bit-ops per field multiplication) throughout.

| omitted term | side | bound (bits) | could it close a surviving margin? |
|---|---|---|---|
| O1 Weil descent of EQS4 per trial R (only the last S_3 equation depends on x(R); n descended coordinates × ≤ n²(C_0+1) terms, × #Fb·2^{T4} trials) | attack, time | 44.8 | no — 128 bits below the charged time |
| O1b Weil descent of the whole (m−1)-equation system once | attack, time | 36.8 | no |
| O2 computing R = n_1P + n_2Q per trial (two scalar multiplications, ~1.5n group ops each, n² bit-ops per op) | attack, time | 43.2 | no |
| O3 relation verification (m point additions per relation, 3 log n or n² bit-ops each) | attack, time | 48.8 | no — 124 bits below; this is the largest attack-side omission |
| O4 final linear algebra — already charged as T6 = ω·T3 = 39.8, log-added (T6 − time = −133 at this cell; max over bound-B cells at n = 571 is −95.8) | attack, time | 39.8 | no |
| O4b … as sparse Wiedemann, 2·T3 + log m | attack, time | 34.5 | no |
| O4c/O4d relation-matrix memory, dense / sparse | attack, memory | 28.3 / 24.2 | no — ≥ 85 bits below T5 dense (and 28 below T5 frozen) |
| O5 final descent of P and Q | attack | none: Algorithm 2 decomposes R = n_1P + n_2Q (l. 864), so P and Q never need a separate descent | — |
| O6 communication / machine model | both | uncharged on both sides; no machine model in the contract; symmetric omission, unboundable here | not boundable |
| O8 over-collection (#Fb + 1 vs #Fb + 64 relations) | attack | 0.01 | no |
| O9 randomness per trial | attack | 10.2 bits per trial, log-domain; ≪ per-trial solve cost | no |
| O7 negation map | baseline | **already in the baseline**: W = 0.886·2^{n/2} = √(π·2^n/4) is the negation-equivalence figure, not √(π·2^n/2) | not an omission |
| O7b prime-order subgroup cofactor h = 2 (B-curves) / 4 (K-curves): vOW runs in a group of order ≈ 2^{n−1} / 2^{n−2} | baseline | 0.5 / 1.0 bits **in vOW's favour** | erases nothing on its own |
| **O10 Koblitz Frobenius** (K-curves only): the order-n automorphism beyond negation gives vOW a further √n speed-up, 0.5·log2 571 = **4.58 bits in vOW's favour**; provenance recalled (Wiener–Zuccherato 1998; Gallant–Lambert–Vanstone 2000), pointers only | baseline | 4.58 (+1.0 with the cofactor = 5.6) | **yes, for the six thinnest entries on a Koblitz curve only**: ω = 2.807 loose C_0 = 10 (−2.1 → +2.4, T×M and AT), ω = 3.0 C_0 = 10 (−4.3 → +0.3, T×M and AT), equal-rate ω = 2.376 C_0 ∈ {10, 12} (−1.1/−2.0 → +1.2/+0.3); 33 of 39 survive; the −10.6 and −35.0 headlines become −6.0 and −30.4. The run's baseline is curve-agnostic (n only), so this is a refinement outside the model, recorded here because it is the only omitted term that moves any flag |
| O11 harvesting every solution of one solve: at the grid C_0 the expected solution count per trial is λ = 2^{mC_0 − n − Δ} = 2^{4.8} / 2^{9.0} / 2^{5.0} / 2^{5.0} at C_0 = 8 / 10 / 12 / 16, all extracted from the same Gröbner basis; Algorithm 2 as written takes one relation per R (l. 865–868) and the run's T4 convention charges Pr[≥ 1 solution], so the model omits a factor of up to λ **in Nagao's favour** | attack | 4.8–9.0 bits deeper | wrong direction — cannot erase |

**Verdict on omitted terms.** No attack-side omission is within 85 bits of mattering on either time or memory. The only omitted terms that move a flag are baseline-side refinements for one curve family (Koblitz Frobenius + cofactor), and they erase only the six entries whose margins were already below 4.4 bits. Nothing omitted closes the −10.6 (ω = 2.807) or −35.0 (ω = 2.376) headline at C_0 = 8, and the solution-harvest omission would deepen both by ~5 bits.

### B1(5) The unit — direction and converted margins

Nagao's unit is one F_2 Macaulay-matrix operation (one bit operation); vOW's is one E(F_{2^n}) group operation (≥ one field inversion and two multiplications: ~n log n bit-ops with fast arithmetic, ~n² schoolbook). Expressing both in bit operations multiplies vOW's count and leaves Nagao's alone, so every conversion **raises** vOW and makes margin = Nagao − vOW **more negative**: the conversion cannot erase a flag. Direction independently confirmed; the producer's disclosure (`unit_conversion_sensitivity`: +12.35 / +18.31 bits to vOW at n = 571) is right, and my own figures are the same numbers (log2 571 + log2 log2 571 = 12.35; 2·log2 571 = 18.31). Converted margins at the dense survivors, binomial reading (**recomputed**; equal-rate takes half the conversion):

| ω | C_0 | metric | unconverted | n log n | n² |
|---|---|---|---|---|---|
| 2.376 | 8 | T×M | −35.0 | −47.4 | −53.3 |
| 2.376 | 10 | equal-rate | −1.1 | −7.3 | −10.3 |
| 2.376 | 10 | T×M | −38.9 | −51.2 | −57.2 |
| 2.376 | 12 | equal-rate | −2.0 | −8.2 | −11.2 |
| 2.376 | 12 | T×M | −42.0 | −54.4 | −60.3 |
| 2.376 | 16 | equal-rate | −2.5 | −8.7 | −11.6 |
| 2.376 | 16 | T×M | −45.9 | −58.2 | −64.2 |
| 2.807 | 8 | T×M | −10.6 | −23.0 | −28.9 |
| 2.807 | 10 | T×M | −15.0 | −27.4 | −33.3 |
| 2.807 | 12 | T×M | −18.6 | −31.0 | −37.0 |
| 2.807 | 16 | T×M | −23.2 | −35.6 | −41.5 |
| 3.0 | 10 | T×M | −4.3 | −16.7 | −22.6 |
| 3.0 | 12 | T×M | −8.2 | −20.5 | −26.5 |
| 3.0 | 16 | T×M | −13.1 | −25.4 | −31.4 |

The unconverted figures are the ones least favourable to Nagao and are the ones I report; the conversion is disclosed direction, not applied.

### B1(6) The claim tier

**Strongest statement supported, in the hypothesis's `method_ceiling` form** (H-SEMBIN-4a80f3 l. 142–148):

> "Granting Proposition 5 (d_F ≤ 4) **and Assumption 1 in its strong form (every degree reached in the F4 computation is ≤ d_F, i.e. solving degree = first fall degree)**, HEUR-1 and HEUR-2, Lemma 2's O(·) constant taken as 1, and memory charged as the dense width² C(N+4,4)² that Lemma 2's D^ω time charge coherently implies — and with T1–T5 made explicit as the run defines them (T1 = log2 C(N+4,4) or 4 log2 N; T2 = (ω−1)T1; T3 = log2(m·2^{C_0}+1); T4 = log2 1/Pr[≥ 1 solution] under the typical-product convention; T5 = 2·T1) — the charged cost of Nagao Theorem 1 at n = 571 for bound-B-satisfying C_0 ∈ {8, 10, 12, 16} is **below** van Oorschot–Wiener's time × memory Pareto minimum 6nW (= 2^{297.1}) by 24.1–45.9 bits at ω = 2.376, by 2.1–23.2 bits at ω = 2.807, and by 4.3–13.1 bits at ω = 3.0 for C_0 ≥ 10 (+0.3 bits above it at C_0 = 8); it is **above** it at every C_0 and ω at n ∈ {163, 233, 283, 409} (minimum margin at 409: +18.2). Every one of those margins is smaller than the 52–67-bit rise one additional degree of solving-degree slack would produce and, at ω ≥ 2.807, smaller than 2^{23.2} of absorbed Lemma-2 constant. Unit conversion, if applied, would deepen every margin by 12–18 bits. And Nagao's no-empty-coset condition forces C_0 ≥ 4 (bound A) and his Θ(1)-yield condition C_0 ≥ 7 (bound B) at n = 571 under the fixed-coset reading."

**About P3 and C2, in the charged model.** P3 ("the charged Nagao cost exceeds vOW's Pareto minimum under T×M and AT at ALL FIVE labels for ALL THREE ω, and no crossover exists below n = 571") is **falsified in the charged model** at the n = 571 label under the coherent memory reading for ω ∈ {2.376, 2.807} at every bound-B-satisfying grid C_0, and for ω = 3.0 at C_0 ≥ 10; the producer's dense T×M crossovers (**producer**, 457–697 across cells, straddling 571 at ω = 3.0) are consistent with my margins. C2's literal falsification criterion — "any memory-charging metric in the committed set giving a crossover below n = 571 for any omega in the committed set at any defensible C_0" — **is met in the charged model** (ω = 2.807, C_0 = 8, T×M dense, bound-B-satisfying). Whether that makes C2 `weakened` or leaves it `inconclusive within the model's own precision` is the Coordinator's decision, and the decisive fact for it is that the margins meeting the criterion (2.1–45.9 bits) are inside the constants the model leaves unquantified (Lemma 2's O(·); one degree of Assumption-1 slack). My recommendation to the Coordinator is that any status change name those two constants beside the margin. C2's *time-only* clause ("a crossover may exist below n = 571") is not my joint but is confirmed incidentally (time-only margins −112 to −117 bits at n = 571, ω = 2.807).

**About curves: nothing.** The tier vocabulary of `docs/claims-and-verification.md` derives a run's tier from the field size of *measurements*; this run measures nothing on any curve — it evaluates closed forms at the field sizes of B-/K-163…571 — so it contributes no `toy`/`medium`/`crypto` measurement tier and may make no scoped claim about any curve at any tier. It is a heuristic-conditional **derivation** (two-record rule: conditional on Prop. 5, Assumption 1 strong, HEUR-1, HEUR-2), and the conditional qualifier must travel with every rendering of it. The scope statement the contract requires ("no standardised curve is affected") **can be stated here as a conclusion, with its table**: no row of the surviving-flag list is a statement about B-571, K-571 or any curve; every row is a statement about the charged model's closed form under the grants above; the algorithm costed has not been run at any n by anyone in this program; and the only curve-specific refinement examined (Koblitz automorphisms, O10) moves the comparison *away* from Nagao. **No standardised curve is affected by anything in RUN-SEMBIN-251fd3**, in the precise sense that nothing in the run bears on any curve's security in either direction.

### B1 — verdict: **holds** (for the 39 dense-reading survivors at n = 571; **breaks** for the 81 frozen-only cells including every n = 409 cell)

The plan's breaking artifact was "a defensible memory model, constant, omitted term or grant under which NO flagged cell survives at n = 571". I found none *within the charged model as stated*: the coherent memory reading leaves 39 survivors and is the most pessimistic coherent reading (§1.1); no omitted term I can bound reaches them (§1.4); the unit deepens them (§1.5). What *does* erase every survivor is one degree of Assumption-1 slack, and what erases the ω ≥ 2.807 survivors is an absorbed constant of ≤ 2^{23.2} — but those are the model's premises, and the plan asks whether the flags are an artifact of the granted assumptions: they are a *consequence* of them, disclosed as such, not an artifact. The holding artifacts (surviving-flag lists, erasing-constant table, grant statement, omitted-term bounds, unit-converted margins, claim-tier statement) are all above.

**Prior overturned?** On B1: the prior's main expectation (frozen width is the weak joint; 409 flags do not survive; 571 flags survive under dense for ω ≤ 2.807 and sit within the absorbed constant; ω = 2.376 rests on an unreachable ω; strong FFD is the grant) is **confirmed on every point**. Two sharpenings the prior did not contain: (i) dense width² is the *ceiling* of the coherent readings, so the 571 flags cannot be erased by any memory model — only by the constants and the grant — and cheaper coherent readings would restore 409 (§1.1, §4); (ii) ω = 3.0 also survives at C_0 ≥ 10 (4.3–13.1 bits), which the prior's "ω ≤ 2.807" understates.

## 2. Joint B2 — ARM C's inference to Theorem 1 and trigger (b)

### B2(1) The exponent under bound B (**recomputed**, `scratch/b2_exponent.py`, `b2_exponent.json`)

Bound B (the run's operationalisation of "∏#Fb_i ∼ p^n": total Jensen deficit Δ ≤ 1 bit) with Δ = m·δ(C_0), δ(C_0) = log2 E[2B] − E[log2 2B | B ≥ 1] for B ∼ Bin(2^{C_0}, ½), δ(C_0) = 1/(2^{C_0+1} ln 2) + O(4^{−C_0}), and m = n/C_0:

Δ = n/(C_0 · 2^{C_0+1} ln 2) ≤ tol  ⟺  2^{C_0} ≥ n/(2·C_0·tol·ln 2)  ⟺  **C_0 ≥ log2 n − log2 log2 n + O(1)**.

My integer bound B tracks log2 n − log2 log2 n to within +0.0…+0.8 at n = 2^7…2^25 (`bound_B_growth`), and reproduces 5/6/6/6/7 at the labels. So 2^{C_0} = Θ(n/log n) and:

- m = n/C_0 = Θ(n/log n);
- #Fb = m·2^{C_0} = Θ(n²/log² n)  — *not* O(n) as Section 7 states (l. 764: "#Fb ∼ m·p^k = p^{C_0}/C_0 · n = O(n)", which holds only for constant C_0);
- N = n(m − 1) = Θ(n²/log n);
- D = C(N+4,4) = Θ(N⁴) = Θ(n⁸/log⁴ n);
- decompose = #Fb · 2^{T4} · D^ω = **Θ(n^{8ω+2} / (log n)^{4ω+2})** with 2^{T4} = O(1) by construction of bound B;
- linear algebra = #Fb^ω = Θ(n^{2ω}/log^{2ω} n), dominated.

**Polynomial, exponent 8ω + 2 up to a (log n)^{−(4ω+2)} cofactor** — the producer's "8ω+2 up to logarithmic factors" is confirmed; Nagao's 8ω + 1 is what one gets with #Fb = O(n), i.e. constant C_0. A numerical aside the Coordinator should know: the local slope d(log2 cost)/d(log2 n) at n ∈ [2^14, 2^25] under bound B is 19.7–20.2 (ω = 2.376), 23.0–23.5 (ω = 2.807), 24.4–25.0 (ω = 3.0) — numerically within one of **8ω + 1**, not 8ω + 2, because the polylog cofactor's slope is ≈ −0.7 to −1.2 per doubling in that range. The asymptotic exponent is 8ω + 2; at any n a reader will ever evaluate, Nagao's 8ω + 1 is the better numerical description. Both are polynomial. **Trigger (b) — "ARM C establishes C_0 = Ω(log n) and the run proposes that Theorem 1 is non-polynomial as stated" — correctly did not fire**, and the Coordinator's contract prior (non-polynomial) is correctly recorded by the producer as overturned.

For completeness, the fixed-C_0 side (`fixed_C0_fixed_cosets_T4_asymptotics`): at literally constant C_0 with m = ⌈n/C_0⌉ and cosets fixed before inspection, Δ = n·δ(C_0)/C_0 grows *linearly* in n (0.033 bits per unit n at C_0 = 3; 0.0004 at C_0 = 8), so the typical product is 2^{n(1 − δ/C_0)} and 2^{T4} = 2^{Θ(n)}: the decompose step is not polynomial at constant C_0 under that reading. Polynomiality needs Δ = O(log n), i.e. C_0 ≥ log2 n − 2 log2 log2 n + O(1) = Θ(log n) — bound B's 1-bit version is the tighter member of the same family — **or** one of the two repairs in §2.2.

### B2(2) Section 7 / Algorithm 2 — does the text fix the cosets or permit choosing them?

Quotations (`inputs/NAGAO-2015-984/paper_fulltext.md`, line numbers of the frozen text):

- l. 663: "*Let v_1, ..., v_m be elements in F_{p^n} such that all V + v_i (i = 1, ..., m) are disjoint.*"
- l. 685: "*Note that #Fb_i ∼ #V_i = #V ∼ p^k, #Fb ∼ m · p^k.*"
- l. 746–751: "*The difference between using normal factor base and disjoint factor base is the probability that decomposition success. The number of the elements in E(F_{p^n}) written by the form P_1 + ... + P_m (P_i ∈ Fb_i) is ∏_{i=1}^m #Fb_i ∼ (p^k)^m ∼ p^{km} ∼ #E(F_{p^n}). So, the probability that decomposition success, is O(1). On the other hands, the size of all factor base ∪Fb_i became m times large. However, it is not heavy problem.*"
- l. 753–760: "*Now fix k = C_0 be a small natural number and put the parameter m ∼ n/C_0. Then we have ∏_{i=1}^m #Fb_i ∼ (p^k)^m ∼ p^n. (Note: if one takes k = 1, it sometimes happens #Fb_i = ∅ for some i. To avoid such case and confirm the relation ∏_{i=1}^m #Fb_i ∼ p^n, we choose suitable constant C_0.)*"
- l. 762–764: "*since we must collect #Fb + 1 decompositions, the cost of "decompose step" is estimated by … #Fb ∼ m · p^k = p^{C_0}/C_0 · n = O(n).*"
- Algorithm 2, l. 852–858: "*Set parameter k, m satisfying km ∼ n / Put V = {Σ x_i α_i | x_i ∈ F_p} / Put v_1, ..., v_m ∈ F_{p^n} st. V + v_i are disjoint / Put V_i := V + v_i / Put Fb_i := {P ∈ E(F_{p^n}) | x(P) ∈ V} [sic: V_i] / Put Fb := ∪ Fb_i*".

**Reading.** The only condition the text ever places on the v_i is disjointness (l. 663, l. 855). The two things that go wrong with small k — an empty coset, and the product falling short of p^n — are both named in the parenthesis, and the remedy the text gives for *both* is the same: "*we choose suitable constant C_0*". Nowhere does the text inspect #Fb_i or select v_i on the basis of it; Algorithm 2's "Put v_1, …, v_m st. V + v_i are disjoint" is a construction step with no test in it. So the text is not silent, as the prior expected; it **fixes the cosets by disjointness alone and repairs by C_0** — the unsearched reading is the text's own, and HEUR-1 (binomial coset counts, cosets fixed before inspection) formalises exactly it. The searched-coset reading — pick the m fullest of the 2^{n−C_0} available translates — is a *repair* a reader may make; the text permits it in the weak sense that it forbids nothing, not in the sense of describing it. **This partly overturns the Coordinator's prior on B2** ("Nagao's text does not settle it"): the text leans one way, and the way it leans is the one under which bounds A and B bind.

**Selection cost under the searched-coset reading (recomputed, `searched_coset_selection_n571`).** Test a coset by evaluating, for each of its 2^{C_0} x-values, whether x is the abscissa of a point (one trace of x + a + b/x², ~n² bit-ops schoolbook), keeping cosets with #Fb_i ≥ 2^{C_0} (B_i ≥ 2^{C_0−1}, probability ≈ 0.52–0.75). Expected cosets tested to find m keepers = m/Pr[keep]; at n = 571: 137 tested for m = 72 at C_0 = 8 (2^{33.4} bit-ops), 239 for m = 143 at C_0 = 4 (2^{30.2}), 761 for m = 571 at C_0 = 1 (2^{28.9}). Building Fb itself (a square root per surviving x, ~n² each) is 2^{32.5} / 2^{29.5} / 2^{28.5} at the same C_0. **Selection costs 0.4–0.9 bits more than construction — the same order, as the producer says.** Availability is never an issue (2^{563} cosets for 72 needed at C_0 = 8). Under this reading every kept coset has #Fb_i ≥ 2^{C_0}, so ∏#Fb_i ≥ 2^{mC_0} ≥ 2^n, Δ ≤ 0, no coset is empty, and **neither bound constrains C_0** — "fix k = C_0 a small natural number" is available at every C_0 ≥ 1 (even C_0 = 1, where the "cosets" are pairs {v, v+α_1} and one keeps those with both x-values on the curve). The prior's expectation that both bounds dissolve under the searched reading is **confirmed**.

**A third reading the plan did not name (recorded as unexpected, §4).** Keep the cosets fixed (the text's reading) but read "m ∼ n/C_0" loosely enough to over-provision by the constant factor 1 + δ/C_0 — m = ⌈n/(C_0 − δ(C_0))⌉ + O(√n) instead of ⌈n/C_0⌉ (197 + O(24) instead of 191 at C_0 = 3, n = 571). Then E[log2 ∏#Fb_i] ≥ n with the CLT fluctuation Θ(√n) bits covered, Pr[success] = Θ(1) with high probability over the factor base, and bound B no longer binds; only bound A (no empty coset, Θ(log log n)) remains. Under bound A, 2^{C_0} = Θ(log n), #Fb = Θ(n log n / log log n), N = Θ(n²/log log n), decompose = Θ(n^{8ω+1} · polylog): **the stated exponent 8ω + 1 survives up to polylog factors.** The cost of the repair is a constant-factor increase in N (1 + δ/C_0 ≤ 1.035 at C_0 ≥ 3) and in #Fb — bits, not exponents. This reading is not in the text either (m = ⌈n/C_0⌉ is what "m ∼ n/C_0" most naturally means and is what the run uses), but it is a smaller departure than searching, and it matters for C1.

### B2(3) C1's status — one sentence

**C1 is reading-dependent: under the text's own fixed-coset reading it holds (C_0 must grow — Θ(log n) via bound B for Nagao's Θ(1)-yield claim with m = ⌈n/C_0⌉, or Θ(log log n) via bound A if m is over-provisioned by a constant factor — and #Fb is then not O(n), though the exponent moves to 8ω+2 up to polylog in the first case and stays 8ω+1 up to polylog in the second); under the searched-coset reading, which the text does not describe but which costs no more than building Fb, it fails (constant C_0 is available at every C_0 ≥ 1); and under no reading does Theorem 1 become non-polynomial.**

### B2(4) Does anything in ARM C contradict a published result?

**No.** Theorem 1 is an O(·) statement, conditional on the first-fall-degree assumption, with unstated constant and n_0 and with its parameter C_0 specified only as a "suitable constant"; by the hypothesis's own `quantifier_order` no finite table can contradict it, and ARM C does not try to — it derives what "suitable" must mean under HEUR-1 and follows the consequence, which is a polynomial cost with an exponent refined from 8ω+1 to 8ω+2 (up to polylog) under one reading and left at 8ω+1 (up to polylog) under two others. That is a critique of the theorem's parameter regime and of the sentence "#Fb = O(n)" at l. 764, not a contradiction of a proven result; the producer proposes no non-polynomiality; the enumeration (28 cells, n ≤ 20) is a check of HEUR-1's binomial model against a null and reaches no verdict. Trigger (b)'s second clause is not met, and the Coordinator's expectation ("NO") is confirmed.

### B2 — verdict: **holds**

Breaking artifacts were "a derivation giving a non-polynomial cost under bound B" or "a demonstration that bound B's growth is not Θ(log n)"; neither exists — the derivation above gives Θ(n^{8ω+2}/polylog) and my integer bound B tracks log2 n − log2 log2 n within 0.8 over eighteen doublings. **Prior overturned in part**: the text does settle the reading more than the prior allowed (fixed cosets, repair by C_0), and a third, over-provisioning reading exists under which only bound A binds and the stated exponent survives up to polylog; the prior's conclusions (polynomial; trigger (b) not fired; searched reading dissolves both bounds; C1 reading-dependent; no published result contradicted) are all confirmed.

## 3. Proves-too-much object — **passed**

**This section imports and runs the producer's `experiments/EXP-SEMBIN-db9bc3/code/nagao_cost.py` (and its imports `semaev_repro.py`, `arm_c_coset.py`) as-is**, by the plan's instruction; script `scratch/proves_too_much.py`, output `scratch/proves_too_much.json`. The object: the producer's own charging at n = 571, C_0 = ⌈n/3⌉ = 191 (m = 3, N = 1142, #Fb ≈ 3·2^{191}) and C_0 = ⌈n/2⌉ = 286 (m = 2, N = 571, #Fb ≈ 2·2^{286} > 2^{285.3} = W), where "Nagao ahead" is known false at m = 2 by counting (more relations must be collected than vOW's whole work). Failure signature: `nagao_ahead = true` at m = 2 under any metric, or at m = 3 under a memory-charging metric by more than T6 can explain. Every metric × memory reading × monomial reading × ω is in the JSON; the ω = 2.807 binomial rows:

**m = 3, C_0 = 191** — `any_nagao_ahead: false`; minimum margin over all 48 rows **+172.3 bits**.

| metric | memory reading | T1 | T3 | T6 | time (T6 log-added) | T5 | Nagao | vOW | margin | margin without T6 |
|---|---|---|---|---|---|---|---|---|---|---|
| time_only | frozen / dense | 36.1 | 192.6 | 540.6 | 540.6 | 36.1 / 72.1 | 540.6 | 285.3 | +255.3 | +8.5 |
| T×M = AT | frozen | 36.1 | 192.6 | 540.6 | 540.6 | 36.1 | 576.6 | 297.1 | +279.6 | +32.8 |
| T×M = AT | dense | 36.1 | 192.6 | 540.6 | 540.6 | 72.1 | 612.7 | 297.1 | +315.6 | +68.9 |
| equal-rate | frozen / dense | 36.1 | 192.6 | 540.6 | 540.6 | 36.1 / 72.1 | 540.6 | 148.5 | +392.1 | +145.3 |

Without T6 the minimum over all rows is −7.0 bits, at ω = 2.376 under **time_only** (T3 + ω·T1 = 192.6 + 85.8 = 278.4 vs 285.3); under every *memory-charging* metric the no-T6 margin is positive (smallest: T×M frozen at ω = 2.376, 278.4 + 36.1 = 314.5 vs 297.1, +17.4). The plan's m = 3 expectation — "time dominated by T3 + ω log2 C(2n+4,4) and should sit near or above vOW" — is met: +8.5 at ω = 2.807 without T6; T6 = ω·T3 = 2^{540.6} then dominates.

**m = 2, C_0 = 286** — `any_nagao_ahead: false`; minimum margin over all rows **+396.6 bits**; minimum *without T6* **+78.1** (time_only, ω = 2.376: T3 + ω·T1 = 287.0 + 76.3 = 363.3 vs 285.3): the counting argument is reproduced by T3 alone (287.0 > 285.3) before any linear algebra is charged.

**Reading.** The producer's accounting does not prove too much: at the parameter where Nagao-ahead is known false, #Fb enters through T3 (per-relation multiplicity) and T6 (ω·T3, log-added) and both grow as they must; there is no under-charged #Fb-dependent term to bound at the 120 cells. As a further check I swept C_0 at n = 571 with the producer's code (ω = 2.807, binomial): the dense T×M margin is negative from C_0 = 6 (−4.1) through C_0 = 64 (−17.9), **most negative at C_0 = 32 (−28.3 bits, m = 18)**, and positive from C_0 = 96 (+62.3) as T6 overtakes the decompose term; time-only is negative through C_0 = 96 (−8.6) and positive at 128. The grid's C_0 ≤ 16 therefore understates the model's own deepest dense-reading margin at n = 571 by about 5 bits (−23.2 on grid at C_0 = 16 vs −28.3 off grid); the d_F 4→5 T×M rise at C_0 = 32 (N = 9707) is ≈ 41 bits, so that deeper margin is still inside one degree of slack. Recorded in §4.

## 4. Anything unexpected

1. **Dense width² is the ceiling of the coherent memory readings, not a midpoint.** T×M = r^ω D² is monotone in the row count r of the eliminated matrix, so no coherent reading of Lemma 2 charges more memory-time than the producer's dense reading, and the cheaper coherent readings (one-step rectangular, r = N(N+1)) would deepen the n = 571 flags to −84 bits and restore the n = 409 flags (−15.7 at C_0 = 8, ω = 2.807). They are not adoptable because they assert an F4 shape (IMP-SEMBIN-ENGINE), but the Coordinator should know that "a more honest memory model" cannot be the route by which P3 is rescued at n = 571; only the O(·) constant and the degree grant can.
2. **Off-grid C_0 window.** The producer's declared C_0 range stops at 16; the model's dense T×M margin at ω = 2.807 keeps falling to −28.3 bits at C_0 ≈ 32 (m = 18) before T6 takes over at C_0 ≈ 96 (§3). The headline "−10.6 at C_0 = 8" is a grid artifact of where the grid stopped, not of the model. Still inside one degree of slack.
3. **A third reading of the parenthesis** — over-provision m by the constant factor 1 + δ(C_0)/C_0 (+ Θ(√n) for the CLT fluctuation) with cosets fixed — leaves only bound A binding, so C_0 = Θ(log log n) and the stated exponent 8ω+1 survives up to polylog factors (§2.2). C1's exponent conclusion depends on which of three readings is taken; its "not a constant" conclusion survives two of them.
4. **The text is less silent than the prior thought** (§2.2): the v_i are fixed by disjointness only and the remedy for both failure modes is C_0. The fixed-coset reading is Nagao's; searching is a repair.
5. **Solution harvest.** At the grid C_0 the expected number of decompositions per trial is 2^{4.8}–2^{9.0}, all delivered by the same Gröbner basis; Algorithm 2 as written and the run's T4 convention take one relation per R. That is a 5–9-bit uncharged term *in Nagao's favour* at n = 571 — it cannot erase a flag, but it means the erasing-constant table (§1.2) is slightly generous to erasure.
6. **The generic baseline over-charges vOW on Koblitz curves** by the Frobenius √n (4.58 bits at n = 571) plus the cofactor (0.5 B / 1.0 K bits); this erases the six thinnest dense entries (margins ≤ 4.4 bits) *for a K-curve* and none of the headlines (§1.4). The run's baseline is curve-agnostic by design; this is recorded so nobody reads a −2.1-bit entry as robust.
7. **Numerical exponent under bound B** reads as ≈ 8ω + 1.0–1.5 at n ≤ 2^25 although the asymptotic exponent is 8ω + 2, because the (log n)^{−(4ω+2)} cofactor's local slope is ≈ −1 per doubling in that range (§2.1).
8. **Key-name mismatch between producer artifacts.** `cost-surface.json` names the monomial-count reading `monomial_count_reading`; `known-false-dF5.json` names the same field `reading`. Cosmetic, but it silently broke a cross-file lookup in my own first-incarnation script (the failure was swallowed by a `try/except` and surfaced as `None`); any downstream consumer joining the two files should be told. Not a defect of the run's arithmetic.
9. **Equal-rate survivors are within 2.5 bits of zero** (−1.1 / −2.0 / −2.5 at ω = 2.376, C_0 ≥ 10) — indistinguishable from a tie at the model's precision; the producer reports them as flags and the plan counts them, which is correct bookkeeping, but they carry no information the T×M flags do not.
10. **T6 headroom** at every bound-B cell at n = 571: T6 − time ≤ −95.8 bits (binomial). Negligible everywhere, as N4's prior expected (N4 is not my joint; the number fell out of my recomputation).

## 5. Every source path read

- `AGENTS.md`; `CLAUDE.md`; `agents/validator.md`; `.claude/agents/validator.md`; `.claude/agents/validator-breakthrough.md`
- `docs/inventor-protocol.md` (sections 3–7); `docs/claims-and-verification.md` (in full); `docs/target-result-profile.md` (Part A cost-honesty items l. 185–209 and the profile rule; checklist items C13–C16 by heading)
- `coordination/review/sembin-20260913-251fd3/review-plan.yaml` (in full)
- `coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/dispatch_queue.json` (my task entry and top-level keys)
- `experiments/EXP-SEMBIN-db9bc3/specification.yaml`
- `experiments/EXP-SEMBIN-db9bc3/code/nagao_cost.py`, `semaev_repro.py`, `arm_c_coset.py` (in full); `arm_i_independent_memory.py`, `selftest.py` (in full); `run_experiment.py` (ARM N surface/crossover/escalation-flag construction l. 309–422 and `main` l. 763–861 — the flag filter at l. 383 is the one my own filter reproduces; other arms skimmed by symbol list only)
- `experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/task-report.md` (in full); `cost-surface.json` (all top-level blocks, `vow_baseline`, `column_definitions`, `unit_conversion_sensitivity`, the 242-entry flag list, cells — every committed-ω cell consumed programmatically); `known-false-dF5.json` (all top-level blocks; every cell consumed programmatically); `c0-lower-bound.json` (all top-level blocks incl. `closed_forms`, `bounds_at_each_n_p`, `order_of_growth_table_p2`, `headline_p2`, enumeration summary); `matched-nulls.json` (top-level blocks and one cell — ARM M is joint N3's); `concrete-cost.yaml` (header, unit and comparator declarations, structure and one parameter set — a re-rendering of cost-surface.json, not separately verified); `manifest.yaml` (structure and inference/attempt fields)
- `ledger/hypotheses/H-SEMBIN-4a80f3.yaml`
- `ledger/evidence/EV-SEMBIN-71e5cd.yaml`; `ledger/corrections/CORR-20260913-53739b.yaml`
- `experiments/EXP-SEMBIN-f4a17b/specification.yaml` (metric definitions)
- `inputs/NAGAO-2015-984/paper_fulltext.md` (header index; Sections 1–7; Assumption 1; Lemma 2; Definitions 5–8; Propositions 2–6; Theorem 1; Algorithm 2; footnote 6)
- `inputs/SEMAEV-2015-310/paper_fulltext.md` (Section 4.3 and eq. (11) only, l. 394–431, for HEUR-2's origin; nothing else in that paper was read for this review)
- Under my own write scope: `report.md` (earlier draft), `attestation.yaml` (earlier draft), `scratch/b1_recompute.py`, `scratch/b2_exponent.py`, `scratch/proves_too_much.py` (earlier incarnation; re-read and re-run), `scratch/b1_extras.py` (written this session), and the JSON/MD outputs they produced this session.
- `tools/check_review_independence.py` (attestation-parsing and blindness/re-derivation checks, l. 74–175 and 240–325) — read only to make `attestation.yaml` machine-readable; not a review source.
- Git: `git log`, `git diff --stat a2cdafc67 HEAD -- experiments/EXP-SEMBIN-db9bc3`, `git status --short` on this task directory.

Not read: `coordination/review/sembin-20260913-251fd3/TASK-20260913-3b91d0/`, `.../TASK-20260913-7fb774/`, `coordination/bus/`.

## 6. Independent recomputation (tier output discipline)

**Recomputed myself, from the definitions, with code sharing nothing with the producer's** (`scratch/b1_recompute.py`, `b1_extras.py`, `b2_exponent.py`): T1–T6 at every committed-ω cell; all four metrics and the vOW Pareto minimum; every margin (3,840 values, worst 1.2e-13 bits); the flag counts 242/180/120; ARM C bounds A and B at every label and their growth over n = 2^7…2^25; the d_F 4→5 rise at every surviving cell (equals `known-false-dF5.json` exactly); the erasing constants; the unit conversions; the omitted-term bounds; the coherent r-family; the Koblitz/cofactor baseline corrections; the exponent under bound B and the fixed-C_0 asymptotics; the searched-coset selection cost.

**Re-verified with a disjoint checker:** the Jensen deficit δ(C_0) — exact pmf via `lgamma` in log space (mine) vs the producer's cumulative log-factorial table (theirs); agreement to 1e-13 bits in every T4.

**Run with the producer's code, deliberately and by instruction:** the proves-too-much object and the off-grid C_0 sweep (`scratch/proves_too_much.py`), which are *about* the producer's charging.

**Taken on the producer's word (not recomputed here):** ARM R's 107-cell reproduction gate and ARM I's independent memory term (joint N3, not mine); the exact-enumeration cells of ARM C (joint N1, not mine); the manifest hashes against the snapshot receipt (N3); the identity of AT and T×M under the committed metric definitions (N2). I read these and found nothing that bears on B1/B2, but I did not verify them and this report does not rest on them.

**Not verifiable by anyone in this program, and stated as grants:** Proposition 5 (proof omitted in the source) and Assumption 1 in its strong form; Lemma 2's absorbed constant; HEUR-1 and HEUR-2 beyond the n ≤ 20 enumeration.
