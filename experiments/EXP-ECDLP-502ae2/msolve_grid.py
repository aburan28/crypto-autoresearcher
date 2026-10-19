#!/usr/bin/env python3
"""EXP-ECDLP-502ae2 launcher: the EXP-ECDLP-f49f75 m = 3 grid re-run under msolve
(F4 + sparse-FGLM), to test whether the chain-encoding slowdown is an artefact of
Singular's Buchberger-type std/slimgb.

Instances are IDENTICAL to EXP-ECDLP-f49f75 (same construction code, imported
from that experiment's launcher, and the same seed string "EXP-ECDLP-f49f75/v1"),
so every (m, L, instance) is paired with its Singular measurement.

Per Groebner arm (A chain, B dense same set, C dense random set) and instance:
  gb   : msolve -g 2 -v 2   (reduced DRL basis; timed; max F4 degree parsed from
                             the verbose log; basis used for the planted check)
  solve: msolve -P 1        (full solve: F4 + FGLM parametrization; timed)
Arm E (enumeration) is re-measured unchanged.
The summation polynomial S_4 = Res_X(S_3(x1,x2,X), S_3(x3,xT,X)) is expanded once
per instance by Singular (untimed preprocessing, identical input for A and B).
"""
import argparse, hashlib, importlib.util, json, os, platform, random, re, subprocess, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "pkm", os.path.join(HERE, "..", "EXP-ECDLP-f49f75", "pkm_isogeny_fb.py"))
pkm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pkm)

S3 = pkm.S3


def summation_poly(p, m, a, b, xT):
    """Expanded S_{m+1}(x1..xm, xT) as a string in variables x1..xm (Singular, field arithmetic)."""
    num = pkm.num
    if m == 2:
        body = "poly S = " + S3.format(x1="x1", x2="x2", x3=num(xT), a=num(a), b=num(b)) + ";"
        ring = f"ring r0 = {p},(x1,x2),dp;"
    else:
        body = ("poly S = resultant(" + S3.format(x1="x1", x2="x2", x3="X", a=num(a), b=num(b)) + ","
                + S3.format(x1="x3", x2=num(xT), x3="X", a=num(a), b=num(b)) + ",X);")
        ring = f"ring r0 = {p},(x1,x2,x3,X),dp;"
    script = f'{ring}\n{body}\nprint(string(S));\nquit;\n'
    out = subprocess.run(["Singular", "-q", "--no-rc"], input=script, capture_output=True, text=True, timeout=600)
    s = "".join(out.stdout.split())
    assert s and "X" not in s, out.stdout[:200] + out.stderr[:200]
    return s


def lin_terms(terms, p):
    """terms: list of (coeff, monomial-string or '') -> msolve polynomial string."""
    acc = {}
    for c, mono in terms:
        acc[mono] = (acc.get(mono, 0) + c) % p
    parts = [f"{c}*{mono}" if mono else f"{c}" for mono, c in acc.items() if c]
    return "+".join(parts) if parts else "0"


def build_system(arm, p, m, S, enc):
    xs = [f"x{i}" for i in range(1, m + 1)]
    vars_, polys = list(xs), [S]
    if arm == "A":
        L = len(enc["steps"])
        for i in range(1, m + 1):
            ws = [f"w{i}{j:02d}" for j in range(1, L)]
            vars_ += ws
            chain = [f"x{i}"] + ws + [None]  # None = the constant c
            for j, (x0, t) in enumerate(enc["steps"]):
                u, v = chain[j], chain[j + 1]
                # v*(u - x0) - u*(u - x0) - t
                if v is None:
                    c = enc["c"]
                    terms = [(c, u), (-c * x0, ""), (-1, f"{u}^2"), (x0, u), (-t, "")]
                else:
                    terms = [(1, f"{v}*{u}"), (-x0, v), (-1, f"{u}^2"), (x0, u), (-t, "")]
                polys.append(lin_terms(terms, p))
    else:
        for x in xs:
            polys.append(lin_terms([(ci, f"{x}^{k}" if k else "") for k, ci in enumerate(enc["coeffs"])], p))
    return vars_, polys


def write_input(vars_, p, polys):
    f = tempfile.NamedTemporaryFile("w", suffix=".ms", delete=False)
    f.write(",".join(vars_) + "\n" + str(p) + "\n" + ",\n".join(polys) + "\n")
    f.close()
    return f.name


def run_msolve(args, timeout):
    t0 = time.monotonic()
    try:
        out = subprocess.run(["msolve"] + args, capture_output=True, text=True, timeout=timeout)
        status = "ok" if out.returncode == 0 else f"rc{out.returncode}"
        log = out.stdout + out.stderr
    except subprocess.TimeoutExpired as e:
        status, log = "timeout", ""
    return status, round(time.monotonic() - t0, 4), log


