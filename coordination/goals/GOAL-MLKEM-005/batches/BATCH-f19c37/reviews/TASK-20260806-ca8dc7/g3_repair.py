import numpy as np
rng = np.random.default_rng(11); NDRAW = 8; TR = 200_000
def cell_fail(kfac, n_flat, dz=4.0, trials=TR):
    steps = np.array([0.0]*n_flat + [-dz]*(12-n_flat)); f=0
    for _ in range(trials):
        x = rng.standard_normal((steps.size, NDRAW)) + steps[:, None]
        D = x.mean(1); SE = x.std(1, ddof=1)/np.sqrt(NDRAW)
        if np.any(D > kfac*SE): f += 1
    return f/trials
print("tolerance k x SE_step   ->  P(cell FAIL) / P(overall FAIL over 4 cells), perfect instrument")
for k in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0):
    r3 = cell_fail(k, 3); r4 = cell_fail(k, 4)
    print("  k = %.1f : n_flat=3  cell %.4f overall %.4f   |  n_flat=4  cell %.4f overall %.4f"
          % (k, r3, 1-(1-r3)**4, r4, 1-(1-r4)**4))
