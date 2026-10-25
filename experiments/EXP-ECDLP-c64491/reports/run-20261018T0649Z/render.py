#!/usr/bin/env python3
"""Write descriptive reports from published native worksheet outputs only."""
from datetime import datetime
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path
import yaml

ROOT = Path('/workspace/crypto-autoresearcher')

def tex(value):
    escaped={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(escaped.get(c,c) for c in str(value))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiment',required=True)
    parser.add_argument('--runs',nargs='+',required=True)
    parser.add_argument('--outer-git-preload-disabled',action='store_true')
    parser.add_argument('--outer-command-style',choices=['env','shell'],default='env')
    parser.add_argument('--legacy-stages',action='store_true')
    args=parser.parse_args()
    exp=args.experiment
    base=ROOT/'experiments'/exp
    plan=json.loads((base/'trial-plan.json').read_text())
    spec=yaml.safe_load((base/'specification.yaml').read_text())['experiment']
    records=[]
    for run_id in args.runs:
        run=base/'runs'/run_id
        receipt=json.loads((run/'execution-receipt.json').read_text())
        archive=subprocess.check_output(['git','log','-1','--format=%H','--',str((run/'execution-receipt.json').relative_to(ROOT))],cwd=ROOT,text=True).strip()
        refs=subprocess.check_output(['git','for-each-ref','--contains='+archive,'--format=%(refname)','refs/remotes/origin/'],cwd=ROOT,text=True).splitlines() if archive else []
        if not archive or not refs:raise RuntimeError('Raw run must be published first: '+run_id)
        manifest=yaml.safe_load((run/'manifest.yaml').read_text())['run'] if (run/'manifest.yaml').exists() else None
        raw=json.loads((run/'raw-result.json').read_text()) if (run/'raw-result.json').exists() else None
        launch=json.loads((run/'launch.json').read_text())
        records.append({'run_id':run_id,'run_path':str(run.relative_to(ROOT)),'archive_commit':archive,'published_refs':refs,'receipt':receipt,'manifest':manifest,'raw':raw,'environment':json.loads((run/'environment.json').read_text()),'outer_environment_prefix':({'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'core.preloadIndex','GIT_CONFIG_VALUE_0':'false'} if args.outer_git_preload_disabled else {}),'outer_command_style':args.outer_command_style if args.outer_git_preload_disabled else None,'runtime_amendment':'coordination/goals/GOAL-ECDLP-001/batches/BATCH-d60d5d/runtime/outer-supervisor-environment.json' if args.outer_git_preload_disabled else None,'supervisor_argv':[('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3' if args.outer_git_preload_disabled and args.outer_command_style=='env' else 'python3'),'tools/experiment_execution.py','run','--plan',str((base/'trial-plan.json').relative_to(ROOT)),'--owner',receipt['authority']['owner'],'--epoch',str(receipt['authority']['epoch'])],'native_driver_argv':launch['argv'],'native_checker_argv':launch['check_argv'],'native_elapsed_seconds_derived':(datetime.fromisoformat(receipt['finished_at'])-datetime.fromisoformat(receipt['started_at'])).total_seconds()})
    stamp=min(datetime.fromisoformat(r['receipt']['started_at']) for r in records).strftime('%Y%m%dT%H%MZ')
    out=base/'reports'/('run-'+stamp)
    out.mkdir(parents=True,exist_ok=False)
    lineage=spec.get('lineage')
    lineage_text=('Source experiment: '+str(lineage.get('source_experiment'))+'. '+str(lineage.get('original_scientific_scope',lineage.get('relationship','')))+'. These deterministic readings remain historical in-sample calibration; no ambiguous original criterion is closed or re-scored. Complete lineage hashes remain in report-data.json.') if lineage else ''
    data={'lineage':lineage,'experiment_class':spec.get('experiment_class'),'experiment_id':exp,'hypothesis_id':plan.get('hypothesis_id',spec.get('hypothesis_id')),'goal_id':plan.get('goal_id',spec.get('goal_id')),'records':records,'scope':'Descriptive finite worksheet observations only; no hypothesis verdict, asymptotic claim or deployed-curve result.'}
    (out/'report-data.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    scalar_rows=[]
    table=[]
    for r in records:
        m=r['manifest'] or {}
        metrics=m.get('result',{}).get('metrics',{})
        scalar_rows.append({'run_id':r['run_id'],'scalar_metrics':{k:v for k,v in metrics.items() if v is None or type(v) in (bool,int,float,str)},'structured_metric_fields_retained_in_report_data':[k for k,v in metrics.items() if v is not None and type(v) not in (bool,int,float,str)]})
        if isinstance(metrics.get('observations'),dict):
            scalar_rows[-1]['observed_scalar_fields']={k:v for k,v in metrics['observations'].items() if v is None or type(v) in (bool,int,float,str)}
        table.append([r['run_id'],r['receipt']['status'],m.get('timing',{}).get('wall_seconds'),m.get('resources',{}).get('cpu_seconds'),m.get('resources',{}).get('peak_rss_bytes')])
    (out/'scalar-metrics.json').write_text(json.dumps(scalar_rows,indent=2,sort_keys=True)+'\n')
    dot='digraph run { graph[rankdir=LR,bgcolor=white,fontname="Helvetica"];node[shape=box,style="rounded,filled",fillcolor="#edf2f7",fontname="Helvetica",fontsize=11];a[label="Frozen finite inputs\\nNative source-bound launch"];b[label="Selected scientific route\\nRaw transcript and witness"];c[label="Separate checker process\\nIndependent finite recomputation"];d[label="Native manifest acceptance\\nObservation only"];a->b->c->d;label='+json.dumps(exp+' / '+', '.join(args.runs))+';labelloc=t;}\n'
    if args.legacy_stages:
        dot=dot.replace('Selected scientific route','Unchanged legacy stage').replace('Raw transcript and witness','Exact legacy workspace retained').replace('Separate checker process','Original legacy checker').replace('Independent finite recomputation','Labels and file presence only')
    (out/'pipeline.dot').write_text(dot)
    for fmt in ['svg','png']:subprocess.run(['dot','-T'+fmt,'pipeline.dot','-o','pipeline.'+fmt],cwd=out,check=True)
    measured=[r for r in records if r['manifest'] and type(r['manifest'].get('timing',{}).get('wall_seconds')) in (int,float)]
    plot=False
    if len(measured)>=2:
        os.environ.setdefault('MPLCONFIGDIR','/tmp/ideas-worksheet-mpl')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(8,3))
        ax.bar([r['run_id'] for r in measured],[r['manifest']['timing']['wall_seconds'] for r in measured],color='#42687a')
        ax.set_ylabel('Recorded driver interval (seconds)')
        ax.set_title('One recorded interval per run; no uncertainty interval recorded')
        ax.tick_params(axis='x',labelsize=9)
        fig.tight_layout()
        for fmt in ['svg','png']:fig.savefig(out/('timings.'+fmt),dpi=180)
        plt.close(fig);plot=True
    header='| Run | Native status | Driver wall s | Driver CPU s | Peak RSS bytes |\n| --- | --- | ---: | ---: | ---: |\n'
    rows='\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in table)
    boundary='All values are recorded unless expressly labeled derived. Native elapsed is derived as finished_at minus started_at. Driver wall/CPU/RSS use each manifest\'s explicit boundaries, retained in report-data.json; RSS is a lifetime per-process peak, not aggregate memory. These deterministic route observations have one datum each, no sampled uncertainty or performance inference. No random draw is introduced; null seed and curve_id remain as recorded. A finite worksheet witness is not a formal, decomposition or discrete-log certificate.'
    if args.legacy_stages:
        seeds=[r['manifest']['inputs']['seed'] for r in records if r['manifest']]
        scopes=[r['manifest']['environment'].get('checker_scope') for r in records if r['manifest']]
        boundary='Recorded values are stage observations only. Native elapsed is derived as finished_at minus started_at; each measured manifest interval and child resource boundary is retained in report-data.json. These are dependent stages, not independent primary arithmetic routes. Actual recorded legacy seeds are '+str(seeds)+'. Canonical certificate kind is none. The unchanged legacy checker verifies outcome vocabulary and file presence only; no independent arithmetic verification or scientific validity follows from native output_validated. Full recorded checker scopes: '+str(scopes)+'. Raw legacy outcomes remain uninterpreted; O-CONTROL-FAIL and O-IMPEDIMENT carry no hypothesis verdict. Timing bars are single process intervals for different stages, not a performance comparison. This is the explicit adjacent nineteenth candidate; historical eighteen membership remains unauthenticated.'
    if args.outer_git_preload_disabled:
        boundary+=' The authorized outer supervisor environment sets GIT_CONFIG_COUNT=1, GIT_CONFIG_KEY_0=core.preloadIndex and GIT_CONFIG_VALUE_0=false under DEC-20261018-1a5209; exact direct child argv and resource limits are unchanged. The exact outer command style is retained in report-data.json.'
    graphs='Canonical graph scope checked: knowledge/frontiers/ecdlp and the frozen specification. These finite records do not change a scientific status or graph. The pipeline diagram records what ran; the timing plot, where present, plots recorded driver intervals only and claims no speedup.'
    md=f"# Native worksheet execution: {exp}\n\n{data['scope']}\n\n{lineage_text}\n\nHypothesis `{data['hypothesis_id']}`; goal `{data['goal_id']}`. Requested {len(records)} trials; native statuses and resources follow.\n\n{header}{rows}\n\n{boundary}\n\nComplete raw transcripts, controls, prediction comparisons, witness bindings, source/input hashes, code commits, dirty states, environment and exact commands: [report-data.json](report-data.json). All run paths and published raw commit IDs are listed there. Prediction comparison is distinct from control/output validity.\n\nRecorded metric fields (complete, unchanged):\n\n```json\n{json.dumps([{'run_id':r['run_id'],'metrics':(r['manifest'] or {}).get('result',{}).get('metrics')} for r in records],indent=2,sort_keys=True)}\n```\n\n{graphs}\n\n[Pipeline](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Raw source paths:\n\n"+'\n'.join('- `'+r['run_path']+'`; archive `'+r['archive_commit']+'`.' for r in records)+'\n'
    (out/'report.md').write_text(md)
    lines='\n'.join(tex(' | '.join(format(v,'.6g') if type(v) is float else str(v) for v in row))+r'\par' for row in table)
    doc=r'''\documentclass[10pt]{article}
\usepackage[margin=16mm]{geometry}
\usepackage{graphicx,listings}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible}
\begin{document}
\section*{'''+tex('Native worksheet execution: '+exp)+r'''}
'''+tex(data['scope'])+r'''\par\medskip
'''+tex(lineage_text)+r'''\par\medskip
'''+tex('Hypothesis '+str(data['hypothesis_id'])+'; goal '+str(data['goal_id'])+'. Requested '+str(len(records))+' trials.')+r'''\par\medskip
'''+tex('Run | Native status | Driver wall seconds | CPU seconds | RSS bytes (floating values displayed to 6 significant digits; full precision retained in report-data.json)')+r'''\par
'''+lines+r'''\medskip
'''+tex(boundary)+r'''\par\medskip
\begin{center}\includegraphics[width=\linewidth]{pipeline.png}\end{center}
'''+(r'\begin{center}\includegraphics[width=0.9\linewidth]{timings.png}\end{center}' if plot else '')+r'''
'''+tex(graphs)+r'''\par\medskip
'''+tex('Complete commands, controls, parameters, code/dirty/environment identities, exact source hashes and raw publication commits are retained in report-data.json and the linked raw runs. Missing data remain null. No result of a control gate is promoted to a hypothesis verdict.')+r'''
\newpage
\section*{Recorded scalar metrics}
\lstinputlisting{scalar-metrics.json}
'''+tex('Structured fields are retained completely in report-data.json and report.md; no truncation or numerical inference changes the raw evidence.')+r'''
\end{document}
'''
    (out/'report.tex').write_text(doc)
    shutil.copy2(__file__,out/'render.py')
    (out/'.gitignore').write_text('build/\n')
    (out/'build').mkdir()
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','report.tex'],cwd=out,capture_output=True,text=True)
    (out/'render.stdout.log').write_text(result.stdout);(out/'render.stderr.log').write_text(result.stderr);result.check_returncode()
    shutil.copy2(out/'build/report.pdf',out/'report.pdf')
    subprocess.run(['pdftotext','report.pdf','extracted.txt'],cwd=out,check=True)
    subprocess.run(['pdftoppm','-scale-to','1600','-png','report.pdf','build/page'],cwd=out,check=True,capture_output=True)
    print(out)

if __name__=='__main__':main()
