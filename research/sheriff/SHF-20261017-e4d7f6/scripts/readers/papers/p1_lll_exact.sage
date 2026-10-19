# P1 independent check (Sage/PARI/fplll; shares no code with crypto:src).
# (1) Instance identity: the three 256-bit group orders equal #E(F_p) (SEA).
# (2) Exact-precision LLL (fplll via Sage) on the Boneh-Venkatesan basis as
#     written in the note (m = 8, k_bits = 3/4 n_bits), random planted d and
#     nonces, for every curve the note tabulates. If the secp256k1 failure were a
#     property of the curve (i.e. of n) and not of f64 arithmetic, it would show
#     here too.
import random as pyrandom

curves256 = {
    "secp256k1": (2**256 - 2**32 - 977, 0, 7,
                  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141),
    "P-256": (2**256 - 2**224 + 2**192 + 2**96 - 1, -3,
              0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
              0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551),
    "brainpoolP256r1": (0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
                        0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
                        0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
                        0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7),
}
print("== (1) #E(F_p) vs standard n ==")
for name, (p, a, b, n) in curves256.items():
    E = EllipticCurve(GF(p), [a, b])
    N = E.order()
    print(f"{name:16s} #E == n: {N == n}  n prime: {is_prime(n)}")

orders = {
    "secp192k1": 0xFFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D,
    "secp224k1": 0x010000000000000000000000000001DCE8D2EC6184CAF0A971769FB1F7,
    "secp256k1": curves256["secp256k1"][3],
    "P-256": curves256["P-256"][3],
    "brainpoolP256r1": curves256["brainpoolP256r1"][3],
    "P-384": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
    "brainpoolP384r1": 0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565,
    "P-521": 6864797660130609714981900799081393217269435300143305409394463459185543183397655394245057746333217197532963996371363321113864768612440380340372808892707005449,
}


def hnp_trial(n, m, kb, rng):
    n = int(n); m = int(m); kb = int(kb)
    d = rng.randrange(1, n)
    a = [rng.randrange(1, n) for _ in range(m)]
    k = [rng.randrange(1, 2**kb) for _ in range(m)]
    t = [(k[i] - d * a[i]) % n for i in range(m)]          # d*a_i + t_i = k_i (mod n)
    rows = []
    for i in range(m):
        r = [0] * (m + 2); r[i] = n * n; rows.append(r)
    rows.append([n * x for x in a] + [2**kb, 0])
    rows.append([n * x for x in t] + [0, n * 2**kb])
    L = matrix(ZZ, rows).LLL(delta=0.75)
    for row in L.rows():
        if abs(row[m + 1]) == n * 2**kb:
            s = 1 if row[m + 1] > 0 else -1
            cand = (s * row[m]) // 2**kb
            if (s * row[m]) % 2**kb == 0 and cand % n == d:
                return True
    return False


print("\n== (2) exact-precision LLL (fplll), m = 8, k_bits = 3/4 n_bits, delta = 0.75 ==")
rng = pyrandom.Random(int(20261017))
TRIALS = 5
for name, n in orders.items():
    nb = int(Integer(n).nbits())
    kb = 3 * nb // 4
    ok = sum(hnp_trial(n, 8, kb, rng) for _ in range(TRIALS))
    print(f"{name:16s} n_bits={nb} k_bits={kb}: recovered {ok}/{TRIALS}")

# Negative control: too little bias (k_bits = n_bits - 8): the lattice should NOT reveal d.
print("\n== negative control: k_bits = n_bits - 8 (8 known bits per nonce, 64 bits total < n_bits) ==")
for name in ("secp256k1", "P-256"):
    n = orders[name]
    nb = int(Integer(n).nbits())
    ok = sum(hnp_trial(n, 8, nb - 8, rng) for _ in range(TRIALS))
    print(f"{name:16s} k_bits={nb-8}: recovered {ok}/{TRIALS}")
