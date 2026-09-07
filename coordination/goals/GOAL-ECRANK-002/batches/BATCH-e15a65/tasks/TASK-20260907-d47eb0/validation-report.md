# Validation report — TASK-20260907-d47eb0

- **Task:** TASK-20260907-d47eb0 (Validator, `review-adversarial` @ xhigh, independent session)
- **Goal / question / batch:** GOAL-ECRANK-002 / RQ-ECRANK-27dcc5 / BATCH-e15a65
- **Package under review:** `experiments/EXP-ECRANK-73275e` version 1, eight enumerated runs,
  produced by TASK-20260907-2a3331, snapshot-archived by TASK-20260907-5058f5 at commit
  `03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad`
- **Frozen review plan:** `ledger/decisions/DEC-20260907-9953c0.yaml` (`REVIEW-PLAN-BATCH-e15a65`)
- **Joints owned:** J1, J2, J3, J4. J5, J6, J7 belong to TASK-20260907-46731e and are not
  addressed here.
- **Authority:** findings only. No status changed, nothing promoted, no F1–F4 finding assigned,
  no raw artifact modified, nothing committed. **No whole-claim verdict is returned** — four of
  seven joints cannot compose one.
- **Scope of every statement below:** n ∈ {6, 8}; nested H ≤ 10⁴ at n = 6 and ≤ 10³ at n = 8;
  the seeded 10⁴ b-tuple sample per arm; exact stdlib `fractions.Fraction` arithmetic; the
  1.0e8 counted-exact-op cap per run; toy claim tier per `docs/claims-and-verification.md`.

---

## PART A — J4 BLIND RE-DERIVATION (written before any producer record was opened)

> **This section was written to disk in full before `experiments/EXP-ECRANK-73275e/execution-report.yaml`,
> `.../runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json`,
> `.../runs/RUN-ECRANK-73275e-R4-construct-n6-replay/raw-result.json`, or any other
> `raw-result.json` in the package was opened.** Part B and everything after it were written
> afterwards. `experiments/EXP-ECRANK-73275e/source` and
> `experiments/EXP-ECRANK-73275e/implementation.md` (the declared `blind_from` set) were **never**
> opened at any point in this task.

### A.0 Read order actually followed (exact, in order)

Before writing this section, and only these:

