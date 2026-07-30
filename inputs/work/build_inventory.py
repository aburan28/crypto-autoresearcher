#!/usr/bin/env python3
"""Build ledger_inventory_20260724.json from fresh ledger copies."""
import json, re, sys
from collections import Counter, OrderedDict

IN = '/Volumes/Volume/crypto-autoresearcher/inputs'

# ---------------- parsing ----------------
def parse_rows(path, source_file):
    rows = []
    section = None
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            s = line.rstrip('\n')
            if s.startswith('## '):
                section = s[3:].strip()
            elif s.startswith('|'):
                cells = [c.strip() for c in s.split('|')][1:-1]
                if (cells and re.match(r'^[A-Z][A-Z0-9]*(-[A-Za-z0-9]+)*$', cells[0])
                        and re.search(r'\d', cells[0]) and cells[0] != 'ID'):
                    rows.append({'id': cells[0], 'cells': cells, 'section': section,
                                 'line': ln, 'source_file': source_file})
    return rows

STATUS_RE = re.compile(r'\b(NEGATIVE RESULT|HYPOTHESIS|OBSERVATION|RESTRICTED THEOREM|POSITIVE|SUPERSEDED|RETRACTION|MIXED RESULT|THEOREM|OPEN|CLAIM|SCOPED NEGATIVE|RED TEAM|TOY-EVIDENCE|MODEL-BOUND)\b', re.I)

def logical_cells(cells):
    """Return (claim, status, evidence, next_action) from raw cells, tolerating pipes in text."""
    claim = cells[1] if len(cells) > 1 else ''
    status = ''
    status_idx = None
    for i in range(2, min(len(cells), 6)):
        if STATUS_RE.search(cells[i]):
            status = cells[i]; status_idx = i; break
    next_action = cells[-1] if len(cells) >= 5 else ''
    if status_idx is not None and len(cells) >= 5:
        ev = ' '.join(cells[status_idx+1:-1]).strip()
    else:
        ev = ' '.join(cells[2:-1]).strip() if len(cells) > 3 else ''
    return claim, status, ev, next_action

# ---------------- keyword extractor ----------------
KW = {
 'representation': [
   ('weil restriction','weil-restriction'), ('kummer line','kummer-line'), ('kummer','kummer'),
   ('theta','theta'), ('jacobian','jacobian'), ('prym','prym'), ('genus-two','genus-2'),
   ('genus-2','genus-2'), ('genus-three','genus-3'), ('genus-3','genus-3'), ('genus-four','genus-4'),
   ('genus-4','genus-4'), ('hyperelliptic','hyperelliptic'), ('plane','plane-model'),
   ('function field','function-field'), ('function-field','function-field'), ('x-line','x-line'),
   ('x-only','x-only'), ('montgomery','montgomery'), ('hesse','hesse'), ('graph','graph/ecfg'),
   ('ecfg','graph/ecfg'), ('summation polynomial','summation-polynomial'), ('semaev','semaev'),
   ('lattice','lattice'), ('incidence','incidence'), ('torsor','torsor'), ('divisor','divisor'),
   ('cover','cover'), ('surface','surface'), ('abelian','abelian-variety'), ('supersingular','supersingular'),
   ('ordinary','ordinary'), ('quadratic twist','quadratic-twist'), ('twist','twist'),
   ('extension field','extension-field'), ('finite field','finite-field'), ('hermitian','hermitian'),
   ('quartic','quartic'), ('cubic','cubic'), ('conic','conic'), ('module','module'),
   ('isogeny graph','isogeny-graph'), ('volcano','volcano'), ('ideal','ideal-class'),
   ('quadratic order','quadratic-order'), ('binary quadratic','binary-quadratic-form')],
 'exploited_structure': [
   ('isogeny','isogeny'), ('endomorphism','endomorphism'), ('cm ','cm'), ('cm)','cm'), ('cm,','cm'),
   ('frobenius','frobenius'), ('trace','trace'), ('norm','norm'), ('torsion','torsion'),
   ('kernel','kernel'), ('automorphism','automorphism'), ('involution','involution'), ('deck','deck-group'),
   ('gluing','gluing'), ('polarization','polarization'), ('rosati','rosati'), ('prym','prym'),
   ('pairing','pairing'), ('weil pairing','weil-pairing'), ('tate','tate-pairing'), ('bockstein','bockstein'),
   ('orientation','orientation'), ('oriented','orientation'), ('volcano','volcano'), ('crater','crater'),
   ('cycle','cycle'), ('component','graph-component'), ('spectral','spectral'), ('large prime','large-prime'),
   ('large-prime','large-prime'), ('smooth','smoothness'), ('subgroup','subgroup'), ('coset','coset'),
   ('orbit','orbit'), ('symmetr','symmetry'), ('sign','sign-structure'), ('self-pairing','self-pairing'),
   ('ramanujan','ramanujan'), ('expander','expander'), ('ramif','ramification'), ('branch','branch-point'),
   ('galois','galois'), ('isotypic','isotypic'), ('idempotent','idempotent'), ('projector','projector'),
   ('isogeny class','isogeny-class'), ('class group','class-group'), ('unit','unit'), ('character','character'),
   ('bockstein','bockstein'), ('divided','divided-orientation'), ('sigma','sigma-invariant')],
 'factor_base': [
   ('factor base','factor-base'), ('factor-base','factor-base'), ('large prime','large-prime'),
   ('large-prime','large-prime'), ('one-large-prime','one-large-prime'), ('two-large-prime','two-large-prime'),
   ('three-large-prime','three-large-prime'), ('degree-one','degree-1'), ('degree-1','degree-1'),
   ('rational-map','rational-map'), ('product','product-factor-base'), ('summation','summation'),
   ('split','split-factor-base'), ('signed','signed-factor-base'), ('orbit','orbit-factor-base'),
   ('interval','interval-factor-base'), ('column','column-factor-base'), ('packet','packet')],
 'relation_shape': [
   ('summation','summation'), ('3-sum','3-sum'), ('three-sum','3-sum'), ('4-sum','4-sum'),
   ('five-term','5-term'), ('5-term','5-term'), ('six-term','6-term'), ('m-term','m-term'),
   ('incidence','incidence'), ('cycle','cycle'), ('cofiber','cofiber'), ('co fiber','cofiber'),
   ('ternary','ternary'), ('principal divisor','principal-divisor'), ('principal-divisor','principal-divisor'),
   ('zero-sum','zero-sum'), ('zero sum','zero-sum'), ('pair','pair-relation'), ('row','row-relation'),
   ('four-term','4-term'), ('two-term','2-term'), ('diamond','kani-diamond'), ('kani','kani-diamond')],
 'relation_generation': [
   ('direct-source','direct-source'), ('direct source','direct-source'), ('collector','collector'),
   ('scout','scout'), ('sieve','sieve'), ('grobner','grobner'), ('gröbner','grobner'),
   ('resultant','resultant'), ('eliminant','eliminant'), ('elimination','elimination'), ('sat ','sat'),
   ('membership','membership'), ('interpolation','interpolation'), ('streaming','streaming'),
   ('enumeration','enumeration'), ('census','census'), ('scan','scan'), ('backtest','backtest'),
   ('holdout','holdout-validation'), ('generator','source-generator'), ('selector','selector'),
   ('prefilter','prefilter'), ('preflight','preflight'), ('harvest','harvesting'), ('replay','replay'),
   ('verifier','verification'), ('mutation','mutation-control'), ('red team','red-team')],
 'compression': [
   ('large prime','large-prime-filtering'), ('large-prime','large-prime-filtering'), ('peeling','peeling'),
   ('krylov','krylov'), ('structured gaussian','structured-gaussian'), ('compression','compression'),
   ('trim','trim'), ('bucket','bucketing'), ('compaction','compaction'), ('packing','packing'),
   ('sparsif','sparsification'), ('dense','dense-output'), ('compact','compact-representation'),
   ('slp','straight-line-program'), ('straight-line','straight-line-program')],
 'linear_algebra_object': [
   ('matrix','matrix'), ('rank','rank'), ('nullity','nullity'), ('sparse','sparse-matrix'),
   ('krylov','krylov'), ('wiedemann','wiedemann'), ('lanczos','lanczos'), ('echelon','echelon'),
   ('smith','smith-normal-form'), ('kernel','kernel-space'), ('nullspace','nullspace'),
   ('rowspace','rowspace'), ('gram','gram-matrix'), ('hermitian','hermitian-form'),
   ('inner product','inner-product'), ('lattice','lattice-reduction'), ('lll','lll'),
   ('smith type','smith-type'), ('isotropic','isotropic-subspace')],
 'target_descent': [
   ('descent','descent'), ('individual log','individual-log'), ('individual-log','individual-log'),
   ('blind','blind-descent'), ('target','target-descent'), ('mitm','mitm'), ('meet-in-the-middle','mitm'),
   ('bsgs','bsgs'), ('rho','rho-comparison'), ('pollard','pollard-rho'), ('recovery','key-recovery'),
   ('logarithm','log-recovery'), ('return map','return-map'), ('lift','lift'), ('transport','transport')],
 'cost_bottleneck': [
   ('memory','memory'), ('wall-clock','wall-clock'), ('wall clock','wall-clock'), ('field operation','field-operations'),
   ('torsion-field','torsion-field-degree'), ('torsion field','torsion-field-degree'), ('degree','degree-growth'),
   ('dense','dense-output-size'), ('matrix','matrix-size'), ('rho','rho-ratio'), ('preprocessing','preprocessing-cost'),
   ('setup','setup-cost'), ('storage','storage'), ('gb','memory-gb'), ('timeout','timeout'),
   ('timed out','timeout'), ('exponential','exponential-cost'), ('floor','optimistic-floor'),
   ('oracle','oracle-dependence'), ('uncharged','uncharged-cost'), ('advice','advice-size'),
   ('candidate','candidate-enumeration'), ('search','search-space')],
}

