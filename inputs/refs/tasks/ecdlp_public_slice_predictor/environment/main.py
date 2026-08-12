import argparse
import hashlib
import importlib.util
import json
import math
import os
import secrets
from pathlib import Path
from typing import Any


APP_DIR = Path(os.environ.get("APP_DIR", "/app"))
if not APP_DIR.exists():
    APP_DIR = Path(__file__).resolve().parent

DATA_PATH = Path(os.environ.get("LMFDB_DATA", APP_DIR / "lmfdb_curves.json"))
CAMPAIGN_STATE_DIR = Path(os.environ.get("ECDLP_CAMPAIGN_STATE", APP_DIR / "ecdlp_campaign_state"))
RESEARCH_DIR = Path(os.environ.get("ECDLP_RESEARCH_DIR", APP_DIR / "ecdlp_research"))
PRIME_LIMIT = int(os.environ.get("PRIME_LIMIT", "12000"))
TOP_K = int(os.environ.get("TOP_K", "5"))
MAX_CANDIDATES = 500
MAX_RELATIONS = 96
GENERIC_METHOD_MARKERS = ("bsgs", "baby", "giant", "pollard", "rho", "brute", "exhaustive", "linear_scan")
LOW_SIGNAL_NOTE_MARKERS = ("placeholder", "dummy", "lorem", "todo:", "todo ")
POINT_AT_INFINITY = None


