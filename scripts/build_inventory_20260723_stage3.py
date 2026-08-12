#!/usr/bin/env python3
"""Stage 3: emit ledger_digest_20260723.md."""
import json, re, os
from collections import Counter, defaultdict

IN = '/Volumes/Volume/crypto-autoresearcher/inputs'
OUT = '/Volumes/Volume/crypto-autoresearcher/outputs'
inv = json.load(open(os.path.join(OUT, 'ledger_inventory_20260723.json')))
manifest = json.load(open(os.path.join(OUT, 'referenced_files_manifest.json')))
by = {r['id']: r for r in inv}

F_MAIN = 'research_ledger_main.md'
F_IC = 'research_ledger_ic_state.md'
F_TR = 'non_generic_transfer_search_20260610.md'
F_BIB = 'bibliography.json'

def oneline(s, n=220):
    s = re.sub(r'\s+', ' ', (s or '')).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'

def dom_outcome(recs):
    c = Counter(r['outcome'].split(' (')[0] for r in recs)
    return ', '.join(f'{k} ({v})' for k, v in c.most_common(3))

L = []
A = L.append
A('# Ledger digest — 2026-07-23')
A('')
A('Built from four fresh inputs: `research_ledger_main.md` (main ledger, current 2026-07-23), '
  '`research_ledger_ic_state.md` (index-calculus state ledger, identical to the prior-run copy), '
  '`non_generic_transfer_search_20260610.md`, and `bibliography.json`. '
  'Companion artifact: `ledger_inventory_20260723.json` (one object per distinct ledger/research ID).')
A('')
A('## 1. Totals')
A('')
A(f'- Total distinct IDs: **{len(inv)}**')
fam = Counter(r['id_family'] for r in inv)
src = Counter()
for r in inv:
    for s in r['source_files']:
        src[s] += 1
A('')
A('### Counts by ID family')
A('')
A('| ID family | count |')
A('|---|---:|')
for k, v in fam.most_common():
    A(f'| {k} | {v} |')
A('')
A('### Counts by source file (an ID in several files is counted once per file)')
A('')
A('| source file | IDs |')
A('|---|---:|')
for k, v in src.most_common():
    A(f'| `{k}` | {v} |')
A('')
multi = [r for r in inv if len(r['source_files']) > 1]
A(f'- IDs appearing in multiple input files (deduplicated into one object): {len(multi)} '
  f'(all in main + IC ledgers).')
A('')
A('## 2. Per-family summary')
A('')
ESSENCE = {
 'ECFG': 'Evans functional-graph (ECFG) index calculus: reverse indices, graph selectors/schedulers, coordinate relation surfaces, Semaev membership backends, and the RT-1472/RT-1476 restricted-theory frontier on toy ECDLP transfers.',
 'TRANSFER': 'Non-generic transfer channel search: correspondence/cover/Jacobian/Prym/Kummer objects that could expose a hidden factor base or decomposition for the original prime-field ECDLP subgroup.',
 'ISO': 'Isogeny- and orientation-based attacks: ascending-volcano self-pairings, oriented-ideal Kani recovery (IKD/ONK), double orientation (DO), Bockstein/pairing lower bounds (BWL), balanced-primary identification (BP/BPI), NIST-curve map applicability.',
 'OFQ': 'Open-frontier questions without a ledger-native ID (synthetic IDs carried over from the prior-run inventory, matched by question text).',
 'SHA1': 'SHA-1 differential-path research recorded in the same main ledger (seed rotation, template-support allocation).',
 'ECDLP-IDEA': 'Idea contracts (ideas/artifacts/ECDLP-IDEA-*) referenced by IC-ledger experiment gates.',
 'BIBLIOGRAPHY': 'Literature references on summation-polynomial / decomposition index calculus.',
 'PO-TRANSFER': 'Early non-generic transfer experiment campaigns (horizontal slice, target-coupled MITM, bielliptic BNIT, Plucker gate, trace quotient, trielliptic cofiber).',
 'NR': 'Short-form numbered negative results in the IC ledger (remaining-column source-family pivots).',
 'BAR': 'Proposed frontier ideas (batch2 idea generation), unscheduled.',
 'RT': 'Restricted-theory frontier questions from idea-generation batches.',
 'P': 'IC-ledger packet-integration baseline row (P1085).',
 'RITT': 'Proposed functional-indecomposability idea (Ritt/Lattes census).',
 'MODHECKE': 'Proposed modular/Hecke idea, unscheduled.',
 'ZILBERPINK': 'Proposed Zilber-Pink style idea, unscheduled.',
 'AMORT': 'Proposed amortization idea, unscheduled.',
 'DRINFELD': 'Proposed Drinfeld-style idea, unscheduled.',
 'PADICHT': 'Proposed p-adic Iwasawa/height idea, unscheduled.',
 'PO': 'Older scalar Weil-restriction evidence reference (PO-004).',
}
A('| family | count | mechanism essence (one line) | dominant outcomes |')
A('|---|---:|---|---|')
for k, v in fam.most_common():
    recs = [r for r in inv if r['id_family'] == k]
    A(f"| {k} | {v} | {ESSENCE.get(k, '')} | {dom_outcome(recs)} |")
