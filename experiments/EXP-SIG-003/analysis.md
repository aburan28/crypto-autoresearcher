# EXP-SIG-003 — Analysis: syzygy ↔ d_reg-deficit link test

Experiment: EXP-SIG-003 (hypothesis H-SIG-001, question RQ-SIG-001)
Dispatched by: DEC-20260718-017 (next_actions); handoff TASK-20260718-SIG-F3.
Runs: RUN-EXP-SIG-003-a (pilot, **invalid** — driver semantics bug caught by
the pre-registered sanity gate), -b (n=12 s2 sem), -c (n=12 s2 null),
-d (n=15 s1 sem), -e (n=15 s1 null), -f (determinism repeat of -b),
-g (determinism compare receipt), -h (n=12 seed-2026 sem cross-check),
-i (n=12 seed-2026 null).
Instrument: bit-identical copy of the EXP-SIG-001/002 instrument
(`src/h013_f5_signatures.sage`, sha256
`1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087`); new driver
`SIG3_run.sage` (link logic lives only in the driver).
Git: commit df595e8ac25c5be078485dea50e3a7f07d4e9a5b, dirty tree.
Budget: 9 runs of 10 maximum (one deliberately unspent — see §6); ≈ 342 s
compute wall of 3,300 s; peak RSS 2.22 GB of 24 GB (RUN-e). No censoring, no
timeouts; the 600 s kill rule never engaged (longest invocation 158.5 s).

## 0. What was measured (fixed before execution — specification.yaml)

On the same boolean chained Semaev m=3 systems (t=3, standard instances per
the EXP-SIG-002 input-side filter), per cell:

- D3/D4 classification with kernel bases; `residual_4` by the **verbatim**
  EXP-SIG-002 v3-multiples logic (continuity anchor).
- D5 count: rank, sr_pred, deficit_5 = sr_pred − rank, kernel_dim, rankK5,
  extra_5 = kernel_dim − rankK5 (the non-model syzygy-space dimension).
- LINK at D5: with `full_reduce` (canonical, exact mod-K5 ranks — see §5.4):
  - A3 = rank of {ν·ker_3 : deg ν ≤ 2} mod K5 (D3-syzygy closure);
  - A4 = rank of {ν·ker_4 : ν ∈ {1}∪{x_j}} mod K5 (closure of ALL
    lower-degree non-model syzygies; K4-images land in K5, so this is the
    closure of the D4 extra space);
  - A4_beyond_A3 = incremental rank of A4 over K5+A3-closure;
  - A4_id = rank of identity embeddings of ker_4 mod K5;
  - residual_5 = extra_5 − A4 (non-rewritable directions born at D5).

Merge (i) ⟺ residual_5 = 0; independence (ii) ⟺ residual_5 > 0.
A dimension argument is sufficient (handoff item 3).

## 1. The overlap/dimension table (sem cells; all numbers exact integers)

| cell | extra_4 | residual_4 | extra_5 (syz-space dim) | deficit_5 (missing pivots) | A3 | A4 (closure∩extra) | A4_beyond_A3 | A4_id | bound extra_4·(nb+1) | **residual_5** | coverage A4/deficit_5 | amplification A4/extra_4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n=12 seed 2     | 32 | 9  | 1,322 | 1,321 | 242 | **444** | 202 | 1 | 800   | **878**  | 0.3361 | 13.88 |
| n=12 seed 2026  | 32 | 9  | 1,323 | 1,322 | 242 | **444** | 202 | 1 | 800   | **879**  | 0.3359 | 13.88 |
| n=15 seed 1     | 40 | 10 | 1,863 | 1,862 | 392 | **705** | 313 | 1 | 1,240 | **1,158** | 0.3786 | 17.62 |
| all 3 null arms | 0  | 0  | 0     | 0     | 0   | 0       | 0   | 0 | 0     | 0        | —      | —     |

Consistency (all verified exactly): A3 + A4_beyond_A3 = A4 on every sem cell
(242+202=444; 392+313=705) — the D3 closure sits inside the D4 closure;
A4 ≤ extra_4·(nb+1); A4 ≤ extra_5; residual_5 ≥ 0.

Deficit decomposition (exact, each cell): **deficit_5 = A4 + residual_5 − 1**
(1,321 = 444 + 878 − 1; 1,322 = 444 + 879 − 1; 1,862 = 705 + 1,158 − 1).
The −1 is the rankK5 shortfall (one K-model vector dependent on sem that is
independent on the null): the identity
`deficit_5 = extra_5 + rankK5_sem − rankK5_null` holds on all three sem/null
pairs (rankK5 sem/null: 2,093/2,094 at n=12 both seeds; 3,944/3,945 at n=15).

## 2. Dimension accounting — merge or independence? (numbers only)