def load_solver():
    spec = importlib.util.spec_from_file_location("solve", APP_DIR / "solve.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_records():
    with DATA_PATH.open() as f:
        data = json.load(f)
    records = data["records"] if isinstance(data, dict) else data
    normalized = []
    seen = set()
    for row in records:
        label = row.get("label") or row.get("lmfdb_label")
        ainvs = row.get("ainvs")
        if not isinstance(label, str) or not isinstance(ainvs, list) or len(ainvs) != 5:
            raise ValueError(f"bad LMFDB record: {row!r}")
        if label in seen:
            raise ValueError(f"duplicate LMFDB label in snapshot: {label}")
        seen.add(label)
        targets = []
        for target in row.get("precomputed_targets", []):
            if not isinstance(target, dict):
                raise ValueError(f"bad precomputed target for {label}: {target!r}")
            base = target.get("base")
            if not isinstance(base, list) or len(base) != 2:
                raise ValueError(f"bad precomputed target base for {label}: {target!r}")
            targets.append(
                {
                    "p": int(target["p"]),
                    "order": int(target["order"]),
                    "twist_order": int(target["twist_order"]),
                    "base": [int(base[0]), int(base[1])],
                }
            )
        normalized.append({"label": label, "ainvs": [int(x) for x in ainvs], "precomputed_targets": targets})
    return normalized


def read_json_maybe(path):
    try:
        if path.is_file():
            with path.open() as f:
                return json.load(f)
    except Exception:
        return None
    return None


def research_context():
    manifest_path = RESEARCH_DIR / "manifest.json"
    manifest = read_json_maybe(manifest_path) or {}
    documents = manifest.get("documents") if isinstance(manifest, dict) else []
    if not isinstance(documents, list):
        documents = []
    usable_docs = [row for row in documents if isinstance(row, dict)]
    priority_tags = {"ecdlp", "index-calculus", "summation-polynomials", "grobner", "pollard-rho", "isogenies"}
    priority_sources = []
    for row in usable_docs:
        tags = set(row.get("topic_tags") or [])
        if tags & priority_tags:
            priority_sources.append(
                {
                    "source_id": row.get("source_id"),
                    "title": row.get("title"),
                    "topic_tags": sorted(tags),
                    "pdf_path": row.get("runtime_pdf_path"),
                    "text_path": row.get("runtime_text_path"),
                }
            )
        if len(priority_sources) >= 12:
            break

    return {
        "available": manifest_path.is_file(),
        "root": str(RESEARCH_DIR),
        "manifest_path": str(manifest_path),
        "literature_map_path": str(RESEARCH_DIR / "literature_map.md"),
        "pdf_dir": str(RESEARCH_DIR / "papers"),
        "text_dir": str(RESEARCH_DIR / "text"),
        "document_count": int(manifest.get("document_count") or len(usable_docs)) if isinstance(manifest, dict) else 0,
        "unique_pdf_count": int(manifest.get("unique_pdf_count") or 0) if isinstance(manifest, dict) else 0,
        "text_ok_count": int(manifest.get("text_ok_count") or 0) if isinstance(manifest, dict) else 0,
        "pdf_mount_expected": str(RESEARCH_DIR / "papers"),
        "source_ids": [row.get("source_id") for row in usable_docs if row.get("source_id")][:80],
        "priority_sources": priority_sources,
        "usage_hint": (
            "Search /app/ecdlp_research/text and cite source_id values in /app/research artifacts. "
            "Original PDFs are mounted read-only at /app/ecdlp_research/papers by the campaign runners."
        ),
    }


def load_jsonl_maybe(path):
    rows = []
    try:
        if not path.is_file():
            return rows
        for line in path.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        return []
    return rows


def target_key(label, p):
    return f"{label}@{int(p)}"


def campaign_state_context():
    state_dir = CAMPAIGN_STATE_DIR
    context = {
        "known_success_targets": set(),
        "global_best_metric": 0.0,
        "global_best_target": None,
        "scalar_free_successes": 0,
        "has_state": False,
    }
    if not state_dir.exists():
        return context

    context["has_state"] = True
    plateau = read_json_maybe(state_dir / "plateau_report.json") or {}
    leaderboard = read_json_maybe(state_dir / "leaderboard.json") or {}
    runs = load_jsonl_maybe(state_dir / "runs.jsonl")

    success_targets = plateau.get("success_targets")
    if isinstance(success_targets, dict):
        context["known_success_targets"].update(str(key) for key in success_targets)

    best_by_label = leaderboard.get("best_by_label")
    if isinstance(best_by_label, dict):
        for row in best_by_label.values():
            label = row.get("best_label")
            prime = row.get("best_p")
            if label and prime is not None:
                context["known_success_targets"].add(target_key(label, prime))

    for row in runs:
        label = row.get("best_label")
        prime = row.get("best_p")
        if row.get("correctness") and label and prime is not None:
            context["known_success_targets"].add(target_key(label, prime))

    global_best = leaderboard.get("global_best") or {}
    context["global_best_metric"] = float(global_best.get("metric") or plateau.get("global_best_metric") or 0.0)
    context["global_best_target"] = target_key(global_best["best_label"], global_best["best_p"]) if global_best.get("best_label") and global_best.get("best_p") is not None else plateau.get("global_best_target")
    context["scalar_free_successes"] = int(plateau.get("scalar_free_successes") or 0)
    return context


def is_prime(n):
    if not isinstance(n, int) or n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def discriminant(ainvs):
    a1, a2, a3, a4, a6 = ainvs
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 * b4 * b4 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def inv_mod(a, p):
    return pow(a % p, -1, p)


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    v = pow(a, (p - 1) // 2, p)
    return 1 if v == 1 else -1


def count_points(ainvs, p):
    a1, a2, a3, a4, a6 = [x % p for x in ainvs]
    total = 1
    for x in range(p):
        rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
        linear = (a1 * x + a3) % p
        dy = (linear * linear + 4 * rhs) % p
        total += 1 + legendre(dy, p)
    return total


def factor(n):
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exponent = 0
            while n % d == 0:
                n //= d
                exponent += 1
            out.append((d, exponent))
        d += 1 if d == 2 else 2
    if n > 1:
        out.append((n, 1))
    return out


def largest_prime_factor(n):
    return max((prime for prime, _ in factor(n)), default=1)


def isogeny_class(label):
    return label.rstrip("0123456789")


def embedding_degree(p, r, limit=24):
    if r <= 2 or math.gcd(p, r) != 1:
        return None
    value = 1
    for k in range(1, limit + 1):
        value = (value * p) % r
        if value == 1:
            return k
    return None


def neg_point(point, ainvs, p):
    if point is POINT_AT_INFINITY:
        return POINT_AT_INFINITY
    a1, _, a3, _, _ = [x % p for x in ainvs]
    x, y = point
    return (x, (-y - a1 * x - a3) % p)


def add_points(left, right, ainvs, p):
    if left is POINT_AT_INFINITY:
        return right
    if right is POINT_AT_INFINITY:
        return left

    a1, a2, a3, a4, _ = [x % p for x in ainvs]
    x1, y1 = left
    x2, y2 = right

    if x1 == x2 and (y1 + y2 + a1 * x1 + a3) % p == 0:
        return POINT_AT_INFINITY

    if left == right:
        denom = (2 * y1 + a1 * x1 + a3) % p
        if denom == 0:
            return POINT_AT_INFINITY
        slope = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) * inv_mod(denom, p)
    else:
        slope = (y2 - y1) * inv_mod(x2 - x1, p)
    slope %= p
    intercept = (y1 - slope * x1) % p

    x3 = (slope * slope + a1 * slope - a2 - x1 - x2) % p
    y3 = (-(slope + a1) * x3 - intercept - a3) % p
    return (x3, y3)


def mul_point(k, point, ainvs, p):
    result = POINT_AT_INFINITY
    addend = point
    while k > 0:
        if k & 1:
            result = add_points(result, addend, ainvs, p)
        addend = add_points(addend, addend, ainvs, p)
        k >>= 1
    return result


def point_to_json(point):
    if point is POINT_AT_INFINITY:
        return None
    return [int(point[0]), int(point[1])]


def point_from_json(value):
    if value is None:
        return POINT_AT_INFINITY
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise TypeError(f"point must be [x, y] or None, got {value!r}")
    return (int(value[0]), int(value[1]))


def is_on_curve(point, ainvs, p):
    if point is POINT_AT_INFINITY:
        return True
    a1, a2, a3, a4, a6 = [x % p for x in ainvs]
    x, y = point
    lhs = (y * y + a1 * x * y + a3 * y) % p
    rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
    return lhs == rhs


def sqrt_table(p):
    table = [[] for _ in range(p)]
    for y in range(p):
        table[(y * y) % p].append(y)
    return table


def iter_curve_points(ainvs, p):
    a1, a2, a3, a4, a6 = [x % p for x in ainvs]
    roots_by_residue = sqrt_table(p)
    inv2 = inv_mod(2, p)
    for x in range(p):
        rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
        linear = (a1 * x + a3) % p
        dy = (linear * linear + 4 * rhs) % p
        for root in roots_by_residue[dy]:
            yield (x, ((-linear + root) * inv2) % p)


def point_order(point, ainvs, p, group_order, group_factors=None):
    if point is POINT_AT_INFINITY:
        return 1
    order = group_order
    group_factors = group_factors or factor(group_order)
    for prime, _ in group_factors:
        while order % prime == 0:
            candidate = order // prime
            if mul_point(candidate, point, ainvs, p) is POINT_AT_INFINITY:
                order = candidate
            else:
                break
    return order


def find_attack_point(ainvs, p, group_order):
    group_factors = factor(group_order)
    best = None
    best_order = 1
    checked = 0
    for point in iter_curve_points(ainvs, p):
        checked += 1
        order = point_order(point, ainvs, p, group_order, group_factors)
        if (largest_prime_factor(order), order) > (largest_prime_factor(best_order), best_order):
            best = point
            best_order = order
        if order == group_order or (checked >= 256 and best_order > 64):
            break
    if best is None:
        raise ValueError("could not find a nontrivial curve point")
    return best, best_order


def sqrt_mod_prime(a, p):
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)

    q = p - 1
    s = 0
    while q % 2 == 0:
        s += 1
        q //= 2

    z = 2
    while legendre(z, p) != -1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q + 1) // 2, p)
    while t != 1:
        i = 1
        value = (t * t) % p
        while value != 1:
            value = (value * value) % p
            i += 1
            if i == m:
                return None
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def point_from_x(ainvs, p, x):
    a1, a2, a3, a4, a6 = [value % p for value in ainvs]
    rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
    linear = (a1 * x + a3) % p
    dy = (linear * linear + 4 * rhs) % p
    root = sqrt_mod_prime(dy, p)
    if root is None:
        return None
    y = ((-linear + root) * inv_mod(2, p)) % p
    return (x, y)


