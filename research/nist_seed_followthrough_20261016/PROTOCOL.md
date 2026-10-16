# NIST seed follow-through: frozen scope and inference rules

Date: 2026-10-16. This follow-up uses the candidate generator and target
definitions frozen in `../nist_seed_selection_20261016/PROTOCOL.md` and its
amendments. Earlier raw records are inputs; they are never overwritten.

## A. Complete public-reference count

For each distinct prime-field stream through its last published block, inspect
every candidate that yields a nonsingular seeded coefficient under each of
the two recorded SHA-1 mappings: published-compatible unmasked FIPS and the
bit-cleared September 1998 X9 working-draft variant. Count both coefficient
roots, with a twist-order identity allowed only for fields congruent to 3
modulo 4; for P-224 the two signs are isomorphic. Reuse an earlier exact order
only after field, coefficient, seed, and source digest agree. Otherwise use
PARI `ellcard` for an exact count. Each failed or timed-out count is an
`INDETERMINATE` row with a retained command and log, never a rejected curve.

The reference acceptance test is the September 1998 draft's near-prime
criterion at declared `lmax=255`, `r>2^160`, `r>4 sqrt(q)`, MOV degrees 1
through 20, and nonanomalous order. The order is divided by *all* primes at
most 255; the remaining factor must be proven prime. Record the smooth
cofactor and subgroup order for every accepted root. Present sensitivity for
`lmax` in 7, 15, 31, 63, 127, 255 and subgroup lower bounds 2^160, 2^180,
2^200, holding the `4 sqrt(q)` and MOV-20 conditions. A candidate is counted
once per mapping and seed if either root qualifies. Project shared streams
onto named targets without treating them as independent generator runs.

Retain a source-bound machine-readable row per evaluated coefficient, all
subprocess outputs, version and host information, and a separate summary.
Independently check every accepted root with a subgroup point and Hasse
uniqueness where applicable. Published anchors are positive controls; the
known 11 selected-root skips and the completed P-192/binary reference counts
are comparison controls. The historical private `lmax`, `rmin`, root choice,
timestamp restarts and stopping rule remain unknown even if this count ends.

One counting worker and a 512 MiB PARI stack are the initial machine guards;
P-521 may use 1024 MiB. Raise concurrency only after checking headroom. A
per-candidate watchdog of 600 seconds prevents a stalled point count from
holding the machine; such rows remain unknown and are retried with an explicit
superseding record. There is no research sample cap: all valid candidates in
the six distinct streams are the target.

## B. Remaining selection choices

Recompute the reachable-state ceiling for the exact 20-consecutive-draw recipe
and count timestamp starts under explicitly declared date intervals. Separate
the number of *reachable states* from attempted starts, candidate slots and
historical runs. Check the four unexplained prime-field base points against a
small, declared set of deterministic rules only: first valid nonnegative
`x`, SHA-1 of `seed || counter` and `counter || seed` interpreted modulo `p`,
and the corresponding SHA-256 forms, for counters 0 through 65535. The
counter is four-byte big-endian. Also test a declared long-output variant:
concatenate `SHA-1(seed || counter || j)` (or SHA-256) for consecutive
four-byte big-endian `j` starting at zero until at least the field bit length
is available, then interpret the concatenation modulo `p`; test the mirrored
`counter || seed || j` form. Retain the
first matching counter or a bounded no-match record, together with all four
published point controls and a synthetic positive for every rule. The rules
are modern diagnostics; a match without historical source is not attribution.

## C. Mechanism-specific comparative screens

Compare the ten published prime curves with all 59 earlier cofactor-one
alternatives in the six distinct streams. A candidate is one seed with at least
one eligible coefficient root; branch-level results remain separate. Test a
specific possible transfer route: an Fp-rational isogeny into a curve with
CM field discriminant in `{-3,-4,-7,-8,-11,-19,-43,-67,-163}`. Its necessary
condition is that the certified Frobenius discriminant `t^2-4p` equal `D*f^2`
for some integer `f`; decide this exactly by divisibility and integer square
root. A failure rules out only these nine CM fields as destinations of an
Fp-rational isogeny. It says nothing about high-degree routes to other CM
fields or hidden algorithms on ordinary curves.

Independently recompute the ordinary order, anomalous and MOV-20 predicates
for every eligible root using the frozen exact order. For a separate
implementation threat model, trial-divide the quadratic-twist order by every
prime at most 10,000 and record the product of fully extracted small-prime
powers. This is an exact small-factor diagnostic, not a complete factorization
or an exploitation cost. A potential invalid-curve route
requires a specified implementation that accepts off-curve points and exposes
an informative oracle; absent that implementation the twist screen is a
conditional diagnostic only. A small-CM or isogeny route requires an explicit
map, subgroup preservation, destination solver and complete costs. Do not
promote a structural difference into an ECDLP advantage. Record a mechanism
table with prerequisites, evidence, counterexamples and unresolved work.

If any count or screen conflicts with a frozen control, stop the dependent
conclusion and retain both records. Positive findings need independent replay
before any claim change. This study changes no official hypothesis status.
