#!/usr/bin/env python3
# =====================================================================
# run_measurements.py — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)
#
# Driver for the three measurement runs of this task. Inventory and
# benchmark ONLY; NO cryptanalysis; asserts nothing about AES at any
# round count; infrastructure failures are infrastructure signal, never
# negative mathematical evidence about AES (AGENTS.md rule 5). This
# artifact is infrastructure and is expressly NOT a completion
# (GOAL-AES-002 non_completion_criteria (vi)).
#
# ------------------- COMMENT-BLOCK INFERENCE STANZA -------------------
# authored_by_task: TASK-20260810-2a0a37
# authored_by_role: executor
# handoff_inference_policy: executor-implementation
# handoff_reasoning_effort: null (policy default)
# fallback_used: false
# degraded_allowed: false
# degraded_requirements: []
# resolved_model_id: null (not surfaced by this runtime; unverified
#   configuration until a doctor --probe confirms a backend serves it)
# resolved_runtime: claude-code session (api_direct-equivalent tool set)
# bedrock: NOT selected, configured, probed or contacted, and never may
#   be (AGENTS.md rule 16; task constraint SC-11)
# claim_tier_of_this_artifact: infrastructure measurement only; states
#   no margin and no cryptanalytic claim; R5 of RQ-AES-002 binds any
#   later record that quotes these numbers in a margin.
# ---------------------------------------------------------------------
# =====================================================================

import json, os, platform, random, shutil, subprocess, sys, time

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
C_SRC = os.path.join(TASK_DIR, "measure_envelope.c")
BIN = "/tmp/measure_envelope_2a0a37"
RUN_T0 = time.time()

def sh(cmd, stdin_text=None, input_bytes=None):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True,
                       input=(input_bytes if input_bytes is not None else (stdin_text.encode() if stdin_text else None)))
    return {
        "command": cmd,
        "returncode": p.returncode,
        "stdout": p.stdout.decode("utf-8", "replace"),
        "stderr": p.stderr.decode("utf-8", "replace"),
        "wall_seconds_observed_by_driver": round(time.time() - t0, 4),
    }

def write_log(name, payload):
    payload["driver_wall_seconds_total"] = round(time.time() - RUN_T0, 3)
    path = os.path.join(TASK_DIR, name)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=False)
    print("WROTE", path)

# ----------------------------- RUN 1 ---------------------------------

