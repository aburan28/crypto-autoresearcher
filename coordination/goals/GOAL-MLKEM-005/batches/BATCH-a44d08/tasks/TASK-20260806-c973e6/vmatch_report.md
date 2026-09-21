# SECTION C — the matched-`V` cross-family comparison, reproduced ON THE COMMITTED BASES

TASK-20260806-c973e6 / BATCH-a44d08 / GOAL-MLKEM-005
Executor artifact. **Observations only.** No status change, no hypothesis
movement, no evidence record, no interpretation beyond the declared verdicts of
`prereg.md` §4.4. Whether the frozen criterion's verdict is *believed* is for the
Reviewer and the Coordinator; this report records what was measured.

**Claim tier TOY, unconditionally.** Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model. `V`, `m3`
and `D` are properties of a basis **presentation**, not of a lattice
(`prereg.md` §1.1); no verdict below is offered as an AM-4 adjudicator.

---

## 0. Notarized pre-registration — verified, and quoted

```
sha256(prereg.md) = 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
prereg bytes      = 54928
```

Four independent sources were compared and **all four agree**:

| source | value |
|---|---|
| recomputed by this run (`hashlib.sha256`) | `8d00ca3f…a2a6c80` |
| expected sha256 stated in the dispatch task | `8d00ca3f…a2a6c80` |
| `snapshot-receipt.json` → `archive.path_sha256[prereg.md]` | `8d00ca3f…a2a6c80` |
| `snapshot-receipt.json` → `prereg_sha256` field | `8d00ca3f…a2a6c80` |
| producer sidecar `prereg_sha256.txt` | `8d00ca3f…a2a6c80` |

Independently re-verified at the shell with `shasum -a 256`: identical.

**Ancestry, asserted against the NOTARIZING COMMIT ITSELF and not its parent**
(`prereg.md` §0.2, correction V-7):

```
git merge-base --is-ancestor 9cb2d3e28ae7a474edbb116d694969470829e112 HEAD  ->  true
HEAD at run time = 974ad579443984d9369ac050dadd800caa5d10f4
branch           = feat/crypto-autoresearcher-kb-adfc38
worktree dirty   = yes, and only with UNTRACKED task directories of this batch:
                   TASK-20260806-3084bc/, TASK-20260806-c973e6/, TASK-20260806-e17677/
```

`prereg.md` was opened read-only and was not modified. This run made no git
write and no commit.

---

## 1. THE PLAIN ANSWER, stated either way as the dispatch requires

**Does the red team's matched-`V` effect reproduce against the committed bases?**

**Partly, and the "partly" is the result. Direction reproduces everywhere;
falsifying strength does not reproduce in the red team's own cell, and does
reproduce — decisively in one case — in two cells the red team never probed.**

Concretely, and with nothing rounded:

1. **Under the frozen §4.4 criterion the family verdict on the committed bases
   is `L2 TAIL-SUFFICIENCY FALSIFIED`.** Two of the ten scored pairs are
   FALSIFYING PAIRS. The verdict is the same under the declared `n_C = 12`
   critical value `3.6358074219539622` **and** under the `prereg.md` §4.3/§4.5
   recomputation at the realized `n_C = 10` (critical value
   `3.4994832973505026`).
