# Approval of the three bounded calibrations

The user explicitly said **“yes all approved”**. DEC-20260906-f73475 records Coordinator approval of all three unchanged designs and authorizes their necessary bounded implementation/reuse work. This is a durable approval action, not a request for further user confirmation.

| Experiment | Measurement budget approved | Implementation task | Implementation archive |
| --- | --- | --- | --- |
| EXP-ECDLP-1b1b99 |7200wall seconds,2CPU hours,8GiB,1run/worker | TASK-20260906-2f2a56 | TASK-20260906-ebfb30 |
| EXP-ECDLP-910fcd |3600wall seconds,1CPU hour,8GiB,1run/worker | TASK-20260906-681152 | TASK-20260906-cb2dfb |
| EXP-ECDLP-651b94 |5400wall seconds,1.5CPU hours,8GiB,1run/worker | TASK-20260906-9393c3 | TASK-20260906-c1e2d5 |

Each implementation task has its own3600wall-second/1CPU-hour/8GiB envelope, one worker and **maximum_runs0**. It owns exactly five files beneath its experiment’s implementation/task directory. Software checks are limited to20 synthetic or mocked tests,10seconds each and120seconds aggregate within that envelope. Scientific fixtures, pairing measurements, collision censuses and timing matrices are not unit tests and may not run in these tasks.

The original hypotheses and specifications remain byte-for-byte immutable. Each experiment now has an additive experiment_approval record at approvals/DEC-20260906-f73475.yaml binding the original specification SHA256, source snapshot **1a7917e234dd599e9fec58fe93299652a5c019ce**, decision and user authorization. The effective approved contract is that source plus its additive approval and decision. Original review_required/approved_by:null metadata accurately describes the earlier design snapshot and does not negate current user approval. These authority records are not fabricated runtime/code locks.

The user’s explicit authorization admits these three named calibrations despite the standing GOAL-CRYPTO-001 curve-work hold. It does not establish a novel breakthrough mechanism, satisfy broad scientific admission/completion criteria, promote any hypothesis, or change the goal head. The known CM auxiliary, known Tate interface and Coordinator-selected spectral control retain their narrow design boundaries; the user’s truncated spectral mechanism remains missing.

Parent control plane will archive this approval package, verify receipts, publish the existing PR update and admit the implementation/reuse tasks sequentially. Reuse inspection takes precedence over duplicate work. Each implementation is archived before downstream admission. Experimental measurement proceeds only after independent implementation review and a genuine launch lock binding actual code, runtime, plan and budgets, plus a proper run handoff. No new user confirmation is needed for this unchanged approved scope. A genuine protocol change is handled through an additive amendment with appropriately scoped authority.

No implementation, successful check, independent-review verdict, runtime lock, run record or empirical result was produced by this approval task. Parent reported that automated PR review failed because Anthropic credentials were missing; that is an infrastructure condition, not a scientific verdict or evidence that substantive review passed.

Authored by TASK-20260906-546f9d. Parent owns queue, archival receipts and PR publication. This report and the seven YAML authority records are the task’s eight exact output paths.
