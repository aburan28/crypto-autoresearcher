# Gate N1-N4: C2. Field-operation pricing for the prime arms (with fairness guard)

Field key: HPC constants (memory hierarchy, batched-inversion scheduling, SIMD/field-op pricing, GF(2)/GF(p) linear algebra, bit-sliced arithmetic, rho step vs IC relation cost at matched hardware) - round 2.
Scout: read-only. Nothing was written inside any repository. Raw tool output is in this file and under raw-C2-fieldops/ (same directory).
Environment for all runs: LEAD_ATLAS_CRYPTO=.../scratchpad/crypto-main, LEAD_ATLAS_CRYPTANALYSIS=.../scratchpad/cryptanalysis-main, LEAD_ATLAS_ECC_CHALLENGES=/Volumes/SSD990-2/ecc-challenges; cwd /Volumes/SSD990-2/crypto-autoresearcher.

## 0. Verdict (short)

advances_lead. Lead sharpened: LEAD-ICP-prime-ic-constant-engineering (open_next_step). Its next_action is the unimplemented two-level target batching arm, whose discriminator ("paired ratio with the interval below 1") cannot fire in counted GAE: the sealed lanes check reads 72/72 pairs at exactly 1 and records field_ops_available false. A field-op (or L2 wall) read-out is a prerequisite for that lead, and the candidate supplies the unit rule.

For LEAD-ICE-rootfind-pairtable-oracle (open_blocked) the candidate's components (a)+(b) are NOT sharper: serializing the already-counted native field operations and pricing native work in a common unit is the named "Next discriminating step" of problems/rootfinding-complete-cost-calibration.md and the lead's own next_action. The only addition there is the price rule (3M + I/n per element instead of a flat 0 / 0.1 / 1 GAE per native op).

