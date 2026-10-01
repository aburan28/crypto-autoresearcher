# EXP-SDEG-85eefd — implementation (protocol version 4)

Task: `TASK-20260928-c7aad3` (implementation only; `DEC-20260928-54db4a`), with the
v3 follow-up after `AMD-20260928-7ce387` (`DEC-20260928-6b03c5`).
Contract: `specification.yaml` (v1) + `amendments/AMD-20260926-3479cf.yaml` (v2) +
`amendments/AMD-20260928-7ce387.yaml` (v3; governs where they differ). **No scientific run was performed.** No `runs/RUN-*`
directory was created. The only computations were: fixture reproduction, offline
S4/S5 derivation, unit tests, and L = 8 seed-1 smoke checks under the
`smoke|EXP-SDEG-85eefd/v2` label namespace (never the frozen planted/random/rho
labels). No beta was computed across sizes.

## File map

| file | role |
| --- | --- |
| `fparith.py` | instrumented F_p (`Fp`, `OpCounter`) and affine EC (`Curve`) — charged paths |
| `polyfp.py` | instrumented univariate polynomials, `rem`/`prem`, subresultant PRS with early abort |
| `derive_semaev.py` | Sage: S4, S5 over Z[a,b] by resultant elimination → `semaev_polys.json` |
| `semaev_polys.json` | derived S3/S4/S5 term lists (sha256 in `implementation_report.yaml`) |
| `semaev.py` | per-fixture dense S4/S5 over F_p, charged Horner specialization, C-3 identity checker |
| `labels.py` | SHA256 seed labels (frozen and smoke namespaces) |
| `fixtures.py` | frozen fixture loader + byte-for-byte reproduction via the frozen generator |
| `decks.py` | interval_x / subgroup_x / random_x decks, progression control, C-5 targets |
| `backends.py` | forward table, B0, B1, B2, witness replay |
| `verify.py` | independent verifier arithmetic (Jacobian coords, Cipolla sqrt; no shared code) |
| `oracle.py` | exact A5 oracle (exhaustive 5-multisets of signed FB points) |
| `rho.py` | Pollard rho baseline (negation map, r = 32, fruitless-cycle escape) |
| `analysis.py` | C-6 metrics and C-7 outcome mapping (tested on synthetic data only) |
| `audit.py` | C-8 accounting audit (10% selection + receipt checker) |
| `cellrun.py` | one (fixture, deck) cell: oracle, table, B0/B1/B2, watchdog, agreement |
| `driver.py` | run driver, modes `charged` / `sage` / `merge` / `full`; **not executed** for a scientific run |
| `celltask.py` | independent task units (identity, cell, rho) run in parallel worker processes |
| `hostinfo.py` | host identity and the host-aware C-9 precondition (macOS / Linux pod) |
| `b2split.py` | no-Sage B2 split cross-check (charged host) |
| `pod_sync.sh` | sync protocol files + implementation to the pod, pod smoke, charged-part pull-back |
| `make_trial_plan.py` → `trial-plan-v2.json` | every cell, query id and seed label (header: protocol v3; cells unchanged) |
| `sage_b2_crosscheck.py` | Sage B2 cross-check (`fglm` literal Singular elimination; `split` eliminant) |
| `smoke.py` | the L = 8 smoke checks → `smoke/` |
| `tests/` | pytest unit tests |

## Protocol v4 (AMD-20260928-d3ed9e): FX-1..FX-5

v4 accepts D-1 and OQ-17..OQ-19 as implemented. No threshold, statistic,
cost accounting or outcome mapping changed. The v4 Mac smoke's
`opcounts.json` is byte-identical to v3 (sha `79e80dd1…`).

- **FX-1:** every mode admits only the explicitly named decision. It must be
  a `coordinator_decision` with a matching `id`, with `EXP-SDEG-85eefd` in
  `target_ids`, and with `execution_admission.currently_admitted: true` (a
  YAML boolean). Mentioning the experiment is not enough.
- **FX-2:** on Linux, an unreadable or unparseable `cpu.max` or load average
  refuses admission (fail closed).
- **FX-3:** a B0/B1 hit-triple set mismatch is a procedure defect that stops
  the run.
- **FX-4:** every task runs in a fresh spawn process (`max_tasks_per_child=1`,
  also with one worker). Its `peak_rss_bytes` and the 8 GiB guard therefore
  cover that task alone.
