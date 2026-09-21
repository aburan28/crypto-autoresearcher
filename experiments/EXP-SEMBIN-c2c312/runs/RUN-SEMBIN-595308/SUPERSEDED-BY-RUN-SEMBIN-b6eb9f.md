# RUN-SEMBIN-595308 is superseded by RUN-SEMBIN-b6eb9f

This directory holds the interim snapshots of an in-flight run that were
committed while two workers were still writing to it. That was a mistake
against the append-only rule for run records (AGENTS.md rule 4;
tools/check_run_immutability.py): the snapshots that reached `main` froze
`workerA/`, `workerB/`, `RUN-STATUS.md` and the logs at partial states, and
every later write to them was a modification of a committed run file.

Nothing here is edited after the fact. The measurement continues, on the
instrument as merged at commit 49043c6ba (single-level Macaulay statistic
multiplying the original generators; identity control without msolve
timings; per-child peak RSS) and with the oversize msolve cells deferred to
a serialized heavy pass, under a fresh identifier:

    experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/

That run is committed exactly once, when complete, with its manifest. The
records in this directory (controls, the (15,5,3,3) cell, the memory-cap
failures at N = 40 and N = 42 that motivated `msolve -u 1` and the heavy
pass) remain as raw outputs of failed and partial attempts, per the run
skill's "retain raw outputs and failed attempts". They are not an official
run record and no manifest will be added here.
