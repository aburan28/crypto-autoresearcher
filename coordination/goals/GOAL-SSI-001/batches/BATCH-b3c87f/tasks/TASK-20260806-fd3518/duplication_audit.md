# Duplication audit — TASK-20260806-fd3518

Deliverable Zero for BATCH-b3c87f. Written **before** any proposal in this task
was drafted. No claim of novelty anywhere in this task may be read except
against this file.

Author: idea-generator (this session). Date: 2026-08-06.

---

## 1. The glob executed, and the file count it returned

Tool: the harness `Glob` tool (no shell is available in this session — see §5).

```
pattern: ledger/proposals/*.yaml
```

**Result: 257 matching files.** (The tool listed the first 100 and reported
`Showing 100 of 257 matching files; 157 more are not listed.`)

Two further globs were executed to scope the audit:

```
pattern: ledger/goals/GOAL-SSI-001/**          -> 34 files (goal.yaml + 33 checkpoints)
pattern: ledger/proposals/IDEA-20260806-*.yaml -> 0 files  (no IDEA minted on this date yet)
```

A structured field extraction over `ledger/proposals/IDEA-20260805-*.yaml` was
run with `Grep` on `^  (id|question_id|goal_id|title|class):` to establish which
of the 2026-08-05 cohort belong to RQ-SSI-001 / RQ-SSIQ-9702af and which belong
to adjacent questions (RQ-WESO-8aff57, RQ-SQISIGN-*). That extraction is what
produced §3 below.

## 2. The 19 committed proposals, one line each

Every file below was opened in this session. For the long records
(`IDEA-20260803-48e258`, `-82b2b7`; `IDEA-20260804-170692`, `-4c9ac0`, `-84328c`;
the six `IDEA-20260805-*`) the head of the record through `mechanism` /
`object_first_candidate` was read; `IDEA-20260805-062bee` was read in full as the
schema template. Where only the head was read, the line below states what the
record covers on the evidence of its `title`, `claim`, `class` and
`tracked_object` fields, and nothing more.

