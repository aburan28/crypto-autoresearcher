import json, re
IN = '/Volumes/Volume/crypto-autoresearcher/inputs'
# Build text with leading row-ID cells stripped to reduce self-mention inflation
texts = []
for path in ['main_research_ledger.md', 'index_calculus_ledger.md', 'non_generic_transfer_search_20260610.md']:
    with open(f'{IN}/{path}') as f:
        for line in f:
            if line.startswith('|'):
                cells = line.split('|')
                if len(cells) > 2:
                    line = '|' + '|'.join(cells[2:])  # drop first cell (the ID)
            texts.append(line)
text = ''.join(texts).lower()

TERMS = [
 ('rho', r'\brho\b'), ('rank', r'\brank(s)?\b'), ('source-generation', r'\bsource(s)?\b'),
 ('relation', r'\brelation(s)?\b'), ('selector', r'\bselector(s)?\b'), ('certificate/verifier', r'\b(certificate|verifier|verification|verify)\b'),
 ('descent', r'\bdescent(s)?\b'), ('transfer', r'\btransfer(s)?\b'), ('toy/model-bound', r'\b(toy|model-bound)\b'),
 ('holdout', r'\bholdout(s)?\b'), ('graph', r'\bgraph(s)?\b'), ('factor base', r'\bfactor[- ]base\b'),
 ('ecfg', r'\becfg\b'), ('cover', r'\bcover(s|ing)?\b'), ('large-prime', r'\blarge[- ]prime(s)?\b'),
 ('divisor', r'\bdivisor(s)?\b'), ('kummer', r'\bkummer\b'), ('theta', r'\btheta\b'),
 ('norm', r'\bnorm(s)?\b'), ('kernel', r'\bkernel(s)?\b'), ('trace', r'\btrace(s)?\b'),
 ('fiber/cofiber', r'\b(co)?fiber(s)?\b'), ('mutation-control', r'\bmutation(s)?\b'),
 ('isogeny', r'\bisogen(y|ies)\b'), ('torsion', r'\btorsion\b'), ('orientation', r'\borientation(s)?\b'),
 ('pairing', r'\bpairing(s)?\b'), ('frobenius', r'\bfrobenius\b'), ('jacobian', r'\bjacobian(s)?\b'),
 ('kani', r'\bkani\b'), ('factor', r'\bfactor(s)?\b'), ('prym', r'\bprym(s)?\b'),
 ('semaev', r'\bsemaev\b'), ('weil', r'\bweil\b'), ('summation', r'\bsummation(s)?\b'),
 ('endomorphism', r'\bendomorphism(s)?\b'), ('polarization', r'\bpolarization(s)?\b'),
 ('gluing', r'\bgluing(s)?\b'), ('lattice', r'\blattice(s)?\b'), ('large prime (split)', None),
 ('bucket', r'\bbucket(s)?\b'), ('character', r'\bcharacter(s)?\b'), ('krylov', r'\bkrylov\b'),
 ('spectral', r'\bspectral\b'), ('bockstein', r'\bbockstein\b'), ('volcano', r'\bvolcano(es)?\b'),
]
counts = []
for name, pat in TERMS:
    if pat is None: continue
    counts.append({'term': name, 'count': len(re.findall(pat, text))})
counts.sort(key=lambda x: -x['count'])
top = counts[:25]
with open(f'{IN}/ledger_inventory_20260724.json') as f:
    inv = json.load(f)
inv['dominant_vocabulary'] = top
with open(f'{IN}/ledger_inventory_20260724.json', 'w') as f:
    json.dump(inv, f, indent=1)
for c in top: print(c)
