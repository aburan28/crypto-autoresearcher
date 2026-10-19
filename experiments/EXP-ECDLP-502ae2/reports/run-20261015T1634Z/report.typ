#set page(paper: "a4", margin: 1.6cm, numbering: "1")
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")
#show table: set text(size: 8pt)

= Run report: EXP-ECDLP-502ae2 (RUN-ECDLP-502ae2-01)

*Observations only.* No verdict or support/weaken language; the evidence review is in `reports/review-*/`.

- *Experiment* EXP-ECDLP-502ae2 (instrument replication of EXP-ECDLP-f49f75 at m = 3) · *hypothesis* H-ECDLP-60de36 · *question* RQ-ECDLP-001 · *goal* GOAL-ECDLP-001
- *Run* RUN-ECDLP-502ae2-01: started 2026-10-15 16:34 UTC, finished 18:26 UTC, exit 0, 30 instances; launcher commit 43f93787df (clean tree at launch).
- *Command* `python3 experiments/EXP-ECDLP-502ae2/msolve_grid.py --plan experiments/EXP-ECDLP-502ae2/trial-plan.json --out …/RUN-ECDLP-502ae2-01/raw-result.jsonl --workers 4`; seed string `EXP-ECDLP-f49f75/v1` (instances identical to EXP-ECDLP-f49f75 RUN-02 for L = 3..5).
- *Host* 4 vCPU Intel Xeon 2.10 GHz, 15 GB; msolve 0.6.5-1build2 (1 thread per process); Singular 4.3.2 used only to expand $S_4$ (untimed).

== Instrument and arms

Per Gröbner arm and instance: `msolve -g 2 -v 2` (reduced DRL basis; wall time; max F4 degree from the verbose log; basis used for the planted check), then, if it finished, `msolve -P 1` (full solve: F4 + FGLM parametrization; wall time). An instance counts as completed only when both finish within 600 s each. Arms: A chain encoding ($3L$ variables), B same set dense (3 variables), C random set dense, E meet-in-the-middle enumeration. Stopping rule: an arm with every instance timed out in a cell is not run at larger $L$.

#figure(image("msolve-cost-vs-L.svg", width: 100%), caption: [Left: median full-solve time (msolve `-P 1`, measured, ms) per arm vs $L$, bars min–max over completed instances; dotted: Singular std+fglm medians on the same instances (EXP-ECDLP-f49f75 RUN-02); × = every instance timed out. At $L = 6$ only the two random targets (no decomposition, quotient dimension 0) completed for B and C. Right: maximum F4 degree reached in the `-g 2` run, over instances whose basis completed. n = 6 per cell.])

== Per-cell measurements

Columns: completed / timed out / crashed / degenerate target; median full-solve ms [min–max]; median basis-only (`-g 2`) ms; max F4 degree (basis-completed instances); instances whose basis completed; planted check passed/checked.

#table(columns: 9, stroke: 0.3pt,
[*L*],[*p bits*],[*arm*],[*ok/to/crash/deg*],[*solve ms [min–max]*],[*gb ms*],[*max F4 deg*],[*gb done*],[*planted*],
[3],[10],[A],[6/0/0/0],[1,403 [150–2,632]],[205],[12],[6],[4/4],
[3],[10],[B],[6/0/0/0],[85 [18–177]],[26],[16],[6],[4/4],
[3],[10],[C],[6/0/0/0],[126 [19–162]],[24],[16],[6],[4/4],
[3],[10],[E],[6/0/0/0],[54 group ops (FB 4)],[—],[—],[—],[—],
[4],[13],[A],[6/0/0/0],[291,249 [10,769–295,409]],[10,488],[13],[6],[4/4],
[4],[13],[B],[6/0/0/0],[1,941 [286–2,049]],[343],[24],[6],[4/4],
[4],[13],[C],[6/0/0/0],[1,375 [309–1,960]],[322],[24],[6],[4/4],
[4],[13],[E],[6/0/0/0],[152 group ops (FB 8)],[—],[—],[—],[—],
[5],[16],[A],[0/6/0/0],[—],[—],[—],[—],[—],
[5],[16],[B],[6/0/0/0],[35,222 [7,126–49,713]],[7,588],[40],[6],[4/4],
[5],[16],[C],[6/0/0/0],[49,120 [7,106–50,496]],[7,736],[40],[6],[4/4],
[5],[16],[E],[6/0/0/0],[629 group ops (FB 17)],[—],[—],[—],[—],
[6],[19],[B],[2/4/0/0],[214,509 [213,622–215,396]],[223,386],[72],[6],[0/0],
[6],[19],[C],[2/4/0/0],[229,398 [227,944–230,853]],[218,344],[72],[6],[0/0],
[6],[19],[E],[6/0/0/0],[2,146 group ops (FB 32)],[—],[—],[—],[—],
[7],[22],[B],[0/6/0/0],[—],[—],[—],[—],[—],
[7],[22],[C],[0/6/0/0],[—],[—],[—],[—],[—],
[7],[22],[E],[6/0/0/0],[8,000 group ops (FB 62)],[—],[—],[—],[—]
)

== Operational notes (facts)

- Stopping rule retired arm A at $L = 5$ (all 6 instances timed out in the basis step) and arms B, C at $L = 7$.
- At $L = 6$, all 6 B and C bases completed (max F4 degree 72); the full solve timed out on the 4 planted instances and finished on the 2 random targets.
- Arm A at $L = 4$: basis step about 10 s on every instance; full solve 10.8–295 s.
- msolve 0.6.5 segfaults on the dense $m = 2$, $L = 8$ system (degree-256 univariates), so $m = 2$ was out of scope. Its input parser keeps only the last of several constant terms; the launcher always emits one merged constant.
