# Independent Validation Report — EXP-ICINV-fcb497

Role: Validator (`agents/validator.md`). Snapshot validated: **`0e78af07a`** (run
package landed at `ab0c59b4c`). Working tree clean at start of this pass.
This report verifies artifacts; it does not interpret them, and it changes no
status and no raw artifact.

**Plain-English verdict: VALIDATED WITH DEFECTS.**
**Terminal verdict (contract enum): `incomplete`.**

The *measurement* is validated without reservation: every one of the 21
decade–seed medians and every one of the 21 KS statistics recomputes
**bit-exactly** from `per-instance-measurements.json`; both deterministic
streams regenerate exactly across all 21 000 instances; all blocking controls
pass on independent recomputation; the frozen decision rule reproduces from a
clean-room reimplementation, including the dissenting seed. Nothing I found
changes a single number, a terminal state, the evidence strength, or the claim
tier.

The verdict is `incomplete` rather than `passed` for three reasons, in
decreasing severity:

- **V-1** Ten pinned raw byte streams under `runs/*/sources/*.raw` — including
  **both HTTP 403 response bodies**, the only artifacts evidencing the STAGE-0
  retrieval failure — are matched by `.gitignore:26` (`*.raw`) and are
  **not committed**. The frozen contract names `runs/<RUN-ID>/sources/ … every
  retrieved byte stream … IMMUTABLE. BLOCKING for STAGE 0`. My own contract
  forbids accepting a working-tree-only artifact as a durable receipt.
- **V-2** `EV-ICINV-c68f13` **OBS-8** asserts an "exactly characterised" small-`m`
  family. The full per-instance corpus contradicts it: a **second** small-`m`
  family of 54 instances exists that OBS-8 does not mention and that its
  density argument does not cover.
- **V-3** `EV-ICINV-c68f13` **OBS-2** describes a STAGE-0 passage "at byte offset
  1160" that does not exist as a recorded quotation, and attributes to it a
  double `kernel_field` classification that the recorded artifact does not
  support for the square-root-Vélu count.

None of V-1..V-3 is a measurement defect and none invalidates a run. All three
require superseding corrections (never edits) before the evidence is cited.

---

## 1. Metric recomputation — recomputed vs recorded

Recomputed from `per-instance-measurements.json` only (not from
`distributions.json`, not from `decision-rule-evaluation.json`). Median =
`statistics.median` (mean of order statistics 500/501 at n = 1000). Two-sample
KS = sup |F_curve − F_null| over the pooled support, computed by a clean-room
implementation written for this pass.

**Declared tolerance: 0 ULP. All 42 statistics matched at 0 ULP — the maximum
absolute discrepancy over medians was `0.0` and over KS statistics was `0.0`.**

| k | seed | n | median (recomputed) | median (recorded) | KS D (recomp) | KS D (rec) | crit | null median | distinct (d,m) recomp | rec |
|---|------|---|---------------------|-------------------|---------------|------------|------|-------------|----------------------|-----|
| 12 | 20260807 | 1000 | 0.6869344921421261 | 0.6869344921421261 | 0.0870 | 0.0870 | 0.0607 | 0.6877 | 173 | 173 |
| 12 | 20260814 | 1000 | 0.6869344921421261 | 0.6869344921421261 | 0.0660 | 0.0660 | 0.0607 | 0.6877 | 165 | 165 |
| 12 | 11235813 | 1000 | 0.6869344921421261 | 0.6869344921421261 | 0.1010 | 0.1010 | 0.0607 | 0.6965 | 164 | 164 |
| 14 | 20260807 | 1000 | 0.6147614403434642 | 0.6147614403434642 | 0.1210 | 0.1210 | 0.0607 | 0.6437 | 271 | 271 |
| 14 | 20260814 | 1000 | 0.6285549195850053 | 0.6285549195850053 | 0.1100 | 0.1100 | 0.0607 | 0.6695 | 273 | 273 |
| 14 | 11235813 | 1000 | 0.6172130434826564 | 0.6172130434826564 | 0.1040 | 0.1040 | 0.0607 | 0.6599 | 280 | 280 |
| 16 | 20260807 | 1000 | 0.6472644607570641 | 0.6472644607570641 | 0.0720 | 0.0720 | 0.0607 | 0.6667 | 440 | 440 |
| 16 | 20260814 | 1000 | 0.6397846033332105 | 0.6397846033332105 | 0.0950 | 0.0950 | 0.0607 | 0.6434 | 434 | 434 |
| 16 | 11235813 | 1000 | 0.6397846033332105 | 0.6397846033332105 | 0.0830 | 0.0830 | 0.0607 | 0.6552 | 432 | 432 |
| 18 | 20260807 | 1000 | 0.8016265997755164 | 0.8016265997755164 | 0.0320 | 0.0320 | 0.0607 | 0.7949 | 580 | 580 |
| 18 | 20260814 | 1000 | 0.8119548905536386 | 0.8119548905536386 | 0.0320 | 0.0320 | 0.0607 | 0.8075 | 603 | 603 |
| 18 | 11235813 | 1000 | 0.8008181989703216 | 0.8008181989703216 | 0.0370 | 0.0370 | 0.0607 | 0.7974 | 606 | 606 |
| 20 | 20260807 | 1000 | 0.7241138068675823 | 0.7241138068675823 | 0.0810 | 0.0810 | 0.0607 | 0.7409 | 786 | 786 |
| 20 | 20260814 | 1000 | 0.6939740011860049 | 0.6939740011860049 | 0.0710 | 0.0710 | 0.0607 | 0.7173 | 758 | 758 |
| 20 | 11235813 | 1000 | 0.7178319910506832 | 0.7178319910506832 | 0.0550 | 0.0550 | 0.0607 | 0.7202 | 742 | 742 |
| 22 | 20260807 | 1000 | 0.7231507754890125 | 0.7231507754890125 | 0.0610 | 0.0610 | 0.0607 | 0.7314 | 854 | 854 |
| 22 | 20260814 | 1000 | 0.7185248061272704 | 0.7185248061272704 | 0.0540 | 0.0540 | 0.0607 | 0.7297 | 850 | 850 |
| 22 | 11235813 | 1000 | 0.7189593433920110 | 0.7189593433920110 | 0.0590 | 0.0590 | 0.0607 | 0.7291 | 851 | 851 |
| 24 | 20260807 | 1000 | 0.7923947341131429 | 0.7923947341131429 | 0.0440 | 0.0440 | 0.0607 | 0.8023 | 924 | 924 |
| 24 | 20260814 | 1000 | 0.7950378657148436 | 0.7950378657148436 | 0.0370 | 0.0370 | 0.0607 | 0.7970 | 939 | 939 |
| 24 | 11235813 | 1000 | 0.7841518539264043 | 0.7841518539264043 | 0.0340 | 0.0340 | 0.0607 | 0.7906 | 907 | 907 |

