"""Sylvester resultant and Lagrange interpolation, shared by the m>=5 probes.

fp.resultant fixes the matrix size from the NOMINAL degrees, which is exactly
the trap RUN-FALSIFY-d770c1-001 fell into. Callers here assert full degree
before calling; these wrappers add nothing but a stable import point.
"""
from . import fp


def sylvester(f, g, p):
    return fp.resultant(f, g, p)


def interp(xs, ys, p):
    return fp.interpolate(xs, ys, p)