A('')

# ---------------------------------------------------------------- new since Jul 20
A('## 3. New since the 2026-07-20 main-ledger copy')
A('')
A('Diff of the fresh main ledger against the Jul-20 copy (`main_research_ledger.md`): exactly 53 added '
  'lines; the IC state ledger is byte-identical to the prior-run copy, so nothing there is new. '
  'Added ledger IDs (41 table rows + 2 new open questions):')
A('')

NEW_SUM = {
 'ISO-BP-001': 'Hypothesis/restricted theorem: pairwise-coprime sign-free primary generators identify a degree-d isogeny up to global sign when beta=min_S(N_S+N_complement)>4d; strict region realized at d=13 with a kernel/scale decoder. Positive toy evidence, model-bound.',
 'ISO-BP-NR-001': 'Negative result: sign-free generator images alone do NOT determine a map without a product-partition condition — exact CM counterexample over F_157 (beta=8<=136) and a degree-11 KCD fixture with a spurious gcd root. Keeps beta>4d as sufficient, not universal.',
 'ISO-BP-P001': 'Positive: balanced complementary-product criterion succeeds where additive sign-oblivious interpolation provably fails; arbitrary-target kernel/scale decoder recovers the unique degree-13 toy map over F_30029 (T=321, scale 289).',
 'ISO-RT-IKD-015': 'Restricted theorem/negative: exact Kani lifts with one public ramified pairing transcript keep a norm-one digit; pairing-only constant-success selection needs Omega(ell) candidates locally, Omega(m/2^omega(m)) for odd squarefree m (ell=5,17,37 verified).',
 'ISO-RT-DO-016': 'Restricted theorem: two coherently transported effective orientations determine a known-degree isogeny\'s n-torsion action up to exactly 2^omega(n) scalar roots; prime n gives one normalized x-map (Macula-Stange Thm 12 has priority for the broad result).',
 'ISO-NR-DO-021': 'Negative/retraction: the earlier degree-3 n=5,7 double-orientation fixture used secret-derived quasi-endomorphism actions; geometric interpretation withdrawn (custody failure), algebra counts remain valid. Retraction note preserved.',
 'ISO-RT-BWL-017': 'Restricted theorem: in the marked valuation-one ramified truncation, one cross-level pairing character equals the hidden Bockstein digit (sufficient statistic for local quotient transport); 72000 rebasings prove noncanonicity of fresh-coordinate maps.',
 'ISO-RT-BPI-018': 'Restricted theorem: sign-oblivious primary images identify a bounded-degree homomorphism up to global sign when the complementary generated-subgroup sum exceeds twice the degree sum (degree parallelogram law); strict tuples verified for degrees 5..1021.',
 'ISO-OBS-BPI-019': 'Observation: genuine Frobenius-oriented self-pairings at orders 3,7,11 feed a public three-row decoder recovering the unique degree-5 conductor 15->3 ascent over F_34651 (beta=32>20 vs additive capacity 9<10).',
 'ISO-NR-BPI-020': 'Negative: the degree-5 toy does not show balanced-primary rows improve recovery — nine orbit rows recover the same map in 0.006-0.011s vs the three-row decoder\'s 0.043-0.059s; zero-row ablation also recovers (median 0.0019s).',
 'TRANSFER-H037': 'New hypothesis (mixed result): geometrically indecomposable (1,2) polarization on fixed E^2 materialized as an explicit genus-3 curve; Jacobian J(C)~E3xE6xD; level-separated; R3 factor-through certificate; routed onward only to H038.',
 'TRANSFER-H038': 'New hypothesis (partial positive): degree-9 kernel descent + inversion quotient exposes explicit coordinates on the elliptic complement D; 118-term bidegree-(9,11) field materialized; Weierstrass model, rational inverse, packets, and sub-rho family descent remain open (harder family goal).',
 'TRANSFER-NR-K1P9A': 'Negative: multiplicity-3 signed labels from rational inversion orbits are random-matched; expected streamed first relation 4.768595, mean rank-11 position 150.916; no parent inverse, factor logs, descent, or two-coordinate target rank.',
 'TRANSFER-NR-K1P10B': 'Negative/incomplete: generic Brill-Noether adjunction on the 118-term presentation hit the 20-minute cap without emitting genus/place (positive control passed). Preserves the high-degree quotient field; route replaced by specialized low-pole search.',
 'TRANSFER-NR-K1P10C': 'Negative: common-pole ansatz disproved — X11/X9 coefficient multisets give a shared degree-1 infinite pole of multiplicity 1, contradicting divisibility by 11 and 9; R3 proves field equality, not pole shape.',
 'TRANSFER-P-K1P8': 'Positive: H018 exposes level-separated J(C)~E3xE6xD with cover degrees (6,3,2), reversible two-coordinate order-109 transfer through corrected H#, auxiliary factor of order 119 (7*17).',
 'TRANSFER-P-K1P10': 'Positive: K1P10A+R3 materialize the actual degree-9 kernel-invariant elliptic quotient field inside F(D_tilde) (pole degrees 99/81, 10674x120 rank 119, unique irreducible 118-term relation, 47524/47524 product equalities).',
 'TRANSFER-P096': 'Positive: the exceptional normalized compositum carries a genuine abelian fourfold interaction projector (A^2=3A, B^2=2B, AB=BA=C, E^2=6E); exact toy geometry, not target support.',
 'TRANSFER-P097': 'Positive: complete exact involution-dimension census of the nine F5F4 correspondences (eight split 3+3 with g(D6)=6; exceptional 2+2 with g(D6)=5); producer 13/13, clean-room verifier 11/11.',
 'TRANSFER-P098': 'Positive: all sixteen nonexceptional F5F10 dimension-3 slots have exact target multiplicity zero in two independent low-genus presentations; R5 16/16 + 120/120 checks; not yet the full-field family negative.',
 'TRANSFER-P099': 'Positive: two disjoint cubic collision places account for every affine singular source-lift point through degree 3 on one F5F10 record; corrected/control factors carry exact 101-Weil certificates (R15 22/22, R16 10/10).',
 'TRANSFER-P100': 'Positive (custody-flagged): complete projective divisor support + third-presentation direct count numerically reconcile normalized parent counts on one record (R17 20/20; R18 12/12) but custody/backend independence marked REVISE.',
 'TRANSFER-P101': 'Positive: R19 — raw-to-normalized correction per source cover is exactly double-square minus double-nonsquare count across the frozen 8-record family; 18,275,452 base elements visited; all sixteen repaired factors exact Weil; comparator 14/14 + 15/15 mutations.',
 'TRANSFER-P102': 'Positive: PO96N exact non-product Kummer smoke object and reduced-support negative control for K1; frozen receipt insufficient for rational-curve cycle enumeration (preflight 8/8).',
 'TRANSFER-P103': 'Positive: PO96N smoke curve yields exact base-defined Kummer quartic — 21 monomials, 16 geometric nodes, standard Kummer lattice rank 16 det 64, polarization+Kummer rank 17 det 256 (K0 16/16).',
 'TRANSFER-P104': 'Positive: PO96N quotient is unpolarized-isomorphic to ExE; endomorphism-induced Hermitian classes saturate NS(A) (rank 4, signature (1,3), det -387); direct Kummer lattice rank 20 det 396288.',
 'TRANSFER-P105': 'Positive: primitive Frobenius-compatible discriminant-graph gluing materializes full abstract Kummer lattice (rank 20, signature (1,19), det -1548) and the product-Kummer elliptic pencil with 4 I0* fibers.',
 'TRANSFER-P106': 'Positive: degree-24 quotient lifts recover PO96N\'s actual product-to-theta two-torsion marking and select the geometric Kummer gluing (B-images [34952,36960,42688,58408]; K0D 22/22, independent verifier 16/16).',
 'TRANSFER-P107': 'Positive: recovered product surface carries an indecomposable principal polarization distinct from product and PO96N forms, yielding a base-field genus-2 corresponding object (Jac order 109^2; two geometric degree-4 maps certified, formulas open).',
 'TRANSFER-P108': 'Positive: the alternate K1P0 curve has exactly two independent base-field degree-4 maps to the original elliptic curve (mod target negation) with a deterministic quartic pullback interface (18/18 + 19/19 byte-identical).',
 'TRANSFER-P109': 'Mixed/negative: the two K1P1 maps realize the expected complementary split-Jacobian pull-push identity, but canonical signed-point rows fail full factor-base rank (support 48 rank 31; 154/216 tautologies) and native factors never recur (support 450, recurrence 0).',
 'TRANSFER-P110': 'Negative-leaning: every ordinary pointwise map C4->E has aggregate fiber push in End(E); the phi_i+[b]phi_j repair reaches full rank only via a linear-size signed log table (positive control), closing aggregate novelty for one-point maps on this fixture.',
 'TRANSFER-P111': 'Negative-leaning: quartic six-subset resolvent gives exact source-recoverable Sym^2(C4) rows, but after trace it is a direct complementary elliptic pair; production factor base 53 vs matched-control mean 53.0625 fails the frozen concentration threshold.',
 'TRANSFER-P112': 'Positive: saturated Hermitian lattice contains a geometrically indecomposable type-(1,2) polarization H018=(9,11,-3,-1) (no elliptic class at degree 1 or 2); least class F3=(9,11,-4,-1) at intersection 3.',
 'TRANSFER-P113': 'Positive: K1P5\'s conductor-local class F3 is the primitive class of an exact base-field elliptic embedding (closed embedding into ker[[9,1+pi],[-4-pi,11]]^0); a direct-isogeny control, all algorithm gates false.',
 'TRANSFER-P114': 'Positive/cautionary: K0D\'s corrected marking selects the unique Frobenius-fixed normalized H018 half-class [0,2,5,7], but the root frame is lattice arithmetic, not an effective Kummer fibration.',
 'TRANSFER-P115': 'Positive: complementary class F6=3H018-2F3 is the primitive class of a second exact base-field elliptic embedding (E6: y^2=x^3+47x+33, order 109, j=77; exact identities g11_6 phi9_6=4+pi, g9_6 phi9_6=-[9]).',
 'TRANSFER-NR-096': 'Negative: frozen target elliptic factor has exact multiplicity zero in the exceptional fourfold interaction (P_int splits into two dimension-2 involution factors); scoped to (101,100,63,113) and the frozen projector.',
 'TRANSFER-NR-097': 'Negative/reclassification: F5F10 R3/R4 low-genus counts exceed normalized BF/BG degree-3 counts by 3 (raw-vs-normalized collision contributions 1/0 and 3/2); reclassified as independent presentations of shared raw point semantics, not a global repair.',
 'TRANSFER-NR-098': 'Verifier-cost negatives: global Sage function-field routes stalled — R7 in maximal-order work, R8 in integral-basis construction, R11 consumed ~6.55 GB RSS and was interrupted during degree-3 BF place work; preserved as cost negatives, not counterexamples.',
 'TRANSFER-NR-099': 'Negative (family-level): all sixteen normalized dimension-3 factors in the frozen nonexceptional F5F10 split genus-2 residual-cover family have target multiplicity zero; representation-only variants cannot answer the hard goal — a new corresponding-object family is required.',
}
A('| ID | 1-2 line summary |')
A('|---|---|')
new_table_ids = [i for i in ['ISO-BP-001','ISO-BP-NR-001','ISO-BP-P001','ISO-RT-IKD-015','ISO-RT-DO-016','ISO-NR-DO-021','ISO-RT-BWL-017','ISO-RT-BPI-018','ISO-OBS-BPI-019','ISO-NR-BPI-020','TRANSFER-H037','TRANSFER-H038','TRANSFER-NR-K1P9A','TRANSFER-NR-K1P10B','TRANSFER-NR-K1P10C','TRANSFER-P-K1P8','TRANSFER-P-K1P10','TRANSFER-P096','TRANSFER-P097','TRANSFER-P098','TRANSFER-P099','TRANSFER-P100','TRANSFER-P101','TRANSFER-P102','TRANSFER-P103','TRANSFER-P104','TRANSFER-P105','TRANSFER-P106','TRANSFER-P107','TRANSFER-P108','TRANSFER-P109','TRANSFER-P110','TRANSFER-P111','TRANSFER-P112','TRANSFER-P113','TRANSFER-P114','TRANSFER-P115','TRANSFER-NR-096','TRANSFER-NR-097','TRANSFER-NR-098','TRANSFER-NR-099']]
for i in new_table_ids:
    A(f"| {i} | {NEW_SUM[i]} |")
