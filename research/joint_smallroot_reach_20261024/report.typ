#set page(paper: "a4", margin: 19mm)
#set text(size: 10pt)
#set heading(numbering: "1.")
= Joint small-root finite accounting audit
Software diagnostics, 2026-10-24. No ECDLP experiment or IC speedup is claimed.

== Objective and status
Establish the reach-cost tradeoff of joint-system small-root decomposition and
demonstrate a verified improvement over the prime-field IC baseline. This goal
remains incomplete. The delivered work is a finite accounting prerequisite.

== Exact accounting
For N triangular rows with modulus exponent sum q, each evaluating to a multiple
of p to the power t, the determinant-level available budget is t N minus q.
Column scaling consumes the sum of each coordinate exponent times its bound
exponent. LLL approximation and evaluation-norm factors further reduce the
finite budget. Independent short polynomials and root extraction remain separate.

The t=1 single S3 fixture has 13 rows, q=12 and coordinate sums (11,11,11).
Its determinant is exactly 101 to the power 12 times 2 to the power 33. The
available modulus exponent is 1. The historical calculator instead uses 12.
The univariate large-multiplicity calibration cannot expose this difference.

== Finite joint construction
The three equations are S3(x1,x2,u), S3(x3,x4,v), S3(u,v,xQ), with xQ fixed.
Products of all three inputs are used. The finite column set and distinct monic
pivots are checked. No globally optimal shift construction is asserted.

#image("reach-cost.svg", width: 100%)

Exact diagnostic counts: one construction per plotted cell; no random sample or
statistical interval. Joint t=1,2,3 dimensions are 31,382,2591 and normalized
equal-bound determinant statistics are 3/41,98/1039,640/5417. Dense entry counts
are structural proxies, not actual memory or total solver time. Large matrices
were counted, not reduced. Single and joint normalization differ.

== Checks and remaining obligations
23 software tests pass, including independently expanded S3 coefficients, exact
single/joint determinants, finite direct counts and toy root divisibility.
The ten historical tests remain unchanged. Details, exact argv, source hashes,
dependency versions, logs and rational values are in report.md and artifacts/.

No optimized external shifts, higher-rank GAP substitution, root extraction,
random-target relation yield/rank, or full IC comparison has been completed.
The earlier 0.8408 versus 8/9 argument requires reconciliation; the diagnostic
does not establish that the lead is impossible. Independent review task
TASK-20261024-da3810 is prepared but unexecuted. No independent attestation exists.

Automatic approval review rejected publication of the branch. Work is committed
locally; no PR is claimed. External artifact retrieval also encountered HTTP 403.
Those are operational limits, not mathematical conclusions. The next step is
publication authorization, independent budget review and an applicable executable
optimized joint construction. See the linked named problem in report.md.
