#!/usr/bin/env python3
"""Administrative report builder for root-owned TASK-20261029-cbafca.

No experiment/host verifier/reference/SDK import or invocation. Call only after
root reports the existing source postrun terminated. Outputs are fresh outside
packages; canonical writes/publication remain root-owned. Original source
reports, exports, receipts and native statuses remain exact.
"""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, math, os, shutil, subprocess, sys

E='experiments/EXP-ECDLP-080f41'
RUN=E+'/runs/RUN-ECDLP-939237'
SOURCE=E+'/postrun-from-view-346631'
BATCH='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7'
VIEW=BATCH+'/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1'
CUSTODY=E+'/postrun/custody'
MAX_JSON=64<<20

def need(v,msg):
    if not v: raise ValueError(msg)

def unique(pairs):
    d={}
    for k,v in pairs:
        need(k not in d,'duplicate JSON key');d[k]=v
    return d

def badfloat(x):raise ValueError('nonfinite JSON')
def read(path):
    p=Path(path);need(p.is_file() and not p.is_symlink() and p.stat().st_size<=MAX_JSON,'bounded regular JSON input '+str(p))
    return json.loads(p.read_bytes(),object_pairs_hook=unique,parse_constant=badfloat)

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def encode(d):return (json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def fresh(path,data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)

def optional(root,name):
    p=root/name
    return read(p) if p.is_file() else None

def desc(path,logical=None):
    p=Path(path);need(p.is_file() and not p.is_symlink(),'regular file required')
    return {'path':logical or str(p),'sha256':sha(p),'bytes':p.stat().st_size}

def finished(path):
    d=read(path)
    need(d.get('task_id')=='TASK-20261029-cbafca','wrong completion task')
    need(type(d.get('returncode')) is int and isinstance(d.get('finished_at'),str),'actual source completion required')
    need(d.get('candidate_or_VM_invocation') is False,'source completion scope')
    ended=datetime.datetime.fromisoformat(d['finished_at']);need(ended.tzinfo is not None,'timezone-aware actual finish required')
    expected=['harness/classical_ecdlp_controlled_followup/postrun/run_postrun.py','--destination',SOURCE]
    argv=d.get('argv',[])
    need(expected[0] in argv and argv[-2:]==expected[-2:],'unexpected source command')
    return d

def load_metadata(repo):
    repo=Path(repo).resolve();launch=read(repo/RUN/'launch.json');native=read(repo/RUN/'execution-receipt.json');env=read(repo/RUN/'environment.json');raw=read(repo/RUN/'raw-result.json');protocol=read(repo/E/'protocol.json')
    need(launch['started_at']==native['started_at'],'native timestamp mismatch')
    stamp=datetime.datetime.fromisoformat(launch['started_at']).astimezone(datetime.timezone.utc).strftime('%Y%m%dT%H%MZ')
    need(stamp=='20261029T2258Z','actual native timestamp changed')
    need(native['status']=='invalid_output' and native['returncode']==0 and native['check_returncode']==1 and native['published'] is False,'original native status changed')
    controller=raw['controller'];view=read(repo/VIEW/'view-provenance.json')
    return {'launch':launch,'native':native,'environment':env,'controller':controller,'protocol':protocol,'view':view,'native_report_directory':E+'/reports/run-'+stamp}

def calibration_observations(value):
    if value is None:return None
    out=[]
    for curve in value['curves']:
        if curve.get('stage') not in ['discovery','validation']:continue
        for arm,v in curve['arms'].items():
            n=v.get('n');signed=v.get('score_sum');corr=v.get('correlation')
            need(type(n) is int and type(signed) is int and corr=={'numerator':signed,'denominator':n},'calibration numerator/denominator drift')
            # Missing zero-valued categories may be absent in source Counter output;
            # only this algebraic consistency check uses their mathematical zero.
            correct=v.get('correct',0);wrong=v.get('wrong',0);undefined=v.get('undefined',0)
            need(all(type(x) is int and x>=0 for x in [correct,wrong,undefined]),'calibration state counts')
            need(n==correct+wrong+undefined and signed==correct-wrong,'calibration state arithmetic')
            out.append({'curve_id':curve['curve_id'],'stage':curve['stage'],'arm_id':arm,'signed_numerator':signed,'retained_n':n,'correct':correct,'wrong':wrong,'undefined':undefined,'complete_1800':n==1800,'reported_score':{'numerator':signed,'denominator':n},'score_grid_not_uncertainty':True})
    return out

def collect(repo,completion):
    repo=Path(repo).resolve();meta=load_metadata(repo);source=repo/SOURCE
    result=optional(source,'postrun-result.json');analysis=optional(source,'analysis.json');partial=optional(source,'partial-analysis.json');verification=optional(source,'verification.json');export=optional(source,'export.json');validation=optional(source,'export.validation.json');cal=optional(source,'calibration.json');refs=optional(source,'references.json')
    observed=analysis if analysis is not None else partial
    cellrows=None if observed is None else observed.get('per_curve_six_cell')
    bsgs=None
    if refs is not None:
        records=[t for c in refs['curves'] for t in c.get('bsgs_targets',[])]
        bsgs={'retained_target_records':len(records),'status_counts':{state:sum(t['bsgs']['status']==state for t in records) for state in sorted({t['bsgs']['status'] for t in records})},'scope':'Source-generated independent BSGS entries; full cold/warm setup/online vectors remain in references.json. No timing claim.'}
    sourcefiles=[desc(p,p.relative_to(repo).as_posix()) for p in sorted(source.rglob('*')) if p.is_file() and not p.is_symlink()]
    verification_checked=verification is not None and verification.get('status')=='checked'
    return {'schema':'classical.ecdlp.native-run-report-observations/v1','task_id':'TASK-20261029-cbafca','experiment_id':'EXP-ECDLP-080f41','run_id':'RUN-ECDLP-939237','goal_id':'GOAL-ECDLP-e70832','hypothesis_id':'H-ECDLP-6674c9','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_report_directory':meta['native_report_directory'],'native_trial':meta['native'],'native_dirty_tree_state':meta['environment'].get('dirty_tree','unknown'),'native_environment':meta['environment'],'launch':meta['launch'],'controller':{k:meta['controller'].get(k) for k in ['status','sandbox_id','vm_creates','engine_execs','engine_returncode','collection_complete','uid1000_quiescent','termination_ack']},'derived_view':{'path':VIEW,'manifest_sha256':meta['view']['derived_manifest_sha256'],'provenance_sha256':sha(repo/VIEW/'view-provenance.json'),'original_native_status':meta['view']['native_status_unchanged']},'host_postrun_command':completion,'host_postrun_status':None if result is None else result.get('status'),'host_postrun_errors':None if result is None else result.get('errors'),'host_verification':verification,'host_verification_checked':verification_checked,'unified_export_validation':validation,'unified_export_flow':None if export is None else export.get('flow'),'logical_evaluator_rows':None if export is None else [{'run_id':r['run_id'],'arm':r['arm'],'instance_id':r['instance_id'],'replicate':r['replicate'],'status':r['status'],'measurements':{'counted':r['measurements']['counted'],'wall_valid':r['measurements']['wall_valid'],'wall_seconds':r['measurements']['wall_seconds'],'cpu_user_seconds':r['measurements']['cpu_user_seconds'],'cpu_sys_seconds':r['measurements']['cpu_sys_seconds'],'max_rss_bytes':r['measurements']['max_rss_bytes']},'recorded_component_counters':{k:v for k,v in r['measurements']['counters'].items() if k!='observed_trace_ids_json'},'verification':r.get('verification'),'exclusion':r.get('exclusion')} for r in export['runs']],'source_analysis_kind':'complete' if analysis is not None else ('partial' if partial is not None else 'missing'),'coverage':None if observed is None else observed.get('coverage'),'per_curve_six_cell':cellrows,'paired_discordants_t0e0_t1e2':None if observed is None else observed.get('paired_discordants_t0e0_t1e2'),'calibration':calibration_observations(cal),'BSGS':bsgs,'source_files':sourcefiles,'controls':meta['protocol']['controls'],'qualifications':{'calibration_resolution_field':'NOT QUALIFIED: frozen1/512 label disagrees with all1800draw definition; actual signed numerator/allretainedn and undefined counts retained. Grid is not uncertainty.','curve_is_population_unit':True,'six_cells_share_confirmation_trace':True,'paired_evaluators_share_ONE_native_VM':True,'native_status_is_not_rewritten':True,'wall_valid':False,'counter_replay_qualified':False,'unmetered':['nativeRSS','interpreterallocations','I/O','Pythonintegerinternals'],'scientific_conclusion':None}}

def text(v):return 'missing' if v is None else json.dumps(v,sort_keys=True,allow_nan=False)
def display(v):return 'missing' if v is None else str(v)

def write_report(repo,completion_path,package):
    repo=Path(repo).resolve();completion=finished(completion_path);d=collect(repo,completion);package=Path(package).resolve();need(not package.exists(),'fresh outside package required');need(not package.is_relative_to(repo),'outside package required');package.mkdir(parents=True)
    report=package/d['native_report_directory'];report.mkdir(parents=True)
    fresh(report/'observations.json',encode(d));drawing=Path(__file__).with_name('draw_observations.py');fresh(report/'draw_observations.py',drawing.read_bytes())
    python=sys.executable;draw=[python,str(report/'draw_observations.py'),'--data',str(report/'observations.json'),'--svg',str(report/'observations.svg')];r=subprocess.run(draw,capture_output=True,text=True);fresh(package/'drawing.command.json',encode({'argv':draw,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}));need(r.returncode==0,'native graph rendering failed')
    n=d['native_trial'];c=d['controller'];v=d['host_verification'];validation=d['unified_export_validation'];coverage=d['coverage'];cal=d['calibration'];rows=d['logical_evaluator_rows'];BSGS=d['BSGS'];nativeDIR=d['native_report_directory']
    lines=['# Controlled classical ECDLP run observations','','EXP-ECDLP-080f41 / RUN-ECDLP-939237 / GOAL-ECDLP-e70832 / H-ECDLP-6674c9. Observations only; this report changes no scientific status.','',f"One physical candidate VM was retained. Native supervisor status remains `{n['status']}` (driver{n['returncode']}, checker{n['check_returncode']}, publishedfalse) after a JSON/YAML manifest serialization refusal. The separately derived complete read-only JSON representation passed independent compatibility/custody validation. Host postrun returned{completion['returncode']}, source status `{d['host_postrun_status']}`. These distinct statuses remain recorded.",'','## Recorded process and coverage','','| Quantity | Recorded value |','| --- | --- |',f"| Native first-trial start UTC | {n['started_at']} |",f"| Native terminal UTC | {n['finished_at']} |",f"| VM creates / candidate engine executions | {c['vm_creates']} / {c['engine_execs']} |",f"| Engine returncode / controller status | {c['engine_returncode']} / {c['status']} |",f"| Collection / UID1000 quiescence / actual termination ACK | {c['collection_complete']} / {c['uid1000_quiescent']} / {c['termination_ack']['acknowledged']} |",f"| Native source authority | `{n['authority']['commit']}` |",f"| Native dirty-tree field | {d['native_dirty_tree_state']} |",f"| Host verifier | {display(None if v is None else v['status'])} |",f"| Host observed row counts | `{text(None if v is None else v['observed'])}` |",f"| Unified export flow | `{text(d['unified_export_flow'])}` |",f"| Retained analysis counts | `{text(None if coverage is None else {k:coverage[k] for k in ['retained_curves','retained_physical_trace_records','retained_decoder_cells','retained_curve_cell_pairs']})}` |",'','The graph displays every retained curve/cell row from the source analysis, with separate confirmationA/B panels. Six decoder cells share traces; paired original/incremental evaluator aggregates share the same single VM. Missing outcomes remain missing. The plotted fractions are labelled arithmetic on recorded successes and attempts, with no new interval, p-value or fit.','', '![Retained decoder observations](observations.svg)','','## Logical evaluator rows','']
    if rows is None:lines.append('Source export is missing; no evaluator row is invented.')
    else:
        for row in rows:lines.extend([f"- `{row['run_id']}` / `{row['arm']}` / `{row['instance_id']}` / replicate{row['replicate']}: status`{row['status']}`; recorded measurements `{text(row['measurements'])}`."])
    lines.extend(['','## Calibration and references','',f"Calibration arm records: {display(None if cal is None else len(cal))}. Exact signed numerators, actual all-draw denominators, correct/wrong/undefined counts and complete1800flags are preserved in observations.json. The frozen1/512resolution literal is NOTQUALIFIED for calibration. Undefined draws remain in the denominator. A score grid is not uncertainty.",f"BSGS source summary: `{text(BSGS)}`.",'The source calibration/error-erasure histograms, conditional matched-M nonzero uniform streams, mask orientations/support/duplicates/ties, BSGS cold/warm vectors and all setup/common/query/list/public-verification components remain in the unchanged source files. Their scopes and missing/partial states are retained there. M0 means zero reference guesses; common/setup/M-determination work remains charged.','','## Registered controls and uncertainty','',f"Frozen controls/excuses: `{text(d['controls'])}`.",'Fresh A/A, positive-arm and inferential-negative outcomes are not inferred from source fixtures, bridge controls or host references. Curve is the population unit. Source-provided zero-event bounds, when present, retain their stated fixed-curve restart assumption; nonzero fractions are descriptive. No curve-population interval, exchangeable-null p-value or exponent fit is added.','','## Failures, representation and scope','',f"Host source errors: `{text(d['host_postrun_errors'])}`.",f"Unified export validation: `{text(validation)}`.",'The original native YAML, receipt, checker traceback, raw archive and all51native files remain unchanged. The fullJSONview preserves all supervisor fields/types and has explicit storage/source mapping; independent TASK-20261029-3b5feb checked10positive conditions/48mutant refusals and ordinary full C4 check. This is representation/custody qualification, separate from host verification.',f"Derived manifestSHA256 `{d['derived_view']['manifest_sha256']}`; view-provenanceSHA256 `{d['derived_view']['provenance_sha256']}`.",'Native elapsed orchestration is not algorithm timing. Wall clocks, actual VM isolation and independent native worker counter replay remain unqualified; nativeRSS, interpreter allocations, I/O and Python integer internals are unmetered. Source component counts remain separate and carry no mixed total or attack-cost ratio. No scientific verdict is added.','','## Source, command, seed and provenance','',f"Native environment: `{text(d['native_environment'])}`.",f"Actual native argv: `{text(d['launch']['argv'])}`.",f"Actual host postrun command: `{text(completion)}`.",'Candidate public nonce is retained in the sealed native cohort/nonce records. Any source host seed is retained only if the source emitted it after full authenticated workload verification, collection seal/readback, quiescence and actual termination acknowledgement. This report draws no entropy.',f"Actual source output root: `{SOURCE}`. Original source-created reports/export/validation remain unchanged. Any experiment-root export is a new separately rebased derivative with its own actual file-check record.",'Exact source hashes/bytes: observations.json. Prelaunch calibration qualification, later Coordinator assessment, point-in-time root resources and actual commands/failures are separately indexed in postrun custody. The native dirty field is unknown; external earlier clean-tree observations do not fill that native field.','This local graph records this run only. Canonical research graphs are unchanged: no scientific status or graph-supported mathematical finding is changed by this producer report.','', 'Procedural primary sources read: AGENTS.md; docs/agent-contract-extended.md (literature/observation rules); agents/executor.md; run and research-visuals skills; effective cbafca card; frozen protocol/output contract; fullnativeJSONbridge contract/addendum; source postrun/analysis/renderer/reference. Provenance internal. No external paper or novelty search was needed for this administrative reporting task; no scientific novelty claim or model probe is made.'])
    fresh(report/'report.md',('\n'.join(lines)+'\n').encode())
    # A concise PDF keeps the quantitative graph and explicit complete links;
    # report.md and observations.json retain the complete native report data.
    def lit(x):return json.dumps(str(x),ensure_ascii=False)
    typ=['#set page(paper:"a4",margin:(x:17mm,y:16mm),numbering:"1")','#set text(font:"DejaVu Sans",size:9.2pt)','#set par(leading:0.55em)','#set heading(numbering:none)','= Classical ECDLP run observations','*EXP-ECDLP-080f41 / RUN-ECDLP-939237* \\','GOAL-ECDLP-e70832 · H-ECDLP-6674c9 · TASK-20261029-cbafca','', 'Observations only; no scientific status transition. One actual candidate VM. The original native invalid_output/check1/publishedfalse is preserved. A separate complete readonlyJSONview passed independent representation/custody validation before this host analysis.','', '#table(columns:(1.25fr,1.75fr),inset:4pt,align:left,','[*Recorded quantity*],[*Actual value*],',f'[{lit("Native start / finish UTC")}],[{lit(n["started_at"]+" / "+n["finished_at"])}],',f'[{lit("Native driver / checker / status")}],[{lit(str(n["returncode"])+" / "+str(n["check_returncode"])+" / "+n["status"])}],',f'[{lit("VM creates / engine executions / engine RC")}],[{lit(str(c["vm_creates"])+" / "+str(c["engine_execs"])+" / "+str(c["engine_returncode"]))}],',f'[{lit("Collection / quiescence / ACK")}],[{lit(str(c["collection_complete"])+" / "+str(c["uid1000_quiescent"])+" / "+str(c["termination_ack"]["acknowledged"]))}],',f'[{lit("Native dirty field")}],[{lit(d["native_dirty_tree_state"])}],',f'[{lit("Host RC / source status / verifier")}],[{lit(str(completion["returncode"])+" / "+str(d["host_postrun_status"])+" / "+display(None if v is None else v["status"]))}],',f'[{lit("Host observed row counts")}],[{lit(text(None if v is None else v["observed"]))}],',')','', '#image("observations.svg",width:100%)','', 'Every retained source-analysis curve/cell row is plotted. Six cells share each confirmation trace; the two evaluator aggregates share one physical VM. Fractions are recorded successes divided by recorded attempts. Missing values are not filled. No new interval, p-value or fit.','#pagebreak()','= Recorded outcomes, references and controls',f'Calibration arm records: {display(None if cal is None else len(cal))}. Exact signed numerators, actual retained n, undefined counts and complete1800flags are in observations.json. *Frozen1/512calibrationresolution is NOTQUALIFIED.* Undefined draws remain in the denominator; score grid is not uncertainty.','',f'BSGS source summary: #text({lit(text(BSGS))})','', 'Full original/incremental metrics, all six retained cells, error/erasure histograms, source null/support/duplicates/ties, nonzero matched-M uniform streams and BSGS cold/warm/setup/online vectors remain in the unchanged source outputs linked by path/hash. M0 has zero reference guesses, while common/setup/M-determination work remains paid.','',f'Host errors: #text({lit(text(d["host_postrun_errors"]))})','',f'Unified export validation: #text({lit(text(validation))})','', 'The protocol records absent fresh A/A, positive-arm and inferential-negative controls with descriptive-scope excuses. Prior source fixtures, bridge corruption controls and host references do not become fresh detector/noise-floor outcomes. Curve is the population unit. Source zero-event bounds keep their stated fixed-curve assumption; nonzero fractions are descriptive. No population interval, exchangeable-null p-value or exponent fit is added.','', 'Native clocks/isolation and independent native worker counter replay remain unqualified. NativeRSS, allocations, I/O and integer internals are unmetered. Worker/host/setup/common/list components remain separate. This report adds no attack-cost, speedup or scientific verdict.','#pagebreak()','= Provenance and preservation',f'Native source authority: #text({lit(n["authority"]["commit"])})','',f'Derived fullnativeJSONmanifest SHA256: #text({lit(d["derived_view"]["manifest_sha256"])})','',f'View provenance SHA256: #text({lit(d["derived_view"]["provenance_sha256"])})','', 'Independent TASK-20261029-3b5feb checked five representation/custody joints, ten positive conditions and 48 refused mutants. Unchanged full C4 check passed. All51originalnative bytes/modes remain exact; original failure and later host analysis stay distinct.','',f'Native report path: #text({lit(nativeDIR)})','',f'Unchanged source postrun path: #text({lit(SOURCE)})','', 'Complete report prose: report.md. Exact observations, native command/environment/status, final host command, source output paths/bytes/SHA256 and controls/excuses: observations.json. Editable graph: draw_observations.py plus observations.json; rendering observations.svg. Editable PDF source: report.typ. Exact prelaunch qualification and later Coordinator assessment are retained separately in postrun custody, with original timestamps; no retrospective prelaunch claim is created.','', 'Public candidate nonce and any host seed stay in their source custody; the host seed is emitted only after the source authenticated full workload/seal/readback/quiescence/ACK gate. This report draws no entropy. Original source reports/export/checks remain unchanged. Experiment-root derivative paths/checks, if produced, are new records.','', 'Source environment Python/platform and exact argv are retained in observations.json. Native dirty field remains unknown; earlier separate root point-in-time facts do not fill it. This producer report changes no canonical mathematical graph.','', 'Sources/provenance: internal primary protocol/output/bridge contracts; task card; AGENTS and observation/literature rules; Executor/run/research-visuals; source postrun/analysis/renderer/reference. This administrative task performs no external novelty search, model probe, scientific sample or rerun.']
    fresh(report/'report.typ',('\n'.join(typ)+'\n').encode())
    import typst
    typst.compile(str(report/'report.typ'),output=str(report/'report.pdf'))
    files=[desc(p,p.relative_to(package).as_posix()) for p in sorted(report.iterdir()) if p.is_file()]
    delivery={'schema':'classical.ecdlp.native-report-prepared/v1','task_id':'TASK-20261029-cbafca','package_directory':str(package),'native_directory':nativeDIR,'files':files,'source_completion':desc(completion_path),'original_source_unchanged':True,'original_native_status_unchanged':True,'PDF_inspection':'pending actual allpage inspection; no inspection pass claimed','storage_conversion':'pending root actual policy publication; indexes must finalize afterward'}
    fresh(package/'native-report-delivery.json',encode(delivery));print(json.dumps(delivery,indent=2));return delivery

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--completion-record',type=Path,required=True);p.add_argument('--package',type=Path,required=True);a=p.parse_args();write_report(a.repo,a.completion_record,a.package)
if __name__=='__main__':main()
