# External ECDLP idea corpus — non-canonical dedup input

**Status: pointer index only. Nothing here is an allocated idea, a canonical ID,
a contract, or approved evidence.** No row in this file has passed this program's
deduplication or red-team review, and only the Coordinator may allocate an ID or
change an official state. The file exists so that the Idea Generator and the
dedup pass can screen *against* an external corpus instead of rediscovering or
duplicating it.

The external work lives in a separate workspace (`/Volumes/Volume/research/`) and
was produced outside this repo's ledger, contract, and run-receipt discipline.
Paths are recorded verbatim so a reviewer can read the primary bytes.

## Why this is not a bulk import

The canonical corpus already spans IDs `001`-`410` with 17 active, 27 deferred and
366 rejected records, all screened by named dedup and red-team passes. Minting IDs
for externally-generated mechanisms without those passes would (a) bypass the
review gate and (b) very likely re-create existing rejections — the external
catalogue below was mined against a different taxonomy (R6/K1/K2/Defect-B/CM
cells) and has substantial expected overlap with existing scoped negatives.
Screening is a Coordinator-run operation, not a file copy.

## Pointer index

| External source | What it holds | Relevance here |
|---|---|---|
| `inputs/idea_generation_20261005_coordinate_orbit_non_ic_non_rho.md` | Six coordinate/orbit alternatives with toy measurements on seven ordinary prime-order groups and two anomalous controls | **Screened external packet.** Five mechanisms map to existing records or known results; the carry-ranked binary branch score is a distinct tested variant with no stable control advantage. H3's matched-random result directly bears on ECDLP-IDEA-110. No IDs allocated. |
| `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md` | Frozen ECDLP mechanism follow-ups from p-adic cocycles through compact representative and state-fingerprint tables | **Screened external mixed results.** Early cocycle/beam/coordinate successors failed their gates; exact rational-addition structure led back to signed/shifted BSGS. Later capped sketches, nonlinear fingerprints, stopping rules, minimum-ticket representatives, and compact state reuse measured time-memory-validation frontiers on toy curves, including complete recovery, but no new exponent. No IDs allocated. |
| `ECDLP_MECHANISM_CATALOG.md` | ~111 prime-field mechanisms mined from an external corpus, mapped to R6 / K1 / K2 / Defect-B / CM cells | **Largest unscreened input.** Candidate generation + dedup screening against IDs 001-410 |
| `LIT_REVIEW_PRIME_FIELD_ECDLP.md` | 23-paper review, 8 field cards, dedup tags | Literature cross-check for `knowledge/literature`; names three untouched gaps: syzygies/Betti, singular loci of the Semaev ideal/variety, and Yokoyama semi-normality (flagged there as the top F_p test) |
| `ISOGENY_SEMAEV_REVIEW.md`, `isogeny-semaev/` | Four-channel isogeny x Semaev sweep, alpha-stable factor bases, GLV/CM orbit folding, scaling study | Verdict recorded below|
| `POLLARD_RHO_FRONTIER.md` | Six-lens adversarial survey of rho improvements (0 live / 9 capped / 17 dead) | Verdict recorded below|
| `ecdlp-autolab/PKM_ANALYSIS.md` | Prime-field index-calculus analysis (incl. P-521/P-256 scope, bounded d_reg) | KN-OPEN-001 / KN-OPEN-002 prior art |
| `ecdlp-autolab/P256_HIDDEN_STRUCTURE.md`, `P256_FORMAL.md` | P-256 five-routes note; End = O_K and k = (n-1)/3 proved + certified; weak-neighbour definition, JMV reduction | Curve-specific structure claims with machine-checked certificates |
| `ecdlp-autolab/SAT_VS_GB.md` | SAT vs Gröbner solver comparison for ECDLP systems | Alternative-solver lane for KN-OPEN-002 |
| `ecdlp-autolab` (ML-guided policy) | Learned triage + Gröbner ordering; decomposition signal real at n=8, gone by n=10 | Negative scaling result for learned heuristics |
| `EC_SIEVE` last-corner probe | Non-algebraic predicates pushed to d = 8,16,32,64 via Walsh/linear correlation; signal ~1e-3 flat, no growth | Closes a sieve-predicate corner; no entry here yet |
| `QUANTUM_CIRCUITS.md` | Shor-on-ECC circuit review; inversion is the bottleneck | Out of scope for the classical program; recorded for completeness |
| `ecdlp-cost-challenge/research/rho96/` | Checkpointed 96-bit rho attempt, stopped at ~7.2%, `solved 0` | Operational baseline cost datapoint (see the rho verdict below) |

