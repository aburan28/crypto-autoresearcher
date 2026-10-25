# Resolve the second bundled fixture before resuming controls

24 October 2026 UTC, after checker-controls-v1 stopped and before its continuation.

The first run assumed both bundled C-format examples were valid positives. The second example was rejected at its first two theorem-3 steps. That assumption was not source-verified and is corrected additively here; the raw example and failed run are preserved.

The current reader divides N−1 by every factor listed in the certificate and treats the remaining cofactor as the prime p for theorem 3. In the second example's first two steps, the listed factors already consume all of N−1, so the recovered cofactor is 1. The checker then rejects the witnesses as predicted by ordinary modular arithmetic. This is a fixture/current-reader discrepancy, not evidence of a wrong arithmetic result or an identified historical bug. The archive does not establish whether the example was stale or intentionally negative.

Keep the raw example as a rejected-format control. Create a separately named variant omitting the large factor from each of those two lists, so the current reader recovers 1583 and 113. Independently check primality and the stated theorem-3 modular conditions before executing the variant. Do not alter the original example, reader or mathematical algorithm. fixture_diagnostic.py records the exact edits, hashes and arithmetic.

Resume checker controls using the already captured first two runs; execute only the new variant and the remaining fixtures. There are five proposed positives and four negatives in the completed set. Add a final-zero structural requirement to the admission predicate so an incomplete byte stream cannot pass merely through partial successful output. This remains a bounded compatibility control, not a general independent certificate verifier.
