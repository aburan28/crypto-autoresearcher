# Native AES laboratory adapter

This is a new **engineering study and proposed experiment family**, separate
from the existing GOAL-AES-001/002/003 trial queues. It grants no permission to
run those held arms and changes no official scientific status. The user's
current request authorizes building and exercising this separate public
synthetic-input instrument.

The program is the compiled Rust `aes-discover` binary in the companion
`cryptanalysis` repository. Its exact frozen command card and first raw results
are published there. This adapter does not introduce a second Python cipher,
statistical evaluator or data generator. The literature assessment, source
receipt and nine falsifiable follow-up cards are in
[`research/aes_open_angles_20261017`](../../research/aes_open_angles_20261017/REPORT.md).

```sh
# From this repo, with the companion checkout and compiled binary available:
bash experiments/aes-distinguisher-lab-20261017/run-native.sh \
  /path/to/cryptanalysis \
  /path/to/cryptanalysis/tools/aes-discover/target/release/aes-discover \
  /path/to/NEW-output-directory
```

The output parent's directory must exist. The new output directory must not.
The adapter delegates only to the committed native command card and inherits
its explicit seeds, sampling plan, control gates, write-once outputs and binary
hash receipt. A trial is not claimed until its raw directory and process exit
record exist. Existing official programs continue through their original `run`
entry point and admission controls.

The first bounded suite ran in the companion repository; it has 41 successful
commands, 12 discovery/validation families and eight fresh validation keys per
family. This is a link to those observations, not a new independent run:
[source branch](https://github.com/aburan28/cryptanalysis/tree/codex/aes-distinguisher-research/experiments/aes-distinguisher-lab-20261017).
No autoresearcher official trial plan was executed or marked complete here.

Remaining integration work is explicit: exact SAT/UNSAT certification, full
published quartet algorithms, complete toy hull enumeration, learned-model
training and independent campaign admission. A
planning or software PR does not discharge these requirements.

[`crypto-integration.patch`](crypto-integration.patch) preserves the original
prepared integration. The current user authorized standalone application; the
native mirror is now applied in `crypto`, with eleven implementation/Cargo files
matching the companion and fourteen native tests passing. It is delivered in
[crypto PR #2105](https://github.com/aburan28/crypto/pull/2105). The required root
suite fails before tests on 26 unchanged-base compile errors; exact evidence
and remaining obligations are tracked in
[the problem record](../../problems/aes-lab-conductor-and-campaign-admission.md).
Nine native backlog proposals retain their missing implementation and admission
requirements. This integration copies the cipher sources and lockfile rather
than adding a separate implementation.
