import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import walk_forward_chain
from driver.curve_order import compute_group_order
from driver.ecc import seeded_rng, random_point, scalar_mult
from driver.sssa import sssa_solve
from driver.predicates import classify

# small known anomalous curve from earlier test: p=1009, a=307, b=856, N=1009
p, a0, b0 = 1009, 307, 856
walk_rng = seeded_rng("chain-test")
chain = None
for attempt in range(50):
    try:
        chain = walk_forward_chain(a0, b0, p, chain_len=4, walk_rng=seeded_rng("chain-test", attempt))
        break
    except RuntimeError as e:
        print("dead end, retry:", e)
if chain is None:
    print("could not build chain")
    sys.exit(1)

print("chain length", len(chain))
for node in chain:
    print(node)

e_rand = chain[-1]
N_er, _, _ = compute_group_order(e_rand["a"], e_rand["b"], p, seeded_rng("verify-erand"))
print("E_rand N =", N_er, " (should equal origin N=1009, by Tate)")

cls = classify(N_er, p, 6)
print("E_rand classification:", cls)

# now solve DLP directly on E_rand via SSSA (since it's still anomalous)
rng = seeded_rng("dlp-test")
P = random_point(e_rand["a"], e_rand["b"], p, rng)
while P[1] == 0:
    P = random_point(e_rand["a"], e_rand["b"], p, rng)
k_true = 456
Q = scalar_mult(k_true, P, e_rand["a"], p)
k_computed, diag = sssa_solve(P[0], P[1], Q[0], Q[1], e_rand["a"], e_rand["b"], p)
print("k_true", k_true, "k_computed", k_computed, "OK", k_true == k_computed)
