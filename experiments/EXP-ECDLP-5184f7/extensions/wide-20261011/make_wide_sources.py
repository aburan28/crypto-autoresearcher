#!/usr/bin/env python3
"""Materialize a separate prospective extension without editing frozen baseline sources."""
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path('/workspace/solinas-run/experiments/EXP-ECDLP-5184f7')
OUT = BASE / 'extensions/wide-20261011'
OUT.mkdir(parents=True, exist_ok=False)
SRC = OUT / 'implementation'
SRC.mkdir()
for name in ['common.py', 'finite_math.py', 'curve_identity.py', 'GPL-2.txt', 'attack.cpp', 'arithmetic.py', 'run_attacks.py', 'prepare.py']:
    shutil.copyfile(BASE / 'implementation' / name, SRC / name)


def replace(text, old, new):
    assert old in text, old
    return text.replace(old, new)


p = SRC / 'prepare.py'
t = p.read_text()
t = replace(t, "anchors = plan['exact_anchor_cohort']['anchors']", "anchors = []\n    sampling_bits = plan['bit_strata']")
t = replace(t, "all_bits = sorted({24, 28, 32} | {a['p_bits'] for a in anchors})", "all_bits = sampling_bits")
t = replace(t, "used = {int(a['p']) for a in anchors}", "used = set(plan['excluded_baseline_moduli'])")
t = replace(t, "for bits in [24, 28, 32]:", "for bits in sampling_bits:")
t = replace(t, "if len(available) < 12:", "if len(available) < 18:")
t = replace(t, "for _ in range(4):", "for _ in range(6):")
t = replace(t, "for arm in ['S', 'R', 'C']:", "for arm in ['S', 'R1', 'R2', 'C1', 'C2']:")
t = replace(t, "arm == 'C' and q % 12 != p % 12", "arm.startswith('C') and q % 12 != p % 12")
t = replace(t, "desired = 512 if modulus['attack_eligible'] else 32", "desired = 1024 if modulus['attack_eligible'] else 128")
t = replace(t, "not 16 <= ell.bit_length() <= 26", "not 16 <= ell.bit_length() <= 28")
t = replace(t, '<512*log(1.1)', '<1024*log(1.1)')
t = replace(t, "sr, er = matching(eligible['S'], eligible['R'])\n        sc, ec = matching(eligible['S'], eligible['C'])\n        selected = sorted(set(sr) & set(sc))[:8]\n        match_logs.append({'block': block['block'], 'S_R_matches': sr, 'S_C_matches': sc,\n                           'S_R_edges': er, 'S_C_edges': ec, 'selected_S_indices': selected,\n                           'candidate_counts': {k: len(v) for k, v in eligible.items()}})\n        for slot, idx in enumerate(selected):\n            for arm, candidate in [('S', idx), ('R', sr[idx]), ('C', sc[idx])]:\n                groups.append(make_group(curves[ms[arm]['id']][candidate], ms[arm], slot))", "pairs, edges = {}, {}\n        for arm in ['R1', 'R2', 'C1', 'C2']:\n            pairs[arm], edges[arm] = matching(eligible['S'], eligible[arm])\n        selected = sorted(set.intersection(*(set(v) for v in pairs.values())))[:8]\n        match_logs.append({'block': block['block'], 'matches': pairs, 'edges': edges,\n                           'selected_S_indices': selected, 'candidate_counts': {k: len(v) for k, v in eligible.items()}})\n        if len(selected) != 8:\n            raise RuntimeError('Fixed pool lacks eight common five-arm matches; retain all outputs and report incomplete scope')\n        for slot, idx in enumerate(selected):\n            for arm, candidate in [('S', idx)] + [(arm, pairs[arm][idx]) for arm in pairs]:\n                groups.append(make_group(curves[ms[arm]['id']][candidate], ms[arm], slot))")
# The second bit-stratum loop is in main; derive it from the loaded plan there.
t = replace(t, "plan = json.loads(args.plan.read_text())", "plan = json.loads(args.plan.read_text())\n    sampling_bits = plan['bit_strata']")
t = t.replace('/20261011', '/wide-20261011')
p.write_text(t)
p = SRC / 'run_attacks.py'
t = p.read_text().replace("for bits in [24, 28, 32]:", "for bits in sorted({g['bits'] for g in groups}):")
t = t.replace("g['slot']))[:2]", "g['slot']))[:4]")
assert "g['slot']))[:4]" in t
t = t.replace('/20261011', '/wide-20261011').replace('2026101108', '2026101128').replace('2026101109', '2026101129')
p.write_text(t)
p = SRC / 'arithmetic.py'
p.write_text(p.read_text().replace('/20261011', '/wide-20261011').replace('2026101110', '2026101130'))
baseline_sample = BASE / 'runs/RUN-ECDLP-a24605/preparation/prime-sample.json'
baseline = json.loads(baseline_sample.read_text())
contract = {'label': 'Prospective extension requested after completed baseline; no baseline observations pooled',
 'authorization': 'User requested wider sample, larger control and higher-confidence results for all prime studies',
 'bit_strata': [24, 28, 32, 36], 'primes_per_stratum': 18, 'total_S_primes': 72,
 'main_prime_sample': {'seeds': [2026101125, 2026101126, 2026101127], 'draws_per_seed_per_stratum': 6},
 'excluded_baseline_moduli': [m['p'] for m in baseline['moduli']],
 'excluded_baseline_sample_SHA256': hashlib.sha256(baseline_sample.read_bytes()).hexdigest(),
 'prime_family': 'Deduplicated prime integers p=2^b-2^a+s*2^c+t; 1<=c<a<=b-2; s,t in {-1,+1}',
 'control_arms': {'R1': 'fresh random prime, same bits and +/-1% p', 'R2': 'second independent R draw',
                 'C1': 'fresh random prime, same bits and +/-1% p and same p mod 12', 'C2': 'second independent C draw'},
 'global_uniqueness': True, 'primality': 'PARI isprime exact; every candidate and rejection retained',
 'curve_pool_per_modulus': 1024, 'unconditional_audit_per_modulus': 128,
 'matching': 'First 8 common S indices in maximum-cardinality/minimum-log-distance matchings to all four control arms; ell within 10%',
 'largest_subgroup_ell_bits': [16, 28], 'matched_groups_expected': 2880, 'targets_per_group': 4,
 'solver_seed_repetitions': 4, 'attacks': ['16-adding native rho', '16-adding opaque rho', '32-adding independent native rho', 'memory-accounted BSGS'],
 'primary_endpoint': 'Prime-block weighted log-ratio of mean restricted search group calls/sqrt(ell), S divided by pooled R1/R2, averaged over 8 matching slots',
 'secondary_endpoints': ['S versus pooled C1/C2', 'Opaque rho', '32-adding rho', 'BSGS', 'Unconditional subgroup-order proxy', 'Python arithmetic'],
 'confidence': {'marginal_level': .999, 'replicates': 500000, 'seed': 2026101131,
                'primary_bonferroni_level': 1-.001/3, 'reserved_primary_family_tests': 3,
                'method': 'Percentile whole-prime-block bootstrap within field-bit strata; approximate nominal coverage'},
 'stopping': 'All 72 fresh blocks, no outcome-driven extension; incomplete or infrastructure failures retained, no replacement primes after attack outcomes',
 'decision_rule': 'Similarity if 99.9% primary CI entirely inside [1/1.2,1.2]; higher generic work if lower endpoint >1.2; otherwise inconclusive',
 'tiny_positive_control': 'One small-prime group per field-bit stratum, complete-coverage BSGS instrument',
 'exact_control_jobs': 'First four S matched groups per bit stratum, all targets/seeds, sham/replay/transport; native isomorphism diagnostic',
 'scope': 'Toy conditional subgroup attacks; no claim for undefined P1-19/P2-4 or deployed prime sizes',
 'no_claim_promotion': True}
