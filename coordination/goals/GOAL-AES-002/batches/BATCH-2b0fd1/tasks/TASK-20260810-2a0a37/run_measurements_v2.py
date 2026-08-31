#!/usr/bin/env python3
# =====================================================================
# run_measurements_v2.py — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)
#
# CORRECTED DRIVER, superseding run_measurements.py IN THIS TASK DIRECTORY
# ONLY, by new path (artifacts are immutable; a correction is a new path).
# run_measurements.py assumed a Linux host with /proc and x86-64 gcc
# supporting -maes; it failed on /proc/cpuinfo at RUN-1 step 1. The
# failure is recorded in this task's logs as infrastructure signal
# (specification_error against the observed host), never as negative
# evidence about AES (AGENTS.md rule 5).
#
# HOST AS MEASURED (RUN-1 v2): Darwin 25.6.0, arm64, Apple M4 Pro,
# 14 online cores, 48 GB physical RAM. This host has NO /proc and its
# gcc is Apple clang targeting arm64, on which -maes is not a supported
# flag. THE AES-NI PATH IS THEREFORE MEASURED ON ARM64 EQUIVALENTS:
#   - the C benchmark is built with -march=armv8.6-a+crypto (Arm Cryptography
#     Extension; vaeseq_u128/vaesmcq_u128 are the arm64 counterparts of
#     _mm_aesenc_si128), AND is also built with NO crypto flags as the
#     no-acceleration control.
#   - x86-64 -maes IS NOT MEASURED ON THIS HOST AND CANNOT BE: the host
#     cannot execute x86-64 binaries. That is an infrastructure fact
#     about this host, not evidence about any toolchain elsewhere
#     (AGENTS.md rule 5, task constraint on infrastructure signal).
#
# Inventory and benchmark ONLY; NO cryptanalysis; asserts nothing about
# AES security at any round count; infrastructure failures are
# infrastructure signal. This artifact is infrastructure and is
# expressly NOT a completion (GOAL-AES-002 non_completion_criteria (vi)).
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
# -----------------------------------------------------------------------
# =====================================================================

import json, os, platform, random, shutil, subprocess, sys, time

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
C_SRC = os.path.join(TASK_DIR, "measure_envelope.c")
BIN_ACC = "/tmp/measure_env_2a0a37_acc"     # arm64 crypto-extension build
BIN_NOACC = "/tmp/measure_env_2a0a37_noacc"  # no-acceleration control build
BIN_XMAES = "/tmp/measure_env_2a0a37_xmaes"  # -maes build attempt (x86 flag on arm64)
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

