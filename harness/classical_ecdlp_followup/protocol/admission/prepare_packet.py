#!/usr/bin/env python3
"""Prepare exact unapproved drafts and prospective approval bytes.

This command never writes the repository, records approval, grants a claim,
executes C++ diagnostics, or fabricates an admission result. Copy source/
and draft/ into the repository and publish them before invoking preapproval.
Only a Coordinator may later archive the preview bytes after a genuine pass.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

MODULES = {'projection_scale_0': ['L9-scale'], 'projection_scale_1': ['L9-scale'], 'projection_scale_2': ['L9-scale'], 'decoder': ['L9-decoder'], 'basis_audit': ['L4-audit']}
FEATURES = {'projection_scale': ['full_point','constant','kummer_x','x_mod_7','power_residue_5','x_hash_7'], 'decoder': ['x_mod_7','power_residue_5','x_hash_7','constant']}
PART_COUNT = 256
VERIFICATION_PART_COUNT = 32
GENERATED = ('launch.json', 'execution-receipt.json', 'command.txt', 'environment.json',
             'stdout.log', 'stderr.log', 'check.stdout.log', 'check.stderr.log')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(root: Path, relative: str, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    return path


def artifacts():
    names = ['manifest.yaml', 'raw-result.json', 'parts-manifest.json']
    empty = []
    for name in MODULES:
        for stage in ('build', 'self-test', 'run'):
            for stream in ('stdout', 'stderr'):
                item = name+'-'+stage+'.'+stream+'.txt'
                names.append(item)
                empty.append(item)
        item = name+'-rescue.jsonl.gz'
        names.append(item)
        empty.append(item)
    for item in ['verification-manifest.json','verification-build.stdout.txt','verification-build.stderr.txt','verification-run.stdout.txt','verification-run.stderr.txt','verification-input-rescue.tsv.gz','verification-output-rescue.tsv.gz']:
        names.append(item)
        if item != 'verification-manifest.json': empty.append(item)
    for item in ['verification-check-build.stdout.txt','verification-check-build.stderr.txt','verification-check-run.stdout.txt','verification-check-run.stderr.txt','verification-check-input-rescue.tsv.gz','verification-check-output-rescue.tsv.gz','verification-replay.json']:
        names.append(item)
        if item!='verification-replay.json': empty.append(item)
    for i in range(VERIFICATION_PART_COUNT):
        item = f'verification-part-{i:03}.jsonl'
        names.append(item); empty.append(item)
    for i in range(PART_COUNT):
        item = f'rows-part-{i:03}.jsonl'
        names.append(item)
        empty.append(item)
    return names, empty


def prepare(args):
    lab, out = args.lab_root.resolve(), args.out.resolve()
    ids = json.loads(args.ids.read_text())
    prefix = args.source_prefix.strip('/')
    if args.check_ids:
        for ident in ids.values():
            subprocess.run([sys.executable, 'tools/allocate_id.py', '--check', ident], cwd=args.repo_root, check=True)
    out.mkdir(parents=True, exist_ok=False)
    source, draft, preview = out/'source', out/'draft', out/'preview'
    for p in sorted((lab/'src').glob('*')):
        if p.suffix not in ('.cpp', '.hpp'):
            continue
        target = source/prefix/'src'/p.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    for name in ('fixtures.tsv', 'public-targets.tsv', 'followup.json', 'fixture-certificate.json', 'target-custody.json', 'fixture-shards.json', 'excluded-pilot-fixtures.tsv'):
        target = source/prefix/'protocol'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(lab/'protocol'/name, target)
    for shard in sorted((lab/'protocol').glob('fixtures-shard-*.tsv')):
        target=source/prefix/'protocol'/shard.name
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(shard,target)
    for history in sorted((lab/'protocol').glob('fixture-history*.jsonl')):
        target = source/prefix/'protocol'/history.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(history, target)
    verifier_rel = prefix+'/protocol/admission/verify_candidates.cpp'
    target = source/verifier_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('verify_candidates.cpp'), target)
    driver_rel = prefix+'/protocol/admission/driver.py'
    target = source/driver_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('driver.py'), target)
    source_hashes = {p.relative_to(source).as_posix(): sha(p) for p in sorted(source.rglob('*')) if p.is_file() and p.suffix in ('.cpp', '.hpp', '.py')}
    input_hashes = {p.relative_to(source).as_posix(): sha(p) for p in sorted((source/prefix/'protocol').glob('*')) if p.is_file()}
    fixture_ids = [line.split('\t', 1)[0] for line in (lab/'protocol/fixtures.tsv').read_text().splitlines()[1:] if line.strip()]
    if len(fixture_ids) != 24 or len(set(fixture_ids)) != 24:
        raise ValueError('exact twenty-four-fixture follow-up required')
    fixture_meta=[]
    for line in (lab/'protocol/fixtures.tsv').read_text().splitlines()[1:]:
        if not line.strip(): continue
        fields=line.split()
        if len(fields)!=10: raise ValueError('fixture columns')
        fixture_meta.append({'id':fields[0],'stratum':fields[1],'p':int(fields[2]),'r':int(fields[7]),'N':int(fields[8])})
    lines=(lab/'protocol/public-targets.tsv').read_text().splitlines()
    if not lines or lines[0].split()!=['fixture_id','target_id','Qx','Qy','Qinf']: raise ValueError('target header')
    target_meta=[]
    for line in lines[1:]:
        if not line.strip(): continue
        f=line.split()
        if len(f)!=5 or f[0] not in fixture_ids or f[4] not in ('0','1'): raise ValueError('target row')
        target_meta.append({'fixture_id':f[0],'target_id':f[1]})
    if len(target_meta)!=192 or len({x['target_id'] for x in target_meta})!=192 or any(sum(x['fixture_id']==f for x in target_meta)!=8 for f in fixture_ids): raise ValueError('exact 192 globally unique public target identities / eight per fixture required')
    shards={}
    for index in range(3):
        name='fixtures-shard-'+str(index)+'.tsv'
        values=[line.split()[0] for line in (lab/'protocol'/name).read_text().splitlines()[1:] if line.strip()]
        if not values or len(set(values))!=len(values): raise ValueError('invalid fixture shard')
        shards[index]=values
    if sorted(x for values in shards.values() for x in values)!=sorted(fixture_ids): raise ValueError('fixture shards must be disjoint complete union')
    config_rel = prefix+'/protocol/admission/batch-config.json'
    config = {'schema': 'classical.ecdlp.followup-config.v1', 'experiment_id': ids['experiment'], 'run_id': ids['run'],
              'maximum_module_workers': 3, 'compiler_flags': ['-std=c++20', '-O2', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-Wconversion', '-Wshadow'],
              'watchdog_seconds': 3600, 'watchdog_reason': '3600-second operational subprocess backstop; not mathematical evidence',
              'fixtures': prefix+'/protocol/fixtures.tsv', 'fixture_ids': fixture_ids, 'fixture_meta':fixture_meta, 'public_targets':prefix+'/protocol/public-targets.tsv', 'target_meta':target_meta, 'verifier_source':verifier_rel,
              'modules': [{'name': name, 'kind':'projection_scale' if name.startswith('projection_scale_') else name, 'source': prefix+'/src/'+('projection_scale' if name.startswith('projection_scale_') else name)+'.cpp', 'tracks': tracks, 'features':FEATURES.get('projection_scale' if name.startswith('projection_scale_') else name,[]), 'fixtures':prefix+'/protocol/fixtures-shard-'+name[-1]+'.tsv' if name.startswith('projection_scale_') else prefix+'/protocol/fixtures.tsv', 'fixture_ids':shards[int(name[-1])] if name.startswith('projection_scale_') else fixture_ids, 'global_fixture_aliases': ['shared_basis_audit'] if name == 'basis_audit' else []} for name, tracks in MODULES.items()],
              'source_sha256': source_hashes, 'input_sha256': input_hashes,
              'scope': 'exploratory_toy_followup', 'attack_advantage_claimed': False, 'instance_witness_policy':'Conditional genuine discrete_log certificate iff independent public Jacobian verification confirms any candidate, including chance-control hits; no advantage claim.'}
    config_path = write(source, config_rel, config)
    source_hashes = {**source_hashes, config_rel: sha(config_path)}
    exp, goal, task, archive, batch = (ids[x] for x in ('experiment','goal','executor_task','archive_task','batch'))
    spec_rel = f'experiments/{exp}/specification.yaml'
    plan_rel = f'experiments/{exp}/trial-plan.json'
    queue_rel = f'coordination/goals/{goal}/batches/{batch}/dispatch_queue.json'
    handoff_rel = f'ledger/handoffs/{task}.yaml'
    archive_handoff_rel = f'ledger/handoffs/{archive}.yaml'
    goal_rel = f'ledger/goals/{goal}/goal.yaml'
    run_base = f'experiments/{exp}/runs/{ids["run"]}'
    scientific = {'id': exp, 'title': 'Classical ECDLP projection-scale, public decoder and basis-audit follow-up', 'goal_id': goal,
        'hypothesis_id': ids['hypothesis'], 'version': 1, 'designed_at': '2026-10-25',
        'scope': 'Twenty-four fresh public synthetic toy curves at 8/10/12 subgroup bits, 192 public targets, exact scaled projection diagnostics, a public-input approximate decoder, and a precisely scoped basis audit. No advantage or asymptotic claim.',
        'controls': ['Exact finite-r Kummer and constant/full-point entropy calibrations; sign-pair matched nulls', 'Fresh-curve x_mod_7 and fifth-power replication with 99+99 declared null draws', '2048 unlabelled training samples and512 fresh held-out calibration samples per kernel; no tuning on calibration', 'Paired model/exact prefix modes, fixed beam widths1/8, four public offset views, canonical scalar range and constant/hash controls', 'Independent Jacobian verification of every returned candidate using public points; no scalar truth input', 'Pins, AND, rational and characteristic-two exact polynomial certificate controls'],
        'metrics': ['Exact per-module JSONL observations and fixture identifiers', 'Constructor/evaluation counters with units',
                    'All control outcomes and failure/censoring classifications', 'Decoder training/held-out logloss/top1 accuracy, candidate lists and public equation verification', 'Pair/unary entropy, exact null values, fibre data and basis audit/certificate counts', 'Output bytes, complete row counts, per-module wall intervals and source/input digests'],
        'budget': {'policy': 'advisory', 'maximum_runs': 1, 'maximum_workers': 4, 'memory_gb': 12},
        'stopping_rules': ['Complete the one frozen24-curve/192-target batch and every declared finite coverage item.', 'Supervisor watchdog or actual process/memory failure is operational censoring, not scientific falsification.'],
        'invalidation_rules': ['Any failed mandatory calibration, changed hash, malformed row, missing track, truncated output or unreconstructable partition invalidates the affected batch.', 'No post-hoc scalar advice or uncharged inverse table may be described as a solver.'],
        'success_criterion': 'C-integrity: collect all three follow-up track outputs and controls with exact reconstruction, zero output-integrity errors and complete custody; no required anomaly or advantage.',
        'falsification_criterion': 'A concrete counterexample rejects only its explicitly stated finite identity or frozen candidate; operational failures and missing constructors have no mathematical negative interpretation.',
        'decision_impact': {'on_positive': 'Archive descriptive observations; separately identify a specific surviving construction for a fresh prospective study, without promoting an algorithm claim.',
                            'on_negative': 'Retain the exact counterexample or operational failure and repair the affected instrument/construction in a new additive protocol; do not close a whole lead.'},
        'input_bindings': {'fixture_manifest': {'path': prefix+'/protocol/fixtures.tsv', 'sha256': input_hashes[prefix+'/protocol/fixtures.tsv']},
                           'protocol': {'path': prefix+'/protocol/followup.json', 'sha256': input_hashes[prefix+'/protocol/followup.json']}, 'public_targets':{'path':prefix+'/protocol/public-targets.tsv','sha256':input_hashes[prefix+'/protocol/public-targets.tsv']},
                           'driver': {'path': driver_rel, 'sha256': source_hashes[driver_rel]}},
        'variable_ledger': {'independent': [{'name': x} for x in ('fixture','stratum','module','feature','target','prefix_mode','beam_width','basis_matrix')],
            'factors': [{'name': 'source_build', 'treatment': 'fixed', 'how': 'Exact source hashes and compiler flags are sealed in the batch configuration.'},
                        {'name': 'input_selection', 'treatment': 'fixed', 'how': 'Twenty-four fresh certified fixtures, all rejection history,192 public targets and generation/custody commitments are committed before measurement.'},
                        {'name': 'null_seed', 'treatment': 'fixed', 'how': 'Module RNG algorithms and finite seed domains are source-bound before execution.'},
                        {'name': 'truth_access', 'treatment': 'fixed', 'how': 'Entropy censuses use charged reference orbits; decoder training samples public unlabelled points and receives only public targets. Scalar truth is absent from the candidate and checker inputs.'},
                        {'name': 'host_load', 'treatment': 'measured', 'how': 'Concurrent wall intervals are descriptive only and are not compared as algorithm costs.'}],
            'comparisons': [{'id': 'C-integrity', 'arms': ['frozen follow-up'], 'differs_in': [], 'design': 'absolute'}, {'id':'C-prefix-mode', 'arms':['model','exact'], 'differs_in':['prefix_mode'], 'design':'one_factor', 'pairing':'Same fixture, feature, target, beam width, public offset views and tie seeds. Descriptive paired outcomes; no significance or advantage criterion.'}],
            'aa_not_applicable': 'Exact finite censuses and rational identities are deterministic. Floating entropy uses stated rounding/calibration tolerances. Wall time is descriptive, never a decisive metric.',
            'crosses_map': False},
        'prediction_provenance': [{'prediction': 'P-calibration', 'first_recorded_in': prefix+'/protocol/followup.json', 'written_at': '2026-10-25',
            'data_seen': [{'path': 'experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/observations.md', 'measured': 'Prior eight-curve pilot selected x_mod_7 and fifth-power follow-up; Kummer sign-matched calibration and finite common-basis failures were observed.'}],
            'sample_status': 'out_of_sample', 'overlap': 'Fresh curves and public target cohort; feature choices and decoder design were informed by prior pilot. Known calibration identities are references, not novel algorithmic predictions. Candidate source is truth-free; no OS-isolated blindness or performance advantage is claimed.'}],
        'interpretation_limits': ['Toy8/10/12-bit curves; this is not the original blinded12/14/16/18-bit solver cohort.', 'The multiview HMM/beam score is an explicitly approximate conditional-independence heuristic, not an exact scalar posterior.', 'Training, construction, all failed branches and public verification costs are charged; no rho comparison or advantage claim.', 'All null and ordinary observations retained; curves are replication units and targets share preprocessing.', 'No independent-session or formal proof validation; exact written basis arguments have stated model hypotheses.', 'No exponent, novelty or official scientific support/reject transition.']}
    draft_spec = {'experiment': {**scientific, 'status': 'review_required', 'frozen': False, 'approved_by': None, 'execution_authorized': False}}
    final_spec = {'experiment': {**scientific, 'status': 'approved', 'frozen': True, 'approved_by': ids['approval_decision'], 'execution_authorized': True}}
    write(draft, spec_rel, draft_spec)
    preview_spec = write(preview, 'specification.yaml', final_spec)
    names, empty = artifacts()
    trial = {'id': 'followup-batch', 'run_id': ids['run'], 'depends_on': [],
             'argv': ['python3', driver_rel, 'run', '--config', config_rel, '--run-dir', '{run_dir}'],
             'check_argv': ['python3', driver_rel, 'check', '--config', config_rel, '--run-dir', '{run_dir}'],
             'artifacts': names, 'allow_empty_artifacts': empty, 'memory_mb': 3072,
             'watchdog_seconds': 4200, 'watchdog_reason': 'Bound a hung compiler/module process group on the four-core, 16GiB host; no campaign budget or mathematical inference.',
             'seed': 'source-bound fixed module domains and fixture generation manifest', 'parameters': {'fixture_ids': fixture_ids, 'module_workers': 3, 'tracks': ['L9-scale','L9-decoder','L4-audit'], 'targets':192}}
    plan = {'schema': 'crypto.autoresearch.trial_plan.v1', 'experiment_id': exp, 'hypothesis_id': ids['hypothesis'],
            'task_id': task, 'approved_by': ids['approval_decision'], 'frozen': True, 'specification': spec_rel,
            'specification_sha256': sha(preview_spec), 'queue': queue_rel, 'source_sha256': source_hashes,
            'input_sha256': input_hashes, 'stop_on_invalid_output': True, 'trials': [trial]}
    preview_plan = write(preview, 'trial-plan.json', plan)
    binding = {'mode': 'experiments', 'kind': 'run', 'experiment_id': exp, 'trial_plan': plan_rel,
               'trial_plan_sha256': sha(preview_plan), 'approved_by': ids['approval_decision']}
    required = [run_base+'/'+name for name in (*GENERATED, *names)]
    handoff = {'id': task, 'from': 'coordinator', 'to': 'executor', 'role': 'executor', 'archived_by': archive,
               'objective': 'Execute and preserve the frozen three-module scaled observational batch.',
               'uncertainty_reduced': 'Whether pilot projection differences persist across fresh scales, what a public approximate scalar model records, and which local-basis assumptions cause the obstruction; no advantage conclusion.',
               'inputs': [spec_rel, plan_rel, *source_hashes, *input_hashes],
               'constraints': ['Run only after genuine repository preapproval, committed Coordinator approval/archive, selector ready, and published live claim.',
                               'Use the unchanged repository supervisor and preserve every failed/null output.', 'Three module workers; driver plus at most three module processes; no nested module threads.'],
               'deliverables': ['Every exact file listed in artifact_paths, including all supervisor logs and every lossless row part.'], 'artifact_paths': required,
               'completion_gate': ['Supervisor output-integrity receipt covers every declared artifact and all three follow-up tracks, or a complete retained operational-failure receipt.'],
               'budget': {'maximum_runs': 1, 'maximum_workers': 4, 'memory_gb': 12},
               'inference': {'policy': 'executor-implementation', 'delivery': 'interactive', 'fallback_allowed': False, 'degraded_allowed': False},
               'execution': binding}
    handoff_preview = write(preview, 'handoff.yaml', {'handoff': handoff})
    archive_receipt = f'coordination/goals/{goal}/batches/{batch}/archives/{archive}/snapshot-receipt.json'
    archive_handoff = {'id': archive, 'from': 'coordinator', 'to': 'coordinator', 'role': 'coordinator',
          'objective': 'Archive the exact completed or failed observational batch without scientific interpretation.', 'uncertainty_reduced': 'Immutable source/output custody.',
          'inputs': [run_base+'/'], 'constraints': ['Exact bytes and failed outcomes; isolated archive; no scientific transition.'],
          'deliverables': [archive_receipt], 'artifact_paths': [archive_receipt], 'completion_gate': ['Committed snapshot receipt and declared hashes verify.'],
          'budget': {'maximum_runs': 0}}
    embedded_handoff=copy.deepcopy(handoff)
    embedded_handoff['artifact_paths']=[run_base+'/'+name for name in ('manifest.yaml','raw-result.json','parts-manifest.json','verification-manifest.json','verification-replay.json')]
    embedded_handoff['full_handoff_ref']=handoff_rel
    embedded_handoff['artifact_coverage_note']='Canonical handoff and source task artifact_paths enumerate every exact supervisor/trial path. Embedded entrypoints avoid redundant path duplication; exact trial-plan SHA binding is unchanged.'
    queue = {'schema': 'crypto.autoresearch.dispatch_queue.v1', 'goal_id': goal, 'objective': 'Complete one source-bound classical projection/decoder/basis follow-up.', 'max_concurrent': 1,
       'tasks': [{'id': task, 'title': 'Execute the scaled three-module follow-up', 'role': 'executor', 'state': 'queued', 'priority': 90, 'review_required': False,
                  'depends_on': [], 'read_scope': [prefix+'/', spec_rel, plan_rel], 'write_scope': [run_base+'/'], 'artifact_paths': required,
                  'archived_by': archive, 'handoff': embedded_handoff},
                 {'id': archive, 'title': 'Archive the complete follow-up observations', 'role': 'coordinator', 'state': 'queued', 'priority': 80, 'review_required': False,
                  'depends_on': [task], 'read_scope': [run_base+'/'], 'write_scope': [str(Path(archive_receipt).parent)+'/',], 'artifact_paths': [archive_receipt],
                  'archived_by': archive, 'handoff': archive_handoff, 'archive': {'kind': 'snapshot', 'binding_mode': 'content_at_commit', 'source_task_ids': [task],
                      'commit_sha': None, 'parent_sha': None, 'path_sha256': {}, 'record_ids': [exp, ids['run']]}}]}
    queue_preview = write(preview, 'queue.json', queue)
    write(preview, 'archive-handoff.yaml', {'handoff': archive_handoff})
    decision = {'coordinator_decision': {'id': ids['approval_decision'], 'context': 'Prospective only until a genuine exact-byte preapproval pass and Coordinator archive.',
        'decision': 'approve', 'target_ids': [exp], 'rationale': ['Explicit user implementation/execution request and standing experiment authorization.',
          'Finite descriptive follow-up with complete controls, hashes, output preservation, machine protection and conditional per-instance witness certification, without an advantage claim.'],
        'evidence_refs': [], 'limitations': scientific['interpretation_limits'], 'next_actions': ['Require selector ready, publish a live executor claim, and execute via tools/experiment_execution.py.'],
        'knowledge_promotion': {'promoted': [], 'not_warranted': 'Approval is execution authority only; no observation or scientific finding exists yet.'},
        'decided_by': 'coordinator', 'decided_at': '2026-10-25', 'user_authorization': 'Current user explicitly requires implementing and running the programme; standing 2026-09-06 authorization.',
        'prospective_sha256': {'specification': sha(preview_spec), 'trial_plan': sha(preview_plan), 'queue': sha(queue_preview), 'handoff': sha(handoff_preview)}}}
    write(preview, 'approval-decision.yaml', decision)
    write(draft, goal_rel, {'research_goal': {'id': goal, 'title': 'Classical ECDLP projection scaling and public compressed-model investigation',
        'objective': 'Execute the fresh-scale projection, public-input approximate decoder and local-basis model audits with complete custody and no assumed advantage.', 'question_ids': [ids['question']],
        'status': 'active', 'completion_criteria': ['The frozen24-curve/192-target follow-up is source-bound, executed and completely reported.', 'Any proposed new solver remains a separate unresolved obligation.'],
        'pause_conditions': [], 'next_action': f'Finish source freeze and exact prospective admission for {exp}; then execute under its published claim.',
        'owner': 'coordinator', 'campaign_budget': {'maximum_runs': None, 'cpu_hours': None, 'wall_clock_seconds': None, 'max_concurrent': 1},
        'open_batches': [batch], 'impediments': [], 'claim_scope': 'No general solver, novelty or complexity advantage claim. Actual public per-instance scalar recoveries, including chance controls, require genuine discrete_log witness certificates.'}})
    write(draft, f'ledger/questions/{ids["question"]}.yaml', {'research_question': {'id': ids['question'], 'title': 'Do selected projection patterns persist at larger scales, and does a public compressed transition model extract scalar information?',
        'scope': scientific['scope'], 'status': 'open', 'owner': 'coordinator'}})
    write(draft, f'ledger/hypotheses/{ids["hypothesis"]}.yaml', {'hypothesis': {'id': ids['hypothesis'], 'question_id': ids['question'],
        'statement': 'Fresh-scale exact observations and a fixed truth-free approximate transition model can be measured against registered references; no success advantage is asserted in advance.',
        'mechanism': 'Exact pair/unary feature censuses, sign-matched nulls, publicly trained double-and-add transition kernels and beam search, and exact local-basis/certificate controls.', 'status': 'proposed',
        'asymptotic_claim': None, 'interpretation_limits': scientific['interpretation_limits'], 'prior_art': {'lead': 'LEAD-EXO-lossy-object-propagation', 'novelty': 'unverified; instruments use known methods'}}})
    lane_rel = f'coordination/goals/{goal}/lanes/{batch}.lane.json'
    write(draft, lane_rel, {'schema': 'crypto.autoresearch.goal_lane.v1', 'goal_id': goal, 'batch_id': batch,
        'dispatch_queue_path': queue_rel, 'write_scope': [f'coordination/goals/{goal}/batches/{batch}/'],
        'opened_by': 'coordinator-classical-followup', 'opened_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'opening_decision_id': None, 'objective': 'Prepare and execute the user-authorized classical follow-up on fresh inputs.', 'branch': args.source_ref.removeprefix('origin/'),
        'session': 'classical-followup-20261025', 'concurrent_open_lanes_at_open': []})
    packet = {'schema': 'crypto.autoresearch.preapproval_packet.v1', 'experiment_id': exp, 'approval_decision_id': ids['approval_decision'],
       'specification': spec_rel, 'trial_plan': plan_rel, 'queue': queue_rel, 'handoff': handoff_rel,
       'preview': {'specification': str(preview_spec), 'trial_plan': str(preview_plan), 'queue': str(queue_preview), 'handoff': str(handoff_preview)},
       'source_ref': args.source_ref, 'lane_id': batch, 'execution_route': {'kind': 'implementation', 'reason': 'New C++ exploratory instruments require implementation-tier source/output custody; no mechanical runbook is claimed.'}}
    write(out, 'preapproval-packet.json', packet)
    bindings = {'specification': spec_rel, 'trial_plan': plan_rel, 'queue': queue_rel, 'handoff': handoff_rel,
                'archive_handoff': archive_handoff_rel, 'approval_decision': 'ledger/decisions/'+ids['approval_decision']+'.yaml', 'goal': goal_rel, 'lane': lane_rel}
    write(out, 'canonical-bindings.json', bindings)
    print(json.dumps({'out': str(out), 'prospective_only': True, 'official_approval_recorded': False, 'experiment': exp,
                      'artifacts_per_trial': len(names), 'required_supervisor_and_trial_paths': len(required), 'source_files': len(source_hashes),
                      'packet': str(out/'preapproval-packet.json'), 'bindings': bindings}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, required=True)
    p.add_argument('--lab-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--ids', type=Path, default=Path(__file__).with_name('ids.json'))
    p.add_argument('--source-prefix', default='harness/classical_ecdlp_followup')
    p.add_argument('--source-ref', default='origin/plan/direct-ecdlp-cancellation-20261025')
    p.add_argument('--check-ids', action='store_true')
    prepare(p.parse_args())
