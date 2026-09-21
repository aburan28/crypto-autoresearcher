# Handoff: EXP-SGCP-SECANT-REP-001 V5 accounting review

## Claim or task

Audit exact commit `a33427b255ae1fca37146647788962e9b0960257`
for deterministic source-stage accounting.

## Status

`OPEN` - **REVISE**

## Evidence so far

The 121-leaf nested vector, success and total failure vectors, supervisor
scope, half-open concurrency, and authority transition passed.

## Failure modes

1. Additive, maximum, deduplicated, makespan, concurrency, and storage-charge
   paths are not exhaustively partitioned.
2. Attempts and storage artifacts lack all-and-only process-DAG closure.
3. Design and implementation bindings do not form one closed post-source
   chain.
4. Coordinator action order and review equality are not canonical.
5. Several input, decision, and control-detail digest preimages remain open.

## Next concrete action

Keep campaign accounting locked and authorize, after separate review, only a
pure mathematical kernel with explicitly non-campaign operation counters.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/source-schema-v5.json`
- `experiments/EXP-SGCP-SECANT-REP-001/process-accounting-v2.json`