Genuinely additional, all narrow and program-internal: (i) the batched-inversion price rule in the *_full/*_wordram repricing (none exists today), (ii) prime entries for those twins and field-op emission from the prime ic.pipeline, (iii) prime_fast::rho_parallel registered as a batched matched prime rho with an A/A (no lead covers it), (iv) the guard, which is an application of AGENTS.md section 5a. The Montgomery cost formula is known (KR-RHO-cb1c58; closed lead LEAD-RHO-batched-inversion-shared-pm is not reopened). No standing obstruction is escaped (SO-TABLE, SO-GEN quoted in section 5). Cautions C1-C3 in section 9 change how the write-up must be worded.

## 1. N1 raw output: lead_atlas.py --match

### 1.1 match_phrasings[0]
`python3 tools/lead_atlas.py --match "price prime-field additions from serialized field operation counts with batched inversion in a full or wordram twin of rho.negation and the prime ic pipeline"`
```
   17  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   16  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   14  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
   14  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   14  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   14  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   13  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
```
### 1.2 match_phrasings[1]
`python3 tools/lead_atlas.py --match "make batched inversion visible in the benchmark cost unit for prime index calculus and rho"`
```
   19  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   18  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   16  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   15  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   15  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
   15  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   15  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   15  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
```
### 1.3 match_phrasings[2]
`python3 tools/lead_atlas.py --match "native work unpriced; serialization and common-unit pricing of native field operations; two-level target batching counted GAE ratio exactly 1"`
```
   10  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    7  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    6  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged
    6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    5  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    5  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    4  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
```
### 1.4 own phrasing
`python3 tools/lead_atlas.py --match "Montgomery simultaneous inversion field-operation cost unit word-RAM budget fairness guard against serial rho"`
```
   20  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   15  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   13  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   11  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    9  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
    9  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
```

## 2. N2 raw output: build_frontier_map.py --match (same four phrasings, same order)

### 2.1
```
KR-RHO-e7f98e  score=16  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-cb1c58  score=14  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-RHO-cd0049  score=14  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-9e610d  score=11  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-33f837  score=10  [record/reported]  Prime-field ECDLP records
    sources: KN-LIT-095, KN-LIT-a714d3, KN-LIT-24b9c7, KN-LIT-ff80da
KR-RHO-825bca  score=10  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-5931ee  score=9  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-38be82  score=8  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
```
### 2.2
```
KR-IC-a4dd54  score=19  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-5931ee  score=18  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-9e610d  score=15  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-1fcdbc  score=12  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-e7f98e  score=12  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-cb1c58  score=10  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-RHO-cd0049  score=10  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```
### 2.3
```
KR-IC-791cb7  score=5  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5931ee  score=4  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-081a58  score=3  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-9e610d  score=3  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-18cc42  score=3  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-RHO-1c2928  score=3  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-33f837  score=3  [record/reported]  Prime-field ECDLP records
    sources: KN-LIT-095, KN-LIT-a714d3, KN-LIT-24b9c7, KN-LIT-ff80da
```
### 2.4
```
KR-RHO-cb1c58  score=13  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-1c2928  score=10  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-e7f98e  score=9  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-cd0049  score=8  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-482ed3  score=7  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-18cc42  score=6  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
```

## 3. N1 reading of the top hits (YAML opened for every top-5 hit of every run)

Lead rows read in full: /Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/<family>/LEAD-*.yaml. Problem file read in full: crypto-main/problems/rootfinding-complete-cost-calibration.md. Source read: crypto-main/src/cryptanalysis/{ic_boundary.rs, prime_fast.rs, ecbench/{full_price,wordram_price,methods,bounds}.rs}, AGENTS.md section 5a and 6.

Runs 1-4 top-5 union and verdict per hit (S = same mechanism, R = related, L = lexical only):

| hit | disposition | verdict | why |
|:--|:--|:--|:--|
| LEAD-ICP-prime-ic-constant-engineering | open_next_step | R, the lead this candidate sharpens | next_action is the two-level target batching paired arm, "~2x predicted", discriminated by "a paired ratio with the interval below 1". Its forecloses list includes "batched inversion speeds up prime index calculus". The candidate does not claim a speed-up; it supplies the unit in which that discriminator can fire. |
| LEAD-ICE-rootfind-pairtable-oracle | open_blocked | S for component (a) | next_action: "Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op"; blocked_by problems/rootfinding-complete-cost-calibration.md "native work unpriced". Component (a)+(b) is that step with a different price rule. |
| LEAD-RHO-native-step-cost | open_next_step | R | prices canonicalisation "in field-multiplication equivalents" and says section 5a "must price it": same unit family, but Koblitz canonicaliser, not prime batching. |
| LEAD-RHO-matched-rho-calibration | open_next_step | R | its next_action seals prime medium-tier rho.negation / rho.plain / bsgs.negation bounds at log2 r 32-48; no batched or lock-step prime reference, no field-op unit. Component (c) is adjacent, not covered. |
| LEAD-RHO-batched-inversion-shared-pm | closed_known | answered below (S for the mechanism the candidate does NOT propose) | forecloses "Montgomery trick for rho", "simultaneous inversion across walks", "batched affine addition". |
| LEAD-ICP-generic-table-decomposition | closed_obstructed | SO-TABLE, scope applies | see section 5. |
| LEAD-ICE-charged-toy-ic-exponent-vs-rho | open_blocked | R (top-5 of runs 2 and 4) | blocked_by EXP-ICEX-153c34 backend and the C-7 host-load gate; the candidate (correctly) does not claim to unblock it. |
| LEAD-ICP-full-width-arity-grid | open_blocked | L | 50-63-bit solver feasibility, not pricing. |
| LEAD-ICP-gfp5-rho-reference-audit | closed_known | R | F_{p^5} affine rho step with norm-based inversion and batching; a rho-cost instrument, different field. |
| LEAD-ICP-retained-setup-online | closed_dominated | L (6th hit of run 3; YAML not opened, title only) | retained-setup online IC as a per-target win; different object. |
| LEAD-ICB-multi-target-and-portfolio | closed_obstructed | not a hit of runs 1-4; read for SO-MULTI | candidate states no multi-target claim; obstruction (multi-instance generic bound, Table C 3.62-14.9x above batch rho) is untouched. |
| LEAD-TRF-pairing-target-field-recost | open_next_step | L | exTNFS in GF(p^12) with memory charged; lexical hit on "native work unpriced" / "recost". Not same object. |
| LEAD-TRF-same-field-genus-g-embedding | closed_obstructed | L | hit through "native"/"unpriced" tokens only; cover attacks, SO-COVER. |
| LEAD-STR-isogeny-class-generic-invariance | closed_obstructed | L (one tangent) | its revisit_when names "a level-dependent change in step cost (field-arithmetic model cost)" as a constant belonging to LEAD-STR-class-representative-ic-selection; no overlap with batching/pricing of the benchmark unit. |

KR-only top hits not opened beyond their KRMAP row/title and marked lexical-only: KR-IC-a4dd54 (hyperelliptic IC genus threshold), KR-IC-791cb7 (weak binary fields GHS), KR-IC-9e610d (survey consensus), KR-RHO-e7f98e (GPU rho SOTA).

Problem file (not a lead, but the lead's blocked_by): problems/rootfinding-complete-cost-calibration.md already states, verbatim in substance:
- "Missing capability: Serialization and common-unit pricing of native field operations ... inversion counts are absent from sealed ecbench records."
- Observed 2026-10-14: "the sealed ecbench record does not serialize GroupOps.field_ops, so a field-operation improvement is not established there" (72/72 serial/batch pairs match counted cost).
- "Next discriminating step: Expose the already-counted native field operations in sealed ecbench records, price the remaining native operations, and run the frozen L2 lane panel ... Recheck trigger: Native field-operation serialization or pricing."
- lanes-pair-check.json (crypto-main/research/ecbench_rootfinding_lanes_20261013/lanes-pair-check.json) read: widths 4, 8, 16 each "pairs": 24, "all_exact": true, "field_ops_available": false, "inversion_reduced_when_available": null. That is 72 pairs, ratio exactly 1 in counted GAE by construction, and the check script already has a slot for the field-op read-out when it becomes available.

Consequence for the candidate's "first_step" (zero-compute derivation that the batching step is invisible in counted units): this is already recorded in the problem file and in lanes-pair-check.json. It is a restatement, not a new derivation. It is still useful as a one-line note attached to LEAD-ICP-prime-ic-constant-engineering, whose own discriminator ("paired ratio with the interval below 1") is stated without this caveat.

### 3.1 What exists in source today (verified by reading, not by running)

- FieldOps {muls, sqrs, invs} is a counter in ic_boundary.rs; GroupOps carries it with #[serde(skip)]. ecbench Record has an optional field_ops block, written only when the group counts it (methods.rs ~937-980 doc comment: "None is unknown, never zero: binary and Koblitz curves do not count, and the index-calculus pipeline does field arithmetic outside the group law (square roots, Legendre symbols, the oracles, the elimination) that this tally would not see, so it reports none").
- bounds.rs defines FIELD_AXES = field_muls, field_sqrs, field_invs (per sqrt r) as bound/verdict axes for prime generic walks and tables. So a field-op axis already exists for prime rho.
- full_price.rs UNITS already contains field_mul, field_sqr, field_inv; wordram_price.rs already prices them (Fermat inversion I = 2k(M+64)+128(s+1)) and its doc says the prime-field budgets are CurveSmash's, unchanged. Neither file contains the words batch, Montgomery or simultaneous (grep: only the "additions and doublings at one each" comment at full_price.rs:200). base_of in both files lists only ic.pipeline, rho.signed_frobenius, rho.signed_frobenius_strong (Koblitz/binary). So the candidate's claim "twins are Koblitz/binary only" and "no batched-inversion price rule" are both correct.
- Method ids registered in ecbench (methods.rs): rho.frozen_reference, rho.plain, rho.negation, rho.multitarget_pooled, rho.cubic, rho.quartic, rho.frobenius_orbit, rho.gls, rho.signed_frobenius, rho.signed_frobenius_strong; no prime lock-step/batched rho. prime_fast::rho_parallel (prime_fast.rs:826) is documented as "r-adding walk with a 1024-entry table, the negation map with a deterministic fruitless-2-cycle escape, lock-step walkers per thread so every step is batched, and a shared DP table" and uses Fp64::batch_inv (line 192). Candidate's description matches. Its RhoConfig::for_bits clamps walkers_total to >= 32 (line 736), so at toy sizes it carries a lock-step set-up share; see caution C3.
- Committed session record (seal/audit receipt not checked), prime rho.negation, read: research/conductor_gap_rho_large_sample_20261018/sessions/t1-pairs00-02/records.jsonl, first rho.negation row: cost.total_gae = 111569983.0, field_ops = {muls 223508429, sqrs 111692804, invs 111569983}. So invs / total_gae = 1.0000, muls / invs = 2.003, sqrs / invs = 1.001 (one inversion, two muls, one squaring per affine add, serial; the record is flagged lower_bound with canonicalisations_uncharged). The candidate's statement "rho.negation records already serialize them (invs ~ adds, serial)" is confirmed on this record.
- ic_boundary.rs ~3780-3840 (native lane walk adder) increments ops.field_ops (muls += 2, sqrs += 1, and invs += 1 only when not batched). So the lane adder does tally; the tally is simply not written into ic.pipeline records. Candidate's H2' (tallies exact) is consistent with the code I read; I did not run the tests.

## 4. N1 verdict logic

Same mechanism? For component (a) serialize + (b) price in a common unit: yes, it is the named next step of the open problem file and of LEAD-ICE-rootfind-pairtable-oracle; for it the candidate adds one thing, the price rule (3M + I/n per element instead of a flat 0 / 0.1 / 1 GAE per native op). For (c) matched batched prime rho reference with A/A: not covered by any lead's next_action (LEAD-RHO-matched-rho-calibration seals serial prime bounds at medium sizes). For (d) the guard: it is an application of AGENTS.md section 5a ("Never compare a calibrated cost on one side with an uncalibrated one on the other"), not a new rule.

Which open lead does it make sharper? LEAD-ICP-prime-ic-constant-engineering: the paired two-level-batching arm cannot fire its own discriminator in GAE (counted ratio exactly 1 by construction), so a field-op (or L2 wall) read-out is a prerequisite. That is the substantive sharpening. For LEAD-ICE-rootfind-pairtable-oracle, (a) only duplicates the problem file's next step and adds a price rule.

Answer to the closed lead LEAD-RHO-batched-inversion-shared-pm (closed_known, forecloses "Montgomery trick for rho", "simultaneous inversion across walks", "batched affine addition"; revisit_when "An inversion-free step cheaper than 1I/n + 3M per walk"): the candidate does not meet revisit_when (it proposes no step cheaper than 1I/n + 3M; it adopts exactly that price) and does not reopen the lead. It is not a duplicate because it claims no speed-up from the trick; it uses the trick's cost as a ruler for both arms. Any wording in the write-up that presents the 2.0-2.5x batching step as a result, rather than as a prediction to be read out in a new unit, would collide with that closed lead.

## 5. Standing obstructions quoted (obstruction.statement, Scope clause included)

SO-TABLE, LEAD-ICP-generic-table-decomposition (closed_obstructed, kind theorem):
"Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."

SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed, kind theorem):
"Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."

The candidate escapes neither (it says so). Under SO-GEN it is a constant-only instrument, which matches "Every lead in this family moves only the constant". Under SO-TABLE it is a ruler inside the scope. Both statements are quoted from the lead YAMLs, not from the candidate's paraphrase.

## 6. N2 reading (KR hits)

Top KR hits across the four build_frontier_map.py runs: KR-RHO-cb1c58 (Simultaneous (batched) inversion, known_mechanism/proven), KR-RHO-e7f98e (GPU rho, thin SOTA), KR-RHO-825bca (Bos-Costello-Miele cycles/step on standard curves, ~1129 cycles/step for 32-adding walks on P-256), KR-RHO-cd0049 (prime toy negation-map BSGS), KR-RHO-1c2928 (Koblitz lean vs strong lock-step reference), KR-IC-5931ee (naive Semaev IC over F_p cannot beat generic), KR-IC-9e610d (survey consensus), KR-RHO-13bf67 (generic lower bound), KR-RHO-fbd582 (free P-Q beside P+Q, found by reading KRMAP, adjacent).

Known: the 3(n-1)M + I batching cost (KR-RHO-cb1c58), pricing affine rho steps in field operations with batched inversion (KR-RHO-825bca, KR-RHO-e7f98e community literature), and that no prime IC arm is sub-rho (KR-IC-5931ee, KR-IC-9e610d). The candidate's novelty is therefore not literature-level. What is new, stated exactly and narrowly (program-internal instrument content):
1. prime entries in base_of for the *_full / *_wordram twins (ic.pipeline, rho.negation);
2. field-op emission from the prime ic.pipeline records (currently field_ops absent by design);
3. a batched-inversion price rule (per element 3M + I/n) in full_price::reprice_with and the wordram formulas (currently none exists);
4. registering prime_fast::rho_parallel as an ecbench arm with field-op tallies, plus an A/A against rho.negation in GAE;
5. a reporting guard.
No KR claims a result about 1-4. Verdict from N2 alone: known_result for the mechanism, program-internal for the instrument. It does not by itself change the N1 verdict.

Citation provenance (Montgomery 1987, KR-RHO-cb1c58):
- retrieved (WebSearch, standard mode, 2026-10-25): bibliographic existence of P. L. Montgomery, "Speeding the Pollard and elliptic curve methods of factorization", Math. Comp. 48 (177), 243-264 (1987), DOI 10.1090/S0025-5718-1987-0866113-7 (AMS listing https://www.ams.org/mcom/1987-48-177/S0025-5718-1987-0866113-7/ returned by the search; bibliographic existence only, the page itself returned HTTP 403 to WebFetch). The retrieved abstract text does not mention simultaneous inversion.
- retrieved (secondary sources in search results: https://arxiv.org/pdf/2607.11337 and https://arxiv.org/pdf/2501.03245): cost of n simultaneous inversions = 1 inversion + 3(n-1) multiplications.
- recalled / NOT verified: attribution of the trick to that paper (KN-LIT-e72678 in the repo itself says "section 10 (as cited)"). AMS page returned HTTP 403 and the Brent PDF was unreadable, so the full text was not reached. One search result (a blog) dates the trick to 1985, which conflicts with 1987 and is unresolved. The load-bearing part for this candidate is the cost formula, which is retrieved from secondary sources; the primary attribution stays recalled.

## 7. N3 ledger collisions

Greps run over /Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl (2678 proposals, 2131 hypotheses; fields claim/mechanism/title/statement) with terms: field[- _]op, FieldOps, word-?ram, rho_parallel, simultaneous / batch(ed) inversion, Montgomery, two-level, lock-?step, full_price, serializ, field mult, 3M, "GAE ratio", ICPERF, unpriced / native work, inversion amortis. Literal misses: FieldOps, wordram, word-ram, rho_parallel, prime_fast, "GAE ratio", simultaneous inversion (0 hits each). That is a lexical miss only; the semantic neighbours are below.

Possibly same object (id, 100-char claim):
- IDEA-20260815-66496a (proposed): "The lane's C_decomp is destined for an exponent comparison against rho. Wall clocks are machine-, compiler- and load-dependent, and an exponent fitted from them inherits all three. Field-operation co..." NEAREST PRIOR OBJECT in the Semaev lane: mechanism "Instrument the Semaev pipeline to count field operations by type alongside wall clock. Report both per instance." Not opened (index row only). Differs: Semaev decomposition cost (SDEG), no batched-inversion price rule, no rho reference.
- IDEA-20260802-007 (OPENED, ledger/proposals/IDEA-20260802-007.yaml, novelty adaptation): "A SINGLE SHARED CHARGED-UNIT ACCOUNTING LAYER - counting group operations, field multiplications and inversions, table entries and table-build charges with an amortization policy fixed in the contract ..." Same family of instrument (shared ledger, fixed amortization policy, matched frontiers rho-with-negation / BSGS / Kuhn-Struik, planted-bug detection, honest-vs-honest 1.000 +- 0.01). Overlaps the A/A and fairness-guard parts of the candidate. Does not contain the batched-inversion price rule or a prime lock-step reference. Its A/A criterion (1.000 +- 0.01) is tighter than the candidate's 5%.
- IDEA-20260926-c98e92 (OPENED, ledger/proposals/IDEA-20260926-c98e92.yaml, status proposed, RQ-ICPERF-94c86e): "THE SAME-UNIT EXCHANGE RATE: 64-bit word operations per field multiplication, per affine group addition and per W_4 refutation on the archived RC-1 instances ... with the inversion model declared as a row rather than hidden in a constant". Closest prior object for the unit: three inversion-model rows (table lookup, Itoh-Tsujii, Fermat) and it names "Itoh-Tsujii or batched Montgomery inversion, KR-RHO-cb1c58" as the n=131 models. It is binary (F_2[t]/(t^17+t^3+1)), a Koblitz/binary R1 cell, does not cover prime arms, does not define a per-element batched price (I/n amortisation), and has no batched matched rho. The candidate extends this exchange-rate idea to prime arms; it should cite it.
- IDEA-20260808-3f8a2b / H-XOR-a227dc: charged field-operation cost of the x-oracle MITM vs exhaustive search (toy m=3, one field operation = one E.add). Same flat convention the candidate wants to replace; different object.
- IDEA-20260920-0d218c (+ H-GFPN-9a7042, IDEA-20260920-204828): "One affine r-adding rho step with Montgomery-batched inversion on E(F_{p^5}) costs about 5M + 1S in extension-field operations ...". Closed_known via LEAD-ICP-gfp5-rho-reference-audit; per-step rho pricing with batching, F_{p^5}, not the benchmark unit.
- IDEA-20261018-e7a860 (proposed): "Measure K, the column-touch to group-operation conversion for the m=4 oracle ... Count the field multiplications, squarings and inversions per column touch inside the oracle". A unit-conversion measurement for the ECC2K-130 m=4 oracle (binary), not prime batching.
- IDEA-20260926-c98e92 / H-ICPERF-16cf38 / H-ICPERF-888b38 are contract-style arithmetic checks for the same exchange-rate record; no batching.
- IDEA-20260816-c1314e, IDEA-20260903-399a18, H-ICEX-b2c8cf: declare kappa in {1,10,100} or "8 field multiplications per group operation" as a convention; the candidate would replace such conventions on the prime arms with counted values.
- IDEA-20261006-a0e3bd (proposed): one shared inversion for x(P+Q) and x(P-Q) on a toy F_101 curve; referenced by LEAD-RHO-batched-inversion-shared-pm (closed_known). Mechanism, not pricing.
- IDEA-20260807-8e20fe (OPENED, third and last full record): AES lane, counted-op to measured-second conversion as a function of working-set size. Not the same object; conceptually related to "counted units hide hardware effects" only.
- IDEA-20261015-c6f017 / H-CERTBIN-7e3a51: n=131 matched rho (64 lockstep lanes, batched inversion) for ECC2K-130; binary analogue of component (c), no prime.

Records opened in full: exactly three (IDEA-20260802-007, IDEA-20260926-c98e92, IDEA-20260807-8e20fe). None is the same object as C2; IDEA-20260926-c98e92 and IDEA-20260802-007 are partial precedents (unit with inversion-model rows; shared ledger with A/A and matched frontiers).

## 8. N4 notation check

Not applicable in the strong sense: C2 is an instrument. It adds no representation, no factor base, no quotient and no coordinate system. Pair as stated by the candidate: (R1 prime affine IC, Sigma = translation by factor-base sums, partial action) priced against (F1 full-translation generic rho). C2 makes no propagation, projection or rigidity claim, so it cannot re-encode IDEA-20260806-c5d183 (no lossy object propagates under full translation), IDEA-20260901-863e36 (propagation is a property of a projection paired with an operation group), KN-OPEN-020 (bounded-degree algebraic factor bases over F_p scoped out) or KN-FIND-ffe1df Theorem C; it also does not try to escape them. The candidate's own "trichotomy: instrument; no placement" is consistent with how IDEA-20260926-c98e92 treated the same situation ("TRICHOTOMY: not applicable to a unit instrument, stated rather than omitted").

## 9. Cautions the write-up must carry (not verdict-blocking)

C1. Section 5a and 6 of AGENTS.md. The 0 / 0.1 / 1 GAE-per-native-op band must always be reported and a calibrated cost "never replaces the band"; section 6 lists "A ratio improved by moving the boundary, changing the unit, or dropping a cost from the budget" under what does not count. A field-op (3M + I/n) or word-RAM price can therefore only be an ADDED point beside the band, applied to every arm including the reference. The candidate's outcomes_to_dispositions ("Field-op batch/serial upper CI < 0.8 ... best_measured = the ratio") must be read as "added point", not "replacement unit". The candidate's self_kill_risk ("program may decline a field-op unit for the board") is consistent with this.
C2. Lopsidedness of step (a). methods.rs documents that the prime ic.pipeline reports no field_ops precisely because it does field arithmetic outside the group law (square roots, Legendre symbols, oracles, elimination; prime_fast's rootfind avoids sqrt/inversion per element but the u64 Gauss-Jordan mod r, hash probes, coordinate conversion (from_mont) remain). A group-law-only tally would give IC a field-op LOWER BOUND against a fully counted serial rho: exactly the lopsided comparison section 5a forbids ("An arm that names a counter but does not emit its count cannot be ranked"). The candidate's text "(all phases)" must include row operations, probes and conversions, priced by the existing row_op / lookup units, or the IC arm stays flagged lower_bound.
C3. Lock-step set-up share. rho_parallel clamps walkers_total >= 32; KR-RHO-1c2928 measured the analogous strong lock-step Koblitz reference at 71% set-up share at toy sizes. At fp20-fp28 a batched reference may carry an inflated fixed cost that makes IC/rho look smaller. The A/A and a set-up-share column are the right place to see this; the guard should cut both ways (do not divide by the serial reference; do not rely on an uncalibrated batched reference either).
C4. The candidate's predictions (walk-lanes/walk-serial x0.50 at n=8 to x0.41 at n=1024; factor-base phase x0.27; IC-lanes/batched-rho 12-13; serial-reference artifacts 5-6, 1.2 and 0.85) come from derive_c1.py, which I did not rerun. They are the candidate's predictions, not measurements, and are not reproduced here. Only the invs = adds serial structure was checked (section 3.1).
C5. Not unblocked: LEAD-ICE-charged-toy-ic-exponent-vs-rho (C-7 is a host-load gate, DEC-20261001-36e4fa R-2); LEAD-ICE-rootfind-pairtable-oracle also stays blocked on L2 isolation and independent-host replay, as the candidate says.

## 10. Housekeeping disclosure

The scout directory is shared with sibling gates. My first capture wrote scout/raw/atlas1.txt .. atlas4.txt and scout/raw/frontier1.txt .. frontier4.txt with ">" and then moved them to scout/raw-C2-fieldops/ (mv -n). If a sibling gate had files with those exact names at that moment they were overwritten by mine; I did not check beforehand, and the listing then showed siblings' differently named files (atlas_1..5, fm1..4, kr_1..4, la1..4, frontier_1..5). Two sibling gate files mention those names (the C1 commutative-algebra gate states it moved its own copies to a private directory earlier, at about 23:47; the C4 p-adic/tropical gate mentions its own check) and I did not edit them. Nothing was written or modified inside any repository by this scout: all writes are under scout/ (this file, raw-C2-fieldops/); the only other files touched were read-only reads, WebFetch cache and the tool-results copy of a downloaded PDF under ~/.claude/projects/.../tool-results/ (not opened).
