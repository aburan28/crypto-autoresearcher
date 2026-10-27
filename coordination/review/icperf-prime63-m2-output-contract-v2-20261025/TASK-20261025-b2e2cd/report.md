# Independent Validator report — TASK-20261025-b2e2cd

Date: 2026-10-25  
Session: `01a17478-c9be-7150-b1a0-84fb816cfec6`  
Role/policy: independent Validator, `review-adversarial`, `xhigh`  
Review plan: `REVIEW-ICPERF-PRIME63-M2-OUTPUT-CONTRACT-V2-20261025`

## Outcome first

The exact hash-bound engineering snapshot satisfies joints O1, O2 and O3 on
the tested no-science fixture scope. I independently reproduced two
`output_validated` canned terminals and four `invalid_output` producer
controls through the real `tools/experiment_execution.py::execute_trial`
path. I then added one-field diagnostic-digest, claim-identity and
certificate mutations; all three were also `invalid_output`. Direct custody
inspection found no absent, empty, malformed, mismatched or undeclared member
accepted in the tested cases. Both accepted fixtures have
`attack_claimed: false`, `result.certificate.kind: none`,
`scientific_conclusion: null`, and `published: false`.

This is not a scientific result. No solver or scientific trial was launched,
and nothing here supports an ECDLP cost, speedup, solve, decomposition,
certificate, experiment approval or research-status transition.

There is one independent review-mechanics BREAKS condition, separate from the
candidate claim: the frozen review plan cannot pass the current
`tools/check_review_independence.py` while this attestation remains honest and
complete. The plan names this same task in `blindness.lifted_for` but omits the
checker-required `blindness.rationale`; additionally, the checker always
rejects a blind re-deriver whose complete `sources_read` later contains a
`blind_from` path, even after the plan's deliberate same-task seal-then-compare
lift. I did not edit the frozen plan, hide the post-seal reads, or weaken the
attestation. The exact reproducer and required disposition are below.

## Blind seal and read discipline

The Phase 1 blind derivation was verified before any candidate source, test,
fixture report, archive member, old bridge, or historical run was read:

- seal commit: `932e5d00147cc206a5a15144f5001d928c3d5259`
- committed path:
  `coordination/review/icperf-prime63-m2-output-contract-v2-20261025/TASK-20261025-b2e2cd/blind-derivation.yaml`
- committed SHA-256: `117dc867ae55748ee904f0e52455283e89f68545446e93c96a215d3a3aba7bf0`
- working-tree SHA-256 at lift: the same value
- reachability: seal commit was an ancestor of the checkout and was visible
  on `origin/codex/icperf-output-contract-batch-20261019`
- seal commit changed path: only the blind derivation, added with commit
  message `seal TASK-20261025-b2e2cd blind derivation before candidate reads`

Phase 1's exact source order is itself sealed in the blind artifact. It was:

1. `.agents/skills/review-evidence/SKILL.md` (procedural adapter).
2. `.claude/skills/review-evidence/SKILL.md` (canonical procedure).
3. frozen review plan.
4. source handoff `ledger/handoffs/TASK-20261020-f237a2.yaml`.
5. frozen `experiments/EXP-ICPERF-515ae3/trial-plan.json`.
6. `tools/experiment_execution.py`, completed in ranges after a truncated
   whole-file display.

After the seal verified, Phase 2 read sources in this order:

1. The two review-evidence skill files, for procedure only.
2. Seal commit metadata and the sealed blob bytes.
3. Frozen review plan.
4. Validator handoff `ledger/handoffs/TASK-20261025-b2e2cd.yaml`.
5. Snapshot receipt
   `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-ac3c38/archives/TASK-20261020-fa096d/snapshot-receipt.json`.
6. The ten bound Git-tree blobs at snapshot commit `61d8e90…`, initially
   only to recompute their hashes.
7. Candidate `README.md`, `output-contract.json`, and `input_manifest.json`.
8. Candidate `output_contract.py`.
9. Candidate `execute.py`, then `check.py`.
10. Candidate `fixture_supervisor.py`.
11. Candidate `test_output_contract.py`.
12. Bound `fixture-report.json`.
13. The outer fixture archive member table, then its safely extracted
    members in a disposable root.
14. All six archived `execution-receipt.json` files.
15. For both positive cases: `command.txt`, `launch.json`,
    `environment.json`, `diagnostic/receipt.json`, `raw-result.json`,
    `manifest.yaml`, inner tar member tables, and `diagnostic/fixture.txt`.
