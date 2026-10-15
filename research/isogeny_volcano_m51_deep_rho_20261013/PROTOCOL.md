# Frozen protocol: four-level m=51 native-rho benchmark

Status: **endpoint-bound and frozen, not launched**.  `deep_selection.json`
binds the sealed full-range discovery selection, and `FROZEN.sha256` covers the
exact scientific inputs.  No endpoint timing or rho outcome from the deep
levels is admitted at this freeze point.

The exact machine-readable contract is [`spec.json`](spec.json).  The exact
endpoint-independent 4,096-block crossover is [`schedule.csv`](schedule.csv).

## Requirement-to-evidence plan

| Requirement | Frozen evidence or launch gate |
|---|---|
| Measure all four conductor orders with one action | Four native mode-0 signed-negation arms `C=f_E 1`, `A=271`, `P=120871`, `B=32756041` in every block |
| Bind discovery without outcome selection | `bind_selection.py` accepts only a sealed, valid, full-range first-32 scan; `deep_selection.json` must then be included in `FROZEN.sha256` |
| Complete f=271 crossover | Every deep pair uses all 16 f=271 orbit representatives six times in inference and twice in held-out A/A |
| Exercise certified endpoint edges | Every P/B pair exercises all 51 conjugates in inference; the same Frobenius exponent is applied to the certified raw `parent_b -> bottom_b` coefficients.  The canonical `bottom_orbit_rep` remains only the population identity and is never substituted for the raw child coefficient |
| Avoid canonical-representative bias | f=271 and P/B assignments are globally near-balanced; calibrated cell means give every exercised model equal weight |
| Preserve native endpoint semantics | Each curve constructs and certifies its own `Pgen`, tables, and `Q=kP`; no point or walk state is transported |
| Pair stochastic work | The scalar and numeric walk stream are shared across all four arms in a block; A/A repeats hold target/setup fixed and change only the walk namespace.  This common-random-number plan is a pre-freeze amendment that supersedes the nonfrozen blueprint's arm/domain-separated streams |
| Measure operation work | `walk_ops` primary; target setup, total group ops, canonicalizer primitives, native setup seconds, process seconds, restarts and cycles remain separate |
| Freeze one inferential family | Six pairwise contrasts plus `M271`, `M120871`, and `I`, using one 100,000-draw per-draw re-studentized Rademacher max-|T| critical value; report `2I` only as the derived ordinary difference-in-differences |
| Represent endpoint sampling honestly | Report the finite selected-32 estimand only as a point estimate and descriptive heterogeneity; reserve simultaneous intervals for the explicitly modeled pilot-excluded population estimand |
| Detect harness/randomization drift | 32 held-out blocks per pair, all four arms, two independent walk streams; 8,192 held-out solves |
| Detect an influential setup choice when required | After a valid A/A gate and estimable primary family, a predeclared trigger launches 16 fresh inferential setup roots plus one noninferential original-root bridge on one identical fixed panel in the same admitted run |
| Prevent unsupported conclusions | Association/noncausal labels, one-child-per-parent limitation, no map/transfer/end-to-end/weak-curve claim |

## Objects and lattice

The field and curve family are

```text
F = GF(2)[z]/(z^51+z^6+z^3+z+1)
E_b: y^2 + x*y = x^3 + b.
```

All arms have ambient order `2,251,799,852,369,764`, prime subgroup order
`r=17,192,986,687` (`log2(r)=34.001101...`), and cofactor `130,972`.
The trace is `-38,684,515` and

```text
Delta_pi = -7*(271*120871)^2,
f_pi = 271*120871 = 32,756,041.
```

The four endomorphism orders form a square, not a chain:

```text
                 degree 120871
       C (1)  --------------------  P (120871)
         |                               |
 degree 271                         degree 271
         |                               |
       A (271) -------------------- B (271*120871)
                 degree 120871
```

These labels express conductor-order adjacency.  Discovery certifies an
ascending cyclic kernel and its endpoint only for each selected `P-B` edge.
It does not provide an evaluator or dual.  The benchmark itself invokes no
isogeny: all four points and targets are constructed natively.

Each selected discovery record distinguishes three values: the certified raw
parent coefficient `parent_b`, the certified raw child coefficient `bottom_b`,
and the canonical bottom-orbit representative `bottom_orbit_rep`.  The last is
the population/census identity.  It is not generally the raw child coefficient.
For exponent `e`, the benchmark therefore instantiates
`Frob^e(parent_b)` and `Frob^e(bottom_b)`.  Applying `e` to both raw endpoints
preserves the certified P/B edge.  Conjugating `bottom_orbit_rep` instead would
measure a different pairing and is rejected.