def sysctl(name):
    r = sh(["sysctl", "-n", name])
    return {"name": name, "stdout": r["stdout"].strip(), "returncode": r["returncode"]}

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
    return xs[len(xs) // 2]

# ----------------------------- RUN 1 ---------------------------------

def run1():
    log = {"run": "RUN-1 (v2) toolchain-and-environment inventory, corrected for the measured host",
           "supersedes": "run_measurements.py RUN-1, which failed on /proc/cpuinfo; that failure is recorded below as infrastructure signal",
           "prior_driver_failure_infrastructure_signal": {
               "file": "run_measurements.py",
               "failure": "FileNotFoundError: /proc/cpuinfo — driver assumed a Linux host; the measured host is Darwin/arm64",
               "classification": "specification_error/infrastructure_error",
               "not_evidence_about": "AES at any round count (AGENTS.md rule 5)"
           },
           "steps": []}

    log["python_version"] = sys.version
    log["platform_platform"] = platform.platform()
    log["os_uname"] = [os.uname().sysname, os.uname().nodename, os.uname().release,
                       os.uname().version, os.uname().machine]
    log["os_cpu_count"] = os.cpu_count()
    log["sched_getaffinity_available"] = hasattr(os, "sched_getaffinity")
    if hasattr(os, "sched_getaffinity"):
        log["sched_getaffinity_count"] = len(os.sched_getaffinity(0))

    for nm in ["hw.model", "machdep.cpu.brand_string", "hw.ncpu", "hw.physicalcpu",
               "hw.performancecorecount", "hw.efficiencycorecount", "hw.memsize",
               "hw.ncpu.max"]:
        log["steps"].append(sysctl(nm))

    phys = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else None
    log["sysconf_physical_bytes"] = phys
    log["sysconf_physical_gb"] = round(phys / 1e9, 3) if phys else None
    # usable RAM estimate via VM statistics (free + inactive + purgable pages)
    vm = sh(["vm_stat"])
    log["steps"].append({"step": "vm_stat", **vm})
    usable = None
    if vm["returncode"] == 0:
        ps = 16384
        free = spec = purg = 0
        try:
            for line in vm["stdout"].splitlines():
                if "Pages free" in line:
                    free = int(line.split(":")[1].strip().rstrip("."))
                if "Pages speculative" in line:
                    spec = int(line.split(":")[1].strip().rstrip("."))
                if "Pages purgable" in line:
                    purg = int(line.split(":")[1].strip().rstrip("."))
            usable = (free + spec + purg) * ps
        except Exception as e:
            log["vm_stat_parse_error"] = repr(e)
    log["usable_ram_estimate_bytes_from_vm_stat"] = usable
    log["usable_ram_estimate_gb_from_vm_stat"] = round(usable / 1e9, 3) if usable else None
    log["usable_ram_method"] = ("free + speculative + purgable pages from vm_stat times 16384-byte "
                                "page size, a snapshot at measurement time; alternative conventions "
                                "(adding compressed/wired, or counting inactive pages) would give a "
                                "larger figure; the figure recorded here is the CONSERVATIVE one")

    try:
        import Crypto
        from Crypto.Cipher import AES  # noqa
        log["pycryptodome_importable"] = True
        log["pycryptodome_version"] = Crypto.__version__
    except Exception as e:
        log["pycryptodome_importable"] = False
        log["pycryptodome_import_error"] = repr(e)

    try:
        import numpy  # noqa
        log["numpy_importable"] = True
        log["numpy_version"] = numpy.__version__
    except Exception as e:
        log["numpy_importable"] = False
        log["numpy_import_error"] = repr(e)

    gcc = shutil.which("gcc")
    log["gcc_path"] = gcc
    if gcc:
        log["steps"].append({"step": "gcc --version", **sh([gcc, "--version"])})
        log["steps"].append({"step": "gcc -dumpmachine (target triple)", **sh([gcc, "-dumpmachine"])})
        log["steps"].append({"step": "gcc -print-search-dirs (excerpt)", **sh([gcc, "-print-search-dirs"])})

    # THE MEASURED POINT OF THE CONTRADICTION: does -maes compile HERE?
    log["steps"].append({"step": "compile WITH x86 flag -maes on this host (THE POINT OF THE CONTRADICTION, MEASURED)",
                         **sh([gcc, "-O3", "-maes", "-o", BIN_XMAES, C_SRC])})
    # arm64 crypto-extension build (the counterpart path on this host)
    log["steps"].append({"step": "compile WITH -march=armv8.6-a+crypto (arm64 crypto extension)",
                         **sh([gcc, "-O3", "-march=armv8.6-a+crypto", "-o", BIN_ACC, C_SRC])})
    # no-acceleration control build
    log["steps"].append({"step": "compile WITHOUT any AES acceleration flags (control)",
                         **sh([gcc, "-O3", "-o", BIN_NOACC, C_SRC])})

    for binpath, label in [(BIN_ACC, "arm64-crypto build"), (BIN_NOACC, "no-acceleration control build")]:
        if os.path.exists(binpath):
            log["steps"].append({"step": f"run {label}: selftest", **sh([binpath, "selftest"])})
            rng = random.Random(0x2A0A37)
            from Crypto.Cipher import AES as _AES
            vectors = [(bytes(rng.randrange(256) for _ in range(16)),
                        bytes(rng.randrange(256) for _ in range(16))) for _ in range(8)]
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
            c = sh([binpath, "vec"], stdin_text=vec_input)
            c_cts = [line.split("ct=")[1].strip() for line in c["stdout"].splitlines() if line.startswith("VEC")]
            agree_py = agree_ossl = 0
            for i, r in enumerate(rows):
                r["c_ct_hex"] = c_cts[i] if i < len(c_cts) else None
                if r["c_ct_hex"] == r["pycryptodome_ct_hex"]:
                    agree_py += 1
                if r["openssl_ct_hex"] is not None and r["c_ct_hex"] == r["openssl_ct_hex"]:
                    agree_ossl += 1
            log[f"cross_check_{label.replace(' ', '_').replace('-', '_')}"] = {
                "vectors": 8, "seed": "0x2A0A37",
                "c_agrees_pycryptodome": agree_py, "c_agrees_openssl_cli": agree_ossl,
                "c_vec_mode_raw": c}
            log[f"cross_check_vectors_{label.replace(' ', '_').replace('-', '_')}"] = rows

    o = sh(["openssl", "version"])
    log["openssl_version_raw"] = o
    log["steps"].append(o)
    write_log("run1-inventory.json", log)

# ----------------------------- RUN 2 ---------------------------------

def run2():
    log = {"run": "RUN-2 (v2) accelerated AES throughput on the measured host (arm64 crypto extension), plus no-acceleration control",
           "single_core": [], "multi_core": []}
    plans = [(BIN_ACC, "fresh", 20000000, 3),
             (BIN_ACC, "dep", 20000000, 3),
             (BIN_ACC, "ind", 100000000, 3),
             (BIN_NOACC, "dep", 2000000, 3)]
    for binpath, mode, n, reps in plans:
        tag = os.path.basename(binpath).replace("measure_env_2a0a37_", "")
        r = sh([binpath, "bench", mode, str(n), str(reps)])
        rec = {"build": tag, "mode": mode, "N": n, "reps": reps, "raw": r}
        parsed = parse_result_lines(r["stdout"])
        rec["parsed"] = parsed
        if parsed:
            rates = [float(p["rate"]) for p in parsed]
            rec["median_rate_evals_per_sec_per_core"] = median(rates)
        log["single_core"].append(rec)

    procs = os.cpu_count() or 1
    log["multi_core_processes_used"] = procs
    for mode, n in [("fresh", 20000000), ("ind", 100000000)]:
        t0 = time.time()
        pops = [subprocess.Popen([BIN_ACC, "bench", mode, str(n), "1"],
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
            if rec["mode"] == mode and rec["build"] == "acc":
                single = rec.get("median_rate_evals_per_sec_per_core")
        log["multi_core"].append({
            "mode": mode, "build": "acc", "processes": procs, "N_per_process": n,
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
    log = {"run": "RUN-3 (v2) pure-Python and pinned-implementation throughput on the measured host"}
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
        log.setdefault("steps", []).append({"benchmark": label, "reps": reps,
                                            "median_rate": median([r["rate_evals_per_sec_per_core"] for r in reps])})

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
                             "note": "pycryptodome is C/native-backed, NOT pure Python; recorded as the pinned FIPS-197-verified implementation of RQ-AES-002, for CM-1 context"})
    write_log("run3-python.json", log)

if __name__ == "__main__":
    print("RUN-1 starting"); run1()
    print("RUN-2 starting"); run2()
    print("RUN-3 starting"); run3()
    print("ALL RUNS COMPLETE in %.1f s (driver wall)" % (time.time() - RUN_T0))