16. Negative checker stderr and the missing-output receipt detail.
17. The four old-bridge bytes by hash at pinned commit `d7c8cdc…`, then their
    hashes at the review snapshot/current checkout.
18. The historical run-root inventory and read-only supervisor status.
19. `tools/check_review_independence.py`, its relevant tests, and the
    review-attestation template needed to construct the final attestation.

No sibling reviewer report was read. No memory or rollout summary was used.

## Bound snapshot and custody

The snapshot receipt declares commit
`61d8e90af4d7d4c34d80065009cd9aac552d47e2`, parent
`0a30d55bb96e6fe940f54fead27bc15d22469161`, and tree
`f0d6b06187e100701f5f3f3bdfb435938e55bbd4`. All three match Git. The commit
is visible on `origin/codex/icperf-output-contract-batch-20261019`.

The separate snapshot receipt is tracked unchanged at current HEAD, with
SHA-256 `fcb59e21d275ea8dd27927905e313f83856723f99a2661cf97f0c6fcf9352090`.
I recomputed all ten content hashes from the bound Git tree, not from the
producer report:

| Bound path | SHA-256 | Receipt match |
|---|---|---|
| `fixture-custody.tar.gz` | `973fc389ab0f50d250dc2cf707bb00c86771385759296807fb6ef2c2452dd263` | yes |
| `fixture-report.json` | `75ab6c67cd0e35e6b521433298c1d71a703ee38b48f0eb6a325662d214290263` | yes |
| `README.md` | `aeb62b936283174394c88e8ac8c34e94ee28a203bc96108a5190e512e637548f` | yes |
| `check.py` | `2377ad1256458eb624343793f38ae8495145942bd01b5ff57efcaa5efa96290c` | yes |
| `execute.py` | `68ecefbd8285f12cfdae2f6de4ea7ba95bd1d883fe02e39f4ca2fdb58af014b3` | yes |
| `fixture_supervisor.py` | `98d5c80039afba27b6576c7f67938d8b388737053b2a4cad0f85eeff914aafc7` | yes |
| `input_manifest.json` | `4b8cc361e77a4191e2b47fe44adcbc36c34e5ebc9d5a335138e5315a04435009` | yes |
| `output-contract.json` | `4a9f6e634691dec5ebe692d905ec45729bf4f7be4c6d0574b710f5d3ff69336a` | yes |
| `output_contract.py` | `ed01f0f0e8eae66019daa5ddb65cfd4b3ac7ade5ecbdf02f6af9d08fa4ec6421` | yes |
| `test_output_contract.py` | `a53e648b32578b93cd912c0e94154d1d7a950dca9c7c0ece97699df8058e9c98` | yes |

The fixture report's source commit
`9ec1c183d1260dae2a5835aafb5b98894cf154fa` is an ancestor of the snapshot,
is visible on the same origin branch, and contains the exact eight source
bytes listed in the report. The current working copies used for independent
execution were byte-identical to snapshot `61d8e90…`. Fixed-input hashes also
matched:

- specification: `3e24c2c1df6451f39388082a6b9594c6a6491f86c3075e1bf5878d6093792a30`
- trial plan: `08f32f02a191dfd16f5342540716a327da73f5091528bac07cf5ee77cdb7cbc9`
- supervisor: `26d1e08f6a126625ccd0d037c88df1bd6c419898ebf54562cfdb887a61bdb4a8`

The old bridge's four pinned bytes at commit `d7c8cdc22b1b82ae9faaa08f690781bd17f70bb4`
match the source handoff exactly:

- `README.md`: `2dbc2c0a0203b213bbef7a8d35839adc8411933643b257def42dc62ea01f0c65`
- `contract.py`: `41b15b9a07c6889e19c5bbf2181c660642138303eceeb47399d1fd9018bbc6d4`
- `test_contract.py`: `6a12018cafe2b00d37c55a7b596584bf4996948d1fef2efedd55c471a4fd7e3d`
- `validation.log`: `ec1cc1037e08307744cc0cd9e9d638f66a2bb2a6442af25a1c1dac58a38c7d7d`

Three old-bridge working-tree files differ because the earlier follow-up
commit `c2fb442cf51f761be2621df2f13c559f12ccbb99` changed them on 2026-10-19;
`validation.log` is unchanged. The v2 producer commits did not touch any old
bridge path, do not execute the bridge, and pin its introduction commit rather
than silently consuming the later bytes. This is recorded as provenance
context, not a v2 break.

