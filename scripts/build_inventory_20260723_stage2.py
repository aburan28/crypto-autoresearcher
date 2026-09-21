#!/usr/bin/env python3
"""Stage 2: compute fields and emit ledger_inventory_20260723.json."""
import json, re, os, pickle
from collections import defaultdict, Counter

IN = '/Volumes/Volume/crypto-autoresearcher/inputs'
OUT = '/Volumes/Volume/crypto-autoresearcher/outputs'
F_MAIN = 'research_ledger_main.md'
F_IC = 'research_ledger_ic_state.md'
F_TR = 'non_generic_transfer_search_20260610.md'
F_BIB = 'bibliography.json'
NS = 'not stated'

d = pickle.load(open('/tmp/build_stage1.pkl', 'rb'))
entries, order = d['entries'], d['order']

texts = {f: open(os.path.join(IN, f)).read() for f in (F_MAIN, F_IC, F_TR)}

# ---------------------------------------------------------------- id family
def id_family(idv, kind):
    if kind == 'bibliography':
        return 'BIBLIOGRAPHY'
    for p in ('ECFG-IDEA',):
        pass
    m = re.match(r'^(ECDLP-IDEA|TRANSFER|ECFG|ISO|SHA1|OFQ|NR|RT|RITT|ISOWALK|MODHECKE|AMORT|DRINFELD|ZILBERPINK|PADICHT|BAR|PO-transfer|PO|P)-?', idv)
    if m:
        f = m.group(1)
        return {'PO-transfer': 'PO-TRANSFER', 'PO': 'PO', 'P': 'P'}.get(f, f)
    return 'OTHER'

# ---------------------------------------------------------------- outcome parsing
def norm_status_token(status):
    s = (status or '').strip('` ').strip()
    if not s:
        return NS
    head = re.split(r'\s*/\s*', s)[0].strip()
    table = {
        'NEGATIVE RESULT': 'negative-result', 'HYPOTHESIS': 'hypothesis',
        'OBSERVATION': 'observation', 'RESTRICTED THEOREM': 'restricted-theorem',
        'OPEN': 'open', 'MIXED RESULT': 'mixed-result',
        'PARTIAL POSITIVE': 'partial-positive', 'POSITIVE SIGNAL': 'positive-signal',
        'COMPLETE': 'complete', 'PREREGISTERED THEOREM GATE': 'preregistered-gate',
    }
    out = table.get(head.upper())
    if out:
        quals = []
        for q in ('MODEL-BOUND', 'TOY-EVIDENCE', 'NOVELTY-UNVERIFIED', 'CUSTODY FAILURE',
                  'PRESERVED RETRACTION', 'FAMILY LEVEL', 'RETRACTION'):
            if q in s.upper():
                quals.append(q.lower())
        return out + ((' (' + ', '.join(quals) + ')') if quals else '')
    m = re.match(r'Status is ([A-Z0-9 `\-/]+)', s)
    if m:
        return m.group(1).strip().lower()[:120]
    return head.lower()[:120]

def cells_join(e):
    return ' | '.join(c for c in e['cells'][1:] if c)

