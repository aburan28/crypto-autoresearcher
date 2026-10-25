#!/usr/bin/env python3
"""Render only the published partial615fcf native observation."""
from datetime import datetime
from pathlib import Path
import hashlib,json,shutil,subprocess

ROOT=Path('/workspace/crypto-autoresearcher')

def tex(s):
    d={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(d.get(c,c) for c in str(s))

def main():
    exp='EXP-ECDLP-615fcf';rid='RUN-ECDLP-7f3a18';run=ROOT/'experiments'/exp/'runs'/rid
    read=lambda name:json.loads((run/name).read_text())
    receipt=read('execution-receipt.json')
    archive=subprocess.check_output(['git','log','-1','--format=%H','--',str((run/'execution-receipt.json').relative_to(ROOT))],cwd=ROOT,text=True).strip()
    refs=subprocess.check_output(['git','for-each-ref','--contains='+archive,'--format=%(refname)','refs/remotes/origin/'],cwd=ROOT,text=True).splitlines() if archive else []
    if not archive or not refs:raise RuntimeError('Actual partial raw archive must be published first')
    plan=json.loads((ROOT/'experiments'/exp/'trial-plan.json').read_text())
    primary=read('primary-output.json');check=read('independent-check.json')
    elapsed=(datetime.fromisoformat(receipt['finished_at'])-datetime.fromisoformat(receipt['started_at'])).total_seconds()
    trial=next(t for t in plan['trials'] if t['run_id']==rid)
    stamp=datetime.fromisoformat(receipt['started_at']).strftime('%Y%m%dT%H%MZ')
    out=ROOT/'experiments'/exp/'reports'/('run-'+stamp);out.mkdir(parents=True,exist_ok=False)
    launch=read('launch.json')
    data={'experiment_id':exp,'run_id':rid,'run_path':str(run.relative_to(ROOT)),'hypothesis_id':plan.get('hypothesis_id'),'goal_id':plan.get('goal_id'),'source_experiment':'EXP-ECDLP-c9110e','raw_archive_commit':archive,'origin_tracking_refs':refs,'native_receipt':receipt,'primary_output':primary,'raw_result':read('raw-result.json'),'native_primary':read('native-primary.json'),'independent_check':check,'environment':read('environment.json'),'launch':launch,'check_stderr_unchanged':(run/'check.stderr.log').read_text(),'actual_files':sorted(p.name for p in run.iterdir()),'missing_driver_outputs':[name for name in trial['artifacts'] if not(run/name).exists()],'native_elapsed_seconds_derived':elapsed,'canonical_timing_resources':None,'not_launched_primary_route_b':'RUN-ECDLP-f8d192','scope':'Partial arithmetic/control observations retained; native output invalid, no complete two-primary-route measurement or scientific verdict.'}
    (out/'report-data.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    (out/'command.json').write_text(json.dumps({'supervisor_argv':['python3','tools/experiment_execution.py','run','--plan','experiments/EXP-ECDLP-615fcf/trial-plan.json','--owner',receipt['authority']['owner'],'--epoch',str(receipt['authority']['epoch'])],'outer_environment_prefix':{},'native_driver_argv':launch['argv'],'native_checker_argv':launch['check_argv']},indent=2)+'\n')
    observations={k:v for k,v in primary.items() if k not in ['points','commuting_points']}
    (out/'observations.json').write_text(json.dumps({'partial_primary_observations':observations,'independent_check_measurement_valid':check['measurement_valid'],'independent_check_route_agreement':check['route_agreement'],'independent_check_prediction_match':check['prediction_match'],'boundary':'Independent checker computation is not a separately allocated second primary run.'},indent=2,sort_keys=True)+'\n')
    dot='digraph failure { graph[rankdir=LR,bgcolor=white,fontname="Helvetica"];node[shape=box,style="rounded,filled",fillcolor="#edf2f7",fontname="Helvetica",fontsize=10];a[label="Primary route A\\nCompiled arithmetic completed"];b[label="Independent checker arithmetic\\nControls/route agreement true"];c[label="Metadata Git status failed\\nNo manifest; invalid_output",fillcolor="#fee8d5"];a->b->c;label='+json.dumps(exp+' / '+rid)+';labelloc=t;}\n'
    (out/'pipeline.dot').write_text(dot)
    for fmt in ['svg','png']:subprocess.run(['dot','-T'+fmt,'pipeline.dot','-o','pipeline.'+fmt],cwd=out,check=True)
    summary=f"Two primary routes were requested. Route A driver exited 0 and the checker exited 1; native status is invalid_output. Thirteen real files are preserved; manifest.yaml was never emitted. Dependent primary route B RUN-ECDLP-f8d192 was not launched. Native elapsed {elapsed:.6f} seconds is derived as finished_at minus started_at. The primary and independent checker compiled and ran arithmetic; the checker then failed in metadata git status with threaded-lstat resource error 128."
    boundary='The independent-check artifact records measurement_valid:true, route_agreement:true and prediction_match:true for the observed primary transcript. This is not the second primary RUN and does not make the native trial valid. Canonical whole-driver timing/resources and certificate fields are unavailable because there is no manifest; actual per-subprocess argv/CPU/wall/RSS observations remain in native-primary.json and independent-check.json. No missing measurement is replaced by zero.'
    limits='The fixed scientific source is the generalized curve y^2=x(x^2+8x+2) over F11; no source parameter was edited. All readings are deterministic in-sample calibration, with no uncertainty interval, attack-cost claim, hypothesis verdict or formal certificate. A prospective process-local Git thread setting may be recorded for future fresh runs; it was not applied to this attempt. The failed slot and unlaunched dependent identity remain untouched.'
    graphs='Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment frozen specification. No scientific graph/status changes follow. A stopping-point diagram is used because only one primary route ran and metadata failed.'
    (out/'report.md').write_text(f"# Partial native execution: {exp}\n\n{data['scope']}\n\nRun `{rid}`; source `EXP-ECDLP-c9110e`; hypothesis `{data['hypothesis_id']}`; goal `{data['goal_id']}`. Raw archive `{archive}`.\n\n{summary}\n\nExact checker stderr:\n\n```text\n{data['check_stderr_unchanged']}```\n\n{boundary}\n\nRecorded partial observations:\n\n```json\n{(out/'observations.json').read_text()}```\n\n{limits}\n\n{graphs}\n\nExact [commands](command.json), full raw/source/provenance/resource data [report-data.json](report-data.json), [diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: `{data['run_path']}` native receipt/logs, primary-output.json, raw-result.json, native-primary.json, independent-check.json and certificate.yaml. The latter is an instrument witness, not a mathematical certificate.\n")
    doc=r'''\documentclass[10pt]{article}
\usepackage[margin=17mm]{geometry}
\usepackage{graphicx,listings}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible}
\begin{document}
\section*{'''+tex('Partial native execution: '+exp)+r'''}
'''+tex(data['scope'])+r'''\par\medskip
'''+tex('Run '+rid+'; source EXP-ECDLP-c9110e; hypothesis '+str(data['hypothesis_id'])+'; goal '+str(data['goal_id'])+'.')+r'''\par
'''+tex('Raw archive '+archive+'.')+r'''\par\medskip
'''+tex(summary)+r'''\par\medskip
'''+tex('Exact checker stderr: '+data['check_stderr_unchanged'])+r'''\par\medskip
'''+tex(boundary)+r'''\par\medskip
\begin{center}\includegraphics[width=\linewidth]{pipeline.png}\end{center}
'''+tex(limits)+r'''\par\medskip
'''+tex(graphs)+r'''\par\medskip
'''+tex('Full actual commands, source/environment/receipt hashes and subprocess timing/resources remain in command.json/report-data.json and ../../runs/'+rid+'. The existing certificate.yaml is only an instrument witness.')+r'''
\newpage
\section*{Recorded partial observations}
\lstinputlisting{observations.json}
\end{document}
'''
    (out/'report.tex').write_text(doc);shutil.copy2(__file__,out/'render.py');(out/'.gitignore').write_text('build/\n');(out/'build').mkdir()
    r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','report.tex'],cwd=out,capture_output=True,text=True)
    (out/'render.stdout.log').write_text(r.stdout);(out/'render.stderr.log').write_text(r.stderr);r.check_returncode();shutil.copy2(out/'build/report.pdf',out/'report.pdf')
    subprocess.run(['pdftotext','report.pdf','extracted.txt'],cwd=out,check=True)
    subprocess.run(['pdftoppm','-scale-to','1600','-png','report.pdf','build/page'],cwd=out,check=True,capture_output=True)
    print(out)

if __name__=='__main__':main()
