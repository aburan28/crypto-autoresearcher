#!/usr/bin/env python3
"""Generate outputs/prior_proposals_digest.md from prior_proposals_index.json + curated clusters."""
import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path('/Volumes/Volume/crypto-autoresearcher')
d = json.load(open(ROOT / 'outputs' / 'prior_proposals_index.json'))
NS = 'not stated'
batch = [c for c in d if 'idea_generation' in c['source_file'] or 'research_directions' in c['source_file']]
registry = [c for c in d if c['source_file'].startswith('ideas/')]

def sid(c):
    f = c['source_file'].split('/')[-1].replace('idea_generation_', 'ig-').replace('research_directions_', 'RD-').replace('.md', '')
    return f"{f}:{c['label']}"

by_key = {}
for c in batch:
    f = c['source_file'].split('/')[-1]
    by_key[(f, c['label'])] = c

def K(igfile, label):
    if igfile.startswith('research_directions'):
        fname = f'{igfile}.md'
    else:
        fname = f'idea_generation_{igfile}.md'
    c = by_key.get((fname, label))
    assert c, (igfile, label)
    return c

# ---------------- curated cross-batch duplicate clusters (verified by reading) ----------------
CLUSTERS = [
 ("Sparse-interpolation / Prony / power-series recovery of the RT-1476 membership backend",
  "Recover Semaev-system roots or the compiler output from O(r) evaluations via Prony/Ben-Or-Tiwari, Hankel pencils, power sums, or transposed power projection — same sparse-recovery primitive re-skinned each batch.",
  [('20260718','A1'), ('20260719','A1'), ('20260718_batch3','A3'), ('20260718_batch5','A1'), ('20260719_batch2','A3')]),
 ("Scalar-sequence recurrences: elliptic nets / EDS / Mahler / umbral / cluster / continuant",
  "Represent k -> x([k]P) or the serial-S3 backward state as a low-complexity bilinear/functional/cluster recurrence and read the log from recurrence structure.",
  [('research_directions_20260717','B1'), ('20260717','A2'), ('20260719','C2'), ('20260718_batch5','B1'),
   ('20260719_batch2','B3'), ('20260719_batch10','C3'), ('20260719_batch13','B3')]),
 ("List-decoding (Guruswami-Sudan) relation predicates",
  "Decode the source-coded relation predicate / membership system as an error-correcting code to batch-generate relations.",
  [('20260718','A3'), ('20260719','B2')]),
 ("Matroid / graph-theoretic large-prime enrichment delta-meters (RT-1472)",
  "Pack 2-large-prime partial relations into full relations via cycle bases, matroid union, or spectral sparsification of the LP graph.",
  [('20260718_batch2','A2'), ('20260718_batch3','A2'), ('20260718_batch5','A2'), ('20260718_batch5','D2')]),
 ("Point-counting supply meters/barriers (Lang-Weil / Deligne / Ax-Katz / Newton polygon / Betti)",
  "Ceil or meter the Semaev-variety relation supply via p-adic or l-adic point counts.",
  [('20260718_batch6','A3'), ('20260718_batch6','D2'), ('20260719','A2'), ('20260719','C1'),
   ('20260719_batch3','A2'), ('20260719_batch3','D3'), ('20260719_batch6','C2')]),
 ("Tensor-rank complexity of the Semaev summation tensor",
  "Beat the L^(3/2) backend floor via tensor-train/tensor-network contraction, border rank, slice rank, geometric rank, asymptotic spectrum, or Temperley-Lieb diagram contraction — each batch pairs it with its own rank lower-bound barrier.",
  [('20260717','B2'), ('20260717','D3'), ('research_directions_20260717','C2'), ('20260718','B4'), ('20260718','D3'),
   ('20260718_batch4','D2'), ('20260718_batch5','D1'), ('20260719_batch7','B3'), ('20260719_batch13','B1')]),
 ("Matchgate / holographic / Pfaffian contraction",
  "Reduce the m-term decomposition count to a Pfaffian/matchgate contraction with a Holant-dichotomy or common-norm barrier.",
  [('20260718_batch3','C1'), ('20260718_batch3','D3'), ('20260719_batch5','C1'), ('20260719_batch9','B3')]),
 ("Coppersmith / lattice small-root relation finding",
  "Turn windowed or lifted relation finding into a lattice small-root problem.",
  [('research_directions_20260718','B3'), ('20260719_batch4','B1'), ('20260718_batch3','C3')]),
 ("p-adic lifts: canonical lift / formal group / crystalline / Cartier-Manin / prismatic delta-rings",
  "Linearize the addition law or the log through a p-adic lift or formal-group logarithm; repeatedly closed by the crystalline order-only barrier and rejected as internal duplicates.",
  [('20260717_batch2','B2'), ('20260717_batch2','D2'), ('20260717_batch2','C2'), ('20260718','B1'), ('20260718','B2'),
   ('20260719_batch2','B1'), ('20260719_batch8','B3'), ('research_directions_20260718','C1')]),
 ("Character-sum / exponential-sum relation bias",
  "Predict or bias relation supply via elliptic character sums, Kloosterman sums, or the Weil explicit formula.",
  [('20260717_batch2','C3'), ('20260718','C2'), ('20260718_batch6','C3')]),
 ("Monodromy / Chebotarev / Galois group of the decomposition cover",
  "Census the Galois/monodromy group of the summation (decomposition) cover; attack only if non-full. RD-20260718 itself declares A1/C2/D2 'one object with three stances'. Arboreal/iterated-preimage and homotopy variants reappear later.",
  [('research_directions_20260718','A1'), ('research_directions_20260718','C2'), ('research_directions_20260718','D2'),
   ('20260719_batch4','C2'), ('20260719_batch3','C3'), ('20260718_batch5','C1'), ('20260718_batch5','D3')]),
 ("Global lifts / xedni / elliptic-surface Mordell-Weil / heights",
  "Lift the ECDLP to a global field or elliptic surface and exploit height compression / MW lattices / special cycles; scarcity of lifts (JKSST xedni collapse) is the recurring fatal obstruction.",
  [('20260717','C3'), ('research_directions_20260718','B2'), ('research_directions_20260718','C3'), ('20260719_batch7','B2')]),
 ("SOS / Lasserre / Sherali-Adams moment relaxations",
  "Relax membership to an SDP moment problem; paired rank barriers.",
  [('20260718_batch4','A1'), ('20260718_batch4','D1'), ('20260719_batch6','B1'), ('20260719_batch6','D2'), ('20260719_batch7','C2')]),
 ("Proof-complexity barriers and certificates (Nullstellensatz / Polynomial-Calculus / resolution / cutting-planes / pebbling / natural proofs)",
  "Lower-bound refutation or certificate size of (non-)membership, or exploit feasibility certificates as alpha-meters.",
  [('20260719','D2'), ('20260719_batch3','A1'), ('20260719_batch3','D2'), ('20260719_batch11','A3'), ('20260719_batch11','D2'),
   ('20260719_batch7','A3'), ('20260719_batch7','D2'), ('20260719_batch4','D3'), ('20260719_batch5','D1')]),
 ("Arithmetic-circuit lower bounds on the membership polynomial (RT-1476 alpha floors)",
  "Shifted partials, partial-derivative dimension, elusive functions, depth-reduction, rigidity, multilinear-formula, formula-size, magnification — a per-batch parade of circuit-LB technologies aimed at the same alpha>=3/2 floor.",
  [('20260719_batch4','A1'), ('20260719_batch4','A2'), ('20260719_batch4','D1'), ('20260719_batch4','D2'),
   ('20260719_batch2','A1'), ('20260719_batch5','D3'), ('20260719_batch13','A3'), ('20260719_batch13','D2'),
   ('20260719_batch13','C1'), ('20260719_batch13','D3')]),
 ("Communication-complexity barriers",
  "Sign-rank/gamma2, number-on-forehead, direct-sum information complexity, discrepancy/corruption, round elimination, query-to-communication lifting against sub-L^(3/2) membership.",
  [('20260719','D1'), ('20260718_batch4','B3'), ('20260719_batch2','D2'), ('20260719_batch5','A2'),
   ('20260719_batch6','A3'), ('20260719_batch9','D3')]),
 ("Analytic sieve supply/barriers (large sieve / Selberg / Bombieri-Vinogradov / parity / singular series)",
  "Sieve-theoretic ceilings on signed 2-LP enrichment; Selberg parity kills signed sieves at the root.",
  [('20260719_batch8','A1'), ('20260719_batch8','A2'), ('20260719_batch8','A3'), ('20260719_batch8','D1'),
   ('20260719_batch8','D3'), ('20260719_batch9','A1'), ('20260719_batch9','D1')]),
 ("Concentration / second-moment / small-ball supply-barriers (Halasz / Janson / Paley-Zygmund / Stein-Chen / Berry-Esseen)",
  "Anti-concentration of weighted LP logs forces delta<=1/4; two consecutive batches attack the same RT-1472 gate with inverse-Littlewood-Offord and dependency-graph variance bounds.",
  [('20260719_batch12','A1'), ('20260719_batch12','A2'), ('20260719_batch12','A3'), ('20260719_batch12','D1'),
   ('20260719_batch13','A1'), ('20260719_batch13','A2'), ('20260719_batch13','C2'), ('20260719_batch13','D1')]),
 ("Incidence-geometry relation harvesting and ceilings",
  "Output-sensitive incidence reporting / polynomial partitioning for chord-rich relation harvest; paired with incidence-richness ceilings.",
  [('research_directions_20260717','A2'), ('research_directions_20260717','D3'), ('20260717','A3'), ('20260719','A3'), ('20260719_batch3','B2')]),
 ("Newton-polytope / tropical / non-archimedean valuations",
  "BKK mixed volume, tropical skeletons, Ronkin/coamoeba, Newton-Okounkov bodies, Newton polygons — the same polytope-sparsity hope; measured Newton saturation (MV = Bezout box) closed the first wave.",
  [('20260717','A1'), ('research_directions_20260717','B2'), ('research_directions_20260717','D2'), ('20260717','B3'),
   ('20260718_batch3','B3'), ('20260719','B1'), ('20260719_batch3','B3')]),
 ("Additive combinatorics / higher-order Fourier structure-vs-pseudorandomness",
  "Approximate-homomorphism stability, nilsequences, analytic rank, PFR, almost-periodicity, GAP-structure barriers on the x-map or LP logs.",
  [('20260718','C1'), ('20260718','D2'), ('20260718_batch3','C2'), ('20260718_batch3','D1'), ('20260719_batch5','B1'),
   ('20260719_batch3','C2'), ('20260719','C3'), ('research_directions_20260718','D1')]),
 ("Amortization / many-target / non-uniform preprocessing crossover",
  "Win only in amortized or advice-charged models; each is metered against the Corrigan-Gibbs/Kogan preprocessing frontier.",
  [('20260718_batch2','A3'), ('20260718_batch2','D2'), ('research_directions_20260718','A2'), ('20260717_batch2','A3')]),
 ("Noncommutative / quiver path-algebra searches",
  "Syzygy/Hochschild/path-algebra computations on the correspondence or summation quiver; commutative-quotient collapse closed the first instance.",
  [('20260717','C1'), ('research_directions_20260717','C3'), ('20260719_batch13','B2')]),
 ("Markov-chain sampling / statistical physics of the relation ensemble",
  "Log-concave/Lorentzian samplers, spectral independence, survey propagation, mixing-time barriers for the enrichment sampler.",
  [('20260719_batch5','C2'), ('20260719_batch8','C2'), ('20260719_batch8','C1'), ('20260719_batch8','D2')]),
 ("Isogeny-walk / expander relation harvesting",
  "Non-backtracking walks on isogeny graphs as relation generators; spectral gap is constant-factor, not an exponent change.",
  [('20260718_batch2','C1'), ('research_directions_20260718','A2')]),
 ("Boolean-function analysis of the membership predicate",
  "Sensitivity/block-sensitivity/certificate complexity, evasiveness (KSS), approximate degree, hypercontractivity, quantum adversary/span programs, SQ dimension applied to the m=5 membership predicate.",
  [('20260719_batch7','A1'), ('20260719_batch7','A2'), ('20260719_batch7','D1'), ('20260719_batch10','A1'),
   ('20260719_batch10','D1'), ('20260719_batch10','C1'), ('20260719_batch2','D1'), ('20260719_batch6','C1'), ('20260719_batch11','C3')]),
 ("Group-theoretic / representation-theoretic representations",
  "Equivariant/isotypic rank, GCT occurrence obstructions, Schubert constants, immanants, FI-modules, Kazhdan-Lusztig cells, Deligne-Lusztig characters, Yangian R-matrices, Schur/plethysm.",
  [('research_directions_20260717','B3'), ('20260719_batch4','B2'), ('20260719_batch5','B3'), ('20260719_batch6','B2'),
   ('20260719_batch10','B1'), ('20260719_batch12','B3'), ('20260719_batch12','C3'), ('20260719_batch12','B1'), ('20260719','B3')]),
 ("Structured-linear-algebra backends (displacement rank / Toeplitz / Bezoutian)",
  "Exploit displacement structure of relation matrices for fast solves; measured displacement rank grows linearly (no structure).",
  [('research_directions_20260717','A3'), ('20260718_batch3','A1')]),
 ("Genus-2 / Jacobian / RM transfers",
  "Kani-torsion-glued genus-2 Jacobians and generalized-Jacobian modulus extensions as transfer targets; bounded by the Gaudry fixed-genus barrier.",
  [('20260717_batch2','B1'), ('20260717_batch2','D3'), ('20260718_batch4','B1')]),
]

