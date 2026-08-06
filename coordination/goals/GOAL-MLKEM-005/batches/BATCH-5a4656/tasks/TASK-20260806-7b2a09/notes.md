# Validator working notes — TASK-20260806-7b2a09 (BATCH-5a4656)

Independent session. Nothing below is copied from any producer's own
prose beyond the numbers I verify against; every "match" line is computed
by code I wrote in this session, run in this session.

## 0. Snapshot verification

```
$ git cat-file -t 8a121df975c8665b7b7a62436b228822d4fe9545
commit
$ git merge-base --is-ancestor 8a121df9... 5c445c9e... && echo YES-ANCESTOR
YES-ANCESTOR
$ git rev-list --count 8a121df9...5c445c9e...
1
$ git show --stat 5c445c9e...
    coordination: bind TASK-20260806-6c5a4b snapshot receipt
 .../TASK-20260806-6c5a4b/snapshot_receipt.json | 29 +++++++++++++++++---
 .../batches/BATCH-5a4656/dispatch_queue.json    | 31 +++++++++++++++++++---
```

**Finding:** the working-tree HEAD (`5c445c9e`) is one commit *ahead* of the
snapshot named in my task card (`8a121df975c8665b7b7a62436b228822d4fe9545`).
That one extra commit is the disclosed self-referential "binding" commit
(same two-step pattern as BATCH-a51f91's own snapshot, per
`snapshot_receipt.json.binding_note`): it fills in `commit_sha`, `parent_sha`
and `path_sha256` inside `snapshot_receipt.json` itself (which the *committed
blob at 8a121df9* carries as `null`/`{}`) and marks the archive task
`completed` in `dispatch_queue.json`. It touches **exactly** those two files
and **no producer artifact**. I confirmed this with
`git diff --name-only 8a121df9 5c445c9e`, which returns only those two paths.

I then independently recomputed sha256 of all 21 declared producer/receipt
paths via `git show 8a121df9:<path> | sha256` (script:
`verify_hashes.py`, not embedded here — trivial hash loop) and diffed the
result against `snapshot_receipt.json`'s `path_sha256` (as filled in by the
binding commit): **0 mismatches, 21/21 match**. Since the binding commit
does not touch any producer file, reading producer content from the working
tree (as I do below, via the `Read` tool) is safe and byte-identical to what
`git show 8a121df9:<path>` would return — I spot-checked this for
`results.json`, `report.md`, `census.json` explicitly with `sha256sum`
against the recomputed values above.

`8a121df9`'s parent is `da16e6d3` (`git log -1 --format='%H %P' 8a121df9`),
matching the archive's declared `parent_sha`.

## 1. Independent re-derivation of P4 (Gaussian null-of-the-null)

I do **not** trust `report.md`'s own P4 table. I extract the raw per-draw
`ratio_2^-10` values from `results.json`'s `cells.*.arms.gaussian_null_of_null.per_draw[i].p2em10.ratio`
(the `ratio_2em10_over_draws` field next to it is only a *summary* dict —
mean/sd/min/max — not raw draws, so I go one level deeper to the actual
8 numbers). I recompute mean, sample sd (`ddof=1`), `SE = sd/sqrt(8)`,
`|mean-1|`, and the SE-multiple, entirely from scratch with `numpy`/`math`,
and diff against `results.json`'s own `P4_gaussian_null_of_null` block.

Full script: `rederive_p3_p4_p5.py` (reproduced in full below). Full output:
`rederive_output.txt` (reproduced in full below).

**Result: exact match in all four cells, to the digits shown (`math.isclose`
at `rel_tol=1e-9` for the linear quantities, `1e-6` for the SE-multiple).**

| cell | my dev/SE | reported dev/SE | P4 met |
|---|---|---|---|
| d100_b30 | 0.7329 | 0.732885 | PASS |
| d100_b40 | 0.8788 | 0.878785 | PASS |
| d140_b30 | 0.0603 | 0.060324 | PASS |
| d140_b40 | 0.5170 | 0.517036 | PASS |

**This CONFIRMS the reported P4 range "0.06–0.88 SE against a 4-SE budget"
exactly** (max is 0.8788 → rounds to 0.88; min is 0.0603 → rounds to 0.06).

## 2. Independent re-derivation of P3 (SE-of-the-difference sensitivity gate)

Same discipline: raw per-draw `ratio_2^-10` values for `graded.t0.00`
(coordinate-aligned) and `graded.t1.00` (Haar), extracted the same way. I
recompute `mean_t0`, `sd_t0`, `mean_t1`, `sd_t1`,
`SE_unpaired = sqrt(sd_t0^2+sd_t1^2)/sqrt(8)`, the signed shift, and the
SE-multiple, from scratch.

**Result: exact match in all four cells.**

| cell | my shift/SE | reported shift/SE | P3 met (≥4 SE) |
|---|---|---|---|
| d100_b30 | 46.8158 | 46.81580 | PASS |
| d100_b40 | 73.1455 | 73.14551 | PASS |
| d140_b30 | 52.9396 | 52.93956 | PASS |
| d140_b40 | 53.9901 | 53.99014 | PASS |

