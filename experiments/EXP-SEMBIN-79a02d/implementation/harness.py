"""EXP-SEMBIN-79a02d -- Python glue: write generator files, call the C arms
and the E2 enumerator, and a small pure-Python reference (big-int XOR basis)
used only in development tests."""
import json, os, subprocess, resource
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))


def write_gens(path, polys, N):
    with open(path, "w") as f:
        f.write(f"N {N}\n")
        for p in polys:
            f.write(" ".join(format(m, "x") for m in sorted(p)) + "\n")


def _limit(mem_bytes):
    def f():
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return f


def run_tool(args, timeout, mem_bytes=7 * 2**30):
    p = subprocess.run([os.path.join(HERE, args[0])] + [str(a) for a in args[1:]],
                       capture_output=True, text=True, timeout=timeout,
                       preexec_fn=_limit(mem_bytes))
    if p.returncode != 0:
        raise RuntimeError(f"{args[0]} rc={p.returncode} stderr={p.stderr[-500:]}")
    return json.loads(p.stdout)


# ---------------- pure-Python reference (dev tests only)
def ref_mono_list(N, D):
    out = []
    for d in range(D, -1, -1):
        for c in combinations(range(N), d):
            m = 0
            for v in c:
                m |= 1 << v
            out.append(m)
    return out


def ref_mul(f, m):
    s = {}
    for t in f:
        s[t | m] = s.get(t | m, 0) ^ 1
    return {k for k, v in s.items() if v}


def ref_rank(rows_as_sets, cols):
    idx = {m: i for i, m in enumerate(cols)}
    piv = {}
    for r in rows_as_sets:
        v = 0
        for m in r:
            v ^= 1 << (len(cols) - 1 - idx[m])
        while v:
            lb = v.bit_length() - 1
            if lb in piv:
                v ^= piv[lb]
            else:
                piv[lb] = v
                break
    return len(piv), piv


def ref_mac(polys, N, D):
    cols = ref_mono_list(N, D)
    rows = []
    for f in polys:
        df = max(bin(m).count("1") for m in f)
        if df > D:
            continue
        for s in range(D - df + 1):
            for c in combinations(range(N), s):
                m = 0
                for v in c:
                    m |= 1 << v
                p = ref_mul(f, m)
                if p:
                    rows.append(p)
    r, _ = ref_rank(rows, cols)
    return len(rows), r


def ref_closure(polys, N, D):
    cols = ref_mono_list(N, D)
    ncol = len(cols)
    idx = {m: i for i, m in enumerate(cols)}
    piv = {}
    def ins(p):
        v = 0
        for m in p:
            v ^= 1 << (ncol - 1 - idx[m])
        while v:
            lb = v.bit_length() - 1
            if lb in piv:
                v ^= piv[lb]
            else:
                piv[lb] = v
                return True
        return False
    for f in polys:
        for s in range(D + 1):
            for c in combinations(range(N), s):
                m = 0
                for v in c:
                    m |= 1 << v
                p = ref_mul(f, m)
                if p and max(bin(t).count("1") for t in p) <= D:
                    ins(p)
    # low region: columns with degree <= D-1 ; in bit positions (ncol-1-idx) small
    lowcols = [i for i, m in enumerate(cols) if bin(m).count("1") <= D - 1]
    lowbits = {ncol - 1 - i for i in lowcols}
    done = set()
    it = 0
    while True:
        todo = [lb for lb in piv if lb in lowbits and lb not in done]
        if not todo:
            break
        before = len(piv)
        for lb in todo:
            done.add(lb)
            v = piv[lb]
            g = {cols[ncol - 1 - b] for b in range(v.bit_length()) if (v >> b) & 1}
            for x in range(N):
                ins(ref_mul(g, 1 << x))
        if len(piv) > before:
            it += 1
        else:
            break
    one = (0 in piv)  # constant monomial is last column -> bit 0
    return len(piv), ncol - len(piv), one, it
