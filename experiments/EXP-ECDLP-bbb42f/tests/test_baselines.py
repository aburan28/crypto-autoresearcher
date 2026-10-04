import sys, time, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.sampler import sample_unplanted_curves
from driver.baselines import pollard_rho_negation, bsgs_dlp
from driver.ecc import scalar_mult, random_point

for bits in (20, 24, 28):
    p, accepted, tally, attempts = sample_unplanted_curves(bits, master_seed=999, count=1, k_max=6)
    c = accepted[0]
    a, b, N = c["a"], c["b"], c["N"]
    rng = random.Random(bits)
    P = random_point(a, b, p, rng)
    # ensure P generates G (N prime, P != O) -> ord(P) = N
    k_true = rng.randrange(1, N)
    Q = scalar_mult(k_true, P, a, p)

    t0 = time.time()
    k_bsgs, ctr_b, m = bsgs_dlp(P, Q, a, N, p)
    dt_bsgs = time.time() - t0
    ok_bsgs = (k_bsgs == k_true)

    t0 = time.time()
    k_rho, steps, ctr_r = pollard_rho_negation(P, Q, a, N, p, random.Random(bits + 1))
    dt_rho = time.time() - t0
    ok_rho = (k_rho == k_true) or (k_rho is not None and scalar_mult(k_rho, P, a, p) == Q)

    import math
    sqrtN = math.isqrt(N)
    print(f"bits={bits} N={N} BSGS: ok={ok_bsgs} time={dt_bsgs:.2f}s mults={ctr_b.field_mults} m={m} (2*sqrt(N)~{2*sqrtN})")
    print(f"          RHO: ok={ok_rho} time={dt_rho:.2f}s steps={steps} (0.886*sqrt(N)~{int(0.886*sqrtN)}) k_rho={k_rho} k_true={k_true}")