def extract_tags(field, text):
    tl = text.lower()
    tags = []
    for pat, tag in KW[field]:
        if pat in tl and tag not in tags:
            tags.append(tag)
    return ';'.join(tags) if tags else None

def outcome_of(section, status, full):
    s = (status or '').upper()
    toks = []
    for t in ['NEGATIVE RESULT','SCOPED NEGATIVE','SUPERSEDED','RETRACTION','HYPOTHESIS','OBSERVATION',
              'RESTRICTED THEOREM','POSITIVE','MIXED RESULT','THEOREM','TOY-EVIDENCE','MODEL-BOUND',
              'NOVELTY-UNVERIFIED','OPEN','CUSTODY']:
        if t in s:
            toks.append(t.lower().replace(' ','-'))
    sec = (section or '').lower()
    base = None
    if 'negative' in sec: base = 'negative-result'
    elif 'positive' in sec: base = 'positive-signal'
    elif 'active hyp' in sec: base = 'active-hypothesis'
    elif 'frontier' in sec: base = 'open-question'
    if not toks and base: toks.append(base)
    elif base and base not in toks: toks.append(base)
    return ';'.join(dict.fromkeys(toks)) if toks else None

def gist(text, n=220):
    t = re.sub(r'\s+', ' ', (text or '')).strip()
    return t[:n] + ('...' if len(t) > n else '') if t else None

def neg_boundary(claim, evidence, full):
    tl = full.lower()
    m = re.search(r'(scoped negative[^.]*\.)', tl)
    parts = []
    if m: parts.append(m.group(1))
    # capture quantitative fragments
    quants = re.findall(r'(`?\d[\d.,]*\s*(?:x|×)\s*(?:the\s*)?(?:11\*)?rho`?)', tl)
    quants += re.findall(r'(q\^[\(\)\d./a-z]+)', tl)
    quants += re.findall(r'(2\^[\d.]+)', tl)
    quants += re.findall(r'(rank[s]?\s+[\d/,.\-\> ]+)', tl)
    quants += re.findall(r'(multiplicity (?:is )?zero)', tl)
    quants += re.findall(r'(\d+/\d+ (?:blind )?(?:targets|descents|recoveries|mutations|checks))', tl)
    if quants: parts.append('quant: ' + '; '.join(dict.fromkeys(quants))[:200])
    if not parts:
        parts.append(gist(claim, 180) or '')
    return ' | '.join(parts)[:400] if parts else None

def mechanism_of(claim, full):
    tags = []
    tl = full.lower()
    mech_terms = [
      ('self-pairing','self-pairing'), ('kani','kani-diamond'), ('transfer','transfer'),
      ('index calculus','index-calculus'), ('index-calculus','index-calculus'),
      ('factor base','factor-base-construction'), ('selector','selector'), ('source','source-generation'),
      ('prym','prym-construction'), ('jacobian','jacobian-transfer'), ('isogeny walk','isogeny-walk'),
      ('isogeny','isogeny-method'), ('pairing','pairing-leakage'), ('orientation','orientation-recovery'),
      ('kummer','kummer-reduction'), ('theta','theta-model'), ('weil descent','weil-descent'),
      ('weil restriction','weil-restriction'), ('cover','cover-attack'), ('decomposition','decomposition'),
      ('graph','graph-method'), ('ecfg','ecfg-graph'), ('collision','collision-search'),
      ('summation','summation-relation'), ('semaev','semaev-relation'), ('descent','descent'),
      ('preprocessing','preprocessing'), ('amortiz','amortization'), ('batch','batching'),
      ('interpolation','interpolation'), ('lattice','lattice-method'), ('gluing','gluing'),
      ('novelty','novelty-audit'), ('custody','custody-audit'), ('audit','audit'),
      ('benchmark','benchmark'), ('retraction','retraction')]
    for pat, tag in mech_terms:
        if pat in tl and tag not in tags:
            tags.append(tag)
    g = gist(claim, 160)
    return (((';'.join(tags[:6])) + ' | ') if tags else '') + (g or '')

def family_of(i):
    parts = i.split('-')
    head = []
    for p in parts:
        if re.search(r'\d', p): break
        head.append(p)
    return '-'.join(head) if head else re.match(r'^[A-Z]+', i).group(0)