## Recorded verdicts (summaries, not knowledge entries)

These results are **not** `knowledge/findings` entries. That schema requires
`internal_refs` resolving to this program's own ledger records, and these have
none: they were produced outside this repo's ledger, contract, and run-receipt
discipline and have not been re-run under this harness. They are recorded here as
a screening prior so the corpus is not re-derived, and they carry no approved
state.

- **Coordinate/orbit alternatives produced no new canonical survivor.** Seven ordinary
  prime-order toy groups (orders 83 to 947) and two anomalous controls tested scalar-bit
  prediction, function-field interpolation, a spectral shift decoder, carry-ranked
  binary descent, coordinate recurrences, and a generalized p-adic lift quotient.
  Interpolation required orbit-sized advice; recurrences had complexity `r` or `r-1`;
  and the ordinary p-adic arm stayed at 0-3.1% while both anomalous controls recovered
  96/96 logs. Most importantly, the spectral decoder's predeclared matched-null rule
  passed on 0/7 curves: random relabelings and random phases needed the same 15-20%
  mode fraction. This is external screening evidence for ECDLP-IDEA-110, not a
  repository evidence record. The binary carry/height score is a narrow distinct
  variant of published binary division and adjacent to ECDLP-IDEA-034/005, but it
  did not consistently beat a scrambled control. Source:
  `inputs/idea_generation_20261005_coordinate_orbit_non_ic_non_rho.md`.
- **Five preregistered coordinate/orbit successors also fail their gates.**
  Four-section p-adic cocycle arithmetic was exact and both Smart controls
  recovered 96/96 logs, but all six signed/dyadic formulas changed with the
  section and had 0/7 ordinary-curve support. Separately, scalar-balanced
  inverse-doubling beams gave W90 exponent estimates 0.731 (height) and 0.621
  (carry), with upper 99% bounds above 1/2; neither score beat both controls for
  every generator on any curve. A stricter largest-scalar-bucket diagnostic
  increased the estimates to 0.970 and 0.938. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
  A third successor sought `f(Q+P)-f(Q)=1` outside explicit exceptions. For
  `f in L(mO)`, the residual has pole degree at most `2m`, forcing the
  undercharged bound `d+e >= ceil(r/2)`. All planted controls passed, but no
  curve beat both matched controls on all four generators (0/7). This closes
  only the explicit sparse-exception representation, not every compact dense
  correction rule.
  Finally, a six-channel block-Hankel successor had exact joint autonomous
  linear-state dimension `r` on every curve and generator because required
  scalar channels already had complexity `r`. Both matched controls did too
  (0/7 strict support), and no sub-square-root state-to-index decoder was
  supplied. This closes the frozen linear state, not nonlinear models.
  A fifth successor trained a frozen 172-term coordinate grammar with
  leave-one-curve-out and scalar holdout. All 28 one-sided 99% lower parity
  advantages were negative, no generator beat all matched refits, and support
  was 0/7; recursive peeling was not run. This closes only the frozen grammar,
  not every mathematically derived generator-covariant predicate.
