#!/usr/bin/env python3
"""Build prior_proposals_index.json from all proposal corpora.

Corpora:
  A. inputs/idea_generation_*.md  (20 batch files)
  B. research_directions_20260717.md, research_directions_20260718.md
  C. ideas/ registry: active (*.md at top level), deferred/, rejected/
Never fabricate: missing fields -> "not stated".
"""
import re, json, sys
from pathlib import Path

ROOT = Path('/Volumes/Volume/crypto-autoresearcher')
INPUTS = ROOT / 'inputs'
NS = "not stated"

# ---------------------------------------------------------------- batch files
BATCH_FILES = sorted(INPUTS.glob('idea_generation_2026071*.md'))
REPORT_FILES = [ROOT / 'research_directions_20260717.md',
                ROOT / 'research_directions_20260718.md']

CAND_RE = re.compile(r'^(#{2,4})\s*Candidate:?\s+(.+?)\s*$')
ANY_HDR_RE = re.compile(r'^(#{1,4})\s+\S')

def candidate_blocks(lines):
    hdrs = []  # (line_no, level, title)
    for i, ln in enumerate(lines):
        m = CAND_RE.match(ln)
        if m:
            hdrs.append((i, len(m.group(1)), m.group(2)))
    out = []
    for j, (i, lvl, title) in enumerate(hdrs):
        end = len(lines)
        if j + 1 < len(hdrs):
            end = hdrs[j + 1][0]
        for k in range(i + 1, end):
            m2 = ANY_HDR_RE.match(lines[k])
            if m2 and len(m2.group(1)) <= lvl:
                end = k
                break
        out.append((title, lines[i + 1:end]))
    return out

SEC_RE = re.compile(r'^(#{2,5})\s+(.+?)\s*$')

def get_section(block_lines, *name_patterns):
    """Return (text_lines) of the section whose header matches any pattern."""
    start = None
    for i, ln in enumerate(block_lines):
        m = SEC_RE.match(ln)
        if m:
            title = m.group(2).strip()
            for pat in name_patterns:
                if re.match(pat, title, re.I):
                    start = i + 1
                    break
            if start is not None:
                break
    if start is None:
        return None
    end = len(block_lines)
    for k in range(start, len(block_lines)):
        if SEC_RE.match(block_lines[k]):
            end = k
            break
    txt = [l for l in block_lines[start:end]]
    # strip trailing separators/blank
    while txt and (not txt[-1].strip() or txt[-1].strip() == '---'):
        txt.pop()
    return txt

def flatten(lines, max_chars=2000):
    if not lines:
        return NS
    t = ' '.join(l.strip() for l in lines if l.strip() and l.strip() != '---')
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:max_chars] if t else NS

FP_KEYS = {
    'algebraic_object': ['algebraic object', 'object'],
    'relation_generation_primitive': ['relation-generation primitive', 'relation primitive',
                                      'relation-gen primitive', 'relation-gen',
                                      'relation generation primitive'],
    'compression_primitive': ['compression primitive', 'compression'],
    'descent_mechanism': ['descent mechanism', 'descent'],
    'claimed_cost_exponent': ['dominant cost exponent', 'dominant cost', 'dominant exponent',
                              'dominant', 'cost exponent', 'cost'],
}

def parse_fingerprint(lines):
    tags = {k: NS for k in FP_KEYS}
    raw = flatten(lines, 4000)
    if not lines:
        return tags, NS
    text = '\n'.join(lines)
    # list style:  - key: value (value may wrap onto following indented lines)
    items = []
    cur = None
    for ln in lines:
        m = re.match(r'\s*[-*]\s*([A-Za-z][A-Za-z0-9 /_()-]{1,60}?)\s*:\s*(.*)$', ln)
        if m:
            if cur:
                items.append(cur)
            cur = [m.group(1).strip().lower(), m.group(2).strip()]
        elif cur and ln.strip() and not ln.strip().startswith('#'):
            cur[1] += ' ' + ln.strip()
        elif not ln.strip():
            if cur:
                items.append(cur)
                cur = None
    if cur:
        items.append(cur)
    if not items:
        # parenthesized / inline style: F = (key: value; key2: value2) or positional
        body = re.sub(r'\s+', ' ', text).strip()
        body = re.sub(r'^\s*`?F(?:\([^)]*\))?\s*(?:\(C\))?\s*=\s*', '', body)
        body = body.strip().strip('()')
        parts = re.split(r';(?=\s*[a-z][a-z0-9 /_()-]{1,45}\s*[:=])', body)
        first_positional = True
        for p in parts:
            m = re.match(r'\s*([a-z][a-z0-9 /_()-]{1,45}?)\s*[:=]\s*(.*)', p, re.I)
            if m:
                items.append((m.group(1).strip().lower(), m.group(2).strip()))
            elif p.strip() and first_positional:
                items.append(('object', p.strip()))
            first_positional = False
    for k, v in items:
        kn = re.sub(r'\s+', ' ', k).strip()
        for field, aliases in FP_KEYS.items():
            if tags[field] == NS and any(kn == a or kn.startswith(a + ' ') for a in aliases):
                tags[field] = v[:600] if v else NS
    return tags, raw

