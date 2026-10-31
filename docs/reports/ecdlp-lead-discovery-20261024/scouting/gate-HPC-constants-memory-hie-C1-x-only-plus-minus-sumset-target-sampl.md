# Novelty gate N1-N4: HPC constants, C1 "x-only plus-minus sumset target sampler for prime m=2 IC, priced against a batched rho in the same unit"

Date of gate: 2026-10-25. Field key: HPC constants (round 2). Read-only inputs; nothing inside the repositories was edited, created or committed. Everything this gate wrote lives under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/` (raw outputs under `hpcC1_raw/`).

## 0. Verdict

**verdict: `advances_lead`**, lead = **LEAD-ICP-prime-ic-constant-engineering** (disposition `open_next_step`).

One-paragraph reason. The primitive is not new: one shared denominator gives x(A+B) and x(A-B), Montgomery batches the inversion (KR-RHO-fbd582, KR-RHO-cb1c58; Galbraith-Wang-Zhang's own BSGS giant-step block schedule "compute S +- P', then S = S + P''" with x-coordinates only, retrieved from Galbraith's slides, see 3.2). The C1 sampler is the two-list (grid) version of that schedule, so the mechanism is `known_result` at the level of mathematics. What is not in the atlas, the frontier map, the ledger index or the code is its use as the *target source of prime-field index-calculus relation collection*, priced in one unit against lock-stepped batched rho. That slot belongs to an open lead whose stated job is to collect verified constant-factor gains from exactly this family of tricks (Montgomery simultaneous inversion is in its mechanism text), so C1 is a sharper next step for it, not a new lead and not a duplicate. The novelty is the arm and the measurement; none is claimed or available for the mathematics. SO-TABLE and SO-GEN are not escaped (C1 itself says so) and nothing here should be filed as an exponent lever.

Provenance legend used below: `retrieved` = I read it in this session from the file or URL named; `recalled` = from memory, not re-read; `derived` = my own algebra here; `candidate-stated` = taken from the candidate text and not re-measured by me. All performance numbers about C1 (x0.67, x0.59, 8.5, 12.5, 13.46 and the intervals) are `candidate-stated` PREDICTIONS from the candidate's `derive_c1.py`; I read `scout/hpc-r2/derive_c1.out`: across its five parameter sets it shows pairset S x0.653-0.701 and relation phase x0.565-0.607 against walk lanes, IC/batched-rho 8.02-9.12, walk lanes 11.94-13.10, GAE board 13.46, so the point values and the upper interval ends match the candidate text; the lower ends (0.60 for S, 0.51 for the relation phase) are not visible in that file and I did not trace them. I did not rerun the script and did not produce any measurement.

## 1. What was and was not produced here

| item | status |
|---|---|
| 8 atlas `--match` runs (3 given phrasings + 5 own), top hits of each read at the lead-YAML level | produced, raw in Appendix A |
| 7 frontier-map `--match` runs | produced, raw in Appendix B |
| ledger index sweeps (35 terms over proposals.jsonl + hypotheses.jsonl) and 3 full-record opens | produced, raw in Appendix C |
| repo snapshot greps (`/private/tmp/.../scratchpad/crypto-main`) for PairSet / sumset / side-target / plus-minus primitive | produced, results in 2.5 and 4 |
| algebra check of the I+2M+2S claim | derived here, matches the slides (3.2) |
| any measurement of C1, any run of ecbench/callgrind | NOT produced; none attempted |
| GWZ full text | NOT retrieved (PDF returned HTTP 403); abstract page and Galbraith's slides retrieved |

## 2. N1 Atlas collision

### 2.1 Runs and top hits (rank, score, id, disposition)

| run | phrase | top hits (score) |
|---|---|---|
| N1-a | given phrasing 1 (x-only plus-minus sumset ...) | LEAD-RHO-correlated-walks-shared-sums (18, closed_obstructed); LEAD-ICP-residual-partial-relations (13, open_next_step); KR-IC-5931ee (12); KR-IC-a4dd54 (12); LEAD-EXO-split-jacobian-projection (12, closed_obstructed); then LEAD-ICP-prime-ic-constant-engineering (12), LEAD-EXO-curve-model-representation (11), LEAD-ICE-gpu-rootfind-oracle (11) |
| N1-b | given phrasing 2 (two targets per inversion without y) | KR-IC-5931ee (15); KR-IC-a4dd54 (12); LEAD-ICP-retained-setup-online (12, closed_dominated); KR-IC-9e610d (11); LEAD-EXO-global-lift-height (11, open_next_step); LEAD-ICB-multi-target-and-portfolio (11); LEAD-ICP-lattice-ic-relation-construction (10); LEAD-ICP-prime-ic-constant-engineering (10) |
| N1-c | given phrasing 3 (shared inversion P+Q, P-Q; free P-Q beyond best-of) | LEAD-RHO-batched-inversion-shared-pm (27, closed_known); KR-RHO-fbd582 (16); LEAD-ICB-multi-target-and-portfolio (14); KR-IC-5931ee (12); KR-IC-a4dd54 (12); LEAD-ICE-generic-oracle-arity-cost-floor (12); LEAD-RHO-correlated-walks-shared-sums (12) |
| N1-d | own: batched Montgomery inversion affine addition relation phase prime IC constant factor | LEAD-ICP-prime-ic-constant-engineering (25, open_next_step); LEAD-RHO-batched-inversion-shared-pm (25); LEAD-ICP-isogeny-transported-relation-yield (18, open_blocked); KR-IC-5931ee (16); KR-RHO-cb1c58 (16); LEAD-EXO-curve-model-representation (15); LEAD-ICP-lattice-ic-relation-construction (15); LEAD-ICP-algebraic-membership-factor-base (14) |
| N1-e | own: BSGS sumset pair sums and differences as IC targets | LEAD-RHO-correlated-walks-shared-sums (16); LEAD-ICP-lattice-ic-relation-construction (15); LEAD-RHO-bsgs-family-memory (14, closed_known); KR-IC-5931ee (12); KR-IC-a4dd54 (12); then isogeny-transported (12), prime-ic-constant-engineering (12), multi-target (11) |
| N1-f | own: prime IC target source, one batched affine addition per target, lanes, stride | LEAD-RHO-batched-inversion-shared-pm (21); LEAD-RHO-native-step-cost (12, open_next_step); LEAD-STR-class-representative-ic-selection (12, open_next_step); KR-RHO-cb1c58 (11); LEAD-ICB-koblitz-rho-reference (11, open_next_step) |
| N1-g | own: Galbraith Wang Zhang X-Y with X+Y | LEAD-RHO-bsgs-family-memory (10); KR-RHO-cd0049 (6); KR-RHO-fbd582 (6); KR-RHO-fbd7b1 (6); LEAD-EXO-lossy-object-propagation (4, open_next_step) |
| N1-h | own: stride renew cheaper target generator for the relation loop | LEAD-ICP-retained-setup-online (17); LEAD-ICP-isogeny-transported-relation-yield (16); LEAD-ICP-lattice-ic-relation-construction (15); LEAD-ICE-gpu-rootfind-oracle (14); LEAD-RHO-correlated-walks-shared-sums (13) |

Lexical remark: the matcher keys on words (shared inversion, P+Q, pair, sums, batched), so runs a, b, e, h return topically near but mostly unrelated leads (large-prime variation, split Jacobian, global lift, lattice). Runs c, d, f are the informative ones. A lexical miss proves nothing, so the semantic check below does not rest on the scores.

### 2.2 Hit-by-hit reading (YAML opened; mechanism / obstruction / forecloses)

**LEAD-ICP-prime-ic-constant-engineering** (ic-prime, `open_next_step`). Closest lead; C1 targets its exact bottleneck. Its mechanism: "Montgomery u64 fields, simultaneous inversion, blocked pair-table construction, a fixed-window repeated-base generator for aP+bQ, CADO-style filtering and an automatic stage planner lower the constant of each Table B phase (relations 68-93 % of S, factor base 5-30 %). Each verified gain is an improvement over the current IC baseline under the owner's success criterion even though the exponent is fixed." Its next_action: validation gate on the eight Table B prime rows, "then run the unimplemented two-level target batching (step 1024 targets in lock-step so the R <- R + G inverse is amortised) as a paired ecbench arm against the current folded/walked m = 2 recipe at fp20-fp28." Discriminates: a paired ratio with the interval below 1 at every size is a measured constant improvement; an interval spanning 1 closes the batching item. Its `forecloses` list contains "batched inversion speeds up prime index calculus" and "Montgomery native arithmetic for the relation search", which match C1 lexically, but the disposition is open and the lead's own next step is a batching arm, so these phrases are scope labels for the lead, not a closure. best_measured on this lead is the fixed-window aP+bQ generator, 1.161 [1.127, 1.198] full-solve (EV-ICPERF-92c130): the closest precedent for "cheaper target generation" inside the same lead. C1 neither repeats that nor the lead's lock-step walk arm; it adds a different target source and a same-unit rho comparison. **Verdict-bearing: C1 is a sharper next step for this open lead.**

**LEAD-RHO-batched-inversion-shared-pm** (generic, `closed_known`, obstruction kind `literature`). Mechanism: Montgomery's trick plus the free x(P-Q) beside x(P+Q) "make affine parallel rho cheap per step". Obstruction statement: "Known (KR-RHO-cb1c58, KR-RHO-fbd582) and reproduced: batch inversion proved correct in Lean (rho_assurance); GPU NIST W-sweep 1.52x/2.61x cumulative with by-reference inversion; plain-step cost falls with batch size (179 ns at 1024 walks on P-256). The remaining use of the free P-Q is the best-of lead." revisit_when: an inversion-free step cheaper than 1I/n + 3M per walk. forecloses: "Montgomery trick for rho", "simultaneous inversion across walks", "shared inversion for P+Q and P-Q", "batched affine addition". The last two phrases match C1's ingredient. The row has no Scope clause and its subject is the rho step; the sentence "the remaining use of the free P-Q is the best-of lead" is stated inside the rho family. C1 contests that sentence only if the sentence is read universally; read as rho-scoped it is untouched, because C1 makes no claim about any walk step and needs neither an inversion-free step nor a best-of rule. I do NOT claim C1 answers a closed obstruction here: the ingredient is the known one, and the row is the reason the verdict is not `new`. (Coordinator note, not an edit: if the sentence is meant universally, the row and C1 disagree and C1 should be dispositioned as "known primitive, new slot" rather than as a contest.)

**LEAD-RHO-correlated-walks-shared-sums** (generic, `closed_obstructed`, kind `proof`; top hit of run a, so read most carefully). Semantic overlap: "shared precomputed sums across walks", "pair table R_i + R_j steps". Statement: "With a shared index sequence every walk adds the same R_i at every step, so pairwise differences P_i - P_j are invariant and two walks can never meet unless they started equal; measured 0.073x [0.070, 0.076] (176/1000 censored, a lower bound on the loss). A pair table still costs one addition per step: 1.027 [0.982, 1.073]. Changing the representative rule per epoch breaks walk determinism: 0.83x [0.79, 0.87], worse than no negation map. Scope: any parallel rho." What it covers: sharing sums to avoid additions (no saving: one addition per pair, 1.027) and the collision-between-walks failure. What it does not cover: (i) C1 does not claim fewer additions; it claims a cheaper addition per emitted target (x-only, shared denominator, no y3, one inversion share for two outputs); (ii) the invariance obstruction needs walks that must meet, while IC targets probe a fixed table and a repeat is only a guard event; (iii) the Scope clause is parallel rho. Residual overlap that the pair-table result does bear on: the arithmetic per pair is still one addition-equivalent, so the gain is bounded by the cost ratio of an x-only pair against a full batched add (see H-G4). Not a duplicate.

**LEAD-ICP-generic-table-decomposition** (SO-TABLE, `closed_obstructed`, kind `theorem`; not a top-5 hit but named by the candidate). Quoted obstruction: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup) ... Scope: any generic (enumeration/table) decomposition over F_p." forecloses includes "faster S_3 root finding or batched subtraction makes prime IC sub-rho". C1 sits inside this Scope and does not claim to leave it; it claims only a constant on the relation phase and itself predicts IC/rho of 8.5 against batched rho. Not escaped, and not claimed to be.

**LEAD-RHO-generic-sqrt-lower-bound** (SO-GEN, `closed_obstructed`, `theorem`). Quoted: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group ... Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r." Not escaped; C1 is a constant.

**LEAD-ICB-multi-target-and-portfolio** (SO-MULTI, `closed_obstructed`, `theorem`). Quoted: "The multi-instance generic bound (L logarithms cost >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up, and batch rho (Kuhn-Struik) attains it; the L^-1 amortisation applies only to the online part after a set-up that obeys the same bound." C1 solves one target; the "L logarithms" premise is not entered. (Do not confuse "many targets inside one IC relation phase" with "many logarithms": the relation targets are auxiliary aP+bQ points, not separate ECDLP instances, so the multi-instance bound is not the relevant one.) Fine.

**LEAD-ICE-gpu-rootfind-oracle** (`open_blocked`). Its mechanism text is the sibling statement: "one Montgomery-batched inversion per target ... It can only lower the relation-phase constant (68-95% of Table B S); a matched comparison needs rho on the same GPU". Same bottleneck class (relation-phase constant), but its inversion is per target over the factor-base axis (the sweep side), C1's is over the target axis. Complementary, not the same.

**LEAD-ICP-residual-partial-relations** (`open_next_step`). Mechanism: "At m = 2 the signed-sum sweep computes 2B residual x-coordinates x(R +/- P_v) per target"; large-prime crediting. Shows the +-pair x-coordinate is already an object of the IC engine on the factor-base side. It concerns what is done with residuals, not target generation. No overlap in mechanism.

**LEAD-EXO-curve-model-representation** (`closed_obstructed`, kind `measured`). forecloses "Montgomery x-only factor base", "Kummer line coordinate change". Its obstruction closes the exponent lever of model changes and ends: "revisit_when: ... or a constant-factor model gain is wanted inside an IC engine (then it belongs to ic-prime)". That clause routes exactly this kind of constant to ic-prime, i.e. to LEAD-ICP-prime-ic-constant-engineering. C1 does not change the factor base or the summation-polynomial degree; it is not the model lever.

**LEAD-ICP-retained-setup-online** (`closed_dominated`), **LEAD-ICE-generic-oracle-arity-cost-floor** (`closed_obstructed`), **LEAD-ICP-algebraic-membership-factor-base** (`closed_obstructed`, SO-ALGFB), **LEAD-EXO-split-jacobian-projection**, **LEAD-EXO-global-lift-height**, **LEAD-ICP-lattice-ic-relation-construction**, **LEAD-ICP-isogeny-transported-relation-yield**, **LEAD-STR-class-representative-ic-selection**, **LEAD-EXO-lossy-object-propagation**, **LEAD-RHO-native-step-cost**, **LEAD-RHO-cheaper-step-primitives**: opened; each is a different mechanism (retained advice, free-oracle arity floor, bounded-degree factor base, genus-2 embedding, global lifts, lattice relation construction, isogeny transport, class-representative choice, lossy tracked objects, rho step instruction counts, tag tracing/halving).

**LEAD-ICB-koblitz-rho-reference** (ic-binary, `open_next_step`; 5th hit of run N1-f; YAML opened in the second pass of this gate). Mechanism: "Every gap in this family divides by a rho reference ... Strengthening the reference is accounting, not an IC improvement, but it fixes the distance remaining." forecloses: "Table A rho reference is fair", "no matched rho for ECC2K-130 IC lanes", "Frobenius-class walk constant sqrt(2n)". Binary/Koblitz rho pricing for Table A; no target-generation mechanism. Same spirit as C1's "price rho in the same unit" demand, different curve family and object; not a match. C1 touches none of their objects; two relevant constraints carried over from them: closed_dominated retained-setup says any IC online claim must be compared with Bernstein-Lange preprocessing rho at equal advice (C1 is a cold single-target relation-phase constant, so this does not bind, but a write-up must not drift into online/retained framing), and native-step-cost says rho constants in GAE understate native cost, which supports C1's choice to price both sides in one field-op unit.

**LEAD-RHO-bsgs-family-memory** (`closed_known`) and **LEAD-RHO-best-of-candidates-indegree** (`open_next_step`). bsgs-family-memory: "bsgs.negation is the prime-toy ops leader at 1.100 [0.978, 1.225] x sqrt(pi/4) but needs 0.50 sqrt(r) table entries"; forecloses BSGS-beats-rho. It is the BSGS family C1's schedule descends from (see 3.2); C1 makes no claim about BSGS vs rho. best-of: the open lead on "the better of P+R and P-R" in rho, with net per-step 0.95 at 1024 walks per inversion; it is the "best-of lead" the candidate's wording refers to. Different object (selection among two candidates inside a walk), C1 takes both as separate probes.

### 2.3 What C1 does that the hits' `forecloses` phrases do not cover

The union of relevant forecloses phrases: "batched inversion speeds up prime index calculus"; "shared inversion for P+Q and P-Q"; "batched affine addition"; "shared precomputed sums across walks"; "pair table R_i + R_j steps"; "faster S_3 root finding or batched subtraction makes prime IC sub-rho"; "Montgomery x-only factor base". Not covered by any of them, as far as the atlas rows say:
1. Target-side use of the +- pair inside IC relation collection (every recorded IC use is factor-base side: the signed-sum sweep, the pair table, GPU cells).
2. A two-list sumset target source with no successor chain, so that the batch width is decoupled from the number of walk lanes.
3. Pricing the whole relation phase and a lock-stepped batched rho in one field-op unit (this is what the equal-prefix FIXED_PREFIX_FRESH protocol and the "C2 unit" are for).
The first two are an arm to implement; the third is a measurement protocol. None is a mechanism the atlas lacks a sentence about at the mathematical level (3.1, 3.2).

What the phrases DO cover and C1 re-enters: batching as such. If the coordinator's reading of "batched inversion speeds up prime index calculus" in the forecloses list is "no such speed-up is available", it conflicts with the lead's own open next step; I read it as a scope label (see above).

### 2.4 Standing obstructions touched (candidate's list: SO-TABLE, SO-GEN, SO-WALK, SO-MULTI)

SO-TABLE: inside Scope (quoted in 2.2); not escaped; the candidate says so. SO-GEN: same. SO-WALK: the closed row's Scope is "any parallel rho"; C1 is not rho, and its sums are probed against a fixed table (premise escaped by non-applicability, not by a new argument). SO-MULTI: one logarithm; premise not entered. I add no other SO: C1 does not touch SO-ENDO (it keeps Z/N as the only operation group on the relation vector), SO-ISO, SO-ALGFB (factor base unchanged; KN-OPEN-020 class untouched), SO-DECK, SO-CHEON.

### 2.5 Repository facts bearing on the collision (snapshot `scratchpad/crypto-main`, `retrieved` by grep and reading)

- `TargetSource` in `src/cryptanalysis/ic_boundary.rs` has Random, RandomUnguarded, Walk, WalkPrimeFast, WalkPrimeLanes{lanes, batched}, WalkSharedJumps, Stride, StrideRenew. No PairSet, no side-target co-arm, no "sumset" anywhere in source or research notes outside unrelated contexts.
- `PrimeField` batch API: `add_many_batched` advances lanes with one Montgomery inversion across ordinary additions and returns full points (`add_with_inv`, so y is computed); there is no plus-minus-sharing primitive in `src/cryptanalysis/prime_fast.rs`. C1's primitive is new code.
- The collector's guard hashes every presented point (`seen.insert(g.key(&point))`), so each emitted x-value pays a guard probe regardless of how it was produced; C1 acknowledges two guard probes per pair.
- Stride and StrideRenew (research/ecbench_rootfind_speedup_20261014/README.md): "About half of the counted cost of the best complete rootfind arm ... was the relation loop's *target generator*"; `stride-renew` measured 0.531 [0.506, 0.557] of walk S at n = 13 and 0.835 [0.741, 0.943] at n = 19, on Koblitz a=0 toy curves, in counted GAE, with the caveat that both arms are lower bounds. These are binary-lane results and no atlas lead records them (a gap in the atlas, see H-G1). They are the nearest measured competitor *in the same slot*, and they are not among C1's arms.
- Lock-stepped lanes (4, 8, 16) are implemented and sealed (research/ecbench_rootfinding_lanes_20261013): batch-8 at 7.463 times rho's cold counted GAE (interval 5.817-9.626), "a lower-bound comparison with unpriced native operations"; the report names the remaining gate (serialise native field-op counters, price in a common unit). C1's "C2 unit" is that gate. So the lead's "unimplemented two-level target batching" at width 1024 is not what exists (width <= 16); C1 does not duplicate the implemented arms.

## 3. N2 Known results

### 3.1 Frontier-map hits

KR-RHO-fbd582 [known_mechanism / proven], "Nearly free P-Q alongside P+Q": "With a shared inversion, x(P-Q) costs little extra once x(P+Q) is computed; Galbraith-Wang-Zhang use this to speed baby-step giant-step, grumpy giants and interval search." KR-RHO-cb1c58 [known_mechanism / proven], simultaneous (batched) inversion. KR-IC-5931ee [known_negative / proven]: naive Semaev IC over F_p does not beat generic methods; scoped to the exponent, C1 claims none. KR-IC-9e610d (survey consensus): no prime-field attack better than rho; consistent. KR-RHO-cd0049 and KR-RHO-fbd7b1 (negation BSGS toy measurement; grumpy giants) belong to the BSGS family. No KR concerns IC relation-collection target generation or a sumset target source. Disposition of every other KR row that appeared in a top-8 list of runs N2-a..g (each YAML opened in the second pass of this gate, claim and forecloses read): KR-IC-a4dd54 [known_bound/heuristic], hyperelliptic IC with double large primes, O~(q^{2-2/g}), genus threshold: different mechanism (genus >= 3 Jacobians; SO-COVER), no overlap. KR-IC-ae532f [record/reported], largest practical algebraic ECDLP computations (Joux-Vitse F_{p^6} cover-and-decomposition; GLS-assisted GHS descent): different mechanism; its last sentence (no summation-polynomial method has beaten rho on a cryptographic-size prime-field curve) is consistent with C1 making no exponent claim. KR-IC-46d822 [known_bound/heuristic], Gaudry decomposition over E(F_{q^n}), n fixed: extension-field IC, different object. KR-IC-b0fcda [known_mechanism/heuristic], Frobenius-invariant factor bases for subfield curves: Koblitz factor-base symmetry, C1 leaves the factor base unchanged and is prime-field. KR-RHO-6654ba [known_mechanism/reported], point halving as a rho step on binary curves: binary-only cheaper rho step; no target-generation role. KR-IC-1fcdbc [known_negative/measured], characteristic-2 summation algorithms slower than rho: binary exponent evidence; no overlap. KR-IC-64659b [known_bound/proven], Diem subexponential ECDLP over E(F_{q^n}) for suitable n: extension fields; no overlap. So the only KR rows whose mechanism C1 re-uses are fbd582 and cb1c58, and the only ones whose scope it sits inside are 5931ee and 9e610d.

Under the rule "a KR hit means known_result unless you can state exactly what is new", I state the split:

NOT new (known, with provenance):
- the shared denominator and the operation counts (3.2);
- Montgomery batching of the inversion (KR-RHO-cb1c58; Montgomery 1987, recalled);
- x-only storage with giant steps taken in blocks, "S +- P'" then "S = S + P''" (Galbraith slides, retrieved);
- the program's own identification of the folded m = 2 engine as BSGS on the quotient (IDEA-20261015-7a3c9e, Koblitz case, ledger proposal, status proposed): under that reading C1 is the GWZ giant-step schedule applied to an engine the program already files as BSGS-like.

New in the sense of "not found in any of the four sources I searched" (atlas, frontier map, ledger index, code):
- the two-list grid A_i +- B_k with J + K precomputed points and no chain, as the target source of a prime-field IC relation phase (GWZ's block schedule keeps a chain S = S + P'' that needs y and one more inversion share per iteration; the grid drops it);
- sign resolution only on hits (about 70 per solve per the candidate), one add each;
- same-unit pricing against a lock-stepped batched rho.
The honest classification is "adaptation of a known primitive into a new slot", which is what `advances_lead` encodes. If the coordinator's rule is that adaptation of a KR primitive is `known_result` even when the slot is open, the verdict would flip; I judge the lead's explicit scope (verified constant gains under the owner's criterion) to make the slot-level delta the point of the lead.

### 3.2 External citation check (provenance)

- Galbraith, Wang, Zhang, ePrint 2015/605: **retrieved** (eprint.iacr.org/2015/605 abstract page, 2026-10-25). Title, authors as in the candidate. The abstract sentence the candidate quotes is there: for any two elliptic curve points X and Y, one can efficiently get X-Y when computing X+Y; the abstract also states the combination with the negation map and Montgomery's simultaneous inversion, and BSGS/grumpy-giants/interval results. The abstract does not mention index calculus. The full PDF returned HTTP 403, so the full text was not read: any claim about GWZ internals beyond the abstract rests on the slides below.
- Galbraith, "Degustazione of the ECDLP" (Ascona slides, www.math.auckland.ac.nz/~sgal018/ascona.pdf, joint with Wang and Zhang): **retrieved** (PDF saved by the fetch tool, text extracted locally with pdftotext into hpcC1_raw/ascona_untrusted/; treated as data). Slide "New method": P1+P2 in affine coordinates requires I + 2M + S; P1+P2 and P1-P2 together require I + 4M + 2S; "organise BSGS to store x-coordinates only and to compute the giant steps in blocks": with P' = N P and P'' = 3P', S = Q, at each iteration compute S +- P' and then S = S + P''. The slide ends with the question whether this works for Pollard rho (the best-of lead is the program's answer).
- **derived** here: with y dropped on both outputs the pair costs I + 2M + 2S (lambda+ = (y_B - y_A)/(x_B - x_A), lambda- = (-y_B - y_A)/(x_B - x_A), then x+- = lambda+-^2 - x_A - x_B). That is the slides' I + 4M + 2S minus the two y3 multiplications, consistent with the candidate's "I+2M+2S". With Montgomery batching of n pairs, I becomes I/n + 3M. Per emitted x-value: (3M + 2M + 2S)/2 = 2.5M + 1S against a batched full affine add 3M + 1M + 1S + 1M = 5M + 1S. Arithmetic-only ratio (S = M): 3.5/6 = 0.58, in line with the candidate's pairset-versus-batched-add figures in `derive_c1.out` (0.228 against 0.391 at M = 0.065, i.e. 0.58). This is the field-arithmetic share only; the end-to-end share is the experiment's question (H-G4).
- Montgomery 1987, "Speeding the Pollard and elliptic curve methods of factorization": **recalled**; no WebSearch/WebFetch verification attempted for it (the program's KR-RHO-cb1c58 records it as a known mechanism with `abstract_read` and `secondary_source` verification states).
- Prior-art search for IC relation collection using this trick: one standard WebSearch ("index calculus elliptic curve prime field relation search simultaneous inversion x(P+Q) x(P-Q) ...") returned only Vitse/Diem-era talks on extension-field IC and Semaev's naive IC, nothing on target generation or on batched relation search. One weak negative; it does not prove absence.

## 4. N3 Ledger

Sweeps (Appendix C): sumset, pair-sum, pairset, p-q, r-j, side target, target source, targetsource, walkprimelanes, walk lanes, lock-step, lockstep, galbraith-wang-zhang, galbraith/wang, fbd582, x(p-q), shared inversion, shared denominator, montgomery simultaneous (sweep 1); batch inversion, batched inversion, batched affine, simultaneous inversion, per inversion, two targets, x-only, walked target, r-adding, stride, target generation, target-generation, relation phase, icperf, double-ended, bsgs (sweep 2). Zero hits on: pairset, side target, target source, targetsource, walkprimelanes, walk lanes, lock-step, galbraith-wang-zhang, galbraith/wang, batched affine, simultaneous inversion, per inversion, target generation, double-ended, montgomery simultaneous. Hits on generic words (p-q, r-j, stride, bsgs, x-only) are overwhelmingly unrelated (ML-KEM, quantum, CSIDH, ECDLP chains); the ones that could be the same object:

| id | status | 100-char claim (index) | same object? |
|---|---|---|---|
| IDEA-20261006-a0e3bd | proposed | "On y^2 = x^3 + 5x + 7 over F_101, for each of 40 frozen pairs of affine points with distinct abscissae, the joint comput..." | No. Opened in full: counts inversions and multiplications for x(P+Q), x(P-Q) on 40 toy pairs (RQ-GRUMPY); the saving is "one saved inversion per pair ... a constant-factor field-arithmetic fact"; no IC target generation. It is the ledger ref of LEAD-RHO-batched-inversion-shared-pm. Same ingredient, rho/BSGS framing. |
| IDEA-20260926-d3c5a5 | proposed | "A BINARY PORT OF THE PRIME-FIELD MEET-IN-THE-MIDDLE ENGINE (table of tails keyed by abscissa, one shared inversion per pair)..." | No. Opened (filtered on inversion/target): the shared inversion yields F+S and F-S inside the table of tails and the per-target probes x(R - F); factor-base/table side, binary curves, solver-free oracle for measurement. It shows the +- pair is already used on the table side of the MITM engine in the program's own proposals; the target side is not. |
| IDEA-20261015-7a3c9e | proposed | "Orbit-folded m=2 Koblitz index calculus is baby-step giant-step on the quotient and sits on the Bernstein-Lange r/P law..." | Adjacent, not the same. Opened (first 60 lines): states probes per target = r/(A*#states) and that the folded engine is BSGS on the quotient; no target-generation change. It supports reading C1 as the GWZ giant-step schedule on an engine the program itself calls BSGS-like. |
| IDEA-20260926-c98e92 | proposed | "THE SAME-UNIT EXCHANGE RATE: 64-bit word operations per field multiplication, per affine group addition and per W_4 refutation on the archived RC-1 instances..." | Adjacent: the unit-pricing prerequisite (binary RC-1, not prime). This is the family of the "C2 unit" C1 depends on; not the same object as C1. Referenced by the lead. |
| H-ICPERF-a2284c | specified | "A fixed-window repeated-base generator for aP+bQ can reduce complete native toy-IC solve time on the fixed public workload..." | Same slot (target generation constant in prime IC), different mechanism (cached digit multiples for the Random source). Its measured result is the lead's best_measured (1.161). Not a duplicate; a precedent. |
| H-PFDR-011a4b, IDEA-20261017-90d9c5, IDEA-20260731-012 | proposed/adaptation | pair-sum coincidences; rho-trail harvest; large-prime variation | No: sumsets as occupancy statistics or table-memory tradeoffs, not a target source. |

Opened full records: 3 (IDEA-20261006-a0e3bd, IDEA-20260926-d3c5a5, IDEA-20261015-7a3c9e; the latter two read through filters/first lines). Plus the N4-named records (see 5). No ledger record is the same object as C1. The ledger index search proves little about unindexed free text, so this is a bounded negative.

## 5. N4 Notation change

Candidate pair: (R1 = x-coordinate of an affine short-Weierstrass point, Montgomery u64 limbs; Sigma = translation by the two precomputed lists, A_i = A_{i-1} + T and B_k = B_{k-1} + G', then the +- partner A_i - B_k; at the table side, translation by negation-folded factor-base pair sums), tracked object = the IC relation vector (factor-base coefficients plus the (a, b) coefficients of the presented point aG + bQ, carried exactly mod r).

Reading against the recorded results (all `retrieved`):

- **IDEA-20260806-c5d183 (Theorem A and the trichotomy).** A projection propagating under full translation is constant or injective on a prime-order group, so every non-trivial tracked object is partial-action (Class I, index calculus), branching (Class II, incl. Kummer pseudo-addition), or coordinate-dependent (Class III). Here: x is not translation-closed, x(A+B) is not a function of (x(A), x(B)); only the unordered pair {x(A+B), x(A-B)} is (branching b = 2, the Kummer pseudo-addition). C1 does not exploit that branching: it keeps y on the O(sqrt trials) base lists, so both signs are individually labelled, and its outputs are terminal probes, never fed forward. The "IC-only asymmetry" (targets need no y and no successor, a walk step does) is therefore the practical face of Theorem A, not a statement beyond it. C1 stays in Class I (translation by a proper subset, here the two lists) with the relation vector tracked injectively. No rigidity result is circumvented and none is claimed to be.
- **IDEA-20260901-863e36 (propagation = block systems of the operation group).** The x-projection's fibres are the {+1, -1} orbits, the standard multiplication-slice block system; C1 does not vary the group Gamma and adds no block system. The translation slice is the c5d183 case above.
- **KN-OPEN-020 (universal algebraic-factor-base no-go).** The factor base is unchanged (candidate states "no factor-base escape is claimed"); C1 supplies no description of a factor base, bounded-degree or otherwise, so the open class (high-degree, implicit-membership, target-dependent descriptions) is untouched in either direction.
- **KN-FIND-ffe1df Theorem C (exact sum-compatible filters with associativity give a homomorphism, impossible for prime N).** There is no bucket or filter function in C1; the combining rule is the group law, and the join A_i +- B_k = F_j +- F_l is a plain four-term collision under the generic bounds already recorded (SO-TABLE).

Conclusion: the pair is not a recorded rigidity result in new notation; it is also not a new rigidity escape. If a write-up presents "x-only" as a representation advantage it must state that y is retained on the level-1 lists.

## 6. Observations for whoever runs the first step (not verdict-bearing; numbered heuristics)

H-G1. Nearest measured competitor in the target-source slot is Stride/StrideRenew (one batched addition per target after four scalar multiplications of setup; 0.531 and 0.835 of walk S on binary toys). The candidate's arms (lanes 8/16, side target, pairset, batched rho) omit it. If `Stride` runs on the prime lanes it has the same lock-step batching available, so "pairset vs walk lanes" alone overstates the margin the slot offers. Cheap addition: a stride-on-prime-lanes arm. Code reading (`ic_boundary.rs`, retrieved, not executed): the Stride/StrideRenew branch of the collector uses the group-generic `g.add(&mut rel.group_ops, ...)` on one serial chain, is included in `is_guarded()` and excluded from `is_walk()`, and the prime lane adder (`native_lane_walk_adder`) is only attached for `WalkPrimeLanes`. So a serial Stride arm can be pointed at a prime group with no new collector code (whether it was ever run on a prime curve was not verified), whereas a lock-stepped multi-lane Stride (the like-for-like comparator for lanes and pairset) is new code.

H-G2. Sharing structure. Pairs (i,k), (i',k), (i,k'), (i',k') satisfy t_ik - t_i'k - t_ik' + t_i'k' = 0 identically, the pairset analogue of the "four-row dependency ... which cancels the target and pins nothing" that motivated StrideRenew (doc comment of `TargetSource::StrideRenew`, retrieved). My arithmetic, assuming independent hits with the candidate's counts (about 70 hits in about 32768 probes, J = K = 128, so roughly 2e-3 per probe): the expected number of rectangles with all four corners hit is about C(128,2)^2 x (2e-3)^4 ~ 1e-3. So the dependency is expected to be rare at those sizes; the candidate's H4 (independent rank per probe within +-5%) remains the right test, and the correlation between the two signs of one pair and between pairs sharing a base point should be reported separately rather than pooled. Labelled derived, not measured.

H-G3. A gain visible in instruction counts (Ir) may not be visible in the GAE board; the candidate's own outcomes table handles this ("expected by construction; no board move before the C2 unit exists"). Agreed.

H-G4. Dilution. The arithmetic share is 0.58 (3.2). The guard probe, hash, table lookup (3.70 ns), coordinate round trip (4.22 ns) and 8-16-wide scratch handling per emitted x-value are not reduced, and there are twice as many emitted values per arithmetic unit. The candidate's own risk note (ratio toward 0.8) is the right size of concern; the predicted x0.67 for S (versus x0.58 arithmetic) already includes some of it by construction in `derive_c1.py` (candidate-stated). Whether it survives is exactly the paired measurement.

H-G5. Adaptation label. In any record, cite GWZ's block giant-step schedule as the source of the structure and state C1 as the two-list version with sign resolved on hits; do not describe the primitive as new.

H-G6. The asymmetric claim "needs neither y nor a successor" holds for the outputs only. A call-count budget should include y for the 2(J+K) base points and the final sign-resolving add on each hit.

## 7. Disposition suggestion (coordinator's call; I changed nothing)

LEAD-ICP-prime-ic-constant-engineering stays `open_next_step`; C1's arms become an extension of its `next_action` (pairset, side target, stride-on-lanes, lock-stepped batched rho; equal-prefix protocol; field-op unit). The comparison to report is rank per priced cost, then complete cold S, and IC/batched-rho as the distance remaining, as the candidate already proposes. No row for SO-TABLE, SO-GEN, SO-WALK or SO-MULTI needs revisiting on the strength of C1. If the coordinator wants the atlas to stay consistent, the missing record is a lead for "target-source engineering" (Stride, StrideRenew, fixed-window generator, lanes), whose evidence is currently scattered across crypto research notes.


## APPENDIX A. Raw N1 outputs (python3 tools/lead_atlas.py --match "<phrase>")

### N1-a  phrase: x-only plus-minus sumset target sampler for prime-field index calculus: x(A_i + B_k) and x(A_i - B_k) from one shared inversion

```
   18  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   13  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
   12  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   11  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
   11  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```

### N1-b  phrase: generate two index calculus targets per field inversion without computing y

```
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   11  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   11  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   11  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
   10  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   10  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
