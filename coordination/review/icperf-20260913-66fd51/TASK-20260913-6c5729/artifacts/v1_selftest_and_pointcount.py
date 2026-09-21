"""Self-test of val_gf2n.py and brute-force #E(F_{2^n}) for the shipped curve
at n = 15, 17, 19 (validator's own arithmetic; V1 instrument check and the
V6 cross-check against the Frobenius recursion). Seconds of one core."""
import json, os, random, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from val_gf2n import GF2n, BinaryCurve, decode_le

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
INFO = {15: "INFOn15l5-1-S.dimacs", 17: "INFOn17l6-1-S.dimacs", 19: "INFOn19l6-1-S.dimacs"}

out = {}
for n, fn in INFO.items():
    lines = open(os.path.join(BENCH, fn)).read().split("\n")
    F = GF2n.from_info_modulus(n, lines[1])
    # every INFO file of the cell must carry the same modulus
    same = True
    for f in os.listdir(BENCH):
        if f.startswith(f"INFOn{n}l"):
            if open(os.path.join(BENCH, f)).read().split("\n")[1].strip() != lines[1].strip():
                same = False
    rng = random.Random(1)
    # field axiom spot checks
    for _ in range(300):
        x, y, z = (rng.getrandbits(n) for _ in range(3))
        assert F.mul(x, y) == F.mul(y, x)
        assert F.mul(F.mul(x, y), z) == F.mul(x, F.mul(y, z))
        assert F.mul(x, y ^ z) == F.mul(x, y) ^ F.mul(x, z)
        if x:
            assert F.mul(x, F.inv(x)) == 1
        assert F.trace(x) == F.trace_slow(x)
        assert F.sq(x) == F.pow(x, 2)
        assert F.pow(x, 1 << n) == x  # Frobenius x^(2^n) = x
    # a generates F* iff its order is 2^n - 1 (Conway polynomials are primitive)
    N = F.order
    exp = [0] * N
    log = [-1] * (1 << n)
    g = 1
    for i in range(N):
        exp[i] = g
        log[g] = i
        g <<= 1
        if (g >> n) & 1:
            g ^= F.mod
    assert g == 1, "a^(2^n-1) != 1"
    assert all(v >= 0 for v in log[1:]), "a is not primitive: log table not full"
    # curve x-criterion vs direct root finding on 2000 random x
    E = BinaryCurve(F, a2=1, a6=1)
    for _ in range(2000):
        x = rng.getrandbits(n)
        ys = E.ys(x)
        if x == 0:
            assert ys == [1]
        else:
            assert (len(ys) == 2) == (E.x_criterion(x) == 0)
            assert (len(ys) == 0) == (E.x_criterion(x) == 1)
    # brute-force point count: O, (0,1), and 2 points per nonzero x with Tr(x + 1 + x^-2) = 0
    t0 = time.time()
    cnt_on = 0
    cnt_tw = 0
    tm = F.trmask
    for lx in range(N):
        x = exp[lx]
        inv2 = exp[(-2 * lx) % N]  # x^-2
        c = x ^ 1 ^ inv2
        if bin(c & tm).count("1") & 1 == 0:
            cnt_on += 1
        else:
            cnt_tw += 1
    n_points = 2 + 2 * cnt_on
    n_twist_points = 2 + 2 * cnt_tw  # twist E': a2 = 0 has the complementary x set, plus O and (0,1)
    dt = time.time() - t0
    # sanity: group-law check, random points P,Q: (P+Q)-Q = P, and order divides #E
    for _ in range(20):
        while True:
            x = rng.getrandbits(n)
            ys = E.ys(x)
            if ys:
                break
        P = (x, ys[0])
        while True:
            x2 = rng.getrandbits(n)
            ys2 = E.ys(x2)
            if ys2:
                break
        Q = (x2, ys2[rng.randrange(len(ys2))])
        assert E.add(E.add(P, Q), E.neg(Q)) == P
        # [#E]P == O via double-and-add
        R = None
        A = P
        k = n_points
        while k:
            if k & 1:
                R = E.add(R, A)
            A = E.add(A, A) if A is not None else None
            k >>= 1
        assert R is None, "[#E]P != O: point count or group law wrong"
    out[n] = {
        "modulus": F.modulus_str(), "modulus_info_string": lines[1].strip(),
        "all_INFO_files_of_cell_share_modulus": same,
        "a_is_primitive": True,
        "count_x_nonzero_on_E": cnt_on, "count_x_nonzero_on_twist": cnt_tw,
        "E_points_bruteforce": n_points, "twist_points_bruteforce": n_twist_points,
        "sum_check_E_plus_twist_equals_2q_plus_2": n_points + n_twist_points == 2 * (1 << n) + 2,
        "bruteforce_seconds": round(dt, 2),
        "group_law_random_checks": "20 x ((P+Q)-Q = P and [#E]P = O) passed",
    }
    print(n, out[n])
json.dump(out, open(os.path.join(os.path.dirname(__file__), "v1_selftest_pointcount.json"), "w"), indent=1)
print("SELFTEST_OK")
