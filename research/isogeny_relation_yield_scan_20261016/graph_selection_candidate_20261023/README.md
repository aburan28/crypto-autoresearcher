# Candidate graph discovery selector

`discovery_select.py` is an implementation candidate for the prespecified
post-discovery selection rule. It is not an approved `EXP-*` contract and has
no scientific discovery data. A Coordinator must freeze this source, the
8,206-arm schedule, a complete trial plan, and an independent control-index
root commitment before any scientific target stream is run.
The approved plan's `source_sha256` must bind this selector, the schedule, and
the control-index commitment before the run; the revealed root itself is
checked against that committed hash.

The selector requires **every** scheduled arm to have a supervisor receipt
with `output_validated`, zero driver and checker exit codes, and matching
artifact hashes. It also reads the graph attempt and prepared input, checks
curve/model/generator identity against the schedule, verifies the fixed target
quota and rank prefixes, and hashes every `(alpha,beta)` pair. All arms in a
stratum must share the same coefficient sequence; all arms must share the
committed base, target, and verifier roots. Commitment-file digests must be
constant within each stratum and distinct between P29 and P37 because each
file binds that stratum's different archived graph hash. A graph or coordinate
transport arm must have a dependency on its scheduled reference and a checker
receipt confirming targetwise transport comparison. Missing, censored, failed,
or mismatched arms stop selection; none is scored as zero or replaced.

For each main base and stratum, selection takes the prescribed top and bottom
eight P29 or four P37 vertices by useful-target count (the quota is constant
within a stratum), breaking ties by smaller `j`. It unions these vertices
with source index 0 and 16 P29 or eight P37 indices drawn without replacement
from a separately committed 256-bit root, independent of yields. It emits the
three main-base confirmation arm keys for the union. It does not pick finalist
ECDLP curves or calculate confirmation intervals; those require fresh targets
and a later prespecified stage.

The control commitment is a JSON object with schema
`ectd.graph-control-index-commitment/v1`, `schedule_sha256`, and
`control_root_sha256`. The root file contains 32 bytes as 64 hexadecimal
characters and is revealed only after its hash is frozen. An eventual
approved launch can call:

```text
python3 discovery_select.py --repo REPO --schedule DISCOVERY_ARMS_JSONL \
  --plan APPROVED_TRIAL_PLAN --control-commitment COMMITMENT_JSON \
  --control-root CONTROL_ROOT_HEX --out NEW_SELECTION_JSON
```

The CLI writes once. It deliberately refuses the current candidate schedule
without its complete approved plan and 8,206 validated run receipts. The
three synthetic tests cover the full 8,206-row schedule shape, tie breaking,
complete coverage, paired-stream rejection, supervisor hash binding, and
tamper rejection. They are software controls and carry no relation-yield
estimate.