- **FX-5:** inference provenance comes from `AUTORESEARCH_*` variables only;
  unset variables are null, and the resolved model is `unverified`
  (`driver.inference_block`).

`PROTOCOL_VERSION = 4`. The trial plan's header carries the v4 amendment
sha256; its cells are unchanged.

## Protocol v3 (AMD-20260928-7ce387)

**Work quantities (OQ-1, OQ-4).** Every B0/B1 record carries:

| field | meaning |
| --- | --- |
| `W` | **primary**: decision cost — charged work through the first hit triple in the lexicographic (i3 ≤ i4 ≤ i5) order, full enumeration for a query without a hit — plus the cell's amortized table/deck share |
| `W_full` | secondary: full enumeration + share (the v2 `W`) |
| `W_fixed_xR` | B1's charged specialization of S5 at x(R) (52,488 mults at every size; 0 for B0 and for R = O) |
| `W_triple` | `W − W_fixed_xR` |

The per-(i3), per-(i3, i4) and per-triple specializations stay in `W_triple`;
only the per-query term is removed. `rho_c` uses `W`. `beta_work` (W),
`beta_work_full` (W_full) and `beta_work_triple` (B1, W_triple) are all
reported. Outcome A needs, in addition to the v2 conditions,
`B1_triple_all_worst_upper_ci_lt_gate`; outcome B uses W. The accounting audit
recomputes W, W_full, W_fixed_xR and W_triple from the op log.

**Flat (OQ-9).** For each size, `per_L[L].median_logW_over_logq` is the median
over the pooled queries of log W / log q. "Non-increasing or flat" means each
value exceeds the previous size's by at most `FLAT_TOL = 0.02`. The same test
feeds the known-false B0 gate.

**Host split.**

| step | mode | host | Sage |
| --- | --- | --- | --- |
| identity checks, decks, oracle, B0, B1, B2, no-Sage B2 split (L = 8), witness replay, rho | `charged` | pod (Linux) | never imported (AST test; `sage_imported` recorded) |
| fixture reproduction (C-1), literal FGLM B2 cross-check (L = 8) | `sage` | Mac | yes |
| consistency, FGLM vs B2, audit, metrics, C-7 | `merge` | Mac | no |

A run package is `runs/<RUN-ID>/{charged/, sage/}` (each with its own
manifest, command, environment, stdout/stderr) plus the merged top-level
`manifest.yaml`, `raw-result.json`, `metrics.json`, `audit.json` and
`cell_provenance.json` (host, container id, pid and file sha256 per cell).

Merge refuses to mark the run valid if any of these differ between the parts:
run id, trial-plan sha256, admission decision, label namespace, or the sha256
of any implementation file. It does the same if the charged process imported
Sage.

The sage part regenerates decks and targets deterministically; FGLM inputs are
not read from the charged part. Merge then checks that V and x(R) agree per
query.

**C-9 per host** (`hostinfo.py`).

| host | 15-min load | free disk |
| --- | --- | --- |
| Linux | ≤ floor(quota / period) from `/sys/fs/cgroup/cpu.max` (23 on the pod) | run volume ≥ 20 GiB, `/` ≥ 5 GiB |
| macOS (v2 rule) | ≤ 14 | `/` ≥ 5 GiB, repository volume ≥ 20 GiB |

Every part manifest records hostname, container id, cgroup quota, and the
Python, numpy and psutil versions.

**Parallelism.** `--workers N` sets the number of spawn processes: N ≤ 16 on
Linux, 1 elsewhere (enforced).
- Each task is one cell, one fixture's identity check, or one fixture's rho
  set. It runs single-threaded (BLAS/OpenMP thread variables are 1) and writes
  only its own file.
- The parent sorts every aggregate by id, so outputs do not depend on
  completion order (`test_scheduling_order_independent`).
- Each process has its own 8 GiB peak-RSS guard.
- After a defect or task error, no new task starts.
- `--after-cell-cmd` runs a copy-back hook after each task.
  `pod_sync.sh pull RUN-ID` pulls a charged part to the Mac.

**Cross-host op-count identity.** `smoke.py` and the charged part write
`opcounts.json`: per (query, backend) status, member, ops, W_query,
W_query_to_first_hit, W_fixed_xR, W_components, hit triples, PRS steps, and
the B2 degree/roots hash. Rows are sorted and written as compact JSON with
sorted keys, so two hosts agree iff the sha256 values agree.