## Blind derivation comparison

The sealed derivation correctly predicted:

- exact frozen run root
  `experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88`;
- the only plan-declared top-level outputs, nonempty `manifest.yaml` and
  `raw-result.json`;
- all eight supervisor-generated custody files;
- nested `diagnostic/receipt.json` and `diagnostic/raw.tar.gz` bytes;
- the manifest-to-raw and raw-to-diagnostic digest chain;
- fixed plan/run/trial/claim/source bindings;
- `attack_claimed: false` and certificate kind `none` for canned work;
- missing, empty, changed-digest and unlisted-member negative classes;
- checker rejection of wrong plan/claim/source bindings and false success;
- infrastructure errors being distinct from mathematical evidence.

The candidate resolved the Phase 1 uncertainties as follows:

- `raw-result.json` contains experiment/run/trial/plan identities,
  `diagnostic_receipt_sha256`, `diagnostic_raw_tar_sha256`, `cell_stops`,
  `verification_status`, `attack_claimed: false`, and a null scientific
  interpretation.
- `manifest.yaml` is canonical JSON that is also valid YAML. It links to
  `raw-result.json` and its SHA-256; the raw result links to both diagnostic
  byte objects. The fixed diagnostic paths are declared in
  `output-contract.json` and used by the checker.
- The inner allowlist has exactly one ordinary file, `fixture.txt`; ordering,
  duplicates, non-files, path traversal, size, and SHA-256 are checked.
- The canned-positive case labels `random-m2` as `exited` with response
  `canned_positive`, but leaves `attack_claimed` false and provides no
  scientific interpretation or certificate.
- Fixture authority calls the real `execute_trial` directly only inside a
  temporary root after verifying a reachable commit contains all exact source
  bytes. It does not call `run_plan` or `authorize`, and it does not claim that
  fixture authority is production admission.
- Emitter and checker share `output_contract.py`; that agreement alone would
  be self-consistency, so I separately recomputed archive and digest relations
  with standard-library code and independently introduced adversarial
  mutations. Those independent checks agreed for the bounded scope.

One Phase 1 expectation was intentionally conditional: the supervisor may
complete missing envelope fields, but a manifest already passing the run
schema is returned unchanged. Both archived positive receipts record
`manifest_completion.action: unchanged`. Their manifests are therefore not
required to contain every optional completion field listed in the blind note.

## Joint verdicts

### O1 — HOLDS

Both canned terminal classes emit the two nonempty plan-declared outputs and
the two diagnostic byte objects. For each positive archive I independently
verified:

- every execution-receipt artifact digest against the exact extracted bytes;
- receipt/launch/plan/run/trial/claim identities;
- diagnostic receipt SHA-256 from `raw-result.json`;
- diagnostic tar SHA-256 from both receipt and raw result;
- the exact one-member tar allowlist, size and member digest;
- the manifest's SHA-256 link to `raw-result.json`;
- manifest command equality with `command.txt`;
- manifest code commit equality with the fixture authority commit;
- `attack_claimed: false`, certificate kind `none`, and null scientific
  interpretation.

Archived positive receipt SHA-256 values:

- bounded censor: `3229ddeae1b56083efb1df3ae3a60e3b1a010502cbdc1633dda094e2980e2235`
- canned positive: `4cf1981af21577471f8a614a58cc710e2ff433e9a45f685b94714efd4ae4b1f1`

The exact archived inner member hashes are:

- bounded censor `fixture.txt`:
  `9dc0cb943d468803c0ae62c3d2f9b30718fe4815f928a900b22929c3318abefc`
- canned positive `fixture.txt`:
  `5eb46d4ca2ed9e629a6ec4620b85efd70665d5520794836ed2304ec4ed40c7c5`

No O1 breaking artifact was found.

### O2 — HOLDS

Archived custody and fresh independent execution agree on all six stated
cases:

| Case | Archived | Fresh | driver rc | checker rc |
|---|---:|---:|---:|---:|
| bounded censor | `output_validated` | `output_validated` | 0 | 0 |
| canned positive | `output_validated` | `output_validated` | 0 | 0 |
| missing top-level output | `invalid_output` | `invalid_output` | 0 | null (supervisor schema refusal) |
| empty top-level output | `invalid_output` | `invalid_output` | 0 | 1 |
| producer changed-digest fixture | `invalid_output` | `invalid_output` | 0 | 1 |
| unlisted raw member | `invalid_output` | `invalid_output` | 0 | 1 |

