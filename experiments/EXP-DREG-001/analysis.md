# EXP-DREG-001 — analysis

**Experiment:** EXP-DREG-001 (hypothesis H-DREG-001, question RQ-DREG-001)
**Instrument:** `src/h012c_block_m4ri.py` (checkpointable block-m4ri exact full-column
rank over GF(2), block-staircase carriers, sha256 `0eb38126…`, protocol version 1)
**Executor session:** TASK-20260718-DREG (continuation of TASK-20260717-001 work begun
by the prior executor session; coordinator live-bookkept the anchor runs)
**Cutoff:** 2026-07-18T20:05Z. Budget applied: handoff 3,000 s wall / 12 runs /
600 s-per-invocation kill rule (supersedes the spec's H100-scale budget; deviation D1).

---

## 1. Validation anchors — ALL FIVE PASS

Spec gate: *"no past-wall number is recorded until every validation anchor reproduces
exactly."* The gate is now fully satisfied.

| # | Anchor cell (t=3, D=5, ti=0, seed 2026) | Expected | Measured | Result | Run |
|---|---|---|---|---|---|
| 1 | n=12 sem full rank | 28,096 (pred 29,418, deficit 1,322) | **28,096** | PASS | RUN-DREG-001-VALIDATE-N12-A |
| 2 | n=15 sem full rank | 69,073 (pred 70,935, deficit 1,862) | **69,073** | PASS | RUN-DREG-001-VALIDATE-N15-A |
| 3 | n=18 sem full rank | 143,882 (pred 145,881, deficit 1,999) | **143,882** | PASS | RUN-DREG-001-VALIDATE-N18-A |
| 4 | n=12 null rank == sr_pred | 29,418 | **29,418** (deficit 0) | PASS | RUN-DREG-001-VALIDATE-N12-NULL |
| 5 | n=15 null rank == sr_pred | 70,935 | **70,935** (deficit 0) | PASS | RUN-DREG-001-VALIDATE-N15-NULL |

Anchors 1–3 reproduce the h012 full-exact cells (including the two-engine value
143,882 at n=18: peel+core and dense m4ri on the H100) with a *third*, independent
engine (block-m4ri) on hash-identical systems — engine cross-validation control
satisfied at three sizes. Anchors 4–5 confirm the T11 support-matched null is
semi-regular at n≤15 (rank == sr_pred exactly). Review correction C1's null-side
premise (null tracks sr_pred) holds at n≤15; the C1 cell itself (n=17 null full
rank) remains unmeasured (censoring table, §4).

## 2. Controls

| Control | Outcome | Evidence |
|---|---|---|
| Same-seed re-run (determinism) | PASS — n=12 sem re-run from a fresh dir: rank 28,096, identical system_hash `c47d17c3…` | RUN-DREG-001-CONTROL-N12-DET |
| Checkpoint / column-partition consistency | PASS at mechanism level — n=12 sem with chunk 8,000 vs 12,000 (6 vs 4 units): rank 28,096 both | RUN-DREG-001-CONTROL-N12-PARTB |
| Dense-m4ri cross-validation (n≤18) | PASS — block-m4ri reproduces the dense-m4ri H100 cells 69,073 (n=15) and 143,882 (n=18) exactly, and the peel+core cell 143,882 | anchors 2–3 |
| Null == sr_pred at every n≤15 h012 cell | PASS — 29,418 (n=12), 70,935 (n=15) | anchors 4–5 |

Per-cell checkpoint-resume consistency for *past-wall* cells: not exercisable — no
past-wall cell completed (§4). The mechanism is validated at n=12.

## 3. Measurements obtained

**Deficit series (sem, D=5, full exact, this instrument):** 1,322 / 1,862 / 1,999
at n = 12 / 15 / 18 — bit-identical to the h012 series. The series is decelerating
relative to rank growth (deficit +40.8% then +7.4% while rank ×2.2); whether it
grows super-linearly past n=18 is exactly the open question and is **not** answered
here (no past-wall data).

> *Addendum (§9–§11, later session):* the n=17 cells were subsequently measured and
> the D=5 series was resolved **degree-by-degree**, which shows this cumulative-D=5
> series is not the right cross-section to extrapolate — see §10.

**d_ff (sem arm, ic_first_fall algorithm, monoset-native driver `DREG_dff.sage`,
max_D=6):** n=12: d_ff(ti=0) = 3, d_ff(ti=1) = 2 (2 of 8 planned targets resolved;
cell then censored, §4). Prior series had d_ff flat at 2 where resolved; ti=0
yielding 3 is a single-sample deviation — recorded, no distribution claim.

**Structural observation (unexpected, recorded per rule 8):** the sem Macaulay
support covers only a fraction of the boolean simplex: ncols = 46,717 / 143,421 /
358,678 at n = 12 / 15 / 18, i.e. 84.2% / 82.2% / 80.8% of C(nb,≤5), decreasing
with n; the support-matched null covers 100% (55,455; 174,437 = C(30,≤5) exactly).
The Semaev system's missing monomials are a structural signature distinct from the
rank deficit itself.

**Null-arm plateau:** at n=15 null the running rank hit sr_pred (70,935) at column
100,000 of 174,437 with zero new pivots thereafter — the clean semi-regular
saturation profile.

## 4. Censoring table (stopping rules; none of this is evidence — AGENTS rule 5)

| Cell | State | Reason |
|---|---|---|
| n=17 sem full rank (C1 sem side) | not attempted *(as of the 2026-07-18 cutoff; SUPERSEDED — measured in the 2026-07-19/20 session, §9)* | estimated ~2,000–2,600 s work (10.1× work growth n=15→18 observed); exceeds 600 s kill rule and remaining budget |
| n=17 null full rank (review correction C1) | not attempted *(as of the 2026-07-18 cutoff; SUPERSEDED — measured, §9: C1 discharged)* | same scale; the one number the review explicitly wants — top resume priority |
| n=21, n=24 sem/null | not attempted | extrapolated ~7–8 h (n=21) to days (n=24) per cell; ladder ceiling reported, not smoothed |
| d_ff sem n=15,17,18,21,24 | not attempted | budget exhausted by anchors; driver also showed non-preemptible C-level echelon risk (below) |
| d_ff null, all n | not attempted | semi-regular first-fall needs D≈5–6 echelons (31k×55k+ sparse at n=12) — infeasible in budget |
| d_ff sem n=12, ti=2..7 | censored mid-cell | ti=2 entered a sparse echelon that the SIGALRM cap cannot preempt; executor killed the cell at >600 s per the stopping rule (RUN-DREG-001-DFF-N12-SEM-c, 2 targets preserved) |

Run budget consumption: 6 completed cells (5 anchors + 2 controls = 7 completed
runs, of which 3 anchor runs were coordinator-driven), 1 censored d_ff cell,
2 failed_infrastructure driver-debug runs (§5 D6). No sage invocation under my
control exceeded 600 s except the killed d_ff cell (1,027 s incl. the
non-preemptible echelon; instrument invocations were self-capped by `--budget`).

## 5. Deviations from the frozen specification

- **D1 (budget):** spec budget was 120 CPU-h / 7,200 s-per-run (H100). The
  coordinator handoff capped this session at 3,000 s wall / 12 runs / 600 s kill
  rule, with follow-up instruction to keep the largest feasible sizes and record a
  partial ladder. The d_reg/d_ff ladder past n=18 and the ≥8-target replication
  are therefore unmeasured; anchors and n≤15 cells were prioritized per the spec's
  own gating rule.
- **D2 (naming):** runs follow the experiment's live convention
  `RUN-DREG-001-<PURPOSE>-<TAG>` with docs-compliant receipts
  (`raw-result.json`, `stdout.log`, `stderr.log`, `command.txt`,
  `environment.json`, `work/` checkpoints), not the handoff's example pattern
  `RUN-EXP-DREG-001-a/raw.json`. Consistency with the coordinator's active
  bookkeeping and cross-referenced EV record was prioritized.
- **D3 (targets):** all rank cells are ti=0 (the h012 anchor cells are ti=0); the
  ≥8-target d_ff replication resolved only ti=0..1 at n=12.
- **D4 (instrument location):** `src/h012c_block_m4ri.py` + dependencies exist at
  the workspace root (created by the prior executor session per the spec's
  required_artifacts). This session modified nothing outside
  `experiments/EXP-DREG-001/` and `ledger/EV-DREG-001.yaml`.
- **D5 (two-invocation cell):** RUN-DREG-001-VALIDATE-N15-NULL completed across
  two invocations (Bash 300 s cap killed the harness, not the checkpointed
  instrument; resumed to completion). Instrument work total 404.2 s; rank was
  already 70,935 at the interruption point and unchanged on resume.
- **D6 (failed runs preserved):** RUN-DREG-001-DFF-N12-SEM and -SEM-b failed
  in 5 s each (Sage preparser coerced argparse default `3`→`Integer` and
  `round()`→`RealDoubleElement`, breaking JSON serialization in my driver;
  fixed in -SEM-c). No data produced; manifests record failed_infrastructure.
- **D7 (contention):** a foreign session process (`/Volumes/Volume/research/
  ecdlp-autolab` h012c probes, n=17/18, `timeout 280`) contended CPU during
  several cells. Ranks are exact integers and unaffected; timings in manifests
  are as-measured and should be read with this caveat.

## 6. Gate arithmetic vs H-DREG-001 (numbers, not a verdict)

- Success clause (i): d_reg(sem) < d_reg(null) at any n — **not evaluable**: no
  past-wall d_reg measured; d_reg(n) at D=5 is >5 for sem at n=15,18 (rank
  69,073 < 74,880 = nrows; 143,882 < 152,532) and >5 for the null (70,935 <
  74,880; plateau at pred). d_reg by the "full rank" definition was not reached
  at D=5 in any measured cell.
- Success clause (ii): deficit growth super-linear — series stands at
  1,322 / 1,862 / 1,999 (n=12/15/18). Growth increments: +540, +137. Exponent
  fit over three points is meaningless; the n=17+ points required by the clause
  do not exist.
- Success clause (iii): gap(n) = d_reg − d_ff bounded — **not evaluable**:
  d_reg unmeasured at any n past the wall; d_ff sem at n=12 is {3, 2} (n=2
  samples).
- Falsification clause: d_reg tracks null within CIs at all reachable n /
  deficit keeps decelerating — **not evaluable**: same missing cells.
- The hypothesis is therefore **untouched by this experiment's data**; the
  experiment's output is instrument validation + within-wall reproduction.
  Status decision belongs to the Coordinator.

## 7. Cost model for the resume (measured, this machine, M4 Pro 14-core, 48 GB)

| cell | work s | wall s | peak RSS |
|---|---|---|---|
| n=12 sem | 28.2 | 42.3 | 1.05 GB |
| n=12 null | 50.4 | 74.5 | 0.74 GB |
| n=15 sem | 316.7 | 449.1 | 3.18 GB |
| n=15 null | 404.2 | ~570 (2 invocations) | 2.64 GB |
| n=18 sem | 3,212.0 | 3,775.0 | 4.63 GB |

Work ratio n=15→n=18 ≈ 10.1×. Extrapolated: n=17 sem ≈ 1,300–2,000 s; n=17 null
similar; n=21 ≈ 25,000–32,000 s (~7–9 h); n=24 ≈ 2–3 days. Resume order
recommended: (1) n=17 null full (C1 discharge), (2) n=17 sem full, (3) d_ff sem
ladder n=15..18 with a preemptible (m4ri-block or subprocess-capped) driver,
(4) n=21 sem with checkpointing.

## 8. Artifact index

All under `experiments/EXP-DREG-001/`:

- `specification.yaml` (frozen protocol, status: running per coordinator)
- `DREG_harness.py` (run receipt harness), `DREG_dff.sage` (d_ff driver)
- `runs/RUN-DREG-001-VALIDATE-N12-A/` — anchor 1 (coordinator-driven)
- `runs/RUN-DREG-001-VALIDATE-N15-A/` — anchor 2 (coordinator-driven)
- `runs/RUN-DREG-001-VALIDATE-N18-A/` — anchor 3 (coordinator-driven)
- `runs/RUN-DREG-001-VALIDATE-N12-NULL/` — anchor 4
- `runs/RUN-DREG-001-VALIDATE-N15-NULL/` — anchor 5
- `runs/RUN-DREG-001-CONTROL-N12-DET/` — determinism control
- `runs/RUN-DREG-001-CONTROL-N12-PARTB/` — partition control
- `runs/RUN-DREG-001-DFF-N12-SEM-c/` — d_ff n=12 sem partial (censored)
- `runs/RUN-DREG-001-DFF-N12-SEM/`, `-SEM-b/` — failed_infrastructure (driver debug)
- Each receipt: manifest.yaml, command.txt, environment.json, stdout.log,
  stderr.log, raw-result.json (where produced), work/ checkpoints with
  sha256-pinned carries. Per-file sha256 in each manifest.

---

# Addendum — session 2026-07-19/20 (n=17/18 completion + syzygy characterization)

**Cutoff:** 2026-07-20. Same instrument and protocol; §1–§8 above are unchanged except
for two explicitly-marked supersessions (§3 addendum, §4 rows 1–2).

## 9. Ladder completed — C1 discharged

| Cell | pred | rank | deficit | Run | Status |
|---|---|---|---|---|---|
| n=17 sem | 126,922 | **125,099** | 1,823 | RUN-DREG-001-MEASURE-N17-SEM-A / -B | completed_valid (duplicate runs agree) |
| n=17 null | 126,922 | **126,922** | **0** | RUN-DREG-001-MEASURE-N17-NULL-A, -B-CONT-1 | completed_valid (C1 discharged) |
| n=18 null | 145,881 | **145,881** | **0** | RUN-DREG-001-VALIDATE-N18-NULL | completed_valid, 4,004 s wall |

The n=18 null was run as a **matched control** for anchor 3, differing from
RUN-DREG-001-VALIDATE-N18-A only in `--which null` (identical `--t 3 --targets 1
--d 5 --seed 2026 --chunk-force 24000`), with the expectation `deficit: 0`
preregistered in its manifest before the result existed.

**Null-arm result (now at every measured n):** deficit = 0 at n = 12, 15, 17, 18,
all replicates. The support-matched null is semi-regular at every size measured, so
the predictor carries no systematic bias and the sem-arm deficit is signal, not
predictor error. Review correction C1's premise holds past n=15.

## 10. Degree-resolved deficit (new measurement)

The cumulative D=5 deficit conflates degrees. Resolving it (exact GF(2) rank of the
degree-≤D Macaulay matrix, `peel_and_rank`, same construction and seed):

| n | k=dim V | nb | D=3 | D=4 | D=5 | cumulative(D=5) |
|---|---|---|---|---|---|---|
| 9 | 3 | 18 | 0* | 23 | 577 | 600 |
| 12 | 4 | 24 | 1 | 31 | 1,290 | 1,322 |
| 15 | 5 | 30 | 1 | 39 | 1,822 | 1,862 |
| 17 | 6 | 35 | 1 | 45 | 1,777 | 1,823 |
| 18 | 6 | 36 | 1 | 47 | 1,951 | 1,999 |
| 21 | 7 | 42 | 1 | 55 | — | — |

\* n=9 carries only 8 quadrics (not 9), so no degree-3 relation forms.

**Closed forms (exact, no fitted parameters):**
- graded deficit at **D=3 = 1** for every full system (n ≥ 12);
- graded deficit at **D=4 = 8k − 1**, exact for k = 3,4,5,6,7 (n = 9,12,15,18,21);
- equivalently **cumulative deficit at D=4 = 8k = 8·dim(V)**.

**Two artifacts in the §3 cumulative series are explained by this:**
1. The n=15→17 *dip* (1,862 → 1,823) is not a smaller deficit: n=17 is a
   structurally **deficient** system (nb = 2n+1 = 35 with only 34 equations, versus
   nb = 2n = m for full n = 3k), and its D=4 deficit is correspondingly 45, two below
   the full k=6 value of 47. n=17 and n=9 are the two deficient cells.
2. The D=5 graded deficit is **not polynomial in k** (differences 713, 532, 129 over
   k = 3→4→5→6). A fixed degree D=5 sits at a different depth relative to each
   system's degree of regularity, so the cumulative-D=5 series mixes regimes. The
   regime-consistent invariants live at low degree (D=3, D=4). **Consequence for
   clause (ii) of §6: extrapolating the cumulative D=5 series across n is not a
   sound test of super-linear growth**, independent of how many points are added.

## 11. Syzygy characterization (mechanism — structure identified, derivation open)

The deficit is by construction the excess of the true quotient dimension over the
semi-regular (Bardet–Faugère–Salvy) prediction, i.e. the extra non-Koszul syzygies.
Measured properties, full systems n = 12, 15, 18:

- **Semaev-specific.** The support-matched null has deficit 0 at *every* degree
  (D=3 and D=4 checked directly at n=12). A random system of identical shape, degree
  distribution and support has none of this structure.
- **Generic baseline is exactly the classical trivial syzygies.** The span of the
  n_q Frobenius relations (q_i² = q_i) plus the C(n_q,2) quadric Koszul pairs has
  rank exactly nrows − pred[4] (78 / 120 / 171 at k = 4/5/6) and lies in the kernel.
  So the semi-regular prediction's "expected" syzygies are precisely these, and the
  deficit is everything beyond them.
- **The syzygies are product / shared-factor relations.** The single degree-3
  syzygy was extracted and factors cleanly as **(Σ of a subset of quadrics)·(affine
  form L) = 0** for every n tested. The supports are coordinate-dependent (|Q| =
  8/7/7 and |L support| = 4/4/1 at n = 12/15/18) while the *count* is exact and
  reproducible — the signature of a graded Betti number: deterministic dimension,
  coordinate-dependent generators.

**Hypotheses tested and REFUTED (recorded per rule 8):**
1. *Frobenius self-relations as the source of 8k−1* — refuted: q² = q holds in every
   Boolean ring including the null arm, whose deficit is 0.
2. *Variable separation* (quadrics from S₃(u₁,x₃,R_X) confined to {u₁,x₃}) —
   refuted by direct measurement: every generator touches all four variable classes
   {u₁,x₁,x₂,x₃}; the α-Weil descent fully couples coordinates.
3. *Split 8k−1 = (5k−1) lifts-of-the-degree-3-relation + 3k new degree-4 seeds* —
   holds at k=4 only; the lift/seed boundary is coordinate-dependent noise
   (lifts 20/26/35, seeds 12/14/13 at k = 4/5/6). The invariant is the total, 8k.
4. *α-orbit invariance under the naive action* — refuted: multiplication-by-α
   realized as the companion matrix acting block-wise on descent components (with
   monomial multipliers fixed) preserves neither the kernel (110/110 basis vectors
   fail) nor even the universal generic space (78/78). The operator is therefore
   incomplete: a correct field action must co-transform the Boolean variables
   (u₁ is a full-field variable), which is a Weil-restriction module calculation.

**Open (theory-level, not measurement):** derive 8·dim(V) from the correct
Weil-restriction / Frobenius symmetry of the descended ideal. The count "8 per
V-direction" is exact and reproducible; its group-theoretic explanation is not
established, and the simplest candidate action is ruled out above.

**Scope note.** The §11 isolation is valid only for full systems (n = 3k). At n = 9
the system is over-determined (nb = 18) and the generic space is much larger than
Frobenius + Koszul, so the baseline subtraction does not apply there — the same
structural reason n=9 and n=17 are the deficient cells of §10.

## 12. Effect on §6 gate arithmetic (numbers, not a verdict)

- Clause (ii) (deficit growth super-linear): the cumulative D=5 series now reads
  1,322 / 1,862 / 1,823 / 1,999 at n = 12/15/17/18. Per §10 this cross-section mixes
  regularity regimes and contains two structurally deficient cells, so it does not
  support an extrapolation either way. At the degrees where the systems are
  regime-comparable, the deficit is **exactly linear in dim(V)** (8k), measured over
  k = 3..7 — i.e. linear, not super-linear, in the low-degree regime. Whether this
  persists at D ≥ 5 past the wall is unmeasured.
- Clauses (i), (iii) and the falsification clause: unchanged, still not evaluable
  (no past-wall d_reg; d_ff cells still censored).
- The hypothesis status decision remains the Coordinator's.

## 13. Addendum artifact index

- `runs/RUN-DREG-001-VALIDATE-N18-NULL/` — matched null control for anchor 3
  (manifest with preregistered `expected`, raw-result.json, work/ checkpoints).
- Characterization probes (analysis-side, not instrument changes; exact GF(2) linear
  algebra over the archived construction): system invariants, degree-resolved
  deficit, degree-3 syzygy extraction, degree-4 generic/extra isolation, α-action
  test. Narrative writeup: `DREG_DEFICIT_CLOSED_FORM.md`.
- All §9–§11 numbers derive from the construction in
  `runs/RUN-DREG-001-VALIDATE-N12-A/code/` (`semaev_tree.py`, `h012_peel_rank.py`,
  `macaulay_export.py`, `ic_first_fall_fast.py`) at seed 2026, t=3, ti=0 — the
  per-run archived code snapshot, which is authoritative after the workspace `src/`
  relocation of 2026-07-20.