## How each change is realized

**C-1 fixtures.** `fixtures.reproduce()` runs `sage -python ic_leads_fixtures_v2.py`
and byte-compares stdout with the frozen JSON. The driver does this first
and stops on a mismatch. Smoke: byte-identical, sha256 `543f49ca…a45`.

**C-2 decks.** V is a sorted list of liftable x (x³+ax+b a non-zero square); the
factor base is both lifts of each x, and the canonical lift is (x, min(y, p−y)).
- `interval_x`: the smallest L liftable x ≥ 0.
- `subgroup_x`: generator g = c^((p−1)/L) (first c ≥ 2 of exact order L); the
  elements g^0..g^(L−1) are filtered to the liftable ones (|V| may be < L; at L8-s1 it is 4).
- `random_x`: draw i = 0, 1, … as `uniform(SHA256('EXP-SDEG-85eefd/v2|random_x|L<L>|<seed>|<i>'), p)`.
  A draw is rejected if it is in the 2^256 remainder zone, a duplicate, or not
  liftable. Stop at |V| = |interval_x|.
- Deck construction is charged (spec v1 `charging_rule`: "Charge FB construction")
  on its own counter and amortized with the table.

**C-3 membership / S3 / S4 / S5.** S3 is P1480's formula, verbatim. S4 is
Res_t(S3(x1,x2,t), S3(x3,x4,t)) and S5 is Res_t(S4(x1,x2,x3,t), S3(x4,x5,t)),
both over Z[a,b] in Sage (content 1). S5 has 131,005 terms, degree 8 in every
variable, and is symmetric. The identity checker (`semaev.identity_check`)
draws four liftable points per tuple. Even tuples set the last coordinate to
x(P1 ± P2 …), a true relation; odd tuples use a uniform x. It checks the exact
equivalence "S_m = 0 ⇔ last x ∈ {x(P1 ± P2 ± …)}" with independent point
arithmetic for m = 3, 4, 5 on 1000 tuples. The driver stops on any failure.

*Point at infinity.* The forward sum U = e1P1 + e2P2 can be O (P2 = −P1).
The literal T = {u : S3 = 0} has no element for O. Omitting it would make
B0/B1 disagree with the oracle on every target that is a signed 3-sum
(repetition is allowed, so P − P + P3 + P4 + P5 is a member). Both charged
backends therefore carry an explicit INF element, present whenever V ≠ ∅:
- B0 sees it as a backward point equal to O.
- B1 sees it as a degree drop of b(u) below its formal degree 8. The leading
  coefficient of S5 in u vanishes iff S4(x3,x4,x5,x(R)) = 0.

A unit test (`test_three_sum_target_uses_infinity`) pins this.

**C-4 backends.**
- *Forward table* (shared): for each unordered pair (i1 ≤ i2), compute x(P1+P2)
  and x(P1−P2) by charged point arithmetic, with one charged hash probe per
  insert. The roots of S3(x1,x2,·) are exactly these x-coordinates; smoke checks
  S3(x1,x2,u) = 0 for every entry. B1 additionally builds
  F_T = ∏(u − v) sequentially (charged, Σ i mults). Table cost is reported
  unamortized and amortized over the deck's 32 queries. B0's table excludes F_T.
- *B0*: for each triple (i3 ≤ i4 ≤ i5, lexicographic over sorted V), all 8
  candidates x(R − e3P3 − e4P4 − e5P5) are computed incrementally
  (R∓P3 → ∓P4 → ∓P5) by charged affine additions. Each candidate costs one
  charged hash probe into T ∪ {INF}.
- *B1*: b(u) = S5(u, x3, x4, x5, x(R)) is formed by charged Horner
  specialization of the dense per-fixture S5 array. Order: x(R) once per query,
  then x3 per i3, x4 per (i3, i4), and x5 per triple, using S5's symmetry. Then
  it runs `polyfp.subresultant_prs(F_T, b)`: Collins/Brown (Cohen Alg. 3.3.7)
  with pseudo-remainders and exact divisions by g·h^δ. It aborts at the first
  vanishing pseudo-remainder (gcd found) or the first constant one (coprime).
  No resultant or eliminant is expanded. For R = O the generator is
  S4(u, x3, x4, x5) (formal degree 4). Decision: some triple has
  deg gcd ≥ 1, or an INF hit.
