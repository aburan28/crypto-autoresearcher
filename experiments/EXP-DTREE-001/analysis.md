<!--
This file was written by the Coordinator, not the Executor. The Executor's
Write tool refused to create it directly ("Subagents should return findings
as text, not write report files" — a harness-level restriction on that
session), so the Executor delivered the intended content as text in its
final response instead. The Coordinator transcribed that text verbatim into
this file during the snapshot-archive step and independently re-verified the
underlying claims against runs/RUN-DTREE-*/raw.json and summary.json before
persisting it — see the snapshot commit message for the specific checks
performed (tiny-curve lambda table recomputed by hand; two decomposition/
discrete-log certificates independently re-verified via from-scratch EC
point-addition and scalar-multiplication, not the Executor's own verifier).
No content below was altered from what the Executor reported.
-->

# EXP-DTREE-001 — Analysis

## 1. Observation

**C1 (slope).** The frozen slope-grid rule yields 0 qualifying cells on all
three tiny curves. This is arithmetically forced by the frozen inputs: given
the grid's own B′ ≥ 8 floor, the smallest achievable C(B′,3) is C(8,3) = 56
(not the naive 50 the "n ≥ 71.4" shorthand assumes), so the precise
necessary-and-sufficient threshold is n ≥ 56/0.7 = 80 — corrected during
`/review-evidence` from an earlier, looser "n ≥ 71.4" (= 50/0.7) figure that
was a necessary-but-not-sufficient shorthand, not a computational error; the
conclusion is unchanged either way. The frozen `generate_instance` seed-1
curves have n = 23, 19, 31 at 8/10/12 bits — far below either threshold.
RUN-DTREE-002 confirms the confirmatory fit, CTRL-ENUMERATION-AUDIT, and all
three tail checks are `not_applicable` as a direct consequence. A
diagnostic-only point outside the grid (B′ = 8) shows P_dec = 0.96, 0.42,
0.19 at 8, 10, 12 bits respectively — illustrating deep saturation at the
smallest allowed B′, not a measurement inside the registered grid.

**C2 (cost).** Single-level decomposition probability P(m=3, B) was measured
as 0.0, 0.32, 0.0 at 16, 20, 24 bits, with mean capped-solve costs
C_solve(3) = 1.40s, 20.0s, 20.0s respectively (the latter two are 100%
Gröbner-capped). This gives C1 = undefined, 62.5, undefined by size.

At the depth-2 stage: 16-bit meets the pre-registered validity prefix (8/8
configurations reach ≥10 measured targets), but every one of its C2 values is
undefined — the stage-2 decomposition probability was measured as an exact
0/15–16 success rate in every attempted configuration there, not merely
small. 20-bit and 24-bit both fail the validity prefix (0/8 configurations
each reach the 10-target minimum; actual n₁ = 3–4 at 20-bit, 6–7 at 24-bit).

Where C2 is defined at all — six of eight 20-bit configurations — the range
is 110–200. Of those six, **five** carry a reported bootstrap 95% CI on
C2/C1 (corrected during `/review-evidence` from an earlier, incorrect "six"
count): m2_x16 [1.25,4.75], m3_x16 [1.619,10.0], m3_x2 [1.15,9.625], m3_x4
[2.133,4.0], m3_x8 [3.333,10.0] — all entirely **above** 1 (lowest lower
bound: 1.15). The sixth, m2_x8 (point estimate C2=160.0), has no reported CI:
only 854 of 2000 bootstrap replicates (42.7%) produced a computable ratio,
below `costs.py`'s own 50% applicability floor, so its interval is genuinely
not reported rather than merely omitted here. Its point estimate is
directionally consistent with the other five. No configuration, at any size,
meets the frozen success criterion C2 < 0.8·C1 with a CI entirely below 1.

CTRL-GENERIC-HEURISTIC labels every computable cell (all at 20-bit)
`non_generic_signal`: the measured/HEUR-001-predicted C2 ratio falls in
[0.00044, 0.00095] — 100–800× cheaper than HEUR-001's own prediction —
far outside the pre-registered [0.5, 2] tolerance band. No cell is labeled
`generic_equivalent`.

**Unregistered observation.** Measured single-level P does not track
HEUR-001's own (B/N)² point-prediction in either direction or magnitude
(measured 0.0/0.32/0.0 vs. predicted 0.047/0.000239/0.003 at 16/20/24-bit),
coincident with measured main-curve cofactors of 2280, 196, and 31512
respectively. This is reported per AGENTS.md rule 8 (record, never discard)
and is explicitly **not** scored against any pre-registered threshold, since
it was not a metric the frozen contract defined.

## 2. Comparison to predefined criteria

- **C1 success/falsification paths:** unreachable. No slope, no confidence
  interval, no comparison to γ = 2 or γ = 3 exists to compare against either
  path — the grid that would have produced them is empty by construction.
- **C2 success path** ("≥1 configuration at 24-bit achieves C2 < 0.8·C1 with
  a bootstrap CI entirely below 1"): **not met.** Every 24-bit configuration
  is undefined.
- **C2 falsification path (a)** ("C2 ≥ C1 at every size meeting the validity
  prefix"): only 16-bit meets the prefix, and there every C2 is *undefined*
  (an exact 0-success stage-2 rate) — distinguished here from a computed
  "C2 ≥ C1", since the frozen contract treats undefined and dominated as
  different outcomes.
- **C2 falsification path (c)** ("every winning configuration is
  generic-equivalent"): the winning set is empty, so this path is vacuously
  true rather than a genuine equivalence finding — distinguished explicitly
  rather than collapsed into a positive result.
- **Unconditional clauses** (12 terminal runs; complete, mutually agreeing
  raw/summary artifacts; C1 measured as a cost quantity on all three main
  instances): met.

## 3. Inference (compatible explanations)

The empty slope grid is a direct, checked arithmetic consequence of
`generate_instance`'s weak-bar search at these specific seeds (it accepts the
first curve meeting "largest prime factor ≥ 5", not one with a large
prime-order subgroup) — it is a property of the frozen instance-selection
procedure, not a measurement bearing on HEUR-001's exponent claim either way.

The C2 pattern — zero winning configurations overall, and an *exact-zero*
stage-2 success rate at the one size (16-bit) that meets the validity
prefix — is compatible with at least two distinct explanations that this
data does not separate: (a) the depth-2 tree's second stage genuinely never
clears the standard base at these curves/seeds/factor-base construction, or
(b) cofactor size is a first-order driver of whether standard-base
decomposition is measurable at all here — 20-bit (cofactor 196) is the only
size where any stage-2 success was ever observed, and the only size with any
defined C2. Isolating between these was the job of the (unavailable) C1
slope fit; it is not attempted here from C2 data alone, and no claim is made
about which explanation is correct.

## 4. Limitations

- Toy scale only: cost measured at 16–24 bits, slope entirely unmeasured at
  the frozen 8–12 bit grid.
- C1 is not merely "not yet measured" — it is structurally unmeasurable
  under this specific frozen seed/instance-generation combination. This is a
  property of the protocol's frozen inputs, not a scientific result about
  the heuristic under test.
- The 20-bit and 24-bit C2 comparisons are `resource_exhaustion`, not
  decisive negatives, per the protocol's own validity-prefix rule.
- The unrestricted-factor-base/cofactor observation is unregistered — not
  scored against any threshold, not diagnosed further than reported here.
- Absolute Gröbner timings are bound by sympy's Buchberger implementation,
  not a crypto-scale cost model.
- Certificates cover positive claims only (256 claimed across all runs, 256
  independently verified — the Coordinator independently re-verified two of
  these, one decomposition and one discrete-log certificate, via
  from-scratch elliptic-curve arithmetic rather than trusting the Executor's
  verifier). A negative result (P = 0, or no qualifying grid cell) is a
  scoped absence-of-witness-within-budget, not a proof of non-existence.
