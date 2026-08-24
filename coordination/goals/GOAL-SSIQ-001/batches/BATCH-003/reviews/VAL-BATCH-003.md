# VAL-BATCH-003 — Validator review of GOAL-SSIQ-001 BATCH-003 (EXP-SSIQ-58b642, RUN-SSIQ-58b642-a, VOID)

**Task:** `TASK-20260805-2c086d` · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-003`
**Role:** validator · **Verifies artifact integrity, controls, and metric recomputation; does
not decide what the evidence means for `H-SSIQ-18dc91`.**

**Snapshot validated:** commit `3c117cbc` (declared parent `f5244c18`), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/archives/TASK-20260805-fdd699-receipt.yaml`.
Read in full before acting: `AGENTS.md`, `docs/claims-and-verification.md`,
`ledger/hypotheses/H-SSIQ-18dc91.yaml`, `experiments/EXP-SSIQ-58b642/specification.yaml`,
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/RT-PREFREEZE-EXP-SSIQ-58b642.md`,
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/tasks/PF5-research/pf5_degenerate_vertex_convention.md`,
and (after writing my own findings) `RT-BATCH-003.md`, the Red Team's parallel review, to
check for convergence/contradiction without adopting its conclusions uncritically.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md, "Model policy
    note"); this session runs model: inherit. Ran `python3 -m orchestration.adapter doctor
    --probe` directly (see below): every credentialed backend (anthropic, fireworks,
    fireworks-anthropic, openai, openrouter, zai, zai-anthropic) is unusable in this
    environment (no API key set) and the local backend's model-listing probe fails
    (connection refused) -- so no backend in this harness can be probe-verified from inside
    this session, not just this one.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Every other agent in this batch
    (Executor, PF-5 researcher, RT-PREFREEZE, RT-BATCH-003) self-reports resolved_model_id
    claude-sonnet-5 under the identical model:-inherit fallback; this session reports the
    same identifier through the same mechanism. I have no tooling in this environment that
    can establish I am a genuinely different model from the ones that produced or reviewed
    this contract -- doctor --probe could not verify ANY backend, including whichever one is
    actually serving this session, so even same-vs-different is asserted, not measured.
    Nothing below should be read as corroboration from an independently-resolved model; per
    AGENTS.md's suspended-quorum note, this is exactly the situation that rule anticipates.
```

---

## 1. Receipt verdict: PASS (content-verified)

Recomputed every `path_sha256` in the receipt against the git blobs at `3c117cbc` directly
(`git show 3c117cbc:<path> | sha256sum`, bypassing the working tree entirely) — all 11
declared artifact hashes match exactly. `git show --name-status 3c117cbc` lists exactly the
12 declared paths (11 artifacts + the receipt itself), all as `A` (added), matching
`declared_paths` with no extra or missing files. `git rev-parse 3c117cbc^` returns
`f5244c18583255186fd0fc30dc7c73645d86607a`, matching the receipt's declared `parent_sha`
exactly. `git merge-base --is-ancestor 3c117cbc HEAD` confirms reachability from `HEAD`.

## 2. Contract-freeze verdict: PASS

