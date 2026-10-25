# Admission corrections and remaining branch control

24 October 2026 UTC, before the CM-only and certificate-checker calls.

The first small-control launcher correctly ran primes 101/65537 and composite 15, but its parser did not recognize the percent-prefixed fast-precheck message for 15. Those native outputs are retained and reused. The corrected launcher runs only the remaining 341 and induced empty/missing-catalog cases; it does not repeat the first three.

The two normal primes took N−1 proofs, leaving the elliptic-curve proving/checking path unexercised. Add one correctness control: known prime 101, original complete data, N−1/N+1 routes disabled, proof enabled. This is a branch-admission check, not a new candidate-selection trial or a configuration fitted to the eleven curves.

For the separately compiled unchanged legacy checker, retain its verdict for both bundled C-format certificate fixtures, the newly generated 101/65537 certificates and the CM-only 101 certificate. Add three negative files: empty bytes, a deliberately truncated 101 certificate and the 101 certificate with its root integer changed to 105. Fix these files before checker execution. A positive requires exit zero, at least one per-step verdict, every verdict one and no error marker. Negative inputs must fail that admission predicate. Bound each checker call at 15 seconds; retain and remove only its named container on watchdog expiry. Empty or incomplete output cannot pass. A small-case/certificate success does not establish behavior of any named NIST/ANSI order.
