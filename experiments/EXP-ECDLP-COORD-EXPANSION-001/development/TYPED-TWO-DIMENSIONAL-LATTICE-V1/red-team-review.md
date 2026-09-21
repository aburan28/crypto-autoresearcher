# Independent Red-Team Review: Typed Two-Dimensional Target Lattice V1

## Handoff: second-direction rank signal

### Claim or task

Audit whether the second target direction genuinely improves relation rank
without silently restoring the full unrelated-target materialization cost.

### Status

`REVISE`, with a scoped rank trend and a `NEGATIVE RESULT` for this exact
materialized lattice organization.

### Evidence so far

- 120 cells pass deterministic replay and exact-record consistency.
- The key record identity is exact for every tested `U,V` pair.
- Median rank deficit drops from 8 at `V=1` to 1 at `V=16`.
- Full-rank cells remain `0/120`.
- Coverage reaches the unrelated-target control band in most `V>=4` cells.

### Main objections

1. `V=1` has an unused second-direction coefficient, so its rank is a sanity
   control rather than a fair two-dimensional relation test.
2. The public `E` direction is a deterministic known-log test point. Its use
   is allowed as a public group element, but no deployment conclusion follows
   from the frozen generator-derived fixture.
3. The verifier imports the producer and reruns it. It is a strong deterministic
   envelope check but not a second elliptic implementation.
4. The key record reduction is real only for public lattice-aligned targets;
   unrelated public keys erase the `u-i` identity.
5. The near-full rank at `V=16` may be a finite-size occupancy effect. Larger
   `V` could eventually fill the row space, but the measured state and scan
   grow linearly in `V`.
6. The current cost proxy counts group operations and deep payload bytes, not
   full allocator traffic, distributed bandwidth, or a completed target
   descent.

### Clean counterfactual

Replace `Q_{u,v}` by unrelated targets while keeping `U*V` fixed. The key
record count becomes `U*V*|A|*|R|`, removing the diagonal reduction. Conversely,
pooling equations across distinct `Q0` or `E` offsets without introducing
their unknown logs would artificially inflate rank.

### Strongest valid conclusion

On the frozen toy fixtures, a second public target direction produces a
measurable rank trend and control-level coverage, but the exact materialized
lattice fails the full-rank gate through `V=16` while its target-side state
grows linearly in `V`. This is not a generic ECDLP improvement.

### Next concrete action

Implement a nonlinear/quotient slice operator that answers the `v`-indexed
complement queries without storing one full key block per `v`. Require an
independent row reconstruction and compare its charged state against the
materialized lattice baseline.

### Artifact paths

- `development/TYPED-TWO-DIMENSIONAL-LATTICE-V1/contract.md`
- `development/TYPED-TWO-DIMENSIONAL-LATTICE-V1/raw-result.json`
- `development/TYPED-TWO-DIMENSIONAL-LATTICE-V1/verification.json`
- `src/typed_two_dimensional_lattice.py`
- `src/verify_typed_two_dimensional_lattice.py`
