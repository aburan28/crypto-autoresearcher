#!/usr/bin/env python3
# =====================================================================
# run_measurements_v4.py — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)
#
# FINAL DRIVER (v4). Supersedes v1/v2/v3 in this task directory, by new
# immutable paths for its logs. Correction lineage, all recorded, none
# discarded; each failure is INFRASTRUCTURE SIGNAL, never negative
# evidence about AES (AGENTS.md rule 5):
#   v1: assumed Linux x86-64 (/proc, -maes) — failed on /proc/cpuinfo.
#   v2: assumed pycryptodome importable — MEASURED ABSENT; RUN-2 crashed
#       because the x86-intrinsic build cannot exist on arm64. Its RUN-1
#       inventory is preserved (run1-inventory.json) and carries the
#       MEASURED -maes compile failure on this host.
#   v3: decoded openssl's BINARY ciphertext as utf-8 text —
#       UnicodeEncodeError. Corrected here: openssl output is captured as
#       RAW BYTES, never decoded.
# Inventory and benchmark ONLY; NO cryptanalysis; asserts nothing about
# AES security at any round count. This artifact is infrastructure and
# is expressly NOT a completion (GOAL-AES-002 non_completion_criteria
# (vi)).
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

import json, os, random, subprocess, sys, time

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(TASK_DIR, "measure_envelope_arm64.c")
BIN_ACC = "/tmp/mea_acc"
BIN_NOACC = "/tmp/mea_noacc"
RUN_T0 = time.time()

def sh(cmd, stdin_text=None, input_bytes=None):
    """Text-mode helper: stdout/stderr decoded utf-8/replace. NEVER used
    on commands whose output is binary."""
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True,
                       input=(input_bytes if input_bytes is not None else (stdin_text.encode() if stdin_text else None)))
    return {"command": cmd, "returncode": p.returncode,
            "stdout": p.stdout.decode("utf-8", "replace"),
            "stderr": p.stderr.decode("utf-8", "replace"),
            "wall_seconds_observed_by_driver": round(time.time() - t0, 4)}

def openssl_ecb_raw(key, pt):
    """openssl CLI ECB single block; output captured as RAW BYTES (the
    ciphertext is binary and must never pass through a text codec)."""
    t0 = time.time()
    p = subprocess.run(["openssl", "enc", "-aes-128-ecb", "-K", key.hex(), "-nopad"],
                       capture_output=True, input=pt)
    rec = {"command": ["openssl", "enc", "-aes-128-ecb", "-K", key.hex(), "-nopad"],
           "returncode": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace"),
           "wall_seconds_observed_by_driver": round(time.time() - t0, 4)}
    return (p.stdout[:16] if p.returncode == 0 else None), rec

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

def cross_check(binpath, tag, log):
    rng = random.Random(0x2A0A37)
    vectors = [(bytes(rng.randrange(256) for _ in range(16)),
                bytes(rng.randrange(256) for _ in range(16))) for _ in range(8)]
    rows = []
    vec_input = ""
    for key, pt in vectors:
        ct, _ = openssl_ecb_raw(key, pt)
        rows.append({"key_hex": key.hex(), "pt_hex": pt.hex(),
                     "openssl_ct_hex": ct.hex() if ct else None})
        vec_input += key.hex() + " " + pt.hex() + "\n"
    c = sh([binpath, "vec"], stdin_text=vec_input)
    c_cts = [line.split("ct=")[1].strip() for line in c["stdout"].splitlines() if line.startswith("VEC")]
    agree = 0
    for i, r in enumerate(rows):
        r["c_ct_hex"] = c_cts[i] if i < len(c_cts) else None
        if r["c_ct_hex"] == r["openssl_ct_hex"]:
            agree += 1
    log[f"cross_check_{tag}"] = {
        "vectors": 8, "seed": "0x2A0A37",
        "independent_implementation": "openssl CLI (enc -aes-128-ecb -nopad)",
        "c_agrees_openssl_cli": agree, "c_vec_mode_raw": c}
    log[f"cross_check_vectors_{tag}"] = rows

def bench_single(binpath, tag, log, plans):
    for mode, n, reps in plans:
        r = sh([binpath, "bench", mode, str(n), str(reps)])
        rec = {"build": tag, "mode": mode, "N": n, "reps": reps, "raw": r}
        parsed = parse_result_lines(r["stdout"])
        rec["parsed"] = parsed
        if parsed:
            rates = [float(p["rate"]) for p in parsed]
            rec["median_rate_evals_per_sec_per_core"] = median(rates)
        log["single_core"].append(rec)

