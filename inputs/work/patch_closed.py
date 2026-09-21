import json, re
IN = '/Volumes/Volume/crypto-autoresearcher/inputs'

def rowtext_map(path):
    m = {}
    with open(path) as f:
        for line in f:
            s = line.rstrip('\n')
            if s.startswith('|'):
                cells = [c.strip() for c in s.split('|')][1:-1]
                if cells and re.match(r'^[A-Z][A-Z0-9]*(-[A-Za-z0-9]+)*$', cells[0]) and re.search(r'\d', cells[0]) and cells[0] != 'ID':
                    m.setdefault(cells[0], []).append(' '.join(cells))
    return m

MAIN = rowtext_map(f'{IN}/main_research_ledger.md')
IC = rowtext_map(f'{IN}/index_calculus_ledger.md')

BUL = {}
for path, lo, hi, short in [('main_research_ledger.md', 3, 116, 'autolab_main'), ('index_calculus_ledger.md', 3, 13, 'ecdlp_index_calculus')]:
    idx = 0
    with open(f'{IN}/{path}') as f:
        for ln, line in enumerate(f, 1):
            if ln < lo or ln > hi: continue
            mm = re.match(r'^\s*- \[([ x])\] (.*)$', line.rstrip('\n'))
            if mm:
                idx += 1
                BUL[f'OFQ-{short}-{idx:02d}'] = mm.group(2).strip()

QPATS = [
 r'\d[\d.,]*\s*x\s*(?:the\s*)?(?:11\*)?\s*rho',
 r'2\^\{?[\d.,]+\}?',
 r'\b[qn]\^\(?[\d.,/]+\)?',
 r'q\^\([\d./]+\)',
 r'rank[s]?\s*`?[\d,;/\.\-> ]+',
 r'nullity\s*`?[\d,;/\.\-> ]+',
 r'multiplicity[^.;]{0,30}zero',
 r'\d[\d,]*(?:\.\d+)?\s*(?:GB|MB|seconds|sec|minutes|hours|s\b)',
 r'\d[\d,]*(?:\.\d+)?\s*bits?',
 r'\d+/\d+(?:\s*(?:blind\s*)?(?:targets|descents|checks|mutations|recoveries|assertions))?',
 r'\d+(?:\.\d+)?\s*<=?\s*\d',
 r'\d[\d,]*\s+(?:candidates|rows|fixtures|curves|seeds|records|fibers|controls|samples|comparisons)',
 r'B\s*-\s*1',
 r'\d+\.\d{2,}',
]

def quants(text, limit=6):
    found = []
    for p in QPATS:
        for m in re.finditer(p, text, re.I):
            frag = m.group(0).strip(' `')
            frag = re.sub(r'\s+', ' ', frag)
            if 2 < len(frag) < 60 and frag not in found:
                found.append(frag)
            if len(found) >= limit:
                return found
    return found

with open(f'{IN}/ledger_inventory_20260724.json') as f:
    inv = json.load(f)

E = {e['id']: e for e in inv['entries']}
newct = []
for x in inv['closed_territory']:
    i = x['id']
    base = i.split('#')[0]
    texts = []
    if base in MAIN: texts = MAIN[base]
    elif base in IC: texts = IC[base]
    elif i in BUL: texts = [BUL[i]]
    qs = []
    for t in texts:
        qs = quants(t)
        if qs: break
    obst = x['obstruction']
    if qs:
        obst = 'QUANT: ' + '; '.join(qs) + ' || ' + obst
    newct.append({'id': i, 'source_file': x['source_file'], 'obstruction': obst[:700], 'scope_closed': x['scope_closed']})

inv['closed_territory'] = newct
with open(f'{IN}/ledger_inventory_20260724.json', 'w') as f:
    json.dump(inv, f, indent=1)
q = sum(1 for x in newct if x['obstruction'].startswith('QUANT'))
print('closed with QUANT:', q, '/', len(newct))
for x in newct[:3]:
    print('---', x['id'], x['obstruction'][:300])