- *Witnesses* (both backends, every hit triple) are replayed with the
  independent verifier. The candidate u must lie in T. For B1, the PRS gcd must
  vanish at u and deg gcd must equal the number of distinct finite common roots
  (F_T is squarefree). An exact S5 evaluation must give 0. The 5-term
  decomposition (forward pair from the table) must sum to R.
- *B2*: the number of distinct finite x(R + e3P3 + e4P4 + e5P5) over
  unordered triples and signs, computed with verifier arithmetic and uncharged.
  Whether O occurs is recorded separately (it is not a root in u).
- *B2 cross-check*: `sage_b2_crosscheck.py` has two methods.
  - `fglm`: the literal Singular elimination. A Gröbner basis of
    I_R = ⟨S5(u,X3,X4,X5,x(R)), f_V(X3), f_V(X4), f_V(X5)⟩ in degrevlex, then
    FGLM to lex; the basis element in F_p[u] generates I_R ∩ F_p[u].
  - `split`: f_V splits into distinct linear factors, so
    rad(I_R ∩ F_p[u]) = rad(lcm over ordered V³ of S5(u,v3,v4,v5,x(R))).
    Univariate Sage arithmetic only.

  Both compare the radical degree and the root set with B2.
- *Arithmetic rule.* B0/B1 do all arithmetic through `Fp`. Units:
  `mul` (mult or square), `inv` (1 per inversion), `gcd_steps` (extended-Euclid
  division steps) and `probes` (hash lookups and inserts). The charged work is
  **W = mul + inv + gcd_steps + probes**. Every component is also stored
  separately so any other weighting can be recomputed. Bulk counts in
  vectorised kernels equal the number of elementwise products performed (see
  the tests). B1 also reports `W_components` (S5 specialization vs PRS).

**C-5 trial plan / oracle.** `trial-plan-v2.json` lists 9 fixtures × (3 decks
+ progression) = 36 cells × 32 queries (16 planted + 16 random).
- Planted query j, term k: r = uniform(SHA256('…|planted|L<L>|<seed>|<deck>|<j>|<k>'), 2|V|),
  index r // 2, sign + if r is even.
- Random query j: k = SHA256('…|random|L<L>|<seed>|<deck>|<j>') mod q and R = kG.
- Totals: 864 primary queries per backend and 288 control queries; B0, B1 and
  B2 all run on every query.
- The A5 oracle enumerates all C(2|V|+4, 5) multisets once per cell (its count
  is asserted) into an x-indexed parity bitmap.
- A planted target that the oracle rejects, or any B0/B1/oracle disagreement,
  is a procedure defect and stops the run.

**C-6 metrics** (`analysis.py`).
- beta_work = OLS slope of log(stat W) on mean log q over L = 8, 16, 32.
  The statistic is the median or maximum over queries pooled across the 3 seeds.
  It is computed per backend, per deck and per class (successful /
  unsuccessful / all).
- 95% percentile-bootstrap CIs: 2000 resamples, with replacement, within each
  (fixture, deck) cell after class filtering. numpy PCG64 is seeded from
  SHA256('EXP-SDEG-85eefd/v2|bootstrap'), fresh for each metric.
- Also computed: beta_elim (B2 median), beta_sub (B1 Σ deg gcd per query,
  median), P(success) per cell, and rho_c = median W(successful) / median W(all)
  per cell and pooled per (L, deck).
- A statistic ≤ 0 makes a beta *undefined* (recorded with its reason), not zero.
- Watchdog-stopped queries enter only class (iii), as flagged lower bounds.

**C-7 mapping** (`analysis.outcome`). Every condition of A and B is reported
individually.
- Procedure defects: B0/B1/oracle disagreement, an unverified witness,
  progression beta_elim ≥ 0.30, or B0 passing the outcome-A beta criteria
  (the known-false gate).
- Calibration failure gives `inconclusive`.
- beta_sub and successful-subset betas never enter A; a unit test pins the
  forbidden reading.

**C-8 controls.**
- Matched null: the random_x deck.
- Progression: V = x(kG), k = 1..L, run through every backend, plus the
  beta_elim < 0.30 check.
