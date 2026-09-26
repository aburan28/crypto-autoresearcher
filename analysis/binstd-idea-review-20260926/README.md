# Index calculus for the ECDLP on ECC2K-130: review of the remaining RQ-BINSTD-b6f698 proposals and a fresh ideation round

Date: 2026-09-26. Branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv`, base
`a36978c0` (= `origin/main` at session start). Working analysis and proposals
only: nothing here changes a hypothesis, experiment, goal or proposal status,
and no run was launched. The dispatch brief is `BRIEF.md`; the six lane cards
are in `handoffs/`; per-idea reviews and lane reports are in `reviews/`.

## 1. What was asked and what was done

User request: review the rest of the index-calculus ideas for the ECDLP on
ECC2K-130 and establish new novel ideas with concrete experiment examples.

"The rest" is the 26 of 30 proposals filed on 2026-09-22 under
`RQ-BINSTD-b6f698` that `DEC-20260924-99ce20` did not select for design (the
selected two, `IDEA-20260922-7d6d43` and `-261004` with its absorbed `-b19793`
and `-dacfc2`, are in revision design batch `BATCH-b67954` and were not
touched). That decision weighed the 26 at the level of a ranking report and
said so; this round re-read every one in full, with independent arithmetic.

Six lanes ran (seven sessions; one reviewer session produced nothing and was
re-run as two halves):

| lane | card | work | output |
| --- | --- | --- | --- |
| R1 | TASK-20260926-002d0e | 7 queued_for_design proposals | `reviews/IDEA-*.yaml`, `reviews/TASK-20260926-002d0e-summary.md` |
| R2 | TASK-20260926-5d1a51 | 9 design_after proposals | same pattern |
| R3 | TASK-20260926-843cf5 | 11 return_for_revision and hold proposals, in two halves | `reviews/TASK-20260926-843cf5-summary-{a,b}.md` |
| G1 | TASK-20260926-995431 | seam: the arity lever against the product law | 4 proposals |
| G2 | TASK-20260926-aa3c9f | seam: solver-side asymmetry at the measured CERTBIN cells | 4 proposals |
| G3 | TASK-20260926-b3c93a | seam: representation objects specific to ECC2K-130 | 3 proposals, one id returned unused |

Every review YAML follows the schema in `BRIEF.md` section 6 and carries a
runnable-shaped concrete experiment. Every new proposal follows the lane's
record form (`agents/idea-generator.md` plus the extra fields of
`IDEA-20260922-845a77`), is `status: proposed`, `approved_by: null`,
`novelty_status: unverified`, and carries a concrete experiment cell in
`minimal_test`. All 13 new ids were minted with `tools/allocate_id.py --next`
and confirmed with `--check`; all 13 appear in
`python3 tools/ecc_priority.py --open-ideas`.

## 2. The frame every result is read against

Three numbers from the corpus bound what any index-calculus line can do on
ECC2K-130 (details and record ids in `BRIEF.md` section 2):

- Matched rho with negation and the 131-fold Frobenius class reduction is
  about 2^60.8 iterations (`KN-FIND-aa2efc`, `KN-LIT-661e97`). Every reviewer
  re-derived it; lane R1 reproduces 2^60.8090 from the exact 130-bit prime
  `l`, and R3a confirms `l` prime and `#E = 4l` by the Frobenius-trace
  recurrence.
- The product-law floor (`KN-FIND-aa2efc`, unreviewed external provenance):
  even a free decomposition oracle costs 2^68.58 at arity m = 3 and 2^56.40
  at m = 4, so m <= 3 cannot beat rho and m = 4 leaves about 2^4.4 group
  operations per attempt. Lane R1 reproduced the finding's table exactly as
  `min over l of m! 2^(131-(m-1)l) + m 2^(2l)`; lanes R3a and R3b, using a
  different balance, got floors 1 to 3 bits lower with the same ordering and
  verdict. Lane G1's `IDEA-20260926-4b65e3` argues the finding's oracle-budget
  column understates the budget at m >= 5 by 17 to 20 bits once the
  per-target cap is enforced and B re-optimised; that is a proposal, not a
  finding, and its Stage 0 is a zero-run recomputation.
