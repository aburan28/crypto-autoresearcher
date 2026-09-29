# Ideation report — TASK-20260915-5ba08b

- Goal / question: GOAL-ICPERF-e6b6a4 / RQ-ICPERF-94c86e (measured cost boundary
  for index calculus on Koblitz, binary and small-extension prime-field curves).
- Role: idea-generator, policy `research-deep`, `maximum_runs: 0` (no solver was
  launched; every number below is proposal-time arithmetic or an UNREVIEWED
  observation from RUN-ICPERF-305ca3 and is cited as such).
- Deliverables: 7 IDEA records in `ledger/proposals/IDEA-20260915-*.yaml`, all
  parse and pass `tools/validate_ledger.py` with zero new errors; this report.
- Nothing committed (task constraint); no hypothesis, contract, decision or
  status change written.

## Ranked list (one line each)

Kind: (a) INSTRUMENT changes what the table measures; (b) MECHANISM moves a
measured phase cost by a stated factor. `dominated_by` verdicts are Pareto
across time/memory/data after reading the frontier rows named in each record.

| rank | id | kind | claim (one line) | novelty_status | dominated_by verdict | priority |
|---|---|---|---|---|---|---|
| 1 | IDEA-20260915-3f1964 | (a) | Exhaustive side-classified V^3 table per cell: every F_q-root of the descended S_4 system is all-E or all-twist, so one 2^{3l}/6 enumeration certifies U, classifies every solver answer (E / twist / spurious) and replaces the generator's "random x_R" label; would have classified the five n19l6-19-U answers as E / twist / spurious instead of counting them as a bare P1 failure. | adaptation | n/a (no cost result claimed); frontier rows read | high |
| 2 | IDEA-20260915-0d8e90 | (b) | WDSat UNSAT conflicts = c·2^{ml}, c∈[0.9,1.0] (exhaustive core), so the S_4 relation phase costs 3c·2^{n+l} conflicts — exponent 1 in n vs rho's 1/2 — and the measured slope in n, not per-instance wall time, is the boundary quantity. | adaptation | n/a as a result; the law itself places the SAT row under rho and exhaustive search at every n ≥ 8 | high |
| 3 | IDEA-20260915-7ef636 | (a) | 2×2 + planted-core null: a structure-preserving relabelling randomises branching order at fixed algebra, a random system with a propagating ml-variable core fixes the order at random algebra; separates the ≥50× order effect from the 20–114× structure effect observed in RUN-ICPERF-305ca3. | unverified | n/a (control, no cost result) | high |
| 4 | IDEA-20260915-3476de | (a) | Make the Groebner column measurable: RSS watchdog replacing RLIMIT_AS, BRiAl/PolyBoRi over GF(2) beside M2/Singular, and a hardware-independent unit (d_solv × Macaulay dimensions); would have turned 36 abort/timeout rows into numbers or a measured memory obstruction. | unverified | n/a (no cost result); alternatives for a Groebner number compared | high |
| 5 | IDEA-20260915-eee7e4 | (b) | Side-constrained core: adding x_i ∈ x(E) to each of the m blocks shrinks the leaf count |V|^m → |V∩x(E)|^m ≈ 2^{m(l-1)}, predicting 2^m = 8× fewer UNSAT conflicts and removal of every twist root from the S column. | unverified | rho with negation, 0.886·2^{n/2}; the SAT row stays dominated at every n ≥ 8 | high |
| 6 | IDEA-20260915-3119c9 | (b) | Yield by counting: Λ(V) = C(F1+2,3) + F1·C(F0+1,2) predicts decompositions per G-target from (F1,F0,r); class-aligned affine slices set F0 = 0 and best-of-K enrichment adds (1+√(2lnK)/2^{l/2})^3 — 4–8× on relation search at l = 6, capped at 8×; would have predicted the 3.7× yield gap between (17,6) and (19,6) at the same l. | unverified (recalled Gumbel citation) | rho with negation; constant on a dominated row | high |
| 7 | IDEA-20260915-8fe0ef | (b) | Frobenius-invariant factor bases on Koblitz cells: τ-stable V are ker g(τ), g \| x^n−1, so a lane exists iff ord_n(2) < n−1 (n = 17: l = 8, m = 2; n = 19 and K-163: none; K-233/283/409/571: one balanced lane each); every linear stable V not containing F_2 sits in ker Tr and is parity-confined → even m forced at Tr(a) = 1; N_rel and U fall by n, LA by n^2, per-instance PDP unchanged, and the matched rho baseline falls by √(2n), so the IC/rho gap closes by √(n/2) only; the current row's rho baseline is 5.5–6.2× too generous to index calculus because the Trimoska curve [1,1,0,0,1] IS Koblitz. | unverified (2020/1315 full text unopened; FIPS/GLV recalled) | rho on ⟨τ,−1⟩ classes √(πr/(4n)); as a mechanism, GGMP 2020/1315 already claims the factors n and n^2 | medium |