def hash_factor_base(ainvs, p, base_order, seed, limit=48):
    factor_base = []
    seen = set()
    counter = 0
    while len(factor_base) < limit and counter < limit * 200:
        digest = hashlib.sha256(f"{seed}:fb:{counter}".encode()).digest()
        x = int.from_bytes(digest, "big") % p
        point = point_from_x(ainvs, p, x)
        counter += 1
        if point is None or point in seen:
            continue
        if mul_point(base_order, point, ainvs, p) is not POINT_AT_INFINITY:
            continue
        seen.add(point)
        factor_base.append(point)
    if len(factor_base) < min(8, limit):
        raise ValueError(f"could not build hashed factor base for p={p}")
    return factor_base


def build_factor_base(ainvs, p, base_order, limit=48, seed=None):
    if p > 200_000:
        if seed is None:
            raise ValueError("large-prime factor-base generation requires a seed")
        return hash_factor_base(ainvs, p, base_order, seed, limit)

    factor_base = []
    seen = set()
    for point in iter_curve_points(ainvs, p):
        if point in seen:
            continue
        if mul_point(base_order, point, ainvs, p) is not POINT_AT_INFINITY:
            continue
        seen.add(point)
        factor_base.append(point)
        if len(factor_base) >= limit:
            break
    return factor_base


def precomputed_target(record, p):
    for target in record.get("precomputed_targets", []):
        if int(target["p"]) == p:
            return target
    return None


def score_reduction_invariants(record, p, order, twist_order, base, base_order, precomputed=False):
    if precomputed:
        emb = embedding_degree(p, base_order)
        flags = ["prime_order_index_calculus_target"]
        score = 35.0 + math.log2(order) / 2.0
        if order.bit_length() >= 80:
            flags.append("large_precomputed_prime_order_target")
            score += 240.0 + min(120.0, math.log2(order))
        if emb is not None and emb <= 6 and base_order >= 17:
            flags.append(f"mov_embedding_degree_{emb}")
            score += 20.0 + 2.0 * (7 - emb)
        score += min(10.0, math.log2(p) / 2)
        return {
            "label": record["label"],
            "isogeny_class": isogeny_class(record["label"]),
            "p": p,
            "order": order,
            "twist_order": twist_order,
            "order_lpf": order,
            "twist_lpf": None,
            "base": base,
            "base_order": base_order,
            "base_lpf": base_order,
            "embedding_degree": emb,
            "flags": flags,
            "score": round(score, 6),
            "precomputed_target": True,
        }

    order_lpf = largest_prime_factor(order)
    twist_lpf = largest_prime_factor(twist_order)
    base_lpf = largest_prime_factor(base_order)
    emb = embedding_degree(p, base_lpf)

    flags = []
    score = 0.0
    if is_prime(order) and base_order == order:
        if order <= 257:
            flags.append("toy_prime_order_ecdlp")
            score += 12.0 + math.log2(order) / 2.0
        elif order == p:
            flags.append("prime_order_anomalous_baseline")
            score += 55.0 + math.log2(order) / 3.0
        else:
            flags.append("prime_order_index_calculus_target")
            score += 35.0 + math.log2(order) / 2.0
    if base_order > 64 and base_lpf <= 43:
        flags.append("pohlig_hellman_smooth_group")
        score += 45.0 + math.log2(base_order) - 2.0 * math.log2(max(base_lpf, 2))
    if order == p:
        flags.append("smart_anomalous_curve")
        score += 20.0
    if emb is not None and emb <= 6 and base_lpf >= 17:
        flags.append(f"mov_embedding_degree_{emb}")
        score += 20.0 + 2.0 * (7 - emb)
    if twist_order > 64 and twist_lpf <= 43:
        flags.append("invalid_curve_smooth_twist")
        score += 12.0 + math.log2(twist_order) - 2.0 * math.log2(max(twist_lpf, 2))
    if flags:
        score += min(10.0, math.log2(p) / 2)

    return {
        "label": record["label"],
        "isogeny_class": isogeny_class(record["label"]),
        "p": p,
        "order": order,
        "twist_order": twist_order,
        "order_lpf": order_lpf,
        "twist_lpf": twist_lpf,
        "base": base,
        "base_order": base_order,
        "base_lpf": base_lpf,
        "embedding_degree": emb,
        "flags": flags,
        "score": round(score, 6),
        "precomputed_target": precomputed,
    }


def reduction_invariants(record, p):
    ainvs = record["ainvs"]
    if discriminant(ainvs) % p == 0:
        raise ValueError(f"{record['label']} has singular reduction at p={p}")

    target = precomputed_target(record, p)
    if target is not None:
        order = int(target["order"])
        twist_order = int(target["twist_order"])
        base = point_from_json(target["base"])
        if not is_on_curve(base, ainvs, p):
            raise ValueError(f"precomputed base is not on {record['label']} mod {p}")
        if mul_point(order, base, ainvs, p) is not POINT_AT_INFINITY:
            raise ValueError(f"precomputed base does not have claimed order on {record['label']} mod {p}")
        return score_reduction_invariants(record, p, order, twist_order, base, order, precomputed=True)

    order = count_points(ainvs, p)
    twist_order = 2 * p + 2 - order
    base, base_order = find_attack_point(ainvs, p, order)
    return score_reduction_invariants(record, p, order, twist_order, base, base_order)


def make_challenge(inv, ainvs, factor_base_limit=None):
    secret = 1 + secrets.randbelow(inv["base_order"] - 1)
    public = mul_point(secret, inv["base"], ainvs, inv["p"])
    factor_seed = f"{inv['label']}:{inv['p']}:{inv['base_order']}"
    factor_limit = int(factor_base_limit) if factor_base_limit is not None else 48
    if factor_limit <= 0:
        raise ValueError(f"factor_base_limit must be positive, got {factor_limit}")
    factor_base = build_factor_base(ainvs, inv["p"], inv["base_order"], limit=factor_limit, seed=factor_seed)
    return {
        "label": inv["label"],
        "isogeny_class": inv["isogeny_class"],
        "p": inv["p"],
        "ainvs": ainvs,
        "group_order": inv["order"],
        "base": point_to_json(inv["base"]),
        "base_order": inv["base_order"],
        "public": point_to_json(public),
        "factor_base": [point_to_json(point) for point in factor_base],
        "generic_rho_steps": math.ceil(math.sqrt(math.pi * inv["base_order"] / 2.0)),
        "breakthrough_goal": "find relation-collection structure that beats generic sqrt(n) Pollard rho on prime-order ECDLP",
        "precomputed_target": bool(inv.get("precomputed_target")),
        "certificate_requirements": {
            "direct_factor_log_rows": "no_full_credit",
            "min_mixed_wide_relations": 12,
            "min_mixed_relation_rank": 8,
            "min_distinct_factor_base_indices": 6,
            "work_estimate": "must_claim_less_than_generic_rho",
            "scalar_field": "optional; strongest large-target credit comes from mixed relations without returning k",
        },
        "weaknesses": inv["flags"],
        "research_targets": [
            "ecdlp",
            "prime_order_index_calculus_target",
            "semaev_summation_polynomials",
            "grobner_basis_modeling",
            "isogeny_class_transfer",
            "pohlig_hellman_when_smooth",
            "mov_when_embedding_degree_is_low",
        ],
        "research_context": research_context(),
    }, secret


