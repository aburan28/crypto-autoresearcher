# Separate worker qualification

The pinned lab image completed the three small software controls in job
`semaev-worker-control-20261029-1540`. All three certificates are byte-identical
to the original native reference outputs; solution counts 3, 1, and 1 equal
full Boolean enumeration. The unchanged independent checker accepted each
certificate in the worker and again locally after S3 download.

Evidence: [remote result](worker-remote-20261029/result.json),
[S3 readback](worker-remote-20261029/readback.json),
[job and image identity](worker-remote-20261029/job-status.json),
[local rechecks](worker-remote-20261029/local-recheck/), and
[local controls](worker-local-20261029/result.json).
All 25 entries in the remote hash manifest were verified after GET.

This qualifies the tested software on the tested pod. It establishes no
frontier lower bound, runtime advantage, universal CPU portability, or
large-memory capacity. Each future scientific worker still needs its own
controls, frozen input/protocol identity and durable artifact upload.

The [pending-input inventory](../runtime/remaining-n42-n45.json) retains 32
unfinished degree-four requests: 2 at n=42 and 10 each at n=43,44,45.
It preserves the original input IDs and hashes the two existing n=42
certificate candidates, which remain unverified. They should be checked
before deciding whether new elimination is necessary. The inventory is not
a frozen execution protocol; no scientific remote job was launched.

The separate local 64 GiB degree-five continuation remains active. These
software controls do not change the status of the search for LFD at least 6.