Also recomputed and matching exactly:

- `ks_critical = 1.358·sqrt(2/1000) = 0.060731606268894296` — identical.
- `median_d_over_p` at PS-TOY-24 seed 20260807 = `0.8325220046976813` — identical
  to `concrete-cost-table.json`.
- `excluded_curve_fraction` max over all 21 cells = `0.005964214711729622`
  (EV OBS-4 "in [0.000, 0.006]" — correct). `degenerate_fraction` = 0.0 in all 21
  cells — correct.
- Total resources across 13 manifests: **25.12 s wall, 23.88 CPU-s = 0.00663
  CPU-hours, 99.16 MB peak RSS** (EV OBS-11: 25.1 s / 0.007 / 99 MB — correct).
- Memory ratio range over 13 manifests: **[0.6808846761453397,
  1.744368254059974]** (EV OBS-11 "[0.68, 1.74]" — correct); `within_band: true`
  in all 13.

**Contract invalidation rule "raw per-instance records and the reported summary
statistics disagree on recomputation by a reviewer → INVALID" does not fire.**
This closes the exact gap the reviewing Coordinator declared open.

## 2. The derivational claim (handoff item 3) — the most consequential check

`EV-ICINV-c68f13.proof_status_note` and `CONFOUND-1` rest on
`λ = ±round(t/2)`, hence `|λ| ≤ (|t|+1)/2 ≤ √p + 1`, confirmed in the record
against **one** row (k24: u = 455, v = −1, λ = 455, d = 16570188, t = 910).

Tested across the **entire per-instance corpus, all 21 000 instances, all seven
decades, all three seeds**:

| check | result |
|---|---|
| `λ ≡ ±round(t/2) (mod d)` | **21000 / 21000**, 0 failures |
| minimiser has `v ∈ {+1, −1}` (T3) | **21000 / 21000**, 0 failures |
| `min(λ, d−λ) ≤ ⌈(|t|+1)/2⌉` | **21000 / 21000**, 0 failures |
| `min(λ, d−λ) ≤ ⌊√p⌋ + 1` | **21000 / 21000**, 0 failures |
| tightness: max over corpus of `min(λ,d−λ)/(√p+1)` | **0.9970745956678385** |

**CONFOUND-1 is on firm ground and is stronger than the record states.** It
holds universally on the tested corpus, not on one row, and it is near-tight:
the curve-derived λ really does live in a window of size ≈ √p ≈ √d while the
matched null draws uniformly from all of (Z/d)\*. The central inference of the
review is correct. This also means the deficit anomaly (OBS-6) genuinely cannot
be attributed to CM arithmetic on these data, exactly as `KN-OPEN-2c095b` says.

Also recomputed exactly across all 21 000 instances (0 failures each):
`d = u² + uvt + v²p`; `D = t² − 4p`; `#E = p + 1 − t`;
`log_m_over_log_d = log m / log d` to < 1e-12.

## 3. Order arithmetic (handoff item 2)

Independent deep re-verification on a sample of **150 instances per
decade–seed cell = 3150 instances**, drawn uniformly without replacement
(`python3` `random.seed(4242)`), i.e. **15.75× the Executor's 200**. Prime
factorisations of `m` and `null_m` obtained independently via `sympy.factorint`,
not read from the artifacts.

| check | failures |
|---|---|
| `λ^m ≡ 1 (mod d)` | 0 / 3150 |
| `λ^(m/q) ≢ 1 (mod d)` for every prime `q ∣ m` | 0 / 3150 |
| `∏ q^e` over recorded factorisation `= d` | 0 / 3150 |
| `a^m_null ≡ 1 (mod d)` for the null draw | 0 / 3150 |
| `a^(m_null/q) ≢ 1` for every prime `q ∣ m_null` | 0 / 3150 |

The checker was mutation-tested (a deliberately doubled `m` is detected by both
the `pow` and the minimality branch), so the zero-failure result is not a
vacuous pass. EV OBS-4's "200 checked with 0 failures" is corroborated and
superseded upward.

## 4. Seed integrity / determinism (handoff item 7)

Regenerated independently of the harness, from the contract text only:

- **Prime ladder**, recomputed as the largest prime strictly below 2^k with an
  independent primality test: `{12: 4093, 14: 16381, 16: 65521, 18: 262139,
  20: 1048573, 22: 4194301, 24: 16777213}` — **identical** to every recorded
  ladder entry.
- **Curve stream** `a = sha256("{seed}:{p}:a:{i}") mod p`,
  `b = sha256("{seed}:{p}:b:{i}") mod p`: regenerated for **all 21 000
  instances across all 7 decades and all 3 seeds — 0 mismatches.** The k = 24
  stream head reproduces (index 0–5: (10440638, 10814834), (9645167, 11080270),
  (13036499, 12851226), (13802615, 14141681), (5195364, 125717),
  (2508096, 5949833)).
- **Null stream** `a = sha256("{seed}:null:{p}:{i}") mod d`, redrawn as
  `"{seed}:null:{p}:{i}:r{j}"` while `gcd(a,d) > 1`: regenerated for **all
  21 000 draws — 0 mismatches**, including the recorded `null_redraws` counts
  (which range to 23).

The contract's seed-integrity invalidation rule does not fire.

## 5. Controls (independently recomputed)

- **Planted positive control (BLOCKING)** — all 10 frozen `r`. I recomputed
  `d = r²−1`, `r² mod d = 1` and `r mod d ≠ 1` for every row: `m = 2` is correct
  by construction on all ten, `d` spans 8 → 4 295 098 368, and `pow_check`,
  `minimality_check`, `order_verification_ok` are all `true`. **PASS.** Same code
  path as STAGE 3 (`harness.exp_kerfield.multiplicative_order`), as declared.