Fresh execution-receipt SHA-256 values, using snapshot commit `61d8e90…` as
fixture authority:

- bounded censor: `37ddcb504fbe61f8cd68d773af5aabf2e164aec2fb3208a7c190773bb65c5e07`
- canned positive: `81fa41347db8d208092a9e96d72d5babf9d72dec8a1daebe4ee743bb3220967b`
- missing output: `ab94db37e3a7c40cb70514f9d5259f842970a5f2eca35ffebc720baed9f4517e`
- empty output: `d34304b28fe40818f868690460301736933f6aebd24f8939dbc608748ff3a6b4`
- producer changed-digest: `9effe53a41d3e8ad54877887f03499e975424010c466fcc9c6ec20c8880d7472`
- unlisted member: `4b218b91b0fb2764f4100312a9316346b1a2545720027228e90cad7a25c50ef2`

The producer's changed-digest fixture replaces all of `raw-result.json` with
`{}` rather than varying one digest field. I therefore added three narrower
real-supervisor cases:

| Independent mutation | Status | driver rc | checker rc | Receipt SHA-256 | Failure signature |
|---|---:|---:|---:|---|---|
| only diagnostic receipt `raw_tar_sha256` changed | `invalid_output` | 0 | 1 | `deeeb415a998b33d774f046b6b673317c6c49dd434581922f89ecd59df0e5ccb` | `diagnostic archive mismatch` |
| only diagnostic receipt `claim_epoch` changed | `invalid_output` | 0 | 1 | `23d35cc3dde884bc8652825b96dbe74d1b5d38700f3cf99dee7baba7231e7d94` | `plan/claim/source binding mismatch` |
| only manifest certificate kind changed to `forged` | `invalid_output` | 0 | null | `47a65edc1f2d152574e1ef38528cf35510b4a2fb73e2b834573a42d5579fd69f` | run-schema refusal before checker |

A separate coherent false-claim mutation changed raw and manifest attack
fields, updated the manifest's raw-result digest, and supplied a forged
verified certificate. `check.py` still returned 1 because exact rederivation
rejected the altered `raw-result.json`.

The historical run root was inspected read-only. It still has neither
`manifest.yaml` nor `raw-result.json`; standard supervisor status reports one
`needs_reconciliation`, zero `output_validated`, and
`measurement_complete: false`. Git status was unchanged before and after the
check. No historical file was repaired or overwritten.

No O2 breaking artifact was found.

### O3 — HOLDS

All ten snapshot hashes match the separate receipt. The source commit is
reachable and contains exact source bytes. The input manifest's fixed
specification/plan/supervisor hashes match, and its source hashes match the
bound snapshot. The old bridge introduction commit and four declared hashes
exist exactly as pinned; v2 commits do not modify those paths.

Static inspection found no solver import or solver invocation. The only
`subprocess` calls in production fixture source are `git merge-base` and
`git show` for source-commit reachability and byte equality. The canned driver
has only bounded-censor/canned-positive modes and writes under the passed
disposable run root. Production admission is not invoked or bypassed:
fixture-only authority is explicitly substituted around `execute_trial`,
while the production `run_plan`/`authorize` gates remain separate.

All accepted manifests record the actual canned command and a reachable source
commit. All accepted receipts say `published: false` and
`scientific_conclusion: null`. No artifact claims a solver success,
certificate, prospective approval, or ECDLP performance inference.

No O3 breaking artifact was found.

## Proves-too-much controls

| Control | Expected failure signature | Observation | Result |
|---|---|---|---|
| historical invalid output | historical run remains invalid and unrepaired | both required files absent; status `needs_reconciliation` | passed |
| missing or empty required output | supervisor returns `invalid_output` | both archived and fresh controls did | passed |
| changed digest or undeclared member | checker/supervisor rejects | broad producer mutation, exact one-field digest mutation, and extra member all rejected | passed |
| canned certificate | certificate remains none; no admission | positive manifests use kind `none`; forged kind rejected; production admission untouched | passed |

None of the known-false conclusions was accepted.

## Commands and observed results

The principal read-only or disposable commands were:

