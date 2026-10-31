#set page(paper: "a4", margin: 22mm)
#set text(size: 11pt)
= Certified D4 panel input: n45 polynomial01
Observations only. The original independent checker accepted the newly produced degree-four certificate. All 46 multiplication-closure checks passed. Accepted codimension is 12,742 and fresh exact solution count is 0. The strict inequality establishes LFD at least 5 for this exact input; neither degree six nor an upper bound follows.

#image("flow.svg", width: 100%)

The certificate contains 288,550,808 bytes. SHA-256: #text(size: 8pt)[9dcb292d0e181ae960e25da8bd61886407ddb1dcf84ccd70b592ddb1617c1324]. All 47 worker-recorded hashes and the frozen request identity were verified after successful worker termination. Controls, counter, producer and checker completed without timeout. Host timings are L0 diagnostics only.

One original unfinished input completed, with no new draw; a prior attempt was refused before worker launch. The 32-input panel now has 24 terminal inputs and 17 certified lower bounds; eight n45 inputs remain unfinished. The separate high-memory campaign remains in scope. No n47 D5 acceptance is inferred from this result.

The accompanying raw archive includes all records except the separately retained main certificate, including the small control certificates. The full certificate is retained under panel-local-n45-poly01-002/attempt-001 in the data directory. Publication and full download verification are recorded separately in panel-local-archive-001; publication success is not anticipated here.

Frozen protocol analysis_plan.inputs retains the earlier local01 request/system paths. The hash-pinned plan points to local02; the requests differ only in attempt id and the system bytes are identical. This stale path list is disclosed, not rewritten or represented as full protocol conformance.

Source commit: 23f57b9b558625dbb19c0ffd972ffc13404793d0. The protocol and two-stage export accompany the report. These are two stages on one input, not two independent samples. No population or timing claim is made.
