#!/usr/bin/env python3
"""Render a custody-checked report of the immutable pre-Sandbox failure only."""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, shlex, subprocess, tarfile

HERE = Path(__file__).resolve().parent
PUB = '19ad348e28071021e9f752e559d5bfd628cfc63f'
REL = 'experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986'

def sha(p):
    with Path(p).open('rb') as s: return hashlib.file_digest(s,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('/workspace/classical-ecdlp-validation-ready'));a=p.parse_args();r=a.repo/REL
    names=['raw-result.json','manifest.yaml','modal-evidence-manifest.json','modal/controller-receipt.json','modal-evidence.tar.gz.blob.json','artifact-readback.json','execution-receipt.json','environment.json','launch.json','command.txt']
    raw=json.loads((r/'raw-result.json').read_bytes());c=json.loads((r/'modal/controller-receipt.json').read_bytes());m=json.loads((r/'modal-evidence-manifest.json').read_bytes());ptr=json.loads((r/'modal-evidence.tar.gz.blob.json').read_bytes());rb=json.loads((r/'artifact-readback.json').read_bytes());env=json.loads((r/'environment.json').read_bytes());execution=json.loads((r/'execution-receipt.json').read_bytes());launch=json.loads((r/'launch.json').read_bytes())
    assert raw['experiment_id']=='EXP-ECDLP-ef7323' and raw['run_id']=='RUN-ECDLP-ea5986' and raw['controller']==c
    assert c['measurement_started'] is False and c['submission_ambiguous'] is False
    assert [c[k] for k in ['sandbox_create_calls','engine_exec_calls','plan_probe_exec_calls']]==[0,0,0]
    assert c['error']=={'type':'ConnectionError','message':'Could not connect to the Modal server.'}
    archive=r/'modal-evidence.tar.gz';e=raw['evidence'];assert archive.stat().st_size==e['bytes']==68583 and sha(archive)==e['sha256']==ptr['content_sha256']
    assert sha(r/'modal-evidence-manifest.json')==e['member_manifest_sha256'];expected={x['path']:x for x in m['files']};assert len(expected)==len(m['files'])==13
    seen=set()
    with tarfile.open(archive,'r:gz') as tar:
        for member in tar:
            q=PurePosixPath(member.name);assert member.isfile() and member.name in expected and member.name not in seen and not q.is_absolute() and '..' not in q.parts and q.parts[0]=='modal'
            seen.add(member.name)
            with tar.extractfile(member) as s:d=hashlib.file_digest(s,'sha256').hexdigest()
            assert member.size==expected[member.name]['bytes'] and d==expected[member.name]['sha256']
            assert (r/member.name).is_file() and not (r/member.name).is_symlink() and sha(r/member.name)==d
    assert seen==set(expected)
    assert not any('provider-context' in n or '/raw/' in n or 'cohort.json' in n for n in seen)
    assert rb['all_full_s3_gets_verified'] is True and rb['readbacks'][0]['full_s3_get_verified'] is True and rb['readbacks'][0]['bytes']==68583 and rb['readbacks'][0]['sha256']==e['sha256']
    supervisor_path=HERE.parent/'execution-attempt-01.json';supervisor=json.loads(supervisor_path.read_bytes());progress_path=HERE.parent/'execution-attempt-01.stdout.txt';progress=json.loads(progress_path.read_bytes());assert supervisor['returncode']==3 and progress['needs_reconciliation']==1 and progress['output_validated']==0
    elapsed=(datetime.datetime.fromisoformat(c['finished_at'])-datetime.datetime.fromisoformat(c['started_at'])).total_seconds()
    facts={'schema':'classical.ecdlp.transfer-study.failed-attempt-report/v1','scope':'Operational observation and local custody check only; no scientific verification, launch, cohort draw or inferred mathematical outcome.','publication_commit':PUB,'run_path':REL,'experiment_id':'EXP-ECDLP-ef7323','hypothesis_id':'H-ECDLP-e1270c','goal_id':'GOAL-ECDLP-e70832','run_id':'RUN-ECDLP-ea5986','batch_id':'BATCH-319445','controller':c,'supervisor':supervisor,'supervisor_progress':progress,'execution_receipt':execution,'environment_record':env,'dirty_state':'not recorded in environment.json','launch_argv':launch['argv'],'planned_controls':['uniform_candidate','bsgs_reference','aa_circuit1_a1'],'controls_executed':False,'local_archive_members_verified':13,'local_archive_member_manifest':m,'archive_pointer':ptr,'retained_s3_readback_receipt':rb,'new_network_requests_by_report':0,'derived_controller_timestamp_interval_seconds':elapsed,'scientific_cpu_wall_or_operation_metrics_available':False,'source_records':[{'path':REL+'/'+n,'bytes':(r/n).stat().st_size,'sha256':sha(r/n)} for n in names]+[{'path':str(supervisor_path),'bytes':supervisor_path.stat().st_size,'sha256':sha(supervisor_path)},{'path':str(progress_path),'bytes':progress_path.stat().st_size,'sha256':sha(progress_path)}],'sources_reviewed':['AGENTS.md','docs/agent-contract-extended.md#literature-first','.claude/skills/research-visuals/SKILL.md','harness/classical_ecdlp_transfer_study/driver.py','harness/classical_ecdlp_transfer_study/controller.py'],'canonical_graphs_changed':False,'reason_no_canonical_graph_update':'No mathematical observation, cost measurement or evidence decision was produced.'}
    (HERE/'facts.json').write_text(json.dumps(facts,indent=2)+'\n')
    (HERE/'pipeline.dot').write_text('''digraph failed_attempt {
 graph [rankdir=TB, bgcolor="white", pad="0.12", nodesep="0.25", ranksep="0.22", fontname="DejaVu Sans"];
 node [shape=box, style="rounded,filled", fontname="DejaVu Sans", fontsize=11, color="#334155", margin="0.15,0.08"];
 edge [color="#64748b", arrowsize=0.65, fontname="DejaVu Sans", fontsize=9];
 prepared [label="Local driver prepared source and frozen plan", fillcolor="#e0f2fe"];
 failed [label="Modal connection failed before Sandbox creation\\nConnectionError: Could not connect to the Modal server.", fillcolor="#fee2e2", color="#b91c1c"];
 future [label="Not reached: Sandbox 0 / probe 0 / engine 0\\nNo generated cohort or scalar-recovery data", fillcolor="#f1f5f9", style="rounded,filled,dashed"];
 archive [label="Failure records sealed: 13 members / 68,583 bytes\\nRUN-ECDLP-ea5986", fillcolor="#fef3c7"];
 prepared -> failed;
 failed -> future [style=dashed,label="recorded call counts"];
 failed -> archive [label="preserved evidence"];
}
''')
    source_link='https://github.com/isogeny-labs/crypto-autoresearcher/blob/'+PUB+'/'+REL+'/'
    command=['python3 harness/classical_ecdlp_transfer_study/driver.py run \\']
    argv=launch['argv'][3:]
    for i in range(0,len(argv),2): command.append('  '+shlex.quote(argv[i])+' '+shlex.quote(argv[i+1])+(' \\' if i+2<len(argv) else ''))
    md=f'''---
title: "Transfer study: pre-Sandbox connection failure"
date: "28 October 2026"
fontsize: 10pt
geometry: margin=16mm
colorlinks: true
---

This is an **operational observation report** for `EXP-ECDLP-ef7323`, `RUN-ECDLP-ea5986`, hypothesis `H-ECDLP-e1270c` and goal `GOAL-ECDLP-e70832`. It records a failed launch and preserved evidence. No mathematical conclusion or algorithm comparison is drawn.

The controller recorded `ConnectionError: Could not connect to the Modal server.` before creating a Sandbox. Its recorded Sandbox-create, plan-probe and engine-execution call counts are each **0**; `measurement_started=false` and `submission_ambiguous=false`. The seal contains no provider-context, generated cohort or raw scientific data. These are lifecycle observations, not zero scalar-recovery successes.

![Observed launch boundary and preservation path. All counts are recorded lifecycle counts for RUN-ECDLP-ea5986. A diagram is used because this attempt produced no comparable scientific measurements.](pipeline.pdf){{width=94%}}

| Recorded field | Observation |
|:--|:--|
| Controller start / finish (UTC) | 17:01:50.369184 / 17:02:47.501303 |
| Controller timestamp interval | {elapsed:.6f} s, derived from those timestamps |
| Driver / supervisor return codes | 1 / 3 |
| Supervisor state | `needs_reconciliation`; 0 output-validated trials |
| Transport / scientific validity | incomplete / `not_assessed` |
| Independent verifier / analysis | not executed / not executed |

The timestamp difference describes infrastructure waiting; it is not an algorithm runtime. No scientific CPU, wall-time, operation, success-rate or uncertainty measurements exist for this attempt. No remote measurement host was created. The local environment records Linux and Python 3.12.14; dirty state was not recorded. Planned uniform-guess, BSGS and A/A controls did not execute. The plan requested one trial, with a 3,600 s engine watchdog, 2 requested Modal CPU units and 12,288 MiB; these are requested settings, not observed resource use. No actual scientific target seeds were produced.

\\newpage

## Source and custody

The local environment records commit `{env['commit']}`. The plan binds transfer source revision `{c['plan']['source_revision_c']}`. The complete staged-source, protocol, plan, image and binary identities are retained without modification in `facts.json` and the original controller receipt. Code and image pins describe a planned executable; `native_binary_executed=false`.

The raw records were published at commit `{PUB}`. The sealed outer archive contains **13 exact members** and **68,583 bytes**. This report reread every member and compared its size and SHA-256 against the original member manifest and hydrated file. The retained artifact-readback receipt records a full S3 GET matching that size and digest; this report made no new network request.

Archive SHA-256:
`{e['sha256']}`

The [actual content-addressed object]({ptr['uri']}) is named by the retained identity pointer. `facts.json` preserves the exact URI, pointer, full readback receipt and every source/member hash. The archive retains source/plans and the connection-error receipt; it contains no scientific outcome rows.

## Exact driver command

The following is the argv in the immutable [command record]({source_link}command.txt); line continuations only format it for reading.

```sh
{chr(10).join(command)}
```

## Evidence and limits

Primary records read: [raw result]({source_link}raw-result.json), [run manifest]({source_link}manifest.yaml), [execution receipt]({source_link}execution-receipt.json), [member manifest]({source_link}modal-evidence-manifest.json), [identity pointer]({source_link}modal-evidence.tar.gz.blob.json), and [retained S3 readback]({source_link}artifact-readback.json). The controller receipt is a member of the sealed archive. The supervisor return/progress records and all hashes are retained in `facts.json`.

The research-visuals rule and the transfer driver/controller sealing code were checked for reporting scope. No literature or algorithm claim is assessed here. No verifier was run, no missing output rows were synthesized, and no cohort or candidate function was called. No canonical mathematical graph changes: this attempt supplies no new mathematical or cost observation. A separately authorized successor must keep its own run identity, records and eventual report; it cannot replace these failed-attempt bytes.
'''
    (HERE/'report.md').write_text(md)
    for ext in ['svg','pdf']:subprocess.run(['dot','-T'+ext,str(HERE/'pipeline.dot'),'-o',str(HERE/('pipeline.'+ext))],check=True)
    subprocess.run(['pandoc',str(HERE/'report.md'),'--pdf-engine=xelatex','--resource-path='+str(HERE),'--include-in-header='+str(HERE/'header.tex'),'-V','mainfont=DejaVu Serif','-V','monofont=DejaVu Sans Mono','-o',str(HERE/'report.pdf')],check=True)
    print(HERE/'report.pdf')

if __name__=='__main__':main()
