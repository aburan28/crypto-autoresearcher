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

MODULES = {**{f'candidate_{i}':['solver-candidate'] for i in range(3)}, **{f'solvers_{i}':['solver-baselines'] for i in range(3)}}
FEATURES = ['x_mod_7','power_residue_5','x_hash_7','constant']
METHODS = ['rho_upstream_auto','rho_upstream_auto_aa','hybrid_xmod7_exact_b8_then_rho','bernstein_lange_precomp','bsgs_complete']
PART_COUNT = 2560
VERIFICATION_PART_COUNT = 256
GENERATED = ('launch.json', 'execution-receipt.json', 'command.txt', 'environment.json',
             'stdout.log', 'stderr.log', 'check.stdout.log', 'check.stderr.log')


PROTOCOL = {'schema':'classical.ecdlp.solver-validation-protocol.v1','scope':'larger_solver_validation',
 'cohort':{'fixtures':48,'subgroup_bits':[12,14,16,18],'curves_per_size_stratum':6,'targets_per_fixture':16,'targets':768,'nested_core_targets':192,'extension_targets':576},
 'primary_candidate':{'feature':'x_mod_7','prefix_mode':'exact','beam_width':8,'training_samples':2048,'views':4,'unused_diagnostics':False},
 'primary_comparison':{'methods':['hybrid_xmod7_exact_b8_then_rho','rho_upstream_auto'],'metric':'whole process CPU, paired per-curve cold and m16 full/m8 core costs','wall_time':'descriptive under three concurrent curve workers','operation_vector':'reported separately, never add nested calls as disjoint work'},
 'secondary_methods':['rho_upstream_auto_aa','bernstein_lange_precomp','bsgs_complete'],
 'uncertainty_summary':'Paired per-curve ratios, equal-curve geometric mean/range, and A/A noise; no bootstrap or asymptotic fit preregistered.',
 'secondary_candidate':{'features':['x_mod_7','power_residue_5','x_hash_7','constant'],'prefix_modes':['model','exact'],'beam_widths':[1,8],'training':2048,'heldout':512,'diagnostics':True},
 'success_scope':'Checked working correctness, candidate-only recovery and complete fallback dependency are distinct; incremental gain does not require novelty.',
 'full_contract':'prospective-review.md','source_separation':'Private scalar labels and target seeds are not solver/verifier inputs; no OS-isolated blindness claim.',
 'host':{'active_cpu_limit':4,'module_process_limit':3,'maximum_os_threads_including_waiters':7,'memory_gib':12},
 'storage':{'producer_parts':2560,'verification_parts':256,'part_limit_bytes':61440,'lossless_reconstruction_required':True},
 'resources':'Operational watchdogs classify censoring and do not impose mathematical failure or a lifetime spending cap.'}


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
    def copy_file(original: Path, relative: str):
        target = source/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
    for folder in ('candidate','baselines'):
        for p in sorted((lab/folder).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(lab/folder)
            if any(x in ('build','cryptanalysis-reference','__pycache__','tests') for x in rel.parts):continue
            if p.suffix not in ('.cpp','.hpp','.c','.h','.py','.json','.md') and p.name!='LICENSE':continue
            copy_file(p,prefix+'/'+folder+'/'+rel.as_posix())
    cohort_handoff=json.loads((lab/'cohort/publication-handoff.json').read_text())
    for entry in cohort_handoff['files']:
        original=Path(entry['source']);relative=original.relative_to(lab/'cohort').as_posix()
        if sha(original)!=entry['sha256']:raise ValueError('changed cohort handoff source '+relative)
        copy_file(original,prefix+'/cohort/'+relative)
    copy_file(lab/'protocol-review.md',prefix+'/protocol/prospective-review.md')
    write(source,prefix+'/protocol/validation-protocol.json',PROTOCOL)
    verifier_rel=prefix+'/admission/verify_candidates.cpp';copy_file(Path(__file__).with_name('verify_candidates.cpp'),verifier_rel)
    driver_rel=prefix+'/admission/driver.py';copy_file(Path(__file__).with_name('driver.py'),driver_rel)
    for name in ('prepare_packet.py','archive_snapshot.py','check_new_records.py','test_driver.py','ids.json','id-checks.json','driver-unit-tests.txt','OPERATIONS.md'):
        original=Path(__file__).with_name(name)
        if original.is_file():copy_file(original,prefix+'/admission/'+name)
    source_hashes={p.relative_to(source).as_posix():sha(p) for p in sorted(source.rglob('*')) if p.is_file() and '/protocol/' not in p.relative_to(source).as_posix() and '/cohort/public/' not in p.relative_to(source).as_posix()}
    input_hashes={p.relative_to(source).as_posix():sha(p) for directory in (source/prefix/'protocol',source/prefix/'cohort/public') for p in sorted(directory.glob('*')) if p.is_file()}
    fixture_ids = [line.split('\t', 1)[0] for line in (lab/'cohort/public/fixtures.tsv').read_text().splitlines()[1:] if line.strip()]
    if len(fixture_ids) != 48 or len(set(fixture_ids)) != 48:
        raise ValueError('exact forty-eight-fixture solver cohort required')
    fixture_meta=[]
    for line in (lab/'cohort/public/fixtures.tsv').read_text().splitlines()[1:]:
        if not line.strip(): continue
        fields=line.split()
        if len(fields)!=10: raise ValueError('fixture columns')
        fixture_meta.append({'id':fields[0],'stratum':fields[1],'p':int(fields[2]),'r':int(fields[7]),'N':int(fields[8])})
    lines=(lab/'cohort/public/public-targets.tsv').read_text().splitlines()
    if not lines or lines[0].split()!=['fixture_id','target_id','Qx','Qy','Qinf']: raise ValueError('target header')
    target_meta=[]
    for line in lines[1:]:
        if not line.strip(): continue
        f=line.split()
        if len(f)!=5 or f[0] not in fixture_ids or f[4] not in ('0','1'): raise ValueError('target row')
        target_meta.append({'fixture_id':f[0],'target_id':f[1]})
    if len(target_meta)!=768 or len({x['target_id'] for x in target_meta})!=768 or any(sum(x['fixture_id']==f for x in target_meta)!=16 for f in fixture_ids): raise ValueError('exact 768 globally unique public targets / sixteen per fixture required')
    subsets={}
    for line in (lab/'cohort/public/target-subsets.tsv').read_text().splitlines()[1:]:
        f,t,ordinal,subset=line.split();subsets[t]={'fixture_id':f,'ordinal':int(ordinal),'subset':subset}
    if len(subsets)!=768 or sum(x['subset']=='core' for x in subsets.values())!=192 or sum(x['subset']=='extension' for x in subsets.values())!=576:raise ValueError('core/extension coverage')
    for target in target_meta:
        v=subsets[target['target_id']]
        if v['fixture_id']!=target['fixture_id']:raise ValueError('subset identity')
        target.update(ordinal=v['ordinal'],subset=v['subset'])
    shards={}
    for index in range(3):
        name='fixtures-shard-'+str(index)+'.tsv'
        values=[line.split()[0] for line in (lab/'cohort/public'/name).read_text().splitlines()[1:] if line.strip()]
        if not values or len(set(values))!=len(values): raise ValueError('invalid fixture shard')
        shards[index]=values
    if sorted(x for values in shards.values() for x in values)!=sorted(fixture_ids): raise ValueError('fixture shards must be disjoint complete union')
    config_rel = prefix+'/admission/batch-config.json'
    config={'schema':'classical.ecdlp.solver-validation-config.v1','experiment_id':ids['experiment'],'run_id':ids['run'],
        'maximum_module_workers':3,'compiler_flags':['-std=c++20','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-Wconversion','-Wshadow'],
        'watchdog_seconds':3600,'watchdog_reason':'Operational subprocess backstop, never mathematical evidence.',
        'fixtures':prefix+'/cohort/public/fixtures.tsv','fixture_ids':fixture_ids,'fixture_meta':fixture_meta,
        'public_targets':prefix+'/cohort/public/public-targets.tsv','target_meta':target_meta,'target_subsets':prefix+'/cohort/public/target-subsets.tsv',
        'verifier_source':verifier_rel,'modules':[], 'source_sha256':source_hashes,'input_sha256':input_hashes,
        'scope':'larger_solver_validation','attack_advantage_claimed':False,
        'instance_witness_policy':'Checked public per-instance witnesses; candidate-only and fallback-dependent complete-solver scopes remain separate.'}
    for name,tracks in MODULES.items():
        kind='candidate' if name.startswith('candidate_') else 'solvers';index=int(name[-1])
        module={'name':name,'kind':kind,'source':prefix+('/candidate/main.cpp' if kind=='candidate' else '/baselines/baselines.cpp'),
            'tracks':tracks,'fixtures':prefix+'/cohort/public/fixtures-shard-'+str(index)+'.tsv',
            'public_targets':prefix+'/cohort/public/public-targets-shard-'+str(index)+'.tsv','fixture_ids':shards[index]}
        if kind=='candidate':module['features']=FEATURES
        else:module.update(methods=METHODS,hybrid_method='hybrid_xmod7_exact_b8_then_rho',
            setup_rows=[['baseline_setup','bernstein_lange_precomp'],['baseline_setup','bsgs_complete'],['hybrid_setup','hybrid_xmod7_exact_b8_then_rho']],
            build_argv=['python3',prefix+'/baselines/build.py','--output','{binary}'])
        config['modules'].append(module)
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
    scientific={'id':exp,'title':'Larger classical ECDLP solver validation and matched baseline costs','goal_id':goal,
        'hypothesis_id':ids['hypothesis'],'version':1,'designed_at':'2026-10-25',
        'scope':'48 fresh curves at 12/14/16/18 subgroup bits, 768 public targets, and a nested 192-target core; candidate-only recovery, complete hybrid/baseline correctness, and matched full costs.',
        'controls':['Separate fixed development correctness suite: k=0,1,r-1, nontrivial cofactors, malformed and nonmember inputs, and wrong-witness mutations.',
            'Same public target and Ops arithmetic backend; rho only, identical-seeded fresh-state rho A/A, and candidate followed by the same rho fallback.',
            'Actual vendored Bernstein-Lange precomputation and separately named complete BSGS; retain failures and preserve their distinct cost models.',
            'Primary x_mod_7/exact/beam 8/four views/2048 training uses fresh cold Ops state; unused heldout/contraction work is omitted from the primary constructor and retained in secondary diagnostics.',
            'Full secondary four-feature, two-mode, two-beam coverage; all misses and structural NAs retained.',
            'Separate Jacobian public-equation verification of every candidate, prefix candidate and returned scalar; recompilation/replay by the output checker.'],
        'metrics':['Primary candidate-only hit count and rate over all 768 targets; core 192 and extension 576 reported separately and not treated as independent studies.',
            'Solved/failed/censored/invalid counts for each complete arm; answer origin explicitly prefix or fallback.',
            'Whole-process CPU times for required setup and target work, stage costs, wall intervals, complete operation vector and memory payload.',
            'Counterfactual cold setup plus one-target totals, full m=16 per-curve batch/amortized totals, and nested core m=8 on 24 predeclared curves.',
            'Paired per-curve hybrid/rho CPU ratios by group size; zero-cost, invalid and censored ratios remain undefined and visible, with no numerical floor or success-only full-panel gain.',
            'Rho A/A deterministic work equality and CPU/wall drift; randomized paired arm order; all seeds, candidate lists and counters retained.',
            'Study overhead, including input certification, independent verification, secondary heldout/contraction work and output serialization, reported separately.'],
        'budget':{'policy':'advisory','maximum_runs':1,'maximum_workers':4,'memory_gb':12},
        'stopping_rules':['Complete one frozen 48-curve/768-target batch and all declared coverage items.','Watchdogs and memory limits protect the host; timeouts are operational censoring, not mathematical falsification.'],
        'invalidation_rules':['A changed hash, missing coverage, truncated or unreconstructable rows, failed mandatory control or independent witness contradiction invalidates the affected measurement.','Solver misses and censored outcomes remain visible; fallback occurs only where the named hybrid declares and charges it.'],
        'success_criterion':'Working-solver milestone: all 768 targets and development controls yield independently checked answers for each declared complete arm; candidate-only success and fallback dependency are separate. Incremental baseline improvement is assessed at measured scope from matched costs, without a novelty gate.',
        'falsification_criterion':'A wrong witness rejects the affected implementation; a prefix miss is a recorded bounded-candidate miss; costs greater than baseline characterize only the frozen revision/regime. Operational censoring does not close a mathematical lead.',
        'decision_impact':{'on_positive':'Credit working correctness and any matched baseline improvement at the measured scope; qualified quantitative claims require their proper record and review.','on_negative':'Preserve all misses, costs and failures, and identify the next algorithm revision or validation gap without declaring the family exhausted.'},
        'input_bindings':{'fixture_manifest':{'path':config['fixtures'],'sha256':input_hashes[config['fixtures']]},'public_targets':{'path':config['public_targets'],'sha256':input_hashes[config['public_targets']]},'protocol':{'path':prefix+'/protocol/validation-protocol.json','sha256':input_hashes[prefix+'/protocol/validation-protocol.json']},'driver':{'path':driver_rel,'sha256':source_hashes[driver_rel]}},
        'variable_ledger':{'independent':[{'name':x}for x in ('fixture','stratum','subgroup_bits','target','method','prefix_mode','beam_width')],
            'factors':[{'name':'source_build','treatment':'fixed','how':'Exact published source/vendor/input hashes and declared compiler flags.'},
                {'name':'input_selection','treatment':'fixed','how':'Complete frozen 48-curve/768-target cohort, with all rejections, pre-target fixture seal and withheld-truth commitments.'},
                {'name':'rho_randomness','treatment':'fixed','how':'Rho A/A and hybrid fallback share the declared per-target seed/restarts but receive no free completed tables or caches.'},
                {'name':'training','treatment':'fixed','how':'2048 unlabelled samples, four views and fixed primary preset; fresh primary cold state; secondary heldout data unused for tuning.'},
                {'name':'execution_order','treatment':'randomized','how':'Frozen public target-independent arm-order stream; A/A repeats share algorithm seeds but differ in execution slot.'},
                {'name':'host_load','treatment':'measured','how':'Three concurrent measurement processes; full-process CPU and A/A repeats; wall times descriptive.'}],
            'comparisons':[{'id':'C-rho-AA','arms':['rho-only','rho-AA'],'differs_in':['execution_order'],'design':'aa'}, {'id':'C-solver-validation','arms':['candidate-only','hybrid','rho-only','rho-AA','Bernstein-Lange','BSGS'],'differs_in':['method'],'design':'one_factor'},
                {'id':'C-primary-paired','arms':['hybrid','rho-only'],'differs_in':['method'],'design':'one_factor','pairing':'Same fixture, target, backend and rho seed; all required setup, failed candidate checks, fallback and final verification charged.'}],
            'aa_not_applicable':None,'crosses_map':False},
        'prediction_provenance':[{'prediction':'P-larger-validation','first_recorded_in':prefix+'/protocol/validation-protocol.json','written_at':'2026-10-25',
            'data_seen':[{'path':'https://github.com/aburan28/crypto-autoresearcher/blob/68f1b0406cb4a497aa943aef6d55736b4c0d4123/experiments/EXP-ECDLP-7c0b1e/reports/run-20261025T0651Z/observations.md','measured':'Prior 24 curves at 8/10/12 bits and 192 targets; primary xmod7/exact/beam8 was chosen before this fresh cohort; no full algorithm runtime baseline was measured.'}],
            'sample_status':'out_of_sample','overlap':'Fresh curves by (p,a,b), at larger 12/14/16/18-bit subgroup sizes; full panel and nested core specified before outputs. Source-enforced label separation is not OS-isolated blindness.'}],
        'interpretation_limits':['Toy subgroups at 12–18 bits; observed scaling does not prove an asymptotic exponent.','Complete hybrid recovery does not validate candidate-alone completeness; report answer origin and primary candidate success separately.','Cube-root online methods pay their actual setup and memory; no asymmetric cost amortization.','Novelty is assessed separately from working correctness and incremental baseline gains.','Same-session implementation/analysis and a distinct arithmetic checker do not constitute an independent scientific review session.','No qualified performance claim is inferred solely from controls, output validation or a generic certificate.']}
    draft_spec = {'experiment': {**scientific, 'status': 'review_required', 'frozen': False, 'approved_by': None, 'execution_authorized': False}}
    final_spec = {'experiment': {**scientific, 'status': 'approved', 'frozen': True, 'approved_by': ids['approval_decision'], 'execution_authorized': True}}
    write(draft, spec_rel, draft_spec)
    preview_spec = write(preview, 'specification.yaml', final_spec)
    names, empty = artifacts()
    trial = {'id': 'followup-batch', 'run_id': ids['run'], 'depends_on': [],
             'argv': ['python3', driver_rel, 'run', '--config', config_rel, '--run-dir', '{run_dir}'],
             'check_argv': ['python3', driver_rel, 'check', '--config', config_rel, '--run-dir', '{run_dir}'],
             'artifacts': names, 'allow_empty_artifacts': empty, 'memory_mb':12288,
             'watchdog_seconds': 4200, 'watchdog_reason': 'Bound a hung compiler/module process group on the four-core, 16GiB host; no campaign budget or mathematical inference.',
             'seed': 'Source-bound independent cohort/training/walk/order domains and published public manifests', 'parameters': {'fixture_ids': fixture_ids, 'module_workers': 3, 'tracks':['solver-candidate','solver-baselines'],'targets':768,'fixtures':48,'core_targets':192}}
    plan = {'schema': 'crypto.autoresearch.trial_plan.v1', 'experiment_id': exp, 'hypothesis_id': ids['hypothesis'],
            'task_id': task, 'approved_by': ids['approval_decision'], 'frozen': True, 'specification': spec_rel,
            'specification_sha256': sha(preview_spec), 'queue': queue_rel, 'source_sha256': source_hashes,
            'input_sha256': input_hashes, 'stop_on_invalid_output': True, 'trials': [trial]}
    preview_plan = write(preview, 'trial-plan.json', plan)
    binding = {'mode': 'experiments', 'kind': 'run', 'experiment_id': exp, 'trial_plan': plan_rel,
               'trial_plan_sha256': sha(preview_plan), 'approved_by': ids['approval_decision']}
    required = [run_base+'/'+name for name in (*GENERATED, *names)]
    handoff = {'id': task, 'from': 'coordinator', 'to': 'executor', 'role': 'executor', 'archived_by': archive,
               'objective':'Execute and preserve the frozen larger solver-validation and baseline-comparison batch.',
               'uncertainty_reduced':'Candidate-only recovery at larger sizes, complete-arm correctness, and full matched baseline costs under the registered cold/reuse models.',
               'inputs': [spec_rel, plan_rel, *source_hashes, *input_hashes],
               'constraints': ['Run only after genuine repository preapproval, committed Coordinator approval/archive, selector ready, and published live claim.',
                               'Use the unchanged repository supervisor and preserve every failed/null output.', 'At most three module processes plus driver; upstream single-compute-thread baseline uses one worker pthread plus waiting main (at most seven OS threads, at most four active CPUs).'],
               'deliverables': ['Every exact file listed in artifact_paths, including all supervisor logs and every lossless row part.'], 'artifact_paths': required,
               'completion_gate': ['Supervisor output-integrity receipt covers every declared artifact and both solver-validation tracks, or a complete retained operational-failure receipt.'],
               'budget': {'maximum_runs': 1, 'maximum_workers': 4, 'memory_gb': 12},
               'inference': {'policy': 'executor-implementation', 'delivery': 'interactive', 'fallback_allowed': False, 'degraded_allowed': False},
               'execution': binding}
    handoff_preview = write(preview, 'handoff.yaml', {'handoff': handoff})
    archive_receipt = f'coordination/goals/{goal}/batches/{batch}/archives/{archive}/snapshot-receipt.json'
    archive_handoff = {'id': archive, 'from': 'coordinator', 'to': 'coordinator', 'role': 'coordinator',
          'objective':'Archive exact solver-validation outputs, including misses and failed outcomes, without prewriting interpretation.', 'uncertainty_reduced': 'Immutable source/output custody.',
          'inputs': [run_base+'/'], 'constraints': ['Exact bytes and failed outcomes; isolated archive; no scientific transition.'],
          'deliverables': [archive_receipt], 'artifact_paths': [archive_receipt], 'completion_gate': ['Committed snapshot receipt and declared hashes verify.'],
          'budget': {'maximum_runs': 0}}
    embedded_handoff=copy.deepcopy(handoff)
    embedded_handoff['artifact_paths']=[run_base+'/'+name for name in ('manifest.yaml','raw-result.json','parts-manifest.json','verification-manifest.json','verification-replay.json')]
    embedded_handoff['full_handoff_ref']=handoff_rel
    embedded_handoff['artifact_coverage_note']='Canonical handoff and source task artifact_paths enumerate every exact supervisor/trial path. Embedded entrypoints avoid redundant path duplication; exact trial-plan SHA binding is unchanged.'
    queue = {'schema': 'crypto.autoresearch.dispatch_queue.v1', 'goal_id': goal, 'objective':'Complete the larger source-bound solver-validation and matched baseline batch.', 'max_concurrent': 1,
       'tasks': [{'id': task, 'title': 'Execute the scaled six-job solver validation', 'role': 'executor', 'state': 'queued', 'priority': 90, 'review_required': False,
                  'depends_on': [], 'read_scope': [prefix+'/', spec_rel, plan_rel], 'write_scope': [run_base+'/'], 'artifact_paths': required,
                  'archived_by': archive, 'handoff': embedded_handoff},
                 {'id': archive, 'title': 'Archive the complete solver-validation observations', 'role': 'coordinator', 'state': 'queued', 'priority': 80, 'review_required': False,
                  'depends_on': [task], 'read_scope': [run_base+'/'], 'write_scope': [str(Path(archive_receipt).parent)+'/',], 'artifact_paths': [archive_receipt],
                  'archived_by': archive, 'handoff': archive_handoff, 'archive': {'kind': 'snapshot', 'binding_mode': 'content_at_commit', 'source_task_ids': [task],
                      'commit_sha': None, 'parent_sha': None, 'path_sha256': {}, 'record_ids': [exp, ids['run']]}}]}
    queue_preview = write(preview, 'queue.json', queue)
    write(preview, 'archive-handoff.yaml', {'handoff': archive_handoff})
    decision = {'coordinator_decision': {'id': ids['approval_decision'], 'context': 'Prospective only until a genuine exact-byte preapproval pass and Coordinator archive.',
        'decision': 'approve', 'target_ids': [exp], 'rationale': ['Explicit user implementation/execution request and standing experiment authorization.',
          'Larger solver validation with explicit correctness criteria, matched named baselines, full costs, complete failed outcomes and source/input custody; novelty is a separate question.'],
        'evidence_refs': [], 'limitations': scientific['interpretation_limits'], 'next_actions': ['Require selector ready, publish a live executor claim, and execute via tools/experiment_execution.py.'],
        'knowledge_promotion': {'promoted': [], 'not_warranted': 'Approval is execution authority only; no observation or scientific finding exists yet.'},
        'decided_by': 'coordinator', 'decided_at': '2026-10-25', 'user_authorization': 'Current user explicitly requires implementing and running the programme; standing 2026-09-06 authorization.',
        'prospective_sha256': {'specification': sha(preview_spec), 'trial_plan': sha(preview_plan), 'queue': sha(queue_preview), 'handoff': sha(handoff_preview)}}}
    write(preview, 'approval-decision.yaml', decision)
    write(draft,goal_rel,{'research_goal':{'id':goal,'title':'Larger classical ECDLP working-solver validation and baseline improvement',
        'objective':'Validate a working classical public-input solver at larger cohort sizes, then compare complete costs with explicit baselines and credit measured incremental progress.',
        'question_ids':[ids['question']],'status':'active','completion_criteria':['The frozen 48-curve/768-target cohort and all named arms are executed and completely reported with checked public witnesses.','Candidate-only correctness/recovery, complete fallback dependence and matched baseline costs are separate outcomes.'],
        'pause_conditions':[],'next_action':f'Finish exact prospective source/input admission for {exp}, publish a live executor claim, then execute the frozen cohort.',
        'owner':'coordinator','campaign_budget':{'maximum_runs':None,'cpu_hours':None,'wall_clock_seconds':None,'max_concurrent':1},'open_batches':[batch],'impediments':[],
        'claim_scope':'Working correctness and measured baseline comparison first; novelty separately. No exponent is inferred from four toy bit sizes.'}})
    write(draft,f'ledger/questions/{ids["question"]}.yaml',{'research_question':{'id':ids['question'],'title':'How does the frozen public candidate recover larger-cohort targets, and how do its complete composed costs compare with explicit baseline solvers?','scope':scientific['scope'],'status':'open','owner':'coordinator'}})
    write(draft,f'ledger/hypotheses/{ids["hypothesis"]}.yaml',{'hypothesis':{'id':ids['hypothesis'],'question_id':ids['question'],
        'statement':'A fixed public candidate can be validated on larger fresh curves, composed transparently with a complete fallback, and measured against named complete baselines at declared setup/reuse costs.',
        'mechanism':'Public unlabelled transition training and exact-prefix beam candidates, checked public equations, honest seeded-rho fallback, actual rho/Bernstein-Lange/BSGS references.','status':'proposed','asymptotic_claim':None,'interpretation_limits':scientific['interpretation_limits']}})
    lane_rel = f'coordination/goals/{goal}/lanes/{batch}.lane.json'
    write(draft, lane_rel, {'schema': 'crypto.autoresearch.goal_lane.v1', 'goal_id': goal, 'batch_id': batch,
        'dispatch_queue_path': queue_rel, 'write_scope': [f'coordination/goals/{goal}/batches/{batch}/'],
        'opened_by':'coordinator-classical-solver-validation', 'opened_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'opening_decision_id': None, 'objective':'Prepare and execute the user-authorized larger classical solver-validation cohort.', 'branch': args.source_ref.removeprefix('origin/'),
        'session':'classical-solver-validation-20261025', 'concurrent_open_lanes_at_open': []})
    packet = {'schema': 'crypto.autoresearch.preapproval_packet.v1', 'experiment_id': exp, 'approval_decision_id': ids['approval_decision'],
       'specification': spec_rel, 'trial_plan': plan_rel, 'queue': queue_rel, 'handoff': handoff_rel,
       'preview': {'specification': str(preview_spec), 'trial_plan': str(preview_plan), 'queue': str(queue_preview), 'handoff': str(handoff_preview)},
       'source_ref': args.source_ref, 'lane_id': batch, 'execution_route': {'kind': 'implementation', 'reason': 'New larger-cohort candidate/baseline adapters require implementation-tier source/output custody; no mechanical runbook is claimed.'}}
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
    p.add_argument('--source-prefix', default='harness/classical_ecdlp_solver_validation')
    p.add_argument('--source-ref', default='origin/experiment/classical-ecdlp-solver-validation-20261025')
    p.add_argument('--check-ids', action='store_true')
    prepare(p.parse_args())
