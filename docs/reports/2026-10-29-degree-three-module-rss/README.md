# Peak memory of `BooleanParityDegreeThreeRankCertificate` with `LEAN_NUM_THREADS=1` — 2026-10-29

Measured for [problems/formal-workspace-build-exceeds-16gb.md](../../../problems/formal-workspace-build-exceeds-16gb.md).

## Result

With `LEAN_NUM_THREADS=1`, elaborating the module on this cloud container was
**OOM-killed after 339 s**, with **13.52 GB (12.89 GiB) of anonymous memory**
still growing. The kill came from a **memory-cgroup limit of 14,341,885,952 bytes
(13.36 GiB)** on the session's command cgroup. Physical RAM did not run out.
So the module's peak resident memory is **above 13.5 GB**. The upper value
is unmeasured, because the run never completed.

- `LEAN_NUM_THREADS=1` does **not** fix it. It limits Lean's task workers, but
  the process still had 8 OS threads, and almost all the memory is one growing
  anonymous heap.
- The earlier record called this a "15 GiB container". `MemTotal` is
  15.7 GiB, but Bash commands run in a memcg capped at 13.36 GiB. That cap,
  not the RAM size, is what killed the 2026-10-23 builds too. They died at
  471 s and 500 s on the same module.

## Inputs

| | |
| --- | --- |
| Revision | `origin/main` `1896454c43bede18d19fb51362d748ed3246227e` |
| Module | `formal/CryptoResearch/Semaev/BooleanParityDegreeThreeRankCertificate.lean`, sha256 `e9db58305eb32c33bf7d6aef26f028a6791f5816dcfa53a4b3b2b95b2c0751e9` |
| Toolchain | Lean 4.35.0-rc1, Lake 5.0.0-src+86c6347, Mathlib `7fa22735` (from `lake exe cache get`) |
| Dependencies | `lake build CryptoResearch.Semaev.BooleanParitySemanticRankCertificate` (exit 0; FiniteCertificate 34 s, SemanticRank 194 s) |
| Command | `LEAN_NUM_THREADS=1 python3 -I measure.py threads1 <dir> -- lake env lean CryptoResearch/Semaev/BooleanParityDegreeThreeRankCertificate.lean` (from `formal/`) |
| Host | [host.txt](host.txt): 4 CPUs, MemTotal 16,477,352 kB, no swap, memcg limit 14,341,885,952 B |

## Files

- [measure.py](measure.py) samples the process tree's `VmRSS` and Lean's
  `VmHWM` every 0.5 s. Its watchdog (MemAvailable < 600 MB) never fired,
  because the memcg limit is below physical RAM.
- [anon.sh](anon.sh) samples Lean's `RssAnon` and `RssFile` every 0.5 s.
- [threads1.samples.tsv](threads1.samples.tsv), [threads1.anon.tsv](threads1.anon.tsv)
  and [threads1.summary](threads1.summary) are the raw output.
- [dmesg-oom.txt](dmesg-oom.txt) is the kernel OOM record:
  `constraint=CONSTRAINT_MEMCG`, `Killed process 7668 (lean) ... anon-rss:13520596kB`.

## Memory over time (from `threads1.anon.tsv`)

| t | RssAnon | RssFile (mapped Mathlib `.olean`) |
| ---: | ---: | ---: |
| 20 s | 3.02 GiB | 6.47 GiB |
| 102 s | 4.69 GiB | 6.47 GiB |
| 185 s | 7.45 GiB | 4.86 GiB |
| 226 s | 4.26 GiB | 2.92 GiB |
| 268 s | 8.12 GiB | 1.36 GiB |
| 288 s | 10.21 GiB | 0.02 GiB |
| 310 s | 12.79 GiB | 0.02 GiB |
| 339 s | killed at 12.89 GiB | |

From about 250 s, the heap grows about 0.12 GiB/s. Under pressure the kernel
dropped the mapped `.olean` pages (RssFile → 0) before the kill. Those pages are
reclaimable, so only anonymous memory counts toward the failure. The hosted
runner needed 579 to 671 s for the whole module. This run was killed at about
340 s, so peak use may come later and be higher than 13.5 GB.

## What this does not establish

- The true peak. Measuring it needs a host with more than about 16 GB
  available to the process, or swap.
- A run with the default thread count. It would hit the same 13.36 GiB cap.
- Anything about the module's correctness. CI builds and audits it.