`git log --oneline -- experiments/EXP-SSIQ-58b642/specification.yaml` shows three commits:
draft (`c3a94f56`) → six-fixes-applied (`f06d7350`) → freeze (`f5244c18`, message states
`frozen_at: 2026-08-05`, all seven PF findings resolved). `git diff f5244c18 HEAD --
experiments/EXP-SSIQ-58b642/specification.yaml` is empty: byte-unchanged since freeze.
Freeze commit timestamp `2026-08-05 06:18:46 +0000`; the run's `manifest.yaml.timing.
started_at` is `2026-08-05T06:50:51Z`, ~32 minutes later — the contract preceded the run.

## 3. Independent C-CAL-GAP re-derivation: PASS, and the reported numbers reproduce bit-for-bit

Two independent checks, not one:

**(a) A from-scratch implementation**, written without importing anything from
`experiments/EXP-SSIQ-58b642/implementation/`: my own OLS-on-logs fit and my own
population-median-with-sentinel function, over the identical N-window (the 12 primes'
`floor(p/12)` sizes), with a **different noise model** (Irwin-Hall-flavoured jitter mixed
with `-ln(U)`, not their `-median*ln(U)/ln2` Exponential construction) and a **different RNG
call structure**, to avoid simply cloning their random stream. Run over 20 independent trial
seeds (not their `20260805`) for each of the three synthetic pairs (`constant_offset c=1`,
`constant_offset c=10`, `saturating_capped`):

| variant | mean recovered gap | sd | pass rate (±0.10 of 0.25) |
|---|---|---|---|
| constant_offset c=1 | 0.2729 | 0.0146 | 20/20 |
| constant_offset c=10 | 0.2761 | 0.0214 | 20/20 |
| saturating_capped | 0.2516 | 0.0202 | 20/20 |

This is a stronger check than matching their single seed: it shows the **estimator design**
(OLS-on-logs + population-median-with-sentinel, exactly as `C-CAL-GAP` specifies) recovers the
known gap robustly across independent draws and an independently-authored noise model, not
that one lucky seed happened to pass.

**(b) Direct re-execution of the producer's actual code.** I ran
`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py` myself (the real
`primary_execution` command from `command.txt`, with a scratch `--wisde-cache-dir` so Phase 0
runs before the WISDE-dependent Phase 1 fails) and captured stdout:

```
constant_offset(c=1)   m_gap=0.272119 abs_error=0.022119 pass=True
constant_offset(c=10)  m_gap=0.258219 abs_error=0.008219 pass=True
saturating_capped      m_gap=0.275418 abs_error=0.025418 pass=True
```

Bit-identical to `raw-result.json`'s `phase0_calibration` block and to `manifest.yaml`'s
reported errors (0.022119, 0.008219, 0.025418). This also reproduced the Phase 1 graph
construction log lines (vertex counts, seed j-invariants, discriminants, timings) exactly, up
to the point where the script needs the (uncached) WISDE files — see §5.

**Conclusion: C-CAL-GAP's PASS is genuine, not asserted.** Both an independently-authored
estimator and the producer's own code, independently executed, recover the pre-registered
0.25 gap within the declared ±0.10 tolerance.

## 4. Independent WISDE-format check: the data gap is REAL

Fetched, myself, via the identical `raw.githubusercontent.com` route (same proxy, TLS never
disabled): `README.md`, `results/results37.sage`, `results/results2437.sage`,
`results/results3889.sage`, `results/results5737.sage`. All five byte counts and SHA-256
hashes match `source_access_log.yaml` exactly (e.g. `results2437.sage`: 9025 bytes,
`55380aeb...`). Inspected content directly:

- `results37.sage` (full file, 231 bytes): two entries, each `i = <k>` / `[<quaternion Z-basis
  in i,j,k>]` / `(N1,N2,N3)`. No numeric j-invariant, no elliptic-curve coefficient, no
  identifier linking an order type to a computed curve, anywhere in the file.
- `README.md`: "`resultsp.sage` contains a list containing a basis for each maximal order of
  the quaternion algebra over QQ ramified at p and infinity as well as the tuple (N1,N2,N3)
  giving the successive minima of the quadratic module R" — confirms the format directly, no
  j-invariant field mentioned.

I went one step further than the producer's own due diligence: I fetched and read
`code/deltacomputation.sage` — the WISDE authors' own script that **generates**
`resultsp.sage` — to check whether the generation pipeline itself ever touches a j-invariant.
It does not: `find_dp`/`find_dp_magma` iterate `CCs = Omag.ConjugacyClasses()` (conjugacy
classes of maximal orders — `i` in the output file is just this loop index) and compute each
order's Gross-lattice Gram matrix via Eisenstein reduction to get `(N1,N2,N3)`. No elliptic
curve, no `j`-invariant, no isogeny is constructed anywhere in this file. This closes the
"is there a route the producer missed inside WISDE's own release" question as far as is
practical without independently implementing the Deuring correspondence: the linkage the
contract's `delta_E_cross_reference` clause assumed simply is not computed by the dataset's
own generating pipeline, so it cannot be recovered by reading harder, only by adding a new
computation the WISDE data itself does not perform.

One gap in my own check: the README also names a `delta_p dictionaries` folder (dictionaries
keyed by **prime**, valued by the prime's max `delta_p`) and I could not fetch its contents —
`api.github.com` returned 403 through the proxy for directory listings (the same route the
producer avoided by using `raw.githubusercontent.com` per-file fetches, which is fine, but I
did not separately try guessing that folder's file names). This does not change the
conclusion: the README's own description ("keys are primes... values are the associated value
of delta_p") is unambiguously an aggregate scalar per prime, not a per-vertex mapping, and is
consistent with `find_dp`'s return value `m` in the code I did read. **Finding, not blocking:**
a future check could fetch this folder explicitly rather than relying on the README's prose
description of it.

**Conclusion: the WISDE data-gap claim is real**, independently confirmed by direct fetch of
5 files plus the generating source code, not merely accepted on the producer's word.

## 5. Graph-construction correctness: independently verified beyond the 2-prime minimum

**Vertex-count formula, all 12 primes** (not just 2): wrote my own primality test and
`p mod 12` / `floor(p/12)` check in Python, independent of any repo code. All 12 primes are
prime, all ≡ 1 (mod 12), and `floor(p/12)` matches the reported `N` exactly for every one —
confirms CGL/De Feo Theorem 47's `epsilon = 0` anchor holds for the full pre-registered set,
not a sample.

**Phi_2 polynomial correctness, independent of the producer's own q-expansion check:** wrote
my own from-scratch verification using **exact rational elliptic-curve arithmetic** (a third,
independent route from both the producer's floating-point q-expansion test and their
root-finding code): for 5 curves `y^2 = x^3 + ax^2 + bx` with 2-torsion point `(0,0)`, computed
the classical 2-isogenous curve `Y^2 = X^3 - 2aX^2 + (a^2-4b)X` and both j-invariants exactly
via `Fraction` arithmetic, then evaluated the producer's stated `Phi_2(X,Y)` coefficients at
the two j-invariants. Result: `Phi_2(j(E), j(E')) = 0` exactly, in all 5 cases. This
independently confirms the nine integer coefficients used in `phi2_coeffs_in_X` are the
genuine classical modular polynomial, not a transcription error the producer's own
q-expansion self-check happened to also miss.

**Direct re-execution of `build_isogeny_graph.py` for the smallest pre-registered prime
(p=2437):** called `seed_j_invariant`, `verify_seed_supersingular`, `build_graph_bfs`,
`degree_sequence_check`, and `independent_edgelist_check` myself. Reproduced exactly:
`seed_j0=689, disc=-8` (matches `stdout.log`); `n_vertices=203` (matches `floor(2437/12)`);
`verify_seed_supersingular` independently confirms trace of Frobenius = 0 by naive point
counting; `degree_sequence_check`: 0 vertices with degree ≠ 3 out of 203; `independent_edgelist_check`:
0 mismatches out of 203 vertices checked. All match `raw-result.json`'s `correctness_gates`
block for p=2437 exactly.

## 6. PD-2 audit: independently reproduced, correctly handled, orthogonal to M-DEGSEQ

Built the p=2437 graph myself (as in §5) and scanned `graph['adjacency']` for vertices whose 3
raw roots are not 3 distinct values. Found exactly 2 (within the reported "0-3 of 203-1800"
range): `v=(749,1684)` with adjacency `[(161,712), (749,753), (749,753)]`, and its mirror
`v=(749,753)` with adjacency `[(161,1725), (749,1684), (749,1684)]`. Verified algebraically
that `(749,753)` is exactly the Frobenius conjugate of `(749,1684)` under `p=2437`
(`-1684 mod 2437 = 753`) — confirming PD-2's specific claim ("a double edge to its own
Frobenius conjugate"), not merely "some repeated root."

**No leak into M-DEGSEQ found.** `degree_sequence_check` counts `len(adjacency[v])`, which is
always 3 by `Phi_2`'s cubic degree regardless of distinctness; the spec's own PF-5-narrowed
text for M-DEGSEQ is "every vertex has degree exactly 3" (plain multiset statement, not
"3 distinct neighbours"), and that is exactly what's checked. PD-2 is a real, correctly
reported anomaly against `degenerate_j_handling`'s stronger "genuine SIMPLE graph" prose (which
the execution report flags as revising a load-bearing claim, per AGENTS.md rule 8), but it does
not corrupt any reported statistic — confirmed by direct re-computation, not by trusting the
producer's own claim that the two are orthogonal.

## 7. VOID classification: a real taxonomy gap, converging with (but distinct from) RT-BATCH-003's GD-6

The frozen `decision_rule_frozen_before_data` enumerates exactly three outcomes:
`DETECTED` (CI excludes 0, positive), `UNRESOLVED-BY-THIS-TEST` (CI includes/below 0), and a
`VOID` **defined narrowly and only** for "Either C-NULL-LABEL or C-CONNECTIVITY fails." This
run's outcome is none of the three: `M-GAP` could not be computed at all, and both of the
controls the contract's own `VOID` branch names (`C-NULL-LABEL`, `C-CONNECTIVITY`) **passed**.
The producer invokes `invalidation_rules`' separate, generic clause ("the contract is found
underspecified on any point that changes M-GAP") to justify the outcome, then reuses the
specific word `VOID` for the `decision.branch` / `decision_rule_branch` field value.

This is defensible in substance — the producer is transparent about the distinction in
`raw-result.json`'s own `decision.reason` text ("This is DISTINCT FROM, and not caused by, a
C-NULL-LABEL or C-CONNECTIVITY failure in the contract's own listed VOID-triggering sense") —
but the label itself is a genuine contract gap: a downstream reader who filters run records by
`decision_branch: VOID` cannot distinguish "signal contaminated by graph/tie-break structure"
(the only case the contract's own decision rule defines `VOID` for) from "no data existed to
test either direction" (what actually happened here), even though these are materially
different epistemic situations — one says something (weakly) about the estimator, the other
says nothing about `delta_E` at all. `execution_report.yaml`'s own internal field
`M_GAP_real_status: BLOCKED` is the more precise term and was available; the top-level decision
label did not use it.

I read `RT-BATCH-003.md` (the parallel Red Team review) after writing the above, per this
task's instruction to check convergence without adopting conclusions uncritically. RT-BATCH-003
independently proposes a new defect **GD-6**, but aimed at a different (earlier) point in the
causal chain: *why* the contract's `delta_E_cross_reference` clause assumed a per-vertex WISDE
linkage without re-reading `EXP-SSIQ-4de240`'s already-committed `M_GRAD` finding that no such
linkage exists. That is a **pre-freeze discoverability** defect. My finding here is narrower and
downstream of theirs: **even granting that the gap was undiscoverable before freeze, the
contract's decision-rule vocabulary itself has no outcome for "M-GAP could not be produced,"
and reusing `VOID` for it risks conflation at the ledger/aggregation level.** These are
complementary, not duplicate, findings, and I recommend the Coordinator address both under one
GD-6 entry: the root cause (RT-BATCH-003's finding) and the taxonomy fix (mine — e.g., a
successor contract template distinguishes `VOID-CONTROL-FAILURE` from
`VOID-DATA-UNAVAILABLE`/`BLOCKED` as distinct decision-rule branches, not one overloaded label).

## 8. Overclaim / premature-closure audit: PASS, no overclaim found

- `receipt`'s `claim_boundary` and `producer_reported_outcome_recorded_verbatim_not_endorsed`
  sections are correctly hedged; the Coordinator's own `interpretation: NOT_PERFORMED` check
  explicitly defers the WISDE-gap and VOID adjudication to this task.
- `manifest.yaml`'s `validity: completed_valid_primary_metric_blocked` and
  `result.metrics.M_GAP_real: null` / `M_GAP_real_status: BLOCKED` accurately reflect that no
  confirmatory result exists; nothing reads as if the real-label test happened.
- Anomaly `A-1` (null-arm sentinel-dominated `gamma_greedy_null`) explicitly states "this arm
  is exploratory only... enters no decision" and separately warns that a **future** real-arm
  attempt should expect the same trapped-fraction risk — correctly forward-looking, not a
  claim about the real arm now.
- "Graph construction... passed C-CONNECTIVITY, M-DEGSEQ, C-EDGELIST... exactly" (commit
  message, receipt, execution_report) is consistently scoped to construction/correctness
  fidelity and never conflated with a claim about a `delta_E`-gradient existing.
- No sentence found, in any of the eleven committed artifacts, asserting or implying the
  real-label descent arm was measured.

## 9. A finding not requested by name but caught by re-execution: `command.txt`'s standalone
   Phase-0 invocation does not reproduce as committed

`command.txt` lists two commands and states both "were actually executed during this run's
development/verification": (1) `python3 experiments/EXP-SSIQ-58b642/implementation/
calibration_synthetic.py` standalone, and (2) the `primary_execution` command
(`descent_hitting_time.py --wisde-cache-dir ... --out ...`), which is what actually produced
`raw-result.json`.

I ran command (1) exactly as written, from the repo root, against the committed code at
`3c117cbc`/`HEAD` (identical, per §2): it raises `ImportError: cannot import name
'ols_loglog_fit' from partially initialized module 'descent_hitting_time' (most likely due to
a circular import)`. Root cause: `descent_hitting_time.py` does `import calibration_synthetic
as cal` at module level (line 83), and `calibration_synthetic.py` does `from
descent_hitting_time import ols_loglog_fit, population_median_with_sentinel` at module level
(line 54) — a genuine circular import. The direction that works is running
`descent_hitting_time.py` as `__main__` (verified: `python3 descent_hitting_time.py --help`
succeeds, and the full `primary_execution` command reproduces `raw-result.json`'s Phase 0
numbers bit-for-bit, per §3b); the reverse direction (`calibration_synthetic.py` as `__main__`)
does not, because Python's module-registration order resolves the cycle differently depending
on which file is `__main__`.

**This does not affect any reported number** — `raw-result.json` was produced by command (2),
which I independently verified works and reproduces exactly. But `command.txt`'s claim that
command (1) "was actually executed" is not reproducible as the code is currently committed,
which is either a stale claim (the import structure changed after that manual check was
supposedly done, with no record of the earlier working version) or an inaccurate one. Per
AGENTS.md rule 9 ("Agents must not fabricate commands, outputs, timings... or successful
runs"), an artifact asserting a command "was actually executed" when it currently fails is a
finding that must be recorded, not silently passed over, even though it is narrow in scope and
does not touch the confirmatory result.

**Resolution:** correct `command.txt` to either (a) remove the false claim that the standalone
invocation was executed, or (b) fix the circular import (e.g., move the shared estimator
functions to a third module both files import from, rather than having the two import each
other) and re-verify the standalone command actually works before re-asserting that it does.

---

## Numbered findings

1. **[Informational, not blocking]** Receipt content-verification: all 11 artifact hashes,
   the parent commit, and the exact declared-path set match git history at `3c117cbc`.
   Resolved by this review; no further action needed.
2. **[Informational, not blocking]** Contract freeze: `specification.yaml` byte-unchanged from
   `f5244c18` (2026-08-05T06:18:46Z) through `HEAD`, preceding the run's start
   (2026-08-05T06:50:51Z). Resolved by this review; no further action needed.
3. **[Informational, not blocking]** C-CAL-GAP: independently re-derived with a from-scratch
   estimator/noise-model and independently re-executed via the producer's actual code;
   both confirm the reported PASS is genuine. Resolved by this review; no further action
   needed.
4. **[Informational, not blocking]** WISDE data-gap: independently confirmed real via direct
   fetch of 5 files (hash-matched) plus the WISDE generating source code
   (`deltacomputation.sage`), which itself never computes a j-invariant. One unchecked
   ancillary route (`delta_p dictionaries` folder) remains, but the README's own description
   rules it out as a per-vertex source; resolves by fetching that folder explicitly in any
   successor task, not required to close this finding.
5. **[Informational, not blocking]** Graph-construction correctness: independently verified
   for all 12 primes (vertex-count formula) and deeply re-executed for p=2437 (seed
   construction, supersingularity, vertex count, degree sequence, edge-list check), plus an
   independent third-route confirmation of the Phi_2 polynomial coefficients. Resolved by this
   review.
6. **[Informational, not blocking]** PD-2: independently reproduced for p=2437 (2 vertices,
   confirmed Frobenius-conjugate mechanism) and confirmed orthogonal to M-DEGSEQ by direct
   re-computation. Resolved by this review.
7. **[MEDIUM — contract taxonomy gap, complements RT-BATCH-003's GD-6]** The frozen
   `decision_rule_frozen_before_data` defines `VOID` only for a `C-NULL-LABEL`/`C-CONNECTIVITY`
   failure; this run's outcome (M-GAP structurally uncomputable, both named controls passing)
   is a fourth, unforeseen category reusing that label via `invalidation_rules`' generic
   underspecification clause. **Resolves when:** the Coordinator records this alongside
   RT-BATCH-003's proposed GD-6 (or as a sibling defect) and a successor contract template
   distinguishes a data-unavailable outcome from a control-failure `VOID` as separate,
   named decision-rule branches.
8. **[MEDIUM — new finding, not previously flagged]** `command.txt`'s claim that the standalone
   `python3 .../calibration_synthetic.py` invocation "was actually executed" does not
   reproduce against the committed code (`ImportError`, circular import between
   `descent_hitting_time.py` and `calibration_synthetic.py`). Does not affect any reported
   metric (the `primary_execution` command that actually produced `raw-result.json`
   independently reproduces bit-for-bit). **Resolves when:** `command.txt` is corrected (remove
   the false claim, or fix the circular import and re-verify) in a follow-up artifact
   correction, per the immutable-record/superseding-record discipline (AGENTS.md rule 4) —
   this validation report does not repair it in place.
9. **[Informational, not blocking]** No overclaim or premature-closure drift found anywhere in
   the eleven committed artifacts; every "graph construction passed" statement is correctly
   scoped away from any claim about a `delta_E`-gradient.

---

## Required output block

```yaml
validation_report:
  id: VAL-BATCH-003
  task_id: TASK-20260805-2c086d
  run_ids: [RUN-SSIQ-58b642-a]
  artifact_checks:
    - {check: receipt_path_sha256, result: PASS, detail: "all 11 declared artifact hashes recomputed from git blobs at 3c117cbc match the receipt exactly"}
    - {check: receipt_commit_reachability, result: PASS, detail: "3c117cbc reachable from HEAD, ancestor confirmed via git merge-base --is-ancestor"}
    - {check: receipt_parent_commit, result: PASS, detail: "git rev-parse 3c117cbc^ == f5244c18583255186fd0fc30dc7c73645d86607a, matches receipt.parent_sha"}
    - {check: receipt_declared_paths_exact, result: PASS, detail: "git show --name-status 3c117cbc lists exactly the 12 declared paths, all status A, no extras/omissions"}
    - {check: contract_freeze_byte_unchanged, result: PASS, detail: "git diff f5244c18 HEAD -- experiments/EXP-SSIQ-58b642/specification.yaml is empty"}
    - {check: contract_precedes_run, result: PASS, detail: "freeze commit 2026-08-05T06:18:46Z precedes manifest.timing.started_at 2026-08-05T06:50:51Z"}
    - {check: required_artifacts_present, result: PASS, detail: "all 11 required_artifacts entries present and parse"}
    - {check: command_txt_standalone_invocation_reproducibility, result: FAIL, detail: "python3 experiments/EXP-SSIQ-58b642/implementation/calibration_synthetic.py, as command.txt claims was executed, raises ImportError (circular import with descent_hitting_time.py) against the committed code at 3c117cbc/HEAD; does not affect any reported metric since raw-result.json was produced by the separately-verified primary_execution command"}
  metric_recomputations:
    - {metric: phase0_calibration.constant_offset_c1, reported: 0.272119, recomputed_via_producer_code: 0.272119, match: bit_identical}
    - {metric: phase0_calibration.constant_offset_c10, reported: 0.258219, recomputed_via_producer_code: 0.258219, match: bit_identical}
    - {metric: phase0_calibration.saturating_capped, reported: 0.275418, recomputed_via_producer_code: 0.275418, match: bit_identical}
    - {metric: phase0_calibration.overall_pass, independent_from_scratch_estimator: "20/20 pass rate on all three variants across 20 independent seeds with a different noise model and RNG structure", conclusion: "estimator design genuinely recovers the pre-registered gap within tolerance, not an artifact of one seed"}
    - {metric: C-CONNECTIVITY.floor_p_over_12_formula, recomputed_independently: "all 12 primes: prime, p mod 12 == 1, floor(p/12) == reported N, exact match"}
    - {metric: phi2_modular_polynomial_coefficients, recomputed_independently: "5 elliptic curves, exact rational arithmetic (Fraction), Velu 2-isogeny, Phi_2(j(E),j(E'))=0 exactly in all 5 cases -- third independent route beyond producer's q-expansion self-check"}
    - {metric: p2437_graph_construction, recomputed_via_producer_code: "seed_j0=689 disc=-8 n_vertices=203 degree_sequence_pass=True edgelist_mismatches=0", match: "bit-identical to raw-result.json correctness_gates for p=2437"}
    - {metric: PD_2_anomaly_p2437, recomputed_independently: "2 vertices with repeated (non-distinct) neighbours, confirmed algebraically to be each other's Frobenius conjugates ((749,1684) <-> (749,753), -1684 mod 2437 = 753)", conclusion: "within reported 0-3 range; multiset degree unaffected (len(adjacency)==3 always); orthogonal to M-DEGSEQ as the spec defines it"}
  control_checks:
    - {control: C-CAL-GAP, result: PASS, method: "independent re-derivation (from-scratch estimator, different noise model, 20 seeds x 3 variants) plus direct re-execution of producer code, both confirm"}
    - {control: C-NULL-LABEL, result: PASS_AS_REPORTED, note: "ran to completion per raw-result.json and stdout.log; not independently re-executed in full (requires WISDE fetch + full graph set), but internally consistent with C-REPRO and with the sentinel-dominance explanation given for seed-invariant gamma_greedy_null"}
    - {control: C-CONNECTIVITY, result: PASS, method: "independently recomputed floor(p/12)+epsilon formula for all 12 primes"}
    - {control: C-DEGSEQ, result: PASS, method: "independently re-executed degree_sequence_check for p=2437"}
    - {control: C-EDGELIST, result: PASS, method: "independently re-executed independent_edgelist_check for p=2437, 0 mismatches"}
    - {control: C-SEED, result: PASS_AS_REPORTED, note: "three declared seeds [20260805, 11, 977] present in manifest.inputs.parameters.seeds and used in null_arm; not independently re-run for all three under full Phase 1"}
    - {control: C-REPRO, result: PASS_AS_REPORTED, note: "reported bit-identical in raw-result.json; consistent with the deterministic pure-Python OLS/median implementation confirmed in C-CAL-GAP re-derivation"}
  heuristic_validation_checks:
    - not_applicable: true
    - reason: >-
        H-SSIQ-18dc91.heuristic_assumptions is empty by design (gradient-existence screen,
        not a proof-oriented or heuristic-conditional claim per proof_search_map's
        not_applicable_reason). No numbered heuristic, Dickman-de-Bruijn-style CDF
        comparison, or Deuring-correspondence-substitution claim is made anywhere in this
        experiment's confirmed scope, so docs/target-result-profile.md's heuristic-validation
        checklist does not apply to this run. C-CAL-GAP is a calibration control (checked
        above under control_checks), not a heuristic-validation record in the profile's sense.
  cost_model_checks:
    - not_applicable: true
    - reason: >-
        No concrete-cost table, no asymptotic-complexity claim, and asymptotic_claim is
        correctly null per the frozen contract and H-SSIQ-18dc91.asymptotic_claim_note. Budget
        bookkeeping was checked as an ordinary resource record instead (wall_clock 37.5s
        against a 7200s cap; memory ulimit 4GiB never hit) -- present and consistent, not a
        cost-model claim requiring per-attempt-cost x inverse-success-probability review.
  proof_architecture_checks:
    - not_applicable: true
    - reason: >-
        H-SSIQ-18dc91.proof_search_map.not_applicable_reason states this is not a
        proof-oriented proposal (docs/inventor-protocol.md section 8 governs complexity-
        reduction proposals, not gradient-existence screens). Checked this reasoning against
        the actual experiment design and found no place a proof-architecture audit would have
        caught something this reasoning missed -- same conclusion RT-PREFREEZE and RT-BATCH-003
        independently reached.
  verdict: passed
  limitations:
    - >-
      "passed" here means the receipt is ADMISSIBLE EVIDENCE that this run happened as
      described, its artifacts are genuine, its controls that could be checked did pass, and
      its VOID outcome is an honest, non-fabricated report of a real, independently-confirmed
      data-availability blocker -- NOT that H-SSIQ-18dc91 is supported, refuted, or that lever
      L4 is resolved in either direction. asymptotic_claim is null and stays null.
    - >-
      CONDITION 1 [finding 7]: the VOID decision label is reused for an outcome the frozen
      contract's decision_rule_frozen_before_data never defines (M-GAP structurally
      uncomputable, with both C-NULL-LABEL and C-CONNECTIVITY passing) -- a taxonomy gap, not
      a fabrication, complementary to RT-BATCH-003's independently-proposed GD-6. Should be
      recorded as a named contract defect and fixed in the decision-rule vocabulary of any
      successor contract before the Coordinator or a future ledger aggregation reads
      "VOID" as uniformly meaning "control failure contaminated the signal."
    - >-
      CONDITION 2 [finding 8]: command.txt's claim that the standalone Phase-0-only invocation
      "was actually executed" does not reproduce against the committed code (circular import).
      Does not affect any reported metric (the actual primary_execution command was
      independently re-run and reproduces bit-for-bit), but is a real artifact-accuracy defect
      under AGENTS.md rule 9 and should be corrected (not repaired in place by this report) in
      a follow-up.
    - >-
      C-NULL-LABEL, C-SEED, and C-REPRO were checked for internal consistency and against
      stdout.log, but NOT independently re-executed end-to-end in this review (doing so
      requires re-fetching all 12 WISDE files and re-running full Phase 1 under all 3 seeds,
      which this review's time budget did not extend to after the deeper checks in findings
      3-6 above); this is a scope limitation of THIS validation pass, not a defect found in
      those controls.
    - >-
      Toy-scale scope: field bit-length up to 15 bits (p=21601), graphs up to 1800 vertices --
      toy tier per docs/claims-and-verification.md's mechanical rule, matching
      H-SSIQ-18dc91.scope_ceiling.claim_tier exactly. Nothing in this validation extends that
      scope.
    - >-
      Model-independence cap: this session self-reports resolved_model_id claude-sonnet-5,
      the same identifier every other agent in this batch reports, under the same
      unverifiable model:-inherit fallback (orchestration.adapter doctor --probe could not
      verify ANY backend in this environment). This review is session-independent only.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/VAL-BATCH-003.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Independent Python re-implementations and direct re-executions: (1) from-scratch
    OLS-on-logs + population-median-with-sentinel estimator with an independently-authored
    noise model, run over 20 seeds x 3 synthetic variants; (2) direct re-execution of the
    producer's calibration_synthetic.py and descent_hitting_time.py (primary_execution
    command) against the committed code; (3) independent primality/mod-12/floor(p/12) check
    for all 12 pre-registered primes; (4) independent exact-rational-arithmetic elliptic-curve
    2-isogeny check of the Phi_2 polynomial coefficients (5 curves); (5) direct re-execution of
    build_isogeny_graph.py's seed construction, supersingularity check, BFS, degree-sequence
    check, and edge-list check for p=2437; (6) direct re-fetch of 5 WISDE files plus the WISDE
    generating source code (deltacomputation.sage) via the identical raw.githubusercontent.com
    route; (7) git-level hash/reachability/diff verification of the snapshot commit and the
    frozen contract's history.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the Coordinator's ledger/archive
    task commits this report; it is not durable until that archive exists. Per write_scope,
    this task modified nothing outside coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/
    reviews/VAL-BATCH-003.md -- no raw artifact, ledger record, or specification.yaml was
    touched.
```