A('')
A('Also changed since Jul 20 (same IDs, updated content):')
A('')
A('- **TRANSFER-H036** — evidence updated: F5F7 projector independently passed, F5F8 exceptional dimension-4 target zero, F5F9 census, F5F10/R19 repair chain complete; current frozen family recorded as a MISS; next branch is to freeze a semantically distinct corresponding-object family.')
A('- **TRANSFER-P095** — updated: normalization no longer pending (F5F7 proves A^2=3A, B^2=2B, AB=BA=C, E^2=6E); F5F8 target multiplicity zero noted; preserved as the 2+2 control.')
A('- One open question replaced: the F5F5-R7 completed-local-certificate question (prior synthetic id **OFQ-autolab_main-19**, now marked superseded) was replaced by the checked R19 item (new **OFQ-autolab_main-106**) plus the two hard-goal questions for TRANSFER-H036/H038.')
A('- One brand-new open question: the ramified-orientation strict-balanced-primary question (**OFQ-autolab_main-105**).')
A('- One new literature-map row: "Isogeny/Jacobian ECDLP transfer" (Johnston 2010; Tian 2020; Tsakou-Ionica 2021), with the gap clause aimed at TRANSFER-H036.')
A('')
A('Coverage note (not new ledger content): 18 IC-ledger IDs from combined rows '
  '(ECFG-P253..ECFG-P271 except ECFG-P269, which already had its own row) were absent from the prior-run '
  'inventory because the prior parser skipped slash-combined row IDs. They are included now; their content '
  'predates Jul 20. Similarly, 7 proposed question IDs from the batch2 comment (AMORT-A3, DRINFELD-B2, '
  'ZILBERPINK-C2, PADICHT-C3, BAR-TRANSPORT-D1, BAR-AMORT-D2, BAR-RITT-D3) and the ECDLP-IDEA-* contracts '
  'referenced in IC-ledger text are now included.')