ID_TOKEN_RE = re.compile(
    r'\b(?:ECFG|TRANSFER|ISO|SHA1|PO|NR|RT|MX|IR|POS|EV|DEC|EXP|RQ|SYN|CLM|FINDING|H|N|P|B)'
    r'(?:-[A-Za-z0-9]+){1,4}\b|\bP1[0-9]{3}(?:-R\d+)?\b|\bECDLP-IDEA-\d+\b'
    r'|\bB-[a-z][a-z0-9=-]{2,}\b|\bRT-1[0-9]{3}\b|\bNR-[0-9]{3,4}\b|\bPO-[0-9]{3}\b')
BACKTICK_RE = re.compile(r'`([^`]{2,80})`')

def parse_ledger_ids(lines):
    if not lines:
        return []
    text = '\n'.join(lines)
    ids = []
    for m in ID_TOKEN_RE.finditer(text):
        ids.append(m.group(0))
    for m in BACKTICK_RE.finditer(text):
        t = m.group(1).strip()
        if re.match(r'^[A-Z][A-Z0-9-]{2,60}$', t) and not t.endswith('.md'):
            ids.append(t)
    seen, out = set(), []
    for i in ids:
        i = i.strip().rstrip('.,;:')
        if i and i not in seen and not i.lower().endswith(('.md', '.json', '.yaml', '.py')):
            seen.add(i)
            out.append(i)
    return out[:25]

CAT_OF = {'conservative': 'conservative', 'representation': 'representation',
          'representation-changing': 'representation', 'high-risk': 'high_risk',
          'a': 'conservative', 'b': 'representation', 'c': 'high_risk'}
CAT_WORD_RE = re.compile(r'(?i)\b(conservative|representation(?:-changing)?|high-risk|high risk)\b')
REJ_RE = re.compile(r'(?i)\b(REJECT(?:ED|ION)?|DEMOTED|INCOMPLETE|DUPLICATE|ADJACENT)\b')

def clean_name(header_title):
    t = header_title
    t = re.sub(r'\*\(.*?\)\*', ' ', t)
    t = re.sub(r'★.*$', ' ', t)
    t = re.sub(r'⊗', ' ', t)
    t = re.sub(r'`[^`]*`', ' ', t)
    t = re.sub(r'\((?:ECFG-)?P1[0-9]{3}\)', ' ', t)
    t = re.sub(r'(?i)\s*—\s*(CONSERVATIVE|REPRESENTATION|HIGH-RISK)\s+WINNER.*$', ' ', t)
    t = re.sub(r'(?i)\s*—\s*(REJECTED|DEMOTED).*$', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' —-')
    return t

def parse_label(name):
    m = re.search(r'(?<![A-Za-z0-9])([ABCD])(\d+)(?![0-9])', name)
    return (m.group(1) + m.group(2)) if m else None

def _find_needle(line, needle):
    return re.search(r'(?<![A-Za-z0-9-])' + re.escape(needle) + r'(?![A-Za-z0-9])', line)

