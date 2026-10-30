# ECDLP retrospective leads: ledger filing (2026-10-09 retrospective)

Five research leads of the program's 2026-10-09 ECDLP retrospective, filed as
schema-complete proposal records, plus a sixth short note on the validation
backlog. Filed by an Idea Generator session; no hypothesis, experiment, goal or
decision status is changed, nothing is approved, no trial is run, and no
existing record is edited.

## Provenance and limits of this filing

- **Stale base.** The ledger base is main at `85e1d32b7` (committed 2026-10-10).
  The filing happened on 2026-10-26, about 15 days later. GitHub access was
  unavailable (raw git returned 403, the API returned 404 for the private
  repositories), so `origin/main` could not be fetched or merged, and
  AGENTS.md's "merge main before generating" is **not satisfied**. Records
  merged since 2026-10-10 are invisible to the novelty checks below. The
  Coordinator should re-run `tools/build_ledger_index.py` and
  `build_frontier_map.py --match` on current main before designing from any of
  these ideas.
- **Frontier map.** Rendered from the checkout at `85e1d32b7` (areas
  `index-calculus` and `generic-rho`, 25 and 26 rows); `--match` run on every
  idea after drafting, every top hit cited in its `rows_checked`.
- **Retrospective numbers.** The retrospective itself is in neither repository.
  Its measured numbers reach the records as the program's earlier reports
  relayed in the filing brief, provenance `internal`, **reported and not
  replayed**. Each notes file carries a fact-check table separating what was
  found in a committed artifact (crypto repo at `bbd330a9d`, 2026-10-11, the
  local `origin/main`) from what was not located.
- **Implementation branches (crypto repo) are local only.** As of filing, three
  exist in the local crypto repository (`phase-aware` with one protocol-only
  commit; `conductor-gap` and `solver-total` at `bbd330a9d` with no commits of
  their own); `orbit-aware`, `transfer-audit` and `validation-backlog` are not
  present locally. None is known to be on a remote.
- **Bus inbox** for the idea-generator role was read once at the start (two
  unread messages, from `executor-sembin-79a02d` and
  `coordinator-portfolio-20261005`, neither addressed to this work); nothing was
  acknowledged.
- **Not publishable here.** Pushing and opening the pull request are deferred
  until GitHub access returns; the commit is local on
  `claude/retrospective-leads-ledger-20261011`.

## Map: lead, record, question, goal, branch

| # | lead | IDEA | question / goal | crypto-repo branch | state of the branch |
| --- | --- | --- | --- | --- | --- |
| 1 | phase-aware Frobenius summation | `IDEA-20261011-049724` | RQ-FROB-7d8dd4 / GOAL-FROB-6333a9 | `claude/phase-aware-paired-fixed-budget-20261011` | local, one commit `db05afd8b` (protocol only, no code, no runs); on `research/frobenius_quotient_sat_20260930/`; draft PR crypto#1630 unverified |
| 2 | conductor-gap paired relation cost | `IDEA-20261011-07c83f` | RQ-ECTD-001 (+ RQ-VOLC-f6253b) / GOAL-ECTD-001 | `claude/conductor-gap-paired-smoke-20261011` | local at `bbd330a9d`, no commits of its own; protocol of this repo's PR #2041 read from local ref `e7d5ff26e`; #2047, #2038 unverified |
| 3 | orbit-aware double-large-prime graph | `IDEA-20261011-6bdbe2` | RQ-BINSTD-b6f698 / GOAL-ECDLP2M-001 | `claude/orbit-aware-double-large-prime-20261011` | not present locally; targets `large_prime_filter.rs`, `ecbench_large_prime.rs` (read at `bbd330a9d`) |
| 4 | solver selection by total relation cost | `IDEA-20261011-dcfc4d` | RQ-ICPERF-94c86e / GOAL-ICPERF-e6b6a4 | `claude/solver-total-relation-cost-20261011` | local at `bbd330a9d`, no commits of its own |
| 5 | Jacobian and Weil-descent transfer audit | `IDEA-20261011-fb7b7e` | RQ-BINSTD-b6f698 (+ RQ-ECDLP-002) / GOAL-ECDLP2M-001 | `claude/transfer-audit-automation-20261011` | not present locally; this repo's PR #2054 read from local ref `04282d58a` (31-line spec) |
| 6 | validation backlog (note, no IDEA) | none | none | `claude/validation-backlog-ci-20261011` | not present locally |

Question choices are justified in each record's notes file. In short: lead 1
asks whether Frobenius helps inside the decomposition system, which is
RQ-FROB-7d8dd4's own decision target; lead 2 is GOAL-ECTD-001's priority (2),
"large-conductor vertical barriers", and RQ-ECTD-001 is an ECC area where
RQ-VOLC-f6253b is not (see the registry gap below); leads 3 and 5 sit with the
BINSTD lineage whose scope names the large-prime columns and the GHS/cover
family; lead 4 supplies a column definition for the RQ-ICPERF boundary table.

## What the ledger and the crypto repository already held (read before ranking)

The retrospective's priority order is recorded as given; these findings bear on
it and are the Coordinator's to weigh.

