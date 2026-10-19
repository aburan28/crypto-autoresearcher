from pathlib import Path
import hashlib,json,os,subprocess,sys,yaml

REPORT=Path(__file__).resolve().parents[1];ART=REPORT/'artifacts';REVIEW=Path('/workspace/review-lean-evidence')
initial=json.loads((ART/'controls-results.json').read_text())
followup=json.loads((ART/'followup-results.json').read_text())
bindings=json.loads((ART/'input-bindings.json').read_text())
runtime=json.loads((ART/'runtime-input-bindings.json').read_text())
def put(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
read_details=[]
def read(path,depth):read_details.append({'path':str(path),'depth':depth})
read('skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md','full')
for p in ['AGENTS.md','ledger/handoffs/TASK-20261018-695548.yaml',
 'research/lean_review_evidence_20261018/repair-plan.yaml','research/lean_review_evidence_20261018/repair-inputs.json',
 '.claude/skills/route/SKILL.md','.claude/skills/review-evidence/SKILL.md',
 '.claude/skills/review-evidence/references/lean-review.md','.claude/skills/formal/SKILL.md',
 '.claude/skills/research-visuals/SKILL.md','formal/README.md','formal/targets/README.md',
 'formal/smoke/lakefile.toml','formal/smoke/lean-toolchain','formal/smoke/lake-manifest.json',
 'formal/smoke/CryptoResearch/Smoke.lean','orchestration/formal/workspace.py',
 'orchestration/formal/targets.py','orchestration/formal/__init__.py','orchestration/__init__.py',
 'research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/report.md',
 'research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/replay_frozen_cli.py',
 'research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/final_controls.py',
 'research/lean_review_evidence_20261018/machine/gate-repair-selftest.log']:
    read(REVIEW/p,'full displayed')
for p,depth in [('agents/validator.md','displayed responsibilities, review-plan and blind-task sections, then lines 100 onward'),
 ('templates/research-records.md','review_attestation section excerpt'),
 ('tools/check_review_independence.py','matched excerpts; exact bound copy executed for declaration check'),
 ('orchestration/formal/mathcode.py','first 110 lines'),('orchestration/formal/models.py','first 70 lines'),
 ('research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/checks.json','partial displayed output; concatenated read was truncated'),
 ('research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/review_attestation.yaml','partial displayed output; concatenated read was truncated')]:read(REVIEW/p,depth)
semantic_frozen={'README.md','tools/proof-gate.sh','tools/selftest/run.sh','tools/AuditAxioms.lean',
 'tools/lean/README.md','tools/lean/proof-gate.sh','tools/lean/selftest/run.sh',
 'orchestration/formal/cli.py','orchestration/formal/receipts.py','orchestration/formal/lean_worker.py',
 'tests/test_lean_live.py','research/lean_retrospective_20261018/summarize.mjs',
 '.agents/skills/review-evidence/SKILL.md','docs/skill-routing.md'}
for b in bindings:
    depth='hash/Git-blob comparison and retained byte snapshot'
    if b['path'] in semantic_frozen:depth+='; content displayed or same-byte executable exercised'
    if b['path']=='docs/skill-catalog.json':depth+='; primary_intents/topics excerpt displayed'
    if b['path'].startswith('.claude/skills/'):depth+='; canonical same-revision content displayed from review checkout'
    read(Path('/workspace/lean-review-repairs')/b['repository']/b['path'],depth)
for p in runtime:
    read(Path('/tmp/TASK-20261018-695548/runtime-v2')/p['path'],
         'exact Git blob retained and hashed; imported verifier dependencies executed where used; no semantic claim for unimported modules')
read(Path('/tmp/TASK-20261018-695548/runtime-v2/formal/AxiomAudit.lean'),'full displayed; real Lean executed')
put(ART/'sources-read-details.json',read_details)
sources=sorted({r['path'] for r in read_details})
attestation={'review_attestation':{
 'task_id':'TASK-20261018-695548','joints_owned':['J3-repair-workflow-boundaries'],
 'sources_read':sources,'source_read_details':'artifacts/sources-read-details.json',
 'read_sibling_reports':False,'permitted_prior_J3_report_read':True,
 'blind_from_respected':None,'blind_rederivation':False,'independent_session':True,
 'subagents_used':False,'producer_source_edits':False,'official_status_changes':False,
 'verdict':'breaks','verdict_scope':'Frozen repair candidate at exact revisions in repair-inputs.json; owned joint only',
 'protocol_deviations':[
  'No mathematical blind rederivation assigned; real replay is not called a blind derivation.',
  'Repository /usr/local/bin/python3 path absent; used handoff-provided CPython 3.12.14 venv.',
  'First git archive setup stalled and was interrupted; no output used; exact individual Git blobs were read instead.',
  'First deletion hook did not inject a mutation; retained as an ineffective control and replaced by a new real-worker postcheck deletion control.',
  'First strict-summary positive had zero project-namespace theorem count and was conservatively rejected; retained, then a new positive with a nonempty project audit passed.',
  'Report PDF uses installed ReportLab renderer; source and inspected page rendering retained.'
 ],
 'limitations':[
  'No full historical project rebuild, serial producer verification, live CI or console autoresearch entrypoint exercised.',
  'No external lean4checker fresh recheck or dependency-binary authentication; core-only controls use installed pinned Lean.',
  'Pre/post binding cannot detect restored transient edits; no such guarantee inferred.',
  'Strict receipt consistency is not run authentication or mathematical source-claim fidelity.',
  'Coordinator message reporting a scoped-summary format limitation was received; no serial-run artifact was read, and the local zero-count conservative rejection is independently reproduced.'
 ]}}
with (REPORT/'review_attestation.yaml').open('x') as f:yaml.safe_dump(attestation,f,sort_keys=False)
checks={
 'schema':'lean-review.repair-checks.v1','task_id':'TASK-20261018-695548','joint':'J3-repair-workflow-boundaries',
 'verdict':'breaks','input_files':len(bindings),'all_snapshot_and_git_hashes_match':all(b['matches_bound_git'] for b in bindings),
 'scope':{'plan_commit':'d47080d59f4b5b54ffd29df46d8089c5665689c5','review_revision':'aaccd2f5d0a801fd73209e2a51b587efbda3ee5e',
 'autoresearcher_revision':'2951f9b77d96606820be80bf61ee0d539cfbb4dd'},
 'findings':[
  {'id':'R-F1-source-coverage','status':'holds_scoped','evidence':'artifacts/controls-results.json',
   'observed':'12 independent real gate cases across shared and both consumer entrypoints match expected pass/failure signatures; nested ownership and explicit tool exclusions checked.'},
  {'id':'R-F2-receipt-consistency','status':'holds_scoped_with_conservative_format_limit',
   'evidence':'artifacts/followup-results.json','observed':'Actual nonempty-audit positive receipt and active Node wrapper pass; all 15 field attacks plus stale imported helper reject. Zero-count project audit is conservatively rejected even when a separate exact theorem audit succeeds.'},
  {'id':'R-F3-persistent-input-binding','status':'breaks','evidence':'artifacts/hidden-counterexample.json',
   'observed':'Ordinary imported-source mutation/create/delete and verifier/config/audit/target changes invalidate with exit 3. A configured hidden local source helper False→True remains absent from manifests, yields exit 0, and passes strict receipt_errors.'},
  {'id':'R-F4-adapted-skill-fidelity','status':'partial_mismatch','observed':'Review/fidelity/authentication distinctions are accurate; complete-local-input wording exceeds hidden-directory coverage.'}
 ],
 'initial_controls':initial['controls'],'initial_receipt_controls':initial['receipt_controls'],
 'followup_controls':followup['controls'],'followup_receipt_controls':followup['receipt_controls'],
 'initial_control_corrections':{
 'cli-deleted-imported-source':'No mutation injected; not counted as evidence of deletion handling. New followup deletion ran real worker then removed imported source and returned 3.',
 'receipt-baseline':'Control.good lies outside project-auditor namespace; zero project theorem count triggers strict rejection. New CryptoResearch.Control.good positive passes.',
 'summary-wrapper-positive':'Same zero-count issue; new followup positive returns 0.'},
 'hidden_strict_receipt_errors':followup['hidden_receipt_errors'],
 'not_claimed':['proof of False','kernel unsoundness','any producer theorem refuted','run authentication','scientific status change'],
 'sources_read_details':'artifacts/sources-read-details.json'}
put(REPORT/'checks.json',checks)
report='''# Independent review of Lean workflow repairs

TASK-20261018-695548 · J3-repair-workflow-boundaries · 2026-10-18

**Own-joint verdict: breaks.** The three original reproductions now reject within their ordinary input layouts. A remaining persistent imported-source change escapes the repaired CLI when Lake configures a hidden local source directory. The strict receipt validator also accepts that resulting receipt. This is a source-binding defect; Lean checks the changed proposition, and no proof of False or theorem refutation is asserted.

## Authority and exact candidate

The authority is the committed handoff and repair plan published at `d47080d59f4b5b54ffd29df46d8089c5665689c5` before this dispatch. All 32 manifest entries match both frozen `/workspace/lean-review-repairs` bytes and their bound Git blobs. Candidate revisions are CryptoLean `617b0a5433516796f9ea9d48109b8eb135f92dfc`, crypto `f1052053f01e7db23692e4ab4824f4df5a7bf29b`, cryptanalysis `93b5ce33fd5b3794e3fbc6b548986cb2ae72ccca`, autoresearcher `2951f9b77d96606820be80bf61ee0d539cfbb4dd`, and review `aaccd2f5d0a801fd73209e2a51b587efbda3ee5e`. Exact supporting runtime files were individually copied from that review revision; loaded repaired CLI/worker/receipt bytes agree with the manifest. See `artifacts/input-bindings.json`, `runtime-input-bindings.json`, and retained source snapshots.

I did not author these repairs. Only the permitted prior J3 report, its checks/attestation excerpts and two reproducer scripts were read. No J1/J2/J4 report or Coordinator synthesis was read. No subagent, commit, producer edit or scientific status change occurred. Every Lean command ran under this task's `/tmp/TASK-20261018-695548` tree. The original autoresearcher formal workspace was neither written nor used as a Lean working directory.

## Observation: repaired original controls

| Boundary | Fresh positive control | Fresh negative control | Result |
| --- | --- | --- | --- |
| Shared and both consumer gates | Configured, unimported valid module passes; two theorems audited | Unconfigured good or false source: exit 1, FAIL_build_source. Configured false source: exit 1, FAIL_audit/sorryAx | 12/12 expected signatures |
| Gate ownership/exclusions | Outer project passes and lists only its own Root source | Separately discovered nested project with sorry fails its own audit | Declared boundary reproduced |
| CLI input binding | Ordinary valid named theorem: exit 0 | Imported False before mutation: exit 1; False→True after version query: exit 3 | Original failure repaired |
| Persistent input-set/software changes | Exact theorem checked by real worker | Add source; delete imported source after successful real audit; change target, audit, lakefile or scratch verifier: exit 3 | Tested changes invalidate evidence |
| Strict receipts and active summary wrapper | Actual CLI receipt with nonempty project and exact-name audit: accepted, wrapper exit 0 | Fifteen isolated identity/status/boolean/forbidden/log/version/input attacks and a stale helper reject; original combined forgery makes wrapper exit 1 | Original contradictory acceptance repaired |

Raw commands, stdout/stderr, build/audit logs and before/after source copies are in `artifacts/controls/`, `gate-receipts/`, and `control-sources/`. Every case is enumerated in `checks.json`; `controls-results.json` preserves the original attempts, and `followup-results.json` preserves the discriminating follow-ups. The controls use actual pinned Lean 4.35.0 for gate projects and Lean 4.22.0/Lake 5.0.0 for the dependency-free CLI projects, not fake Lean output or test-suite assertions.

## Breaking artifact: configured hidden local source

At repaired `orchestration/formal/receipts.py:27`, `workspace_inputs` removes every directory whose name starts with a dot. Its docstring describes dependency/build exclusions, while the skill promises complete local source/configuration coverage. Lake supports a normal local library with a hidden source directory:

```toml
[[lean_lib]]
name = "Helper"
srcDir = ".hidden"
```

`formal/.hidden/Helper.lean` defines `CryptoResearch.Control.P : Prop := False`. The unchanged target `CryptoResearch/Test.lean` imports Helper and states `theorem good : P := by trivial`. The frozen CLI returns exit **1** on those initial bytes. A wrapper around the real `lake env lean --version` subprocess changes only the helper's P from False to True immediately after the query. All later build and axiom checks still run real Lean.

The repaired CLI now returns exit **0**, `machine_verified`, with no infrastructure failure. The target's before/after SHA-256 is identical. The complete recorded `workspace_inputs` omits `.hidden/Helper.lean`; the strict `receipt_errors` returns **[]**. The matching hidden-layout positive also returns 0, so the result is not explained by an unsupported build or failed control. This helper is a configured local source, not a dependency binary or transient restored edit. The mutation remains present after verification.

The load-bearing artifacts are `artifacts/hidden-counterexample.json` and `artifacts/controls/followup-hidden-{positive,false-before,loadbearing-mutated}/`. Each contains source snapshots and raw receipts. The unchanged target has SHA-256 `420c3f280e415d8438f56afd1b4d6c9172bbd5cfe7b963d2b08808249df52a4f`. Lean proves the changed True statement; the evidence cannot be bound to the original complete local input set.

## Comparison, fidelity and limits

The adapted review-evidence/formal skills correctly require fresh exact-name checks, independent semantic fidelity, explicit source inventory, and separate treatment of consistency, run authentication and mathematical validity. The active Node summary delegates to `orchestration.formal.receipts`, propagates failure and states its authentication/fidelity limit. Those claims are supported by the exercised commands. Its complete-local-input promise is too broad for the blanket hidden-directory pruning, so workflow fidelity is partial/mismatch and review outcome is needs_revision for this candidate.

The validator also conservatively rejects a successful exact-theorem receipt whose project audit has zero theorems in its selected namespace. My first `Control.good` positive reproduced that rejection; a new `CryptoResearch.Control.good` receipt with a nonempty project audit passed. This is false rejection, not acceptance of a bad proof. The Coordinator separately reported a scoped zero-axiom audit-format rejection; I received that message but did not read the serial-run artifacts or count them as independent evidence. The validator recognizes only its main-workspace nonempty audit string, so alternative valid project-audit formats need a new expressly supported contract.

One original deletion hook did not fire because the worker's default runner retained the original subprocess function. Its exit 0 is preserved and excluded from deletion evidence. The follow-up invokes the original real worker, confirms successful machine checks, then deletes the imported helper; it returns exit 3. Initial receipt/summary positive failures are also preserved, with their zero-count reason. The first setup tried a repository-documented Python path absent in this runtime, then used the handoff venv. A git-archive setup stalled and was interrupted; exact individual blobs supplied the runtime instead. These failed attempts were not rewritten.

No full historical rebuild, live CI, proof generation/MathCode, installed console command, external lean4checker fresh check or dependency-binary authentication was performed. Pre/post hashes do not establish absence of transient edits. Actual source-read paths and depth, including hash-only bindings and truncated reads, are in `artifacts/sources-read-details.json` and the attestation. No mathematical or performance canonical graph changes: this is a workflow boundary review. The diagram/PDF describe only the tested instrument behavior.

## Next discriminating correction and reproduction

Bind hidden local proof/configuration sources, or reject unsupported local-source layouts before checking them; reserve exclusions for expressly declared infrastructure. A new committed candidate must pass the ordinary controls and the hidden positive, reject the original hidden False baseline, and invalidate the persistent False→True helper mutation with exit 3 and no successful verification object. Keep the current failed candidate and logs immutable. Receipt format support should similarly receive a new positive/negative control rather than accepting arbitrary strings.

The retained scripts are `artifacts/bootstrap.py` (failed setup preserved), `bootstrap-v2.py` (exact runtime setup), `review_controls.py`, and `followup_controls.py`. Run the successful setup and the two control scripts in that order with `/tmp/lean-review-venv/bin/python`, fresh scratch/output names, and `PATH=/workspace/.elan/bin:$PATH ELAN_HOME=/workspace/.elan XDG_CACHE_HOME=/workspace/.cache PYTHONDONTWRITEBYTECODE=1`. They declare every source and command; existing output paths intentionally refuse overwrite. Archival publication belongs to TASK-20261018-95bdb1.

Full top-level `review_attestation` wrapper: [review_attestation.yaml](review_attestation.yaml). It assigns only J3-repair-workflow-boundaries and records **breaks**; this is not a whole-claim approval vote.
'''
with (REPORT/'report.md').open('x') as f:f.write(report)
print(json.dumps({'report':str(REPORT/'report.md'),'sources_read':len(sources),'verdict':'breaks'}))