- The multiplication closure of **all** lower-degree non-model syzygies
  reaches rank **444 / 444 / 705** mod K5 = **33.6% / 33.6% / 37.9%** of the
  deficit (33.6% / 33.6% / 37.8% of extra_5). The closure **does** amplify:
  13.9 (n=12) and 17.6 (n=15) independent D5 directions per D4 extra syzygy,
  i.e. 55.5% / 56.9% of its count bound extra_4·(nb+1).
- **residual_5 = 878 / 879 / 1,158 > 0** on every sem cell: new non-rewritable
  directions exist at D5 that no lower-degree syzygy generates. The residual
  family alone (the strict "non-rewritable" 9/10 dims) is bounded by count at
  9·25 = 225 / 10·31 = 310 — even 4× that family (all of extra_4) measures
  444/705. Full merge (residual_5 = 0) is arithmetically impossible at these
  sizes (pre-registered bound: closure ≤ 800/1,240 < 1,321/1,862).
- Of the closure itself: the single D3 non-Koszul syzygy's multiplies account
  for A3 = 242/392 (80.4%/84.1% of its 301/466 images); the D4 extra family
  adds A4_beyond_A3 = 202/313.
- Verdict on merge vs independence for H-SIG-001 / the DREG program belongs to
  the Coordinator. Numbers: the D4 SIG family explains ~1/3 of the D5 deficit
  rank-wise; ~2/3 of the deficit (878/879/1,158 dims, minus/plus the rankK
  ±1) is a **new, independent D5-born component**.

## 3. Controls (all passed unless noted)

| Control | Outcome | Evidence |
|---|---|---|
| C1 continuity D3/D4 | PASS all sem cells: D3 def=extra=1; D4 def=extra=8n/3 (32/32/40); residual_4 = 9/9/10 (verbatim pinned semantics) | raw.json b/d/h |
| C2 continuity D5 | PASS: n=12 s2 rank 28,097/def 1,321/extra 1,322 and n=15 s1 rank 69,073/def 1,862/extra 1,863 reproduce EXP-SIG-002 anchors bit-exactly; seed-2026 reproduces the EXP-DREG-001 anchor 28,096/1,322 exactly | raw.json b/d/h |
| C3 null | PASS all 3 null arms: extra=0 and rank==sr_pred at D3/D4/D5; residual_4=0; A3=A4=A4_id=0; **residual_5=0** (zero deficit AND zero residual, as required) | raw.json c/e/i |
| C4 determinism | PASS: RUN-b vs RUN-f cell payloads identical modulo timing (formal compare receipt RUN-g, identical=True) | RUN-g raw.json |
| C5 instance filter | PASS: filter applied input-side; all 6 measured cells standard (R_x≠0, no degree-1 equation); nothing to exclude | raw.json filter blocks |
| C6 dimension sanity | PASS on all canonical-semantics cells (A3≤A4, A4≤extra_5, A4≤bound, A3+A4b==A4, A4_id≤A4, no missing rows, residual_5≥0). **FAILED on pilot RUN-a** — see §5.4 | raw.json sanity blocks |
| Kill rule / budget | Never engaged; longest invocation 158.5 s < 600 s | manifests |

## 4. Scope executed vs approved spec

All handoff items executed: n=12 AND n=15 arms both reached (no scope
reduction needed); link quantified (intersection vs deficit vs syzygy-space
dimensions, §1); amplification reported (§2); controls per spec (§3);
sha256-pinned instrument copies reused and re-hashed in every receipt.
One addition inside the sanctioned write scope: the seed-2026 cross-check
cells (RUN-h/-i), exercising the optional cell the specification pre-declared
— they close the EV-SIG-002 O(1)-seed-dependence confound (§5.2).

## 5. Unexpected observations (AGENTS rule 8)

1. **A4_id = 1 exactly (canonical) on every sem cell.** The identity
   embeddings of the D4 kernel at D5 are almost entirely absorbed by the K5
   model family: dim(span(K5) ∩ V4) ≥ 109 of 110 dims (n=12) and ≥ 159 of
   160 (n=15), vs rankK4 = 78/120. The surplus over K4 is **exactly
   extra_4 − 1** (31 = 32−1; 39 = 40−1) on all three sem cells: of the D4
   extra quotient, all but one dimension becomes model-explainable at D5.
   The D4 extra syzygies do NOT persist as extras at D5 — only their
   multiplied images contribute to the closure (A4 − A4_id = 443/443/704).
   Whether the single surviving dimension is the D3 syzygy's own identity
   embedding is undetermined (rank data cannot distinguish; recorded, not
   resolved).
2. **The closure is seed-stable while the deficit is not.** n=12 seeds 2 and
   2026 give identical A3/A4/A4_beyond_A3/A4_id (242/444/202/1) but extra_5
   1,322 vs 1,323 and deficit 1,321 vs 1,322: the O(1) D5 seed variance
   recorded in EV-SIG-002 (unresolved confound) localizes **entirely in
   residual_5** (878 vs 879), the new-at-D5 component — not in the closure.
