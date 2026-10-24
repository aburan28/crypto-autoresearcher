#set page(paper: "a4", margin: 1.6cm, numbering: "1")
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")
#show table: set text(size: 7.5pt)

= Run report: EXP-ECDLP-8c41d7 — m=4 block order, L=2..4

*Observations only.* This report records what ran and what was measured. It has no verdict, support or weaken language; those belong to the evidence review.

- *Experiment* EXP-ECDLP-8c41d7 · *hypothesis* H-ECDLP-60de36 · *question* RQ-ECDLP-001 · *goal* GOAL-ECDLP-001 · *protocol* `EXP-ECDLP-8c41d7/specification.yaml` with its amendments.
- *Host* 4 vCPU Intel Xeon 2.10 GHz, 15 GB; msolve 0.6.5-1build2 (1 thread per process); Singular 4.3.2. Four worker processes, one solver process per solve. Timeout 600 s per solve. Seeds: sha256 of `EXP-ECDLP-f49f75/v1|m|L|instance`.

== Runs

#table(columns: 5, stroke: 0.4pt, [*run*],[*started (UTC)*],[*finished*],[*rows*],[*git HEAD*],
[8c41d7-01],[2026-10-16 01:07],[none (lost)],[6],[6d6df97b6d],
[8c41d7-02],[2026-10-16 03:15],[none (lost)],[6],[04a87943e2],
[8c41d7-03],[2026-10-19 16:58],[2026-10-19 17:38],[6],[4ad12014e3],
[8c41d7-04],[2026-10-19 17:41],[2026-10-19 18:32],[6],[7413b95b6a]
)

#figure(image("block-order-vs-L.svg", width: 100%), caption: [Median basis time per arm vs $L$ (measured; process wall time), bars min–max over completed instances; × = every instance timed out (600 s). Source runs as in the table. Where a cell mixes two primes (EXP-ECDLP-8c41d7, L = 4: Singular arms at p = 65551, msolve arms at p = 262271) only comparisons within one solver family are on shared instances.])

== Per-cell measurements

Columns: completed / timed out / other failure / degenerate target; median ms [min–max]; planted-in-variety (passed/checked); max F4 degree (msolve arms). A cell can mix two runs (and two primes, `p bits`) where an amendment re-ran arms; the source runs are listed.

#table(columns: 8, stroke: 0.3pt, [*L*],[*p bits*],[*arm*],[*runs*],[*ok/to/oth/deg*],[*median ms [min–max]*],[*planted*],[*F4 deg*],
[2],[9],[A_block_sg],[01],[6/0/0/0],[113 [109–127]],[4/4],[—],
[2],[9],[A_drl_ms],[01],[6/0/0/0],[40 [38–63]],[4/4],[32],
[2],[9],[A_elim_ms],[01],[6/0/0/0],[25 [23–28]],[4/4],[32],
[2],[9],[B_ms],[01],[6/0/0/0],[22 [20–27]],[4/4],[32],
[2],[9],[B_sg],[01],[6/0/0/0],[49 [48–50]],[4/4],[—],
[3],[13],[A_block_sg],[02],[5/0/0/1],[344,621 [344,433–349,883]],[3/3],[—],
[3],[13],[A_drl_ms],[02],[5/0/0/1],[61,421 [59,168–62,017]],[3/3],[32],
[3],[13],[A_elim_ms],[02],[5/0/0/1],[12,929 [11,990–13,389]],[3/3],[32],
[3],[13],[B_ms],[02],[5/0/0/1],[10,700 [10,378–10,976]],[3/3],[32],
[3],[13],[B_sg],[02],[5/0/0/1],[70,364 [65,931–71,061]],[3/3],[—],
[4],[17],[A_block_sg],[03],[0/5/0/1],[— [—–—]],[—],[—],
[4],[19],[A_drl_ms],[04],[0/4/1/1],[— [—–—]],[—],[—],
[4],[19],[A_elim_ms],[04],[0/5/0/1],[— [—–—]],[—],[—],
[4],[19],[B_ms],[04],[5/0/0/1],[582,996 [518,230–586,271]],[3/3],[40],
[4],[17],[B_sg],[03],[0/5/0/1],[— [—–—]],[—],[—]
)

== Operational notes (facts, not findings)

- Three interruptions: RUN-01 (L = 2 complete) lost to a VM restart during L = 3; RUN-02 (L = 3 complete) lost to a second VM restart during L = 4; RUN-03 (L = 4) ran to the end. Amendments AMD-01 and AMD-02 resumed the unexecuted cells with an unchanged launcher, seeds, arms, timeout and stopping rule.
- RUN-03, cell L = 4 at p = 65551 (17 bits): every msolve arm crashed with a segmentation fault (rc -11) on every instance within a fraction of a second; both Singular arms timed out on all six instances. The crash is an msolve 0.6.5 defect on 17- and 18-bit primes (reproduced on standalone systems; CORR-20261019-e6f65b, AMD-03).
- RUN-04 (AMD-03) re-ran the msolve arms of L = 4 at p = 262271 (19 bits), via block_order_m4_p19.py, which overrides only that prime choice. The Singular arms of L = 4 stay at p = 65551 from RUN-03. RUN-03's msolve rows are instrument failures and are replaced by RUN-04's in the merged table.
- RUN-04, cell L = 4: B_ms completed on every non-degenerate instance in 518–586 s (cap 600 s); A_elim_ms timed out on every one; A_drl_ms timed out on all but one instance, which was killed with rc -9 after 184 s (signal 9; cause not diagnosed. The validator measured A_drl_ms alone reaching 3.4 GB by 200 s, so four concurrent copies may have exceeded the memory budget; unproven). One of six instances had a degenerate planted target (sum = point at infinity).
- A unit-test run (about 6 s on one core, including a msolve canary) shared the host with RUN-04 at about 17:44 UTC (recorded in its operational-notes.txt).
- Every planted decomposition found lies in the computed basis; the eliminated chain basis equals the dense basis on every instance where both finished (L = 2, 3).

