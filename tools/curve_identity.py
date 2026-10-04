"""EC1 metadata identities. No arithmetic, runner imports, or network access.

Identical vendored reference in crypto, crypto-autoresearcher and cryptanalysis.
See docs/curve-identities.md. Hash equality is not mathematical verification.
"""
import hashlib
import json
import re


def canonical(value):
    def check(v):
        if v is None or type(v) in (str, int, bool):
            return
        if isinstance(v, list):
            for item in v:
                check(item)
            return
        if isinstance(v, dict) and all(isinstance(k, str) for k in v):
            for item in v.values():
                check(item)
            return
        raise ValueError("Identity records require JSON without floats.")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def curve_identity(field, curve, tag):
    """Preserve the existing EC1 hash input, including subgroup and generator.

    This is representation identity, not an isomorphism-class identifier.
    Require exact metadata; never infer it from a degree or friendly name.
    """
    if not isinstance(field, dict) or not isinstance(curve, dict):
        raise ValueError("Field and curve records must be objects.")
    required_field = ("characteristic", "degree", "representation", "element_encoding")
    required_curve = ("model", "subgroup_order", "cofactor", "generator", "target_group")
    if any(field.get(k) is None for k in required_field) or any(curve.get(k) is None for k in required_curve):
        raise ValueError("Exact field, curve, subgroup and generator metadata are required.")
    p, n = field["characteristic"], field["degree"]
    if type(p) is not int or p < 2 or type(n) is not int or n < 1:
        raise ValueError("Characteristic and degree must be positive integers.")
    if not isinstance(tag, str) or not re.fullmatch(r"[a-z][a-z0-9]*", tag):
        raise ValueError("Invalid readable curve tag.")
    if n > 1 and not any(field.get(k) is not None for k in ("modulus_exponents", "modulus", "defining_polynomial")):
        raise ValueError("Extension-field defining polynomial is required.")
    # Existing N/P namespaces; general extension fields must not masquerade as binary.
    prefix = f"N{n}" if p == 2 else f"P{p.bit_length()}" if n == 1 else f"Q{p}D{n}"
    clean = {k: v for k, v in curve.items() if k != "curve_id"}
    sha = digest({"field": field, "curve": clean})
    return {"curve_id": f"EC1{prefix}C{tag}h{sha[:12]}", "curve_sha256": sha,
            "curve_uid": f"urn:ec-record:1:sha256:{sha}", "field_sha256": digest(field)}


def inspect_manifest(manifest):
    """Check a recorded EC1 alias against its exact stored preimage."""
    field, curve = manifest["field"], manifest["curve"]
    alias = curve.get("curve_id", "")
    match = re.fullmatch(r"EC1(?:N[0-9]+|P[0-9]+|Q[0-9]+D[0-9]+)C([a-z][a-z0-9]*)h([a-f0-9]{12,64})", alias)
    if not match:
        raise ValueError("Missing or unsupported EC1 alias.")
    identity = curve_identity(field, curve, match[1])
    prefix = identity["curve_id"].rsplit("h", 1)[0]
    if alias.rsplit("h", 1)[0] != prefix or not identity["curve_sha256"].startswith(match[2]):
        raise ValueError("EC1 alias does not match the canonical curve record.")
    identity["curve_id"] = alias
    return identity


def candidate_identity(manifest):
    """Global metadata ID shared by IC, rho and other recorded method configs.

    Preserve legacy IC1/PS1 labels separately. Do not treat factor-base sizes
    or isogeny degrees as sufficient configuration identities.
    """
    inspect_manifest(manifest)
    sha = digest(manifest)
    return {'candidate_uid': f'urn:ec-candidate:1:sha256:{sha}', 'candidate_sha256': sha}
