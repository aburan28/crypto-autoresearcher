#!/usr/bin/env python3
"""automation_runner.py — EXP-SIG-007 rank5 relaunch wrapper (Blueprint code Automation entry).

Runs the SIG7_run.sage resume command in fires (one sage subprocess per fire),
looping while wall budget remains. Enforces an RSS self-abort and prints exactly
one JSON status line per fire plus one final summary line.

Layout contract (learned the hard way — do not change casually):
  * driver lives at experiments/EXP-SIG-007/runtime/SIG7_run.sage (git blob
    34ce16d5 from branch coordinator/sig-dreg-frontier-20260724, identical to
    the instrument that produced runs a..aa; see runtime/DRIVER_BLOB_PIN.txt)
  * driver computes EXPDIR = Path(--out).resolve().parents[2] and loads
    EXPDIR/src/*.  Therefore every fire's --out is
    experiments/EXP-SIG-007/fires/fire_NNN/raw.json  =>  EXPDIR = EXP-SIG-007,
    where src/ holds the 4 pinned files (subset-hash check, AppleDouble-safe).
  * --work may point anywhere (production: work/n21_s1; smoke: scratch copy).

State self-healing: if <work>/rank5/state.json is missing but carry_*.pkl files
and RECOVERY.json exist, the runner rebuilds state.json (npiv per carry scanned
from pickle streams; anchor values from RECOVERY.json) before the first fire.

Config precedence: JSON file at argv[1] > $RUNNER_CONFIG_JSON > stdin JSON
(if non-TTY and parses) > built-in defaults (production-correct).

Every stdout line beginning with "{" is a status object with field "kind":
  "rebuild" — checkpoint state.json was rebuilt from carries + RECOVERY.json
  "fire"    — a sage fire finished (check exit_code)
  "abort"   — RSS limit tripped; process group killed; wrapper stops
  "done"    — staircase reached ncols; measurement complete
  "summary" — final line; suitable as the Automation artifact payload
"""
import glob, json, os, pickletools, subprocess, sys, time, signal, hashlib

REPO = os.path.dirname(os.path.abspath(__file__))          # experiments/EXP-SIG-007
ROOT = os.path.abspath(os.path.join(REPO, "..", ".."))     # repo root

DEFAULTS = {
    "n": 21,
    "seed": 1,
    "work": "experiments/EXP-SIG-007/work/n21_s1",
    "driver": "experiments/EXP-SIG-007/runtime/SIG7_run.sage",
    "fire_budget": 3300,       # sage --budget per fire (s)
    "wall_budget": 3540,       # wrapper total wall limit (s); stays < timeoutMs
    "rss_limit_gb": 20.0,      # self-abort threshold for the sage process tree
    "chunk_force": 5000,
    "max_units": 0,            # 0 = unlimited; fire budget governs
    "min_next_fire": 900,      # don't open a new fire with less wall remaining
    "poll_s": 5,
    "fires_dir": "experiments/EXP-SIG-007/fires",  # repo-relative; EXPDIR-safe
    "allow_state_rebuild": True,
}

def log(msg):
    print("[runner %.1f] %s" % (time.time() - T0, msg), flush=True)

LAST_EMIT = {}

def emit(kind, **kw):
    d = {"kind": kind, "t": round(time.time() - T0, 1)}
    d.update(kw)
    if kind == "summary":
        LAST_EMIT.clear()
        LAST_EMIT.update(d)
    print(json.dumps(d, sort_keys=True), flush=True)

def load_config():
    cfg = dict(DEFAULTS)
    cands = []
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        cands.append(("argv1", open(sys.argv[1]).read()))
    if os.environ.get("RUNNER_CONFIG_JSON"):
        cands.append(("env", os.environ["RUNNER_CONFIG_JSON"]))
    if not os.environ.get("RUNNER_CONFIG_JSON") and not sys.stdin.isatty():
        try:
            data = sys.stdin.read()
            if data and data.strip():
                cands.append(("stdin", data))
        except Exception:
            pass
    for src, text in cands:
        try:
            user = json.loads(text)
            cfg.update({k: v for k, v in user.items() if v is not None})
            log("config loaded from %s: %s" % (src, json.dumps(user, sort_keys=True)[:400]))
            break
        except Exception as e:
            log("config candidate %s ignored: %s" % (src, e))
    # Blueprint runtime nests Automation.run runInput under a top-level
    # "input" key in the injected env config; give it highest precedence.
    if isinstance(cfg.get("input"), dict):
        cfg.update({k: v for k, v in cfg["input"].items() if v is not None})
        log("runInput merged: %s" % json.dumps(cfg["input"], sort_keys=True)[:300])
    return cfg