# ---------------------------------------------------------------- keyword labels
KW = {
 'representation': [
   ('Evans functional graph (ECFG)', r'functional graph|ECFG|Evans'),
   ('Semaev summation polynomials', r'Semaev|summation polynomial'),
   ('correspondence', r'correspondence'),
   ('cover/Prym', r'Prym|\bcover'),
   ('Jacobian', r'Jacobian'),
   ('Kummer model', r'Kummer'),
   ('isogeny map', r'isogen'),
   ('orientation/ideal class', r'orientation|oriented ideal|ideal class'),
   ('pairing transcript', r'pairing|Tate|Weil pairing'),
   ('lattice', r'lattice|LLL|Gram'),
   ('Weil restriction', r'Weil restriction'),
   ('theta/Kummer constants', r'theta'),
   ('quadratic twist', r'quadratic twist|twist'),
   ('graph/DB join', r'\bjoin\b|worst-case-optimal|FD\b'),
   ('resultant/eliminant', r'resultant|eliminant'),
   ('Groebner basis', r'Groebner|Gr.bner'),
   ('trace quotient', r'trace[- ]quotient|ker\(Tr'),
   ('Kani diamond', r'Kani'),
   ('functional graph index', r'reverse index'),
 ],
 'exploited_structure': [
   ('Frobenius action', r'Frobenius'),
   ('endomorphism ring', r'endomorphism|End\('),
   ('negation/sign symmetry', r'negation|sign symmetry|\{k, -k\}|antipodal'),
   ('torsion structure', r'torsion'),
   ('kernel structure', r'kernel'),
   ('isotropic subgroup', r'isotropic'),
   ('automorphism', r'automorphism'),
   ('CM/order structure', r'\bCM\b|conductor|quadratic order'),
   ('deck group', r'\bdeck\b'),
   ('gluing graph', r'gluing'),
   ('norm equation', r'\bnorm\b|Norm\('),
   ('trace identities', r'\btrace\b'),
   ('component/cycle graph shape', r'component size|depth|cycle|tail'),
   ('matched random controls', r'matched (random |symmetric )?control'),
   ('Hermitian/polarization form', r'Hermitian|polarization|Rosati'),
   ('two-torsion/marking', r'two-torsion|2-torsion|marking'),
   ('Riemann-Roch', r'Riemann'),
 ],
 'factor_base': [
   ('factor base mentioned', r'factor[ -]base'),
   ('x-coordinate factor base', r'factor base.{0,40}x-coord|x-coord.{0,40}factor base'),
   ('signed-point factor base', r'signed.{0,20}(factor base|label|point)'),
   ('elliptic-quotient factor base', r'elliptic-quotient factor base'),
   ('public-factor/quadratic-root surface', r'public.factor|quadratic.root'),
   ('large-prime variants', r'large.prime'),
 ],
 'relation_shape': [
   ('pair/2-sum', r'\bpairs?\b|2-sum|two-sum|\bbinary\b'),
   ('3-sum', r'3-sum|S3|three-sum|ternary'),
   ('m>=4 summation', r'5-term|five-term|S5|4-sum|m-ary|arity'),
   ('principal-divisor relation', r'principal divisor'),
   ('incidence relation', r'incidence'),
   ('cofiber relation', r'cofiber'),
 ],
 'relation_generation': [
   ('membership predicate', r'membership'),
   ('interpolation', r'interpolat'),
   ('resultant/gcd', r'resultant|\bgcd\b'),
   ('Groebner solve', r'Groebner|Gr.bner'),
   ('enumeration/census', r'census|enumerat'),
   ('streaming', r'streaming'),
   ('collector/scout probe', r'collector|scout|probe'),
   ('selector/scheduler routing', r'selector|scheduler|routing|guard'),
 ],
 'compression': [
   ('batch/amortization', r'batch|amortiz'),
   ('shared/reuse', r'shared|reuse'),
   ('cache', r'cache'),
   ('dedup/duplicate collapse', r'dedup|duplicate'),
   ('negation compression', r'negation.compress|half.scan'),
   ('compressed depth', r'compress'),
 ],
 'linear_algebra_object': [
   ('sparse matrix', r'sparse'),
   ('rank/nullity', r'\brank\b|nullity|nullity'),
   ('kernel/nullspace', r'kernel|null'),
   ('Wagner/k-tree', r'Wagner|k-tree'),
   ('Krylov/Lanczos', r'Krylov|Lanczos'),
   ('matrix solve', r'matrix|linear algebra'),
   ('Berlekamp-Massey', r'Berlekamp|BM\b'),
 ],
 'target_descent': [
   ('descent mentioned', r'descent'),
   ('scalar-blind/blind descent', r'blind'),
   ('individual log', r'individual.{0,10}(log|descent)|target descent'),
   ('target recovery', r'target recovery|recover.{0,20}target'),
 ],
 'cost_bottleneck': [
   ('rho comparison', r'\brho\b|Pollard'),
   ('memory', r'memory|RSS|storage'),
   ('setup/preprocessing', r'setup|preprocessing|precomputation'),
   ('relation collection cost', r'relation collection|relation yield|relation generation cost'),
   ('linear algebra cost', r'linear.algebra|matvec|sparse solve'),
   ('map construction cost', r'map cost|construction cost|map normalization'),
   ('descent cost', r'descent cost'),
   ('charged operation ledger', r'charged|operation-ledger'),
   ('exponent boundary', r'exponent'),
   ('torsion-field degree', r'torsion.field'),
   ('elimination degree', r'degree'),
 ],
}