# ---------------- hand-authored overrides for new/changed entries (2026-07-24) ----------------
# fields: mechanism, outcome, negative_boundary, next_branch (others auto-extracted)
OV = {
# --- Active hypotheses additions ---
'ISO-BP-001': dict(
  mechanism='balanced-primary sign-free Kummer rows: pairwise-coprime primary generator images identify a degree-d isogeny up to global sign when beta=min_S(N_S+N_compl)>4d; strictly extends additive x-orbit interpolation; ramified self-pairing acquisition realizes the strict region at degrees 13 and 17',
  outcome='restricted-theorem;positive-toy-evidence;model-bound;novelty-unverified;active-hypothesis',
  negative_boundary=None,
  next_branch='Same-instance fully charged comparison vs additive curve-identity, BMSS-style normalized reconstruction, GGR/Kani/theta with torsion fields, DLP/root search, memory, explicit-output costs'),
'TRANSFER-H036': dict(
  mechanism='corresponding-object transfer: prospectively frozen family must contain a primitive factor carrying the original ECDLP Weil factor OUTSIDE the saturated visible correspondence algebra, with explicit saturated transfer maps both ways and complete sub-rho decomposition',
  outcome='hypothesis;family-level;current-frozen-family-miss;toy-first;model-bound;algorithm-false',
  negative_boundary='R19 frozen 8-record F5F10 family: all 16 normalized interaction factors have target multiplicity zero; F5F7 projector passed; F5F8 exceptional dim-4 target zero; comparator 14/14, mutations 15/15; strict custody & distinct backend false',
  next_branch='Freeze a semantically distinct corresponding-object family with prospective target-positive off-visible-factor gate; then saturated maps + fully charged blind descent below rho at three increasing sizes'),
'TRANSFER-H037': dict(
  mechanism='geometrically indecomposable (1,2)-polarization on fixed E^2 with hidden degree-3 elliptic classes, materialized as explicit genus-3 curve whose Jacobian exposes a non-generic transfer/decomposition channel',
  outcome='mixed-result;exact-jacobian-channel-positive;factor-through-certified;toy-first;model-bound;novelty-unverified;algorithm-false',
  negative_boundary='K1P9A-R1: expected first relation 577/121=4.768595, mean rank-11 position 150.916 (random-matched); K1P10B/C/D/E negatives on Weierstrass/pole routes; no factor base logs, descent, or two-coordinate target rank',
  next_branch='Route only to H038: derive and independently verify a low-degree Weierstrass model plus rational forward/inverse maps before any quotient packet is admitted'),
'TRANSFER-H038': dict(
  mechanism='degree-nine kernel descent + inversion quotient exposes explicit coordinates on elliptic complement D; mixed divisor packets cancel both auxiliary elliptic coordinates while retaining nonzero order-q target boundary for sub-rho factor-base-to-target descent',
  outcome='k1p10f-r1-producer-positive;audit-repair-required;dependency-bound;toy;model-bound;algorithm-false',
  negative_boundary='K1P10F-R1 matrix-trace control is a similarity tautology (not an independent algebraic trace); arithmetic normal-closure order uncomputed; factor base/relations/logs/descent/family/cost gates all false',
  next_branch='Freeze K1P10F-R2: 9-dim algebraic F(D_tilde)/F(D) multiplication representation, per-fiber rank custody, fail-closed exceptions; then divisor push/pull, mixed packets, factor base <= q^(31/64), total cost < 0.886*sqrt(q) at three increasing sizes'),
# --- Negative results additions ---
'TRANSFER-NR-K1P9A': dict(
  mechanism='multiplicity-three signed labels from rational inversion orbits of the enumerable H018 section as nonrandom elliptic-quotient factor base',
  outcome='negative-result;random-matched;toy;model-bound',
  negative_boundary='12 signed rows rank 11 over 109-point sumset; expected streamed first relation 577/121=4.768595; mean rank-11 position 150.916; matches 256+4096-sample random controls; no parent inverse, factor logs, descent, or two-coordinate A-target rank',
  next_branch='Preserve streaming as open cost optimization; H038 must descend the order-nine kernel first and retain both target coordinates'),
'TRANSFER-NR-K1P10B': dict(
  mechanism='generic singular-plane adjunction + Brill-Noether preprocessing to convert 118-term K1P10A presentation to low-pole genus-one data',
  outcome='negative-result;bounded-adjunction-route-negative-or-incomplete;toy;model-bound',
  negative_boundary='Positive control (singular quartic) returns genus 1 in cap; H018 bidegree-(9,11) equation emits no genus/place marker before 20-minute cap; infrastructure-bound, not impossibility',
  next_branch='Replace generic adjunction with specialized low-pole search exploiting the known degree-nine embedding'),
'TRANSFER-NR-K1P10C': dict(
  mechanism='common-pole ansatz: R3 generators hypothesized to have pole divisors 11F and 9F for one common effective degree-nine fiber',
  outcome='negative-result;scoped-negative;pre-schedule;toy;model-bound',
  negative_boundary='Exact pole degrees 99/81 but X11 coefficients = one 1 + eight 2s, X9 = one 1 + ten 2s; shared degree-1 infinite pole has multiplicity 1 for both, disproving divisibility by 11 and 9; finite supports differ',
  next_branch='K1P10D must materialize a quotient fiber as common zero divisor with genuine cover-space Riemann-Roch intersections; do not revive total-degree inference'),
'TRANSFER-NR-K1P10D': dict(
  mechanism='uncentered denominators from monoid generated by X11,X9 to expose nonconstant functions in L(nF) above fixed quotient value (99,88)',
  outcome='negative-result;scoped-negative;toy;model-bound',
  negative_boundary='Fiber F reduced with support degrees 1,2,6, centered valuations 1; X11,X9 are units on F so any admitted ratio is pole-free on F; L(nF) + projectivity forces constant; R5 accumulated ranks 1/1 (byte-identical replay)',
  next_branch='A viable representation must vanish on F or synthesize principal parts through an exact projector; do not enlarge uncentered exponent rectangles'),
'TRANSFER-NR-K1P10E': dict(
  mechanism='centering the two quotient generators at (99,88) to recover quotient low-pole spaces on unchanged 56x30 rational-function schedule',
  outcome='negative-result;scoped-negative;toy;model-bound',
  negative_boundary='Control recovers ranks 2/3 with exact order-87 model; H018: all 30 denominators have intersection dimensions 1/1, accumulated ranks remain 1/1, no model admitted (byte-identical replay)',
  next_branch='Close frozen centered rectangles; use ambient principal parts plus normalized relative trace rather than tuning monomial bounds'),
'ISO-BP-NR-001': dict(
  mechanism='test whether sign-free generator images determine a degree-d map without the quantitative beta>4d product-partition condition (necessity), and whether two raw KCD residuals always have linear gcd',
  outcome='negative-result;counterexample-below-threshold;model-bound',
  negative_boundary='Over F_157, degree-34 maps 3+5i and 3-5i are not global signs yet agree in x on exact-order 3 and 5 points with beta=8<=136=4d; degree-11 KCD fixture has quadratic two-row gcd whose extra root is not a finite subgroup',
  next_branch='Keep beta>4d as sufficient, not universal; KCD must preserve algebraic branches and accept only after subgroup/endpoint/map verification'),
'TRANSFER-NR-093': dict(
  mechanism='primitive interaction factor of frozen F5F0 normalized six-sheet incidence cover as carrier of target trace-(-1) Weil factor for off-visible transfer',
  outcome='negative-result;scoped-negative;exact-smooth-function-fields;toy;model-bound',
  negative_boundary='A_int ~ A_F x A_G; L_AF=1-8T+154T^2-803T^3+15554T^4-81608T^5+1030301T^6 and L_AG=1-12T+78T^2-319T^3+7878T^4-122412T^5+1030301T^6 irreducible, each gcd 1 with target 1+T+101T^2 → target multiplicity zero; checks 16/16,17/17,27/27,28/28',
  next_branch='Close target transfer for frozen smooth function-field fixture only; F5F4 must vary the family prospectively and require explicit saturated maps before relation promotion'),
'TRANSFER-NR-096': dict(
  mechanism='frozen target elliptic factor occurrence test inside the exceptional abelian fourfold interaction projector',
  outcome='negative-result;scoped-negative;exact-two-route-counts;toy;model-bound',
  negative_boundary='P_int splits into two dimension-two involution factors; L_target=1+11T+101T^2 has exact multiplicity zero (scoped to (101,100,63,113) and the frozen projector)',
  next_branch='Keep all map/factor-base/relation/descent/cost gates closed; screen the other eight correspondences rather than generalizing the miss'),
'TRANSFER-NR-097': dict(
  mechanism='R3/R4-vs-R6 count agreement test: do ordinary/inverse-slope low-genus presentations certify normalized projective counts',
  outcome='negative-result;reclassified-presentations;local-corrections-preserved;toy;model-bound',
  negative_boundary='R3/R4 exceed normalized BF/BG degree-three counts by 3; F collision raw/normalized 1/0, disjoint G collision 3/2; applying -3 to each parent reproduces R6 factor pair; global exhaustiveness rejected by red team',
  next_branch='Reclassify R3/R4 as independent presentations of shared raw point semantics; audit projective conductor support and common-mode corrections before calling it a global repair'),
'TRANSFER-NR-098': dict(
  mechanism='global Sage function-field route as practical independent normalized-zeta verifier for the one-record repair',
  outcome='negative-result;verifier-cost-negative;infrastructure-bound',
  negative_boundary='R7 stalled in global/infinite maximal-order work; R8 stalled on global simple D6 integral basis; R11 reached exact genera 2,6,6 but consumed ~6.55 GB RSS and was interrupted during degree-three BF place work',
  next_branch='Use conductor/local-support computation or a second backend rather than another unbounded global zeta run; keep interrupted attempts'),
'TRANSFER-NR-099': dict(
  mechanism='frozen nonexceptional F5F10 split genus-two residual-cover family screened for a target-positive primitive interaction factor after exact normalization',
  outcome='negative-result;scoped-family-negative;exact-weil;toy;model-bound',
  negative_boundary='All 16 normalized dimension-three factors across 8 records (p=101,163) have exact target multiplicity zero; forward/reverse agree; target injection increments multiplicity exactly once (control)',
  next_branch='Change the corresponding object or correspondence family before map/factor-base/relation/descent work; representation-only variants do not answer the hard goal'),
# --- Positive signals additions ---
'TRANSFER-P-K1P8': dict(
  mechanism='H018 level-separated non-generic Jacobian decomposition J(C)~E3 x E6 x D with elliptic cover degrees (6,3,2) and reversible two-coordinate order-109 transfer through corrected H#',
  outcome='positive-signal;abstract-theorem-scope;toy;model-bound',
  negative_boundary=None,
  next_branch='H038 must compute F(C)=F(C_tilde)^K and the actual C->D map, then test only packets retaining both target and auxiliary coordinates under full rho accounting'),
'TRANSFER-P-K1P10': dict(
  mechanism='K1P10A+R3 materialization of the actual degree-nine kernel-invariant elliptic quotient field inside F(D_tilde) via two explicit forward coordinates',
  outcome='positive-signal;exact-field-materialization;toy;model-bound',
  negative_boundary=None,
  next_branch='K1P10D must certify the fixed (99,88) degree-nine quotient fiber and use exact cover-space Riemann-Roch intersections to derive/verify maps both directions before mixed packets'),
'TRANSFER-P-K1P10F': dict(
  mechanism='reconstruction of order-119 quotient model and maps with named fiber certified as exact pullback of recovered point at infinity',
  outcome='positive-signal;producer-positive;independent-trace-control-audit-repair-required;toy;model-bound',
  negative_boundary='Independent audit: 2581 replayed matrix traces are tautological under E^-1 diag(f_i) E (do not identify algebraic trace); arithmetic normal-closure order uncomputed',
  next_branch='Run only K1P10F-R2: explicit algebraic field multiplication trace, qualified scalar-extension scope, per-fiber rank custody, exact fail-closed exceptions'),
'ISO-BP-P001': dict(
  mechanism='balanced complementary-product criterion succeeds where additive sign-oblivious interpolation provably fails; arbitrary-target kernel/scale decoder constructs the unique toy map',
  outcome='positive-signal;toy-evidence;model-bound',
  negative_boundary=None,
  next_branch='Replace supplied rows by independently computed ramified self-pairing rows; run exact GGR/Kani comparator with extension-field and output costs charged'),
}
OV.update({
'TRANSFER-P094': dict(
  mechanism='frozen three-field Shaska family census: twenty exact bounded degree-four complements (map psi=(N/A, yM/A^2)) incl. nine non-anomalous candidates for primitive interaction-factor search',
  outcome='positive-signal;exact-census;independently-replayed;toy;model-bound',
  negative_boundary=None,
  next_branch='Run F5F5 R1 geometry preflight on all nine non-anomalous paths; map existence is not transfer evidence — require verified primitive target factor + saturated off-visible maps first'),
'TRANSFER-P095': dict(
  mechanism='one F5F4 non-anomalous path: exact toy completed-local certificate for genus-12 normalized residual compositum via two shared tame infinity branch places',
  outcome='positive-signal;exact-geometry;later-scoped-target-miss(F5F8);toy;model-bound',
  negative_boundary='F5F8 later finds target multiplicity zero in this exceptional projector',
  next_branch='Preserve as the 2+2 control for F5F10, not as a broader transfer obstruction'),
'TRANSFER-P096': dict(
  mechanism='exceptional normalized compositum carries genuine abelian fourfold interaction projector: pull-push A^2=3A, B^2=2B, AB=BA=C, E=6-2A-3B+C with E^2=6E, dimension four',
  outcome='positive-signal;projector-theorem;exact-toy-geometry;model-bound',
  negative_boundary=None,
  next_branch='Preserve as projector theorem for F5F8/F5F9; require exact Weil support before map/relation construction'),
'TRANSFER-P097': dict(
  mechanism='complete exact involution-dimension census of the nine F5F4 correspondences for bounded family target screen (eight 3+3 splits g(D6)=6; exceptional 2+2 split g(D6)=5)',
  outcome='positive-signal;exact-census;clean-room-verified;toy;model-bound',
  negative_boundary=None,
  next_branch='Preserve dimension census as full-field route genus/projector control; do not promote low-genus gcd agreement to a completed family screen'),
'TRANSFER-P098': dict(
  mechanism='16 nonexceptional F5F10 dimension-three slots screened in two independently implemented low-genus quotient presentations (ordinary-slope producer, elimination inverse-slope verifier)',
  outcome='positive-signal;two-presentation-agreement;toy;model-bound',
  negative_boundary='All 16 slots have exact target multiplicity zero in both presentations; R5 collapses 8 records to 6 arithmetic signatures; neither route serializes the full normalized-field inventory — not yet the F5F10 family negative',
  next_branch='Implement full-field P1,D2,D3,D6,C,Y2,Y3,Z interaction sums on (101,10,64,113) through r=3; require exact trace agreement before family extension'),
'TRANSFER-P099': dict(
  mechanism='two disjoint cubic collision places account for every affine singular source-lift point through degree three on one F5F10 record; corrected/+3 control factors have exact Weil certificates',
  outcome='positive-signal;one-record-finite-affine;exact-arithmetic;toy;model-bound',
  negative_boundary=None,
  next_branch='Compute projective conductor support and a blind global count; family/map/factor-base/relation/descent/algorithm gates remain false'),
'TRANSFER-P100': dict(
  mechanism='complete projective divisor support + third-presentation direct count numerically reconcile normalized parent counts for one F5F10 record (R17 exact genus-2 model; R18 direct count)',
  outcome='positive-signal;one-record-observation;custody-revise;toy;model-bound',
  negative_boundary='R18 red team: strict custody and backend independence REVISE — producer conditioned success on expected nonsquare class, hardcoded F/G, no runtime access proof',
  next_branch='Use preregistered R19 to remove square-class condition, derive F/G, increment op counters, cover all records; map/relation/descent/cost/algorithm gates remain false'),
'TRANSFER-P101': dict(
  mechanism='raw-to-normalized correction per F5F10 source cover = double-square count minus double-nonsquare count, across frozen eight-record family (R19 forward/reverse, 18,275,452 base elements visited)',
  outcome='positive-signal;deterministic-same-backend-family-normalization;toy;model-bound',
  negative_boundary='Strict runtime custody and distinct-backend confirmation false',
  next_branch='Do not generalize correction signs without local residue data; do not infer target transfer or algorithm'),
'TRANSFER-P102': dict(
  mechanism='PO96N exact non-product Kummer smoke object as reduced-support negative control for K1; frozen receipt sufficiency preflight for rational-curve cycle enumeration',
  outcome='positive-signal(artifact-exact);sufficiency-negative(stage-success-false);toy;model-bound',
  negative_boundary='Receipt lacks Neron-Severi basis, Kummer quartic equation, 16 exceptional-curve equations, alternate fibration, bounded curve family, incidence lift',
  next_branch='Preserve as historical artifact-sufficiency observation; P103 supersedes part of the missing list; relation enumeration remains unauthorized'),
'TRANSFER-P103': dict(
  mechanism='PO96N smoke curve independently yields exact base-defined Kummer quartic (21 monomials, 16 geometric ordinary double points) with standard Kummer lattice rank 16 det 64, polarization+Kummer rank 17 det 256',
  outcome='positive-signal;exact-standard-geometry;toy;model-bound',
  negative_boundary=None,
  next_branch='Full Neron-Severi saturation, global resolved curves, alternate fibration, incidence lift, relation, algorithm gates remain false'),
'TRANSFER-P104': dict(
  mechanism='PO96N quotient unpolarized-isomorphic to E x E; endomorphism-induced Hermitian classes saturate NS(A) (rank 4, signature (1,3), det -387; conductor 3, disc -387)',
  outcome='positive-signal;abstract-saturation-theorem;toy;model-bound',
  negative_boundary=None,
  next_branch='Do not substitute an arbitrary pure-summand maximal overlattice for geometric Kummer gluing'),
'TRANSFER-P105': dict(
  mechanism='primitive Frobenius-compatible discriminant-graph gluing materializes full abstract Kummer lattice (rank 20, (1,19), det -1548) and product-Kummer elliptic pencil (W^2=f(u)f(x), four I0* fibers)',
  outcome='positive-signal;marked-corresponding-object-fibration;toy;model-bound',
  negative_boundary=None,
  next_branch='Lexicographic marking is not yet PO96N custody; visible sections are product/endomorphism controls'),
'TRANSFER-P106': dict(
  mechanism='degree-24 quotient lifts recover PO96N actual product-to-theta finite two-torsion marking (image integers [34952,36960,42688,58408]) and select the geometric Kummer gluing (720 symplectic relabelings exhausted)',
  outcome='positive-signal;finite-marking-custody-closed;toy;model-bound',
  negative_boundary=None,
  next_branch='Prove the section-control theorem and start bounded multisection saturation; arbitrary-point functions, non-control cycles, incidence rows, factor base, descent, algorithm gates false'),
'TRANSFER-P107': dict(
  mechanism='recovered product surface carries indecomposable principal polarization (minimum 4 vs product 1, PO96N 8) inequivalent to both, yielding distinct base-field genus-2 curve y^2=29x^6+...+58, Igusa (98,68,4), Jacobian order 109^2',
  outcome='positive-signal;distinct-corresponding-object;toy;model-bound',
  negative_boundary=None,
  next_branch='Run K1P1 to recover both explicit maps and compare pull-push algebra with product projections and Z[pi]; no factor-base/relation work until a noncontrol operation survives'),
'TRANSFER-P108': dict(
  mechanism='alternate K1P0 curve has exactly two explicit independent base-field degree-4 maps to the original prime-order elliptic curve (mod negation) with deterministic quartic pullback interface; 96,417 normalized denominator cases',
  outcome='positive-signal;restricted-theorem(map-recovery);toy;model-bound',
  negative_boundary=None,
  next_branch='Run K1P2: compare quartic factorization/paired incidence vs random quartics, direct elliptic/Semaev, split-Jacobian, endomorphism controls before relations'),
'TRANSFER-P109': dict(
  mechanism='two K1P1 maps realize expected complementary split-Jacobian pull-push identity (all 216/216 cross sums zero, same-map sums [4]R), but canonical signed-point rows fail full factor-base rank and native factors never recur',
  outcome='mixed;pull-push-identity-positive;factor-base-rank-failure;toy;model-bound',
  negative_boundary='Native support 450, recurrence 0; canonical signed support 48 rank 31 with 154/216 rows tautologies; rational signed support 26 rank 8; noncontrol_structure=false',
  next_branch='Preserve only native-label no-recurrence theorem + signed-point rank/cost failure; K1P3 must derive nonzero off-diagonal target coefficient and independently recurring canonical labels'),
'TRANSFER-P110': dict(
  mechanism='every ordinary pointwise map C4->E has aggregate fiber push in End(E); strongest target-bearing controls phi_i+[b]phi_j repair rank only by building linear-size signed log table (Jac(C4)~E^2 universal property)',
  outcome='negative-result(aggregate-novelty-closed);positive-control(linear-table);toy;model-bound',
  negative_boundary='Joint canonical classes/factor-base/rank 106/51-54/51-54 vs matched direct control 106/54/54; full rank is a linear-table positive control — sublinear support, descent, cost gates false',
  next_branch='Close aggregate novelty for ordinary one-point maps on this split-Jacobian fixture; move to K1P4 multi-point pair-resolvent or Kummer multisection incidence'),
'TRANSFER-P111': dict(
  mechanism='quartic six-subset resolvent gives exact source-recoverable Sym^2(C4) target-bearing rows, but after trace it is a direct complementary elliptic pair with no factor-base concentration',
  outcome='negative-result(label-model-closed);exact-reconstruction;toy;model-bound',
  negative_boundary='216 fibers: 236 raw nonself rows + 160 self-complement controls; canonical 117 classes, factor base/rank 53/53; matched controls mean 53.0625 std 1.1163, frozen threshold 49.7136 — production 53 fails concentration',
  next_branch='Close complementary pair-resolvent label model; K1P5 must use non-complementary Kummer multisection outside K1P3/K1P4 controls'),
'TRANSFER-P112': dict(
  mechanism='saturated Hermitian lattice contains geometrically indecomposable type-(1,2) polarization H018=(9,11,-3,-1) (det 2, square 4, arithmetic genus 3) whose least elliptic intersection is conductor-local class F3=(9,11,-4,-1) at intersection 3',
  outcome='positive-signal;exact-class-census;toy;model-bound',
  negative_boundary=None,
  next_branch='K1P6 must orient integral base-field maps and prove F3 is the connected kernel of the explicit degree-nine conductor-three isogeny chain before any genus-3/ECDLP relation experiment'),
'TRANSFER-P113': dict(
  mechanism='K1P5 conductor-local class F3 is the primitive class of an exact base-field elliptic embedding i=(g11,g9):E_F->E^2 with image ker([[9,1+pi],[-4-pi,11]])^0',
  outcome='positive-signal;direct-isogeny-control;toy;model-bound',
  negative_boundary=None,
  next_branch='K1P7 must recover the primitive Kummer fiber class of H018 from the actual four base nodes and materialize its base-field pencil'),
'TRANSFER-P114': dict(
  mechanism='K0D corrected marking selects unique Frobenius-fixed normalized H018 half-class (tetrad [0,2,5,7]); resulting root frame is lattice arithmetic, not an effective Kummer fibration',
  outcome='mixed;exact-frame-positive;effectivity-negative;toy;model-bound',
  negative_boundary='Actual gluing-basis images [34952,36960,42688,58408] != geometric-support list [34952,36960,48680,64704] (both accidentally give aggregate H018 image 23040); base scheme/effectivity/nefness/Kodaira fibers/pencil all false',
  next_branch='Compute H^0(E^2,L_H) and saturated length-four base ideal for an explicitly oriented normalized Poincare representative'),
'TRANSFER-P115': dict(
  mechanism='complementary numerical class F6=3H018-2F3 is the primitive class of a second exact base-field elliptic embedding (E6: y^2=x^3+47x+33, order 109, j=77; g11_6 phi9_6=4+pi, g9_6 phi9_6=-[9])',
  outcome='positive-signal;exact-embedding;toy;model-bound',
  negative_boundary=None,
  next_branch='Combine exact F3 and F6 embeddings; recover order-nine addition-map kernel over full 3-torsion field; verify all four entries of pulled-back H018 polarization before theta operators'),
})
OV.update({
# --- 2026-07-18 oriented norm Kani recovery (new IDs only; ONK-001/IKD-012/IKD-013 are changed entries) ---
'ISO-RT-IKD-015': dict(
  mechanism='exact Kani-shaped lifts with one public ramified pairing transcript retain norm-one digit a in F_ell; finite source line has exactly (ell+3)/2 target lines',
  outcome='restricted-theorem;negative-result(local-pairing-transcript-model);model-bound;novelty-unverified',
  negative_boundary='Constant-success pairing-only selection requires Omega(ell) candidates locally and Omega(m/2^omega(m)) for odd squarefree m; at ell=5,17,37 all exact transports invertible, all projective lines vary, linearized two-selector predecessor fails',
  next_branch='Formalize a pairing-oracle transcript; determine whether Tate-Weil-Cartier data exposes non-Hermitian cross-level value linear in a; preserve the exact lower bound if not'),
'ISO-RT-DO-016': dict(
  mechanism='two coherently transported effective orientations generating M_2(Z/nZ) determine a known-degree isogeny full n-torsion action up to exactly 2^omega(n) determinant-compatible scalar roots (centralizer argument); prime n sign pair yields one normalized x-map',
  outcome='restricted-theorem;positive-recovery-reduction;toy-evidence;model-bound;novelty-unverified(Macula-Stange-Th12-priority)',
  negative_boundary=None,
  next_branch='Build geometric prime-power denominator-bearing fixture; compare fully charged recovery vs Macula-Stange Th12, single-orientation conic branch, two-endomorphism EndRing routes'),
'ISO-NR-DO-021': dict(
  mechanism='custody retraction: earlier degree-3 n=5,7 fixture does not establish a public double-orientation recovery interface',
  outcome='negative-result;custody-failure;preserved-retraction',
  negative_boundary='Target actions were computed as rational quasi-endomorphism actions THROUGH the hidden isogeny; one source automorphism did not preserve the secret kernel; verifier checked serialized consistency rather than independent reconstruction',
  next_branch='Keep predecessor out of submission evidence; use only integral public endpoint maps, public-only selection, secret-aware independent verification'),
'ISO-RT-BWL-017': dict(
  mechanism='in marked valuation-one ramified truncation, one designated cross-level pairing character has exponent equal to the hidden Bockstein digit (f_B^T J delta_a e_A = a) and is a sufficient statistic for local quotient transport',
  outcome='restricted-theorem;marked-basis-truncated-local-model;conditional-charged-oracle;toy-evidence;novelty-unverified',
  negative_boundary='Geometric realization and oracle acquisition unproved; acquisition circular for public recovery (character needs hidden Kani block on ell^2-torsion lift); 72000 marked rebasings preserve value; fresh-coordinate maps 4000 injective/10000 noninjective/400 constant (noncanonicity)',
  next_branch='Instantiate the block in the GGR Tate-Weil-Cartier diagram; decide whether a geometrically computable value is zeta^(u*a+v) for public u!=0 without circular secret-torsion access'),
# --- balanced-primary identification (2026-07-20 + 2026-07-24) ---
'ISO-RT-BPI-018': dict(
  mechanism='sign-oblivious primary images identify bounded-degree EC homomorphism up to global sign when min complementary generated-subgroup sum exceeds twice the degree sum (degree parallelogram law); generated-subgroup/unequal-degree/error-erasure forms proved',
  outcome='restricted-theorem;novelty-unverified;paper-proof(papers/balanced_primary_isogeny_identification)',
  negative_boundary=None,
  next_branch='Seek expert priority review and a sharp converse; do not call the arithmetic sign-partition architecture wholly new'),
'ISO-OBS-BPI-019': dict(
  mechanism='genuine Frobenius-oriented self-pairings at orders 3,7,11 feed public three-row decoder for unique degree-5 conductor 15->3 ascent over F_34651 (beta=32>20, additive capacity 9<10)',
  outcome='observation;toy-evidence;model-bound;full-path-interface-validation',
  negative_boundary=None,
  next_branch='Build multiple nontrivial degrees/curve families with more than one rational degree-d source edge'),
'ISO-NR-BPI-020': dict(
  mechanism='degree-5 toy does not show balanced-primary rows improve recovery: nine orbit rows + public curve identity recover same map faster (0.006-0.011s vs 0.043-0.059s)',
  outcome='negative-result;toy-evidence;model-bound',
  negative_boundary='Preregistered 30-run source-only zero-row ablation also recovers the unique edge, median 0.001903375 s — the balanced-primary rows are not the discriminating resource on this fixture',
  next_branch='Run same-instance fully charged direct-Kummer/additive-identity/BMSS/Kani-theta comparisons on sources with multiple candidate edges before any cryptographic claim'),
'ISO-OBS-BPI-021': dict(
  mechanism='reversing the degree-13 ramified fixture removes the source-only uniqueness shortcut while balanced-primary rows still recover the target degree-13 map (F_390391, primaries 3,5,7,11; beta=68>52; additive 11<26)',
  outcome='observation;toy-evidence;model-bound;nonunique-source-recovery;not-asymptotic',
  negative_boundary=None,
  next_branch='Fully charged same-instance comparison vs root-enumerating Kani/theta, additive curve-identity, BMSS/normalization on this nonunique-source fixture'),
'ISO-OBS-BPI-025': dict(
  mechanism='genuine Frobenius-oriented ramified self-pairings at orders 3,5,7,11 feed public four-row decoder for degree-13 conductor 13->1 ascent over F_390391 in strict balanced-primary region',
  outcome='observation;toy-evidence;model-bound;positive-signal;novelty-unverified',
  negative_boundary=None,
  next_branch='Same-instance cost comparison vs additive curve-identity, BMSS-style normalized reconstruction, GGR/Kani/theta across increasing degrees'),
'ISO-NR-BPI-026': dict(
  mechanism='implementation custody negative: first degree-13 producer wrapper updated runpy result dictionary rather than producer function globals (reused old degree-5 rows)',
  outcome='negative-result;implementation-custody;pre-acceptance',
  negative_boundary='V1 reused degree-5 primary rows and was rejected by the new degree-13 checks; arithmetic claim unaffected',
  next_branch='Mutate run.__globals__ or replace with parameterized library; keep failure as wrapper-custody regression test'),
'ISO-NR-BPI-027': dict(
  mechanism='hash custody negative: second degree-13 producer had valid arithmetic but invalid final payload hash (included previous base payload hash field)',
  outcome='negative-result;hash-custody;pre-acceptance',
  negative_boundary='Verifier rejected only producer_payload_hash',
  next_branch='Always remove prior payload_sha256 before recomputing final digests after wrapper augmentation'),
'ISO-OBS-BPI-028': dict(
  mechanism='genuine Frobenius-oriented ramified self-pairings at orders 3,5,7,11,13 feed public five-row decoder for degree-17 conductor 17->1 ascent over F_8678671 (beta=248>68; additive 17<34)',
  outcome='observation;toy-evidence;model-bound;second-fixture-positive-signal',
  negative_boundary=None,
  next_branch='Add blind-instance sweep and fully charged same-instance baseline comparison; do not promote to general complexity claim'),
'ISO-NR-BPI-029': dict(
  mechanism='contract-control negative: first degree-17 verifier incorrectly required every leave-one-primary control to fall below threshold (five-primary tuples can stay strict after deleting a small primary)',
  outcome='negative-result;contract-control;pre-acceptance',
  negative_boundary='Correct diagnostic tuple: removals 3,5,7,11,13 give betas 142,116,94,74,68; only removing 13 lands at threshold',
  next_branch='Treat leave-one as diagnostic for redundant primary sets; use additive rank, nonramified controls, independent fixtures as negative controls'),
'ISO-OBS-BPI-030': dict(
  mechanism='balanced-primary rows can collapse a nonconstant local square-root branch factor under bounded torsion-product budget: under cap prod(n_i)<=64d^2, canonical small-prime witnesses satisfy beta>4d with additive deficit while root classes mod global sign grow 8 (d=13) to 256 (d=8191)',
  outcome='observation;combinatorial-screen;model-bound;not-a-break',
  negative_boundary=None,
  next_branch='Same-instance benchmark on nonunique-source fixture: direct Kummer-row decoding vs explicit root-tuple enumeration feeding same decoder vs additive curve-identity vs closest Kani/theta or BMSS backend, all costs charged'),
'ISO-OBS-BPI-031': dict(
  mechanism='on reverse degree-13 nonunique-source fixture, explicit local root-branch enumeration feeding the same Kummer-row decoder is map-identity redundant (14 rational source degree-13 maps, 1 marked endpoint, 8 root branches)',
  outcome='observation;same-decoder-microbenchmark;model-bound;not-a-break',
  negative_boundary=None,
  next_branch='Run admission audit for same-instance Kani/theta and BMSS-normalization backends in this checkout; preserve missing-backend gap before runtime claims'),
'ISO-NR-BPI-032': dict(
  mechanism='admission audit: checkout has Kani/theta machinery but NO same-instance Kani/theta or BMSS-normalization backend wired to the reverse degree-13 balanced-primary fixture (80 candidate scripts scanned)',
  outcome='negative-result;admission-audit;missing-same-instance-backend;not-a-break',
  negative_boundary='same_instance_backend_available=false; closest reusable script iso_balanced_kani_recovery.sage.py has fixtures p43_degree7, p43_degree7_non_one_auxiliary, p619_degree15_composite — not F_390391 reverse degree-13',
  next_branch='Adapt iso_balanced_kani_recovery.sage.py to verifier-protected p390391_degree13_reverse fixture, or redirect breakthrough search; no runtime-improvement claim until this gate passes'),
'ISO-NR-BRK-033': dict(
  mechanism='breakthrough triage: no current internal line establishes the requested breakthrough beyond the balanced-primary paper (balanced-primary, oriented-ideal Kani, integral-lattice Schur, Bockstein-Weil branches)',
  outcome='negative-result;breakthrough-triage;model-bound',
  negative_boundary='Balanced-primary strongest signal: toy theta-gated-Kani wall-clock ratios 20.113/7.679/42.261 at degrees 23/31/39 but no normalized field-operation theorem or compact decoder; oriented-ideal same-ideal SCALLOP transfer blocked by ell+1 local branch barrier (counts 6,18,38); Schur/Bockstein need extra public action/leakage not in SCALLOP passive keys',
  next_branch='Crosswalk full GGR 2025/1243 PDF vs balanced-primary theorem; instrument field operations/output size; reopen SCALLOP claims only if a public selector beats product(ell+1) local branch barrier'),
'ISO-XW-BPI-034': dict(
  mechanism='novelty crosswalk: supplied GGR 2025/1243 text does not appear to state the balanced-primary beta(n_i)>4d sign-free Kummer-row uniqueness criterion',
  outcome='novelty-unverified;orthogonal-formulation;not-a-breakthrough',
  negative_boundary='Direct PDF retrieval returned HTTP 403 — based on user-provided GGR text + public ePrint metadata, not a full independent PDF audit',
  next_branch='Acquire full non-403 GGR PDF; check Section 4.3/Theorem 4.3 end to end; if no equivalent criterion, cite GGR for row acquisition/backend and state balanced-primary as separate reconstruction-stage criterion'),
'ISO-GATE-BPI-035': dict(
  mechanism='manuscript gate: balanced-primary passes same-instance toy implementation comparison but fails general-complexity gate because decoder is dense and explicit-map oriented (residual bidegree [d,d], resultant degrees 2d^2 and 6d^2, output sizes 59/79/99 field elements)',
  outcome='observation;toy-evidence;model-bound;proxy-cost;not-a-breakthrough;claim-gates-false',
  negative_boundary='Every measured residual bidegree [d,d]; nonzero resultant degree 2d^2; total 6d^2; pole/content stripping removes no nonconstant scale; primitive resultants 2d^2; squarefree degrees 146,258,486 = d^2-2d+3 still quadratic',
  next_branch='Prove or falsify the leading-term lemma for the current (kernel parameter, target scale) representation; test squarefree-first root extraction as constant-factor optimization only'),
'ISO-OBS-PEARL-036': dict(
  mechanism='implementation-leakage observation: public PEARL-SCALLOP Sage and C++ reference examples print sampled GroupAction secret action vectors to stdout (print(vec), printVector(es))',
  outcome='observation;implementation-leakage-hazard;not-a-protocol-break',
  negative_boundary=None,
  next_branch='Remove or guard print(vec)/printVector(es); do not promote to protocol-level PEARL-SCALLOP break or isogeny-complexity result'),
'ISO-NR-RPDO-037': dict(
  mechanism='repeated-prime ascent obstruction: explicit rational-map carriage of primitive divided orientation does not promote ell=3 conductor-9/27 ascent to complexity breakthrough (right-division degree obstruction)',
  outcome='negative-result;right-division-degree-obstruction;model-bound;not-a-break',
  negative_boundary='Proxy reproduces three fixed-ell^2 failures on conductor-27 fixtures; max right-division power 4; max explicit primitive-orientation degree lower bound 243; claim gates general_isogeny_complexity_improvement/scallop_break/ecdlp_consequence all false',
  next_branch='Implement sentinel compact-evaluator gate forbidding torsion_basis(ell^(r+1)) and full lift-order torsion-field basis construction; only compact SLP/x-only divided-orientation evaluator can reopen'),
'ISO-NR-RPDO-038': dict(
  mechanism='admission audit: current checkout has no admitted compact repeated-prime divided-orientation evaluator',
  outcome='negative-result;admission-audit;no-compact-right-division-evaluator;not-a-break',
  negative_boundary='Accepted path still contains torsion_basis(lift_order) and full lift-torsion acquisition; fixed-ell^2 profile failure present on p in {577,619,757}; compact_evaluator_admitted=false; all claim gates false',
  next_branch='Build runtime sentinel harness first, then develop candidate evaluators inside it; evaluators asking for lift-order torsion or secret path data remain model-bound'),
'ISO-NR-RPDO-039': dict(
  mechanism='negative control: accepted repeated-prime algebraic-basis path is blocked by the compact-evaluator runtime sentinel (fixture F_577, conductor 27, ell=3)',
  outcome='negative-control;sentinel-gated;accepted-path-uses-banned-high-torsion;not-a-break',
  negative_boundary='Sentinel patches constructor globals and blocks on find_algebraic_basis_guided_orientation_lift; first incorrect monkeypatch-scope failure preserved',
  next_branch='Implement candidate evaluators as separate functions; require fixture recovery while sentinel active before reopening complexity/SCALLOP/ECDLP claims'),
'ISO-NR-RPDO-040': dict(
  mechanism='ell-torsion-only invariant obstruction: bare E[ell] operations and Frobenius-on-E[ell] signatures cannot select later repeated-prime ascending lines (nine-fixture suite)',
  outcome='negative-result;ell-torsion-only-invariant-obstruction;model-bound;not-a-break',
  negative_boundary='Across 9 fixtures and 12 later steps, hidden ascending line lies in collision class of size 4=ell+1; step-zero distinguishable; missing datum is divided/Bockstein operator omega_0/ell^r mod ell',
  next_branch='Test whether modular-polynomial derivative/root-multiplicity data recovers the Bockstein digit without E[ell^(r+1)]; if it collides too, pivot away from repeated-prime compact evaluation'),
'ISO-NR-RPDO-041': dict(
  mechanism='coarse modular-derivative obstruction: coarse modular-polynomial derivative data is not a reliable repeated-prime compact selector',
  outcome='negative-result;coarse-modular-derivative-obstruction;model-bound;not-a-break',
  negative_boundary='Coarse signatures distinguish 10/12 later steps but collide completely on conductor-27 middle steps for p=577 and p=619; raw derivative values remain root labels absent a structural Bockstein formula',
  next_branch='Deprioritize repeated-prime compact evaluation unless a provable raw-derivative/Bockstein formula appears; pivot breakthrough search to a different isogeny-recovery lead'),
'ISO-NR-PEARL-042': dict(
  mechanism='passive-transcript-surface audit: audited PEARL-SCALLOP public example stdout does not expose passive Bockstein/marked-torsion data needed for protocol-level attack',
  outcome='negative-result;passive-transcript-surface-audit;implementation-leaks-only;not-a-protocol-break',
  negative_boundary='Stdout prints secret action vectors and shared-secret j-invariants but NOT pairings, BiDLP coefficients, kernel generators, eigenvalue matrices, isomorphism constants, marked torsion images, or Bockstein/divided-orientation transcripts; claim gates false',
  next_branch='Search for non-stdout transcript or verification API returning marked torsion images/pairings/normalized kernels/divided-orientation data; otherwise keep passive PEARL route closed'),
# --- POKE-4D (2026-07-23) ---
'ISO-RT-P4D-022': dict(
  mechanism='POKE-4D norm fiber x^2+y^2=c mod 2^a (c=1 mod 4) has exactly 2^(a+1)=2A ordered pairs streamable in output-linear time; Snake Mackerel level I a=75 gives exactly 2^76 outer candidates before charging candidate reconstruction',
  outcome='restricted-theorem;conditional-OW-KCA-consequence;arithmetic-independently-verified;novelty-unverified',
  negative_boundary='Scalar-mask checking relation M B0 = B1 M with M=alpha I is independent of (q1,q2) — no binary-search direction oracle; conditional on charged fixed-dimensional HDRecover candidate-to-key interface',
  next_branch='Execute iso_poke4d_candidate_to_key_recovery_contract: implement/benchmark candidate-to-key HDRecover on faithful POKE-4D/Snake toy instance; determine candidate-key equivalence quotient and false-candidate early-rejection profile'),
'ISO-NR-P4D-023': dict(
  mechanism='candidate-collapse preflight: fixed public torsion-module graph candidates do not collapse below the norm-fiber size except constant endpoint automorphism quotients',
  outcome='restricted-theorem;finite-module-preflight;negative-result(candidate-collapse);not-HDRecover',
  negative_boundary='For a in {4,5,6,8,10,12,14}: exact marked graph count 2^(a+1), sign quotient 2^a, Gaussian-unit quotient 2^(a-1); c=3 mod 4 controls empty; scalar-mask relation independent of (q1,q2)',
  next_branch='Build two-process public/secret HDRecover harness with sentinels; abort and record scoped negative if it cannot output a complete candidate key with secret file absent'),
'ISO-NR-P4D-024': dict(
  mechanism='admission audit: current checkout does not contain a faithful public-only POKE-4D/Snake candidate-to-key HDRecover implementation',
  outcome='negative-result;admission-audit;missing-geometric-HDRecover;not-a-key-recovery-attack',
  negative_boundary='Expected candidate-to-key producer/verifier absent; no public/secret two-process harness; no complete candidate-key output or OW-KCA recognizer exercised; F_137 N8 Kani/theta control explicitly disqualified as faithful POKE-4D/Snake',
  next_branch='Implement missing two-process public/secret HDRecover harness for faithful toy POKE-4D/Snake receiver instance with sentinels blocking secret (q1,q2,alpha), planted-map, direct-edge, post-hoc rational-map access'),
# --- IC ledger new rows ---
'H325': dict(
  mechanism='after strict P1072/P1073 [14,15] packet, remaining free columns [6,7] may require new source-construction or representation pivot rather than reranking the P1071 selector/top-k source pool',
  outcome='hypothesis;active-hypothesis',
  negative_boundary=None,
  next_branch='Create P1079: search/generate source rows whose public support touches exactly one of [6,7] before adding to the [14,15] packet; column-15 replay only as calibration control'),
'H326': dict(
  mechanism='missing [6,7] descent direction may require new residual supply: column-7 target-eliminated rows, independent column-6 residual rows, or a representation splitting dependent [5,6]/[2,4,5,6]/[1,2,5,6] motifs',
  outcome='hypothesis;active-hypothesis',
  negative_boundary=None,
  next_branch='Create P1080 as source-generator or representation-change scout explicitly requesting column-7 support or independent column-6 residuals before packet insertion'),
'H327': dict(
  mechanism='verified P1083 column-7 relation can be integrated into the order-11779 packet without RHS repair, moving packet one rank closer to target descent',
  outcome='observation;active-hypothesis',
  negative_boundary=None,
  next_branch='Preserve P1085 as current packet baseline: rank 14->15, free columns [6,7,16]->[6,16]; score all next column-6 candidates against this packet'),
'H328': dict(
  mechanism='refreshed public routes or carrier-quotient representations providing verified below-rho column-6 coefficient row with marginal rank gain after P1085',
  outcome='negative-result;active-hypothesis',
  negative_boundary='P1086 scanned 385 verified column-6 support rows across 1749 refreshed artifacts and found 0 strict successes; all 255 representation rows collapse under identity projection',
  next_branch='Do not count carrier-quotient-only progress; column-6 needs genuinely new supply'),
'H329': dict(
  mechanism='source-form generator forcing actual order-11779 column-6 exported forms before certificate export to escape the P1086 rowspace-dependence obstruction',
  outcome='hypothesis;active-hypothesis',
  negative_boundary=None,
  next_branch='Create P1087: generate only cases with actual exported coefficient support touching column 6, export direct certificates, rescore against P1085 packet'),
# --- changed key existing entries ---
'TRANSFER-H011': dict(
  mechanism='pointed Lang torsor implicit invariant quotient for growing scalar-dilation action R+P -> R+[m]P; K=<m,-1> orbit labels for collision search on (q-1)/|K| classes',
  outcome='observation;exact-quotient-and-384-of-384-conditional-recoveries-independently-verified;cyclotomic-invariant-algebra-identified;full-orbit-and-degree-q-realizations-cost-negative',
  negative_boundary='Only realized labels enumerate the orbit or materialize the degree-q Lang algebra; exhaustive cost grows 14.18x to 61.32x rho; no evaluator admitted',
  next_branch='(see PO96O/PO96P successors) construct a structure-bearing evaluator below rho or close the lane'),
'TRANSFER-H035': dict(
  mechanism='normalized six-sheet incidence cover pi:Z=Norm(Y2 x_C Y3)->C primitive Prym/isotypic Jacobian factor after removing visible + disconnected-augmentation copies, with q-isotypic embedding/return pair and sub-rho divisor decomposition',
  outcome='scoped-negative-target-transfer;structural-interaction-object-positive;exact-smooth-function-fields;toy;model-bound;algorithm-false',
  negative_boundary='Dimension-six interaction A_int ~ A_F x A_G; both threefold Weil polynomials irreducible and coprime to target polynomial → target multiplicity zero; projective-incidence binding pending',
  next_branch='Close primitive target transfer for frozen smooth function-field fixture; preserve projective-incidence audit separately; F5F4 must change the family prospectively with target-factor hit outside saturated visible algebra before any relation experiment'),
'ISO-NR-ONK-001': dict(
  mechanism='non-scalar element of the common floor order cannot give a near-degree rank-one Kani auxiliary for a tall ascending isogeny',
  outcome='negative-result;restricted-theorem;model-bound',
  negative_boundary='Exact minimum non-scalar norm is ceil(|D|/4); barrier replay checks 576 rows: 561 protected windows zero hits, 8 positive controls pass; substituting maximal order creates 12,525 false hits',
  next_branch='Keep principal route closed for tall conductors unless a publicly evaluable auxiliary outside the common quadratic order is supplied'),
'ISO-NR-IKD-012': dict(
  mechanism='same-ideal coprime split does not replace the dimension-eight backend in the standard cyclic self-pairing recovery architecture (GGR forms D=mf, N=n1*m share m with D)',
  outcome='negative-result;restricted-local-obstruction;model-bound;preserved-retraction',
  negative_boundary='At ell^r||m in maximal ramified local order, both block directions carry varpi^r; block Smith type (varpi^r,varpi^(3r)) gives #ker(M|A[ell^r])=ell^(3r) not ell^(2r); former B^10->B^4 estimate and synthetic 9.5-bit margin withdrawn',
  next_branch='Test whether an order-N^2 maximal-isotropic subgroup strictly inside the oversized kernel can be selected and transported from available partial torsion data; do not run SCALLOP parameter census first'),
'ISO-RT-IKD-013': dict(
  mechanism='polarized N^2-similitude M of pp abelian surfaces: geometric check #ker(M|A[N])=N^2 forces full-kernel type (Z/N^2Z)^2 and yields two polarized degree-N factors from restricted kernels on both sides, without coprimality',
  outcome='restricted-theorem;model-bound;noncoprime-transversality;novelty-unverified',
  negative_boundary='Exact module producer 9/9 positives for N=4,6,12; 9/9 maps M=N*S retain similitude but fail transversality; verifier 27/27, mutations 4/4 rejected',
  next_branch='Verify local rank-three obstruction on a geometric m>1 block, then test internal maximal-isotropic subgroup selection as the only remaining same-ideal escape route'),
'ECFG-NR-1498': dict(
  mechanism='P1498: does the frozen cubic cover Prym admit a base-field homomorphic quotient of dimension one or two that could carry a non-scalar collision label',
  outcome='negative-result;toy-evidence;model-bound',
  negative_boundary='Exact PO58 genus-4 cyclic cover Jac(X)~E x P; degree-6 Prym Frobenius polynomial irreducible over Q (no dim-1/2 homomorphic quotient); birthday-model collision gains fail',
  next_branch='(auto-extracted)'),
'ECFG-NR-1499': dict(
  mechanism='P1499: remaining nonhomomorphic loophole on frozen cubic cover — reconstruct exact deck lifts in each P1497 residual quadratic algebra and collide preregistered character resultants',
  outcome='negative-result;toy-evidence;model-bound',
  negative_boundary='(auto-extracted from fresh text)',
  next_branch='(auto-extracted)'),
})

