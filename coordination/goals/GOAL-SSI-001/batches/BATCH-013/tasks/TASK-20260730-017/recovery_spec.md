# End-to-end recovery and common-error specification

This is a required **specification**, written separately from the bounded
analyzer. It is not claimed to be implemented by
`CollimationSieve@6f9188e4`, whose extracted behavior ends in a statistics
report rather than recovered-key verification.

## State and final event

Let `x` be the public instance, `k` the hidden target, and `Verify(x,k')` a
total deterministic predicate. A completed candidate is successful exactly
when `Verify(x,k') = true`. Define one common operational failure event:

\[
 F=\{\text{the procedure fails to return a }k'\text{ with Verify}(x,k')=true
 \text{ within its declared stopping policy}\}.
\]

All exits are typed either `success` (a true verification result) or a named
failure constituent of `F`. A report-only completion, an unverified candidate,
and an exhausted residual search are all failures, not successes.

## Required stages and object schedule

1. **Initialize.** Parse and validate `x`; derive a declared attempt
   schedule. Birth `B_input` (classical immutable input/backing) and
   `B_attempt` (classical attempt metadata). Their deaths occur after the
   final verification record is retained. Parse/parameter failure maps to
   `F_input subseteq F`.
2. **Oracle/label preparation.** Birth coherent workspace `W_label` and
   QRACM object `R_label` with declared logical widths and address semantics.
   `W_label` and `R_label` may coexist with `B_input` and `B_attempt`.
   Oracle/label approximation or implementation failure maps to
   `F_oracle subseteq F`. On an accepted handoff, explicitly uncompute and
   verify cleanup of `W_label`; destroy `R_label` only after its last declared
   query.
3. **Sieve attempt.** Birth `W_sieve`, `R_sieve`, and classical backing
   `B_sieve` before each local transition. During a collimation operation,
   `W_sieve`, `R_sieve`, `B_sieve`, and the current attempt metadata may be
   concurrent. A retry must destroy or reset all attempt-local `W_sieve` and
   `R_sieve` state and release its `B_sieve` allocation before the next
   attempt; cleanup failure maps to `F_cleanup subseteq F`. A stopping-policy
   breach maps to `F_stop subseteq F`.
4. **Classical postprocessing/recovery.** After an accepted sieve output,
   destroy `W_sieve` and `R_sieve` only after their final specified use, then
   birth `B_post` and `B_recovery` for candidate reconstruction. They may
   coexist with `B_input`, `B_attempt`, and the retained accepted sieve
   transcript. Algebraic/reconstruction error maps to `F_recovery subseteq F`.
5. **Residual tail.** Birth `M_tail` only after the recovery transition and
   declare its width, enumeration order, stopping rule, and whether it shares
   `B_recovery`. `M_tail`, `B_recovery`, and the candidate record may be
   concurrent; no `W_*` or `R_*` object may be counted as dead merely because
   source variables are unused. Tail exhaustion, timeout, or an omitted
   residual branch maps to `F_tail subseteq F`.
6. **Verification event.** Birth a candidate buffer `B_candidate` and run the
   single predicate `Verify(x,k')`. Verification computation may coexist with
   `B_input`, `B_recovery`, `M_tail`, and `B_candidate`. A false result or
   verification fault maps to `F_verify subseteq F`; a true result yields the
   only success exit. Then destroy `B_candidate`, `M_tail`, `B_recovery`,
   `B_post`, and finally `B_attempt`/`B_input` under explicit cleanup rules.

## Concurrency and peak-accounting obligations

The required peak is the maximum over the explicitly named stage live sets,
not a sum of separate expected maxima:

- preparation: `{B_input, B_attempt, W_label, R_label}`;
- sieve attempt: `{B_input, B_attempt, W_sieve, R_sieve, B_sieve}`;
- recovery: `{B_input, B_attempt, B_post, B_recovery, accepted transcript}`;
- tail/verification: `{B_input, B_attempt, B_recovery, M_tail, B_candidate}`.

For every object class `W`, `R`, `B`, and `M_tail`, a future implementation
must provide a width/unit, birth point, last use, cleanup precondition, and
peak-stage membership. Retry counts may not be converted into a peak-memory
bound without those cleanup facts. The specification intentionally supplies no
numeric widths or probabilities.

## Error composition obligation

Before any success, resource, or finite-expectation assertion, a derivation
must justify a common-event inclusion such as

\[
 F_{\rm input}\cup F_{\rm oracle}\cup F_{\rm cleanup}\cup F_{\rm stop}
 \cup F_{\rm recovery}\cup F_{\rm tail}\cup F_{\rm verify}\subseteq F,
\]

and identify any dependency assumptions needed to bound that union. This is
only a checklist until an end-to-end implementation and verification trace
instantiate it. It does not map the BATCH-012 `F_sim` to `F`.
