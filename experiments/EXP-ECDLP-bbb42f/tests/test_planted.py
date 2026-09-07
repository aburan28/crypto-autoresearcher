import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import construct_planted_instance
from driver.predicates import classify

for bits in (20, 24, 28):
    t0 = time.time()
    inst = construct_planted_instance(bits, master_seed=20260902004, chain_len=6, k_max=6)
    dt = time.time() - t0
    p = inst["p"]
    er = inst["e_rand"]
    cls_special = classify(inst["special_curve"]["N"], p, 6)
    print(f"bits={bits} p={p} special_N={inst['special_curve']['N']} chain_len={inst['chain_len']} "
          f"forward_degree={inst['forward_degree']} restarts={inst['restarts_used']} time={dt:.3f}s "
          f"E_rand=({er['a']},{er['b']}) special_cls={cls_special['e1_anomalous']}")