# winners table
def _file_order(f):
    m = re.match(r'inputs/idea_generation_(\d+)(?:_batch(\d+))?\.md', f)
    date, b = m.group(1), int(m.group(2) or 1)
    return (date, b)
win_files = sorted({c['source_file'] for c in batch if 'idea_generation' in c['source_file']}, key=_file_order)
def win_fmt(c):
    if not c:
        return '—'
    n = c['name']
    if ' — ' in n:
        head, tail = n.split(' — ', 1)
        return f"{head} {' '.join(tail.split()[:5])}"
    return n.split('  (')[0].strip()
winner_rows = []
for f in win_files:
    cs = [c for c in batch if c['source_file'] == f]
    ws = {c['selected_winner']: c for c in cs if c['selected_winner'] != NS}
    row = (f.split('/')[-1].replace('idea_generation_', '').replace('.md', ''),
           ws.get('conservative'), ws.get('representation'), ws.get('high_risk'))
    winner_rows.append(row)

# registry stats
reg_state = defaultdict(int)
for c in registry:
    src = c['source_file'].split('/')[1] if c['source_file'].split('/')[1] in ('deferred', 'rejected') else 'active'
    reg_state[src] += 1

# blacklist
def shortname(c):
    n = c['name']
    n = re.sub(r'\s+', ' ', n).strip()
    return n