2. **In `(d, beta) = (100, 30)` — the only cell the red team probed — the effect
   does NOT reach falsifying strength on the committed bases.** The largest
   relative difference there is `5.38%` at `|t| = 1.300`, against that pair's own
   detection floor of `15.03%`. No pair in that cell is a FALSIFYING PAIR, and
   the red team's `|t|` of `-1.91 / -3.45 / +1.41` and ratios `0.931 / 0.799 /
   1.119` are **not** reproduced in magnitude on the committed frames.
3. **The sign does reproduce in `(100, 30)`.** The red team found `D_TL < D_GR`
   at matched `V` in its two larger-`V` pairs; the committed-basis
   `graded_t0.0050` pair here gives `D_GR - D_TL = +0.00199221`, the same
   direction. The one committed-basis pair with the opposite sign,
   `d100_b30 graded_t0.0025`, has `|t| = 0.080`.
4. **The falsification is carried entirely by two pairs in cells the red team
   never probed**: `d100_b40 graded_t0.0075` (`|t| = 3.689`, relative `17.48%`)
   and `d140_b40 graded_t0.0050` (`|t| = 8.148`, relative `23.74%`). The first
   clears its critical value by `1.5%` of the critical value and is fragile; the
   second does not depend on which critical value is used.
5. **The eight non-falsifying pairs are NOT evidence of agreement.** Every one of
   them is individually unresolving: their detection floors run from `6.29%` to
   `17.23%` relative, all above the `5%` effect size the design calls
   practically meaningful. Each is an upper bound at its own floor and is
   reported as one. Under `prereg.md` §4.4 an unresolving pair is never rounded
   into agreement, and none is here.

**What this does NOT say (`prereg.md` §4.1, binding, in those words).**
`Var(e^T P e) = 2*beta + (mu_4 - 3)(V + beta^2/d)` **is** a function of `V`
alone, so **L2's derivation is correct at second order, and nothing in this run
contradicts it.** The frozen criterion addresses only whether the `2^-10` tail
quantile inherits that sufficiency; the third cumulant involves
`sum_a P_aa^3` independently of `V`. A `FALSIFIED` verdict here refutes the
**tail-level** claim and **not** the variance-level derivation.

---

## 2. What was reproduced, and what "the committed bases" means here

The red team's probe (`BATCH-f19c37/reviews/TASK-20260806-ca8dc7/l2_vmatch.py`)
used its own objects: `seed_graded = 500000 + j`, error seed `20260806 + d`
(the committed *Gaussian-null* seed, not the CBD one), a random-permutation TL
support, and `D` measured as a raw shift against its own Haar arm. Its `D`
values are therefore not absolutely comparable to the committed instrument's.

This run replaces every one of those with the committed object:

| ingredient | committed value used here |
|---|---|
| graded seeds | `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j` |
| error seeds | `seed_error(d) = 20260805 + d`, CBD_{eta=2}, `N = 2^20`, chunk `2^15` |
| basis seeds | `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i`, fpylll `qary`, `k = d/2`, `q = 3329` |
| frame | last `beta` columns of `Q` from `QR(B^T)`, float32, via the `BETA_MAX = 60` tail slice |
| estimator | `D = sort(R)[1023] / q_Beta(2^-10) - 1`, `q_Beta = betaincinv(beta/2,(d-beta)/2,2^-10)` |
| draws | `8` per arm, all arms sharing the same `2^20` error vectors |

**NO LLL AND NO BKZ WAS RUN.** The unreduced arm is read from the raw q-ary
basis exactly where `BATCH-436ddd`'s `reduce_one` reads it, before any reduction.

### 2.1 Reproduction check against the committed measurement — the thing that makes "the committed bases" verified rather than asserted

Every GR and unreduced arm this run regenerates was compared, per draw, against
`BATCH-f19c37/tasks/TASK-20260806-ca4377/results.json`:

| cells | max abs deviation in `D` | max abs deviation in `V` | bitwise identical `D`? |
|---|---|---|---|
| `d100_b30`, `d100_b40` | `0` (exactly) | `3.0e-07` | **yes, all draws** |
| `d140_b30`, `d140_b40` | `2.22e-16` | `2.1e-07` | no — one ULP |

The one-ULP difference in the two `d = 140` cells is fully accounted for: this
session's `scipy.special.betaincinv` returns `q_Beta(2^-10)` one ULP away from
the committed value in exactly those two cells
(`d140_b30`: `0.089292887180437708` vs `0.089292887180437722`;
`d140_b40`: `0.14038737713830945` vs `0.14038737713830948`; identical in both
`d = 100` cells). The `V` deviations of order `2e-07` are float32 frame-ULP
level and arise from LAPACK/`numpy.linalg.qr` differences between the two
sessions. Both are recorded as instrument facts, not results.

**Are those deviations large enough to matter?** Measured on the committed
graded path, `dD/dV` over the low-`t` steps is `0.0028` to `0.0048` per unit `V`
across the four cells (post-processing of committed values, no new
measurement). A `V` perturbation of `3e-07` therefore moves `D` by about
`1.4e-09`, against measured pair differences of `1.3e-04` to `6.3e-03`. That is
five to six orders of magnitude below the effect and cannot produce it.

---

## 3. Target selection under §4.3 — the rule, and every exclusion

Selection uses no measurement of `D`: only the deterministic frame scalar `V`.

| cell | TL-reachable `V` | degenerate `V` | survivors (t) | rule applied | chosen (t) | unreduced arm |
|---|---|---|---|---|---|---|
| `d100_b30` | `[6.000000, 21.000000]` | `21.000000` | `0.0025, 0.005` | exactly two survive → take both | `0.0025, 0.005` | `V = 9.362794`, reachable, **used** |
| `d100_b40` | `[4.000000, 24.000000]` | `24.000000` | `0.0025, 0.005, 0.0075, 0.01` | first and third by `t` ascending | `0.0025, 0.0075` | `V = 16.244628`, reachable, **used** |
| `d140_b30` | `[8.571429, 23.571429]` | `23.571429` | `0.0025` | exactly one survives → take it | `0.0025` | `V = 6.750435`, **UNREACHABLE, excluded** |
| `d140_b40` | `[8.571429, 28.571429]` | `28.571429` | `0.0025, 0.005` | exactly two survive → take both | `0.0025, 0.005` | `V = 11.807462`, reachable, **used** |

`t = 0` is excluded in every cell by the §4.3 step-3 degeneracy rule at
tolerance `1e-9`: its `V` equals `beta(1 - beta/d)` exactly, to `0` or
`7.1e-15`. All other exclusions are `UNREACHABLE` for TL. The mean-`V` and the
all-8-draws reachability criteria agree at every grid point in every cell; no
point is reachable by one and not the other.

**Recorded objection, run anyway (`prereg.md` §5.5).** §4.3 step 5 states
parenthetically that the four committed unreduced `V` values
`9.3628 / 16.2446 / 6.7504 / 11.8075` are "all inside the reachable intervals
above". **That is not correct for `(140, 30)`**: `6.750435` lies below that
cell's TL minimum `V_TL(1/2) = 8.571429`, and all eight draws are below it. The
frozen rule of §4.2 — "a target `V` outside the reachable interval is declared
`UNREACHABLE` and excluded, with the exclusion reported" — was applied, the
target was excluded, and the objection is recorded here and in
`vmatch.json.objections_recorded_and_run_anyway`. No threshold was changed.

**`n_C` accounting.** Declared `n_C = 12` (fpylll 0.6.4 IS available, so the
`n_C = 8` branch does not apply). Realized `n_C = 10`: `(140, 30)` contributes
one target instead of three (one graded survivor; unreduced UNREACHABLE). **Zero
pairs were excluded for non-informativeness** — every one of the ten scored
pairs clears the §4.5 `m3` separation requirement, most by a wide margin.

---

## 4. Every `D` beside the third diagonal moment `m3 = sum_a (P_aa - beta/d)^3` of its frame

Values are means over the 8 draws; per-draw values are in `vmatch.json`.
`floor` is the §4.4 detection floor
`|t|crit * SE / max(|D_GR|,|D_TL|)` at the declared `n_C = 12`.

| cell | target | V (matched) | m3 GR | m3 TL | D GR | D TL | D_GR - D_TL | SE | \|t\| | rel diff | floor | INFORM | FALSIFYING |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 12.951247 | +4.070781 | +3.570748 | +0.05758667 | +0.05771864 | -0.00013197 | 1.656e-03 | 0.080 | 0.23% | 10.43% | yes | no |
| d100_b30 | graded_t0.0050 | 8.473481 | +2.155150 | +0.884088 | +0.03705014 | +0.03505793 | +0.00199221 | 1.532e-03 | 1.300 | 5.38% | 15.03% | yes | no |
| d100_b30 | unreduced | 9.362794 | +0.321742 | +1.417676 | +0.03761620 | +0.03956477 | -0.00194857 | 1.200e-03 | 1.624 | 4.93% | 11.03% | yes | no |
| d100_b40 | graded_t0.0025 | 14.778516 | +2.318539 | +2.033555 | +0.05200001 | +0.05149185 | +0.00050816 | 1.072e-03 | 0.474 | 0.98% | 7.49% | yes | no |
| d100_b40 | graded_t0.0075 | 6.546441 | +0.680289 | -0.436068 | +0.02285961 | +0.01886438 | +0.00399523 | 1.083e-03 | 3.689 | 17.48% | 17.23% | yes | **YES** |
| d100_b40 | unreduced | 16.244628 | +0.287507 | +2.473389 | +0.05549318 | +0.05758659 | -0.00209341 | 9.955e-04 | 2.103 | 3.64% | 6.29% | yes | no |
| d140_b30 | graded_t0.0025 | 12.476462 | +5.186319 | +3.959416 | +0.04816919 | +0.04765238 | +0.00051681 | 1.065e-03 | 0.485 | 1.07% | 8.04% | yes | no |
| d140_b40 | graded_t0.0025 | 15.234807 | +4.767765 | +3.671356 | +0.04362991 | +0.04251620 | +0.00111371 | 1.360e-03 | 0.819 | 2.55% | 11.33% | yes | no |
| d140_b40 | graded_t0.0050 | 9.086503 | +2.192117 | -0.281126 | +0.02638101 | +0.02011863 | +0.00626238 | 7.686e-04 | 8.148 | 23.74% | 10.59% | yes | **YES** |
| d140_b40 | unreduced | 11.807462 | +0.324959 | +1.468062 | +0.02959157 | +0.03218091 | -0.00258934 | 1.061e-03 | 2.440 | 8.05% | 11.99% | yes | no |

Readings that must not be lost:

* **`m3` separation is large at every scored pair**, from `12.3%` (`d100_b40
  graded_t0.0025`) to `>100%` (the pairs where `m3_TL` changes sign). The `V`
  match is exact to the precision reported in §5; the `m3` mismatch is the
  candidate mechanism and it is what the design intends to vary.
* **The two FALSIFYING PAIRS are the two pairs where `m3_TL` is NEGATIVE while
  `m3_GR` is positive** (`-0.436068` vs `+0.680289`; `-0.281126` vs
  `+2.192117`). They are also the two smallest-`V` scored pairs.
* **Sign concordance, POST-HOC and DESCRIPTIVE, uncitable as a result
  (`prereg.md` §5.6).** In `9` of the `10` scored pairs
  `sign(D_GR - D_TL) = sign(m3_GR - m3_TL)`; the single discordant pair has
  `|t| = 0.080`. This was **not** pre-registered, is **not** a declared verdict,
  is **not** scored, and is recorded only because an executor records unexpected
  observations rather than discarding them. Three of the ten pairs (the three
  unreduced arms) have `m3_GR < m3_TL` and all three have `D_GR < D_TL`, which
  is why the concordance is not an artefact of a single family's direction.

---

## 5. The `V`-match tolerance ACTUALLY ACHIEVED, per pair

Two numbers are reported per pair because they answer two different questions,
and only one of them meets the frozen `1e-9`.

* **float64 closed-form residual** — `|V_TL(u_j) - V_GR,j|` from the §4.2
  inverse, which is the quantity `prereg.md` §4.2 describes ("achieved by the
  closed-form inverse above in float64"). **Max over all 80 draws:
  `5.33e-15`. Within the frozen `1e-9` at every draw of every pair.**
* **float32 realized residual** — `|V(Q_TL,j) - V(Q_GR,j)|` recomputed from the
  float32 frame the projection actually consumes, which is the committed
  instrument's frame dtype. **Max over all 80 draws: `2.31e-06`. Above the
  frozen `1e-9`.**

| cell | target | max_j \|V_TL,j - V_GR,j\| (float32 frame, as projected) | mean_j same | max_j \|V_TL(u_j) - V_GR,j\| (float64 closed form) | within frozen 1e-9? |
|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 1.729e-06 | 9.975e-07 | 3.553e-15 | float64 YES / float32 no |
| d100_b30 | graded_t0.0050 | 1.049e-06 | 3.760e-07 | 1.776e-15 | float64 YES / float32 no |
| d100_b30 | unreduced | 1.112e-06 | 6.588e-07 | 1.776e-15 | float64 YES / float32 no |
| d100_b40 | graded_t0.0025 | 1.842e-06 | 1.027e-06 | 5.329e-15 | float64 YES / float32 no |
| d100_b40 | graded_t0.0075 | 1.186e-06 | 6.921e-07 | 1.776e-15 | float64 YES / float32 no |
| d100_b40 | unreduced | 2.305e-06 | 1.391e-06 | 3.553e-15 | float64 YES / float32 no |
| d140_b30 | graded_t0.0025 | 1.396e-06 | 9.146e-07 | 1.776e-15 | float64 YES / float32 no |
| d140_b40 | graded_t0.0025 | 1.670e-06 | 8.184e-07 | 5.329e-15 | float64 YES / float32 no |
| d140_b40 | graded_t0.0050 | 8.842e-07 | 5.727e-07 | 1.776e-15 | float64 YES / float32 no |
| d140_b40 | unreduced | 1.357e-06 | 1.007e-06 | 1.776e-15 | float64 YES / float32 no |


**Recorded deviation, and why the frozen number was not changed.** `1e-9`
absolute is **not attainable at float32 frame precision**: float32 has a
relative resolution of about `1.2e-07`, so a rank-`beta` frame's `P_aa` values
are quantized at that level and `V = sum_a (P_aa - beta/d)^2` inherits a
quantization of order `1e-06`. The tolerance is achievable only if the TL frame
is carried in float64 — but then the TL arm's projection would run in a
different arithmetic from the GR arm's, and the GR arm would no longer
bit-reproduce the committed measurement, which is precisely what this task
exists to do. The committed float32 frame convention was kept, the frozen
tolerance was **not** edited, and the achieved residual is reported honestly in
both conventions (`prereg.md` §5.5).

**Is the residual large enough to matter?** No, by the same `dD/dV` measurement
as §2.1: at `dD/dV <= 0.0048`, the worst residual `2.31e-06` moves `D` by about
`1.1e-08`. The two FALSIFYING PAIRS have `|D_GR - D_TL|` of `4.00e-03` and
`6.26e-03` — five to six orders of magnitude larger. The `V` match cannot be
the source of the observed differences.

---

## 6. NAMED BEFORE THE RUN: the arrangements in which this check could not fail, and the demonstration that it is not in any of them

`prereg.md` §4.6 names three. All three are carried here with computed evidence,
plus the mirror defect (a falsifier that cannot fire).

### Form 1 — F-A1's own defect: scoring co-monotonicity within a single monotone path

*The arrangement.* Along the graded path both `V(t)` and `D(t)` move together,
so "no pair with higher `V` and lower `D`" is forced by the construction and the
test cannot fail.

*Why this run is not in it — structural.* **Every scored pair is cross-family by
construction: `10` cross-family pairs, `0` within-path pairs.** The comparison
is GR (or the unreduced real-lattice arm) against TL at equal `V`. Removing the
within-path pairs is not a filter applied to results; the scored family never
contained one.

*Why this run is not in it — computed, on the committed path.* Post-processing
of `BATCH-f19c37`'s committed values (no measurement made for this block):

| cell | `V` strictly decreasing in `t`? | `D` strictly decreasing in `t`? | ordered pairs with higher `V` and lower `D` | out of |
|---|---|---|---|---|
| `d100_b30` | no | no | 9 | 156 |
| `d100_b40` | yes | no | 4 | 156 |
| `d140_b30` | yes | no | 4 | 156 |
| `d140_b40` | yes | no | 5 | 156 |

**Correction to a sentence inside `vmatch.json`.** The prose field
`could_not_fail_demonstration.form_1_….committed_path_evidence_note` asserts
that the count "is 0 IDENTICALLY". **That sentence is wrong and the computed
field beside it is right**: the counts are `9 / 4 / 4 / 5`. The run record is
immutable and was not edited; the correction is recorded here, in
`run_manifest.yaml`, and is flagged for the Validator. The corrected statement
is narrower and still supports Form 1: **every one of the 22 inversions lies
between grid points with `t >= 0.05`**, on the Haar plateau where `V` has fallen
to `0.31–0.66` and `D` is at its noise floor. In the region the scored
comparison actually inhabits — `t <= 0.01`, `V` from `4.2` to `28.6` — both `V`
and `D` are strictly decreasing in `t` in all four cells, so a within-path
co-monotonicity test restricted to that region **is** vacuous, which is the
F-A1 arrangement, and this run does not use it.

### Form 2 — matching at the degenerate `V = beta(1 - beta/d)`, where both families ARE the same object

*The arrangement.* At the global maximum of `V`, GR at `t = 0` and TL at `u = 1`
are both coordinate projectors on `beta` axes. Agreement is forced by identity,
not by mechanism — the P3 failure, an anchor placed where the statistic attains
its bound.

*Why this run is not in it.* The degenerate point is excluded **by rule**, before
any data, at tolerance `1e-9` (§4.3 step 3), in all four cells. It is excluded
**twice over**: at that point `m3_GR = m3_TL` exactly, so the pair is also
non-informative under §4.5 and could not enter the family even if the degeneracy
rule were dropped. The **minimum distance in `V` from any scored pair to the
degenerate `V`** is `8.05` (`d100_b30`), `7.76` (`d100_b40`), `11.10`
(`d140_b30`), `13.34` (`d140_b40`) — no scored pair is anywhere near it.

*It is retained as a labelled INSTRUMENT CHECK and never as support for
anything*, as §4.6 requires:

|---|---|---|---|---|---|---|---|
| d100_b30 | 21.000000 | +8.400000 | +0.09541610 | +0.09163629 | 3.96% | 2.084 | 0.695 |
| d100_b40 | 24.000000 | +4.800000 | +0.08633408 | +0.08731759 | 1.13% | 1.013 | 0.338 |
| d140_b30 | 23.571429 | +13.469388 | +0.09352337 | +0.09259511 | 0.99% | 0.670 | 0.223 |
| d140_b40 | 28.571429 | +12.244898 | +0.08302658 | +0.07926481 | 4.53% | 4.527 | 1.509 |

The check passes in the sense §4.6 asks for: `V` agrees to `7.1e-15` or better,
`m3` agrees exactly, and `D_GR` and `D_TL` agree to `0.99–4.53%` relative.

**A caution the Reviewer must have, stated plainly and not smoothed over.** The
raw `|t|` at the degenerate point reaches `4.527` in `d140_b40`, which is above
the falsifier's own critical value `3.6358`. That does **not** show the
falsifier misfires on the scored pairs, and the reason is structural: at the
degenerate point TL is **one** frame replicated across all 8 draws
(`sd(D_TL) = 0` exactly, 1 distinct value), so the frozen paired SE
`sd_j(D_GR,j - D_TL,j)/sqrt(8)` omits the TL arm's between-frame variance
entirely and inflates the statistic by exactly `sqrt(1 + n) = 3`. Divided by
that factor the four values are `0.695 / 0.338 / 0.223 / 1.509`, which are
unremarkable. **The scored pairs do not carry this inflation** — their TL arms
have 8 distinct frames (`u_j` matched to `V_GR,j` per draw) and
`sd(D_TL) = 1.6e-04` to `1.4e-03`. The degenerate check is therefore one
null-calibration point of a mis-scaled statistic, not a false-positive rate, and
it is reported as such. A properly powered null calibration of the frozen
statistic — two independent frame families that are genuinely exchangeable at
matched `V`, replicated enough times to estimate a rate — does not exist in this
batch and is named in §9 as a follow-up rather than asserted here.

### Form 3 — a decoy TL family whose `m3` tracks GR's

*The arrangement.* If the second family's `m3` moved with GR's, equal `V` would
imply equal everything and agreement would again be forced.

*Why this run is not in it.* §4.5 requires a **declared** `m3` separation
(`|m3_GR - m3_TL| > 0.10 * max(|m3_GR|,|m3_TL|)`) before a pair may enter the
family, `m3` is reported for every frame in §4, and the realized separations
are `12.3%` at the tightest and exceed `100%` at the two pairs where `m3_TL`
crosses zero. `m3` is a deterministic function of the frames and uses no `D`
value, so this filter cannot be tuned to an outcome. **Zero pairs were excluded
by it**, so it did not act as a selection mechanism either.

Positively: the TL family's `m3` **anti**-tracks GR's over the scored set. As
`V` falls from `15.2` to `6.5`, `m3_GR` stays positive (`+5.19` down to `+0.68`)
while `m3_TL` crosses zero and goes negative (`+3.96` down to `-0.44`). And the
three unreduced arms invert the order entirely (`m3_GR` `+0.29` to `+0.32`
against `m3_TL` `+1.42` to `+2.47`) — a real-lattice frame at `V ≈ 9–16` has a
far smaller third diagonal moment than either synthetic family at the same `V`.
A decoy family could not produce that.

*Construction cross-check (§4.6 item 3).* The closed-form `m3_TL` used here
reproduces the red team's independently constructed frames at `(100, 30)` to
`4.4e-16`: `V = 8.6334 → +0.980040` and `V = 6.0526 → -0.568440`, exactly the
two values `red_team_report.md` §4.2 reports. This checks that this TL
construction is the **same object** as theirs; it is not evidence about `D`.
(Note that this run's TL support is the deterministic coordinate pairs
`(a, a+beta)` frozen in §4.2, whereas the red team used a random permutation of
the support. The error law is i.i.d. across coordinates, so the two are equal in
distribution, and `V` and `m3` are identical by construction.)

### Form 4 — the mirror defect: a falsifier that cannot fire

*Why this run is not in it.* §4.4 forces `UNDERPOWERED — UPPER BOUND` rather
than `CONSISTENT` whenever the detection floor sits above the `5%` effect size,
and the realized floors are reported per pair. In this run the falsifier **did**
fire, twice, so the question of an unreachable rejection region does not arise
for the family verdict — but it very much arises for the eight pairs that did
not fire, whose floors (`6.29%` to `17.23%`) are all above `5%`. Those eight are
reported as upper bounds at their own floors and never as agreement.

---

## 7. The frozen §4.4 scoring, exactly as declared

```
declared n_C = 12 (fpylll 0.6.4 available)      |t| crit = 3.6358074219539622   <- PRIMARY
realized n_C = 10 (after UNREACHABLE and        |t| crit = 3.4994832973505026   <- prereg §4.3/§4.5
                   informativeness screening)                                       recomputation
