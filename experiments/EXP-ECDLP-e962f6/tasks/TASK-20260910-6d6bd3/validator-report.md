# Validator Report — EXP-ECDLP-e962f6 Stages 1-2 run package

**Task:** TASK-20260910-6d6bd3 (role: validator)
**Contract:** ledger/handoffs/TASK-20260910-6d6bd3.yaml
**Frozen review plan:** coordination/reviews/e962f6-stages12-20260910/review-plan.yaml
**Frozen experiment contract:** experiments/EXP-ECDLP-e962f6/specification.yaml (v1, approved, frozen)
**Joints assigned to this validator:** J1, J2, J5, J6, J7, J8
**Joints NOT mine (sibling reviewer / red team):** J3, J4
**Inference:** policy review-adversarial, independent session, no fallback, no degradation
**Scope discipline:** observations-only per-joint verdicts (HOLD/BREAK); no hypothesis
status change (H-ECDLP-f2bdd0 stays `specified`); no commit, no push; no Bedrock;
provenance on every citation; no B71/breakthrough language (this is a validator pass,
not a claim tier).

---

## 0. Blindness attestation

I did **not** open, read, or reference `experiments/EXP-ECDLP-e962f6/tasks/
TASK-20260910-2c0931/` or any red-team output. That directory did not exist when I
began; it appeared at 10:11 (a parallel red-team session) and I have not listed,
opened, or read anything inside it. I did not read the red-team handoff
`ledger/handoffs/TASK-20260910-2c0931.yaml` either. The frozen review plan (which
names the J3/J4 joints) is a shared Coordinator-authored document and is part of my
contract; reading it is not reading the red-team's report. My per-joint verdicts below
rest only on the sources listed in §8 (sources_read).

The blind re-derivation in §4 was performed from **exactly two sources** — the
`top_T_share` definition in `specification.yaml` and the `basin_histogram_8W` block of
`RUN-ECDLP-e962f6-002/raw-result.json` — and is blind_from `source/run_anchor.py`,
`source/instrument.py`, RUN-002's `summary.json`/`run-meta.json`/manifests, the
execution report, and the red-team report, per the plan's `blind_rederivation`
statement. (I read the execution report and the implementation for the *other* joints;
the re-derivation value itself was computed from only the two allowed sources and did
not use any of the blind_from material.)

---

## 1. Per-joint verdicts

### J1 — QUADRATURE (RUN-ECDLP-e962f6-001): **HOLD**

Independent re-solve with a deliberately different method (pure bisection, no Newton,
bracket [1e-6, 20], 200 iterations, `math.erfc`) — the producer used "bisection
bracketing (100 iterations, bracket [1e-9, 50]) plus Newton refinement" per the
manifest.

- **Q1 (anchors within 5e-5 at all four a):** my independent roots reproduce the
  committed anchor values to machine precision (max |dev| = 4.4e-16, far inside 5e-5):
  a=1 → x*=0.1903808702719756, C_max=0.6625998114129124; a=1/2 → x*=0.4045307067767451,
  C_max=0.5247586384598776; a=1/4 → x*=0.7423409681771704, C_max=0.3889120129663709;
  a=1/8 → x*=1.2085522833979216, C_max=0.27161902810059757. **PASS.**
- **Q2 (assembly minimum):** on the fine grid a∈[0.05,2] step 0.001 (1951 points), the
  minimum of sqrt(a)/C_max(a) is at **a=0.207** (in [0.2,0.25]) with value
  **1.2829044476506803** (within 0.01 of 1.28; |dev|=0.0029). Matches the committed
  `assembly_minimum` exactly. **PASS.**
- **Q3 (baseline-embedding):** c_rand(a_m=1)=1−3^(−1/2)=0.42264973081037427 (dev from
  0.423 = 3.5e-4 < 5e-3); c_max(a=1)=0.6625998114129124 (dev from 0.66 = 2.6e-3 < 5e-3).
  **PASS.**
