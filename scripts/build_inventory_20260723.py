#!/usr/bin/env python3
"""Build ledger_inventory_20260723.json from the four fresh input files.

Factual extraction only:
- id set = prior-run inventory ids (validated against fresh text) + new table-row
  ids + named open-question ids (incl. HTML-comment proposed ids) + ECDLP-IDEA-###
  + PO-transfer/PO-004/NR-022 from the transfer-search note + bibliography ids
  + OFQ synthetic ids for untagged open questions (remapped by prefix match).
- All fields recomputed from the FRESH source text. Structural fields use a
  documented keyword classifier; "not stated" when no evidence.
"""
import json, re, os
from collections import defaultdict

IN = '/Volumes/Volume/crypto-autoresearcher/inputs'
OUT = '/Volumes/Volume/crypto-autoresearcher/outputs'
F_MAIN = 'research_ledger_main.md'
F_IC = 'research_ledger_ic_state.md'
F_TR = 'non_generic_transfer_search_20260610.md'
F_BIB = 'bibliography.json'

texts = {f: open(os.path.join(IN, f)).read() for f in (F_MAIN, F_IC, F_TR)}
bib = json.load(open(os.path.join(IN, F_BIB)))
NS = 'not stated'

def parse_sections(txt):
    lines = txt.split('\n')
    secs, cur = [], ('(preamble)', 0)
    for i, ln in enumerate(lines):
        if ln.startswith('## '):
            secs.append((cur[0], cur[1], i)); cur = (ln[3:].strip(), i)
    secs.append((cur[0], cur[1], len(lines)))
    return secs, lines

ID_CELL = re.compile(r'^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$|^P[0-9]{3,4}$|^NR-[0-9]+$')
entries, order = {}, []

def add_entry(idv, source, section, cells, header, kind='table', **kw):
    if idv not in entries:
        entries[idv] = {'id': idv, 'sources': [], 'section': section,
                        'cells': cells, 'header': header, 'kind': kind, **kw}
        order.append(idv)
    else:
        e = entries[idv]
        if kind == 'table' and sum(len(c) for c in cells) > sum(len(c) for c in e['cells']):
            e.update({'cells': cells, 'header': header, 'section': section, 'kind': kind})
    if source and source not in entries[idv]['sources']:
        entries[idv]['sources'].append(source)

def split_cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]

def parse_ledger(fname):
    secs, lines = parse_sections(texts[fname])
    for sname, a, b in secs:
        header = None
        for i in range(a, b):
            ln = lines[i]
            if not (ln.startswith('|') and ln.rstrip().endswith('|')):
                continue
            cells = split_cells(ln)
            if cells and cells[0] == 'ID':
                header = cells; continue
            if set(''.join(cells)) <= set('-: '):
                continue
            first = cells[0].strip('`').strip()
            ids = [x.strip() for x in first.split('/') if x.strip()]
            # propagate family prefix: "ECFG-P253/P254" -> ECFG-P253, ECFG-P254
            full_ids = []
            for j, p in enumerate(ids):
                if j == 0:
                    full_ids.append(p)
                elif '-' in p:
                    full_ids.append(p)
                elif p[0].isdigit():
                    full_ids.append(ids[0][:ids[0].rfind('-') + 1] + p)
                else:  # letter-led short tail, e.g. P254 / N076
                    full_ids.append(ids[0][:ids[0].find('-') + 1] + p)
            for idv in full_ids:
                if ID_CELL.match(idv) and len(cells) >= 3:
                    add_entry(idv, fname, sname, cells, header)

parse_ledger(F_MAIN)
parse_ledger(F_IC)

# ------------------------------------------------------- questions
def parse_questions(fname):
    secs, lines = parse_sections(texts[fname])
    qs = []
    for sname, a, b in secs:
        if 'frontier' not in sname.lower():
            continue
        for i in range(a, b):
            m = re.match(r'- \[([ x])\]\s*(.*)', lines[i])
            if m:
                qs.append({'checked': m.group(1) == 'x', 'text': m.group(2).strip(), 'source': fname})
    return qs

questions = parse_questions(F_MAIN) + parse_questions(F_IC)

BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')
QID = re.compile(r'\b((?:RT|RITT|ISOWALK|MODHECKE|AMORT|DRINFELD|ZILBERPINK|PADICHT|BAR|TRANSFER|ECFG|ISO|SHA1)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b')
named_q, unnamed_q = {}, []
for q in questions:
    ids = set()
    for b in BOLD_RE.findall(q['text']):
        head = b.split(':')[0]
        ids.update(QID.findall(head))
    if ids:
        for idv in sorted(ids):
            named_q.setdefault(idv, q)
    else:
        unnamed_q.append(q)

for idv, q in named_q.items():
    if idv not in entries:
        add_entry(idv, q['source'], 'Open frontier questions', [idv, q['text']], ['ID', 'Question'], kind='question')
    else:
        add_entry(idv, q['source'], entries[idv]['section'], entries[idv]['cells'], entries[idv]['header'], kind=entries[idv]['kind'])

