"""Part 1 scoring surface: ord_n(2) census + k | r - 1.

Exposes:
  - packaging_surface(): toy dry probes (packaging integrity only)
  - score_part1(...): callable Part 1 census / k|r-1 scoring API for a later
    authorized /run

This scoring-impl card (TASK-20260930-8ec263 / BATCH-075541) implements the
API but does NOT execute the deployed Part 1 census, mint RUN-*, or write under
experiments/EXP-BINSTD-178742/runs/. No AUXIN/FROB/QSP values.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple


# Deployed census degrees from structural_certificate (specification.yaml).
DEPLOYED_N: List[int] = [131, 163, 233, 283, 409, 571]

# Seven toy degrees from structural_certificate.toy_degree_screen.
TOY_N_POSITIVE: List[int] = [17, 23, 31, 41]
TOY_N_FORCED_NEGATIVE: List[int] = [19, 29, 37]
TOY_N: List[int] = TOY_N_POSITIVE + TOY_N_FORCED_NEGATIVE

# Eleven standardized rows: primary-sourced k,r where frozen; c2pnb NOT COMPUTED.
# Parameters are the contract's frozen design figures (structural_certificate.
# deployed_rows). A later scientific /run still owes primary-source re-read
# under SR-SRC-*; embedding them here enables the scoring capability path.
STANDARDIZED_ROWS: List[Dict[str, Any]] = [
    {
        "row": "K-163",
        "source": "SRC-FIPS",
        "m": 163,
        "k": 163,
        "r": "5846006549323611672814741753598448348329118574063",
        "primary_sourced": True,
    },
    {
        "row": "K-233",
        "source": "SRC-FIPS",
        "m": 233,
        "k": 233,
        "r": "3450873173395281893717377931138512760570940988862252126328087024741343",
        "primary_sourced": True,
    },
    {
        "row": "K-283",
        "source": "SRC-FIPS",
        "m": 283,
        "k": 283,
        "r": "3885337784451458141838923813647037813284811733793061324295874997529815829704422603873",
        "primary_sourced": True,
    },
    {
        "row": "K-409",
        "source": "SRC-FIPS",
        "m": 409,
        "k": 409,
        "r": "330527984395124299475957654016385519914202341482140609642324395022880711289249191050673258457777458014096366590617731358671",
        "primary_sourced": True,
    },
    {
        "row": "K-571",
        "source": "SRC-FIPS",
        "m": 571,
        "k": 571,
        "r": "1932268761508629172347675945465993672149463664853217499328617625725759571144780212268133978522706711834706712800825351461273674974066617311929682421617092503555733685276673",
        "primary_sourced": True,
    },
    {
        "row": "ECC2K-130",
        "source": "SRC-ECC2K130",
        "m": 131,
        "k": 131,
        "r": "680564733841876926932320129493409985129",
        "primary_sourced": True,
    },
    {
        "row": "c2pnb176v1",
        "source": "SRC-X962",
        "m": 176,
        "k": None,
        "r": None,
        "primary_sourced": False,
        "reason": "IMP-X962",
    },
    {
        "row": "c2pnb208w1",
        "source": "SRC-X962",
        "m": 208,
        "k": None,
        "r": None,
        "primary_sourced": False,
        "reason": "IMP-X962",
    },
    {
        "row": "c2pnb272w1",
        "source": "SRC-X962",
        "m": 272,
        "k": None,
        "r": None,
        "primary_sourced": False,
        "reason": "IMP-X962",
    },
    {
        "row": "c2pnb304w1",
        "source": "SRC-X962",
        "m": 304,
        "k": None,
        "r": None,
        "primary_sourced": False,
        "reason": "IMP-X962",
    },
    {
        "row": "c2pnb368w1",
        "source": "SRC-X962",
        "m": 368,
        "k": None,
        "r": None,
        "primary_sourced": False,
        "reason": "IMP-X962",
    },
]


def ord_n_of_2_by_iteration(n: int) -> int:
    """Multiplicative order of 2 modulo n (n odd positive integer)."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")


def _positive_divisors(m: int) -> List[int]:
    divs: List[int] = []
    i = 1
    while i * i <= m:
        if m % i == 0:
            divs.append(i)
            if i * i != m:
                divs.append(m // i)
        i += 1
    divs.sort()
    return divs


def ord_n_of_2_by_divisor_test(n: int) -> int:
    """ord_n(2) via testing divisors of n-1 (prime-divisor route for prime n).

    Finds the least d | (n-1) with 2^d ≡ 1 mod n.
    """
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be an odd integer > 2")
    nm1 = n - 1
    for d in _positive_divisors(nm1):
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"no divisor d of {nm1} with 2^d ≡ 1 mod {n}")


