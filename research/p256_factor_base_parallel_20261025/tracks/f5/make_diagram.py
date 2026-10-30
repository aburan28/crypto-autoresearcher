from pathlib import Path
import json,html
p=Path(__file__).parent; data=json.loads((p/'identities.json').read_text())
D=json.loads((p/'attempt02-frobenius.json').read_text())['Delta_pi']
esc=html.escape
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="680" viewBox="0 0 1700 680">','<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#245975"/></marker></defs>','<rect width="1700" height="680" fill="white"/>','<g font-family="sans-serif" fill="#142d40">','<text x="30" y="35" font-size="24">F5: explicit P-256 rational quotient maps</text>','<text x="30" y="62" font-size="15">TASK-20261025-7144c5; exact implementation checks, no performance trial</text>']
def node(x,y,w,h,title,uid):
 parts.extend([f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#edf5fa" stroke="#245975"/>',f'<text x="{x+14}" y="{y+25}" font-size="17">{esc(title)}</text>',f'<text x="{x+14}" y="{y+47}" font-size="10">{esc(uid)}</text>',f'<text x="{x+14}" y="{y+67}" font-size="9">D_K={esc(D)}</text>',f'<text x="{x+14}" y="{y+87}" font-size="14">f_pi=1; f_E=1 (certified)</text>'])
node(30,280,650,105,'P-256: E / F_p, #E(F_p)=r',data['source']['curve_uid'])
for j,e in enumerate(data['destinations']):
 y=95+j*125;node(990,y,680,105,'Explicit endpoint degree '+str(e['ell'])+', candidate '+str(e['candidate_index']),e['curve_uid'])
 parts.extend([f'<path d="M680 332 C800 332, 835 {y+52}, 985 {y+52}" stroke="#245975" fill="none" stroke-width="2" marker-end="url(#arrow)"/>',f'<text x="800" y="{y+32}" font-size="14">degree {e["ell"]}; F_p</text>',f'<text x="800" y="{y+51}" font-size="12">separable; horizontal</text>'])
parts.extend(['<text x="30" y="625" font-size="16">All maps: dual o phi=[ell] as rational-function identities; gcd(ell,r)=1.</text>','<text x="30" y="650" font-size="14">Rational subgroup scheme does not mean rational kernel points. Complete maps and identities: attempt02-kernel-screen-*.json.</text>','</g></svg>'])
(p/'diagram.svg').write_text('\n'.join(parts)+'\n')