- **Structured spectral continuation exposes exact rational-addition structure.**
  Baby/giant coordinate phases required 78%-93% row rank for 99% energy and
  matched controls. Denominator clearing then produced an exact rank-four
  factor for `(x_B-x_A)^2*x(A+B)` and rank-one second Cauchy displacement on
  all 28 curve/generator cases; shuffled/random outputs returned to full rank.
  A subsequent exact Gauss expansion was dense: square-root mode budgets kept
  3%-11% energy with roughly 0.95-0.99 matrix error, while 90% sign accuracy
  appeared near `p/2` modes. These are external measurements and algebraic
  identities, not canonical findings or a claimed ECDLP algorithm. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Full-coverage continuation isolates two corrections but target decoding is BSGS.**
  Direct factor summation and a joint residue/scalar transform were exact, yet
  tensor ranks matched controls and dense 2D state expanded to 93--895 entries
  per rectangle cell. A quotient/remainder layout then covered the entire
  scalar orbit with an exact rank-four character base plus exactly two
  singular corrections on all 28 cases. Translating the layout by a target
  recovered all 9,096 toy logs through a guaranteed signed point collision,
  using square-root labelled baby/giant tables. This is an end-to-end positive
  control and exact representation, but its decoder is Shanks
  baby-step/giant-step prior art rather than a new ECDLP method. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Table-free collision aggregates trade memory for work but do not yet improve
  both.** An exact `F_(p^2)` resultant stream recovered all 9,096 targets with
  12 working field elements but linear pair work. Hashed two-moment buckets cut
  query work and reached 99.7%, but required substantially more storage than
  the original labelled point table; the only sub-table row recovered 3.6%.
  The label quotient was audited across `F_p` versus scalar order `r` and now
  emits every integer lift. These are time-memory measurements of the same
  collision mechanism, not a new generic ECDLP exponent. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Sequential sketches buy collision-table memory with repeated square-root
  passes.** Capped singleton sketches recovered all 9,096 original targets by
  16 seeds and all 12,288 larger-order samples by 16 seeds. At fixed sub-cap
  memory, one-third of H20's coordinate cap reached complete recovery by 256
  seeds; one-quarter reached 3,065/3,072. An x-coordinate negation quotient
  validated 171/171 inverse-pair label-sum decodes, recovered 3,069/3,072, and
  complemented every point-sketch miss. Exact occupancy predictions, controls,
  and peak-memory accounting are retained. This remains a time-memory variant
  of signed/shifted BSGS, not a non-generic exponent improvement. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Validation-backed nonlinear x fingerprints reduce one charged resource but
  retain a multi-resource trade.** Equal-work point/x alternation did not beat
  either single representation's first complete prefix. A three-element
  validation-backed pair cell then recovered all 3,072 frozen targets while
  rejecting 27,429 pair candidates. A keyed quadratic fingerprint reduced
  total scalar validations by 13.02% but added 396.6 million field
  multiplications. Fixed one-multiplication fingerprints retained complete
  recovery; the frozen `x^2+2x` arm used 141,975 validations, 71 fewer than the
  keyed arm, while charging more additions. Exact scalar-path accounting was
  nonmonotone across prefixes and failed its strict every-prefix gate. These
  are toy time-memory-arithmetic frontiers of the same signed/shifted collision
  mechanism, not evidence of a new ECDLP exponent. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Early stopping and compact representatives improve the measured constants,
  not the collision exponent.** First-success stopping cut the prior full-scan
  charges to 3.46%--4.46%. Deliberately nonuniform occupancy then reduced
  average constructed seeds from 12.21 to 4.70. Minimum-ticket representatives
  reduced this to 1.95, and a two-field selected-x/label layout to 1.49 while
  completing all 3,072 targets by eight seeds under the quarter-H20 cap. A
  two-choice cuckoo layout raised retention to 47.98% and improved early
  recovery, but did not improve the eight-seed completion prefix; bucket reads
  rose 76.22% and its strict gate failed. One invalid shuffled-control run is
  retained alongside the corrected reproduction. These are min-wise/cuckoo
  time-memory variants of signed/shifted BSGS, with no claimed new primitive or
  ECDLP exponent. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **Label-only state reuse further trades construction and memory reads for
  validation work, without changing the square-root collision lineage.** A
  one-field label table completed all 3,072 targets by six seeds but raised
  validation work about 70-fold before filtering. Reusing its charged state
  bits then cut validations 49.23%; a wider state map cut another 43.08% but
  lost early recovery. Ordered ternary and sentinel-quaternary reuse restored
  the larger table and cut validations 32.10% and 48.09% relative to the
  one-bit arm. A decoy-first lookup preserved recovery and validation while
  bringing combined logical query reads 7.01% below that arm. Sorting,
  transient storage, sentinel checks, and all failed gates are retained. An
  audit then replaced inherited harness-only target-scalar seeding with one
  canonical public target-point derivation; all gates passed, with 3.66% more
  validations. All eight preregistered public salts completed by seed 6, and a
  six-equation held-out rerun completed by seed 8. At orders through 524,053,
  recovery and exposure-normalized reads retained their gates, but absolute
  validations rose to 314,428--331,137 and failed the frozen bound. A sealed
  nine-curve decomposition measured validation slopes 0.4365--0.4632 and read
  slopes 0.4658--0.4961. Same-cap fingerprint widening from three through six
  bits then repeatedly passed, with the six-bit arm using 55.02%--58.10% of
  the preceding five-bit validations while retaining all eight completions by
  seed 6. A seven-bit boundary arm missed its primary gate on one salt, despite
  passing correctness and operation gates. Two attempts to carry that extra
  bit in the stored label rank preserved correctness but missed completion or
  read gates. Jointly selecting the existing sentinel as the public stream
  offset removed that loss: all eight salts completed by seed 6, validations
  and operations were 56.55%--59.17% and 56.37%--58.96% of the matched six-bit
  arm, and reads were exactly unchanged. Its held-out transfer preserved
  correctness, recovery, layout, and reads but missed completion, validation,
  and operation gates. Packing the label field's full unused radix with an
  independently mixed public tag then passed every held-out and scaling gate.
  On six 2K--64K curves it used 41.08%--43.16% of paired six-bit validations;
  on 128K--512K curves that fell to 15.60%--16.88%, with exact reads and
  recovery and 361--723 tag states. Replacing SplitMix64 with `x mod
  tag_states` preserved every recovery/read/layout outcome and gave replicated
  1.065--1.066x reduced end-to-end Python timing ratios. Low-bit power-of-two
  tags also preserved the full protocol. Per-call mask derivation was about
  21% slower than modulo; precomputing it was about 10% faster in isolation,
  but two integrated decoder runs failed their timing gate despite fewer
  charged validations and group operations. These are compact-hash
  representation measurements of signed/shifted BSGS, not a new ECDLP
  exponent. Source:
  `inputs/idea_generation_20261006_padic_cocycle_beam_followups.md`.
