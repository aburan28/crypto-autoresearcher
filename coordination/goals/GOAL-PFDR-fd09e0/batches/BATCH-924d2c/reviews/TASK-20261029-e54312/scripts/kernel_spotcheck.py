"""J2b(2): adversarial inputs for the bound kernel labelsum.c against reviewer-written counters.

The kernel is compiled exactly as run.py build_kernel does (gcc -O2 -std=c11 -o <exe> labelsum.c) into a
scratch directory, never into implementation/. Input format as run.py run_kernel: "p" then one line
"n l_1 ... l_n" per set; output "n pairs C D" per set. Reviewer counters: A = numpy sort/run-length,
P = pure-Python dict (ownec.dict_count), and closed forms where the set has one (arithmetic progressions).

usage: python3 -I -B kernel_spotcheck.py <repo-root> <scratch-dir> <out.json>
"""
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownec  # noqa: E402

repo, scratch, out_path = sys.argv[1:4]
src = os.path.join(repo, "experiments/EXP-PFDR-bb0d26/implementation/labelsum.c")
os.makedirs(scratch, exist_ok=True)
exe = os.path.join(scratch, "labelsum")
cc = subprocess.run(["gcc", "-O2", "-std=c11", "-o", exe, src], capture_output=True, text=True)
assert cc.returncode == 0, cc.stderr


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def kernel(p, sets):
    lines = [str(p)] + [f"{len(s)} " + " ".join(map(str, s)) for s in sets]
    pr = subprocess.run([exe], input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=3600)
    if pr.returncode != 0:
        return pr.returncode, pr.stderr.strip(), None
    return 0, "", [tuple(map(int, ln.split())) for ln in pr.stdout.strip().splitlines()]