## Endpoint admission and binding

The discovery runner must first finish its entire rank range `[0,3.6e9)`, pass
its positive/negative controls and certificate checks, select the first 32
eligible distinct parent orbits without backfill, and seal its tree.
`bind_selection.py` independently verifies that seal, terminal session,
selection schema, rank ordering, distinctness, curve-orbit metadata, and all
32 referenced certificate byte hashes.  It emits one write-once
`deep_selection.json` with the source tree-manifest, input-freeze, session,
selection, pair-record and certificate hashes.
The write-capable binder is invoked with the exact sanitized environment shown
below and Python `-I -B`; it compiles the local `design.py` source bytes
directly and never accepts a cached local module.

The benchmark runner then validates the binding again.  Any source failure,
quota failure, unresolved pre-cutoff classification, duplicate selected orbit,
noncanonical representative, or missing byte binding refuses the launch.
There is no replacement endpoint and no backfill.

The source sampling statement remains conditional: under the discovery's
keyed-modeled-PRP/exchangeability model, the 32 parent orbit PSUs sample the
pilot-excluded population of 2,369 parents and 644,368 bottom-child orbits.
This is not a design-free random-sampling fact.

## Exact 20,480-solve schedule

For each of the 32 selected `P-B` pairs, 96 inferential blocks cross every one
of the 16 `A` Frobenius orbits exactly six times.  Within each pair, the deep
conjugate schedule contains a permutation of `0..50` followed by 45 distinct
duplicated conjugates.  Thus every one of the 51 `P` and `B` models is
exercised, and P/B always use the same exponent.  Across pairs the deep-model
counts are exactly 60 or 61.  Within each A-orbit/pair the six conjugates are
distinct; across all pairs every A model occurs 11 or 12 times.

This gives `32*96*4 = 12,288` inference solves.  The disjoint A/A holdout has
32 blocks per pair, exactly two blocks for each A orbit.  Its deep conjugates
are distinct within pair and globally occur 20 or 21 times; A conjugates occur
3 or 4 times.  Every held-out block is repeated under walk streams A and B,
giving `32*32*4*2 = 8,192` solves.  Total: **20,480**.

The schedule is generated by SHA-256 digest ordering under root
`202610136106` and is materialized, reviewed, and hash-bound rather than
regenerated implicitly at launch.  `build_schedule.py --check` independently
reconstructs all rows and verifies the crossover and balance invariants.

Within every four-arm block the target root/index and walk root/index are
identical.  Thus the planted scalar `k` and numeric walk-stream seed are shared
across `C,A,P,B`, while the curve point, native tables, and resulting trajectory
remain curve-specific.  This is paired common-random-number control, not a
claim that the trajectories or curve instances are identical.  It is an
explicit pre-freeze amendment that supersedes the earlier nonfrozen discovery
blueprint's proposal to separate the walk stream by arm/domain.  The held-out
A/A repeats use two distinct walk roots; within either repeat the stream is
again shared across all four arms.  Setup and target roots remain fixed across
the two repeats.

Every curve independently runs native subgroup-generator and action
certificates, constructs `Q=kP` on that curve, recovers `k`, and checks `kP=Q`.
No curve point or walk state is transported.

## Execution and integrity

`rho.c` and `params.h` are byte-identical to the verified completed m=51
degree-271 study.  `batch_driver.c` is only a fail-closed arbitrary-plan
adapter around the same `setup_curve` and `solve_one` functions.  Records are
partitioned into at most 256-record native-curve execution units and scheduled
across four pinned workers.  This is expected to exercise 3,537 distinct
models and 3,556 setup units in the primary schedule (the crater is split into
20 units to avoid a single-core/time-segment arm), before any conditionally
required setup-robustness work.

Each setup unit records its curve, mode, seed, native generator,
reproducibility fingerprint, and setup wall seconds.  Each worker records its
plan and binary hashes, exact command, affinity, stdout, stderr, exit status,
timeout and elapsed seconds.  Raw output is normalized only after independently
recomputing every expected scalar and walk-stream seed and checking all exact
counter identities.

The adapter is compiled as a static ELF.  Admission parses its ELF program
headers and rejects `PT_INTERP` or `PT_DYNAMIC`; a successful compiler exit is
not enough.  Compiler, self-test, and worker children receive exactly this
environment, with no inherited Python or locale variables:

