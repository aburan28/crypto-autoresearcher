# stdout truncation (not a scientific defect)

The Stage-2 producer redirected stdout/stderr to
`experiments/EXP-CERTBIN-1bfef5/runs/RUN-CERTBIN-0dc7c4/{stdout,stderr}.log`.
A concurrent checkout removed that directory while PID 3100090 still held
the file descriptors (`stdout.log (deleted)` in /proc). Progress lines through
`V_S_octic2 progress 104/144` were rescued from the open fd at 07:11 UTC and
copied to stdout.log. Later progress lines were lost when the watcher
overwrote /tmp rescue stdout after process exit.

Process exit was 0 (`exit-code.txt`). `raw-result.json` / `stage2-result.json`
were written. This is recorded as a protocol deviation on logging only,
classified O-IMPEDIMENT would be wrong: the scientific artifacts completed.