def count_A(labels, p):
    x = np.asarray(labels, dtype=np.int64)
    n = len(x)
    if n < 2:
        return 0, 0
    iu, ju = np.triu_indices(n, k=1) if n <= 1024 else (None, None)
    if iu is not None:
        s = x[iu] + x[ju]
    else:
        s = np.concatenate([x[i] + x[i + 1:] for i in range(n - 1)])
    s = np.where(s >= p, s - p, s)
    s.sort()
    cut = np.flatnonzero(s[1:] != s[:-1]) + 1
    L = np.diff(np.concatenate(([0], cut, [len(s)])))
    return int((L * (L - 1) // 2).sum()), int(len(L))


def ap_closed_form(n):
    """C and D of an n-term AP x0 + k w (p prime > 2n): sums depend on t = i + j only, all distinct mod p."""
    C = 0
    for t in range(1, 2 * n - 2):
        m = (t + 1) // 2 - max(0, t - n + 1)
        C += m * (m - 1) // 2
    return C, 2 * n - 3


def prev_prime(n):
    n -= 1
    while not ownec.is_prime(n):
        n -= 1
    return n


rng = random.Random("TASK-20261029-e54312|J2b|kernel")       # reviewer seed, recorded
P20, P24, P28, P31 = prev_prime(1 << 20), prev_prime(1 << 24), prev_prime(1 << 28), prev_prime(1 << 31)
cases = []


def run_case(name, p, sets, expect=None, use_dict=True):
    t0 = time.time()
    rc, err, got = kernel(p, sets)
    ent = {"name": name, "p": p, "set_sizes": sorted(set(len(s) for s in sets)), "sets": len(sets), "kernel_exit": rc}
    if rc != 0:
        ent.update(result="kernel_error", stderr=err)
        cases.append(ent)
        return
    ok = len(got) == len(sets)
    rows = []
    for k, s in enumerate(sets):
        n = len(s)
        A = count_A(s, p)
        P = ownec.dict_count(s, p) if (use_dict and n <= 4096) else None
        E = expect[k] if expect else None
        kn, kp, kC, kD = got[k]
        row_ok = (kn == n and kp == n * (n - 1) // 2 and (kC, kD) == A and (P is None or P == A)
                  and (E is None or E == A))
        ok &= row_ok
        if len(sets) <= 4 or not row_ok:
            rows.append({"n": n, "kernel": [kC, kD], "A_sort": list(A), "P_dict": list(P) if P else None,
                         "closed_form": list(E) if E else None, "agree": row_ok})
    ent.update(result="agree" if ok else "MISMATCH", rows=rows, seconds=round(time.time() - t0, 2),
               set_sha256=[ownec.set_digest(s) for s in sets][:4])
    cases.append(ent)


# (1) arithmetic progressions with closed-form C, D (including wrap-around of terms and sums mod p)
for p in (P20, P28, P31):
    for n in (256, 1024, 4096):
        x0, w = rng.randrange(p), rng.randrange(1, p)
        s = [(x0 + k * w) % p for k in range(n)]
        run_case(f"AP n={n} random x0,w", p, [s], [ap_closed_form(n)], use_dict=(n <= 1024))
# (2) packed sets [p - n, p): every pair sum wraps around p; also an AP, closed form applies
for p in (P20, P28, P31):
    for n in (256, 4096):
        run_case(f"packed [p-n,p) n={n}", p, [list(range(p - n, p))], [ap_closed_form(n)], use_dict=(n <= 256))
# (3) symmetric sets {x, -x}: m_0 = n/2 at least (checked with the histogram of counter A)
sym_m0 = []
for p in (P20, P28, P31):
    for n in (256, 4096):
        half = set()
        while len(half) < n // 2:
            x = rng.randrange(1, p)
            if x not in half and (p - x) not in half and 2 * x != p:
                half.add(x)
        s = sorted(half) + [p - x for x in sorted(half)]
        rng.shuffle(s)
        xs = np.asarray(s, dtype=np.int64)
        tot = np.concatenate([xs[i] + xs[i + 1:] for i in range(n - 1)])
        tot = np.where(tot >= p, tot - p, tot)
        m0 = int(np.count_nonzero(tot == 0))
        sym_m0.append({"p": p, "n": n, "m_0": m0, "expected_m_0": n // 2, "equal": m0 == n // 2})
        run_case(f"symmetric {{x,-x}} n={n}", p, [s], [None], use_dict=(n <= 256))
# (4) random sets at n = 4096 near 2^20, 2^24, 2^28 and 2^31 (two each, one kernel call each)
for p in (P20, P24, P28, P31):
    sets = [rng.sample(range(p), 4096) for _ in range(2)]
    run_case("random n=4096 x2", p, sets, None, use_dict=False)
# (5) driver pattern: 21 sets in one call (20 null-like + 1), no state leaks between sets
for p in (P24, P31):
    sets = [rng.sample(range(p), 512) for _ in range(21)]
    run_case("21 random n=512 sets in one call", p, sets, None, use_dict=True)
# (6) small edge cases and the selftest hand set
run_case("edge n=1,2,3 with labels 0 and p-1", P31, [[0], [0, P31 - 1], [0, 1, P31 - 1]], None)
run_case("saturated sumset p=1009 n=200", 1009, [rng.sample(range(1009), 200)], None)
run_case("hand set 1,2,4,6,8,16 (one coincidence)", 1009, [[1, 2, 4, 6, 8, 16]], [(1, 14)])
run_case("whole field p=1009 n=1009: m_s = (p-1)/2 for every s", 1009, [list(range(1009))],
         [(1009 * math.comb(504, 2), 1009)])

# (7) input guards: out-of-range input must fail loudly (exit 2), never return a count
guards = []
for name, p, sets in (("p = 2^31", 1 << 31, [[1, 2]]), ("label >= p", 1009, [[1, 1009]]),
                      ("n > 8192", P31, [list(range(8193))])):
    rc, err, got = kernel(p, sets)
    guards.append({"name": name, "exit": rc, "stderr": err, "rejected": rc == 2})

ok_all = all(c["result"] == "agree" for c in cases) and all(g["rejected"] for g in guards) and all(s["equal"] for s in sym_m0)
out = {"script": "scripts/kernel_spotcheck.py", "python": sys.version, "executable": sys.executable,
       "numpy": np.__version__, "kernel_source": "experiments/EXP-PFDR-bb0d26/implementation/labelsum.c",
       "kernel_source_sha256": sha(src), "compile": ["gcc", "-O2", "-std=c11", "-o", "<scratch>/labelsum", "labelsum.c"],
       "gcc": subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
       "binary_sha256_not_staged": sha(exe), "primes": {"P20": P20, "P24": P24, "P28": P28, "P31": P31},
       "rng_seed": "random.Random('TASK-20261029-e54312|J2b|kernel')",
       "cases": cases, "symmetric_m0": sym_m0, "input_guards": guards,
       "summary": {"cases": len(cases), "sets": sum(c["sets"] for c in cases),
                   "mismatches": [c["name"] for c in cases if c["result"] != "agree"],
                   "guards_rejected": sum(g["rejected"] for g in guards), "all_agree": ok_all}}
with open(out_path, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps(out["summary"]), json.dumps(guards))