1. **Lead 2 was measured the day after the retrospective.** The crypto repo
   committed a conductor-gap panel on 2026-10-10 and 2026-10-11
   (`research/isogeny_conductor_gap_ic_20261010/`, 38 prime, 5 Koblitz, 3
   random-binary certified pairs; MITM, F4 and rho arms). It reports yield, `S`,
   wall and F4 solving degree unchanged across the gap (floor/crater medians 0.89
   to 1.17). So the lead's primary question has a first, null, answer at toy size
   with MITM and F4. The record is therefore a closing test of what the panel did
   not run (SAT and F5 arms, intermediate levels, the PR #2041 endpoint), with H0
   as the expected outcome. Reported, not replayed.
2. **Lead 3 is partly on the ledger.** The orbit-canonicalised large-prime graph
   is already priced in `IDEA-20260926-1db0e8`, `IDEA-20261001-621974` and the
   approved `H-BINSTD-555991` (dominated by matched rho in the enumeration
   class). The record fills the remaining gap: curve-verified rank with
   lambda^k coefficients against sign-only and no-large-prime arms. It also
   corrects a naive reading: with gains in a group of order 2n only balanced
   cycles cancel their large primes, and the combination space has dimension
   `|E| - |V'| + b` (frame matroid), so the 2n-fold vertex saving is partly
   offset by unbalanced components. See the notes file.
3. **Lead 1 has a protocol waiting.** Another session registered a paired
   fixed-budget protocol on the local `phase-aware` branch. The record follows its
   design (ABBA order, fixed per-attempt budget, every attempt charged) and adds
   the ladder warning: m = 51 in the retrospective's ladder is
   composite (3 x 17), so a 51-bit cell has subfields and is not comparable to
   53, 83 and 131; the ladder is requirement-only.
4. **Lead 4's per-relation figure is undefined on natural targets.** The m = 83
   matrix found zero natural relations, so total cost per relation exists only for
   planted controls; natural targets support per-attempt cost and a yield bound.
5. **Lead 5 is audit tooling, not a mechanism.** A transfer is injective on the
   order-r subgroup, hence a change of coordinates (IDEA-20260806-c5d183); its
   scope is supplied or self-generated toy curves.
6. **Registry gap (not edited).** `tools/ecc_priority.py` classifies
   RQ-VOLC-f6253b and the other questions of GOAL-ENDO-001 as non-ECC although
   ENDO and ECTD are declared ECC areas. Ideas classify through `question_id`.
   `orchestration/research-priority.yaml` is the single place to change it; this
   filing did not.

## ECC-priority rationale

All five records are ECC records under `orchestration/research-priority.yaml`,
checked with `tools/ecc_priority.py --open-ideas`: `IDEA-20261011-049724` [FROB],
`-6bdbe2` [BINSTD], `-fb7b7e` [BINSTD], `-07c83f` [ECTD] and `-dcfc4d` [ICPERF]
all list as open ECC ideas. Per AGENTS.md they are ranked work, not shelved:
`/design-experiment` applies once an idea can be approved, which needs capacity
under `APPROVAL_CAPACITY_CAP` and a runnable contract
(`tools/newest_experiments.py --experiment`). Neither was checked here; that is
the Coordinator's step. Priority fields are the generator's reading, not a rank:
lead 1 `high` (cheap, decisive, protocol ready), the rest `medium`, lead 2
lowered from the retrospective's reading by the panel finding above.

## Sixth note (not a proposal): validation backlog

Branch name given: `claude/validation-backlog-ci-20261011` (not present locally).
No IDEA record is filed: these are repair and replay tasks, and by AGENTS.md
rule 5 a red workflow or timeout is an infrastructure signal, never evidence
against a mathematical hypothesis. What the backlog gates is the promotion of
claims that rest on those workflows. CI outcomes cannot be read from here, so
red/green statements below are the retrospective's, not checked.

| item | retrospective statement | checked locally (crypto `bbd330a9d`) |
| --- | --- | --- |
| Koblitz stage audits | runner starvation, fix in crypto#1624 | `7ab28103d` merged `fix/ci-runner-unjam-20261010` on 2026-10-10 (`3f1424f87` "Stop historical Koblitz stage workflows from starving hosted runners"); at least twenty `koblitz-stage*.yml` workflows exist; whether the audits are now green is unverified |
| point-decomposition validation | `ecc2k130-pdp-difficulty-outcome` replay red on main since #1116 | #1116 merged 2026-10-08 (`e196b82f5`); the workflow file exists; red state unverified |
| Boolean F5 correctness | `boolean-f5-graded-batch` red on pushes | workflow file exists (also `f5-echelon.yml` and four sibling `boolean-f5-*.yml`); red state unverified |
| e2e benchmark replays | `ic-e2e-benchmark` green | workflow file exists; green state unverified |

Consequence worth carrying: the F5 reuse, graded-caching and sibling-pivot
ideas that the retrospective says lack validated improvement stay unvalidated
until the F5 correctness workflow is read green on a pushed commit; the
`IDEA-20261011-dcfc4d` record prices them inside total cost and does not wait on
them. Next action for whoever owns CI: read the four workflows' latest runs on
main and attach the run ids to this note by a new record.

## Files

- `ledger/proposals/IDEA-20261011-{049724,07c83f,6bdbe2,dcfc4d,fb7b7e}.yaml`
  (each under 8 KiB) and their `.notes.md` sidecars (derivations, fact-check
  tables, near-duplicate comparison, frontier-map hits).
- This README.