```

### N1-c  phrase: shared inversion for P+Q and P-Q as index calculus targets; the remaining use of the free P-Q beyond the best-of lead

```
   27  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   16  KR-RHO-fbd582                                known_result       Nearly free P−Q alongside P+Q
   14  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   12  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   10  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
```

### N1-d  phrase: batched Montgomery inversion affine addition relation phase prime-field index calculus constant factor  (own)

```
   25  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   25  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   18  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   16  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   16  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
   15  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   14  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
```

### N1-e  phrase: baby-step giant-step sumset: all pair sums A_i plus B_k and differences A_i minus B_k as index calculus relation targets  (own)

```
   16  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   14  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   11  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
```

### N1-f  phrase: prime-field IC target source: one batched affine addition per target walk lanes stride, cost of generating targets  (own)

```
   21  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   12  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   11  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
   11  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   11  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   10  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   10  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
```

### N1-g  phrase: Galbraith Wang Zhang X-Y computed with X+Y improved baby-step giant-step  (own)

```
   10  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    6  KR-RHO-fbd582                                known_result       Nearly free P−Q alongside P+Q
    6  KR-RHO-fbd7b1                                known_result       Grumpy giants and better-than-rho generic ordering
    4  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
    2  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    1  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    1  KR-IC-49c882                                 known_result       Quasi-subfield polynomials
