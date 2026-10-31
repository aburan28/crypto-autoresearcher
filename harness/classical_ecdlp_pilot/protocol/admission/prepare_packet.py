#!/usr/bin/env python3
"""Prepare exact unapproved drafts and prospective approval bytes.

This command never writes the repository, records approval, grants a claim,
executes C++ diagnostics, or fabricates an admission result. Copy source/
and draft/ into the repository and publish them before invoking preapproval.
Only a Coordinator may later archive the preview bytes after a genuine pass.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

MODULES = {'circuit': ['D', 'L4'], 'padic_endo': ['L1', 'L3'], 'sequences': ['L2', 'L6'],
           'algebraic': ['L5', 'L7', 'L8'], 'lossy': ['L9']}
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
    for i in range(64):
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
    for name in ('fixtures.tsv', 'pilot.json', 'fixture-certificate.json', 'fixture-history.jsonl'):
        target = source/prefix/'protocol'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(lab/'protocol'/name, target)
    driver_rel = prefix+'/protocol/admission/driver.py'
    target = source/driver_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('driver.py'), target)
    source_hashes = {p.relative_to(source).as_posix(): sha(p) for p in sorted(source.rglob('*')) if p.is_file() and p.suffix in ('.cpp', '.hpp', '.py')}
    input_hashes = {p.relative_to(source).as_posix(): sha(p) for p in sorted((source/prefix/'protocol').glob('*')) if p.is_file()}
    fixture_ids = [line.split('\t', 1)[0] for line in (lab/'protocol/fixtures.tsv').read_text().splitlines()[1:] if line.strip()]
    if len(fixture_ids) != 8 or len(set(fixture_ids)) != 8:
        raise ValueError('exact eight-fixture pilot required')
    config_rel = prefix+'/protocol/admission/batch-config.json'
    config = {'schema': 'classical.ecdlp.batch-config.v1', 'experiment_id': ids['experiment'], 'run_id': ids['run'],
              'maximum_module_workers': 3, 'compiler_flags': ['-std=c++20', '-O2', '-Wall', '-Wextra', '-Wconversion', '-Wshadow'],
              'watchdog_seconds': 3300, 'watchdog_reason': 'operational subprocess backstop below the batch supervisor watchdog; not mathematical evidence',
              'fixtures': prefix+'/protocol/fixtures.tsv', 'fixture_ids': fixture_ids,
              'modules': [{'name': name, 'source': prefix+'/src/'+name+'.cpp', 'tracks': tracks,
                           'global_fixture_aliases': ['shared_boolean_gate_grammar'] if name == 'circuit' else []} for name, tracks in MODULES.items()],
              'source_sha256': source_hashes, 'input_sha256': input_hashes,
              'scope': 'exploratory_toy_diagnostic', 'attack_claimed': False}
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
    scientific = {'id': exp, 'title': 'Classical ECDLP finite all-track observational pilot', 'goal_id': goal,
        'hypothesis_id': ids['hypothesis'], 'version': 1, 'designed_at': '2026-10-25',
        'scope': 'Eight public synthetic toy fixtures, ten named track diagnostics; no new solver, comparative performance or asymptotic claim.',
        'controls': ['Exact independent point/circuit arithmetic and corrupted witnesses', 'Finite Kummer, constant/full-point entropy calibrations',
                     'Known matchgate signatures and frozen rational basis grammar', 'Exact coefficient, CRT and count-receipt controls',
                     'Frozen null labels and all unsuccessful/null outcomes retained'],
        'metrics': ['Exact per-module JSONL observations and fixture identifiers', 'Constructor/evaluation counters with units',
                    'All control outcomes and failure/censoring classifications', 'Output bytes, complete row counts, per-module wall intervals and source/input digests'],
        'budget': {'policy': 'advisory', 'maximum_runs': 1, 'maximum_workers': 4, 'memory_gb': 12},
        'stopping_rules': ['Complete the one frozen eight-fixture batch and all finite module grammars.', 'Supervisor watchdog or actual process/memory failure is operational censoring, not scientific falsification.'],
        'invalidation_rules': ['Any failed mandatory calibration, changed hash, malformed row, missing track, truncated output or unreconstructable partition invalidates the affected batch.', 'No post-hoc scalar advice or uncharged inverse table may be described as a solver.'],
        'success_criterion': 'C-integrity: collect all ten declared track outputs and controls with exact reconstruction, zero output-integrity errors and complete custody; no required anomaly or advantage.',
        'falsification_criterion': 'A concrete counterexample rejects only its explicitly stated finite identity or frozen candidate; operational failures and missing constructors have no mathematical negative interpretation.',
        'decision_impact': {'on_positive': 'Archive descriptive observations; separately identify a specific surviving construction for a fresh prospective study, without promoting an algorithm claim.',
                            'on_negative': 'Retain the exact counterexample or operational failure and repair the affected instrument/construction in a new additive protocol; do not close a whole lead.'},
        'input_bindings': {'fixture_manifest': {'path': prefix+'/protocol/fixtures.tsv', 'sha256': input_hashes[prefix+'/protocol/fixtures.tsv']},
                           'protocol': {'path': prefix+'/protocol/pilot.json', 'sha256': input_hashes[prefix+'/protocol/pilot.json']},
                           'driver': {'path': driver_rel, 'sha256': source_hashes[driver_rel]}},
        'variable_ledger': {'independent': [{'name': x} for x in ('fixture', 'module', 'projection', 'basis_matrix', 'prefix_depth')],
            'factors': [{'name': 'source_build', 'treatment': 'fixed', 'how': 'Exact source hashes and compiler flags are sealed in the batch configuration.'},
                        {'name': 'input_selection', 'treatment': 'fixed', 'how': 'Eight certified fixtures, all rejection history and generation rule are committed before measurement.'},
                        {'name': 'null_seed', 'treatment': 'fixed', 'how': 'Module RNG algorithms and finite seed domains are source-bound before execution.'},
                        {'name': 'truth_access', 'treatment': 'fixed', 'how': 'Enumerated scalar-labelled orbits are charged instrumentation, never an uncharged decoder.'},
                        {'name': 'host_load', 'treatment': 'measured', 'how': 'Concurrent wall intervals are descriptive only and are not compared as algorithm costs.'}],
            'comparisons': [{'id': 'C-integrity', 'arms': ['frozen pilot'], 'differs_in': [], 'design': 'absolute'}],
            'aa_not_applicable': 'Exact finite censuses and rational identities are deterministic. Floating entropy uses stated rounding/calibration tolerances. Wall time is descriptive, never a decisive metric.',
            'crosses_map': False},
        'prediction_provenance': [{'prediction': 'P-calibration', 'first_recorded_in': prefix+'/protocol/pilot.json', 'written_at': '2026-10-25',
            'data_seen': [{'path': 'docs/reports/direct-ecdlp-cancellation-20261025/programme/CHECKS.md', 'measured': 'Earlier fixed-fixture point-level development controls only; newly implemented modules have development self-tests.'}],
            'sample_status': 'in_sample', 'overlap': 'Known exact calibration identities are instrumentation references, not fresh algorithmic predictions.'}],
        'interpretation_limits': ['Toy pilot only, smaller than parent discovery cohort.', 'All null and ordinary observations retained.', 'No independent-session or formal proof validation.', 'No exponent, speedup, ECDLP solver, or official scientific support/reject transition.']}
    draft_spec = {'experiment': {**scientific, 'status': 'review_required', 'frozen': False, 'approved_by': None, 'execution_authorized': False}}
    final_spec = {'experiment': {**scientific, 'status': 'approved', 'frozen': True, 'approved_by': ids['approval_decision'], 'execution_authorized': True}}
    write(draft, spec_rel, draft_spec)
    preview_spec = write(preview, 'specification.yaml', final_spec)
    names, empty = artifacts()
    trial = {'id': 'all-track-batch', 'run_id': ids['run'], 'depends_on': [],
             'argv': ['python3', driver_rel, 'run', '--config', config_rel, '--run-dir', '{run_dir}'],
             'check_argv': ['python3', driver_rel, 'check', '--config', config_rel, '--run-dir', '{run_dir}'],
             'artifacts': names, 'allow_empty_artifacts': empty, 'memory_mb': 3072,
             'watchdog_seconds': 3600, 'watchdog_reason': 'Bound a hung compiler/module process group on the four-core, 16GiB host; no campaign budget or mathematical inference.',
             'seed': 'source-bound fixed module domains and fixture generation manifest', 'parameters': {'fixture_ids': fixture_ids, 'module_workers': 3, 'tracks': ['D', *('L'+str(i) for i in range(1,10))]}}
    plan = {'schema': 'crypto.autoresearch.trial_plan.v1', 'experiment_id': exp, 'hypothesis_id': ids['hypothesis'],
            'task_id': task, 'approved_by': ids['approval_decision'], 'frozen': True, 'specification': spec_rel,
            'specification_sha256': sha(preview_spec), 'queue': queue_rel, 'source_sha256': source_hashes,
            'input_sha256': input_hashes, 'stop_on_invalid_output': True, 'trials': [trial]}
    preview_plan = write(preview, 'trial-plan.json', plan)
    binding = {'mode': 'experiments', 'kind': 'run', 'experiment_id': exp, 'trial_plan': plan_rel,
               'trial_plan_sha256': sha(preview_plan), 'approved_by': ids['approval_decision']}
    required = [run_base+'/'+name for name in (*GENERATED, *names)]
    handoff = {'id': task, 'from': 'coordinator', 'to': 'executor', 'role': 'executor', 'archived_by': archive,
               'objective': 'Execute and preserve the frozen all-track finite observational batch.',
               'uncertainty_reduced': 'What each implemented finite diagnostic records on the sealed toy cohort; no algorithmic conclusion.',
               'inputs': [spec_rel, plan_rel, *source_hashes, *input_hashes],
               'constraints': ['Run only after genuine repository preapproval, committed Coordinator approval/archive, selector ready, and published live claim.',
                               'Use the unchanged repository supervisor and preserve every failed/null output.', 'Three module workers; driver plus at most three module processes; no nested module threads.'],
               'deliverables': required, 'artifact_paths': required,
               'completion_gate': ['Supervisor output-integrity receipt covers every declared artifact and all ten tracks, or a complete retained operational-failure receipt.'],
               'budget': {'maximum_runs': 1, 'maximum_workers': 4, 'memory_gb': 12},
               'inference': {'policy': 'executor-implementation', 'delivery': 'interactive', 'fallback_allowed': False, 'degraded_allowed': False},
               'execution': binding}
    handoff_preview = write(preview, 'handoff.yaml', {'handoff': handoff})
    archive_receipt = f'coordination/goals/{goal}/batches/{batch}/archives/{archive}/snapshot-receipt.json'
    archive_handoff = {'id': archive, 'from': 'coordinator', 'to': 'coordinator', 'role': 'coordinator',
          'objective': 'Archive the exact completed or failed observational batch without scientific interpretation.', 'uncertainty_reduced': 'Immutable source/output custody.',
          'inputs': required, 'constraints': ['Exact bytes and failed outcomes; isolated archive; no scientific transition.'],
          'deliverables': [archive_receipt], 'artifact_paths': [archive_receipt], 'completion_gate': ['Committed snapshot receipt and declared hashes verify.'],
          'budget': {'maximum_runs': 0}}
    queue = {'schema': 'crypto.autoresearch.dispatch_queue.v1', 'goal_id': goal, 'objective': 'Complete one ten-track classical finite observational pilot.', 'max_concurrent': 1,
       'tasks': [{'id': task, 'title': 'Execute the all-track pilot', 'role': 'executor', 'state': 'queued', 'priority': 90, 'review_required': False,
                  'depends_on': [], 'read_scope': [prefix+'/', spec_rel, plan_rel], 'write_scope': [run_base+'/'], 'artifact_paths': required,
                  'archived_by': archive, 'handoff': handoff},
                 {'id': archive, 'title': 'Archive the all-track observations', 'role': 'coordinator', 'state': 'queued', 'priority': 80, 'review_required': False,
                  'depends_on': [task], 'read_scope': [run_base+'/'], 'write_scope': [str(Path(archive_receipt).parent)+'/',], 'artifact_paths': [archive_receipt],
                  'archived_by': archive, 'handoff': archive_handoff, 'archive': {'kind': 'snapshot', 'source_task_ids': [task],
                      'commit_sha': None, 'parent_sha': None, 'path_sha256': {}, 'record_ids': [exp, ids['run']]}}]}
    queue_preview = write(preview, 'queue.json', queue)
    write(preview, 'archive-handoff.yaml', {'handoff': archive_handoff})
    decision = {'coordinator_decision': {'id': ids['approval_decision'], 'context': 'Prospective only until a genuine exact-byte preapproval pass and Coordinator archive.',
        'decision': 'approve', 'target_ids': [exp], 'rationale': ['Explicit user implementation/execution request and standing experiment authorization.',
          'Finite descriptive pilot with complete controls, hashes, output preservation, machine protection and no new attack claim.'],
        'evidence_refs': [], 'limitations': scientific['interpretation_limits'], 'next_actions': ['Require selector ready, publish a live executor claim, and execute via tools/experiment_execution.py.'],
        'knowledge_promotion': {'promoted': [], 'not_warranted': 'Approval is execution authority only; no observation or scientific finding exists yet.'},
        'decided_by': 'coordinator', 'decided_at': '2026-10-25', 'user_authorization': 'Current user explicitly requires implementing and running the programme; standing 2026-09-06 authorization.',
        'prospective_sha256': {'specification': sha(preview_spec), 'trial_plan': sha(preview_plan), 'queue': sha(queue_preview), 'handoff': sha(handoff_preview)}}}
    write(preview, 'approval-decision.yaml', decision)
    write(draft, goal_rel, {'research_goal': {'id': goal, 'title': 'Classical ECDLP finite programme instrumentation and observations',
        'objective': 'Implement and collect all ten finite diagnostics while preserving their construction gaps and scope.', 'question_ids': [ids['question']],
        'status': 'active', 'completion_criteria': ['The fixed exploratory pilot is source-bound, executed and its complete outputs reported.', 'Any proposed new solver remains a separate unresolved obligation.'],
        'pause_conditions': [], 'next_action': f'Finish source freeze and exact prospective admission for {exp}; then execute under its published claim.',
        'owner': 'coordinator', 'campaign_budget': {'maximum_runs': None, 'cpu_hours': None, 'wall_clock_seconds': None, 'max_concurrent': 1},
        'open_batches': [batch], 'impediments': [], 'claim_scope': 'No ECDLP algorithm or complexity claim.'}})
    write(draft, f'ledger/questions/{ids["question"]}.yaml', {'research_question': {'id': ids['question'], 'title': 'What do the ten finite classical lead diagnostics record?',
        'scope': scientific['scope'], 'status': 'open', 'owner': 'coordinator'}})
    write(draft, f'ledger/hypotheses/{ids["hypothesis"]}.yaml', {'hypothesis': {'id': ids['hypothesis'], 'question_id': ids['question'],
        'statement': 'The explicitly specified finite instruments can collect exact observations and calibrated references; no beneficial deviation is predicted.',
        'mechanism': 'Total Boolean/point arithmetic, rational finite identities, exact censuses and publicly computable diagnostic features.', 'status': 'proposed',
        'asymptotic_claim': None, 'interpretation_limits': scientific['interpretation_limits'], 'prior_art': {'lead': 'LEAD-EXO-ideas-corpus-algebraic-transforms', 'novelty': 'unverified; instruments use known methods'}}})
    lane_rel = f'coordination/goals/{goal}/lanes/{batch}.lane.json'
    write(draft, lane_rel, {'schema': 'crypto.autoresearch.goal_lane.v1', 'goal_id': goal, 'batch_id': batch,
        'dispatch_queue_path': queue_rel, 'write_scope': [f'coordination/goals/{goal}/batches/{batch}/'],
        'opened_by': 'coordinator-classical-pilot', 'opened_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'opening_decision_id': None, 'objective': 'Prepare and execute the explicit-user classical finite pilot.', 'branch': args.source_ref.removeprefix('origin/'),
        'session': 'classical-pilot-20261025', 'concurrent_open_lanes_at_open': []})
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
    p.add_argument('--source-prefix', default='harness/classical_ecdlp_pilot')
    p.add_argument('--source-ref', default='origin/plan/direct-ecdlp-cancellation-20261025')
    p.add_argument('--check-ids', action='store_true')
    prepare(p.parse_args())