- **m = 1 nearby-object fixture (BLOCKING)** — 3 curves × 3 ℓ = 9 pairs, `m ∈
  {1, 2}`, eigenvalue case declared *by the eigenvalue computation*, cost
  degenerating to Õ(√ℓ) with the `log2(m)` constant reported rather than
  absorbed. I independently reproduced two eigenvalue rows: curve idx 2
  (p = 4093, t = 106), ℓ = 3: `X² − tX + p ≡ X² − X + 1 (mod 3)` has the double
  root 2 ≡ −1, so λ = 2, `ord_3(2) = 2` ✓; curve idx 13 (t = 41), ℓ = 3:
  `(X−1)²`, λ = 1, m = 1 ✓. **PASS.** The argument does not prove too much.
  The 12 skipped curves are recorded with per-curve shortfall reasons, as the
  contract's substitution rule requires.
- **Matched null, null-first ordering (SR2)** — verified as auditable, as
  claimed. `distributions.json.null_first_ordering.matched_null_sha256` matches
  the sha256 of `matched-null.json` on disk in every stage-3 run, and
  `matched_null_written_at` precedes `ks_computed_at` in all seven
  (k24: 03:27:22.242100 → 03:27:22.244218). `ks_input_source` is
  `"matched-null.json read back from disk"`. *Scope note:* this is a 2 ms
  in-process write-then-read inside one 4.8 s run. It proves the recorded null is
  the one the KS statistic consumed and that no null was redrawn after seeing the
  KS; it does not by itself constitute blinding. The stronger guarantee is that
  the null's design is frozen in the pre-registered contract, which I confirmed.
- **Decay check** — the median profile is non-monotone but rising overall and is
  neither flat nor decreasing to the largest decade at any seed; the artifact
  tell did not fire. `median_rising: true` at 3/3 confirmed from the recomputed
  medians.
- **Null-object requirement (`docs/inventor-protocol.md` §3)** — a null of the
  same shape *on d* was measured and the report states what the measured
  quantity should do as p grows. The observed KS deficit **does** decay
  (k12–k16: 0.066–0.121; k24: 0.034–0.044, sub-critical at 3/3), which is the
  non-artifact-tell direction for a small-d artefact. The record does **not**
  claim the deficit as a signal — it labels it UNRESOLVED and files the missing
  shape-match (support of λ) as `KN-OPEN-2c095b`. That is the correct handling
  and I endorse it.

## 6. STAGE 0 (handoff item 5)

- **Every pinned artifact's sha256 re-verified from the bytes on disk**: all 5
  raw streams and all 3 extracted texts, in **both** stage-0 runs — 8 hashes ×
  2 runs, **all match**, including `byte_length_on_disk`.
- **Every quotation re-verified as an exact byte-substring at its recorded
  offsets**: **31 / 31 in each run, 0 failures**, matching the recorded
  `quotations_failing_byte_verification: []`. (Method note: offsets are **byte**
  offsets into the UTF-8 text; slicing by character index fails on 31/31 because
  of `Vélu`. I verified by bytes.)
- **Verdict file reads `AMBIGUOUS`** in both runs, with
  `claim_tier: literature_secondary_or_ambiguous`, `deciding_passages: []`,
  `determinate_verdict_requires_full_text: true`, `stages_1_to_4_still_run:
  true`. `M8 terminal_state = S0-UNDETERMINED`. Confirmed.
- **403s confirmed pinned as claimed** — both PDF fetches returned HTTP 403 with
  a Cloudflare `"Just a moment..."` interstitial body; sha256
  `51877e91…` (2020/341.pdf) and `07912b4c…` (2020/1109.pdf) match the values in
  `execution-report.yaml` exactly. Both are recorded as
  `protocol_deviations[kind: infrastructure_outcome]` with the explicit note that
  they are never read as a BASE_FIELD verdict (AGENTS rule 5) — correct.
  **But see V-1: these two bodies are not committed.**
- Attribution check present and honest: `Bernstein-De`, `Feo-Leroux-Smith` and
  `Velu` are recorded as **absent** from the retrieved artifact (the landing page
  spells the authors out and uses `Vélu`), reported as an attribution defect
  rather than silently accepted.
- The attribution block is read from the contract at run time and byte-pinned
  (`spec_sha256 60c16fff…`, offsets 7102–7980), satisfying
  CORR-20260807-a24675. Verified.

## 7. Provenance, manifests, scope (ordinary validation)

- `python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-fcb497
  --strict` → **exit 0**, `13 pinned, 0 unpinned, 0 unreadable, of 13`.
  `code.source.all_pinned: true` in all 13 manifests. Confirmed.
- All six imported source files' sha256 in the manifests **match the current
  on-disk files exactly** (`harness/{__init__,exp_kerfield,run_kerfield,runner,
  toycurve,velu_stage0}.py`). The three new modules were `untracked` at run time
  and are now tracked; the hashes carried the run across that transition, which
  is what CORR-20260807-911ef7 exists to do.
- **Edit prohibition honoured.** None of `harness/exp_icinv.py`,
  `exp_icinv_fullgroup.py`, `run_fullgroup.py`, `run_saturation.py`,
  `isogeny_class.py` appears in `ab0c59b4c` or `0e78af07a`; their last-touching
  commits are `c9c272216` / `9591caac6`, both earlier.
- Recorded commit `7128debb044389a50ac1bf1a029e74e4bcbb37fb` is a real object and
  an **ancestor of HEAD**.
- **Run count and schema vs contract**: 13 run directories; all required
  artifacts present per stage; `status: completed_valid` in all 13;
  `result.certificate.kind: none`, `verified: true`, `verifier: no-claim` in all
  13.
- **`certificate.kind: none` is right.** I confirmed no run claims a discrete-log
  solve or a factor-base relation; the runs compute curve orders, norm-form
  minima, factorisations and multiplicative orders only. Under
  `docs/claims-and-verification.md` no solution certificate is owed.
- **Claim tier not exceeded.** No artifact asserts above `toy`; the four modeled
  cost rows each carry `conditional_on: ["STAGE-0 verdict KERNEL_FIELD (NOT
  ESTABLISHED: actual verdict AMBIGUOUS)", "HEUR-ORD-1"]`, and
  `affected_vs_safe_scope.affected_constructions` is empty. `sota_delta: 0.0`
  with a populated `dominated_by` — Pareto honesty satisfied.