# ---------------- PO-transfer entries (transfer-search report 2026-06-10, updates through 2026-07-13) ----------------
PO_TRANSFER = [
 dict(id='PO-transfer-001', mechanism='first horizontal slice: same-field isogeny-class scan for decomposition-metric variation (m=3/S4 summation metrics) on flat-volcano toy class',
  outcome='negative-result;model-bound', negative_boundary='Invariant m=3/S4 decomposition metrics across the class; rank-deficient public relations',
  next_branch='PO-transfer-002 target-coupled relations'),
 dict(id='PO-transfer-002', mechanism='target-coupled relation construction recovering the original toy target scalar via raw divisor-list meet-in-the-middle',
  outcome='negative-result;positive-mechanical-signal;toy-evidence;model-bound',
  negative_boundary='Target recovered but at 178x to 317x rho with large MITM memory — target coupling alone is baseline-lost',
  next_branch='Replace raw divisor-list MITM with structure-bearing native correspondence/Jacobian relation or public prefilter predicting rank gain'),
 dict(id='PO-transfer-003', mechanism='BNIT native bielliptic relation source: split genus-2 cover C:y^2=x^6+A x^2+B, push principal divisors of y-v(x) to elliptic quotient E1; cubic interpolation through lift of -lambda*Q + 3 factor-base lifts leaves quadratic residual',
  outcome='negative-result;positive-mechanical-signal;toy-evidence;model-bound',
  negative_boundary='Direct source rank-deficient on shared F_4099 anchor; one-large-prime repair + streaming recovered all four cells (rank 16/16, verified 137*G=Q) but peak memory 3.90*sqrt(n), charged optimistic floor 3375.96x rho, adverse fit n^1.687; row may collapse to known six-point Semaev/Petit relation',
  next_branch='PO-transfer-004 Plucker-pair batch incidence gate'),
 dict(id='PO-transfer-004', mechanism='Plucker-pair batch incidence gate: determinant/wedge equivalence as orthogonality prefilter for the bielliptic relation source',
  outcome='negative-result;model-bound',
  negative_boundary='Every normalized pair plane unique; base incidence/null ratios 0.927..1.110; charged work 8652.33..115587.62x rho on base cells; unimplemented oracle floor 132.67..451.81x rho; base memory 68.3..200.6 sqrt(n); toy exponents 0.958 charged / 0.561 oracle-floor',
  next_branch='PO-transfer-005: lift target into E(F_p^m)/ker(Tr_m) and test extension-field factor base vs pushed-forward weighted search'),
 dict(id='PO-transfer-005', mechanism='trace-quotient lift E(F_p^m)/ker(Tr_m) ~= E(F_p), m in {2,3}: test whether extension-field factor base + algebraic decomposition beats direct search on pushed-forward base',
  outcome='negative-result(restricted-theorem);loophole-narrowed',
  negative_boundary='Exact restricted theorem: tuples in tau^-1(Q) are exactly weighted tuples summing to Q; full kernel fibers multiply successes and trials equally — raw trace-fiber multiplicity is not a relation-probability or rank gain; only solver-time-in-extension-coordinates loophole survives',
  next_branch='Compare surviving solver-time loophole against older scalar Weil-restriction evidence (PO-004/NR-022) before execution'),
 dict(id='PO-transfer-006', mechanism='exact generic degree-3 maps of a (3,3)-split genus-2 curve: complementary quotient labels each E1 lift; complete phi2 fiber pushes to constant-sum ternary relation exposing up to three cofiber decompositions',
  outcome='negative-result;positive-mechanical-signal;toy-evidence;unramified-affine;model-bound',
  negative_boundary='All 114 complete cofibers push to O; production rows/rank/columns 6/6/18, 34/34/78, 74/74/174; every two-core empty; matched EC-addition triples reproduce ranks exactly; no factor base reaches B-1 rank; optimistic full-affine floor 26.92x/56.16x/80.33x rho, adverse fit n^1.188',
  next_branch='PO-transfer-007: cyclic cover X_d:z^d=h(P), target-couple principal divisor of z-v, factor its norm, require measured label-conditioned factorization advantage + reusable rank + blind descent'),
 dict(id='PO-transfer-007', mechanism='(proposed) cyclic-cover norm-factorization relation source: target-couple principal divisor of z-v on X_d:z^d=h(P), factor norm, merge duplicate pushed E images',
  outcome='proposed;not-run-in-report',
  negative_boundary=None,
  next_branch='Compare actual norm smoothness/solver cost against same relation built directly in elliptic function field; do not credit d preimages'),
]