```text
git show 932e5d...:<blind-derivation> | shasum -a 256
git diff --exit-code 932e5d... -- <blind-derivation>
git merge-base --is-ancestor 932e5d... HEAD
# observed: sealed and working bytes 117dc867...; commit on origin branch

git show 61d8e90...:<each of ten paths> | shasum -a 256
# observed: all ten hashes equal snapshot-receipt.json

tar -tzvf <bound fixture-custody.tar.gz>
tar -xzf <bound fixture-custody.tar.gz> -C <disposable-root>
# observed: six case roots, no symlinks; expected diagnostic extra only in the unlisted-member negative

PYTHONDONTWRITEBYTECODE=1 python3 <independent stdlib custody checker>
# observed: independent_custody_checks PASS for all six archived roots

fixture_supervisor.run(<two modes and four faults>, source_commit=61d8e90..., capture=<disposable-root>)
# observed: two output_validated, four invalid_output

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  research/icperf_prime63_m2_output_contract_v2_20261020/test_output_contract.py
# observed: Ran 6 tests; OK. One ResourceWarning from validate_ledger.py opening duplicate_run_ids.yaml was non-fatal.

PYTHONDONTWRITEBYTECODE=1 python3 tools/experiment_execution.py status \
  --plan experiments/EXP-ICPERF-515ae3/trial-plan.json
# observed: historical run needs_reconciliation; measurement_complete false

PYTHONDONTWRITEBYTECODE=1 python3 <three custom execute_trial mutation cases>
# observed: single-digest, wrong-identity and forged-certificate all invalid_output
```

The custom scripts used only Python's standard library, the exact candidate
source and the standard supervisor. They were executed under
`/private/tmp/icperf-validator-b2e2cd.gRguRM/`; they did not alter tracked
source or the historical run.

## BREAKS reproducer — frozen review-plan/tool incompatibility

This BREAKS condition concerns the review procedure, not O1/O2/O3:

```text
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_review_independence.py \
  --plan coordination/review/icperf-prime63-m2-output-contract-v2-20261025/review-plan.yaml \
  --expected-plan-sha256 4e16fd1185f161103ee425f59a3b4927b5a74a27fe5561e9336ddfa644cfed83 \
  --reports coordination/review/icperf-prime63-m2-output-contract-v2-20261025/TASK-20261025-b2e2cd/attestation.yaml
```

The frozen plan has `blindness.lifted_for: [TASK-20261025-b2e2cd]` and a
human-readable `rule`, but no `blindness.rationale`; the checker requires the
latter whenever `lifted_for` is nonempty. The checker also treats every later
candidate read in this task's complete `sources_read` as a permanent blind
leak. It does not implement the plan's declared same-task temporal sequence:
seal blind derivation, commit/push, deliberately lift, then compare.

I cannot truthfully make this green within the allowed write scope. Omitting
the six post-seal candidate reads, or asserting that no `blind_from` path was
ever read, would make the attestation false. Editing the frozen plan or tool is
also outside this task. The Coordinator/operator should preserve this failed
check, then use an additive procedural correction supported by the checker
(for example a separately declared blind-phase task plus scoped lift) before
treating the round's independence gate as mechanically satisfied.

Observed result on the final attestation: return code 1 with exactly two
problems—missing `blindness.rationale`, and one consolidated finding that the
complete read list contains all six post-seal `blind_from` paths.

## Limitations

- This review covers exact source/fixture engineering behavior only.
- The positive data are canned; they provide no evidence about a solver,
  relation yield, rank, extraction, discrete log, cost or speedup.
- The fixture emitter and checker share one contract module. Independent
  source review, direct archive recomputation and adversarial mutations reduce
  the self-consistency risk only for the exact tested contract and cases.
- Fresh top-level hashes differ from archived hashes because commands,
  temporary roots, timestamps, source authority commit and gzip metadata are
  intentionally fresh. Status classes, identities, semantic links and inner
  fixture member hashes were the matched quantities.
- No global backend or resolved model identifier was exposed to this
  Validator. The attestation records only the operator-supplied session,
  policy and effort; it makes no unsupported backend claim.
- The frozen independence plan/tool mismatch remains unresolved and prevents
  a mechanically passing round despite the three joint verdicts holding.

## Handoff state

Source and historical artifacts were not modified. No commit was created.
The operator must validate, preserve the failed independence output, commit
these exact review files, release the task, and archive them under
`TASK-20261025-6d007d` before any Coordinator acceptance decision.