```text
LANG=C
LC_ALL=C
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
TZ=UTC
```

On Linux, the runner is a child subreaper and starts each native invocation in
its own process group.  Success, failure, timeout, or interruption cleans and
reaps the entire group, drains stdout/stderr only to a fixed bound, and rejects
residual descendants or diagnostic stderr.  This prevents a background child
from outliving a nominally completed execution unit or holding a pipe open.

Before any admitted run, eight fixed literal RNG vectors are evaluated by both
the Python schedule oracle and the compiled C adapter.  Each vector binds a
target seed, walk seed, target index, expected scalar, and expected 64-bit walk
stream.  The expected columns are literals rather than values recomputed by one
side, so drift in either implementation fails the gate.

Scientific launch requires one clean committed worktree and a complete
`FROZEN.sha256` over the protocol, specification, selection binding, schedule,
census, core, adapter, runner, analyzer, and tests.  The runner copies and
fsyncs those exact inputs to a new output root, builds only the snapshot, and
checks the worktree again.  Scientific runner and analyzer processes must be
started in an empty, explicitly populated environment with Python isolated mode
and bytecode disabled (`-I -B`).
The analyzer verifies and explicitly loads the run-local frozen source bytes;
it does not import a mutable worktree `design.py`.  The recorded source hash and
runtime binding must agree before analysis.  The receipt includes the exact
Python invocation and sanitized analysis environment, Python executable/hash
and flags, NumPy version/package/core-extension hashes, build configuration,
and mapped NumPy/BLAS runtime-object hashes.

There is no resume.  Output paths are exclusive, partial failures are retained,
peer workers stop on first failure, and a terminal `MANIFEST.sha256` seals every
regular file.  Missing, extra, duplicate, failed, capped, timed-out, incorrect,
or stderr-producing records invalidate the run.  Nothing is rerun or replaced
after outcomes are visible, and the session cannot be rewritten after the tree
is sealed.

Before discovery, only schedule checks, compiler/core self-tests, mock runner
tests, tamper tests, and synthetic analysis are allowed.  They are tagged
non-scientific and schema-incompatible with an admitted endpoint run.

## Accounting interval

The primary response is `walk_ops`: online group additions plus doublings
after the target-dependent table is built, including successful and abandoned
walks, starts, look-ahead operations, cycles and retries.  The runner also
retains:

- `setup_ops`, `setup_adds`, and `setup_doubles` for target-dependent tables;
- `ops`, additions and doublings with exact sum identities;
- canonicalizer calls, field squarings, sign tests, and negations;
- walks, cycles, abandoned walks, useless collisions, and solver seconds;
- native setup/selftest seconds and invocation count; and
- complete worker/process elapsed seconds.

Native generator/table construction is timed but its group-operation count is
not instrumented by the reused core.  Planted-target construction, final
recovery multiplication, and verification are likewise excluded from the
operation counter.  Field/group conversion weights are not frozen.  Therefore
`walk_ops` is a collision-walk metric, not an end-to-end ECDLP cost.  Wall time,
group operations, and field primitives are reported separately.

## Calibrated estimands

For each arm, first form a calibrated arithmetic mean of `walk_ops`, then take
base-two logarithms:

- `C`: the arithmetic mean of all 3,072 inference observations;
- `A`: the mean of 272 per-model arithmetic means, giving every A model equal
  weight despite its 11/12 observation count;
- `P` and `B`: within every pair, mean the 51 per-conjugate arithmetic means,
  then average the 32 pair means.  Every selected model and pair has equal
  weight despite its one/two observation count.

Call the log means `xC,xA,xP,xB`.  The one frozen 95% family is

```text
A-C, P-C, B-C, P-A, B-A, B-P,
M271    = (-xC+xA-xP+xB)/2,
M120871 = (-xC-xA+xP+xB)/2,
I       = ( xC-xA-xP+xB)/2.
```

`2I` is the ordinary difference-in-differences.  The three factorial summaries
and all six pairwise terms are **lattice associations**, not causal conductor
effects.  Their signs and magnitudes can identify follow-up structure but
cannot by themselves attribute it to conductor or assert a weak curve.
`P-A` and `B-C` are diagonals of the order lattice, not adjacent edges.
`2I`, its standard error, and its simultaneous interval are reported explicitly
as twice the corresponding `I` quantities; this deterministic rescaling does
not create a tenth member of the inferential family.

