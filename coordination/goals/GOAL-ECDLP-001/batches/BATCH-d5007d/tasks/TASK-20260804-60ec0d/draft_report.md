# Draft report — TASK-20260804-60ec0d

`EXP-SMTH-afd6f7` is a new `review_required` design draft responding to the
independent `REVISE` review of `EXP-SMTH-92d322`. It is unfrozen,
execution-unauthorized, and evidence-ineligible. This report describes
declared pre-run rules only; it reports no implementation, run, output, or
mathematical conclusion.

## Gap resolutions

1. **GAP-1 — deterministic curve and factor base.** The draft specifies a
   SHA-256 domain-separated seed encoding; an odd, bounded prime candidate
   stream with deterministic trial-division primality testing; a bounded
   `(a,b)` candidate stream; non-singularity and exact point-count ordinary
   tests; ordered rejection rules; and terminal construction failure. It then
   scans x values in increasing order, retains exactly those with an affine
   point, takes the first 512 distinct values, and commits the canonical list
   digest. It forbids wrapping, reseeding, fallback curves, and duplicate
   substitution.

2. **GAP-2 — `S_3`, root multiset, `INT-1`, and `ENC-B`.** The draft states
   the three coefficients of `S_3(x_i,x_j,Z)`, defines the algebraic-closure
   root multiset and computes its elementary symmetric invariant through
   Vieta, not an unnamed root routine. It fixes canonical field lifts and the
   exact encoding `N=E1*p+E2+1`. Repeated and nonsplit roots use the same
   coefficient-derived invariant; zero leading coefficient, inverse failure,
   noncanonical lifts, and range failure have explicit invalid-measurement
   dispositions.

3. **GAP-3 — complete factorization and verification.** The draft declares
   the solver identity, version, call configuration, single-worker model,
   watchdog, and no-retry/no-resume behavior. It gives a line-oriented,
   canonical raw schema for both arms and requires a separate prime-check and
   exact product reconstruction path that does not invoke or trust
   `factorint`'s completeness flag. Incomplete or failed records are retained
   and halt the package rather than being silently accepted or dropped.

4. **GAP-4 — RSS probes.** The draft names `/proc/self/status:VmRSS` from the
   single worker as the source, records probes at ordinals 6,541, 13,082, and
   26,164, supplies a linear forecast, a 5% numerical uncertainty margin, and
   numerical 75% current-RSS / 80% forecast-cap requirements. A missing,
   failed, or missed probe halts at the record boundary as infrastructure or
   budget signal, not mathematical evidence.

5. **GAP-5 — domain comparability.** The draft forbids every comparison with
   predecessor streams or outputs merely because a numerical seed is shared.
   It allows such a comparison only under a separately registered comparator
   contract that declares the domains, artifacts, statistic, expected
   relation, and failure interpretation.

## Scope and requested next authorization

The draft retains strict `i < j` enumeration, an exact-support measured null,
and a toy-only ceiling. It cannot support or reject any ECDLP attack claim,
cost claim, exponent claim, crypto-scale claim, or deployed-scheme claim; one
future run cannot change that limit.

Please authorize only the next review/freeze stage if you wish to proceed.
Execution is not requested and remains prohibited unless you separately
authorize it after an approved, frozen, and archived contract is presented.
