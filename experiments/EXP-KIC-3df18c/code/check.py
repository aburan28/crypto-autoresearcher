#!/usr/bin/env python3
"""Independent coordinate replay for the frozen N19 affine-pool experiment.

This module does not import search.cpp kernels or use a scalar-log lookup.
It is launched once, after the producer's science output is frozen.
"""
from __future__ import annotations
import argparse
import copy
import functools
import hashlib
import itertools
import json
import struct
import time
from collections import Counter, defaultdict
from pathlib import Path

BITS = 19
LIMIT = 1 << BITS
MASK = LIMIT - 1
POLY = LIMIT | 39
ORDER = 262543
TARGET_COUNT = 6909
WORDS = (TARGET_COUNT + 63) // 64

def require(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fmul(a: int, b: int) -> int:
    """Unreduced carryless product, then explicit polynomial long division."""
    raw = 0
    for bit in range(BITS):
        if b & (1 << bit):
            raw ^= a << bit
    for bit in range(2 * BITS - 2, BITS - 1, -1):
        if raw & (1 << bit):
            raw ^= POLY << (bit - BITS)
    return raw

@functools.lru_cache(maxsize=1 << 19)
def fsq(a: int) -> int:
    return fmul(a, a)

def finv(a: int) -> int:
    require(a != 0, "zero independent field inverse")
    u, v, g, h = a, POLY, 1, 0
    while u != 1:
        require(u != 0, "noninvertible field element")
        shift = u.bit_length() - v.bit_length()
        if shift < 0:
            u, v = v, u
            g, h = h, g
            shift = -shift
        u ^= v << shift
        g ^= h << shift
    while g.bit_length() > BITS:
        g ^= POLY << (g.bit_length() - BITS - 1)
    return g

Point = tuple[int, int] | None

def negative(p: Point) -> Point:
    return None if p is None else (p[0], p[1] ^ p[0])

def on_curve(p: Point) -> bool:
    if p is None:
        return True
    x, y = p
    return fsq(y) ^ fmul(x, y) == fmul(fsq(x), x) ^ fsq(x) ^ 1

def plus(p: Point, q: Point) -> Point:
    if p is None:
        return q
    if q is None:
        return p
    x, y = p
    u, v = q
    if x == u:
        if y ^ v == x:
            return None
        require(p == q and x != 0, "invalid independent equal-x input")
        slope = x ^ fmul(y, finv(x))
        z = fsq(slope) ^ slope ^ 1
        return z, fsq(x) ^ fmul(slope ^ 1, z)
    slope = fmul(y ^ v, finv(x ^ u))
    z = fsq(slope) ^ slope ^ x ^ u ^ 1
    return z, fmul(slope, x ^ z) ^ z ^ y

def plus_many(p: Point, others: list[Point]) -> list[Point]:
    """One independent extended-Euclid inverse per nonexceptional batch."""
    out: list[Point] = [None] * len(others)
    indices: list[int] = []
    denominators: list[int] = []
    prefixes: list[int] = []
    acc = 1
    for index, q in enumerate(others):
        if p is None:
            out[index] = q
        elif q is None:
            out[index] = p
        elif p[0] == q[0]:
            out[index] = plus(p, q)
        else:
            d = p[0] ^ q[0]
            indices.append(index)
            denominators.append(d)
            prefixes.append(acc)
            acc = fmul(acc, d)
    if indices:
        inverse = finv(acc)
        for offset in range(len(indices) - 1, -1, -1):
            index = indices[offset]
            q = others[index]
            assert p is not None and q is not None
            one = fmul(inverse, prefixes[offset])
            inverse = fmul(inverse, denominators[offset])
            slope = fmul(p[1] ^ q[1], one)
            x = fsq(slope) ^ slope ^ p[0] ^ q[0] ^ 1
            out[index] = x, fmul(slope, p[0] ^ x) ^ x ^ p[1]
    return out

def times(p: Point, n: int) -> Point:
    result = None
    while n:
        if n & 1:
            result = plus(result, p)
        p = plus(p, p)
        n >>= 1
    return result

def square_point(p: Point) -> Point:
    return None if p is None else (fsq(p[0]), fsq(p[1]))

def canonical_x(x: int) -> int:
    best = x
    for _ in range(18):
        x = fsq(x)
        best = min(best, x)
    return best

def expand(representatives: list[list[int]]) -> tuple[list[list[Point]], list[list[int]]]:
    full: list[list[Point]] = []
    x_orbits: list[list[int]] = []
    all_points: set[Point] = set()
    all_x: set[int] = set()
    for source in representatives:
        p: Point = tuple(source)
        require(p is not None and p[0] != 0 and on_curve(p) and times(p, ORDER) is None,
                "independent representative invalid")
        points: list[Point] = []
        xs: list[int] = []
        for _ in range(19):
            assert p is not None
            require(on_curve(p) and times(p, ORDER) is None, "independent conjugate invalid")
            require(p not in all_points and negative(p) not in all_points and p[0] not in all_x,
                    "independent signed orbit overlap")
            all_points.update((p, negative(p)))
            all_x.add(p[0])
            points.extend((p, negative(p)))
            xs.append(p[0])
            p = square_point(p)
        require(p == tuple(source) and len(set(points)) == 38,
                "independent signed orbit length mismatch")
        full.append(sorted(points))
        x_orbits.append(xs)
    require(len(full) == 37 and len(all_points) == 1406 and len(all_x) == 703,
            "independent pool cardinality mismatch")
    return full, x_orbits

@functools.lru_cache(maxsize=200000)
def canonical_plane(vertices: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    current = vertices
    best = None
    for _ in range(19):
        option = tuple(sorted(current))
        if best is None or option < best:
            best = option
        current = tuple(fsq(value) for value in current)
    assert best is not None
    return best

def enumerate_planes(x_orbits: list[list[int]], basis_transform=lambda x: x) -> dict[tuple[int, ...], tuple[int, ...]]:
    """Hash-bucket implementation independent of the producer's sorted vector."""
    buckets: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    for i in range(len(x_orbits)):
        for j in range(i + 1, len(x_orbits)):
            for x in x_orbits[i]:
                for y in x_orbits[j]:
                    buckets[x ^ y].append((i, j, x, y))
    planes: dict[tuple[int, ...], tuple[int, ...]] = {}
    for records in buckets.values():
        for left, right in itertools.combinations(records, 2):
            ids = tuple(sorted((left[0], left[1], right[0], right[1])))
            if len(set(ids)) != 4:
                continue
            original = tuple(basis_transform(z) for z in (left[2], left[3], right[2], right[3]))
            key = canonical_plane(original)
            require(len(set(key)) == 4 and key[0] ^ key[1] ^ key[2] ^ key[3] == 0,
                    "independent plane degeneracy")
            prior = planes.setdefault(key, ids)
            require(prior == ids, "independent plane conflicting IDs")
    return planes

def exhaustive_first_eight(x_orbits: list[list[int]]) -> set[tuple[int, ...]]:
    owner = {x: i for i, orbit in enumerate(x_orbits[:8]) for x in orbit}
    values = sorted(owner)
    seen: set[tuple[int, ...]] = set()
    for a, b, c in itertools.combinations(values, 3):
        d = a ^ b ^ c
        if d <= c or d not in owner:
            continue
        if len({owner[a], owner[b], owner[c], owner[d]}) != 4:
            continue
        seen.add(canonical_plane((a, b, c, d)))
    return seen

def reverse19(value: int) -> int:
    return int(f"{value:019b}"[::-1], 2)

def check_geometry(run: Path, x_orbits: list[list[int]]) -> tuple[dict[tuple[int, ...], tuple[int, ...]], set[tuple[int, ...]]]:
    catalogue = json.loads((run / "plane_catalogue.json").read_text())
    saved = {tuple(row["key"]): tuple(row["orbit_ids"]) for row in catalogue["planes"]}
    require(len(saved) == len(catalogue["planes"]), "catalogue duplicates plane keys")
    computed = enumerate_planes(x_orbits)
    require(saved == computed, "independent full pair-bucket catalogue mismatch")
    first = enumerate_planes(x_orbits[:8])
    require(set(first) == exhaustive_first_eight(x_orbits), "first-eight triple-XOR mismatch")
    reversed_orbits = [[reverse19(x) for x in orbit] for orbit in x_orbits]
    reversed_result = enumerate_planes(reversed_orbits, reverse19)
    require(reversed_result == computed, "bit reversal plane enumeration mismatch")
    compatible = set(computed.values())
    # Negative controls must fail full-admission plane validity.
    def valid(vertices, orbit_ids):
        return (len(set(vertices)) == 4 and len(set(orbit_ids)) == 4 and
                vertices[0] ^ vertices[1] ^ vertices[2] ^ vertices[3] == 0 and
                computed.get(canonical_plane(tuple(vertices))) == tuple(sorted(orbit_ids)))
    # Structural negative fixtures run even if the finite pool has zero planes.
    fixture = (1, 2, 4, 7)
    assert len(set(fixture)) == 4 and fixture[0] ^ fixture[1] ^ fixture[2] ^ fixture[3] == 0
    assert len(set((fixture[0], fixture[0], fixture[2], fixture[3]))) != 4
    assert len(set((0, 0, 2, 3))) != 4
    assert fixture[0] ^ fixture[1] ^ fixture[2] ^ (fixture[3] ^ 1) != 0
    if computed:
        key, ids = next(iter(computed.items()))
        require(valid(key, ids), "valid plane rejected")
        require(not valid((key[0], key[0], key[2], key[3]), ids), "repeated vertex accepted")
        require(not valid(key, (ids[0], ids[0], ids[2], ids[3])), "repeated orbit accepted")
        require(not valid((key[0] ^ 1, key[1], key[2], key[3]), ids), "one-bit perturbation accepted")
    return computed, compatible

def target_points(pool: dict, generator: Point) -> tuple[list[Point], list[int]]:
    points = []
    keys = []
    all_signed: set[Point] = set()
    for scalar in pool["public_target_scalar_representatives"]:
        require(0 < scalar < ORDER, "invalid public scalar")
        q = times(generator, scalar)
        require(q is not None and on_curve(q) and times(q, ORDER) is None, "invalid public target")
        points.append(q)
        keys.append(canonical_x(q[0]))
        one_orbit: set[Point] = set()
        current = q
        for _ in range(19):
            assert current is not None
            require(on_curve(current), "independent target conjugate off curve")
            for signed in (current, negative(current)):
                require(signed not in one_orbit and signed not in all_signed,
                        "independent target signed-orbit overlap")
                one_orbit.add(signed)
                all_signed.add(signed)
            current = square_point(current)
        require(current == q and len(one_orbit) == 38, "independent target orbit not size 38")
    require(len(points) == TARGET_COUNT and len(set(keys)) == TARGET_COUNT,
            "independent target partition mismatch")
    require(len(all_signed) == ORDER - 1, "independent target signed-orbit union incomplete")
    return points, keys

def direct_mitm(base: list[Point], targets: list[Point], keys: list[int]) -> dict:
    """Unordered coordinate pair sums, followed by Q-P batch queries."""
    pair_witness: dict[Point, tuple[int, int]] = {}
    for i, p in enumerate(base):
        for j, result in enumerate(plus_many(p, base[i:]), i):
            pair_witness.setdefault(result, (i, j))
    point_index = {p: i for i, p in enumerate(base)}
    negatives = [negative(p) for p in base]
    rows = []
    exact_count = at_most_count = 0
    for q, key in zip(targets, keys):
        exact_witness = None
        for i, difference in enumerate(plus_many(q, negatives)):
            pair = pair_witness.get(difference)
            if pair is None:
                continue
            witness = (base[pair[0]], base[pair[1]], base[i])
            require(plus(plus(witness[0], witness[1]), witness[2]) == q,
                    "independent direct-MITM witness group replay failed")
            exact_witness = [pair[0], pair[1], i]
            break
        exact = exact_witness is not None
        at_most = exact or q in point_index or q in pair_witness
        exact_count += exact
        at_most_count += at_most
        rows.append({"target_key": key, "exact_three": exact, "at_most_three": at_most,
                     "triple_witness_indices": exact_witness})
    return {"exact_three": exact_count, "at_most_three": at_most_count,
            "pair_sum_keys": len(pair_witness), "per_target": rows}

def cache_rows(path: Path, target_keys: list[int]):
    blob = path.read_bytes()
    require(blob[:8] == b"KIC19S01", "cache magic mismatch")
    version, targets, words, triples, pairs = struct.unpack_from("<5I", blob, 8)
    require((version, targets, words, triples, pairs) == (1, TARGET_COUNT, WORDS, 9139, 703),
            "cache dimensions mismatch")
    expect = 28 + (triples + pairs) * words * 8
    require(len(blob) == expect, "cache byte length mismatch")
    data = memoryview(blob)[28:]
    rows = []
    for index in range(triples + pairs):
        row = struct.unpack_from("<" + "Q" * words, data, index * words * 8)
        require(row[-1] >> (TARGET_COUNT % 64) == 0, "unused high cache bits are nonzero")
        rows.append(row)
    return rows[:triples], rows[triples:]

def historical_at_most(path: Path) -> dict[str, int]:
    require(digest(path) == "c94567b1257a7137c05174c656f7397b694b6bcc6612d9a9dca9095595781151",
            "historical global JSONL hash mismatch")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    chosen = [row for row in rows if row.get("kind") == "global_pool_optimum"]
    require(len(chosen) == 1, "historical optimum row absent or duplicated")
    histogram = chosen[0]["coverage_histogram"]
    require(sum(histogram.values()) == 66045 and histogram.get("6257") == 1 and
            max(map(int, histogram)) == 6257, "historical at-most histogram malformed")
    return histogram

def full_frontier_from_cache(score_rows: list[dict], triple_rows, pair_rows,
                             representatives: list[Point], index_by_key: dict[int, int],
                             historical: dict[str, int]) -> dict:
    """Independent 66045-base bitset replay with whole-row Python integers."""
    triple_ints = [sum(word << (64 * bit) for bit, word in enumerate(row)) for row in triple_rows]
    pair_ints = [sum(word << (64 * bit) for bit, word in enumerate(row)) for row in pair_rows]
    ti = {name: index for index, name in enumerate(itertools.combinations_with_replacement(range(37), 3))}
    pi = {name: index for index, name in enumerate(itertools.combinations_with_replacement(range(37), 2))}
    singleton = []
    for point in representatives:
        assert point is not None
        singleton.append(1 << index_by_key[canonical_x(point[0])])
    hist = Counter()
    max_exact = -1
    max_ids: list[tuple[int, ...]] = []
    for row in score_rows:
        ids = tuple(row["orbit_ids"])
        exact = 0
        for names in itertools.combinations_with_replacement(ids, 3):
            exact |= triple_ints[ti[names]]
        at_most = exact
        for names in itertools.combinations_with_replacement(ids, 2):
            at_most |= pair_ints[pi[names]]
        for orbit in ids:
            at_most |= singleton[orbit]
        exact_count, at_most_count = exact.bit_count(), at_most.bit_count()
        require((row["exact_three"], row["at_most_three"]) == (exact_count, at_most_count),
                f"frontier score differs from retained cache at {ids}")
        hist[at_most_count] += 1
        if exact_count > max_exact:
            max_exact, max_ids = exact_count, [ids]
        elif exact_count == max_exact:
            max_ids.append(ids)
    require({str(k): v for k, v in hist.items()} == historical,
            "full at-most histogram differs from historical global JSONL")
    require(max(hist) == 6257 and hist[6257] == 1,
            "unique historical at-most maximum failed")
    return {"at_most_histogram": dict(sorted(hist.items())), "global_exact_max": max_exact,
            "global_exact_max_indices": max_ids}

def support_verdicts(ids: tuple[int, ...], triple_rows, pair_rows, target_keys: list[int],
                     index_by_key: dict[int, int], representatives: list[Point]):
    triples = list(itertools.combinations_with_replacement(range(37), 3))
    pairs = list(itertools.combinations_with_replacement(range(37), 2))
    tri_index = {name: i for i, name in enumerate(triples)}
    pair_index = {name: i for i, name in enumerate(pairs)}
    exact = [0] * WORDS
    for names in itertools.combinations_with_replacement(ids, 3):
        row = triple_rows[tri_index[tuple(names)]]
        for j in range(WORDS):
            exact[j] |= row[j]
    at_most = exact[:]
    for names in itertools.combinations_with_replacement(ids, 2):
        row = pair_rows[pair_index[tuple(names)]]
        for j in range(WORDS):
            at_most[j] |= row[j]
    for i in ids:
        p = representatives[i]
        assert p is not None
        k = index_by_key[canonical_x(p[0])]
        at_most[k >> 6] |= 1 << (k & 63)
    return exact, at_most

def verify_certificate(candidate: dict, expected_ids: tuple[int, ...],
                       catalogue: dict[tuple[int, ...], tuple[int, ...]],
                       exact_count: int, at_most_count: int,
                       exact_bits: list[int], at_most_bits: list[int],
                       per_target: list[dict], index_by_key: dict[int, int]) -> None:
    ids = tuple(candidate["orbit_ids"])
    key = tuple(candidate["plane_key"])
    require(ids == expected_ids and len(set(ids)) == 4 and ids == tuple(sorted(ids)),
            "certificate orbit IDs invalid")
    require(len(key) == 4 and key == tuple(sorted(key)) and len(set(key)) == 4 and
            key[0] ^ key[1] ^ key[2] ^ key[3] == 0 and catalogue.get(key) == ids,
            "certificate affine witness invalid")
    require(candidate["exact_three"] == exact_count and
            candidate["at_most_three"] == at_most_count,
            "certificate coverage score invalid")
    require(len(per_target) == TARGET_COUNT and len(exact_bits) == WORDS and
            len(at_most_bits) == WORDS, "certificate support dimensions invalid")
    for row in per_target:
        index = index_by_key[row["target_key"]]
        require(bool(exact_bits[index >> 6] & (1 << (index & 63))) == row["exact_three"] and
                bool(at_most_bits[index >> 6] & (1 << (index & 63))) == row["at_most_three"],
                "certificate cache bitset disagrees with independent target replay")

def forgery_controls(candidate: dict, ids: tuple[int, ...],
                     catalogue: dict[tuple[int, ...], tuple[int, ...]],
                     exact_count: int, at_most_count: int,
                     exact_bits: list[int], at_most_bits: list[int],
                     per_target: list[dict], index_by_key: dict[int, int]) -> list[str]:
    verify_certificate(candidate, ids, catalogue, exact_count, at_most_count,
                       exact_bits, at_most_bits, per_target, index_by_key)
    cases = []
    vertex = copy.deepcopy(candidate)
    vertex["plane_key"][0] ^= 1
    cases.append(("vertex_flip", vertex, exact_bits))
    wrong_id = copy.deepcopy(candidate)
    wrong_id["orbit_ids"][0] = next(i for i in range(37) if i not in ids)
    cases.append(("wrong_orbit_id", wrong_id, exact_bits))
    score = copy.deepcopy(candidate)
    score["exact_three"] += 1
    cases.append(("incremented_score", score, exact_bits))
    damaged = exact_bits[:]
    damaged[0] ^= 1
    cases.append(("corrupted_bitset", copy.deepcopy(candidate), damaged))
    rejected = []
    for name, altered, bits in cases:
        try:
            verify_certificate(altered, ids, catalogue, exact_count, at_most_count,
                               bits, at_most_bits, per_target, index_by_key)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError(f"{name} forgery passed the genuine verifier")
    return rejected

def run(pool_path: Path, run_path: Path, historical_path: Path, out_path: Path) -> dict:
    began = time.monotonic()
    pool = json.loads(pool_path.read_text())
    require(pool["field_bits"] == 19 and pool["subgroup_order"] == ORDER and
            pool["pool_size"] == 37 and pool["cofactor"] == 2, "pool parameter mismatch")
    representatives = pool["pool_representatives"]
    full, x_orbits = expand(representatives)
    generator = tuple(representatives[0])
    targets, target_keys = target_points(pool, generator)
    geometry = json.loads((run_path / "geometry.json").read_text())
    require(geometry["target_keys"] == sorted(target_keys), "producer target-key partition mismatch")
    planes, compatible = check_geometry(run_path, x_orbits)
    require(geometry["canonical_planes"] == len(planes) and
            geometry["plane_compatible_bases"] == len(compatible), "producer plane counts mismatch")
    selected = json.loads((run_path / "selected.json").read_text())
    scores = json.loads((run_path / "base_scores.json").read_text())
    require(len(scores["ranked_scores"]) == 66045, "producer frontier length mismatch")
    require([row["rank"] for row in scores["ranked_scores"]] == list(range(1, 66046)),
            "producer rank labels incomplete")
    score_by_ids = {tuple(row["orbit_ids"]): row for row in scores["ranked_scores"]}
    require(len(score_by_ids) == 66045, "producer frontier duplicate bases")
    require(set(score_by_ids) == set(itertools.combinations(range(37), 4)),
            "producer frontier omitted a four-orbit subset")
    for ids, row in score_by_ids.items():
        require(row["plane_compatible"] == (ids in compatible), "frontier geometry membership mismatch")
    ranked = sorted(scores["ranked_scores"],
                    key=lambda row: (-row["exact_three"], -row["at_most_three"],
                                     tuple(row["orbit_ids"]), tuple(row.get("plane_key", ()))) )
    require(ranked == scores["ranked_scores"], "producer ranking rule mismatch")
    cache_path = run_path / "support_cache.bin"
    cache_manifest = json.loads((run_path / "support_cache_manifest.json").read_text())
    require(cache_manifest["cache_sha256"] == digest(cache_path), "cache manifest hash mismatch")
    cache_blob = cache_path.read_bytes()
    for region_name in ("triple_region", "pair_region"):
        region = cache_manifest[region_name]
        span = cache_blob[region["offset_bytes"]:region["offset_bytes"] + region["bytes"]]
        require(len(span) == region["bytes"] and hashlib.sha256(span).hexdigest() == region["sha256"],
                f"cache {region_name} custody mismatch")
    require(cache_manifest["target_keys_sha256"] == hashlib.sha256(
        json.dumps(sorted(target_keys), separators=(",", ":")).encode()).hexdigest(),
        "cache sorted-target-key binding mismatch")
    triples, pairs = cache_rows(cache_path, target_keys)
    indexed_keys = {key: i for i, key in enumerate(sorted(target_keys))}
    historical = historical_at_most(historical_path)
    full_scores = full_frontier_from_cache(scores["ranked_scores"], triples, pairs,
                                           [tuple(p) for p in representatives], indexed_keys,
                                           historical)
    require({str(k): v for k, v in full_scores["at_most_histogram"].items()} ==
            scores["at_most_histogram"], "frontier histogram serialization mismatch")
    require(scores["global_exact_max"] == full_scores["global_exact_max"] and
            [tuple(ids) for ids in scores["global_exact_max_indices"]] ==
            sorted(full_scores["global_exact_max_indices"]),
            "measured global exact maximum metadata mismatch")
    require(selected["candidate_exists"] == bool(compatible), "zero-plane/winner status mismatch")
    chosen = tuple(selected["orbit_ids"]) if selected["candidate_exists"] else None
    require(chosen is None or chosen in compatible, "selected base not plane-compatible")
    if chosen is not None:
        best = next(row for row in ranked if row["plane_compatible"])
        require(chosen == tuple(best["orbit_ids"]), "selected base violates frozen ranking")
        expected_key = min(key for key, ids in planes.items() if ids == chosen)
        require(tuple(selected["plane_key"]) == expected_key,
                "selected encoding witness is not the lexicographically first plane")
    prior = (6, 9, 22, 28)
    null = next((ids for ids in itertools.combinations(range(37), 4) if ids not in compatible), None)
    bases = [("selected", chosen), ("prior", prior), ("null", null)]
    unique_results = {}
    output = {}
    for name, ids in bases:
        if ids is None:
            output[name] = {"exists": False}
            continue
        if ids not in unique_results:
            base = sorted(point for orbit in ids for point in full[orbit])
            unique_results[ids] = direct_mitm(base, targets, target_keys)
        result = unique_results[ids]
        score = score_by_ids[ids]
        require(result["exact_three"] == score["exact_three"] and
                result["at_most_three"] == score["at_most_three"],
                f"{name} direct MITM disagrees with frontier score")
        exbits, atbits = support_verdicts(ids, triples, pairs, target_keys, indexed_keys,
                                         [tuple(p) for p in representatives])
        for row in result["per_target"]:
            key_index = indexed_keys[row["target_key"]]
            require(bool(exbits[key_index >> 6] & (1 << (key_index & 63))) == row["exact_three"] and
                    bool(atbits[key_index >> 6] & (1 << (key_index & 63))) == row["at_most_three"],
                    f"{name} cache support disagrees with direct MITM")
        output[name] = {"exists": True, "orbit_ids": ids, **result}
    require(output["prior"]["exact_three"] == 6224 and output["prior"]["at_most_three"] == 6257,
            "independent prior regression failed")
    if chosen is not None:
        require(tuple(selected["plane_key"]) in planes and
                planes[tuple(selected["plane_key"])] == chosen, "selected plane certificate invalid")
        require(output["selected"]["exact_three"] == selected["exact_three"] and
                output["selected"]["at_most_three"] == selected["at_most_three"],
                "selected score certificate invalid")
        exbits, _ = support_verdicts(chosen, triples, pairs, target_keys, indexed_keys,
                                    [tuple(p) for p in representatives])
        _, atbits = support_verdicts(chosen, triples, pairs, target_keys, indexed_keys,
                                    [tuple(p) for p in representatives])
        rejected = forgery_controls(selected, chosen, planes,
                                    output["selected"]["exact_three"],
                                    output["selected"]["at_most_three"],
                                    exbits, atbits, output["selected"]["per_target"], indexed_keys)
        forgery_scope = "actual selected plane and direct target replay"
    else:
        # The pre-registered zero-plane outcome remains valid. Exercise the
        # identical verifier on an explicit synthetic affine fixture.
        fixture = (1, 2, 4, 7)
        ids = (0, 1, 2, 3)
        synthetic = {"orbit_ids": list(ids), "plane_key": list(fixture),
                     "exact_three": 0, "at_most_three": 0}
        empty_rows = [{"target_key": key, "exact_three": False, "at_most_three": False}
                      for key in target_keys]
        rejected = forgery_controls(synthetic, ids, {fixture: ids}, 0, 0,
                                    [0] * WORDS, [0] * WORDS, empty_rows, indexed_keys)
        forgery_scope = "synthetic affine fixture; no selected pool plane exists"
    result = {
        "schema": "crypto.autoresearch.n19_independent_replay.v1",
        "status": "passed",
        "method": "independent Python long-division GF(2^19), extended-Euclid inverse, coordinate group law and direct unordered pair-sum MITM",
        "scope": "finite public-synthetic fixed 37-orbit pool",
        "pool_sha256": digest(pool_path),
        "geometry_sha256": digest(run_path / "geometry.json"),
        "plane_catalogue_sha256": digest(run_path / "plane_catalogue.json"),
        "base_scores_sha256": digest(run_path / "base_scores.json"),
        "support_cache_sha256": digest(cache_path),
        "historical_global_sha256": digest(historical_path),
        "full_frontier_cache_replay": {"bases": 66045, "at_most_histogram_match": True,
                                       "global_exact_max": full_scores["global_exact_max"],
                                       "global_exact_max_indices": full_scores["global_exact_max_indices"]},
        "canonical_planes": len(planes),
        "plane_compatible_bases": len(compatible),
        "first_eight_triple_xor": len(exhaustive_first_eight(x_orbits)),
        "bit_reversal_control": "passed",
        "negative_geometry_controls": "passed",
        "forgery_controls": rejected,
        "forgery_scope": forgery_scope,
        "distinct_bases_replayed": len(unique_results),
        "base_results": output,
        "wall_seconds": time.monotonic() - began,
    }
    out_path.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.pool, args.run, args.historical, args.output)
    print(json.dumps({"status": result["status"], "canonical_planes": result["canonical_planes"],
                      "bases_replayed": result["distinct_bases_replayed"]}, sort_keys=True))

if __name__ == "__main__":
    main()
