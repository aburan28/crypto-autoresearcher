# Coverage ratio qualification for the CMFB review

This additive correction applies to the interpretation of PR #2418 at
`bfab487f3655603548db77d204bc0ce0cd02360a`. It preserves the archived
`EV-CMFB-e3d1ec`, `DEC-20261019-f33f3e`, hypothesis, reviewer records and runs.
The author's concurrent correction at `2a635d1907894bf84c795949bfc31deeaa65e3f1`
adds `CORR-20261019-a89bfa` and prominent qualifications to the analysis and
decision report, including its PDF. Those changes are retained. The companion
hash bindings identify the earlier review snapshot and the later author update
separately. This correction makes no new scientific decision and supplies no
execution approval.

## Exact identity and conditional ratio

For a base of B elements and unsigned size-three multisets, let
`M = binomial(B+2,3)`, `mu = M/N`, and let `c_D(r)` count decompositions of r.
The exact conservation identity is `sum_r c_D(r) = M`. Consequently the
coverage fraction `C_D = #{r: c_D(r)>0}/N` satisfies
`C_D <= min(1,mu)`. This argument determines the total count; it does not
determine how that count is distributed among targets.

For any specified positive baseline coverage `c0`, the resulting ratio bound is

```
C_D / c0 <= min(1,mu) / c0.
```

Replacing `c0` by `1-exp(-mu)` adds a Poisson occupancy assumption. Under that
model the right side is at most `1/(1-exp(-1))`, approximately 1.58198. For
`0 < mu <= 1`, `mu/(1-exp(-mu))` increases to that value; for `mu >= 1`,
`1/(1-exp(-mu))` decreases from it. If only a proved positive lower bound L
for the relevant baseline is available, the rigorous ratio bound is instead
`min(1,mu)/L`. A heuristic approximation with an error tolerance must retain
that tolerance in the denominator.

The cited conservation derivation proves the identity and absolute coverage
bound. `KN-FIND-007` also states the 1.582 expression, but its cited identity
does not supply the additional baseline lower bound. The CMFB hypothesis calls
Poisson occupancy heuristic H2. Thus passages in this PR calling 1.582 a
universal finite-instance theorem should be read as a conditional model bound.
The approximate signed-convention headroom quoted by the red team has the same
baseline dependence and its own counting convention.

References: [conservation derivation](../../EXP-FB3-001/conservation.md),
[finding KN-FIND-007](../../../knowledge/findings/KN-FIND-007.md),
[hypothesis](../../../ledger/hypotheses/H-CMFB-9b2eed.yaml),
[evidence](../../../ledger/evidence/EV-CMFB-e3d1ec.yaml),
[decision](../../../ledger/decisions/DEC-20261019-f33f3e.yaml).

## Retained empirical scope

The reported statistic divides the recorded small-x coverage by the arithmetic
mean of 200 recorded matched random-base coverages. That observed denominator
can be used directly. The conservation identity and the model qualification do
not replace it or change the archived T values. The empirical interpretation
remains confined to the tested instances, unsigned multiset convention,
integral chart and base definition, with `2^14 < p <= 2^25` and the declared
0.5 percent resolution. It does not establish distributional equality at zero
resolution, an end-to-end cost bound, or a result for untested bases or sizes.

The separate D1/D2 analysis retains classification `NULL_AT_RESOLUTION`, with
powered cells C20 and C24 under the specification text. This review recomputed
T, MDE, I10 and Holm arithmetic from retained values and checked that the two
stored analysis objects differ at exactly the 53 declared fields after excluding
the separately identified timing and peak-RSS fields. No bootstrap or
randomization resampling, producer trial, solver or new-instance campaign was
run for this correction.

The archived analyzer's reproduction comparator permits floating differences
up to `1e-12 * max(1,abs(a),abs(b))`; its report's exact or leaf-for-leaf wording
therefore exceeds that comparator's guarantee. The archived validator's eight
scratch rebuild outputs are not committed. This PR review checks retained
records and the archived comparison logs; it does not independently certify
byte-identical historical scratch output or execute a new rebuild.

The 703.303 seconds and 2642.604 CPU seconds in the manifests describe the
driver scopes. The execution receipts total 940.148115 wall seconds including
their checker intervals. Those scopes must remain separate in any later cost
accounting. No new cross-method ranking is made here.
