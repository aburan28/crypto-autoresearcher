# K11 input replay preparation failure

On 2026-10-17, the first invocation of
`python3 experiments/EXP-ICPERF-018b0c/implementation/check.py --out experiments/EXP-ICPERF-018b0c/inputs/independent_replay.json`
exited 1 after the target schedule and both positive controls had passed. It
raised `KeyError: 'gzip_bytes'` at `verify_arm` while checking the first natural
formula. The emitter had stored the compressed SHA-256 and raw byte count but
had not included the redundant compressed byte count expected by that verifier.
No independent replay output file was written by this attempt. It was a checker
metadata interface error, not a SAT or point relation observation.

The correction creates a temporary verifier view whose `gzip_bytes` is read
from the existing compressed file; it leaves all prepared target, positive,
formula, and XCNF bytes intact. The second invocation with the same command
exited 0 and reported `targets_checked: 8`, `positives_checked: 2`, and
`formulas_checked: 64`. Its complete replay record is `independent_replay.json`.
Neither invocation launched a solver.

The first two independent Sage attempts also exited before importing Sage:
the managed launcher overrides `DOT_SAGE` and writes its lazy-import cache to
`/Volumes/SSD990/cryptanalysis/.sage-build-tmp/runtime/cache`, which was
outside this session's default write sandbox. The observed exception was
`PermissionError: [Errno 1] Operation not permitted` while creating a cache
temporary file. Passing a local `DOT_SAGE` value did not affect that launcher.
The unchanged `sage -python` command then ran with approved filesystem access
and verified eight targets and 32 raw channels. Its output is
`sage_replay.json`. This was an access failure, not a mathematical result.