bl_batch = []
for c in batch:
    f = c['source_file'].split('/')[-1].replace('idea_generation_', 'ig').replace('research_directions_', 'RD').replace('.md', '')
    bl_batch.append(f"{shortname(c)} [{f}:{c['label']}]")
bl_reg = [f"{c['label']} {shortname(c)}" for c in registry]

lines = []
A = lines.append
A("# Prior Proposals Digest — ECDLP Idea-Generation Mission")
A("")
A("Compiled from the workspace record for the de-duplication of the next idea-generation run. Every entry below is extracted verbatim from the cited files; fields absent in the source are marked `not stated` in the JSON index.")
A("")
A("## 1. Corpus and total candidate count")
A("")
A("| Corpus | Files | Candidates |")
A("|---|---|---|")
A(f"| Idea-generation batch reports | inputs/idea_generation_20260717…20260719_batch13 (20 files) | {sum(1 for c in batch if 'idea_generation' in c['source_file'])} |")
A(f"| Research-Director final reports | research_directions_20260717.md, research_directions_20260718.md | {sum(1 for c in batch if 'research_directions' in c['source_file'])} |")
A(f"| ECDLP-IDEA registry (ideas/) | 17 active + 27 deferred + 366 rejected hypothesis files | {len(registry)} |")
A(f"| **TOTAL indexed** | | **{len(d)}** |")
A("")
A("Additionally, `plan.md` dispatches the 12 `research_directions_20260717.md` candidates as experiments EXP-JET/INC/STR/NET/BKK/EQJ/TRA/TTN/NCP/JETB/BKKMV/INCB-001; `focus/` and `coordination/` contain only execution tracking (focus plans, claim matrix, dispatch queues) for ledger IDs P1509–P1553 and ECDLP-IDEA contracts — **no further proposal lists**. `idea_generation_20260718_batch5.md` §2 also names four lanes **rejected during generation** (never tabled): a half-GCD backend (= batch2-0718 A1 subresultant PRS), an LSH/sketch prefilter (= post-hoc feature control), a Wormald differential-equation 2-core meter (= batch4-0718 A3), and a p-adic-Hodge translation coordinate (= crystalline/Serre–Tate, batch2-0717 B2 + report-0718 B2). These are on the blacklist.")
A("")
A("**Internal batch numbering used inside the files** (verified against cross-references such as “batch5 POWERPROJ-A1”, “batch7 POLYCALC-D2”, “batch14 LARGE-SIEVE-BARRIER”, “batch17 ERGODIC-SZEMEREDI-BARRIER”, “batch18 HALASZ-BARRIER”): the two 2026-07-17 files are “the 07-17 batches”; then batch1 = idea_generation_20260718, batch2 = …20260718_batch2, batch3 = …_batch3, batch4 = …_batch4, batch5 = …_batch5, batch6 = …_batch6, batch7 = idea_generation_20260719, batch8 = …20260719_batch2, batch9 = …_batch3, batch10 = …_batch4, batch11 = …_batch5, batch12 = …_batch6, batch13 = …_batch7, batch14 = …_batch8, batch15 = …_batch9, batch16 = …_batch10, batch17 = …_batch11, batch18 = …_batch12, batch19 = …_batch13. (Caution: inside research_directions_20260718-adjacent prose, “batch2” can also mean 07-17 batch 2, e.g. “DUPLICATE of batch2 STATE-B2”.)")
A("")
A("## 2. Batch winners (3 per batch file: conservative / representation / high-risk)")
A("")
A("| Batch file | Conservative | Representation | High-risk |")
A("|---|---|---|---|")
for (f, w1, w2, w3) in winner_rows:
    A(f"| {f} | {win_fmt(w1)} | {win_fmt(w2)} | {win_fmt(w3)} |")
