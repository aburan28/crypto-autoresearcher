# Local Linux resource-control probe

TASK-20260908-e7e0db completed three fixed operational controls under DEC-20260908-4f847e. No scientific experiment, curve, arithmetic benchmark, launch key, signature, allocation or RUN record was created. The result remains pending archive and independent review.

| Control | Observed result |
|---|---|
| Exact profile | Linux/arm64, memory.max=8589934592, memory.swap.max=0, cpu.max=100000 100000, pids.max=32, UID65534, exit0. |
| Deliberate mismatch | Actual memory.max=67108864 against the required8589934592; typed resource-profile refusal and exit42 before workload. |
| Small OOM control | Actual64MiB/no-swap profile, flushed before-allocation marker for128MiB, Docker OOMKilled=true and exit137. |

All three containers used user65534:65534, no network, no host mounts, a read-only root, dropped capabilities, no-new-privileges, private cgroup namespace, one CPU and a32PID limit. Their terminal states were inspected before their exact task-owned IDs were removed. The pinned official Python helper image remains cached. Its Python is3.13.15; its Linux kernel is7.0.12-linuxkit/aarch64. This helper is not the pinned Sage/PARI/FFT runtime of any experiment.

The first invocation downloaded the exact pinned manifest successfully but stopped on an absent optional Entrypoint metadata field before starting any container. Its commands, exit, UTC boundaries and exact source are preserved. The reader was corrected and the second invocation reused the image; exactly one image pull and three container-start attempts occurred, within the six-case allowance. Both invocation outputs are retained in probe-receipt.json.

The8GiB configuration readback and the64MiB OOM observation have different scopes. No8GiB stress test occurred, and the Docker VM reports only7,529,156,608bytes of physical memory. No full-capacity claim is made. Parent Docker CLI CPU is not container CPU, and post-OOM child CPU/RSS is unavailable. No successful Darwin RLIMIT_AS enforcement is inferred.

Next action: archive the four exact outputs under TASK-20260908-6cde4a, independently review the source and terminal receipts, then bind the required experiment arithmetic images, implementations and launch guards. Five reserve definitions are approved, but this probe alone admits none for scientific measurement.