## Ranking rationale (information gain vs cost)

The four ideas ranked first are the ones whose outcome changes how every later
row is read, and each is cheap. 3f1964 costs one enumeration per cell
(≤ 2^24/6 additions at l ≤ 8) and converts the P1 "failure" into a classified
answer while certifying every U label — without it every S/U count in the table
is a count of generator labels, not of decompositions. 0d8e90 costs nothing
beyond fitting the existing conflict counts plus three larger cells, and turns
the P2/P3 comparisons into a one-constant law whose slope in n is the actual
boundary quantity. 7ef636 and 3476de are the two attribution repairs the run
exposed: without the relabelling control, the order/structure split is one
number carrying two mechanisms; without a Groebner engine that finishes, P2
asserts nothing. The three mechanism ideas are ranked below the instruments
because each predicts a constant factor on a row that is exponentially
dominated by rho (verdicts above), and because two of them (eee7e4, 3119c9)
depend on the exhaustive table of 3f1964 to be scored at all. 8fe0ef is ranked
last on priority — its mechanism factors are already published (GGMP) and the
one shipped cell where a lane exists is n = 17 only — but it carries the one
correction that applies to every existing Koblitz row (the √(2n) baseline) and
the one structural constraint no corpus record states (linear Frobenius lanes
are parity-confined; even m or the affine slice 1 + ker g(τ) is required).

## Test first: IDEA-20260915-3f1964

It is the cheapest valid discriminator in the set: one exhaustive enumeration
per shipped cell, no solver, no new engine, and it decides three things at
once — whether n19l6-19-U is a twist decomposition (Coordinator prior) or a
genuine spurious answer (P1 really failed), how many of the 30 "U" labels are
actually UNSAT (the Coordinator's "random target" reading predicts a nonzero
SAT fraction; a certified generator predicts zero), and the ground-truth yield
that 0d8e90, eee7e4 and 3119c9 all divide by. Its known-false control (a
target with a planted E-triple must appear in the table) and its null (a
non-E x_R must have zero all-E preimages) are both free.

## Honest accounting (docs/inventor-protocol.md §5)

- Objects considered (tracked object → operation set):
  the pass/fail solver verdict → (E / twist / spurious) class of a root under
  the descended S_4 map (3f1964); the DPLL leaf count as a function of block
  sizes under the core-first branching order (0d8e90, 7ef636, eee7e4); the
  (side bit, class bit) pair of a factor-base x under m-fold addition (3119c9);
  the ⟨τ,−1⟩-orbit of a factor-base point with its class bit under {add, τ,
  negate} (8fe0ef); the Groebner run as (d_solv, Macaulay dimensions) rather
  than as wall time under a hard address-space cap (3476de). The
  lossy-projection test was run in each record; the class bit and the orbit
  each pass, and their interaction (8fe0ef S2) is the only genuinely new
  object this session found.
