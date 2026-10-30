from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
p=Path(__file__).resolve().parent
nodes=[('Frozen inputs','22 source bindings','#e8f0fa'),('Four candidates','4 to 0 targeted errors','#e3f3e9'),('Independent review','pending','#fff0d5'),('Live application','not admitted / not applied','#f5e4e4')]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="110"><rect width="960" height="110" fill="white"/>']
for i,(t,s,col) in enumerate(nodes):
 x=5+i*240;svg += [f'<rect x="{x}" y="10" width="225" height="70" rx="6" fill="{col}" stroke="#526579"/>',f'<text x="{x+112}" y="36" text-anchor="middle" font-family="sans-serif" font-size="15">{t}</text>',f'<text x="{x+112}" y="62" text-anchor="middle" font-family="sans-serif" font-size="12">{s}</text>']
 if i<3:svg += [f'<path d="M{x+226} 45h12" stroke="#526579" stroke-dasharray="3 2"/>']
svg+=['<text x="480" y="103" text-anchor="middle" font-family="sans-serif" font-size="12">Candidate metadata checks do not validate the experiments or change the live ledger. T-782.</text></svg>'];(p/'boundary.svg').write_text('\n'.join(svg)+'\n')
c=canvas.Canvas(str(p/'report.pdf'),pagesize=(612,792),invariant=1);c.setTitle('BINSTD attribution correction candidates');c.setFont('Helvetica-Bold',17);c.drawString(38,753,'BINSTD attribution correction candidates');c.setFont('Helvetica',9);c.drawString(38,735,'2026-10-29 | T-782 | TASK-20261029-8b1359 | APPLICATION PENDING')
for i,(t,s,col) in enumerate(nodes):
 x=38+i*135;c.setFillColor(HexColor(col));c.setStrokeColor(HexColor('#526579'));c.roundRect(x,650,127,62,5,fill=1,stroke=1);c.setFillColor(HexColor('#182b40'));c.setFont('Helvetica-Bold',9);c.drawCentredString(x+63.5,688,t);c.setFont('Helvetica',7)
 for j,line in enumerate(simpleSplit(s,'Helvetica',7,117)):c.drawCentredString(x+63.5,672-j*9,line)
 if i<3:c.setDash(2,2);c.line(x+128,680,x+134,680);c.setDash()
y=627
sections=[('Source and reading scope','Source: 7e45528b293fd42049b1486a03135670ab5ac55c. The packet hash-binds 22 documents. The coordinator read six KR cards and four effective proposal claim/prior-art/citation blocks. This is a repository-card comparison; it is not new full-text literature verification. The factor-base V card is heuristic and its citations are abstract_read.'),('Four proposed attribution changes','IDEA-20261003-43f871 and -4f41d0: preserve internal idea comparisons verbatim under internal_lineage. The latter also receives a truthful SAT/XOR-card comparator. IDEA-20261003-94078e and -c9c6c3: add explicitly retrospective comparisons, dated October 29, retaining scoped and inconclusive package boundaries.'),('Preservation and checks','Every parsed field outside prior_art equals its effective source. Original and prior replacement bytes are unchanged. The real pinned prior-art validator gives four errors before and zero for these four candidates. Twelve negative controls pass: claim mutation, invalid typed IDEA reference and absent prior_art, for each candidate.'),('Limitations and retained failures','This is a targeted function check, not full-ledger validation or live routing. The global error count has not changed. V1 candidates are retained; V2 repairs the misleading SAT/XOR comparator. An initial sparse-dependency failure was retained and corrected before the successful check.'),('Independent review and application','Review TASK-20261029-d6606a remains pending. Conductor refused ledger/registry admission because of T-650/T-673 migration reservations; only the report directory was admitted. Before application: acquire the proper scopes, verify current source hashes, validate all routes, compare full-corpus errors, and pass independent review and current-head CI.'),('Scientific and visual boundary','No seed, threshold, approval, claim, novelty status, result or experiment contract changes. No new theorem, experiment or attack-cost claim is established. The diagram is a procedure outline; no canonical performance graph is changed. Full details and exact hashes are in REPORT.md, sources.json and candidate-checks-v2.json.')]
for title,body in sections:
 c.setFont('Helvetica-Bold',10);c.drawString(38,y,title);y-=15;c.setFont('Helvetica',9)
 for line in simpleSplit(body,'Helvetica',9,536):c.drawString(38,y,line);y-=12
 y-=11
assert y>40,y
c.setFont('Helvetica',7);c.drawString(38,26,'Reviewable candidates only. Sources and verifier bindings are retained beside this PDF; no live ledger write occurred.');c.save();print('rendered one page; bottom',y)
