import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.sampler import sample_unplanted_curves
from driver.graph_search import bounded_isogeny_search, degree_budget_steps

for bits in (20, 24):
    t0 = time.time()
    p, accepted, tally, attempts = sample_unplanted_curves(bits, master_seed=20260902001, count=3, k_max=6)
    print(f"bits={bits} p={p} sampled {len(accepted)} curves in {time.time()-t0:.2f}s attempts={attempts} tally={tally}")
    for c in accepted:
        max_steps = degree_budget_steps(c["N"])
        t1 = time.time()
        res = bounded_isogeny_search(c["a"], c["b"], p, c["N"], k_max=6, max_steps=max_steps, max_nodes=50000, time_budget_seconds=60)
        dt = time.time() - t1
        print(f"  curve a={c['a']} b={c['b']} N={c['N']} max_steps={max_steps} -> status={res['status']} nodes={res['nodes_visited']} depth={res['max_depth_reached']} crater_closed={res['crater_closed']} time={dt:.2f}s")