**This CONFIRMS the underlying figures 46.82/73.15/52.94/53.99 SE exactly.**

I also cross-checked that `graded['t0.00']` is bit-identical to the
dedicated `coord_aligned` arm and `graded['t1.00']` to `haar_null`
(`np.allclose` — True in all 8 cases), i.e. the report is not silently using
two different code paths for the "same" quantity.

**Correction to my own launch-instruction text and the Coordinator's commit
message:** both state the P3 range as "46.8–73.2 SE". The precise reported
maximum is `73.14551134617912`, which rounds to **73.1**, not 73.2, at one
decimal place (`round(73.14551134617912, 1) == 73.1` — checked directly in
Python). `report.md`'s own prose only ever states the *integer*-rounded
range "47–74 SE" (Sec. 0) and the exact table value "73.15" (Sec. 3, itself
a correct 2-decimal rounding of 73.14551...); **B2-A's own artifacts never
write "73.2" anywhere.** The "73.2" figure originates in the Coordinator's
commit message / `snapshot_receipt.json.producer_headlines`, and was passed
to me verbatim in my own task launch text. Recorded as a minor Coordinator
commit-message defect below (DEF-3); it changes no pass/fail verdict since
73.1 and 73.2 both vastly clear the 4-SE gate.

**Diagnostic (not a defect):** the P3 SE choice is declared "UNPAIRED" and
justified as "conservative" because `t=0` and `t=1` use disjoint seed
families. I checked the empirical correlation between the 8 `t=0` and 8
`t=1` draws (indexed by replicate `j`) directly: it ranges from **-0.57 to
+0.72** across the four cells — essentially noise at `n=8`, consistent with
the claimed population correlation of ~0 but not able to confirm the
"plausibly non-negative" claim either way from 8 points. This does not
change any P3 verdict: even the *smallest* alternative (paired-style) SE I
computed (0.00094 at d140_b30, using that cell's own +0.72 sample
correlation) would only make the SE-multiple larger, not smaller, and the
margins (47–74 SE against a 4-SE gate) swamp this by more than an order of
magnitude regardless of SE convention.

## 3. Independent re-derivation of P5 (the falsifier)

Departure is defined as the P3 signed shift (`mean_t0 - mean_t1`) — I reuse
my own independently-computed P3 shifts from step 2, not the report's, and
compute `departure(beta=40)/departure(beta=30)` at each `d`, compared
against the pre-registered `predicted_ratio_beta40_over_beta30` in
`prediction_frozen.json`.

**Result: exact match.**

| d | my measured ratio | reported | predicted | my rel. discrepancy | reported |
|---|---|---|---|---|---|
| 100 | 0.892575 | 0.8925753827199299 | 0.801784 | 11.3237% | 0.1132370913355345 |
| 140 | 0.890255 | 0.8902550943598917 | 0.825723 | 7.8152% | 0.07815246063452075 |

**This CONFIRMS the reported decay ratios 0.8926/0.8903 vs predicted
0.8018/0.8257, and the 7.8–11.3% relative-discrepancy figures, exactly.**
Both cells: departure positive, `departure(beta=40) < departure(beta=30)`
(decay, correct direction), no artifact tell.

## 4. D-1 (the graded-family scale-mismatch defect) — checked two ways

### 4a. Empirically: run1 vs run2 bit-comparison

Script: `compare_run1_run2.py` (below). I directly diffed
`results_run1_raw.json` against `results.json` field-by-field for every
quantity that feeds P1–P5: `P4_gaussian_null_of_null`, `P3_sensitivity`,
`verdict_on_the_real_arm`, `verdict_on_the_null_arm_FIRST`, `arms.real`,
`arms.coord_aligned` (`=graded t=0`), `arms.haar_null` (`=graded t=1`),
`arms.gaussian_null_of_null`, `forced_values`, and the top-level
`P5_falsifier_adjudication` and `frozen_prediction` blocks.

**Result: every one of these is bit-for-bit (`==` on the parsed JSON
sub-objects) identical between run 1 and run 2, in all four cells.** This is
a *stronger* check than the report's own claim (which states P1–P5 match; I
additionally checked `forced_values` and the raw `arms.real`/`arms.graded`
sub-objects those depend on, not just the summary P-blocks).

I then checked the **interior** graded-family points (`t=0.05` through
`t=0.75`), which the report claims *should* differ: **all 20 (4 cells × 5
interior t-values) differ**, and the pattern matches the described "cliff"
exactly — run 1's interior means collapse to ≈1.00 (near-Haar) already at
`t=0.05`, while run 2's decay smoothly from ≈1.09 at `t=0` to ≈1.00 at
`t=1`. Run 1's `monotone_nonincreasing` flag is `False` in exactly 3 of 4
cells (`d100_b40`, `d140_b30`, `d140_b40`) and `True` in 1 (`d100_b30`) —
an exact match to receipt.json's own claim ("3 of 4 cells failed strict
monotonicity"). Run 2 is `True` in all four.