A('')

# ---------------------------------------------------------------- negative list
A('## 4. Consolidated CLOSED / negative-control list')
A('')
negs = [r for r in inv if r['outcome'].startswith('negative-result')]
A(f'{len(negs)} records carry a `negative-result` outcome. One line each: ID — obstruction as stated '
  '(measured quantities preserved where the ledger states them). Full text in the JSON `negative_boundary` field.')
A('')
for r in negs:
    b = r['negative_boundary']
    b = re.sub(r'^(Ruled out/finding|Ruled out): ', '', b)
    b = b.replace(' || Lesson/boundary: ', ' ⟶ ').replace(' || Evidence: ', ' ‖ ').replace('Declared boundary: ', '')
    A(f"- **{r['id']}** ({r['source_files'][0].replace('.md','')}) — {oneline(b, 300)}")
A('')

# ---------------------------------------------------------------- open questions
A('## 5. Open-frontier questions (exactly as stated)')
A('')
main_txt = open(os.path.join(IN, F_MAIN)).read()
ic_txt = open(os.path.join(IN, F_IC)).read()

def questions(txt):
    out = []
    inq = False
    for ln in txt.split('\n'):
        if ln.startswith('## '):
            inq = 'frontier' in ln.lower()
            continue
        if inq:
            m = re.match(r'- \[([ x])\]\s*(.*)', ln)
            if m:
                out.append((m.group(1), m.group(2).strip()))
    return out

