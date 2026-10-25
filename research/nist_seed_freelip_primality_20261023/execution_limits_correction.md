# Additive correction: memory limit was measured, not enforced

**23 October 2026.** The frozen first protocol says the FreeLIP replay is bounded to 256 MiB resident memory. The committed `run.py` does not install a hard memory limit or monitor child processes against that cap. This is a protocol implementation deviation. It does apply a 30-second monotonic whole-run watchdog to the compilation and each case process, although setup between subprocesses is not interrupted by an external supervisor.

The successful immutable [results](runs/freelip-20261023T2014Z/results.json) record `child_maxrss = 61292544` on macOS, approximately 58.5 MiB. That is below the intended cap as measured by `resource.getrusage(resource.RUSAGE_CHILDREN)`, but it does not prove that the cap was enforced. The 25 process exit codes, 75 raw classifications, and source/build digests are unaffected by this reporting correction. The first two build-failure records also remain unchanged.

If a future replay requires strict admission under the frozen memory cap, specify and verify an external supervisor or a platform-specific limit in a new protocol and new write-once run directory. Do not reinterpret this run as hard capped.