def scan_carry_npiv(path):
    """npiv of a carry pickle without sage: nrows=279048 marker int, next int = H.ncols()."""
    prev = None
    for op, arg, pos in pickletools.genops(open(path, "rb").read()):
        if op.name in ("BININT", "BININT1", "BININT2", "INT", "LONG1", "LONG4") and isinstance(arg, int):
            if prev == 279048 and arg < 1000000:
                return arg
            prev = arg
    raise RuntimeError("npiv marker not found in %s" % path)

def rebuild_state_if_missing(work_abs):
    r5 = os.path.join(work_abs, "rank5")
    sp = os.path.join(r5, "state.json")
    if os.path.exists(sp):
        return False
    recp = os.path.join(r5, "RECOVERY.json")
    carries = sorted(glob.glob(os.path.join(r5, "carry_*.pkl")))
    if not (carries and os.path.exists(recp)):
        return False
    rec = json.load(open(recp))
    log("state.json missing — rebuilding from %d carries + RECOVERY.json" % len(carries))
    entries, units, cum = [], [], 0
    for p in carries:
        k = scan_carry_npiv(p)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        entries.append({"file": os.path.basename(p), "npiv": k, "sha256": h})
        cum += k
        units.append({"j0": None, "j1": None, "k": k, "rank_acc": cum, "tm": {}, "reconstructed": True})
    assert cum == rec["rank_acc"], "rebuild mismatch: sum(npiv)=%d != RECOVERY rank_acc=%d" % (cum, rec["rank_acc"])
    st = {"tag": "rank5", "nrows": rec.get("nrows", 279048), "ncols": rec.get("ncols", 778394),
          "next_col": rec["next_col"], "rank_acc": rec["rank_acc"], "carries": entries,
          "done": False, "rate_mat": 2.0e12, "secs_total": rec.get("secs_total", 0.0),
          "units": units, "_reconstruction": "auto-rebuilt by automation_runner from RECOVERY.json + carry scan"}
    tmp = sp + ".tmp"
    json.dump(st, open(tmp, "w"))
    os.replace(tmp, sp)
    emit("rebuild", carries=len(entries), rank_acc=rec["rank_acc"], next_col=rec["next_col"])
    return True

def tree_rss_kb(root_pid):
    """Sum RSS (KB) of root_pid and all descendants, via ps (macOS has no /proc)."""
    try:
        out = subprocess.check_output(["ps", "-axo", "pid=,ppid=,rss="], text=True)
    except Exception:
        return 0
    kids, rss = {}, {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) != 3:
            continue
        try:
            pid, ppid, r = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            continue
        kids.setdefault(ppid, []).append(pid)
        rss[pid] = r
    total, stack, seen = 0, [root_pid], set()
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        total += rss.get(p, 0)
        stack.extend(kids.get(p, []))
    return total

def read_state(work_abs):
    with open(os.path.join(work_abs, "rank5", "state.json")) as f:
        st = json.load(f)
    return {"next_col": st["next_col"], "ncols": st["ncols"],
            "rank_acc": st["rank_acc"], "carries": len(st["carries"]),
            "done": bool(st.get("done"))}

def rel(p):
    return os.path.relpath(p, ROOT) if p.startswith(ROOT) else p

def next_fire_dir(fires_abs):
    existing = sorted(glob.glob(os.path.join(fires_abs, "fire_*")))
    idx = 0
    if existing:
        idx = int(os.path.basename(existing[-1]).split("_")[1]) + 1
    d = os.path.join(fires_abs, "fire_%03d" % idx)
    os.makedirs(d, exist_ok=True)
    return d, idx

