# Source-derived unguarded linear input

This is a static control-flow observation, not a native crash reproduction or attribution of the2001 ChangeLog fix.

For f=X-a over F_p, its reduced Frobenius image h=X^p mod f is the constant a, so the low-level polynomial predicate h.is_x() is false. The recovered1997 compute_degree routine then constructs a factor list for F.deg()=1 and calls its recursive helper with lo=0 and hi=number_of_factors-1=-1. fac_vec::compute_factorization(1) sets the factor count to zero and does not enter its factorization loop.

The recursive helper has an h.is_x test and a lo==hi test, but neither catches this case. Its split routine receives lo=0,hi=-1, computes mid=-1 and then decrements mid to-2. The next product range includes index-1 in the factor vector. That is an unguarded invalid-index path in the read source. Native behavior, compiler, error handler and memory layout have not been executed or measured here.

The later endpoint still has no explicit F.degree()==1 check in the low-level degree routine. This does not identify the2001 defect or prove that callers are required to support linear inputs. The later SEA caller handles all-linear/one-fixed-root cases separately and, in the two-fixed-root branch, strips those roots before degree computation. Whether the original NIST program ever reached this low-level function with a linear polynomial remains UNKNOWN for every cohort curve.

No curve is labeled rejected from this observation. An actual test would first need a declared native producer/control protocol and a sourced caller condition, then complete21-identity accounting. A hand reconstruction of this path is not a native1997 execution.