- **Barrier-table quotations re-verified independently**: all **177** rows
  (175 + 2 required) have their `quoted_charged_cost` re-checked as an exact
  byte-substring of the cited artifact at the recorded
  `quotation_byte_start`/`_end`. **177 / 177 verified, 0 failures.** Nineteen
  rows cite `ledger/hypotheses/H-ICINV-82ee6a.yaml`, whose *current* sha256
  differs from the pinned one because the later ledger commit `0e78af07a`
  updated that hypothesis; those 19 verify against the blob at the run commit
  `ab0c59b4c`. This is ordinary, legitimate post-run drift, not a defect.
- `row_count: 177` vs `len(rows) == 175` is **internally consistent**, not an
  error: the two contract-required rows are stored in a separate `required_rows`
  array and are not duplicated in `rows`. 48 (`no`) + 127 (`undetermined`) + 2
  required (`no`) = 177, and EV OBS-9's "among the 50 rows the audit could
  classify" is exactly 48 + 2. Both required rows are present, both
  `exponent_changed: no`, and `open_mark_carried_forward: true` on the
  IDEA-20260807-c36472 transport row as the contract demands.

## 8. Cost-model checks (`agents/validator.md` §49-83)

| obligation | finding |
|---|---|
| Unit declared | **Yes** — `time_log2_fp_operations`, `memory_log2_fp_elements`; F_p operations / F_p elements. |
| Memory beside time | **Yes**, in every row. |
| Optimistic assumptions with direction of bias | **Yes**, four, each with `affects` and an explicit bias direction; three biases are declared conservative (favouring the worry, not the hypothesis). |
| Hidden overhead enumerated | **Yes**, three items including the subexponential cost of factoring `d`. |
| Measured / modeled never share a column | **Yes at row level**; see the one borderline below. |
| Every modeled row conditional on KERNEL_FIELD | **Yes, all four**, each stating in the same string that KERNEL_FIELD was *not* established. |
| Arithmetic recomputed | PS-TOY-24 `0.5·24 + 0.79239·24 = 31.0175` ✓; PS-P256 `128+256 = 384` ✓; PS-P384 `192+384 = 576` ✓; PS-ELL-SMALL `0.5·log2 13 = 1.8502` ✓. |
| Baselines byte-verified | **Yes** — KN-TECH-001/006/018/031 quoted with artifact sha256 and offsets. |
| per-attempt × inverse success probability | **N/A and correctly N/A** — no attack, no success probability; the record does not fabricate one. |

**Borderline, disclosed, not a defect call:** the PS-TOY-24 modeled row carries
`m_exponent_used: 0.7923947341131429`, which is a *measured* median, inside a
row labelled `basis: modeled`. The contract says "no table, row or column may
mix bases". The row's own note declares the provenance and the measured value is
also carried in the separate `measured_inputs` block. I record this as a
disclosed borderline rather than a violation: the row's output is modeled and
nothing is presented as measured that was not.

## 9. Scale binding and heuristic-validation checks

- **Pre-registered prediction**: yes. The specification is a pre-registration
  (`retrospective: false`), the sample size N ≥ 369 is *derived* from the KS
  critical value and a declared minimum resolvable distance of 0.10 before any
  data existed, and the STAGE-0 four-branch rule including the record-inverting
  BASE_FIELD branch is frozen. `amendments/` contains only `.gitkeep`, so no
  post-hoc protocol edit exists — see D-4 below for the one thing that
  arguably should have been amended.
- **Sample integrity**: sample size, seeds and sampling procedure are in the
  manifests and I regenerated the samples from them (§4).
- **Correspondence validity**: `correspondence: null`, explicitly, with the
  reason (no correspondence exists, which is *why* crypto scale is unreachable).
  Correct and honest — there is no substitute-sampling theorem to cite.
- **Scale binding**: p < 2^24 on every decade; `claim_tier: toy` throughout;
  crypto-scale rows are labelled MODELED-ONLY and conditional. AGENTS rule 7
  satisfied.

## 10. Defects and discrepancies

### V-1 (blocking-artifact gap) — pinned raw source streams are not committed

`.gitignore:26` (`*.raw`) matches every file under
`experiments/EXP-ICINV-fcb497/runs/RUN-ICINV-kf-stage0{,-v2}/sources/*.raw` — ten
files, **all untracked/ignored**, confirmed by `git status --porcelain
--ignored` and `git check-ignore -v`. The extracted `.txt` files **are**
committed.

- Contract text: `required_artifacts` names `runs/<RUN-ID>/sources/` — "every
  retrieved byte stream and its extracted text … IMMUTABLE. BLOCKING for
  STAGE 0."
- Practical consequence, bounded: every byte-verified quotation is checked
  against the `.txt` files, which are committed and which I re-verified from
  committed content. So the STAGE-0 verdict and all 31 quotations are fully
  reproducible from committed state. What is **not** reproducible from committed
  state is (a) the derivation of the `.txt` from the retrieved HTML and (b) the
  two 403 bodies — the only direct evidence of the retrieval failure. Their
  sha256 values are durably recorded in the committed
  `stage0-verdict.json` and `execution-report.yaml`, so the hashes survive; the
  bytes do not.
- Record / field / correction needed: not a record field — a repository
  configuration and archival gap. The correction is either a narrow
  `.gitignore` negation for `experiments/**/runs/*/sources/*.raw`, or a
  Coordinator archival task that force-adds those ten files, or an explicit
  statement in a superseding record that raw streams are hash-only in the
  archive. **Until one of these happens, the STAGE-0 blocking artifact is not a
  durable receipt and I may not certify it as one.**

### V-2 (substantive) — OBS-8's small-`m` family is not exactly characterised

`EV-ICINV-c68f13` OBS-8: *"Every m = 1 instance in the T1 small-order tail at
k12 and k14 has u = 1, v = −1, lambda = 1 with t in {1, 2}; the m = 2 instances
have lambda = d − 1 at t = −1. The family is: ordinary E/F_p with |t| ≤ 2 … It is
named here and handed forward as a deliverable."*

Full-corpus scan (all 21 000 instances) of every instance with `m ≤ 2`
— **256 instances**:

| family | count | characterisation (verified exactly) |
|---|---|---|
| A | **202** | `|t| ≤ 3`; the `m = 1` members all have `(u, v, λ) = (1, −1, 1)`; the `m = 2` members all have `(u, v) = (−1, −1)` and `λ = d − 1`. |
| B | **54** | `v = −1`, `u = t/2` **exactly**, `λ = u`, `p ≡ 1 (mod d)`, `m = 2`. `|t| ∈ {122, 126, 254, 362, 418, 502, 2042}`. Present at k12 (23), k14 (7), k16 (23), k20 (1). **54/54 match this description with 0 exceptions.** |

