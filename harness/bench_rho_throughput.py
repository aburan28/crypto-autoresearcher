"""Measure rho STEP throughput on CPU and (where present) GPU, comparably.

Motivation. Cost models for a rho campaign are quoted in steps per second, and
that number is usually inherited from somebody else's hardware, somebody else's
field size, and an inner loop that may not have been carrying the coefficients
a walk needs to be worth running. This module measures it here, on one walk
definition, with the accumulators carried, and reports what it measured next to
what it did not.

Three implementations of ONE walk:

  * `reference`  -- straightforward Python, one modular inversion per step. The
                    definition of correct; too slow to be a cost model.
  * `batched`    -- Python with Montgomery's trick across walks. Same result,
                    one inversion per batch. This is the honest CPU number.
  * `gpu`        -- gpu/rho_kernel.cu via CuPy, same walk, compared against
                    `reference` before it is allowed to report a rate.

Nothing reports a throughput number until it has reproduced the reference walk
exactly, limb for limb (`--self-test`). A benchmark that is fast and wrong is
the failure mode this guards against.

What is measured: sustained step rate for walks resident in memory, including
branch selection, the affine add, the (a, b) updates mod n, and the
distinguished-point test. What is NOT measured: the host-side DP table, the
device-to-host transfer of DPs, and the collision search. At realistic DP rates
those amortize to a small correction, but they are not zero -- so every rate
here is an UPPER BOUND on end-to-end campaign throughput and is labelled as
such in the emitted record.

Usage:

    python -m harness.bench_rho_throughput --self-test
    python -m harness.bench_rho_throughput --seconds 5 --out bench.json
    python -m harness.bench_rho_throughput --seconds 10 --gpu \
        --cpu-usd-per-hour 1.50 --gpu-usd-per-hour 0.60 --out bench.json
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

# secp256k1: the field size that matters for the deployed-curve cost model.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
A_COEF, B_COEF = 0, 7

R = 1 << 256
R_MOD_P = R % P
N0 = (-pow(P, -1, 1 << 64)) % (1 << 64)      # -p^-1 mod 2^64, for CIOS
MASK64 = (1 << 64) - 1

GPU_DIR = Path(__file__).resolve().parent / "gpu"


# --------------------------------------------------------------------------
# curve setup (only used to build the instance; not on any timed path)
# --------------------------------------------------------------------------
def ec_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = (3 * x1 * x1 + A_COEF) * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)


def ec_mul(k, pt):
    r, addend = None, pt
    while k:
        if k & 1:
            r = ec_add(r, addend)
        addend = ec_add(addend, addend)
        k >>= 1
    return r


def to_mont(v: int) -> int:
    return v * R % P


def from_mont(v: int) -> int:
    return v * pow(R, -1, P) % P


def _lcg(seed: int):
    """Deterministic, dependency-free, and identical in every reimplementation
    of this benchmark -- which is the only property required of it here."""
    state = seed & MASK64
    while True:
        state = (state * 6364136223846793005 + 1442695040888963407) & MASK64
        yield state


@dataclass
class Case:
    """One frozen walk instance: branch table, start states, step budget."""
    nbranch: int
    nwalks: int
    nsteps: int
    dp_bits: int
    tx: list = field(default_factory=list)
    ty: list = field(default_factory=list)
    tc: list = field(default_factory=list)
    td: list = field(default_factory=list)
    x: list = field(default_factory=list)
    y: list = field(default_factory=list)
    a: list = field(default_factory=list)
    b: list = field(default_factory=list)


def build_case(seed: int, nbranch: int, nwalks: int, nsteps: int,
               dp_bits: int) -> Case:
    rng = _lcg(seed)
    k_secret = (next(rng) << 64 | next(rng)) % N          # the instance's k
    G = (GX, GY)
    Q = ec_mul(k_secret, G)

    c = Case(nbranch=nbranch, nwalks=nwalks, nsteps=nsteps, dp_bits=dp_bits)
    for _ in range(nbranch):
        cs = (next(rng) << 64 | next(rng)) % N
        ds = (next(rng) << 64 | next(rng)) % N
        T = ec_add(ec_mul(cs, G), ec_mul(ds, Q))
        c.tx.append(T[0]); c.ty.append(T[1]); c.tc.append(cs); c.td.append(ds)
    for _ in range(nwalks):
        ai = (next(rng) << 64 | next(rng)) % N
        bi = (next(rng) << 64 | next(rng)) % N
        W = ec_add(ec_mul(ai, G), ec_mul(bi, Q))
        c.x.append(W[0]); c.y.append(W[1]); c.a.append(ai); c.b.append(bi)
    return c


# --------------------------------------------------------------------------
# the walk, three ways
# --------------------------------------------------------------------------
def _branch(x: int, mask: int) -> int:
    """Branch index, read off the LOW LIMB OF THE MONTGOMERY FORM of x.

    The kernel works in the Montgomery domain and converting out per step would
    cost more than the step. Any deterministic function of the point is a valid
    r-adding branch function, so the kernel's choice is adopted here verbatim
    rather than corrected -- this is the definition all three implementations
    share, and the differential test depends on it.
    """
    return (to_mont(x) & MASK64) & mask


def _is_dp(x: int, dp_bits: int) -> bool:
    if dp_bits <= 0:
        return False
    return (to_mont(x) & ((1 << dp_bits) - 1)) == 0


def walk_reference(c: Case, nsteps: int | None = None):
    """One inversion per walk per step. Slow, obvious, and the ground truth."""
    nsteps = c.nsteps if nsteps is None else nsteps
    x, y = list(c.x), list(c.y)
    a, b = list(c.a), list(c.b)
    mask = c.nbranch - 1
    dps = 0
    for _ in range(nsteps):
        for i in range(c.nwalks):
            s = _branch(x[i], mask)
            lam = (y[i] - c.ty[s]) * pow(x[i] - c.tx[s], -1, P) % P
            xr = (lam * lam - x[i] - c.tx[s]) % P
            y[i] = (lam * (x[i] - xr) - y[i]) % P
            x[i] = xr
            a[i] = (a[i] + c.tc[s]) % N
            b[i] = (b[i] + c.td[s]) % N
            if _is_dp(x[i], c.dp_bits):
                dps += 1
    return x, y, a, b, dps


def walk_batched(c: Case, nsteps: int | None = None):
    """One inversion per STEP across all walks (Montgomery's trick).

    Identical output to walk_reference; the entire difference is that the
    inversion -- which dominates everything else combined -- is amortized.
    """
    nsteps = c.nsteps if nsteps is None else nsteps
    x, y = list(c.x), list(c.y)
    a, b = list(c.a), list(c.b)
    tx, ty, tc, td = c.tx, c.ty, c.tc, c.td
    mask = c.nbranch - 1
    nw = c.nwalks
    dp_mask = (1 << c.dp_bits) - 1 if c.dp_bits > 0 else 0
    rinv = pow(R, -1, P)
    dps = 0

    for _ in range(nsteps):
        br = [(x[i] * R % P & MASK64) & mask for i in range(nw)]
        dx = [(x[i] - tx[br[i]]) % P for i in range(nw)]

        # batch inversion: prefix products, one pow(), unwind
        pref = [0] * nw
        acc = 1
        for i in range(nw):
            pref[i] = acc
            acc = acc * dx[i] % P
        inv = pow(acc, -1, P)
        dxinv = [0] * nw
        for i in range(nw - 1, -1, -1):
            dxinv[i] = pref[i] * inv % P
            inv = inv * dx[i] % P

        for i in range(nw):
            s = br[i]
            lam = (y[i] - ty[s]) * dxinv[i] % P
            xr = (lam * lam - x[i] - tx[s]) % P
            y[i] = (lam * (x[i] - xr) - y[i]) % P
            x[i] = xr
            a[i] = (a[i] + tc[s]) % N
            b[i] = (b[i] + td[s]) % N
            if dp_mask and (xr * R % P & dp_mask) == 0:
                dps += 1
    return x, y, a, b, dps


# --------------------------------------------------------------------------
# GPU path
# --------------------------------------------------------------------------
def _limbs_le(v: int) -> list:
    return [(v >> (64 * i)) & MASK64 for i in range(4)]


def gpu_available():
    try:
        import cupy  # noqa: F401
    except Exception as exc:
        return False, f"cupy not importable: {exc}"
    try:
        import cupy as cp
        if cp.cuda.runtime.getDeviceCount() < 1:
            return False, "cupy present but no CUDA device"
    except Exception as exc:
        return False, f"no usable CUDA device: {exc}"
    return True, ""


def walk_gpu(c: Case, nsteps: int, walks_per_thread: int, threads: int = 128):
    """Run the CUDA kernel over the same case; returns the same tuple shape."""
    import cupy as cp

    src = (GPU_DIR / "rho_kernel.cu").read_text()
    mod = cp.RawModule(code=src, backend="nvrtc",
                       options=("-I", str(GPU_DIR), "-std=c++11"),
                       name_expressions=None)
    kern = mod.get_function("rho_steps")

    def pack(vals, mont):
        flat = []
        for v in vals:
            flat.extend(_limbs_le(to_mont(v) if mont else v))
        return cp.asarray(flat, dtype=cp.uint64)

    X, Y = pack(c.x, True), pack(c.y, True)
    A, Bc = pack(c.a, False), pack(c.b, False)
    TX, TY = pack(c.tx, True), pack(c.ty, True)
    TC, TD = pack(c.tc, False), pack(c.td, False)
    pbuf = cp.asarray(_limbs_le(P), dtype=cp.uint64)
    onebuf = cp.asarray(_limbs_le(R_MOD_P), dtype=cp.uint64)
    ordbuf = cp.asarray(_limbs_le(N), dtype=cp.uint64)
    dxbuf = cp.zeros_like(X)
    dxinv = cp.zeros_like(X)
    scratch = cp.zeros_like(X)
    dp_count = cp.zeros(1, dtype=cp.uint64)

    nthreads = (c.nwalks + walks_per_thread - 1) // walks_per_thread
    blocks = (nthreads + threads - 1) // threads
    kern((blocks,), (threads,), (
        X, Y, A, Bc, TX, TY, TC, TD, pbuf, cp.uint64(N0), onebuf, ordbuf,
        dxbuf, dxinv, scratch,
        cp.int32(c.nwalks), cp.int32(walks_per_thread), cp.int32(nsteps),
        cp.int32(c.nbranch), cp.int32(c.dp_bits), dp_count))
    cp.cuda.Stream.null.synchronize()

    def unpack(buf, mont):
        raw = cp.asnumpy(buf).tolist()
        out = []
        for i in range(c.nwalks):
            v = sum(int(raw[i * 4 + j]) << (64 * j) for j in range(4))
            out.append(from_mont(v) if mont else v)
        return out

    return (unpack(X, True), unpack(Y, True), unpack(A, False),
            unpack(Bc, False), int(cp.asnumpy(dp_count)[0]))


# --------------------------------------------------------------------------
# differential self-test
# --------------------------------------------------------------------------
def _selftest_vectors(c: Case) -> str:
    """Serialize a case for mont256_selftest.c (64-hex-char big-endian words)."""
    def h(v, mont):
        return "%064x" % (to_mont(v) if mont else v)

    out = [h(P, False), "%x" % N0, h(R_MOD_P, False), h(N, False),
           f"{c.nbranch} {c.nwalks} {c.nsteps} {c.dp_bits}"]
    for s in range(c.nbranch):
        out += [h(c.tx[s], True), h(c.ty[s], True),
                h(c.tc[s], False), h(c.td[s], False)]
    for i in range(c.nwalks):
        out += [h(c.x[i], True), h(c.y[i], True),
                h(c.a[i], False), h(c.b[i], False)]
    return "\n".join(out) + "\n"


def run_c_selftest(c: Case):
    """Compile mont256.h as host C and run the same walk. Returns None if no
    C compiler is available -- absence of a toolchain is not a test failure,
    but it IS reported, never silently passed."""
    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        return None, "no C compiler found (set CC to run the C differential test)"
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "selftest")
        cp_ = subprocess.run([cc, "-O2", "-I", str(GPU_DIR), "-o", exe,
                              str(GPU_DIR / "mont256_selftest.c")],
                             capture_output=True, text=True)
        if cp_.returncode != 0:
            return None, f"compile failed: {cp_.stderr.strip()[:500]}"
        run = subprocess.run([exe], input=_selftest_vectors(c),
                             capture_output=True, text=True)
        if run.returncode != 0:
            return None, f"selftest run failed: {run.stderr.strip()[:500]}"

    lines = run.stdout.split()
    dps = int(lines[0])
    vals = lines[1:]
    x, y, a, b = [], [], [], []
    for i in range(c.nwalks):
        x.append(from_mont(int(vals[4 * i + 0], 16)))
        y.append(from_mont(int(vals[4 * i + 1], 16)))
        a.append(int(vals[4 * i + 2], 16))
        b.append(int(vals[4 * i + 3], 16))
    return (x, y, a, b, dps), ""


def _compare(name, got, want, errors):
    if got is None:
        return
    for lbl, g, w in zip("xyab", got[:4], want[:4]):
        if g != w:
            bad = next(i for i, (u, v) in enumerate(zip(g, w)) if u != v)
            errors.append(f"{name}: {lbl} differs at walk {bad}")
            return
    if got[4] != want[4]:
        errors.append(f"{name}: DP count {got[4]} != {want[4]}")


def self_test(nwalks=8, nsteps=32, nbranch=32, dp_bits=8, seed=20260916):
    """Every implementation must reproduce `reference` exactly, or no rate is
    reported from it. Also checks the walks stay on the curve, which catches a
    whole class of field-arithmetic error that a same-answer check would not if
    two implementations shared a bug."""
    c = build_case(seed, nbranch, nwalks, nsteps, dp_bits)
    ref = walk_reference(c)
    errors, notes = [], []

    _compare("batched", walk_batched(c), ref, errors)

    for i, (xi, yi) in enumerate(zip(ref[0], ref[1])):
        if (yi * yi - xi * xi * xi - A_COEF * xi - B_COEF) % P != 0:
            errors.append(f"reference: walk {i} left the curve")
            break

    c_res, c_note = run_c_selftest(c)
    if c_res is None:
        notes.append(f"C differential test SKIPPED: {c_note}")
    else:
        _compare("mont256.h (host C)", c_res, ref, errors)

    ok, why = gpu_available()
    if not ok:
        notes.append(f"GPU differential test SKIPPED: {why}")
    else:
        try:
            _compare("gpu kernel", walk_gpu(c, nsteps, walks_per_thread=nwalks),
                     ref, errors)
        except Exception as exc:
            errors.append(f"gpu kernel: raised {type(exc).__name__}: {exc}")

    return errors, notes


# --------------------------------------------------------------------------
# timing
# --------------------------------------------------------------------------
def time_cpu(fn, c: Case, seconds: float):
    """Time `fn` for at least `seconds`, returning steps/s for ONE core.

    Steps are counted as walk-steps (nwalks per iteration), which is the unit a
    rho cost model is denominated in.
    """
    chunk = max(1, int(8 / max(c.nwalks, 1)) or 1)
    fn(c, 1)                                       # warm caches / JIT-free
    t0 = time.perf_counter()
    steps = 0
    while time.perf_counter() - t0 < seconds:
        fn(c, chunk)
        steps += chunk * c.nwalks
    return steps / (time.perf_counter() - t0)


def time_gpu(c: Case, seconds: float, walks_per_thread: int):
    import cupy as cp
    walk_gpu(c, 1, walks_per_thread)               # compile + warm
    steps_per_launch = 64
    t0 = time.perf_counter()
    steps = 0
    while time.perf_counter() - t0 < seconds:
        walk_gpu(c, steps_per_launch, walks_per_thread)
        cp.cuda.Stream.null.synchronize()
        steps += steps_per_launch * c.nwalks
    return steps / (time.perf_counter() - t0)


def machine_info():
    info = {"platform": platform.platform(), "python": platform.python_version(),
            "cpu_count": os.cpu_count()}
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                info["cpu_model"] = line.split(":", 1)[1].strip()
                break
    except Exception:
        pass
    ok, why = gpu_available()
    if ok:
        import cupy as cp
        props = cp.cuda.runtime.getDeviceProperties(0)
        info["gpu"] = props["name"].decode()
    else:
        info["gpu"] = None
        info["gpu_absent_reason"] = why
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seconds", type=float, default=3.0,
                    help="measurement window per implementation")
    ap.add_argument("--walks", type=int, default=512,
                    help="walks per batch (the inversion amortization width)")
    ap.add_argument("--branches", type=int, default=32, help="r-adding table size")
    ap.add_argument("--dp-bits", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20260916)
    ap.add_argument("--gpu", action="store_true", help="also time the CUDA kernel")
    ap.add_argument("--gpu-walks", type=int, default=131072,
                    help="total walks resident on the device")
    ap.add_argument("--walks-per-thread", type=int, default=64,
                    help="inversion batch width per CUDA thread")
    ap.add_argument("--reference", action="store_true",
                    help="also time the unbatched reference (slow)")
    ap.add_argument("--cpu-usd-per-hour", type=float, default=None)
    ap.add_argument("--gpu-usd-per-hour", type=float, default=None)
    ap.add_argument("--self-test", action="store_true",
                    help="run the differential tests and exit")
    ap.add_argument("--out", type=str, default=None, help="write JSON record here")
    args = ap.parse_args(argv)

    errors, notes = self_test(seed=args.seed)
    for n in notes:
        print(f"note: {n}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        print("refusing to report throughput: implementations disagree",
              file=sys.stderr)
        return 1
    print("self-test: all available implementations match the reference",
          file=sys.stderr)
    if args.self_test:
        return 0

    rec = {
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "curve": "secp256k1", "field_bits": 256,
        "machine": machine_info(),
        "parameters": {k: getattr(args, k) for k in
                       ("walks", "branches", "dp_bits", "seed", "seconds",
                        "walks_per_thread")},
        "scope": ("Steps per second for resident walks: branch selection, "
                  "affine add with batched inversion, (a,b) updates mod n, and "
                  "the DP test. EXCLUDES the host DP table, DP transfer, and "
                  "collision search, so every rate here is an UPPER BOUND on "
                  "end-to-end campaign throughput."),
        "results": {},
    }

    c = build_case(args.seed, args.branches, args.walks, 1, args.dp_bits)
    if args.reference:
        cref = build_case(args.seed, args.branches, min(args.walks, 32), 1,
                          args.dp_bits)
        rec["results"]["cpu_reference_1core"] = {
            "steps_per_second": time_cpu(walk_reference, cref, args.seconds),
            "note": "one modular inversion per step; ground truth, not a cost model",
        }
    rate_cpu = time_cpu(walk_batched, c, args.seconds)
    rec["results"]["cpu_batched_1core"] = {
        "steps_per_second": rate_cpu,
        "steps_per_second_all_cores_extrapolated": rate_cpu * (os.cpu_count() or 1),
        "note": ("single core, measured; the all-cores figure is an "
                 "EXTRAPOLATION by core count, not a measurement"),
    }

    if args.gpu:
        ok, why = gpu_available()
        if not ok:
            rec["results"]["gpu"] = {"steps_per_second": None, "reason": why}
        else:
            cg = build_case(args.seed, args.branches, args.gpu_walks, 1,
                            args.dp_bits)
            rec["results"]["gpu"] = {
                "steps_per_second": time_gpu(cg, args.seconds,
                                             args.walks_per_thread),
                "resident_walks": args.gpu_walks,
            }

    # cost comparison, only where both a rate and a price exist
    costs = {}
    cpu_all = rec["results"]["cpu_batched_1core"].get(
        "steps_per_second_all_cores_extrapolated")
    if args.cpu_usd_per_hour and cpu_all:
        costs["cpu_steps_per_usd"] = cpu_all * 3600 / args.cpu_usd_per_hour
    gpu_rate = (rec["results"].get("gpu") or {}).get("steps_per_second")
    if args.gpu_usd_per_hour and gpu_rate:
        costs["gpu_steps_per_usd"] = gpu_rate * 3600 / args.gpu_usd_per_hour
    if "cpu_steps_per_usd" in costs and "gpu_steps_per_usd" in costs:
        costs["gpu_advantage_x"] = (costs["gpu_steps_per_usd"] /
                                    costs["cpu_steps_per_usd"])
        costs["price_inputs_usd_per_hour"] = {
            "cpu": args.cpu_usd_per_hour, "gpu": args.gpu_usd_per_hour}
        costs["note"] = ("Prices are USER-SUPPLIED inputs, not measurements. "
                         "The ratio inherits their accuracy entirely.")
    if costs:
        rec["cost"] = costs

    text = json.dumps(rec, indent=2, sort_keys=True)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