qm, qi = questions(main_txt), questions(ic_txt)
A(f'### Main ledger ({len(qm)} items; [ ] = open, [x] = checked/answered)')
A('')
for c, t in qm:
    A(f'- [{c}] {t}')
A('')
A(f'### IC state ledger ({len(qi)} items)')
A('')
for c, t in qi:
    A(f'- [{c}] {t}')
A('')
A('Proposed-but-unscheduled idea IDs listed in the main-ledger preamble comment (batch2 idea generation): '
  'RT-1476-SUBRES-A1, RT-1472-CYCLEMAT-A2, AMORT-A3, MODHECKE-B1, DRINFELD-B2, RITT-B3, ISOWALK-C1, '
  'ZILBERPINK-C2, PADICHT-C3, BAR-TRANSPORT-D1, BAR-AMORT-D2, BAR-RITT-D3.')
A('')

# ---------------------------------------------------------------- refs
A('## 6. Referenced-file audit (Task 2)')
A('')
A(f"Repo-relative file paths referenced by the three markdown ledgers (backtick-quoted, brace-expanded): "
  f"{len(manifest['copied']) + len(manifest['missing'])} distinct. "
  f"Copied into `inputs/refs/` (preserving relative names): **{len(manifest['copied'])}**. "
  f"Missing under `/Volumes/Volume/git/autolab/`: **{len(manifest['missing'])}** "
  f"(full list also in `outputs/referenced_files_manifest.json`).")