Two concrete corrections are needed:

1. `t ∈ {1, 2}` is wrong for the `m = 1` set: **9 instances have `|t| = 3`**
   (8 at k12, 1 at k14). The corpus `m = 1` set is `(u,v,λ) = (1,−1,1)` with
   `t ∈ {1, 2, 3}`.
2. "the m = 2 instances have lambda = d − 1 at t = −1" is false for **54 of the
   143 `m = 2` instances**, including **30 at k12 and k14**, the very decades
   OBS-8 names. These are family B, a second and arithmetically distinct
   mechanism (`p ≡ 1 mod d`), which OBS-8 does not mention at all.

Why it matters, precisely: OBS-8's argument that the family is harmless is *"the
trace-density of |t| ≤ 2 is O(1/√p) → 0 and a density-zero exceptional set is
exactly what H1 asserts exists."* **That argument does not cover family B**,
whose traces run to |t| = 2042 and which is defined by a congruence
(`p ≡ 1 mod |D|/4`), not by a trace bound. Family B may well also be
density-zero — I did not test that and make no claim — but the record's stated
reason is not the reason for 54/256 = 21% of the observed small-`m` set.

What does **not** change: no falsification condition is affected (F-ii needs
`OUTCOME_FAMILY_small_m` at ≥ 2 seeds, which fired at 1; F-vi concerns
action-step and fixture instances, not stage-3 curves). No median, KS statistic,
terminal state, seed vote, evidence strength or claim tier moves. OBS-8 is a
*deliverable* and a *handed-forward characterisation*, and it is the
characterisation that is wrong, not any number.

Correction needed: a superseding evidence record (never an edit) restating OBS-8
with both families, or a `CORR-*` naming `EV-ICINV-c68f13.observations` OBS-8.

### V-3 (traceability / overstatement) — OBS-2's "byte offset 1160"

`EV-ICINV-c68f13` OBS-2, `analysis.md:91`, and
`execution-report.yaml:177-186` all state that a passage **at byte offset 1160**
of the pinned 2020/341 landing-page text has
`verified_exact_substring: true` and is labelled `kernel_field` by *both* the
windowed and the document-aware classifier.

Verified facts:

- **No quotation in either `stage0-verdict.json` has `byte_start == 1160`.** The
  ten recorded 2020/341 offsets are `{474, 542, 785, 799, 944, 986, 987, 1001,
  1015, 1445}`.
- Byte 1160 is the start of the sentence fragment `"using only
  $\widetilde{O}(\sqrt{\ell})$ $\mathbb{F}_q$-operations, where the
  $\widetilde{O}$ is again uniform in $q$."` — which *is* an exact byte
  substring at that offset (I checked). So the dispatching session's re-test
  succeeded; it just was not testing a recorded quotation.
- The five recorded passages whose window covers the square-root count
  (`byte_start` 944, 986, 987, 1001, 1015) are labelled
  **`label: base_field`** by the windowed classifier and
  `label_with_document_context: kernel_field` by the document-aware one. The
  only two passages labelled `kernel_field` by **both** classifiers are at 785
  and 799, whose term matches sit in the sentence about the **classical** Vélu
  `Õ(ℓ)` count, not the square-root count.

So OBS-2's "both … classifiers label it kernel_field" is **not supported for the
square-root-Vélu operation-count passages**; for those, the windowed classifier
said `base_field`. The direction of the overstatement favours the branch that
keeps cost corollary CC alive.

Bounded impact: the STAGE-0 verdict is `AMBIGUOUS` under both classifiers and in
both runs (I verified both verdict files directly), because it is gated on
full-text retrieval, not on labels. No cost statement is made in either
direction. The record is explicit that the passage "is not a verdict". Nothing
numeric changes.

Correction needed: OBS-2 should cite the actual recorded offsets and report both
labels as they stand (windowed `base_field`, document-aware `kernel_field`), or
state plainly that offset 1160 is a substring of the text that the dispatcher
re-tested rather than a quotation-tail entry.

### V-4 (protocol-freeze note) — the v2 re-runs changed a classifier with no amendment

`RUN-ICINV-kf-stage0-v2` supersedes `RUN-ICINV-kf-stage0` and its
`supersession_note` declares the change honestly: a "document-level flag beside
the window label" was added because a kernel-rationality qualification lay
outside the frozen 400-character window. The effect is that five passages moved
from `base_field` to `kernel_field` at the document-aware level. This new
classifier is **not** in the frozen contract, and
`experiments/EXP-ICINV-fcb497/amendments/` contains only `.gitkeep`.

I do not call this an invalidation: SR5 freezes the grid (decades, seeds, sample
sizes, r-set, fixture rule, search terms) and none of those changed; the search
terms are identical in both runs; the verdict is identical in both runs; and the
run declares the change rather than hiding it. But it is a change to how a
*frozen primary metric's* supporting evidence is labelled, made after the first
run's output was seen, and it moved labels in the direction favourable to the
hypothesis. It is worth a Coordinator note alongside D1, and it is the second
reason (with D1) that the re-runs deserve a filed record.

### V-5 (fragility, not an error) — the 2-of-3 seed vote turns on one ECDF step

The dissenting seed 20260807 fails `OUTCOME_NULL` because only 1 of its 3
largest decades has `ks_D < crit`. The binding cell is **k22, where
`ks_D = 0.0610` against `ks_crit = 0.0607316`** — a margin of `0.00027`. At
n = m = 1000 the KS statistic is quantised in steps of `0.001`, so `0.061` is the
smallest attainable value strictly above the critical value: **a displacement of
a single instance's worth of ECDF would give `0.060 < crit`**, which would make
`ks_below_critical_at_least_2_of_3` true, fire `OUTCOME_NULL` at seed 20260807,
produce a 3/3 vote, and — under the frozen
`evidence_strength_calibration` (3 of 3 seeds AND ≥ 6 of 7 decades) — permit
`replicated` rather than `preliminary`.

This is not an error and the record errs conservatively. But
`EV-ICINV-c68f13.inference(2)`'s "the dissent rests entirely on deficits at k20
(0.081) and k22 (0.061)" understates how marginal k22 is, and the whole
"dissenting seed" narrative (and hence the `preliminary` cap) rests on one ECDF
step at one decade of one seed. A Red Team should have this. It should be stated
in any successor record.