def eval_gb_at(gb_text, point, p):
    body = gb_text[gb_text.index("["):gb_text.rindex("]") + 1]
    env = dict(point)
    for poly in body.strip("[]").split(","):
        poly = poly.strip()
        if not poly:
            continue
        expr = re.sub(r"\^", "**", poly)
        if eval(expr, {"__builtins__": {}}, env) % p:
            return False
    return True


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
    randV = sorted(rng.sample(range(p), 2 ** L))
    out = dict(job, p=p, p_bits=p.bit_length(), b=b, chain_c=chain["c"], results={})
    for arm in arms:
        Vset = randV if arm == "C" else chain["V"]
        fb = pkm.factor_base(Vset, a, b, p)
        trng = random.Random(f"{seed}-{arm in 'C'}-target")
        if kind == "planted":
            picks = [trng.choice(fb) for _ in range(m)]
            picks = [P if trng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
            T = None
            for P in picks:
                T = pkm.ec_add(T, P, a, p)
            if T is None:
                out["results"][arm] = dict(status="degenerate_target")
                continue
        else:
            while True:
                x = trng.randrange(p)
                y = pkm.sqrt_mod(x ** 3 + a * x + b, p)
                if y is not None:
                    T, picks = (x, y), None
                    break
        if arm == "E":
            t0 = time.monotonic()
            ops, nfound = pkm.enumerate_decomp(T, fb, m, a, p)
            out["results"][arm] = dict(status="ok", group_ops=ops, decompositions=nfound,
                                       wall_s=round(time.monotonic() - t0, 4), fb_size=len(fb))
            continue
        S = summation_poly(p, m, a, b, T[0])
        enc = chain if arm == "A" else dict(coeffs=pkm.poly_from_roots(Vset, p))
        vars_, polys = build_system(arm, p, m, S, enc)
        path = write_input(vars_, p, polys)
        res = dict(fb_size=len(fb), nvars=len(vars_), npolys=len(polys))
        gb_out = path + ".gb"
        st, wall, log = run_msolve(["-f", path, "-o", gb_out, "-g", "2", "-v", "2", "-t", "1"], timeout)
        res.update(gb_status=st, gb_wall_s=wall)
        degs = [int(l.split()[0]) for l in log.splitlines() if re.match(r"^\s*\d+\s+\d+\s+\d+\s+\d+ x \d+", l)]
        if degs:
            res["f4_max_deg"] = max(degs)
        mq = re.search(r"Dimension of quotient:\s*(\d+)", log)
        if mq:
            res["quotient_dim"] = int(mq.group(1))
        if st == "ok" and picks is not None:
            point = {f"x{i}": P[0] for i, P in enumerate(picks, 1)}
            if arm == "A":
                for i, P in enumerate(picks, 1):
                    tr = pkm.chain_eval(P[0], chain["steps"], p, trace=True)
                    point.update({f"w{i}{j:02d}": tr[j] for j in range(1, L)})
            res["planted_in_variety"] = eval_gb_at(open(gb_out).read(), point, p)
        if st == "ok":
            st2, wall2, _ = run_msolve(["-f", path, "-o", path + ".sol", "-P", "1", "-t", "1"], timeout)
            res.update(solve_status=st2, solve_wall_s=wall2)
        res["status"] = "ok" if st == "ok" and res.get("solve_status") == "ok" else (
            "timeout" if "timeout" in (st, res.get("solve_status")) else st if st != "ok" else res.get("solve_status"))
        for f in (path, gb_out, path + ".sol"):
            if os.path.exists(f):
                os.unlink(f)
        out["results"][arm] = res
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
                if not [x for x in arms if x != "E"]:
                    break
                jobs = []
                for inst in range(plan["planted_per_cell"] + plan["random_per_cell"]):
                    kind = "planted" if inst < plan["planted_per_cell"] else "random"
                    seed = int(hashlib.sha256(f"{plan['seed']}|{m}|{L}|{inst}".encode()).hexdigest()[:12], 16)
                    jobs.append(dict(m=m, L=L, inst=inst, kind=kind, seed=seed, timeout=plan["timeout_s"], arms=arms))
                rows = [f.result() for f in as_completed([ex.submit(run_instance, j) for j in jobs])]
                for r in sorted(rows, key=lambda r: r["inst"]):
                    fh.write(json.dumps(r) + "\n")
                    print(f"m={m} L={L} inst={r['inst']} " + " ".join(
                        f"{k}:{v.get('status')}/{v.get('gb_wall_s', v.get('group_ops'))}/{v.get('solve_wall_s')}/d{v.get('f4_max_deg')}"
                        for k, v in r["results"].items()), flush=True)
                fh.flush(); n += len(rows)
                # frozen stopping rule: retire an arm whose every instance timed out in a cell
                for arm in [x for x in arms if x != "E"]:
                    if all(r["results"].get(arm, {}).get("status") == "timeout" for r in rows):
                        arms.remove(arm)
                        print(f"stop: arm {arm} retired at m={m} L={L}", flush=True)
    print(json.dumps(dict(jobs=n, elapsed_s=round(time.time() - t0, 1), python=platform.python_version())))


if __name__ == "__main__":
    main()
