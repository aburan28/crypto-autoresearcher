from pathlib import Path
import argparse, json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import typst, pymupdf

parser=argparse.ArgumentParser(description='Render the saved historical inventory without running experiments.')
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--out',type=Path,required=True,help='A new output directory; preserve the archived report.')
args=parser.parse_args();ROOT=args.root.resolve();OUT=args.out.resolve()
OUT.mkdir(parents=True,exist_ok=False)
rows=json.loads((ROOT/'snfs-ecdlp-followup/all-lead-dispositions.json').read_text())
records=json.loads((ROOT/'tracking.json').read_text())['records']
assert len(rows)==23 and {x['provisional_id'] for x in rows}=={x['provisional_id'] for x in records}
rows=sorted(rows,key=lambda x:x['provisional_id'])
fig,ax=plt.subplots(figsize=(10,2.8));ax.set_xlim(0,10);ax.set_ylim(0,3);ax.axis('off')
labels=['E1 / E2\nCertified surface, rank\nand basis heights','E4\nCoverage and degree\nfrom the actual encoding','E3\nBlind section finding\nplus basis coordinates','Full operation\nRelations, verified log\nand complete costs']
for i,label in enumerate(labels):
 x=.08+i*2.5
 ax.add_patch(FancyBboxPatch((x,.8),2.22,1.3,boxstyle='round,pad=.08',edgecolor='#29536f',facecolor='#edf4f7'))
 ax.text(x+1.11,1.45,label,ha='center',va='center',fontsize=9)
 if i<3:ax.annotate('',xy=(x+2.48,1.45),xytext=(x+2.25,1.45),arrowprops={'arrowstyle':'->','color':'#29536f'})
ax.text(5,.25,'Research dependencies only; no arrow asserts feasibility or a speedup.',ha='center',fontsize=9)
fig.tight_layout();fig.savefig(OUT/'dependencies.svg');plt.close(fig)
T=lambda s:'#text('+json.dumps(s,ensure_ascii=False)+')'
intro=[
'Historical evidence inventory — October 17, 2026',
'This inventory reproduces the existing local pilot scopes and limitations from the imported follow-up record. It is not an independent scientific review, harness execution-proof evidence, a status transition, or completion of the original full protocols.',
'E3 with E1/E2/E4 support is the recorded conditional research priority. No demonstrated attack advantage follows. The diagram shows obligations that must be charged and verified before a completed-operation comparison against the frozen index-calculus baseline. The rho gap is reported as the distance remaining.',
'All 23 original leads retain their canonical IDEA identities in canonical-coverage.json and tracking.json. The original ledger, audit corrections, code, raw observations, local reports and requirements are preserved in sibling directories. The current canonical execution attempts, their failures and outstanding contracts are tracked separately in STATUS.md.',
'Toy controls have limited scope. A working prototype is finite control, never a subexponential ECDLP result. Original theorem-closed items remain receipt-only. No deployed-key recovery or NFS sieving is in scope.',
'Source of the following table: snfs-ecdlp-followup/all-lead-dispositions.json. Each row reproduces pilot_scope and full_protocol_limitations literally; historical conclusions and draft spending gates are not new approvals. Current execution and budget conventions remain those in STATUS.md.',
'Tracking PR: https://github.com/aburan28/crypto-autoresearcher/pull/2382'
]
source='#set page(paper:"a4",margin:16mm)\n#set text(size:10pt)\n#set par(leading:0.5em)\n= Historical evidence inventory\n\n'+'\n\n'.join(T(s) for s in intro[1:3])+'\n\n#image("dependencies.svg",width:100%)\n\n'+'\n\n'.join(T(s) for s in intro[3:])
for start in (0,8,16):
 group=rows[start:start+8]
 source+='\n#pagebreak()\n#set text(size:8.2pt)\n= Pilot scope and outstanding work\n'+T(f'Historical inventory: entries {start+1}–{start+len(group)} of 23. Full original protocols remain outstanding.')+'\n\n#table(columns:(0.7fr,2.0fr,3.3fr),inset:6pt,stroke:0.4pt + luma(190),align:top,table.header([*Lead*],[*Historical pilot scope*],[*Explicit limitations*]),\n'
 for r in group:
  source+=','.join('['+T(r[k])+']' for k in ('provisional_id','pilot_scope','full_protocol_limitations'))+',\n'
 source+=')\n'
(OUT/'report.typ').write_text(source)
(OUT/'report.md').write_text('# Historical evidence inventory\n\n'+'\n\n'.join(intro[1:])+'\n\n'+ '\n\n'.join(f"**{r['provisional_id']}** — {r['pilot_scope']}\n\n{r['full_protocol_limitations']}" for r in rows)+'\n')
typst.compile(str(OUT/'report.typ'),output=str(OUT/'report.pdf'),root=str(OUT))
manifest={'scope':'Historical inventory only; no trial or independent scientific review','inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'tracking.json',ROOT/'snfs-ecdlp-followup/all-lead-dispositions.json']},'lead_count':len(rows),'canonical_id_count':len({r['canonical_idea_id'] for r in records}),'claims_new_attack_advantage':False,'original_full_campaigns_completed':False}
(OUT/'inventory.json').write_text(json.dumps(manifest,indent=2)+'\n')
pdf=pymupdf.open(OUT/'report.pdf')
for i,page in enumerate(pdf):
 page.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(f'/tmp/snfs-historical-inventory-page-{i+1}.png')
 print('PAGE',i+1,'characters',len(page.get_text()))
print('TOTAL PAGES',len(pdf))