- **Consistency (the real risk):** the root equation
  `2 x*^{-1/2} e^{-x*/2} − sqrt(2π) erfc(sqrt(x*/2)) = a sqrt(2π)` and
  `C_max(a)=erfc(sqrt(x*/2))` used by the quadrature (spec `definitions.C_max(a)`,
  RUN-001 manifest `method`) are **identical** to the derivation document's Lemma 5
  statement (`derivation/derivation-lemmas-1-6.md` lines 313-316). No mismatch: the
  reproduced anchors are the right anchors.

No breaking artifact. **J1 = HOLD.**

### J2 — 2^26 ANCHOR + F2 (RUN-ECDLP-e962f6-002): **HOLD**

- **Partition identity (recomputed from the committed histogram, digit-for-digit):**
  sum of basin sizes (from `basin_histogram_8W` sizes×counts) = 67,002,039;
  + capped_mass_8W 5,339 + cycle_mass 101,486 = **67,108,864 = N**. Holds
  digit-for-digit. (The histogram is of distance-capped basin sizes — points within
  8W of each DP; capped_mass = points that reach a DP beyond 8W; cycle_mass = points on
  cycles. n_basins = 262,671 = nDP, so every DP has a nonempty basin.)
- **Seeds / W / theta / cap (as frozen):** walk_key=1, dp_key=101, tie_break=401 (all
  match the frozen seed policy). **W = 256.0**, which equals the contract's own
  definition `W = sqrt(a N / T) = sqrt(0.25·2^26/256) = 256` — **not** the "W = 2048"
  contract text (a documented transcription of the cap, per execution report §7c.1).
  theta = 1/256 = 0.00390625; cap 8W = 2048. nDP = 262,671 ≈ N/256 confirms theta=1/256
  (a W=2048 run would give nDP≈32,768). So the run used W=256 per the definition.
- **F2 trigger correctly identified:** Spearman rho = 0.8242794131641281, p = 0.0,
  significant at alpha = 0.01 — this is the contract-named F2 condition. The
  mean-walk-length alternative (255.284 exact, 0.28% below W=256) is **within** W, so
  it is **not** the trigger. The trigger is the Spearman condition.
- **Spearman population/construction (as the contract names them):** population =
  "points whose forward orbit reaches a DP"; walk length = exact distance array d[x]
  (no cap); basin size = capped-at-8W size of the reached DP; n_pairs = 67,007,378 =
  N − cycle_mass (67,108,864 − 101,486). The construction matches the contract exactly;
  the Spearman was **not** computed on the capped walk length or a different population.

No breaking artifact. **J2 = HOLD.**

### J5 — STAGE 2 RE-READ + D3 (RUN-ECDLP-e962f6-008): **HOLD**

- **Read-only guarantee (sha256 re-verified independently):** I re-verified the sha256
  of every file RUN-008 read against `git show HEAD:<path>` (the committed state) **and**
  the working tree. 17 files total: 16 committed (15× EXP-ECDLP-869870 at N∈{2^20,2^22,
  2^24}×5 seeds; 1× EXP-ECDLP-612fb1-002) + 1 new artifact (RUN-ECDLP-e962f6-002
  summary.json, `sha256_committed: null` by record). **All 17 match**
  (git-HEAD == recorded_at_read == recorded_committed == working-tree). The recorded
  `all_sha256_match_committed_state: true`, `mismatches: []` is correct. No committed
  file was modified; no re-simulation.
- **Corrected residual R(N) (recomputed per (N,seed) from the committed fields):**
  R(N) = (top_T_share + cycle_mass_frac + capped_mass_8W_frac − C_max(a))/C_max(a),
  C_max(1/4)=0.3889120129663709. All 16 cells match RUN-008's committed
  `residual_table` exactly (e.g. 2^20 s1: R=0.1329810970496981; 2^26: R=−0.002695283002235006).