family-wise level 0.10, Bonferroni, t_7 two-sided
FALSIFYING PAIR  iff  (i) |D_GR - D_TL| / SE > |t|crit   AND   (ii) |D_GR - D_TL| / max(|D_GR|,|D_TL|) > 0.05
SUGGESTIVE       iff  3.0 <= |t| < |t|crit  AND  (ii);   P(|t_7| > 3.0) = 0.019942126131992522
```

Both critical values were taken as frozen and neither was re-derived; the
recomputed realized-`n_C` value is reported because `prereg.md` §4.3 step 4 and
§4.5 direct it, and the declared value is the larger — hence more conservative
against falsification — and is used as PRIMARY.

| reading | abs-t critical value | FALSIFYING pairs | SUGGESTIVE pairs | verdict |
|---|---|---|---|---|
| PRIMARY, declared `n_C = 12` | `3.6358074219539622` | **2** (`d100_b40 graded_t0.0075`; `d140_b40 graded_t0.0050`) | 0 | **L2 TAIL-SUFFICIENCY FALSIFIED** |
| secondary, realized `n_C = 10` | `3.4994832973505026` | **2** (the same two) | 0 | **L2 TAIL-SUFFICIENCY FALSIFIED** |

No pair falls in the SUGGESTIVE band under either reading. The two pairs with
`|t|` between `2.0` and `2.5` (`d100_b40 unreduced` at `2.103`,
`d140_b40 unreduced` at `2.440`) are below the `3.0` band floor and are recorded
here with their values so that they are on the record rather than discarded;
the second of them also exceeds the `5%` relative bar (`8.05%`) while failing
the `|t|` bar.

**Margins, because one of the two is fragile.** `d100_b40 graded_t0.0075` clears
`3.6358` at `3.689`, a margin of `1.5%` of the critical value; it would not clear
a critical value above `3.689`. `d140_b40 graded_t0.0050` clears at `8.148` and
is insensitive to any critical value in the declared range. A reader who
discounts the fragile pair entirely is left with one FALSIFYING PAIR, and the
verdict under §4.4 is unchanged, because §4.4 requires **at least one**.

---

## 8. Budget, resources and reproducibility

```
command  : python3 coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/
           TASK-20260806-c973e6/vmatch.py --wall-budget-seconds 5400
           (run under `ulimit -t 5400`)
