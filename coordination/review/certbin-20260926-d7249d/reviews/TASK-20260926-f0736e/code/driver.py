"""Driver for the blind re-derivation TASK-20260926-f0736e (joint J6 of
REVIEW-CERTBIN-20260926-d7249d).

  python3 code/driver.py --inputs <blind-inputs.json> --out <task dir> [--resume]

Order: environment record -> BR-2 self-tests (stop on failure) -> blind
inputs -> per system Q1..Q7 with a checkpoint per system -> assemble
rederivation.json, wdag.jsonl.gz, ann.jsonl.gz -> seal.txt.  report.yaml and
attestation.yaml are written afterwards, outside this program (BR-7).

Imports nothing from crypto_autoresearcher.  No specification seed is used.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import algebra as G  # noqa: E402
import certs as C  # noqa: E402
import checkers as K  # noqa: E402
import field as F  # noqa: E402
import selftest as ST  # noqa: E402

SCHEMA = "certbin.n19.rederivation.v1"
TASK = "TASK-20260926-f0736e"
EXPECT_B = 306147
EXPECT_A = 46693


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(msg):
    print("[%s] %s" % (utcnow(), msg), flush=True)


def environment():
    def cmd(c):
        try:
            return subprocess.check_output(c, shell=True, stderr=subprocess.STDOUT, text=True).strip()
        except Exception as e:  # pragma: no cover
            return "unavailable: %s" % e
    code_files = sorted(f for f in os.listdir(HERE) if f.endswith((".py", ".c", ".json")))
    G.lib()  # compile (if needed) and load the own C kernel
    so = os.path.join(os.environ.get("F0736E_BUILD_DIR", os.path.join(HERE, "..", "build")), "gf2kern.so")
    return {
        "c_kernel_shared_object": {"built_from": "code/gf2kern.c", "path_outside_repo": so,
                                   "sha256": sha256_file(so)},
        "python": sys.version,
        "numpy": np.__version__,
        "gcc": cmd("gcc --version | head -1"),
        "c_flags": G.CFLAGS,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "env": {k: os.environ.get(k) for k in ("PYTHONDONTWRITEBYTECODE", "OPENBLAS_NUM_THREADS",
                                                "OMP_NUM_THREADS", "F0736E_BUILD_DIR")},
        "code_sha256": {f: sha256_file(os.path.join(HERE, f)) for f in code_files},
        "imports_crypto_autoresearcher": False,
    }


def parse_explicit_algebra(equations):
    """Algebra-side parse of an explicit system (independent of checkers.py)."""
    eqs = []
    dup_monomials = 0
    unsorted = 0
    for eq in equations:
        ms = []
        for mono in eq:
            assert all(isinstance(v, int) and 0 <= v < G.NV for v in mono), mono
            assert len(set(mono)) == len(mono), mono
            if list(mono) != sorted(mono):
                unsorted += 1
            m = 0
            for v in mono:
                m |= 1 << v
            ms.append(m)
        if len(set(ms)) != len(ms):
            dup_monomials += 1
        eqs.append(G.poly_reduce(np.array(ms, dtype=np.int64)))
    return eqs, (dup_monomials, unsorted)


def e_hex(eqs):
    E = G.eqs_to_E(eqs)
    out = []
    for row in E:
        x = 0
        for j in np.flatnonzero(row):
            x |= 1 << int(j)
        out.append(format(x, "x"))
    return out


def process_system(inst, B):
    label = inst["label"]
    kind = inst["kind"]
    rec = {"label": label, "kind": kind}
    tm = {}
    t = time.time()
    # ---- construction ----------------------------------------------------
    if kind == "curve":
        xR = int(inst["x_R"])
        rec["x_R"] = xR
        eqs = G.descend_S3(xR, B)
        e_cf = G.descend_S3_closed_form(xR, B)
        eqs_chk = K.curve_system(xR, B)
        rec["construction"] = {
            "method": "generic expansion of S_3(x_1, x_2, x_R) over F_{2^19} (algebra.descend_S3)",
            "equals_algebra_closed_form": all(np.array_equal(a, b) for a, b in zip(eqs, e_cf)),
            "equals_checker_closed_form": all(np.array_equal(a, b) for a, b in zip(eqs, eqs_chk)),
        }
    elif kind == "explicit":
        xR = None
        eqs, dups = parse_explicit_algebra(inst["equations"])
        eqs_chk = K.explicit_system(inst["equations"])
        rec["construction"] = {
            "method": "monomial lists of blind-inputs.json",
            "equations_with_duplicate_monomials": dups[0],
            "monomials_not_in_ascending_index_order": dups[1],
            "equals_checker_parse": all(np.array_equal(a, b) for a, b in zip(eqs, eqs_chk)),
        }
    else:
        raise ValueError("unknown kind %r" % kind)
    assert len(eqs) == G.NEQ, "expected 19 equations"
    maxdeg = max(G.poly_deg(e) for e in eqs)
    rec["construction"]["max_degree"] = maxdeg
    rec["construction"]["monomials_per_equation"] = [int(len(e)) for e in eqs]
    assert maxdeg <= 2, "an equation has degree > 2"
    rec["E_hex"] = e_hex(eqs)
    tm["construction"] = time.time() - t
    # ---- Q1 --------------------------------------------------------------
    t = time.time()
    s = G.exhaustive_s(eqs)
    Q1 = {"s_exhaustive_2^20": s}
    if kind == "curve":
        s2, nroots = G.s_route_quadratic(xR, B)
        Q1["s_quadratic_route"] = s2
        Q1["quadratic_route_roots_verified"] = nroots
        Q1["routes_agree"] = bool(s == s2)
        Q1["degenerate"] = bool(xR < (1 << G.L_DIM))
    else:
        Q1["s_quadratic_route"] = None
        Q1["degenerate"] = None
    rec["Q1"] = Q1
    tm["Q1"] = time.time() - t
    # ---- Q2 --------------------------------------------------------------
    t = time.time()
    r3, _, _, _ = G.macaulay_closure(eqs, G.NV, 3)
    r4, bas4, M4, labels = G.macaulay_closure(eqs, G.NV, 4)
    rec["Q2"] = {"M3_shape": r3["shape"], "rank_3": r3["rank"], "one_in_R3": r3["one"],
                 "M4_shape": r4["shape"], "rank_4": r4["rank"], "one_in_R4": r4["one"],
                 "dims_by_deg_M4": r4["dims_by_deg"]}
    tm["Q2"] = time.time() - t
    # ---- Q3 --------------------------------------------------------------
    t = time.time()
    w, basw = G.w_closure_literal(bas4, G.NV, 4)
    rec["Q3"] = {"dims_W_i": w["dims"], "fixpoint_index": w["fixpoint_index"],
                 "one_first_iteration": w["one_first_iteration"], "one_in_W4": w["one"],
                 "final_dim": w["final_dim"], "dims_by_deg_W4": w["dims_by_deg"],
                 "basis_sizes_W_i_cap_B3_multiplied": w["basis_low_sizes"]}
    tm["Q3"] = time.time() - t
    # ---- Q4 --------------------------------------------------------------
    t = time.time()
    rc, aux = G.rc_b(eqs, G.NV, xR if kind == "curve" else None)
    if aux is not None:
        er, er_rank = G.ell_route(bas4, aux["ell"])
        rc["ell_route"] = er
        rc["ell_route_space_dim"] = er_rank
    else:
        rc["ell_route"] = None
        rc["ell_route_note"] = "no ell (rc_b step (1) not applicable)"
    if kind != "curve":
        rc["c_equals_Tr(t^k/x_R^2)"] = None
    rec["Q4"] = rc
    tm["Q4"] = time.time() - t
    # ---- Q7 (optional) -----------------------------------------------------
    t = time.time()
    if rc.get("applicable"):
        wp, _ = G.w_closure_literal(aux["bas4"], G.NV - 1, 4)
        rec["Q7"] = {"W'_4": {"dims_W_i": wp["dims"], "fixpoint_index": wp["fixpoint_index"],
                              "one_first_iteration": wp["one_first_iteration"], "one": wp["one"],
                              "final_dim": wp["final_dim"], "dims_by_deg": wp["dims_by_deg"]},
                     "final_dim_W4_eq_final_dim_W'4_plus_1160": bool(w["final_dim"] == wp["final_dim"] + 1160),
                     "one_agrees": bool(w["one"] == wp["one"]),
                     "required_by_card": kind == "curve"}
    else:
        rec["Q7"] = None
    tm["Q7"] = time.time() - t
    # ---- Q5 / Q6 ---------------------------------------------------------
    t = time.time()
    cert = None
    fmt = None
    if w["one"]:
        fmt = "wdag-v1"
        try:
            cert, st = C.build_wdag(label, eqs, M4, labels, bas4.cols, w)
            ok, why = K.check_wdag(cert, eqs_chk, label)
            rec["Q5"] = {"status": "refuted, witnessed" if ok else "refuted, witness REJECTED by own checker",
                         "construction": st, "check": {"valid": ok, "reason": why}}
            if not ok:
                cert = None
        except Exception as e:
            rec["Q5"] = {"status": "refuted, unwitnessed", "error": "%s: %s" % (type(e).__name__, e)}
        rec["Q6"] = None
    else:
        fmt = "ann-v1"
        try:
            cert, st, Lm = C.build_ann(label, basw)
            ok, why, det = K.check_ann(cert, eqs_chk, label)
            rec["Q6"] = {"status": "not refuted, certified" if ok else "not refuted, certificate REJECTED by own checker",
                         "construction": st, "codim_W4": int(6196 - w["final_dim"]),
                         "check": {"valid": ok, "reason": why, "details": det}}
            if not ok:
                cert = None
        except Exception as e:
            rec["Q6"] = {"status": "not refuted, uncertified", "error": "%s: %s" % (type(e).__name__, e)}
        rec["Q5"] = None
    tm["Q5_Q6"] = time.time() - t
    # ---- internal consistency (not a required quantity) -------------------
    rec["internal_checks"] = {
        "one_M3_implies_one_M4_implies_one_W4": bool((not r3["one"] or r4["one"]) and (not r4["one"] or w["one"])),
        "W4_contains_M4": bool(w["final_dim"] >= r4["rank"] and w["dims"][0] == r4["rank"]),
        "satisfiable_not_refuted": bool(s == 0 or not w["one"]),
        "codim_W4_ge_s": bool((6196 - w["final_dim"]) >= s),
    }
    rec["seconds"] = {k: round(v, 3) for k, v in tm.items()}
    return rec, fmt, cert


def dump_line(obj):
    return json.dumps(obj, separators=(",", ":")).encode()


def write_gz(path, lines):
    with open(path, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as g:
            for ln in lines:
                g.write(ln + b"\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--expect-count", type=int, default=90,
                    help="number of systems the input must hold (90 for the blind inputs; dry runs only differ)")
    args = ap.parse_args()
    out = args.out
    ck = os.path.join(out, "checkpoints")
    os.makedirs(ck, exist_ok=True)
    for f in ("rederivation.json", "wdag.jsonl.gz", "ann.jsonl.gz", "seal.txt"):
        if os.path.exists(os.path.join(out, f)):
            raise SystemExit("refusing to overwrite sealed artifact %s" % f)
    started = utcnow()
    t_all = time.time()
    log("environment")
    env = environment()
    # ---- self-tests before any blind input is read ---------------------------
    st_path = os.path.join(ck, "_selftest.json")
    if args.resume and os.path.exists(st_path):
        selftests = json.load(open(st_path))
        log("self-tests loaded from checkpoint (all_passed=%s)" % selftests["all_passed"])
    else:
        log("self-tests")
        ok, res = ST.run_all()
        selftests = {"all_passed": ok, "seed": ST.SELFTEST_SEED, "started_utc": started,
                     "finished_utc": utcnow(), "results": res}
        with open(st_path, "w") as f:
            json.dump(selftests, f, indent=1, default=str)
    if not selftests["all_passed"]:
        log("SELF-TEST FAILURE: stopping before any blind input is read")
        raise SystemExit(2)
    # ---- blind inputs ---------------------------------------------------------
    inp_sha = sha256_file(args.inputs)
    data = json.load(open(args.inputs))
    assert data["schema"] == "certbin.n19.blind_inputs.v1"
    assert data["field"]["modulus_int"] == F.MOD and data["field"]["n"] == 19
    assert data["m"] == 2 and data["l"] == 10
    A, B = int(data["curve"]["A"]), int(data["curve"]["B"])
    assert (A, B) == (EXPECT_A, EXPECT_B), "curve differs from the specification"
    insts = data["instances"]
    labels = [i["label"] for i in insts]
    assert len(labels) == len(set(labels)) == args.expect_count
    log("inputs sha256 %s, %d systems" % (inp_sha, len(insts)))
    progress = os.path.join(ck, "_progress.log")
    systems = {}
    missing = {}
    for n, inst in enumerate(insts):
        label = inst["label"]
        rp = os.path.join(ck, label + ".json")
        cp = os.path.join(ck, label + ".cert.json.gz")
        if args.resume and os.path.exists(rp):
            rec = json.load(open(rp))
            # re-check the completed system: certificate and s
            recheck = {}
            if os.path.exists(cp):
                with gzip.open(cp, "rb") as g:
                    cert = json.loads(g.read())
                eqs_chk = (K.curve_system(int(inst["x_R"]), B) if inst["kind"] == "curve"
                           else K.explicit_system(inst["equations"]))
                if "nodes" in cert:
                    recheck["certificate"] = list(K.check_wdag(cert, eqs_chk, label))
                else:
                    recheck["certificate"] = list(K.check_ann(cert, eqs_chk, label)[:2])
            eqs_r = (G.descend_S3(int(inst["x_R"]), B) if inst["kind"] == "curve"
                     else parse_explicit_algebra(inst["equations"])[0])
            recheck["s_exhaustive_2^20"] = G.exhaustive_s(eqs_r) == rec["Q1"]["s_exhaustive_2^20"]
            rec.setdefault("resume_rechecks", []).append({"at_utc": utcnow(), **recheck})
            systems[label] = rec
            log("%s resumed from checkpoint %s" % (label, recheck))
            continue
        t0 = time.time()
        try:
            rec, fmt, cert = process_system(inst, B)
        except Exception as e:
            missing[label] = "%s: %s" % (type(e).__name__, e)
            log("%s FAILED: %s\n%s" % (label, e, traceback.format_exc()))
            continue
        rec["completed_utc"] = utcnow()
        rec["peak_rss_mb_so_far"] = round(peak_rss_mb(), 1)
        if cert is not None:
            with open(cp, "wb") as raw:
                with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as g:
                    g.write(dump_line(cert))
        with open(rp, "w") as f:
            json.dump(rec, f, indent=1)
        systems[label] = rec
        with open(progress, "a") as f:
            f.write("%s %s done in %.1fs\n" % (utcnow(), label, time.time() - t0))
        log("[%d/%d] %s done in %.1fs" % (n + 1, len(insts), label, time.time() - t0))
    # ---- assemble -------------------------------------------------------------
    wd_lines, an_lines = [], []
    for inst in insts:
        label = inst["label"]
        cp = os.path.join(ck, label + ".cert.json.gz")
        if label in systems and os.path.exists(cp):
            with gzip.open(cp, "rb") as g:
                line = g.read().strip()
            cert = json.loads(line)
            (wd_lines if "nodes" in cert else an_lines).append(line)
            systems[label]["certificate_line_sha256"] = hashlib.sha256(line).hexdigest()
    cov = {
        "systems_in_inputs": len(insts),
        "systems_computed": len(systems),
        "missing_systems": missing,
        "Q5_wdag_records": len(wd_lines),
        "Q6_ann_records": len(an_lines),
        "refuted_unwitnessed": sorted(l for l, r in systems.items() if r.get("Q5") and r["Q5"]["status"] != "refuted, witnessed"),
        "not_refuted_uncertified": sorted(l for l, r in systems.items() if r.get("Q6") and r["Q6"]["status"] != "not refuted, certified"),
        "s_route_disagreements": sorted(l for l, r in systems.items() if r["kind"] == "curve" and not r["Q1"]["routes_agree"]),
        "construction_cross_check_failures": sorted(
            l for l, r in systems.items()
            if not all(v for k, v in r["construction"].items() if k.startswith("equals"))),
        "internal_check_failures": sorted(l for l, r in systems.items() if not all(r["internal_checks"].values())),
    }
    red = {
        "schema": SCHEMA,
        "task_id": TASK,
        "review_id": data.get("review_id"),
        "joint": "J6",
        "inputs": {"path": os.path.relpath(os.path.abspath(args.inputs), os.path.abspath(os.path.join(out, "..", "..", "..", "..", ".."))),
                   "sha256": inp_sha},
        "conventions": {
            "variables": "v_0..v_19; x_1 = sum_{j<10} v_j t^j, x_2 = sum_{j<10} v_{10+j} t^j",
            "field": "F_2[t]/(t^19+t^5+t^2+t+1), 19-bit integers, bit j = coefficient of t^j",
            "curve": {"A": A, "B": B},
            "column_order": "all multilinear monomials of degree <= D sorted by (-degree, bitmask ascending) (= the ann-v1 coordinate order)",
            "macaulay_rows": "(mu, k), mu over multilinear monomials of degree <= D-2 by degree ascending then ascending sorted index tuple, row index mu_index*19 + k, zero rows retained",
            "dims_by_deg": "dim(X cap B_{<=d}) for d = 0..4 (d = 0..3 for nothing else); counted as echelon rows with leading monomial of degree <= d in the graded column order",
            "one_in_X": "the constant polynomial lies in the F_2-subspace X",
            "W_iteration": "dims_W_i lists dim W^(0), ..., dim W^(i*+1) with i* = fixpoint_index = the first i with dim W^(i+1) = dim W^(i); one_first_iteration = first i with 1 in W^(i) (0 = already in rowspace(M_4)), null if never",
            "E_hex": "E_layout of the specification: 19 hex integers (no 0x prefix), bit j (LSB first) = column j of mu_order(2, 20)",
            "hex_format": "lowercase hexadecimal digits without a 0x prefix (int(s, 16))",
            "wdag_mu": "sorted list of variable indices, [] for the constant monomial",
        },
        "elimination_method": (
            "Own C kernel (code/gf2kern.c), bit-packed incremental semi-echelon basis: every row has a distinct "
            "leading column (its first set coordinate in the degree-descending column order) and a vector is reduced "
            "by XOR-ing the row of its lowest set pivot coordinate until no pivot coordinate is set; a nonzero "
            "remainder is appended. Rank = number of rows; dims_by_deg from leading degrees; '1 in X' iff the "
            "constant column (last) is a pivot. The certificate checkers (code/checkers.py) use a separate numpy "
            "Gauss-Jordan elimination and float32 BLAS parity products and share no code with the kernel."),
        "environment": env,
        "started_utc": started,
        "finished_utc": utcnow(),
        "wall_seconds": round(time.time() - t_all, 1),
        "peak_rss_mb": round(peak_rss_mb(), 1),
        "self_tests": selftests,
        "coverage": cov,
        "systems": {i["label"]: systems[i["label"]] for i in insts if i["label"] in systems},
    }
    amb_path = os.path.join(HERE, "ambiguities.json")
    red["ambiguities"] = json.load(open(amb_path)) if os.path.exists(amb_path) else []
    rp = os.path.join(out, "rederivation.json")
    with open(rp, "w") as f:
        json.dump(red, f, indent=1)
    write_gz(os.path.join(out, "wdag.jsonl.gz"), wd_lines)
    write_gz(os.path.join(out, "ann.jsonl.gz"), an_lines)
    seal_time = utcnow()
    lines = ["# seal of TASK-20260926-f0736e (BR-7): written before report.yaml and attestation.yaml",
             "sealed_utc: %s" % seal_time]
    for f in ("rederivation.json", "wdag.jsonl.gz", "ann.jsonl.gz"):
        lines.append("%s  %s" % (sha256_file(os.path.join(out, f)), f))
    with open(os.path.join(out, "seal.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    log("sealed at %s" % seal_time)
    log("coverage: computed %d/%d, missing %d" % (len(systems), len(insts), len(missing)))


if __name__ == "__main__":
    main()
