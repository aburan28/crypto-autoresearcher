#!/usr/bin/env python3
"""Render observations from a native export; no solver or new measurement."""
import argparse, hashlib, json, shutil, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store
import experiment_protocol as ep

def render(export_path,raw_path,out):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import typst
 export=ep.read_json(export_path);raw=artifact_store.read_json(raw_path)
 protocol_path=(export_path.parent/export['protocol']['path']).resolve()
 protocol=ep.read_json(protocol_path)
 errors=ep.schema_errors(export,'experiment.export/v1') or ep.lint_export(export,protocol,export_path.parent,True)
 if errors:raise ValueError('\n'.join(errors))
 out.mkdir(parents=True,exist_ok=True)
 for name in ('report.md','diagram.svg','report.typ','report.pdf','report-data.json','renderer.py'):
  if (out/name).exists():raise FileExistsError(out/name)
 receipt=artifact_store.read_json(raw_path.parent/'execution-receipt.json');launch=artifact_store.read_json(raw_path.parent/'launch.json');env=artifact_store.read_json(raw_path.parent/'environment.json')
 elapsed=(datetime.fromisoformat(receipt['finished_at'])-datetime.fromisoformat(receipt['started_at'])).total_seconds()
 rows=[{'arm':r['arm'],**r['measurements']['counted']} for r in export['runs']]
 data={'run':raw_path.parent.name,'rows':rows,'config':raw['config'],'resources':raw.get('resources',{}),'derived_native_elapsed_seconds':elapsed,'receipt':receipt,'launch':launch,'environment':env,'source_sha256':protocol['extensions']['source_sha256'],'input_sha256':protocol['extensions']['input_sha256']}
 (out/'report-data.json').write_text(json.dumps(data,indent=2)+'\n');shutil.copyfile(__file__,out/'renderer.py')
 fig,axes=plt.subplots(2,1,figsize=(9,6.5),layout='constrained')
 for ax,selected,title in [(axes[0],rows[:4],'Coordinate encoding search (106 fixed cells per arm)'),(axes[1],rows[4:8],'Coefficient search (6 fixed cells per arm)')]:
  labels=[r['arm'] for r in selected];done=[r['search_complete'] for r in selected];censored=[r['search_censored'] for r in selected]
  ax.barh(labels,done,label='Complete search',color='#2b708e');ax.barh(labels,censored,left=done,label='Censored search',color='#e69f00')
  ax.set_xlabel('Recorded subcells (exact integer counts)');ax.set_title(title);ax.invert_yaxis();ax.legend(loc='lower right');ax.grid(axis='x',alpha=.15)
 fig.suptitle(raw_path.parent.name+' — search completion is separate from model equivalence',fontsize=11)
 fig.savefig(out/'diagram.svg');plt.close(fig)
 intro='Observations only. This report records exact finite checks and instrumented counters; it does not promote a hypothesis or claim timing, intrinsic regularity, or an ECDLP advantage.'
 scope='The fixed public inputs were seen in earlier work. Complete independent model censuses verify all encodings even when bounded search is censored. Coefficient model counts and squarefree point relations have distinct domains; repeated divisors are outside the relation claim. The degree-two PC window can discard an unrestricted quartic until branch restriction; it is an intentionally bounded instrument, not a regularity determination.'
 custody='The cell journals are durable partial observations, not resumable checkpoints. No restart or second scientific attempt is authorized by this run. Counter totals retain phase and primitive units and cover only instrumented arithmetic/events, not complete CPU instructions. Canonical research graphs were not changed because this report records observations without an official scientific decision.'
 md=['# Prime-field encoding and coefficient-SAT follow-up',intro,'',f"Experiment `{protocol['links']['experiment_id']}`; hypothesis `{protocol['links']['hypothesis_ids'][0]}`; goal `{protocol['links']['goal_id']}`.",f"Run `{raw_path.parent.name}` at `{raw_path}`. Native receipt status `{receipt['status']}`; producer return `{receipt.get('returncode')}`; independent checker return `{receipt.get('check_returncode')}`.",f"Code commit `{env['commit']}`; dirty state `{export['source']['dirty']}`. One trial requested; terminal receipt retained. Seed 17, fixed cell and arm order; all caps are in the config below.",f"Command: `{json.dumps(launch['argv'])}`",f"Started `{launch.get('started_at')}`; finished `{receipt.get('finished_at')}`. Host metadata: `{raw_path.parent/'environment.json'}`. Resource telemetry boundary and values: `{json.dumps(raw.get('resources',{}),sort_keys=True)}`. Native elapsed seconds `{elapsed}` are derived as receipt.finished_at minus receipt.started_at, including independent checking; they are not a comparison metric. Unrecorded telemetry remains unknown.",'',scope,'',custody,'','| Arm | Subcells | Complete search | Censored search | Search models | Control pass/fail |','|---|---:|---:|---:|---:|---:|']
 for r in rows:md.append(f"| {r['arm']} | {r['subcells']} | {r['search_complete']} | {r['search_censored']} | {r['models_found']} | {r.get('control_pass','—')}/{r.get('control_fail','—')} |")
 md+=['','All table values are recorded counts or exact sums of explicitly named raw fields. No uncertainty interval applies to the fixed finite census. Search models in different packages are not comparable domain sizes.','',f'![Recorded completion counts; {raw_path.parent.name}](diagram.svg)','',f"Export SHA256: `{hashlib.sha256(export_path.read_bytes()).hexdigest()}`; protocol hash: `{protocol['freeze']['protocol_sha256']}`; config SHA256: `{raw['config_sha256']}`.",'','Complete per-arm phase-specific counters and native custody facts are in [report-data.json](report-data.json). Raw package certificates, independent checks and cell journals remain linked by the native export; no scientific code is invoked by this renderer.','','```json',json.dumps(raw['config'],indent=2),'```']
 (out/'report.md').write_text('\n'.join(md)+'\n')
 quote=lambda x:json.dumps(str(x),ensure_ascii=False)
 typ=['#set page(paper: "a4", margin: 16mm)','#set text(size: 9pt)','= Prime-field encoding and coefficient-SAT follow-up',f'#text({quote(intro)})',f'#text({quote("Experiment "+protocol["links"]["experiment_id"]+"; run "+raw_path.parent.name)})',f'#text({quote("Code "+env["commit"]+"; native receipt "+receipt["status"]+"; independently checked artifacts.")})',f'#text({quote(scope)})','#image("diagram.svg", width: 100%)',f'#text({quote(custody)})','#pagebreak()','= Recorded counts and provenance']
 for line in md:
  if line.startswith('| ') and not line.startswith('|---'):typ.append('#text('+quote(line)+')\n#parbreak()')
 typ+=['#parbreak()',f'#text({quote("Resource telemetry: "+json.dumps(raw.get("resources",{}),sort_keys=True))})',f'#text({quote("Export SHA256 "+hashlib.sha256(export_path.read_bytes()).hexdigest())})',f'#text({quote("Protocol hash "+protocol["freeze"]["protocol_sha256"])})',f'#text({quote("Config SHA256 "+raw["config_sha256"])})',f'#text({quote("Command "+json.dumps(launch["argv"]))})',f'#text({quote("Started "+str(launch.get("started_at"))+"; finished "+str(receipt.get("finished_at")))})','#text("Full fixed parameters, counter units, source/input hashes, receipts, controls and primitive counters are in report.md and report-data.json beside this PDF. Every plotted value is a recorded count. PDF must be visually inspected before publication.")']
 (out/'report.typ').write_text('\n\n'.join(typ)+'\n');typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
 print(json.dumps({'report':str(out/'report.md'),'graph':str(out/'diagram.svg'),'pdf':str(out/'report.pdf'),'inspection_required':True}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--export',required=True,type=Path);a.add_argument('--raw',required=True,type=Path);a.add_argument('--out',required=True,type=Path);x=a.parse_args();render(x.export.resolve(),x.raw.resolve(),x.out.resolve())
