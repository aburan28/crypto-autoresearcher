#!/usr/bin/env python3
"""Check archived signed-Frobenius data for the NIST Koblitz curves.

This is a deterministic consistency audit of an existing endomorphism-sweep
artifact.  It trusts that artifact's point-check booleans, then independently
recomputes the scalar identities and action orders they imply.  It does not
run Pollard rho, emit a primality certificate, or turn the random-map model
into a measured attack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from sympy import isprime


KOBLITZ_CURVES = ("K-163", "K-233", "K-283", "K-409", "K-571")
REQUIRED_TAU_CHECKS = (
    "order_from_lucas_sequence",
    "h_equals_E(F_2)",
    "tau^2-mu*tau+2=0_on_points",
    "tau(G)=[lambda]G",
    "N(delta)=n",
)


class AuditError(ValueError):
    """The supplied structural artifact does not certify the claimed action."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _field_degree(field: str) -> int:
    match = re.fullmatch(r"F_2\^(\d+), .+", field)
    if not match:
        raise AuditError(f"unrecognized binary-field identity: {field!r}")
    return int(match.group(1))


def _ztau_norm(delta: tuple[int, int], mu: int) -> int:
    a, b = delta
    return a * a + mu * a * b + 2 * b * b


def audit_curve(name: str, record: dict[str, Any]) -> dict[str, Any]:
    """Return exact and model fields for one certified NIST K curve."""
    m = _field_degree(record.get("field", ""))
    _require(name == f"K-{m}", f"{name}: field degree does not match curve name")
    _require(_is_prime(m) and m % 2 == 1, f"{name}: m must be an odd prime")
    _require(record.get("verified") is True, f"{name}: curve identity/order is not verified")
    _require(record.get("koblitz") is True, f"{name}: artifact does not classify the curve as Koblitz")
    _require(record.get("b_bits") == 1, f"{name}: b is not certified as 1")

    exact = record.get("exact") or {}
    _require(exact.get("D_K") == -7, f"{name}: maximal CM discriminant is not -7")

    tau = record.get("tau") or {}
    checks = tau.get("checks") or {}
    for check in REQUIRED_TAU_CHECKS:
        _require(checks.get(check) is True, f"{name}: missing or failed tau check {check!r}")
    _require(tau.get("all_checks_pass") is True, f"{name}: aggregate tau check did not pass")

    mu = int(tau.get("mu"))
    _require(mu in (-1, 1), f"{name}: mu is not +/-1")
    delta_raw = tau.get("delta")
    _require(isinstance(delta_raw, list) and len(delta_raw) == 2, f"{name}: malformed delta")
    delta = (int(delta_raw[0]), int(delta_raw[1]))
    subgroup_order = _ztau_norm(delta, mu)
    _require(subgroup_order > 2 and subgroup_order % 2 == 1, f"{name}: invalid odd subgroup order")
    _require(bool(isprime(subgroup_order)), f"{name}: reconstructed subgroup order is not prime")

    q = int(record.get("q"))
    trace = int(record.get("t"))
    cofactor = 3 - mu
    _require(q == 1 << m, f"{name}: q != 2^m")
    _require(q + 1 - trace == cofactor * subgroup_order, f"{name}: trace/order/cofactor mismatch")

    eigenvalue = int(tau.get("eigenvalue"), 0)
    _require(0 < eigenvalue < subgroup_order, f"{name}: eigenvalue is outside the subgroup field")
    _require(
        (eigenvalue * eigenvalue - mu * eigenvalue + 2) % subgroup_order == 0,
        f"{name}: eigenvalue does not satisfy lambda^2-mu*lambda+2",
    )
    _require(pow(eigenvalue, m, subgroup_order) == 1, f"{name}: lambda^m != 1")
    _require(eigenvalue != 1, f"{name}: lambda has trivial action")

    # Since m is prime, lambda^m=1 and lambda!=1 prove ord(lambda)=m.  Since
    # m and the subgroup order are odd, adjoining negation doubles the free
    # nonzero-point orbit to exactly 2m.
    action_order = m
    signed_action_order = 2 * m
    gain_factor = math.sqrt(m)
    gain_bits = 0.5 * math.log2(m)
    break_even = 1.0 / gain_factor

    rho_plain_log2 = 0.5 * math.log2(math.pi * subgroup_order / 2)
    rho_negation_log2 = 0.5 * math.log2(math.pi * subgroup_order / 4)
    rho_signed_tau_log2 = 0.5 * math.log2(math.pi * subgroup_order / (4 * m))

    return {
        "curve": name,
        "field_degree_m": m,
        "subgroup_order": str(subgroup_order),
        "subgroup_bits": subgroup_order.bit_length(),
        "cofactor": cofactor,
        "cm_fundamental_discriminant": -7,
        "subgroup_prime_screen": "sympy.isprime passed; no primality certificate is emitted here",
        "tau": {
            "mu": mu,
            "eigenvalue": hex(eigenvalue),
            "eigenvalue_polynomial_mod_r": True,
            "action_order": action_order,
            "signed_action_order": signed_action_order,
            "free_on_nonzero_prime_order_subgroup": "derived conditional on the archived prime-subgroup identity",
        },
        "random_map_model": {
            "plain_rho_log2_expected_transitions": rho_plain_log2,
            "negation_rho_log2_expected_transitions": rho_negation_log2,
            "signed_tau_rho_log2_expected_transitions": rho_signed_tau_log2,
            "signed_tau_gain_vs_plain_factor": math.sqrt(2 * m),
            "signed_tau_gain_vs_plain_bits": 0.5 * math.log2(2 * m),
            "signed_tau_gain_vs_negation_factor": gain_factor,
            "signed_tau_gain_vs_negation_bits": gain_bits,
            "conditional_negation_only_endpoint_max_step_cost_ratio_vs_source_signed_tau": break_even,
        },
        "audit_scope": (
            "derived action-order consistency conditional on archived point/action checks and prime-subgroup identity; "
            "no primality certificate, rho timing, or solve"
        ),
    }