# ---------------- open-frontier bullet parsing ----------------
BULLET_RE = re.compile(r'^\s*- \[([ x])\] (.*)$')
NAMED_RE = re.compile(r'\*\*([A-Z][A-Za-z0-9-]*( / [A-Z][A-Za-z0-9-]*)?)\*\*')

def parse_bullets(path, source_file, lo, hi):
    out = []
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            if ln < lo or ln > hi: continue
            m = BULLET_RE.match(line.rstrip('\n'))
            if m:
                out.append({'line': ln, 'checked': m.group(1) == 'x', 'text': m.group(2).strip(),
                            'source_file': source_file})
    return out

def bullet_entry(b, idx, source_short):
    named = NAMED_RE.search(b['text'])
    if named and idx <= 5 and source_short == 'autolab_main':
        bid = named.group(1)
    else:
        bid = f'OFQ-{source_short}-{idx:02d}'
    full = b['text']
    outcome = 'resolved' if b['checked'] else 'open-question'
    if b['checked']:
        tl = full.lower()
        if any(w in tl for w in ['negative', 'closed', 'false', 'fail', 'zero']):
            outcome = 'resolved-negative'
        else:
            outcome = 'resolved-positive'
    e = {
        'id': bid, 'family': 'OFQ' if bid.startswith('OFQ') else family_of(bid),
        'source_file': b['source_file'], 'section': 'Open frontier questions',
        'mechanism': mechanism_of(full, full),
        'representation': extract_tags('representation', full),
        'exploited_structure': extract_tags('exploited_structure', full),
        'factor_base': extract_tags('factor_base', full),
        'relation_shape': extract_tags('relation_shape', full),
        'relation_generation': extract_tags('relation_generation', full),
        'compression': extract_tags('compression', full),
        'linear_algebra_object': extract_tags('linear_algebra_object', full),
        'target_descent': extract_tags('target_descent', full),
        'cost_bottleneck': extract_tags('cost_bottleneck', full),
        'outcome': outcome,
        'negative_boundary': neg_boundary(full, '', full) if b['checked'] else None,
        'next_branch': None,
    }
    return e

