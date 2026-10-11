"""EXP-WESO-9e2d6d -- shared helpers: SHA-256 counter-mode RNG, GP worker
processes, hashing, JSON/YAML IO.  Run with python3 -B (no bytecode).

RNG (spec replication.derivation):
  per-draw seed  = SHA-256( "<master>|<stage>|<p>|<arm>|<index>" )  (hex stored per record)
  stream block t = SHA-256( seed_bytes || t as 8-byte big-endian ),  t = 0, 1, 2, ...
No other source of randomness is used anywhere in this implementation.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
import threading

import numpy as np

IMPL_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(IMPL_DIR)
REPO = os.path.dirname(os.path.dirname(EXP_DIR))
GP_BIN = "/usr/bin/gp"
GP_LIB = os.path.join(IMPL_DIR, "weso.gp")
PARISIZEMAX = "1G"

SEEDS = {
    "U-1": 2026092600, "B-MAIN": 2026092601, "B-NULL": 2026092602,
    "PC-2": 2026092603, "START-1": 2026092604, "CLS": 2026092605,
    "DET-1": 2026092606,
    "C64-R1": 2026092611, "C64-R2": 2026092612, "C64-NULL": 2026092613,
    "C64-KS1": 2026092614, "C64-PC3": 2026092615, "C64-START2": 2026092616,
    "C96-R1": 2026092621, "C96-R2": 2026092622, "C96-NULL": 2026092623,
    "C128-R1": 2026092631, "C128-R2": 2026092632, "C128-NULL": 2026092633,
    "D-PILOT": 2026092640, "D-R1": 2026092641, "D-R2": 2026092642,
    "D-NULL": 2026092643,
}


def draw_seed(master, stage, p, arm, index):
    s = "%d|%s|%d|%s|%d" % (master, stage, p, arm, index)
    return hashlib.sha256(s.encode()).hexdigest()


class Stream:
    """SHA-256 counter-mode byte stream from a per-draw seed (hex)."""

    def __init__(self, seedhex):
        self.seed = bytes.fromhex(seedhex)
        self.ctr = 0
        self.buf = b""

    def _bytes(self, n):
        while len(self.buf) < n:
            self.buf += hashlib.sha256(self.seed + self.ctr.to_bytes(8, "big")).digest()
            self.ctr += 1
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def randbits(self, b):
        if b == 0:
            return 0
        nb = (b + 7) // 8
        x = int.from_bytes(self._bytes(nb), "big")
        return x >> (8 * nb - b)

    def randbelow(self, n):
        """Uniform integer in [0, n) by rejection on bit-length(n-1) bits."""
        if n <= 1:
            return 0
        b = (n - 1).bit_length()
        while True:
            x = self.randbits(b)
            if x < n:
                return x

    def random(self):
        """Uniform float in [0,1) with 53 bits."""
        return self.randbits(53) / 9007199254740992.0


def uniforms_vector(seedhex, n):
    """n uniform floats in [0,1) (53-bit), SHA-256 counter mode, vectorised.
    Block t yields four 8-byte big-endian words; each word >> 11 gives 53 bits."""
    seed = bytes.fromhex(seedhex)
    nblocks = (n + 3) // 4
    buf = b"".join(hashlib.sha256(seed + t.to_bytes(8, "big")).digest() for t in range(nblocks))
    w = np.frombuffer(buf, dtype=">u8")[:n].astype(np.uint64)
    return (w >> np.uint64(11)).astype(np.float64) / 9007199254740992.0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def impl_hashes():
    out = {}
    for name in sorted(os.listdir(IMPL_DIR)):
        path = os.path.join(IMPL_DIR, name)
        if os.path.isfile(path) and not name.endswith(".pyc"):
            out[name] = sha256_file(path)
    return out


class GP:
    """A persistent gp process with weso.gp loaded.  Commands are evaluated with
    iferr; an error raises RuntimeError (never silently skipped)."""

    def __init__(self, parisizemax=PARISIZEMAX):
        self.proc = subprocess.Popen(
            [GP_BIN, "-q", "-f", "-D", "parisizemax=%s" % parisizemax, "-D", "parisize=64M"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1)
        self.cmd('read("%s")' % GP_LIB, want=False)

    def cmd(self, expr, want=True):
        """Evaluate expr; if want, print its value.  Returns list of output lines."""
        if want:
            line = 'iferr(print(%s),E,print("@@ERR ",E));print("@@END")\n' % expr
        else:
            line = 'iferr(%s,E,print("@@ERR ",E));print("@@END")\n' % expr
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        out = []
        while True:
            l = self.proc.stdout.readline()
            if l == "":
                err = self.proc.stderr.read()
                raise RuntimeError("gp died: %s" % err[-2000:])
            l = l.rstrip("\n")
            if l == "@@END":
                break
            out.append(l)
        for l in out:
            if l.startswith("@@ERR"):
                raise RuntimeError("gp error on %r: %s" % (expr[:200], l))
        return out

    def val(self, expr):
        out = self.cmd(expr)
        return "".join(out)

    def close(self):
        try:
            self.proc.stdin.write("quit\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()


def gp_version():
    out = subprocess.run([GP_BIN, "--version-short"], capture_output=True, text=True).stdout.strip()
    return out


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
        f.write("\n")


def write_jsonl_gz(path, records):
    # mtime=0 so the gzip bytes are deterministic
    with open(path, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as g:
            for r in records:
                g.write((json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode())


def read_jsonl_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(l) for l in f]


def log(*a):
    print(*a, flush=True)


def det_record(r):
    """Deterministic part of a per-sample record (all fields except wall seconds),
    serialised canonically.  Used by DET-1 and the reproduction spot-check."""
    return json.dumps({k: v for k, v in r.items() if k != "wall_s"}, sort_keys=True, separators=(",", ":"))


def write_exec_report(rundir, run_id, stage, body):
    """execution_report.yaml (schema: agents/executor.md required output, plus
    stage-specific gate/control/criteria blocks supplied by the driver)."""
    import subprocess
    import yaml
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
    rep = {"execution_report": {
        "experiment_id": "EXP-WESO-9e2d6d", "spec_version": 1, "spec_status": "approved",
        "spec_approved_by": "coordinator", "spec_approved_under": "DEC-20260926-ec2847",
        "task_id": "TASK-20260926-41c7e7", "run_id": run_id, "stage": stage,
        "implementation_commit": commit, "implementation_dirty": bool(dirty),
        "implementation_dirty_paths": dirty,
    }}
    rep["execution_report"].update(body)
    rep = json.loads(json.dumps(rep, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    with open(os.path.join(rundir, "execution_report.yaml"), "w") as f:
        yaml.safe_dump(rep, f, sort_keys=False, width=110)
