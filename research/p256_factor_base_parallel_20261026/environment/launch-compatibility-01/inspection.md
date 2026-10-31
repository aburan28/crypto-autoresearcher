# Prospective F2–F8 launch compatibility inspection

Task `TASK-20261026-7f2e09`; archive owner `TASK-20261026-54bcce`.

The checkpoint stat-only repair introduces no detected conflict with the selected frozen source pins. All seven canonical/file protocol hashes match the historical freeze receipts, selected source/input/analysis bytes match their pins, and the recorded interpreter matches the executable bytes currently on disk. **F3 nevertheless has a definite static pre-launch refusal: its frozen source-hash map is empty.** The inspected recipes also leave process/checkpoint obligations for a later genuine release unresolved. No scientific execution or release was performed or certified.

## Bound source and method

The dispatch binds branch `research/p256-pass2-checkpoint-20261026` at `616878bcf0c8a749f38dd3ad0dbb1153478d4010`, with main base `6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad`. All seven protocols pin scientific source `de1f9bbe50801ba5cccbe915b7aece2a0ea5c5ff`. Root supplied that inputs were committed/pushed and the archival owner was bound before dispatch. No fetch, commit, push or other Git mutation was performed here.

I read the full handoff and `AGENTS.md`, its literature/observation rules, the lab/protocol operational documentation, repository `route` guidance and `ops` profile, the selected launch documentation, seven frozen JSON protocols, runner guards and common helper. Independent standard-library code parsed JSON/AST and checked byte identity against read-only Git objects. Thirty-four Python files were AST-parsed without importing them. `result.json` enumerates exact source paths, hashes, text/AST exposure and hash-only historical input reads. No external scientific literature assessment was needed for this operational question; no novelty or mathematical conclusion is made.

The native inherited Codex model binding remains unprobed. The requested `review-adversarial` policy on the handoff is not represented as canonical scientific-review admission. There was no model swap, extra agent, sibling inspection report read, official ledger decision or correctness claim.

## Definite refusal

**F3 — the frozen map is empty.** `tracks/f3/protocol.json:566` has `extensions.source_sha256: {}` and lines 567–572 name `run.py`, `oracle.py`, `analysis.py`, `export.py` and `curve-record.json`. `tracks/f3/run.py:402–405` computes those five hashes and raises when the expected map is empty or mismatched. The helper import/call is later, at lines 417–419. Thus the unchanged F3 package would refuse before the checkpoint gate and before scientific output even if authentication and a genuine matching release were later supplied. This is a source-derived prediction, not a launch that was attempted.

A later correction must be an additive prospective protocol version with the exact map and a newly bound freeze/release hash; this inspection did not edit the frozen record. The previously observed successful schema/freeze receipt does not establish launcher admission.

## Release-contract gaps

**F4/F5/F7 need a concrete outer watchdog.** Their protocols set `execution.timeout_seconds: 120` and explicitly call the watchdog a host guard (`f4/protocol.json:483,506`; `f5/protocol.json:282,305`; corresponding F7 fields). F4's runner and F5/F7's identical `panel_io.py` apply a 2-GiB address-space limit but contain no timer/timed subprocess/deadline. The inspected reproduction/preparation commands invoke Python directly. The literal recipes therefore do not enforce the promised deadline. A later root supervisor may supply it; none was available or tested here. F2/F3 contain 115-second panel alarms and F6/F8 contain 112-second panel alarms, set after gate admission. F3/F6/F8 additionally promise a 120-second external infrastructure watchdog. Those alarms do not demonstrate an outer supervisor or bound pre-launch checkpoint work.

**F4's application checkpoint declaration is unresolved.** `f4/protocol.json:484–492` declares `policy: application`, interval 60 seconds, grace 10 seconds and `manifest_sha256` restore validation. No periodic checkpoint timer, restore argument/path or restore-manifest validation was located in the selected runner. Its extension at line 636 and `REPRODUCE.md:38` instead say there is no in-place row resume and any restored process uses a fresh attempt. Per-case JSON writes and the S3 pre-launch backup gate do not by themselves demonstrate the declared application checkpoint fields. Before genuine release, root needs prospective reconciliation or a concrete external implementation. This is an operational contract gap, not an observed checkpoint loss or mathematical result.

## Exact CLI and release paths

All paths below are relative to the study directory. `--out` and `--seed` are required for every runner. A path argument remains relative to the invoking working directory; each default is built from the runner's own track/study path.

