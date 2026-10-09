"""Optional PARI/GP cross-checks. Every function returns None when gp is absent, so the
runners never depend on it; results are recorded as controls with provenance 'pari-gp'."""
from __future__ import annotations

import shutil
import subprocess


def gp_available():
    return shutil.which("gp") is not None


def gp_version():
    if not gp_available():
        return None
    out = subprocess.run(["gp", "--version"], capture_output=True, text=True)
    return (out.stdout + out.stderr).strip().splitlines()[0].strip()


def _run(script, timeout=600):
    if not gp_available():
        return None
    try:
        out = subprocess.run(["gp", "-q", "-f"], input="default(parisize, 64000000);\n" + script + "\n",
                             capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    lines = [ln for ln in out.stdout.splitlines() if ln.strip() and "Warning" not in ln]
    return lines


def ellrank_Q(ainvs, timeout=600):
    """[lower, upper, ...] from ellrank for E/Q given [a1,a2,a3,a4,a6]; None if unavailable."""
    a = ",".join(str(x) for x in ainvs)
    lines = _run(f"E = ellinit([{a}]); r = ellrank(E); print(r[1], \" \", r[2]);", timeout)
    if not lines:
        return None
    try:
        lo, hi = lines[-1].split()
        return {"rank_lower": int(lo), "rank_upper": int(hi)}
    except ValueError:
        return None


def nfdisc(g, timeout=120):
    """Field discriminant of Q[t]/(g) (g low->high integer coefficients); None if unavailable."""
    poly = "+".join(f"({c})*y^{i}" for i, c in enumerate(g) if c)
    lines = _run(f"print(nfdisc({poly}));", timeout)
    if not lines:
        return None
    try:
        return int(lines[-1])
    except ValueError:
        return None