1. `agents/validator.md`
2. `AGENTS.md`
3. `ledger/handoffs/TASK-20260907-d47eb0.yaml` (mandatory; **embeds the full frozen review plan**)
4. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/dispatch_queue.json` (header + own card)
5. `experiments/EXP-ECRANK-73275e/specification.yaml` (the frozen contract — the statement I derive from)
6. `ledger/hypotheses/H-ECRANK-36d8d7.yaml`
7. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-d47eb0/task_card.yaml`
8. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/coordinator-prior-20260907T174252Z.md`
9. Directory listings only (`ls`) of `experiments/EXP-ECRANK-73275e/` and `.../runs/` — file names,
   sizes and mtimes; **no file content**.

No producer run record, checkpoint, stdout, manifest or `execution-report.yaml` had been opened
when the text below was written.

### A.1 Declared limitation of this blindness — stated up front, not discovered afterwards

The plan's compensating control for J4 is a **declared read order**, not true blindness, and the
plan says so (`blind_rederivation.read_order_requirement`). I must add a second, undeclared
weakening that the plan did not anticipate:

**The mandatory readings themselves quote the answer.** The frozen review plan — which the
handoff embeds and which I am required to read first — states in `coordinator_prior` item (8) and
again in the J4 `attack_plan`: *"the recorded 15 at 100, 22 at 1000, 28 at 10000, feasible_tuples
20 and feasibility_fraction 0.002"*. The second Coordinator prior
(`coordinator-prior-20260907T174252Z.md`) repeats `{100: 15, 1000: 22, 10000: 28}` and
`feasibility_fraction: 0.002`.

So this re-derivation is **implementation-blind but not value-blind**. It is blind from
`source/` and `implementation.md`, which is what `blind_from` names and what a
wrong-but-self-consistent implementation would hide in; it is *not* blind from the target numbers,
which were unavoidable. Any agreement I report is therefore weaker evidence than the plan's design
intends, and I flag it rather than letting the round read as more independent than it was. This is
a defect in the plan, not in the producer.

### A.2 The statement I was asked to derive from, quoted exactly

From `experiments/EXP-ECRANK-73275e/specification.yaml`:

- `inputs.b_tuples`: *"affine normal form b_1 = 0, b_2 = 1; b_3..b_n distinct integers in
  [-20, 20] \\ {0, 1}; seeded order, NO adaptive reordering. Sample sizes: n = 6 arm 10^4
  b-tuples"*
- `inputs.support`: `[-1, 2, 3, 5, 7, 11, 13]`
- `inputs.r_heights`: *"nested boxes H in {10^2, 10^3, 10^4} at n = 6 ... counts cumulative over
  nested boxes and reported per H"*
- `inputs.engine`: *"the M3 family of H-ECRANK-36d8d7 (parent H-ECRANK-ee6e0e M2/M3): after
  prescribing the pattern (r_n carries it), ellipticity is the n - 5 quadratic vanishing
  conditions on g's coefficients; at n = 6 a single univariate quadratic in box"*
- `inputs.solver`: *"exact rational algebra (fractions.Fraction, stdlib only) ... NO Groebner
  machinery, NO PARI, NO network"*
- `metrics.primary[construct_count].definition`: *"per (n, H): count of distinct-minimal-model
  certified instances (nonsingular, twist class populated, certified rank above trivial), plus the
  feasibility fraction (fraction of b-tuples with >= 1 in-box solution of the n - 5 system) and the
  near-miss ledger"*
- `replication.seeds_note`: *"760806 -> R3 construct-n6 ... Coset choice, b-tuple order,
  coefficient sub-boxes, and planted positions all derive from the run seed via
  random.Random(seed)"*

### A.3 FINDING J4-A: the quantity N₆(H) is **not** derivable from the frozen contract

I attempted the derivation and stopped at a definitional wall. The plan explicitly invites this
outcome (*"If a definition cannot be pinned from the frozen contract alone, SAY SO; an unpinnable
definition is itself the finding"*), so I report it rather than guessing producer intent — a
guessed family would disagree for reasons that have nothing to do with whether the producer is
right, which is the worst possible output here.

Seven independent gaps. Each is sufficient on its own to block a numerical re-derivation:

| # | Undefined object | What the frozen contract actually says | Why it blocks |
|---|---|---|---|
| G1 | **The family itself — what `g` is** | *"the M3 family of H-ECRANK-36d8d7 (parent H-ECRANK-ee6e0e M2/M3)"*; the hypothesis adds only *"(n + 4)-dimensional in the coefficients of g after fixing the pattern"* | No polynomial, degree, variable set or defining system is written anywhere in the contract or the hypothesis. A dimension count is not a definition. The chain terminates at `H-ECRANK-ee6e0e`, which is **outside my declared `read_scope`** and which the hypothesis itself only paraphrases. |
| G2 | **The ellipticity condition** | *"ellipticity is the n - 5 quadratic vanishing conditions on g's coefficients; at n = 6 a single univariate quadratic in box"* | Which coefficient is the univariate unknown, and what the quadratic's three coefficients are as functions of (b, pattern), is never written. Without this there is no equation to solve. |
| G3 | **"square pattern prescribed on the carrier coordinate r_n" with support {−1,2,3,5,7,11,13}** | `independent_variables`: *"the square pattern's carrier coordinate (frozen: r_n)"* | The support is a 7-element set; the pattern is presumably a choice of squarefree class from the group it generates, but the contract never says which classes are enumerated, in what order, or whether one pattern or many per b-tuple. |
| G4 | **The coefficient box of height H** | *"inside the declared coefficient box"*, *"nested boxes H in {10^2, 10^3, 10^4}"* | "Height H" over ℚ is ambiguous between max(&#124;num&#124;,&#124;den&#124;) ≤ H, naive height ≤ H, integer coefficients &#124;c&#124; ≤ H, and a projective height. These give box cardinalities differing by orders of magnitude, so N₆(H) differs. |
| G5 | **"certified rank above the trivial"** | `inputs.certification_machinery` names *quartic_reduction / cubic_to_weierstrass*, *Mazur non-torsion (m·P ≠ O, m = 1..12)*, *Kummer [K:Q] = 8 via 7 exact integer square tests*, *exact F_l-reduction within-class certifier* | "The trivial" rank is never given a value, and no acceptance predicate composing those four checks is stated. The check *names* are not the check. |
| G6 | **"twist class populated"** | appears only inside the metric definition | Never defined anywhere in the contract or the hypothesis. |
| G7 | **"distinct-minimal-model" deduplication** | *"distinct minimal models"*, *"cross-stream deduplication by minimal model before any count"* | The dedup key (minimal Weierstrass model over ℚ? j-invariant? conductor?) and the equivalence used are not stated. The plan itself identifies this as load-bearing. |

**Consequence.** No independent party can compute N₆(H) or the feasibility fraction from the
frozen contract. The primary metric of this experiment is not reproducible from its own
specification; it is reproducible only from `source/`, which is exactly the artifact a blind
re-derivation exists to route around. **This is my J4 result, and it is a negative one.**

I state plainly what I did **not** show: I did **not** show that 15 / 22 / 28 or 0.002 are wrong.
I showed they are **not independently checkable** at the frozen contract's level of
specification.

### A.4 What I *could* pin blind, and did — committed before opening anything

These are the falsifiable artifacts I commit to in advance.

**(i) The b-tuple sample space.** Pool = integers in [−20, 20] minus {0, 1} ⇒ **39** elements.
Ordered distinct 4-tuples (b₃..b₆ at n = 6): 39·38·37·36 = **1 974 024**. Unordered 4-subsets:
**82 251**.

**(ii) The seeded stream.** `random.Random(760806)` is fully pinned by the contract; the *call
sequence* is not. I enumerated five natural stdlib conventions. **Three of them coincide exactly**,
which materially narrows the ambiguity:

| Convention | first 3 tuples (b₃,b₄,b₅,b₆) | SHA-256 of the 10⁴-tuple stream | distinct as tuples | distinct as sets |
|---|---|---|---|---|
| C1 `rng.sample(pool,4)` | (4,−7,−1,−2), (19,−11,20,−16), (−9,15,4,6) | `b1e62603e999…fafeda` | 9976 | 9453 |
| C3 `rng.choice(pool)` + dup-reject | *identical to C1* | `b1e62603e999…fafeda` | 9976 | 9453 |
| C5 `pool[rng.randrange(39)]` + dup-reject | *identical to C1* | `b1e62603e999…fafeda` | 9976 | 9453 |
| C2 `sorted(rng.sample(pool,4))` | (−7,−2,−1,4), (−16,−11,19,20), (−9,4,6,15) | `50cd816999f7…8061bd` | 9453 | 9453 |
| C4 `rng.randint(-20,20)` + reject 0,1,dups | (2,−7,−1,−2), (17,−11,18,−16), (−9,13,2,4) | `116616bf4a3e…8fb3f9` | 9983 | 9421 |

(Full SHA-256 C1/C3/C5: `b1e62603e99983565d65b38297be7c20eeddef3e6eb352bf89d5ff87c1fafeda`;
C2: `50cd816999f7c890c1b5fcaf1e0128bb242ce2233aab7b61e371b663018061bd`;
C4: `116616bf4a3e5ec0b915fc908e07ae0f6347a330601f8945ebe5f03e598fb3f9`.
Derivation script: `$TMPDIR/j4/blind.py`, stdlib only, no network.)

**Committed prediction:** if the producer's stream is any of C1/C3/C5 its first b-tuple is
(0, 1, 4, −7, −1, −2).

**FINDING J4-B (blind, before opening anything).** Under C1/C3/C5 the 10⁴ draws contain only
**9453 distinct 4-element sets** (547 repeats). The contract says "10^4 b-tuples" and defines the
feasibility fraction as *"fraction of b-tuples with ≥ 1 in-box solution"* without saying whether
the denominator is the 10⁴ **draws** or the distinct **tuples**, and without saying whether
repeated tuples are counted once. A denominator of 9453 versus 10 000 changes the reported
fraction by ~5.8 %. The contract does not pin it.

**(iii) Structural predicates that any correct implementation must satisfy.** Derived from the
contract text alone; I check them against the record in Part B.

- **P-a (arithmetic identity).** `feasibility_fraction = feasible_tuples / 10⁴` if the denominator
  is the declared sample size. 20/10⁴ = 1/500 = **0.002** exactly.
- **P-b (Bézout ceiling at n = 6).** The contract fixes the n = 6 condition as *"a single
  univariate quadratic in box"*. A univariate quadratic over ℚ has **at most 2** rational roots.
  Hence per b-tuple at most 2 in-box solutions, and therefore
  **N₆(H_top) ≤ 2 × feasible_tuples(H_top)**. With 20 feasible tuples the hard ceiling is **40**.
- **P-c (cumulativity).** Boxes are nested and counts cumulative ⇒
  N₆(10²) ≤ N₆(10³) ≤ N₆(10⁴).
- **P-d (HEUR-1 decade law).** HEUR-1 is N(n,H) ~ C·H^(5−n/2); at n = 6 the exponent is **+2**,
  i.e. a factor **100 per decade** of H. `tail_checks` requires the smallest and largest decade
  ratios of N₆ to be *reported against* that prediction.
- **P-e (feasibility fraction per H).** `metrics.primary[construct_count]` defines the feasibility
  fraction **per (n, H)**, so three values are required at n = 6, not one.

**Applying P-b/P-c/P-d to the triple the plan already disclosed to me** (15, 22, 28; 20 feasible):
15 ≤ 22 ≤ 28 satisfies P-c; 28 ≤ 40 satisfies P-b but **requires at least 8 of the 20 feasible
tuples to contribute two distinct certified minimal models each** — i.e. the "distinct-minimal-model"
dedup (gap G7) is load-bearing for 8 of the 28, exactly as the plan suspected. Measured decade
ratios are 22/15 = 1.467 and 28/22 = 1.273, implied exponents **0.166** and **0.105**
(overall 10²→10⁴: ratio 1.867, implied exponent **0.135**) against HEUR-1's predicted **+2**.
From N₆(10²) = 15, exponent +2 would predict N₆(10³) = 1500 and N₆(10⁴) = 150 000. The recorded
triple is **four orders of magnitude below** the pre-registered law at the top box. This is a
derivable arithmetic fact about numbers the plan disclosed; it is **not** a verdict on HEUR-1,
which no one in this round may reach, and it is stated only as the P-d comparison the frozen
`tail_checks` demand.

### A.5 J4 blind bottom line (fixed before Part B)

| Quantity | Blind re-derived value |
|---|---|
| N₆(10²) | **NOT DERIVABLE** from the frozen contract (gaps G1–G7) |
| N₆(10³) | **NOT DERIVABLE** |
| N₆(10⁴) | **NOT DERIVABLE** |
| feasibility fraction at n = 6 | **NOT DERIVABLE** (and denominator unpinned, J4-B) |
| First b-tuple of the seeded stream | (0, 1, 4, −7, −1, −2) under C1/C3/C5 — committed |
| Stream SHA-256 | `b1e62603e99983565d65b38297be7c20eeddef3e6eb352bf89d5ff87c1fafeda` (C1/C3/C5) |
| Hard ceiling N₆(H_top) | ≤ 2 × feasible_tuples |

--- END OF PART A. Producer records opened only after this point. ---

## PART B — verification against the producer records

### B.0 Read order, continued

After Part A was written to disk, and only then, in this order:

10. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/archives/TASK-20260907-5058f5/snapshot-receipt.json`
11. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/dispatch_queue.json` (archive blocks)
12. `tools/validate_ledger.py` (`RUN_REQUIRED_TOP`, `check_run`) — the schema being asserted
13. All eight `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `checkpoints/*.json`
14. All eight `raw-result.json`, R6→R1→R2 last among the audit runs
15. `experiments/EXP-ECRANK-73275e/execution-report.yaml` — **opened last of all the producer artifacts**
16. `ledger/handoffs/TASK-20260907-2a3331.yaml` (producer inference block and completion gate)
17. `ledger/decisions/DEC-20260907-9953c0.yaml` — the **authoritative** review plan, read **last of
    everything**, solely to verify that the copy embedded in my handoff (the copy I actually worked
    against) matches it.

**Plan-copy integrity — checked, not assumed.** I compared the two copies field by field. They are
identical on every field binding on this reviewer: `claim_under_review`, `coordinator_prior`,
`blindness` (`mutual: true`, `lifted_for: []`), `blind_rederivation.{quantity, parameters, blind_from,
blindness_limits}`, `procedure_deviations` (empty in both), and the `attack_plan` / `breaking_artifact`
of J2, J3 and J4. Two benign divergences: the **handoff** copy adds a clause to J1's attack plan (the
explicit ban on `seed*1000 + index` derived seeds) that the decision omits — a strict superset, and I
ran the stricter check; and the **decision** copy adds one explanatory sentence to
`read_order_requirement` about why the re-derivation was not split onto a third reviewer, which imposes
no requirement. The J5/J6/J7 abbreviation in the handoff copy is what the decision's own
`binding_copies_note` prescribes. **No binding requirement differs, and the verdicts below stand
against the authoritative plan.**