| Track | Seed | `--protocol` | Default release | Internal panel timer |
| --- | --- | --- | --- | --- |
| F2 | 2026102602 | accepted; track `protocol.json` | `tracks/f2/phase-b-release.json` | 115 s |
| F3 | 2026102603 | accepted; track `protocol.json` | `tracks/f3/release.json` | 115 s |
| F4 | 2026102604 | accepted; track `protocol.json` | `tracks/f4/phase-b-release.json` | absent |
| F5 | 2026102605 | no argument; fixed track `protocol.json` | `runtime/releases/TASK-20261026-26de77.json` | absent |
| F6 | 2026102606 | accepted; track `protocol.json` | `tracks/f6/phase-b-release.json` | 112 s |
| F7 | 2026102607 | no argument; fixed track `protocol.json` | `runtime/releases/TASK-20261026-59f4c9.json` | absent |
| F8 | 2026102608 | accepted; track `protocol.json` | `tracks/f8/phase-b-release.json` | 112 s |

Parser references: F2 `run.py:129–132`; F3 `run.py:433–436`; F4 `run.py:400–403`; F5/F7 `panel_io.py:48,149–151`; F6 `run.py:393–396`; F8 `run.py:426–429`. Existing per-track recipes follow these differences. A uniform added `--protocol` would be rejected by F5/F7, and one assumed release basename would point at the wrong defaults. These asymmetries are not defects when the native contract is followed. All inspected default/documented release paths and `tracks/f2` through `tracks/f8` run directories are absent locally.

## Source/interpreter and helper compatibility

`runtime/checkpoint_gate.py` is byte-identical to the scientific source pin, SHA-256 `50359bb34063e97b6804c16e97624add872b0cc359df68776aacecc5e9e44039`. The checkpoint script at the dispatch has SHA-256 `de5d922d7b38a14d16843901b5fb182434ff8fdd1b3a81085e66c49ce2dc8f1f`. Its base-to-dispatch diff adds `file_stat` and replaces the state-hash and untracked-size stat calls (`scripts/checkpoint.sh:69,201,305`). The gate dispatch at line 496 and helper's real `bash scripts/checkpoint.sh gate` call at `checkpoint_gate.py:55` remain intact. The script itself is not in the selected frozen scientific pin sets; its operational stat repair therefore does not itself fail those selective pin checks. No shell behavior was exercised here.

The requested `/workspace/dickson-solver/.venv/bin/python` exists and resolves to `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`. Its file SHA-256 is the frozen `fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`. Current unqualified `python3` resolves to the same executable and hash. This was file/path inspection only; the pre-existing `Python 3.12.14` version string was not independently reprobed. Future PATH/dependency availability remains a separate runtime fact.

Enforcement differs by runner. F2/F4 verify selected committed source/helper and actual interpreter before the gate. F3 also requires the missing explicit map. F5/F7 compare selected track-source bytes to the pin and hash inputs, but record helper/interpreter identity after the gate without comparing the interpreter digest to the frozen one (`panel_io.py:60–80,97–99`). F6/F8 record source/interpreter identity after the gate without a pre-gate comparison to the frozen instrument (`f6/run.py:71–82,407–410`; `f8/run.py:47–54,440–443`). Both refuse optimized `-O` execution. No current identity mismatch was found. Root's existing pre-launch byte checks in `RESUME.md:26–27` remain necessary custody evidence; metadata recording alone is not a refusal guard.

The shared helper checks authorization booleans, task, canonical frozen protocol hash and before-data filing, then calls the actual gate under a lock and requires `.last-push` (`checkpoint_gate.py:18–67`). It does not validate a separate source manifest/checkpoint-reference field supplied by a release. Its lock serializes the gate only, ending before panels run. Root must enforce F5→F7 and F6→F8 sequencing and the one-process worker limits already stated in `RESUME.md:36–37`. No concurrency violation was observed because no panel ran.

## Gate state and limits

The supplied current context says the user approved S3 disclosure, the actual gate still fails because supported token/profile transport is missing, and no experiment or Phase B release exists. This inspection did not read credentials or rerun that gate. The older `RESUME.md:17–22` and freeze archive still say consent is pending; those historical statements were preserved and must not be mistaken for the later supplied approval. The stat repair and this report provide neither authentication nor a successful checkpoint receipt.

No scientific module was imported, no `--help` path was executed, and no arithmetic panel, pilot, benchmark, actual gate/upload, export or mathematical computation was performed. AST success and matching bytes establish syntax/identity only. They do not prove dependency availability, arithmetic correctness, resource-guard effectiveness, checkpoint restore behavior, output integrity or scientific validity. No post-data review or official promotion is claimed. Only `inspection.md` and `result.json` were written in this assigned directory; root owns publication and any prospective follow-up.