def classify(field, text):
    if field == 'representation':
        keys = KW['representation']
    elif field == 'exploited_structure':
        keys = KW['exploited_structure']
    elif field == 'factor_base':
        keys = KW['factor_base']
    elif field == 'relation_shape':
        keys = KW['relation_shape']
    elif field == 'relation_generation':
        keys = KW['relation_generation']
    elif field == 'compression':
        keys = KW['compression']
    elif field == 'linear_algebra_object':
        keys = KW['linear_algebra_object']
    elif field == 'target_descent':
        keys = KW['target_descent']
    elif field == 'cost_bottleneck':
        keys = KW['cost_bottleneck']
    else:
        return NS
    hits = [lab for lab, rx in keys if re.search(rx, text, re.I)]
    # drop generic when a more specific sibling hit exists
    if 'factor base mentioned' in hits and len(hits) > 1 and field == 'factor_base':
        hits.remove('factor base mentioned')
    if 'descent mentioned' in hits and len(hits) > 1 and field == 'target_descent':
        hits.remove('descent mentioned')
    return '; '.join(hits[:4]) if hits else NS

# ---------------------------------------------------------------- entry type
def entry_type(e):
    k, sec = e['kind'], e.get('section') or ''
    if k == 'question':
        return 'open-frontier question'
    if k == 'proposed':
        return 'proposed idea (unscheduled)'
    if k == 'referenced':
        return 'referenced idea contract'
    if k == 'transfer-search':
        return 'transfer-search experiment campaign'
    if k == 'bibliography':
        return 'literature reference'
    if k == 'carried':
        return (e.get('prior') or {}).get('status_cell') and 'ledger entry (carried)' or 'ledger entry (carried)'
    s = sec.lower()
    if 'hypothes' in s:
        return 'hypothesis'
    if 'negative' in s:
        return 'negative result'
    if 'positive' in s or 'frontier' in s:
        return 'positive signal / observation'
    if 'baseline' in s:
        return 'baseline/experiment record'
    if re.match(r'20\d\d-', sec):
        return 'dated-section experiment record'
    return 'ledger entry'

# ---------------------------------------------------------------- outcome
def outcome(e):
    k = e['kind']
    idv = e['id']
    if k == 'question':
        if e.get('orphan'):
            return 'superseded (question replaced in the 2026-07-20..23 ledger update)'
        return 'answered/closed (checked)' if e.get('checked') else 'open'
    if k in ('proposed', 'referenced'):
        return NS
    if k == 'bibliography':
        return NS
    text_all = cells_join(e).upper()
    quals = [q.lower() for q in ('MODEL-BOUND', 'TOY-EVIDENCE', 'CUSTODY FAILURE', 'PRESERVED RETRACTION', 'NOVELTY-UNVERIFIED') if q in text_all]
    # ledger naming convention: -NR- / N-suffix series are negative-result records
    if '-NR-' in idv or idv.startswith('NR-') or re.search(r'-N\d+$', idv):
        return 'negative-result' + ((' (' + ', '.join(sorted(set(quals))) + ')') if quals else '')
    sec = (e.get('section') or '').lower()
    hdr = e.get('header') or []
    cells = e['cells']
    status_cell = ''
    if 'Status' in hdr:
        status_cell = cells[hdr.index('Status')] if len(cells) > hdr.index('Status') else ''
    if 'negative' in sec:
        base = 'negative-result'
        return base + ((' (' + ', '.join(sorted(set(quals))) + ')') if quals else '')
    if status_cell:
        return norm_status_token(status_cell)
    # dated sections put status inside scope cell in backticks
    for c in cells[1:]:
        m = re.match(r'^`([A-Z][A-Z0-9 /-]+)`', c.strip())
        if m and '/' in m.group(1):
            return norm_status_token(m.group(1))
    # last cell "Status is ..."
    if cells:
        m = re.search(r'Status is ([A-Z0-9 `\-/]+)', cells[-1])
        if m:
            return norm_status_token(m.group(1))
    # ledger naming-convention fallbacks
    if '-RT-' in idv:
        return 'restricted-theorem' + ((' (' + ', '.join(sorted(set(quals))) + ')') if quals else '')
    if '-MX-' in idv:
        return 'mixed-result'
    if '-OBS-' in idv:
        return 'observation'
    if '-POS-' in idv:
        return 'positive-signal'
    if 'positive' in sec:
        return 'positive-signal'
    return NS