| # | ID | class | What it already covers (tracked object / deliverable) |
|---|---|---|---|
| 1 | `IDEA-20260725-001` | cost-model | Full-cost re-baselining of classical supersingular path-finding: MITM vs low-memory collision search vs Delfs–Galbraith under Wiener accounting; emits one matched-baseline recommendation. `disposition: confirmed_baseline_cost_model_closed`. No tracked object; no exponent claim. |
| 2 | `IDEA-20260725-002` | structure-attack | Effective orientation from a *public* small-degree endomorphism `alpha` on `E0`: treat `Z[alpha]` as an orientation, recover a connecting ideal by charged Cl-vectorization, compare to KN-TECH-050. `disposition: confirmed_scoped_residual_closed`. |
| 3 | `IDEA-20260725-003` | structure-attack | Frozen SQIsign Fiat–Shamir transcript model `SQI-FS-T0` tested against KN-TECH-026 / KN-LIT-077 Kani/Petit necessary conditions; expected fail-closed classification. `disposition: confirmed_negative_classification_closed`. |
| 4 | `IDEA-20260729-001` | control | `CSIDH-COLLIMATION-FC0`: a zero-curve-compute typed resource-vector gate for Peikert's binary collimation sieve (queries, QRACM, schedule, Clifford+T, error composition). The 33-batch FC0 lane. |
| 5 | `IDEA-20260801-007` | control | CSIDH class-group action **dimension test**: measure the effective vOW distinguished-point collision surface of the group action on toy class groups against the birthday surface. |
| 6 | `IDEA-20260803-48e258` | cost-model | The **crossover curve `p*(w)`**: the prime size at which the corrected `p^{1/3+o(1)}` cost overtakes the matched Delfs–Galbraith / vOW middle-memory baseline, as a function of available memory `w`, with a band from the committed `c` bracket and 18 measured-gamma readings and L4-BATCH as a two-valued scenario. Zero compute. |
| 7 | `IDEA-20260803-82b2b7` | barrier | Trace-collision test for `QM-STOPPING`: search for two FC0 executions with equal observable trace and different stopping behaviour, to decide whether a stopping time `tau` is definable on the FC0 trace algebra at all. Terminates the FC0 lane either way. |
| 8 | `IDEA-20260804-170692` | mechanism | **Local transport signatures**: the tuple of bounded-radius local `l`-adic neighbour-tree quotient states induced by a partial path, reduced mod local stabilisers; tests signature-match enrichment of endpoint collisions against a shape-matched local-action null. Prospective `p^{1/6+o(1)}` only if a lifting theorem is found. |
| 9 | `IDEA-20260804-4c9ac0` | measurement | **Kernel-Frobenius type profiles**: the sequence of Frobenius conjugacy types on internally generated cyclic kernel lines along a fixed prime schedule, as a path-half compatibility prefilter, against a shape-matched null. |
| 10 | `IDEA-20260804-84328c` | representation | **Frobenius-orbit quotient** `[E] = {E, E^{(p)}}` as the collision key for a two-stage path-collision procedure; pre-registered fiber bound plus exact-lift check; prospective `p^{1/6+o(1)}`. |
| 11 | `IDEA-20260805-062bee` | mechanism | **`delta(E)` = minimal degree of `E -> E^{(p)}`** and the covering law `Pr[delta <= D] ~ c D^beta p^{-gamma}`, with the forced identity `exponent = gamma/beta`, a matched null (uniformly random target) forced to exponent 1/2, an exact `4^k` Lipschitz envelope, and a three-way pre-registered fork mapping to exponents 1, 1/3, 1/4. |
| 12 | `IDEA-20260805-93ee20` | control | The **disposition-null**: run this goal's own obligation-ledger protocol on a structure-free null target whose correct verdict (`COMPLETE`) is derivable in advance, to decide whether ~20 `advances-X-without-clearing-QUERY_MEMORY` tokens measure the object or the protocol. Tracked object is the disposition token. |
| 13 | `IDEA-20260805-bc8246` | cost-model | The **cost functional** `M: (A,T,n) -> R` as the tracked object: time-only, `A*T^2` and `A*T` applied to the paper's single published tradeoff curve give three different winners; `AT^2` is exactly `w`-invariant along `T = p^{1/2}/w^{1/2}`. Deliverable is a pinned charging register plus a prediction that `p*(w)` is `w`-independent under `AT^2`. |
| 14 | `IDEA-20260805-d66193` | control | **Input-encoding quantifier adjudication** between the frozen `p^{1/3+o(1)}` result and a reported (abstract-only, unverified) 2026 poly-time `End(E)` basis claim; two exhaustive branches (hidden given in the input, or a total break needing rule-12 review). |
| 15 | `IDEA-20260805-250e50` | theory (SSIQ) | The **screen-threshold cost identity** `E(theta,s,gamma) = (1/2 - 3theta/2)_+ + max(gamma, theta - s)`: tracked object is the admitted degree threshold `theta = log_p T` and its conjugate, screen selectivity `s`. Reproduces 1/3 at the incumbent, returns 1/5 under a free exact `delta_E` screen, break-even at `gamma = 1/3`. **Time only; the identity has no memory variable.** |
| 16 | `IDEA-20260805-2d2c41` | control (SSIQ) | **Smoothness conditioning audit**: `delta_E` tracked as a *value of a ternary quadratic form* (factorisation type and local conditions), not as a size; plus a derivation bounding Remark 1's multiplicity to `O(B^{3/2}) = p^{o(1)}` at the operating scale. |
| 17 | `IDEA-20260805-c60813` | mechanism (SSIQ) | **The relation** (index calculus transported to the Deuring side) as tracked object, with a three-pronged one-page kill: groupoid not group, trivial two-sided class group, Hecke module of dimension `~p/12`. |
| 18 | `IDEA-20260805-de1490` | control (SSIQ) | **The estimator** as tracked object: `gamma_random` is forced to exactly 1/2 by an expander hitting-time theorem and the committed run returned 0.4014; installs the forced-value anchor and derives the null trapped fraction the campaign's 0.5 threshold was never calibrated against. |
| 19 | `IDEA-20260805-e7ee4a` | theory (SSIQ) | The **pair `(rank, log_p det)` of the Hom-lattice** as target varies, with the trace-vanishing selection rule forcing rank 3 below degree `p/4`, and an auxiliary-target census against the admissibility criterion `log_p(det)/rank <= 1/4`. Two cells decided at zero compute (generic `E'`: rank 4, exponent 1/2; `E^{(p^k)}`: degenerate). |

## 3. Adjacent committed proposals checked but NOT in the 19

These carry different `question_id`s, so they are outside the handoff's list, but
they orbit the same frozen paper and a proposal that ignored them would be
duplicating in a neighbouring lane. All were checked by field extraction; the
first three by reading the title/claim head.

- `IDEA-20260805-f9e801` (RQ-WESO-8aff57) — the published middle-memory line is a
  **section, not a frontier**: `B` is optimised at the full-memory corner and then
  held fixed while `w` slides; plus the never-run reproduction of the paper's own
  five-row table. **This is the nearest committed record to any "re-optimise the
  split/`B` under a memory budget" idea, and it is why no such idea is filed here.**
