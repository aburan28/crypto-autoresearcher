"""Static conformance boundary for a future ECTD v6 construction implementation.

The module deliberately contains no finite-field or curve execution engine.  It
freezes a total finite set of stages, deterministic algorithms, receipt fields,
and typed terminals that a later separately authorized implementation must
satisfy.  Validation here is structural; mathematical receipts remain subject
to independent replay before any target access.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any, Iterable, Mapping

CONSTRUCTION_SCHEMA = "crypto.autoresearch.ectd_v6_construction_witness.v1"
CONSTRUCTION_TERMINAL_SCHEMA = "crypto.autoresearch.ectd_v6_construction_terminal.v1"
RNG_STATE_SCHEMA = "crypto.autoresearch.ectd_v6_rng_state.v1"
RNG_ALGORITHM = "ECTD-SHAKE256-RANDBELOW-v1"
CONTROL_SCHEMA = "crypto.autoresearch.ectd_v6_control_measurement.v1"
CONTROL_MODULUS = 957_628_555_753
MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991

FINITE_STAGE_ORDER: tuple[str, ...] = (
    "SOURCE_CUSTODY",
    "FIELD",
    "CM_MODEL",
    "TWIST",
    "ORDER_CERTIFICATE",
    "ORDER_N_POINT",
    "Q_DIVISION_POLYNOMIAL",
    "ELL_DIVISION_POLYNOMIAL",
    "CYCLIC_LINES",
    "FROBENIUS_STABILITY",
    "CANONICAL_KERNEL",
    "VELU_CODOMAIN",
    "DUAL",
    "END_RING",
    "ENDPOINT_CONDUCTOR",
    "CONTROL",
    "COMPLETE",
)

TERMINAL_REGISTRY: dict[str, dict[str, str | tuple[str, ...]]] = {
    "SOURCE_GAP": {"class": "resource_incomplete", "stage": "SOURCE_CUSTODY", "details": ("missing_paths",)},
    "FIELD_CONSTRUCTION_FAILURE": {"class": "construction_rejection", "stage": "FIELD", "details": ("field_id", "reason")},
    "CM_MODEL_ABSENT": {"class": "construction_rejection", "stage": "CM_MODEL", "details": ("D_K", "enumerated_models")},
    "CM_MODEL_AMBIGUOUS": {"class": "construction_rejection", "stage": "CM_MODEL", "details": ("D_K", "canonical_keys")},
    "TWIST_ORDER_MISMATCH": {"class": "construction_rejection", "stage": "TWIST", "details": ("model_key", "twist_orders")},
    "ORDER_CERTIFICATE_FAILURE": {"class": "construction_rejection", "stage": "ORDER_CERTIFICATE", "details": ("curve_key", "claimed_M")},
    "ORDER_N_POINT_CERTIFICATE_FAILURE": {"class": "construction_rejection", "stage": "ORDER_N_POINT", "details": ("curve_key", "point_key", "N")},
    "Q_DIVISION_POLYNOMIAL_FAILURE": {"class": "construction_rejection", "stage": "Q_DIVISION_POLYNOMIAL", "details": ("curve_key", "q")},
    "ELL_DIVISION_POLYNOMIAL_FAILURE": {"class": "construction_rejection", "stage": "ELL_DIVISION_POLYNOMIAL", "details": ("curve_key", "ell")},
    "CYCLIC_LINE_ENUMERATION_FAILURE": {"class": "construction_rejection", "stage": "CYCLIC_LINES", "details": ("prime", "expected_lines", "observed_lines")},
    "FROBENIUS_STABILITY_FAILURE": {"class": "construction_rejection", "stage": "FROBENIUS_STABILITY", "details": ("kernel_sha256", "prime")},
    "KERNEL_CANONICALIZATION_FAILURE": {"class": "construction_rejection", "stage": "CANONICAL_KERNEL", "details": ("kernel_sha256", "reason")},
    "VELU_CODOMAIN_FAILURE": {"class": "construction_rejection", "stage": "VELU_CODOMAIN", "details": ("kernel_sha256", "codomain_key")},
    "DUAL_COMPOSITION_FAILURE": {"class": "construction_rejection", "stage": "DUAL", "details": ("isogeny_sha256", "degree")},
    "END_RING_CERTIFICATE_FAILURE": {"class": "construction_rejection", "stage": "END_RING", "details": ("endpoint_key", "reason")},
    "ENDPOINT_CONDUCTOR_FAILURE": {"class": "construction_rejection", "stage": "ENDPOINT_CONDUCTOR", "details": ("endpoint_key", "reported_conductor", "reason")},
    "D7_TWO_ADIC_CERTIFICATE_FAILURE": {"class": "construction_rejection", "stage": "ENDPOINT_CONDUCTOR", "details": ("endpoint_key", "observed_v2")},
    "D7_Q_ADIC_CERTIFICATE_FAILURE": {"class": "construction_rejection", "stage": "ENDPOINT_CONDUCTOR", "details": ("endpoint_key", "q", "observed_vq")},
    "HORIZONTAL_WHOLE_CONDUCTOR_FAILURE": {"class": "construction_rejection", "stage": "ENDPOINT_CONDUCTOR", "details": ("endpoint_A_conductor", "endpoint_B_conductor", "q")},
    "CONTROL_MEASUREMENT_INVALID": {"class": "construction_rejection", "stage": "CONTROL", "details": ("arm", "reason")},
    "RESOURCE_LIMIT": {"class": "resource_incomplete", "stage": "RESOURCE", "details": ("resource", "limit")},
    "DEPENDENCY_FAILURE": {"class": "failed_infrastructure", "stage": "INFRASTRUCTURE", "details": ("dependency", "reason")},
    "TIMEOUT": {"class": "failed_infrastructure", "stage": "INFRASTRUCTURE", "details": ("stage", "limit_seconds")},
    "CRASH": {"class": "failed_infrastructure", "stage": "INFRASTRUCTURE", "details": ("stage", "exit_code")},
    "UNREGISTERED_EXCEPTION": {"class": "invalid", "stage": "INTEGRITY", "details": ("exception_type",)},
    "CUSTODY_FAILURE": {"class": "invalid", "stage": "INTEGRITY", "details": ("path", "expected_sha256", "observed_sha256")},
    "FALSE_RECEIPT": {"class": "invalid", "stage": "INTEGRITY", "details": ("receipt_sha256", "reason")},
    "POST_TARGET_GATE_FAILURE": {"class": "invalid", "stage": "INTEGRITY", "details": ("gate", "target_bytes_existed")},
    "CONSTRUCTION_COMPLETE": {"class": "completed_static_construction", "stage": "COMPLETE", "details": ()},
}

CM_MODEL_BOUNDARY: dict[int, dict[str, Any]] = {
    -7: {"fundamental_discriminant": -7, "hilbert_class_polynomial": [3375, 1], "j_integer": -3375, "required_local_primes": [2, "q"]},
    -8: {"fundamental_discriminant": -8, "hilbert_class_polynomial": [-8000, 1], "j_integer": 8000, "required_local_primes": ["q"]},
    -11: {"fundamental_discriminant": -11, "hilbert_class_polynomial": [32768, 1], "j_integer": -32768, "required_local_primes": ["q"]},
    -19: {"fundamental_discriminant": -19, "hilbert_class_polynomial": [884736, 1], "j_integer": -884736, "required_local_primes": ["q"]},
}

CONSTRUCTION_BOUNDARY: dict[str, Any] = {
    "finite_fields": {
        "base": "Fp with canonical least nonnegative residues and p from the arithmetic witness",
        "extensions": "for each q or ell division-polynomial factor, the least positive extension degree containing its roots",
        "irreducible_polynomial_rule": "enumerate monic polynomials by increasing degree and ascending coefficient array; accept the first passing the exact Rabin irreducibility test using X^(p^d)-X gcd checks",
        "element_basis": "ascending powers of the distinguished root; coefficients are canonical Fp elements",
    },
    "cm_models": {
        "D_K_values": [-7, -8, -11, -19],
        "j_integers": {"-7": -3375, "-8": 8000, "-11": -32768, "-19": -884736},
        "enumeration": "reduce the frozen linear Hilbert class polynomial modulo p; for its sole root j use k=j/(1728-j), E:y^2=x^3+3*k*x+2*k; find the least quadratic nonresidue d>=2 and also enumerate its twist y^2=x^3+d^2*(3*k)*x+d^3*(2*k)",
        "both_twists_required": True,
        "selection": "retain the first model in JCS curve-key order whose independently certified order is M; reject absent or ambiguous keys before measurement",
    },
    "order_certificates": {
        "curve_order": "deterministic Schoof: process auxiliary primes in ascending order, rederive each division polynomial and trace residue, stop only when their product exceeds 4*isqrt(p)+2, recover the unique Hasse-interval trace by CRT, and prove #E(Fp)=p+1-t=M",
        "order_N_point": "scan x=0..p-1; choose the least nonnegative square root y (Tonelli-Shanks with least quadratic nonresidue) when it exists; set P=[h](x,y); accept the first finite P in x-then-y order satisfying the curve equation, [N]P=O, and P!=O",
    },
    "division_polynomials": {
        "primes": ["q", "horizontal_ell"],
        "normalization": "monic, ascending canonical coefficient array, no trailing zero",
        "verification": "rederive psi_l from the selected curve and verify every factor/product identity",
    },
    "cyclic_lines": {
        "domain": "all one-dimensional cyclic subgroup lines in E[l] over the minimal splitting field",
        "expected_count": "l+1",
        "ordering": "canonical monic kernel-polynomial JCS bytes then SHA-256",
        "multiplicity": "retain and report every line exactly once",
    },
    "frobenius_and_kernels": {
        "stability": "prove Frobenius maps every kernel line to itself before treating it as Fp-rational",
        "canonicalization": "multiply x-coordinate factors across the full Frobenius orbit, make monic, encode in the base field, and choose no representative after measurement",
    },
    "isogeny_checks": {
        "velu": "recompute the codomain from the canonical kernel and verify the normalized rational maps",
        "codomain": "canonicalize the codomain isomorphism class and independently certify its order M",
        "dual": "construct the canonical dual and verify dual(phi) o phi = [degree] and phi o dual(phi) = [degree] on symbolic maps or a complete certified basis",
    },
    "end_ring_receipts": {
        "per_endpoint": [
            "Frobenius polynomial X^2-tX+p and exact Delta_pi factorization",
            "exact endomorphism-order discriminant and whole conductor f_E",
            "an independently replayable order basis or equivalent certificate",
            "local valuation and stable-kernel enumeration for every prime dividing f_pi",
            "product of local prime powers equals the reported whole conductor",
        ],
        "vertical": "endpoint whole conductors are independently certified as 1 and q",
        "horizontal": "endpoint A and endpoint B are independently recomputed locally and each whole conductor equals q; copying, pair inference, q-parts alone, one endpoint, and gcd(ell,q) are insufficient",
        "D_K_minus_7": "both endpoints separately certify the 2-adic level and q-adic level; full horizontal endpoints each equal whole conductor q",
        "verification_algorithm": "set omega=(1+sqrt(D_K))/2 when D_K is 1 mod 4 and omega=sqrt(D_K)/2 otherwise; for every divisor f of f_pi in increasing order, rederive the order basis [1,f*omega], verify discriminant f^2*D_K, verify explicit rational maps for both basis generators commute with Frobenius, and use complete stable-line counts at every prime dividing f_pi/f to certify maximality; the unique passing f is the whole conductor",
    },
    "totality": "every finite stage returns its unique success record or the first registered terminal in stage order; resource and infrastructure terminals are not construction or scientific evidence",
}

CONTROL_CALL_SCHEDULE: tuple[dict[str, Any], ...] = (
    {"label": "factor_base", "trials": 24, "randbelow_calls_per_trial": 1, "purpose": "full 24-sample factor-base enumeration"},
    {"label": "m3", "trials": 32, "randbelow_calls_per_trial": 3, "purpose": "measured S3 relation hits"},
    {"label": "m4", "trials": 256, "randbelow_calls_per_trial": 4, "purpose": "measured S4 relation hits"},
)

CONTROL_ARMS: tuple[dict[str, Any], ...] = (
    {"arm": "ordinary", "plant_requested": False, "planting_code_enabled": False},
    {"arm": "planted", "plant_requested": True, "planting_code_enabled": True},
    {"arm": "planting_disabled_negative", "plant_requested": True, "planting_code_enabled": False},
)


def _assert_canonical_domain(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise ValueError("ASCII keys required")
            _assert_canonical_domain(item)
    elif isinstance(value, list):
        for item in value:
            _assert_canonical_domain(item)
    elif isinstance(value, float):
        raise TypeError("floating point prohibited")
    elif isinstance(value, int) and abs(value) > MAX_SAFE_JSON_INTEGER:
        raise ValueError("unsafe JSON integer must be a decimal string")


def jcs_bytes(value: Any) -> bytes:
    _assert_canonical_domain(value)
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def rng_root_state(*, meter_subseed: int, arm: str) -> dict[str, Any]:
    """Exact public state.  Arms share draws; arm behavior is not RNG state."""
    if arm not in {entry["arm"] for entry in CONTROL_ARMS}:
        raise ValueError("unregistered arm")
    return {
        "algorithm": RNG_ALGORITHM,
        "amendment_ordinal": 6,
        "domain": "ECTD-V6-PLANTED-CONTROL-20260813",
        "experiment_id": "EXP-ECTD-9e4248",
        "meter_subseed": meter_subseed,
        "schema": RNG_STATE_SCHEMA,
    }


def _block(state: Mapping[str, Any], *, label: str, draw_index: int, block_counter: int) -> int:
    block_state = dict(state)
    block_state.update({"block_counter": block_counter, "draw_index": draw_index, "label": label})
    return int.from_bytes(hashlib.shake_256(jcs_bytes(block_state)).digest(32), "big")


def randbelow(state: Mapping[str, Any], *, label: str, draw_index: int, n: int) -> dict[str, int]:
    """256-bit rejection-sampled randbelow; modulo bias is forbidden."""
    if not isinstance(n, int) or not 1 <= n <= (1 << 256):
        raise ValueError("n must satisfy 1 <= n <= 2^256")
    limit = (1 << 256) - ((1 << 256) % n)
    for block_counter in range(1 << 32):
        x = _block(state, label=label, draw_index=draw_index, block_counter=block_counter)
        if x < limit:
            return {"block_counter": block_counter, "value": x % n}
    raise RuntimeError("registered RESOURCE_LIMIT terminal required")


def fixed_calls(*, meter_subseed: int, arm: str, modulus: int = CONTROL_MODULUS) -> list[dict[str, int | str]]:
    """Generate only the frozen call schedule; no meter or predicate is evaluated."""
    if modulus != CONTROL_MODULUS:
        raise ValueError("control modulus must equal the frozen inherited field modulus")
    state = rng_root_state(meter_subseed=meter_subseed, arm=arm)
    calls: list[dict[str, int | str]] = []
    draw_index = 0
    for segment in CONTROL_CALL_SCHEDULE:
        for trial in range(int(segment["trials"])):
            for coordinate in range(int(segment["randbelow_calls_per_trial"])):
                sample = randbelow(state, label=str(segment["label"]), draw_index=draw_index, n=modulus)
                calls.append({
                    "block_counter": sample["block_counter"], "coordinate": coordinate,
                    "draw_index": draw_index, "label": str(segment["label"]),
                    "trial": trial, "value": sample["value"],
                })
                draw_index += 1
    return calls


def expected_call_count() -> int:
    return sum(int(s["trials"]) * int(s["randbelow_calls_per_trial"]) for s in CONTROL_CALL_SCHEDULE)


def validate_measured_control(record: Mapping[str, Any]) -> None:
    """Reject direct metric assignment; metrics must derive from raw counts."""
    if record.get("schema") != CONTROL_SCHEMA:
        raise ValueError("wrong control schema")
    if record.get("arm") not in {a["arm"] for a in CONTROL_ARMS}:
        raise ValueError("unregistered control arm")
    if record.get("call_count") != expected_call_count():
        raise ValueError("fixed call schedule mismatch")
    if record.get("factor_base_samples") != 24 or record.get("m3_trials") != 32 or record.get("m4_trials") != 256:
        raise ValueError("raw trial counts mismatch")
    for prefix in ("m3", "m4"):
        hits = record.get(f"{prefix}_hits")
        trials = record.get(f"{prefix}_trials")
        if not isinstance(hits, int) or not isinstance(trials, int) or not 0 <= hits <= trials:
            raise ValueError("invalid raw hit/trial count")
        exact = Fraction(hits, trials)
        expected = {"denominator": str(exact.denominator), "numerator": str(exact.numerator)}
        if record.get(f"{prefix}_density") != expected:
            raise ValueError("metric was not derived exactly from raw counts")
    if "expected_primary_vector" in record or "assigned_metric" in record:
        raise ValueError("direct expected-value assignment prohibited")


def terminal(code: str, details: Mapping[str, Any]) -> dict[str, Any]:
    if code not in TERMINAL_REGISTRY:
        raise ValueError("unregistered construction terminal")
    spec = TERMINAL_REGISTRY[code]
    required = tuple(spec["details"])
    if tuple(sorted(details)) != tuple(sorted(required)):
        raise ValueError("terminal details mismatch")
    return {
        "class": spec["class"], "code": code, "details": dict(details),
        "schema": CONSTRUCTION_TERMINAL_SCHEMA, "stage": spec["stage"],
    }


def validate_construction_witness(record: Mapping[str, Any]) -> None:
    """Static completeness check for a future construction witness."""
    if record.get("schema") != CONSTRUCTION_SCHEMA:
        raise ValueError("wrong construction schema")
    required = {
        "schema", "slot", "D_K", "q", "horizontal_ell", "arithmetic_witness_sha256", "source_manifest_sha256",
        "field_receipts", "cm_models", "twists", "order_certificates",
        "order_N_point_certificates", "division_polynomials", "cyclic_lines",
        "frobenius_stability", "canonical_kernels", "velu_codomain_checks",
        "dual_checks", "end_ring_receipts", "vertical_endpoints",
        "horizontal_endpoints", "control_measurements", "terminal",
    }
    if set(record) != required:
        raise ValueError("construction witness property set mismatch")
    terminal_record = record["terminal"]
    code = terminal_record.get("code")
    if code not in TERMINAL_REGISTRY:
        raise ValueError("unregistered construction terminal")
    registered = TERMINAL_REGISTRY[code]
    if terminal_record.get("schema") != CONSTRUCTION_TERMINAL_SCHEMA or terminal_record.get("class") != registered["class"] or terminal_record.get("stage") != registered["stage"] or set(terminal_record.get("details", {})) != set(registered["details"]):
        raise ValueError("construction terminal does not match registry")
    if code != "CONSTRUCTION_COMPLETE":
        return
    end_rings = record["end_ring_receipts"]
    if not isinstance(end_rings, list) or len(end_rings) < 4:
        raise ValueError("independent endpoint end-ring receipts missing")
    horizontal = record["horizontal_endpoints"]
    if not isinstance(horizontal, list) or len(horizontal) != 2:
        raise ValueError("exactly two horizontal endpoint receipts required")
    q = str(record["q"])
    if len({item.get("endpoint_key") for item in horizontal}) != 2:
        raise ValueError("horizontal endpoints must be independently keyed")
    if any(item.get("q") != q or item.get("whole_conductor") != q for item in horizontal):
        raise ValueError("each independently computed horizontal whole conductor must equal q")
    vertical = record["vertical_endpoints"]
    if len(vertical) != 2 or len({item.get("endpoint_key") for item in vertical}) != 2:
        raise ValueError("exactly two independently keyed vertical endpoints required")
    if {item.get("whole_conductor") for item in vertical} != {"1", q}:
        raise ValueError("vertical whole conductors must be exactly 1 and q")
    if len(record["cm_models"]) != 2 or len(record["twists"]) != 2 or len(record["order_certificates"]) != 2:
        raise ValueError("both CM twists and both exact order certificates required")
    expected_lines = int(record["q"]) + int(record["horizontal_ell"]) + 2
    if len(record["cyclic_lines"]) != expected_lines or len(record["frobenius_stability"]) != expected_lines or len(record["canonical_kernels"]) != expected_lines:
        raise ValueError("all q+1 and ell+1 cyclic lines require stability and canonical-kernel receipts")
    if len(record["division_polynomials"]) != 2 or len(record["velu_codomain_checks"]) != expected_lines or len(record["dual_checks"]) != expected_lines:
        raise ValueError("division-polynomial, Velu/codomain, or dual receipt totality failed")
    if len(record["control_measurements"]) != 3:
        raise ValueError("ordinary, planted, and planting-disabled control receipts required")
    if record.get("D_K") == -7:
        for item in vertical:
            if not item.get("two_adic_certified") or not item.get("q_adic_certified"):
                raise ValueError("D_K=-7 requires independent 2-adic and q-adic certification")


if __name__ == "__main__":
    raise SystemExit("design/static conformance module; curve execution is not authorized")
