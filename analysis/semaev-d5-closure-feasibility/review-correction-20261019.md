# Review correction: conditional memory sizing and evidence scope

This additive correction qualifies the [original report](report.md),
[frozen proposed card](CARD-d5-c19.md), and its PDF. Those records, all three
calibration rows, the estimator output, and the plots are retained unchanged.
This is an allocation-code and arithmetic review, not another closure run or
an approval of the proposed experiment.

## The square-matrix number is conditional

For C19 at degree five, the exact column count is
`C = sum(comb(40, d), d=0..5) = 760099`. The expression `C*C/8` is about
72.2 decimal GB of unpadded bit payload **if a matrix has C rows**. It does not
establish the allocated row count. Consequently, twice that expression is
neither an unconditional peak-memory lower bound nor a complete peak estimate.
The earlier statement `>= 145 GB` must not be used as a proved requirement.

The allocation sites in
[`lfdclose2.c`](../semaev-m2-last-fall-degree/code/lfdclose2.c) instead give the
following phase-dependent payload accounting. Let `w = ceil(C/64)` words per
row before any library alignment; actual M4RI row stride and workspace must
also be included in host sizing.

| Phase | Simultaneously retained matrix/map payload, before library overhead |
| --- | --- |
| Initial Macaulay elimination | `8*w*max(R0,1)`, where `R0` is the number of generated rows at that degree |
| Replacement within an iteration | `8*w*(R_A + rank_A + take + nnew)`: old A retains its allocated `R_A` rows, new B has `rank_A + take` rows, and Lw has `nnew` rows |
| Certificate export | Retained A plus `8*C*max(1,ceil(nq/64))` for the map; B and Lw are no longer live |

`R0` is the sum of the numbers of permitted monomial multipliers over the
nonzero input polynomials. The preliminary degree-four Macaulay matrix is
freed before the degree-five matrix is allocated. At a replacement step,
`take` is bounded by the configured chunk size and the remaining products;
the old allocated row count can exceed its reduced rank. Arrays of column
masks, pivots, new-row indices and multiplication flags, the input polynomials,
M4RI workspaces and allocator overhead add further memory.

Thus, two live matrices need not both have C rows, and the implementation also
holds Lw during their overlap. The certificate map belongs to a later phase.
For the card's illustrative `nq=100000`, the map alone is approximately
9.50 decimal GB, conditional on that unmeasured quotient dimension.

## Planning consequence

The fitted 98.1 GB RSS is an extrapolation from three smaller recorded points;
it is not a lower bound or a validated prediction for C19. The proposed
256 GB host is a planning choice, not an established minimum or a demonstrated
sufficient capacity. This packet does not establish that 768 GB is unnecessary.
Before selecting a host, bind the exact system and chunk size, determine the
initial row counts, account for row stride and each allocation phase, and state
what remains unknown about rank, iteration history and library workspace.

The three-point wall-time and RSS fits in `estimate-output.txt` reproduce
exactly from `calib.json`. This verifies the recorded arithmetic, not the
original measurements. The packet does not include the `calibrate.sh` named
in the estimator docstring, the exact calibration-system artifacts, complete
argv/environment receipts, or their raw resource logs. Recover and bind those
records before treating the calibration as independently replayable. Three
points permit a residual fit calculation, but do not establish a reliable
predictive uncertainty interval for this extrapolation.

## Closure-certificate interpretation

The inherited [closure verification correction](../semaev-m2-last-fall-degree/results/verification-correction-20261019.md)
applies here as well. The checker establishes containment of the degree-bounded
closure in its checked kernel and excludes one when the certificate checks
pass. It does not independently establish equality with that kernel. Its
codimension claim is a lower bound; intersection dimensions of the kernel are
upper bounds for the corresponding closure dimensions.

The reported degree-four exclusions concern the specific recorded systems.
They do not establish a threshold for every larger instance. Either outcome
of a future degree-five test is scoped evidence about its exact input; neither
alone proves a uniform degree bound or its absence. Original certificates
were not replayed as part of this PR review.

The existing calibration plots and PDF are preserved: their three displayed
data points and fitted curves have not changed. Their extrapolations acquire
the qualifications above, rather than becoming new measurements or resource
guarantees. No hypothesis, decision, frozen protocol or execution authority
is changed by this correction.
