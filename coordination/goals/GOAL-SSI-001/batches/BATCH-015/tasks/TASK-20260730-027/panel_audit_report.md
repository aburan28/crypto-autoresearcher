# BATCH-015 typed-tape panel audit: specification failure

Task `TASK-20260730-027` audited the two preregistered rows from commit
`4460a82c3948fa83240673f907612a44a1bd1cb5`, using the literal types and
recursive return rule of `ttm-v1`.  This is not a curve, isogeny, or
quantum-circuit computation.

## Result

The frozen transition specification cannot reach its designated internal
`S=2` collimation in either row.  Consequently, neither a projected `S=2`
pair set nor an occupancy/reachability/recurrence result is computable under
the specified machine.  This is a `specification_error`, not negative
mathematical evidence.

The obstruction is at the first return from the base frame.  The base rule
returns a vector reduced modulo `n`, while the restored parent state requires
each child-store vector to be over `Z/s_r Z`.  At the first internal parent,
`s_r=2`, but the base frame has `s_d=n`:

| Row | Base-return type | Required parent child-store type | Result |
|---|---|---|---|
| `[1,2,4]` | `Z/4Z` | `Z/2Z` | invalid typed return |
| `[1,2,5,8]` | `Z/8Z` | `Z/5Z` | invalid typed return |

`ttm-v1` specifies neither a coercion/reduction at return nor a parent
acceptance rule for a vector in a distinct modulus.  Adding either would
change the preregistered transition machine.  Its rule permitting only
label-matched returns does not supply the missing value-type transition.

The machine also fixes the base draw count to `round(log2 L)` for the row,
but it does not include the requested-length parameter used by the BATCH-014
static analyzer.  Therefore importing that analyzer's length-dependent
construction would be an unregistered semantic amendment, not an execution
of `ttm-v1`.

## Per-row typed transition audit

For each row the explorer enters root, spawns the first internal child, then
spawns that child's base child.  The base child consumes exactly two valid
`BaseDraw` symbols (because `L=4`) and produces a sorted vector modulo `n`.
The labeled return is rejected by the parent-frame value type shown above.
No `LeftIndex` or `RightIndex` is enabled, no `decide` state is reached, and
no retry successor exists.  These invalid return attempts are retained as
unavailable transitions; they are not converted into a reduction or a
different transition.

Thus, for both rows:

- projected `S=2` pair set: not computable;
- zero-progress occupancy: not computable;
- `jointly_reachable`: not computable;
- `recurrent` through one retry: not computable;
- minimum keep probability: not computed.

## Analyzer source

The following standard-library check is the complete executed typed boundary
analyzer.  It explicitly consumes the base tape symbols, constructs the
source-compatible subset sums for the frozen fixed `L=4` draw count, and
permits a return only when the produced modulus equals the active parent
child-store modulus.  It reports the two exact blocked transitions above.

```python
from itertools import product

ROWS = (
    ("CSIDH-CS-6f9188e4-logn2-logl2-logs0-theta3over4", (1, 2, 4), 4),
    ("CSIDH-CS-6f9188e4-logn3-logl2-logs0-theta3over4", (1, 2, 5, 8), 4),
)

def base_returns(n, L):
    draws = round(L.bit_length() - 1)  # round(log2(4)) = 2
    assert draws == 2
    # Every sequence of two valid BaseDraw symbols is consumed once.
    for tape in product(range(n), repeat=draws):
        vector = tuple(sorted(
            sum(((mask >> bit) & 1) * tape[bit] for bit in range(draws)) % n
            for mask in range(1 << draws)
        ))
        yield tape, vector

for schedule_id, ss, L in ROWS:
    parent_modulus, endpoint = ss[-2], ss[-1]
    invalid = 0
    for tape, vector in base_returns(endpoint, L):
        # This is the typed return transition required before child_store=(v1).
        if endpoint != parent_modulus:
            invalid += 1
            continue
        raise AssertionError("unexpectedly type-compatible panel row")
    print(schedule_id, invalid, endpoint, parent_modulus)
```

The output is deterministically:

```text
CSIDH-CS-6f9188e4-logn2-logl2-logs0-theta3over4 16 4 2
CSIDH-CS-6f9188e4-logn3-logl2-logs0-theta3over4 64 8 5
```

These counts are invalid typed base-return attempts, not pair counts,
probabilities, or empirical observations about the implementation.

## BATCH-014 comparison and wording qualification

BATCH-014 reported 176 static pre-collimation pairs for `[1,2,4]` and an
empty zero-progress class under its own definition, where every q-bin must
be below the threshold.  That analyzer was static pair-set enumeration; it
was not an explicit `ttm-v1` typed-tape/history transition machine.

No equality or disagreement with the 176-pair result can be asserted here:
the frozen machine blocks before a pair can be formed, and its syntactic
zero-progress definition is an individual threshold-rejected `decide` state,
not BATCH-014's all-q-bins predicate.  DEC-20260730-013 already requires
that the BATCH-014 pin order be described as self-attested rather than
independently durable, and that its analyzer be described as static
enumeration.  This audit confirms those qualifications remain necessary; it
does not replace the BATCH-014 result.

## Boundary

This report neither infers a global stopping tail nor changes C2, C3, the
error map, or query-memory semantics.  It performs no recovery or
object-lifetime work and makes no numeric-security, breakthrough, or
goal-completion claim.  A Coordinator-approved successor specification would
need to define the return-modulus coercion and requested-length semantics
before a panel reachability audit can be run.
