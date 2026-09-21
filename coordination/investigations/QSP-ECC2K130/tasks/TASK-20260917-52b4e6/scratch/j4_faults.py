"""J4 (b): FAULT INJECTION on a SCRATCH COPY of the implementation.
If a deliberate bug in a SHARED primitive leaves the agreement matrix M2 at 0,
the matrix is measuring shared code rather than agreement.

Every fault is applied by rewriting the scratch copy of qspcore.py; the
committed implementation is never touched.  For each fault we recompute, on a
sample of the Stage 1 candidate set, all three instruments and report
  (i) whether any instrument's N CHANGED vs the unfaulted baseline, and
  (ii) whether I1/I2/I3 still AGREE with each other (M2 == 0)."""
import importlib.util, os, random, sys, json, re, signal

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = open(os.path.join(HERE, "faultcopy", "qspcore_base.py")).read()

CELLS = [(7,3)]

def load(src, name):
    path = os.path.join(HERE, "faultcopy", name + ".py")
    open(path,"w").write(src)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m

class _TO(Exception): pass
def _h(sig, frm): raise _TO()
signal.signal(signal.SIGALRM, _h)

def run_matrix(mod, cells=CELLS, degs=range(2,6), limit=None, per_cand_s=1):
    """returns list of (cell,lam,I1,I2,I3) and the pairwise disagreement counts"""
    rng = random.Random(20260917)
    rows=[]; d12=d13=d23=0; err=0
    for (n,npr) in cells:
        K = mod.KField(n)
        for d in degs:
            for low in range(1<<d):
                lam=(1<<d)|low
                if limit is not None and len(rows)>=limit: break
                try:
                    signal.alarm(per_cand_s)
                    i1 = mod.i1_brute_f2(K, lam, npr)[0]
                    i2 = mod.i2_gcd_f2(n, npr, lam)
                    r3 = mod.i3_injection_f2(K, lam, npr, rng)
                    i3 = None if r3.get("degenerate") else r3["N"]
                    signal.alarm(0)
                except _TO:
                    signal.alarm(0); err+=1; i1=i2=i3="TIMEOUT"
                except Exception as e:
                    signal.alarm(0); err+=1; i1=i2=i3=("ERR:"+type(e).__name__)
                rows.append((n,npr,lam,i1,i2,i3))
                if i1!=i2: d12+=1
                if i3 is not None and i1!=i3: d13+=1
                if i3 is not None and i2!=i3: d23+=1
    return rows, dict(I1_vs_I2=d12, I1_vs_I3=d13, I2_vs_I3=d23, errors=err, n=len(rows))

FAULTS = {
 "none (baseline)": None,
 "F-a  square(): drop the top spread mask (off-by-one in the squaring ladder)":
    ("    for s, m in _SPREAD_MASKS[w]:\n        if s == w:\n            continue",
     "    for s, m in _SPREAD_MASKS[w][:-1]:\n        if s == w:\n            continue"),
 "F-b  polymod(): stop one degree early (off-by-one in the reduction)":
    ("def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    while a and deg(a) >= dm:",
     "def polymod(a: int, m: int) -> int:\n    dm = deg(m)\n    while a and deg(a) > dm:"),
 "F-c  clmul(): drop the highest set bit of the sparser operand":
    ("    r = 0\n    while a:\n        low = a & -a\n        r ^= b << (low.bit_length() - 1)\n        a ^= low\n    return r",
     "    r = 0\n    if a and a.bit_count() > 1:\n        a ^= 1 << (a.bit_length() - 1)\n    while a:\n        low = a & -a\n        r ^= b << (low.bit_length() - 1)\n        a ^= low\n    return r"),
 "F-d  gcd(): swap one step early (Euclid off-by-one)":
    ("def gcd(a: int, b: int) -> int:\n    while b:\n        a = polymod(a, b)\n        a, b = b, a\n    return a",
     "def gcd(a: int, b: int) -> int:\n    while b:\n        a, b = b, polymod(a, b)\n    return a if a else b"),
 "F-e  polymod_sparse_tail(): drop the high word (I2-only path)":
    ("    while a >> np2:\n        high = a >> np2\n        a = (a & mask) ^ clmul(high, lam)",
     "    while a >> np2:\n        high = (a >> np2) & ((1 << max(1,(a.bit_length()-np2-1))) - 1)\n        if high == 0: break\n        a = (a & mask) ^ clmul(high, lam)"),
 "F-f  frob_power_mod(): one squaring too few (I3-only path)":
    ('def frob_power_mod(k: int, m: int) -> int:\n    """X^(2^k) mod m, dense reduction."""\n    x = 0b10\n    for _ in range(k):',
     'def frob_power_mod(k: int, m: int) -> int:\n    """X^(2^k) mod m, dense reduction."""\n    x = 0b10\n    for _ in range(max(0,k-1)):'),
 "F-g  _frob_table(): one Frobenius too few (I1-only path)":
    ("        t = list(range(1 << K.n))\n        for _ in range(npr):",
     "        t = list(range(1 << K.n))\n        for _ in range(max(0,npr-1)):"),
}

base_mod = load(BASE, "qspc_base")
base_rows, base_dis = run_matrix(base_mod)
print("BASELINE over %d Stage-1 candidates: %s" % (base_dis["n"], base_dis))
base_map = {(r[0],r[1],r[2]):(r[3],r[4],r[5]) for r in base_rows}
out=[{"fault":"none (baseline)", **base_dis, "changed_vs_baseline":0}]
for name,(fault) in list(FAULTS.items()):
    if fault is None: continue
    old,new = fault
    assert old in BASE, "fault anchor not found: "+name
    src = BASE.replace(old,new,1)
    tag = "qspc_" + re.sub(r'\W','_',name)[:24]
    try:
        m = load(src, tag)
        rows, dis = run_matrix(m)
    except Exception as e:
        print("%-72s MODULE LOAD FAILED: %s -- the package's OWN self-check caught it" % (name, type(e).__name__)); sys.stdout.flush(); continue
    changed = sum(1 for r in rows if (r[3],r[4],r[5]) != base_map[(r[0],r[1],r[2])])
    agree_clean = (dis["I1_vs_I2"]==0 and dis["I1_vs_I3"]==0 and dis["I2_vs_I3"]==0 and dis["errors"]==0)
    sys.stdout.flush()
    print("%-72s changed=%-6d M2=(%d,%d,%d) err=%-4d  AGREEMENT STILL CLEAN: %s"
          % (name, changed, dis["I1_vs_I2"], dis["I1_vs_I3"], dis["I2_vs_I3"], dis["errors"], agree_clean))
    out.append({"fault":name, **dis, "changed_vs_baseline":changed, "agreement_clean":agree_clean})
json.dump(out, open(os.path.join(HERE,"scratch","j4_faults_out.json"),"w"), indent=1)
