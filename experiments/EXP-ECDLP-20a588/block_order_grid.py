#!/usr/bin/env python3
"""EXP-ECDLP-20a588 launcher: the chain arm (A) solved with a block order that
eliminates the 2-isogeny chain variables first, against the dense same-set arm
(B), on the EXP-ECDLP-f49f75 / EXP-ECDLP-502ae2 m = 3 instances.

Every arm computes a Groebner basis whose part in x1..x3 is a basis of the SAME
ideal I = <S_4, F_V(x1), F_V(x2), F_V(x3)> (eliminating the chain variables
from arm A's equations gives F_V, the degree-2^L fibre polynomial):

  A_elim_ms : msolve -e (#w) -g 2, variables (w..., x1..x3)   block order (DRL | DRL)
  A_drl_ms  : msolve -g 2, variables (x1..x3, w...)           plain DRL (as EXP-ECDLP-502ae2)
  B_ms      : msolve -g 2, variables (x1..x3)                 DRL
  A_block_sg: Singular std, ring (w..., x...), (dp(#w), dp(3)) block order
  B_sg      : Singular std, ring (x1..x3), dp

Timed: process wall time per solve (and Singular's rtimer for std).
Controls: planted decomposition satisfies every basis element; the x-only part
of A_elim_ms's reduced basis must equal B_ms's reduced basis (same reduced DRL
basis of the same elimination ideal) -> recorded as elim_equals_B.
"""
import argparse, hashlib, importlib.util, json, os, platform, random, re, subprocess, tempfile, time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("msg", os.path.join(HERE, "..", "EXP-ECDLP-502ae2", "msolve_grid.py"))
msg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(msg)
pkm = msg.pkm

ARMS_MS = ("A_elim_ms", "A_drl_ms", "B_ms")
ARMS_SG = ("A_block_sg", "B_sg")


def gb_polys(text):
    body = text[text.index("["):text.rindex("]") + 1].strip("[]")
    return [q.strip() for q in body.split(",") if q.strip()]


def run_ms(vars_, polys, p, extra, timeout):
    path = msg.write_input(vars_, p, polys)
    out = path + ".gb"
    st, wall, log = msg.run_msolve(["-f", path, "-o", out] + extra + ["-g", "2", "-v", "2", "-t", "1"], timeout)
    res = dict(status=st, wall_s=wall)
    degs = [int(l.split()[0]) for l in log.splitlines() if re.match(r"^\s*\d+\s+\d+\s+\d+\s+\d+ x \d+", l)]
    if degs:
        res["f4_max_deg"] = max(degs)
    text = open(out).read() if st == "ok" and os.path.exists(out) else None
    for f in (path, out):
        if os.path.exists(f):
            os.unlink(f)
    return res, text


def run_sg(vars_, polys, p, order, point, timeout):
    lines = ["option(redSB);", 'system("--ticks-per-sec",1000);',
             f"ring r = {p},({','.join(vars_)}),{order};",
             "ideal I = " + ",".join(polys) + ";",
             "int t0 = rtimer; ideal G = std(I); int t = rtimer - t0;",
             "int dg = 0; int k; for (k=1;k<=size(G);k++){ if (deg(G[k])>dg) {dg=deg(G[k]);} }",
             'print("STD " + string(t) + " " + string(vdim(G)) + " " + string(size(G)) + " " + string(dg));']
    if point:
        lines.append("ideal Z = subst(G," + ",".join(f"{v},{val}" for v, val in point.items()) + ");")
        lines.append('print("PLANTED " + string(size(Z)==0));')
    lines.append("quit;")
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as f:
        f.write("\n".join(lines) + "\n")
        path = f.name
    t0 = time.monotonic()
    try:
        out = subprocess.run(["Singular", "-q", "--no-rc", path], capture_output=True, text=True, timeout=timeout)
        st, so = ("ok" if out.returncode == 0 else f"rc{out.returncode}"), out.stdout
    except subprocess.TimeoutExpired:
        st, so = "timeout", ""
    res = dict(status=st, wall_s=round(time.monotonic() - t0, 4))
    os.unlink(path)
    for l in so.splitlines():
        p_ = l.split()
        if p_ and p_[0] == "STD":
            res.update(std_ms=int(p_[1]), vdim=int(p_[2]), gb_size=int(p_[3]), gb_maxdeg=int(p_[4]))
        elif p_ and p_[0] == "PLANTED":
            res["planted_in_variety"] = p_[1] == "1"
    if st == "ok" and "std_ms" not in res:
        res["status"] = "incomplete"
    return res


