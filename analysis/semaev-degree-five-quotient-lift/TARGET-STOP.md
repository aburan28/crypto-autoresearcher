# Optional stopping when this producer cannot reach its target

`quotient_lift_target.cpp` is a separate candidate derived from the portable-qualified block rewrite. It adds an optional final CLI argument, `target_codimension_exclusive`. Without that argument, the producer retains its previous behavior. No active scientific worker uses this candidate.

Let `work` be the fixed dimension of the provisional coordinate space and let `r` be the rank of the accumulated relation rows. The construction subsequently appends rows to this relation span. Its rank cannot decrease, so the eventual quotient produced by this particular construction has dimension at most `work - r`. If that ceiling is at most a requested target `s`, completing this construction cannot produce a certificate with codimension strictly greater than `s`.

This is a statement about the construction, not an upper bound on the codimension of the true degree-bounded closure. It remains valid as a reason to abandon this candidate even if the partial construction is not yet closed. A different construction could still yield a stronger certificate.

For a future degree-six search, `s` can be the independently obtained exact solution count. The strict certificate inequality then cannot be met once `work - r <= s`. A future driver must bind that count to the same input and preserve prior accepted stages. This option cannot establish an LFD bound, prove an upper bound, or establish membership in the true closure.

The diagnostic is `target_codimension_unreachable`, with the working dimension, partial relation rank, constructed-dimension ceiling, and requested target. It writes no new certificate. The existing `projection_kills_one` diagnostic takes precedence. The test is made after relation batches in both the seed-relation and closure loops. No incomplete map is exported as a certificate.

## Software controls

`test_target_stop.py` uses retained Semaev fixtures whose outputs were previously accepted by the original independent checker. Across three lifts it checks an omitted target, a target one below the final codimension, equality, and a target one above it. Omitted/below-target runs export byte-identical certificates; equality/above-target runs emit the diagnostic without a certificate. Four malformed target arguments are refused, including negative, empty, nonnumeric, and overflowing values.

All 12 boundary cases and four argument-rejection cases passed. Fixture, source, binary, compiler and library identities and the raw outputs are retained in `validation/target-stop-20261029/`. The binary uses baseline x86-64 flags and the SIMD-disabled static M4RI library. These tests establish local software behavior, not a measured speed advantage or frontier result.

Scientific deployment still requires a separately frozen instrument/protocol and driver handling of the new diagnostic. The active high-memory driver, binaries, fixed input order and prior attempts are unchanged.
