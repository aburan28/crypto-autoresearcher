# NON-PROTOCOL design-time feasibility probe for TASK-20261001-768475.
# Synthetic curve y^2 = x^3 + 3x + 7 over F_10007 (not a fixture of any
# experiment; no protocol label or seed is used). Measures only the size and
# build time of summation polynomials f4, f5 and the target-specialised f6 as
# built by the resultant recursion EXP-ICEX-fa2b37 specifies. One JSON line per
# step, flushed. A watchdog thread exits the process when peak RSS passes
# 4 GiB (the card's memory budget; macOS ignores RLIMIT_AS).
# Attempt 1 of this probe (same steps, no watchdog, output buffered to the
# end) was killed by the session at 8.56 GB RSS after 6.6 minutes; it wrote
# no output, so which step was running is unknown.
#   nice -n 10 sage -python feasibility_probe.sage.py
import json
import os
import resource
import signal
import sys
import threading
import time

from sage.all import GF, PolynomialRing

LIMIT = 4 * 2**30
P, A, C = 10007, 3, 7
F = GF(P)
R = PolynomialRing(F, ["x1", "x2", "x3", "x4", "x5", "z"], order="degrevlex")
x1, x2, x3, x4, x5, z = R.gens()
T0 = time.time()


def rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def emit(rec):
    rec["elapsed_s"] = round(time.time() - T0, 2)
    rec["peak_rss_bytes"] = rss()
    sys.stdout.write(json.dumps(rec) + "\n")
    sys.stdout.flush()


def watchdog():
    while True:
        if rss() > LIMIT:
            emit({"event": "watchdog_exit", "limit_bytes": LIMIT, "running_step": CURRENT[0]})
            os._exit(3)
        time.sleep(0.25)


CURRENT = ["start"]
threading.Thread(target=watchdog, daemon=True).start()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)


def f3(u, v, w):
    return (u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + A) + 2 * C) * w + (u * v - A) ** 2 - 4 * C * (u + v)


def step(name, fn, limit, describe):
    CURRENT[0] = name
    emit({"event": "start", "step": name, "timeout_s": limit})
    signal.alarm(limit)
    t0 = time.time()
    try:
        val = fn()
        signal.alarm(0)
        rec = {"event": "done", "step": name, "seconds": round(time.time() - t0, 3)}
        rec.update(describe(val))
        emit(rec)
        return val
    except Timeout:
        emit({"event": "timeout", "step": name, "seconds": limit})
        return None


def desc(poly):
    return {"terms": int(len(poly.monomials())), "deg_x1": int(poly.degree(x1)),
            "total_degree": int(poly.total_degree())}


emit({"event": "label", "text": "NON-PROTOCOL feasibility probe; synthetic curve p=10007 a=3 c=7"})
f4 = step("f4 = Res_z(f3(x1,x2,z), f3(x3,x4,z))", lambda: f3(x1, x2, z).resultant(f3(x3, x4, z), z), 120, desc)
f5 = None
if f4 is not None:
    f4z = f4.subs({x4: z})
    f5 = step("f5 = Res_z(f4(x1,x2,x3,z), f3(x4,x5,z))", lambda: f4z.resultant(f3(x4, x5, z), z), 600, desc)
if f5 is not None:
    f5z = f5.subs({x5: z})
    xr = F(1234)
    step("f6(x1..x5, x_R=1234) = Res_z(f5(x1..x4,z), f3(x5,x_R,z))",
         lambda: f5z.resultant(f3(x5, xr, z), z), 600, desc)
emit({"event": "end"})
