"""Fast bit-packed GF(2) elimination for the CERTBIN Macaulay engines.

``kernels`` holds the elimination, row-pass, replay, back-trace and product
kernels (native C via ctypes, numpy reference fallback, identical outputs);
``closure`` holds the M_D / W_D closures and the trace instrument built on
them. See docs in each module and tests/test_gf2_kernels.py.
"""
from . import kernels  # noqa: F401
from .kernels import backend  # noqa: F401