def relation_terms(relation, challenge, ainvs, p):
    if not isinstance(relation, dict):
        return None
    factor_base = [point_from_json(point) for point in challenge.get("factor_base", [])]
    factor_index = {point: index for index, point in enumerate(factor_base)}
    if not factor_base or len(factor_index) != len(factor_base):
        return None

    if "indices" in relation:
        indices = relation["indices"]
        if not isinstance(indices, list) or len(indices) == 0 or len(indices) > 6:
            return None
        terms = []
        for raw_index in indices:
            index = int(raw_index)
            if not 0 <= index < len(factor_base):
                return None
            terms.append(index)
        return terms
    elif "points" in relation:
        points = relation["points"]
        if not isinstance(points, list) or len(points) == 0 or len(points) > 6:
            return None
        terms = []
        for raw_point in points:
            point = point_from_json(raw_point)
            if point not in factor_index or not is_on_curve(point, ainvs, p):
                return None
            terms.append(factor_index[point])
        return terms

    return None


def verify_relation(relation, challenge, ainvs, p, base, public):
    terms = relation_terms(relation, challenge, ainvs, p)
    if terms is None:
        return False

    factor_base = [point_from_json(point) for point in challenge.get("factor_base", [])]
    a = int(relation.get("a", 0))
    b = int(relation.get("b", 0))
    lhs = add_points(mul_point(a, base, ainvs, p), mul_point(b, public, ainvs, p), ainvs, p)

    rhs = POINT_AT_INFINITY
    for index in terms:
        rhs = add_points(rhs, factor_base[index], ainvs, p)

    return lhs == rhs


def relation_linear_form(relation, terms, challenge, modulus):
    coeffs = [0] * (1 + len(challenge.get("factor_base", [])))
    coeffs[0] = int(relation.get("b", 0)) % modulus
    for index in terms:
        coeffs[1 + index] = (coeffs[1 + index] - 1) % modulus
    rhs = (-int(relation.get("a", 0))) % modulus
    return tuple(coeffs), rhs


