# Continuing the four factor-base leads

29 October 2026. Implemented software and correctness controls only. **Zero new
scientific trials; zero p=4099 natural targets generated.** This continues the
[four-track worklist](../prime_field_leads_20261028/PLAN.md), preserving its
original workload and evidence distinctions. No scientific status changes.

## Changes that can now be checked

`src/crypto_autoresearcher/index_calculus/target_relations.py` snapshots `Mz=b`
and appends verified target rows as `v*z - t*k = offset`. It tests whether the
unit vector on k belongs to the augmented row space, returning weights on the
original base and target rows. Each successful certificate is checked against
those original rows and `[k]P=Q`. Individual target rows are also tested against
the original base kernel, so single-row and combined recovery remain separate.
Zero target coefficients are retained without declaring them target information;
inconsistent rows leave the system unchanged. No full-base-rank test is used.

The additive `target_completion.py` collector keeps the historical curve,
base and cubic law, with the already implemented x=0 completion. It constructs
sources from `[t]Q`, sets `source_scalar=0, target_coefficient=t`, verifies each
witness through the existing separate arithmetic lane, and folds known anchors
with their signs. Anchors come only from the frozen `[s]P` preprocessing schedule.
The collector retains witness events, all statuses/digests and recovery prefixes,
then completes its entire declared census even after a recovery. Public-anchor
and signed-base target coincidences are flagged rather than omitted.

`hash_public_target` fixes UTF-8 encoding, domain, curve UID, index and counter:
`domain|curve_uid|decimal_index|decimal_counter`. SHA-256 maps to x modulo p;
the first rational canonical-y r-subgroup point is selected. The launcher flushes
every hash attempt, including rejections before counter exhaustion. It generates
no scalar label. The domain defaults
to `prime-field-leads/20261028/target/v1`. A finite counter bound is required.
This recipe is implemented and tested on p=101; the eight proposed p=4099
targets remain ungenerated. Exhaustion is a failed target-generation attempt,
not a successful empty target set; its exception is retained by the launcher.

The optional F1 `--profile-stages` path records scalar-chain and polynomial
construction, relation and elementary operators, kernel elimination,
off-diagonal projection, operator restriction, character extraction, cubic
factoring, coordinate validation, lifting, subgroup checks, sign enumeration,
fingerprinting and the separate finite oracle. Each event carries CPU/wall ns,
status, case and stratum; failures are flushed before propagation. The
`solver_total` event includes its inner phases: **do not sum it with them**.
Control cases have separate events. RSS is a process-lifetime high-water mark
(KiB on Linux), not phase-local memory. Clocks include instrumentation overhead,
have no isolation guarantee, and are diagnostic, not a measured cost bound.
FLINT's internal elimination-operation counts remain unavailable.

The frozen F1 `core.py`, `exterior.py`, inputs, derivation and old results are
unchanged. The profiled adapter copies orchestration and calls the same
arithmetic primitives. Tests compare the entire returned result, including
certificates and operation counters, with the frozen path at depths 2 and 4.
The 560-dimension guard runs before either path allocates operators.

## Validation and delivery

The [test log](validation/software-tests.txt) records 164 passing tests and nine
existing optional-msolve skips. It covers the existing IC solver/harvester,
offset logic, partial cancellation, target certificates, complete F1 states and
signed solutions, Prym replay, checkpoint and relay behavior. Additional final
focused checks and exact source/environment identity are in
[validation.json](validation.json). Tests use p=101 and p=127 software fixtures;
their outcomes are not new results on the proposed p=4099 or P-256 panels.

The p=101 target collector test independently checks every projected equation
as a public point identity and rejects changed target labels. The affine
combination tests enumerate all solutions over F5/F7, checking target uniqueness
while base variables remain free. A wrong final public target is rejected.
No calibrated profile or scientific export is produced by these software tests.