### V-6 (minor) — OBS-7's "null medians differ"

OBS-7 says the k12 curve-derived median is bit-identical across three seeds
"while the null medians and the excluded fractions differ". Recomputed k12 null
medians: `0.6877159642375641`, `0.6877159642375641`, `0.6964615910910642` —
**two of the three are also bit-identical**. The substantive point survives (the
curve samples are genuinely different, which I confirmed by regenerating three
distinct (a,b) streams; and the curve median is a true population atom — order
statistics 500 and 501 are both `0.6869344921421261` at all three seeds). The
phrasing is loose.

### V-7 (minor) — `code.dirty: false` alongside `all_clean: false`

All 13 manifests carry `code.dirty: false` while `code.source.all_clean: false`
with three `untracked` imported modules. The source block is explicit and the
sha256 pins are what the invalidation rule actually requires, so this is a
labelling inconsistency in `harness/runner.py`'s manifest schema rather than a
defect in this experiment. Noted for the harness owner, not charged here.

### V-8 (minor) — T1 tail check covers one seed

`tail-checks.json.T1_small_order_outlier` is keyed by decade only and carries 5
rows per decade for a single seed. The contract asks for "the 5 instances with
the smallest log m / log d" in each decade without specifying per-seed, so this
is arguably compliant; I record it because OBS-8 generalises from this
single-seed tail to a corpus-wide claim (see V-2).

## 11. Disposition on the items the handoff asked me to rule on

### D1 — 13 runs against a frozen `maximum_runs: 12`

**Factual predicates confirmed.** 13 run directories exist. No amendment is
filed. Resource caps were nowhere approached (25.12 s wall vs 7200 s/run; 0.0066
CPU-hours vs 6; 99.2 MB vs 4 GB). All 13 runs are retained, none edited or
deleted. Both superseded runs are evidentially inert as claimed: **verified
directly** — `M0 = AMBIGUOUS` in both STAGE-0 verdict files, and both barrier
tables are **byte-identical row-for-row** (see CONFOUND-5 below). The
contract's own `budget_note` does enumerate only 10 core runs while
`required_artifacts` and SR7 both mandate the aggregate decide run, so the
contract's arithmetic is genuinely short by one.

**I concur with the disposition** (disclosed, not retroactively authorised, no
corrective run). Discarding `RUN-ICINV-kf-decide` to enforce a count would delete
the exact artifact SR7 exists to produce and hand terminal-state selection back
to a human after the data were seen — a worse breach than the overrun.
**One addition the decision does not make:** the two runs that consumed the
headroom were the v2 re-runs, and one of them changed a classifier without an
amendment (V-4). D1 and V-4 are the same event seen from two angles and should
be recorded together.

### D4 — gate G9 PARTIAL (tail check T5)

**Factual predicates confirmed by recomputation.**
`tail-checks.json.T5_memory_reconciliation` carries exactly
`{analytic_peak_bytes: 93339648, band: [0.25, 4.0], basis: modeled, components:
{…, instances: null}}` — **no measured value, no ratio, no `within_band`**. And
**all 13 manifests do carry** `resources.memory_reconciliation` with
`measured_peak_rss_bytes`, `analytic_peak_bytes`,
`ratio_measured_over_analytic` and `within_band` — I read all 13 and computed
the ratio range `[0.6809, 1.7444]`, all inside the declared band, decide-run
figures `63553536 / 93339648 / 0.6809 / true` exactly as the decision states.

**I concur.** (S-i) is met; (S-j) is partial at the file level for T5 only. A
corrective run to copy verified numbers into a second file would consume a
further run against a cap already exceeded, for zero information. The
reconciliation is recomputable end-to-end from committed manifests, which I did.

### CONFOUND-5 — the stale barrier-table binding

**CONFIRMED, and confirmed harmless.**

- `RUN-ICINV-kf-decide/decision-rule-evaluation.json.inputs.barrier_table_sha256
  = ee853b769220e24c2eda4b46b506d501be75fa08b53c2e46219d82c8961f64fa`. I hashed
  both tables: that is
  `RUN-ICINV-kf-stage1-barrier/barrier-table.json` (the **superseded** v1). The
  v2 table hashes to `85791f2c0c30…`. The stale binding is real.
- **M4 is identical in both tables, verified structurally rather than by
  assertion:** both have `row_count: 177`, `len(rows) == 175`,
  `M4_exponent_changed_count: 0`, `M4_undetermined_count: 127`,
  `rows_failing_byte_verification: 0`, `audit_outcome:
  OUTCOME_AUDIT_PARTIAL`. Row-set comparison: **0 rows present in one and not
  the other; 0 common rows differing in any field.** The tables are semantically
  identical; only their JSON serialisation differs (v2's `raw-result.json`
  differs, hence the differing file hash).
- **No number depends on the wrong binding.** `decide` binds the **correct** v2
  STAGE-0 verdict (`40b4788d…`, verified) and the correct seven stage-3
  `distributions.json` files (all seven hashes verified).

**Disposition: the record's classification is right.** It is a traceability
defect, correctly recorded rather than absorbed, with no numeric consequence.
The correction, if made, is a superseding note in a new record binding
`85791f2c…`; it is not worth a rerun.

## 12. What I could not check

- **Whether the square-root Vélu operation count is stated over the base field
  or the kernel-generator field.** This is `M0` and it is `AMBIGUOUS`. I did not
  attempt to resolve it: adjudicating it from my own knowledge of the paper is
  exactly what the contract's `background_knowledge_prohibition` forbids, and
  doing so would substitute my recollection for a retrieval. It stays open, with
  the successor action the record names (ANTS XIV proceedings or a locally
  archived PDF).
- **Whether family B (V-2) is density-zero.** I characterised it exactly and
  stopped. Establishing its density is new measurement, not validation.
- **CONFOUND-1's discriminating experiment** — a null drawn from small integers
  of matched magnitude rather than uniform units. This is cheap and decisive and
  it is exactly `KN-OPEN-2c095b` / next action N3. I did **not** run it: it would
  generate new evidence, which is not the Validator's role, and it would
  prejudge the discriminating replication the decision ordered.
- **Whether `H-ICINV-82ee6a`'s status transition is warranted.** Out of scope; I
  verify receipts, not what they mean for a hypothesis.
