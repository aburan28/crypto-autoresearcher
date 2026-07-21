"""Exact GF(2) rank via m4ri, and an SMS sparse-matrix reader.

Splits the Boolean degree-of-regularity pipeline cleanly: a Sage environment
constructs and exports the Macaulay matrix to SMS (macaulay_export.py); this
module computes its exact rank here via m4ri -- no Sage needed for the rank.

SMS format (LinBox): "<rows> <cols> M" header, 1-indexed "<i> <j> 1" lines,
"0 0 0" terminator.

Provision m4ri first: tools/provision_m4ri.sh
Usage: python3 tools/m4ri_rank.py matrix.sms [--deficit SR_PRED]
"""
from __future__ import annotations
import ctypes, os, sys

_SHIM = "/usr/local/lib/m4ri_shim.so"


def _load():
    if not os.path.exists(_SHIM):
        raise SystemExit("m4ri shim not found; run tools/provision_m4ri.sh first")
    sh = ctypes.CDLL(_SHIM)
    sh.rank_coo.restype = ctypes.c_int
    sh.rank_coo.argtypes = [ctypes.c_int, ctypes.c_int,
                            ctypes.POINTER(ctypes.c_int),
                            ctypes.POINTER(ctypes.c_int), ctypes.c_long]
    sh.rank_random.restype = ctypes.c_int
    sh.rank_random.argtypes = [ctypes.c_int, ctypes.c_int]
    return sh


def rank_coo(rows: int, cols: int, ri: list[int], cj: list[int]) -> int:
    sh = _load()
    n = len(ri)
    ari = (ctypes.c_int * n)(*ri)
    acj = (ctypes.c_int * n)(*cj)
    return sh.rank_coo(rows, cols, ari, acj, n)


def read_sms(path: str):
    rows = cols = None
    ri: list[int] = []
    cj: list[int] = []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if rows is None:
                rows, cols = int(parts[0]), int(parts[1])   # ignore 'M' tag
                continue
            i, j = int(parts[0]), int(parts[1])
            if i == 0 and j == 0:
                break
            ri.append(i - 1)                                 # 1-indexed -> 0
            cj.append(j - 1)
    return rows, cols, ri, cj


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    rows, cols, ri, cj = read_sms(sys.argv[1])
    rank = rank_coo(rows, cols, ri, cj)
    print(f"rows={rows} cols={cols} nnz={len(ri)} rank={rank}")
    if "--deficit" in sys.argv:
        sr = int(sys.argv[sys.argv.index("--deficit") + 1])
        print(f"sr_pred={sr} deficit={sr - rank}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