I also checked `unreduced_qary` and `lll_only` (arms that don't touch
`E_S`/`G` at all): identical between runs in all four cells, as expected.

### 4b. Mathematically: is the QR-invariance argument correct?

The claim (`measure.py`'s `build_graded_Q` docstring, `receipt.json` D-1):
*"standard (unpivoted) QR is invariant under any independent positive
per-column rescaling of its input… leaving Q at t=0 (pure `E_S`) and Q at
t=1 (pure `G`, now rescaled) unchanged… it changes only the interior t."*

I re-derived this from first principles rather than taking it on faith:

- At `t=0`: the mixed matrix is `sqrt(1)·E_S + sqrt(0)·G = E_S` exactly — `G`
  does not appear in the expression at all, so no rescaling of `G` can touch
  `Q_0`. Trivially unaffected.
- At `t=1`: the mixed matrix is `sqrt(0)·E_S + sqrt(1)·G = G` (or `G`'s
  rescaled version). For an unpivoted (fixed column order) QR / Gram-Schmidt
  process, each output column `q_i` is the *normalized* orthogonal residual
  of input column `i` against `q_1,...,q_{i-1}`. Rescaling input column `i`
  by any positive scalar `c_i` scales that residual by the same `c_i` before
  normalization — normalizing divides it back out, so `q_i` (its direction,
  possibly up to an implementation-defined sign convention) is unchanged.
  More directly: independent positive per-column rescaling of a full-rank
  matrix's columns does not change the *column space* it spans (each column
  is only rescaled along its own line, so the span of the whole set is the
  same subspace), and the orthogonal projector `P = QQ^T` onto a fixed
  subspace is the *unique* projector onto that subspace regardless of which
  orthonormal basis (`Q`) is used to represent it. So `R = e^T P e` is
  provably unaffected. **This part of the argument is correct.**
- At interior `t ∈ (0,1)`: each column of the mixed matrix is
  `sqrt(1-t)·e_i + sqrt(t)·g_i` — a **linear combination of two different
  vectors**, not a single rescaled vector. Rescaling `g_i` alone (to
  `g_i/‖g_i‖`) changes the *relative weight* of the two terms in that sum,
  which generically changes the **direction** of the resulting column (not
  just its magnitude), since `e_i` and `g_i` are not parallel. So the
  per-column-positive-rescaling invariance argument does **not** apply at
  interior `t`, and the column space — hence the projector, hence `R` — is
  expected to change there. **This matches exactly what I observed
  empirically in 4a: only interior points move.**

I also read `measure.py`'s actual `build_graded_Q` function (lines
180-216): it implements exactly this (`G = G / np.linalg.norm(G, axis=0,
keepdims=True)` before mixing; `M = sqrt(1-t)*E_S + sqrt(t)*G`), matching
the docstring and the receipt's description of the fix. The delivered
script is the *post-fix* (run-2) version only; the pre-fix version that
produced `results_run1_raw.json` was not separately preserved as a file (the
receipt discloses this and describes the one-line diff instead), so I could
not literally re-execute run 1's exact code — but the run1-vs-run2 JSON
diff in 4a is independent, stronger evidence for the same conclusion (it
doesn't depend on trusting the receipt's description of what changed).

**Conclusion: the D-1 claim is CONFIRMED, both empirically (bit-identical
P1-P5-relevant fields; differing, and correctly-collapsing, interior
points) and mathematically (the QR-invariance argument is a correct,
non-trivial fact about unpivoted QR, correctly applied to the `t=0`/`t=1`
special cases and correctly NOT claimed for interior `t`).**

**Limitation:** receipt.json's D-1 entry also cites specific principal-angle
diagnostic numbers (67.7°/81.2°/89.1° at `t=0.01/0.02/0.05`) from "an
independent principal-angle diagnostic (not part of measure.py)" — that
standalone script is not among the delivered artifacts, so I cannot
independently recompute those three specific numbers. They are illustrative
motivation for the fix, not load-bearing for the D-1 conclusion itself,
which I verified through the delivered code and the run1/run2 diff
independently of them.

## 5. B2-B (C1 bound) — checked against T3's committed verification.json

- R20/R21 `bounding_mechanism` quotes in `bound.md` verified verbatim,
  character-for-character, against
  `BATCH-a51f91/TASK-20260805-e6a153/census.json` rows R20/R21 (including
  section numbers "Sec. 6" / "Sec. 3").