PR #2665 previously failed its artifact-size check on the 86,927-byte PNG preview.
Regenerating that derived preview at 90 dpi produces 51,905 bytes. The SVG,
retained data and historical PDF are unchanged; the vector report remains the
full-detail view. No artifact policy or required check is weakened.

## What each lead does next

| Lead | Available implementation | Next scientific work, still unexecuted |
|---|---|---|
| Partial relations | Original-row cancellation certificates and exact Delta scorer | Consume naturally generated signed F4 rows, compare with the dense oracle, charge collection plus elimination |
| Prym x=0 | Paired collector and independent complete branch replay | The fixed two-curve/two-arm 9,175,040-branch comparison; score new equations and old-kernel syndromes |
| Dickson depth 4 | Complete extractor, 560 guard, stage events, full finite oracle | Fixed P-256 positive/public targets; retain costs and unknown/failure cases; no toy-to-P-256 scaling inference |
| Natural targets | Public hash recipe, target-aware collector, single and combined certificates | Bind the two preprocessing spaces and eight independent public targets; replay the complete target branch stream independently before research interpretation |

Scientific launch syntax (not executed here):

```sh
PYTHONPATH=src:. python research/prime_field_factor_base_20261028/run_targets.py \
  --inputs FROZEN_TARGET_CELLS --protocol NEW_FROZEN_PROTOCOL \
  --release COMMITTED_RELEASE --out FRESH_OUTPUT_DIRECTORY
PYTHONPATH=src:. python research/p256_factor_base_parallel_20261026/tracks/f1/driver.py \
  --inputs research/p256_factor_base_parallel_20261026/tracks/f1/inputs.json \
  --protocol NEW_FROZEN_PROTOCOL --release COMMITTED_RELEASE \
  --max-dimension 560 --profile-stages --out FRESH_OUTPUT_DIRECTORY
```

Target input cells embed `fixture`, `source_order`, `preprocessing_rows` and
`target_indices`; global fields freeze `target_domain`, `max_target_counters`
and `multipliers`. The release parameters are
`{"stopping_rule":"full census regardless of recovery","include_zero":true}`.
The profiled F1 release adds `"profile_stages":true` to `{"max_dimension":560}`;
the uninstrumented launch retains its original parameter shape. Changed sources
require fresh source/input/interpreter locks, not the October 26 releases.
Both CLIs call the existing real admission/checkpoint helper before outputs or
target generation. Direct target collection accepts only marked p<=211 software
fixtures unless the admitted native launcher supplies its capability.

The managed executor still reports no secrets, runtime variables or outbound
identities; presence-only inspection finds no checkpoint environment token,
default token file or AWS CLI. The already recorded canonical checkpoint
failure remains applicable. No repeated gate retry, credential lookup/bypass,
scientific process or background worker was started. See the linked
[operational problem](../../problems/prime-field-lead-checkpoint-transport.md).
New prospective protocol/native ownership/supervision bindings also remain
necessary. These software interfaces are not a scientific execution release.

## Sources and limits

Internal sources retrieved/read: the October 28 plan and implementation/source
notes; original F1 `core.py`/`exterior.py`; Prym `relations.py`, `independent.py`,
`collect_width.py` and the retained diagnostics. Prior primary-source retrieval
of Petit–Kosters–Messeng (PKC 2016), sections 2.4 and 3.1–3.5, and its digest
remain in `prime_field_factor_base_20261028/validation.json`. Its relation-solver
and linear-algebra costs still apply. This continuation makes no novelty,
speedup, natural-target-recovery or end-to-end attack claim. Target branch
completeness still needs a separate replay implementation before interpreting
scientific outputs; checking each accepted row alone does not prove completeness.

The earlier retained-diagnostics graph, historical F1 preparation diagram and
Prym result graphs were checked for relevance and left unchanged: there are no
new scientific observations to add. The [editable diagram](diagram.svg),
[report source](report.typ) and inspected [PDF](report.pdf) document the new
software paths and outstanding execution boundary.
