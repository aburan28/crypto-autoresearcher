from pathlib import Path
import json
p=Path(__file__).resolve().parent
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260"><rect width="1000" height="260" fill="#f4f7fa"/><style>text{font-family:Arial,sans-serif;fill:#183247;font-size:17px}.h{font-size:22px;font-weight:bold}</style><text x="24" y="35" class="h">DRAFT — NOT APPROVED; no M8191 scientific launch</text><g fill="#fff" stroke="#477c9c" stroke-width="2"><rect x="20" y="65" width="285" height="120" rx="8"/><rect x="355" y="65" width="285" height="120" rx="8"/><rect x="690" y="65" width="290" height="120" rx="8"/></g><text x="35" y="92">Bind clean source / installed binary</text><text x="35" y="122">control, custody, native watchdog</text><text x="35" y="152">wait for existing P192 terminal</text><text x="370" y="92">ONE native M8191 constructor</text><text x="370" y="122">1800s / sampled RSS 8GiB</text><text x="370" y="152">seal unreduced certificate</text><text x="705" y="92">ONE fresh independent verifier</text><text x="705" y="122">3600s / sampled RSS 8GiB</text><text x="705" y="152">LL, norm, differential, 8 points</text><g stroke="#477c9c" stroke-width="2" stroke-dasharray="6 5"><path d="M305 125H350"/><path d="M640 125H685"/></g><text x="25" y="220">Trusted SEC2 p/n | independent degree LL | compact known-endomorphism category | no expanded-board score</text></svg>'''
(p/'flow.svg').write_text(svg)
parts=['#set page(paper: "a4", margin: 17mm)','#set text(font: "Libertinus Serif", size: 9.5pt)','#set par(justify: false, leading: 0.5em)','#image("flow.svg", width: 100%)','#v(8pt)']
for name in ['PROTOCOL_DRAFT.md','P192_NEXT_ACTION_RULE.md']:
 if name.startswith('P192'):parts+=['#pagebreak()']
 for para in (p/name).read_text().split('\n\n'):
  if para.startswith('# '):parts+=['= '+para[2:]]
  elif para.startswith('## '):parts+=['== '+para[3:]]
  else:parts+=['#text('+json.dumps(para,ensure_ascii=False)+')','#parbreak()']
(p/'protocol.typ').write_text('\n'.join(parts)+'\n')
