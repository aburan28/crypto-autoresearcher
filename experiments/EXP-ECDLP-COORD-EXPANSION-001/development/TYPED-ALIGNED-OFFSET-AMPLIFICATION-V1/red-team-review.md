# Independent Red-Team Review: Typed Aligned Offset Amplification V1

## Handoff: common-offset coverage claim

### Claim or task

Check whether multiple aligned offsets improve target coverage after charging
the full target-specialization and query costs, and whether that improvement
has been mistaken for relation independence.

### Status

`REVISE`, with a scoped `OBSERVATION` and no promotion evidence.

### Evidence so far

- The full 12-row, 144-cell sweep passes witness replay and equation checks.
- The exact diagonal record bound holds for every offset.
- 108/144 cells meet the provisional 80%-of-control coverage gate.
- No offset reaches full quotient rank.
- The verifier's normalized rerun is byte-for-byte exact after excluding
  runtime fields.

### Main objections

1. The unrelated control materializes all target records, so its work is not
   the same algorithmic organization as the aligned route; the comparison is a
   coverage control, not a security lower bound.
2. The producer and verifier share the aligned implementation. The receipt is
   a deterministic replay and envelope-consistency check, not an independent
   second elliptic implementation.
3. The test offsets are deterministic known-log public controls. Natural public
   keys are not generally supplied as a progression `Q0+tD`.
4. Per-offset ranks cannot be pooled because each common offset has its own
   unknown target log. Summing ranks across offsets would be an invalid claim.
5. Peak retained advice assumes sequential offset processing; cumulative
   transient advice and repeated scans are charged separately, but allocator
   overhead and network/communication cost remain outside the proxy.
6. Three toy group orders and one frozen input seed do not establish scaling.

### Clean counterfactual

Replace the public target progression by unrelated public points while keeping
the same number of offsets and scans. The `k=t-i` identity disappears and the
target-key record count returns to `Theta(K*T*|A|*|R|)`. Thus the observed gain
depends on the aligned public-target structure.

### Strongest valid conclusion

On the frozen toy fixtures, a small set of deterministic common offsets can
move some aligned cohorts into the coverage band of an unrelated-target
control, with exact witnesses and explicit linear-in-offset scan cost. This is
an aligned many-target decomposition observation, not an ECDLP attack or a
one-instance relation improvement.

### Next concrete action

Test a two-dimensional public target lattice with a verifier that separately
reconstructs the target schedule, complement-key record count, and quotient
row independence. Require the candidate to beat the charged aligned baseline
after all second-direction target records and scans are included.

### Artifact paths

- `development/TYPED-ALIGNED-OFFSET-AMPLIFICATION-V1/contract.md`
- `development/TYPED-ALIGNED-OFFSET-AMPLIFICATION-V1/raw-result.json`
- `development/TYPED-ALIGNED-OFFSET-AMPLIFICATION-V1/verification.json`
- `src/typed_aligned_offset_amplification.py`
- `src/verify_typed_aligned_offset_amplification.py`