def run1():
    log = {"run": "RUN-1 toolchain-and-environment inventory", "steps": []}

    log["python_version"] = sys.version
    log["platform"] = platform.platform()
    cpuinfo_model = None
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("model name"):
                cpuinfo_model = line.split(":", 1)[1].strip()
                break
    log["cpuinfo_model_name"] = cpuinfo_model
    log["os_cpu_count"] = os.cpu_count()
    log["sched_getaffinity_count"] = len(os.sched_getaffinity(0))

    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            parts = line.split()
            if parts and parts[0].rstrip(":") in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
                mem[parts[0].rstrip(":")] = int(parts[1]) * 1024  # kB -> bytes
    log["proc_meminfo_bytes"] = mem

    try:
        import Crypto
        from Crypto.Cipher import AES
        log["pycryptodome_version"] = Crypto.__version__
        log["pycryptodome_importable"] = True
    except Exception as e:
        log["pycryptodome_importable"] = False
        log["pycryptodome_import_error"] = repr(e)

    try:
        import numpy
        log["numpy_importable"] = True
        log["numpy_version"] = numpy.__version__
    except Exception as e:
        log["numpy_importable"] = False
        log["numpy_import_error"] = repr(e)

    gcc = shutil.which("gcc")
    log["gcc_path"] = gcc
    if gcc:
        log["steps"].append({"step": "gcc --version", **sh([gcc, "--version"])})

    log["steps"].append({"step": "compile WITH -maes -msse4.1",
                         **sh(["gcc", "-O3", "-maes", "-msse4.1", "-o", BIN, C_SRC])})
    log["steps"].append({"step": "compile WITHOUT -maes (control)",
                         **sh(["gcc", "-O3", "-o", BIN + "_nomaes", C_SRC])})

    if os.path.exists(BIN):
        log["steps"].append({"step": "run compiled binary: selftest", **sh([BIN, "selftest"])})
        # cross-check on random vectors against two independent implementations
        rng = random.Random(0x2A0A37)
        vectors = [(bytes(rng.randrange(256) for _ in range(16)),
                    bytes(rng.randrange(256) for _ in range(16))) for _ in range(8)]
        from Crypto.Cipher import AES as _AES
        rows = []
        for key, pt in vectors:
            py_ct = _AES.new(key, _AES.MODE_ECB).encrypt(pt)
            o = sh(["openssl", "enc", "-aes-128-ecb", "-K", key.hex(), "-nopad"], input_bytes=pt)
            ossl_ct = o["stdout"].encode("latin-1")[:16] if o["returncode"] == 0 else None
            rows.append({"key_hex": key.hex(), "pt_hex": pt.hex(),
                         "pycryptodome_ct_hex": py_ct.hex(),
                         "openssl_ct_hex": ossl_ct.hex() if ossl_ct else None,
                         "openssl_returncode": o["returncode"]})
        vec_input = "".join(r["key_hex"] + " " + r["pt_hex"] + "\n" for r in rows)
        c = sh([BIN, "vec"], stdin_text=vec_input)
        c_cts = [line.split("ct=")[1].strip() for line in c["stdout"].splitlines() if line.startswith("VEC")]
        agree_py = agree_ossl = agree_ossl_py = 0
        for i, r in enumerate(rows):
            r["c_ct_hex"] = c_cts[i] if i < len(c_cts) else None
            if r["c_ct_hex"] == r["pycryptodome_ct_hex"]:
                agree_py += 1
            if r["openssl_ct_hex"] is not None:
                if r["c_ct_hex"] == r["openssl_ct_hex"]:
                    agree_ossl += 1
                if r["pycryptodome_ct_hex"] == r["openssl_ct_hex"]:
                    agree_ossl_py += 1
        log["cross_check"] = {
            "vectors": 8, "seed": "0x2A0A37",
            "c_agrees_pycryptodome": agree_py,
            "c_agrees_openssl_cli": agree_ossl,
            "pycryptodome_agrees_openssl_cli": agree_ossl_py,
            "c_vec_mode_raw": c,
        }
        log["cross_check_vectors"] = rows

    o = sh(["openssl", "version"])
    log["openssl_version_raw"] = o
    write_log("run1-inventory.json", log)

# ----------------------------- RUN 2 ---------------------------------

def parse_result_lines(stdout):
    out = []
    for line in stdout.splitlines():
        if line.startswith("RESULT"):
            d = {}
            for tok in line.split()[1:]:
                k, _, v = tok.partition("=")
                d[k] = v
            out.append(d)
    return out