A("")
A("None of the 60 batch winners is recorded in-workspace as having produced a rho-beating result; per `ideas/README.md` discipline, all contracts stayed `review_required`/unapproved or were retired, and “no contract or experiment ran … no breakthrough”. The three 2026-07-18-report winners and the A2 probe, the only winners with executed smoke runs, are detailed in §4.")
A("")
A("## 3. Near-duplicate clusters across batches")
A("")
A(f"{len(CLUSTERS)} clusters of cross-file near-duplicates (same essential mechanism, possibly renamed or re-rolled as meter/barrier). Labels: ig<file>:<label>; RD = research_directions report.")
A("")
for i, (title, desc, members) in enumerate(CLUSTERS, 1):
    A(f"### C{i}. {title} ({len(members)} proposals)")
    A(desc)
    A("")
    A("Members: " + "; ".join(f"{sid(K(*m))}" for m in members))
    A("")
A("## 4. Winners of the two research_directions reports and what happened to them")
A("")
A("### research_directions_20260717.md — no winner vote; all 12 candidates dispatched (plan.md Stage 1), Coordinator decisions in ledger/DEC-20260718-001…012")
A("")
A("| Cand | Mechanism (short) | Experiment | Official decision |")
A("|---|---|---|---|")
for lab in ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']:
    c = K('20260717'.replace('20260717','20260717'), lab) if False else by_key[('research_directions_20260717.md', lab)]
    disp = c['batch_disposition']
    m = re.match(r'Dispatched as (\S+) per plan.md; Coordinator decision (\S+) \((\S+)\): (.*)', disp)
    exp, dec, decid, why = m.groups()
    A(f"| {lab} | {c['name'].split(' — ')[1][:70]} | {exp} | **{dec}** ({decid}) — {why[:130]} |")
