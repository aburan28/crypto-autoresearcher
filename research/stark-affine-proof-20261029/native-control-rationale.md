# Native control implementation rationale

The official Lean reference documents `#check_failure term`: it elaborates by the same process as `#check`, reports an error if the term succeeds, and retains the partial term/type in the message log when it fails. Source: https://lean-lang.org/doc/reference/latest/Interacting-with-Lean/#Testing-Type-Errors (retrieved2026-10-29). This is a test of elaboration failure, not a proof of the negated proposition.

Place the exact zero-ring application after the six positive fully explicit `#check` declarations in the existing AffineTransition module. It attempts to derive False using the multiplication obstruction and the already-proved zero-ring equality. Successful positive declaration checks and the concrete argument types rule out a nonexistent declaration being the intended failure. Native logs must still be inspected for the specific missing Nontrivial (ZMod1) instance; unrelated failures do not satisfy review.

The original TXT fixture remains unchanged. The source addition creates no theorem and changes no six theorem statements. Existing CI builds the actual changed module; do not count the source addition as observed native rejection before that new build. No local build or experiment was launched.
