# Prospective full prime-field X9 reference evaluation

Recorded before evaluating the remaining prime-field near-prime candidates.
This amendment keeps the candidate generator, two prime SHA-1 mappings, and
published-family profile in `PROTOCOL.md` and `AMENDMENT_1.md` unchanged.

The accessible X9.62 text is a **20 September 1998 working draft**, and
FIPS 186-2 was published on 27 January 2000. Both postdate all fourteen
recovered 1997–1998 timestamps. They are public references, not authenticated
records of the constructors' internal rule. The draft's Annex
A.3.2 leaves `lmax` and `rmin` as choices. The reference setting here is
`lmax = 255`, `r > 2^160`, and `r > 4 sqrt(q)`, plus MOV for degrees 1–20 and
the anomalous exclusion. We report sensitivity to other `lmax` and subgroup
bounds after exact counting; no setting is imputed to the constructors.

For each of the six distinct prime streams, count every earlier seeded curve
that was not already counted in the published-family campaign. Evaluate the
unmasked published-compatible SHA-1 mapping and the bit-cleared strict X9
working-draft mapping **separately**, including where their coefficients
differ. For each valid coefficient, retain both square roots `b`. Reuse an
exact family-campaign point count only when its field and `b` agree. A
missing root or singular curve is a proven no-curve result under that mapping;
even or three-divisible order is *not* a near-prime rejection. Every valid
curve needs an exact point count or an explicit `INDETERMINATE` record.

The X9 reference accepts a branch when its order factors as `h*r`, all prime
factors of `h` are at most 255, `r` is proven prime, the minimum size and
MOV/anomalous checks pass, and a subgroup point exists. The last condition
is checked independently for every earlier survivor using affine scalar
multiplication and the Hasse interval. The published field, fixed `a=-3`,
seed relation, nonsingularity, prime field, and basis are also checked.
Before launch, four representative evaluator controls must match the existing
P-192 count and Sage's separate cardinality path; their immutable result is
`raw/x9_evaluator_controls.json`, bound by the campaign plan.

A named target's candidate is an earlier public-rule-eligible *seed* if at
least one admissible root passes. Report root-level counts and whether the
published root rule would also pass. Shared streams are counted once and
projected to each named index after exact seed and anchor validation.

Run with no more than eight workers, PARI stack 512 MiB or 1024 MiB for
P-521, and a two-hour per-shard process watchdog. These guard the machine
and do not truncate the scientific target. Frozen shards, stdout/stderr,
errors and partials remain as generated. Any stopped row stays unknown until
an immutable retry completes it.

Complete arithmetic enumeration still cannot recover the original timestamp
choice, candidate order across abandoned starts, private `lmax` or `rmin`,
other unpublished filters, or motive. An X9-reference survivor is a
mathematically admissible alternative under the stated reference, not proof
that it was an option the historical constructor considered.