def run_fire(cfg, fires_abs, work_abs):
    before = read_state(work_abs)
    fdir, idx = next_fire_dir(fires_abs)
    out_json = os.path.join(fdir, "raw.json")
    cmd = ["sage", cfg["driver"], "--mode", "rank5",
           "--n", str(cfg["n"]), "--seed", str(cfg["seed"]),
           "--work", rel(work_abs),
           "--budget", str(cfg["fire_budget"]),
           "--max-units", str(cfg["max_units"]),
           "--chunk-force", str(cfg["chunk_force"]),
           "--out", rel(out_json)]
    log("fire %d cmd: %s" % (idx, " ".join(cmd)))
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=ROOT, start_new_session=True,
                            stdout=open(os.path.join(fdir, "stdout.txt"), "w"),
                            stderr=subprocess.STDOUT)
    rss_peak_kb, aborted = 0, False
    while True:
        rc = proc.poll()
        r = tree_rss_kb(proc.pid)
        rss_peak_kb = max(rss_peak_kb, r)
        if r > cfg["rss_limit_gb"] * 1e6:
            log("RSS %.2f GB > limit %.2f GB — killing process group" % (r / 1e6, cfg["rss_limit_gb"]))
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            aborted = True
        if rc is not None:
            break
        time.sleep(cfg["poll_s"])
    wall = time.time() - t0
    after = read_state(work_abs)
    rec = {"fire": idx, "exit_code": rc, "wall_s": round(wall, 1),
           "cols_done": after["next_col"] - before["next_col"],
           "next_col": after["next_col"], "ncols": after["ncols"],
           "rank_acc": after["rank_acc"], "carries": after["carries"],
           "rss_peak_mb": round(rss_peak_kb / 1024.0, 1),
           "aborted_rss": aborted, "out_json": rel(out_json)}
    emit("abort" if aborted else "fire", **rec)
    return rec, after

def main():
    cfg = load_config()
    work_abs = cfg["work"] if os.path.isabs(cfg["work"]) else os.path.join(ROOT, cfg["work"])
    fires_abs = cfg["fires_dir"] if os.path.isabs(cfg["fires_dir"]) else os.path.join(ROOT, cfg["fires_dir"])
    os.makedirs(fires_abs, exist_ok=True)
    log("config: %s" % json.dumps(cfg, sort_keys=True))
    if cfg["allow_state_rebuild"]:
        rebuild_state_if_missing(work_abs)
    fires, cols_total, rss_peak = [], 0, 0.0
    state = read_state(work_abs)
    while True:
        if state["done"]:
            emit("done", next_col=state["next_col"], ncols=state["ncols"],
                 rank_acc=state["rank_acc"], carries=state["carries"])
            break
        remaining = cfg["wall_budget"] - (time.time() - T0)
        if fires and remaining < cfg["min_next_fire"]:
            log("wall remaining %.0fs < min_next_fire %ds — stopping" % (remaining, cfg["min_next_fire"]))
            break
        rec, state = run_fire(cfg, fires_abs, work_abs)
        fires.append(rec)
        cols_total += rec["cols_done"]
        rss_peak = max(rss_peak, rec["rss_peak_mb"])
        if rec["aborted_rss"]:
            emit("summary", fires=len(fires), cols_total=cols_total,
                 rss_peak_mb=rss_peak, terminal="rss_abort",
                 next_col=state["next_col"], rank_acc=state["rank_acc"],
                 carries=state["carries"], done=False)
            return 2
        if rec["exit_code"] != 0:
            emit("summary", fires=len(fires), cols_total=cols_total,
                 rss_peak_mb=rss_peak, terminal="sage_error",
                 last_exit_code=rec["exit_code"], next_col=state["next_col"],
                 rank_acc=state["rank_acc"], carries=state["carries"], done=False)
            return 3
    emit("summary", fires=len(fires), cols_total=cols_total, rss_peak_mb=rss_peak,
         terminal="complete" if state["done"] else "wall_budget",
         next_col=state["next_col"], rank_acc=state["rank_acc"],
         carries=state["carries"], done=state["done"])
    return 0

T0 = time.time()

def run(ctx=None):
    """Managed Python runner entrypoint (Blueprint code Automation).

    Accepts config overrides from ctx (dict-like with .input / get, or plain dict),
    executes the fire loop, and returns the final summary as the artifact payload.
    """
    user = None
    for cand in (getattr(ctx, "input", None), ctx if isinstance(ctx, dict) else None):
        if isinstance(cand, dict) and cand:
            user = cand
            break
        if isinstance(cand, str) and cand.strip():
            try:
                user = json.loads(cand)
                break
            except Exception:
                pass
    if user:
        os.environ["RUNNER_CONFIG_JSON"] = json.dumps(user)
    rc = main()
    out = dict(LAST_EMIT) if LAST_EMIT else {"kind": "summary", "terminal": "no_output"}
    out["exit_code"] = rc
    return {"artifact": out}

if __name__ == "__main__":
    sys.exit(main())