- The lane-(a) "curvature-independent" claim: re-derived from first
  principles. For `M=1`, `log2(M)=0` is pure arithmetic, no convexity
  needed. The *general* inequality `G ≤ log2(M)` (for `M>1`) needs only the
  **sign** of `f''` (convexity), not its magnitude, to license the
  tangent-line-below-the-curve argument — the magnitude of `f'`/`f''` only
  matters for computing a *specific* `G` at `M>1`, which lane (a) never
  does. There's also a second, even more elementary argument bound.md gives
  ("a selection over one candidate is not a selection") that needs no
  convexity at all. **Both arguments are correct; "no f'' table applies to
  this lane" is justified.**
- Single-target reference costs (140.1994731076207 / 200.9587149140538 /
  270.7236234535225, betas 389/606/855, d 1005/1420/1867) verified exactly
  against `BATCH-a51f91/TASK-20260805-9672b3/results.json`'s `baselines`
  block.
- `receipt.json`'s claim `matches_T3_receipt_declared_hash: true` for
  `results.json` and `verification.json`: I independently confirmed both —
  T3's own `receipt.json.artifacts` declares
  `results.json` sha256 `9d2cedc97def...` and `verification.json` sha256
  `7e56af508982...`, both matching B2-B's `receipt.json`
  `sha256_recomputed_by_this_task` values exactly.
- **Defect found (DEF-1, minor):** `fpp_sensitivity.json` Section A and B
  each quote an `ols_residual_sd_bits` / `ols_residual_sd_blocks` figure and
  attribute it (via `reused_from`) to T3's check `V7_...` (Section A) or
  `V5_...` (Section B) respectively. I read T3's actual
  `verification.json` directly: those two specific residual-sd fields live
  under check **`V6_slope_of_the_optimiser_vs_the_linearised_slope`**, not
  V5 or V7 (V5 has only anomalous-pair counts and drops; V7 has only the
  OLS bits-per-block figures, no residual sd). The **values themselves are
  byte-exact correct** (I checked all nine numbers — 3 sets × 3 fields —
  digit-for-digit against `verification.json`), so nothing is fabricated;
  only the check-ID citation is wrong for those two specific numbers within
  otherwise-correctly-cited sections.

## 6. B2-C (finding.md) — spot-checked quotations

