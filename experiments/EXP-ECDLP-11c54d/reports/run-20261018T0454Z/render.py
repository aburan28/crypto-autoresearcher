#!/usr/bin/env python3
"""Descriptive rendering only: read sealed native records; never run science."""
from datetime import datetime
import argparse,hashlib,json,shutil,subprocess,textwrap
from pathlib import Path
import yaml

ROOT=Path('/workspace/crypto-autoresearcher')
PAIRS=[('3521b9','03ccb4'),('087aea','42ded6'),('11c54d','d9188a'),('5d6ec1','6671fe')]
DIAGNOSTIC=Path('/tmp/ideas-ar-native-runtime-diagnostic-20261018.json')
PREFIX={'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'core.preloadIndex','GIT_CONFIG_VALUE_0':'false'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tex(s):
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--experiments',nargs='*');args=parser.parse_args()
 for exp,rid in PAIRS:
  if args.experiments and exp not in args.experiments:continue
  exp='EXP-ECDLP-'+exp;rid='RUN-ECDLP-'+rid
  run=ROOT/'experiments'/exp/'runs'/rid
  receipt=json.loads((run/'execution-receipt.json').read_text())
  # Native outputs must be committed and already published before writing report.
  head=subprocess.check_output(['git','-C',str(ROOT),'log','-1','--format=%H','--',str((run/'execution-receipt.json').relative_to(ROOT))],text=True).strip()
  if not head:raise RuntimeError('Raw run is not yet committed: '+rid)
  refs=subprocess.check_output(['git','-C',str(ROOT),'for-each-ref','--contains='+head,'--format=%(refname)','refs/remotes/origin/'],text=True).strip()
  if not refs:raise RuntimeError('Raw run is not yet published in origin tracking refs: '+rid)
  stamp=datetime.fromisoformat(receipt['started_at']).strftime('%Y%m%dT%H%MZ')
  out=ROOT/'experiments'/exp/'reports'/('run-'+stamp)
  out.mkdir(parents=True,exist_ok=False)
  plan=json.loads((ROOT/'experiments'/exp/'trial-plan.json').read_text())
  legacy=plan['legacy_trial']
  manifest=yaml.safe_load((run/'manifest.yaml').read_text())['run'] if (run/'manifest.yaml').exists() else None
  oldraw=ROOT/'experiments'/legacy['experiment_id']/'runs'/legacy['run_id']/'raw-result.json'
  raw=run/'raw-result.json'
  exact=(sha(oldraw)==sha(raw)) if oldraw.exists() and raw.exists() else None
  derivedwall=(datetime.fromisoformat(receipt['finished_at'])-datetime.fromisoformat(receipt['started_at'])).total_seconds()
  command={'supervisor_argv':['python3','tools/experiment_execution.py','run','--plan',str((ROOT/'experiments'/exp/'trial-plan.json').relative_to(ROOT)),'--owner','executor-ideas-20261018','--epoch',str(receipt['authority']['epoch'])],
           'outer_environment_prefix':PREFIX if manifest else {},'native_launch_argv':json.loads((run/'launch.json').read_text())['argv']}
  (out/'command.json').write_text(json.dumps(command,indent=2)+'\n')
  data={'experiment_id':exp,'run_id':rid,'hypothesis_id':plan.get('hypothesis_id'),'goal_id':plan.get('goal_id'),'run_path':str(run.relative_to(ROOT)),
        'raw_archive_commit':head,'origin_tracking_refs':refs.splitlines(),'status':receipt['status'],'trials_requested':1,
        'trials_output_validated':int(receipt['status']=='output_validated'),'trials_failed':int(receipt['status']!='output_validated'),'trials_timed_out':0,
        'native_started_at':receipt['started_at'],'native_finished_at':receipt['finished_at'],'native_elapsed_seconds_derived':derivedwall,
        'execution_commit':receipt['authority']['commit'],'manifest_code_dirty':manifest['code']['dirty'] if manifest else None,
        'metrics':manifest['result']['metrics'] if manifest else None,'measured_manifest_timing':manifest['timing'] if manifest else None,
        'measured_manifest_resources':manifest['resources'] if manifest else None,'certificate':manifest['result']['certificate'] if manifest else None,
        'parameters_and_seed':manifest['inputs'] if manifest else None,'environment':json.loads((run/'environment.json').read_text()),
        'legacy_experiment_id':legacy['experiment_id'],'legacy_run_id':legacy['run_id'],'raw_bytes_match_original_archive':exact,
        'failure':(run/'stderr.log').read_text() if not manifest else None,
        'missing_declared_outputs':[name for name in plan['trials'][0]['artifacts'] if not (run/name).is_file()],
        'input_seed_semantics':legacy['input_seed_semantics'],
        'scope':'Observations only. Deterministic original worksheet reproduction/calibration; no scientific verdict, independent scientific review, attack claim or execution proof.'}
  (out/'report-data.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
  shutil.copy2(DIAGNOSTIC,out/'runtime-diagnostic.json')
  draw='''digraph run { graph[rankdir=LR,bgcolor=white,fontname="Helvetica"]; node[shape=box,style="rounded,filled",fillcolor="#edf2f7",fontname="Helvetica",fontsize=11]; edge[color="#667788"];'''
  labels=[('plan','Frozen legacy fixture\nNative supervisor:256 MiB')]
  if manifest:
   labels += [('driver','Unchanged legacy driver\nOriginal pre-envelope checker'),('envelope','Fresh outer EXP/RUN envelope\nExact original raw bytes'),('end','Supervisor checker replay\noutput_validated')]
  else:labels += [('git','Metadata Git status\nThread creation failed'),('end','infrastructure_error\nNo worksheet or raw result')]
  for ident,label in labels:draw+=ident+' [label='+json.dumps(label)+(' fillcolor="#fee8d5"' if ident=='end' else '')+'];'
  draw+=' -> '.join(i for i,_ in labels)+';label='+json.dumps(exp+' / '+rid)+';labelloc=t;}'
  (out/'pipeline.dot').write_text(draw+'\n')
  subprocess.run(['dot','-Tsvg','pipeline.dot','-o','pipeline.svg'],cwd=out,check=True)
  subprocess.run(['dot','-Tpng','pipeline.dot','-o','pipeline.png'],cwd=out,check=True)
  metrics=json.dumps(data['metrics'],indent=2) if manifest else 'No worksheet metrics produced.'
  params=json.dumps(data['parameters_and_seed'],indent=2) if manifest else 'No worksheet parameter echo produced; declared inputs remain in the frozen plan/specification.'
  wall=data['measured_manifest_timing']['wall_seconds'] if manifest else None
  cpu=data['measured_manifest_resources']['cpu_seconds'] if manifest else None
  rss=data['measured_manifest_resources']['peak_rss_bytes'] if manifest else None
  summary=(f"Native status: {data['status']}. Requested 1, output_validated {data['trials_output_validated']}, failed {data['trials_failed']}, timed out 0. "
           f"Native elapsed {derivedwall:.6f} seconds is derived as finished_at minus started_at. "
           f"Measured manifest interval seconds={wall}, child CPU seconds={cpu}, per-process RSS maximum bytes={rss}. "
           "Missing measurements are null, never zero. There is one deterministic worksheet, not a sampled inference; no uncertainty interval was recorded.")
  limitation=("This reports operational outputs only. Original predictions are historical calibration targets; repeated deterministic bytes are not fresh confirmatory data. "
              "Input seed remains null: no new random draw. Any original fixture/seed labels remain untouched. A null curve_id does not certify an exact cross-repository subgroup identity. "
              "No discrete-log/decomposition certificate is claimed. The native checker is a source/control check, not independent scientific review. "
             "The first run's metadata Git utility failed to create threaded lstat under 256 MiB; its slot remains immutable. The subsequent three used the explicitly authorized process-local Git preload limit shown in command.json, with unchanged source/argv/scientific inputs and supervisor ceiling.")
  canonical=("Canonical graph scope checked: knowledge/frontiers/ecdlp/ index and the batch's existing source/approval references. "
             "No scientific frontier, hypothesis status or isogeny graph was changed by these operational reproductions. "
             "A pipeline diagram is used because this experiment has one deterministic fixture, without two comparable experimental arms.")
  md=f'''# Native execution report: {exp}

{data['scope']}

Run `{rid}`; hypothesis `{data['hypothesis_id']}`; goal `{data['goal_id']}`.
Immutable records: `{data['run_path']}`. Raw publication commit `{head}`.

{summary}

Execution commit `{data['execution_commit']}`; recorded dirty state `{data['manifest_code_dirty']}`.
Host/platform and Python: see copied whitelist in [report-data.json](report-data.json); detailed CPU hardware was not recorded.

Original identities: `{legacy['experiment_id']}` / `{legacy['run_id']}`.
Raw bytes match the preserved original archive: `{exact}`.

Recorded metrics, unchanged:

```json
{metrics}
```

Parameters, controls and seeds: [report-data.json](report-data.json), original frozen specification, exact [command.json](command.json).
Legacy output and original checker are retained; checker runs once before outer-envelope construction and once in supervisor check phase.
For the failed run neither worksheet invocation occurred. Missing declared outputs: `{data['missing_declared_outputs']}`.
Failure text: `{data['failure']}`.

{limitation}

{canonical}

[Diagram](pipeline.svg), editable [DOT source](pipeline.dot), [PDF](report.pdf), [runtime diagnostic](runtime-diagnostic.json).
'''
  (out/'report.md').write_text(md)
  (out/'metrics.json').write_text(metrics+'\n')
  content=r'''\documentclass[10pt]{article}
\usepackage[margin=16mm]{geometry}
\usepackage{graphicx,listings}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible}
\begin{document}
\section*{'''+tex('Native execution report: '+exp)+r'''}
\noindent '''+tex(data['scope'])+r'''\par\medskip
\noindent '''+tex('Run '+rid+'; hypothesis '+str(data['hypothesis_id'])+'; goal '+str(data['goal_id'])+'.')+r'''\par
\noindent '''+tex('Raw publication commit '+head+'.')+r'''\par\medskip
'''+tex(summary)+r'''\par\medskip
'''+tex('Execution commit '+data['execution_commit']+'; recorded dirty state '+str(data['manifest_code_dirty'])+'. Host/platform and Python are retained in report-data.json; detailed CPU model is missing.')+r'''\par\medskip
'''+tex('Legacy identities '+legacy['experiment_id']+' / '+legacy['run_id']+'; raw bytes match original archive: '+str(exact)+'.')+r'''
\subsection*{Recorded metrics}
\lstinputlisting{metrics.json}
\subsection*{Exact supervisor command and resource prefix}
\lstinputlisting{command.json}
\noindent '''+tex('Immutable record path: '+data['run_path']+'. Parameters, controls, null-seed semantics, full environment whitelist and source/input hashes are retained in report-data.json and the sealed run. Missing declared outputs: '+str(data['missing_declared_outputs'])+'.')+r'''\par\medskip
'''+tex('Failure: '+str(data['failure']))+r'''\par\medskip
'''+tex(limitation)+r'''\par\medskip
'''+tex(canonical)+r'''\par
\begin{center}\includegraphics[width=\linewidth]{pipeline.png}\end{center}
\noindent '''+tex('Sources: ../../runs/'+rid+'/execution-receipt.json, manifest.yaml when present, raw-result.json when present, legacy-execution.json when present; report-data.json and runtime-diagnostic.json. All numbers are recorded measurements unless expressly labeled derived.')+r'''
\end{document}
'''
  (out/'report.tex').write_text(content)
  shutil.copy2(Path(__file__),out/'render.py')
  build=out/'build';build.mkdir()
  log=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','report.tex'],cwd=out,capture_output=True,text=True)
  (out/'render.stdout.log').write_text(log.stdout);(out/'render.stderr.log').write_text(log.stderr)
  if log.returncode:raise RuntimeError(str(out)+' LaTeX build failed')
  shutil.copy2(build/'report.pdf',out/'report.pdf')
  subprocess.run(['pdftotext','report.pdf','extracted.txt'],cwd=out,check=True)
  subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1400','-png','report.pdf','build/page1'],cwd=out,check=True,capture_output=True)
  (out/'.gitignore').write_text('build/\n')
  print(out.relative_to(ROOT))
if __name__=='__main__':main()