(OUT / 'contract.json').write_text(json.dumps(contract, indent=2)+'\n')
(OUT / 'measurement-boundary.json').write_text(json.dumps({'rho_cap': 'ceil(20*sqrt(ell)) = isqrt(400*ell)+1 for prime ell',
 'rho_horizon': 20, 'BSGS_M': 'min(4096,ceil(sqrt(ell)))', 'truth': 'Validation-only q excluded from public kernel job inputs',
 'setup_search_verification': 'Separate counters; primary counts search only; BSGS setup+search; timing is not a sealed bound',
 'resource_limit': 'One affine attack/arithmetic worker, 4 GiB AS, 600 seconds per block/worker; two preparation workers'},indent=2)+'\n')
(OUT / 'README.md').write_text('# Prospective wider Solinas comparison\n\nThis extension follows RUN-ECDLP-a24605 and excludes all its sampled moduli. It adds a 36-bit stratum, doubles the independent S prime count to 72, quadruples unconditional models per prime to 128, and uses four distinct random controls per S prime. The unchanged attack kernel counts setup/search/verification separately. Every family claim uses 99.9% marginal block-bootstrap intervals; a reserved three-family primary Bonferroni interval is also reported. Exact identities, incomplete matches and every raw result are retained. This is a toy experiment and does not define the requested P1-19/P2-4 names.\n\nSource changes and the contract are committed before any new prime selection or attack. Original sources and results are preserved.\n')
shutil.copyfile(__file__, OUT / 'make_wide_sources.py')
print(OUT)
