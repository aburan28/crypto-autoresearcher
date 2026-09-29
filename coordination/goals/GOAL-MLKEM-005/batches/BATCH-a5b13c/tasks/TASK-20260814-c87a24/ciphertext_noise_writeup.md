# TASK-20260814-c87a24 -- Ciphertext-side noise census + block-size readout

Executing PREREG-7 (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-d13724/prereg.md`,
notarized at commit `89bf454eaf67dffa0e9585e2bccfb4b2e2b1543c`) in full: section 1
(infrastructure re-verification), Stage A (the exact Compress_d fibre census,
C1), Stage B (the three-noise-model ciphertext-side block-size readout, C2).

`H-MLKEM-11aabf`'s status is NOT changed by this document; that is a separate
Coordinator act. No lattice reduction (fpylll/BKZ/HKZ) of any kind was used
anywhere -- every number below is exact integer/rational arithmetic (Stage A)
or a closed-form readout of the pinned `estimator.lwe_primal.primal_bdd`
under `RC.MATZOV` (Stage B).

Requested inference policy: `executor-implementation`, `effort: medium`.
Resolved model: `claude-sonnet-5` (Claude Code CLI), `independent_session:
true`, `model_verified: false` (AGENTS.md rule 12 unmet/unwaived in this
goal, per PREREG-7 section 7 -- independence here is procedural, not
model-level; see `run_manifest.yaml`).

---

## R-CN-OUT-0 -- section 1, infrastructure re-verification

**Obligation 1 (clone).** Cloned `https://github.com/malb/lattice-estimator`
to `/tmp/le`, checked out `3e48ef421ec256afddb3e7d2249a77eab6e9ba12` explicitly
(the fresh clone's `HEAD` already equalled the pin, matching the harness
README's own note that this was true as of 2026-08-03; checked out
explicitly anyway rather than relying on that). Clean tree confirmed.

**Obligation 2 (known-answer control).** Ran
`tools/sage_free_estimator/known_answer_control.py` unmodified. Result:
**PASS, exit 0**.

```
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

Kyber512   143.7884782479     143.7884782479   3.13e-13     dual_hybrid(fft=True)
Kyber768   203.7878630676     203.7878630676   2.27e-13     dual_hybrid(fft=True)
```

`primal_bdd` reproduces the archived Sage reference for Kyber512/768 at
**exact delta 0.0** (not a tolerance); `dual_hybrid(fft=True)` agrees within
its own declared `1e-9` tolerance (observed ~3e-13, round-off). Per PREREG-7
section 1 point 2 and section 3.6's own guard: this does **not** halt the
batch. Full transcript: `stdout.log` / `stderr.log`, invocation 1 of 3.

**Obligation 3 (scheme parameters).** Independently confirmed
`estimator.schemes.Kyber512/768/1024` (read directly, not assumed):

| set | q read | q expected | n read | k implied (n/256) | eta1 recovered from `Xs.stddev` | eta1 expected | matches FIPS 203 Table 2 |
|---|---|---|---|---|---|---|---|
| Kyber512  | 3329 | 3329 | 512  | 2 | 3 | 3 | yes |
| Kyber768  | 3329 | 3329 | 768  | 3 | 2 | 2 | yes |
| Kyber1024 | 3329 | 3329 | 1024 | 4 | 2 | 2 | yes |

`eta1` was recovered from `Xs.stddev` by inverting `CenteredBinomial(eta).stddev
= sqrt(eta/2)` (source-verified: `estimator/nd.py` lines 296-313), rather than
reading a private field, so the check exercises the same public quantity
`primal_bdd` itself consumes. `Xs` and `Xe` are identical (`CenteredBinomial(eta1)`
for both) on all three base scheme objects -- this reflects Kyber's own
key-generation equation (`s`, `e` both ~ `CBD(eta1)`), and is why **eta2 is not,
and cannot be, independently read off these base objects**: eta2 = 2 for all
three parameter sets per FIPS 203 Table 2 is stated for the record but governs
only the ciphertext-side `e1`/`e2` terms, which this document's own
Compress_d-census construction (below) handles directly rather than via a
base-object `Xe` field. No mismatch found; all three parameter sets match.

**Obligation 4 (API-surface determination, performed BEFORE constructing any
modified instance).**

*(a) Explicit, finite, non-parametric-family error distribution.*
`estimator/nd.py`'s `NoiseDistribution` is a plain `@dataclass` carrying only
`(n, mean, stddev, bounds, is_Gaussian_like, _density)` -- there is no
constructor anywhere in that file for an arbitrary finite pmf (`grep`
confirms no `pmf`, `from_support`, or similar). **However**, the entire call
graph of `primal_bdd` (`estimator/lwe_primal.py`, read directly, every use of
`Xe.` / `Xs.` grepped) reads **only `Xe.stddev`** (and the `Xs <= Xe` /
`Xs < Xe` comparisons the base class also implements via `stddev`) -- never a
pmf or a moment beyond variance, for this attack/cost-model path. So the
API's cost model is **variance-only** for the noise. This means an explicit
finite distribution IS representable for `primal_bdd`'s purposes exactly as
PREREG-7 section 1 point 4 licenses as a fallback: "a documented,
variance-matched discretization if the API only accepts named families" --
constructing a raw `NoiseDistribution(mean=0.0, stddev=<exact computed
variance**0.5>, bounds=(-inf, inf))` instance directly. This is **not** full
pmf representation; the estimator discards everything but the variance for
this cost path, and this document does not claim otherwise. **No
infrastructure signal.**

*(b) Reduced sample/equation count relative to the base `Kyber1024` object.*
`LWEParameters.m` (`estimator/lwe_parameters.py`) is a first-class field
(default `oo`), and `rop`/`beta`/`d` all scale directly with it -- confirmed
empirically (constructing `LWEParameters(..., m=<reduced int>)` and calling
`primal_bdd` produces a different, self-consistent `d`/`beta`/`rop`). Directly
and natively representable; no workaround needed. **No infrastructure
signal.**

**Conclusion: `stage_B_gated_go = True`.** `T-CIPHNOISE-NODATA` branch (b)
does **not** fire. (See `ciphertext_noise_readout.py`'s
`section1_obligation4_api_surface()` for the executable form of this
determination, and `results_ciphertext_noise.json`'s
`R-CN-OUT-0_infrastructure_reverification` for the full machine-readable
record.)

---

## Rounding convention -- stated and checked before any census number, per section 2.3 obligation 0

`inputs/MLKEM-DUAL-SOURCES-20260802/fips203_selected_text.txt` (the committed
source this task's read_scope names) turned out, on inspection, to carry
**only FIPS 203's front matter and abstract** -- it does not contain section
2.3 ("Rounding") or section 4.2.1 ("Conversion and Compression Algorithms"),
the two passages this census actually needs. This is recorded as a protocol
deviation (`run_manifest.yaml` -> `protocol_deviations`), not silently
worked around: the lead fetched the primary source directly,
`https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf` (network,
`command.txt` step 0c), extracted it with `pdftotext -layout` (poppler-utils,
installed this session -- `pypdf` and `pdfminer.six` were tried first and
both failed on an unrelated sandbox defect, a Rust/PyO3 panic inside the
system `cryptography` package's crypt-provider import; abandoned in favour of
`pdftotext`, which has no such dependency -- see `environment.json`).

The exact text (FIPS 203 section 2.3, rounding operators, and section 4.2.1,
Compression and decompression):

> `⌈x⌋` -- The rounding of `x` to the nearest integer. If `x = y + 1/2` for
> some `y ∈ ℤ`, then `⌈x⌋ = y + 1`.
>
> Compression and decompression. Recall that `q = 3329`, and that the bit
> length of `q` is 12. For `d < 12`, define
>
> `Compress_d : ℤ_q → ℤ_{2^d}`, `x ↦ ⌈(2^d/q) · x⌋ mod 2^d`
> `Decompress_d : ℤ_{2^d} → ℤ_q`, `y ↦ ⌈(q/2^d) · y⌋`
>
> Division and rounding in the computation of these functions are performed
> in the set of rational numbers. Floating-point computations shall not be
> used.

**FIPS 203 specifies ROUND-HALF-UP** (ties broken upward: `x = y+1/2` rounds
to `y+1`) -- not round-half-to-even and not, in general, round-half-away-
from-zero. **This implementation uses round-half-up**, via exact
`fractions.Fraction` arithmetic (`math.floor(v + Fraction(1,2))`, never a
`float`, matching FIPS 203's explicit floating-point prohibition literally).
On this script's domain every rounding argument is non-negative
(`x ∈ [0, q-1]`, so `(2^d/q)·x ≥ 0`), so round-half-up and
round-half-away-from-zero coincide here; the distinction is stated because it
would matter off this domain and PREREG-7 required checking rather than
assuming it.

---

## R-CN-OUT-1 -- Stage A: the exact fibre census

Full histograms (all 3329 residues, every `d`):

| d | codewords (2^d) | fibre-size histogram | sum check |
|---|---|---|---|
| 4  | 16   | size 208: 15, size 209: 1 | 15×208 + 1×209 = 3329 |
| 5  | 32   | size 104: 31, size 105: 1 | 31×104 + 1×105 = 3329 |
| 10 | 1024 | size 3: 767, size 4: 257  | 767×3 + 257×4 = 3329 |
| 11 | 2048 | size 1: 767, size 2: 1281 | 767×1 + 1281×2 = 3329 |
| 12 | 4096 | size 1: 3329 (every fibre a singleton) | 3329×1 = 3329 |

**`d_u = 11` roundtrip agreement:** `Decompress_11(Compress_11(x))` exact
matches: **2048 of 3329** total (one per codeword, as expected for any `d` --
this is `2^11`, not `767`). Restricted to the 767 singleton residues
specifically: **0 mismatches** (all 767 singleton residues roundtrip
exactly, matching `H-MLKEM-11aabf`'s prediction "EXACTLY 767 of 767 exact
matches ... on the d_u=11 singleton residues"). The remaining `2048-767=1281`
matches are, by construction, exactly one representative per doublet fibre
-- consistent with the prediction's second clause ("for no residue in a
doublet fibre except the fibre's own representative").

**`d = 12` degenerate gate:** every one of the 3329 fibres is a singleton
(`2^12 = 4096 > q = 3329`), so `delta(x) = x - Decompress_12(Compress_12(x))`
is identically 0 for all `x` -- a constant random variable under any
distribution on `x` (including the stated simple model, `x` uniform on
`Z_q`). A constant carries zero information about any other variable, so
`I(delta; bin) = 0` **exactly**, forced by the census itself (every fibre a
singleton) rather than estimated by a separate Monte Carlo computation.

**Falsification read (before Stage B proceeds):**

- `F(a)`: singleton count at `d_u=11` is exactly 767 with 1281 doublets
  (767+2×1281=3329 exact); `d_u=10` census is exactly 767 fibres of size 3
  and 257 of size 4. **CLEARS.**
- `F(d)`: `d=12` gate returns every fibre a singleton with `I(delta;bin)=0`
  exactly. **CLEARS.**

**Stage A is complete and stands as an independent result regardless of
Stage B**, per PREREG-7 section 2.4/6. Reproduced twice in this session
(standalone `ciphertext_noise_census.py` run, and the same module imported
inside `ciphertext_noise_readout.py`); both agree field-for-field
(`results_ciphertext_noise.json`'s `_stage_A_standalone_reproduction_cross_check.matches_readout_embedded_census
= true`).

---

## R-CN-OUT-2 -- Stage B obligation 1: the three noise models

**M0 (single marginal).** The population-average compression-error
distribution -- the exact histogram of `centered_delta(x) = ((x -
Decompress_{d_u}(Compress_{d_u}(x)) + q/2) mod q) - q/2` over all 3329
residues at that parameter set's own `d_u` -- convolved (exact `Fraction`
arithmetic) with `CBD(eta1)` (`Var = eta1/2` exactly). Fed to `primal_bdd`
as a raw `NoiseDistribution(stddev=<sqrt of the exact total variance>)`.

**A note on the centering fix.** The first working version of this
computation used the naive integer difference `x - Decompress(Compress(x))`
without reducing it into the signed range `(-q/2, q/2]`. Because
Compress/Decompress arithmetic is circular mod `q`, this produced exactly
one spurious huge-magnitude outlier per `d` from residues near the `q-1/0`
wraparound boundary (verified: at `d=10`, one residue had raw
`x - Decompress(Compress(x)) = 3328` instead of the true signed distance
`-1`), inflating the computed variance by orders of magnitude (`stddev`
~57.7 instead of ~1.4-1.6 at Kyber512/768). This was caught and fixed
**before any number was reported as final** -- see
`ciphertext_noise_census.centered_delta`'s docstring and
`run_manifest.yaml`'s `protocol_deviations`. The buggy intermediate run's
numbers are not reported anywhere in the deliverables; only the corrected
run is.

**M1 (per-class rescaling).** PREREG-7 section 3.2 states M1's literal
mixture probabilities (767/3329 singleton, 2×1281/3329 doublet) using
`d_u=11`'s own class structure specifically. Since **ML-KEM-512/768 use
`d_u=10`, where the frozen §2.2 prediction states explicitly "NO SINGLETON
FIBRE EXISTS"**, those literal numeric probabilities cannot apply verbatim
to those two parameter sets even though §3.2 states M1 is defined "at every
parameter set". **This is reported as a finding about the frozen text's
own internal scope, not silently reconciled**: the construction actually
executed here generalizes M1 in the only way consistent with §3.0's stated
purpose (condition on the coordinate's own public class label, whatever
classes exist at that parameter set's own `d_u`) -- at `d_u=10`, the two
classes are "fibre size 3" (767 fibres, 2301 residues) and "fibre size 4"
(257 fibres, 1028 residues); at `d_u=11`, the classes are exactly the
literal singleton/doublet split §3.2 states. Each class's own exact
compression-error distribution (from the Stage A census, centered) is
convolved with `CBD(eta1)`, and the probability-weighted mixture of these
per-class convolutions is fed to `primal_bdd` as **one combined
distribution**, exactly matching §3.2's own instruction ("The estimator is
fed a single effective distribution constructed as this properly
class-weighted mixture").

**THE CENTRAL STAGE B FINDING: `beta(M0) == beta(M1)` EXACTLY, at every
parameter set** -- not merely equal integers, but bit-identical `stddev` fed
to the estimator and bit-identical `log2(rop)` returned (verified
numerically; see `results_ciphertext_noise.json`'s
`IDENTICAL_TO_M0_variance_exactly: true` at all three sets). **This is a
forced mathematical identity, not a coincidence, an implementation
approximation, or a bug**: the classes that M1 conditions on **partition**
`Z_q` exactly, so M0's population-average distribution is *already* the
same probability-weighted mixture over those same classes that M1
constructs explicitly. Convolution distributes over mixtures -- for a
mixture `D = Σ p_i · D_i`, `Law(Xe + D) = Σ p_i · Law(Xe + D_i)` exactly, by
linearity of expectation applied to sums of independent random variables --
so "convolve `Xe` with the population mixture" (M0) and "mixture of
`Xe`-convolved-with-each-class, fed as one combined distribution" (M1, per
§3.2's own literal instruction) **are the same distribution to full
precision**. Given M1 is specified, per §3.2, as a *single marginal noise
law applied uniformly to every coordinate*, it cannot differ from M0 by
construction; only a change to **which samples/equations the estimator
sees at all** -- M2's dimension reduction -- can move `beta` away from M0.
This is reported plainly as the honest reading of what M1, as literally
specified, can and cannot do under this estimator's API, per the
executor's obligation not to silently reconcile or paper over a frozen
clause it finds surprising (AGENTS.md rule 5/9; executor prohibitions).

**M2 (clean-samples-only, reduced dimension -- ML-KEM-1024 only).** Retain
only the 767 singleton-class residues (noise = `Xe` alone, exact zero
compression contribution by the `Decompress(Compress(x))=x` identity on a
singleton fibre); drop every doublet coordinate. Represented via
`LWEParameters.m` (native field): `reduced_m = round(base_m ×
767/3329) = round(1024 × 767/3329) = 236` (base `m = n = 1024` for
Kyber1024). The `round()` used here is Python's standard round-half-to-even
on this specific integer-construction choice -- **not** FIPS 203's own
round-half-up, which governs Compress/Decompress specifically and is not
extended to this document's own dimension-reduction arithmetic; stated
explicitly rather than silently inherited. `NOT_APPLICABLE` at
ML-KEM-512/768 (no singleton class exists at `d_u=10`), recorded as such,
never as missing or failed.

### Readout table

| set | beta(key-side) | beta(M0) | beta(M1) | beta(M2) | beta(best) | best model | gain (best-M0), bits | ciphertext(best) - key, bits | verdict |
|---|---|---|---|---|---|---|---|---|---|
| ML-KEM-512  | 389 | 404 | 404 | N/A (no singleton class at d_u=10) | 404 | M0 | 0 | +15 | CLOSED |
| ML-KEM-768  | 606 | 633 | 633 | N/A (no singleton class at d_u=10) | 633 | M0 | 0 | +27 | CLOSED |
| ML-KEM-1024 | 855 | 872 | 872 | 617 | 872 | M0 | 0 | +17 | CLOSED |

("best" = the MAXIMUM defined beta, per §3.4 point 3's own convention that
higher beta is the model giving the ciphertext-side attacker LESS
advantage.)

**K-sensitivity sweep.** The tunable this installed, unmodified API actually
exposes for `RC.MATZOV` is `nn` (`estimator/reduction.py`:
`Kyber.__init__(self, nn="classical")`, inherited unmodified by `GJ21` and
`MATZOV`; `"classical"` aliases to `"list_decoding-classical"`, `"quantum"`
to `"list_decoding-dw"`; the full `NN_AGPS` dict names ~21 named
nearest-neighbour-cost variants). **This document does not assert that `nn`
is the specific symbol H-MLKEM-11aabf's prose calls "K"** -- only that `nn`
is the concrete, source-verified tunable this cost model exposes, which is
what was swept:

| set | classical (default) | quantum | all_pairs-classical | random_buckets-classical |
|---|---|---|---|---|
| ML-KEM-512  | beta 389 | beta 388 | beta 394 | beta 392 |
| ML-KEM-768  | beta 606 | beta 604 | beta 611 | beta 609 |
| ML-KEM-1024 | beta 855 | beta 851 | beta 860 | beta 858 |

(key-side object, all four `nn` variants; brackets a modest ±1 to +5 bit
spread around the default -- see `results_ciphertext_noise.json` for the
`log2(rop)` values and the same sweep is not separately re-run against
M0/M1/M2 within this task's budget).

---

## R-CN-OUT-3 -- Stage B obligation 2

**`HEUR-MLKEM-11aabf-1`'s own falsification check, at ML-KEM-1024, checked
first and independently of CLOSED/OPEN:** `beta(M2)=617 < beta(M0)=872` ->
**`F(b)` NOT FIRED**.

**An anomaly worth flagging plainly, alongside `F(b)` not firing:**
`H-MLKEM-11aabf`'s own `minimum_effect` prediction for M2 vs M0 at
ML-KEM-1024 is "a reduction of 2 to 4 core-SVP bits". The measured reduction
is **255 bits** (872 -> 617) -- roughly two orders of magnitude larger than
predicted, though directionally consistent (M2 < M0, satisfying the
prediction's stated *minimum* floor, since "minimum_effect" as phrased sets
a threshold rather than a ceiling). `reduced_m = 236` against `base_m = base_n
= 1024` is a **severely underdetermined regime** (`m << n`, `d = m+n = 1260`
vs the key-side lattice's `d=1867`). This task does **not** conclude whether
the 255-bit figure represents a sound security-relevant effect of "removing
compression noise" (the hypothesis's own mechanism) or is dominated by a
different, much larger effect intrinsic to feeding `primal_bdd` a sample
count far below the base scheme's own `m=n` -- both readings are recorded
here rather than either being silently adopted. This is exactly the kind of
unexpected observation AGENTS.md rule 9/the executor's own obligations
require preserving rather than discarding or smoothing into "matches
prediction."

**Per-parameter-set verdict:** ML-KEM-512 CLOSED, ML-KEM-768 CLOSED,
ML-KEM-1024 CLOSED. **Aggregate: CLOSED-ALL.**

---

## R-CN-OUT-4 -- termination branch

Read off R-CN-OUT-1 through R-CN-OUT-3 under PREREG-7 section 3.6's frozen
precedence (`T-CIPHNOISE-NODATA` dominates and fires alone; among the
remaining three, `MIXED` fires on disagreement, `CLOSED`/`OPEN` fire only on
full agreement): `T-CIPHNOISE-NODATA` does not fire (Stage A clears, section
1's API check succeeds); the three parameter sets agree (all CLOSED), so
`MIXED` does not fire.

**`T-CIPHNOISE-CLOSED` FIRES**, per PREREG-7 section 3.6's own verbatim text:

> **MEANS:** the honest, class-aware noise treatment still leaves the
> ciphertext-side lattice materially worse positioned than the key-side
> lattice at every tested parameter set -- the hypothesis's own predicted,
> expected verdict, recorded as a closure WITH THE EXACT NUMBER (the bit
> gap table), not assumed. **LICENSES:** citing the exact M0/M1/M2 beta
> figures and the exact ciphertext-vs-key-side bit gaps, at the tested
> parameter sets, under the pinned estimator and RC.MATZOV, as a labelled
> model readout (medium tier) -- narrowly. **FORBIDS:** any claim that this
> closes RQ-MLKEM-001 itself, any claim about best-of-M ciphertext
> selection (unrelated per H-MLKEM-11aabf's own interpretation_limits), any
> claim beyond the pinned estimator/cost model tested, any ML-KEM security
> claim, any claim that a DIFFERENT compression parameter, cost model, or
> attack would give the same verdict.

`F(b)` (not fired) is reported alongside this branch, not folded into or
allowed to change which branch fired.

**What this task does NOT license (restated, PREREG-7 section 6 / this
task's own constraints), stated explicitly rather than left implicit:**
does not close, pause, or complete `GOAL-MLKEM-005`; does not change
`H-MLKEM-11aabf`'s status; does not close `RQ-MLKEM-001`; says nothing
about best-of-M ciphertext selection; does not extrapolate beyond the
pinned `lattice-estimator` commit / `RC.MATZOV` / `primal_bdd` tested; does
not touch, reopen, or re-score the `hkz`/HKZ-independence lineage or
`DEC-20260813-9c7353`'s deferred epsilon-sweep candidate; licenses no
further measurement of this same hypothesis at these same three parameter
sets under these same three models as an automatic successor (a new
compression parameter, cost model, or noise-model construction requires its
own, separately-commissioned Coordinator decision, per PREREG-7 section
3.6's declared forward boundary).

---

## Every path this task wrote (within its declared write_scope)

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/ciphertext_noise_census.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/ciphertext_noise_readout.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/results_ciphertext_noise.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/ciphertext_noise_writeup.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/command.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/run_manifest.yaml
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/environment.json
```

Nine paths, matching the task card's declared `artifact_paths` exactly. No
file was written outside this list. Nothing was committed; the Coordinator's
snapshot archive (`TASK-20260814-07bfae`) commits these nine paths.
