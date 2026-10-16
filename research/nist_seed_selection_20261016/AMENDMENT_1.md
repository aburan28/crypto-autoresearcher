# Prospective cofactor-one screening amendment

Recorded before the full prime-stream family-profile campaign, 2026-10-16.
The original `PROTOCOL.md` and its candidate-generation results stay fixed.
This amendment changes only the cost of rejecting prime-field candidates for
the **published cofactor-one family profile**. It does not claim to complete
the broader X9.62 near-prime screen on candidates rejected here.

## Exact rejection lemmas

For each nonsingular `y^2 = x^3 - 3x + b` over the published prime field:

1. If `x^3 - 3x + b` has a root in the field, the curve has a rational point
   of order two. Its group order is even and cannot be the published profile's
   prime group order.
2. If the 3-division polynomial has a field root whose curve right-hand side
   is a square, the curve has a rational point of order three. Its group
   order is divisible by three and cannot be the published profile's prime
   group order.
3. If neither screen decides a branch, count one root using PARI `ellcard`.
   The other root's order is `2(p+1)-N` for `p = 3 mod 4`; for `p = 1 mod 4`
   the roots are isomorphic and have equal order. Apply prime-order,
   subgroup-size, MOV-20, and anomalous checks to both. Keep any PARI error,
   watchdog expiration, or missing row `INDETERMINATE`.

The screening records are `raw/prime_2torsion_screen.jsonl` and
`raw/prime_3torsion_screen.jsonl`. The prior P-192 full count and P-256 index
876 are controls. All ten published prime orders have separate independent
affine-scalar/Hasse certificates. Every screen and exact-count shard binds the
candidate-file SHA-256. Shared same-field/same-timestamp streams are counted
once at their longest index and projected to each named target only after
checking published anchors at their own indices.

## Work and inference limits

Six representative prime streams: `prime192v2`, `prime239v3`, `P-224`,
`P-256`, `P-384`, `P-521`. The campaign plan is fixed in
`raw/family_campaign/plan.json` before launch. No more than eight count workers
run simultaneously. PARI stack is 512 MiB except P-521 at 1024 MiB; each
shard has a two-hour watchdog to protect the machine. These are operational
guards, not a scientific search or spending cap. A stopped shard is retained
and rescheduled under a new immutable record; its unprocessed candidates
remain unknown. Candidate indices, SHA mapping, roots, fields, acceptance
checks, and anchor controls remain as in `PROTOCOL.md`.

This amendment can establish a complete published-profile decision for a
prime stream when every index has a proved rejection or exact count. It
cannot establish that all private historical criteria were known, nor classify
the X9.62 near-prime status of torsion-rejected curves without an exact count.
