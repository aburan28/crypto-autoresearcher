# Prime-order certificate effort as a possible 1997 selection filter

Frozen 2026-10-23 UTC before factoring the 19 matched curves' order neighbors.
This is a retrospective workflow proxy, not a reconstruction of original code,
an ECDLP attack, or evidence that a correct primality test rejects a prime.

## Exact input and question

Read the eleven omitted seed-level classes from
`research/nist_seed_skipped_curves_20261016/assessed.json` (SHA-256
`370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`)
and eight published controls over the same four prime fields from
`traits.json` (SHA-256
`a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`).
Exclude the P-384 and P-521 singletons. The source orders `n` are pinned
prime-order certificates from the earlier reconstruction. Never substitute a
curve with only the same bit length; bind every result to its EC1 UID, seed
ordinal, field prime, and group order.

Question: if a 1997 workflow sought *deterministic* Pocklington-style
primality certificates for group orders, does the factor structure of `n-1`
separate omitted from published curves? Factor `n+1` as an arithmetic negative
control, not as part of Pocklington's theorem. For each integer, run GP/PARI
complete factorization with a 180-second per-case watchdog, 1 GiB GP stack,
sampled 2 GiB RSS watchdog, and serial execution. Retain every input,
stdout, stderr, exit and resource receipt, including censored cases. New run
directories are write-once. Run three exact controls: `15=3*5`, `60=2^2*3*5`,
and `101` prime. Inject exception and early-return launcher failures; each
must exit nonzero without a completion marker. Sage separately checks raw
factor products and every factor with `is_prime(proof=True)`; Sage and GP may
share arithmetic internals, so this is a separate output check rather than an
independent factorization.

## Fixed metrics and comparison

For `n-1` and `n+1`, record the product `F_B` of all proven prime powers at or
below each fixed bound `B = 1,000; 10,000; 100,000; 1,000,000`, the bit length
of `F_B`, and whether `F_B^2 > n`. When complete factors exist, record the
minimum number of prime-power components, taking largest first, whose product
exceeds `sqrt(n)`, and the largest factor required at that crossing. These are
proxy measures of Pocklington certificate effort; recursive factor
certification and witnesses are outside this test. For every feature, compare
the within-field labels and report any counterexample to an exact separating
threshold. No post hoc choice of `B` or feature is promoted as a historical
rule. A complete result requires all 38 real factorizations and three
controls to verify; otherwise report exact censored scope.

Interpretation: if published orders are consistently easier under one fixed
metric, that is a lead to investigate actual 1997 software, not proof it was
used. If a published control is as hard or harder than an omission, the
corresponding universal monotone proof-ease rule fails for these 19. A correct
probable-prime test does not need `n-1` factors and does not label a true prime
composite; this protocol cannot test implementation defects, timeouts, or
manual review. Retain a dated report, editable graph, vector comparison and
visually inspected PDF, whether results are positive, negative or censored.
