"""Check legacy prefix transcripts without enumerating the Boolean cube.

Identities are checked in (Z/p)[b]/(b_i**2-b_i). Completeness refers to
projected models, not every auxiliary witness. Primality is not certified.
The optional EC wrapper retains the original encoding construction costs.
"""
from collections import Counter
from collections.abc import Mapping
from functools import lru_cache
import importlib.util
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=None)
def _load(relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location("_prefix_adapter_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _legacy():
    return _load("research/prime_sat_followup_20261029/encoding.py")


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(name + " must be a canonical integer >= " + str(minimum))
    return value


def _list(value, name):
    if type(value) is not list:
        raise ValueError(name + " must be a list")
    return value


def _fields(value, required, name):
    if not isinstance(value, Mapping) or any(key not in value for key in required):
        raise ValueError(name + " is missing required mapping fields")


def _polynomial(value, p, n, counts):
    if not isinstance(value, Mapping):
        raise ValueError("polynomial must be a mapping")
    result = {}
    for raw_mask, coefficient in value.items():
        counts["polynomial_entries"] += 1
        if type(raw_mask) is str:
            if re.fullmatch(r"0|[1-9][0-9]*", raw_mask) is None:
                raise ValueError("noncanonical monomial mask string")
            mask = int(raw_mask)
        else:
            mask = _integer(raw_mask, "monomial mask")
        if mask.bit_length() > n:
            raise ValueError("monomial mask outside ring")
        if mask in result:
            raise ValueError("aliased monomial mask")
        coefficient = _integer(coefficient, "coefficient", 1)
        if coefficient >= p:
            raise ValueError("coefficient outside canonical residue range")
        result[mask] = coefficient
    return result


def _block(prefix, depth):
    return [-(i + 1) if prefix >> i & 1 else i + 1 for i in range(depth)]


def _domain(domain, n, m, bound, counts):
    _list(domain, "domain_cnf")
    if bound is None:
        if domain:
            raise ValueError("full-cube domain requires empty CNF")
        return
    _integer(bound, "aux_bound")
    width = n - m
    capacity = 1 << width
    if bound > capacity:
        raise ValueError("aux_bound exceeds auxiliary capacity")
    excluded = set()
    for clause in domain:
        counts["clauses"] += 1
        _list(clause, "domain clause")
        if len(clause) != width:
            raise ValueError("domain clause must block one full auxiliary value")
        value = 0
        for bit, literal in enumerate(clause):
            counts["literals"] += 1
            if type(literal) is not int or abs(literal) != m + bit + 1:
                raise ValueError("domain clause has noncanonical auxiliary literals")
            if literal < 0:
                value |= 1 << bit
        if value < bound or value in excluded:
            raise ValueError("domain clause blocks a valid or repeated auxiliary value")
        excluded.add(value)
    if len(excluded) != capacity - bound:
        raise ValueError("domain CNF omits excluded auxiliary values")


def _restrict(poly, depth, prefix, p, counts):
    zero_bits = ((1 << depth) - 1) ^ prefix
    result = {}
    for mask, coefficient in poly.items():
        counts["term_visits"] += 1
        if not mask & zero_bits:
            residual_mask = mask & ~prefix
            result[residual_mask] = (result.get(residual_mask, 0) + coefficient) % p
            counts["coefficient_additions"] += 1
    return {mask: coefficient for mask, coefficient in result.items() if coefficient}


def _identity(generators, multipliers, p, counts):
    total = {}
    for generator, multiplier in zip(generators, multipliers):
        for left, coefficient in generator.items():
            for right, factor in multiplier.items():
                mask = left | right
                total[mask] = (total.get(mask, 0) + coefficient * factor) % p
                counts["coefficient_multiplications"] += 1
                counts["coefficient_additions"] += 1
    return {mask: coefficient for mask, coefficient in total.items() if coefficient} == {0: 1}


def _evaluate(poly, bits, p, counts):
    value = 0
    for mask, coefficient in poly.items():
        counts["term_visits"] += 1
        if mask & bits == mask:
            value = (value + coefficient) % p
            counts["coefficient_additions"] += 1
    return value


def verify_transcript(p, n, projected_bits, polynomials, domain_cnf, answer, aux_bound=None):
    """Validate all submitted records, then certify projected-set coverage.

The supported domain is the full cube or the exact legacy auxiliary-range
CNF. There is no expected-model oracle and no call to a search algorithm.
Legacy telemetry is ignored. Invalid records or false completeness raise
ValueError; a valid censored transcript is never promoted to complete.
"""
    _integer(p, "p", 2)
    _integer(n, "n")
    m = _integer(projected_bits, "projected_bits")
    if m > n:
        raise ValueError("projected_bits exceeds n")
    parsing, domain_cost, restriction, identity_cost, model_cost = (Counter() for _ in range(5))
    _list(polynomials, "polynomials")
    generators = [_polynomial(poly, p, n, parsing) for poly in polynomials]
    _domain(domain_cnf, n, m, aux_bound, domain_cost)
    _fields(answer, ("status", "models", "learned"), "answer")
    status = answer["status"]
    if type(status) is not str or status not in ("complete", "censored"):
        raise ValueError("unknown declared status")
    _list(answer["learned"], "learned")
    _list(answer["models"], "models")
    prefixes = []
    for item in answer["learned"]:
        parsing["learned_entries"] += 1
        _fields(item, ("depth", "prefix", "clause", "certificate"), "learned entry")
        depth = _integer(item["depth"], "depth")
        prefix = _integer(item["prefix"], "prefix")
        if depth > n or prefix.bit_length() > depth:
            raise ValueError("prefix outside ring")
        clause = _list(item["clause"], "prefix clause")
        if any(type(literal) is not int for literal in clause) or clause != _block(prefix, depth):
            raise ValueError("prefix clause does not match its cylinder")
        parsing["prefix_literals"] += len(clause)
        certificate = _list(item["certificate"], "certificate")
        if len(certificate) != len(generators):
            raise ValueError("wrong multiplier count")
        multipliers = [_polynomial(poly, p, n, parsing) for poly in certificate]
        residuals = [_restrict(poly, depth, prefix, p, restriction) for poly in generators]
        if not _identity(residuals, multipliers, p, identity_cost):
            raise ValueError("certificate identity is not one")
        prefixes.append((depth, prefix))
    projections = set()
    projection_mask = (1 << m) - 1
    for model in answer["models"]:
        parsing["models"] += 1
        _integer(model, "model")
        if model.bit_length() > n or (aux_bound is not None and model >> m >= aux_bound):
            raise ValueError("model outside declared domain")
        values = [_evaluate(poly, model, p, model_cost) for poly in generators]
        if any(values):
            raise ValueError("model is not a polynomial root")
        projection = model & projection_mask
        if projection in projections:
            raise ValueError("repeated model projection")
        projections.add(projection)
        prefixes.append((m, projection))
    cover = _load("research/prime_sat_costbridge_controls_20261029/prefix_cover.py").verify_cover(
        n, prefixes, projected_bits=m, aux_bound=aux_bound)
    if status == "complete" and not cover["covered"]:
        raise ValueError("claimed completeness leaves uncovered assignment " + str(cover["uncovered"]))
    return {
        "valid": True, "declared_status": status, "projected_models": sorted(projections),
        "cover_complete": cover["covered"],
        "projected_model_set_complete": status == "complete" and cover["covered"],
        "uncovered": cover["uncovered"], "prime_field_verified": False,
        "proof_scope": "Boolean quotient identities modulo p and projected-model coverage",
        "costs": {"parsing": dict(parsing), "domain_validation": dict(domain_cost),
                  "restriction": dict(restriction), "identity_check": dict(identity_cost),
                  "model_evaluation": dict(model_cost),
                  "coverage": {"prefixes": len(prefixes),
                               "prefix_depth_sum": sum(depth for depth, _ in prefixes),
                               "trie_nodes": cover["trie_nodes"]}},
    }


def verify_encoding_search(cell, arm, answer):
    """Check unchanged encoding.solve output and reconstruct its EC witnesses.

Primality is an external premise. Frozen build retains its truth-table and
range-CNF construction; its counters are separate from transcript checking.
"""
    _fields(cell, ("p", "s", "a", "b", "target"), "cell")
    p = _integer(cell["p"], "p", 4)
    s = _integer(cell["s"], "s", 1)
    a, b = (_integer(cell[key], key) for key in ("a", "b"))
    target = cell["target"]
    if type(target) not in (list, tuple) or len(target) != 2:
        raise ValueError("target must be an affine coordinate pair")
    r, t = (_integer(value, "target coordinate") for value in target)
    if any(value >= p for value in (a, b, r, t)) or t == 0:
        raise ValueError("noncanonical curve or zero target ordinate")
    if s >= p.bit_length() or (4 * a**3 + 27 * b*b) % p == 0:
        raise ValueError("nonsingular curve and distinct digit domain required")
    if (t*t - r**3 - a*r - b) % p:
        raise ValueError("target is off curve")
    if type(arm) is not str or arm not in ("quartic", "membership", "quadratic", "quadratic_aa"):
        raise ValueError("unknown encoding arm")
    legacy = _legacy()
    ring, polynomials, domain = legacy.build(cell, arm)
    construction = dict(ring.counts)
    bound = p if arm in ("quadratic", "quadratic_aa") else None
    result = verify_transcript(p, ring.n, 2*s, polynomials, domain, answer, aux_bound=bound)
    digit_mask = (1 << s) - 1
    pairs = sorted((model & digit_mask, model >> s) for model in result["projected_models"])
    try:
        witnesses, reconstruction = legacy.reconstruct(cell, pairs)
    except (AssertionError, ZeroDivisionError) as error:
        raise ValueError("rational witness reconstruction failed") from error
    result.update(coordinate_pairs=[list(pair) for pair in pairs], witnesses=witnesses,
                  proof_scope=result["proof_scope"] + "; rational EC witnesses conditional on prime p")
    result["costs"]["construction"] = construction
    result["costs"]["witness_reconstruction_and_check"] = reconstruction
    return result