- **Model-provenance verification.** `model_verified: false` in all 13 manifests
  with the reason recorded (no `orchestration.adapter doctor --probe` receipt).
  I did not run a probe; this is a standing, disclosed harness limitation, not a
  defect of this experiment.
- **Wall-clock honesty of the recorded timings.** I verified they are internally
  consistent and under cap; I cannot independently attest that the runs took the
  wall time recorded.

## 13. What a passed validation would and would not mean

Even had every defect above been absent, this report would establish only that
the receipts are admissible evidence. **It would not support an ECDLP claim, would
not demonstrate a speedup, and would not authorise promotion.** The experiment
mounts no attack, evaluates no isogeny, implements no square-root Vélu, and
records `sota_delta: 0.0` against 0.886·√N. The `docs/inventor-protocol.md` §6
ladder for un-executable improvements does not apply, because **no improvement is
claimed** — the only quantitative movement is an *upward* cost correction on an
object that mechanism STEP 4 renders useless for the ECDLP anyway. Step 2 of that
ladder (measured ratio against a baseline on a scaled-down instance) is
inapplicable rather than skipped.

---

```yaml
validation_report:
  id: VAL-20260807-ICINV-fcb497
  task_id: null            # dispatched by direct handoff; no TASK id was bound
  snapshot_commit: 0e78af07a
  run_ids:
    - RUN-ICINV-kf-stage0
    - RUN-ICINV-kf-stage0-v2
    - RUN-ICINV-kf-stage1-barrier
    - RUN-ICINV-kf-stage1-barrier-v2
    - RUN-ICINV-kf-stage2-controls
    - RUN-ICINV-kf-stage3-k12
    - RUN-ICINV-kf-stage3-k14
    - RUN-ICINV-kf-stage3-k16
    - RUN-ICINV-kf-stage3-k18
    - RUN-ICINV-kf-stage3-k20
    - RUN-ICINV-kf-stage3-k22
    - RUN-ICINV-kf-stage3-k24
    - RUN-ICINV-kf-decide
  artifact_checks:
    - {check: run_count_vs_contract, result: DEVIATION_CONFIRMED, detail: "13 dirs vs maximum_runs 12 (D1)"}
    - {check: required_artifacts_present_per_stage, result: PASS}
    - {check: source_provenance_strict, result: PASS, detail: "exit 0; 13 pinned, 0 unpinned"}
    - {check: code_source_all_pinned, result: PASS, detail: "true in 13/13; 6 file hashes match on-disk exactly"}
    - {check: recorded_commit_reachable, result: PASS, detail: "7128debb0 is an ancestor of HEAD"}
    - {check: edit_prohibition_five_modules, result: PASS}
    - {check: stage0_source_sha256, result: PASS, detail: "8 hashes x 2 runs, all match incl. byte_length"}
    - {check: stage0_quotation_byte_substrings, result: PASS, detail: "31/31 exact at recorded BYTE offsets, both runs"}
    - {check: stage0_verdict_file_reads_AMBIGUOUS, result: PASS, detail: "both runs"}
    - {check: stage0_403_bodies_pinned, result: PASS_CONTENT_FAIL_ARCHIVE, detail: "sha256 match Cloudflare interstitials; files gitignored, not committed (V-1)"}
    - {check: sources_dir_committed, result: FAIL, detail: "10 *.raw files ignored by .gitignore:26 (V-1); .txt files are committed"}
    - {check: barrier_table_quoted_cells, result: PASS, detail: "177/177 byte-verified at recorded offsets, 0 failures"}
    - {check: certificate_kind_none_is_correct, result: PASS}
    - {check: claim_tier_not_exceeded, result: PASS}
  metric_recomputations:
    - {metric: M1_decade_medians, cells: 21, source: per-instance-measurements.json, tolerance: 0_ULP, max_abs_error: 0.0, result: EXACT}
    - {metric: M2_two_sample_KS, cells: 21, source: per-instance-measurements.json, tolerance: 0_ULP, max_abs_error: 0.0, result: EXACT}
    - {metric: ks_critical_value, recomputed: 0.060731606268894296, result: EXACT}
    - {metric: distinct_d_m_pairs_OBS7, cells: 21, result: EXACT, detail: "k12 164-173 ... k24 907-939 confirmed"}
    - {metric: median_d_over_p_PS_TOY_24, recomputed: 0.8325220046976813, result: EXACT}
    - {metric: excluded_curve_fraction_range, recomputed: "[0.0, 0.005964214711729622]", result: MATCHES_OBS4}
    - {metric: memory_ratio_range_13_manifests, recomputed: "[0.6808846761453397, 1.744368254059974]", result: MATCHES_OBS11}
    - {metric: total_resources, recomputed: "25.12 s wall / 0.00663 CPU-h / 99.16 MB", result: MATCHES_OBS11}
    - {metric: frozen_decision_rule, method: clean_room_reimplementation, result: EXACT, detail: "seed votes NULL 2 / FAMILY 1 / INSTRUMENT 0, dissenting seed 20260807"}
    - {metric: derivational_claim_lambda_eq_plus_minus_round_t_over_2, n: 21000, failures: 0, result: HOLDS_UNIVERSALLY}
    - {metric: magnitude_bound_lambda_le_sqrt_p_plus_1, n: 21000, failures: 0, max_ratio: 0.9970745956678385, result: HOLDS_AND_NEAR_TIGHT}
    - {metric: norm_form_and_discriminant_identities, n: 21000, failures: 0, result: EXACT}
    - {metric: order_arithmetic_deep_sample, n: 3150, sampling: "150/cell uniform w/o replacement, seed 4242", failures: 0, result: PASS}
    - {metric: seed_integrity_curve_stream, n: 21000, mismatches: 0, result: EXACT}
    - {metric: seed_integrity_null_stream, n: 21000, mismatches: 0, result: EXACT}
    - {metric: prime_ladder, result: EXACT}
  control_checks:
    - {control: planted_positive_BLOCKING, result: PASS, detail: "m=2 recomputed on all 10 frozen r"}
    - {control: m1_nearby_object_BLOCKING, result: PASS, detail: "9 pairs, m in {1,2}, 2 eigenvalue rows independently reproduced"}
    - {control: matched_null_null_first_SR2, result: PASS, detail: "sha256 of matched-null.json matches recorded; written_at < ks_computed_at in all 7"}
    - {control: decay_check, result: PASS, detail: "artifact tell did not fire at any seed"}
    - {control: factorisation_and_order_verification, result: PASS}
    - {control: order_certificate, result: PASS}
    - {control: run_source_provenance_BLOCKING, result: PASS}
    - {control: null_object_same_shape_inventor_protocol_s3, result: PARTIAL_AND_DISCLOSED, detail: "matched on d, NOT on support of lambda; disclosed as CONFOUND-1 and filed as KN-OPEN-2c095b; validator confirmed the support gap is real and near-tight"}
  heuristic_validation_checks:
    - {check: prediction_pre_registered, result: PASS}
    - {check: sample_size_derived_before_data, result: PASS, detail: "N>=369 from KS crit and D_min=0.10"}
    - {check: sample_integrity_regenerable_from_manifest_seeds, result: PASS}
    - {check: correspondence_validity, result: NA_CORRECTLY_DECLARED_NULL}
    - {check: scale_binding_toy_recorded_as_limitation, result: PASS}
  cost_model_checks:
    - {check: unit_declared, result: PASS}
    - {check: memory_beside_time, result: PASS}
    - {check: optimistic_assumptions_with_bias_direction, result: PASS}
    - {check: hidden_overhead_enumerated, result: PASS}
    - {check: no_row_mixes_measured_and_modeled, result: PASS_WITH_DISCLOSED_BORDERLINE}
    - {check: every_modeled_row_conditional_on_KERNEL_FIELD, result: PASS, detail: "4/4, each noting KERNEL_FIELD was NOT established"}
    - {check: cost_arithmetic_recomputed, result: EXACT}
    - {check: per_attempt_times_inverse_success_probability, result: NA_NO_SUCCESS_PROBABILITY_CLAIMED}
    - {check: sota_delta_and_dominated_by, result: PASS}
  proof_architecture_checks:
    - {check: baseline_fixture, result: PASS, detail: "standing baselines byte-verified from KN-TECH-001/006/018/031"}
    - {check: strictness_witness, result: NA_NO_IMPROVEMENT_CLAIMED}
    - {check: observation_collisions_bound_to_scope, result: PASS, detail: "(d,m) collision multiset recomputed exactly; forbids (d,m) as an identifying invariant"}
    - {check: method_ceiling_and_nearby_control, result: PASS, detail: "m=1 fixture is the preregistered nearby object and passes through the STAGE-3 code path"}
    - {check: quantifier_fidelity, result: PASS}
  defects:
    - {id: V-1, severity: blocking_archive, record: "experiments/EXP-ICINV-fcb497/runs/RUN-ICINV-kf-stage0{,-v2}/sources/*.raw", issue: "10 pinned raw byte streams incl. both 403 bodies are matched by .gitignore:26 and not committed; contract calls sources/ BLOCKING and IMMUTABLE"}
    - {id: V-2, severity: substantive, record: EV-ICINV-c68f13, field: "observations[OBS-8]", issue: "small-m family is not exactly characterised: 9 m=1 instances have |t|=3, and 54 m=2 instances form a second family (v=-1, u=t/2, lambda=u, p=1 mod d, |t| up to 2042) that OBS-8 omits and whose density argument does not cover"}
    - {id: V-3, severity: traceability, record: EV-ICINV-c68f13, field: "observations[OBS-2]", issue: "no quotation at byte_start 1160 exists; the square-root-count passages are labelled base_field by the windowed classifier and only kernel_field by the document-aware one"}
    - {id: V-4, severity: protocol_note, record: "experiments/EXP-ICINV-fcb497/amendments/", issue: "v2 re-runs added a document-aware classifier after seeing v1 output, with no amendment filed; verdict unchanged in both runs"}
    - {id: V-5, severity: fragility_note, record: EV-ICINV-c68f13, field: "inference(2)", issue: "the 2-of-3 seed vote and hence the preliminary cap turn on ks_D 0.0610 vs crit 0.0607316 at k22/seed 20260807 - one ECDF step of 0.001"}
    - {id: V-6, severity: minor, record: EV-ICINV-c68f13, field: "observations[OBS-7]", issue: "two of three k12 null medians are also bit-identical"}
    - {id: V-7, severity: minor, record: "harness/runner.py manifest schema", issue: "code.dirty:false alongside code.source.all_clean:false"}
    - {id: V-8, severity: minor, record: "runs/RUN-ICINV-kf-decide/tail-checks.json", field: T1_small_order_outlier, issue: "covers one seed only; OBS-8 generalises from it"}
  settled_deviation_dispositions:
    - {id: D1, predicates: CONFIRMED, disposition: CONCUR, note: "add V-4: the two headroom runs were the un-amended v2 re-runs"}
    - {id: D4, predicates: CONFIRMED, disposition: CONCUR}
    - {id: CONFOUND-5, predicates: CONFIRMED, disposition: CONCUR, note: "stale binding real; both barrier tables verified 0 differing rows, 0 set difference; decide binds the CORRECT v2 stage0 verdict and all 7 correct distributions"}
  verdict: incomplete
  verdict_plain: "validated with defects"
  verdict_rationale: >-
    The measurement is validated without reservation: all 42 primary statistics
    recompute bit-exactly from raw, both seeded streams regenerate exactly over
    21000 instances, all blocking controls pass on independent recomputation,
    and the frozen decision rule reproduces from a clean-room reimplementation.
    The verdict is `incomplete` rather than `passed` because a BLOCKING
    contract-required artifact class (runs/*/sources/*.raw, incl. both 403
    bodies) is not committed and is therefore not a durable receipt (V-1), and
    because two recorded observations (OBS-8, OBS-2) do not survive
    recomputation and need superseding corrections (V-2, V-3). No defect found
    changes any number, terminal state, evidence strength or claim tier.
  limitations:
    - "STAGE-0's substantive question (base field vs kernel-generator field) is not resolved by this pass and was deliberately not adjudicated from validator knowledge (background_knowledge_prohibition)."
    - "The density of the newly identified family B was not measured; only its exact characterisation was verified."
    - "The discriminating small-integer null (KN-OPEN-2c095b / N3) was deliberately not run: generating it is producer work, not validation."
    - "model_verified is false in all 13 manifests (no adapter probe receipt); a standing disclosed harness limitation, not charged to this experiment."
    - "Recorded wall-clock timings were checked for internal consistency and against caps, not independently attested."
    - "This report is a Validator receipt only. It supports no ECDLP claim, demonstrates no speedup, and authorises no promotion."
  artifact_paths:
    - experiments/EXP-ICINV-fcb497/validation-report.md
```
