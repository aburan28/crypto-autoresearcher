"""Frozen-plan public-coordinate cohort generation, invoked only by actual compute.

No constructor, scalar log, fitting rule or candidate result is imported.  The
point census and validity search are preprocessing costs, not free advice.
The public random nonce is recorded before any future-cohort draw.  Plan-only
schedule descriptions neither draw entropy nor enumerate curve points.
"""
from __future__ import annotations

from collections import Counter as Bag, OrderedDict
import hashlib
import json
from math import isqrt
import os
from pathlib import Path
import re
import secrets
from typing import Any

from curve import Counter, Curve, point_json

SCHEMA = "classical.ecdlp.transfer-study.public-cohort/v1"
EXCLUSION_SCHEMA = "classical.ecdlp.transfer-study.exclusions/v1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
MAX_P = 1048575


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} outside declared integer domain")
    return value


def _config(plan: dict) -> dict:
    config = plan.get("cohort")
    if not isinstance(config, dict):
        raise ValueError("cohort plan object required")
    seed = config.get("seed_hex")
    if not isinstance(seed, str) or HEX64.fullmatch(seed) is None:
        raise ValueError("fixed 256-bit cohort seed required")
    strata = config.get("strata")
    if not isinstance(strata, list) or not strata:
        raise ValueError("nonempty frozen strata required")
    ids = set()
    for s in strata:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not ID.fullmatch(s["id"]) or s["id"] in ids:
            raise ValueError("unique safe stratum IDs required")
        ids.add(s["id"])
        _integer(s.get("curve_count"), "curve_count", 1, 64)
        low = _integer(s.get("p_min"), "p_min", 7, MAX_P)
        high = _integer(s.get("p_max"), "p_max", low, MAX_P)
        first = low + ((3 - low) % 4)
        if first > high:
            raise ValueError("field interval has no p=3 mod4 candidates")
        _integer(s.get("max_proposals"), "max_proposals", 1, 100000)
        mode = s.get("target_mode")
        r = s.get("target_order")
        if mode == "all_nonidentity":
            _integer(r, "target_order", 3, MAX_P + 2049)
            if r % 2 == 0 or not prime(r, Bag()):
                raise ValueError("fixed exact order must be odd prime")
            if s.get("target_count") not in (None, r - 1):
                raise ValueError("exact stratum target count must equal r-1")
        elif mode == "sampled_unique":
            _integer(s.get("target_count"), "target_count", 1, MAX_P)
            if r is not None:
                _integer(r, "target_order", 3, MAX_P + 2049)
        else:
            raise ValueError("unsupported target mode")
        if s.get("r_bits") is not None:
            _integer(s["r_bits"], "r_bits", 2, 21)
    _integer(config.get("max_point_sampling_attempts", 10000), "max_point_sampling_attempts", 1, 1000000)
    return config


def describe_plan(plan: dict) -> dict:
    """Return exact schedule sizes without entropy or future-cohort generation."""
    config = _config(plan)
    panels = []
    for s in config["strata"]:
        n = s["target_order"] - 1 if s["target_mode"] == "all_nonidentity" else s["target_count"]
        panels.append({"id": s["id"], "curve_count": s["curve_count"], "targets_per_curve": n,
                       "target_cases": n * s["curve_count"], "target_mode": s["target_mode"],
                       "p_min": s["p_min"], "p_max": s["p_max"],
                       "max_proposals": s["max_proposals"]})
    return {"schema": "classical.ecdlp.transfer-study.cohort-description/v1",
            "fixture_count_planned": sum(s["curve_count"] for s in panels),
            "target_cases_planned": sum(s["target_cases"] for s in panels),
            "curve_proposal_cap": sum(s["max_proposals"] for s in panels),
            "panels": panels, "cohort_draws": 0, "entropy_draws": 0,
            "measurement_started": False}


