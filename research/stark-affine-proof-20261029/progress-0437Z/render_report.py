from pathlib import Path
import hashlib,json,html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
p=Path(__file__).resolve().parent
root=p.parent/'TASK-20261029-912498'
expected={'report.md':'68499c8493ef98bf6248c3cbb2b8055b953df8665be32665fca4d68aa2a74ca6','attestation.json':'58cf0dcbb3decaf2a10fb95b6e3b1954f52cc32fbc822659ea6e4ef996e08068','blind-math.md':'854236e982008c70057d981a072ed8683756734db3d1e5d1e2e325b9b6ed20b4'}
for name,digest in expected.items():
 assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
binding={'schema':'crypto.technical_review.progress.v1','as_of':'2026-10-29T04:37:00Z','archival_task':'TASK-20261029-4cdb4c','conductor_task':'T-781','proof_snapshot':'45934075ea81628e699d7778a523b2923269aa6a','handoff_snapshot':'9f5302e3ea60f04d5fa5ca55a3313eb1834c9bf6','review_task':'TASK-20261029-912498','review_files_sha256':expected,'machine_status':'not_verified','fidelity':'not_reviewed','review_outcome':'inconclusive','manual_math':'holds with stated nontriviality','native_last_observed':'2026-10-29T04:29Z','native_run_id':40817739806,'native_job_id':123263187245,'native_last_state':'in_progress','J2':'not_dispatched; awaiting native types','J3':'not_dispatched; awaiting native evidence and control','canonical_graphs':'No performance result changed; no performance graph update justified. New diagram describes proof obligations only.'}
(p/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
sections=[('Observation','The merged Rust API restricts transitions to a*x+b*y+c. Candidate Lean source contains six declarations: recovery, coefficient uniqueness, extensionality, multiplication obstruction, missing-probe control, and the zero-ring control.'),('Independent manual mathematics','J1 derived the statements from an isolated mathematical input. Recovery and uniqueness hold in all commutative rings, including the zero ring. Multiplication is not affine in a nontrivial ring; the zero ring is the exact exception. Two probes alone do not determine the affine family in a nontrivial ring.'),('Verification and fidelity','Machine status: NOT VERIFIED. Fidelity: NOT REVIEWED. Overall outcome: INCONCLUSIVE. The native workspace job was running at 04:29 UTC; that observation is not completion. J2 needs actual elaborated types; J3 needs the native module, six axiom outputs and rejection of the false strengthening.'),('Limits','Three probes determine a function within the affine family; they do not certify that an arbitrary function is affine. No proof of Rust BigUint/modular arithmetic, byte encoding, fingerprint injectivity, full STARK soundness, historical execution or performance is asserted.'),('Next actions','Collect the existing native run without restarting it. Bind its exact source and verifier inputs. Obtain independent J2/J3 reviews and native negative-control evidence. Archive the completed packet, inspect all applicable final-head CI checks, and only then deliver the scoped proof.'),('Graph and provenance','This diagram records proof obligations, not measured performance. No experiment or canonical performance graph changes follow from this partial review. Exact source and review hashes are in binding.json; the original reports remain immutable.')]
lines=['# Affine STARK proof review: progress snapshot','','As of 2026-10-29 04:37 UTC. T-781 / TASK-20261029-4cdb4c.','','Source proof commit: `'+binding['proof_snapshot']+'`.','Review handoff commit: `'+binding['handoff_snapshot']+'`.','PR: https://github.com/isogeny-labs/crypto-autoresearcher/pull/2681','','![Proof boundary](proof-boundary.svg)','']
for title,body in sections: lines += ['## '+title,'',body,'']
(p/'report.md').write_text('\n'.join(lines))
nodes=[('Merged Rust claim','typed affine expression','#e8f0fa'),('J1 manual mathematics','holds with stated assumptions','#e3f3e9'),('Native Lean / J2 / J3','pending; not verified','#fff0d5'),('Implementation / security','unproved bridges','#f5e4e4')]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="125" viewBox="0 0 960 125">','<rect width="960" height="125" fill="white"/>']
for i,(title,sub,color) in enumerate(nodes):
 x=5+i*240
 svg += [f'<rect x="{x}" y="15" width="225" height="75" rx="7" fill="{color}" stroke="#526579"/>',f'<text x="{x+112}" y="44" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(title)}</text>',f'<text x="{x+112}" y="68" text-anchor="middle" font-family="sans-serif" font-size="12">{html.escape(sub)}</text>']
 if i<3: svg += [f'<path d="M{x+226} 52h12" stroke="#526579" stroke-dasharray="3 2"/>']
svg += ['<text x="480" y="115" text-anchor="middle" font-family="sans-serif" font-size="12">Dashed connectors are review obligations, not established implications. T-781 / J1 TASK-20261029-912498.</text>','</svg>']
(p/'proof-boundary.svg').write_text('\n'.join(svg)+'\n')
c=canvas.Canvas(str(p/'report.pdf'),pagesize=(612,792),invariant=1)
c.setTitle('Affine STARK proof review - partial evidence')
c.setFont('Helvetica-Bold',17);c.drawString(38,754,'Affine STARK proof review')
c.setFont('Helvetica',9);c.drawString(38,736,'Progress snapshot 2026-10-29 04:37 UTC | T-781 | TASK-20261029-4cdb4c')
c.drawString(38,723,'PR #2681 | Candidate proof 45934075ea81 | J1 handoff 9f5302e3ea60')
for i,(title,sub,color) in enumerate(nodes):
 x=38+i*135;c.setFillColor(HexColor(color));c.setStrokeColor(HexColor('#526579'));c.roundRect(x,649,127,58,5,fill=1,stroke=1)
 c.setFillColor(HexColor('#182b40'));c.setFont('Helvetica-Bold',8);c.drawCentredString(x+63.5,684,title)
 c.setFont('Helvetica',7)
 for j,line in enumerate(simpleSplit(sub,'Helvetica',7,116)):c.drawCentredString(x+63.5,671-j*9,line)
 if i<3:c.setDash(2,2);c.line(x+128,678,x+134,678);c.setDash()
c.setFont('Helvetica',7);c.drawString(38,637,'Dashed connectors indicate outstanding obligations; no end-to-end implication is established.')
y=615
for title,body in sections:
 c.setFont('Helvetica-Bold',10);c.drawString(38,y,title);y-=14
 c.setFont('Helvetica',9)
 for line in simpleSplit(body,'Helvetica',9,536): c.drawString(38,y,line);y-=12
 y-=10
assert y>35,y
c.setFont('Helvetica',7);c.drawString(38,25,'Sources: CLAIMS.md, review-plan.json, J1 report.md + attestation.json; exact hashes in binding.json.')
c.save()
print(json.dumps({'pdf':str(p/'report.pdf'),'bottom_y':y,'review_hashes_verified':len(expected)}))