def _prime_factors(m: int) -> List[int]:
    """Trial factorization of a small positive integer into primes."""
    if m <= 1:
        return []
    factors: List[int] = []
    x = m
    p = 2
    while p * p <= x:
        if x % p == 0:
            factors.append(p)
            while x % p == 0:
                x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        factors.append(x)
    return factors


def verify_ord_n_2(n: int, d: int) -> bool:
    """Confirm d = ord_n(2): 2^d ≡ 1 and 2^(d/p) ≠ 1 for every prime p|d."""
    if d <= 0 or pow(2, d, n) != 1:
        return False
    for p in _prime_factors(d):
        if pow(2, d // p, n) == 1:
            return False
    return True


def stable_dimensions_from_ord(n: int, d: int) -> Dict[str, Any]:
    """Derive tau-stable F_2-subspace dimensions from d = ord_n(2) (n prime).

    Phi_n factors into f = (n-1)/d irreducibles of degree d over F_2. Stable
    dimensions are {b*d, b*d+1 for b = 0..f}, i.e. 0,1,...,n-1,n.
    """
    if n <= 1 or (n - 1) % d != 0:
        raise ValueError(f"d={d} does not divide n-1={n - 1}")
    f = (n - 1) // d
    dims: List[int] = []
    for b in range(f + 1):
        dims.append(b * d)
        dims.append(b * d + 1)
    usable = [x for x in dims if x not in (0, 1, n - 1, n)]
    return {
        "factors_of_Phi_n": {"count": f, "degree": d},
        "stable_dimensions": dims,
        "usable_dimensions": usable,
    }


def _stable_subspace_count(f: int) -> int:
    """Match structural_certificate counts: 2^{f+1} (include F_2 constants)."""
    return 1 << (f + 1)


def k_divides_r_minus_1(k: int, r: int) -> bool:
    """Exact arithmetic predicate: k | (r - 1)."""
    if k <= 0:
        raise ValueError("k must be positive")
    return (r - 1) % k == 0


def score_ord_row(n: int) -> Dict[str, Any]:
    """Score one n: ord_n(2) by both routes + stable-dimension set."""
    by_iter = ord_n_of_2_by_iteration(n)
    by_div = ord_n_of_2_by_divisor_test(n)
    routes_agree = by_iter == by_div
    d = by_div if routes_agree else by_iter
    verified = verify_ord_n_2(n, d) if routes_agree else False
    stab = stable_dimensions_from_ord(n, d) if routes_agree and (n - 1) % d == 0 else None
    row: Dict[str, Any] = {
        "n": n,
        "ord_n_2_iteration": by_iter,
        "ord_n_2_divisor_test": by_div,
        "routes_agree": routes_agree,
        "ord_n_2": d if routes_agree else None,
        "order_verified": verified,
    }
    if stab is not None:
        f = stab["factors_of_Phi_n"]["count"]
        row["factors_of_Phi_n"] = stab["factors_of_Phi_n"]
        row["stable_dimensions"] = stab["stable_dimensions"]
        row["stable_subspace_count"] = _stable_subspace_count(f)
        row["usable_dimensions"] = stab["usable_dimensions"]
    row["ok"] = bool(routes_agree and verified and stab is not None)
    return row


def score_k_divides_row(spec_row: Dict[str, Any]) -> Dict[str, Any]:
    """Score one standardized k | r - 1 row."""
    out: Dict[str, Any] = {
        "row": spec_row["row"],
        "source": spec_row.get("source"),
        "m": spec_row.get("m"),
        "primary_sourced": bool(spec_row.get("primary_sourced")),
    }
    k = spec_row.get("k")
    r_raw = spec_row.get("r")
    if k is None or r_raw is None:
        out["k"] = None
        out["r"] = None
        out["r_mod_k"] = None
        out["verdict"] = "NOT COMPUTED"
        out["reason"] = spec_row.get("reason", "IMP-X962")
        out["ok"] = True  # expected NOT COMPUTED is not a failure
        return out
    r = int(r_raw)
    divides = k_divides_r_minus_1(int(k), r)
    out["k"] = int(k)
    out["r"] = str(r)
    out["r_digit_count"] = len(str(r))
    out["r_mod_k"] = r % int(k)
    out["verdict"] = "TRUE" if divides else "FALSE"
    out["ok"] = True
    return out


def score_part1(
    ns: Optional[Sequence[int]] = None,
    rows: Optional[Sequence[Dict[str, Any]]] = None,
    *,
    include_toys: bool = False,
    write_artifacts: bool = False,
) -> Dict[str, Any]:
    """Compute Part 1 census and k|r-1 verdicts (in-memory scoring API).

    Args:
      ns: degrees for ord_n(2) census. Default DEPLOYED_N when include_toys is
          false; DEPLOYED_N+TOY_N when include_toys is true. Pass an explicit
          list (e.g. toys only) for unit smoke without a deployed census.
      rows: standardized k|r-1 row specs. Default STANDARDIZED_ROWS (eleven).
      include_toys: when ns is None, also include the seven toy degrees.
      write_artifacts: must remain False on the scoring-impl card. Artifact
          writes under experiments/.../runs/ belong to a later /run.

    Returns a structured result. Does not mint RUN-* and does not write files.
    """
    if write_artifacts:
        raise ValueError(
            "write_artifacts=True is forbidden on the scoring-impl path; "
            "artifact writes belong to a later authorized /run under runs/"
        )
    if ns is None:
        ns_list = list(DEPLOYED_N)
        if include_toys:
            ns_list = list(DEPLOYED_N) + list(TOY_N)
    else:
        ns_list = list(ns)
    row_specs = list(STANDARDIZED_ROWS if rows is None else rows)

    census_rows = [score_ord_row(n) for n in ns_list]
    k_rows = [score_k_divides_row(spec) for spec in row_specs]

    false_verdicts = [r for r in k_rows if r.get("verdict") == "FALSE"]
    census_ok = all(r.get("ok") for r in census_rows)
    k_ok = all(r.get("ok") for r in k_rows)
    # TB-3 / SR-4: any computed FALSE verdict is a Part-1 halt signal for later /run.
    halt_before_part2 = len(false_verdicts) > 0

    return {
        "module": "part1_surface",
        "stage": "P1_census_and_k_divides_r_minus_1",
        "status": "scored",
        "scientific_scoring": True,
        "write_artifacts": False,
        "runs_minted": False,
        "ns": ns_list,
        "census": census_rows,
        "k_divides_verdicts": k_rows,
        "standardized_row_count": len(k_rows),
        "false_verdicts": [r["row"] for r in false_verdicts],
        "halt_before_part2_SR4": halt_before_part2,
        "ok": bool(census_ok and k_ok),
        "note": (
            "In-memory Part 1 scoring. Does not write part1_census.json or mint "
            "RUN-*. Deployed primary-source re-read under SR-SRC-* remains owed "
            "by the scientific /run that persists artifacts."
        ),
    }


def packaging_surface() -> Dict[str, Any]:
    """Dry packaging probe on tiny n only — not Part 1 scoring."""
    toys = [3, 5, 7, 11, 13, 17]
    rows: List[Dict[str, Any]] = []
    ok = True
    for n in toys:
        by_iter = ord_n_of_2_by_iteration(n)
        by_div = ord_n_of_2_by_divisor_test(n)
        agree = by_iter == by_div
        if not agree:
            ok = False
        rows.append(
            {
                "n": n,
                "ord_n_2_iteration": by_iter,
                "ord_n_2_divisor_test": by_div,
                "routes_agree": agree,
            }
        )
    k_checks: List[Tuple[int, int, bool, bool]] = [
        (3, 7, True, k_divides_r_minus_1(3, 7)),
        (5, 7, False, k_divides_r_minus_1(5, 7)),
        (17, 65587, True, k_divides_r_minus_1(17, 65587)),
    ]
    for k, r, expected, got in k_checks:
        if got != expected:
            ok = False
    # Capability smoke: score_part1 on toys only (not deployed census).
    toy_score = score_part1(ns=toys, rows=[], include_toys=False)
    if not toy_score.get("ok"):
        ok = False
    return {
        "module": "part1_surface",
        "stage": "P1_census_and_k_divides_r_minus_1",
        "status": "packaging_probe_with_scoring_api",
        "scientific_scoring": False,
        "score_part1_callable": True,
        "toy_ord_rows": rows,
        "toy_score_part1_smoke": {
            "ok": toy_score.get("ok"),
            "ns": toy_score.get("ns"),
            "status": toy_score.get("status"),
        },
        "k_divides_checks": [
            {
                "k": k,
                "r": r,
                "expected": expected,
                "got": got,
                "ok": got == expected,
            }
            for k, r, expected, got in k_checks
        ],
        "ok": ok,
        "note": (
            "Packaging surface + score_part1 API present. Deployed Part 1 census "
            "(n in {131,163,233,283,409,571} and eleven standardized k|r-1 "
            "checks) is not executed here; invoke score_part1 via run.py "
            "--run --score-part1 on a later authorized /run."
        ),
    }
