"""Render this preparation report; no scientific program is invoked."""
from pathlib import Path
import json
import typst
import pymupdf


folder = Path(__file__).resolve().parent
diagram = {
    "scope": "Prospective E3 complete-operation path; no attack-cost claim",
    "nodes": [
        ["Surface + target", "frozen scientific input needed", "missing"],
        ["Projective equations", "13 combined software fixtures", "fixture"],
        ["Blind section solver", "not implemented here", "missing"],
        ["Integer coordinates", "not implemented here", "missing"],
        ["Full kernel + recovery", "supplied-vector verifier only", "fixture"],
    ],
}
(folder / "diagram-source.json").write_text(json.dumps(diagram,indent=2)+"\n")
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="290" viewBox="0 0 800 290">',
       '<rect width="800" height="290" fill="white"/>',
       '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="#444"/></marker></defs>']
positions=[(15,20),(280,20),(545,20),(545,145),(280,145)]
for (title,detail,status),(x,y) in zip(diagram['nodes'],positions):
    color='#dbeeff' if status=='fixture' else '#f0f0f0'
    dash='' if status=='fixture' else ' stroke-dasharray="5 3"'
    parts.append(f'<rect x="{x}" y="{y}" width="240" height="80" rx="6" fill="{color}" stroke="#444"{dash}/>')
    parts.append(f'<text x="{x+120}" y="{y+30}" text-anchor="middle" font-family="sans-serif" font-size="17">{title.replace("+","&#43;")}</text>')
    parts.append(f'<text x="{x+120}" y="{y+55}" text-anchor="middle" font-family="sans-serif" font-size="12">{detail}</text>')
for path in ('M255 60 H278','M520 60 H543','M665 100 V143','M545 185 H522'):
    parts.append(f'<path d="{path}" fill="none" stroke="#444" marker-end="url(#arrow)"/>')
parts.append('<text x="15" y="255" font-family="sans-serif" font-size="13">Blue: fixture checks. Dashed: outstanding scientific input or implementation.</text>')
parts.append('<text x="15" y="277" font-family="sans-serif" font-size="13">The verifier takes supplied vectors; it does not find sections or establish an attack cost.</text></svg>')
(folder/'diagram.svg').write_text('\n'.join(parts)+'\n')
pages=[
    ('E3 implementation preparation',[
        '2026-10-17. Observations and derived encoding only; no scientific approval, rank claim, performance claim or new scientific grid. Base: fd49e52ff70a859a09febf52112f3cfae0ec9455 (merged PR #2382).',
        'The prospective encoder uses Y^2 = X^3 + A X Z^4 + B Z^6, with x=X/Z^2 and y=Y/Z^3. It includes monic-denominator charts, finite Bezout saturation, infinity primitivity and smooth affine/O target conditions. The zero section is excluded.',
        'For supplied chi and encoding degree D: deg X <= 2(D+chi), deg Y <= 3(D+chi), and deg Z=e<=D. Primary unknowns: 5(D+chi)+e+2; saturation witnesses add variables and equations. A bounded search needs every chart e and every D up to its bound. D is not a certified canonical height, and model minimality/chi are not certified by this component.',
        '13 deterministic engineering fixtures pass. They include a rational section obtained by doubling (1,t) over F_31(t), specialization to O at a finite fibre, a base inversion with O at infinity, denominator saturation, and a known-answer order-19 group over F_17. Sage checks the doubled-section formula with its own group law. Earlier failed development attempts are retained.',
        'The supplied-vector recovery verifier checks every image/relation, full integer rank, exact kernel index ell, quotient calibration and the final scalar. A full-rank proper sublattice is refused. No section finder or MW-coordinate recovery algorithm is supplied.',
        'Next protocol: fix the surface before target selection; bind height/model conventions; include all charts and actual auxiliaries; separate planted/oracle input from blind solving. Charge setup, system construction, solving/censoring, coordinate recovery, kernel index and final verification. Coverage must be measured, not inferred from a point count.',
        'Sources: e3-projective/README.md, section_encoding.py, kernel_recovery.py and fixture-checks.json. The original frozen E3 stage-0 source and admission refusal remain unchanged.',
    ]),
    ('D1 inputs and admission preparation',[
        'Two public source snapshots now supply separate 30- and 31-point candidate lists. Exact Fraction arithmetic checks all 61 equation memberships and nonzero discriminants. The 31-point model/list matches the existing archived ICARM source exactly. A changed-coordinate and duplicate-index control are both refused.',
        'These are membership checks, not independence or rank certification. No full Gram matrix, certified height-error interval, saturated basis or D1 count/coverage run was produced. Existing validator/red-team reports retain the numerical-regulator limitation and correct the executor\'s spurious factor-10^10 discrepancy.',
        'Next D1 obligation: bind the actual generated subgroup, reproducible Gram-matrix constructor, height convention and certified error treatment. Then freeze an executable finite count/coverage workload. Do not substitute subgroup counts for a saturated full MW lattice.',
        'The isolated additive-admission prototype passes 28 synthetic fixtures. It retains original scientific fields/source bindings and separates fresh retry identities. Production preapproval, selector and supervisor code are unchanged. Technical fixture success grants no approval or execution authority.',
        'A network-enabled native Codex doctor returned zero and reported working inherited authentication and HTTP reachability, with a WebSocket warning. No inference or model/session probe ran. The remaining integration needs a genuine scoped SQLite/rollout persistence route and exact session metadata; doctor success cannot attest a model or retroactively verify this session.',
        'Actual E3/D4 launches and the distinct G1 retry still need supported additive admission/selection, exact committed amendment approval, source/archive bindings and live published ownership. The old refusals/failure remain immutable.',
        'Sources: d1-inputs/fetch-record.json, input-reconciliation.json, parser-refusal-controls.json; coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/README.txt, test-results.json and native-doctor-readiness.json.',
        'All 23 original full protocols remain incomplete. Existing canonical graphs/statuses are unchanged: this round creates no reviewed scientific finding. KB tools were unavailable; actual repository artifacts and fetched source bytes are cited. No deployed-key recovery or NFS sieving occurred.',
    ]),
]
source='#set page(paper:"a4",margin:17mm)\n#set text(size:10pt)\n'
for i,(title,paragraphs) in enumerate(pages):
    if i:source+='\n#pagebreak()\n'
    source+='\n= '+title+'\n\n'
    for j,p in enumerate(paragraphs):
        source+='#text('+json.dumps(p)+')\n\n'
        if i==0 and j==0:source+='#image("diagram.svg",width:100%)\n\n'
(folder/'report.typ').write_text(source.rstrip()+'\n')
typst.compile(str(folder/'report.typ'),output=str(folder/'report.pdf'),root=str(folder.parents[2]))
pdf=pymupdf.open(folder/'report.pdf')
for i,page in enumerate(pdf):
    page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(f'/tmp/snfs-continuation-page-{i+1}.png')
print(json.dumps({'pages':len(pdf),'pdf':str(folder/'report.pdf')}))