def rref_mod(rows, modulus):
    if not rows:
        return [], [], True
    rows = [[value % modulus for value in row] for row in rows]
    nvars = len(rows[0]) - 1
    pivot_cols = []
    pivot_row = 0

    for col in range(nvars):
        pivot = None
        for row in range(pivot_row, len(rows)):
            if rows[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue

        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inv = inv_mod(rows[pivot_row][col], modulus)
        rows[pivot_row] = [(value * inv) % modulus for value in rows[pivot_row]]

        for row in range(len(rows)):
            if row == pivot_row:
                continue
            scale = rows[row][col] % modulus
            if scale:
                rows[row] = [
                    (rows[row][i] - scale * rows[pivot_row][i]) % modulus
                    for i in range(nvars + 1)
                ]

        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    for row in rows:
        if all(row[col] % modulus == 0 for col in range(nvars)) and row[-1] % modulus:
            return rows, pivot_cols, False
    return rows, pivot_cols, True


def derive_secret_from_relations(forms, modulus):
    if not forms or not is_prime(modulus):
        return None, False, 0

    rows = [list(coeffs) + [rhs] for coeffs, rhs, _terms in forms]
    reduced, pivot_cols, consistent = rref_mod(rows, modulus)
    if not consistent or 0 not in pivot_cols:
        return None, False, len(pivot_cols)

    nvars = len(rows[0]) - 1
    free_cols = set(range(nvars)) - set(pivot_cols)
    row = pivot_cols.index(0)
    if any(reduced[row][col] % modulus for col in free_cols):
        return None, False, len(pivot_cols)
    return reduced[row][-1] % modulus, True, len(pivot_cols)


def analyze_relations(answer, challenge, ainvs, p, base, public, base_order):
    empty = {
        "relation_count": 0,
        "q_relation_count": 0,
        "wide_relation_count": 0,
        "direct_factor_log_count": 0,
        "mixed_wide_relation_count": 0,
        "mixed_wide_q_coeff_count": 0,
        "mixed_wide_index_count": 0,
        "relation_rank": 0,
        "relation_secret": None,
        "relation_proves_k": False,
        "mixed_wide_relation_rank": 0,
        "mixed_wide_relation_secret": None,
        "mixed_wide_relation_proves_k": False,
    }
    if not isinstance(answer, dict):
        return empty
    relations = answer.get("relations") or []
    if not isinstance(relations, list):
        return empty

    seen = set()
    forms = []
    mixed_wide_forms = []
    q_relation_count = 0
    wide_relation_count = 0
    direct_factor_log_count = 0
    mixed_wide_indices = set()
    mixed_wide_q_coeffs = set()
    for relation in relations[:MAX_RELATIONS]:
        terms = relation_terms(relation, challenge, ainvs, p)
        if terms is None:
            continue
        if not verify_relation(relation, challenge, ainvs, p, base, public):
            continue
        coeffs, rhs = relation_linear_form(relation, terms, challenge, base_order)
        key = (coeffs, rhs)
        if key in seen:
            continue
        seen.add(key)
        forms.append((coeffs, rhs, terms))
        b_coeff = int(relation.get("b", 0)) % base_order
        unique_terms = set(terms)
        if b_coeff:
            q_relation_count += 1
        if len(unique_terms) >= 3:
            wide_relation_count += 1
        if not b_coeff and len(terms) == 1:
            direct_factor_log_count += 1
        if b_coeff and len(unique_terms) >= 3:
            mixed_wide_forms.append((coeffs, rhs, terms))
            mixed_wide_indices.update(unique_terms)
            mixed_wide_q_coeffs.add(b_coeff)

    relation_secret, relation_proves_k, relation_rank = derive_secret_from_relations(forms, base_order)
    mixed_secret, mixed_proves_k, mixed_rank = derive_secret_from_relations(mixed_wide_forms, base_order)
    return {
        "relation_count": len(forms),
        "q_relation_count": q_relation_count,
        "wide_relation_count": wide_relation_count,
        "direct_factor_log_count": direct_factor_log_count,
        "mixed_wide_relation_count": len(mixed_wide_forms),
        "mixed_wide_q_coeff_count": len(mixed_wide_q_coeffs),
        "mixed_wide_index_count": len(mixed_wide_indices),
        "relation_rank": relation_rank,
        "relation_secret": relation_secret,
        "relation_proves_k": relation_proves_k,
        "mixed_wide_relation_rank": mixed_rank,
        "mixed_wide_relation_secret": mixed_secret,
        "mixed_wide_relation_proves_k": mixed_proves_k,
    }


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def analyze_work_claim(answer, challenge):
    rho_steps = int(challenge.get("generic_rho_steps", 0))
    empty = {
        "work_claim_present": False,
        "work_method": "",
        "work_beats_rho": False,
        "work_generic_like": True,
        "claimed_generic_dlp_steps": None,
        "claimed_group_ops": None,
        "claimed_relation_trials": None,
    }
    if not isinstance(answer, dict):
        return empty

    raw = answer.get("work_estimate") or answer.get("work") or answer.get("cost_estimate")
    if not isinstance(raw, dict):
        return empty

    method = str(raw.get("method") or raw.get("algorithm") or "").lower()
    generic_steps = safe_int(raw.get("generic_dlp_steps"), 0)
    group_ops = safe_int(raw.get("group_ops"), 0)
    relation_trials = safe_int(raw.get("relation_trials"), 0)
    declared_generic = bool(raw.get("uses_generic_dlp") or raw.get("uses_bsgs") or raw.get("uses_pollard_rho"))
    generic_like = declared_generic or any(marker in method for marker in GENERIC_METHOD_MARKERS)
    if rho_steps:
        generic_like = generic_like or generic_steps >= max(1, rho_steps // 2)
        if group_ops:
            generic_like = generic_like or group_ops >= rho_steps

    claimed_work = max(generic_steps, group_ops, relation_trials)
    claimed_beats = bool(raw.get("beats_rho", False))
    work_beats_rho = bool(
        claimed_beats
        and not generic_like
        and rho_steps
        and claimed_work > 0
        and claimed_work < rho_steps
    )

    return {
        "work_claim_present": True,
        "work_method": method,
        "work_beats_rho": work_beats_rho,
        "work_generic_like": generic_like,
        "claimed_generic_dlp_steps": generic_steps,
        "claimed_group_ops": group_ops,
        "claimed_relation_trials": relation_trials,
    }


def empty_artifact_meta():
    return {
        "algebra_artifact_bundle_present": False,
        "artifact_bundle_present": False,
        "artifact_relation_count": 0,
        "artifact_mixed_wide_relation_count": 0,
        "artifact_polynomial_present": False,
        "artifact_grobner_present": False,
        "artifact_cost_present": False,
        "artifact_cost_beats_rho": False,
        "artifact_error": "",
        "research_notebook_present": False,
        "research_hypothesis_present": False,
        "research_result_present": False,
        "research_next_hypothesis_present": False,
        "research_novelty_claim_present": False,
        "research_notebook_error": "",
    }


def artifact_path(raw_path):
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    path = Path(raw_path)
    if not path.is_absolute():
        path = APP_DIR / path
    try:
        resolved = path.resolve()
        app_root = APP_DIR.resolve()
    except OSError:
        return None
    if resolved == app_root or app_root not in resolved.parents:
        return None
    return resolved


def read_artifact_text(raw_path, max_bytes=256_000):
    path = artifact_path(raw_path)
    if path is None or not path.is_file():
        return None
    if path.stat().st_size > max_bytes:
        return None
    return path.read_text(errors="replace")


def first_existing_artifact_text(raw_paths, max_bytes=256_000):
    for raw_path in raw_paths:
        text = read_artifact_text(raw_path, max_bytes=max_bytes)
        if text is not None:
            return text
    return None


def parse_relation_artifact(text):
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed = parsed.get("relations", [])
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                return []
            rows.append(row)
        return rows


def parse_cost_artifact(text):
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def parse_json_artifact(text):
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def useful_research_note(text, required_terms, evidence_terms):
    if not text:
        return False
    lower = text.lower()
    if len(text.strip()) < 120:
        return False
    if any(marker in lower for marker in LOW_SIGNAL_NOTE_MARKERS):
        return False
    return any(term in lower for term in required_terms) and any(term in lower for term in evidence_terms)


def analyze_artifacts(answer, challenge, ainvs, p, base, public, base_order):
    meta = empty_artifact_meta()
    if not isinstance(answer, dict):
        return meta
    artifacts = answer.get("artifacts")
    if not isinstance(artifacts, dict):
        return meta

    relation_file = artifacts.get("relation_file") or artifacts.get("relations")
    polynomial_file = artifacts.get("polynomial_system") or artifacts.get("polynomials")
    grobner_file = artifacts.get("grobner_log") or artifacts.get("groebner_log")
    cost_file = artifacts.get("cost_accounting") or artifacts.get("cost")
    hypothesis_file = artifacts.get("hypothesis") or artifacts.get("hypothesis_file")
    result_file = artifacts.get("experiment_result") or artifacts.get("result_file")
    next_file = artifacts.get("next_hypothesis") or artifacts.get("next_hypothesis_file")
    novelty_file = artifacts.get("novelty_claim") or artifacts.get("novelty_file")

    relation_text = read_artifact_text(relation_file)
    polynomial_text = read_artifact_text(polynomial_file)
    grobner_text = read_artifact_text(grobner_file)
    cost_text = read_artifact_text(cost_file)
    relation_path_obj = artifact_path(relation_file)
    artifact_dirs = []
    if relation_path_obj is not None:
        artifact_dirs.append(relation_path_obj.parent)
    artifact_dirs.append(APP_DIR / "research")
    target_dir = APP_DIR / "research" / f"{str(challenge.get('label', 'curve')).replace('/', '_')}_{int(challenge.get('p', 0))}"
    artifact_dirs.append(target_dir)

    hypothesis_text = first_existing_artifact_text(
        [hypothesis_file, *[str(path / "hypothesis.md") for path in artifact_dirs]]
    )
    result_text = first_existing_artifact_text(
        [result_file, *[str(path / "experiment_result.md") for path in artifact_dirs]]
    )
    next_text = first_existing_artifact_text(
        [next_file, *[str(path / "next_hypothesis.md") for path in artifact_dirs]]
    )
    novelty_text = first_existing_artifact_text(
        [novelty_file, *[str(path / "novelty.json") for path in artifact_dirs]]
    )

    if relation_text is None:
        meta["artifact_error"] = "missing relation artifact"
        return meta

    seen = set()
    relation_count = 0
    mixed_count = 0
    for relation in parse_relation_artifact(relation_text)[:MAX_RELATIONS]:
        terms = relation_terms(relation, challenge, ainvs, p)
        if terms is None or not verify_relation(relation, challenge, ainvs, p, base, public):
            continue
        coeffs, rhs = relation_linear_form(relation, terms, challenge, base_order)
        key = (coeffs, rhs)
        if key in seen:
            continue
        seen.add(key)
        relation_count += 1
        if int(relation.get("b", 0)) % base_order and len(set(terms)) >= 3:
            mixed_count += 1

    poly_lower = (polynomial_text or "").lower()
    grobner_lower = (grobner_text or "").lower()
    polynomial_present = bool(
        polynomial_text
        and len(polynomial_text) >= 200
        and ("semaev" in poly_lower or "summation" in poly_lower)
        and ("factor" in poly_lower or "base" in poly_lower)
        and ("f3" in poly_lower or "polynomial" in poly_lower or "equation" in poly_lower)
    )
    grobner_present = bool(
        grobner_text
        and len(grobner_text) >= 200
        and ("grobner" in grobner_lower or "groebner" in grobner_lower)
        and ("basis" in grobner_lower or "elimination" in grobner_lower or "lex" in grobner_lower)
    )

    cost = parse_cost_artifact(cost_text)
    rho_steps = int(challenge.get("generic_rho_steps", 0))
    cost_present = isinstance(cost, dict)
    cost_beats_rho = False
    if cost_present:
        method = str(cost.get("method") or cost.get("algorithm") or "").lower()
        generic_steps = safe_int(cost.get("generic_dlp_steps"), 0)
        group_ops = safe_int(cost.get("group_ops"), 0)
        relation_trials = safe_int(cost.get("relation_trials"), 0)
        generic_like = bool(
            cost.get("uses_generic_dlp")
            or cost.get("uses_bsgs")
            or cost.get("uses_pollard_rho")
            or any(marker in method for marker in GENERIC_METHOD_MARKERS)
        )
        claimed_work = max(generic_steps, group_ops, relation_trials)
        cost_beats_rho = bool(
            cost.get("beats_rho")
            and not generic_like
            and rho_steps
            and 0 < claimed_work < rho_steps
            and generic_steps == 0
        )

    research_terms = (
        "relation",
        "scalar-free",
        "scalar free",
        "summation",
        "semaev",
        "grobner",
        "groebner",
        "isogen",
        "prime-order",
        "precomputed",
        "rho",
    )
    hypothesis_present = useful_research_note(
        hypothesis_text,
        ("hypothesis", "claim", "proposal"),
        research_terms,
    )
    result_present = useful_research_note(
        result_text,
        ("result", "verifier", "evidence", "metric", "score"),
        (*research_terms, "pass", "fail", "accepted", "rejected"),
    )
    next_present = useful_research_note(
        next_text,
        ("next", "follow-up", "follow up", "future"),
        research_terms,
    )
    novelty_claim = parse_json_artifact(novelty_text)
    novelty_claim_present = bool(
        novelty_claim
        and isinstance(novelty_claim.get("claim_type"), str)
        and isinstance(novelty_claim.get("baseline"), str)
        and isinstance(novelty_claim.get("evidence"), str)
    )
    research_notebook_present = bool(hypothesis_present and result_present and next_present)

    meta.update(
        {
            "artifact_relation_count": relation_count,
            "artifact_mixed_wide_relation_count": mixed_count,
            "artifact_polynomial_present": polynomial_present,
            "artifact_grobner_present": grobner_present,
            "artifact_cost_present": cost_present,
            "artifact_cost_beats_rho": cost_beats_rho,
            "research_hypothesis_present": hypothesis_present,
            "research_result_present": result_present,
            "research_next_hypothesis_present": next_present,
            "research_novelty_claim_present": novelty_claim_present,
            "research_notebook_present": research_notebook_present,
        }
    )
    meta["algebra_artifact_bundle_present"] = bool(
        mixed_count >= 12 and polynomial_present and grobner_present and cost_beats_rho
    )
    meta["artifact_bundle_present"] = bool(
        meta["algebra_artifact_bundle_present"] and research_notebook_present
    )
    if not meta["artifact_bundle_present"]:
        missing = []
        if mixed_count < 12:
            missing.append("relations")
        if not polynomial_present:
            missing.append("polynomial_system")
        if not grobner_present:
            missing.append("grobner_log")
        if not cost_beats_rho:
            missing.append("cost_accounting")
        if not research_notebook_present:
            missing.append("research_notebook")
        meta["artifact_error"] = "missing_or_invalid:" + ",".join(missing)
    if not research_notebook_present:
        note_missing = []
        if not hypothesis_present:
            note_missing.append("hypothesis.md")
        if not result_present:
            note_missing.append("experiment_result.md")
        if not next_present:
            note_missing.append("next_hypothesis.md")
        meta["research_notebook_error"] = "missing_or_low_signal:" + ",".join(note_missing)
    return meta


def optional_secret(answer):
    if isinstance(answer, dict):
        for key in ("k", "secret", "scalar", "discrete_log"):
            if key in answer:
                return int(answer[key]), True
        return None, False
    return int(answer), True


def verify_discrete_log(mod, challenge, secret, ainvs, p, base, public, base_order):
    if not hasattr(mod, "solve_ecdlp"):
        return False, "solve.py must define solve_ecdlp(challenge)", {}
    answer = mod.solve_ecdlp(challenge)
    relation_meta = analyze_relations(answer, challenge, ainvs, p, base, public, base_order)
    if relation_meta["relation_secret"] is not None:
        relation_meta["relation_proves_k"] = bool(
            relation_meta["relation_proves_k"] and relation_meta["relation_secret"] % base_order == secret
        )
    if relation_meta["mixed_wide_relation_secret"] is not None:
        relation_meta["mixed_wide_relation_proves_k"] = bool(
            relation_meta["mixed_wide_relation_proves_k"]
            and relation_meta["mixed_wide_relation_secret"] % base_order == secret
        )

    raw_secret, scalar_returned = optional_secret(answer)
    scalar_valid = False
    recovered = None
    if scalar_returned:
        recovered = raw_secret % base_order
        if recovered == secret:
            scalar_valid = True
        else:
            recovered_public = mul_point(recovered, base, ainvs, p)
            scalar_valid = recovered_public == public
        if not scalar_valid:
            return False, f"wrong discrete log: got {recovered}", {}
    elif relation_meta["mixed_wide_relation_proves_k"]:
        recovered = relation_meta["mixed_wide_relation_secret"] % base_order
    else:
        return False, "no scalar returned and mixed wide relations do not derive the discrete log", {}

    return True, recovered, {
        **relation_meta,
        **analyze_work_claim(answer, challenge),
        **analyze_artifacts(answer, challenge, ainvs, p, base, public, base_order),
        "scalar_returned": scalar_returned,
        "scalar_free_relation_proof": bool(not scalar_returned and relation_meta["mixed_wide_relation_proves_k"]),
    }


def normalize_candidate(item):
    if isinstance(item, dict):
        label = item.get("label") or item.get("lmfdb_label")
        p = item.get("p") or item.get("prime")
    elif isinstance(item, (list, tuple)) and len(item) >= 2:
        label, p = item[0], item[1]
    elif isinstance(item, str) and "@" in item:
        label, p = item.rsplit("@", 1)
    else:
        raise TypeError(f"candidate must be dict, pair, or label@p string: {item!r}")
    if not isinstance(label, str):
        raise TypeError(f"candidate label must be a string: {item!r}")
    return label, int(p)


def call_solver(mod, records):
    if hasattr(mod, "find_index_calculus_targets"):
        try:
            return mod.find_index_calculus_targets(records, prime_limit=PRIME_LIMIT, top_k=TOP_K)
        except TypeError:
            return mod.find_index_calculus_targets(records)
    if hasattr(mod, "find_weak_curves"):
        try:
            return mod.find_weak_curves(records, prime_limit=PRIME_LIMIT, top_k=TOP_K)
        except TypeError:
            return mod.find_weak_curves(records)
    if hasattr(mod, "solve"):
        return mod.solve(records)
    raise AttributeError(
        "solve.py must define find_index_calculus_targets(records, prime_limit=12000, top_k=5)"
    )


def analyze_novelty_evidence(label, p, inv, relation_meta, campaign_context, strict_relation_system):
    key = target_key(label, p)
    known_targets = campaign_context.get("known_success_targets") or set()
    evidence = []

    if key not in known_targets:
        evidence.append("new_verified_target")
    if relation_meta.get("scalar_free_relation_proof"):
        if campaign_context.get("scalar_free_successes", 0) == 0:
            evidence.append("first_scalar_free_relation_proof")
        else:
            evidence.append("scalar_free_target_upgrade")
    if inv.get("precomputed_target") and relation_meta.get("scalar_free_relation_proof"):
        evidence.append("large_precomputed_scalar_free_proof")
    if strict_relation_system and key not in known_targets:
        evidence.append("new_target_strict_relation_system")
    if (
        relation_meta.get("mixed_wide_relation_proves_k")
        and relation_meta.get("mixed_wide_relation_rank", 0) >= 8
        and relation_meta.get("research_notebook_present")
        and relation_meta.get("artifact_cost_beats_rho")
        and key not in known_targets
    ):
        evidence.append("notebook_linked_mixed_relation_proof")

    seen = set()
    evidence = [item for item in evidence if not (item in seen or seen.add(item))]
    replay = bool(key in known_targets)
    notebook_present = bool(relation_meta.get("research_notebook_present"))
    novelty_bonus_eligible = bool(notebook_present and evidence)
    if novelty_bonus_eligible:
        novelty_bonus = 40.0
        if "new_verified_target" in evidence:
            novelty_bonus += 90.0
        if "first_scalar_free_relation_proof" in evidence:
            novelty_bonus += 260.0
        elif "scalar_free_target_upgrade" in evidence:
            novelty_bonus += 160.0
        if "large_precomputed_scalar_free_proof" in evidence:
            novelty_bonus += 500.0
        if "new_target_strict_relation_system" in evidence:
            novelty_bonus += 120.0
        if "notebook_linked_mixed_relation_proof" in evidence:
            novelty_bonus += 60.0
    else:
        novelty_bonus = 0.0

    return {
        "campaign_replay_target": replay,
        "novelty_evidence": evidence,
        "novelty_evidence_count": len(evidence),
        "novelty_bonus_eligible": novelty_bonus_eligible,
        "novelty_bonus": round(min(1000.0, novelty_bonus), 6),
    }


def evaluate_candidates(records, candidates, mod):
    if not isinstance(candidates, list):
        raise TypeError(f"solver must return a list, got {type(candidates).__name__}")
    by_label = {row["label"]: row for row in records}
    seen_pairs = set()
    evaluated = []
    proof_failures = []
    campaign_context = campaign_state_context()

    for raw in candidates[:MAX_CANDIDATES]:
        label, p = normalize_candidate(raw)
        if label not in by_label:
            raise ValueError(f"unknown LMFDB label: {label}")
        target = precomputed_target(by_label[label], p)
        if p < 3 or (target is None and not is_prime(p)):
            raise ValueError(f"p must be an odd prime: {p}")
        if not (3 <= p < PRIME_LIMIT) and target is None:
            raise ValueError(f"p must be below {PRIME_LIMIT} unless it is a precomputed target: {p}")
        pair = (label, p)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)

        record = by_label[label]
        inv = reduction_invariants(record, p)
        if not inv["flags"]:
            continue
        challenge, secret = make_challenge(inv, record["ainvs"])
        public = point_from_json(challenge["public"])
        ok, proof, relation_meta = verify_discrete_log(
            mod,
            challenge,
            secret,
            record["ainvs"],
            p,
            inv["base"],
            public,
            inv["base_order"],
        )
        if not ok:
            proof_failures.append({"label": label, "p": p, "reason": proof})
            continue
        if "prime_order_index_calculus_target" in inv["flags"]:
            strict_relation_system = (
                relation_meta.get("mixed_wide_relation_proves_k")
                and relation_meta.get("mixed_wide_relation_count", 0) >= 12
                and relation_meta.get("mixed_wide_relation_rank", 0) >= 8
                and relation_meta.get("mixed_wide_q_coeff_count", 0) >= 6
                and relation_meta.get("mixed_wide_index_count", 0) >= 6
                and relation_meta.get("direct_factor_log_count", 0) == 0
                and relation_meta.get("artifact_bundle_present")
                and relation_meta.get("artifact_cost_beats_rho")
            )
            if strict_relation_system:
                relation_bonus = min(
                    700.0,
                    160.0
                    + 30.0 * relation_meta["mixed_wide_q_coeff_count"]
                    + 18.0 * relation_meta["mixed_wide_relation_rank"]
                    + 8.0 * relation_meta["mixed_wide_relation_count"],
                )
                if inv.get("precomputed_target"):
                    if relation_meta.get("scalar_free_relation_proof"):
                        relation_bonus = 3200.0 + min(900.0, 20.0 * math.log2(inv["base_order"]))
                    else:
                        relation_bonus = 900.0
            else:
                if relation_meta.get("direct_factor_log_count", 0):
                    relation_bonus = min(18.0, 2.0 * relation_meta.get("mixed_wide_relation_count", 0))
                else:
                    relation_bonus = min(90.0, 6.0 * relation_meta.get("mixed_wide_relation_count", 0))
        else:
            strict_relation_system = False
            relation_bonus = min(30.0, 5.0 * relation_meta.get("relation_count", 0))
        novelty_meta = analyze_novelty_evidence(
            label, p, inv, relation_meta, campaign_context, strict_relation_system
        )
        if novelty_meta["campaign_replay_target"] and not novelty_meta["novelty_bonus_eligible"]:
            relation_bonus = min(relation_bonus, 30.0)
        flags = [*inv["flags"]]
        if relation_meta.get("relation_count", 0):
            flags.append("verified_index_calculus_relations")
        if relation_meta.get("relation_proves_k"):
            flags.append("relation_derived_ecdlp")
        if relation_meta.get("mixed_wide_relation_proves_k"):
            flags.append("mixed_wide_relation_derived_ecdlp")
        if relation_meta.get("direct_factor_log_count", 0):
            flags.append("direct_factor_log_rows")
        if relation_meta.get("work_beats_rho"):
            flags.append("rho_beating_work_claim")
        if relation_meta.get("work_generic_like"):
            flags.append("generic_work_claim")
        if relation_meta.get("artifact_bundle_present"):
            flags.append("durable_research_artifacts")
        if relation_meta.get("algebra_artifact_bundle_present"):
            flags.append("algebra_relation_artifacts")
        if relation_meta.get("research_notebook_present"):
            flags.append("research_notebook_artifacts")
        if novelty_meta.get("campaign_replay_target"):
            flags.append("campaign_replay_target")
        if novelty_meta.get("novelty_bonus_eligible"):
            flags.append("novelty_bonus_eligible")
        for evidence in novelty_meta.get("novelty_evidence") or []:
            flags.append(f"novelty_{evidence}")
        if relation_meta.get("artifact_cost_beats_rho"):
            flags.append("artifact_cost_beats_rho")
        if relation_meta.get("scalar_returned"):
            flags.append("scalar_returned")
        if relation_meta.get("scalar_free_relation_proof"):
            flags.append("scalar_free_relation_proof")
        score = round(inv["score"] + relation_bonus + novelty_meta["novelty_bonus"], 6)
        inv = {
            **inv,
            "base": point_to_json(inv["base"]),
            "flags": flags,
            "score": score,
            "proof_secret": int(proof),
            **relation_meta,
            **novelty_meta,
            "index_calculus_bonus": relation_bonus,
            "strict_relation_system": bool(strict_relation_system),
            "challenge_public": point_to_json(public),
        }
        evaluated.append(inv)

    best_by_label = {}
    for inv in evaluated:
        old = best_by_label.get(inv["label"])
        if old is None or (inv["score"], inv["p"]) > (old["score"], old["p"]):
            best_by_label[inv["label"]] = inv

    ranked = sorted(best_by_label.values(), key=lambda row: (row["score"], row["label"], row["p"]), reverse=True)
    ranked = ranked[:TOP_K]
    total_score = round(sum(row["score"] for row in ranked), 3)
    return ranked, total_score, proof_failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()

    try:
        records = load_records()
        mod = load_solver()
        candidates = call_solver(mod, records)
        ranked, total_score, proof_failures = evaluate_candidates(records, candidates, mod)
    except Exception as exc:
        print(f"result=FAIL error={type(exc).__name__}:{exc}")
        if args.verify:
            raise SystemExit(1)
        raise

    if args.emit:
        print(
            json.dumps(
                {"score": total_score, "top": ranked, "proof_failures": proof_failures[:5]},
                indent=2,
                sort_keys=True,
            )
        )
        return

    if not ranked:
        print(f"result=FAIL candidates=0 score=0.000 proof_failures={len(proof_failures)}")
        if args.verify:
            raise SystemExit(1)
        return

    best = ranked[0]
    print(
        " ".join(
            [
                "result=ok",
                f"proved={len(ranked)}",
                f"score={total_score:.3f}",
                f"best={best['label']}@{best['p']}",
                f"base_order={best['base_order']}",
                f"base_lpf={best['base_lpf']}",
                f"flags={','.join(best['flags'])}",
                f"novelty={','.join(best.get('novelty_evidence') or []) or 'none'}",
                f"replay={'yes' if best.get('campaign_replay_target') else 'no'}",
            ]
        )
    )


if __name__ == "__main__":
    main()