- **GLV/CM orbit folding is a bounded constant, not a scaling win.** Measured
  `save_IC ~ 3-6`, **flat** across p ~ 2^12..2^24 for all five tested
  D = 5 mod 8 discriminants. An earlier apparent **~30x** seed-efficiency was a
  collection-free/small-`c` accounting artifact; once relation collection is
  charged it reduces to the bounded 3-6. Verifier 250/250, so the arithmetic is
  real but not asymptotically useful. Bears on KN-OPEN-003 (symmetry lane) —
  symmetry moves constants, in the same family as GLV/GLS and negation-map rho
  speedups (KN-TECH-018), not exponents.
  Source: `isogeny-semaev/` and `RESULTS_PILOT.md`.
- **Semaev solving complexity behaves as an isogeny-class invariant.** A
  four-channel sweep returned three nulls: walking to an isogenous curve does not
  move solving complexity. The one positive is bounded — an alpha-stable
  (FHJRV-symmetrized) factor base enriches relation yield **7-16x** but does
  **not** lower the per-relation solving degree (at n = 10,
  `corr(vsdim, gb) ~ 0.94`, matched difference ~0). More relations per unit
  search, same cost per relation. Single toy size; a null channel closes only the
  exact tested boundary. Source: `ISOGENY_SEMAEV_REVIEW.md`.
- **No live generic speedup remains on the rho baseline.** A six-lens adversarial
  survey classified 26 candidates as **0 live / 9 capped / 17 dead**: every
  candidate is either absorbed by the known constant-factor toolkit (negation
  map, distinguished points, parallel collision search) or fails. This fixes the
  denominator for KN-OPEN-001 — an index-calculus claim must beat a baseline
  whose exponent is fixed at 1/2 with well-optimized constants. Identified next
  measurements are joules-per-step and negation-ON bitslicing, i.e. cost-model
  refinement. Source: `POLLARD_RHO_FRONTIER.md`. Operational datapoint: a
  detached 96-bit rho attempt reached ~7.2% of expected work, `solved 0`.
- **Prime-field S_3 decomposition cost (internal, EXP-SEMAEV-001).** A *fixed*
  factor base degenerates the measurement: decomposition probability ~ F^2/2p, so
  at bits >= 12 the target stops decomposing and the basis collapses to `{1}` —
  `basis_size=1` / `max_degree_proxy=0` are degenerate values, not cheap solves.
  Gröbner cost is a function of **F alone** (identical to three significant
  figures across field sizes at fixed F). With `F = ceil(sqrt(p))` the
  measurement is restored and cost grows as **p^1.2-1.5** per decomposition test.
  This result lives with its experiment, in
  `experiments/EXP-SEMAEV-001/factor-base-scaling/README.md`, which records the
  full tables and caveats (toy scale, sympy Buchberger not F4/F5, and
  `max_degree_proxy` confounded by the ideal's solution count).

## Suggested screening order

1. `ECDLP_MECHANISM_CATALOG.md` — highest volume, highest duplication risk.
   Screen cell-by-cell against the rejected corpus before any ID allocation.
2. `LIT_REVIEW_PRIME_FIELD_ECDLP.md` gaps — the syzygies/Betti and singular-loci
   items are adjacent to KN-FIND-006,
   whose open question is exactly a Betti-number count; semi-normality is
   currently near-absent from `knowledge/`.
3. The remaining rows are already summarized as findings or are out of scope.

Nothing in this file is a breakthrough, a promotion, or a claim that any listed
mechanism works.