A("")
A("Outcome summary: all nine positive (A/B/C) candidates **reject_scoped** — each one's own named fatal obstruction was measured (Newton saturation MV = Bézout box; displacement rank at generic maximum; birthday-model collisions; σ = 1.0000 exactly; zero output sensitivity; L = O(1); bond-rank α = 1.161/1.322; 4/10 isotypic blocks empty; commutative quotient reproduces all NC relations). All three D-barriers **supported_scoped** (JETB generic-model jet barrier; BKKMV exact growth law MV_m = (m−1)!·2^((m−1)(m−2)); INCB incidence-richness ceiling).")
A("")
A("### research_directions_20260718.md — winners A1 (conservative), B2 (representation), C2 (high-risk); smoke runs executed same session")
A("")
A("- **A1 Chebotarev census (EXP-MONO-001)** — phase-1 smoke (p≤431, seed 20260718): controls pass; toy relation rates match exact predictions inside Weil floors; the substantive m=3 Semaev Chebotarev gate is phase 2, **not yet run** at report time.")
A("- **B2 function-field xedni (EXP-XEDN-001)** — harness smoke: controls pass; xedni scarcity already visible at toy scale (0 sections in 5760 random slots; 0 squares in 200,000 sextics), consistent with the named JKSST-2000 obstruction; promotion gate **not yet run**.")
A("- **C2 imprimitive monodromy (EXP-IMON-001)** — harness smoke: census separates full from non-full covers on controls; the curve cover shows no deviation beyond Weil error (D2-ward); joint m=3 test is phase 2. Its sibling D2 (full-monodromy barrier) shares the same harness.")
A("- **A2 isogeny-class advice (EXP-ISADV-001 probe)** — phase-1 result: cross-curve advice transfer statistically indistinguishable from baseline at all three toy sizes ⇒ **A2 weakened** (scoped negative on transfer).")
A("- **C1 (Buium δ-characters) and C3 (Heegner/Drinfeld cycles)** — **rejected as winners** in-report: stages 1,7 / 4,7 INCOMPLETE, no complete route to target descent, no rho comparison possible.")
A("")
A("## 5. Mechanisms proposed more than twice (family frequency across the 277 mission candidates)")
A("")
freq = [(t, len(m)) for (t, _, m) in CLUSTERS if len(m) >= 3]
freq.sort(key=lambda x: -x[1])
A("| Family | # proposals |")
A("|---|---|")
for t, n in freq:
    A(f"| {t} | {n} |")