# ---------------------------------------------------------------- next_branch
def next_branch(e):
    hdr = e.get('header') or []
    cells = e['cells']
    for name in ('Next action', 'Next validation', 'Reusable lesson'):
        if name in hdr and len(cells) > hdr.index(name):
            return cells[hdr.index(name)] or NS
    if e['kind'] == 'bibliography':
        return (e.get('bib') or {}).get('experiment_hook') or NS
    return NS

# ---------------------------------------------------------------- negative boundary
def negative_boundary(e):
    o = outcome(e)
    if not (o.startswith('negative-result') or 'negative' in o):
        return NS
    hdr = e.get('header') or []
    cells = e['cells']
    parts = []
    if 'Ruled out' in hdr and len(cells) > hdr.index('Ruled out'):
        parts.append('Ruled out: ' + cells[hdr.index('Ruled out')])
    if 'Reusable lesson' in hdr and len(cells) > hdr.index('Reusable lesson'):
        parts.append('Lesson/boundary: ' + cells[hdr.index('Reusable lesson')])
    if parts:
        return ' || '.join(parts)
    if 'Status' in hdr and len(cells) > hdr.index('Status'):
        return 'Declared boundary: ' + cells[hdr.index('Status')]
    for c in cells[1:]:
        m = re.match(r'^`([A-Z][A-Z0-9 /-]+)`', c.strip())
        if m and 'NEGATIVE' in m.group(1):
            return 'Declared boundary: ' + m.group(1)
    # NR-series rows filed outside negative-results tables: claim + evidence cell
    if len(cells) >= 3 and cells[1]:
        ev = cells[3] if len(cells) > 3 else ''
        b = 'Ruled out/finding: ' + cells[1]
        if ev:
            b += ' || Evidence: ' + ev[:400]
        return b
    return NS

# ---------------------------------------------------------------- mechanism
def mechanism(e):
    k = e['kind']
    if k == 'bibliography':
        b = e.get('bib') or {}
        au = ', '.join(b.get('authors') or [])
        return f"{b.get('title','')} ({au}, {b.get('year','?')}; {b.get('source','')})"
    if len(e['cells']) > 1 and e['cells'][1]:
        return e['cells'][1]
    return NS

