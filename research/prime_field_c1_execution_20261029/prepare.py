"""Bind/freeze C1 before data; root authorization is an explicit later command."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from common import HERE, ROOT, F1, INPUTS, PARAMETERS, bindings, digest, git, write_once


def protocol_tools():
    spec = importlib.util.spec_from_file_location('_c1_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    binary = digest(Path(sys.executable).resolve())
    input_data = json.loads(INPUTS.read_text())
    metrics = [(name, description) for name, description in [
        ('cases_completed', 'Number of seven fixed cases completed with their required checks.'),
        ('complete_triple_cases', 'Number of four fixed triple cases with complete signed/state oracle equality.'),
        ('symmetric_states', 'Total rational symmetric states in completed triple cases.'),
        ('signed_solutions', 'Total distinct signed point decompositions in completed triple cases.'),
        ('controls_passed', 'Completed arity-four, nonseparable and corrupt-certificate control cases.'),
        ('unknown_cases', 'Cases absent or explicitly unknown; never interpreted as empty sets.')]]
    protocol = dict(schema='experiment.protocol/v1', protocol_id='P256-C1-CONTINUATION-20261029', version=1,
        created='2026-10-29', repository='crypto-autoresearcher', study_dir=str(HERE.relative_to(ROOT)),
        authors=['C1 execution-contract coordinator subagent; inherited model identity unverified'],
        links=dict(prior_task='TASK-20261026-a0cc5b', literature='literature.md', worklist='../prime_field_leads_20261028/PLAN.md'),
        question='Do the unchanged seven fixed F1 cases complete with the exact depth-four extractor, all multiplicity strata, and complete finite state/signed-point oracle checks?',
        claims=[dict(id='C1-exact', text='Completed fixed triple cases have exact symmetric-state and signed-point solution equality with the separate complete finite oracle; internal controls are retained individually.',
                     **{'class':'exact_computation'}, decided_by=['C-complete'])],
        arms=[dict(id='extractor', role='candidate',
            description='One execution of the whole seven-case fixed panel. The independent finite oracle is integrated validation, not a separately timed comparison arm.',
            instrument=dict(repo='crypto-autoresearcher', commit=commit,
                build=[[sys.executable, '-B', str(F1.relative_to(ROOT)/'driver.py'), '--max-dimension', '560', '--profile-stages']],
                binary_sha256=binary, flags={'profile_stages':'true'}, env={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}, threads=1),
            parameters=dict(**PARAMETERS, cases=[c['id'] for c in input_data['cases']], inputs_sha256=digest(INPUTS)))],
        controls=dict(
            aa=dict(present=False, comparison=None, not_applicable_reason='No noisy comparative primary metric; deterministic complete set equality is checked by a separate finite implementation.'),
            positive=dict(present=False, arm=None, expected_detection=None, not_applicable_reason='Embedded fixed depth-three/depth-four constructed positives and all five arity-four partitions exercise the actual extraction/recovery and complete oracle paths.'),
            negative=dict(present=False, arm=None, null_population=None, not_applicable_reason='Embedded nonseparable-fibre and corrupted-solution controls must be rejected. The public-generator cases have no assumed empty outcome. No statistical null population is claimed.')),
        variable_ledger=dict(independent=[dict(name='fixed_case',levels=[c['id'] for c in input_data['cases']]),
                                          dict(name='exact_method',levels=['extractor','finite_reference'])],
            factors=[dict(name='curve_base_targets_source',treatment='fixed',value='Exact original P-256 inputs and source bytes',how='Source/input locks, committed source, unchanged input hash and all strata.'),
                     dict(name='operator_guard',treatment='fixed',value=560,how='Guard before matrix allocation; no replacement targets or deeper fibre.'),
                     dict(name='threads',treatment='fixed',value=1,how='One compute process; OMP/OpenBLAS thread environment set to1; no throughput comparison.'),
                     dict(name='host',treatment='measured',how='Host facts, CPU/rusage/RSS and all diagnostic stage clocks retained. Shared host, wall_valid=false.'),
                     dict(name='case_order',treatment='fixed',value='Original input order',how='No timed comparison or success-dependent stop; guard/control failure retains the prefix.'),
                     dict(name='analysis',treatment='fixed',value='Unmasked exact cases',how='Analysis source frozen prospectively; no p-value or performance claim.')],
            comparisons=[dict(id='C-complete', arms=['extractor','finite_reference'], differs_in=['exact_method'], design='absolute', threshold='Complete state and signed-set oracle equality, positive cases retained, and refusal controls passed.')],
            aa_not_applicable='Exact deterministic set identities, no noisy comparative metric.', crosses_map=False),
        randomization=dict(arm_order='fixed',arm_order_reason='Extractor followed by finite oracle within each original fixed case; two method records share one supervised process and diagnostic resources, with no valid comparative clock.',
            seed_derivation=dict(method='explicit_list', seeds=[2026102601], nonce=None, note='Original fixed-input seed; no new draw or pilot.'),
            instance_sampling=dict(rule='The original seven-case panel is the sole instance0; no target substitutions.',independent_of_arm=True),
            blinding=dict(analysis_labels_masked=False,how='Public fixed case/control identities; exact descriptive equality only.',unmasked_at=None)),
        sample_size=dict(instances=1,replicates=1,warmups=0,
            power=dict(method='exact',alpha=0.05,tests_in_family=1,correction='none',rank_test_n=None,min_attainable_two_sided_p=None,passes=True,
                       note='Complete enumeration within each completed fixed case; no population power, rare-yield or statistical inference.'),
            preflight_runtime=dict(fixed_seconds=None,per_sample_seconds=None,threads=1,estimated_total_seconds=3600,
                                   measured_on='No affected P-256 computation has run.3600 seconds names the supervisor machine/process watchdog ceiling solely to satisfy the frozen-record engineering field; it is not a measured runtime, speed prediction or spend cap.')),
        metrics=dict(primary=[dict(id=name,name=name.replace('_',' '),unit='objects',kind='exact',definition=description,
            source='analysis.json metrics.'+name,aggregation='per_row',resolution='1',uncertainty='none_exact') for name, description in metrics],secondary=[]),
        measurement=dict(isolation_required='none',warmups=0,order='sequential',clock='counted',
            counters=['stratum.tensor.*','stratum.recovery.*'],
            record=['cpu_model','logical_cpus','memory_bytes','kernel','executable_sha256','source_commit','observed_git_head','git_dirty','source_unchanged_after','diagnostic_wall_cpu_rss','all stage events'],timed_primary_justification=None),
        execution=dict(backend='local',queue=None,measurement_class='search',timeout_seconds=3600,
            placement=dict(shared_managed_host=True,memory_bytes=2147483648,concurrent_compute_processes=1,isolated_clock_claim=False),
            checkpoint=dict(policy='none',interval_seconds=None,grace_seconds=None,restore_validation='none',after_restore=dict(wall_time='invalid',counted_units='valid')),
            retries=dict(infrastructure_only=True,max_attempts=1)),
        stopping_rules=[dict(rule='Exactly the original seven cases, no success-based stop or sample replacement.',kind='fixed_n',preregistered=True),
            dict(rule='A wrong certificate/control/source mutation invalidates the panel; retain all earlier files and mark later cases unknown.',kind='invalidation',preregistered=True),
            dict(rule='2GiB process memory guard and3600-second wall/CPU watchdog protect the machine; a stop is unknown, never mathematical emptiness.',kind='budget',preregistered=True)],
        invalidation_rules=['Oracle mismatch, changed source or failed control prevents a complete-panel observation.','Incomplete or absent cases remain unknown.','Diagnostic clocks are not isolated or valid performance evidence.'],
        decision_rule=dict(text='Report every case status, exact complete states/signed sets and native counters. No official scientific transition or performance claim. Stopped/failed cases are unresolved.',
            comparison_ids=['C-complete'],threshold='Exact oracle equality and retained controls.',statistic='Complete finite sets and exact object counts.',interval='none_exact',multiple_comparison_correction='none',effect_size_measure='not applicable; no comparative effect',verdict_vocabulary=['completed_within_scope','invalid_measurement','inconclusive']),
        analysis_plan=dict(script=dict(path='analyze.py',sha256=digest(HERE/'analyze.py')),inputs=['<run>/execution.json','<run>/raw/*.json'],outputs=['<run>/analysis.json','<run>/export.json'],blinded=False,frozen_before_data=True),
        reporting=dict(export_schema='experiment.export/v1',review_schema='experiment.review/v1',graphs=['Per-case exact states/solutions and control/status coverage; unknown separated.'],report_dir='reports/<fresh-run>/'),
        inadmissible=['Any execution before committed exact source, frozen protocol, real S3 checkpoint and explicit root release.','Any timed primary, natural-yield or attack-cost claim.','Replacing public targets, excluding slow cases, or interpreting unknown as empty.','Summing nested solver_total stage times with their child stages.'],
        literature=[dict(ref='https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',provenance='retrieved',claim='Membership representation does not remove relation solver and linear algebra costs.',verified_by='/root/c1_execution_contract,2026-10-29; retained primary PDF page8 read directly.'),
                    dict(ref='research/p256_factor_base_parallel_20261026/tracks/f1/{core,exterior,driver,profiled,reference}.py; literature.md',provenance='internal',claim='Exact prepared arithmetic, all multiplicity strata and complete finite validation; original frozen bytes unchanged.',verified_by='/root/c1_execution_contract,2026-10-29')],
        amendments=[],freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),
        extensions=dict(original_task='TASK-20261026-a0cc5b',export_unit='One method over the full fixed panel = one execution cell; two method records share a single physical process and internal seven cases. Shared costs must not be added or treated as independent replicates.',
            model_verified=False,model_identity=None,checkpoint_semantics='S3 source/resume backup and the real gate mandatory; no in-process restore; each retry uses fresh output and loses clock validity.',
            missing_costs=['FLINT internal elimination operation counts','calibrated complete S','matched optimized rho and IC costs'], official_status_transition=False))
    import copy
    reference = copy.deepcopy(protocol['arms'][0])
    reference.update(id='finite_reference',role='reference',description='Complete finite inverse-chain/resultant/point-sum oracle invoked after each candidate triple case, plus the shared control cases. Same physical process; no independent reference timing is claimed.',same_instrument_as='extractor')
    protocol['arms'].append(reference)
    return protocol


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action',required=True)
    proto = sub.add_parser('protocol')
    proto.add_argument('--source-commit',required=True)
    proto.add_argument('--out',type=Path,required=True)
    proto.add_argument('--freeze',action='store_true')
    proto.add_argument('--draft-preview',action='store_true')
    release = sub.add_parser('release')
    release.add_argument('--source-commit',required=True)
    release.add_argument('--protocol',type=Path,required=True)
    release.add_argument('--out',type=Path,required=True)
    release.add_argument('--owner',required=True)
    release.add_argument('--authorize-root',action='store_true',required=True)
    args = p.parse_args()
    tools = protocol_tools()
    if args.action == 'protocol':
        if args.freeze and args.draft_preview:
            raise ValueError('a draft preview cannot be frozen')
        if args.out.resolve().parent != HERE:
            raise ValueError('protocol belongs beside its pinned analysis source')
        if not args.draft_preview:
            bindings(args.source_commit)
        value = make_protocol(args.source_commit)
        errors = tools.schema_errors(value,'experiment.protocol/v1') or tools.lint_protocol(value,HERE)
        if errors:
            raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:
            tools.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,input_map = bindings(args.source_commit)
        protocol = json.loads(args.protocol.read_text())
        if protocol['freeze']['status'] != 'frozen' or protocol['freeze']['filed_before_affected_data'] is not True:
            raise ValueError('prospectively frozen protocol required')
        if protocol['freeze']['commit'] != args.source_commit or any(
                arm['instrument']['commit'] != args.source_commit for arm in protocol['arms']):
            raise ValueError('release source commit differs from frozen protocol instruments')
        errors = tools.schema_errors(protocol,'experiment.protocol/v1') or tools.lint_protocol(protocol,args.protocol.parent)
        if errors:
            raise ValueError(json.dumps(errors))
        relative = str(args.protocol.resolve().relative_to(ROOT))
        if subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT) != args.protocol.read_bytes():
            raise ValueError('protocol must already be committed unchanged')
        check = subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current (' not in check.stdout:
            raise ValueError('a prior actual canonical checkpoint of the current state is required')
        checkpoint = (ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):
            raise ValueError('canonical checkpoint receipt has unexpected shape')
        value = dict(schema='prime-field-c1-root-release/v1',execution_authorized=True,
            authority='Explicit root Phase B release under standing user authorization; no research-state promotion.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=input_map,
            interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],
            checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=3600,
            package_versions={name:importlib.metadata.version(name) for name in ['python-flint','sympy','jsonschema','PyYAML']},
            issued_utc=datetime.now(timezone.utc).isoformat(),model_verified=False,model_identity=None)
        write_once(args.out,value)
        print(json.dumps(dict(release=str(args.out),owner=args.owner,execution_authorized=True)))


if __name__ == '__main__':
    main()
