/* Minimal C shim exposing m4ri GF(2) rank to Python via ctypes.
   The bit accessors (mzd_write_bit) are static-inline in m4ri's headers, so
   they are not in libm4ri.so; compiling this shim against the headers pulls
   them in. Build with tools/provision_m4ri.sh. */
#include <m4ri/m4ri.h>
int rank_coo(int rows, int cols, const int* ri, const int* cj, long nnz){
    mzd_t* M = mzd_init(rows, cols);
    for(long k=0;k<nnz;k++) mzd_write_bit(M, ri[k], cj[k], 1);
    int r = mzd_echelonize(M, 1);
    mzd_free(M);
    return r;
}
int rank_random(int rows, int cols){
    mzd_t* M = mzd_init(rows, cols);
    mzd_randomize(M);
    int r = mzd_echelonize(M, 1);
    mzd_free(M);
    return r;
}