class Stream:
    """SHAKE256 counter stream with rejection-sampled bounded integers."""
    def __init__(self, seed: bytes, domain: str, costs: Bag):
        self.seed, self.domain, self.index, self.costs = seed, domain, 0, costs

    def randbelow(self, bound: int) -> int:
        if type(bound) is not int or bound < 1:
            raise ValueError("positive bounded draw required")
        width = max(1, (bound.bit_length() + 7) // 8)
        ceiling = 1 << (8 * width)
        cutoff = ceiling - ceiling % bound
        while True:
            raw = hashlib.shake_256(self.seed + b"\0" + self.domain.encode() + self.index.to_bytes(16, "big")).digest(width)
            self.index += 1
            self.costs["cohort_shake_draw"] += 1
            self.costs["cohort_shake_output_bytes"] += width
            value = int.from_bytes(raw, "big")
            if value < cutoff:
                return value % bound
            self.costs["cohort_rng_rejection"] += 1


def prime(n: int, costs: Bag) -> bool:
    """Exact trial-division certification, explicitly outside constructor costs."""
    costs["cohort_primality_call"] += 1
    if type(n) is not int or n < 2:
        return False
    if n % 2 == 0:
        costs["cohort_trial_division"] += 1
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        costs["cohort_trial_division"] += 1
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def j_invariant(p: int, a: int, b: int, costs: Bag | None = None) -> int:
    denominator = (4 * a * a * a + 27 * b * b) % p
    if denominator == 0:
        raise ValueError("singular curve has no accepted j key")
    if costs is not None:
        costs["cohort_j_invariant_call"] += 1
        costs["cohort_builtin_modular_inverse_call"] += 1
    return (1728 * 4 * a * a * a * pow(denominator, -1, p)) % p


class ResidueCache:
    """At most eight O(p) residue tables; all construction work is charged."""
    def __init__(self, costs: Bag, capacity: int = 8):
        self.costs, self.capacity, self.tables = costs, capacity, OrderedDict()
        self.peak_bytes = 0

    def get(self, p: int) -> bytearray:
        if p in self.tables:
            self.costs["cohort_residue_cache_hit"] += 1
            self.tables.move_to_end(p)
            return self.tables[p]
        self.costs["cohort_residue_cache_miss"] += 1
        table = bytearray(p)
        table[0] = 1
        for y in range(1, (p + 1) // 2):
            table[y * y % p] = 1
            self.costs["cohort_residue_table_square"] += 1
        self.tables[p] = table
        if len(self.tables) > self.capacity:
            self.tables.popitem(last=False)
            self.costs["cohort_residue_cache_eviction"] += 1
        self.peak_bytes = max(self.peak_bytes, sum(map(len, self.tables.values())))
        return table


def rhs(p: int, a: int, b: int, x: int, costs: Bag) -> int:
    costs["cohort_rhs_evaluation"] += 1
    # Exactly three integer products and two additions, one modular reduction.
    costs["cohort_rhs_integer_product"] += 3
    costs["cohort_rhs_integer_addition"] += 2
    costs["cohort_rhs_modular_reduction"] += 1
    return (x * x * x + a * x + b) % p


def point_count(p: int, a: int, b: int, cache: ResidueCache, costs: Bag) -> int:
    table = cache.get(p)
    total = 1
    for x in range(p):
        value = rhs(p, a, b, x, costs)
        total += 1 if value == 0 else (2 if table[value] else 0)
        costs["cohort_point_count_x"] += 1
    return total


def _sample_point(p: int, a: int, b: int, stream: Stream, costs: Bag, cap: int) -> tuple[int, int]:
    for _ in range(cap):
        costs["cohort_point_proposal"] += 1
        x = stream.randbelow(p)
        value = rhs(p, a, b, x, costs)
        if value == 0:
            # An odd prime-order curve has no affine order-two points.
            costs["cohort_point_zero_rhs_rejection"] += 1
            continue
        y = pow(value, (p + 1) // 4, p)
        costs["cohort_builtin_modular_power_call"] += 1
        if y * y % p != value:
            costs["cohort_point_nonresidue_rejection"] += 1
            continue
        if stream.randbelow(2):
            y = p - y
        return x, y
    raise RuntimeError("frozen public point-sampling cap reached")


def _all_points(p: int, a: int, b: int, cache: ResidueCache, costs: Bag) -> list[tuple[int, int]]:
    table = cache.get(p)
    points = []
    for x in range(p):
        value = rhs(p, a, b, x, costs)
        costs["cohort_target_census_x"] += 1
        if value == 0:
            points.append((x, 0))
        elif table[value]:
            y = pow(value, (p + 1) // 4, p)
            costs["cohort_builtin_modular_power_call"] += 1
            points.extend(((x, y), (x, p - y)))
    return sorted(points)


def exclusion_keys(document: dict) -> set[tuple[int, int]]:
    if not isinstance(document, dict) or document.get("schema") != EXCLUSION_SCHEMA:
        raise ValueError("frozen prior-exclusion schema required")
    blocked = document.get("excluded_fields", [])
    if not isinstance(blocked, list):
        raise ValueError("excluded fields must be a list")
    for p in blocked:
        _integer(p, "excluded field", 7, MAX_P)
    records = document.get("curve_keys")
    if not isinstance(records, list):
        raise ValueError("prior exclusion key list required")
    result = set()
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("bad prior exclusion item")
        p = _integer(item.get("p"), "exclusion p", 7, MAX_P)
        j = _integer(item.get("j"), "exclusion j", 0, p - 1)
        result.add((p, j))
    return result


def _snapshot(path: Path, value: dict, *, exclusive: bool = False) -> None:
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    target = path if exclusive else path.with_name(path.name + ".tmp")
    with target.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if not exclusive:
        os.replace(target, path)


def _history(stream, item: dict) -> None:
    stream.write(json.dumps(item, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def generate(plan: dict, outdir: Path | str, *, exclusions_data: dict) -> dict:
    """Generate once after frozen admission; retain every validity-only proposal.

    Operational shortfall returns an explicitly incomplete public cohort.  The
    caller must perform zero scientific candidate attempts on an incomplete
    cohort.  This is never a request to extend a frozen proposal cap.
    """
    config = _config(plan)
    schedule = describe_plan(plan)
    if plan.get("status") != "frozen":
        raise ValueError("actual generation requires frozen standalone plan")
    prior = exclusion_keys(exclusions_data)
    excluded_fields = set(exclusions_data.get("excluded_fields", []))
    directory = Path(outdir)
    directory.mkdir(parents=True, exist_ok=False)
    nonce = secrets.token_hex(32)
    _snapshot(directory / "cohort-nonce.json", {"schema": "classical.ecdlp.transfer-study.cohort-nonce/v1",
              "public_nonce_hex": nonce, "plan_canonical_sha256": sha(canonical(plan)),
              "recorded_before_first_curve_draw": True}, exclusive=True)
    costs: Bag = Bag()
    cache = ResidueCache(costs)
    seed = bytes.fromhex(config["seed_hex"]) + bytes.fromhex(nonce) + hashlib.sha256(canonical(plan)).digest()
    public = {"schema": SCHEMA, "experiment_id": plan["experiment_id"], "plan_canonical_sha256": sha(canonical(plan)),
              "public_nonce_hex": nonce, "generation_status": "incomplete", "fixtures": [],
              "schedule": schedule, "selection_rule": "public validity only; no constructor or scalar-ordering output consulted",
              "deduplication_rule": "equal (field prime,j) excluded, including both twist classes",
              "scalar_truth_generated": False, "shortfalls": []}
    seen = set(prior)
    base_order_costs = Bag()
    failures = []
    _snapshot(directory / "cohort-public.json", public, exclusive=True)
    try:
        with (directory / "cohort-history.jsonl").open("x") as history:
            for s in config["strata"]:
                selected = 0
                stream = Stream(seed, "curve/" + s["id"], costs)
                for ordinal in range(s["max_proposals"]):
                    if selected == s["curve_count"]:
                        break
                    before = dict(costs)
                    first = s["p_min"] + ((3 - s["p_min"]) % 4)
                    p = first + 4 * stream.randbelow((s["p_max"] - first) // 4 + 1)
                    a, b = stream.randbelow(p), stream.randbelow(p)
                    record = {"stratum": s["id"], "proposal_ordinal": ordinal, "p": p, "a": a, "b": b}
                    # Durable intent precedes validity work, so interrupted last
                    # proposals are unresolved rather than silently absent.
                    _history(history, {"event": "proposal_intent", **record})
                    reason = None
                    if p in excluded_fields:
                        reason = "excluded_prior_field"
                    elif not prime(p, costs):
                        reason = "nonprime_field"
                    else:
                        costs["cohort_discriminant_check"] += 1
                        if (4 * a * a * a + 27 * b * b) % p == 0:
                            reason = "singular"
                        else:
                            j = j_invariant(p, a, b, costs)
                            record["j"] = j
                            if (p, j) in seen:
                                reason = "prior_or_current_field_j_key"
                            else:
                                r = point_count(p, a, b, cache, costs)
                                trace = p + 1 - r
                                record.update(r=r, trace=trace)
                                if s.get("target_order") is not None and r != s["target_order"]:
                                    reason = "wrong_exact_order"
                                elif s.get("r_bits") is not None and r.bit_length() != s["r_bits"]:
                                    reason = "wrong_order_bitlength"
                                elif r == p:
                                    reason = "anomalous_order"
                                elif trace == 0:
                                    reason = "supersingular_trace_zero"
                                elif not prime(r, costs) or r <= 2:
                                    reason = "nonprime_or_even_curve_order"
                                else:
                                    curve_id = f"transfer-{s['id']}-{selected:03d}-" + sha(canonical({"p": p, "a": a, "b": b, "r": r}))[:12]
                                    point_stream = Stream(seed, "points/" + curve_id, costs)
                                    cap = config.get("max_point_sampling_attempts", 10000)
                                    base = _sample_point(p, a, b, point_stream, costs, cap)
                                    counter = Counter()
                                    curve = Curve(p, a, b, counter)
                                    if not curve.contains(base) or curve.multiply(base, r) is not None:
                                        raise RuntimeError("public full-order/base certificate disagreement")
                                    base_order_costs.update(counter.snapshot())
                                    if s["target_mode"] == "all_nonidentity":
                                        targets = _all_points(p, a, b, cache, costs)
                                        if len(targets) != r - 1:
                                            raise RuntimeError("exact target census/order disagreement")
                                        panel = "exact"
                                    else:
                                        if s["target_count"] > r - 1:
                                            raise RuntimeError("frozen unique target count exceeds nonidentity subgroup")
                                        targets, target_set = [], set()
                                        proposals = 0
                                        while len(targets) < s["target_count"]:
                                            if proposals >= cap:
                                                raise RuntimeError("frozen unique-target selection cap reached")
                                            proposals += 1
                                            point = _sample_point(p, a, b, point_stream, costs, cap)
                                            if point in target_set:
                                                costs["cohort_duplicate_target_rejection"] += 1
                                                continue
                                            target_set.add(point)
                                            targets.append(point)
                                        panel = "sampled"
                                    fixture = {"curve_id": curve_id, "stratum_id": s["id"], "p": p, "a": a, "b": b, "r": r,
                                               "base": point_json(base), "panel": panel,
                                               "targets": [{"target_id": f"{curve_id}-q{i:05d}", "point": point_json(q)} for i, q in enumerate(targets)],
                                               "generation_certificate": {"method": "complete quadratic-residue x census", "point_count": r,
                                                    "x_values_counted": p, "trace": trace, "j": j, "full_order_prime": True,
                                                    "base_nonidentity": True, "base_r_multiple_is_identity": True,
                                                    "base_order_check_counts": counter.snapshot(), "proposal_ordinal": ordinal}}
                                    public["fixtures"].append(fixture)
                                    seen.add((p, j))
                                    selected += 1
                                    record.update(curve_id=curve_id, selected_slot=selected - 1, target_count=len(targets))
                                    reason = "accepted"
                    record["event"] = "proposal_result"
                    record["status"] = reason
                    record["cost_delta"] = {key: costs[key] - before.get(key, 0) for key in costs if costs[key] != before.get(key, 0)}
                    _history(history, record)
                    if reason == "accepted":
                        _snapshot(directory / "cohort-public.json", public)
                if selected != s["curve_count"]:
                    failures.append({"stratum": s["id"], "reason": "frozen_curve_proposal_cap", "selected": selected,
                                     "planned": s["curve_count"], "proposal_cap": s["max_proposals"]})
                    break
    except Exception as error:
        failures.append({"reason": "generation_exception", "error_type": type(error).__name__, "message": str(error)})
    public["generation_status"] = "complete" if not failures and len(public["fixtures"]) == schedule["fixture_count_planned"] else "incomplete"
    completed = {s["id"]: sum(f["stratum_id"] == s["id"] for f in public["fixtures"]) for s in config["strata"]}
    public["shortfalls"] = [{"stratum": s["id"], "planned_fixtures": s["curve_count"], "actual_fixtures": completed[s["id"]]}
                            for s in config["strata"] if completed[s["id"]] != s["curve_count"]]
    public["generation_failures"] = failures
    public["fixture_count"] = len(public["fixtures"])
    public["target_cases"] = sum(len(f["targets"]) for f in public["fixtures"])
    _snapshot(directory / "cohort-public.json", public)
    cost_record = {"schema": "classical.ecdlp.transfer-study.cohort-costs/v1", "counts": dict(sorted(costs.items())),
                   "base_order_check_counts": dict(sorted(base_order_costs.items())), "residue_cache_peak_bytes": cache.peak_bytes,
                   "scope": "Actual public validity search/census/point generation only; no candidate evaluation or log labels",
                   "unpriced_work": ["Python containers/control/JSON/hashing/fsync", "integer bit costs of products, trial division, SHAKE and builtin modular power/inverse"]}
    _snapshot(directory / "cohort-costs.json", cost_record, exclusive=True)
    _snapshot(directory / "cohort-completion.json", {"schema": "classical.ecdlp.transfer-study.cohort-completion/v1",
              "generation_status": public["generation_status"], "fixture_count": public["fixture_count"], "target_cases": public["target_cases"],
              "plan_fixture_count": schedule["fixture_count_planned"], "plan_target_cases": schedule["target_cases_planned"],
              "public_cohort_sha256": sha((directory / "cohort-public.json").read_bytes()),
              "history_sha256": sha((directory / "cohort-history.jsonl").read_bytes()), "scientific_candidate_attempts": 0,
              "scalar_truth_generated": False, "failures": failures}, exclusive=True)
    return public