- No Frobenius-stable F_2-subspace of useful dimension exists at n = 131
  (`ord_131(2) = 130`), the F_2-coefficient quasi-subfield bases are closed
  (`KN-FIND-617d78`), and Frobenius on the descended system is an
  equivariance between conjugate targets, not a per-instance symmetry
  (`IDEA-20260906-a77711`).

Read plainly: on ECC2K-130 the only exponent-relevant lever left in the
index-calculus family is arity m >= 5 with a decomposition oracle whose cost
grows slowly in m. Every review and every new proposal states where it sits
relative to that.

## 3. Review verdicts for the 26 remaining proposals

| idea | rank / disposition (DEC-20260924-99ce20) | verdict | agrees with hold | one-line finding |
| --- | --- | --- | --- | --- |
| 1a081a | 7 queued (HOLD-B) | sound_with_corrections | yes | Curve-blindness census stands; its C3 sign depends on the realised Frobenius relation gain G against sqrt(2m), which no record measures. |
| c07598 | 8 into 1a081a | sound_with_corrections | yes | Aut(E) = Z/2 for every ordinary binary curve (j = 1/b), so rho symmetry is exactly 2k on all five c2pnb rows; corrected rows +0.25 bit. |
| 6cf862 | 11 queued (HOLD-D) | sound_with_corrections | yes | Emptiness certificate holds on all five rows; net movement is sqrt(k) not sqrt(k/2); c2pnb208w1 has the most product-law headroom in the population. |
| 29b1c5 | 12 queued (HOLD-E) | defective | NO | The lemma is false as stated (proof drops sqrt(b)); iota-stable subspaces are exactly b^{1/4} F_{2^d}, one per divisor d of n. Prime-row emptiness survives; the composite-row verdict hides a live object. Return for revision. |
| 6028ed | 13 queued (HOLD-F) | sound_with_corrections | yes | Carrier must be sharded write-once records, not one YAML; schema lacks unit, m, floor and budget columns, convention pointer, provenance tier. |
| 818b73 | 14 into 6028ed | dominated | yes | gamma* is KN-FIND-aa2efc's per-m budget column, uncited; its worked example conflates two QSP cells (same-cell gap is >= 49 bits, not 72). |
| 77bf31 | 15 queued (HOLD-G) | sound_with_corrections | yes | Stage 1 grid unrunnable at six of seven n (no tau-stable V at l = ceil(n/m) except (17,2,9), (23,2,12), (31,2,16), (31,3,11), (41,2,21)). |
| d11575 | 16 design_after (HOLD-H, T2) | sound_with_corrections | yes | 0.9 to 12.3-bit advantages reproduce under its own convention; C1 closure conditional on the unread Hess theorem; MMT body unread. |
| 0e3641 | 17 into d11575 | sound | yes | tau(N) census reproduces; a proof, so a section of d11575. |
| f37254 | 19 into cdca3a | sound | yes | Basis sparsity as a c_leaf lever; merge with 9d12bd and 99294c into one basis design. |
| 9d12bd | 20 into cdca3a | sound_with_corrections | yes | Same seam; width-matched relabelling null added. |
| 99294c | 21 into cdca3a | sound | yes | Basis invariance question is real; fold into ICPERF's boundary table as one coordinate. |
| 8ac1ea | 22 design_after (HOLD-J) | sound | yes | The K-163/B-163 single-coefficient factorial is well designed; the C-GK null exists nowhere in the standard; decisive arm runs solver-free. |
| 1b16d7 | 23 revision (HOLD-K) | defective | yes, larger than the hold implies | Parity is reversed: Tr(a) = 1 rows are empty at ODD m, and the affine half {c_0 = 1} is aligned at every m. The "six helped, five emptied" split dissolves; net gain is one bit at any m. |
| 153a90 | 24 into 1b16d7 (T5) | sound_with_corrections | yes | Closure overreaches its own Sigma; part D wrongly calls pi a rho amortisation; the E/4E class census is the cheap test. |
| 8278db | 25 design_after (HOLD-L, T4) | sound | yes | Model record: computes a 27 to 73-bit "apparent break" to discredit it; regime ratio >= 1 at 3 of 5 rows; rho_reg = g/log2 q is a reusable overclaim tripwire. |
| 2e2a58 | 26 design_after (HOLD-M) | sound_with_corrections | yes | Only record that can invert a time-axis verdict on memory: the binding rho axis is N^{1/(m+1)} storage, not parallel width. |
| 9e5383 | 27 design_after (HOLD-N) | sound_with_corrections | yes | Null reasoning wrong: n = 31 hosts 128 stable subspaces (ord_31(2) = 5); the right null is a primitive prime (ord_n(2) = n - 1) such as 37. |
| e3048d | 28 revision (HOLD-O) | defective | yes | "Quotients of the 2-Sylow are trivial or all" is false (Z/4 -> Z/2); the h = 1 null is impossible in the family; part B is factor-base size, not a cofactor lever. |
| 845a77 | 29 hold (HOLD-P) | dominated | yes, reason corrected | Undominated time/memory row against 96c4f3, but the product law kills it: probe cost 2^54 at m = 4 against a 2^4.4 budget. faa8d2's factor bounds a construction nobody filed. |
| faa8d2 | 30 into 845a77 | sound_with_corrections | yes | Correct arithmetic on a strawman; c_amort* stated three inconsistent ways (correct form 2^{-l} m2!/(m-1)!). |
| c2bbe6 | 31 revision (HOLD-Q) | dominated | yes | Single-large-prime is sqrt(2NB) >= 2^66 attempts at B = 1 against rho 2^60.8; the GTTD form is a new proposal, not a revision (seeded to G1 as 1db0e8). |
| 7ab503 | 32 revision (HOLD-R) | defective | yes | x -> x^2 maps the system for R to the system for sigma(R); no stable V at 131 or 163; the parser point is stale. |
| 2a3771 | 33 revision (HOLD-S) | defective | yes | Its Lemma A2 fails; the toy ladder is half empty (n = 29, 37 host no stable V); ECC2K-130 is already in a normal basis. |
| 493606 | 34 revision (HOLD-T) | defective | yes, deeper | Re-choosing n does not rescue it: the divisor n is a77711's equivariance in disguise, and on the orbit system n cancels, so the Koblitz and pseudorandom arms are predicted equal. |
| 793fd8 | 35 hold (HOLD-U) | defective | yes, conditions tightened | With deterministic index calculus and exponential rho, the restart-portfolio value is <= 0 whenever the IC mean exceeds rho's; release only on floor ratio < 1 and tail index <= 1. |
| 6237e5 | 36 hold (HOLD-V) | sound_with_corrections | yes | Misses an exact correlation: in a normal basis Tr(x) = HW(x) mod 2 carries the E -> E/2E quotient; the uniform control must be drawn from the prime-order subgroup. |