`experiments/EXP-ECRANK-73275e/source/**` and `experiments/EXP-ECRANK-73275e/implementation.md` were
**never opened**. Two contacts with those paths are disclosed precisely:
(i) a `find`/`os.walk` directory listing that returned file *names* only;
(ii) an SHA-256 integrity check of the eight `source/*.py` files against the digests declared in
`run.code.source_sha256`, run **after** Part A was frozen. A digest carries no implementation
content and this is the artifact-binding check `agents/validator.md` responsibility 1 requires.
No byte of either path was read or displayed.

---

## J1 — run-record integrity, schema conformance, seed integrity, raw/summary agreement

### VERDICT: **holds**, with ten named defects, none of them a numeric disagreement.

#### J1.1 Snapshot binding — verified

| Check | Result |
|---|---|
| `git diff --stat 03c6e3181..HEAD -- experiments/EXP-ECRANK-73275e/` | **empty** — the tree I validated is byte-identical to the snapshot commit |
| `03c6e3181…` reachable from `HEAD` (`51af17ddf…`) | yes, ancestor |
| Snapshot receipt `path_sha256` (60 paths) recomputed | **60 matched, 0 mismatched, 0 missing** |
| `runs/` git history | **exactly one commit** (`03c6e3181`) — no run record was written twice |
| `experiments/EXP-ECRANK-73275e/amendments/` | does not exist — no post-approval protocol amendment |
| `specification.yaml` vs approval archive TASK-20260907-2cd955 declared sha256 `9edd4a9ba1c9…` | **match** |
| Post-design edits to `specification.yaml` (`54de63f99→20e55df41→486945631`) | **only** `status`, `approved_by`, `approval_note`. **No protocol field was edited after design.** |
| `tools/validate_ledger.py` | **zero violations naming EXP-ECRANK-73275e** |

Evidence: `coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/archives/TASK-20260907-5058f5/snapshot-receipt.json`;
`coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/dispatch_queue.json` (`TASK-20260907-5058f5.archive.commit_sha = 03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad`, `parent_sha = 528580934eba3e1b49d3f50797a748aa2e898779`).

**I found no evidence of re-scoring anywhere in the package.**

#### J1.2 Schema conformance — verified, all eight

`RUN_REQUIRED_TOP` as actually enforced by `tools/validate_ledger.py:181` is
`[id, experiment_id, status, code, environment, inputs, timing, result]`.

All eight `manifest.yaml`: nested `run:` mapping present; **0 missing** `RUN_REQUIRED_TOP` fields;
`code.commit` = `5b83fed02e40d5a2aea939220ff34e2ef4961f6b` and `code.command` present in all eight;
all five companions (`command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`)
present in all eight; `command.txt` string-equal to `run.code.command` in all eight;
`environment.json` byte-identical across all eight (sha256 `6c893fe431007f6e…`, CPython 3.12.3,
Linux-6.12.94, `stdlib_only_pipeline: true`, `pari_in_pipeline: false`, `network: "none"`,
`cypari_present: false`), matching the contract's `descent_calls: 0 / pari_ellrank_calls: 0 / network: none`.