def audit_document(document: dict[str, Any], source_sha256: str | None = None) -> dict[str, Any]:
    curves = document.get("curves")
    _require(isinstance(curves, dict), "input has no curve mapping")
    rows = []
    for short_name in KOBLITZ_CURVES:
        key = f"nist/{short_name}"
        _require(key in curves, f"input is missing {key}")
        rows.append(audit_curve(short_name, curves[key]))
    return {
        "schema": "koblitz-rho-structural-audit-v1",
        "source": {
            "kind": "archived endomorphism-sweep artifact",
            "std_curves_commit": document.get("std_curves_commit"),
            "sha256": source_sha256,
            "limitations": (
                "point/action checks are consumed as archived booleans; this tool does not replay their point arithmetic"
            ),
        },
        "model": {
            "plain_rho_expected_transitions": "sqrt(pi*r/2)",
            "negation_rho_expected_transitions": "sqrt(pi*r/4)",
            "signed_tau_rho_expected_transitions": "sqrt(pi*r/(4*m))",
            "gain_vs_same_curve_negation": "sqrt(m) = 2^(log2(m)/2)",
            "warning": "derived random-map work, not measured wall time or an attack projection",
        },
        "all_consistency_checks_pass": True,
        "curves": rows,
        "unresolved_measurements": [
            "fully charged source signed-tau canonicalization cost",
            "explicit vertical isogeny construction, evaluation, dual, and subgroup transport",
            "endpoint negation-only and transported-action transition cost",
            "rho walk, distinguished-point, collision-recovery, and verification cost",
        ],
    }


def markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# NIST Koblitz signed-Frobenius rho audit",
        "",
        "Status: **derived consistency audit of archived certificates and random-map model; no rho timing or solve.**",
        "",
        "| curve | ord(lambda) | signed orbit | gain vs negation (bits) | transitions factor | conditional endpoint ceiling |",
        "|:--|--:|--:|--:|--:|--:|",
    ]
    for row in audit["curves"]:
        model = row["random_map_model"]
        lines.append(
            f"| {row['curve']} | {row['tau']['action_order']} | {row['tau']['signed_action_order']} | "
            f"{model['signed_tau_gain_vs_negation_bits']:.6f} | "
            f"{model['signed_tau_gain_vs_negation_factor']:.6f}x | "
            f"{100 * model['conditional_negation_only_endpoint_max_step_cost_ratio_vs_source_signed_tau']:.4f}% |"
        )
    lines.extend(
        [
            "",
            "The gain column compares with the same curve's negation-only rho. The additional half bit in the",
            "plain-rho comparison is not a second Koblitz advantage. Conditional on an endpoint having only",
            "negation as a usable quotient, the floor ceiling is its maximum cost per transition",
            "relative to one fully charged source signed-tau transition, needed",
            "to offset the lost orbit quotient before setup and transfer costs.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="endosweep nist.json")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args(argv)

    raw = args.input.read_bytes()
    document = json.loads(raw)
    audit = audit_document(document, hashlib.sha256(raw).hexdigest())
    encoded = json.dumps(audit, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(encoded)
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(audit))
    if not args.json_out and not args.markdown_out:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
