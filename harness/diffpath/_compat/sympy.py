"""DISCLOSED ENVIRONMENT SHIM -- not sympy, and it does not pretend to be.

harness/runner.py imports sympy at module scope, and uses it for EXACTLY ONE
thing: `sympy.__version__` in the environment block (harness/runner.py line
179).  sympy is NOT INSTALLED in this environment and IR-10 forbids acquiring
it over the network; `uv pip install --offline sympy` was attempted and failed
because the wheel is not in the local cache.  IR-6 forbids editing
harness/runner.py.

So this module is placed on sys.path by harness.diffpath.compat, and it reports
a version string that says plainly that sympy is ABSENT.  A run manifest
produced under this shim therefore records the truth -- "no sympy here" --
rather than a plausible-looking version number that would be a fabrication.

Nothing in EXP-DIFFP-fe894e is mathematically dependent on sympy: every
certificate in this experiment is `kind: none`, so runner's certificate
verification paths that would use a computer-algebra system are never entered.
This shim is an infrastructure workaround, disclosed as a protocol deviation
and as an anomaly, and it is NOT evidence about anything.
"""

__version__ = "ABSENT (sympy not installed; harness.diffpath disclosed shim)"
__shim__ = True
