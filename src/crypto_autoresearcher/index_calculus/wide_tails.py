"""Exact file-backed prime-field tails. The default TailTable is unchanged.

The native producer uses unsigned 128-bit intermediates for every modular
product. Its file format is sorted little-endian pairs of uint64 x and code;
the Python reader never narrows a wide coordinate. Large builds require an
explicit workspace-volume directory and are supervised for wall, RSS and disk.
"""

from __future__ import annotations

import hashlib
import json
import math
import mmap
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

_PAIR = struct.Struct("<QQ")
_SOURCE = Path(__file__).with_name("wide_tails.cpp")
_GIB = 1 << 30


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _tree_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.iterdir() if p.is_file())


class WidePackedTailTable:
    """File-backed signed tails with the same code convention as TailTable.

    Construction creates no target relation. The producer keeps its raw
    stdout/stderr, exact input, binary, and sorted chunk files in work_dir.
    A caller must retain or archive those bytes separately; a digest alone
    is not custody of a large table.
    """

    def __init__(self, E, fb, arity: int = 4, work_dir: str | Path = "",
                 *, timeout_seconds: int = 14400,
                 rss_limit_bytes: int = 8 * _GIB,
                 scratch_limit_bytes: int = 12 * _GIB,
                 min_free_bytes: int = 12 * _GIB,
                 chunk_entries: int = 1_000_000,
                 backend: str = "auto") -> None:
        if not 2 <= arity <= 8 or not 0 < E.p < 1 << 63:
            raise ValueError("wide table requires 2<=arity<=8 and p<2^63")
        if not work_dir:
            raise ValueError("explicit work_dir is required")
        self.fb, self.p, self.arity = fb, E.p, arity
        self.base = 2 * len(fb)
        if backend == "auto":
            # Numba runs in an existing Python runtime on hosts which stall
            # fresh Mach-O binaries before main. Its exact corrected quotient
            # is proved only for p < 2^50. C++ handles wider primes.
            backend = "numba" if E.p < 1 << 50 else "cpp"
        if backend not in ("numba", "cpp") or (backend == "numba" and E.p >= 1 << 50):
            raise ValueError("numba backend requires p<2^50; cpp handles wider fields")
        self.backend = backend
        self.work_dir = Path(work_dir).resolve()
        self.work_dir.mkdir(parents=True, exist_ok=True)
        if any(self.work_dir.iterdir()):
            raise FileExistsError("wide table work_dir must be empty")
        if shutil.disk_usage(self.work_dir).free < min_free_bytes:
            raise RuntimeError("insufficient workspace-volume disk headroom")
        if min(timeout_seconds, rss_limit_bytes, scratch_limit_bytes, chunk_entries) <= 0:
            raise ValueError("resource limits must be positive")
        try:
            import psutil
        except ImportError as exc:
            raise RuntimeError("psutil is required for the RSS watchdog") from exc
        t0 = time.monotonic()
        self.input_path = self.work_dir / "input.txt"
        self.binary_path = self.work_dir / "table.bin"
        self.executable_path = self.work_dir / "wide_tails"
        with self.input_path.open("w") as out:
            out.write(f"{E.p} {E.a} {E.b} {arity} {self.base}\n")
            for x, y in fb.points:
                out.write(f"{x} {y}\n")
        if backend == "cpp":
            self.compile_command = ["c++", "-std=c++17", "-O2", "-Wall", "-Wextra",
                                    str(_SOURCE), "-o", str(self.executable_path)]
            compile_result = subprocess.run(self.compile_command, capture_output=True,
                                            timeout=min(120, timeout_seconds), check=False)
            (self.work_dir / "build-stdout.log").write_bytes(compile_result.stdout)
            (self.work_dir / "build-stderr.log").write_bytes(compile_result.stderr)
            if compile_result.returncode:
                raise RuntimeError(f"native compilation failed: {compile_result.returncode}")
            self.run_command = [str(self.executable_path), str(self.input_path),
                                str(self.work_dir), str(self.binary_path), str(chunk_entries)]
        else:
            self.compile_command = []
            (self.work_dir / "build-stdout.log").write_bytes(b"")
            (self.work_dir / "build-stderr.log").write_bytes(b"")
            self.run_command = [sys.executable, "-m",
                                "crypto_autoresearcher.index_calculus.wide_tails",
                                "--produce-numba", str(self.input_path),
                                str(self.work_dir), str(self.binary_path)]
        peak_rss = peak_scratch = 0
        with (self.work_dir / "run-stdout.log").open("wb") as stdout, \
             (self.work_dir / "run-stderr.log").open("wb") as stderr:
            proc = subprocess.Popen(self.run_command, stdout=stdout, stderr=stderr)
            observed = psutil.Process(proc.pid)
            reason = None
            while proc.poll() is None:
                try:
                    # The native producer does not fork. Enumerating every
                    # system PID via psutil.children() is sandbox-blocked on
                    # macOS; observe the one launched PID directly.
                    rss = observed.memory_info().rss
                    peak_rss = max(peak_rss, rss)
                except psutil.Error:
                    pass
                peak_scratch = max(peak_scratch, _tree_bytes(self.work_dir))
                if peak_rss > rss_limit_bytes:
                    reason = "rss_limit"
                elif peak_scratch > scratch_limit_bytes:
                    reason = "scratch_limit"
                elif time.monotonic() - t0 > timeout_seconds:
                    reason = "wall_limit"
                if reason:
                    proc.kill()
                    break
                time.sleep(0.25)
            code = proc.wait()
        self.build_status = reason or ("ok" if code == 0 else "failed")
        self.metrics = {"status": self.build_status, "returncode": code,
                        "backend": backend,
                        "sampled_peak_rss_bytes": peak_rss,
                        "sampled_peak_scratch_bytes": peak_scratch,
                        "wall_seconds": time.monotonic() - t0,
                        "source_sha256": _sha256(_SOURCE),
                        "input_sha256": _sha256(self.input_path),
                        "executable_sha256": (_sha256(self.executable_path)
                                              if backend == "cpp" else None)}
        if code or reason:
            raise RuntimeError(f"wide table build {self.build_status}; logs in {self.work_dir}")
        native = json.loads((self.work_dir / "run-stdout.log").read_text())
        self.metrics.update(native)
        self.entries = native["entries"]
        self.s3_solves = native["s3_solves"]
        if self.binary_path.stat().st_size != self.entries * _PAIR.size:
            raise RuntimeError("native entry count and binary size disagree")
        self.metrics["table_sha256"] = _sha256(self.binary_path)
        self.metrics["payload_bytes"] = self.binary_path.stat().st_size
        self.seconds = self.metrics["wall_seconds"]
        self._file = self.binary_path.open("rb")
        self._map = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)

    def close(self) -> None:
        if hasattr(self, "_map"):
            self._map.close()
            self._file.close()

    def _at(self, i: int) -> tuple[int, int]:
        return _PAIR.unpack_from(self._map, _PAIR.size * i)

    def codes(self, x: int, lo: int) -> list[int]:
        if not 0 <= x < self.p:
            return []
        l, r = 0, self.entries
        while l < r:
            mid = (l+r)//2
            if self._at(mid)[0] < x:
                l = mid+1
            else:
                r = mid
        out = []
        while l < self.entries:
            key, code = self._at(l)
            if key != x or ((code >> 1) % self.base) >> 1 < lo:
                break
            out.append(code)
            l += 1
        return out

    def decode(self, code: int):
        v, out = code >> 1, []
        for _ in range(self.arity):
            v, d = divmod(v, self.base)
            out.append((d >> 1, -1 if d & 1 else 1))
        return out, code & 1

    def orient(self, code: int, y: int):
        v, flip = code >> 1, (code & 1) != (y > self.p // 2)
        out = []
        for _ in range(self.arity):
            v, d = divmod(v, self.base)
            s = -1 if d & 1 else 1
            out.append((d >> 1, -s if flip else s))
        return out

    def iter_keys(self):
        i = 0
        while i < self.entries:
            x, code = self._at(i)
            group = [code]
            i += 1
            while i < self.entries and self._at(i)[0] == x:
                group.append(self._at(i)[1])
                i += 1
            yield x, group

    def describe(self) -> dict:
        return {"arity": self.arity, "entries": self.entries,
                "s3_solves": self.s3_solves, "seconds": self.seconds,
                "storage": "wide_file_backed", **self.metrics}


def _produce_numba(input_path: Path, work_dir: Path, output_path: Path) -> None:
    """Build the same table inside an existing Python process for p<2^50.

    For a,b,p<2^50, conversion to binary64 is exact. The two rounded float
    operations estimating floor(a*b/p) have absolute quotient error <1/4.
    Thus the estimated integer quotient differs by at most one. The low 64
    bits of a*b-q*p recover the signed exact residual, whose magnitude is
    <2p<2^51, and one conditional correction yields the exact product mod p.
    Neither fastmath nor approximate arithmetic is used for the result.
    """
    import numpy as np
    from numba import njit

    lines = input_path.read_text().splitlines()
    p, a, _b, h, base = map(int, lines[0].split())
    if not 3 <= p < 1 << 50 or not 2 <= h <= 8 or base % 2:
        raise ValueError("numba backend input outside proved range")
    points = np.array([list(map(int, line.split())) for line in lines[1:]],
                      dtype=np.uint64)
    if len(points) * 2 != base:
        raise ValueError("factor-base length differs from header")
    P, A, BASE = np.uint64(p), np.uint64(a), np.uint64(base)

    @njit
    def mulm(x, y, mod):
        q = np.uint64((float(x) * float(y)) / float(mod))
        t = np.int64(x * y - q * mod)
        if t < 0:
            t += np.int64(mod)
        if t >= np.int64(mod):
            t -= np.int64(mod)
        return np.uint64(t)

    @njit
    def addm(x, y, mod):
        z = x + y
        return z - mod if z >= mod else z

    @njit
    def subm(x, y, mod):
        return x - y if x >= y else x + mod - y

    @njit
    def powm(x, n, mod):
        z = np.uint64(1)
        while n:
            if n & np.uint64(1):
                z = mulm(z, x, mod)
            x = mulm(x, x, mod)
            n >>= np.uint64(1)
        return z

    @njit
    def extend(x, y, v, nv, first, pts, ox, oy, ov, onv, of, last,
               mod, curve_a, digit_base):
        count = charges = batches = exceptions = 0
        start = 0
        for i in range(len(pts)):
            while start < len(first) and first[start] < i:
                start += 1
            n = len(first) - start
            if not n:
                continue
            charges += n
            batches += 1
            xa, ya = pts[i, 0], pts[i, 1]
            pref = np.empty(n + 1, dtype=np.uint64)
            pref[0] = np.uint64(1)
            for j in range(n):
                dx = subm(x[start+j], xa, mod)
                pref[j+1] = mulm(pref[j], dx if dx else np.uint64(1), mod)
            inv = powm(pref[n], mod - np.uint64(2), mod)
            for j in range(n - 1, -1, -1):
                pos = start + j
                dx = subm(x[pos], xa, mod)
                dxinv = mulm(pref[j], inv, mod)
                inv = mulm(inv, dx if dx else np.uint64(1), mod)
                if not dx:
                    exceptions += 1
                for sign in range(2):
                    sy = y[pos] if sign == 0 else subm(np.uint64(0), y[pos], mod)
                    if dx:
                        lam = mulm(subm(sy, ya, mod), dxinv, mod)
                    else:
                        if addm(ya, sy, mod) == 0:
                            continue
                        den = addm(ya, ya, mod)
                        x2 = mulm(xa, xa, mod)
                        numerator = addm(addm(x2, x2, mod), x2, mod)
                        numerator = addm(numerator, curve_a, mod)
                        lam = mulm(numerator,
                                   powm(den, mod - np.uint64(2), mod), mod)
                    xx = subm(mulm(lam, lam, mod), addm(xa, x[pos], mod), mod)
                    yy = subm(mulm(lam, subm(xa, xx, mod), mod), ya, mod)
                    vv = np.uint64(2*i) + digit_base * (v[pos] if sign == 0 else nv[pos])
                    if last:
                        ox[count] = xx
                        ov[count] = (vv << np.uint64(1)) | np.uint64(yy > mod // np.uint64(2))
                    else:
                        ox[count], oy[count] = xx, yy
                        ov[count] = vv
                        onv[count] = np.uint64(2*i+1) + digit_base * (nv[pos] if sign == 0 else v[pos])
                        of[count] = i
                    count += 1
        return count, charges, batches, exceptions

    x, y = points[:, 0].copy(), points[:, 1].copy()
    v = np.arange(0, base, 2, dtype=np.uint64)
    nv = v + np.uint64(1)
    first = np.arange(len(points), dtype=np.uint16)
    pair_dtype = np.dtype([("x", "<u8"), ("code", "<u8")])
    charges = batches = exceptions = 0
    level_times = {}
    t0 = time.monotonic()
    raw = None
    for k in range(2, h + 1):
        t = time.monotonic()
        upper = (1 << (k-1)) * math.comb(len(points)+k-1, k)
        last = k == h
        if last:
            raw = np.memmap(work_dir / "unsorted.bin", dtype=pair_dtype,
                            mode="w+", shape=(upper,))
            ox, ov = raw["x"], raw["code"]
            oy = onv = of = np.empty(0, dtype=np.uint64)
        else:
            ox = np.empty(upper, dtype=np.uint64)
            oy = np.empty(upper, dtype=np.uint64)
            ov = np.empty(upper, dtype=np.uint64)
            onv = np.empty(upper, dtype=np.uint64)
            of = np.empty(upper, dtype=np.uint16)
        n, c, b, e = extend(x, y, v, nv, first, points, ox, oy, ov, onv, of,
                            last, P, A, BASE)
        if n > upper:
            raise AssertionError("enumeration exceeded combinatorial bound")
        charges += c
        batches += b
        exceptions += e
        level_times[str(k)] = time.monotonic() - t
        print(f"level={k} entries={n} upper={upper} charges={c}", file=sys.stderr, flush=True)
        if not last:
            x, y, v, nv, first = (ox[:n], oy[:n], ov[:n], onv[:n], of[:n])
    del x, y, v, nv, first
    raw.flush()
    t_sort = time.monotonic()
    keys_first = ((raw["code"][:n] >> np.uint64(1)) % BASE) >> np.uint64(1)
    order = np.lexsort((raw["code"][:n],
                        np.uint64(len(points)-1) - keys_first, raw["x"][:n]))
    del keys_first
    sort_seconds = time.monotonic() - t_sort
    t_write = time.monotonic()
    out = np.memmap(output_path, dtype=pair_dtype, mode="w+", shape=(n,))
    for start in range(0, n, 1_000_000):
        end = min(start + 1_000_000, n)
        out[start:end] = raw[order[start:end]]
    out.flush()
    del out, order, raw
    print(json.dumps({"entries": n, "s3_solves": charges,
                      "inverse_batches": batches, "exceptions": exceptions,
                      "seconds": time.monotonic() - t0,
                      "level_seconds": level_times,
                      "sort_seconds": sort_seconds,
                      "write_seconds": time.monotonic() - t_write,
                      "backend": "numba", "arithmetic": "binary64_quotient_exact_residual_p_lt_2pow50"}))


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] != "--produce-numba":
        raise SystemExit("usage: python -m ...wide_tails --produce-numba input work_dir output")
    _produce_numba(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
