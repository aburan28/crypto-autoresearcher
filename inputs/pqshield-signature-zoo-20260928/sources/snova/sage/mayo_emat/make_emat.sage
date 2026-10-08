# Uses parts of MAYO's sage implementation

if True:
    # MAYO-1

    v = 78
    o = 8
    q = 16
    l = 1
    aes = True
    r = 10
    m1 = 78
    m2 = o * l * r
    RANDOM_E = False

else:
    # SNOVA_24_5_23_4

    v = 24
    o = 5
    q = 23
    l = 4
    aes = False
    r = l
    m1 = o
    m2 = o * l * r
    RANDOM_E = False

# Set GF

GF_q = GF(q, 'x')
x = GF_q.gen()

if q == 16:
    def from_int(x): return GF_q.from_integer(x)
    def to_int(x): return x.to_integer()
else:
    def from_int(x): return x
    def to_int(x): return int(x)


# Compose emat

emati = [[[[[0 for _ in range(r**2)] for _ in range(m2)] for a in range(l)] for b in range(l)] for mi in range(m1)]

emat_d = {}
for mi in range(m1):
    for i1 in range(r):
        for j1 in range(r):
            p_test = [[[matrix(GF_q, r, r, lambda i, j: 1 if mi == mj and i == i1 and j == j1 else 0)
                        for a in range(l)] for b in range(l)] for mj in range(m1)]

            # MAYO emulsifier
            R = GF_q['z']
            z = R.gen()
            f = z**78 + z**2 + z + x**3
            fx = R.quotient_ring(f)

            y = vector(GF_q, m1)
            ell = 0
            for i in range(r):
                for j in range(r-1, i-1, -1):
                    # convert to polynomial
                    u2 = fx(list([p_test[mj][0][0][i][j] if i == j else p_test[mj][0][0][i][j] + p_test[mj][0][0][j][i]
                                  for mj in range(m1)]))

                    # y <- y + E^(ell) * u
                    y = y + vector(z**ell * u2)

                    # ell <- ell + 1
                    ell = ell + 1

            emat_d[(mi, i1, j1)] = list(y)

            for mj in range(m1):
                emati[mi][0][0][mj][i1 * r + j1] = to_int(y[mj])

print('mayo1 =', emati)
