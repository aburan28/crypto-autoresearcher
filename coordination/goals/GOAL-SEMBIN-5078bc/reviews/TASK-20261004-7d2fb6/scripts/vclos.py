"""vclos.py -- reviewer's thin ctypes wrapper around ANY libclosure variant (original, evalcheck build, mutants).
Mirrors closure_cert._run/_lm_stats but takes the library path, so several variants can be loaded in one process.
SCRATCH (TASK-20261004-7d2fb6)."""
import ctypes, hashlib, struct
from array import array

class Clos:
    def __init__(self, path):
        self.path = path
        L = self.L = ctypes.CDLL(path)
        L.closure_run.restype = ctypes.c_int
        L.closure_run.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_int, ctypes.c_double,
                                  ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long),
                                  ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_long)]
        L.closure_rank.restype = ctypes.c_long
        L.closure_ncols.restype = ctypes.c_long
        L.closure_lm_dump.argtypes = [ctypes.c_void_p]
        L.closure_count_deg.restype = ctypes.c_long; L.closure_count_deg.argtypes = [ctypes.c_int]
        L.closure_dropped_terms.restype = ctypes.c_longlong
        L.closure_reset_dropped.restype = None
        L.closure_elimination.restype = ctypes.c_char_p
        L.closure_resumed.restype = ctypes.c_long
        L.closure_ech_faults.restype = ctypes.c_long
        L.closure_m4ri_library.restype = ctypes.c_char_p
        L.closure_row_masks.restype = ctypes.c_long; L.closure_row_masks.argtypes = [ctypes.c_long, ctypes.c_void_p]
        L.closure_standard_count.restype = ctypes.c_long; L.closure_standard_count.argtypes = [ctypes.c_long]
        L.closure_free.restype = None
        self.has_eval = hasattr(L, "closure_set_witness")
        if self.has_eval:
            L.closure_set_witness.argtypes = [ctypes.c_uint64]
            L.closure_set_method.argtypes = [ctypes.c_int]
            L.closure_ech_stats.argtypes = [ctypes.POINTER(ctypes.c_long)] * 3
            L.closure_ech_reset.restype = None
        self.m4ri = L.closure_m4ri_library().decode()
        self.elim = L.closure_elimination().decode()

    def run(self, N, D, eqs, max_iter=64, mem_cap_gb=1.0, want_rows=False, standard_cap=10**7):
        L = self.L
        L.closure_reset_dropped()
        ptr = array("q", [0]); masks = array("Q")
        for e in eqs:
            masks.extend(e); ptr.append(len(masks))
        n_it = max_iter + 2
        ir = array("q", [0] * n_it); ik = array("q", [0] * n_it); inew = array("q", [0] * n_it); iw = array("d", [0.0] * n_it)
        ncols = ctypes.c_long(0); iters = ctypes.c_long(0); rank = ctypes.c_long(0); one = ctypes.c_int(0); mr = ctypes.c_long(0)
        pbuf = (ctypes.c_long * len(ptr)).from_buffer(ptr)
        mbuf = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks) if len(masks) else (ctypes.c_uint64 * 1)()
        rc = L.closure_run(N, D, len(eqs), ctypes.addressof(pbuf), ctypes.addressof(mbuf), max_iter, float(mem_cap_gb * (1 << 30)),
                           ctypes.byref(ncols), ctypes.byref(iters),
                           (ctypes.c_long * n_it).from_buffer(ir), (ctypes.c_long * n_it).from_buffer(ik),
                           (ctypes.c_long * n_it).from_buffer(inew), (ctypes.c_double * n_it).from_buffer(iw),
                           ctypes.byref(rank), ctypes.byref(one), ctypes.byref(mr))
        k = iters.value
        out = {"rc": rc, "ncols": ncols.value, "rank": rank.value, "contains_one": bool(one.value),
               "profile": [(ir[i], ik[i], inew[i]) for i in range(k)], "iterations": k,
               "dropped": int(L.closure_dropped_terms()), "faults": int(L.closure_ech_faults()),
               "resumed": int(L.closure_resumed())}
        if rc == 0 or want_rows:
            rk = L.closure_rank()
            lms = array("Q", [0] * max(1, rk))
            L.closure_lm_dump(ctypes.addressof((ctypes.c_uint64 * len(lms)).from_buffer(lms)))
            lm = list(lms[:rk])
            out["lm"] = lm
            h = hashlib.sha256()
            for x in lm: h.update(int(x).to_bytes(8, "big"))
            out["lm_sha256"] = h.hexdigest()
            out["by_deg"] = {d: int(L.closure_count_deg(d)) for d in range(0, D + 1)}
            out["std"] = int(L.closure_standard_count(standard_cap))
            if want_rows:
                buf = array("Q", [0] * (ncols.value + 1))
                cbuf = (ctypes.c_uint64 * len(buf)).from_buffer(buf)
                rows = []
                for i in range(rk):
                    c = L.closure_row_masks(i, ctypes.addressof(cbuf))
                    rows.append(sorted(buf[:c]))
                out["rows"] = rows
        L.closure_free()
        return out

def write_rows_bin(rows, path):
    with open(path, "wb") as fh:
        for r in rows:
            fh.write(struct.pack("<I", len(r)))
            fh.write(array("Q", r).tobytes())

def write_sys(N, eqs, path):
    with open(path, "w") as fh:
        fh.write(f"{N} {len(eqs)}\n")
        for e in eqs:
            fh.write(f"{len(e)} " + " ".join(map(str, e)) + "\n")
