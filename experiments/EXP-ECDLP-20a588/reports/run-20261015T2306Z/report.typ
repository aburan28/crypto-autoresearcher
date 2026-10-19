#set page(paper: "a4", margin: 1.6cm, numbering: "1")
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")
#show table: set text(size: 7.5pt)

= Run report: EXP-ECDLP-20a588 — m=3 block order, L=3..7

*Observations only.* This report records what ran and what was measured. It has no verdict, support or weaken language; those belong to the evidence review.

- *Experiment* EXP-ECDLP-20a588 · *hypothesis* H-ECDLP-60de36 · *question* RQ-ECDLP-001 · *goal* GOAL-ECDLP-001 · *protocol* `EXP-ECDLP-20a588/specification.yaml` with its amendments.
- *Host* 4 vCPU Intel Xeon 2.10 GHz, 15 GB; msolve 0.6.5-1build2 (1 thread per process); Singular 4.3.2. Four worker processes, one solver process per solve. Timeout 600 s per solve. Seeds: sha256 of `EXP-ECDLP-f49f75/v1|m|L|instance`.

== Runs

#table(columns: 5, stroke: 0.4pt, [*run*],[*started (UTC)*],[*finished*],[*rows*],[*git HEAD*],
[20a588-01],[2026-10-15 23:06],[2026-10-16 01:07],[24],[b19cbdaf66],
[20a588-02],[2026-10-19 16:08],[none (lost)],[0],[d2d3f9ef29],
[20a588-03],[2026-10-19 16:18],[2026-10-19 16:58],[6],[1b1f8c2d02]
)

#figure(image("block-order-vs-L.svg", width: 100%), caption: [Median basis time per arm vs $L$ (measured; process wall time), bars min–max over completed instances; × = every instance timed out (600 s). Source runs as in the table. Where a cell mixes two primes (EXP-ECDLP-8c41d7, L = 4: Singular arms at p = 65551, msolve arms at p = 262271) only comparisons within one solver family are on shared instances.])

== Per-cell measurements

Columns: completed / timed out / other failure / degenerate target; median ms [min–max]; planted-in-variety (passed/checked); max F4 degree (msolve arms). A cell can mix two runs (and two primes, `p bits`) where an amendment re-ran arms; the source runs are listed.

#table(columns: 8, stroke: 0.3pt, [*L*],[*p bits*],[*arm*],[*runs*],[*ok/to/oth/deg*],[*median ms [min–max]*],[*planted*],[*F4 deg*],
[3],[10],[A_block_sg],[01],[6/0/0/0],[121 [112–130]],[4/4],[—],
[3],[10],[A_drl_ms],[01],[6/0/0/0],[146 [133–160]],[4/4],[12],
[3],[10],[A_elim_ms],[01],[6/0/0/0],[33 [27–41]],[4/4],[14],
[3],[10],[B_ms],[01],[6/0/0/0],[25 [19–32]],[4/4],[16],
[3],[10],[B_sg],[01],[6/0/0/0],[75 [74–80]],[4/4],[—],
[4],[13],[A_block_sg],[01],[6/0/0/0],[7,329 [7,116–7,984]],[4/4],[—],
[4],[13],[A_drl_ms],[01],[6/0/0/0],[9,933 [8,947–10,140]],[4/4],[13],
[4],[13],[A_elim_ms],[01],[6/0/0/0],[591 [512–642]],[4/4],[32],
[4],[13],[B_ms],[01],[6/0/0/0],[309 [277–336]],[4/4],[24],
[4],[13],[B_sg],[01],[6/0/0/0],[5,112 [4,472–5,458]],[4/4],[—],
[5],[16],[A_block_sg],[01],[0/6/0/0],[— [—–—]],[—],[—],
[5],[16],[A_drl_ms],[01],[0/6/0/0],[— [—–—]],[—],[—],
[5],[16],[A_elim_ms],[01],[6/0/0/0],[16,183 [14,145–16,526]],[4/4],[65],
[5],[16],[B_ms],[01],[6/0/0/0],[6,993 [6,559–7,195]],[4/4],[40],
[5],[16],[B_sg],[01],[6/0/0/0],[370,938 [274,132–376,859]],[4/4],[—],
[6],[19],[A_elim_ms],[01],[6/0/0/0],[411,159 [347,985–418,707]],[4/4],[133],
[6],[19],[B_ms],[01],[6/0/0/0],[210,271 [194,599–213,522]],[4/4],[72],
[6],[19],[B_sg],[01],[0/6/0/0],[— [—–—]],[—],[—],
[7],[22],[A_elim_ms],[03],[0/6/0/0],[— [—–—]],[—],[—],
[7],[22],[B_ms],[03],[0/6/0/0],[— [—–—]],[—],[—]
)

== Operational notes (facts, not findings)

- RUN-01 was stopped by the host's 7200 s background-task limit during L = 7; cells L = 3..6 were complete. RUN-02 (the AMD-01 run for L = 7) was lost to a VM recycle after about ten minutes and wrote no rows; RUN-03 (AMD-02) re-ran L = 7 for the two arms the stopping rule had not retired (A_elim_ms, B_ms).
- Stopping rule: A_drl_ms and A_block_sg were retired at L = 5, B_sg at L = 6; at L = 7 every instance timed out for both A_elim_ms and B_ms.
- Cell L = 6: A_elim_ms 411 s and B_ms 210 s median (completed); the Singular dense arm timed out on all six instances.
- msolve 0.6.5 segfaults on systems over 17- and 18-bit primes (CORR-20261019-e6f65b); no cell of this experiment used one (primes 10, 13, 16, 19 and 22 bits).
- A unit-test run (tools/test_pkm_isogeny_launchers.py, about 6 s on one core) and a few seconds of exploratory analysis shared the host with RUN-02/RUN-03 (L = 7, where every solve ended at the 600 s cap, so the timings are not affected).
- Every planted decomposition found lies in the computed basis; the eliminated chain basis equals the dense basis on every instance where both finished.

