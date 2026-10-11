# TASK-20260926-e93f77 generator report (round 2, seam S6: instruments, cost laws and controls)

Lane: idea-generator, policy research-deep. Written 2026-09-26/28 (the lane was
interrupted by an API rate limit after three records and resumed; the three
pre-interruption files were re-inspected and found complete). No run, no
solver, no status change, no existing record edited. All five records are
`status: proposed`, `approved_by: null`, `novelty_status: unverified` (corpus
grep only; no web search; every external reference `recalled`), and each
carries the `prior_art` block of BRIEF-ROUND2 section 2 with rows read in the
rendered frontier map (`retrieved`).

## 1. The five records

| id | class | question | claim (25 words) | column or record it changes | novelty | cost (estimate) |
| --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-c98e92 | measurement | RQ-ICPERF-94c86e | Word operations per field multiplication, per affine addition (three inversion models as rows) and per W_4 refutation on archived RC-1 instances give the first same-unit oracle cost per attempt. | Adds the UNIT row (exchange rate) to the boundary table; converts KN-FIND-5a8d3e/c3a917 rates into KN-FIND-aa2efc's budget unit. | unverified | impl low; minutes to an hour, pure Python |
| IDEA-20260926-d06324 | control | RQ-CERTBIN-836ce2 | The (L, b) meter run on binary-curve addition for six coordinate projections against Z/NZ and a random bijection; two exact calibration rows; E-MIX predicted. | Creates the saturation control every bucketed-residual or prefix-keyed proposal (faa8d2, 136bd3 Stage 1) must beat; unblocks H-TLD-f4c8ba's dependency. | unverified | impl low; minutes |
| IDEA-20260926-d1adfc | measurement | RQ-ICPERF-94c86e | Per-attempt cost distribution columns (CV, max/median, Hill alpha, censored fraction; sat/unsat separate) populated zero-run from committed msolve and closure rows; Groebner sat/unsat symmetry tested. | Adds four columns to the boundary-table schema; fills them for every committed engine cell; gives 793fd8's closure a number. | unverified | impl low; seconds, zero solver runs |
| IDEA-20260926-d3c5a5 | tooling | RQ-CERTBIN-836ce2 | Binary port of the prime-field table-of-tails MITM engine as exact, certificate-producing, generic ground truth for m = 3, 4 cells; calibration line theta_mitm = floor(m/2)/m. | Supplies the ground-truth oracle and the second known-answer line for 4b65e3's cap-locus ladder and 89886c's m = 3 design; adds a "generic oracle" row per cell. | unverified | impl medium; minutes per cell (loop ground truth up to an hour) |
| IDEA-20260926-dacb83 | measurement | RQ-ICPERF-94c86e | Memory-charged column at the cap locus with both Frobenius-collapse readings, oracle working set and two rho storage conventions; predicts the oracle, not the matrix, binds at m >= 5. | Adds the memory column (M1-M4, P*, binding component) to the boundary table and the ECC2K-130 row of 6028ed's carrier; can invert 2e2a58's (E2) at the cap. | unverified | impl low; seconds (Stage 0) plus minutes (Stage 1) |

Every record states its target arity and its position against the budget
column (none can move a row; c98e92 and dacb83 change the unit and the memory
axis in which rows are read), carries a runnable-shaped cell on the CERTBIN
instruments or on committed index_calculus rows, controls (null object,
Koblitz sibling, relabelled Z/NZ where a group-structure claim is made), a
three-row outcome table, a pre-registered falsification threshold and an
order-of-magnitude cost labelled as an estimate.

## 2. Ranking rationale (expected information gain against cost)

1. **d1adfc first.** Zero solver runs, seconds of compute, on rows already on
   `main` (687 msolve per-target timings with sat/unsat decided by exhaustive
   enumeration; per-instance closure wall times at n = 17 and 19). It has two
   independent falsifiable readings (E-LIGHT/E-HEAVY on the tail; E-SYM/E-ASYM
   on the Groebner sat/unsat ratio), and either surprise would change what a
   budget MEAN means for every m >= 4 row and what "the full solve" means as
   89886c's comparator. It is the cheapest valid discriminator in the lane
   because its inputs exist and its nearby-object control (the fixed-shape
   closure, which must read light) is in the same data.
2. **dacb83 second**: seconds of arithmetic that, if the recomputation holds,
   inverts the lane's habitual memory verdict at the cap locus (the oracle's
   working set, never charged on any ECC2K-130 row, binds; the collapse moves
   nothing that binds) and forces every m >= 5 oracle proposal to declare
   bytes. Its toy validation is an accounting check on archived checkpoints.
3. **c98e92 third**: the unit row; a prerequisite for reading any CERTBIN
   refutation cost against the budget column, with a pre-registered band
   (closure-to-oracle-A ratio in [2^8, 2^15]) whose violation in the cheap
   direction would re-rank 89886c.
4. **d06324 fourth**: the controlled null the closure standard asks for, with
   numbers; its expected outcome moves nothing, its unexpected outcome
   (E-PARTIAL) would be the only exponent-relevant surprise a control here
   could produce.
5. **d3c5a5 fifth**: tooling whose value is realised only when 4b65e3's ladder
   or 89886c's m = 3 design is approved; medium implementation cost.

## 3. Candidate not filed, and why