def winner_scan(full_text, candidates, header_lines):
    """Priority-based winner assignment per file."""
    lines = full_text.split('\n')
    # per candidate: {cat: best_priority}
    best = {i: {} for i in range(len(candidates))}
    dispositions = {i: [] for i in range(len(candidates))}

    def needles(c):
        ns = []
        if c['label'] != NS:
            ns.append(c['label'])
        if c.get('slug') and c['slug'] != NS:
            ns.append(c['slug'])
        return ns

    def bump(i, cat, prio):
        cur = best[i].get(cat, -1)
        if prio > cur:
            best[i][cat] = prio

    # priority 3: inline header markers
    for i, c in enumerate(candidates):
        hl = header_lines[i]
        m = re.search(r'(?i)(conservative|representation(?:-changing)?|high-risk)\s+winner', hl)
        if m:
            bump(i, CAT_OF[m.group(1).lower().replace('high risk', 'high-risk')], 3)
        if re.search(r'(?i)\bwinner\b', hl) and not m:
            pass  # generic winner mention without category: ignore

    # identify "winners section" line ranges (after a Winners/Selected winners header)
    winsec = set()
    for n, ln in enumerate(lines):
        stripped = re.sub(r'^[#\s*>]+', '', ln.strip())
        if re.match(r'(?i)^(selected\s+(three\s+)?)?winners\b', stripped) \
           and not re.search(r'(?i)(experiment|contract|red.?team|disguised)', stripped):
            for k in range(n, min(n + 12, len(lines))):
                winsec.add(k)

    for n, ln in enumerate(lines):
        if 'winner' not in ln.lower() and n not in winsec:
            continue
        is_table = ln.lstrip().startswith('|')
        cells = [c.strip() for c in ln.split('|')] if is_table else None
        first_cell = cells[1] if cells and len(cells) > 1 else ''
        cats_in_line = CAT_WORD_RE.findall(ln)
        cat = None
        mcat = re.search(r'(?i)(conservative|representation(?:-changing)?|high-risk|high risk)[ -]winner', ln)
        if mcat:
            cat = mcat.group(1).lower().replace('high risk', 'high-risk')
        else:
            mcat2 = re.search(r'(?i)winner\s*\((conservative|representation(?:-changing)?|high-risk)\)', ln)
            if mcat2:
                cat = mcat2.group(1).lower()
            else:
                mcat3 = re.search(r'(?i)\b([ABC])-winner\b', ln)
                if mcat3:
                    cat = CAT_OF[mcat3.group(1).lower()]
        cat = CAT_OF.get(cat, cat) if cat else None
        if not cat and cats_in_line:
            cat = CAT_OF.get(cats_in_line[0].lower().replace('high risk', 'high-risk'))
        for i, c in enumerate(candidates):
            for nd in needles(c):
                if not _find_needle(ln, nd):
                    continue
                # priority 2: table row, needle in first (or second) ID cell
                if is_table and (_find_needle(first_cell, nd) or
                                 (len(cells) > 2 and _find_needle(cells[2], nd))):
                    if cat:
                        bump(i, cat, 2)
                    else:
                        # category from candidate's own group letter
                        if c['label'] != NS and c['label'][0] in 'ABC':
                            bump(i, CAT_OF[c['label'][0].lower()], 2)
                # priority 1: winners-section line with category+needle proximity
                if n in winsec and cat:
                    bump(i, cat, 1)
                # proximity: needle immediately followed by "(conservative)" etc.
                if re.search(re.escape(nd) + r'[^A-Za-z0-9)]{0,3}\((?:conservative|representation|high-risk)', ln, re.I):
                    bump(i, cat or 'conservative', 1)
    # resolve
    assigned = {}
    for cat in ['conservative', 'representation', 'high_risk']:
        cands_cat = [(i, p[cat]) for i, p in best.items() if cat in p]
        if not cands_cat:
            continue
        top = max(p for _, p in cands_cat)
        winners = [i for i, p in cands_cat if p == top]
        assigned[winners[0]] = cat  # ties -> first in file order
    for i in range(len(candidates)):
        candidates[i]['selected_winner'] = assigned.get(i, NS)
        candidates[i]['batch_disposition'] = NS
    # dispositions: ranking-table row verdict for the candidate
    for n, ln in enumerate(lines):
        if not ln.lstrip().startswith('|'):
            continue
        cells = [c.strip() for c in ln.split('|')]
        if len(cells) < 4:
            continue
        idzone = cells[1] + ' ' + (cells[2] if len(cells) > 2 else '')
        for i, c in enumerate(candidates):
            for nd in needles(c):
                if _find_needle(idzone, nd):
                    verdict = cells[-2] if cells[-1] == '' else cells[-1]
                    verdict = re.sub(r'\*\*', '', verdict).strip()
                    if verdict and not re.match(r'^(Cand|ID|Candidate|:-|-)', verdict):
                        dispositions[i].append(verdict[:220])
    for i in range(len(candidates)):
        if dispositions[i]:
            # prefer a verdict containing winner/reject info
            ds = dispositions[i]
            ds.sort(key=lambda d: (('winner' not in d.lower()), (not REJ_RE.search(d))))
            candidates[i]['batch_disposition'] = ds[0]

