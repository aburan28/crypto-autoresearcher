# distutils: libraries = m4ri
# Raw-bit carrier codec for sage Matrix_mod2_dense (GF(2) m4ri matrices).
# TRUE raw-bit path: per-row memcpy via m4ri's own mzd_row() pointers.
# No PNG, no pure-Python element loops.
from sage.matrix.matrix_mod2_dense cimport Matrix_mod2_dense
from sage.libs.m4ri cimport mzd_t, mzd_row
from libc.string cimport memcpy

def dump_raw(Matrix_mod2_dense H, Py_ssize_t nr, Py_ssize_t nc):
    cdef Py_ssize_t width = (nc + 63) >> 6
    cdef Py_ssize_t i
    out = bytearray(nr * width * 8)
    cdef char *dst = out
    for i in range(nr):
        memcpy(dst + i * width * 8, <char *> mzd_row(H._entries, i), width * 8)
    return bytes(out)

def load_raw(bytes buf, Matrix_mod2_dense H2, Py_ssize_t nr, Py_ssize_t nc):
    cdef Py_ssize_t width = (nc + 63) >> 6
    cdef Py_ssize_t i
    cdef char *src = buf
    for i in range(nr):
        memcpy(<char *> mzd_row(H2._entries, i), src + i * width * 8, width * 8)
    return H2