def median(xs):
    xs = sorted(xs)
    return xs[len(xs)//2]

def run2():
    log = {"run": "RUN-2 AES-NI throughput (compiled measure_envelope.c)", "single_core": [], "multi_core": []}
    plans = [("fresh", 20000000, 3), ("dep", 20000000, 3), ("ind", 100000000, 3)]
    for mode, n, reps in plans:
        r = sh([BIN, "bench", mode, str(n), str(reps)])
        rec = {"mode": mode, "N": n, "reps": reps, "raw": r}
        parsed = parse_result_lines(r["stdout"])
        rec["parsed"] = parsed
        if parsed:
            rates = [float(p["rate"]) for p in parsed]
            rec["median_rate_evals_per_sec_per_core"] = median(rates)
        log["single_core"].append(rec)

    procs = os.cpu_count() or 1
    for mode, n in [("fresh", 20000000), ("ind", 100000000)]:
        t0 = time.time()
        pops = [subprocess.Popen([BIN, "bench", mode, str(n), "1"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(procs)]
        outs = []
        for p in pops:
            so, se = p.communicate()
            outs.append({"returncode": p.returncode, "stdout": so.decode(), "stderr": se.decode()})
        wall = time.time() - t0
        parsed_all = [parse_result_lines(o["stdout"]) for o in outs]
        total_n = n * procs
        agg = total_n / wall
        single = None
        for rec in log["single_core"]:
            if rec["mode"] == mode:
                single = rec.get("median_rate_evals_per_sec_per_core")
        log["multi_core"].append({
            "mode": mode, "processes": procs, "N_per_process": n,
            "wall_seconds_observed_by_driver": round(wall, 4),
            "aggregate_evals_per_sec_over_all_cores": agg,
            "single_core_median_for_same_mode": single,
            "measured_scaling_factor_vs_single_core": (agg / single) if single else None,
            "per_process_raw": outs, "per_process_parsed": parsed_all,
        })
    write_log("run2-aesni.json", log)

# ----------------------------- RUN 3 ---------------------------------

SBOX = None
RC = []
SHIFT = None

def _gmul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p

def _init_tables():
    global SBOX, RC, SHIFT
    SBOX = [0] * 256
    for x in range(256):
        inv = 0
        if x:
            for y in range(1, 256):
                if _gmul(x, y) == 1:
                    inv = y
                    break
        r = 0x63 ^ inv
        t = inv
        for _ in range(4):
            t = ((t << 1) | (t >> 7)) & 0xFF
            r ^= t
        SBOX[x] = r
    rc = 1
    for _ in range(10):
        RC.append(rc)
        rc = _gmul(rc, 2)
    SHIFT = [0] * 16
    for i in range(16):
        rrow, col = i % 4, i // 4
        SHIFT[4 * col + rrow] = 4 * ((col + rrow) % 4) + rrow

def expand_key128(key):
    w = bytearray(key)
    rci = 0
    for i in range(16, 176, 4):
        t = [w[i-4], w[i-3], w[i-2], w[i-1]]
        if i % 16 == 0:
            f = t[0]
            t = [SBOX[t[1]] ^ RC[rci], SBOX[t[2]], SBOX[t[3]], SBOX[f]]
            rci += 1
        for j in range(4):
            w.append((w[i-16+j] ^ t[j]) & 0xFF)
    return bytes(w)

def encrypt_block(pt, w):
    s = [pt[i] ^ w[i] for i in range(16)]
    for rnd in range(1, 10):
        s = [SBOX[b] for b in s]
        s = [s[SHIFT[j]] for j in range(16)]
        out = [0] * 16
        for c in range(4):
            a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
            out[4*c+0] = _gmul(a0, 2) ^ _gmul(a1, 3) ^ a2 ^ a3
            out[4*c+1] = a0 ^ _gmul(a1, 2) ^ _gmul(a2, 3) ^ a3
            out[4*c+2] = a0 ^ a1 ^ _gmul(a2, 2) ^ _gmul(a3, 3)
            out[4*c+3] = _gmul(a0, 3) ^ a1 ^ a2 ^ _gmul(a3, 2)
        rk = w[16*rnd:16*rnd+16]
        s = [out[i] ^ rk[i] for i in range(16)]
    s = [SBOX[b] for b in s]
    s = [s[SHIFT[j]] for j in range(16)]
    rk = w[160:176]
    return bytes(s[i] ^ rk[i] for i in range(16))

def run3():
    _init_tables()
    log = {"run": "RUN-3 pure-Python and pinned-implementation throughput", "steps": []}
    from Crypto.Cipher import AES as _AES

    rng = random.Random(0x2A0A37)
    vectors = [(bytes(rng.randrange(256) for _ in range(16)),
                bytes(rng.randrange(256) for _ in range(16))) for _ in range(4)]
    rows = []
    for key, pt in vectors:
        w = expand_key128(key)
        pyaes_ct = encrypt_block(pt, w)
        pcd_ct = _AES.new(key, _AES.MODE_ECB).encrypt(pt)
        o = sh(["openssl", "enc", "-aes-128-ecb", "-K", key.hex(), "-nopad"], input_bytes=pt)
        ossl_ct = o["stdout"].encode("latin-1")[:16] if o["returncode"] == 0 else None
        rows.append({"key_hex": key.hex(), "pt_hex": pt.hex(),
                     "pure_python_ct_hex": pyaes_ct.hex(),
                     "pycryptodome_ct_hex": pcd_ct.hex(),
                     "openssl_ct_hex": ossl_ct.hex() if ossl_ct else None,
                     "pure_python_agrees_pycryptodome": pyaes_ct == pcd_ct,
                     "pure_python_agrees_openssl": pyaes_ct == ossl_ct})
    log["pure_python_cross_check"] = {"vectors": 4, "rows": rows,
        "all_agree_pycryptodome": all(r["pure_python_agrees_pycryptodome"] for r in rows),
        "all_agree_openssl": all(r["pure_python_agrees_openssl"] for r in rows)}

    # pure-Python fresh-key benchmark (expand + encrypt each iteration)
    key0 = bytes(range(16)); pt0 = bytes(0x10 + i for i in range(16))
    for n, label in [(500, "pure_python_fresh"), (1000, "pure_python_amortised")]:
        reps = []
        for rep in range(3):
            acc = 0
            t0 = time.perf_counter()
            if label.endswith("fresh"):
                for i in range(n):
                    kk = bytearray(key0); kk[0] = i & 0xFF; kk[1] = (i >> 8) & 0xFF
                    acc ^= int.from_bytes(encrypt_block(pt0, expand_key128(bytes(kk))), "big")
            else:
                w = expand_key128(key0)
                for i in range(n):
                    p = bytearray(pt0); p[0] = i & 0xFF
                    acc ^= int.from_bytes(encrypt_block(bytes(p), w), "big")
            el = time.perf_counter() - t0
            reps.append({"rep": rep + 1, "n": n, "elapsed_s": round(el, 6),
                         "rate_evals_per_sec_per_core": round(n / el, 4), "acc": acc})
        log["steps"].append({"benchmark": label, "reps": reps,
                             "median_rate": median([r["rate_evals_per_sec_per_core"] for r in reps])})

    # pinned implementation (pycryptodome, C-backed) for context
    for n, label in [(200000, "pycryptodome_fresh"), (500000, "pycryptodome_amortised")]:
        reps = []
        for rep in range(3):
            acc = 0
            t0 = time.perf_counter()
            if label.endswith("fresh"):
                for i in range(n):
                    kk = bytearray(key0); kk[0] = i & 0xFF; kk[1] = (i >> 8) & 0xFF
                    acc ^= int.from_bytes(_AES.new(bytes(kk), _AES.MODE_ECB).encrypt(pt0), "big")
            else:
                c = _AES.new(key0, _AES.MODE_ECB)
                for i in range(n):
                    p = bytearray(pt0); p[0] = i & 0xFF
                    acc ^= int.from_bytes(c.encrypt(bytes(p)), "big")
            el = time.perf_counter() - t0
            reps.append({"rep": rep + 1, "n": n, "elapsed_s": round(el, 6),
                         "rate_evals_per_sec_per_core": round(n / el, 4), "acc": acc})
        log["steps"].append({"benchmark": label, "reps": reps,
                             "median_rate": median([r["rate_evals_per_sec_per_core"] for r in reps]),
                             "note": "pycryptodome is C-backed native code, NOT pure Python; recorded as the pinned FIPS-197-verified implementation of RQ-AES-002, for CM-1 context"})
    write_log("run3-python.json", log)

if __name__ == "__main__":
    print("RUN-1 starting"); run1()
    print("RUN-2 starting"); run2()
    print("RUN-3 starting"); run3()
    print("ALL RUNS COMPLETE in %.1f s (driver wall)" % (time.time() - RUN_T0))