def bench_multi(binpath, tag, log, procs, plans):
    for mode, n in plans:
        t0 = time.time()
        pops = [subprocess.Popen([binpath, "bench", mode, str(n), "1"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(procs)]
        outs = []
        for p in pops:
            so, se = p.communicate()
            outs.append({"returncode": p.returncode, "stdout": so.decode(), "stderr": se.decode()})
        wall = time.time() - t0
        parsed_all = [parse_result_lines(o["stdout"]) for o in outs]
        agg = (n * procs) / wall
        single = None
        for rec in log["single_core"]:
            if rec["mode"] == mode and rec["build"] == tag:
                single = rec.get("median_rate_evals_per_sec_per_core")
        log["multi_core"].append({
            "mode": mode, "build": tag, "processes": procs, "N_per_process": n,
            "wall_seconds_observed_by_driver": round(wall, 4),
            "aggregate_evals_per_sec_over_all_cores": agg,
            "single_core_median_for_same_mode": single,
            "measured_scaling_factor_vs_single_core": (agg / single) if single else None,
            "per_process_raw": outs, "per_process_parsed": parsed_all})

def run2():
    log = {"run": ("RUN-2 (v4) accelerated AES throughput on the measured host, "
                   "arm64-native build (armv8.6-a+crypto), plus no-acceleration control; "
                   "x86-64 -maes DOES NOT COMPILE on this host (measured, see run1-inventory.json)"),
           "single_core": [], "multi_core": []}
    cross_check(BIN_ACC, "acc_build", log)
    cross_check(BIN_NOACC, "noacc_build", log)
    bench_single(BIN_ACC, "acc", log,
                 [("fresh", 20000000, 3), ("dep", 20000000, 3), ("ind", 100000000, 3)])
    bench_single(BIN_NOACC, "noacc", log,
                 [("dep", 2000000, 3), ("fresh", 200000, 3)])
    procs = os.cpu_count() or 1
    log["multi_core_processes_used"] = procs
    bench_multi(BIN_ACC, "acc", log, procs,
                [("fresh", 20000000), ("ind", 100000000)])
    log["driver_wall_seconds_total"] = round(time.time() - RUN_T0, 3)
    with open(os.path.join(TASK_DIR, "run2-aesni.json"), "w") as f:
        json.dump(log, f, indent=2)
    print("WROTE run2-aesni.json")

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
    log = {"run": ("RUN-3 (v4) pure-Python AES-128 throughput on the measured host. "
                   "pycryptodome is MEASURED ABSENT in this session's interpreters "
                   "(see run1-inventory.json); the independent implementation used "
                   "for cross-checking is the openssl CLI."),
           "steps": []}
    rng = random.Random(0x2A0A37)
    vectors = [(bytes(rng.randrange(256) for _ in range(16)),
                bytes(rng.randrange(256) for _ in range(16))) for _ in range(4)]
    rows = []
    for key, pt in vectors:
        w = expand_key128(key)
        pyaes_ct = encrypt_block(pt, w)
        ct, _ = openssl_ecb_raw(key, pt)
        rows.append({"key_hex": key.hex(), "pt_hex": pt.hex(),
                     "pure_python_ct_hex": pyaes_ct.hex(),
                     "openssl_ct_hex": ct.hex() if ct else None,
                     "pure_python_agrees_openssl": pyaes_ct == ct})
    log["pure_python_cross_check"] = {"vectors": 4, "rows": rows,
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
        log["steps"].append({"benchmark": label, "reps": reps,
                             "median_rate": median([r["rate_evals_per_sec_per_core"] for r in reps])})
    log["driver_wall_seconds_total"] = round(time.time() - RUN_T0, 3)
    with open(os.path.join(TASK_DIR, "run3-python.json"), "w") as f:
        json.dump(log, f, indent=2)
    print("WROTE run3-python.json")

if __name__ == "__main__":
    print("RUN-2 starting"); run2()
    print("RUN-3 starting"); run3()
    print("ALL RUNS COMPLETE in %.1f s (driver wall)" % (time.time() - RUN_T0))