```

### N1-h  phrase: stride renew cheaper target generator for the index calculus relation loop: one addition per target instead of walk jumps  (own)

```
   17  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   14  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   13  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   13  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   13  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

## APPENDIX B. Raw N2 outputs (python3 tools/build_frontier_map.py --match "<phrase>")

### N2-a  phrase: x-only plus-minus sumset target sampler for prime-field index calculus: x(A_i + B_k) and x(A_i - B_k) from one shared inversion

```
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-cb1c58  score=10  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-9e610d  score=9  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=9  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
```

### N2-b  phrase: generate two index calculus targets per field inversion without computing y

```
KR-IC-5931ee  score=15  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-9e610d  score=11  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-RHO-cb1c58  score=8  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
```

### N2-c  phrase: shared inversion for P+Q and P-Q as index calculus targets; the remaining use of the free P-Q beyond the best-of lead

```
KR-RHO-fbd582  score=16  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
```

### N2-d  phrase: baby-step giant-step sumset: all pair sums A_i plus B_k and differences A_i minus B_k as index calculus relation targets  (own)

```
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-b0fcda  score=6  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

### N2-e  phrase: Galbraith Wang Zhang X-Y computed with X+Y improved baby-step giant-step  (own)

```
KR-RHO-cd0049  score=6  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-fbd582  score=6  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
KR-RHO-fbd7b1  score=6  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
KR-RHO-6654ba  score=2  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-9e610d  score=1  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
```

### N2-f  phrase: batched Montgomery inversion affine addition relation phase prime-field index calculus constant factor  (own)

```
KR-IC-5931ee  score=16  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-cb1c58  score=16  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-RHO-e7f98e  score=10  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-IC-46d822  score=9  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=9  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=9  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
```

### N2-g  phrase: stride renew cheaper target generator for the index calculus relation loop: one addition per target instead of walk jumps  (own)

```
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-RHO-6654ba  score=7  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
```

## APPENDIX C. Raw N3 ledger grep output (ledger/.index/proposals.jsonl and hypotheses.jsonl; case-insensitive substring per term; helper hpcC1_raw/lgrep_hpcC1.py; first 25 or 18 hits per term)

### Sweep 1

```
=== TERM: sumset
prop IDEA-20260731-012 | adaptation | ['sumset'] | Large-prime variation for prime-field ECDLP relation collection — near-miss harv | Let E/F_p carry a prime-order subgroup G of order N, let F be a factor base of size B = N^beta, and 
prop IDEA-20260829-390ccc | proposed | ['sumset'] | Join-key rigidity from Cauchy-Davenport and Vosper: any O(L)-time concentrating  | CONDITIONAL THEOREM CANDIDATE, stated for falsification. Let G = <P> have prime order N, let D subse
prop IDEA-20260830-c5c614 | proposed | ['sumset'] | THE ONE DOOR CONSERVATION LEAVES OPEN. KN-FIND-007 forces the mean only when the | (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
prop IDEA-20260905-5a1ea2 | proposed | ['sumset'] | THE SUMSET ENVELOPE, GRAMMAR-FREE AND WITH ITS BLIND SPOT NAMED: the x-histogram | (A) THE OBJECT. For a factor base F of size m inside a prime-order subgroup G of E(F_p), let H_F(x) 
prop IDEA-20260930-14c753 | proposed | ['sumset'] | The four-target union column is the rare-event linearization, and it is not a ba | Representation class R1 of RQ-ECDLP-623a32 (x-coordinate). The attack stage is relation collection's
prop IDEA-20260930-4ebd85 | proposed | ['sumset'] | Triple-sum occupancy against a relabelled cyclic group, two toy binary scales | For a frozen explicit point set B of size m on the prime-order subgroup of a toy binary Koblitz curv
prop IDEA-20261002-cad44c | proposed | ['sumset'] | Weil-cap arity ledger for a rational-point Couveignes factor base: at genus at m | Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimens
prop IDEA-20261006-5bfbcf | proposed | ['sumset'] | Ordered 3-fold sumset of a 4-point small-x factor base versus size-matched rando | Representation R1, attack stage relation yield. On E: y^2 = x^3 + x + 4 over F_61, let F be the four
prop IDEA-20261018-5fa71b | proposed | ['sumset'] | One count vector, three moments: PFDR kappa, RELN Delta, SEMBIN nu and KIC cover | BRIDGE. c(R) = h-sum count vector of a base, mu its mean, Delta = Var/mu. (I1) PFDR kappa_h (IDEA-20
hypo H-CERTBIN-0c5608 | approved | ['sumset'] | The ceiling cross is 10784024 | The written counts are 6154284 and 20708500. The written ceiling mantissas are 254535220 and 8564834
hypo H-CERTBIN-a916e0 | approved | ['sumset'] | The four-target union column is the rare-event linearization, and charged member | Representation class R1 (x-coordinate). Let p <= min(1, C(B+m-1, m)/r). For L independent uniform ta
hypo H-ECDLP-3165ff | proposed | ['sumset'] |  | SCOPE: EXPLICIT reusable precomputations for the target-independent part of a chained point-decompos
hypo H-FROB-24c252 | approved | ['sumset'] | The Weil ceilings force arity 11 and 9 | 6725 is 58811 below 65536. 39201 is 26335 below 65536. The cube of 6725 is 304142328125, which is 28
hypo H-FROB-66d9ae | approved | ['sumset'] | Any Couveignes factor base built from F_2-rational points of a commutative algeb | CLAIM (structural certificate / column pricing; NO ATTACK). Setting: any Couveignes factor base F wh
hypo H-ICEX-c273c2 | proposed | ['sumset'] |  | THE DECOMPOSITION PROBABILITY IS NOT A PROBABILITY TO BE ESTIMATED. For a factor base V of size B, i
hypo H-LHW-e54b1b | approved | ['sumset'] | On the frozen (m,w) ladder, hash-realisable jump sums yield millirho Def(W)/Def( | CLAIM (heuristic_validation / integer sumset instrument; NO ATTACK; NO EXPONENT MOVE). Let W = W(m,w
hypo H-PFDR-1b2386 | proposed | ['sumset'] | Conservation binds only on the WHOLE group, so relation collection is free to at | (A) WHAT IS ALREADY CLOSED, SO THIS IS NOT MISTAKEN FOR IT. The mean per-target decomposition yield 
hypo H-PFDR-2765d2 | specified | ['sumset'] |  | On prime-order ordinary curves E/F_p with log2 p in 20..32, generated by generate_prime_order_curve(
=== TERM: pair-sum
prop IDEA-20260808-b16d04 | unverified | ['pair-sum'] | Reachable-tail signed-partition propagation with occupancy-calibrated duplicates | Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
prop IDEA-20260829-3f0f4b | proposed | ['pair-sum'] | The (gamma, s) exponent surface: retarget the lane from output-sensitive joins t | The entire source-labelled four-list family has a single two-parameter cost law. Let the level-1 joi
prop IDEA-20261017-078074 | proposed | ['pair-sum'] | Dual sum-product probe: do log-domain GAP bases carry label-additive structure t | R1 labels, stage factor-base membership. Let A = {c_1 P_1 + ... + c_r P_r : |c_i| <= T}, r in {1,2,3
prop IDEA-20261017-90d9c5 | proposed | ['pair-sum'] | Rho-trail harvest of pair-sum coincidences: the table family's memory exponent d | Stage: collision structure inside relation decomposition. Replace the stored table of S = B^h h-sums
hypo H-CRYPTO-9557c5 | approved | ['pair-sum'] | On Z/17 the set {0, 1, 3} has 6 pair-sums, not 3 and not 9. | Ordered pairs from {0, 1, 3} number 9. Their sums in Z/17 are exactly {0, 1, 2, 3, 4, 6}, so the ima
hypo H-ECDLP-298630 | approved | ['pair-sum'] | One lambda fills all 36 pair sums, and the other stops at 28. | On y^2 = x^3 + x + 3 over the field of 151 elements, the point (1, 55) lies on the curve and 167 tim
hypo H-JPR-3a00f0 | proposed | ['pair-sum'] | Source-resolved output-sensitive joinability is the missing Wagner-to-ECDLP prim | Let G be a prime-order elliptic-curve subgroup of order N and let four independently sampled, source
hypo H-PFDR-011a4b | proposed | ['pair-sum'] | Base-size axis of pair-sum coincidences: the nontrivial pair-sum coincidence cou | On prime-order ordinary curves E/F_p generated by curve.generate_prime_order_curve(bits, seed) (vend
hypo H-PFDR-727bfc | specified | ['pair-sum'] | Dual sum-product probe at toy scale: the x-label sets of rank-r log-GAP bases {c | Let E/F_p be a generated prime-order ordinary curve, N = #E(F_p), f(x) = x^3 + ax + b, and L = {x in
=== TERM: pairset
=== TERM: p-q
prop IDEA-20260726-011 | unverified | ['p-q'] | Twist-blind Kummer walk — does the shared x-line carry cross-twist information a | E and its quadratic twist E' share the Kummer line P^1 = E/±1, and the differential-addition law the
prop IDEA-20260731-014 | unverified | ['p-q'] | Solving-path re-randomization for Semaev membership — is the min-over- randomize | For the SAME fixed Semaev membership system (frozen target R, factor base F, arity m — the system wh
prop IDEA-20260807-291968 | proposed | ['p-q'] | The relation matrix has never been measured as an object over prime fields, alth | FINDING-PF-IC-001 states the prime-field index-calculus cost 'is dominated by the |F|-size linear al
prop IDEA-20260807-490c34 | proposed | ['p-q'] | A one-sided gate cannot see a deficit: EV-INCB-001's predeclared test asked only | EV-INCB-001 is a controlled negative on its intended gate: the predeclared condition (z > 3 at all t
prop IDEA-20260807-8027a2 | proposed | ['p-q'] | THE KUMMER LINE IS NOT A NEW MODEL, IT IS THE TERMINAL ONE - Semaev's S_3 IS the | (A) THE IDENTIFICATION. For a generic-j curve, E/{+-1} is the Kummer line P^1, and EVERY degree-2 co
prop IDEA-20260811-9ba2aa | proposed | ['p-q'] | THE WHOLE f_V-FREE PANEL MAY FACTOR THROUGH E[2], NOT JUST THE ELIMINATION FAMIL | (A) THE STRUCTURAL CLAIM. Over QQ[a,b], the Jacobian ideal J = < S_3, dS_3/dx_1, dS_3/dx_2, dS_3/dx_
prop IDEA-20260909-7ecf02 | proposed | ['p-q'] | Import MODHECKE-B1 / ZILBERPINK-C2: theory-first IC formalization before experim | MODHECKE-B1 and ZILBERPINK-C2 remain genuinely open (no literature refutation in the external triage
prop IDEA-20260909-f13026 | proposed | ['p-q'] | Import RT-1476-SUBRES-A1: serial-S3 backward-3-sum eliminant beta gate for sub-r | On the SUCCESSFUL-membership subset (per red-team contract), the serial-S3 backward-3-sum eliminant 
prop IDEA-20260918-6c07e1 | proposed | ['p-q'] | A FROBENIUS-ORBIT CONGRUENCE CLOSES THE F_2-COEFFICIENT QUASI-SUBFIELD SHAPE AT  | (A) FROBENIUS STABILITY OF THE ROOT SET. Let lambda in F_2[X] and L = X^(2^n') + lambda(X) over F_2,
prop IDEA-20260922-818b73 | proposed | ['p-q'] | THE EXCHANGE RATE AGAINST RHO: gamma*(cell) = 2^(60.9 - floor_bits), the single  | For any relation-based decomposition line at a cell (curve, arity m, factor-base/system parameters),
prop IDEA-20260926-bc1cab | proposed | ['p-q'] | THE TWISTED-COEFFICIENT CENSUS AT n = 131: K-coefficient quasi-subfield lambda ( | (A) WHAT IS PROVED, WHAT IS MEASURED, WHAT IS UNTOUCHED. The twisted injection bound N_K(X^{2^{n'}} 
prop IDEA-20261006-30b5f6 | proposed | ['p-q'] | Square bias of x(P+Q) x(P-Q) - x(P) x(Q) for one frozen public point | Let E be y^2 = x^3 + 6x + 2. Let p be the smallest prime with 23 ≤ p ≤ 120 such that E over F_p is n
prop IDEA-20261006-a0e3bd | proposed | ['p-q'] | One shared inversion for x(P+Q) and x(P-Q) on y^2 = x^3 + 5x + 7 over F_101 | On y^2 = x^3 + 5x + 7 over F_101, for each of 40 frozen pairs of affine points with distinct absciss
prop IDEA-20261016-a16fa4 | proposed | ['p-q'] | 2-adic Euclid tower: a heights-free decision procedure for dependence of two poi | E: y^2=x(x^2+Ax+B), E(Q)[2^inf]=<T> (B, D non-squares), P,Q non-torsion, x_P != x_Q. W = {v in F_2^2
hypo H-ECDLP-18c7f7 | specified | ['p-q'] |  | On y^2 = x^3 + 6x + 2, at the smallest prime p from 23 through 120 with at least 24 affine points of
hypo H-INCB-dc5010 | proposed | ['p-q'] |  | SCOPE. The three toy primes of EXP-INCB-001, the same factor-base x-sets and the same random x-subse
hypo H-QALG-05fca6 | specified | ['p-q'] | Stage 0 amplitude-amplified pairing selection inside kuperberg sieve identities  | Fix the exact count identity of IDEA-20260813-c6e557 before any later-stage claim. Stage 0 asserts o
hypo H-QALG-0df353 | specified | ['p-q'] | Stage 0 quantum decoding problem real pipeline hqc identities — n=2 — before any | Fix the exact count identity of IDEA-20260829-b32543 before any later-stage claim. Stage 0 asserts o
hypo H-QALG-277c52 | specified | ['p-q'] | Stage 0 grover-style speedups quoted classical search quantum identities — n=2 — | Fix the exact count identity of IDEA-20260815-eaa615 before any later-stage claim. Stage 0 asserts o
hypo H-QALG-29658b | specified | ['p-q'] | Stage 0 secret-window bound dual-based quantum attacks sparse identities — n=3 — | Fix the exact count identity of IDEA-20260818-d5668d before any later-stage claim. Stage 0 asserts o
hypo H-QALG-2d3cb0 | specified | ['p-q'] | Stage 0 electric-network span-program re-derivation mnrs quantum walk identities | Fix the exact count identity of IDEA-20260813-319645 before any later-stage claim. Stage 0 asserts o
hypo H-QALG-2eb8b0 | proposed | ['p-q'] | The sample-access model is unrealizable from one ML-KEM public key: standard lin | SCOPE: the three standardized ML-KEM parameter levels (512, 768, 1024), the STANDARD linear self-red
hypo H-QALG-38c609 | specified | ['p-q'] | Stage 0 coherent prange oracle need gaussian elimination identities — n=2 — befo | Fix the exact count identity of IDEA-20260829-267a06 before any later-stage claim. Stage 0 asserts o
hypo H-QALG-49cb59 | specified | ['p-q'] | Stage 0 prior-matched amplitude amplification quantum isd exponent identities —  | Fix the exact count identity of IDEA-20260818-45b8ea before any later-stage claim. Stage 0 asserts o
hypo H-QALG-749702 | specified | ['p-q'] | Stage 0 orbit-quotient continuous-time quantum walk z-n automorphism identities  | Fix the exact count identity of IDEA-20260813-c34e09 before any later-stage claim. Stage 0 asserts o
=== TERM: r-j
prop IDEA-20260816-699a0f | proposed | ['r-j'] | Three imported ALECF packages carry different scores, and the committed logs sho | (A) Comparability is the prior question to scoring, and this repository already contains a worked in
prop IDEA-20260901-a66d70 | proposed | ['r-j'] | ORDER-JOIN RIGIDITY AND THE SFT CASCADE: the one output-sensitive join the corpu | Setting. G = <P> of prime order N, Q = [x]P. An ORDER KEY is a map nu from G to Z/N (ties allowed), 
prop IDEA-20261016-15a6fc | proposed | ['r-j'] | Route kP through a small-degree F_p-isogenous neighbour: a = -3 gain versus conv | (1) For a deployed prime-order curve E with a not in {-3, 0}, kP = phi_hat(k' phi(P)), k' = k/ell mo
hypo H-ALECF-002 | analyzed | ['r-j'] |  | Autolab package `ecdsafail-frontier-jul23` (ECDSA Fail quantum point-add) produces a scoped empirica
hypo H-JPR-5e33d6 | specified | ['r-j'] | Order-join rigidity and the SFT cascade: on a prime-order group a sound two-poin | SETTING. G = <P> of odd prime order N, Q = [x]P. An ORDER KEY is a map nu from G to Z/N (ties allowe
=== TERM: side target
=== TERM: target source
=== TERM: targetsource
=== TERM: walkprimelanes
=== TERM: walk lanes
=== TERM: lock-step
=== TERM: lockstep
prop IDEA-20261015-c6f017 | proposed | ['lockstep'] | The n=131 denominator: every ECC2K-130 lane (QSP, CERTBIN, FROB at 131) has no m | (1) A three-limb signed-Frobenius walk at n=131 (polynomial basis with CLMUL, table-driven basis cha
=== TERM: galbraith-wang-zhang
=== TERM: galbraith, wang
=== TERM: fbd582
prop IDEA-20261006-4e7025 | proposed | ['fbd582'] | Some affine pair on y^2 = x^3 + x + 1 over F_89 has x(P+Q) = x(P)+x(Q) | REPRESENTATION AND STAGE. The tracked label is the field element x(P)+x(Q)-x(P+Q). The stage is a pu
prop IDEA-20261006-a0e3bd | proposed | ['fbd582'] | One shared inversion for x(P+Q) and x(P-Q) on y^2 = x^3 + 5x + 7 over F_101 | On y^2 = x^3 + 5x + 7 over F_101, for each of 40 frozen pairs of affine points with distinct absciss
=== TERM: x(p-q)
prop IDEA-20260726-011 | unverified | ['x(p-q)'] | Twist-blind Kummer walk — does the shared x-line carry cross-twist information a | E and its quadratic twist E' share the Kummer line P^1 = E/±1, and the differential-addition law the
prop IDEA-20260807-8027a2 | proposed | ['x(p-q)'] | THE KUMMER LINE IS NOT A NEW MODEL, IT IS THE TERMINAL ONE - Semaev's S_3 IS the | (A) THE IDENTIFICATION. For a generic-j curve, E/{+-1} is the Kummer line P^1, and EVERY degree-2 co
prop IDEA-20260811-9ba2aa | proposed | ['x(p-q)'] | THE WHOLE f_V-FREE PANEL MAY FACTOR THROUGH E[2], NOT JUST THE ELIMINATION FAMIL | (A) THE STRUCTURAL CLAIM. Over QQ[a,b], the Jacobian ideal J = < S_3, dS_3/dx_1, dS_3/dx_2, dS_3/dx_
prop IDEA-20261006-30b5f6 | proposed | ['x(p-q)'] | Square bias of x(P+Q) x(P-Q) - x(P) x(Q) for one frozen public point | Let E be y^2 = x^3 + 6x + 2. Let p be the smallest prime with 23 ≤ p ≤ 120 such that E over F_p is n
prop IDEA-20261006-a0e3bd | proposed | ['x(p-q)'] | One shared inversion for x(P+Q) and x(P-Q) on y^2 = x^3 + 5x + 7 over F_101 | On y^2 = x^3 + 5x + 7 over F_101, for each of 40 frozen pairs of affine points with distinct absciss
hypo H-ECDLP-18c7f7 | specified | ['x(p-q)'] |  | On y^2 = x^3 + 6x + 2, at the smallest prime p from 23 through 120 with at least 24 affine points of
=== TERM: shared inversion
prop IDEA-20260926-d3c5a5 | proposed | ['shared inversion'] | A BINARY PORT OF THE PRIME-FIELD MEET-IN-THE-MIDDLE ENGINE (table of tails keyed | CEILING FIRST. No exponent moves and nothing here bears on ECC2K-130 except negatively. Representati
prop IDEA-20261006-a0e3bd | proposed | ['shared inversion'] | One shared inversion for x(P+Q) and x(P-Q) on y^2 = x^3 + 5x + 7 over F_101 | On y^2 = x^3 + 5x + 7 over F_101, for each of 40 frozen pairs of affine points with distinct absciss
=== TERM: shared denominator
hypo H-CRYPTO-b2c203 | proposed | ['shared denominator'] |  | A reproducible group-operation-equivalent (GOE) cost ruler can be installed at secp256k1-adjacent pa
=== TERM: montgomery simultaneous
```

### Sweep 2

```
=== TERM: batch inversion
prop IDEA-20260906-c9f6e0 | proposed | ['batch inversion'] | Coherent zero-masked batch inversion inside CSIDH action blocks | For a block of k simultaneous independent affine normalizations inside a fixed CSIDH action circuit,
prop IDEA-20260920-204828 | proposed | ['batch inversion'] | Inversion through the field norm with the true inversion batched at base-field l | In the affine rho step the denominator d = x_R - x_T in F_{p^5} can be inverted as d^{-1} = c / N(d)
hypo H-GFPN-9a7042 | approved | ['batch inversion'] | The schoolbook extension count exceeds 79 by 3/16. | At batch size 16 the norm count is 2M + 26. For M = 25 that count is 76. The extension numerator is 
=== TERM: batched inversion
prop IDEA-20260920-0d218c | proposed | ['batched inversion'] | Per-step cost floor of affine Pollard rho on F_{p^5} = F_p[z]/(z^5 - 3), p = 2^6 | One affine r-adding rho step with Montgomery-batched inversion on E(F_{p^5}) costs about 5M + 1S in 
prop IDEA-20261015-c6f017 | proposed | ['batched inversion'] | The n=131 denominator: every ECC2K-130 lane (QSP, CERTBIN, FROB at 131) has no m | (1) A three-limb signed-Frobenius walk at n=131 (polynomial basis with CLMUL, table-driven basis cha
=== TERM: batched affine
=== TERM: simultaneous inversion
=== TERM: per inversion
=== TERM: two targets
prop IDEA-20261022-727676 | proposed | ['two targets'] | Replay lever in the PKM tower F4: measure the target-independent share of cost ( | [proposed] In f4_fp_tower on m=3 N=15, m=3 N=18, m=4 N=12 (two committed targets each) the systems o
hypo H-ICEX-6d0c9a | proposed | ['two targets'] |  | For M discrete-log targets in one prime-order subgroup solved by a shared-walk parallel collision se
hypo H-RELN-62a482 | specified | ['two targets'] | Stage 0 distribution-versus-scalar identities — two targets required — before an | Fix the exact two-target identity of IDEA-20260815-f9e978 before any P(decomp) is reported as a scal
=== TERM: x-only
prop IDEA-20260726-011 | unverified | ['x-only'] | Twist-blind Kummer walk — does the shared x-line carry cross-twist information a | E and its quadratic twist E' share the Kummer line P^1 = E/±1, and the differential-addition law the
prop IDEA-20260807-4cebed | proposed | ['x-only'] | THE LOSSY-PROJECTION TEST APPLIED TO THE LANE'S OWN CENTRAL OBJECT, AND IT FAILS | (A) THE PROJECTION, AND THE FIRST CLAUSE IT PASSES. The negation quotient is not merely LIKE the x-c
prop IDEA-20261003-05e0e1 | proposed | ['x-only'] | A projective point stores 3 coordinates and an x-only state stores 1 | A projective point stores 3 coordinates. An x-only state stores 1 coordinate. Three exceeds one by 2
prop IDEA-20261003-7f6cd3 | proposed | ['x-only'] | A full affine point stores 2 field elements and an x-only state stores 1 | A full affine point stores 2 field elements. An x-only ladder state stores 1. Two exceeds one by 1, 
prop IDEA-20261006-c5b972 | approved | ['x-only'] | X-only planted-key recovery through P-192's same-a singular companion | A low-level P-192 scalar multiplication routine that accepts an unchecked affine point and exposes a
hypo H-ECDLP-850278 | approved | ['x-only'] | 3 coordinates exceed 1 by 2 | A projective point stores 3 coordinates. An x-only state stores 1 coordinate. Three exceeds one by 2
hypo H-ECDLP-d8c550 | approved | ['x-only'] | 2 exceeds 1 by 1 | A full affine point stores 2 field elements. An x-only state stores 1. Two exceeds one by 1. The pro
hypo H-FROB-73df22 | proposed | ['x-only'] | Frobenius orbit ideals versus the complete trace-zero index-calculus pipeline | Audit source armA disjointness/equivariance/invariant-degree predictions without assuming x-only fre
hypo H-SCURVE-d5f25f | approved | ['x-only'] | An unchecked P-192 low-level multiplier permits x-only singular-companion plante | For the fixed public synthetic scalar derived by the frozen KDF, a native low-level P-192 scalar_mul
=== TERM: walked target
prop IDEA-20261015-7a3c9e | proposed | ['walked target'] | Orbit-folded m=2 Koblitz index calculus is baby-step giant-step on the quotient  | For the repository's folded pair-state index calculus (a table of #states folded pair sums of base r
=== TERM: r-adding
prop IDEA-20260901-753636 | proposed | ['r-adding'] | PLAIN RHO SEES THE CURVE THROUGH EXACTLY ONE APERTURE -- THE PARTITION h(R) = x( | (A) THE APERTURE, READ OFF THE INSTRUMENT. harness/rho.py implements a Teske r-adding walk whose bra
prop IDEA-20260905-9c4f0c | proposed | ['r-adding'] | THE REAL WALK IS NOT THE CONVOLUTION: the r-adding walk chooses its branch from  | (A) THE OBJECT. The additive walk on G = <P> of prime order N is F(W) = W + T_{s(W)} with s(W) = x(W
prop IDEA-20260906-aed829 | proposed | ['r-adding'] | THE BASIN-PARTITION COVERAGE INSTRUMENT: measure the coverage constant of a Bern | (A) THE OBJECT. Fix a deterministic walk f on the group G of prime order N (an r-adding walk with kn
prop IDEA-20260920-0d218c | proposed | ['r-adding'] | Per-step cost floor of affine Pollard rho on F_{p^5} = F_p[z]/(z^5 - 3), p = 2^6 | One affine r-adding rho step with Montgomery-batched inversion on E(F_{p^5}) costs about 5M + 1S in 
prop IDEA-20260920-2e37b3 | proposed | ['r-adding'] | Instance economics of the rho ruler for a deployed curve with many keys: multi-i | A deployment with L keys on one of these curves is not priced by a single-instance count. Under the 
prop IDEA-20260920-5b1f84 | proposed | ['r-adding'] | Control: does an r-adding walk on E(F_{p^5}) whose partition index and distingui | The cheapest partition function on this field reads the constant coefficient x_0 of x (which is Tr(x
prop IDEA-20260923-5d07e3 | proposed | ['r-adding'] | THE WALK'S IN-DEGREE VARIANCE IS A TABLE CONSTANT: an r-adding walk has in-degre | (A) THE LAW (derivation of this record). For a walk f(x) = g_{h(x)}(x) with bijections g_1..g_r (r-a
prop IDEA-20260923-c2a85f | proposed | ['r-adding'] | THE HUB-COVER CEILING: the basin-partition ceiling C_max(a) of IDEA-20260906-aed | (A) THE FAMILY. Fix the walk f and a probe predicate of density rho_p (every point, rho_p = 1; or fi
prop IDEA-20261001-833e78 | proposed | ['r-adding'] | DOES THE FROBENIUS-CLASS WALK CONSTANT MATCH √(2n) AT TOY KOBLITZ SCALE? On stdl | RQ-BINSTD cost tables need an honest rho baseline with the symmetries the curve grants. CLAIM: on ea
prop IDEA-20261001-ae7005 | proposed | ['r-adding'] | DOES A HALVING STEP BEAT A DOUBLING STEP ON TOY KOBLITZ RHO WALKS? On stdlib (or | KR-RHO-6654ba reports point halving as a cheaper binary-curve rho step in the literature. CLAIM: at 
prop IDEA-20261006-11a1aa | proposed | ['r-adding'] | r=4 versus r=16 step ratio on y^2 = x^3 + 2x + 5 over F_89 | On E: y^2 = x^3 + 2x + 5 over F_89, which this session counted as 101 points including infinity, an 
prop IDEA-20261006-934aa5 | proposed | ['r-adding'] | Length-3 and length-6 fruitless cycles on one toy j=0 orbit walk, against an |Au | On one frozen ordinary prime-field j=0 curve and one |Aut|=2 curve over the same prime p with 100 < 
prop IDEA-20261006-947b64 | proposed | ['r-adding'] | Distinguished-point modulus 32 versus modulus 8 on one walk in Z/401Z | In Z/401Z, one planted logarithm, an r-adding walk with r = 16, and 20 seeds, the lower median of st
hypo H-ECDLP-37dc01 | analyzed | ['r-adding'] | THE BATCH-RESELECTED FIXED-SIZE TABLE: with the advice size held at exactly T en | (A) SETTING. A prime-order group of order N; a deterministic walk f that is a function of the curren
hypo H-ECDLP-3ca750 | proposed | ['r-adding'] |  | SCOPE: the harness r-adding walk F(W) = W + T_{x(W) mod r} (harness/rho.py) on cofactor-1 prime-orde
hypo H-ECDLP-6c52c0 | proposed | ['r-adding'] | The comparator this program scores candidates against is the S = O(1) corner of  | Source proposal IDEA-20260806-3b91c7 (RQ-ECDLP-002, class cost-model). THE SOURCE PROPOSAL IS NOT ED
hypo H-ECDLP-fadd65 | approved | ['r-adding'] | Binomial(r, 1/r) has variance (r-1)/r for r in {2, 3, 4, 16}, which is 1/r below | For r in {2, 3, 4, 16}, the variance r*(1/r)*(1-1/r) equals (r-1)/r. The four values are 1/2, 2/3, 3
hypo H-LHW-e54b1b | approved | ['r-adding'] | On the frozen (m,w) ladder, hash-realisable jump sums yield millirho Def(W)/Def( | CLAIM (heuristic_validation / integer sumset instrument; NO ATTACK; NO EXPONENT MOVE). Let W = W(m,w
=== TERM: stride
prop IDEA-20260816-efb9b3 | proposed | ['stride'] | Measure the only step that actually shrinks the represented body: the duplicate- | (A) H-ALR-001 assumes public duplicate targets may be removed because only the zero union is require
prop IDEA-20260821-121612 | proposed | ['stride'] | Is the source-level stride reading this lane's obstruction depends on even WELL  | (0) REVISION NOTICE, FIRST BECAUSE IT CHANGES THE DELIVERABLE. This record is a repaired revision fi
prop IDEA-20260828-033cb3 | unverified | ['stride'] | Call-site specialization: does a single source-level comparison symbol fracture  | (A) THE TWO OPEN THREADS THIS RECORD CONNECTS. IDEA-20260821-121612 measured whether a FIXED compari
hypo H-MLKEM-142bab | proposed | ['stride'] |  | The vector stride w that this lane's obstruction argument consumes is NOT a well-defined property of
=== TERM: target generation
=== TERM: target-generation
=== TERM: relation phase
prop IDEA-20261018-2c37f5 | proposed | ['relation phase'] | Stacked D4 + double-large-prime arm on E(F_{p^4}), end to end in ecbench | Stacking D4 symmetry (18.2x [16.4, 20.8] whole-solve constant) with double large primes (LA exponent
=== TERM: icperf
prop IDEA-20260915-0d8e90 | proposed | ['icperf'] | The PDP cost law the boundary table should test: WDSat's UNSAT conflict count eq | On the Trimoska S_4 Weil-descent instances with V = {deg x < l} and m = 3 factor-base points, WDSat 
prop IDEA-20260915-3119c9 | proposed | ['icperf'] | Factor-base design by counting: the G-landing triple count Lambda(V) = C(F1+2,3) | Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, n odd, #E = 2r with r odd, G = 2E the odd-order
prop IDEA-20260915-3476de | proposed | ['icperf'] | Make the Groebner column measurable and then decide whether the SAT-over-Groebne | (C1, INSTRUMENT) The 32 Macaulay2 1.22 rows of RUN-ICPERF-305ca3 that exited -6 with std::bad_alloc 
prop IDEA-20260915-3f1964 | proposed | ['icperf'] | Exhaustive side-classified decomposition table as the PDP row's ground truth: ev | Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, b != 0, and let x_1, x_2, x_3, x_R in F_q with 
prop IDEA-20260915-7ef636 | proposed | ['icperf'] | Separate the branching-order effect from the structure effect with a 2x2 plus a  | P3b and P6 of H-ICPERF-cc4847 are measured on objects that differ in TWO ways at once, and as measur
prop IDEA-20260915-8fe0ef | proposed | ['icperf'] | Frobenius-invariant factor bases on binary Koblitz cells, measured against the s | SETTING. E: y^2 + xy = x^3 + a x^2 + b with a, b in F_2 (a Koblitz curve; the Trimoska benchmark cur
prop IDEA-20260915-eee7e4 | proposed | ['icperf'] | Side-constrained core: adding the E-membership constraint x_i in x(E) for each o | Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, and V = {deg x < l} the Trimoska factor-base su
prop IDEA-20260916-b84e2d | proposed | ['icperf'] | ITEM (ii) MEASURED HONESTLY: the per-attempt cost, ideal degree and spurious-sol | (A) WHAT IS MEASURED. For the chain system S = {S^{(0)}, ..., S^{(m-1)}} of KN-LIT-0a321c Section 3.
prop IDEA-20260920-0d218c | proposed | ['icperf'] | Per-step cost floor of affine Pollard rho on F_{p^5} = F_p[z]/(z^5 - 3), p = 2^6 | One affine r-adding rho step with Montgomery-batched inversion on E(F_{p^5}) costs about 5M + 1S in 
prop IDEA-20260920-204828 | proposed | ['icperf'] | Inversion through the field norm with the true inversion batched at base-field l | In the affine rho step the denominator d = x_R - x_T in F_{p^5} can be inverted as d^{-1} = c / N(d)
prop IDEA-20260920-2e37b3 | proposed | ['icperf'] | Instance economics of the rho ruler for a deployed curve with many keys: multi-i | A deployment with L keys on one of these curves is not priced by a single-instance count. Under the 
prop IDEA-20260920-5b1f84 | proposed | ['icperf'] | Control: does an r-adding walk on E(F_{p^5}) whose partition index and distingui | The cheapest partition function on this field reads the constant coefficient x_0 of x (which is Tr(x
prop IDEA-20260920-68b279 | proposed | ['icperf'] | Shared instrument: an F_{p^5} Pollard-rho backend for F_p[z]/(z^5 - 3), p = 2^64 | No rho backend over F_{p^n} exists in this program or in either sibling repository (card V5: the cry
prop IDEA-20260920-a05ca7 | proposed | ['icperf'] | Protocol-conditional rho-family ruler: if a deployment on EcGFp5 or EcMasFp5 dra | The 320-bit group order of these curves buys 2^159.8 of rho cost only if the secret scalar is unifor
prop IDEA-20260920-a639a1 | proposed | ['icperf'] | Symmetrization-aware Gaudry cost audit of EcGFp5 and EcMasFp5 (n = 5, m = 5) | The EcGFp5 design note's ">= 2^142" security floor against Gaudry's index calculus is computed for t
prop IDEA-20260920-b9f0c5 | proposed | ['icperf'] | WDSat conflict audit on Frobenius-invariant factor bases at n = 41 (cheap) and n | On E/F_2 Koblitz curves over F_{2^n}, build Weil-descent PDP instances whose factor base is a Froben
prop IDEA-20260922-2e2a58 | proposed | ['icperf'] | THE CROSSOVER IS A SURFACE IN (TIME, MEMORY, PARALLEL WIDTH), AND BOTH PREMISES  | (A) THE SCALAR CROSSOVER IS UNDER-DETERMINED. This lane's decision target asks, per curve, whether a
prop IDEA-20260922-77bf31 | proposed | ['icperf'] | THE DESCENT COLUMN IS NOT ONE COLUMN, IT IS TWO, AND ONLY ONE OF THEM IS LEGITIM | (A) THE DICHOTOMY, WHICH IS A PROPERTY OF THE FACTOR BASE AND NOT OF THE CURVE. Call a factor base S
=== TERM: double-ended
=== TERM: bsgs
prop IDEA-20260801-003 | adaptation | ['bsgs'] | Closed-form target-descent cost gate: bind every sub-rho claim to an explicit de | On GOAL-ECDLP-001, every hypothesis that claims a sub-rho result must first pass a closed-form targe
prop IDEA-20260802-002 | adaptation | ['bsgs'] | Tracked-object enumeration for the ECDLP with an EXECUTABLE one-step propagation | An attack family on the ECDLP can be indexed by its TRACKED OBJECT, and that index can be made measu
prop IDEA-20260802-003 | unverified | ['bsgs'] | The enumerate-and-join exponent is pinned at 1/2 identically in arity - and the  | TWO CLAIMS, ONE NEGATIVE AND ONE MEASURED, AND THEY ARE STATED SEPARATELY BECAUSE THEY HAVE DIFFEREN
prop IDEA-20260805-2afd22 | unverified | ['bsgs'] | A certificate-backed cost model that certifies 1/m! of its own cost: the decompo | GOAL-SDEG-001's title and objective are "certificate-backed", and its single completion criterion is
prop IDEA-20260807-018769 | proposed | ['bsgs'] | The transfer-operator barrier is a property of the PARTITION, not of the walk: x | EV-TRA-001 is a well-controlled negative: L = O(1) with fitted growth exponent delta = 0.0195, hit r
prop IDEA-20260808-031a59 | proposed | ['bsgs'] | Isogeny-class relation aggregation is exactly cost-neutral, and it stays cost-ne | Let E_1, ..., E_h be the curves of the F_p-isogeny class of E (h = h(D) ~ sqrt(p)), each with its ow
prop IDEA-20260808-2e14f7 | proposed | ['bsgs'] | Coordinate-degree optimisation for the factor base — the window may be taken in  | Every prime-field decomposition record in this corpus takes the factor base to be defined by the x-c
prop IDEA-20260808-2ef5c8 | proposed | ['bsgs'] | The arity threshold was derived for a B-independent oracle and every real oracle | IDEA-20260803-fa9839 charges T = m! N D_trial / B^{m-1} + c_LA B^2 and derives "beats rho iff D_tria
prop IDEA-20260808-40aab9 | proposed | ['bsgs'] | The Kani / Robert higher-dimensional embedding - the single largest recent struc | (A) WHAT THE MACHINERY NEEDS. The SIDH-breaking machinery (Castryck-Decru; Maino-Martindale; Robert)
prop IDEA-20260808-481e07 | proposed | ['bsgs'] | PAUSE-FLAGGED - complete splitting on the factor-base locus means the decomposit | REQUIRES THE GOAL-MONO-001 PAUSE TO CLEAR BEFORE DISPATCH; filed now because the content is a correc
prop IDEA-20260808-5e257f | proposed | ['bsgs'] | The frozen p_exist/p_solve instrument measures a CENSORED BINARY and throws away | GOAL-RELN-001's protocol separates an oracle metric p_exist (does a decomposition exist) from a char
prop IDEA-20260808-6a2b50 | proposed | ['bsgs'] | Is the measured solving degree a coordinate artifact? Import the generic-coordin | There is a published invariant-theoretic route that this lane does not use: for a polynomial system 
prop IDEA-20260808-812554 | proposed | ['bsgs'] | The sigma-threshold: prime-field index calculus with an exhaustive decomposition | Write T_solve = B^{(m-1)sigma} for the cost of finding all m-decompositions of one target over a siz
prop IDEA-20260808-a3f7c1 | proposed | ['bsgs'] | Y-COORDINATE ORACLE FOR GUIDED DECOMPOSITION: the x-oracle MITM obstruction show | (A) THE OBSTRUCTION THIS AVOIDS. H-XOR-d1a480 (rejected_scoped per DEC-20260808-6a7ac4) showed that 
prop IDEA-20260808-b8e2d4 | proposed | ['bsgs'] | FULL-POINT ORACLE FOR ALGEBRAIC CONSTRUCTION: an oracle that returns a complete  | (A) THE OBSTRUCTION THIS AVOIDS. H-XOR-d1a480 (rejected_scoped per DEC-20260808-6a7ac4) and IDEA-202
prop IDEA-20260808-c5f9a2 | proposed | ['bsgs'] | ENDOMORPHISM-IMAGE ORACLE FOR STRUCTURAL DECOMPOSITION: an oracle that returns w | (A) THE OBSTRUCTION THIS AVOIDS. H-XOR-d1a480 (rejected_scoped per DEC-20260808-6a7ac4) shows that c
prop IDEA-20260808-c64123 | proposed | ['bsgs'] | GOAL-ECTD-001's "descent" half has zero finite-field content and this is a one-l | (A) THE DEGENERACY, DERIVED. Let E/F_p and l != p be a prime. The absolute Galois group of F_p is Zh
prop IDEA-20260808-fa1d80 | proposed | ['bsgs'] | Tracked object: the split-quotient certificate. ECDLP is exactly the problem of  | Let G = <P> of prime order N, Q = [k]P, and consider the abelian surface A = E x E with its product 
```
