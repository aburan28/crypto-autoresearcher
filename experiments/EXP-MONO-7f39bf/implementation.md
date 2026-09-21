# EXP-MONO-7f39bf implementation notes

**Status of this document: DRAFT, in progress.** Written incrementally while
Bash tool access on the shared host is intermittently blocked by a
whole-machine `ENOSPC` (disk-full) condition on the root filesystem
(`/dev/disk3s1s1`, mounted `/`), independently confirmed by the Coordinator's
own session hitting the identical error. This is an infrastructure condition,
not caused by this experiment's own file writes (which are small; the repo
itself lives on a separate volume, `/Volumes/SSD990`, unaffected). Per
AGENTS.md rule 3 and agents/executor.md's failure taxonomy, an infrastructure
failure is never treated as negative (or positive) evidence about
IDEA-20260807-5126f4; it is recorded here and in `execution_report.yaml` as
infrastructure signal only.

## New, independent implementation

`implementation/run_experiment.py` is a new file under this experiment's own
directory. It does not import, execute, or modify
`experiments/EXP-MONO-805a02/implementation/run_experiment.py` (frozen,
read-only reference for the `.subs()` construction pattern only, per this
contract's own `inputs.reference_implementation_read_only`). It reuses
`harness/semaev.py` (`s3_expr`, `s4_expr`, `build_factor_base`) and
`harness/toycurve.py` (`EllipticCurve`) directly, per the specification's own
`invalidation_rules` (frozen implementation base).

## Construction, exactly as derived in the specification's own `objective`
and H-MONO-6adf3c's own `mechanism` field

- **m=4**: `x1,x2` fixed to concrete on-curve points `P1,P2`; `g(x_free,T) =
  S4.subs({x1:P1[0], x2:P2[0]})`, leaving `x3` (free) and the local `x4`
  symbol (playing the role of `T`) both symbolic -- the literal `.subs()`
  recipe from the specification's `objective`, with the final
  target-substitution step omitted (unlike EXP-MONO-805a02's frozen
  `stage5_m4`, which also substitutes `x4sym: Rt[0]`).
- Two branches, computed via **direct elliptic-curve arithmetic, zero
  polynomial arithmetic for this step** (per H-MONO-6adf3c `mechanism`):
  `t_+ = x(P1+P2)`, `t_- = x(P1-P2)`. For each branch,
  `quad_branch(x_free,T) = S3(x_free, T, t_branch)`, a quadratic in `x_free`
  with coefficients polynomial in `T`; `disc_branch(T)` is its discriminant.
- **m=5**: `x1,x2,x3` fixed to concrete points `P1,P2,P3`. Mirrors
  EXP-MONO-805a02's own frozen `stage5_m5` construction (`S4_numeric_U`,
  `S3_part`) with the final `.subs(T, Rt[0])` step **omitted** -- T stays
  symbolic through the resultant elimination over the auxiliary variable
  `U`. This experiment additionally builds the m=5 branch decomposition
  directly from theory: since `S4_numeric_U(U)` is a concrete quartic in
  `U` (coefficients numeric, since `P1,P2,P3` are concrete) with roots
  `u = x(e1*P1 + e2*P2 + e3*P3)`, `e_i in {+-1}`, computable via direct EC
  arithmetic (four sign combinations with `e1` fixed `+1` cover all eight,
  modulo the overall-negation duplicate) -- a standard resultant identity
  (`Res_U(A,B) = lc(A)^{deg B} * prod_i B(u_i)` for a fully-split `A`) then
  gives `g(x_free,T)` as (up to a numeric constant) the product of the four
  `quad_branch(x_free,T) = S3(x_free, T, u_branch)` quadratics -- the exact
  m=4 recipe applied per branch, generalized. Each branch's integrity is
  checked in code (`u_root_check_passed`): the computed `u` value is
  substituted back into `S4_numeric_U(U)` and verified `== 0 mod p`.

This m=5 branch construction is **new, not verified in this corpus before
this record** (named risk R1/R2 in the specification): it predicts **4**
independent branches (`2^{5-3}`), each requiring one Legendre-symbol test,
rather than the idea's own stated count of `m-2 = 3` "character levels."
Stage 0 measures and reports the actual count found; a mismatch against the
idea's own `m-2` prediction is reported as a first-class structural finding
per the specification's own `invalidation_rules`, not reconciled or patched
silently. (See `execution_report.yaml`'s STAGE0 block for the measured
counts per cell.)

## Disclosed protocol choices (left open by the frozen specification)

