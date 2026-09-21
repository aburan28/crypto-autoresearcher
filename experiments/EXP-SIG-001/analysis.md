# EXP-SIG-001 — Analysis: signature/Koszul classification of the low-degree syzygy family + Yokoyama #G* CM panel

Experiment: EXP-SIG-001 (hypothesis H-SIG-001, question RQ-SIG-001)
Runs: RUN-EXP-SIG-001-a (gate), -b (boolean n=9,12), -c (boolean n=15,18), -d (panel)
Instrument: `src/h013_f5_signatures.sage` (boolean tagged-Macaulay kernel/signature classifier + K-family model + Yokoyama #G* instrumented Buchberger + Betti helpers), driver `SIG_run.sage`.
Git: commit 09ccb38b838ea17b562add2a439d85a60dc05ced, dirty tree.

## 1. Scope actually executed (deviations from the approved test boundary)

Per the Coordinator's reduced-scope directive (minimum seeds, smallest decisive syzygy-degree range, kill any sage invocation > 600 s):

| # | Deviation | Approved spec (H-SIG-001 test_boundary) | Executed |
|---|-----------|------------------------------------------|----------|
| 1 | Seeds | ≥ 3 | seed 1 only |
| 2 | Syzygy degrees | max_D = 6 | D = 3, 4 only (no D ≥ 5) |
| 3 | t values | t = 3 (+t = 2 arm in experiment spec) | t = 3 only |
| 4 | Boolean Betti probe | planned | not run (`not_run: reduced scope` in driver) |
| 5 | n = 12 instance | generic Semaev | seed 1 produced R_x = 0 (2-torsion target); degenerate instance, recorded, not resampled |
| 6 | n = 9 D4 expectation | 8n/3 = 24 (T2 anchor) | measured 41 — T2 only measured n ≥ 12; gate V3 relaxed to record-not-assert before execution |

The panel arm (p = 1000003 ≈ 2^20, inside the spec q range 2^16..2^24) was executed in full: 7 families × {m=2: d=4,6; m=3: d=4} + gstar determinism rerun + Betti CHAIN t=3 and YOKO d=4 vs matched nulls.

## 2. Controls (all passed)

- **Gate V1** (support-matched T11 null, n = 9, 12, D = 3, 4): rank = semi-regular prediction exactly; kernel = K-family model exactly; extra = 0 everywhere. The K model (pairwise Koszul + principal (1+f_i) + vanishing multiples, GF(2) symmetric-difference semantics) is *exactly right* on random systems.
- **Gate V2** (injected 3-generator syzygy): detected with the correct constant-multiplier representation.
- **Gate V3** (Semaev n = 9 seed 1): D3 anchor deficit = extra = 1 with null extras 0.
- **Determinism**: boolean rerun-check (n = 9 seed 1, full cell computed twice): identical = true. gstar rerun-check: identical = true.
- **Isogenous same-order control**: all 6 base/iso curve pairs have exactly equal #E (generic 1000813, j=0 999007, j=1728 1000004, j=−3375 998272, j=8000 999702, j=−32768 998820).
- Instrument bug found and fixed during validation (before any official run): K-family principal vectors accumulated with OR instead of GF(2) XOR; a generator with a constant monomial double-counted its (i,∅) tag. Post-fix probe: every K vector is a true syzygy at n = 9, 12, 15, 18, D = 3, 4 (bad = 0). No pre-fix numbers appear in any artifact.

## 3. Boolean arm — measured numbers (seed 1, t = 3)

| n | nb | D3 deficit | D3 extra | D3 rankK | D4 deficit | D4 extra | D4 rankK (sem = null) | null extra D3/D4 | wall |
|---|----|-----------|----------|----------|-----------|----------|-----------------------|------------------|------|
| 9  | 18 | 1 | 1 | 0 | 41 | 41 | 45  | 0 / 0 | 0.4 s |
| 12* | 24 | 0 | 0 | 0 | 82 | 82 | 78  | 0 / 0 | 0.5 s |
| 15 | 30 | 1 | 1 | 0 | 40 | 40 | 120 | 0 / 0 | 1.9 s |
| 18 | 36 | 1 | 1 | 0 | 48 | 48 | 171 | 0 / 0 | 4.7 s |

*n = 12 is the degenerate R_x = 0 instance (see §6).

- The T2 count anchors reproduce exactly where T2 measured them: D3 deficit 1 and D4 deficit 8n/3 at n = 15 (40) and n = 18 (48).
- rankK is identical between Semaev and null at every (n, D): the entire K family is support-combinatorial, not curve-specific.

### 3.1 Structure of the extra (non-K-family) syzygies

**D3** (n = 9, 15, 18): exactly one extra syzygy, and rankK(D3) = 0 — it is a genuine degree-3 linear syzygy, *not* Koszul/Frobenius. Quotient-rep structure:

| n | support rows | generators used | generator index range | multiplier degrees | block |
|---|--------------|-----------------|-----------------------|--------------------|-------|
| 9  | 15 | 5  | 10–17 | {1}    | 1 only |
| 15 | 36 | 9  | 15–29 | {1}    | 1 only |
| 18 | 22 | 11 | 18–35 | {0, 1} | 1 only |

All D3-extra mass sits in block 1 (the second summation-polynomial block of the chain).

**D4 — F5 rewritten-rule analysis** (multiples of the D3 syzygy(ies) inside D4, rank taken mod K4):

| n | D3 syzygies | multiplier images | rank mod K4 | residual new at D4 (= extra − rank mod K4) |
|---|-------------|-------------------|-------------|--------------------------------------------|
| 9  | 1 | 18 | 18 | 23 |
| 12* | 0 | 0 | 0 | 82 |
| 15 | 1 | 30 | 30 | 10 |
| 18 | 1 | 35 | 35 | 13 |

Every multiplier image of the D3 syzygy is itself an extra (non-K) syzygy (rank mod K4 = number of nonzero images), and a residual family remains that is explainable neither as Koszul/Frobenius nor as multiples of the D3 syzygy. On the two non-degenerate T2-anchored sizes the residual is 10 (n = 15) and 13 (n = 18) — near 2n/3 but not exactly (2n/3 = 10, 12).

## 4. Panel arm — Yokoyama #G* at p = 1000003 (seed 1, decomposition targets, 55 s time box per cell)

| family | m=2, d=4 | m=2, d=6 | m=3, d=4 |
|--------|----------|----------|----------|
| generic     | #G*=9, #NS=10 | #G*=15, #NS=18 | #G*=49, #NS=58 |
| CM j=0      | 9, 10 | 15, 18 | 49, 58 |
| CM j=1728   | 9, 10 | 15, 18 | 49, 58 |
| CM j=−3375  | 9, 10 | 15, 18 | 49, 58 |
| CM j=8000   | 9, 10 | 15, 18 | 49, 58 |
| CM j=−32768 | 9, 10 | 15, 18 | 49, 58 |
| iso(generic)| 9, 10 | 15, 18 | 49, 58 |

Reference scale m·d^(m−1): 8 (m=2,d=4), 12 (m=2,d=6), 48 (m=3,d=4). Measured ratios: 1.12, 1.25, 1.02 — uniform across all families with zero variance; no censoring (max cell time 1.7 s; maxdeg reached 12 at m=3,d=4). #G* exceeds m·d^(m−1) by a small family-independent factor on every cell.

**Betti** (vs support-matched nulls): CHAIN t=3: reg = 6, pdim = 2, L1 = [0, 0] on all six base families. YOKO d=4: reg = 9/9, L1 = 0 on all six. No homological signature distinguishes any family from its null at these sizes.

## 5. Gate arithmetic (numbers only — status decision belongs to the Coordinator)

Falsification clause (a) requires: ALL extra syzygies rewritable/Koszul AND the T2 counts explained as shared-variable Koszul pairs.
Measured: extra(D3) = 1 at n = 9, 15, 18 with rankK(D3) = 0 — a genuine non-Koszul degree-3 syzygy. At D4, after removing the K family and all multiples of the D3 syzygy, residual non-rewritable syzygies remain: 23 (n = 9), 82 (n = 12*), 10 (n = 15), 13 (n = 18).

Falsification clause (b) requires: #G* ≈ m·d^(m−1) on every panel family.
Measured: #G* / (m·d^(m−1)) = 1.12, 1.25, 1.02 on the three (m, d) cells, identical on all 7 families (including CM and isogenous); no family collapse, no NS(Syz) anomaly, no censoring.

## 6. Unexpected observations (AGENTS rule 8)

1. **n = 9 D4 deficit = 41 ≠ 24.** The 8n/3 law was only measured by T2 for n ≥ 12. At n = 9 the extra family is larger (41, of which 18 are D3-syzygy multiples and 23 residual). Either the 8n/3 law sets in at n ≥ 12, or n = 9 has additional small-n structure. Gate V3 was relaxed to record-not-assert before execution (deviation #6).
2. **n = 12 seed 1 is a degenerate instance.** Instance generation produced R_x = 0 (the 2-torsion x-coordinate); the Weil descent yields block-1 quadrics with constant terms (eq degree histogram {2: 12, 3: 12} but with constants), deficit(D3) = 0, deficit(D4) = 82. This is an instance-generation anomaly, not an instrument bug (the null control at n = 12 is exact, and the K-model post-fix probe passes on this very system). Recorded; the Coordinator should decide whether n = 12 is re-run with a different seed.
3. **Residual D4 family is non-decreasing on the anchored sizes** (10 → 13 from n = 15 to 18) but two points, one seed, no CI — growth is unconstrained by this experiment.

## 7. Artifacts

- `runs/RUN-EXP-SIG-001-a/{raw.json, stdout.txt, stderr.txt, manifest.yaml}` — gate (PASS)
- `runs/RUN-EXP-SIG-001-b/{raw.json, stdout.txt, stderr.txt, manifest.yaml}` — boolean n = 9, 12 + determinism check
- `runs/RUN-EXP-SIG-001-c/{raw.json, stdout.txt, stderr.txt, manifest.yaml}` — boolean n = 15, 18
- `runs/RUN-EXP-SIG-001-d/{raw.json, stdout.txt, stderr.txt, manifest.yaml}` — panel + gstar rerun + Betti
- `src/{semaev_tree.py, ic_first_fall_fast.py, macaulay_export.py, h013_f5_signatures.sage}`, `SIG_run.sage` — instrument and driver
- `ledger/EV-SIG-001.yaml` — evidence record

All raw.json files contain: exact CLI args, environment (SageMath 10.9, Python 3.14.3, macOS-15.6 arm64), started/finished UTC timestamps, per-cell ranks/predictions/kernel data/quotient reps, and control outcomes.
