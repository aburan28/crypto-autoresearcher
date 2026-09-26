"""Sampler draws and null factorisations through a pool of gp workers.

A draw is fully determined by (context, k, P^1 index); the P^1 index is drawn
in the parent from the per-draw SHA-256 stream, so records do not depend on
worker count or scheduling (DET-1).
"""
import json
import multiprocessing as mp
import time

import common

_GP = None


def _init(ctx):
    global _GP
    _GP = common.GP()
    _GP.cmd("setctx(%d,%s,%d)" % (ctx["p"], ctx["start_basis"], ctx["Kmax"]), want=False)
    if ctx.get("factor_watchdog_s"):
        _GP.cmd("CTXWD=%d" % ctx["factor_watchdog_s"], want=False)
    if ctx.get("types"):
        T, labels, grams = ctx["types"]
        _GP.cmd("settypes(%d,%s,[%s])" % (T, "[" + ",".join(str(x) for x in labels) + "]", ",".join(grams)), want=False)


def parse_sample(line):
    parts = line.split("|")
    delta = int(parts[0])
    fac = json.loads(parts[1])
    return {"delta": delta, "fac": fac, "fac_ok": int(parts[2]),
            "ideal_hash": common.sha256_str(parts[3]), "order_hash": common.sha256_str(parts[4]),
            "c2": int(parts[5]), "u2": int(parts[6]), "type": int(parts[7]),
            "ell_max": max([q for q, e in fac], default=1)}


def _draw(task):
    t0 = time.perf_counter()
    line = _GP.val("wsample(%d,%d)" % (task["k"], task["p1_index"]))
    dt = time.perf_counter() - t0
    r = {"arm": task["arm"], "index": task["index"], "seed": task["seed"], "k": task["k"],
         "p1_index": str(task["p1_index"])}
    r.update(parse_sample(line))
    if r["type"] == -2:
        del r["type"]
    for extra in ("contaminated",):
        if extra in task:
            r[extra] = task[extra]
    r["wall_s"] = round(dt, 6)
    return r


def _draw_chunk(tasks):
    return [_draw(t) for t in tasks]


def run_draws(ctx, tasks, workers, chunk=100):
    """Returns records in task order."""
    chunks = [tasks[i:i + chunk] for i in range(0, len(tasks), chunk)]
    out = []
    if workers == 1:
        _init(ctx)
        for c in chunks:
            out.extend(_draw_chunk(c))
        _GP.close()
        return out
    with mp.get_context("fork").Pool(workers, initializer=_init, initargs=(ctx,)) as pool:
        for res in pool.imap(_draw_chunk, chunks):
            out.extend(res)
    return out


_NWD = 0


def _null_init(wd):
    global _GP, _NWD
    _GP = common.GP()
    _NWD = wd or 0


def _null_chunk(tasks):
    out = []
    for t in tasks:
        t0 = time.perf_counter()
        if _NWD:
            line = _GP.val('my(fv=iferr(alarm(%d,vfactor(%d)),E,[[],-1])); Str(fv[1],"|",fv[2])' % (_NWD, t["n"]))
        else:
            line = _GP.val('my(fv=vfactor(%d)); Str(fv[1],"|",fv[2])' % t["n"])
        dt = time.perf_counter() - t0
        fac_s, ok = line.split("|")
        fac = json.loads(fac_s)
        out.append({"arm": t["arm"], "index": t["index"], "seed": t["seed"], "n": t["n"], "fac": fac,
                    "fac_ok": int(ok), "ell_max": max([q for q, e in fac], default=1), "wall_s": round(dt, 6)})
    return out


def run_nulls(tasks, workers, chunk=500, watchdog=None):
    chunks = [tasks[i:i + chunk] for i in range(0, len(tasks), chunk)]
    out = []
    if workers == 1:
        _null_init(watchdog)
        for c in chunks:
            out.extend(_null_chunk(c))
        _GP.close()
        return out
    with mp.get_context("fork").Pool(workers, initializer=_null_init, initargs=(watchdog,)) as pool:
        for res in pool.imap(_null_chunk, chunks):
            out.extend(res)
    return out


def make_tasks(master, stage, p, arm, n, k, start_index=0):
    """Main-arm draws: P^1 index uniform in [0, 3*2^(k-1)) from the per-draw stream."""
    tasks = []
    for i in range(start_index, start_index + n):
        sd = common.draw_seed(master, stage, p, arm, i)
        st = common.Stream(sd)
        idx = 0 if k == 0 else st.randbelow(3 * 2 ** (k - 1))
        tasks.append({"arm": arm, "index": i, "seed": sd, "k": k, "p1_index": idx})
    return tasks