**Executed-code binding (correcting an obvious first reading).** `source/**` and `implementation.md`
are in the Executor's `write_scope` but appear in **no** archive's `artifact_paths` or `path_sha256`
(11 files under the experiment directory are outside the snapshot receipt's 60). They are nonetheless
content-bound *transitively*: every run manifest carries `run.code.source_sha256` with a digest for
each of the eight `source/*.py` files, all eight manifests declare the **same** map, and each manifest
is itself one of the 60 hash-bound paths. I recomputed those eight digests: **8/8 match**. So the
executed code is content-bound, but by a mechanism one level below the archive receipt.

**`code.dirty: true` in all eight — and the dirt is benign.** `code.dirty_files` is identical in every
run and contains exactly two entries, both untracked:
`?? coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/claims/` and
`?? experiments/EXP-ECRANK-73275e/runs/`. That is the run package writing itself. **No tracked source
file was uncommitted at run time**, which the bare `git_dirty_at_runs: true` in
`execution-report.yaml` does not convey. See "Priors" below.

#### J1.3 Seed integrity — verified; no derived seed

| Run | recorded seed | in `replication.seeds`? | assigned by `seeds_note`? |
|---|---|---|---|
| R3 | 760806 | yes | yes (R3) |
| R4 | 760806 | yes | yes (R4 replay, bit-for-bit) |
| R5 | 760810 | yes | yes (R5) |
| R6 | **760806** | yes | **no — the contract assigns R6 no seed** |
| R7 | 760812 | yes | yes (R7) |
| R8 | 760808 | yes | yes (R8) |
| R1, R2 | none recorded (audit runs read committed bytes; `arm_seed: 760708` is the *predecessor's*) | n/a | n/a |

**The forbidden predecessor practice did not recur.** No seed anywhere in the package is derived; there
is no `Random(seed*1000 + index)` pattern in any manifest or raw record. Every seed is a literal member
of the declared list. This is a clean pass on the sub-joint the plan singled out.

Consequence of the undeclared R6 seed: R6's `coset_V` is `[0, 1, 28, 29, 64, 65, 92, 93]`, **identical
to R3's**. For a null object that is a desirable property (same shape as the live arm), but it is the
consequence of a choice the frozen contract does not declare.

#### J1.4 Raw versus summary — every number agrees; three artifacts are missing

I checked every numeric field in `execution-report.yaml` against the named `raw-result.json` /
`manifest.yaml`. **Zero numeric disagreements.** Specifically verified equal: all eight
`counted_exact_ops`, all eight `ops_cap_respected`, all sixteen `wall_seconds_*`, all eight
`peak_rss_bytes`; R1 `inbox 1.0 / mismatches [] / planted_2d meets 5 vs expected 5.0`;
R2 `inbox_fraction 1.0, n_draws 24, n_in_box 24` and the three planted points
`(at 0, plant [7,8], meets 3)`, `(at 1, plant [11,12], meets 3)`, `(at 2, plant [13,14], meets 4)`,
all with `S_abs 1600`, `N_a 8000`, `expected_meets 5.0`;
R3 `found 28 / feasible_tuples 20 / feasibility_fraction 0.002 / counts_per_H {100:15,1000:22,10000:28} / exhaustion null`;
R4 `iv2_instance_list_identical true / iv2_ops_r3 9191003 / iv2_ops_r4 9191003 / iv2_counts_identical_flag_in_raw false`;
R5 `found 0 / feasible_tuples 0 / exhaustion {counted_ops_cap, 100002120, b_index 666}`;
R6 `found [] / feasible_tuples 0 / n_b_declared 64 / null_proof_first null`;
R7 `[5,6,7,7,7,7,6,7]`, `expected 7`, `n6_all_match false`, `n8_all_match false`;
R8 `9 declared / 0 built / recovered 0/0 / slope null / decade_ratios {}`.

The producer **did not hide** the two awkward fields: `iv2_counts_identical: false` and
`null_proof_first: null` are both quoted verbatim into the report and given PD entries. That is
creditable and I record it.

**Named defects.**

| # | Defect | Artifact |
|---|---|---|
| J1-D1 | **`required_artifacts` "the exact op ledger per run with IC-1 exclusions itemized [SR-11]" is ABSENT.** No run record and no line of `execution-report.yaml` itemizes the IC-1 exclusions. The only `IC-*` tokens in the package are `IC-13/15/16/17/18` inside `pred_raw_parameters` — the **predecessor's** implementation choices. | all eight `raw-result.json`; `execution-report.yaml` |
| J1-D2 | **`required_artifacts` "the null-family definition and its infeasibility proof (R6)" is ABSENT from the run record.** The contract states the executor "records the proof of infeasibility **in the run record**". R6 carries `null_proof_first: null` and no other proof field. The producer points to `source/null_family.py`, which is `blind_from` and which I did not open, so I **cannot verify the proof exists**. | `runs/RUN-ECRANK-73275e-R6-null/raw-result.json` |
| J1-D3 | **IV-8's untested statement exists ONLY in the report.** `certified_class_count_max_among_found: 3`, `iv8_four_class_instance_present: false` and `iv8_untested_statement` appear in `execution-report.yaml`; R3's and R5's raw records carry none of them. I re-derived the first two from R3's `found` list (max `n_classes` = 3, present in **all 28**; no 4-class instance) — those two are sound. The statement itself is report-only. | `execution-report.yaml:95-100`; `runs/…R3…/raw-result.json` |
| J1-D4 | **The IV-8 statement is internally incoherent.** It reads "single-class coverage count: 28 instances, all 3-class". The single-class coverage count is **0**; all 28 certified instances carry `n_classes: 3`. Labelling 28 three-class instances as a single-class coverage count misstates the very quantity IV-8's fallback branch demands. | `execution-report.yaml:97-100` |
| J1-D5 | **The report's seed table omits R1, R2 and R6.** `preanalysis_checks.seeds_as_declared` lists R3/R4/R5/R7/R8 only. R6's manifest records `seed: 760806`. The producer's own handoff completion gate requires the report to record "**every seed**" — **not met**. | `execution-report.yaml:218-223`; `ledger/handoffs/TASK-20260907-2a3331.yaml` |
| J1-D6 | **`tail_checks` "The smallest and largest H-decade ratios of N_6 are reported against the exponent +2 prediction" is NOT DONE.** No decade ratio appears in any run record or in the report. | `specification.yaml` `tail_checks`; `execution-report.yaml` |
| J1-D7 | **The feasibility fraction is required per (n, H) and only one value is recorded.** `metrics.primary[construct_count]` defines the count "per (n, H) … plus the feasibility fraction". R3 records a single `feasibility_fraction: 0.002` and a single `feasible_tuples: 20`, not one per H ∈ {10², 10³, 10⁴}. | `runs/…R3…/raw-result.json` |
| J1-D8 | **R5's `feasibility_fraction: 0.0` has no stated denominator.** `n_b_done` is **667**, `n_b_declared` is 10000. The recorded 0.0 is 0/667, not 0/10⁴; the record does not say which. | `runs/…R5…/raw-result.json` |
| J1-D9 | **`resources.cpu_seconds` is `null` in all eight runs**, with an explicit note. Disclosed, not concealed; `peak_rss_bytes` is present throughout. Recorded as a gap against the AGENTS.md artifact policy's "resource measurements". | all eight `manifest.yaml` |
| J1-D10 | **The snapshot receipt carries `commit_sha: null` and `parent_sha: null`**, and its `base_commit_checked` prose says "TASK-20260907-2cd955 stays queued", while `BATCH-a2bf8b/dispatch_queue.json` records that task at `state: completed`. The commit sha is present in the queue's archive block. Content-first binding (CLAUDE.md) makes this non-fatal — and content verified 60/60 — but the receipt file and the queue disagree about a task state. | `…/archives/TASK-20260907-5058f5/snapshot-receipt.json`; `…/BATCH-a2bf8b/dispatch_queue.json` |

**J1 attempt/re-scoring check.** Exactly one attempt directory exists in the package,
`RUN-ECRANK-73275e-R1-audit-smoke/attempt-1-precommit-smoke/`, with a `NOTE.txt` reading
*"Pre-commit smoke of R1 to verify audit reconstruction before the implementation snapshot. Official R1
is the post-commit attempt."* — matching the structure the plan expected. No run exceeded the 12-attempt
ceiling and no 13th-attempt refusal is recorded (none was needed). I note the limit of this check: the
record can show attempts that were preserved; it cannot show that no attempt went unpreserved.

---

## J2 — reproducibility and op accounting

### VERDICT: **holds** on determinism and on the exact op boolean; **two required artifacts are missing** (R5 checkpoint cadence, SR-11 IC-1 exclusions).

#### J2(a) R4 versus R3 — determinism verified, and `iv2_counts_identical` RESOLVED by re-derivation

| File | R3 sha256 | R4 sha256 | verdict |
|---|---|---|---|
| `checkpoints/ckpt-001-final.json` | `a6ae120aafd975d35689fad92bf833747a5b201cc5be52fd3162080b88cd4ecc` | **same** | identical; matches the digest declared in the frozen plan |
| `stdout.log` | `68a499ffb459337bde19a483eb51acb4255dd7fd60cb7c36c8da8d297fe3612c` | **same** | identical; matches the digest declared in the frozen plan |
| `stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **same** | both empty |
| `raw-result.json` | `01378190bac559862922a7a572d9b4d50a825f3617a74efafff6802d98975f2f` (25914 B) | `c239a8e95f70606e44257a3bbde5a456cf86f4e7312a05b0aac16b444f3f9afc` (26032 B) | **differs, and the difference is fully accounted for** |

Structural diff of the two `raw-result.json`: R4's key set is R3's key set **plus exactly four**
(`iv2_counts_identical`, `iv2_instance_list_identical`, `iv2_ops_r3`, `iv2_ops_r4`). On the intersection,
**every key is equal**, including `found` deep-equal over all 28 instances,
`counts_per_H`, `feasible_tuples`, `feasibility_fraction`, `coset_V`, `ops`, `n_b_done`,
`near_miss_ledger`. The 118-byte size difference is those four keys.

**Resolving `iv2_counts_identical: false` — re-derived, not accepted.** The frozen plan calls this the
single most dangerous item in the package, and the producer's note (`execution-report.yaml:115-119`) is
a claim about a bug made by the party being checked. I did not accept it. Instead I recomputed
`counts_per_H` **independently from each run's own `found` list**, as the cumulative number of
instances with `r_height ≤ H`:

- from R3's `found`: `{100: 15, 1000: 22, 10000: 28}` — equals R3's recorded map
- from R4's `found`: `{100: 15, 1000: 22, 10000: 28}` — equals R4's recorded map

Since `found` is deep-equal between the runs and `counts_per_H` is a function of `found`, **no divergence
in the data is possible**. The recorded `false` is a defect in the *check*, not a divergence in the *run*.

Precisely what I did and did not establish:
- **Established independently:** there is no substantive divergence between R3 and R4. IV-2's requirement
  ("must reproduce R3's instance list, counts, and op ledger bit-for-bit") is met on all three of instance
  list, counts and op ledger.
- **NOT established:** the producer's stated *mechanism* — an in-memory int-keyed dict compared against a
  str-keyed dict before `json.dump`. That lives in `source/`, which is `blind_from`; I did not open it.
  The mechanism is consistent with everything I can observe and remains **unverified**.
- A residual note the Coordinator should have: a **reported boolean whose value depends on dict key
  representation** sits uncomfortably beside IV-7, which forbids "dict-order dependence in **any reported
  quantity**". Key *typing* is not literally key *order*, so I do not claim IV-7 fails on this; I flag it
  as control-adjacent and stop.

Scope limit: this determinism check exercises the **R3/R4 pair only**. No replay of R1, R2, R5, R6, R7 or
R8 was executed, so their determinism is **not evaluated**.

#### J2(b) Op accounting — the required per-run table

Cap = `1.0e8` exact, no band. Recomputed boolean = `counted_ops < 1.0e8`.

| Run | `counted_ops` | recomputed `counted_ops < 1.0e8` | recorded `ops_cap_respected` | agree? | checkpoints present | cadence checkpoints due (⌊ops/1e7⌋) |
|---|---:|:---:|:---:|:---:|---:|---:|
| R1 audit-smoke | 0 | **true** | true | ✔ | 0 | 0 |
| R2 draw-support | 0 | **true** | true | ✔ | 0 | 0 |
| R3 construct-n6 | 9 191 003 | **true** | true | ✔ | 1 (`ckpt-001-final.json`) | 0 |
| R4 construct-n6-replay | 9 191 003 | **true** | true | ✔ | 1 (`ckpt-001-final.json`) | 0 |
| **R5 construct-n8** | **100 002 120** | **false** | **false** | ✔ | **1** | **10** |
| R6 null | 37 416 | **true** | true | ✔ | 1 (`ckpt-001-final.json`) | 0 |
| R7 known-false | 308 732 | **true** | true | ✔ | 0 | 0 |
| R8 planted | 6 751 | **true** | true | ✔ | 0 | 0 |

- **Every recorded boolean equals my exact recomputation. 8 of 8.** No tolerance band is applied anywhere.
- `raw-result.json:ops` equals `manifest.run.result.metrics.counted_exact_ops` in all eight runs, and
  `execution-report.yaml` quotes both correctly in all eight.
- **R5's stop is recorded as exhaustion, never as a result.**
  `exhaustion: {"kind": "counted_ops_cap", "ops": 100002120, "b_index": 666}`, `n_b_done: 667` of
  `n_b_declared: 10000`, and the report's own note reads "exhaustion is inert in both directions
  (stopping_rules)". The overshoot is 2 120 counted ops past the cap; the contract's boolean is defined
  precisely to surface that, and it does. **R5's `found: 0` is inert in both directions and says nothing
  about n = 8 in either direction.**
- **J2-D1 (defect). R5 is missing its required checkpoint cadence.** `stopping_rules` and
  `required_artifacts` both require "checkpoints every 1e7 counted ops for R3/R5". R5 reached
  100 002 120 counted ops ⇒ **10 cadence checkpoints due; 1 present**, and that one is
  `ckpt-001-final.json`, a terminal checkpoint rather than a cadence checkpoint. R3 at 9 191 003 ops had
  0 cadence checkpoints due and carries its final one, so R3 is conformant. **This omission is not
  disclosed under PD-1, PD-2 or PD-3.**
- **J2-D2 (defect). SR-11's IC-1 exclusion list is not recorded** (see J1-D1). If "op accounting" is read
  to include SR-11's itemized exclusions, that sub-clause is **NOT SATISFIED** and `counted_ops` is a
  lower bound on true cost by an unstated amount.
- **SR-10, both `wall_seconds` forms, exactly as recorded:**

| Run | `wall_seconds_monotonic` | `wall_seconds_timestamp_span` | identical? |
|---|---:|---:|:---:|
| R1 | 0.324303 | 0.324303 | yes |
| R2 | 0.313583 | 0.313583 | yes |
| R3 | 18.148213 | 18.148213 | yes |
| R4 | 18.257394 | **18.257395** | **no (Δ = 1e-6)** |
| R5 | 75.686747 | **75.686748** | **no (Δ = 1e-6)** |
| R6 | 0.250887 | 0.250887 | yes |
| R7 | 0.628985 | 0.628985 | yes |
| R8 | 0.110704 | 0.110704 | yes |

Both forms are present in all eight runs, so SR-10's *reporting* requirement is met. Whether two
near-identical numbers constitute two independent instruments is J6's joint and I do not answer it;
I record only that the prior's factual premise needs correction (see "Priors").

---

## J3 — the recorded outcome of every control IV-1 … IV-9 against its frozen text

Every "recorded outcome" below is quoted from the named **`raw-result.json`**, never from
`execution-report.yaml`, as the plan requires. Verdicts are mechanical. **I decide no disposition and
assign no F1–F4 finding.**

| Control | Frozen text (abridged, `specification.yaml controls`) | Recorded outcome, with raw artifact | Verdict | Frozen consequence (`invalidation_rules`) |
|---|---|---|---|---|
| **IV-1** | "known-false d = (1,1,…) Mestre degeneration (R7), n = 6 and n = 8; **certified totals must equal n − 1 (5 and 7)**; failure voids ALL runs." | `runs/…R7-known-false/raw-result.json`: `results["6"].per_b` = 8 entries, **every one** `{"built": false, "reason": "degenerate_deg_s_2"}`, `all_match: false`, `expected: 5`. `results["8"].per_b` = 8 entries, all `built: true`, `aggregate_total` = **[5, 6, 7, 7, 7, 7, 6, 7]**, `expected: 7`, `matches_n_minus_1` false at indices 0, 1, 6; `all_match: false`. | **NOT SATISFIED overall.** n = 6 branch: **NOT EVALUATED** — no certified total was produced, so the required equality with 5 has no left-hand side. n = 8 branch: **NOT SATISFIED** — 3 of 8 totals (5, 6, 6) ≠ 7. | **"IV-1 failure voids ALL runs of this experiment."** |
| **IV-2** | "arm replay R4 (same seed 760806 as R3) must reproduce R3's instance list, counts, and op ledger **bit-for-bit**." | R3/R4 `raw-result.json` equal on every shared key; `found` deep-equal over 28; `counts_per_H` `{100:15,1000:22,10000:28}` both, and **independently recomputed** from each `found` list; `ops` 9 191 003 both; `ckpt-001-final.json` and `stdout.log` digests identical. `iv2_counts_identical: false` is a check defect, established above without relying on the producer's note. | **SATISFIED** on all three required objects. | (would void R3 and R5 readings; does not fire) |
| **IV-3** | "planted yield R8 — instances planted from the R7 family (seed 760808) **must be detected** by the construction solver with the exponent gate in [0.699, 1.301] and per-decade ratios in [5, 20]; failure voids R3/R5 readings." | `runs/…R8-planted/raw-result.json`: `plants` = 9 entries, **all** `{"built": false, "h0": null, "r": null, "reason": "degenerate_deg_s_2"}`; `recovered: []`; `cells: {100:0, 1000:0, 10000:0}`; `decade_ratios: {}`; `log_log_slope: null`. `exponent_window: [0.699, 1.301]` and `per_decade_window: [5, 20]` are recorded but **never applied to anything**. | **NOT EVALUATED.** The control produced zero objects, so the detection gate never ran. `recovered: 0/0` is an **empty denominator, not a 0 % rate**. This is neither a pass nor a failure. | The frozen rules provide a branch for IV-3 *failure* only. **They provide no branch for a control that never evaluated** — a gap in the contract, recorded here for the Coordinator. |
| **IV-4** | "null object R6 — the solver on the null_family **must return exactly 0 solutions AND the audit code must flag the infeasibility**; a nonzero result voids the solver for all counts." | `runs/…R6-null/raw-result.json`: `found: []`, `counts_per_H: {"10000": 0}`, `feasible_tuples: 0`, `feasibility_fraction: 0.0` over `n_b_declared: 64`, `n_b_done: 64` — **conjunct 1 met exactly**. `null_proof_first: null` and no other proof or flag field — **conjunct 2 not present in the record**. | **PARTIALLY SATISFIED / conjunction NOT SATISFIED.** Conjunct 1 **satisfied**. Conjunct 2 **NOT EVALUATED in the run record**; I am blind from `source/null_family.py` and cannot say whether the frozen proof exists there. | "IV-4 failure voids every count." Whether an unrecorded flag beside a correct zero constitutes "IV-4 failure" is a reading; I state both halves and stop. |
| **IV-5** | "audit self-test R1 — stream reconstruction on one fixed b-tuple (first of R3-armB stream) must reproduce the recorded draws **bit-for-bit**, and the planted-meet arithmetic must hit a synthetic 2-D box case with a known answer; failure voids the audit (R2)." | `runs/…R1-audit-smoke/raw-result.json`: `b_tuple_mismatches: []`; `reconstruction_bit_identical_replay: true`; `reconstructed.rows` = 1 row at `b_index: 0` with 8 draws; `inbox: {in_box_fraction: 1.0, n_draws: 8, n_in_box: 8, out_of_box: []}`; `r1_planted_2d: {H: 20, N_a: 8000, S_abs: 1600, expected_meets: 5.0, meets_observed: 5, plant: [1,2]}` — the known-answer case hits exactly its expectation. `audit_source_commit_bound: a20a49b6adbcce51893c1221dbd69cdcd486ad9d` as the contract requires. | **SATISFIED**, at the scope of one b-tuple and 8 draws. | (would void R2 only; does not fire) |
| **IV-6** | "per-run attempt ceiling [SR-4], at most 12 attempts per run; **every** attempt preserved under `attempt-<k>-<label>/` with `NOTE.txt`; a 13th attempt is refused and reported, not run." | One attempt directory in the package: `runs/…R1-audit-smoke/attempt-1-precommit-smoke/` with `NOTE.txt`, `command.txt`, `environment.json`, `manifest.yaml`, `raw-result.json`, `stdout.log`, `stderr.log`. No other run carries an `attempt-*` directory; no 13th-attempt refusal is recorded. | **SATISFIED** on the ≤ 12 ceiling and on the preservation of the one attempt that exists. The "every attempt preserved" clause is **NOT EVALUABLE** from the record — absence of an attempt directory is consistent both with one attempt and with an unpreserved one. | none |
| **IV-7** | "determinism of all audit and construction outputs under frozen seeds; no wall-clock, pid, or dict-order dependence in **any reported quantity**." | R3 ≡ R4 on `found`, `counts_per_H`, `ops`, checkpoint digest and stdout digest (above). `runs/…R2/raw-result.json`: `reconstruction_bit_identical_replay: true`. No replay exists for R5, R6, R7 or R8. | **SATISFIED for the n = 6 construction pair (R3/R4) and for the R2 audit reconstruction; NOT EVALUATED for R1, R5, R6, R7, R8.** Flagged, not asserted: the reported boolean `iv2_counts_identical` is claimed by the producer to depend on dict **key typing**, which is adjacent to — but not literally — the "dict-order" this control names. | none stated |
| **IV-8** | "multi-class certificate coverage [SR-7] — at least one certified instance with **4 distinct twist classes** among R3/R5 output, **OR the run record carries** the explicit statement that the multi-class path remains untested (with the single-class coverage count). Absent both, the certification claim is downgraded to single-class." | `runs/…R3…/raw-result.json`: all 28 certified instances carry `certificate.n_classes: 3` and `verdict: "PASS"`; **max `n_classes` = 3, no 4-class instance**. `runs/…R5…/raw-result.json`: `found: []`. Top-level keys of R3's record contain **no** multi-class or untested field: `[H_levels, coset_V, counts_per_H, exhaustion, feasibility_fraction, feasible_tuples, found, n, n_b_declared, n_b_done, near_miss_ledger, near_miss_total, null_proof_first, ops, seed]`. | **NOT SATISFIED.** Branch 1 fails (no 4-class instance). Branch 2 fails **in the run record**: the untested statement appears only in `execution-report.yaml`, and IV-8 says "the **run record** carries". The statement is additionally miscounted (J1-D4). | **"the certification claim is downgraded to single-class"** — a downgrade, **not** a voiding. |
| **IV-9** | "planted distinctness [SR-8] — every planted instance (R8 **and** the R2 planted audit points) is a distinct (b-tuple, pattern) pair; no two plants share an h0 unless the record names the shared value and the reason." | `runs/…R2…/raw-result.json` `r2_plants`: `h0` = **7, 11, 13** — 3 distinct, plants `[7,8] [11,12] [13,14]`. `runs/…R8…/raw-result.json` `plants`: **9 distinct b-tuples**, but **1 distinct pattern** — all nine are `[1,1,1,1,1,1]` — and **all nine `h0` are `null`**. The record's own `iv9_distinct_h0: true` is therefore **a boolean over an empty set**. | **SATISFIED for R2** (3 distinct h0). For R8: the (b-tuple, pattern) distinctness clause is **SATISFIED** (9 distinct b-tuples); the h0 clause is **NOT EVALUATED** and the recorded `true` is vacuous. The predecessor's forbidden shape (repeated A-tuple, shared h0 = 191) did **not** recur. | none |

### J3 — the two readings I was asked to decide from the frozen text, and how they came out

**(a) Is `degenerate_deg_s_2` the known-false object behaving CORRECTLY, so that "not built" is the
control PASSING? — NO. Refuted by the frozen text itself.**

Three frozen passages pre-register a *positive* expectation for the all-ones family at n = 6:

- `specification.yaml` IV-1: "certified totals must equal n − 1 (**5** and 7)" — the 5 is paired with n = 6.
- `H-ECRANK-36d8d7` `structural_ingredients`: "The known-false d = (1, 1, …) Mestre degeneration as the
  control family (closed form; **expected certified totals n − 1 at n = 6 and n = 8**)."
- `H-ECRANK-36d8d7` `proof_search_map.baseline_reproduction`: "The draw-side law's anchor (d = 1 closed
  form) **is reproduced in R7** (known-false control, expected certified totals n − 1)."

The contract nowhere says the family should fail to build, and it names 5 as the value it should produce.
A run that builds nothing has produced no certified total, so the pre-registered equality is not
established. Reading "not built = correct degeneration" would require re-interpreting a frozen control
after seeing its result, which the protocol forbids and which is the convenient reading rather than the
textual one. **I therefore reject alternative (a).**

The right verdict, and it is not the same as "failed": the n = 6 branch is **NOT EVALUATED**. A control
that produced no object cannot pass, and `docs/inventor-protocol.md` treats a control that cannot fail
as the canonical artifact tell — but whether that reading applies here is **J5's joint (Red Team,
TASK-20260907-46731e)**, and I stop at the mechanical verdict.

**(b) Does the spec require ALL eight n = 8 totals to equal n − 1, or an aggregate? — The universal
reading is the only one with operational content.**

IV-1's text is a plural subject with "must equal" and a single scalar target per n: "certified totals
must equal n − 1 (5 and 7)". **The contract defines no aggregation over b-tuples anywhere** — no mean,
no max, no modal value, no tolerance. The record's own per-tuple field `aggregate_total` aggregates over
*twist classes within one instance*, not over tuples; its companion `matches_n_minus_1` is per-tuple and
`all_match` is the conjunction. So the producer implemented the universal reading, and it evaluates
`false`. An aggregate reading has nothing to bind to; and were one invented, `mean([5,6,7,7,7,7,6,7]) =
6.5 ≠ 7`, while `max = 7` would make the control unfailable by construction. **IV-1's n = 8 branch is
NOT SATISFIED: 3 of 8 totals (5, 6, 6) ≠ 7.**

**A fact neither prior recorded, and the Coordinator needs it: every n = 8 deviation is DOWNWARD.**
No total exceeds 7. The frozen plan's `proves_too_much.failure_signature` (a) is "the pipeline reports a
certified instance **above** n − 1 on the all-ones family" — **that did not occur.** The certifier is
documented as a verifier-checked **lower bound** from exhibited points (`H-ECRANK-36d8d7 walls`: "every
rank is a verifier-checked lower bound from exhibited points"), and under-certification is exactly what a
lower-bound certifier does when it cannot exhibit enough independent points. So IV-1 fails its frozen
**equality**, and it fails in the **conservative** direction for the pipeline's soundness. Both facts are
needed to compose a disposition; neither is a disposition.

### J3 — mechanical consequence, and its limits

Applying `invalidation_rules` and nothing else: **IV-1 is not satisfied against its frozen text, and the
frozen consequence of IV-1 failure is that ALL runs of this experiment are void.** IV-2 does not fire.
IV-8's consequence is a downgrade of the certification claim to single-class, not a voiding. IV-3 and
IV-4's second conjunct fall into a gap: the frozen rules branch on control *failure*, and a control that
**never evaluated** is neither pass nor failure — the contract has no rule for it, and that gap is itself
a finding.

Two limits I state plainly:

1. **This is a report of a frozen consequence, not a disposition.** I do not decide the batch outcome.
2. **A control failure is an instrument failure and is never negative mathematical evidence.** AGENTS.md
   core rule 3 and the contract's own `F4_controls` ("closes: **nothing** about the mathematics; the
   affected runs are VOID … per core rule 3") both bind. Nothing here says anything about HEUR-1,
   H-ECRANK-36d8d7, or the mathematics of the M3 construction in either direction.

---

## J4 — blind re-derivation of N₆(H) and the n = 6 feasibility fraction (comparison phase)

### VERDICT: **breaks** — the load-bearing quantity is not independently re-derivable from the frozen contract.

The word "breaks" here has one precise meaning and I hold to it: **N₆(H) cannot be recomputed by an
independent party from the frozen contract, so the number 28 has no independent check behind it.**
I did **not** show that 28, 22, 15 or 0.002 is wrong. Everything I could check about them checked out.

#### J4.1 The committed blind prediction — FALSIFIED, in the predicted way

Part A committed, before opening anything: the first b-tuple of the seeded stream is
(0, 1, 4, −7, −1, −2) under conventions C1/C3/C5, stream SHA-256
`b1e62603e99983565d65b38297be7c20eeddef3e6eb352bf89d5ff87c1fafeda`.

The record says otherwise. `runs/…R3…/raw-result.json`, `found[0]`:
`b_index: 579`, `instance.b = ["0","1","7","-14","16","-2"]`. My C1/C3/C5 stream at index 579 is
(0, 1, **10, −20, −13, −2**). Across all 28 certified instances, **blind-stream agreement is 0/28**, and
the 4-set {7, −14, 16, −2} appears **nowhere** in my 10⁴-draw stream.

I then ran a bounded search — **3 pool orderings × 5 stdlib generators × 25 RNG burn-in offsets = 375
conventions** — for any that reproduces `b_index 579 = (7, −14, 16, −2)`. **None does.**

This is not a defect in the producer. It is the empirical confirmation of finding J4-B: the frozen
contract fixes `random.Random(760806)` but not the *call sequence*, and it explicitly lists four
consumers of that one stream — "**Coset choice, b-tuple order, coefficient sub-boxes, and planted
positions** all derive from the run seed via `random.Random(seed)`" — **without fixing their order**.
The record shows a `coset_V` of `[0, 1, 28, 29, 64, 65, 92, 93]` drawn from the same stream, so the
b-tuple sequence is offset by an amount the contract does not state. **The declared 10⁴ b-tuple sample is
not reconstructible from the frozen contract.** That, plus gaps G1–G7, is J4's result.

#### J4.2 The structural predicates I committed to blind — ALL FOUR CONFIRMED

| Predicate (committed in Part A) | Record | Verdict |
|---|---|---|
| **P-a** `feasibility_fraction = feasible_tuples / 10⁴` | `feasible_tuples: 20`, `feasibility_fraction: 0.002`; and 20/10⁴ = 1/500 = 0.002 exactly. I also counted **distinct `b_index` among the 28 found = 20**, matching `feasible_tuples` independently. | **confirmed** |
| **P-b** univariate quadratic ⇒ ≤ 2 roots/tuple ⇒ N₆ ≤ 2 × feasible; **and ≥ 8 tuples must contribute two** | 28 ≤ 40 ✔. Instances-per-tuple distribution: **12 tuples × 1 instance, 8 tuples × 2 instances**. My blind prediction was "at least 8"; the record says **exactly 8**. | **confirmed, exactly** |
| **P-c** cumulativity | 15 ≤ 22 ≤ 28 ✔ | **confirmed** |
| **P-d** HEUR-1 predicts ×100 per decade at n = 6 | measured 22/15 = 1.467 and 28/22 = 1.273; implied exponents 0.166 and 0.105 (overall 10²→10⁴: 1.867, exponent 0.135) against the pre-registered **+2**. From 15 at H = 10², exponent +2 predicts 1 500 at 10³ and 150 000 at 10⁴. | **arithmetic confirmed**; the comparison the contract's `tail_checks` requires is **not reported anywhere** (J1-D6). I assert nothing about HEUR-1 — that is not my joint. |

The P-b match is the single quantitative agreement in this joint, and it is real blind evidence: it was
written down before the record was opened and it landed exactly. It establishes that the instance ledger
is internally coherent with the contract's own "single univariate quadratic" engine description. It does
**not** establish the value 28.

#### J4.3 What I recomputed from the producer's own output (NOT blind, and labelled as such)

I recomputed `counts_per_H` from each run's `found` list as the cumulative count of instances with
`r_height ≤ H`, obtaining `{100: 15, 1000: 22, 10000: 28}` for **both** R3 and R4. This is a
**recomputation from the producer's raw output**, not an independent derivation. It proves the record is
internally consistent — a real and useful check, and the one that settles IV-2 — and it is precisely the
check that `AGENTS.md` "Review architecture" says cannot see a wrong-but-self-consistent implementation.
I flag it as such rather than letting it read as blind agreement.

#### J4.4 The finding, restated

The frozen contract does not define `g`, the ellipticity condition, the square pattern's enumeration, the
height-H box, "certified rank above the trivial", "twist class populated", or the distinct-minimal-model
dedup key (Part A, G1–G7), and it does not fix the RNG call sequence (J4.1). **The primary metric of this
experiment is reproducible only from `source/`** — the one artifact a blind re-derivation exists to route
around. Any future reader who wants to check 28 must either read the producer's code, in which case the
check reproduces whatever that code does, or re-specify the contract. The remedy is an additive
specification amendment writing the family, the condition, the box, the dedup key and the RNG order down
explicitly; it is not a repair of any run.

---

## The frozen priors — where I confirm, refine, and OVERTURN

Both priors were recorded before any reviewer ran; overturning one is the most valuable thing this task
can produce, and I say plainly where I do.

| Prior | My finding |
|---|---|
| **(8) "I expect J4 to REPRODUCE 15, 22, 28 and 0.002 from the contract statement alone"** — flagged as "the one I would most like overturned" | **OVERTURNED.** No such reproduction is possible. Seven definitional gaps (G1–G7) plus an unfixed RNG call order mean the contract does not determine the quantity. 375 sampling conventions fail to reproduce even the b-tuple stream. What survives is *not* a re-derivation of 28 but four structural predicates, all confirmed, one (P-b) exactly. |
| **(1) "one provenance defect … `resolved_model_id: cursor-grok-4.6`, `model_verified: false`, `fallback_used: true`, `git_dirty_at_runs: true`"** | **PARTIALLY OVERTURNED.** (i) `fallback_used: true` is **contract-permitted**: `ledger/handoffs/TASK-20260907-2a3331.yaml` sets `fallback_allowed: true`, and a reason is recorded ("native Cursor cloud-agent session; adapter doctor unconfigured"), with `degraded_requirements: []`. That is compliance, not a defect. (ii) `git_dirty_at_runs: true` resolves to `code.dirty_files` = **two untracked output directories only** (`…/claims/`, `…/runs/`); **no tracked source file was uncommitted**, and all eight `source/*.py` digests match `code.source_sha256`. What actually remains is **`model_verified: false` alone** — an unprobed identifier, a genuine provenance gap and never a defect in the mathematics. |
| **(2) "iv2_counts_identical false … my prior is the producer explanation is CORRECT — and this is the place I most expect to be wrong"** | **CONFIRMED, and confirmed independently.** Not by accepting the note: by recomputing `counts_per_H` from each `found` list and finding the two runs deep-equal on every shared key. There is no divergence, so IV-2's three objects (instance list, counts, op ledger) all reproduce. The *mechanism* (int- vs str-keyed dicts) remains **unverified** — it lives in `blind_from`. |
| **(3) "ops_cap_respected as the EXACT boolean, false for R5 alone; R5's found 0 INERT in both directions"** | **CONFIRMED, 8/8.** Every recorded boolean equals `counted_ops < 1.0e8` with no band; R5 alone is false at 100 002 120; the stop is recorded as `exhaustion {counted_ops_cap, b_index 666}` of 10 000 and never as a result. **New defect the prior did not anticipate: R5 is missing 9 of its 10 required 1e7-cadence checkpoints, and this is not disclosed under PD-1/2/3.** |
| **(4) "IV-1 IS WHERE I EXPECT THIS ROUND TO BREAK … my prior is that IV-1 as frozen is NOT satisfied"** | **CONFIRMED on the bottom line, REFINED in three ways the prior did not have.** (i) The n = 6 branch is **NOT EVALUATED**, not "failed" — no certified total exists to compare with 5, and that distinction changes what a repair must produce. (ii) Alternative (a) — "degeneration is the control behaving correctly" — is **refuted from the frozen text**, which names 5 as the expected n = 6 total in three separate places. (iii) **Every n = 8 deviation is downward**, so the `proves_too_much` failure signature (a) is **not** triggered; the certifier is a documented lower bound and under-certification is its conservative failure mode. |
| **(9) "wall_seconds_monotonic and wall_seconds_timestamp_span are identical to six decimal places in every one of the eight runs"** | **FACTUALLY CORRECTED.** They differ by 1e-6 in **R4** (18.257394 vs 18.257395) and **R5** (75.686747 vs 75.686748); identical in the other six. The prior's inference (one instrument reported twice) is J6's to make; its premise as stated is not exact. |
| **Second prior (17:42:52Z), IV-3 / R8** | **CONFIRMED and sharpened.** IV-3 was **NOT EVALUATED**: 0 of 9 plants built, `recovered: []`, `decade_ratios: {}`, `log_log_slope: null`, and the frozen exponent window is recorded but never applied. Additions: all nine plants carry the **identical** pattern `[1,1,1,1,1,1]` — the all-ones known-false family — over nine **distinct** b-tuples; and `iv9_distinct_h0: true` is a **boolean over an empty set**, since every `h0` is `null`. |
| **(10) "what would overturn the prior as a whole: the R3 28 produced by a code path the controls never traverse"** | **NOT EVALUATED BY ME, BY CONSTRUCTION.** Deciding whether `degenerate_deg_s_2` lies on the same code path as the counted R3 path requires `source/`, which is my `blind_from` and is J5's. I record only the record-level facts that bear on it: the same `degenerate_deg_s_2` string rejects all eight R7 n = 6 tuples and all nine R8 plants, and does not appear in R3 (whose `near_miss_ledger` is `[]` with `near_miss_total: 0`). |

---

## Limitations — what I could not verify, and why

1. **The producer implementation.** `source/**` and `implementation.md` are the plan's `blind_from`; I
   never opened them. Consequences: I cannot verify the stated `iv2` mechanism, cannot verify that
   `source/null_family.py` contains the R6 infeasibility proof, cannot verify PD-3's `min(H, 20)` box
   claim, and cannot answer whether the control rejection path and the counted path coincide (prior 10).
   All four are J5/J6 territory.
2. **Blindness was implementation-blind, not value-blind.** The mandatory readings — the handoff, which
   embeds the frozen plan, and the 17:42:52Z prior — both quote 15/22/28, `feasible_tuples 20` and
   `feasibility_fraction 0.002` before any reviewer can begin. Part A discloses this up front. It weakens
   J4's agreement evidence and it is a defect in the plan's design, not the producer's.
3. **`near_miss_ledger` is empty in R3, R5 and R6** with `near_miss_total: 0`, while the contract requires
   "the near-miss ledger (tuples with 0 solutions, recorded with the failing condition)" — 9 980 tuples at
   n = 6 had no in-box solution. Whether the ledger is required to enumerate them or only to exist is not
   pinned by the contract text; I record the fact and decline the verdict.
4. **`model_verified: false`, `degraded_requirements: []`.** No `adapter doctor --probe` receipt exists in
   the package, so I can neither confirm nor refute that no policy requirement was missed. **NOT EVALUATED.**
5. **Attempt completeness (IV-6)** is not evaluable from the record: absence of an `attempt-*` directory
   cannot distinguish "one attempt" from "an unpreserved attempt".
6. **Determinism outside R3/R4** was never exercised — no replay of R1, R2, R5, R6, R7 or R8 exists.
7. **No infrastructure failure occurred in my own work.** No timeout, no crash, no `ENOSPC`. Disk headroom
   at the start was 434 GiB on the worktree volume and ~6.8 GiB on the system volume; all intermediate
   files were kept in `$TMPDIR` and are a few kilobytes.
8. **Incidental sibling exposure — disclosed, not absorbed.** A `git status --porcelain` run at the very
   end, to confirm I had written nothing outside my write scope and committed nothing, listed the working
   tree as untracked noise and thereby surfaced two **file names** under
   `…/tasks/TASK-20260907-46731e/`. Neither file was opened, read, diffed, grepped or inferred from; no
   byte of their contents entered this session; both were absent throughout the analysis and every verdict
   above was fixed before they appeared. `read_sibling_reports` is honestly `false`. I record it anyway
   because a disclosed break costs one review and an undisclosed one silently converts this round's
   independence into correlation with nothing downstream able to detect it — the Coordinator should judge
   the exposure rather than take my word that it was harmless.
9. **The snapshot was re-verified after a concurrent `HEAD` move.** `HEAD` advanced mid-task
   (`51af17ddf…` → `574e0ba0a…`, a bus-message publish). I re-ran the binding checks: the snapshot commit
   is still an ancestor of `HEAD`, `git diff 03c6e3181..HEAD -- experiments/EXP-ECRANK-73275e/` is still
   empty, and all **60 declared path hashes still verify**. The package under review did not move.
10. **Scope.** Every statement above is scoped to n ∈ {6, 8}; nested H ≤ 10⁴ at n = 6 and ≤ 10³ at n = 8;
   the seeded 10⁴ b-tuple sample (of which R5 completed 667); exact stdlib `fractions.Fraction`
   arithmetic; the 1.0e8 counted-op cap; and **toy** claim tier. Nothing here transfers to any
   cryptographic parameter, and no transfer assumption is asserted.

---

## Required `validation_report` block (`agents/validator.md`)

```yaml
validation_report:
  id: VAL-20260907-d47eb0
  task_id: TASK-20260907-d47eb0
  run_ids:
    - RUN-ECRANK-73275e-R1-audit-smoke
    - RUN-ECRANK-73275e-R2-draw-support
    - RUN-ECRANK-73275e-R3-construct-n6
    - RUN-ECRANK-73275e-R4-construct-n6-replay
    - RUN-ECRANK-73275e-R5-construct-n8
    - RUN-ECRANK-73275e-R6-null
    - RUN-ECRANK-73275e-R7-known-false
    - RUN-ECRANK-73275e-R8-planted
  artifact_checks:
    - snapshot path_sha256 60/60 verified; working tree byte-identical to 03c6e3181
    - RUN_REQUIRED_TOP complete in all 8; 5 companions present in all 8; command.txt == code.command 8/8
    - environment.json byte-identical across all 8; source_sha256 8/8 verified without reading source
    - runs/ written by exactly one commit; no amendments/; specification.yaml protocol fields untouched since design
    - MISSING - SR-11 IC-1 exclusion ledger (all runs); R6 in-record infeasibility proof; R3/R5 in-record IV-8 statement; R5 cadence checkpoints (1 of 10); tail_checks decade ratios; per-H feasibility fraction
  metric_recomputations:
    - ops_cap_respected recomputed as counted_ops < 1.0e8 for all 8; matches recorded 8/8; R5 false at 100002120
    - counts_per_H recomputed from found (r_height <= H, cumulative) = {100:15,1000:22,10000:28} for R3 and R4
    - feasibility_fraction 0.002 = 20/10^4 exactly; distinct b_index among found = 20 = feasible_tuples
    - instances-per-tuple = 12 singles + 8 doubles, matching the blind <=2-roots ceiling exactly
    - N_6(H) NOT re-derivable from the frozen contract - the J4 finding
  control_checks:
    - IV-1 NOT SATISFIED (n=6 NOT EVALUATED, n=8 not satisfied, all deviations downward)
    - IV-2 SATISFIED (R3 == R4 on instance list, counts, ops; iv2 flag is a check defect)
    - IV-3 NOT EVALUATED (0 of 9 plants built; recovered 0/0 is an empty denominator)
    - IV-4 conjunct 1 SATISFIED, conjunct 2 NOT SATISFIED in the run record
    - IV-5 SATISFIED at the scope of one b-tuple and 8 draws
    - IV-6 SATISFIED on the ceiling; completeness NOT EVALUABLE
    - IV-7 SATISFIED for R3/R4 and R2; NOT EVALUATED elsewhere
    - IV-8 NOT SATISFIED - frozen consequence is a downgrade to single-class, not a voiding
    - IV-9 SATISFIED for R2 and for R8 (b,pattern); R8 h0 clause NOT EVALUATED (vacuous true)
  heuristic_validation_checks:
    - preregistered_prediction present and dated before any run; not adjusted; no amendments directory
    - HEUR-1 decade comparison required by tail_checks is NOT reported anywhere - measured exponent 0.135 vs predicted +2, stated as arithmetic only, asserting nothing about HEUR-1
    - sample seeds and sizes in the manifests; the sampling PROCEDURE is not reproducible from the contract
    - no correspondence trick is used (specification.yaml correspondence null) - nothing to validate
  cost_model_checks:
    - unit declared - counted exact rational operations, cap 1.0e8, exact boolean, no band
    - memory reported beside time - peak_rss_bytes in all 8; cpu_seconds explicitly null in all 8
    - counted_ops is a LOWER bound - the IC-1 exclusion list SR-11 is never itemized, so the shortfall is unstated
    - no per-attempt-cost x inverse-success-probability table is claimed and none is required at this tier
  proof_architecture_checks:
    - baseline fixture (IV-1, the d=1 closed form) does NOT reproduce - see IV-1
    - nearby-object control (R6 null) returns exactly 0 but its infeasibility flag is unrecorded
    - method ceiling - not this task's joint
  verdict: incomplete
  verdict_note: >-
    Scoped to joints J1-J4 only. incomplete, not failed and not invalid - the
    receipts are intact, schema-complete, seed-faithful, internally consistent
    and honestly op-accounted, and the R3/R4 determinism claim verifies; but
    the primary metric is not independently re-derivable from the frozen
    contract, four required artifacts are absent, IV-1 is not satisfied against
    its frozen text, and IV-3 never evaluated. Nothing here is negative
    mathematical evidence about HEUR-1 or H-ECRANK-36d8d7 (AGENTS.md rule 3).
    The batch disposition is the Coordinator's and is not decided here.
  limitations:
    - blind from source/ and implementation.md - mechanism claims unverifiable
    - blindness was implementation-blind, not value-blind - the plan quotes the target numbers
    - J5, J6, J7 not addressed; no whole-claim verdict returned
  artifact_paths:
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-d47eb0/validation-report.md
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-d47eb0/review_attestation.yaml
```

## Authority statement

No status was changed. Nothing was promoted. No F1–F4 finding was assigned. No raw artifact, run record,
manifest, ledger record or dispatch queue was modified. Nothing was committed. H-ECRANK-36d8d7 remains
`specified`; HEUR-1 is neither supported nor refuted; C1 remains OPEN with the DEC-20260905-7adca0
candidate UNPROMOTED; IMP-2 is untouched. Only the two files under
`coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/TASK-20260907-d47eb0/` were written.