A("")
A("## 6. ECDLP-IDEA registry (ideas/) disposition summary")
A("")
A(f"- **{reg_state['active']} active** (proposed_unapproved, novelty_unverified; nine with preflight contracts): ECDLP-IDEA-002/003/004/005/006/007/008/009/010/011/012 (cohort 20260717-a), 050/056/059 (20260717-b), 158/159/160 (20260718-b).")
A(f"- **{reg_state['deferred']} theorem-deferred**: 049, 052, 053, 058, 064, 068, 069, 073, 075, 076, 086, 087, 098, 102, 103, 111, 119, 121, 133, 152, 161, 163, 164, 165, 167, 173, 195.")
A(f"- **{reg_state['rejected']} rejected** (semantic merges or scoped negatives) — see ideas/rejected/. Per ideas/README.md, canonical coverage is IDs 001–410: 17 active, 27 deferred, 366 rejected; nine active contracts; no experiment ever ran; no breakthrough claims. A further ~156 pre-ID screened operations (cohorts 20260720-c/d, 20260721-a…e, 20260722-a…d: classic algorithms, data structures, SAT/CP, DB joins, formal-reasoning tools) were rejected before ID allocation — each transplants a supplied source-bearing object or loses exact provenance against the P1553-R4 endpoint-derived source-return requirement.")
A("")
A("## 7. NAME BLACKLIST — every candidate name ever used")
A("")
A("Do NOT re-propose any of these (including renamed variants). Format: `Name [source:label]`.")
A("")
A("### 7.1 Idea-generation batch files + research_directions reports (277)")
A("")
A(", ".join(bl_batch))
A("")
A("### 7.2 Rejected-during-generation lanes (never tabled)")
A("")
A("half-GCD membership backend (= subresultant PRS, batch2-0718 A1), LSH/sketch relation prefilter, Wormald differential-equation 2-core meter, p-adic-Hodge translation coordinate")
A("")
A("### 7.3 ECDLP-IDEA registry (410)")
A("")
A(", ".join(bl_reg))
A("")
A("### 7.4 Pre-ID screened operation families (rejected before allocation; family names)")
A("")
A("Hopcroft DFA minimization, splay trees, Cartesian-tree RMQ, treaps, B-trees, R-trees, Fibonacci heaps, Boyer–Moore, Gale–Shapley, Stoer–Wagner, PageRank, RTS smoothing, PATRICIA, Fenwick, Dinitz, Johnson reweighting, A*, Tutte–Lovász matching, Metropolis–Hastings, simulated annealing, Gibbs sampling, EM, DBSCAN, Lloyd quantization, Todd–Coxeter, F5, fast multipole, Johnson–Lindenstrauss, sensitivity coresets, Bowyer–Watson Delaunay, Rabin–Karp, Cantor–Zassenhaus, Tarjan SCC, Prim, Savitch, Floyd–Warshall, Lipton–Tarjan separators, FRT metrics, Lovett–Meka, Collins CAD, Prüfer codes, KLM DNF estimation, Lempel–Ziv, Hu–Tucker, cover trees, HNSW, AdaBoost, Remez, Schroeppel–Shamir, Bostan–Mori, Hopcroft–Karp, Bentley–Ottmann, Luby MIS, Jerrum–Sinclair, BCJR, Goemans–Williamson, AMS sketches, Christofides, Fiduccia–Mattheyses, arithmetic coding, Dijkstra, Kahn, Bórůvka, Hierholzer, Havel–Hakimi, Cuthill–McKee, Ukkonen, Manacher, Needleman–Wunsch, Vose alias, Nesterov, Arnoldi, Knuth–Yao, Hopcroft–Tarjan planarity, Gessel–Viennot, y-fast tries, Benczúr–Karger, Micali–Vazirani, Kernighan–Lin, Misra–Gries, weighted reservoirs, Booth canonicalization, Freivalds, BFPRT, AC-3, Davis–Putnam, DPLL, GRASP/CDCL, Chaff, Régin all-different, bucket elimination, junction trees, sum-product, residual BP, WalkSAT, Schöning, Ganter NextClosure, Reiter hitting sets, PinSketch BCH, Kennes Möbius, Björklund determinants, Ryser, Lawler partitioning, Provan–Shier, Tsukiyama, Fredman–Khachiyan, Picard–Queyranne, Makino–Uno, sort-merge join, GRACE hash join, Bloom semijoin, Leapfrog Triejoin, Magic Sets, Rete, Volcano iterators, Selinger, Minesweeper, factorised query results, DBToaster, NPRR joins, Nelson–Oppen, Downey–Sethi–Tarjan congruence closure, SDDs, Angluin L*, algebraic decision diagrams, abstract interpretation, predicate abstraction, Craig interpolation, IC3/PDR, bounded model checking, symbolic execution, superoptimization")

out = ROOT / 'outputs' / 'prior_proposals_digest.md'
out.write_text('\n'.join(lines))
print('wrote', out, len(lines), 'lines')