runs     : 1 of the 1 permitted.  No run was discarded, repeated or re-scored.
wall     : 16.80 s   (budget 5400 s; 0.31% used)
cpu      : 15.98 s   single process
max RSS  : 1.185 GiB (budget 4 GiB; 30% used)
threads  : OMP/OPENBLAS/MKL/VECLIB/NUMEXPR/ACCELERATE all pinned to 1
host load: loadavg 185.9 / 244.3 / 378.6 at start, 190.9 / 242.6 / 375.6 at end,
           on 14 cores.  No budget pressure resulted; the run is gemm-bound and
           single-threaded gemm measured 437 GFLOPS float32 on this host.
python 3.13.5 / numpy 2.4.0 / scipy 1.15.3 / fpylll 0.6.4 / macOS-15.6-arm64
```

All randomness is seeded and recorded: `seed_graded`, `seed_error` and
`seed_basis` as carried (§2), `FPLLL.set_random_seed` per basis, and the TL
family is **deterministic with no seed at all**. There is no other source of
randomness in this run. THE SEEDS ARE THE CACHE: no frame, basis or error
vector was loaded from disk.

**Certificate discipline (`docs/claims-and-verification.md`).** This is a pure
measurement run. `certificate.kind: none` — no discrete-log solve and no
factor-base relation is claimed or produced. The reproduction check of §2.1
against the committed `results.json` is an *instrument* check, not a solution
certificate, and is labelled as such in `run_manifest.yaml`.

---

## 9. Deviations, objections and limits — the complete list

1. **`prereg.md` §4.3 step 5 is factually wrong for `(140, 30)`.** The committed
   unreduced `V = 6.750435` is below that cell's TL minimum `8.571429`. The
   frozen §4.2 UNREACHABLE rule was applied, the target excluded, the objection
   recorded, and no threshold changed (§3).
2. **The frozen `1e-9` `V`-match tolerance is met in float64 (`<= 5.33e-15`) and
   not met at the committed float32 frame precision (`<= 2.31e-06`).** Both are
   reported per pair; the frozen number was not edited; the residual is five to
   six orders of magnitude below the measured effect (§5).
3. **Per-draw rather than mean-level `V` matching.** `prereg.md` §4.2 does not
   say which; this run matched `u_j` to `V_GR,j` **per draw**, which is the
   stricter reading and is what makes `D_GR,j - D_TL,j` a paired difference at
   equal `V`. Mean-level matching would have made all 8 TL frames identical and
   `sd(D_TL) = 0`, inflating `|t|` by `sqrt(1+n) = 3` exactly as the degenerate
   instrument check does. Both the per-draw and the mean-level `V` residuals are
   reported.
4. **A prose sentence inside the committed run record `vmatch.json` is wrong**
   (the Form 1 note claiming an inversion count of 0). The computed field beside
   it is correct. The record is immutable and was not edited; the correction is
   in §6 Form 1 and in `run_manifest.yaml` (§6 Form 1).
5. **One-ULP `scipy.betaincinv` difference** in the two `d = 140` cells relative
   to the committed run, giving `2.22e-16` in `D` (§2.1). Instrument fact.
6. **The frozen SE is a between-frame dispersion at `n = 8` over a SHARED error
   sample.** It does not contain the finite-`N` sampling error of the `2^-10`
   order statistic, which is common-mode within an arm and cancels only to the
   extent that the two frames are alike. This is a property of the frozen
   statistic, recorded and not re-derived. `EV-MLKEM-94c773` already records that
   this instrument at 8 draws is `9–13x` too coarse to resolve the residual that
   survives reduction.
7. **No null calibration of the frozen falsifier exists in this batch.** The
   degenerate instrument check is one point of a statistic that is mis-scaled by
   a known factor of 3 at that point (§6 Form 2). A proper calibration — two
   genuinely exchangeable frame families at matched `V`, replicated enough to
   estimate a false-falsification rate — is a concrete follow-up for the
   Coordinator and is **not** claimed to have been done.
8. **Nothing was rerun, omitted or re-scored.** One run, one result, every pair
   reported whether or not it fired.
9. **Scope.** Two synthetic frame families plus three unreduced real-lattice
   frames, `d <= 140`, `beta <= 40`, `n = 8` draws, `N = 2^20` errors, the
   `2^-10` quantile only. No reduced arm. No lattice invariant. No AM-4
   adjudication. Claim tier TOY. Independence in this batch is **procedural** —
   separate session, no shared scratch, snapshot before review — and never
   model-level.
10. **No conclusion is drawn.** Whether the heuristic is supported or refuted is
    for the Reviewer and the Coordinator. This report records the frozen
    prediction reference, the comparison statistics and the tail-check outcomes,
    and nothing beyond them.

---

## 10. Inference record (verbatim, as dispatched)

> requested_policy `executor-implementation`, degraded_allowed false,
> fallback_allowed false; resolved binding anthropic:claude-sonnet-5 per
> orchestration.adapter, but under the Claude Code runtime per CLAUDE.md
> per-role selection is process-level and subagents keep model: inherit, so the
> resolved model is the session model; fallback_used: false.

---

## 11. Artifacts

| file | sha256 |
|---|---|
| `vmatch.py` | see `run_manifest.yaml` |
| `vmatch.json` | see `run_manifest.yaml` |
| `vmatch_report.md` | this file |
| `run_manifest.yaml` | carries the digests of the other three |

The full stdout of the run is embedded verbatim in `run_manifest.yaml` under
`stdout_verbatim`; stderr was empty.
