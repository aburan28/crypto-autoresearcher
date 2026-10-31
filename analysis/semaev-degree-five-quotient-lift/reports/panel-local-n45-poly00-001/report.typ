#set page(paper: "a4", margin: 22mm)
#set text(size: 11pt)
= Certified D4 panel input: n45 polynomial00
Observations only. The original independent checker accepted the newly produced degree-four certificate. All 46 multiplication-closure checks passed. Accepted codimension is 12,747 and fresh exact solution count is 4. The strict inequality establishes LFD at least 5 for this exact input; neither degree six nor an upper bound follows.

#image("flow.svg", width: 100%)

The certificate contains 288,550,808 bytes. SHA-256: #text(size: 8pt)[e2ee2efe28ed90832632256794bceb2f8f473e82504d6e3bad2c1aa4be013dc1]. All 47 worker-recorded hashes and the frozen request identity were verified after successful worker termination. Controls, counter, producer and checker completed without timeout. Host timings are L0 diagnostics only.

One original unfinished input completed, with no new draw or retry. The 32-input panel now has 23 terminal inputs and 16 certified lower bounds; nine n45 inputs remain unfinished. The separate high-memory campaign remains in scope. No n47 D5 acceptance is inferred from this result.

The accompanying raw archive includes all non-certificate records and controls. The full certificate is retained under panel-local-n45-poly00-001/attempt-001 in the data directory. Publication and full download verification are recorded separately in panel-local-archive-001; publication success is not anticipated here.

Source commit: c863dad4f159ce9e29a8043e89f048ae26ff4a98. The protocol and two-stage export accompany the report. These are two stages on one input, not two independent samples. No population or timing claim is made.

Protocol prose discrepancy: the frozen variable ledger retains stale references to n44 random04 and earlier n43 scheduling. Its request path, prior input id, system digest, plan digest and observed checker arguments bind n45 polynomial00. The certificate claim uses those exact bytes and independent checking. The historical protocol is unchanged; full prose consistency is not claimed.