def run_instance(job):
    m, L, inst, kind, seed, timeout, arms = (job[k] for k in ("m", "L", "inst", "kind", "seed", "timeout", "arms"))
    rng = random.Random(seed)
    p = pkm.find_prime(m, L)
    a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    chain = pkm.build_chain(p, L, rng)
    rng.sample(range(p), 2 ** L)  # keep the RNG stream identical to the predecessors (arm C's set)
    out = dict(job, p=p, p_bits=p.bit_length(), b=b, results={})
    fb = pkm.factor_base(chain["V"], a, b, p)
    trng = random.Random(f"{seed}-False-target")
    if kind == "planted":
        picks = [trng.choice(fb) for _ in range(m)]
        picks = [P if trng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
        T = None
        for P in picks:
            T = pkm.ec_add(T, P, a, p)
        if T is None:
            out["results"] = {k: dict(status="degenerate_target") for k in arms}
            return out
    else:
        while True:
            x = trng.randrange(p)
            y = pkm.sqrt_mod(x ** 3 + a * x + b, p)
            if y is not None:
                T, picks = (x, y), None
                break
    S = msg.summation_poly(p, m, a, b, T[0])
    vA, pA = msg.build_system("A", p, m, S, chain)
    vB, pB = msg.build_system("B", p, m, S, dict(coeffs=pkm.poly_from_roots(chain["V"], p)))
    xs, ws = vA[:m], vA[m:]
    point = None
    if picks is not None:
        point = {f"x{i}": P[0] for i, P in enumerate(picks, 1)}
        for i, P in enumerate(picks, 1):
            tr = pkm.chain_eval(P[0], chain["steps"], p, trace=True)
            point.update({f"w{i}{j:02d}": tr[j] for j in range(1, L)})
    texts = {}
    for arm in arms:
        if arm in ARMS_MS:
            if arm == "A_elim_ms":
                res, text = run_ms(ws + xs, pA, p, ["-e", str(len(ws))], timeout)
            elif arm == "A_drl_ms":
                res, text = run_ms(vA, pA, p, [], timeout)
            else:
                res, text = run_ms(vB, pB, p, [], timeout)
            texts[arm] = text
            if text is not None and point is not None:
                vars_here = vB if arm == "B_ms" else vA
                res["planted_in_variety"] = msg.eval_gb_at(text, {v: point[v] for v in vars_here}, p)
            if text is not None:
                res["gb_size"] = len(gb_polys(text))
        else:
            if arm == "A_block_sg":
                res = run_sg(ws + xs, pA, p, f"(dp({len(ws)}),dp({m}))", point, timeout)
            else:
                res = run_sg(vB, pB, p, "dp", {v: point[v] for v in vB} if point else None, timeout)
        out["results"][arm] = res
    if texts.get("A_elim_ms") is not None and texts.get("B_ms") is not None:
        elim_x = sorted(q for q in gb_polys(texts["A_elim_ms"]) if not re.search(r"\bw\d", q))
        out["elim_equals_B"] = elim_x == sorted(gb_polys(texts["B_ms"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    plan = json.load(open(args.plan))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    t0, n = time.time(), 0
    with open(args.out, "w") as fh, ProcessPoolExecutor(args.workers) as ex:
        for m, Ls in sorted(plan["L_by_m"].items()):
            m = int(m)
            arms = list(plan["arms"])
            for L in Ls:
                if not arms:
                    break
                jobs = []
                for inst in range(plan["planted_per_cell"] + plan["random_per_cell"]):
                    kind = "planted" if inst < plan["planted_per_cell"] else "random"
                    seed = int(hashlib.sha256(f"{plan['seed']}|{m}|{L}|{inst}".encode()).hexdigest()[:12], 16)
                    jobs.append(dict(m=m, L=L, inst=inst, kind=kind, seed=seed, timeout=plan["timeout_s"], arms=list(arms)))
                rows = [f.result() for f in as_completed([ex.submit(run_instance, j) for j in jobs])]
                for r in sorted(rows, key=lambda r: r["inst"]):
                    fh.write(json.dumps(r) + "\n")
                    print(f"m={m} L={L} inst={r['inst']} elim=B:{r.get('elim_equals_B')} " + " ".join(
                        f"{k}:{v.get('status')}/{v.get('wall_s')}/{v.get('planted_in_variety')}" for k, v in r["results"].items()), flush=True)
                fh.flush(); n += len(rows)
                for arm in list(arms):  # frozen stopping rule
                    if all(r["results"].get(arm, {}).get("status") == "timeout" for r in rows):
                        arms.remove(arm)
                        print(f"stop: arm {arm} retired at m={m} L={L}", flush=True)
    print(json.dumps(dict(jobs=n, elapsed_s=round(time.time() - t0, 1), python=platform.python_version())))


if __name__ == "__main__":
    main()
