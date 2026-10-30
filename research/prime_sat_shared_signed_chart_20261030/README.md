# Complete signed interval charts: fixed software construction

This implements TASK-20261030-c64c9e. It constructs a chart from a **supplied signed relation**, and recovers/checks its points from **supplied quotient idempotents**. It does not search for unknown relations or invoke SAT.

Public representations are explicit: curve `{p,a,b}`, interval `{t,s}`, affine point `[x,y]`, identity `None`, and quotient modulus `U={p,coeffs}` with increasing coefficient order and no trailing zeros. Prime p is a mathematical input premise, not a claimed primality certificate. The factor certificate `{p,t,s,factors}` carries sorted distinct `[x,positive_integer_multiplicity]` pairs. It binds the interval needed by signed recovery. Canonical field integers exclude booleans. The supplied affine points omit identity padding; returned multisets are sorted affine points followed by exactly 5-k identities.

1. `charts.construct_from_signed_multiset(curve, interval, points, target)` checks the supplied relation, interpolates the unique normalized chart by local Hasse coefficients, and constructs bit idempotents by CRT from known residual coordinates.
2. `projectors.recover_interval_factors(U,t,s,e)` splits multiplication projectors, using integer dimensions and verifying the linear-factor product independently. There is no coordinate scan or generic factorization.
3. `signed_recovery.recover_signed_divisor(curve,target,A,B,U,factors,root_lifts)` uses common-factor valuations, ratio ordinates, separate two-torsion handling and exact signed target subtraction. Balanced square roots must be supplied (or already given by the target); every supplied point/root is checked. No square-root search is hidden.
4. Add the factor certificate to the witness as `witness['factors']`, then call `check_chart.check_chart(witness,recovered)`. The checker recomputes local orders with its own bounded formal-series implementation, not the recovery valuation formula. Returns `valid`, `invalid` or `error`, with the failed obligation. Shared elementary polynomial arithmetic remains a common dependency for independent review.

The full nilpotent quotient rationality condition is retained. The separate gcd-support research derivation is not implemented here. All k=0..5 charts and the nonexistent pole-one cases are explicit. Interval length must be strictly less than p; wrapping is allowed.

Run only the prospectively admitted fixed suite:

```
python -B research/prime_sat_shared_signed_chart_20261030/test_charts.py --output research/prime_sat_shared_signed_chart_20261030/software-results.json
```

The fixed contract is `coordination/prime_sat_shared_signed_chart_20261030/fixed-software-contract.json`: fifteen chart fixtures, eight projector fixtures and the prescribed mutations; at most four attempts, 240 seconds each. No fixture search, random trials, curve census, SAT calls, timing comparison or remote jobs. Every attempt stores its exact source text/hashes and failures. `quotient.EVENTS` contains named algorithm-call counts only, never an aggregate field-operation count or measured speed; local-series, interpolation, CRT, witness checking, recovery and group checks are included as separate events. Serialization and input sizes are recorded by the suite. Field bit costs, square-root construction, search and output expansion are not estimated by these counters.

No completed test or independent-review result is asserted in this README. Consult the actual result file and later independent reviewer artifacts. Universal chart correspondence, supplied-witness cost bounds and any degree or speed claim require their own scoped review.