A('')
A('Missing referenced files:')
A('')
for p in manifest['missing']:
    A(f'- `{p}`')
A('')
A('Notes: the missing set is dominated by `ecdlp_research_handoff_2026060{1,2,4,5}/.../experiment_result.md` '
  'and `experiment_contract*.md` files — those handoff directories no longer exist under the autolab root '
  '(only five `ecdlp_research_handoff_*` directories, all dated 20260603, are present). Also missing: four '
  '`ideas/artifacts/ECDLP-IDEA-*` documents (the `ideas/` tree is absent) and '
  '`ecdlp_research_handoff_20260625_factor_substitution_family_holdout/experiment_contract.md`. '
  'Key referenced documents that WERE found and read include `research/double_orientation_schur_selector_v1_retraction.md`, '
  '`research/oriented_ideal_kani_recovery.md`, `research/idea_generation_20260718_batch2.md`, '
  '`papers/balanced_primary_isogeny_identification/paper.tex`, the `research/PO_transfer_*` contract series, and '
  '`research/ISO_product_kummer_shared_node_contract.md`.')
A('')
A('## 7. Method and scope decisions')
A('')
A('- Fields `representation, exploited_structure, factor_base, relation_shape, relation_generation, '
  'compression, linear_algebra_object, target_descent, cost_bottleneck` are keyword-derived index labels '
  'computed from each entry\'s full ledger text; `not stated` means the entry text gave no matching evidence. '
  '`mechanism` is the entry\'s claim/signal/hypothesis cell verbatim; `outcome` is normalized from the '
  'ledger\'s own status wording; `next_branch` is the ledger\'s next-action/next-validation/lesson cell verbatim.')
A('- Synthetic `OFQ-*` IDs (prior-run convention) are kept for untagged open questions: 106 prior IDs '
  'matched by question-text prefix, 2 new (105, 106), 1 orphan (OFQ-autolab_main-19, question replaced).')
A('- Slash-combined row IDs are split with family-prefix propagation (ECFG-P253/P254 → ECFG-P253 + ECFG-P254, both sharing the row).')
A('- `IDEA-###` and `ECDLP-IDEA-###` mentions are merged under the canonical `ECDLP-IDEA-###` form.')
A('- Internal run/round tags inside evidence cells (K1P7A-R1, F5F10, R19, PO96AB-R1-F5F4, …) are treated as '
  'sub-references of their parent entries, not as distinct ledger IDs — matching the prior-run granularity.')
A('- Bibliography entries carry `entry_type: literature reference`; `experiment_hook` is mapped to `next_branch`.')
A('- Two prior-run combined question IDs (`RITT-B3 / BAR-RITT-D3`, `MODHECKE-B1 / ZILBERPINK-C2`) are split '
  'into their four component IDs; the combined strings no longer exist as separate records.')
A('')

open(os.path.join(OUT, 'ledger_digest_20260723.md'), 'w').write('\n'.join(L))
print('digest written,', len(L), 'lines')