# ---------------- assembly ----------------
def row_entry(r):
    cells = r['cells']
    claim, status, evidence, next_action = logical_cells(cells)
    full = ' '.join(cells)
    e = {
        'id': r['id'], 'family': family_of(r['id']),
        'source_file': r['source_file'], 'section': r['section'],
        'mechanism': mechanism_of(claim, full),
        'representation': extract_tags('representation', full),
        'exploited_structure': extract_tags('exploited_structure', full),
        'factor_base': extract_tags('factor_base', full),
        'relation_shape': extract_tags('relation_shape', full),
        'relation_generation': extract_tags('relation_generation', full),
        'compression': extract_tags('compression', full),
        'linear_algebra_object': extract_tags('linear_algebra_object', full),
        'target_descent': extract_tags('target_descent', full),
        'cost_bottleneck': extract_tags('cost_bottleneck', full),
        'outcome': outcome_of(r['section'], status, full),
        'negative_boundary': None,
        'next_branch': gist(next_action, 260),
    }
    if 'negative' in (e['outcome'] or '') or 'NR' in r['id'].split('-'):
        e['negative_boundary'] = neg_boundary(claim, evidence, full)
    ov = OV.get(r['id'])
    if ov:
        for k, v in ov.items():
            if v is not None or k in ('negative_boundary',):
                e[k] = v
        # keep auto-extracted next_branch if override is placeholder
        if ov.get('next_branch', '').startswith('(auto'):
            e['next_branch'] = gist(next_action, 260)
        if ov.get('negative_boundary', '') and ov['negative_boundary'].startswith('(auto'):
            e['negative_boundary'] = neg_boundary(claim, evidence, full)
    return e

