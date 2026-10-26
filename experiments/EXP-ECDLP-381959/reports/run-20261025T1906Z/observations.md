# What ran and where it stopped

The three `candidate_0/1/2` compilations each exited 1 under the exact admitted flags, including `-Wshadow -Werror`. In `candidate/decoder.hpp:311`, the self-test local `b` shadows the local `b` declared at line 300. The compiler stderr preserves the declaration locations and error. This is a compiler/build failure, not a scalar-recovery result.

The three `solvers_0/1/2` builds each exited 0. Their fixed development self-tests each reported 269 checks passed. These are repeated development controls, not three independent scientific replications and not the 768-target study.

The driver dispatches the measurement pool only when all six builds and their self-tests succeed. That condition was false. Therefore no candidate or baseline measurement job ran; all 2,560 producer-part slots are empty; zero solver observation rows were produced. Independent public-witness verification was not reached, and the recorded certificate kind is `none`.

The aggregate driver lists six incomplete module records because none reached measurement. This does not mean all six failed compilation: three candidate builds failed, while three baseline builds/self-tests passed and their measurement stages were not dispatched.

Actual metadata and stdout/stderr remain sealed under [RUN-ECDLP-9f18c9](../../runs/RUN-ECDLP-9f18c9/). The report reconstructs no missing outputs and changes no source or sealed run file. All 2,612 artifact digests in the execution receipt match. The actual directory contains 2,613 files including that receipt, while the plan names 2,883 required artifacts; 270 not-created checker/verification-stage artifacts remain explicitly missing.

The next operational action is a versioned local-identifier repair with the exact admitted warning flags, followed by fresh source binding and admission. Reusing the untouched confirmation cohort would not retune on performance outcomes because this attempt generated no such outcomes. That later execution requires its own records and report. Correctness, recovery rates, CPU comparisons and scaling remain unanswered by this stopped attempt.
