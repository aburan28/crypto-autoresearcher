# Run report — EXP-CSIDH-999626

This is an observation-only execution report. It records what the frozen Stage 0–1 successor produced and does not assign evidence strength, promote a claim, change a hypothesis, or change experiment status.

## Identity and custody

- Experiment: `EXP-CSIDH-999626`
- Hypothesis: `H-CSIDH-73e6ab`
- Goal: `GOAL-CSIDH-001`
- Successor task: `TASK-20261011-883597`
- Approval: `DEC-20261011-c28952` for execution custody; the scientific contract remains `DEC-20261006-3cccf4`.
- Plan: `experiments/EXP-CSIDH-999626/trial-plan-v2.json`
- Plan SHA-256: `e4336c1437525dbc02b53a3680ab13336a084a41fefae8686cca47c47dc454f8`
- Executor authority commit: `e66fddc083cc28726282956d28de1ec7eb7ecea2`
- Owner/epoch: `executor-csidh-999626` / `1`
- Runtime recorded by receipts: Linux, Python 3.11.17, runtime-lock SHA `2e527af61020a126a4d55a2be57e7874d7633cc46e80e5e79cb723e8a60c2edd`.
- The working tree also contained unrelated untracked user artifacts; none were staged for the run-record commit.

The supervisor was launched with the narrow safety-approved outer command below. The container image lacked PyYAML, so the existing host PyYAML tree was mounted read-only; this is an execution-environment detail, not a scientific input.

```text
docker run --rm -e PYTHONPATH=/opt/hostsite \
  -v /Users/adamburan/.pyenv/versions/3.12.8/lib/python3.12/site-packages:/opt/hostsite:ro \
  -v /Volumes/SSD990-2/.codex/worktrees/3ffc/crypto-autoresearcher:/Volumes/SSD990-2/.codex/worktrees/3ffc/crypto-autoresearcher \
  -v /Volumes/SSD990-2/crypto-autoresearcher/.git:/Volumes/SSD990-2/crypto-autoresearcher/.git \
  -w /Volumes/SSD990-2/.codex/worktrees/3ffc/crypto-autoresearcher \
  crypto-ci-python:20261008 /usr/local/bin/python3 tools/experiment_execution.py run \
  --plan experiments/EXP-CSIDH-999626/trial-plan-v2.json \
  --owner executor-csidh-999626 --epoch 1
```

## Trials

| Trial | Run | Started UTC | Return/check | Recorded status | Run artifacts |
|---|---|---:|---:|---|---|
| `stage0-memcap-freeze` | `RUN-CSIDH-8a996d` | 19:31:48.379 | 0 / 0 | `output_validated` | [run directory](../../runs/RUN-CSIDH-8a996d/) |
| `stage1-memcap-census` | `RUN-CSIDH-fc6b43` | 19:31:52.888 | 0 / 0 | `output_validated` | [run directory](../../runs/RUN-CSIDH-fc6b43/) |

The requested count was 2; both trials completed and both checker outputs validated. The receipts recorded no timeout, crash, missing dependency, or reconciliation condition. The supervisor's final summary reported `required=2`, `output_validated=2`, `remaining=0`, `waiting_on_dependencies=0`, `needs_reconciliation=0`.

## Frozen parameters and controls

The run used `p=419`, `disc=-419`, `n=4`, the two twin enumeration routes, labels `M=2` and `M=M_free`, G levels 1 and 2, the blind-control instrument, and the forced-`N=1` nearby-object control. No quantum algorithm, CSIDH-512 figure, Magma path, Sage path, or Bedrock path was selected. Seeds were not declared by this deterministic implementation; the receipts and raw results are the complete machine outputs.

Stage 0 produced `S0-FREEZE-OK` and wrote the preregistered predictions, protocol freeze, and worksheet note. Stage 1 produced the recorded label `O-SEPARATES`, with both route counts equal to 9, `M_free=4`, and `reconstruction_ok=true`.

## Recorded values

The following are copied from the machine-readable stage artifacts; the graph uses these values directly and does not add samples or recompute an uncertainty interval.

- Main ratio at `G=1`: `C(1,2)/C(1,M_free) = 8/4 = 2.0`.
- Main ratio at `G=2`: `C(2,2)/C(2,M_free) = 16/8 = 2.0`.
- Blind ratio at `G=1`: `C_blind(1,2)/C_blind(1,M_free) = 4/4 = 1.0`.
- Blind ratio at `G=2`: `C_blind(2,2)/C_blind(2,M_free) = 8/8 = 1.0`.
- Forced `N=1` control ratio: `C(1,2)/C(1,M_free) = 2/2 = 1.0`.
- Route A/B agreement: `N_route_A=9`, `N_route_B=9`.
- No spread or uncertainty was recorded; each listed value is one deterministic instance (`n=1`).

The quantitative graph is [graph.svg](graph.svg), with its editable data in [graph-data.json](graph-data.json). The PDF embeds the same graph and cites both run IDs.

## Missing or non-applicable data

The runner did not record CPU time, a per-stage wall-time measurement, a random seed, or a statistical uncertainty estimate. Those fields are therefore reported as missing rather than inferred. The run receipts contain the exact start and finish timestamps and artifact hashes. This report does not turn the deterministic ratios into a general performance or cryptanalytic claim.
