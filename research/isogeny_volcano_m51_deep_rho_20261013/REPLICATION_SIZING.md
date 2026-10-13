# Provisional sizing for a fresh four-level replication

This is a post-run planning calculation, not a frozen protocol, approval,
confidence claim, or continuation of the sealed run. A future replication can
release only its own predeclared result. It cannot repair or retroactively
release labels from the run whose status is `aa_alert_labels_withheld`.

## Inputs and assumptions

The calculation treats the completed 32-cluster run strictly as a variance and
offset pilot. It assumes:

- the same four arms, block allocation, calibrated estimators, cluster unit,
  and disjoint two-stream A/A design;
- the frozen simultaneous A/A critical value remains `q_AA=3.2758` and the
  all-arm interval margin remains `[-0.15,+0.15]` bit;
- each pilot A/A point estimate is the planning value for its future true
  offset;
- every standard error scales as `sqrt(32/N)` with the number `N` of fresh
  parent clusters;
- the max-|T| critical value, variance structure, leverage, and missingness do
  not worsen; and
- Normal approximations are adequate for sizing.

Those assumptions are not guaranteed. In particular, the pilot variance is
uncertain at 32 clusters, and the primary `P-A` contrast assigns 52.6% of its
squared jackknife influence to one cluster.

## Planning calculation

Using the observed A/A offsets and standard errors with the scaling above,
`N=96` gives approximate per-arm probabilities that a future simultaneous
interval fits strictly inside the margin:

`p_i(N) = Phi((0.15-q*s_i(N)-delta_i)/s_i(N))
          - Phi((-0.15+q*s_i(N)-delta_i)/s_i(N))`,

where `s_i(N)=s_i(32)*sqrt(32/N)`. The reported family lower approximation is
`1-sum_i(1-p_i)`.

| arm | approximate gate probability at `N=96` |
| --- | ---: |
| C | 0.999997 |
| A | 0.987998 |
| P | 0.999169 |
| B | 0.975480 |

The union-bound family lower approximation is `0.96264`. This is conditional
on the pilot-based assumptions, not a guaranteed pass probability. If every
true A/A offset were instead exactly zero, about 56 clusters (rounded to 64)
would target 90% family assurance under the same approximation; that more
optimistic scenario ignores the observed A and B offsets.

The largest current primary simultaneous half-width is about `0.07003` bit.
Holding its critical value and variance constant gives these projections:

| fresh parent clusters | total solves (`640*N`) | projected worst half-width |
| ---: | ---: | ---: |
| 64 | 40,960 | 0.0495 bit |
| 96 | 61,440 | 0.0404 bit |
| 128 | 81,920 | 0.0350 bit |

`N=96` is the smallest listed planning point aimed above 90% approximate gate
assurance under the observed-offset model. `N=128` is the proposed fixed-N
planning target because it adds margin for pilot variance uncertainty and the
observed leverage concentration. Calling it larger does not make gate passage
certain.

## Independence and stopping requirements

A future protocol should freeze a new PRP domain and exclude every previously
measured parent cluster and its bottom-child fiber, as well as the already
excluded feasibility-pilot fiber, before selecting endpoints. Excluding all
42 parent orbits found by the completed scan is the simplest auditable rule and
also keeps the ten unmeasured discoveries out of a nominally fresh sample.
Fresh setup, target, walk, and A/A roots are required.

The scan range, fixed `N`, selection order, exclusions, failure policy,
estimators, nine-contrast family, gate, margins, and stopping rule must be
committed before execution. If a complete frozen scan range yields fewer than
128 eligible clusters, retain it as a bounded census, do not backfill or start
the 128-cluster rho run, and freeze a separate extension before continuing.
There is no repeat-until-pass rule and no post-outcome margin change.

## Scope boundary

This sizing concerns the native same-negation association lane. A rigorous
weak-representative audit separately benchmarks each level's best certified
usable native action. Transfer claims still require executable maps and duals,
subgroup preservation, scalar recovery, and complete construction,
evaluation, verification, memory, and amortization costs.
