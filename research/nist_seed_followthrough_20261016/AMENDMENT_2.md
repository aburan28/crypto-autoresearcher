# Isolated full X9 counting run

Recorded before cloud execution. The 20-position local P-256 shard consumed
315.36 seconds in 15 PARI point counts while host load exceeded five times its
14 logical CPUs. The main `PROTOCOL.md` target and criteria are unchanged.

Use one isolated x86_64 Ubuntu EC2 `c7i.8xlarge` instance (32 vCPUs, 64 GiB),
in us-west-2, with 12 concurrent Python/PARI workers and 100 consecutive
candidate positions per immutable shard. The six distinct stream endpoints
are those in `count_x9.py` and `targets.json`. Run every shard from position
one through its last published anchor. A failed shard remains a separate
failure record and is retried under a new attempt suffix; a row with
`INDETERMINATE` does not become rejected. Keep all GP version, count duration,
input hashes, stdout/stderr, and the instance configuration/identity in a
campaign record. Recheck every published anchor and the 11 selected-root
skips. No hypothesis status changes during counting.

The EC2 instance uses an official Ubuntu 22.04 AMI, IMDSv2, a reused
restricted SSH group and an SSM-only role. Terminate it after results are
retrieved; instance-initiated shutdown terminates it after 12 hours as a
machine/cost guard. Current verified us-west-2 on-demand price is USD 1.428
per instance-hour (AWS Pricing API, 2026-10-16), so the 12-hour ceiling is
USD 17.136 before EBS and transfer. The guard is not a research sample cap:
if unfinished, preserve partial shards and plan a bounded continuation. Do
not silently infer anything from unavailable cloud access, interruption or
timeouts. Public repository inputs may be fetched; do not send credentials
to the instance.

The original local `ellcard` shard and its failed predecessor remain as
independent controls. The rejected large-`tors` `ellsea` pilot in
`FAILED_TORS_PILOT.md` is an implementation limit, not a candidate screen.
