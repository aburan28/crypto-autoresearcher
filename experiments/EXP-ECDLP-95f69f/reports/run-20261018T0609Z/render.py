#!/usr/bin/env python3
"""Descriptive rendering of the immutable pre-science invocation failure."""
from datetime import datetime
from pathlib import Path
import hashlib,json,shutil,subprocess
import yaml

ROOT=Path('/workspace/crypto-autoresearcher')

def tex(value):
    d={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(d.get(c,c) for c in str(value))

def main():
    exp='EXP-ECDLP-95f69f';rid='RUN-ECDLP-f67842'
    run=ROOT/'experiments'/exp/'runs'/rid
    receipt=json.loads((run/'execution-receipt.json').read_text())
    archive=subprocess.check_output(['git','log','-1','--format=%H','--',str((run/'execution-receipt.json').relative_to(ROOT))],cwd=ROOT,text=True).strip()
    refs=subprocess.check_output(['git','for-each-ref','--contains='+archive,'--format=%(refname)','refs/remotes/origin/'],cwd=ROOT,text=True).splitlines() if archive else []
    if not archive or not refs:raise RuntimeError('Partial raw run must be published before its report')
    plan=json.loads((ROOT/'experiments'/exp/'trial-plan.json').read_text())
    trial=next(t for t in plan['trials'] if t['run_id']==rid)
    launch=json.loads((run/'launch.json').read_text())
    stamp=datetime.fromisoformat(receipt['started_at']).strftime('%Y%m%dT%H%MZ')
    out=ROOT/'experiments'/exp/'reports'/('run-'+stamp);out.mkdir(parents=True,exist_ok=False)
    elapsed=(datetime.fromisoformat(receipt['finished_at'])-datetime.fromisoformat(receipt['started_at'])).total_seconds()
    stderr=(run/'stderr.log').read_text()
    data={'experiment_id':exp,'hypothesis_id':plan.get('hypothesis_id'),'goal_id':plan.get('goal_id'),'run_id':rid,'run_path':str(run.relative_to(ROOT)),'native_receipt':receipt,'raw_archive_commit':archive,'origin_tracking_refs':refs,'actual_files':sorted(p.name for p in run.iterdir()),'absent_declared_driver_outputs':[n for n in trial['artifacts'] if not(run/n).exists()],'not_launched_dependency_run_id':'RUN-ECDLP-b477fb','native_elapsed_seconds_derived':elapsed,'elapsed_derivation':'finished_at minus started_at; metadata helper failure interval','cpu_seconds':None,'peak_rss_bytes':None,'scientific_metrics':None,'scientific_certificate':None,'environment':json.loads((run/'environment.json').read_text()),'exact_native_launch':launch,'stderr_unchanged':stderr,'supervisor_argv':['python3','tools/experiment_execution.py','run','--plan','experiments/EXP-ECDLP-95f69f/trial-plan.json','--owner',receipt['authority']['owner'],'--epoch',str(receipt['authority']['epoch'])],'diagnosis':'Actual command starts env and three GIT_CONFIG assignments. The frozen helper compares [sys.executable,*sys.argv] with the full env-prefixed supervisor array; these vectors have different prefixes. Actual command has no -B interpreter flag.','diagnosis_source':'coordination/tasks/TASK-20261018-1cb336/envelope.py invocation_equal/context','scope':'Operational failure before compiler or scientific route; no mathematical observation or verdict.'}
    (out/'report-data.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    (out/'command.json').write_text(json.dumps({'supervisor_argv':data['supervisor_argv'],'native_driver_argv':launch['argv'],'native_checker_argv':launch['check_argv']},indent=2)+'\n')
    dot='digraph failure { graph[rankdir=LR,bgcolor=white,fontname="Helvetica"];node[shape=box,style="rounded,filled",fillcolor="#edf2f7",fontname="Helvetica",fontsize=11];a[label="Frozen env-prefixed argv\\nNative launch provenance"];b[label="Metadata helper invocation check\\nPrefix mismatch before compiler"];c[label="infrastructure_error\\nNo scientific route or checker",fillcolor="#fee8d5"];a->b->c;label='+json.dumps(exp+' / '+rid)+';labelloc=t;}\n'
    (out/'pipeline.dot').write_text(dot)
    for fmt in ['svg','png']:subprocess.run(['dot','-T'+fmt,'pipeline.dot','-o','pipeline.'+fmt],cwd=out,check=True)
    summary=f"Two primary route trials were requested. Route A metadata helper exited 1 with native infrastructure_error; its checker was not invoked. Route B was not launched because it depends on accepted route A. Eight native files were retained, with all six declared driver artifacts absent. Native elapsed {elapsed:.6f} seconds is derived as finished_at minus started_at. CPU, peak RSS, dirty state, scientific metrics and scientific certificate are unavailable, not zero."
    limits='The original failure and never-launched dependent slot are not reused. Any correction requires an additive authorized plan and fresh identities. This failure is not a mathematical refutation. The command metadata and source-bound frozen helper explain the observed prefix incompatibility; no scientific workload, compiler or independent oracle was reached.'
    graphs='Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen experiment specification. No scientific graph changes follow from this operational error. A stopping-point diagram is used because no comparable scientific values were produced.'
    (out/'report.md').write_text(f"# Native invocation failure: {exp}\n\n{data['scope']}\n\nRun `{rid}`; hypothesis `{data['hypothesis_id']}`; goal `{data['goal_id']}`. Raw archive `{archive}`.\n\n{summary}\n\nExact stderr: `{stderr.strip()}`.\n\n{data['diagnosis']}\n\n{limits}\n\nExact commands, source/input hashes, actual whitelist environment and missing outputs: [report-data.json](report-data.json), [command.json](command.json). No random draw was reached or invented.\n\n{graphs}\n\n[Diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: `{data['run_path']}/execution-receipt.json`, command.txt, launch.json, environment.json, stderr.log; frozen helper context/invocation_equal.\n")
    doc=r'''\documentclass[10pt]{article}
\usepackage[margin=17mm]{geometry}
\usepackage{graphicx,listings}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible}
\begin{document}
\section*{'''+tex('Native invocation failure: '+exp)+r'''}
'''+tex(data['scope'])+r'''\par\medskip
'''+tex('Run '+rid+'; hypothesis '+str(data['hypothesis_id'])+'; goal '+str(data['goal_id'])+'. Raw archive '+archive+'.')+r'''\par\medskip
'''+tex(summary)+r'''\par\medskip
'''+tex('Exact stderr: '+stderr.strip())+r'''\par\medskip
'''+tex(data['diagnosis'])+r'''\par\medskip
\begin{center}\includegraphics[width=\linewidth]{pipeline.png}\end{center}
'''+tex(limits)+r'''\par\medskip
'''+tex(graphs)+r'''\par\medskip
'''+tex('Exact parameters, source hashes, declared missing outputs, native environment and commands remain in report-data.json and command.json. No random draw was reached or invented. Sources: ../../runs/'+rid+'/execution-receipt.json, launch.json, command.txt, environment.json, stderr.log; frozen envelope.py invocation_equal/context.')+r'''
\newpage
\section*{Exact supervisor and native commands}
\lstinputlisting{command.json}
\end{document}
'''
    (out/'report.tex').write_text(doc.replace('Raw archive '+archive, r'\par\medskip Raw archive '+archive));shutil.copy2(__file__,out/'render.py');(out/'.gitignore').write_text('build/\n');(out/'build').mkdir()
    r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','report.tex'],cwd=out,capture_output=True,text=True)
    (out/'render.stdout.log').write_text(r.stdout);(out/'render.stderr.log').write_text(r.stderr);r.check_returncode();shutil.copy2(out/'build/report.pdf',out/'report.pdf')
    subprocess.run(['pdftotext','report.pdf','extracted.txt'],cwd=out,check=True)
    subprocess.run(['pdftoppm','-scale-to','1600','-png','report.pdf','build/page'],cwd=out,check=True,capture_output=True)
    print(out)

if __name__=='__main__':main()
