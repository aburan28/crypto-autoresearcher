#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- shared context: paths, plan, seeds, curves, targets, writers.

SEEDS (specification replication.seeds 2026092001 / 2026092002, unchanged; amendment `unchanged`
item 6). Every v2 stream string carries the tag ':v2:' so that NO v1 stream is reused.
  targets   random.Random('2026092001:v2:targets:<p>:<shape>')           -- keyed by (p', shape) only,
            so EVERY ARM AND BOTH m ARE SOLVED ON THE SAME R (amendment DC-3 quantifier_order).
  samples   random.Random('2026092002:v2:build:<p>:<shape>:<arm>:<m>')   -- construction streams keyed by arm id.
  basepoint random.Random('2026092002:v2:basepoint:<p>:<shape>')
  fixture   random.Random('2026092001:v2:fixture:<p>:fresh') / ':planted' and '2026092002:v2:fixture:<p>:basepoint'
  grid      random.Random('2026092002:v2:grid:<p>:<shape>:<arm>:<m>:<target>') -- raw-arm grid nodes
Reading of "v2 streams are keyed by arm id" (amendment `unchanged`): construction streams are keyed by
arm id; the TARGET stream is shared across arms because the quantifier order requires the same R for
every arm. Disclosed in implementation-v2.md.
"""
import datetime
import hashlib
import json
import os
import platform
import random
import re
import subprocess

import yaml

from v2_field import Fq, Curve

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
PLAN_PATH = os.path.join(EXP_DIR, "trial-plan-v2.json")
AMENDMENT_PATH = os.path.join(EXP_DIR, "amendments", "v1_to_v2_reanchor_and_arm_iii.yaml")
AMENDMENT_SHA256 = "e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3"
LADDER_PATH = os.path.join(EXP_DIR, "implementation", "ladder.json")      # v1, read-only
RED_TEAM_SCRATCH = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "reviews", "TASK-20260923-404bf9", "scratch", "k5k7")
FIXTURE_N3_JSON = os.path.join(RED_TEAM_SCRATCH, "square_analogue_n3.json")   # DATA ONLY (AC-4)
FIXTURE_N4_JSON = os.path.join(RED_TEAM_SCRATCH, "square_analogue_n4.json")   # DATA ONLY (AC-4)
COMPARATOR = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "reviews", "TASK-20260923-58953e", "scratch", "k4a_anchor_system.py")
SAGE_PYTHON = "/opt/conda-sage/envs/sage/bin/python"
ARCHIVED_ANCHOR_RUN = os.path.join(EXP_DIR, "runs", "RUN-GFPN-61bba9")
CACHE_DIR = os.environ.get("GFPN_V2_CACHE_DIR", os.path.join(os.environ.get("TMPDIR", "/tmp"), "gfpn05-v2-cache"))
SEED_TARGETS = 2026092001
SEED_CURVES = 2026092002
EXPERIMENT_ID = "EXP-GFPN-05ff43"
TASK_ID = "TASK-20260923-cd932c"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:                              # noqa: BLE001
        return "ERROR: %r" % (e,)


def load_plan():
    with open(PLAN_PATH) as fh:
        return json.load(fh)


def plan_package(plan, run_id):
    for pk in plan["packages"]:
        if pk["run_id"] == run_id:
            return pk
    raise KeyError("run id %s is not reserved in trial-plan-v2.json" % run_id)


def resolve_replacement(plan, rid):
    """If a contingency package replaced `rid` (recorded in its manifest), return that run id; else rid."""
    for pk in plan["packages"]:
        if pk["kind"] != "contingency":
            continue
        mp = os.path.join(EXP_DIR, "runs", pk["run_id"], "manifest.yaml")
        if os.path.exists(mp):
            man = yaml.safe_load(open(mp))["run"]
            if (man.get("package") or {}).get("replaces") == rid:
                return pk["run_id"]
    return rid


def watchdog(plan, arm, m):
    key = "%s|m%d" % (arm, m)
    w = plan["watchdogs"]["per_arm_m"].get(key)
    if w is None:
        raise KeyError("no watchdog declared for %s in trial-plan-v2.json (AC-6 requires one per (arm, m))" % key)
    return w


def run_dir():
    d = os.environ.get("GFPN_RUN_DIR")
    if not d:
        raise SystemExit("GFPN_RUN_DIR not set: launch through v2_run_wrapper.py")
    return d


def run_id():
    return os.path.basename(run_dir().rstrip("/"))


def write_yaml(path, obj):
    with open(path, "w") as fh:
        yaml.safe_dump(obj, fh, sort_keys=False, width=110)


def write_json(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def host_record():
    mi = {}
    with open("/proc/meminfo") as fh:
        for line in fh:
            k, v = line.split(":", 1)
            if k in ("MemTotal", "SwapTotal"):
                mi[k + "_kB"] = int(v.split()[0])
    return {"cpu_model": sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(), "nproc": os.cpu_count(),
            "kernel": platform.release(), "mem_total_kB": mi.get("MemTotal_kB"), "swap_total_kB": mi.get("SwapTotal_kB"),
            "msolve_package": sh("dpkg-query -W -f='${Version}' msolve"),
            "libmsolve_package": sh("dpkg-query -W -f='${Package} ${Version}' 'libmsolve-*'")}


def msolve_version():
    v = sh("dpkg-query -W -f='${Version}' msolve")
    return v.split("-")[0] if v and not v.startswith("ERROR") else None


# ----------------------------------------------------------------------------- ladder (v1 file, read-only)
def load_ladder():
    with open(LADDER_PATH) as fh:
        return json.load(fh)


def ladder_entry(p):
    for r in load_ladder():
        if r["p"] == p:
            return r
    raise KeyError(p)


def ladder_field(rung):
    return Fq.binomial(rung["p"], 5, rung["cmod"])


def ladder_curve(F, rung, shape):
    cv = rung["curves"][shape]
    return Curve(F, F.from_coeffs(cv["a2"]), F.from_coeffs(cv["a4"]), F.from_coeffs(cv["a6"]), shape), cv


def base_point(E, n_sub, cofactor, p, shape):
    rng = random.Random("%d:v2:basepoint:%d:%s" % (SEED_CURVES, p, shape))
    while True:
        P = E.random_point(rng)
        G = E.mul(cofactor, P)
        if G is not None and E.mul(n_sub, G) is None:
            return G


def ladder_targets(E, G, n_sub, p, shape, count):
    rng = random.Random("%d:v2:targets:%d:%s" % (SEED_TARGETS, p, shape))
    out = []
    for i in range(count):
        k = rng.randrange(1, n_sub)
        out.append({"index": i, "k": k, "R": E.mul(k, G), "kind": "random"})
    return out


# ----------------------------------------------------------------------------- red-team fixture DATA (AC-4)
def _parse_xR(F, s):
    """'2390*z^2 + 1423*z + 1310' -> F_q element."""
    cs = [0] * F.n
    for term in s.replace(" ", "").split("+"):
        m = re.fullmatch(r"(\d+)\*z\^(\d+)", term) or re.fullmatch(r"(\d+)\*z", term) or re.fullmatch(r"(\d+)", term)
        if not m:
            raise ValueError("cannot parse x_R term %r" % term)
        if term.endswith("z") and "^" not in term:
            cs[1] = int(m.group(1))
        elif "^" in term:
            cs[int(m.group(2))] = int(m.group(1))
        else:
            cs[0] = int(m.group(1))
    return F.from_coeffs(cs)


def fixture_n3(p):
    """Curves, beta and regression x_R values for n = m = 3, read as data from square_analogue_n3.json."""
    with open(FIXTURE_N3_JSON) as fh:
        data = json.load(fh)
    ent = next(e for e in data["primes"] if e["p"] == p)
    mf = re.fullmatch(r"F_(\d+)\[z\]/\(z\^(\d+) - (\d+)\)", ent["field"])
    assert mf and int(mf.group(1)) == p
    n, cmod = int(mf.group(2)), int(mf.group(3))
    mc = re.fullmatch(r"y\^2 = x\(x\^2 \+ (\d+)x \+ (\d+)\*z\)", ent["curve"])
    assert mc, ent["curve"]
    a2, c = int(mc.group(1)), int(mc.group(2))
    F = Fq.binomial(p, n, cmod)
    E = Curve(F, a2, c * F.z, 0, "fixture_n3")
    cv = {"a2": [a2], "a4": [0, c], "a6": [0], "model": ent["curve"]}
    regs = [{"index": t["target"], "x_R": _parse_xR(F, t["x_R"]), "x_R_text": t["x_R"], "kind": "regression_xR"} for t in ent["targets"]]
    return {"F": F, "E": E, "cv": cv, "beta": int(ent["beta"]), "regression": regs,
            "json_b_is_square": ent["b_is_square"], "json_disc_is_square": ent["a2^2-4b_is_square"],
            "source": FIXTURE_N3_JSON, "source_sha256": sha256_file(FIXTURE_N3_JSON)}


def fixture_n4():
    with open(FIXTURE_N4_JSON) as fh:
        data = json.load(fh)
    r = data["result"]
    p = int(r["p"])
    mm = re.fullmatch(r"GF\((\d+)\^4\) modulus (.*)", r["field"])
    assert mm and int(mm.group(1)) == p
    coeffs = [0] * 5
    for term in mm.group(2).replace(" ", "").split("+"):
        a = re.fullmatch(r"(?:(\d+)\*)?x\^(\d+)", term)
        b = re.fullmatch(r"(?:(\d+)\*)?x", term)
        c = re.fullmatch(r"(\d+)", term)
        if a:
            coeffs[int(a.group(2))] = int(a.group(1) or 1)
        elif b:
            coeffs[1] = int(b.group(1) or 1)
        elif c:
            coeffs[0] = int(c.group(1))
        else:
            raise ValueError(term)
    F = Fq(p, coeffs)
    mc = re.fullmatch(r"y\^2 = x\(x\^2 \+ (\d+)x \+ \(z\+(\d+)\)\^2\)", r["curve"])
    assert mc, r["curve"]
    a2, s = int(mc.group(1)), int(mc.group(2))
    b = (F.z + s) ** 2
    E = Curve(F, a2, b, 0, "fixture_n4")
    cv = {"a2": [a2], "a4": F.coeffs(b), "a6": [0], "model": r["curve"]}
    return {"F": F, "E": E, "cv": cv, "beta": int(r["beta"]), "expected": {"S4": r["S4"]["D_msolve"], "torsion_S4_norm": r["product"]["D_msolve"],
            "torsion_S4_rq": r["D4type"]["D_msolve"]}, "source": FIXTURE_N4_JSON, "source_sha256": sha256_file(FIXTURE_N4_JSON)}


# ----------------------------------------------------------------------------- group orders (PARI)
def curve_order_pari(F, E):
    """#E(F_q) by PARI's ellcard over the field F_p[w]/(M). Used only for fixture curves (whose order is
    not in ladder.json) so that fixture targets are known-scalar and certificates verifiable."""
    import cypari2
    pari = cypari2.Pari()
    M = " + ".join("%d*w^%d" % (c, i) for i, c in enumerate(F.modulus) if c)
    def poly(cs):
        cs = F.coeffs(cs)
        s = " + ".join("%d*w^%d" % (c, i) for i, c in enumerate(cs) if c)
        return s or "0"
    expr = ("my(g = ffgen(Mod(1, %d)*(%s), 'w)); my(E = ellinit([0, subst(%s, 'w, g), 0, subst(%s, 'w, g), subst(%s, 'w, g)])); ellcard(E)"
            % (F.p, M, poly(E.a2), poly(E.a4), poly(E.a6)))
    return int(pari(expr))
