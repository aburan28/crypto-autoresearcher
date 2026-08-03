"""Minimal Sage shim: feasibility spike only.

Goal is narrow -- find out whether the pinned lattice-estimator (3e48ef4) can be
driven without Sage, so that a memory-charged re-derivation of the Kyber cost
table becomes possible in this environment. NOT trustworthy until it reproduces
the archived RUN-MLKEM-015-001 numbers as a known-answer control.
"""
import functools
import math

import mpmath as mp

mp.mp.prec = 200

oo = mp.inf
pi = mp.pi
e = mp.e


def _f(x):
    return mp.mpf(x) if not isinstance(x, mp.mpf) else x


class _Real(mp.mpf):
    """mpf plus the handful of Sage RealNumber methods the estimator calls."""

    def is_NaN(self):
        return mp.isnan(self)

    def is_infinity(self):
        return mp.isinf(self)

    def n(self, prec=None, digits=None):
        """Sage's numerical-approximation method. estimator.lwe_dual.MATZOV
        calls it, so without this the MATZOV cost model -- the one the public
        `LWE.dual_hybrid` name actually resolves to -- cannot run at all.
        Found by BATCH-011, which had to patch it in-process to proceed.
        Third time this shim has been wrong about its own limits (see the pi/e
        attributes from BATCH-010 D4); each was found by someone running it."""
        return _Real(self)


def _mkreal(x):
    if x is oo or x == mp.inf:
        return _Real(mp.inf)
    if x == -mp.inf:
        return _Real(-mp.inf)
    return _Real(x)


class _RealField:
    """Sage's RR/RDF are also *rings*, carrying constants as attributes.
    estimator/prob.py:213 calls RDF.pi(); without these the dual attack dies
    with AttributeError. Found by independent validation (BATCH-010 D4), not by
    the author -- the original shim documented only Arora-GB as unavailable and
    was wrong about the harness's own limits."""

    def __init__(self, prec=53):
        self.prec = prec

    def __call__(self, x):
        return _mkreal(x)

    def pi(self):
        return _mkreal(mp.pi)

    def e(self):
        return _mkreal(mp.e)

    def euler_constant(self):
        return _mkreal(mp.euler)


RR = _RealField()
RDF = _RealField()
RealField = _RealField


def ZZ(x):
    return int(x)


def QQ(x):
    return mp.mpf(x)


def log(x, b=None):
    x = _f(x)
    if b is None:
        return _mkreal(mp.log(x))
    return _mkreal(mp.log(x) / mp.log(_f(b)))


def sqrt(x):
    return _mkreal(mp.sqrt(_f(x)))


def exp(x):
    return _mkreal(mp.exp(_f(x)))


def erf(x):
    return _mkreal(mp.erf(_f(x)))


def coth(x):
    return _mkreal(mp.coth(_f(x)))


def tanh(x):
    return _mkreal(mp.tanh(_f(x)))


def sinh(x):
    return _mkreal(mp.sinh(_f(x)))


def cosh(x):
    return _mkreal(mp.cosh(_f(x)))


def ceil(x):
    return int(mp.ceil(_f(x)))


def floor(x):
    return int(mp.floor(_f(x)))


def round(x, n=0):  # noqa: A001 - shadowing is intentional, matches sage.all
    import builtins
    return builtins.round(float(x), n)


def binomial(n, k):
    return _mkreal(mp.binomial(_f(n), _f(k)))


def prod(it):
    out = mp.mpf(1)
    for v in it:
        out *= _f(v)
    return out


def zeta(x):
    return _mkreal(mp.zeta(_f(x)))


def parent(x):
    return type(x)


def cached_function(f):
    return functools.lru_cache(maxsize=None)(f)


def find_root(f, a, b, **kw):
    return mp.findroot(f, (mp.mpf(a), mp.mpf(b)), solver="anderson")


euler_gamma = mp.euler


def line(*a, **kw):  # plotting only (simulator.py); never on a cost path
    return None


class PowerSeriesRing:
    """Stub. Only gb.py (Arora-GB) needs it, and that attack is never
    competitive at Kyber sizes. Importing must succeed; CALLING must fail
    loudly rather than silently return a wrong cost."""

    def __init__(self, *a, **kw):
        raise NotImplementedError(
            "PowerSeriesRing is not shimmed: the Arora-GB attack is unavailable. "
            "Any 'best attack' claim from this harness is scoped to the attacks "
            "it actually served."
        )


class RealDistribution:
    """chi-squared and beta CDFs, the only two the estimator uses."""

    def __init__(self, kind, params, *a, **kw):
        from scipy import stats

        if kind == "chisquared":
            df = float(params)
            self._d = stats.chi2(df)
        elif kind == "beta":
            a_, b_ = params
            self._d = stats.beta(float(a_), float(b_))
        else:
            raise NotImplementedError(f"RealDistribution kind {kind!r} not shimmed")

    def cum_distribution_function(self, x):
        return float(self._d.cdf(float(x)))


__all__ = [n for n in dir() if not n.startswith("_")]