- Known-false: as above.
- Rho: 64 targets per fixture, k = SHA256('…|rho|L<L>|<seed>|<t>') mod q.
  Walk j(W) = x mod 32, canonical y ≤ (p−1)/2. Every visited point is stored.
  A revisit with b ≠ b' solves; a revisit with equal coefficients is a
  fruitless cycle, escaped by doubling the cycle's min-x point. Each log is
  verified by kG = Q. The driver reports walk (+ escape) group ops / √q against 0.886.
- Accounting audit: the lowest ceil(10%) of SHA256('…|audit|<query_id>') keep
  full per-triple op logs. The checker rejects a receipt if the log does not
  sum to W_query, a triple is missing or charged zero, a B0 triple lacks its 8
  probes, a B1 triple has no mults, the table or its probes are zero, or the
  amortized W is inconsistent.

**C-9 budget/admission.** `driver.py` reads `sysctl -n vm.loadavg`
(15-min ≤ 14) and `shutil.disk_usage` on `/` (≥ 5 GiB) and on the repo
(≥ 20 GiB). It **refuses before creating any directory** if any reading
fails, and records all three readings in the manifest. It also refuses:
- without an existing `ledger/decisions/<DEC>.yaml` that mentions this experiment;
- when trial-plan protocol hashes mismatch the files on disk;
- when the run directory already exists.

The per-query 3600 s watchdog is SIGALRM around each backend call; a stop
records the work so far as a lower bound and never scores the query. Peak RSS
above 8 GiB raises `MemoryLimit`, which stops the run as `resource_exhaustion`.
One run covers all fixtures. The manifest records the command, git commit and
dirty flag, environment and versions, implementation file hashes, seeds
namespace, admission readings, timings, peak RSS and validity; stdout and
stderr are teed.

`--smoke-dry-run` exercises the full driver path. It forces the smoke
namespace, restricts to L8-s1 with a few queries per deck, allows output only
under `implementation/smoke/`, and does not enforce admission. It is an
implementation check, not a run.

## Known limitations (implementation facts, not findings)

1. **B1 fixed overhead.** B1 specializes the *dense* 9⁵ S5 array. Modeled cost
   per query: 52,488 mults to fix x(R), 5,832·L for the x3 step, 648·L(L+1)/2
   for x4 and 72 per triple, against about 9·|T| per triple for `rem(F_T, b)`.
   At L = 8 the specialization terms are a large share of W (smoke cells keep
   `W_components`). At L = 32 they are a small share. This is the literal
   "b(u) = S5(…)" reading. Its effect on a 3-point slope (W at L = 8 raised by
   a fixed term) is to *lower* beta_work(B1). Protocol v3 therefore also
   requires outcome A on W_triple (see above).
2. Literal `fglm` elimination takes about 10 min per query at |V| = 8 on the
   smoke machine (Gröbner ≈ 210 s + FGLM ≈ 370 s). The charged part runs the
   no-Sage `split` on every L = 8 query; the sage part runs `fglm` on all
   |V| ≤ 4 queries plus the first `--b2-fglm-per-cell` (default 1) query of
   each other L = 8 cell (OQ-5 ruling).
3. The oracle is exhaustive in pure Python: C(68, 5) ≈ 10.4 M Jacobian
   additions per L = 32 deck (modeled, not timed).
4. Rho group ops are counted via inversions (one per affine add or double);
   scalar-multiplication precompute is reported separately.
5. The watchdog uses SIGALRM, so each task runs in the main thread of its own
   POSIX process (the parent or a spawn worker).
6. A member's decision cost ends at the end of its first hit triple: all 8 B0
   candidates, or B1's whole PRS, of that triple are charged (OQ-17).

## Running (for the admitted run only)

```sh
# pod (Linux, no Sage), after ./pod_sync.sh sync from the Mac
python3 driver.py --check-admission-only
python3 driver.py --mode charged --run-id RUN-<…> --admission-decision DEC-<…> \
    --workers 16 --source-commit "$(cat /workspace/sdeg/SOURCE_COMMIT)"
# Mac
./pod_sync.sh pull RUN-<…>        # copy runs/RUN-<…>/charged back (repeatable)
python3 driver.py --mode sage  --run-id RUN-<…> --admission-decision DEC-<…>
python3 driver.py --mode merge --run-id RUN-<…> --admission-decision DEC-<…>
# checks
python3 -m pytest -q tests                           # unit tests
python3 smoke.py --out-dir smoke/mac                 # Mac smoke (with Sage)
./pod_sync.sh smoke                                  # pod smoke (no Sage) + copy back
```