- **Per-N median |R| (recomputed):** 2^20 → 0.028827104662559833; 2^22 →
  0.029048152585375842; 2^24 → 0.023135029249220965; 2^26 → 0.002695283002235006. All
  match the committed `per_N_median_abs_R`.
- **D1 (|R(2^26)| ≤ 0.15):** |R(2^26)| = 0.002695 ≤ 0.15. **PASS.**
- **D2 (per-N median |R| non-increasing up to 2pp floor):** 0.02883→0.02905 (Δ+0.00022,
  within 0.02) →0.02314 (Δ−0.00591) →0.00270 (Δ−0.02044). **PASS.**
- **D3 (log-log slope of per-N median |R| over |R|>0.01 points, in [−0.7,−0.1]):** the
  three points above the 0.01 floor are 2^20 (0.02883), 2^22 (0.02905), 2^24 (0.02314);
  2^26 (0.00270) is below the floor and excluded. I recomputed the slope **both ways**:
  endpoint (2^20→2^24) and least-squares over the three points. For three equally-spaced
  log-N points the two are identical: **slope = −0.07933675494762787**, matching the
  committed −0.07933675494762801 to 1.4e-16. This is **outside** [−0.7,−0.1] (near-flat,
  not the predicted −1/3). **D3 does not pass** — and the fail is robust to the slope
  method. (Note: the plan's prior "least-squares is about −0.024" is not borne out; for
  three equally-spaced points least-squares equals the endpoint slope. This does not
  affect the verdict, which is the same under either method.)
- **Substitution clause:** three points exceed the 0.01 floor, so D3 is **not** replaced
  by D2; the clause was correctly not triggered (`substituted_by_D2: false`).
- **Anchor cross-check (EXP-ECDLP-612fb1-002, N=2^20):** C_max_model =
  0.3889120129663709 and x_star_model = 0.7423409681771704 match the contract's
  a=1/4 anchor values. **Largest |R| cell:** RUN-ECDLP-869870-001-N20-s1 (|R|=0.13298).

No breaking artifact. **J5 = HOLD.**

### J6 — SUPERSESSION INTEGRITY (RUN-007 → RUN-008): **HOLD**

- **RUN-007 is a preserved defective run record (no results, never edited):**
  `raw-result.json` is the placeholder `{"status":"RAW_RESULT_NOT_CAPTURED","no_rerun":true}`
  (added later as an additive disclosure file by repair TASK-20260909-cb6cc7); there is
  **no** `summary.json` or `run-meta.json`. Git history shows each original RUN-007 file
  (`manifest.yaml`, `stderr.log`, `command.txt`, `environment.json`, `stdout.log`) has
  exactly **one** creating commit — the snapshot 09de8800d0 — and I confirmed each is
  **byte-identical** to that commit. The two later commits (022b2a9a79, a10241912f) only
  **added** files (`manifest_v2.yaml`, the `raw-result.json` placeholder); they did not
  edit any original byte. So RUN-007 was never edited in place.
- **The path bug is real:** RUN-007 `stderr.log` shows
  `FileNotFoundError: .../run-e962f6-20260909/experiments/EXP-ECDLP-e962f6/experiments/
  EXP-ECDLP-869870/runs/RUN-ECDLP-869870-001-N20-s1/summary.json` — the committed
  repo-relative path was resolved against the **experiment directory**
  (`experiments/EXP-ECDLP-e962f6`, per the manifest `working_directory`) instead of the
  repo root, doubling the `experiments/` prefix. exit_code 1; manifest records
  `id: null`, `status: unknown`, empty seeds/params.
