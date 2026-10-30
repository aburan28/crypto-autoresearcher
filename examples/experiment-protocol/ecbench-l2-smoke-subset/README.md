# Worked example: protocol, export and review on a public ecbench fixture

The three record shapes of `docs/experiment-protocol.md`, filled in on real
data: a 24-record subset of the public ecbench smoke session
`ECBS1hc931106fd275` that aburan28/crypto ran on EKS on 2026-10-19
(`crypto:research/eks_crypto_validation_20261019/artifacts/session`, 72
records, all verified, pod audit 54/54 replays reproduced). The subset keeps
the arms `rho-neg` (reference), `bsgs-neg` (candidate) and `rho-neg-aa`
(A/A control) on both workloads, one warmup and three rounds each; the other
six arms are dropped so the example stays small. `session/session.json`,
`plan.json`, `spec.json` and `host.json` are byte copies, so their
`records_sha256` describes the full session, not this subset.

| file | what it is |
| --- | --- |
| `protocol.json` | an `experiment.protocol/v1` record, frozen (`freeze.protocol_sha256`), written for this subset |
| `session/` | the ecbench session subset (`ecbench.session/v1`) |
| `export.json` | `tools/experiment_protocol.py from-ecbench session --protocol protocol.json` |
| `reviews/REV-*.json` | an `experiment.review/v1` record filled from the export's rows |

What it is not: a preregistration (the protocol was written after the run,
and says so in `links.note` and in the prediction's `sample_status:
in_sample`, role `calibration`), a measurement of wall time (every row earned
L0 against a required L2, so every `wall_valid` is false), or a claim about
either method. The review's finding that the A/A arm shares seeds with the
reference, so its spread is zero and measures determinism rather than seed
variance, is what the example is for: a record a tool can check, read by a
runner that did not produce it.

```sh
python3 tools/experiment_protocol.py validate protocol.json
python3 tools/experiment_protocol.py check-export export.json --protocol protocol.json --verify-files
python3 tools/experiment_protocol.py flow export.json
python3 tools/experiment_protocol.py review validate reviews/REV-*.json
```

`tests/test_experiment_protocol.py` rebuilds the export from the session and
holds it equal to the committed one.