Per the mandate to "spot-check several, not just the first one," I checked
**13 rows/clauses** against `census.json` directly (not against
`finding.md`'s own paraphrase): R01, R03, R09, R10, R11, R12, R13, R14, R20,
R21, R22, R23, R24. **All 13 matched verbatim**, including section numbers,
and including the two-limb delegation-chain quote from R13
(`draft-ietf-tls-hybrid-design-16` Sec. 2, "...abides by any bounds in the
specification of the KEM **or subsequent security analyses**") which
`finding.md` correctly bold-flags as its own added emphasis, not present in
the source's plain-text field (I confirmed `'**' in field` is indeed absent
from R13's/R24's raw `census.json` strings).

Row-count arithmetic: `finding.md`'s "2+2+2+8=14" total-check verified
against `census.json`'s own `row_counts.deployment_mode: 14` and the
`distribution_sentence`'s own row list (R09,R12,R14,R20,R21,R22 as the "6
fix M=1" bucket) — matches CX-1's split exactly.

**No defects found in B2-C.** Its own `receipt.json` additionally discloses
a self-run quotation-integrity check (four splice/punctuation errors found
and corrected before delivery) — a sign of care rather than a defect.

## 7. B2-D (acquisition table) — checked the hash-instability attribution

Independently verified (from `receipt.json`'s own logged `curl` output):
route (OpenAlex → `locations[1]` TU/e, not `best_oa_location`/ACM which
403's), HTTP 200, `application/pdf`, byte count 1,832,736 (all 5 fetches),
page count 17 (via `/Type/Page` object count, cross-checked against
`/Type/Pages/Count`), and — critically — **5 different sha256 values across
5 fetches of the identical URL**, none matching
`RT-20260806-d008e0`'s reported hash, confirmed with three independent
hashing tools (`sha256sum`, `openssl dgst`, Python `hashlib`). These are
genuine, carefully cross-checked raw measurements; I have no basis to doubt
them as *measurements*.

**Defect found (DEF-2, material):** the *causal attribution* of this
phenomenon specifically to **"the TU/e repository's per-request serving"**
is asserted as established fact in `acquisition_procedure.md` ("a real,
previously undocumented property of at least the TU/e repository server
tested here"), and repeated as settled fact in the Coordinator's own commit
message/`snapshot_receipt.json` headline ("a genuine hash-instability
finding... in the TU/e repository's per-request serving... not smoothed
over"). But **every one of B2-D's fetches, per its own `receipt.json`
`network_environment` block, went through this sandboxed harness's
pre-configured local egress/TLS-interception proxy** (`HTTPS_PROXY`,
disclosed to me directly in my own environment context as present for
*every* outbound HTTPS request in this environment) — a plausible
alternative source of small per-request byte-level differences that was
never tested. No **null-object control** was run: e.g. re-fetching an
unrelated, presumably content-stable static resource multiple times through
the same proxy path, to see whether similar instability appears generically
(which would indict the local proxy) or not (which would support the
server-side attribution). Per `docs/inventor-protocol.md` §3, an unusual
signal needs to be checked against a null object of the same shape before
being read as a property of the thing under study; that was not done here.

Notably, `receipt.json`'s own diagnosis is **more careful** than
`acquisition_procedure.md`'s: `receipt.json`
(`part2_independent_reproduction.anomaly.interpretation_offered_not_asserted_as_fact`)
explicitly says "this task does not have access to the server's
implementation and does not assert this as a confirmed root cause — it is
the most parsimonious explanation of the observed byte-diff location." That
hedge is correct and appropriately scientific. `acquisition_procedure.md`
then states the same finding *without* the hedge, as an established
property of the server — an internal inconsistency between B2-D's own two
deliverables. The Coordinator's headline inherits the unhedged version.

This does not touch route/status/byte-count/page-count/document-identity,
which are all independently reproduced and accurate, and it does not affect
the correctly-preserved scope caveat (CCS'21 published version vs. ePrint
PDF, restated verbatim from the red team's own words). It is a defect in
the *strength of a causal claim* that gets institutionalized forward as a
procedural rule (`acquisition_procedure.md`'s "Hash stability" section,
made "a required check" going forward), not a defect in the primary
measurements.

## 8. Coordinator commit-message audit (mandate item 6)

Read `git log -1 --format=%B 8a121df9` in full and checked every quoted
figure against the producer artifact it cites. Findings:

- **DEF-3 (minor):** "P3 ... holds in all four cells by 46.8-73.2 SE" — the
  correct one-decimal rounding of the true maximum (73.14551...) is 73.1,
  not 73.2 (see §2 above). A small rounding slip, not a fabrication; the
  string "73.2" does not appear in any producer artifact I read.
- **DEF-4 (material, derivative of DEF-2):** the B2-D paragraph states the
  hash-instability finding as unhedged fact ("a genuine... finding... in
  the TU/e repository's per-request serving"), losing B2-D's own
  `receipt.json` hedge. See §7.
- Everything else I checked in the commit message — P4's 0.06-0.88 SE
  range, P5's 0.8926/0.8903 vs 0.8018/0.8257 and 7.8-11.3% figures, B2-B's
  0.27416-0.28039 bits/block and 4.14-6.51% overstatement figures, B2-C's
  row counts, B2-D's route/status/byte/page reproduction figures, the
  `coordinator_amendment` for B2-A's 8 extra files (verified against
  `receipt.json`'s own `extra_files_beyond_the_declared_five` /
  `file_sha256` — accurate) — **matched the producer artifacts exactly.**
  This is a marked improvement over the prior batch's commit
  (`DEC-20260805-4823db` CE-1: a wholly fabricated "30-100x" figure); this
  commit's only numeric issues are one one-digit rounding slip (DEF-3) and
  one attribution-hedge loss (DEF-4), not a fabrication.
- Parent commit `da16e6d3` verified as the actual git parent of `8a121df9`.

## 9. Independence disclosure

This validator session, and every one of B2-A/B2-B/B2-C/B2-D's own
`receipt.json` `inference.resolved_model_id` fields, read `claude-sonnet-5`.
Per this session's own system context I am also Sonnet 5. Independence here
is **procedural only** (independent session, independently-written code,
no code or reasoning shared with any producer), consistent with this
campaign's own disclosed limitation
(`GOAL-MLKEM-005.yaml inherited_constraints`: "Independence has been
procedural, never model-level").

---

## Appendix: full script text and full output

### `rederive_p3_p4_p5.py`

```python
#!/usr/bin/env python3
"""
Independent re-derivation of B2-A's P3, P4, P5 adjudications directly from
results.json's raw per-draw data (ratio_2em10_over_draws arrays), computed
from scratch with numpy's ddof=1 sample standard deviation -- NOT copied
from the report's own P3_sensitivity / P4_gaussian_null_of_null /
P5_falsifier_adjudication summary blocks. Those summary blocks are read only
AFTER independent computation, for comparison.
"""
import json
import math
import numpy as np

RESULTS = "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-5a4656/tasks/TASK-20260806-b51ac8/results.json"

d = json.load(open(RESULTS))
cells = ["d100_b30", "d100_b40", "d140_b30", "d140_b40"]

def per_draw_ratios(arm):
    """Extract raw per-draw ratio_2^-10 values from per_draw list -- the
    'ratio_2em10_over_draws' sibling field is a SUMMARY (mean/sd/min/max),
    not raw draws."""
    return np.array([pd["p2em10"]["ratio"] for pd in arm["per_draw"]], dtype=float)

p4_table = {}
for c in cells:
    arm = d["cells"][c]["arms"]["gaussian_null_of_null"]
    draws = per_draw_ratios(arm)
    summary = arm["ratio_2em10_over_draws"]
    assert math.isclose(draws.mean(), summary["mean"], rel_tol=1e-9)
    assert math.isclose(draws.std(ddof=1), summary["sd"], rel_tol=1e-9)
    mean = draws.mean(); sd = draws.std(ddof=1); se = sd / math.sqrt(8)
    dev = abs(mean - 1.0); dev_in_se = dev / se; met = dev_in_se <= 4.0
    p4_table[c] = dict(mean=mean, sd=sd, se=se, dev=dev, dev_in_se=dev_in_se, met=met)
    reported = d["cells"][c]["P4_gaussian_null_of_null"]
    # ... print comparisons (see rederive_output.txt for full transcript)

p3_table = {}
for c in cells:
    graded = d["cells"][c]["arms"]["graded"]
    t0 = per_draw_ratios(graded["t0.00"]); t1 = per_draw_ratios(graded["t1.00"])
    mean_t0 = t0.mean(); sd_t0 = t0.std(ddof=1)
    mean_t1 = t1.mean(); sd_t1 = t1.std(ddof=1)
    se_unpaired = math.sqrt(sd_t0**2 + sd_t1**2) / math.sqrt(8)
    shift = mean_t0 - mean_t1
    shift_in_se = shift / se_unpaired
    met_directional = shift >= 4.0 * se_unpaired
    p3_table[c] = dict(shift=shift, shift_in_se=shift_in_se, met=met_directional)

pred = d["frozen_prediction"]["P5_falsifier"]["predicted_decay_ratio_beta40_over_beta30_at_fixed_d"]
for dd in [100, 140]:
    dep30 = p3_table[f"d{dd}_b30"]["shift"]; dep40 = p3_table[f"d{dd}_b40"]["shift"]
    ratio = dep40 / dep30
    predicted = pred[f"d{dd}"]
    rel_disc = (ratio - predicted) / predicted
    # ... compared against results.json P5_falsifier_adjudication (see transcript)
```

(Full runnable script with all print statements and assertions was executed
in this session; the transcript below is its complete, unedited stdout.)

### Full transcript: `rederive_output.txt`

```
====================================================================================================
P4 RE-DERIVATION (Gaussian null-of-the-null)
====================================================================================================

-- d100_b30 --
  raw draws (ratio_2em10): [0.99161272 0.99921245 1.0015429  0.99733684 0.99896587 0.99809903
 1.00398524 1.00156511]
  my mean=0.9990400191  reported mean=0.9990400191  match=True
  my sd(ddof=1)=0.0037048615  reported sd=0.0037048615  match=True
  my SE=0.0013098664  reported SE=0.0013098664  match=True
  my |dev|=0.0009599809  reported |dev|=0.0009599809  match=True
  my dev_in_SE=0.732885  reported dev_in_SE=0.732885  match=True
  my met(<=4SE)=True  reported met=True  MATCH=True

-- d100_b40 --
  raw draws (ratio_2em10): [0.99833168 0.99984415 1.00120418 1.00072907 1.00294528 0.99798811
 0.99747672 0.99564499]
  my mean=0.9992705227  reported mean=0.9992705227  match=True
  my sd(ddof=1)=0.0023478704  reported sd=0.0023478704  match=True
  my SE=0.0008300975  reported SE=0.0008300975  match=True
  my |dev|=0.0007294773  reported |dev|=0.0007294773  match=True
  my dev_in_SE=0.878785  reported dev_in_SE=0.878785  match=True
  my met(<=4SE)=True  reported met=True  MATCH=True

-- d140_b30 --
  raw draws (ratio_2em10): [1.00297684 1.00337761 1.001201   1.00064462 0.99861419 0.99754224
 1.0010216  0.99510063]
  my mean=1.0000598414  reported mean=1.0000598414  match=True
  my sd(ddof=1)=0.0028058010  reported sd=0.0028058010  match=True
  my SE=0.0009920005  reported SE=0.0009920005  match=True
  my |dev|=0.0000598414  reported |dev|=0.0000598414  match=True
  my dev_in_SE=0.060324  reported dev_in_SE=0.060324  match=True
  my met(<=4SE)=True  reported met=True  MATCH=True

-- d140_b40 --
  raw draws (ratio_2em10): [1.00233702 0.9957554  0.99806497 1.00247851 1.0037742  1.00089135
 0.99773783 1.00331863]
  my mean=1.0005447374  reported mean=1.0005447374  match=True
  my sd(ddof=1)=0.0029799686  reported sd=0.0029799686  match=True
  my SE=0.0010535780  reported SE=0.0010535780  match=True
  my |dev|=0.0005447374  reported |dev|=0.0005447374  match=True
  my dev_in_SE=0.517036  reported dev_in_SE=0.517036  match=True
  my met(<=4SE)=True  reported met=True  MATCH=True

====================================================================================================
P3 RE-DERIVATION (coordinate-aligned t=0 vs Haar t=1, SE of unpaired difference)
====================================================================================================

-- d100_b30 --
  t0 draws: [1.09443538 1.10363237 1.09248448 1.09322066 1.09248448 1.10363237
 1.10363237 1.09386566]
  t1 (haar) draws: [1.00160241 0.9991679  1.00183127 1.00007112 1.00057855 1.00091999
 0.99761462 0.99467497]
  graded.t0.00 identical to coord_aligned arm: True
  graded.t1.00 identical to haar_null arm: True
  my mean_t0=1.0971734730  reported=1.0971734730  match=True
  my sd_t0=0.0053876716  reported=0.0053876716  match=True
  my mean_t1=0.9995576033  reported=0.9995576033  match=True
  my sd_t1=0.0023988133  reported=0.0023988133  match=True
  my SE_unpaired=0.0020851052  reported=0.0020851052  match=True
  my shift=0.0976158697  reported=0.0976158697  match=True
  my shift_in_SE=46.815800  reported=46.815800  match=True
  my met_directional(>=4SE)=True  reported=True  MATCH=True
  [diagnostic] corr(t0,t1) over the 8 draw indices = -0.1458
  [diagnostic] paired-style SE (using observed corr) = 0.0021951891 vs unpaired SE = 0.0020851052

-- d100_b40 --
  t0 draws: [1.08782056 1.08731759 1.08206489 1.08206489 1.08842998 1.08731759
 1.08689552 1.08731759]
  t1 (haar) draws: [0.99993427 0.99838863 0.99579229 1.00213793 0.99719106 0.99731855
 1.00092614 1.00050356]
  graded.t0.00 identical to coord_aligned arm: True
  graded.t1.00 identical to haar_null arm: True
  my mean_t0=1.0861535741  reported=1.0861535741  match=True
  my sd_t0=0.0025637809  reported=0.0025637809  match=True
  my mean_t1=0.9990240519  reported=0.9990240519  match=True
  my sd_t1=0.0021859368  reported=0.0021859368  match=True
  my SE_unpaired=0.0011911807  reported=0.0011911807  match=True
  my shift=0.0871295223  reported=0.0871295223  match=True
  my shift_in_SE=73.145511  reported=73.145511  match=True
  my met_directional(>=4SE)=True  reported=True  MATCH=True
  [diagnostic] corr(t0,t1) over the 8 draw indices = -0.0450
  [diagnostic] paired-style SE (using observed corr) = 0.0012173491 vs unpaired SE = 0.0011911807

-- d140_b30 --
  t0 draws: [1.0946489  1.09416495 1.09017794 1.0946489  1.08880144 1.08880144
 1.09795103 1.09082143]
  t1 (haar) draws: [1.00008682 0.99636574 1.00192667 1.00182404 0.99507893 0.99576698
 1.00529422 0.99634814]
  graded.t0.00 identical to coord_aligned arm: True
  graded.t1.00 identical to haar_null arm: True
  my mean_t0=1.0925020026  reported=1.0925020026  match=True
  my sd_t0=0.0033228544  reported=0.0033228544  match=True
  my mean_t1=0.9990864432  reported=0.9990864432  match=True
  my sd_t1=0.0037240162  reported=0.0037240162  match=True
  my SE_unpaired=0.0017645700  reported=0.0017645700  match=True
  my shift=0.0934155594  reported=0.0934155594  match=True
  my shift_in_SE=52.939560  reported=52.939560  match=True
  my met_directional(>=4SE)=True  reported=True  MATCH=True
  [diagnostic] corr(t0,t1) over the 8 draw indices = 0.7209
  [diagnostic] paired-style SE (using observed corr) = 0.0009400189 vs unpaired SE = 0.0017645700

-- d140_b40 --
  t0 draws: [1.08199704 1.08075347 1.08658179 1.08395719 1.08395719 1.08825864
 1.08658179 1.07745093]
  t1 (haar) draws: [1.00355055 1.00467365 0.99881285 0.99925388 0.99720372 0.99986632
 0.99935662 1.00151101]
  graded.t0.00 identical to coord_aligned arm: True
  graded.t1.00 identical to haar_null arm: True
  my mean_t0=1.0836922547  reported=1.0836922547  match=True
  my sd_t0=0.0035487508  reported=0.0035487508  match=True
  my mean_t1=1.0005285771  reported=1.0005285771  match=True
  my sd_t1=0.0025274058  reported=0.0025274058  match=True
  my SE_unpaired=0.0015403495  reported=0.0015403495  match=True
  my shift=0.0831636776  reported=0.0831636776  match=True
  my shift_in_SE=53.990135  reported=53.990135  match=True
  my met_directional(>=4SE)=True  reported=True  MATCH=True
  [diagnostic] corr(t0,t1) over the 8 draw indices = -0.5738
  [diagnostic] paired-style SE (using observed corr) = 0.0019129050 vs unpaired SE = 0.0015403495

====================================================================================================
P5 RE-DERIVATION (falsifier: 1/sqrt(beta) decay)
====================================================================================================

-- d=100 --
  my departure(beta=30)=0.09761587  reported=0.09761587  match=True
  my departure(beta=40)=0.08712952  reported=0.08712952  match=True
  my measured ratio=0.892575  reported=0.892575  match=True
  predicted ratio=0.801784  reported predicted=0.801784
  my relative discrepancy=11.3237%  reported=11.3237%  match=True
  both positive: True  reported both_positive=True
  decays (dep40<dep30): True  reported decays_beta40_lt_beta30=True

-- d=140 --
  my departure(beta=30)=0.09341556  reported=0.09341556  match=True
  my departure(beta=40)=0.08316368  reported=0.08316368  match=True
  my measured ratio=0.890255  reported=0.890255  match=True
  predicted ratio=0.825723  reported predicted=0.825723
  my relative discrepancy=7.8152%  reported=7.8152%  match=True
  both positive: True  reported both_positive=True
  decays (dep40<dep30): True  reported decays_beta40_lt_beta30=True

====================================================================================================
SUMMARY TABLE
====================================================================================================
cell        P4 dev/SE  P4 met  P3 shift/SE  P3 met
d100_b30       0.7329    True      46.8158    True
d100_b40       0.8788    True      73.1455    True
d140_b30       0.0603    True      52.9396    True
d140_b40       0.5170    True      53.9901    True
```

### `compare_run1_run2.py` — full output

```
====================================================================================================
PART A: P1-P5 fields, claimed bit-for-bit identical
====================================================================================================
[all 4 cells x 11 field groups: identical=True, 44/44]
(top)      P5_falsifier_adjudication           identical=True
(top)      frozen_prediction (P1-P5 statements) identical=True

ALL P1-P5-RELEVANT FIELDS BIT-FOR-BIT IDENTICAL ACROSS RUN1/RUN2: True

====================================================================================================
PART B: interior graded-family t-points (0<t<1), claimed to DIFFER (D-1 defect)
====================================================================================================
d100_b30   t0.05    identical=False  mean_run1=1.002853  mean_run2=1.087982  delta=+0.085129
d100_b30   t0.10    identical=False  mean_run1=1.000983  mean_run2=1.077828  delta=+0.076845
d100_b30   t0.25    identical=False  mean_run1=0.999976  mean_run2=1.051626  delta=+0.051650
d100_b30   t0.50    identical=False  mean_run1=0.999972  mean_run2=1.019055  delta=+0.019083
d100_b30   t0.75    identical=False  mean_run1=0.999785  mean_run2=1.004836  delta=+0.005051
d100_b40   t0.05    identical=False  mean_run1=0.999731  mean_run2=1.076819  delta=+0.077088
d100_b40   t0.10    identical=False  mean_run1=0.999255  mean_run2=1.067901  delta=+0.068647
d100_b40   t0.25    identical=False  mean_run1=0.998290  mean_run2=1.042702  delta=+0.044412
d100_b40   t0.50    identical=False  mean_run1=0.998304  mean_run2=1.012214  delta=+0.013910
d100_b40   t0.75    identical=False  mean_run1=0.998904  mean_run2=1.000566  delta=+0.001662
d140_b30   t0.05    identical=False  mean_run1=1.000329  mean_run2=1.082095  delta=+0.081767
d140_b30   t0.10    identical=False  mean_run1=1.000079  mean_run2=1.074168  delta=+0.074089
d140_b30   t0.25    identical=False  mean_run1=0.998878  mean_run2=1.048879  delta=+0.050001
d140_b30   t0.50    identical=False  mean_run1=0.998041  mean_run2=1.017698  delta=+0.019657
d140_b30   t0.75    identical=False  mean_run1=0.998942  mean_run2=1.003054  delta=+0.004112
d140_b40   t0.05    identical=False  mean_run1=1.000781  mean_run2=1.074191  delta=+0.073410
d140_b40   t0.10    identical=False  mean_run1=0.999789  mean_run2=1.065887  delta=+0.066098
d140_b40   t0.25    identical=False  mean_run1=0.999671  mean_run2=1.043564  delta=+0.043892
d140_b40   t0.50    identical=False  mean_run1=0.999844  mean_run2=1.015907  delta=+0.016063
d140_b40   t0.75    identical=False  mean_run1=1.000055  mean_run2=1.003735  delta=+0.003680

AT LEAST ONE INTERIOR (0<t<1) POINT DIFFERS BETWEEN RUNS: True

====================================================================================================
PART C: additional arms NOT part of the graded family (unreduced_qary, lll_only)
====================================================================================================
[all 4 cells x 2 arms: identical=True, 8/8]

====================================================================================================
PART D: graded_family_summary (aggregated monotonicity table)
====================================================================================================
d100_b30   run1 monotone_nonincreasing=True   run2=True
d100_b40   run1 monotone_nonincreasing=False  run2=True
d140_b30   run1 monotone_nonincreasing=False  run2=True
d140_b40   run1 monotone_nonincreasing=False  run2=True
```

(Both scripts were run in this session against the committed `results.json`
and `results_run1_raw.json`, whose sha256 I verified against the snapshot
receipt in §0 before use.)