Sharing target and walk streams makes the observation rows common-random-number
paired, but calibration does not give every arm the same row weights.  `P` and
`B` have the same pair/conjugate weights, so only `B-P` is exactly target-paired
at the calibrated-estimator level.  The other contrasts are balanced CRN
comparisons, not exactly target-paired estimators.  The report therefore also
includes a descriptive common equal-row-weight sensitivity and per-pair and
per-model heterogeneity summaries.  Those diagnostics are not extra
inferential families and do not replace the frozen calibrated estimands.

For each contrast, recompute the nonlinear calibrated estimator after deleting
each one of the 32 P/B pair clusters.  The delete-one-pair jackknife supplies
the standard error and centered cluster influence values.  Under multiplier
root `202610136107`, 100,000 frozen Rademacher draws form a new centered
studentizer for every draw and contrast:

```text
T* = sum_i(s_i psi_i) * sqrt((n-1)/n)
     / sqrt(sum_i(psi_i^2) - sum_i(s_i psi_i)^2/n).
```

The conservative empirical order statistic `ceil((R+1)*0.95)` of the
draw-wise nine-contrast max-|T*| values is the one simultaneous critical value.
A nonpositive or nonfinite observed jackknife scale still makes the family
non-estimable.  Within a multiplier draw, a re-studentization denominator that
is zero or numerically indistinguishable from zero sets only that
contrast/draw cell's `|T*|` to infinity.  The family is declared
non-estimable for this condition if and only if the frozen critical quantile is
infinite; it never becomes a zero-width interval.  A materially negative
centered sum of squares is an analysis error rather than silently clipped.

The finite **selected-32 estimand** is reported only as a point estimate and
descriptive per-pair/per-model distribution; there is no selected-set confidence
interval.  The pair-jackknife/max-T interval is interpreted as a **modeled
population interval only conditional on the keyed-PRP/exchangeability model**.
It is restricted to the pilot-excluded population.  With only one child orbit
per parent, within-parent child heterogeneity is separately unidentified; the
modeled interval is not a census of the complete bottom level.

For the six pairwise terms only, practical equivalence is recorded when the
entire simultaneous interval is inside `[-0.10,+0.10]` bit, including equality
at either boundary.  This label means
only that no larger collision-walk association was resolved under this design.
It is not a security-bit, causal, transfer, or weak-curve assertion.

## Independent A/A gate

For each arm form the held-out `log2(mean stream-B / mean stream-A)` ratio.
A separate delete-one-pair jackknife and 100,000-draw per-draw re-studentized
Rademacher max-|T*| family produces simultaneous 99% intervals.  It uses the
same per-cell infinity and critical-quantile non-estimability rule stated above.
All four intervals must lie wholly inside `[-0.15,+0.15]` bit, including
equality at either boundary.  Failure
invalidates the nine-contrast endpoint inference; the failed records remain
sealed and are reported.  A/A solves never enter the endpoint estimates.

## Conditionally mandatory setup-robustness lane

After the held-out A/A gate passes and the primary nine-contrast family is
estimable, the runner evaluates one preregistered trigger.  It fires if **any**
primary simultaneous 95% interval strictly excludes zero (`lower>0` or
`upper<0`) and that contrast's absolute point estimate is at least `0.5` bit.
The magnitude threshold is inclusive; an interval touching zero does not fire.

Before primary workers start, the runner reconstructs and hashes the complete
conditional plan and verifies its 2,176-row/97-model/1,649-unit shape.  It then
writes and seals the complete 20,480-solve primary phase, computes the trigger
from those exact sealed bytes, and fsyncs a durable, write-once decision before
conditional work.  A false decision requires the exact absence of
`setup_robustness/`.  A true decision makes exactly one attempt at the complete,
separately sealed subtree in the same admitted run—never a resume, replacement,
or post-outcome backfill—and adds all four arms over
`17*32*4 = 2,176` solves.  The corresponding completed-run totals are therefore
20,480 solves and 3,556 setup units when false, or 22,656 solves and 5,205 setup
units when true.  If the mandatory conditional attempt fails, the outer tree is
sealed as `primary_complete_robustness_failed`: the independently sealed primary
evidence remains valid, but no setup-persistence conclusion is permitted.
An asynchronous exception immediately after an atomic primary or conditional
phase seal does not rely on stale in-memory completion state.  The runner first
re-reads the on-disk `MANIFEST.sha256`, verifies the exact file set and every
bound hash, and only then classifies the primary as independently complete or
reconstructs the completed conditional summary.  A missing, malformed, extra,
or mismatched phase artifact is never recovered as complete.