The specification pins `m in {4,5}`, `p in {211,431,1009}`, seeds, the
`>=1000`-candidate floor (Stage 1) and the `>=20`-sample floor (Stage 0), but
does not pin an exact factor-base size or a Groebner-probe trial count.
These are declared here, applied uniformly, and were not tuned to produce a
favorable result:

- `FACTOR_BASE_SIZE = 30` for both the interval/generator-based factor base
  (`harness/semaev.py build_factor_base(..., scope="full_curve")`, matching
  this lane's own convention) and the random-x-subset factor base
  (RANDOM-SUBSET-NULL control), so the two are directly comparable in size.
- `STAGE1_CANDIDATES = 1000` (exactly the specification's own floor).
- `STAGE0_SAMPLE_T = 25` (>= the specification's own floor of 20).
- The `m-2` concrete factor-base coordinates used to build the tower are the
  first `m-2` elements (by sorted x-coordinate, deterministic) of the
  relevant factor base (interval-based or random-subset), so the tower's
  fixed coordinates are always genuine factor-base members, matching the
  index-calculus semantics the idea's mechanism assumes.
- **RANDOM-SUBSET-NULL is implemented as a full, independent sibling
  construction** (its own Stage-0-style gate check, its own tower built from
  `m-2` points drawn from the random-subset factor base, its own Stage 1
  measurement) rather than only substituting the factor base at Stage 1
  time. This is because the tower construction is inherently tied to which
  concrete `m-2` points it was built from; reusing the interval-locus tower
  while only swapping the membership-check factor base would not test
  whether the *false-positive rate* result is an artifact of the
  interval/generator factor base's own structure, which is what this
  control is for. This interpretation is disclosed here, not assumed
  silently; the primary STAGE0-HARD-GATE decision for the (p,m) cell (which
  gates whether STAGE1/STAGE2 numbers are trusted at all) is the
  interval/generator-based construction's own gate result, matching the
  specification's own STAGE1 description ("cells where Stage 0 passed
  only"); the random-subset construction's own gate result is reported
  alongside it as an additional transparency check, and STAGE1B is only
  computed when that sibling construction itself also passes its own gate.
- **Groebner secondary metric (m=4 only)**: no pre-existing `RQ-MONO-001`
  Groebner-basis membership-test cell at `m>=4` was found in this lane
  (search: `grep -rl "groebner\|Groebner" experiments/EXP-MONO-*/specification.yaml`
  found only `EXP-MONO-805a02`, whose own mentions are Stage-6 label text
  about a different open problem's terminology, not an `m>=4` measurement
  cell). New minimal machinery was built, generalizing
  `harness/semaev.py`'s own `measure_s3_decomposition` pattern to `m=4`
  (`system = [S4(x1,x2,x3,T_fixed), fV(x1), fV(x2), fV(x3)]`,
  `sympy.groebner(..., modulus=p, order="grevlex")`). Independent timing
  during implementation showed steep growth with factor-base size at fixed
  `p=211`: size 5 -> 1.4s, size 6 -> 11.0s, size 7 -> 44.6s, size 8 ->
  150.0s (measured, not estimated). A `FACTOR_BASE_SIZE=30` probe was
  therefore infeasible within budget for a SECONDARY metric; the probe uses
  a reduced factor base (`GROEBNER_PROBE_FACTOR_BASE_SIZE = 6`, `2` trials
  per cell, `30s` soft timeout via `SIGALRM`), disclosed as not
  size-comparable to the main `FACTOR_BASE_SIZE=30` enumerate-and-test /
  resolvent numbers reported elsewhere -- a directional trend proxy only.
  `m=5` Groebner probing was **not attempted**: `harness/semaev.py` has no
  `S5` polynomial, and building one via a further full symbolic resultant
  elimination purely to run a secondary probe was judged out of scope for
  this record's budget; this is a disclosed omission of a secondary metric,
  not a gating requirement (the specification's own `success_criterion`
  does not require it).

## Field-operation counting (never fabricated)

Legendre-symbol / filter-evaluation field operations are counted by a
hand-rolled square-and-multiply `modpow_counted` that increments a counter on
every modular multiplication actually performed -- a genuinely measured
count, not a `2*log2(p)`-style closed-form estimate. Tower-construction cost
(sympy's internal polynomial arithmetic for building `disc_branch(T)`) has no
such observable modmul counter (sympy does not expose one for
`Poly`/`resultant`/`discriminant`); per `harness/semaev.py`'s own "honesty
note" convention (report observable proxies, never a fabricated theoretical
count), only wall-clock seconds is reported for tower construction, both
un-amortized and amortized over the Stage 1 candidate count
(COST-GATE-TOWER-CONSTRUCTION-CHARGED).

## UNIT-DECLARATION-TRIPWIRE

No group-operation-to-field-operation conversion constant is declared
anywhere in this frozen contract (its own control text says so explicitly,
citing EXP-MONO-805a02's identical control). Accordingly, every Stage 2
result sets `refused_no_declared_conversion: true` and reports the
resolvent route's field operations and `D_trial(E) = m-1` group operations
(cited from IDEA-20260806-9d47e2 / EXP-MONO-805a02's own
`STAGE3-OPERATION-COUNT`, not re-derived) **side by side**, never combined
into a ratio.

## Independent verification path (GROUND-TRUTH-INDEPENDENT-CODE-PATH)

Stage 1's ground truth for "does a genuine factor-base-element root of
`g(x_free,T)` exist" is computed by brute-force root-finding of `g`'s own
univariate specialization at the concrete candidate `T` (via
`bruteforce_roots_mod`, iterating all of `F_p`) intersected with the factor
base set -- a second, independent code path from the character-tower filter
itself (`evaluate_candidate`), which only ever consults `disc_branch(T)`'s
Legendre symbol and the branch quadratics' own coefficients, never the
brute-force root list. Any REJECT verdict that brute-force finds to have a
genuine root is reported as `n_reject_exceptions_instrument_bug_candidates`
-- per the specification's own control, this would indicate an instrument
bug in the filter's derivation/evaluation, never evidence against the
idea's mechanism (the REJECT branch is supposed to be an exact necessary
condition).

## p=431 curve

Found by the specification's own deterministic lexicographic search
(`curve_selection.p_431.search_procedure`), executed inside
`run_experiment.py`'s own `find_p431_curve()` (not pre-computed or assumed):
**A=1, B=1** is the very first pair tried (`tries=1`) satisfying
non-singularity, non-supersingularity, and a prime-order subgroup >= 20:
`E: y^2 = x^3 + x + 1` over F_431, `#E(F_431) = 464 = 2^4 * 29`, trace
`t = -32` (`-32 mod 431 != 0`), largest prime-order subgroup **29**. This is
verbatim script output, reproduced in `raw-result.json['p431_curve_search']`
for each run.

## Pre-freeze smoke-test observations (NOT run records; informal, reduced
trial counts, kept here only for transparency about implementation
correctness before the real battery ran)

With `STAGE1_CANDIDATES` temporarily reduced to 50 and `STAGE0_SAMPLE_T` to
5 (m=4, p=211, seed=20260905, interval-generator factor base): STAGE0
`status=pass`, `deg_free_measured=4` (matches `2^{4-2}` prediction),
`n_branches_T_dependent_discriminant=2` (matches the `m-2=2` prediction
exactly at m=4), root-set check 0/5 mismatches. STAGE1 (50 trials, informal):
`n_pass=50`, `n_reject=0`, `false_positive_rate=0.34`. These numbers are
**not evidence**: 50 trials is far below the specification's own `>=1000`
floor, and `n_reject=0` in a 50-trial sample is itself worth re-checking at
the full 1000-trial count (reported honestly in the real run regardless of
which direction it points). They are recorded here only to show the
pipeline was exercised and produced internally-consistent output before the
disk-full infrastructure blocker below.

## Infrastructure blocker encountered during implementation

While smoke-testing the m=4 secondary Groebner-probe machinery at
`p=211`, `factor_base_size in {5,6,7,8}`, sympy's `groebner(...,
modulus=p, order="grevlex")` measured wall times of 1.4s / 11.0s / 44.6s /
150.0s respectively (steep, apparently exponential growth) -- this measured
data directly motivated the reduced-probe-size disclosed choice above, not a
report of infrastructure failure by itself.

Separately (and unrelated to this experiment's own resource use), the
shared host's root filesystem (`/dev/disk3s1s1`, mounted `/`) began
returning `ENOSPC` on essentially every Bash tool invocation partway through
implementation/smoke-testing, independently confirmed by the Coordinator's
own session hitting the identical condition and escalated by the
Coordinator to the user (only the user can free disk space on the shared
box). This blocked further Bash-based execution (including running the real
1000-trial battery and the p=431 search's own live re-verification) for a
period; `Write`/`Read`/`Edit` on this repository (`/Volumes/SSD990`, a
separate volume) remained unaffected throughout, which is why this
`implementation.md` and the implementation source could still be authored
during the blockage. Per AGENTS.md rule 3 / agents/executor.md's failure
taxonomy, this is recorded as `infrastructure_error`, not as measurement
evidence in either direction for IDEA-20260807-5126f4. See
`execution_report.yaml` for the final disposition (either full battery
results once Bash access returned, or a `failed_infrastructure` status if
the condition did not clear within this task's reasonable budget).
