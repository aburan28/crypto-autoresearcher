# Heavy pass plan (serialized, one process, after workers A and B finish)

Cells whose msolve F4 trace or degree-4 closure exceeds the two-worker budget
(7 GB per worker; the container cgroup killed worker B at 9.7 GB RSS while
worker A held 5.8 GB):

- (13,4,4,4) N=42: F4 trace (unreached at 7 GB after 15 rounds, all step degree <= 4)
- (17,3,3,8) N=41: F4 trace
- (19,3,3,7) N=40: F4 trace (unreached at 7 GB after 16 rounds, all step degree <= 4); closure D=4 (OOM in worker B)
- (21,3,3,7) N=42: F4 trace; closure D=4

Each runs alone with an msolve cap of ~12 GB and a closure estimate cap of
5 GB (M4RI working memory is roughly twice the dense matrix estimate), draw 0
first for every cell, further draws only if draw 0 completes.
duplicate B relaunch (pid 9336, --no-closure, 08:10-08:43) stopped; it shared workerB/cells with pid 9160 and may have written duplicate records for the same instances -- summarize.py keeps the first completed record per (instance, instrument)
worker B (pid 9160) stopped at 2026-09-17T09:06:55Z to avoid a second OOM: its remaining closures ((19,3,3,7) ran_B_ran d0; (21,3,3,7) x4 d0) move to the serialized heavy pass; its F4 traces and single-level records are complete
worker C started 2026-09-17T09:28:10Z: off_diagonal F4 traces + single-level only (--no-closure, msolve cap 5 GB) alongside worker A; closures for (17,3,3,7) and (17,3,3,8) draw 0 x 4 variants move to the heavy pass; worker A will skip off-diagonal instances whose F4 trace C completed
(17,3,3,7) N=38 msolve unreached at 5 GB after 12 rounds (all step degree <= 4): F4 trace deferred to the heavy pass; worker C relaunched 2026-09-17T09:33:35Z with both off-diagonal cells on the skip list
A1 + H1 launched 2026-09-17T10:49:29Z: worker A relaunched on (17,3,3,6) with controls after the D=5 null-closure OOM (closure column cap 200k added); heavy pass H1 = msolve at 8 GB on (19,3,3,7) low_B_equ draw 0
heavy H1 (19,3,3,7) low_B_equ d0 at 8 GB: unreached_memory_cap after 16 rounds (751 s), max step degree 4; retry at 12-13 GB once worker A is done
heavy_closure stopped 2026-09-17T11:45:03Z mid-(21,3,3,7) ran_B_equ D=4 closure: free memory had fallen to 3 GB with worker A's 5.9 GB matched-null msolve trace also running; no record was written for that instance, and --closure-only-missing will pick it up again. Restart after worker A's null trace hits its 3600 s wall cap (~12:01Z).
heavy F4 pass queued 2026-09-17T12:01:32Z: waits for all workers to exit, then msolve at 13 GB on (13,4,4,4), (19,3,3,7), (17,3,3,7) low_B_equ draw 0, one at a time, 90 min wall cap each
heavy_closure stopped for good 2026-09-17T12:34:53Z after 3 decided closures at (21,3,3,7) (low_B_equ sufficient, low_B_ran sufficient, ran_B_equ undetermined): free memory was 2 GB with worker A also running, and the remaining variants duplicate cells that already carry a decided closure verdict. (19,3,3,7) already has two decided verdicts from worker B.
worker A scheduled to stop between instances ~13:03Z 2026-09-17T12:37:58Z: its remaining draws replicate cells already measured, while the deferred F4 traces at N = 40-42 are unmeasured; the queued heavy F4 pass takes the machine next
off-diagonal closure launched 2026-09-17T13:49:31Z: (17,3,3,7) and (17,3,3,8) low_B_equ draw 0, the cells where the paper's Section 4.5.1 says the regularity degree generally exceeds 4 while the first fall degree stays 4; their F4 traces now give d_F4 = 4 and |V(I)|, so a closure verdict there is decidable
(17,3,3,8) F4 trace launched 2026-09-17T14:22:12Z at 13 GB: its degree-4 closure left rank deficiency 25588 of 112792 columns (versus 6-36 on the cells that came out sufficient) and is undetermined only for want of |V(I)|; a completed trace settles both the degree and the verdict at k = ceil(n/m) + 2, the furthest off-diagonal cell in the contract