# hand-authored factual fills for special entries (verbatim-derived from sources)
SPECIAL = {
 'ECDLP-IDEA-049': {'mechanism': "Idea contract whose claim (as stated in the IC ledger): complete prime-field elliptic addition has an operation-preserving integer lift whose hidden coordinates, slopes, and carries lie in a sub-modulus multivariate small-root region.",
                    'outcome': 'closed negative (P1507: slope/carry heights are modulus-scale; elimination returns S3)'},
 'ECDLP-IDEA-050': {'mechanism': "Idea contract whose review-required claim (as stated in the IC ledger): one public target-independent binary basis maps a complete elliptic factor-base relation tensor into the matchgate variety.",
                    'outcome': 'closed negative (P1504: all five complete elliptic tensors have zero matchgate bases)'},
 'ECDLP-IDEA-052': {'mechanism': "Idea contract whose claim (as stated in the IC ledger): a curve-specific source-labelled exterior identity can avoid the quadratic pair surface while preserving complete factor-base witnesses.",
                    'outcome': 'closed negative (P1506: source label state equals the pair surface; valid 3+1 sources lost)'},
 'ECDLP-IDEA-053': {'mechanism': "Idea contract whose claim (as stated in the IC ledger): aggregate endpoint moments from the accepted factored addition algebra can recover large-prime keys and exact source tags without endpoint materialization or per-key opening.",
                    'outcome': NS},
 'ECDLP-IDEA-056': {'mechanism': "Idea contract whose review-required claim (as stated in the IC ledger): block Krylov can expose a shared two-transition state and source lift without the dense quadratic resultant.",
                    'outcome': NS},
 'ECDLP-IDEA-058': {'mechanism': "Idea contract referenced in the IC ledger: exact curve-specific quadratic-phase decomposition with conditioned source marginals, to be tested on P1504's complete four-source Boolean tensor before rank scoring.",
                    'outcome': NS},
 'ECDLP-IDEA-059': {'mechanism': "Idea contract whose review-required claim (as stated in the IC ledger): a target-independent elliptic Cremona map can lower the saturated mixed volume of a source-complete Semaev factor-base system.",
                    'outcome': 'closed negative (P1503: natural summation-coordinate map nonbirational; group-addition map exact but source-complete volume invariant)'},
 'ECDLP-IDEA-068': {'mechanism': "Idea contract referenced in the IC ledger: source-coded Hasse-jet FFE reporter / constructive section on P1490 two-transition endpoints, feeding a shared bivariate common-norm identity (P1513 gate).",
                    'outcome': NS},
 'ECDLP-IDEA-115': {'mechanism': "Idea contract referenced in the IC ledger: exact source-biconditional scalar-linear Chow/Tate or determinant-of-cohomology atomizer for the signed five-source incidence (tested by P1512).",
                    'outcome': 'closed negative (P1512: atomizer needs full-cycle payload m >= ceil(binomial(2r+4,5)/3) = Omega(r^5))'},
 'ECDLP-IDEA-117': {'mechanism': "Idea contract referenced in the IC ledger: functional dependencies plus degree-aware worst-case-optimal joining to supply the missing sub-r^1.5 source query on the P1510 representation (tested by P1511).",
                    'outcome': 'closed negative (P1511 R1/R2: FD-width/join planning not reproduced; product-circuit input cubic; both branches closed)'},
 'PO-transfer-001': {'mechanism': "First horizontal slice of the non-generic transfer search: invariant m=3/S4 decomposition metrics and rank-deficient public relations on a flat-volcano toy class (per the transfer-search handoff).",
                     'negative_boundary': 'Rank-deficient public relations on the flat-volcano toy class (invariant m=3/S4 decomposition metrics).',
                     'outcome': 'negative-result / model-bound (rank-deficient public relations)',
                     'next_branch': "Replace raw divisor-list meet-in-the-middle with a structure-bearing native correspondence/Jacobian relation or a public prefilter that predicts target-coupled rank gain before materializing the full divisor table (handoff next action)."},
 'PO-transfer-002': {'mechanism': "Target-coupled correspondence relations that recovered the original toy target scalar, but at 178x to 317x rho with large meet-in-the-middle memory.",
                     'negative_boundary': 'Target coupling alone is baseline-lost: 178x to 317x rho with large meet-in-the-middle memory.',
                     'outcome': 'negative-result (baseline-lost: 178x-317x rho)',
                     'next_branch': "Replace raw divisor-list meet-in-the-middle with a structure-bearing native correspondence/Jacobian relation or a public prefilter (handoff next action)."},
 'PO-transfer-003': {'mechanism': "BNIT: native bielliptic relation source - split genus-2 cover C:y^2=x^6+A*x^2+B with principal divisors of y-v(x) pushed to the elliptic quotient E1; cubic interpolation through a target lift plus three factor-base lifts leaves a quadratic residual.",
                     'negative_boundary': 'Tested direct/large-prime/streaming/bounded-cache algorithms do not turn the native relation source into a rho improvement: charged optimistic floor 3375.96x rho, peak memory 3.90*sqrt(n), adverse four-cell fit n^1.687.',
                     'outcome': 'negative-result / positive mechanical signal / toy-evidence / model-bound (rank repaired by one-large-prime variant; all four cells recovered; charged floor 3375.96x rho; memory 3.90*sqrt(n))',
                     'next_branch': "PO-transfer-004: Plucker-pair batch incidence gate (built and closed out negative under the tested model)."},
 'PO-transfer-004': {'mechanism': "Plucker-pair batch incidence gate for the bielliptic relation source; determinant/wedge equivalence exact after shared-index and repeated-abscissa filters.",
                     'negative_boundary': 'Lane closed under tested model: charged work 8652.33..115587.62x rho on base cells; unimplemented oracle floor 132.67..451.81x; base memory 68.3..200.6 sqrt(n); charged/oracle-floor toy exponents 0.958 and 0.561.',
                     'outcome': 'negative-result (lane closed: charged work 8652.33..115587.62x rho; base memory 68.3..200.6 sqrt(n); not a negative for auxiliary-object transfer generally)',
                     'next_branch': "Build PO-transfer-005: lift the original target into the trace quotient E(F_{p^m})/ker(Tr_m) ~= E(F_p), m in {2,3}, and test extension-field factor base plus real algebraic decomposition against pushed-forward search."},
 'PO-transfer-005': {'mechanism': "Trace-quotient lift E(F_{p^m})/ker(Tr_m) ~= E(F_p), m in {2,3}, with extension-field factor base; trace-quotient audit proved kernel fibers multiply successes and trials equally.",
                     'negative_boundary': 'Restricted theorem: full kernel fibers multiply successes and trials equally; repeated images are duplicate base-group columns, so raw trace-fiber multiplicity is not a relation-probability or rank gain.',
                     'outcome': 'negative-result (restricted theorem: raw trace-fiber multiplicity is not a relation-probability or rank gain; only a solver-time loophole survives)',
                     'next_branch': "Pivot to PO-transfer-006 complementary labels; compare any surviving solver-time loophole against the older scalar Weil-restriction evidence (PO-004/NR-022) before execution."},
 'PO-transfer-006': {'mechanism': "Exact generic degree-3 maps of a (3,3)-split genus-2 curve; complementary quotient labels each E1 lift; complete phi2 fiber pushes to a constant-sum ternary relation on E1.",
                     'negative_boundary': 'All 114 complete cofibers push to O; production rows/rank/columns only 6/6/18, 34/34/78, 74/74/174; every two-core empty; matched EC-addition triples reproduce ranks exactly; no factor base reaches B-1 rank; floor 26.92x,56.16x,80.33x rho with adverse toy fit n^1.188.',
                     'outcome': 'negative-result / positive mechanical signal / toy-evidence / model-bound (all 114 cofibers push to O; no factor base reaches B-1 rank; floor 26.92x..80.33x rho, adverse fit n^1.188)',
                     'next_branch': "Write PO-transfer-007 around a cyclic cover X_d:z^d=h(P): target-couple a principal divisor of z-v, factor its norm, merge duplicate pushed E images, and compare norm smoothness/solver cost against the direct elliptic function-field relation; require measured label-conditioned factorization advantage, reusable rank, and blind descent."},
 'PO-transfer-007': {'mechanism': "Planned cyclic-cover transfer X_d:z^d=h(P): target-couple a principal divisor of z-v, factor its norm, merge duplicate pushed E images, and compare norm smoothness/solver cost against the same relation built directly in the elliptic function field.",
                     'outcome': 'planned (next concrete action in the transfer-search note)',
                     'next_branch': "Do not credit d preimages; require a measured label-conditioned factorization advantage, reusable rank, and blind descent."},
 'PO-004': {'mechanism': "Older scalar Weil-restriction evidence referenced by the transfer-search note (with NR-022) as the comparison baseline for the PO-transfer-005 loophole.",
            'outcome': NS},
 'NR-022': {'mechanism': "Older negative-result record referenced by the transfer-search note as scalar Weil-restriction evidence against the PO-transfer-005 loophole.",
            'outcome': NS},
 'AMORT-A3': {'mechanism': "Batch2 candidate A3 (many-target amortization crossover meter, offline/online separation): an explicit statement and meter that precomputation amortization is decisive only when paired with an online exponent c_on<1/2; falsification plugs measured c_on into C_off/T + q^{c_on} vs sqrt(n/T). Contract research/PO_batch2_A3_amortization_crossover_contract.md.",
              'outcome': 'proposed, not a batch2 winner; no experiment run recorded in the ledgers as of 2026-07-23'},
 'DRINFELD-B2': {'mechanism': "Batch2 candidate B2 (Drinfeld-module / function-field transport): search for a genuine representation change via an additive injection into a Drinfeld-module DLP; the batch2 note predicts it reduces to 'the only cross-category transports are pairings' (MOV landing in F_{p^k}*). Contract research/PO_batch2_B2_drinfeld_transport_contract.md.",
              'outcome': 'proposed, not a batch2 winner; no experiment run recorded in the ledgers as of 2026-07-23'},
 'PADICHT-C3': {'mechanism': "Batch2 candidate C3 (Coleman-Gross p-adic height-pairing relation lattice): apply LLL to Coleman-Gross height vectors as the new operation; the batch2 note's predicted obstruction is the Mordell-Weil rank bound (height-image dimension O(1), too small to separate the n group elements). Contract research/PO_batch2_C3_padic_height_lattice_contract.md.",
              'outcome': 'proposed, not a batch2 winner; no experiment run recorded in the ledgers as of 2026-07-23'},
 'BAR-TRANSPORT-D1': {'mechanism': "Batch2 candidate D1 (cross-category transport-injection barrier, negative theory): prove that a transport psi plus a subexponential DLP oracle in G would solve the DLP in <P>, bounding construction plus query. Theory note research/PO_batch2_D1_transport_injection_barrier_theory.md.",
              'outcome': 'proposed, not a batch2 winner; no experiment run recorded in the ledgers as of 2026-07-23'},
 'BAR-AMORT-D2': {'mechanism': "Batch2 candidate D2 (amortization / preprocessing lower bound, negative theory): show any advice of length S with online time T_on obeys S*T_on >= n (CGK-style), then combine with the multi-target rho bound. Theory note research/PO_batch2_D2_amortization_lower_bound_theory.md.",
              'outcome': 'proposed, not a batch2 winner; no experiment run recorded in the ledgers as of 2026-07-23'},
}

