# EXP-MONO-b1423c implementation notes

## Purpose

K5 sensitivity check on EXP-MONO-b19c6b's Fisher-combined panel-level
statistic: does it reject a genuine, maximally-extreme positive control
(RO3's exact index-2/index-4 subgroup factor base, C/F = 1.0 exactly,
already realized and archived by EXP-MONO-c819ba)? Per
`specification.yaml`, observations only -- no verdict on H-MONO-663fb4.

## Code provenance (read before trusting any number below)

- `fields.py`, `curve.py`, `conv.py`, `groupstate.py`, `stats.py`: copied
  **byte-identical** from `experiments/EXP-MONO-b19c6b/implementation/`
  (verified with `diff`, zero output, at setup time). Not modified.
- `controls.py::subgroup_control`: copied **verbatim** (byte-for-byte,
  including comments) from
  `experiments/EXP-MONO-c819ba/implementation/controls.py`. `run.py`'s
  `verify_subgroup_control_source_verbatim()` re-diffs the two functions
  at every run and halts as `failed_infrastructure` on any mismatch (it
  reported `true` on this run).
- `seed.py` and `controls.py::draw_symmetric_null_subset` are **new** to
  this contract, because this contract's own frozen
  `inputs.seed_derivation_rule` uses a different (smaller) preimage than
  either predecessor's `seed.py` (keyed on `p` and `h` directly, since
  there is exactly one curve and two named cells here, not a multi-curve
  panel needing `family`/`curve_ordinal` keys). The *mechanism*
  (rejection-sampled uniform draw, symmetric +/- pair construction) is
  unchanged from `EXP-MONO-c819ba::draw_symmetric_null` /
  `EXP-MONO-b19c6b::draw_symmetric_subset`.
- `run.py` is new orchestration written for this contract only.

## Step 1: reconstruct RO3 and verify against EXP-MONO-c819ba's archive

`CurveState(p=307, A=269, B=6)` (the byte-identical `groupstate.py`)
reproduced `N=288, n1=3, n2=96`, matching the contract's declared values.

`subgroup_control(cs, k=2)` gave `h=144`; `subgroup_control(cs, k=4)` gave
`h=72`, both matching `n1*(n2//k)`.

