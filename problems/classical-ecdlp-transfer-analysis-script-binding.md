# Transfer postrun analysis-script binding

- **Status:** investigating; versioned mechanical correction in preparation.
- **Kind:** implementation/export binding gap.
- **Affected work:** EXP-ECDLP-8dc19d/RUN-ECDLP-994f70 postprocessing only; frozen CPU scientific source and protocol are preserved.
- **Next action owner:** Executor TASK-20261028-870b3b, custody Coordinator TASK-20261028-cf40ac.
- **Last updated:** 2026-10-28.

The frozen adapter [harness/classical_ecdlp_transfer_successor/postrun/run_postrun.v2.py](../harness/classical_ecdlp_transfer_successor/postrun/run_postrun.v2.py:214) compares the independent verifier SHA to protocol.analysis_plan.script.sha256. The registered script is analysis.py (d5ff4e...), while the verifier is verify.py (2654f5...). They perform different specified roles. The same adapter exports verify.py as analysis.script at line150. Those checks deterministically refuse an otherwise correct source binding or mislabel the analysis source.

This was identified by source inspection during the active scientific VM, without choosing on mathematical outcomes. No before-affected-data claim is made. The seven VM modules, independent verifier, registered d5analysis script, metrics, sample counts, controls and statistical definitions remain correct and unchanged. No scientific algorithm failure or q result is inferred.

Exit criteria: a separate v3 adapter verifies the actual adjacent registered d5analysis bytes and exports that exact script, while independently enforcing the existing seven-module manifest/verifier hash. Preserve v2 and its refusal; add narrow source-binding/export regression checks and actual adapter provenance. Archive corrected outputs with the frozen protocol and an explicit correction note. No new cohort, scientific rerun, estimand, threshold or protocol version is introduced by this repair.

The next step is the versioned mechanical adapter under DEC-20261028-7bc743. A failed binding remains an operational validation failure; it never becomes a mathematical negative. The mechanism graph is unchanged; only the distinction between verifier source and registered statistical-analysis source is corrected. Final resolution requires actual source/test and export checks, not this problem record alone.

## 2026-10-28 observed missing-import refusal

The actual first v2 postrun invocation returned1 before independent verification because `hashlib` was undefined in the official-protocol hashing path. The separately preserved v3 adapter also omitted that import. This observed implementation failure precedes the script-pin check; it is not a failed circuit result. DEC-20261028-743e6e authorizes a separate v4 adding the missing standard-library import, retaining both older versions/refusals. Undefined-name/import and binding checks must pass before the corrected postprocessing. Frozen VM source, registered analysis.py d5, verifier2654, protocol, counts and all scientific outputs remain unchanged. Final resolution still requires actual complete verifier/export/report checks.
