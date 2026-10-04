# Prospective amendment readiness for TASK-20260907-e11ec7

This zero-run Coordinator handoff produced five additive prospective replacement
contracts. Each contract now makes its mathematical objects, deterministic
algorithms, controls, counts, thresholds, exceptional cases, costs and artifact
requirements decidable without a promised later “Stage 0 definition.” At the
design level, no unresolved mathematical or runtime-definition gap remains.

This document does **not** approve or freeze any experiment. Every amendment has
`approved_by: null`, `execution_authorized: false`, and
`evidence_eligible: false`. No experiment, simulation, fixture search, control,
solver or performance measurement was run. No hypothesis or experiment status
was changed, and no numerical value below is an observation.

## Binding and provenance

- Handoff: `TASK-20260907-e11ec7`, a maximum-zero-run mathematical-design task.
- Source snapshot: `3108ed960bdcc51ab895f5c9d0d342fe4bc24e38`.
- Parent archive task: `TASK-20260907-73a70e`.
- Inference policy: `research-deep`, reasoning effort `max`, resolved by the
  committed binding to OpenAI `gpt-5.6-sol`.
- `fallback_allowed: false`; no fallback or degraded execution was used.
- `model_verified: false`: this handoff made no fresh API probe and does not
  claim one.
- No provider, endpoint or model containing `bedrock` was used.
- Mathematical and protocol statements are derived prospectively from the five
  bound source specifications, their archived designs, the five internal
  hypotheses, the six internal proposals, the pinned toy-curve/rho source
  capsule, the supplied internal technique records and the supplied frontier
  inventory. Recalled literature is never used as decision evidence.

The source-binding strings were re-read from the committed handoff capsule at
finalization. They are:

```yaml
- path: experiments/EXP-ECDLP-184fc4/specification.yaml
  sha256: a805989f1ae1880afef401ab98a764067e41eefec87afbc2c5804a4844bdf82a
- path: experiments/EXP-ECDLP-0c717c/specification.yaml
  sha256: 949b447b57e2d652e1d021e8f19c8bb3f6f4b29c4f90fd8c86aef4ae3667b6c2
- path: experiments/EXP-ECDLP-1e6502/specification.yaml
  sha256: 873a61b27d90b0da2f134ce0bb0412cd7d13b1ff7f2b2973632f05ce3b17e82a
- path: experiments/EXP-ECDLP-2c3d20/specification.yaml
  sha256: d38d39bfb8aeee1874433ef054605bc32fdbbc190496bd152379561bf8e62854
- path: experiments/EXP-ECDLP-709063/specification.yaml
  sha256: fbb7e4a95a35b98eee07abe93828ad532301fe83e69b8ffdca67435e262a6bff
- path: coordination/experiment-reserve/BATCH-c26423/designs/EXP-ECDLP-184fc4.yaml
  sha256: 4995223f9be76e1b0d8309f2b1dc488204ac139a002b6e5fdcde6cc93199605d
- path: coordination/experiment-reserve/BATCH-c26423/designs/EXP-ECDLP-0c717c.yaml
  sha256: 67689bf7a9690dc4386d0ac4a0b02e008bdc277a2288ea763f906453719aeaa2
- path: coordination/experiment-reserve/BATCH-c26423/designs/EXP-ECDLP-1e6502.yaml
  sha256: 15726d4745789823107717f14e5dcbe0bafe373c09c7c79912eb4b7069be480b
- path: coordination/experiment-reserve/BATCH-c26423/designs/EXP-ECDLP-2c3d20.yaml
  sha256: ca59f4b0c4b79dbd8cb74f57e0a6c4307d78669d1aa280a16dc306a744979f39
- path: coordination/experiment-reserve/BATCH-c26423/designs/EXP-ECDLP-709063.yaml
  sha256: 1a1b32ceaa7cc8362ae4f1c8676b410a0787c7e1e2333ec214d5e343ec0e76ec
- path: coordination/experiment-reserve/BATCH-c26423/designs/readiness.md
  sha256: 6e79e84a94b1b8a859df42985b4b800ff3078496b5f5b1f3c4708176e15cbf55
```

