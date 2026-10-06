"""Independent arithmetic path B for EXP-AUXIN-339fb0.

Python standard library ONLY (admission item 6: every path B module).
Does NOT import factor_path_a or share factorization code with path A.

Accepts factor lists / recorded parts and:
  1. recomputes products;
  2. independently verifies certificates via cert_verify;
  3. recomputes typed exponents, bounds, depths and bins via e_eval;
  4. enumerates witness sets for BOUND rows.

Never recovers a discrete logarithm and never runs Cheon.
Never opens any path under experiments/EXP-AUXIN-7e2e3d/.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import cert_verify
import e_eval


def product_check(
    n: int, prime_powers: Dict[int, int], recorded_parts: Optional[Sequence[int]] = None
) -> bool:
    prod = 1
    for p, e in prime_powers.items():
        prod *= int(p) ** int(e)
    if recorded_parts:
        for c in recorded_parts:
            prod *= int(c)
    return prod == int(n)


def verify_primes(
    prime_powers: Dict[int, int], certificates: Dict[str, Any]
) -> Dict[str, Any]:
    """Verify each prime's certificate with the independent verifier."""
    out: Dict[str, Any] = {"all_ok": True, "per_prime": {}}
    for p in sorted(prime_powers):
        key = str(p)
        cert = certificates.get(key) or certificates.get(p)
        if cert is None:
            out["all_ok"] = False
            out["per_prime"][key] = {"ok": False, "detail": ["missing certificate"]}
            continue
        ok, detail = cert_verify.verify_certificate(cert)
        out["per_prime"][key] = {"ok": ok, "detail": detail}
        if not ok:
            out["all_ok"] = False
        elif int(cert.get("p", cert.get("steps", [{}])[0].get("N", -1))) not in (
            p,
            int(cert.get("p", -1)),
        ):
            # Pratt: cert.p must equal p; ECPP: first step N must equal p.
            if cert.get("kind") == "pratt" and int(cert["p"]) != p:
                out["all_ok"] = False
                out["per_prime"][key]["ok"] = False
                out["per_prime"][key]["detail"].append("cert.p mismatch")
            if cert.get("kind") == "ecpp":
                first_N = int(cert["steps"][0]["N"])
                if first_N != p:
                    out["all_ok"] = False
                    out["per_prime"][key]["ok"] = False
                    out["per_prime"][key]["detail"].append("ECPP top N mismatch")
    return out


def verify_compositeness_parts(
    parts: Sequence[int], witnesses: Dict[str, Any]
) -> Dict[str, Any]:
    out: Dict[str, Any] = {"all_ok": True, "per_part": {}}
    for c in parts:
        key = str(c)
        w = witnesses.get(key)
        if w is None:
            out["all_ok"] = False
            out["per_part"][key] = {"ok": False, "detail": ["missing witness"]}
            continue
        a = w.get("a") if isinstance(w, dict) else w
        ok, detail = cert_verify.verify_compositeness_witness(int(c), a)
        out["per_part"][key] = {"ok": ok, "detail": detail}
        if not ok:
            out["all_ok"] = False
    return out


def recompute_branch(
    r: int,
    branch: str,
    prime_powers: Dict[int, int],
    recorded_parts: Optional[Sequence[int]] = None,
    certificates: Optional[Dict[str, Any]] = None,
    compositeness_witnesses: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Independent path-B recompute for one branch."""
    n = r - 1 if branch == "minus" else r + 1
    pp = {int(p): int(e) for p, e in prime_powers.items()}
    parts: List[int] = [int(c) for c in (recorded_parts or [])]
    result: Dict[str, Any] = {
        "path": "B",
        "branch": branch,
        "n": n,
        "product_check": product_check(n, pp, parts),
    }
    if certificates is not None:
        result["prime_verification"] = verify_primes(pp, certificates)
    if parts and compositeness_witnesses is not None:
        result["compositeness_verification"] = verify_compositeness_parts(
            parts, compositeness_witnesses
        )
    if not result["product_check"]:
        result["status"] = "VOID"
        result["reason"] = "product_mismatch"
        return result
    if certificates is not None and not result.get("prime_verification", {}).get(
        "all_ok", True
    ):
        result["status"] = "VOID"
        result["reason"] = "certificate_failure"
        return result
    try:
        ev = e_eval.evaluate_branch(
            r, branch, pp, recorded_parts=parts if parts else None
        )
        result.update(ev)
    except ValueError as exc:
        result["status"] = "VOID"
        result["reason"] = str(exc)
    return result


def packaging_surface() -> Dict[str, Any]:
    from decimal import getcontext

    return {
        "path": "B",
        "stdlib_only": True,
        "imports": ["cert_verify", "e_eval"],
        "precision_digits": int(getcontext().prec),
    }