- `dominated_by`: per record above; every cost-claiming record is dominated on
  time by rho (negation-only or ⟨τ,−1⟩) and on memory by rho's O(w) at every
  shipped n; the frontier rows read were rho (both constants), exhaustive
  group search 2^n, the exhaustive V^m table, and the SAT law 3c·2^{n+l}.
  `null` was set nowhere.
- `sota_delta`: no exponent moved anywhere. Constants: eee7e4 predicts 8× on
  UNSAT PDP cost; 3119c9 predicts 4–8× on relation search at l = 6, capped at
  8×; 8fe0ef predicts n on relation collection and n^2 on LA (GGMP's published
  factors, delta zero against them) and a √(2n) correction to the baseline
  (5.5–6.2× at the shipped n). Instruments: 3f1964 certifies 100% of U labels
  and classifies 100% of answers; 0d8e90 replaces per-instance times with a
  one-constant law; 7ef636 splits one conflict ratio into two attributed ones;
  3476de moves 36 Groebner cells from `none` to a number or a measured
  obstruction.
- Closures with mechanism: none claimed. One proposal-time negative that is a
  theorem given H-SEMBIN-83a856, not a closure — a linear τ-stable factor base
  inside ker Tr on a Tr(a) = 1 Koblitz curve yields exactly zero G-target
  decompositions for odd m (8fe0ef S2); it is recorded as a constraint with
  the affine slice 1 + ker g(τ) as the way around it, and it is the KNOWN-FALSE
  control of that record's minimal test.
- Open directions for the next session: (O1) a closed-form x-criterion for
  4E-membership on cofactor-4 Koblitz curves (a = 0), without which no a = 0
  lane row can be written as "unconfined"; (O2) opening the full text of
  eprint 2020/1315 (`downloads/2020-1315.pdf` per KN-LIT-796) to settle whether
  the parity constraint on Frobenius-invariant factor bases is already stated
  there; (O3) the prime-field F_{p^3}/F_{p^5} Gaudry–Diem arm named in the
  handoff — NOT generated this session (the 7-record maximum was reached by
  the binary-field portfolio) and still the only way to fill the prime-field
  row, which remains entirely unmeasured; (O4) an m = 4 version of the Λ(V)
  count (3119c9 states the m = 3 case only); (O5) H1 of 8fe0ef needs n with
  many Φ_n divisors (n = 31, 73) to be a distributional test at all.

## Fields that could not be filled, stated honestly

- `novelty_status` is `unverified` on 3119c9, 8fe0ef, 7ef636, 3476de and
  eee7e4. On 3119c9 and 8fe0ef the corpus reads would support `adaptation`,
  but each carries a `recalled` citation (Gumbel law; FIPS 186-4 a-values and
  GLV 2000) and the validator requires `unverified` until every recalled
  source is opened; the records say so in `novelty_screen.status_note`.
- 8fe0ef's FIPS lane table depends on the recalled a-values (K-163: a = 1;
  others a = 0); the record instructs that the standard be read before any of
  those rows is written, and none of them is claimed as a result.
- 8fe0ef's `what_is_new` item (1) is claimed relative to the corpus only; its
  status relative to the full text of GGMP 2020/1315 is unknown.
- No `proof_search_map` audit was run against compute (budget 0 runs); each
  record's `baseline_embedding.reproduction_check` names what the executor
  must recompute first.
- `estimated_cost.wall_clock_seconds` values are advisory per CLAUDE.md
  research-budget policy and were not measured.
- The Gaudry–Diem prime-field arm (kind b, requested in the handoff) was not
  produced; see O3.

## Two pre-existing files were patched before validation

`IDEA-20260915-3476de.yaml` and `IDEA-20260915-7ef636.yaml` (both untracked,
written earlier in this same task) each had one `internal` citation with
`verified_by: null`; both now name this task as the reader of the corpus record
and state that the underlying paper was not opened. `IDEA-20260915-3119c9.yaml`
and `IDEA-20260915-8fe0ef.yaml` were downgraded from `adaptation` to
`unverified` for the reason above. No committed record was touched.