Each archived-design binding above is at snapshot commit
`3108ed960bdcc51ab895f5c9d0d342fe4bc24e38`. The two amendments authored last
were corrected before relinquishment to use the exact `BATCH-c26423/designs/`
paths from this capsule.

The exact new artifacts are:

1. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/EXP-ECDLP-184fc4.yaml`
2. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/EXP-ECDLP-0c717c.yaml`
3. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/EXP-ECDLP-1e6502.yaml`
4. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/EXP-ECDLP-2c3d20.yaml`
5. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/EXP-ECDLP-709063.yaml`
6. `coordination/experiment-reserve/BATCH-c26423/amendments/TASK-20260907-e11ec7/readiness.md`

## Contract readiness matrix

| Experiment | Design disposition | Fixed primary scope | Exact prospective accounting | Remaining launch work |
|---|---|---|---|---|
| `EXP-ECDLP-184fc4` | Contract-complete, pending Coordinator approval | Seven bit rungs, two domain-separated strata, three replicates, 567 frozen real functions, 64 common marginal permutations, paired order-2q controls | 42 primary curve bundles; 23,814 observed spectra; 1,524,096 null spectra; 42 control bundles | Bind implementation blob hashes, materialize the deterministic cell manifest, run instrument fixtures, independently review, snapshot and approve |
| `EXP-ECDLP-0c717c` | Contract-complete, pending Coordinator approval | Four bit rungs, two strata, three replicates, two gammas, interval/residue bases, additive/quadratic envelopes, size-matched nulls, index-two controls | 24 primary bundles; 96 observed base cells; 1,248 underlying null permutations; 2,496 null-base evaluations; 4,992 null envelope values; 48 control-base cells; 48 observed and 384 common-null slope trajectories | Bind arithmetic/FFT implementations, materialize bases and cell manifest, run fixtures, independently review, snapshot and approve |
| `EXP-ECDLP-1e6502` | Contract-complete, pending Coordinator approval | Six non-anomalous and four anomalous bit rungs, two families, three replicates, precisions 2/3, eight raw digits and sixteen post-functions per digit at precision 3, 64 common permutations | 36 non-anomalous bundles; 8,568 observed spectra; 548,352 null spectra; 24 anomalous bundles; 480 certified target/recovery cases; 36 run artifacts | Implement/review the explicit ring, group, chart and formal-log API; run arithmetic fixtures; materialize manifest; snapshot and approve |
| `EXP-ECDLP-2c3d20` | Contract-complete, pending Coordinator approval | Seven bit rungs, two strata, three replicates, r in 4/8/16/32, 40 partitions, 64 pointwise-label null maps, stationary-basin weighting, order-2q control | 42 curve bundles; 168 true maps; 10,752 null maps; 6,720 true and 430,080 null lumped matrices; 960 true and 61,440 null lumped-slope trajectories; 42 controls | Bind pinned rho blobs, implement independent functional-graph/SVD fixtures, materialize fixture-dependent itinerary row count, independently review, snapshot and approve |
| `EXP-ECDLP-709063` | Contract-complete, pending Coordinator approval | Four subgroup sizes, two shared instances per size, two executions, three positive table budgets, 16 rho streams per instance/execution, exact packed table | 8 shared instances; 16 run artifacts; 48 Arm-A rows; 48 Arm-B rows; 16 unbounded-BSGS rows; 256 rho rows; 8 representation-control records; 368 total algorithm rows | Materialize/review the new shared-instance manifest, additively bind sibling `EXP-ECDLP-4320a7`, implement golden table/accounting fixtures, bind solver blobs, snapshot and approve |

The “remaining launch work” column contains implementation, custody and approval
gates. It does not defer a formula, algorithm, threshold, exceptional case or
scientific decision rule. A failed future implementation fixture remains an
instrument outcome; an infrastructure failure remains non-scientific.

## `EXP-ECDLP-184fc4`: resolved definitions and derivations

The amendment freezes the complete 567-member library by expansion rather than
the source’s approximate count: 525 x-residue indicators, 14 y-residue
indicators, nine Legendre functions, sixteen interval functions and three mixed
functions. It gives every function a full length-­`N` real array, an exact
centering rule, the DFT convention, deterministic maximum/argmax ties, variance,
null normalization, half-energy ordering and seven-rung log-log slope.

The synthetic cosine is treated as a real function. Its centered DFT has the two
conjugate peaks `a0` and `N-a0`; calling this a single complex-frequency peak was
incorrect. The order-2q descent control is also explicit: for the unique
two-torsion point `T=(e,0)`, the local extension is
`delta(T)=Legendre(3e^2+A)`, and the accepted control requires this value to be
`-1`, exhaustive multiplicativity, and the exact parity frequency `q` on a
length-­`2q` log array.

All 64 null permutations for a cell use the same permutation index across every
library member. That preserves the dependence needed for max-over-library
descriptions and requires a named joint exchangeability assumption: under the
null, the observed labeling and the 64 domain-separated marginal permutations
are exchangeable conditional on the frozen curve and function multisets. The
minimum attainable rank is therefore `1/65`; no family-wise p-value finer than
that is claimed.

The source’s fixed `0.5` half-energy value is separated from the correct white
exponential-order-statistic benchmark, approximately `0.1867` in the large-­`N`
model. The empirical permutations remain the primary finite-sample null. Exact
identities, such as centering, Parseval and the order-2q character, are reported
as arithmetic controls; square-root spectral and half-energy values are
statistical models. The amendment never promotes a numerical invariant into a
probability law.

## `EXP-ECDLP-0c717c`: resolved definitions and derivations

The primary and order-2q curves now have deterministic, domain-separated
generation and complete certificates. The interval and residue bases have
literal predicates and a fixed first-in-log-order selection rule. For every base,
unordered pairs use `i<j`; the only geometric exclusion is a sum equal to `O`,
and every accepted sum contributes exactly once to the length-­`p` histogram.
Both Fourier envelopes divide by the recorded accepted count `L`, with `L=0`
and failed mass checks defined as invalid cells rather than silent exceptions.

The matched null is fully counted. At 12, 16 and 20 bits it has 32 permutations;
at 24 bits it has eight. A null permutation is shared between the interval and
residue predicates at a fixed curve/gamma cell so the paired comparison is
defined. Only common null indices `0,...,7` span all four rungs and therefore
enter null slope trajectories. Percentiles, ranks, zero-mass cases and
deterministic ties are specified exactly.

The additive envelope is a statistical diagnostic. The quadratic envelope on
the certified index-two subgroup has the exact normalized value one under the
declared character identity. These two statements are kept separate. The
amendment defines 48 observed slope trajectories and 384 common-null trajectories
and uses descriptive replicated review thresholds rather than inventing a global
significance level from the correlated cells.

## `EXP-ECDLP-1e6502`: resolved definitions and derivations

All ring precision and chart choices are explicit. A Teichmüller representative
at precision `s` is `T_s(x)=x^(p^(s-1)) mod p^s`; `y` is lifted by the stated
Hensel recurrence. The affine addition chain computes `[N-1]L`, and the final
addition with `L` is evaluated in a denominator-safe `(t,w)` chart. The chart is
`[t:-1:w]` with `w=t^3+A*t*w^2+B*w^3`, so a nonunit affine denominator is not
silently divided.

For `p>7`, `s<=3` and `t` in the formal kernel, the formal logarithm begins
`log_E(t)=t+(2A/5)t^5+(3B/7)t^7+...`; all correction terms have valuation beyond
the used precision, hence `log_E(t)=t mod p^s` in this scoped protocol. The sign
of the first correction is positive. This series convention was checked against
the parent-retrieved Sage formal-group documentation; it remains a prospective
derivation until implementation fixtures independently confirm the encoded group
law.

On a non-anomalous curve with `p` not dividing `N`, the formal kernel modulo
`p^s` has exponent `p^(s-1)`. Thus `u=N^(-1) mod p^(s-1)` and the section is
`S_t(R)=L-[u]([N]L)`. This is the explicit inverse formula missing from the
source. The source’s simultaneous instruction to refuse `p|N` and use `N=p` is
resolved by separating two routines: `torsion_section` refuses `p|N`, while
`anomalous_log` requires `N=p`, maps with `[p]` into the formal kernel, and never
calls the nonexistent inverse of `p`.

The first defect digit uses the exact Teichmüller/Fermat-quotient relation; the
second is the second base-­`p` digit of the formal logarithm of the full group
difference between the Teichmüller point and the torsion section. It is not an
unchecked second-order coordinate subtraction. Precision-three objects are
reduced to precision two before comparison.

The raw digit list is complete: the two lifted coordinate digits, Fermat
quotients, first Teichmüller defects, first and second formal defect-log digits,
and the second precision-three x digit. Every raw digit has all sixteen frozen
post-functions. Precision two therefore has 102 spectra and precision three 136
per curve, for 8,568 observed spectra in total. `O`, `x=0` and `y=0` use the
declared zero extension and stay in the full length-­`N` array. Five exact
self-check families, all thresholds, 64 common permutations and the 480 anomalous
recovery certificates are specified before execution.

## `EXP-ECDLP-2c3d20`: resolved definitions and derivations

The primary curves use two disjoint deterministic generator streams and three
source seeds at every rung. The true transition exactly matches the pinned rho
table:

`c_j=seed_int(seed,'rho_cj') mod N`,
`d_j=seed_int(seed,'rho_dj') mod N`,
`t_j=c_j+d_j*k mod N`, and
`F(i)=i+t_(x([i]P) mod r) mod N`, with `O` assigned branch zero.

The archived null merely permuted the `r` branch names, which retains every
original branch fiber. The replacement null assigns a separate domain-separated
uniform label to every scalar index and each of 64 null replicates, while sharing
the exact step table. Since each `r` is a power of two, a bit mask has no modulo
bias. Realized label imbalance is recorded and never redrawn.

For a deterministic functional graph, the stationary measure is fixed as the
uniform-start Cesàro limit: every node on cycle `C` receives
`|B(C)|/(N|C|)`, and transients receive zero. This removes the nonuniqueness that
made “solve for a stationary distribution” incomplete. The lumped matrix uses
these exact rational masses. After subtracting the rank-one stationary component,
the contract reports the **leading** singular value of the centered normalized
operator; the archived “second singular value after centering” had no stable
indexing meaning.

The forty partitions, zero-mass behavior, depths, finite cyclic half-arc,
point-weighted and class-weighted aggregates, class spectra, deterministic
20-percent size matching, conditioning/rejection costs, numerical residuals and
descriptive rank rules are all frozen. The fixture-dependent number of itinerary
rows is not guessed: its exact pre-run formula is the sum of
`K(N,r)=floor(log(sqrt(N))/log(r))` over the 168 true maps and 64 times that for
the nulls, and the frozen instance manifest must evaluate the integer before any
metric runs. That is a deterministic manifest field, not an unresolved
definition.

The order-2q control uses `delta(T)=Legendre(3e^2+A)`, requires value `-1`, and
checks every homomorphism/parity identity. The 64-null resolution is explicitly
descriptive: repeated rank `1/65` effects at both largest rungs, in both strata
and at two of three replicates, queue independent review; they do not promote a
claim or establish a conditioned solver speedup.

## `EXP-ECDLP-709063`: resolved definitions and derivations

The supplied `EXP-ECDLP-4320a7` source is `review_required`, unfrozen,
unapproved, unauthorized, has an empty seed list and has no supplied instance or
run artifact. There is therefore nothing immutable to inherit. The amendment
freezes the literal public master seed
`EXP-ECDLP-709063|shared-instance-set|v2|TASK-20260907-e11ec7|20260907`, exact
SHA-256 candidate-seed derivation, acceptance/certification predicates and two
instances at each size. The resulting future manifest is the sole shared set;
`EXP-ECDLP-4320a7` must receive an additive manifest binding before either sibling
runs.

The table is a portable, fixed physical object. A slot is exactly four
little-endian uint32 fields `(x,y,exponent,state)`, hence 16 bytes. State zero is
empty, one is affine and two stores `O` with zero coordinates. With a `0.70` load
limit, the exact `(slots,usable entries)` pairs are `(0,0)`, `(256,179)`,
`(2048,1433)` and `(16384,11468)` for budgets 8, 4,096, 32,768 and 262,144 bytes.
The byte buffer is allocated once, has no grow/rehash/spill path, and an `E+1`
insertion must return `TABLE_FULL` with unchanged identity, length, content hash
and retained lookups. This tests an addressable physical table rather than an
advisory counter and does not depend on Linux `RLIMIT_AS`, `ENOMEM` or process
termination.

Arm A stores `m=ceil(sqrt(N))` baby steps or refuses before solving when `m>E`;
that outcome is a feasibility cliff. Arm B stores exactly `E` baby steps and
uses giant increment `[E]P` through `ceil(N/E)` blocks; only this arm defines a
cost crossover. Unbounded BSGS uses the identical representation at sufficient
capacity. All operations, including precomputation and solution certification,
run through the same charged group wrapper as rho.

Each execution derives sixteen rho table/start streams per instance from the
same master seed and requires at least twelve certified successes. The median
uses all successful, fully charged `total_group_operations`; failures remain in
raw data. For each instance and budget,
`D=ops_ArmB-median(ops_rho)`, and the two-instance median is evaluated at each
rung. A result is only a replicated adjacent negative-to-nonnegative bracket, a
strict bound above 28 bits, a bound at or below 16 bits, or
`NONMONOTONE_OR_INCONCLUSIVE`. No interpolation is allowed.

The source model `N*=(cE)^2` is retained in its own optimistic-model field and is
never presented as measured. A discrete charged model is shown separately. The
unbounded-BSGS ordering is descriptive rather than a forced truth: solution and
accounting correctness are valid controls, while assuming which correct solver
must be faster would make the experiment circular.

## Exact-vs-statistical boundary across all five contracts

The following are prospective exact checks: curve/subgroup certificates, array
length and mass, centering and Parseval identities, deterministic seed and table
derivations, p-adic congruences at fixed precision, formal-kernel section domains,
functional-graph stationarity equations, buffer size/capacity, operation-component
sums, and `[k_hat]P=Q` certificates. If one fails, the affected instrument is
invalid or inconclusive.

Permutation ranks, slopes, null envelopes, half-energy models, SHA-derived
random-label behavior, bootstrap intervals, rho cost distributions and crossover
replication are statistical or pseudorandom-model quantities. They are never
converted into exact invariants. With 64 common nulls, `1/65` is the finest
descriptive rank and does not supply an unregistered global error rate.

Every future timeout, crash, dependency problem, deterministic candidate-search
exhaustion, watchdog stop or memory exhaustion is infrastructure. It cannot
falsify a mathematical mechanism. Every future surprising valid observation is
retained, archived and independently reviewed before any claim-changing decision.

## Parent completion checks

The parent Coordinator still needs to perform repository-level checks that this
no-command design session cannot truthfully claim:

1. Read back and parse all five YAML amendments and this Markdown file.
2. Confirm exactly these six paths are new and no concurrent file changed through
   this handoff.
3. Recompute file hashes, source bindings, archive coverage and the post-write
   dispatch/claim plan.
4. Run the ledger, handoff-schema and repository validation commands from the
   parent worktree; a PASS is operational validation, not scientific evidence.
5. Snapshot the exact six-artifact set under `TASK-20260907-73a70e`.
6. Conduct implementation-readiness review. Under standing user authorization,
   record approval only in a separate committed Coordinator decision after the
   implementation and custody prerequisites are satisfied.

Until those steps occur, the accurate disposition is: **five mathematically
complete prospective contracts, all unapproved and unrun, ready for parent
snapshot and implementation-readiness review**.