Twenty-five of 26 reviews agree with the recorded hold; the one disagreement
(29b1c5) is a false lemma whose correction exposes a live object on the
composite-degree ANSI rows, not on ECC2K-130. Three reviews confirm a hold
but say its stated reason is wrong (845a77, 793fd8, 1b16d7). None of the 26
is an attack on ECC2K-130; every one is either a structural certificate, a
cost-table column, a constant-factor lever, or a proposal on the composite
curves. That is consistent with what the ranking already said and is now
backed by re-derived arithmetic (each lane summary lists its checks).

Two facts about the environment surfaced by the reviews and worth acting on
before any of the concrete experiments is designed: `numpy` is not installed
in this container although every module of
`experiments/EXP-CERTBIN-e94b27/impl/` except two imports it, and no SAT or
Groebner binary (WDSat, CaDiCaL, msolve, M2, Singular, Sage, Magma) is
installed. Every concrete experiment in `reviews/` declares what it is missing.

## 4. The 13 new proposals

All are `proposed`, unapproved, `novelty_status: unverified` (no lane ran a
web search; corpus greps were run and `discriminated_from` is filled). Each
`minimal_test` names a concrete cell, instrument, metrics, controls, outcome
table and falsification threshold.

| id | question | class | claim in one line | target m and product-law position | test first? |
| --- | --- | --- | --- | --- | --- |
| IDEA-20260926-4b65e3 | CERTBIN | mechanism | With the per-target cap mu <= 1 and B re-optimised, the ECC2K-130 oracle budgets are about 2^11, 2^33, 2^37, 2^42, 2^50 at m = 4, 5, 6, 8, 16; the lever is the (1/2 - 1/m) line. | every m >= 4; a correction to the column every other record prices against | G1's first: zero-run Python recomputation, seconds |
| IDEA-20260926-136bd3 | BINSTD | control | Exact sum-compatible filters on E(F_{2^131}) carry exactly 2 bits (the cofactor, by Theorem C on the order-4l group); an ideal 16-list tree over an orbit-union base would sit 13 bits below rho and needs a 2^25.8-alphabet filter; approximate Koblitz-specific filter capacity is measurable on toys. | k = m = 16; the lane's only exponent-relevant LEAD branch | second in G1 |
| IDEA-20260926-178821 | BINSTD | mechanism | Over the 524 signed Frobenius conjugates of P and Q, one arity-23 decomposition solves ECC2K-130 with zero relations; rho is exactly its generic oracle; the sumset redundancy fixes the true arity. | m about 23; budget is the whole of rho | no |
| IDEA-20260926-1db0e8 | BINSTD | control | Large primes on subspace bases move arity into the large-base oracle: single-large-prime is a birthday search (2^59 sqrt(B) time, 2^58 sqrt(B) memory), the GTTD double-large-prime form costs 2^124 C_2(B')/B'; one reopening condition is measurable. | m = 13 (j = 1) and m = 8 (j = 2); rows cost >= 2^63 and 2^124 | no (closes HOLD-Q's route) |
| IDEA-20260926-89886c | CERTBIN | algorithm | The sat/unsat asymmetry law at m = 3: a sound early-abort mutant-closure filter (W_3 then W_4) on the chained S_3 descent at n = 17, l = 6, priced as ops-to-first-1 on unsatisfiable attempts against ops-to-fixpoint on satisfiable ones and the 2^{(m-1)l} enumeration oracle. | m = 3, a building block for the m >= 4 rows; does not move the m <= 3 closure | G2's first: W_3 rung on the existing closure.py |
| IDEA-20260926-917981 | CERTBIN | control | Closure outcomes (M_D, W_D) are invariant under change of field basis and V-basis, so normal-vs-polynomial descent is a change of coordinates, not a confound; squaring transfers a W_D certificate across a Frobenius orbit on a stable V. | any m; removes a confound from every closure cost law | alongside 89886c, about 1 CPU-h |
| IDEA-20260926-a79052 | CERTBIN | representation | On Koblitz siblings x is an abscissa iff Tr(x) = Tr(1/x) + Tr(a), so restricting V to that set removes every unsatisfiable-by-non-membership attempt for free; measured as a refutation-share against the ordinary RC-1 curve. | m = 2 attempt mix, free at any m; honest prior is null | no |
| IDEA-20260926-ae8f0a | CERTBIN | mechanism | The E -> E/2E -> E/4E chain of the cyclic Z/4 2-Sylow as a two-bit leg label on legs (trivial on prime-order targets by Lagrange), giving four sum-to-target parity cells; HOLD-O made constructive. | at most a 2-bit attempt-mix constant | no |
| IDEA-20260926-b6cc43 | CERTBIN | representation | The Hamming ball B_w in Bailey et al.'s type-2 normal basis is a Frobenius-stable factor base at n = 131 with no shift variables (weight is rotation-invariant); the distinguished-point predicate is B_34; priced by cardinality-constrained descent on the RC-1 cell against a subspace, a random set and the ordinary curve. | m = 4, w = 6, |F| about 2^32.7 | G3's first: minutes on installed pure-Python instruments |
| IDEA-20260926-b48c9d | BINSTD | mechanism | The tau-adic factor base over an orbit-union base is a Gamma-orbit quotient, not a factor base: free-oracle attempts 2^131/(C(131,w) 2^w) reach rho only at w >= 13, and the enumerated form is a generic 2^{131 - l'/2} >= 2^66 walk. | closure predicted at every w | no |
| IDEA-20260926-cafcf1 | BINSTD | control | Abscissa density of a subspace base is Weil-uncontrolled for l <= n/2 + 1 (every l <= 66 at n = 131); Tr(x) = Tr(1/x) reads b = 1 and a; yield ceiling 2^m; corrects the stated Weil support of 1a081a HB1-2. | any m; a factor <= 2^m in yield | no (exact counting, no solver) |

Two ids were returned unused (`IDEA-20260926-d128eb`: lane G3 found its last
two objects already filed the same day by G2 as `ae8f0a` and `917981`;
`IDEA-20260926-d1f6bf`, `-ef2bd8` were spares never assigned). A returned id
is free again for `allocate_id.py`.

## 5. Concrete experiment examples, ranked by cost

These are the cheapest discriminating tests the round produced, each fully
specified in the record named. All reuse the two supported CERTBIN cells
(RC-1: n = 17, f = t^17 + t^3 + 1, A = 97044, B = 126251, m = 2, l = 9,
x(2E) targets; and n = 19, f = t^19 + t^5 + t^2 + t + 1, A = 46693,
B = 306147, h = 2) or a Koblitz sibling of the same n, with the ordinary
curve as the control. Order-of-magnitude costs are the lanes' estimates, not
measurements.

1. **Zero-run recomputation of the arity table** (`IDEA-20260926-4b65e3`
   Stage 0): reproduce `KN-FIND-aa2efc`'s floors 2^89.25 / 68.58 / 56.40 /
   48.44 from `min over l of m! 2^(131-(m-1)l) + m 2^(2l)`, then enforce
   mu <= 1 and emit the corrected budget column. Seconds. Either result
   changes what every m >= 4 record is priced against.
2. **Lemma A2 soundness check** (review of `2a3771`, also serving `7ab503`
   and `493606`): at n = 17 on y^2 + xy = x^3 + x^2 + 1 (#E = 2 * 65587),
   V = ker g(tau) of dimension 8, m = 2, enumerate all 2^16 pairs and test
   closure of the solution set under coordinate squaring and its overlap
   with the solution set for sigma(R). Prediction from a77711: 0 and 0.
   Seconds, gf2n.py and curve.py plus about 100 lines.
3. **Parity census** (review of `1b16d7`): exhaustive m = 2 and m = 3
   decomposition census at RC-1 (Tr(A) = 0) and the n = 19 cell (Tr(A) = 1)
   over V = {deg < l}, its halves {c_0 = 0} and {c_0 = 1}, and a
   size-matched random subspace; aligned/random yield ratio predicted 2 at
   every m. Minutes.
4. **E/4E class census** (reviews of `153a90` and `e3048d`,
   `IDEA-20260926-ae8f0a`): on Koblitz n = 19 (#E = 4 * 130873), halving-bit
   histogram, class-sum certificate, class-restricted vs parity-aligned yield
   predicted 2^{1-m}, with a relabelled Z/(4l) replica as the generic-group
   control and the h = 2 sibling as the no-Z/4 control. Minutes.
5. **Hamming-ball factor base** (`IDEA-20260926-b6cc43` Stage 1): RC-1 with
   the ball arm B_w replacing the subspace V and nothing else changed;
   outcome bands fixed before the run: closure-work ratio in [0.5, 2] with
   equal refutation rate, or above 2 with lower refutation. Minutes on
   pure Python; an optional native-cardinality SAT arm needs WDSat.
6. **Early-abort W_3 rung** (`IDEA-20260926-89886c`): chained S_3 descent at
   n = 17, l = 6 (M_3 629 x 7176, M_4 11339 x 59536), ops-to-first-1 on
   unsatisfiable attempts against ops-to-fixpoint on satisfiable ones, miss
   rate and crossover l*. Tens of CPU-hours at the W_4 rung, seconds per
   attempt at W_3.
7. **Filter-capacity ladder** (`IDEA-20260926-136bd3` Stage 1): exact
   controls Tr(x) (capacity 2) and E/4E (capacity 4) on the n = 19 Koblitz
   cell, then approximate Koblitz-specific filters measured against the
   relabelled Z/NZ control. The only exponent-relevant LEAD branch in the
   round; low compute.
8. **Two-list MITM as a ground-truth oracle** (review of `845a77`): at the
   n = 19 cell, m = 3, l = 6, |V| = 64, against exhaustive enumeration and a
   relabelled Z/NZ control; predicted identical operation counts. Minutes.
   Tooling, not an attack.

Every item needs `numpy` installed (or the sixty scalar lines lifted out of
`gf2n.py` and `curve.py`); items 5 and 6 note the missing SAT engines for
their optional arms.

## 6. What this round did not do, and what is next

- It approved nothing and designed nothing. Under `DEC-20260924-4f8a03` R2
  and CLAUDE.md rule 11 the next `/coordinate` selection point on
  `GOAL-ECDLP2M-001` ranks the 13 new proposals with the 26 reviewed ones.
  The reviews are advisory input to `DEC-20260924-99ce20` NA-3 (the revision
  batch for the six return_for_revision items: the reviews say exactly what
  each revision must contain), NA-4 (the reading tasks for HOLD-H and
  HOLD-L) and NA-7 (re-ranking HOLD-A to HOLD-G).
- Two review findings should reach the next selection as candidate
  corrections, never as edits: 29b1c5's false lemma (HOLD-E is currently
  "queued_for_design"), and the corrected reasons behind HOLD-P and HOLD-U.
- The product-law finding `KN-FIND-aa2efc` has now been re-derived by four
  independent sessions: one reproduces its table exactly, two reproduce its
  ordering and verdict with a different balance, and one proposal
  (`4b65e3`) argues its budget column is too pessimistic at m >= 5. It
  remains unreviewed in this program and every ECC2K-130 arity claim rests
  on it; a validator pass on that finding is the cheapest high-leverage act
  available.
- Novelty of all 13 proposals is `unverified`. No web search ran; every
  external reference is `recalled`. A literature pass (Wagner's k-tree on
  groups with a small quotient; low-weight normal-basis factor bases; GTTD
  on binary curves) is the next honest step before any is ranked as
  `speculative` or better.
- Installing `numpy` in the research container is a prerequisite for every
  concrete experiment above; it is an environment fix, not research.

## 7. What `main` gained while this round ran (merged in before the PR)

Seventeen commits landed on `main` during the round; none touches a path
this branch writes. Three bear on it:

- **PR #1452, a meet-in-the-middle decomposition engine** under
  `src/crypto_autoresearcher/index_calculus/` (`decompose.py`, `tails.py`,
  `--engine mitm`). It is over PRIME fields `E(F_p)` and counts cost in
  `S_3` solves, but it is exactly the two-list, table-of-tails construction
  the review of `IDEA-20260922-845a77` prices for the binary case and names
  as a tooling seam; the binary port is now a port of an existing engine, not
  a new instrument. The review's verdict (dominated on ECC2K-130 by the
  product law) is unchanged.
- **The ECDLP known-results map** `knowledge/frontiers/ecdlp/` (one claim
  per `KR-*` row, with `forecloses` phrases) and
  `tools/build_frontier_map.py --match "<idea text>"`. This is the novelty
  screen the 13 new proposals should be run through before any is ranked
  above `unverified`; it did not exist when the generator lanes ran.
- **A `prior_art` block on idea records**, validated by
  `tools/validate_ledger.py` and REQUIRED for ideas minted from
  `IDEA-20261001` on. The 13 records here predate the cutover, so the block
  is optional for them; a later superseding record that carries the
  frontier-map comparison is the right place for it.