# ---------------------------------------------------------------- assemble
FIELDS = ['id', 'id_family', 'source_files', 'entry_type', 'mechanism', 'representation',
          'exploited_structure', 'factor_base', 'relation_shape', 'relation_generation',
          'compression', 'linear_algebra_object', 'target_descent', 'cost_bottleneck',
          'outcome', 'negative_boundary', 'next_branch']

out = []
for idv in order:
    e = entries[idv]
    text = cells_join(e)
    rec = {
        'id': idv,
        'id_family': id_family(idv, e['kind']),
        'source_files': e['sources'] if e['sources'] else ([s for s in (F_MAIN, F_IC, F_TR) if idv in texts[s]] or []),
        'entry_type': entry_type(e),
        'mechanism': mechanism(e),
        'representation': classify('representation', text),
        'exploited_structure': classify('exploited_structure', text),
        'factor_base': classify('factor_base', text),
        'relation_shape': classify('relation_shape', text),
        'relation_generation': classify('relation_generation', text),
        'compression': classify('compression', text),
        'linear_algebra_object': classify('linear_algebra_object', text),
        'target_descent': classify('target_descent', text),
        'cost_bottleneck': classify('cost_bottleneck', text),
        'outcome': outcome(e),
        'negative_boundary': negative_boundary(e),
        'next_branch': next_branch(e),
    }
    if idv in SPECIAL:
        for k2, v2 in SPECIAL[idv].items():
            if v2 != NS or rec[k2] == NS:
                rec[k2] = v2
    # boundary embedded in outcome for 'closed negative (Pxxxx: ...)' idea contracts
    if rec['negative_boundary'] == NS and rec['outcome'].lower().startswith('closed negative ('):
        rec['negative_boundary'] = rec['outcome'][len('closed negative ('):].rstrip(')').strip()
    if e['kind'] == 'question' and e.get('orphan'):
        rec['source_files'] = ['(prior-run ledger copy; question no longer present in fresh inputs)']
    out.append(rec)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'ledger_inventory_20260723.json'), 'w') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

print("wrote", len(out), "records")
print("by family:", Counter(r['id_family'] for r in out).most_common())
print("by type:", Counter(r['entry_type'] for r in out).most_common())
print("files with no source:", sum(1 for r in out if not r['source_files']))
# spot check a few
for r in out[:2]:
    print(json.dumps(r, indent=1)[:800])
