#!/usr/bin/env python3
"""Administrative binding comparisons only; no solver module is imported."""
import argparse, datetime, hashlib, json, platform, resource, subprocess, time
from pathlib import Path
import yaml

TASK = 'TASK-20260909-129bc2'
DECISION = 'DEC-20260909-b69851'
SNAPSHOT = '1c9b23b662dbe890c5b6e40a5a05979e15e079d0'
ORIGINAL = Path('experiments/EXP-ECDLP-709063/implementation/TASK-20260909-d31be5')
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('duplicate JSON key: ' + k)
        out[k] = v
    return out

def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--receipt', required=True)
    args = ap.parse_args()
    target = Path(args.receipt)
    if target.exists():
        raise FileExistsError('refuse existing attempt receipt')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock = time.monotonic()
    rows = []
    def check(name, fn):
        try:
            ok = fn()
            if ok is not True:
                raise AssertionError('comparison returned ' + repr(ok))
            rows.append({'name': name, 'status': 'passed'})
        except Exception as e:
            rows.append({'name': name, 'status': 'failed', 'error': type(e).__name__ + ': ' + str(e)[:2000]})
    try:
        b = load(HERE / 'solver-source-bindings.json')
        oldpath = REPO / ORIGINAL / 'solver-source-bindings.json'
        old = load(oldpath)
        hpath = REPO / 'ledger/handoffs' / (TASK + '.yaml')
        h = yaml.safe_load(hpath.read_text())['handoff']
        receipt = load(REPO / ORIGINAL / 'check-receipt.json')
        report = yaml.safe_load((REPO / ORIGINAL / 'implementation-report.yaml').read_text())['execution_report']
        phpath = REPO / 'ledger/handoffs/TASK-20260909-d31be5.yaml'
        ph = yaml.safe_load(phpath.read_text())['handoff']
        oldarchive = load(REPO / 'coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-7f5fe3/snapshot.json')
        rpath = REPO / 'coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-adf4e6/review.yaml'
        vr = yaml.safe_load(rpath.read_text())['validation_report']
        check('replacement_identity_and_correct_approval', lambda: b['task_id'] == TASK and b['approval_decision_id'] == h['approval_decision_id'] == DECISION and h['to'] == 'coordinator')
        check('closed_replacement_top_level', lambda: set(b) == {'schema','task_id','experiment_id','approval_decision_id','scope','supersedes','current_source','dependency_bindings','historical_scalar_baseline','historical_inherited_assertions','recorded_source_execution','independent_review','failed_predecessor','correction_preflight','scientific_runs','measurement_admitted','source_acceptance','new_metadata_review'} and b['schema'] == 'crypto.autoresearch.solver_source_bindings.v2')
        check('exact_superseded_document', lambda: b['supersedes']['path'] == str(ORIGINAL / 'solver-source-bindings.json') and b['supersedes']['sha256'] == sha(oldpath) and b['supersedes']['snapshot'] == SNAPSHOT)
        check('original_binding_still_matches_snapshot', lambda: git('show', SNAPSHOT + ':' + str(ORIGINAL / 'solver-source-bindings.json')) == oldpath.read_bytes())
        expected = {str(ORIGINAL / n) for n in ['table.py','bsgs.py','rho-corrected.py','tests.py']}
        current = b['current_source']['path_sha256']
        check('one_complete_current_source_map', lambda: set(current) == expected and b['current_source']['snapshot'] == SNAPSHOT and b['current_source']['source_task_id'] == 'TASK-20260909-d31be5')
        for p, digest in current.items():
            check('current_source_identity:' + p, lambda p=p, digest=digest: sha(REPO/p) == digest == receipt['source_sha256'][Path(p).name] == hashlib.sha256(git('show', SNAPSHOT + ':' + p)).hexdigest())
        for p, digest in oldarchive['source_path_sha256'].items():
            check('original_package_immutable:' + p, lambda p=p, digest=digest: sha(REPO/p) == digest == hashlib.sha256(git('show', SNAPSHOT + ':' + p)).hexdigest())
        for p, name in [(ORIGINAL/'bsgs.py','bsgs.py'),(ORIGINAL/'rho-corrected.py','rho-corrected.py')]:
            check('prior_kernel_preserved:' + name, lambda p=p, name=name: (REPO/p).read_bytes() == git('show','d8f64d928c8f6a28eed97eac70b741ad3232fbd5:experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2/' + name))
        fields = ['current_task_source_sha256','source_binding_preflight','validation_limitation','execution_policy']
        check('exact_historical_assertions_namespaced', lambda: b['historical_inherited_assertions']['values'] == {k:old[k] for k in fields} and b['historical_inherited_assertions']['origin'] == {'path':str(ORIGINAL/'solver-source-bindings.json'),'sha256':sha(oldpath)})
        check('no_competing_top_level_current_fields', lambda: not (set(fields+['task_source_sha256']) & set(b)))
        e = b['recorded_source_execution']
        check('original_execution_links', lambda: e['receipt']['path'] == str(ORIGINAL/'check-receipt.json') and e['receipt']['sha256'] == sha(REPO/e['receipt']['path']) and e['report']['path'] == str(ORIGINAL/'implementation-report.yaml') and e['report']['sha256'] == sha(REPO/e['report']['path']))
        check('original_execution_counts', lambda: e['checks'] == {'focused':6,'complete_suite':365,'total':371,'passed':371,'failed':0} and receipt['accounting']['total_fixed_cases'] == receipt['accounting']['passed'] == report['checks']['total'] == report['checks']['passed'] == 371 and receipt['accounting']['failed'] == report['checks']['failed'] == 0 and report['checks']['smoke'] == 6 and report['checks']['full_suite'] == 365)
        check('original_preflight_not_inherited_49', lambda: e['prior_handoff_declared_inputs'] == len(ph['inputs']) == 62 and e['prior_reported_source_bindings_verified'] == report['source_bindings_verified'] == 62)
        check('original_inference_uncertainty_preserved', lambda: e['inference_as_recorded'] == receipt['inference'] and e['inference_as_recorded']['resolved_model_id'] is None and e['inference_as_recorded']['model_verified'] is False and e['inference_as_recorded']['requested_policy'] == ph['inference']['policy'] == 'coordinator-orchestration-code' and e['hard_memory_guard_claim'] is False)
        check('authority_claim_snapshot_separate', lambda: e['authority_commit'] == report['authority_commit'] and e['published_claim_commit'] == report['published_claim_commit'] and e['archived_source_snapshot'] == SNAPSHOT and len({e['authority_commit'],e['published_claim_commit'],SNAPSHOT}) == 3)
        check('historical_scalar_baseline_preserved', lambda: b['historical_scalar_baseline'] == old['source_baseline'])
        deps=b['dependency_bindings'];pmap={x['path']:x['sha256'] for x in ph['source_bindings']}
        check('dependency_bindings_have_recorded_origin', lambda: deps['files'] == old['bound_files'] and deps['binding_origin'] == {'path':str(phpath.relative_to(REPO)),'sha256':sha(phpath)} and all(pmap[p] == v['sha256'] for p,v in deps['files'].items()))
        cf=b['correction_preflight'];frozen={x['path']:x['sha256'] for x in h['source_bindings']}
        check('correction_preflight_separate_and_complete', lambda: cf['declared_input_count'] == len(h['inputs']) == cf['verified_input_count'] == len(frozen) == 27 and cf['path_sha256'] == frozen and cf['handoff_sha256'] == sha(hpath) and cf['handoff_path'] == str(hpath.relative_to(REPO)))
        for p, digest in frozen.items():
            check('correction_input_unchanged:' + p, lambda p=p,digest=digest: sha(REPO/p) == digest)
        cpath='coordination/experiment-reserve/BATCH-635652/claims/' + TASK + '.1.claim.json'
        check('published_current_claim_binding', lambda: git('show',cf['published_claim_commit']+':'+cpath) == (REPO/cpath).read_bytes())
        check('current_authority_ancestry', lambda: subprocess.run(['git','merge-base','--is-ancestor',cf['authority_commit'],cf['published_claim_commit']],cwd=REPO).returncode == 0)
        check('prior_failed_review_retained', lambda: vr['verdict'] == b['independent_review']['overall_verdict'] == 'failed' and b['independent_review']['sha256'] == sha(rpath) and git('show',b['independent_review']['snapshot']+':'+str(rpath.relative_to(REPO))) == rpath.read_bytes())
        check('missing_predecessor_receipt_not_reconstructed', lambda: b['failed_predecessor']['state'] == 'failed' and b['failed_predecessor']['snapshot'] == '2e44076ebdadb9fac6bb21b9a12257e9d7a179cc' and b['failed_predecessor']['first_per_case_receipt'] == 'unavailable; not reconstructed')
        check('no_admission_or_scientific_claim', lambda: b['scientific_runs'] == 0 and b['source_acceptance'] is False and b['measurement_admitted'] is False and b['new_metadata_review'] == 'pending')
    except Exception as e:
        rows.append({'name':'administrative_checker_setup','status':'failed','error':type(e).__name__+': '+str(e)})
    ru=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    out={'schema':'crypto.autoresearch.binding_administrative_checks.v1','task_id':TASK,'started_at_UTC':started,'ended_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'administrative_comparisons':rows,'passed':sum(r['status']=='passed' for r in rows),'failed':sum(r['status']=='failed' for r in rows),'scientific_runs':0,'solver_module_imports':0,'binding_sha256':sha(HERE/'solver-source-bindings.json'),'checker_sha256':sha(__file__),'wall_seconds':time.monotonic()-clock,'self_cpu_seconds':ru.ru_utime+ru.ru_stime,'children_cpu_seconds':child.ru_utime+child.ru_stime,'self_peak_rss_raw':ru.ru_maxrss,'rss_units':'bytes' if platform.system()=='Darwin' else 'KiB','hard_memory_guard_claim':False}
    with target.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({'passed':out['passed'],'failed':out['failed'],'receipt':str(target)}))
    return 1 if out['failed'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