The fixed 32-slot panel contains one distinct `C` model repeated in every slot;
two hash-selected conjugates in each of 16 `A` orbits (32 distinct A models);
and one hash-selected common Frobenius exponent for each selected raw P/B edge
(32 P and 32 B models).  Thus 97 distinct panel models are exercised.  The same
32 fresh target scalars, numeric walk streams, and panel slots repeat under all
17 roots; only the setup root changes.  Sixteen SHA-256-derived roots form the
inferential family.  The seventeenth is the original primary setup root, which
is trigger-conditioned and therefore excluded from that family.  Every one of
the 97 models must have exactly 17 native setup certificates, one under each
root, with 17 distinct `(pgen_x,pgen_y,setup_fingerprint)` identities.

The 16 fresh setup roots, not rows or pairs, are the jackknife clusters.  Under
the frozen model, SHA-256-derived seeds are treated, conditional on being
distinct and admissible, as an exchangeable pseudorandom sample without
replacement from valid 64-bit setup roots; setup-root sign symmetry is also a
modeling assumption.  The delete-one-root result is n=16 model-based/asymptotic
inference conditional on the fixed panel and target/walk streams.  It
enumerates all `2^16 = 65,536` Rademacher sign vectors and re-studentizes every
draw/contrast.  The simultaneous 95% nine-way max-|T*| critical value is the
1-based order statistic
`ceil(0.95*65,536) = 62,260`; exhaustively enumerated multiplier-reference
adjusted p-values are `count/65,536`, with no Monte Carlo `+1` correction.
Enumeration removes multiplier Monte Carlo error; it does not make the result
exact finite-sample randomization inference.  The same zero-or-numerically-zero
denominator/infinite-critical rule applies.

For every primary triggering contrast, **directional persistence** requires the
fresh-root simultaneous interval to exclude zero strictly in the primary
direction.  **Practical persistence** requires the entire interval to be at or
beyond `+0.5` bit in a positive direction or `-0.5` bit in a negative direction;
equality at `0.5` is included.  Each level is summarized as `complete`, `partial`,
or `none` across triggering contrasts.  A same-sign point estimate alone is not
persistence.  The original-root result is only a descriptive matched bridge on
the identical follow-up panel/streams, with no interval or p-value.

The follow-up's fixed sparse 97-model panel and fresh target/walk streams define
a different estimand from the calibrated primary population result.  Therefore
non-persistence cannot by itself diagnose an original-root accident, even with
the bridge.  This lane cannot establish conductor causality, a security-bit or
weak-curve claim, transfer, or an end-to-end advantage.  A fully executed but
non-estimable family is sealed as
`primary_complete_robustness_non_estimable`, separate from an execution failure,
and carries no persistence label.

## Decision limits

Observed intervals may establish only bounded native walk-work associations or
equivalence in the exact stated scope.  They cannot establish:

- a causal effect of either conductor prime or their interaction;
- that any curve is weak in security bits;
- an isogeny evaluator, dual, subgroup-preserving transfer, recovery path, or
  transfer cost;
- a NIST-scale or other-field extrapolation; or
- absence of within-parent child heterogeneity.

Any stronger claim remains a separate construction and measurement obligation.

## Commands after endpoint binding and freeze

Pre-endpoint checks only:

```text
python3 -I -B build_schedule.py --check
python3 synthetic_test.py
python3 run_benchmark.py --mock --out /new/empty/mock-directory
python3 run_benchmark.py --selftest-only --out /new/empty/selftest-directory
```

After the source scan is sealed, the write-once endpoint binding uses the same
isolated environment contract:

```text
env -i LANG=C LC_ALL=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin TZ=UTC MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /absolute/path/to/python3 -I -B bind_selection.py --scan-run /sealed/discovery-run --out deep_selection.json
```

Scientific execution is not admitted until `deep_selection.json` and
`FROZEN.sha256` exist:

```text
env -i LANG=C LC_ALL=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin TZ=UTC MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /absolute/path/to/python3 -I -B run_benchmark.py --out /new/empty/scientific-run-directory
env -i LANG=C LC_ALL=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin TZ=UTC MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /absolute/path/to/python3 -I -B analyze.py /new/empty/scientific-run-directory --out analysis.json
```

The binding and freeze gates are now satisfied.  The scientific commands above
remain unexecuted at this freeze point, so the directory contains no admitted
timing or rho result yet.
