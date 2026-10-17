from pathlib import Path
import json,sys
sys.path.insert(0,'/workspace/snfs-toolchains/report')
import typst
repo=Path('/workspace/snfs-research-pr');report=repo/'experiments/EXP-ECDLP-84af7b/reports/run-20261017T1822Z';run=report.parents[1]/'runs/RUN-ECDLP-18d26b'
r=json.loads((run/'execution-receipt.json').read_text());env=json.loads((run/'environment.json').read_text())
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180"><rect width="900" height="180" fill="#f4f7fa"/><g font-family="sans-serif" font-size="18" text-anchor="middle"><rect x="20" y="40" width="240" height="80" rx="8" fill="#d9ebf8"/><text x="140" y="73">Supervisor admitted</text><text x="140" y="101">frozen full-grid trial</text><path d="M265 80H330" stroke="#345" stroke-width="3"/><rect x="335" y="40" width="240" height="80" rx="8" fill="#ffe1c9"/><text x="455" y="73">Process launch failed</text><text x="455" y="101">cargo unavailable</text><path d="M580 80H645" stroke="#345" stroke-width="3"/><rect x="650" y="40" width="230" height="80" rx="8" fill="#eee"/><text x="765" y="73">No scientific output</text><text x="765" y="101">No checker executed</text><text x="450" y="156" font-size="14">RUN-ECDLP-18d26b · EXP-ECDLP-84af7b · 2026-10-17</text></g></svg>'''
(report/'pipeline.svg').write_text(svg)
text=f'''Observations only. This report does not review the hypothesis or change any scientific status.

Experiment: EXP-ECDLP-84af7b; hypothesis: H-ECDLP-2f1033; goal: GOAL-ECDLP-001.
Run: RUN-ECDLP-18d26b. Source commit: {env['commit']}.
One frozen full-grid trial was requested. One attempt ended infrastructure_error before its scientific executable started. No scientific cells or controls completed; checker return code is missing because the checker did not run.
Exact recorded error: {r['detail']}.
Start: {r['started_at']}; finish: {r['finished_at']}. CPU time and scientific timings are not available. Host detail beyond platform and Python is not recorded by this legacy supervisor; dirty-tree state is not recorded. Source digests are in environment.json. The run's command.txt records the full command, grid, seeds 1,2,3, controls and 14,400-second watchdog.
The diagram is used because there are no comparable scientific measurements. It depicts the recorded execution path, not a mathematical obstruction.
The failed run remains immutable. Installing the toolchain does not validate it. A retry needs a new immutable run identity and explicit additive authorization, with the original scientific parameters retained.
Artifacts: ../../runs/RUN-ECDLP-18d26b/ (execution-receipt.json, launch.json, command.txt, environment.json, stdout/stderr and empty checker logs). No raw-result.json or manifest.yaml was produced.
'''
(report/'report.md').write_text('# G1 full-grid launch attempt\n\n'+text)
parts=text.split('\n\n')
source='#set page(paper: "a4", margin: 18mm)\n#set text(size: 10pt)\n= G1 full-grid launch attempt\n'+ '\n\n'.join('#text('+json.dumps(p)+')' for p in parts[:3])+'\n\n#image("pipeline.svg", width: 100%)\n\n'+ '\n\n'.join('#text('+json.dumps(p)+')' for p in parts[3:])
(report/'report.typ').write_text(source)
typst.compile(str(report/'report.typ'),output=str(report/'report.pdf'),root=str(repo))
import pymupdf
pdf=pymupdf.open(report/'report.pdf')
for i,p in enumerate(pdf):
 print('PAGE',i+1,p.get_text()[:500]);p.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save('/tmp/snfs-g1-report-page-'+str(i+1)+'.png')
print('pages',len(pdf))
