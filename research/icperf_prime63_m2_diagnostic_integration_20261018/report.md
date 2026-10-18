# Prime63 m=2 diagnostic integration

**Scope:** TASK-20261018-7368da, engineering implementation only. Scientific runs in this handoff: **0**. The prospective diagnostic remains unapproved. The three archived m=2 solver attempts were each time censored at 300 seconds; this work adds a bounded, phase traced route for a future exact experiment. It makes no runtime or index calculus speedup claim.

## What was implemented

`execute.py` fixes the cell order to coset quadratic lift, random direct, and small_x direct over the same 475-point bases. Before either the parent or worker can create task output or invoke Sage, it checks the exact source manifest, frozen plan, repository authorization, owner and epoch claim, plan bound entrypoints, and ready or exact in-flight selector. The in-flight route also binds the supervisor launch, trial, command arrays, run directory and launch age. An injected unreadable-live-root monitor control runs first. A failed null control skips all three positives.

The prospective limits are 600 seconds, 8 GiB sampled process-tree RSS, 8 GiB scratch and model cap 64 per scientific call; 2100 seconds total, one worker, 16 GiB initial scratch free space and a stop below 8 GiB free. The monitor retains flushed phase/resource events plus raw stdout, stderr, request and response when present. The launcher hashes these first-attempt members into a raw archive and receipt. Resource samples with no readable RSS carry `null`. A timeout or cap is censored; a monitor fault is an infrastructure error.

`check.py` independently evaluates every polynomial equation modulo the prime, every full curve point, the signed point sum, factor-base membership, and the recorded summand position. The archived witness indices are summand positions; the checker separately derives actual indices in the 475-point base. It checks raw archive coverage and digests, phase sequence and source hashes, response/censor semantics, and contradictions between a producer no-solution assertion and an independently supplied planted witness.

## Synthetic validation

Thirteen `unittest` cases passed. They cover absent and forged admission, a stale supervisor launch, wrong owner, exact mocked worker forwarding, a synthetic monitor fault with retained trace and raw streams, changed source hash, the three archived planted witnesses, changed coordinate/sign/target/index, response versus bounded censor, missing raw member, and false no-solution. The mocked worker never calls a scientific solver. Exact static witness verification is a checker control, not a new solver result.

The source manifest binds the nine reused files named by [DEC-20261018-51074d](../../ledger/decisions/DEC-20261018-51074d.yaml), the pinned backend and the three implementation source files. The prospective packet binds the manifest and names the fresh-ID preapproval, committed plan, published claim and ready selector still required before any future run.

## Interpretation and remaining limits

This artifact establishes an implementation and synthetic-control result. It does not measure solver degree, relation yield, total index calculus cost or any speedup. The optional 475² ordered-pair full-point enumeration is a separately charged future control and was not run.

The current raw custody starts after repository admission and scratch checks. A disk error before the monitor can create its output directory can leave no call archive; this is an operational launch failure that a future approved supervisor must retain in its own execution receipt. The phase monitor's RSS is sampled, so an unsampled transient peak remains unmeasured. A future scientific diagnostic also needs a fresh approved experiment packet passing repository preapproval and an independent review of the resulting receipts before any performance conclusion.

**Evidence:** [input_manifest.json](input_manifest.json), [diagnostic_packet.json](diagnostic_packet.json), [validation.json](validation.json), and the source/tests in this directory. The flow is rendered in [diagram.svg](diagram.svg) and [report.pdf](report.pdf). Provenance: internal, independently checked by this Executor against the archived inputs and synthetic test run of 2026-10-18.
