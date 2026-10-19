# Continuation of the interrupted prime-family campaign

Recorded before any retry of an interrupted shard. The candidate source,
coefficient mappings, acceptance predicates, torsion screen, and exact point
counting executable in the original [plan](raw/family_campaign/plan.json) do
not change. The original complete shards, partial files, and logs remain
immutable. A retry processes only indices that have no retained result.

`plan_family_retry.py` validates the original plan and every present shard,
then freezes their hashes and a disjoint covering of the unfinished indices
in `raw/family_campaign/retry_plan.json`. The source prefix of a partial shard
is usable only when its header matches the original frozen inputs and every
row has the expected target, seed, consecutive index, and determinate status.
The retry uses the same evaluator and a 7,200 second process watchdog. Shards
are smaller to limit the loss from an interruption: widths of 10 for P-521,
25 for P-384, 100 for P-256, 150 for prime239v3, and 250 for P-224 and
prime192v2. At most one point-count process runs at a time while the host is
heavily loaded. This is a resource safeguard, not a scientific stopping rule.

The final summary must independently verify the hash and coverage of every
original complete shard, retained prefix, and retry shard. It must reject
duplicate, missing, or indeterminate indices. It must keep published anchors
and reused generator streams distinct when projecting results to named curves.
If another retry is interrupted, preserve its partial file and record a new
continuation rather than overwriting or silently dropping rows.

This continuation changes execution only. The still unknown historical
`lmax`, `rmin`, root-selection rule, stopping rule, and any private filters
remain unknown after a complete public-reference enumeration.
