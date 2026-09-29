"""Protocol constants, seed labels and frozen fixtures for EXP-ICEX-aaccfc
protocol v3 (specification.yaml + AMD-20260926-ced670 + AMD-20260929-143d11;
later amendments govern). v3 accepts the v2 implementation's literal readings
and changes no label, so the frozen namespace stays EXP-ICEX-aaccfc/v2.

Seed labels (SHA256 of UTF-8, ``|``-joined; C-4 / C-6 name the kinds marked
"protocol", the rest are implementation choices disclosed in implementation.md):

  <ns>|target|<bits>|<seed>                    protocol (C-4, Q = k*G)
  <ns>|attempt|<bits>|<seed>|<j>               protocol (C-4, a_j and b_j from one hash)
  <ns>|heldout|<bits>|<seed>|<i>               protocol (C-4 stage 2, S = h*G)
  <ns>|descent|<bits>|<seed>|<t>               protocol (C-4 stage 3, k_t)
  <ns>|randfb|<bits>|<seed>|<i>                protocol (C-6 matched null)
  <ns>|descent_r|<bits>|<seed>|<t>|<i>         implementation (descent randomizer r)
  <ns>|rho|<bits>|<seed>|<t>                   implementation (C-6 baseline target)
  <ns>|rho_walk|<bits>|<seed>|<t>|<tag>        implementation (walk multipliers)
  <ns>|scramble|<bits>|<seed>|<fb>|<i>         implementation (C-6 known-false permutation)
  <ns>|lanczos|<bits>|<seed>|<fb>|<try>|<i>    implementation (row scaling D)
  <ns>|audit|<bits>|<seed>|<j>                 implementation (C-6 10% audit selection)
  <ns>|bootstrap                               implementation (C-5 bootstrap)

The frozen namespace is ``EXP-ICEX-aaccfc/v2``. Smoke checks use
``smoke|EXP-ICEX-aaccfc/v2`` so no frozen label is evaluated before an
admitted run.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO_ROOT = EXP_DIR.parent.parent
EXPERIMENT_ID = "EXP-ICEX-aaccfc"
PROTOCOL_VERSION = 3

SPECIFICATION = EXP_DIR / "specification.yaml"
AMENDMENT = EXP_DIR / "amendments" / "AMD-20260926-ced670.yaml"
AMENDMENT_V3 = EXP_DIR / "amendments" / "AMD-20260929-143d11.yaml"
AMENDMENT_V3_SHA256 = "36cad68cee9ff8da0ce86e94c2f9548f05ffd95a5bdaf32eeaeaf32c0514dac7"
SDEG_DIR = EXP_DIR.parent / "EXP-SDEG-85eefd"
B0_AMENDMENT = SDEG_DIR / "amendments" / "AMD-20260926-3479cf.yaml"
FIXTURE_JSON = SDEG_DIR / "amendments" / "ic_leads_fixtures_v2.json"
FIXTURE_GEN = SDEG_DIR / "amendments" / "ic_leads_fixtures_v2.py"
FROZEN_JSON_SHA256 = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
FROZEN_GEN_SHA256 = "bde44afb3e14c34d97bf50c154456565d12f0b5a1d33d63b473f0f4124b1f3b2"

FROZEN_NS = "EXP-ICEX-aaccfc/v2"
SMOKE_NS = "smoke|EXP-ICEX-aaccfc/v2"

# C-3 cost units
UNIT_MUL = 1
UNIT_INV = 10
UNIT_POINT_ADD = 13
UNIT_PROBE = 1
UNIT_LA_MUL = 1

# C-2 / C-4 / C-5 / C-6 constants
M_PRIMARY = 5
M_STAGE_COST_ONLY = (6, 8)
N_HELDOUT = 256
EXCESS_ROWS = 10
N_DESCENTS = 16
N_RHO_TARGETS = 64
RHO_CONST = 0.886
BOOTSTRAP_RESAMPLES = 2000
AUDIT_FRACTION_MOD = 10  # attempt j is replayed iff h(audit label) % 10 == 0
MEMORY_LIMIT_BYTES = 8 * 1024 ** 3


class RejectionFailure(RuntimeError):
    """A uniform draw fell in the rejection zone (probability < n / 2^128)."""


def h(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def lab(ns: str, kind: str, *parts) -> str:
    return "|".join([ns, kind] + [str(x) for x in parts])


def uniform(label: str, n: int) -> int:
    """Uniform integer in [0, n) by rejection sampling on one SHA256 value."""
    v = h(label)
    limit = ((1 << 256) // n) * n
    if v >= limit:
        raise RejectionFailure(label)
    return v % n


def uniform_pair(label: str, n: int) -> tuple[int, int]:
    """Two uniform integers in [0, n) from ONE SHA256 value (C-4 draws a_j and b_j
    from a single label): high 128 bits -> first, low 128 bits -> second, each
    by rejection sampling on its 128-bit half."""
    v = h(label)
    hi, lo = v >> 128, v & ((1 << 128) - 1)
    limit = ((1 << 128) // n) * n
    if hi >= limit or lo >= limit:
        raise RejectionFailure(label)
    return hi % n, lo % n


def rng_seed(label: str) -> int:
    return h(label) >> 192


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_fixtures() -> list[dict]:
    return json.loads(FIXTURE_JSON.read_text())[EXPERIMENT_ID]


def fixture(bits: int, seed: int) -> dict:
    for f in load_fixtures():
        if f["bits"] == bits and f["seed"] == seed:
            return f
    raise KeyError((bits, seed))


def fixture_id(f: dict) -> str:
    return f"b{f['bits']}-s{f['seed']}"


def fb_bound(p: int, m: int) -> int:
    """B_m = ceil(p^(1/m)) computed exactly in integers (C-2)."""
    b = max(1, int(round(p ** (1.0 / m))))
    while b ** m < p:
        b += 1
    while b > 1 and (b - 1) ** m >= p:
        b -= 1
    return b


def find_sage() -> str | None:
    for c in (os.environ.get("SAGE"), "/Users/adamburan/.local/bin/sage", "/usr/local/bin/sage",
              "/Volumes/SSD990/cryptanalysis/sage"):
        if c and Path(c).exists():
            return c
    return None


def reproduce_fixtures(out_path: Path, sage: str | None = None, timeout: int = 3600) -> dict:
    """C-1: re-run the frozen generator with Sage and byte-compare to the frozen JSON."""
    sage = sage or find_sage()
    if sage is None:
        return {"byte_identical": False, "error": "sage not found"}
    env = dict(os.environ)
    tmp = env.get("TMPDIR") or str(EXP_DIR)
    env.setdefault("DOT_SAGE", str(Path(tmp) / "dot_sage_icex"))
    res = subprocess.run([sage, "-python", str(FIXTURE_GEN)], capture_output=True, timeout=timeout,
                         env=env)
    Path(out_path).write_bytes(res.stdout)
    frozen = FIXTURE_JSON.read_bytes()
    return {
        "sage": sage,
        "generator_sha256": sha256_file(FIXTURE_GEN),
        "generator_sha256_matches_amendment": sha256_file(FIXTURE_GEN) == FROZEN_GEN_SHA256,
        "frozen_json_sha256": hashlib.sha256(frozen).hexdigest(),
        "frozen_json_sha256_matches_amendment": hashlib.sha256(frozen).hexdigest() == FROZEN_JSON_SHA256,
        "reproduced_sha256": hashlib.sha256(res.stdout).hexdigest(),
        "byte_identical": res.stdout == frozen,
        "returncode": res.returncode,
        "stderr_tail": res.stderr.decode(errors="replace")[-2000:],
    }


def rho_reference_units(q: int) -> float:
    """C-5 denominator: 13 * 0.886 * sqrt(q)."""
    return UNIT_POINT_ADD * RHO_CONST * math.sqrt(q)