- `IDEA-20260805-b4bc59` (RQ-WESO-8aff57) — two unpriced multiplicities: the
  divisor-window claw count `k_div` and Remark 1's isogeny multiplicity `k_isog`.
- `IDEA-20260805-332316` (RQ-WESO-8aff57) — quantifier-order / input-specification
  audit of the two mutually incompatible 2026 complexities (sibling of `d66193`).
- `IDEA-20260805-c4ae3d` (RQ-SQISIGN-39f231) — SQIsign's SIDH-shape auxiliary datum
  stays in the secret key; the Kani obstruction is a publication boundary.
- `IDEA-20260805-bb4bf8` (RQ-SQISIGN-001) — SQIsign commitment-walk mixing audit.

## 4. The pre-ledger catalogue, which is NOT in the handoff's list and must be

`ideas/catalogue-20260805/` holds **102 pre-ledger ideas** across nine slices
(`INDEX.md`), of which **30 are SSI (`B1`, `B2`, `B3`) and 25 are SSIQ (`C1`,
`C2`)**. It mints no identifiers and is not a ledger record, but it is committed
state in the repository and it is the strongest available duplication filter for
this task. Sections `B1 §0.3`, `C1 §0.2`, `C2 §0` and `B3` were read; the full
`### ` heading list of all nine slices was extracted.

Entries that would have collided with candidate ideas considered in this session,
and which caused those candidates to be **dropped before drafting**:

| Candidate considered here | Collides with | Verdict |
|---|---|---|
| Asymmetric / unbalanced-split streaming tradeoff `T = M^2/w` | `C2-1` (names exactly this curve as its fourth control) and `IDEA-20260805-f9e801` | **Dropped.** Already the nearby-object control of a catalogue entry and the subject of a committed adjacent-lane proposal. |
| Frobenius-orbit key / self-claw under an involution | `C2-4` and `IDEA-20260804-84328c` | **Dropped.** |
| Golden-claw multiplicity `R` charged into vOW | `C2-3`, `IDEA-20260805-b4bc59`, `IDEA-20260805-2d2c41` | **Dropped.** |
| Area-time / 3-D wiring repricing | `C2-6`, `B1-6`, `IDEA-20260805-bc8246` | **Dropped.** |
| Quantum claw finding on the `p^{1/3}` table | `C2-9`, `B1-5` | **Dropped.** |
| Per-vertex `j`-only filter as a screen | `B1-9`, `IDEA-20260805-250e50` | **Dropped as such.** Survives only in the changed-quantifier form (advice/preprocessing) filed as `IDEA-20260806-9c2f80`, which `B1-9` does not contain: `B1-9` is a polynomial-memory walk with a per-vertex test, not a `p`-only advice string. |
| One-large-prime variation of the smooth table | `B1-4` | **Dropped** (and it is `p^{o(1)}` anyway). |
| Cross-attempt table amortisation | `C2-8` method ceiling names it as lever `A7` | **Dropped** (and it is `p^{o(1)}`: attempts number `P0^{-1} = p^{o(1)}`). |
| Successive-minima profile of `Hom(E,E^{(p)})` | `B1-2`, `C1-3` | **Dropped.** |
| Partner-map exponent / auxiliary-target census | `B1-8`, `B1-10`, `IDEA-20260805-e7ee4a` | **Not dropped, but narrowed**: the filed record `IDEA-20260806-e4c719` adds a *third* parameter these do not contain and exhibits a cell where `e7ee4a`'s two-parameter criterion returns the wrong number. |

## 5. What this audit does not establish

- **No shell.** This session has no Bash tool. `tools/allocate_id.py`,
  `tools/validate_ledger.py` and `python3` were **not executed**. Consequences are
  recorded in `ideation_report.md` §5 and in each proposal's
  `id_allocation_provenance` block. No command is reported as run that was not run
  (AGENTS.md rule 9).
- **No literature adjudication.** eprint, arXiv and NIST are unreachable from this
  environment. Every filed record carries `novelty_status: unverified`. This audit
  establishes only that the *committed corpus of this repository* does not already
  contain the filed objects; it establishes nothing about the published literature
  in either direction, and nothing here may be read as "this is new" or as "this is
  known".
- **Head-reads, not full reads.** For 12 of the 19, the record head through
  `mechanism` was read rather than the whole file. A duplication that lives only in
  a `predictions` or `minimal_test` block of one of those 12 would not have been
  caught. This is the audit's stated recall limit and it is the first thing the red
  team should attack.
- **The 257-file glob was not fully enumerated.** The tool returned 100 of 257
  paths. The remaining 157 were reached only through the targeted `IDEA-20260805-*`
  field extraction and the `question_id` filter, so a colliding proposal filed
  under an unexpected `question_id` before 2026-08-05 could have been missed.
