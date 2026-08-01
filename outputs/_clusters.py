#!/usr/bin/env python3
"""Cluster near-duplicate proposals across batches and compute mechanism frequencies."""
import json, re
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path('/Volumes/Volume/crypto-autoresearcher')
d = json.load(open(ROOT / 'outputs' / 'prior_proposals_index.json'))
batch = [c for c in d if 'idea_generation' in c['source_file'] or 'research_directions' in c['source_file']]

STOP = set('''the and that this with from over field prime curve point points relation relations
membership semaev factor base descent barrier candidate ledger batch report rho cost exponent gate
meter winner group target mechanism primitive object rank matrix sparse exact toy novelty hypothesis
conjecture status scalar logs log n/a none same standard public charged honest complete full route
path stage stages online offline setup advice enriched enrichment large small new first only each
every never always measured measure measurement exponent not for are but has have its our their
they them into when what which there here these those than then thus hence also more most less
least much many such like just even still well very really quite rather quite may might could would
should must shall will can cannot does do did done being been was were are is be by at on in of to
a an or if as so we it no yes up out about above after again against all any because before below
between both down during few further had having he her hers herself him himself his how i if in
into is it its itself just me more most my myself no nor not now of off on once only or other our
ours ourselves out over own same she should so some such than that the their theirs them themselves
then there these they this those through to too under until up very was we were what when where
which while who whom why will with you your yours yourself yourselves polynomial polynomials system
solve solver solving equation equations root roots variety degree dense support monomial monomials
elimination resultant resultants grobner gb ideal ideals module modules algebra algebraic geometry
geometric arithmetic combinatorial theorem proof lemma corollary bound bounds upper lower asymptotic
omega theta sigma delta alpha beta gamma epsilon zeta lambda kappa mu nu pi tau phi chi psi
via per vs iff wrt e.g i.e etc et al fig fig. table section appendix remark remarks example
examples note notes claim claims definition definitions proposition propositions question questions
problem problems conjecture conjectures known unknown open closed closure closes closing kill kills
killed killer dead dies die fail fails failed failure negative positive control controls run runs
running ran seed seeds size sizes scale scales scaling toy-scale crypto cryptographic graph graphs
node nodes edge edges vertex vertices tree trees forest forests path paths cycle cycles circuit
circuits formula formulas size complexity class classes hard hardness easy easier easiest difficulty
difficult possible impossible possibly probability probabilities probable random randomized
deterministic heuristic model models model-bound restricted generic general generically special
specialized specific explicitly explicit implicit implicitly construction constructions construct
constructs constructed constructive algorithm algorithms algorithmic compute computes computed
computing computation computations computational computationally efficient efficiently inefficiency
inefficient fast faster fastest slow slower slowest speed speeds speedup speedups acceleration
accelerate accelerated time times timing timings space spaces memory memories word words bit bits
byte bytes input inputs output outputs query queries answer answers answering oracle oracles black
box black-box white white-box key keys keyed security secure insecure attack attacks attacking
attacker attackers adversary adversaries adversarial break breaks breaking broke broken brokenness
win wins won winning lose loses lost losing loser losers'''.split())

def tokens(c):
    text = ' '.join([c['name'], c['one_sentence_mechanism'], c.get('semantic_fingerprint_raw', '')])
    text = re.sub(r'[*_`#|()\[\]{}/\\:;,.=+^$%~!?<>"]', ' ', text.lower())
    toks = [t for t in re.split(r'\s+', text) if len(t) >= 4 and t not in STOP and not t.isdigit()]
    return set(toks)

sigs = [tokens(c) for c in batch]
df = Counter()
for s in sigs:
    df.update(s)
rare = {t for t, n in df.items() if 2 <= n <= 40}

# edges
parent = list(range(len(batch)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb

for i in range(len(batch)):
    ri = sigs[i] & rare
    for j in range(i + 1, len(batch)):
        shared = ri & (sigs[j] & rare)
        if len(shared) >= 2:
            union(i, j)

clusters = defaultdict(list)
for i in range(len(batch)):
    clusters[find(i)].append(i)

def short(c):
    f = c['source_file'].split('/')[-1].replace('idea_generation_', 'ig').replace('.md', '')
    return f"{f}:{c['label']}"

multi = [sorted(v) for v in clusters.values() if len(v) >= 2]
multi.sort(key=lambda v: -len(v))
print(f"clusters with >=2 members: {len(multi)}")
for cl in multi:
    members = [batch[i] for i in cl]
    files = {m['source_file'].split('/')[-1] for m in members}
    shared_all = set.intersection(*[sigs[i] & rare for i in cl]) if cl else set()
    print(f"\n=== cluster size {len(cl)} across {len(files)} files ===")
    print('shared tokens:', sorted(shared_all)[:14])
    for m in members:
        print('   ', short(m), '|', m['name'][:85])
