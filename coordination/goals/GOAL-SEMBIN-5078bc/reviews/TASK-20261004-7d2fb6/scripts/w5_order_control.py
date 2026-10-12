#!/usr/bin/env python3
"""w5_order_control.py -- joint W5 (1): is the within-degree tie-break of the monomial ORDER load-bearing, and would the statement-vs-code comparison notice a wrong one?
Run the production closure on the system with its variable indices reversed (x_i <-> x_{N-1-i}) -- the same system under the opposite within-degree tie-break --
map the leading monomials back, and compare with the reference closure of the ORIGINAL system under the statement's ORDER. The subspace W_D is order-independent
(the budget uses only deg f, the size of the leading monomial), so the ranks must agree; the leading-monomial sets and standard-monomial counts need not.
Usage: w5_order_control.py STEM..."""
import sys, os, json
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts")
import vclos
c = vclos.Clos(f"{W}/build/libclosure_orig.so")
def rev(m, N): return int(format(m, f"0{N}b")[::-1], 2)
for stem in sys.argv[1:]:
    s = json.load(open(f"{W}/inst/{stem}.json")); N = s["N"]; V = s["V"]
    st = dict(kv.split("=") for kv in open(f"{W}/ref/{stem}.D4.stats").read().split())
    ref_lm = [int(x) for x in open(f"{W}/ref/{stem}.D4.lm").read().split()]
    ref_rank, ref_std = int(st["rank"]), int(st["std"])
    a = c.run(N, 4, s["equations"], mem_cap_gb=1.0)                                        # as generated
    b = c.run(N, 4, [[rev(m, N) for m in e] for e in s["equations"]], mem_cap_gb=1.0)     # variables reversed
    lm_back = sorted(rev(m, N) for m in b["lm"])
    print(f"{stem:28s} N={N} V={V} | statement-ORDER reference: rank {ref_rank} std {ref_std} | production as generated: rank {a['rank']} std {a['std']} LM set equals reference: {sorted(a['lm'])==sorted(ref_lm)} "
          f"| reversed tie-break: rank {b['rank']} std {b['std']} LM set (mapped back) equals reference: {lm_back==sorted(ref_lm)}  |LM symmetric difference| = {len(set(lm_back) ^ set(ref_lm))}", flush=True)