# proposed ids from HTML comment in main ledger preamble
comment_ids = set()
secs, lines = parse_sections(texts[F_MAIN])
for i in range(0, 12):
    comment_ids.update(QID.findall(lines[i]))
for idv in sorted(comment_ids):
    if idv not in entries:
        add_entry(idv, F_MAIN, 'Open frontier questions (proposed-id comment)', [idv, ''], ['ID'], kind='proposed')

# ------------------------------------------------------------- OFQ remap
prior = json.load(open(os.path.join(IN, 'ledger_inventory_20260719.json')))
prior_by_id = {}
for o in prior:
    prior_by_id.setdefault(o['id'], o)

def norm(s):
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())

prior_ofq = {k: v for k, v in prior_by_id.items() if k.startswith('OFQ-')}
used_ofq, new_ofq = set(), []
maxn = defaultdict(int)
for k in prior_ofq:
    m = re.search(r'-(\d+)$', k); maxn[k.split('-')[1]] = max(maxn[k.split('-')[1]], int(m.group(1)))

ofq_norm = {k: norm(v.get('title')) for k, v in prior_ofq.items()}
for q in unnamed_q:
    n = norm(q['text'])
    hit = None
    for k, pn in ofq_norm.items():
        if k in used_ofq or not pn:
            continue
        if n[:80] == pn[:80] or (len(n) >= 80 and n.startswith(pn)) or (len(pn) >= 80 and pn.startswith(n)):
            hit = k; break
    if hit is None:  # looser fallback: token jaccard >= .8
        ntok = set(re.findall(r'[a-z0-9]{4,}', n)); best, bs = None, 0.0
        for k, pn in ofq_norm.items():
            if k in used_ofq: continue
            ptok = set(re.findall(r'[a-z0-9]{4,}', pn))
            if not ptok: continue
            sc = len(ntok & ptok) / max(1, len(ntok | ptok))
            if sc > bs: best, bs = k, sc
        if bs >= 0.8: hit = best
    if hit is None:
        ledger = 'autolab_main' if q['source'] == F_MAIN else 'ecdlp_index_calculus'
        maxn[ledger] += 1
        hit = f"OFQ-{ledger}-{maxn[ledger]:02d}"
        new_ofq.append((hit, q['text'][:80]))
    used_ofq.add(hit)
    add_entry(hit, q['source'], 'Open frontier questions', [hit, q['text']], ['ID', 'Question'], kind='question', checked=q['checked'])

orphan_ofq = sorted(set(prior_ofq) - used_ofq)
for k in orphan_ofq:
    o = prior_ofq[k]
    add_entry(k, None, 'Open frontier questions', [k, o.get('title') or ''], ['ID', 'Question'], kind='question', orphan=True)

# ------------------------------------------------------------------ IDEA family
for m in sorted(set('ECDLP-IDEA-' + x for x in re.findall(r'\b(?:ECDLP-IDEA|IDEA)-(\d{3})\b', texts[F_IC]))):
    add_entry(m, F_IC, '(referenced idea contract)', [m, ''], ['ID'], kind='referenced')

# ------------------------------------------------------------- transfer search
tr = texts[F_TR]
for idv in sorted(set(re.findall(r'\bPO-transfer-\d{3}\b', tr))):
    add_entry(idv, F_TR, '(transfer-search)', [idv, ''], ['ID'], kind='transfer-search')
for idv in ('PO-004', 'NR-022'):
    add_entry(idv, F_TR, '(transfer-search reference)', [idv, ''], ['ID'], kind='referenced')

# ------------------------------------------------------------------ bibliography
for b in bib:
    add_entry(b['id'], F_BIB, '(bibliography)', [b['id'], b.get('title', '')], ['ID', 'Title'], kind='bibliography', bib=b)

# --------------------------------------------- carry prior ids not captured fresh
carried = []
for k, o in prior_by_id.items():
    if k in entries or k.startswith('OFQ-'):
        continue
    if ' / ' in k:   # combined question id -> split
        for part in k.split(' / '):
            if part not in entries:
                add_entry(part, F_MAIN, 'Open frontier questions', [part, o.get('title') or ''], ['ID', 'Question'], kind='question')
        carried.append(k + ' (split)')
        continue
    srcs = [f for f in (F_MAIN, F_IC, F_TR) if k in texts[f]]
    add_entry(k, None, o.get('section') or '(referenced)',
              [k, o.get('title') or '', o.get('status_cell') or '', '', o.get('next_branch') or ''],
              ['ID', 'Claim', 'Status', 'x', 'Next'], kind='carried', prior=o)
    for s in srcs:
        if s not in entries[k]['sources']:
            entries[k]['sources'].append(s)
    carried.append(k)

print("questions:", len(questions), "| unnamed:", len(unnamed_q), "| named ids:", sorted(named_q))
print("comment ids:", sorted(comment_ids))
print("new OFQ:", new_ofq)
print("orphan OFQ:", orphan_ofq)
print("carried prior:", carried)
print("total entries:", len(entries))

import pickle
pickle.dump({'entries': entries, 'order': order, 'questions': questions},
            open('/tmp/build_stage1.pkl', 'wb'))