"theta(m) at the cap locus for m in {3, 4} on the CERTBIN cells" (the card's
third candidate) is already, verbatim, the `minimal_test` of
IDEA-20260926-4b65e3 (Stages 1-2, cells (17,3,7), (19,3,8), (17,4,6), (19,4,6),
loop and closure oracles, sat-fraction gate). Re-filing it would be the
duplication BRIEF-ROUND2 section 1 forbids. Instead d3c5a5 supplies the
instrument that makes that ladder affordable (its top loop cell drops from
hours to seconds) and its second known-answer line (floor(m/2)/m beside the
loop's 1 - 1/m and the budget's 1/2 - 1/m). This is duplicate avoidance, not a
closure.

## 4. Inventor-protocol section 5 block

- **Objects considered.** (a) The unit of per-attempt oracle cost (word
  operations; the inversion model as a row). (b) Coordinate projections of the
  abscissa on E(F_{2^n}) as branching objects under the full translation
  action (top-k prefix in polynomial and normal basis, Hamming-weight class,
  halving-trace bit, x-coordinate). (c) The per-attempt cost DISTRIBUTION of
  measured engines. (d) The h-fold sumset table keyed by abscissa (a solver
  choice inside F2, not an object). (e) The memory footprint of an ECC2K-130
  row decomposed into matrix, oracle working set and DP store. None is a new
  tracked object; (b) is the lossy-projection test executed, and its
  pre-registered reading is that no listed projection propagates partially
  (E-MIX).
- **Depth of verified structure.** Zero compute this session. Deterministic
  content: the halving-trace bit is the E -> E/2E homomorphism on the
  composite group (to be re-verified exhaustively at setup, criterion
  recalled); theta_mitm = floor(m/2)/m at the cap locus (derivation from the
  README's model and 4b65e3's locus, my arithmetic); the byte formulas of
  dacb83 (arithmetic under stated storage models, to be recomputed). All
  numbers are labelled estimates or hand arithmetic pending recomputation.
- **dominated_by.** Every record: `n/a (no result claimed)` after checking
  every row of the rendered frontier map; rho at 2^60.81 dominates every
  ECC2K-130 index-calculus row on time and, under the Theta(P) storage floor,
  on memory. d3c5a5 additionally records its toy Pareto position (dominates
  the loop on time, dominated by it on memory) and its closure on ECC2K-130
  at every m by the product law (per-attempt 2^{floor(m/2) n/m} against
  2^{(1/2 - 1/m) n}).
- **sota_delta.** Zero on every ECDLP cost axis for all five. Against the
  program's prior state, quantitatively: the first measured (not declared)
  exchange rate with the inversion model as a row (c98e92); the first
  execution of the (L, b) meter on any curve (d06324); the first tail-index,
  CV and censoring columns for any measured engine (d1adfc); the first
  binary-curve MITM oracle and the exponent form of the generic line at the
  cap (d3c5a5); the first ECC2K-130 memory column charging the oracle's
  working set, both rho conventions and both collapse readings, with P* per
  row (dacb83; predicted P* about 2^26.7 / 2^19.7 at m = 5).
- **Enumerated closures with mechanism.** None new. Re-stated, each with its
  mechanism and source: the generic MITM oracle is closed on ECC2K-130 at
  every m because its per-attempt cost is one factor B_cap above the budget
  line at even m (product law, KN-FIND-aa2efc; locus, 4b65e3; this lane's
  exponent form); the restart portfolio is closed by concentration of the
  attempt-cost sum unless alpha <= 1 (793fd8 review), which d1adfc measures.
  The "theta(m) at the cap" candidate was not filed by duplicate avoidance,
  not closure. Novelty of all five is `unverified`.
- **Open directions for the next session.** (i) A word-operation counter for
  a SAT engine's conflicts and an F4 engine's matrix operations, so c98e92's
  unit covers the engines the boundary table actually wants (none installed
  here). (ii) If d1adfc reads E-ASYM on msolve, a mechanism record on which
  direction and why. (iii) If dacb83 reads E-MATRIX-BINDS at m = 4, hand the
  collapse sensitivity to BATCH-b67954 (b19793) as an input; the rank
  question stays theirs. (iv) A general-n field module at n <= 31 is the
  shared prerequisite of d3c5a5's optional extension and 4b65e3's ladder.
  (v) The external note's section 6.2 (EV-ICPERF-10c5fc, unhashed) should be
  opened by a session with retrieval and compared with dacb83's column.

## 5. Unused ids

None. All five pre-minted ids were used in the order given on the card:
IDEA-20260926-c98e92, -d06324, -d1adfc, -d3c5a5, -dacb83.

## 6. Files written (and nothing else)

- ledger/proposals/IDEA-20260926-c98e92.yaml
- ledger/proposals/IDEA-20260926-d06324.yaml
- ledger/proposals/IDEA-20260926-d1adfc.yaml
- ledger/proposals/IDEA-20260926-d3c5a5.yaml
- ledger/proposals/IDEA-20260926-dacb83.yaml
- analysis/binstd-idea-review-20260926/reviews/TASK-20260926-e93f77-generator-report.md

Parse check: this lane has no shell; the files were inspected for the
known hazards (prose containing `: ` only inside `>-` blocks, list items
with colons or apostrophes single-quoted with doubled quotes, flow lists
only for ids). The dispatcher's `python3 -c "import yaml;
yaml.safe_load(open(path))"` is the authoritative check and should be run
before archiving.