For each cell, `cell_stats_fft` (from the reused `conv.py`) computed
`forced_relative_deviation = N/h - 1` and `C_over_F` (both m-independent
except the `measured_relative_deviation` cross-check at m=2, matching
EXP-MONO-c819ba's own verification path):

| cell | forced_relative_deviation | measured (m=2) | C/F | archived (EXP-MONO-c819ba) |
|---|---|---|---|---|
| h=N/2=144 | 1.0 | 1.0 | 1.0 | forced_relative_deviation=1.0, C/F=1.0 |
| h=N/4=72  | 3.0 | 3.0 | 1.0 | forced_relative_deviation=3.0, C/F=1.0 |

Exact match (`<1e-9`) on both quantities, both cells:
`reconstruction_verified: true`. Per the contract's stopping rule, S1-S5
compute proceeded.

## Step 2: real-arm stats at m=4 and dual-path control

`stat_bundle_from_coords` (route 2, FFT) at m=4 gave:

- h=144: `Var_real = 2,229,025,112,064.0`, `C_over_F_real = 1.0`
- h=72: `Var_real = 26,121,388,032.0`, `C_over_F_real = 1.0`

Route 1 (`convolution_tower`, direct circular-roll summation) reproduced
the identical `Var` values exactly (`relative_difference = 0.0` on both
cells, well within the 1e-9 tolerance). `dual_path_control_all_within_1e-9:
true`.

## Step 3: background panel (reused, not regenerated)

`experiments/EXP-MONO-b19c6b/runs/RUN-MONO-b19c6b-1/raw-result.json`'s
`stage3_per_curve_raw_pvalues["random-ordinary"]` was read directly: 48
curves, each carrying `p_var_raw` and `p_cf_raw`. Not recomputed, not
modified. `background_panel_sha256` in `raw-result.json` fixes its exact
content for audit.

## Step 4: 20000 matched-null draws per cell (S5)

For each cell (F=144, F=72), 20000 symmetric null subsets were drawn on
RO3 via `draw_symmetric_null_subset` keyed by this contract's own
`seed_derivation_rule` (domain, master_seed=20260901, p=307, h, draw_index,
counter). For each draw, `Var_null` (m=4) and `C_null/F` were computed via
one `character_spectrum` FFT call per draw (cheap at N=288).

`permutation_pvalue` (EXP-MONO-b19c6b's own frozen formula,
`(1+count)/(n+1)`, two-sided around the null median) gave, for **both**
cells and **both** statistics:

```
S5_raw_pvalue_var       = 4.999750012499375e-05  (= 1/20001, the floor)
S5_raw_pvalue_C_over_F  = 4.999750012499375e-05  (= 1/20001, the floor)
```

Both known-positive cells landed exactly at the permutation-test floor for
both statistics: `count = 0` null draws were as or more extreme than the
real value in every case. `Var_real` exceeded the largest of 20000 null
draws by roughly 6x (h=144: null max ~3.5e8 vs real ~2.2e12) and ~245x
(h=72: null max ~1.07e8 vs real ~2.6e10); `C_over_F_real = 1.0` exceeded
the null mean by ~5.8x (h=144) and ~3.4x (h=72). **S5 confirms the
known-positive cell is a genuine, near-floor outlier on both statistics,
both cells** -- the `positive_control_itself_not_extreme` falsification
branch does NOT apply here.

## Step 5: Fisher-combined mixed panels (S1-S4, the primary test)

Each known-positive cell's own S5 raw p-value was pooled with the 48
background raw p-values (49 total) and passed through the reused,
unmodified `fisher_combined_pvalue`:

| panel | statistic | Fisher-combined p-value | rejects at 0.05? |
|---|---|---|---|
| S1: h=N/2 + background | Var | 0.5198 | No |
| S2: h=N/4 + background | Var | 0.5198 | No |
| S3: h=N/2 + background | C/F | 0.4709 | No |
| S4: h=N/4 + background | C/F | 0.4709 | No |

(S1=S2 and S3=S4 exactly because both cells' own S5 raw p-values are
identical -- both are exactly at the 1/20001 floor -- so the two mixed
panels differ from each other only in which single p-value out of 49 is
"the floor value," which the Fisher-combined statistic (symmetric in its
inputs) does not distinguish.)

**None of S1-S4 reject at alpha=0.05**, despite S5 confirming the
injected cell is a genuine, maximally-extreme (floor) outlier in the raw
per-cell test. This is the `falsification_criterion(c)` case named in the
contract, and the `sensitivity_gap_confirmed` outcome as the contract
itself defines it.

## Observation (not interpretation; no verdict rendered)

At this panel size (k=49: 1 injected extreme cell + 48 background
curves), pooling one exactly-floor raw p-value with 48 raw p-values whose
Fisher-combined behavior is otherwise consistent with a null (the
background panel is EXP-MONO-b19c6b's own already-reviewed non-exceptional
random-ordinary panel) is not sufficient for the unweighted Fisher-combined
statistic to reject at 0.05, even though the injected cell's own raw
p-value is the theoretical extreme (1/20001) on BOTH statistics
(Var and C/F) at BOTH tested h values. This is reported as the contract's
own named `sensitivity_gap_confirmed` finding, not as a refutation of the
Fisher-combined statistic's construction, and not as evidence about
H-MONO-663fb4's mild/diffuse hypothesized deviation -- per
`scale_relevance` and `claim_ceiling`, this record's scope is exactly:
whether this specific statistic, computed exactly as `stats.py` defines
it, rejects a panel containing this specific maximally-extreme synthetic
cell at this specific panel size. It does not establish anything about
statistical power in general, about a different panel size, or about a
weighted/rank-based alternative combining rule.

## Deviations from protocol

None identified. `dual_path_control_all_within_1e-9: true`, the
reconstruction verification passed before any S1-S5 compute, the
background panel was read unmodified, and all five reused implementation
files diffed byte-identical against their `EXP-MONO-b19c6b` source at
setup time.

## Budget

Wall clock: 4.43s (budget 600s). Peak RSS: ~39.4MB (budget 512MB). Single
run, seed 20260901, as the contract specifies (no replication).
