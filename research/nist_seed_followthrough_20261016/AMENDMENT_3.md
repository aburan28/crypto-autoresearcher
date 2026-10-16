# Modal fallback after EC2 account refusal

Recorded before any Modal scientific process. The one EC2 launch in
`AMENDMENT_2.md` returned `Blocked`: the AWS account is not recognized as a
valid account. The dry run had passed. There is no EC2 instance to recover or
terminate. This is an access failure and says nothing about the candidates.

The same complete six-stream point-count grid and acceptance rules in
`PROTOCOL.md` remain frozen. Use the existing Modal workspace to run each
100-position shard in a Debian container with `pari-gp` and `pari-seadata`.
The container receives only the exact public candidate file, target file,
prior census order files and `count_x9.py`, each checked by SHA-256 before the
count. Twelve one-CPU, 2 GiB containers are the initial concurrency guard;
P-521's GP stack maximum remains 1024 MiB. Each count retains the 600-second
watchdog; each shard has a 7200-second service timeout. One pilot batch checks
P-256 positions 1–20, its published anchor and P-521 positions 1–10 against
local controls. Advance to all 221 full-grid shards if the pilot is complete
and the anchor and shared positions agree. Preserve any failure or timeout as
an indeterminate result, not a rejection. A 12-hour client guard protects
resources and does not change the target grid or its scientific inference.

Modal's public price on 2026-10-16 was USD 0.0000131 per physical CPU-core
second and USD 0.00000222 per GiB-second, before included usage. Twelve
continuously active one-core/2-GiB containers for 12 hours would cost at most
about USD 9.09 at these rates, excluding any other billed service or rate
change. This is a resource ceiling, not a sample limit. The exact measured
usage and all partial results will be recorded separately. Modal execution
does not change the criteria or claim tier.
