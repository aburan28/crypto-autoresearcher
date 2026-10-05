#!/usr/bin/env python3
"""Collects the small-N validation counts of the instrument from the logs in results/logs_small and results/*.json into results/small_n_validation_summary.json."""
import os, re, json, glob
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
L = os.path.join(OUT, 'results', 'logs_small')
def read(p): return open(os.path.join(OUT, p)).read()
s = {}
s['parser_tests'] = dict(log='results/logs_small/test_parser.log', passed=read('results/logs_small/test_parser.log').count('PASS '), failed=int(re.search(r'FAILS (\d+)', read('results/logs_small/test_parser.log')).group(1)))
t = read('results/logs_small/test_counters.log'); m = re.search(r'tests (\d+) fails (\d+)', t)
s['zero_counters_vs_bruteforce'] = dict(log='results/logs_small/test_counters.log', tests=int(m.group(1)), fails=int(m.group(2)), note='modes A and C, both role assignments, vs brute force; incl. a hand-checkable system')
s['parse_vs_python_eval_on_the_twelve_files'] = dict(log='results/logs_small/check_parse_vs_python.log', mismatches=sum(int(x) for x in re.findall(r'eval mismatches vs python-eval (\d+)', read('results/logs_small/check_parse_vs_python.log'))))
diffs = {}
for name in ['diff_c_vs_ref_8_12', 'diff_c_vs_ref_13_16', 'diff_c_vs_ref_17_19', 'diff_c_vs_c2_14_22', 'diff_n23_24']:
    t = read('results/logs_small/%s.log' % name); m = re.search(r'tests (\d+) fails (\d+)', t)
    diffs[name] = dict(tests=int(m.group(1)), fails=int(m.group(2)), log='results/logs_small/%s.log' % name)
s['implementation_diffs'] = diffs
s['implementation_diffs_note'] = ('closure.c (with and without early exit) vs plain Python reference (N 8-19), and vs closure2.c literal passes and incremental (N 14-24); identical LM files, rank and N_std required; '
                                  'the reference additionally checks its own saturation and the evaluation-kernel bound LM(W) subset LM(I<=4) for N<=16')
gt = json.load(open(os.path.join(OUT, 'results', 'w1_ground_truth_10_17.json')))
s['w1_ground_truth_vs_closure'] = dict(json='results/w1_ground_truth_10_17.json', systems=len(gt['records']), violations_LM_W_not_in_LM_I_or_rank_bound=len(gt['violations']), table=gt['table'])
s['polarity_check'] = dict(log='results/logs_small/polarity_check.log', text=read('results/logs_small/polarity_check.log').strip())
s['identity_check'] = dict(log='results/logs_small/identity_check.log', text=read('results/logs_small/identity_check.log').strip())
s['order_experiments'] = {n: read('results/logs_small/%s.log' % n).split('\n')[0:2] for n in ['order_9_12', 'order_13_16', 'order_14_18']}
fs = json.load(open(os.path.join(OUT, 'results', 'order_flip_search.json')))
fc = json.load(open(os.path.join(OUT, 'results', 'order_flip_closure.json')))
s['order_flip_search_closure_free'] = dict(json='results/order_flip_search.json', systems=fs['tested'], systems_whose_GB_degree_le4_differs_between_admissible_orders=len(fs['flips']), signature_histogram=fs['hist'])
s['order_flip_closure_level'] = dict(json='results/order_flip_closure.json', flip_systems_run=len(fc), closure_verdict_flips=sum(1 for x in fc if x['closure_verdict_flips']))
json.dump(s, open(os.path.join(OUT, 'results', 'small_n_validation_summary.json'), 'w'), indent=1)
print(json.dumps(s, indent=1)[:3500])