- **RUN-008 is a complete valid run of the SAME contract Stage 2 spec:** same source
  (`run_reread.py`, the fixed version that resolves the repo root via
  `git rev-parse --show-toplevel`; source_sha256 run_reread.py=28482a86…, runcommon.py=
  bf4f0e10… match the receipt's final state), same corrected-residual definition, same
  N grid [20,22,24,26], same a=0.25, same C_max(1/4). status `completed_valid`,
  exit_code 0, read-only guarantee verified. Its `protocol_deviations` records the
  supersession and routes it to the Coordinator.
- **Run count within budget:** 8 run directories (RUN-001..008) = the contract's 7
  planned runs + 1 spare; the spare is consumed by the RUN-007→RUN-008 re-run. 8 =
  `maximum_runs: 8`. **Within budget.** (Consequently the frozen `maximum_runs` is now
  fully consumed; any further run would require a versioned additive amendment.)

No breaking artifact. **J6 = HOLD.**

### J7 — IMPLEMENTATION FIDELITY: **HOLD** (with one flagged discrepancy, not a break)

- **One code path:** `source/instrument.py` is the single instrument; its docstring
  states "ONE code path for all objects; the object is selected by configuration"
  (walk object: random function | permutation; distinguishing rule: uniform | non-uniform
  {0,2theta}). All Stage 1 drivers (`run_anchor.py`, `run_permutation.py`,
  `run_nonuniform.py`, `run_quadrature.py`) import the same `instrument`; the Stage 2
  verifier (`run_reread.py`) imports only `runcommon`. No separate hidden code path.
- **Producer/verifier blind separation:** I traced `run_reread.py`'s state flow. It
  reads **only** committed `summary.json` files (each hash-verified against
  `git show HEAD:<path>`) plus the new anchor's `summary.json`. It does **not** import or
  call any `instrument` function (no `build_map`, `exact_first_dp`, `basin_sizes_*`),
  and it never touches the producer's in-memory arrays (f, isdp, p, d, reach) — those are
  not persisted. There is **no shared producer/verifier state path**. The verifier is
  blind to producer state; it re-derives everything from the committed, hash-verified
  summaries.
- **W per definition (recomputed on the fixed parameters, compared to recorded):**
  `cell_params` computes `W = math.sqrt(a*N/T)` (the contract's authoritative definition).
  Recorded W matches the definition for every run: RUN-002 (N=2^26,T=256,a=1/4) → W=256.0
  ✓; RUN-003/004/005 and RUN-006 (N=2^20,T=64,a=1/4) → W=64.0 ✓ (theta=1/W, cap8=8W all
  consistent). No W value deviates from the definition.
- **Flagged discrepancy — "stdlib-only" / "any non-stdlib import":** the implementation
  imports **numpy** and **scipy** (non-stdlib). Read literally, the J7 breaking artifact
  ("any non-stdlib import") is present. **However**, this is a discrepancy between the
  joint's phrasing and the frozen contract, not a fidelity defect in the run package:
  the frozen contract **declares and records** numpy and scipy as dependencies
  (`environment.json` records `numpy_version: 2.4.4`, `scipy_version: 1.18.0`; the
  `budget_note` says "single process, numpy vectorised"; `required_artifacts` requires
  recording "environment and **dependency versions**"), and it requires **only erfc** to
  come from the standard library ("erfc from the standard library function named in the
  manifest" — satisfied: `math.erfc`). The usage is deterministic and version-pinned, and
  the critical quadrature fixture (RUN-001, the baseline every other number is compared
  against) is **pure stdlib** (`run_quadrature.py` imports numpy but never uses it). So the
  underlying fidelity intent — no hidden/undeclared dependencies, reproducible from
  declared ones — is satisfied. I flag the "stdlib-only" phrasing for the Coordinator to
  reconcile with the contract's declared dependencies; I do not treat it as a break of the
  run package.

Substantive fidelity checks (one code path, blind separation, W per definition) all pass.
**J7 = HOLD**, with the stdlib-only phrasing discrepancy noted as a finding.

### J8 — GATE CONFORMANCE: **HOLD**

- **Gate vs S3 are separate constructs in the frozen contract.** The execution/completion
  gate (execution report §9) is about **protocol conformance**: (1) stopping rules met,
  (2) every required artifact present, (3) RUN-001 anchor reproduction reported first +
  RUN-008 read-only guarantee verified + decay checks D1-D3 **stated with verdicts**,
  (4) control verdicts stated per control, (5) infrastructure failures recorded, no
  protocol edit, no status language, runs immutable. S3 is a **success criterion**
  (spec `success_criterion`: "the residual decays as N^{-1/3} per checks D2 and D3").
  Item 3 requires the decay checks to be *stated with verdicts*, **not** to *pass* — so a
  D3 fail is a stated verdict that satisfies the gate item while failing S3.
- **The D3 fail is recorded as a scoped negative, not a gate failure.** Execution report
  §9.3: "decay checks D1-D3 stated with verdicts: yes … D1 PASS, D2 PASS, D3 does not
  pass (slope -0.0793 outside [-0.7, -0.1])"; §10 lists "D3 does not pass … This bears on
  success criterion S3" as an observation "recorded, not interpreted," with "The
  Coordinator decides after independent review. No conclusion is drawn here." The
  completion gate is "MET for Stages 1-2" on protocol conformance; S3 is separately not
  met. No conflation.
- **No status transition cites the execution gate as evidence for S3.** H-ECDLP-f2bdd0
  remains `status: specified` (no transition occurred). I searched the ledger for any
  record conflating the completion/execution gate with success or citing it as evidence
  for S3: the only e962f6 Stages-1-2 decision (DEC-20260909-57441e, the RUN-007
  supersession repair) states "no science, no re-scoring, no status change." No DEC/EV
  record promotes a claim or moves a status on the strength of the execution gate.

No breaking artifact. **J8 = HOLD.**

---

## 2. Verdict summary

| Joint | Subject | Verdict | Breaking artifact |
|-------|---------|---------|-------------------|
| J1 | Quadrature (RUN-001) | **HOLD** | none |
| J2 | 2^26 anchor + F2 (RUN-002) | **HOLD** | none |
| J5 | Stage 2 re-read + D3 (RUN-008) | **HOLD** | none |
| J6 | Supersession integrity (RUN-007→008) | **HOLD** | none |
| J7 | Implementation fidelity | **HOLD** | none (stdlib-only phrasing flagged as a discrepancy, not a break) |
| J8 | Gate conformance | **HOLD** | none |

**Validator-clean confirm:** on my six joints (J1, J2, J5, J6, J7, J8), the Stages 1-2
run package is a valid, complete, internally consistent receipt of the frozen
verification protocol. All hash bindings verify, all recomputed quantities match the
committed records, the read-only guarantee holds, the supersession is clean and within
`maximum_runs`, and the execution gate is correctly separated from the (not-met) S3.
This is a verification-protocol result; it does not make the derivation artifact
citable (Stage 0 remains a separate reserved audit) and does not change
H-ECDLP-f2bdd0 (stays `specified`).

**Findings routed to the Coordinator (not breaks):**
1. **J7 "stdlib-only" phrasing** conflicts with the frozen contract's declared
   numpy/scipy dependencies (see J7). Reconcile the joint statement with the contract.
2. **Contract-text arithmetic inconsistencies** (already recorded by the Executor in
   execution report §7c, not edited by me): (a) the anchor "W = 2048" text vs the
   definition W=256 (the run correctly used 256); (b) the permutation "3 T W/N =
   0.046875" frozen threshold vs the arithmetically-correct 0.01171875 (the frozen
   value governs the C2 verdict; the corrected value is reported as secondary). These
   are the J3 red-team territory; I note them only because J2's W check touches (a).
3. **D3 slope method note:** for three equally-spaced log-N points the endpoint and
   least-squares slopes are identical (−0.07934); the plan's prior "least-squares ≈
   −0.024" is not borne out. The D3 fail is robust either way.

---

## 3. Hash re-verification of the 73 receipt-bound paths

Receipt: `experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-2989a0/snapshot-receipt.json`
(task TASK-20260909-b95f26, `n_paths: 73`, `parent_sha: e5859ae9bb49a7e5a6591d13b298977e4fe33429`).

I recomputed the sha256 of all **73** bound paths and compared against the receipt, in
**both** the working tree and the snapshot commit:

- **Snapshot commit:** 09de8800d05b04d66890acd26b0dae67e74f1361 ("runs: EXP-ECDLP-e962f6
  Stages 1-2 package TASK-20260909-2989a0 (snapshot TASK-20260909-b95f26)"), whose parent
  is e5859ae9bb… (matches the receipt `parent_sha`) and which is **reachable from HEAD**.
- **Result: 73/73 match in the working tree; 73/73 match in the snapshot commit.**
  0 mismatches, 0 missing.

The 73 paths cover: `amendments/.gitkeep`, `derivation/derivation-lemmas-1-6.md`,
`runs/.gitkeep`, all 8 run directories' `command.txt`/`environment.json`/`manifest.yaml`/
`raw-result.json`/`run-meta.json`/`stdout.log`/`stderr.log`/`summary.json` (RUN-007 has no
`raw-result.json`/`run-meta.json`/`summary.json` in the receipt — it is the preserved
defective no-result run), the 7 `source/*.py` files, `specification.yaml`, and the
execution report. (The `manifest_v2.yaml` files are **not** in this receipt; they were
added later by the additive supersession repair TASK-20260909-ba7fcb and are pinned in
`tools/run_supersession_registry.yaml` instead.)

**Hash re-verification: PASS (73/73).**

---

## 4. Blind re-derivation of the 2^26 top-T share

**Sources used (exactly two, per the plan):**
1. `specification.yaml` → `definitions.top_T_share`: "sum of the T largest exact basin
   sizes divided by N (cap 8W)"; and `inputs.anchor_enumeration` → N = 2^26, T = 256.
2. `RUN-ECDLP-e962f6-002/raw-result.json` → the `basin_histogram_8W` block
   (`sizes`, `counts`; 5,064 size classes, 262,671 basins, total_mass 67,002,039).

**Blind_from (not used for this value):** `source/run_anchor.py`, `source/instrument.py`,
RUN-002 `summary.json`/`run-meta.json`/manifests, the execution report, the red-team report.

**Derivation:** take the T = 256 largest basin sizes from the histogram (descending),
sum them, divide by N = 2^26 = 67,108,864:

- sum of the 256 largest basin sizes = **25,922,273**
- top_T_share = 25,922,273 / 67,108,864 = **0.38627196848392487**

**Committed value** (`top_T_share_8W` in the same raw-result.json): **0.38627196848392487**.

**Result: exact match (abs diff 0.0).** Cross-check: the sum of the first 256 entries of
the histogram's own `top1000` list is also 25,922,273, confirming the reconstruction.

---

## 5. Resource usage

- **Wall clock:** well under the 1800 s budget (all work was local Python recomputation
  and git hash checks, each seconds-scale; total active compute on the order of a few
  minutes including the 1951-point quadrature grid).
- **Memory:** well under the 2 GB budget (largest transient was the 5,064-class histogram
  and 1,951-point grid; no large arrays allocated).
- **Runs executed: 0** (per `maximum_runs: 0` for this validator task). No experiment was
  run; all checks were recomputation against committed artifacts.
- **No Bedrock** (core rule 16): no provider/backend/endpoint/model containing "bedrock"
  was selected or contacted.
- **Writes:** only under `experiments/EXP-ECDLP-e962f6/tasks/TASK-20260910-6d6bd3/`
  (this report + `work/` helper scripts and JSON). Nothing written outside the declared
  write scope. No commit, no push.

---

## 6. Provenance of citations

All citations in this report are **internal** (committed artifacts of this repository,
read directly in this session): `specification.yaml`, the run records
(`runs/RUN-ECDLP-e962f6-00{1,2,7,8}/…`), `source/*.py`,
`derivation/derivation-lemmas-1-6.md`, the snapshot receipt, the execution report,
`tools/run_supersession_registry.yaml`, `ledger/hypotheses/H-ECDLP-f2bdd0.yaml`,
`ledger/decisions/DEC-20260909-57441e.yaml`, and the frozen review plan. No `recalled`
or external `retrieved`/`kb` references are used to support any verdict. The committed
EXP-ECDLP-869870 / EXP-ECDLP-612fb1 summary values are cited as **internal** committed
measurements (read-only), not as independent literature.

---

## 7. What this report does NOT do

- No whole-claim verdict (I report only on my six joints; J3/J4 are the sibling
  reviewer's / red team's).
- No hypothesis status change (H-ECDLP-f2bdd0 stays `specified`; only the Coordinator
  may change official status).
- No Stage 0 audit (that is a separate reserved validator task; the ceiling is not
  citable until it completes).
- No commit, no push, no write outside the declared scope.

---

## 8. sources_read attestation

Exact paths opened/read in this session (all under the worktree
`/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910`):

**Contract / plan / registry**
- ledger/handoffs/TASK-20260910-6d6bd3.yaml (my handoff)
- coordination/reviews/e962f6-stages12-20260910/review-plan.yaml (frozen plan)
- experiments/EXP-ECDLP-e962f6/specification.yaml (frozen contract)
- tools/run_supersession_registry.yaml

**Receipt / execution report**
- experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-2989a0/snapshot-receipt.json
- experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-2989a0/execution-report.md

**Run records (e962f6)**
- runs/RUN-ECDLP-e962f6-001/{manifest.yaml, summary.json, raw-result.json}
- runs/RUN-ECDLP-e962f6-002/raw-result.json
- runs/RUN-ECDLP-e962f6-007/{manifest.yaml, raw-result.json, stderr.log, command.txt}
- runs/RUN-ECDLP-e962f6-008/{manifest.yaml, raw-result.json}
  (all under experiments/EXP-ECDLP-e962f6/)

**Source (implementation fidelity, J7)**
- experiments/EXP-ECDLP-e962f6/source/instrument.py
- experiments/EXP-ECDLP-e962f6/source/run_reread.py
- experiments/EXP-ECDLP-e962f6/source/{run_anchor.py, run_nonuniform.py,
  run_permutation.py, run_quadrature.py, runcommon.py} (import lines only, via grep)

**Derivation (J1 consistency)**
- experiments/EXP-ECDLP-e962f6/derivation/derivation-lemmas-1-6.md (Lemmas 4-5 region)

**Committed re-read sources (J5, read-only, hash-verified)**
- experiments/EXP-ECDLP-869870/runs/RUN-ECDLP-869870-{001..005}-N20-s{1..5}/summary.json
- experiments/EXP-ECDLP-869870/runs/RUN-ECDLP-869870-{006..010}-N22-s{1..5}/summary.json
- experiments/EXP-ECDLP-869870/runs/RUN-ECDLP-869870-{011..015}-N24-s{1..5}/summary.json
- experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-002/summary.json

**Ledger (J8 gate-conformance search)**
- ledger/hypotheses/H-ECDLP-f2bdd0.yaml (status)
- ledger/decisions/DEC-20260909-57441e.yaml
- (grep over ledger/ for "completion gate"/"S3"/"D3"/"0.0793" — filenames + matching lines only)

**NOT read (blindness):** experiments/EXP-ECDLP-e962f6/tasks/TASK-20260910-2c0931/
(red-team report directory — not opened, not listed beyond confirming existence, nothing
inside read) and ledger/handoffs/TASK-20260910-2c0931.yaml (red-team handoff).
