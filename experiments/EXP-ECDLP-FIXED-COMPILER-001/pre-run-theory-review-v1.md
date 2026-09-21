# Pre-run theory review v1

## Handoff: reject raw ordered-tuple sizing

### Claim or task

Audit whether the first fixed-compiler sizing rule gives a meaningful five-term decomposition probability for a sign-complete factor base.

### Status

NEGATIVE RESULT

### Assumptions

- `TOY-EVIDENCE`: the diagnostic sweep used one clean curve at each of 8, 9, and 10 bits.
- `MODEL-BOUND`: only the sizing rule and formal sign symmetry are under review; no family-wide or asymptotic claim is made.

### Evidence so far

- Development v1 chose the smallest even `B` satisfying `B^5 >= q`.
- This selected `B=4` on groups of orders `257`, `509`, and `937`.
- Every generic `B=4` sign-complete family had exactly 36 five-term group values on those instances, not approximately `B^5` independently distributed values.
- Exact one-query success therefore fell from `36/257` to `36/937` as the group grew.
- The cause is structural: ordered tuples count permutations, and a sign-complete base identifies many tuples through cancellation before any curve-specific collision occurs.

### Failure modes

- A shrinking success probability creates artificial descent failures and can make relation-target counts look like a family effect.
- Comparing coordinate and random families at a mis-sized base answers the wrong point-decomposition question.
- Treating `B^5/q` as a finite support model repeats the unordered-occupancy error already isolated in the recursive-expansion lane.

### Next concrete action

Replace the v1 rule with the exact signed formal-class count at occupancy `0.5`, rerun the three-size development sweep, and preserve `B^5/q` only as an asymptotic sizing heuristic.

### Artifact paths

- `/tmp/fixed-compiler-sweep-8-10.json` (ephemeral development output; independently verified, not canonical evidence)
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/contract.md`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/src/fixed_curve_compiler.py`