3. **Seed-2026 ≡ EXP-DREG-001's n=12 instance, rank-wise.** The SIG
   instrument's seed-2026 build gives rank 28,096 / deficit 1,322 —
   bit-identical to the EXP-DREG-001 VALIDATE-N12-A anchor. EV-SIG-002's
   "1,321 (SIG seed 2) vs 1,322 (DREG seed 2026)" is therefore genuine
   instance variance (both values reproduced here in one instrument), not
   instrument drift.
4. **Pilot semantics bug (recorded in full).** The first driver version used
   the instrument's early-break `reduce_against` for quotient ranks. That
   reduction is exact for membership but can OVERESTIMATE quotient ranks; it
   produced A3+A4_beyond_A3 = 618 < 671 = A4 — arithmetically impossible for
   true ranks (the v3 images lie inside span(v4 images)). The pre-registered
   C6 internal-identity gate caught it on the pilot cell; no pilot data was
   used; the driver was fixed to canonical `full_reduce` (clears every
   pivot-lead bit; linear; rank-exact), after which A3+A4_beyond_A3 == A4
   holds exactly on every cell. **Consequence for the program:** the pinned
   instrument's `residual` measure (rank of v3-multiples mod K4) uses the
   same early-break construction, so the true D4 residual could be LARGER
   than the anchored 9/10/13/14 if that measure overestimates rank_v3mod.
   The anchors themselves are reproduced here verbatim (continuity intact);
   re-measuring the residual under canonical semantics is flagged to the
   Coordinator as a possible follow-up — NOT done here (EXP-SIG-003 tests
   the link, not the residual's value, and the residual anchors are
   program-definitional quantities of H-SIG-001).
5. **Coverage and amplification scale mildly with n.** A4/bound ≈ 0.555
   (n=12) → 0.569 (n=15); A3/images ≈ 0.804 → 0.841; coverage vs deficit
   0.336 → 0.379. Two points only; no law fit attempted.
6. **The −1 rankK5 shortfall persists** on the seed-2026 cell too
   (extra = deficit + 1 on all three sem cells; identity verified against
   matched nulls, §1) — the EV-SIG-002 "extra = deficit + 1" observation
   replicates on an independent instance.

## 6. Deviations

- **D1 (pilot run invalid, preserved):** RUN-EXP-SIG-003-a used the
  early-break quotient reduction (§5.4); marked `invalid` in its manifest;
  superseded by RUN-b; receipt retained per data-integrity rules.
- **D2 (run budget not fully consumed):** 9 of 10 runs used. A 10th run
  isolating the residual-only closure (rank of the 9/10 quotient reps'
  images) was judged unnecessary: the count bound (225/310) plus the measured
  closure of the strictly larger extra_4 family (444/705) already answer the
  handoff's rank-wise question. Recorded as a deliberate scope decision
  (precedent: EXP-DREG-002 deviation D6).
- **D3 (receipt naming):** receipts use `raw.json` / `stdout.txt` /
  `stderr.txt` per the EXP-SIG-002 convention; the docs' `raw-result.json` /
  `stdout.log` names are represented by these.

## 7. Censoring table (AGENTS rule 5 — none of this is evidence)

| Cell | State | Reason |
|---|---|---|
| n=15 arm reduction | not needed | longest invocation 158.5 s, far under the 600 s kill rule |
| residual-only closure isolation | not run | dimension question already closed (D2 above) |
| n=18+ link cells | not attempted | outside the handoff (n=12/15 only); D5 echelon cost grows (EXP-DREG-002: ~2,200 s at n=17) |

## 8. Artifacts

- `specification.yaml`, `implementation.md`, `analysis.md` (this file)
- `SIG3_run.sage` (driver), `make_manifests.py`, `summarize.py`,
  `compare_determinism.py`
- `src/{h013_f5_signatures.sage, semaev_tree.py, ic_first_fall_fast.py,
  macaulay_export.py}` — bit-identical instrument copies (sha256 in every
  manifest and raw.json)
- `runs/RUN-EXP-SIG-003-{a..i}/{manifest.yaml, command.txt, environment.json,
  stdout.txt, stderr.txt, raw.json}` (RUN-g: determinism-compare receipt)
- `summary.json` (machine-readable link table + identity checks)
- `ledger/EV-SIG-003.yaml`

Environment: SageMath 10.9, Python 3.14.3, macOS-15.6 arm64 (M4 Pro).
All raw.json files carry: exact CLI args, environment, UTC timestamps,
instrument sha256 set, per-D ranks/predictions/kernel data, instance-filter
fields, link ranks, sanity flags, and control outcomes. Manifests carry peak
RSS, CPU seconds (from `/usr/bin/time -l`), git commit/dirty state.