GROUP_HDR_RE = re.compile(r'^#{1,4}\s+(?:\d+\.\s*)?Group\s+([ABCD])\s*[—-]\s*(.+?)\s*$', re.I)
SET_HDR_RE = re.compile(r'^#{1,4}\s+(?:\d+\.\s*)?Candidate set\s+([ABCD])\s*[—-]\s*(.+?)\s*$', re.I)

def group_map(lines):
    """line_no -> (letter, description) for group headers; candidates after inherit."""
    spans = []
    for i, ln in enumerate(lines):
        m = GROUP_HDR_RE.match(ln) or SET_HDR_RE.match(ln)
        if m:
            spans.append((i, m.group(1).upper(), m.group(2).strip()))
    return spans

GROUP_DEFAULT = {
    'A': 'conservative extensions', 'B': 'representation changes',
    'C': 'high-risk speculative mechanisms', 'D': 'negative-theory / barrier candidates',
}

def parse_batch_file(path):
    text = path.read_text(errors='replace')
    lines = text.split('\n')
    gspans = group_map(lines)
    # candidate header line numbers for group assignment
    cands = []
    hdr_positions = []
    for i, ln in enumerate(lines):
        m = CAND_RE.match(ln)
        if m:
            hdr_positions.append((i, m.group(2), ln))
    blocks = candidate_blocks(lines)
    nblocks = len(blocks)
    for idx, ((title, block), (pos, _, raw_hdr)) in enumerate(zip(blocks, hdr_positions)):
        name = clean_name(title)
        label = parse_label(title) or parse_label(name)
        if not label and nblocks == 12:
            label = 'ABCD'[idx // 3] + str(idx % 3 + 1)  # positional fallback
        slug_m = re.match(r'^([A-Z][A-Z0-9-]{3,}?)(?:\s+—|\s+-|\s*$)', name)
        slug = slug_m.group(1) if slug_m else None
        # group
        gletter, gdesc = None, None
        for (sp, letter, desc) in gspans:
            if sp < pos:
                gletter, gdesc = letter, desc
        if not gletter and label:
            gletter = label[0]
        group = (f"{gletter} — {gdesc}" if gletter and gdesc
                 else (f"{gletter} — {GROUP_DEFAULT.get(gletter,'')}".strip(' —') if gletter
                       else NS))
        mech = flatten(get_section(block, r'One-sentence mechanism'))
        status = flatten(get_section(block, r'Status$'), 400)
        novelty = flatten(get_section(block, r'Novelty classification'), 600)
        fp_lines = get_section(block, r'Semantic fingerprint')
        tags, fp_raw = parse_fingerprint(fp_lines)
        ledger = parse_ledger_ids(get_section(block, r'Nearest ledger entries'))
        fatal = flatten(get_section(block, r'Likely fatal obstruction'), 700)
        # ledger-id embedded in header
        hdr_id = re.search(r'(ECFG-P1[0-9]{3}|P1[0-9]{3})', title)
        hdr_rej = re.search(r'(?i)—\s*(REJECTED|DEMOTED)[^*]*$', raw_hdr)
        cands.append({
            'name': name or NS,
            'label': label or NS,
            'slug': slug or NS,
            'group': group,
            'source_file': str(path.relative_to(ROOT)),
            'assigned_ledger_id': hdr_id.group(1) if hdr_id else NS,
            'one_sentence_mechanism': mech,
            'tags': tags,
            'semantic_fingerprint_raw': fp_raw,
            'novelty_classification': novelty,
            'status_field': status,
            'likely_fatal_obstruction': fatal,
            'nearest_ledger_ids': ledger,
            '_header_line': raw_hdr,
            '_header_rej': hdr_rej.group(0).strip(' —') if hdr_rej else None,
        })
    # winners
    header_lines = [c.pop('_header_line') for c in cands]
    hdr_rejs = [c.pop('_header_rej') for c in cands]
    winner_scan(text, cands, header_lines)
    for i, c in enumerate(cands):
        if c['batch_disposition'] == NS and hdr_rejs[i]:
            c['batch_disposition'] = hdr_rejs[i]
    return cands

# ---------------------------------------------------------------- ideas registry
def parse_idea_file(path):
    text = path.read_text(errors='replace')
    lines = text.split('\n')
    m = re.match(r'^#\s+(ECDLP-IDEA-\d+)\s*[—-]\s*(.+?)\s*$', lines[0]) if lines else None
    idea_id, title = (m.group(1), m.group(2)) if m else (NS, NS)
    def field(fname):
        mm = re.search(r'^-\s*' + re.escape(fname) + r':\s*`?([^`]+?)`?\s*$', text, re.M)
        return mm.group(1).strip() if mm else NS
    hyp = flatten(get_section(lines, r'Falsifiable hypothesis'), 700)
    mechop = flatten(get_section(lines, r'Mechanism-new operation'), 500)
    fp = flatten(get_section(lines, r'Semantic fingerprint'), 500)
    ledger = parse_ledger_ids(get_section(lines, r'Five closest ledger entries',
                                          r'Closest ledger entries'))
    return {
        'name': title, 'label': idea_id, 'slug': idea_id,
        'group': 'ideas registry — class: ' + field('Class') + ' / risk: ' + field('Risk band'),
        'source_file': str(path.relative_to(ROOT)),
        'assigned_ledger_id': idea_id,
        'one_sentence_mechanism': hyp,
        'mechanism_new_operation': mechop,
        'tags': {k: NS for k in FP_KEYS},
        'semantic_fingerprint_raw': fp,
        'novelty_classification': field('Novelty'),
        'status_field': field('State'),
        'likely_fatal_obstruction': NS,
        'nearest_ledger_ids': ledger,
        'selected_winner': NS,
        'batch_disposition': NS,
    }

PLAN_EXP = {  # plan.md Stage-1 dispatch of research_directions_20260717 candidates
    'A1': 'EXP-JET-001', 'A2': 'EXP-INC-001', 'A3': 'EXP-STR-001',
    'B1': 'EXP-NET-001', 'B2': 'EXP-BKK-001', 'B3': 'EXP-EQJ-001',
    'C1': 'EXP-TRA-001', 'C2': 'EXP-TTN-001', 'C3': 'EXP-NCP-001',
    'D1': 'EXP-JETB-001', 'D2': 'EXP-BKKMV-001', 'D3': 'EXP-INCB-001',
}
# Official Coordinator decisions (ledger/DEC-20260718-001..012) on the 0717 dispatch
DEC_0717 = {
    'A1': ('reject_scoped', 'DEC-20260718-001', 'Survival sigma = 1.0000 exactly at all four sizes; epsilon-system implied by the zeroth-order solution set — named fatal obstruction triggered.'),
    'A2': ('reject_scoped', 'DEC-20260718-002', 'Zero output sensitivity measured: exponent 2.078 = Theta(B^2), zero pairs avoided; marginal cost candidate-proportional.'),
    'A3': ('reject_scoped', 'DEC-20260718-003', 'Displacement rank alpha grows linearly in B (alpha/B 0.56-0.77, at generic maximum, identical to random baseline) — no structure.'),
    'B1': ('reject_scoped', 'DEC-20260718-004', 'Collision statistics equal the random-oracle birthday model; enrichment 1.05-1.20 fully accounted by index-1 tautologies.'),
    'B2': ('reject_scoped', 'DEC-20260718-005', 'Newton saturation measured exactly: S_m support fills the full box at m=3,4,5; MV = Bezout box exactly (rho_m = 1).'),
    'B3': ('reject_scoped', 'DEC-20260718-006', 'Only 4 of 10 isotypic blocks nonzero (forced by S3-invariance); rank never splits across surviving blocks.'),
    'C1': ('reject_scoped', 'DEC-20260718-007', 'Localization L = O(1): growth exponent delta = 0.0195; L_eff median = 1.0 at all sizes; hits at chance.'),
    'C2': ('reject_scoped', 'DEC-20260718-008', 'Bond-rank growth gate NOT crossed: alpha = 1.161 (3-point) / 1.322 (root-only), identical at p = 101/431/1009.'),
    'C3': ('reject_scoped', 'DEC-20260718-009', 'Commutative quotient reproduces ALL found NC relations (0 violations; 94,472 shadow replays) — commutator collapse.'),
    'D1': ('supported_scoped', 'DEC-20260718-010', 'Toy certification lands on the barrier side at all three sizes: sigma_true = 1.0, leakage = 0 — jet-augmented generic-model barrier supported.'),
    'D2': ('supported_scoped', 'DEC-20260718-011', 'Exact 3-point-certified growth law MV_m = (m-1)! * 2^((m-1)(m-2)) for m=3,4,5 — mixed-volume certificate achieved (barrier side).'),
    'D3': ('supported_scoped', 'DEC-20260718-012', 'EC chord richness exponent statistically indistinguishable from random line sets — incidence-richness ceiling (barrier) supported.'),
}
RD0718_WINNERS = {'A1': 'conservative', 'B2': 'representation', 'C2': 'high_risk'}
RD0718_NOTES = {
    'A1': 'WINNER (conservative). EXP-MONO-001 phase-1 smoke executed 2026-07-18 (report §9.2): controls pass, toy relation rates match exact predictions inside Weil floors; substantive Chebotarev gate (m=3 census) is phase 2, not yet run.',
    'A2': 'Weakened by EXP-ISADV-001 phase-1 smoke (report §9.1): cross-curve advice transfer statistically indistinguishable from baseline at all three toy sizes — scoped negative on transfer.',
    'B2': 'WINNER (representation). EXP-XEDN-001 harness smoke executed (report §9.3): controls pass; xedni scarcity obstruction already visible at toy scale (0 sections in 5760 random slots), consistent with JKSST 2000; promotion gate not yet run.',
    'C1': 'Rejected as winner: stages 1,7 INCOMPLETE, no complete route to target descent; no rho comparison possible (report §5).',
    'C2': 'WINNER (high-risk). EXP-IMON-001 harness smoke executed (report §9.4): census separates full from non-full covers on controls; curve cover shows no deviation beyond Weil error at toy size; joint m=3 test is phase 2.',
    'C3': 'Rejected as winner: stages 4,7 INCOMPLETE; no rho comparison possible (report §5).',
}

def main():
    all_cands = []
    for f in BATCH_FILES + REPORT_FILES:
        cs = parse_batch_file(f)
        if f.name == 'research_directions_20260717.md':
            for c in cs:
                exp = PLAN_EXP.get(c['label'])
                dec = DEC_0717.get(c['label'])
                c['selected_winner'] = 'all 12 candidates dispatched (plan.md Stage 1)'
                c['batch_disposition'] = (f"Dispatched as {exp} per plan.md; Coordinator decision "
                                          f"{dec[0]} ({dec[1]}): {dec[2]}" if dec else NS)
        if f.name == 'research_directions_20260718.md':
            for c in cs:
                c['selected_winner'] = RD0718_WINNERS.get(c['label'], NS)
                note = RD0718_NOTES.get(c['label'])
                if note:
                    c['batch_disposition'] = note
        all_cands.extend(cs)
        print(f"{f.name}: {len(cs)} candidates", file=sys.stderr)
    # ideas registry
    n_idea = 0
    for sub in ['ideas', 'ideas/deferred', 'ideas/rejected']:
        for f in sorted(ROOT.glob(sub + '/ECDLP-IDEA-*.md')):
            all_cands.append(parse_idea_file(f))
            n_idea += 1
    print(f"ideas registry files: {n_idea}", file=sys.stderr)
    out = ROOT / 'outputs' / 'prior_proposals_index.json'
    out.write_text(json.dumps(all_cands, indent=1, ensure_ascii=False))
    print(f"TOTAL {len(all_cands)} -> {out}", file=sys.stderr)

if __name__ == '__main__':
    main()