def main():
    main_rows = parse_rows(f'{IN}/main_research_ledger.md', 'main_research_ledger.md')
    ic_rows = parse_rows(f'{IN}/index_calculus_ledger.md', 'index_calculus_ledger.md')
    entries = []
    seen = Counter()
    for r in main_rows + ic_rows:
        e = row_entry(r)
        seen[e['id']] += 1
        if seen[e['id']] > 1:
            e['id'] = f"{e['id']}#{seen[e['id']]}"
        entries.append(e)

    # open-frontier bullets
    mb = parse_bullets(f'{IN}/main_research_ledger.md', 'main_research_ledger.md', 3, 116)
    ib = parse_bullets(f'{IN}/index_calculus_ledger.md', 'index_calculus_ledger.md', 3, 13)
    for idx, b in enumerate(mb, 1):
        entries.append(bullet_entry(b, idx, 'autolab_main'))
    for idx, b in enumerate(ib, 1):
        entries.append(bullet_entry(b, idx, 'ecdlp_index_calculus'))

    # PO-transfer entries
    for p in PO_TRANSFER:
        entries.append({
            'id': p['id'], 'family': 'PO-transfer',
            'source_file': 'non_generic_transfer_search_20260610.md',
            'section': 'Non-generic transfer/decomposition channel search',
            'mechanism': p['mechanism'],
            'representation': 'cover;jacobian;kummer' if '003' in p['id'] or '004' in p['id'] else ('weil-restriction;extension-field' if '005' in p['id'] else ('cover;jacobian' if '006' in p['id'] or '007' in p['id'] else 'isogeny-class')),
            'exploited_structure': extract_tags('exploited_structure', p['mechanism']),
            'factor_base': extract_tags('factor_base', p['mechanism']),
            'relation_shape': extract_tags('relation_shape', p['mechanism']),
            'relation_generation': extract_tags('relation_generation', p['mechanism']),
            'compression': None, 'linear_algebra_object': extract_tags('linear_algebra_object', p['mechanism']),
            'target_descent': extract_tags('target_descent', p['mechanism']),
            'cost_bottleneck': extract_tags('cost_bottleneck', (p.get('negative_boundary') or '') + p['mechanism']),
            'outcome': p['outcome'], 'negative_boundary': p.get('negative_boundary'),
            'next_branch': p.get('next_branch'),
        })

    # family summaries
    fam_entries = {}
    for e in entries:
        fam_entries.setdefault(e['family'], []).append(e)

    # closed territory: entries with negative outcome and a boundary
    closed = []
    for e in entries:
        oc = (e.get('outcome') or '')
        if ('negative' in oc or '-NR-' in e['id'] or e['id'].endswith('-NR')) and e.get('negative_boundary'):
            closed.append({'id': e['id'], 'source_file': e['source_file'],
                           'obstruction': e['negative_boundary'],
                           'scope_closed': gist(e['mechanism'].split('|')[-1].strip(), 200)})
    closed.sort(key=lambda x: x['id'])

    # open frontier: unchecked bullets + hypothesis-status next branches
    open_frontier = []
    for idx, b in enumerate(mb, 1):
        if not b['checked']:
            named = NAMED_RE.search(b['text'])
            bid = named.group(1) if (named and idx <= 5) else f'OFQ-autolab_main-{idx:02d}'
            open_frontier.append({'id': bid, 'question': gist(b['text'], 400)})
    for idx, b in enumerate(ib, 1):
        if not b['checked']:
            open_frontier.append({'id': f'OFQ-ecdlp_index_calculus-{idx:02d}', 'question': gist(b['text'], 400)})
    for e in entries:
        oc = (e.get('outcome') or '')
        if 'hypothesis' in oc and 'negative' not in oc and e.get('next_branch') and not e['id'].startswith('OFQ'):
            open_frontier.append({'id': e['id'], 'next_branch': e['next_branch']})

    # dominant vocabulary
    text = ''
    for path in ['main_research_ledger.md', 'index_calculus_ledger.md', 'non_generic_transfer_search_20260610.md']:
        with open(f'{IN}/{path}') as f:
            text += f.read().lower()
    vocab_terms = ['isogeny', 'transfer', 'prym', 'kummer', 'trace', 'large-prime', 'krylov', 'character',
        'bucket', 'selector', 'factor base', 'factor-base', 'relation', 'descent', 'semaev', 'summation',
        'weil', 'jacobian', 'cover', 'norm', 'frobenius', 'torsion', 'volcano', 'orientation', 'self-pairing',
        'kani', 'theta', 'endomorphism', 'rho', 'bsgs', 'rank', 'nullity', 'collision', 'divisor',
        'resultant', 'eliminant', 'grobner', 'lattice', 'polarization', 'gluing', 'fiber', 'incidence',
        'kernel', 'automorphism', 'involution', 'deck', 'cm ', 'pairing', 'bockstein', 'hecke', 'zeta',
        'spectral', 'ramanujan', 'matroid', 'homology', 'rittj', 'lattès', 'drinfeld', 'graph', 'ecfg',
        'source', 'certificate', 'verifier', 'mutation', 'holdout', 'toy', 'model-bound', 'rho-comparison']
    vocab = []
    for t in vocab_terms:
        c = text.count(t)
        if c: vocab.append({'term': t, 'count': c})
    vocab.sort(key=lambda x: -x['count'])

    out = OrderedDict()
    out['generated'] = '2026-07-24'
    out['entry_count'] = len(entries)
    out['id_families'] = {fam: len(v) for fam, v in sorted(fam_entries.items(), key=lambda kv: -len(kv[1]))}
    out['entries'] = entries
    out['closed_territory'] = closed
    out['open_frontier'] = open_frontier
    out['dominant_vocabulary'] = vocab[:25]

    with open(f'{IN}/ledger_inventory_20260724.json', 'w') as f:
        json.dump(out, f, indent=1)
    print('entries:', len(entries))
    print('families:', out['id_families'])
    print('closed_territory:', len(closed))
    print('open_frontier:', len(open_frontier))
    print('vocab top:', vocab[:25])

if __name__ == '__main__':
    main()
