#!/usr/bin/env python3
"""Pure design logic for the frozen four-level m=51 rho benchmark.

This module has no execution side effects.  The launcher and analyzer both
reconstruct the exact schedule and record plan through these functions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


FIELD_DEGREE = 51
FIELD_MASK = (1 << FIELD_DEGREE) - 1
REDUCTION_MASK = 0x4B
UINT64_MASK = (1 << 64) - 1
AMBIENT_ORDER = 2_251_799_852_369_764
SUBGROUP_ORDER = 17_192_986_687
COFACTOR = 130_972
F_PI = 32_756_041
PARENT_CONDUCTOR = 120_871
BOTTOM_CONDUCTOR = F_PI
PAIR_COUNT = 32
INFERENCE_PER_PAIR = 96
AA_PER_PAIR = 32
INFERENCE_BLOCKS = PAIR_COUNT * INFERENCE_PER_PAIR
AA_BLOCKS = PAIR_COUNT * AA_PER_PAIR
TOTAL_BLOCKS = INFERENCE_BLOCKS + AA_BLOCKS
ROBUSTNESS_SETUP_ROOTS = 16
ROBUSTNESS_BRIDGE_ROOTS = 1
ROBUSTNESS_TOTAL_SETUP_ROOTS = ROBUSTNESS_SETUP_ROOTS + ROBUSTNESS_BRIDGE_ROOTS
ROBUSTNESS_BLOCKS_PER_ROOT = 32
ROBUSTNESS_RECORDS = ROBUSTNESS_TOTAL_SETUP_ROOTS * ROBUSTNESS_BLOCKS_PER_ROOT * 4
ARMS = ("C", "A", "P", "B")
ARM_LEVEL = {
    "C": "f1",
    "A": "f271",
    "P": "f120871",
    "B": "f32756041",
}
ARM_CONDUCTOR = {
    "C": 1,
    "A": 271,
    "P": PARENT_CONDUCTOR,
    "B": BOTTOM_CONDUCTOR,
}
SCHEDULE_HEADER = (
    "block_id",
    "subset",
    "pair_id",
    "within_pair",
    "f271_orbit_id",
    "f271_conjugate",
    "pb_conjugate",
)
PLAN_HEADER = (
    "record_id",
    "block_id",
    "subset",
    "replicate",
    "pair_id",
    "within_pair",
    "arm",
    "level",
    "curve_id",
    "orbit_id",
    "conjugate",
    "b",
    "a2",
    "f_E",
    "mode",
    "setup_seed",
    "target_seed",
    "walk_seed",
    "target_index",
)
CORE_PLAN_HEADER = (
    "unit_id",
    "record_id",
    "b",
    "a2",
    "mode",
    "setup_seed",
    "target_seed",
    "walk_seed",
    "target_index",
)


@dataclass(frozen=True)
class ScheduleRow:
    block_id: int
    subset: str
    pair_id: int
    within_pair: int
    f271_orbit_id: int
    f271_conjugate: int
    pb_conjugate: int


@dataclass(frozen=True)
class EndpointPair:
    pair_id: int
    global_index: int
    parent_b: int
    parent_orbit_rep: int
    bottom_b: int
    bottom_orbit_rep: int
    certificate_sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def require_int(value: Any, context: str, *, low: int = 0, high: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{context}: expected an integer")
    if value < low or (high is not None and value > high):
        raise ValueError(f"{context}: integer outside [{low},{high}]")
    return value


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _digest_order(seed: int, domain: str, labels: tuple[int, ...], value: int) -> bytes:
    payload = "|".join((str(seed), domain, *(str(x) for x in labels), str(value)))
    return hashlib.sha256(payload.encode("ascii")).digest()


def permuted(values: Iterable[int], seed: int, domain: str, *labels: int) -> list[int]:
    items = list(values)
    if len(items) != len(set(items)):
        raise ValueError("permuted input must contain unique integers")
    return sorted(items, key=lambda value: (_digest_order(seed, domain, labels, value), value))


def gf_mul(left: int, right: int) -> int:
    if not 0 <= left <= FIELD_MASK or not 0 <= right <= FIELD_MASK:
        raise ValueError("field element outside GF(2^51)")
    product = 0
    value = left
    multiplier = right
    while multiplier:
        if multiplier & 1:
            product ^= value
        multiplier >>= 1
        value <<= 1
        if value & (1 << FIELD_DEGREE):
            value ^= (1 << FIELD_DEGREE) | REDUCTION_MASK
    return product & FIELD_MASK


def gf_square(value: int) -> int:
    return gf_mul(value, value)


def conjugate(value: int, exponent: int) -> int:
    if not 0 <= exponent < FIELD_DEGREE:
        raise ValueError("conjugate exponent outside [0,50]")
    result = value
    for _ in range(exponent):
        result = gf_square(result)
    return result


def orbit(value: int) -> list[int]:
    seen: list[int] = []
    current = value
    while current not in seen:
        seen.append(current)
        current = gf_square(current)
        if len(seen) > FIELD_DEGREE:
            raise ValueError("Frobenius orbit exceeds field degree")
    if current != value:
        raise ValueError("Frobenius orbit did not return to its start")
    return seen


def frobenius_offset(base: int, value: int) -> int:
    """Return the unique exponent e with Frob^e(base) == value."""
    matches = [exponent for exponent in range(FIELD_DEGREE) if conjugate(base, exponent) == value]
    if len(matches) != 1:
        raise ValueError("Frobenius offset is not unique in a full size-51 orbit")
    return matches[0]


def generate_schedule(seed: int) -> list[ScheduleRow]:
    """Generate the endpoint-independent exact crossover schedule."""
    # A-conjugate streams are cyclic permutations.  Every six- or two-item
    # pair slice is duplicate-free, while global counts differ by at most one.
    a_inf_stream: dict[int, list[int]] = {}
    a_aa_stream: dict[int, list[int]] = {}
    for orbit_id in range(1, 17):
        order_inf = permuted(range(17), seed, "a-inf-conjugates", orbit_id)
        order_aa = permuted(range(17), seed, "a-aa-conjugates", orbit_id)
        a_inf_stream[orbit_id] = [order_inf[i % 17] for i in range(PAIR_COUNT * 6)]
        a_aa_stream[orbit_id] = [order_aa[i % 17] for i in range(PAIR_COUNT * 2)]

    # Every P/B pair sees all 51 conjugates once plus 45 distinct duplicates.
    # Across 32 pairs each conjugate is duplicated 28 or 29 times exactly.
    omission_order = permuted(range(51), seed, "pb-inf-omissions")
    omissions = [omission_order[i % 51] for i in range(PAIR_COUNT * 6)]

    # Held-out P/B assignments use 32 distinct conjugates per pair and each
    # conjugate appears globally 20 or 21 times.
    aa_order = permuted(range(51), seed, "pb-aa-cycle")
    aa_stream = [aa_order[i % 51] for i in range(PAIR_COUNT * AA_PER_PAIR)]

    rows: list[ScheduleRow] = []
    for pair_id in range(PAIR_COUNT):
        orbit_slots = [orbit_id for orbit_id in range(1, 17) for _ in range(6)]
        orbit_slots = permuted(
            range(len(orbit_slots)), seed, "a-inf-slot-order", pair_id
        )
        ordered_orbits = [
            [orbit_id for orbit_id in range(1, 17) for _ in range(6)][index]
            for index in orbit_slots
        ]
        a_positions = {orbit_id: 0 for orbit_id in range(1, 17)}
        first_lap = permuted(range(51), seed, "pb-inf-first-lap", pair_id)
        omitted = set(omissions[pair_id * 6 : (pair_id + 1) * 6])
        duplicate_lap = permuted(
            (value for value in range(51) if value not in omitted),
            seed,
            "pb-inf-second-lap",
            pair_id,
        )
        pb_values = first_lap + duplicate_lap
        for within_pair, orbit_id in enumerate(ordered_orbits):
            offset = pair_id * 6 + a_positions[orbit_id]
            a_positions[orbit_id] += 1
            rows.append(
                ScheduleRow(
                    block_id=pair_id * INFERENCE_PER_PAIR + within_pair,
                    subset="inference",
                    pair_id=pair_id,
                    within_pair=within_pair,
                    f271_orbit_id=orbit_id,
                    f271_conjugate=a_inf_stream[orbit_id][offset],
                    pb_conjugate=pb_values[within_pair],
                )
            )

        aa_orbit_base = [orbit_id for orbit_id in range(1, 17) for _ in range(2)]
        aa_slot_order = permuted(
            range(len(aa_orbit_base)), seed, "a-aa-slot-order", pair_id
        )
        aa_orbits = [aa_orbit_base[index] for index in aa_slot_order]
        a_positions = {orbit_id: 0 for orbit_id in range(1, 17)}
        pb_aa_values = aa_stream[pair_id * AA_PER_PAIR : (pair_id + 1) * AA_PER_PAIR]
        pb_aa_order = permuted(range(AA_PER_PAIR), seed, "pb-aa-slot-order", pair_id)
        pb_aa_values = [pb_aa_values[index] for index in pb_aa_order]
        for within_pair, orbit_id in enumerate(aa_orbits):
            offset = pair_id * 2 + a_positions[orbit_id]
            a_positions[orbit_id] += 1
            rows.append(
                ScheduleRow(
                    block_id=INFERENCE_BLOCKS + pair_id * AA_PER_PAIR + within_pair,
                    subset="aa",
                    pair_id=pair_id,
                    within_pair=within_pair,
                    f271_orbit_id=orbit_id,
                    f271_conjugate=a_aa_stream[orbit_id][offset],
                    pb_conjugate=pb_aa_values[within_pair],
                )
            )
    rows.sort(key=lambda row: row.block_id)
    validate_schedule(rows)
    return rows


def validate_schedule(rows: list[ScheduleRow]) -> None:
    if len(rows) != TOTAL_BLOCKS or [row.block_id for row in rows] != list(range(TOTAL_BLOCKS)):
        raise ValueError("schedule must contain exactly contiguous block IDs 0..4095")
    inference = [row for row in rows if row.subset == "inference"]
    aa = [row for row in rows if row.subset == "aa"]
    if len(inference) != INFERENCE_BLOCKS or len(aa) != AA_BLOCKS:
        raise ValueError("schedule subset counts differ from frozen design")
    if any(not 0 <= row.pair_id < PAIR_COUNT for row in rows):
        raise ValueError("schedule pair ID out of range")
    if any(not 1 <= row.f271_orbit_id <= 16 for row in rows):
        raise ValueError("f271 orbit ID out of range")
    if any(not 0 <= row.f271_conjugate < 17 for row in rows):
        raise ValueError("f271 conjugate out of range")
    if any(not 0 <= row.pb_conjugate < 51 for row in rows):
        raise ValueError("deep conjugate out of range")

    for pair_id in range(PAIR_COUNT):
        pair_inf = [row for row in inference if row.pair_id == pair_id]
        pair_aa = [row for row in aa if row.pair_id == pair_id]
        if len(pair_inf) != 96 or len(pair_aa) != 32:
            raise ValueError(f"pair {pair_id}: incorrect block counts")
        if [row.within_pair for row in pair_inf] != list(range(96)):
            raise ValueError(f"pair {pair_id}: inference within-pair IDs differ")
        if [row.within_pair for row in pair_aa] != list(range(32)):
            raise ValueError(f"pair {pair_id}: A/A within-pair IDs differ")
        if Counter(row.f271_orbit_id for row in pair_inf) != Counter({i: 6 for i in range(1, 17)}):
            raise ValueError(f"pair {pair_id}: inference f271 crossover differs")
        if Counter(row.f271_orbit_id for row in pair_aa) != Counter({i: 2 for i in range(1, 17)}):
            raise ValueError(f"pair {pair_id}: A/A f271 crossover differs")
        pb_inf = [row.pb_conjugate for row in pair_inf]
        counts = Counter(pb_inf)
        if set(counts) != set(range(51)) or sorted(counts.values()) != [1] * 6 + [2] * 45:
            raise ValueError(f"pair {pair_id}: inference P/B conjugates differ")
        if set(pb_inf[:51]) != set(range(51)) or len(set(pb_inf[51:])) != 45:
            raise ValueError(f"pair {pair_id}: P/B first/duplicate laps differ")
        if len({row.pb_conjugate for row in pair_aa}) != 32:
            raise ValueError(f"pair {pair_id}: A/A P/B conjugates are not distinct")
        for orbit_id in range(1, 17):
            if len({row.f271_conjugate for row in pair_inf if row.f271_orbit_id == orbit_id}) != 6:
                raise ValueError(f"pair {pair_id}, orbit {orbit_id}: repeated inference conjugate")
            if len({row.f271_conjugate for row in pair_aa if row.f271_orbit_id == orbit_id}) != 2:
                raise ValueError(f"pair {pair_id}, orbit {orbit_id}: repeated A/A conjugate")

    pb_inf_counts = Counter(row.pb_conjugate for row in inference)
    if set(pb_inf_counts.values()) != {60, 61} or Counter(pb_inf_counts.values()) != Counter({60: 39, 61: 12}):
        raise ValueError("global inference P/B balance differs from 60/61")
    pb_aa_counts = Counter(row.pb_conjugate for row in aa)
    if set(pb_aa_counts.values()) != {20, 21} or Counter(pb_aa_counts.values()) != Counter({20: 47, 21: 4}):
        raise ValueError("global A/A P/B balance differs from 20/21")
    for orbit_id in range(1, 17):
        counts = Counter(
            row.f271_conjugate
            for row in inference
            if row.f271_orbit_id == orbit_id
        )
        if Counter(counts.values()) != Counter({11: 12, 12: 5}):
            raise ValueError(f"orbit {orbit_id}: inference conjugate balance differs")
        counts = Counter(
            row.f271_conjugate for row in aa if row.f271_orbit_id == orbit_id
        )
        if Counter(counts.values()) != Counter({3: 4, 4: 13}):
            raise ValueError(f"orbit {orbit_id}: A/A conjugate balance differs")


def write_schedule(rows: list[ScheduleRow], handle: Any) -> None:
    writer = csv.DictWriter(handle, fieldnames=SCHEDULE_HEADER, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: getattr(row, name) for name in SCHEDULE_HEADER})


def read_schedule(path: Path) -> list[ScheduleRow]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SCHEDULE_HEADER:
            raise ValueError(f"{path}: schedule header differs from frozen schema")
        rows = []
        for line, raw in enumerate(reader, 2):
            if set(raw) != set(SCHEDULE_HEADER) or any(value is None for value in raw.values()):
                raise ValueError(f"{path}:{line}: malformed row")
            try:
                rows.append(
                    ScheduleRow(
                        block_id=int(raw["block_id"]),
                        subset=raw["subset"],
                        pair_id=int(raw["pair_id"]),
                        within_pair=int(raw["within_pair"]),
                        f271_orbit_id=int(raw["f271_orbit_id"]),
                        f271_conjugate=int(raw["f271_conjugate"]),
                        pb_conjugate=int(raw["pb_conjugate"]),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line}: noncanonical schedule value") from exc
    validate_schedule(rows)
    return rows


def read_f271_orbits(path: Path) -> dict[int, int]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ("orbit_id", "b", "a2", "orbit_size", "f_E"):
            raise ValueError(f"{path}: f271 header differs")
        result: dict[int, int] = {}
        for line, raw in enumerate(reader, 2):
            try:
                orbit_id = int(raw["orbit_id"])
                b = int(raw["b"])
                a2 = int(raw["a2"])
                orbit_size = int(raw["orbit_size"])
                conductor = int(raw["f_E"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line}: malformed f271 row") from exc
            if orbit_id in result or a2 != 0 or orbit_size != 17 or conductor != 271:
                raise ValueError(f"{path}:{line}: invalid f271 row")
            values = orbit(b)
            if len(values) != 17 or min(values) != b:
                raise ValueError(f"{path}:{line}: b is not a canonical size-17 orbit representative")
            result[orbit_id] = b
    if set(result) != set(range(1, 17)):
        raise ValueError(f"{path}: expected exactly orbit IDs 1..16")
    all_models = {conjugate(b, exponent) for b in result.values() for exponent in range(17)}
    if len(all_models) != 272:
        raise ValueError(f"{path}: f271 conjugate census is not 272 distinct models")
    return result


def load_selection(path: Path) -> tuple[dict[str, Any], list[EndpointPair]]:
    document = load_json(path)
    required = {"schema", "created_utc", "source_scan", "pairs"}
    if set(document) != required or document.get("schema") != "m51-deep-rho-selection-binding/v1":
        raise ValueError(f"{path}: selection binding fields/schema differ")
    source = document["source_scan"]
    source_required = {
        "study_id",
        "selection_sha256",
        "session_sha256",
        "tree_manifest_sha256",
        "frozen_manifest_sha256",
        "status",
        "scan_range",
        "selected_count",
        "cutoff_global_index",
        "modeled_population",
    }
    if not isinstance(source, dict) or set(source) != source_required:
        raise ValueError(f"{path}: source_scan fields differ")
    for name in (
        "selection_sha256",
        "session_sha256",
        "tree_manifest_sha256",
        "frozen_manifest_sha256",
    ):
        if not valid_sha256(source[name]):
            raise ValueError(f"{path}: invalid source hash {name}")
    if source["status"] != "quota_met_full_range_complete" or source["selected_count"] != 32:
        raise ValueError(f"{path}: source scan was not a valid full-range quota result")
    if source["scan_range"] != [0, 3_600_000_000]:
        raise ValueError(f"{path}: source scan range differs")
    population = source["modeled_population"]
    if population != {
        "eligible_parent_orbits": 2369,
        "eligible_bottom_orbits": 644368,
        "excluded_pilot_parent_fibers": 1,
    }:
        raise ValueError(f"{path}: modeled population differs")
    raw_pairs = document["pairs"]
    if not isinstance(raw_pairs, list) or len(raw_pairs) != PAIR_COUNT:
        raise ValueError(f"{path}: expected 32 selected pairs")
    pairs: list[EndpointPair] = []
    pair_fields = {
        "pair_id",
        "global_index",
        "parent_b",
        "parent_orbit_rep",
        "parent_orbit_size",
        "bottom_b",
        "bottom_orbit_rep",
        "bottom_orbit_size",
        "parent_f_E",
        "bottom_f_E",
        "certificate_path",
        "certificate_sha256",
        "source_pair_sha256",
    }
    for number, raw in enumerate(raw_pairs):
        if not isinstance(raw, dict) or set(raw) != pair_fields:
            raise ValueError(f"{path}: pair {number} fields differ")
        pair_id = require_int(raw["pair_id"], f"pair {number}:pair_id", high=31)
        global_index = require_int(raw["global_index"], f"pair {number}:global_index", high=3_599_999_999)
        parent_b = require_int(raw["parent_b"], f"pair {number}:parent_b", low=1, high=FIELD_MASK)
        parent_rep = require_int(raw["parent_orbit_rep"], f"pair {number}:parent_orbit_rep", low=1, high=FIELD_MASK)
        bottom_b = require_int(raw["bottom_b"], f"pair {number}:bottom_b", low=1, high=FIELD_MASK)
        bottom_rep = require_int(raw["bottom_orbit_rep"], f"pair {number}:bottom_orbit_rep", low=1, high=FIELD_MASK)
        if pair_id != number or parent_b != parent_rep:
            raise ValueError(f"{path}: pair {number} ID/canonical parent differs")
        if raw["parent_orbit_size"] != 51 or raw["bottom_orbit_size"] != 51:
            raise ValueError(f"{path}: pair {number} orbit sizes differ")
        if raw["parent_f_E"] != PARENT_CONDUCTOR or raw["bottom_f_E"] != BOTTOM_CONDUCTOR:
            raise ValueError(f"{path}: pair {number} conductors differ")
        if min(orbit(parent_rep)) != parent_rep or len(orbit(parent_rep)) != 51:
            raise ValueError(f"{path}: pair {number} parent representative is noncanonical")
        if min(orbit(bottom_rep)) != bottom_rep or len(orbit(bottom_rep)) != 51:
            raise ValueError(f"{path}: pair {number} bottom representative is noncanonical")
        if bottom_b not in orbit(bottom_rep):
            raise ValueError(f"{path}: pair {number} bottom source is outside bound orbit")
        frobenius_offset(bottom_rep, bottom_b)
        if not valid_sha256(raw["certificate_sha256"]) or not valid_sha256(raw["source_pair_sha256"]):
            raise ValueError(f"{path}: pair {number} hashes differ")
        if not isinstance(raw["certificate_path"], str) or not raw["certificate_path"]:
            raise ValueError(f"{path}: pair {number} certificate path differs")
        pairs.append(
            EndpointPair(
                pair_id=pair_id,
                global_index=global_index,
                parent_b=parent_b,
                parent_orbit_rep=parent_rep,
                bottom_b=bottom_b,
                bottom_orbit_rep=bottom_rep,
                certificate_sha256=raw["certificate_sha256"],
            )
        )
    if [pair.global_index for pair in pairs] != sorted(pair.global_index for pair in pairs):
        raise ValueError(f"{path}: pairs are not in global-rank order")
    if len({pair.parent_orbit_rep for pair in pairs}) != 32 or len({pair.bottom_orbit_rep for pair in pairs}) != 32:
        raise ValueError(f"{path}: selected orbit representatives are not distinct")
    return document, pairs


def build_plan(
    schedule: list[ScheduleRow],
    pairs: list[EndpointPair],
    f271: dict[int, int],
    seeds: dict[str, int],
) -> list[dict[str, Any]]:
    required_seeds = {
        "setup_root",
        "target_root",
        "walk_inference_root",
        "walk_aa_a_root",
        "walk_aa_b_root",
    }
    if set(seeds) < required_seeds:
        raise ValueError("missing plan seed namespace")
    pair_by_id = {pair.pair_id: pair for pair in pairs}
    records: list[dict[str, Any]] = []
    for row in schedule:
        pair = pair_by_id[row.pair_id]
        a_b = conjugate(f271[row.f271_orbit_id], row.f271_conjugate)
        # Apply the same Frobenius power to the certified edge endpoints.
        # bottom_orbit_rep is retained only as the population identity: the
        # certified child bottom_b can be a shifted member of that orbit.
        p_b = conjugate(pair.parent_b, row.pb_conjugate)
        b_b = conjugate(pair.bottom_b, row.pb_conjugate)
        curve_info = {
            "C": ("C", "", 0, 1),
            "A": (
                f"A-o{row.f271_orbit_id:02d}-c{row.f271_conjugate:02d}",
                row.f271_orbit_id,
                row.f271_conjugate,
                a_b,
            ),
            "P": (f"P-p{row.pair_id:02d}-c{row.pb_conjugate:02d}", row.pair_id, row.pb_conjugate, p_b),
            "B": (f"B-p{row.pair_id:02d}-c{row.pb_conjugate:02d}", row.pair_id, row.pb_conjugate, b_b),
        }
        replicates = ("inference",) if row.subset == "inference" else ("aa-A", "aa-B")
        for replicate in replicates:
            walk_seed = {
                "inference": seeds["walk_inference_root"],
                "aa-A": seeds["walk_aa_a_root"],
                "aa-B": seeds["walk_aa_b_root"],
            }[replicate]
            for arm in ARMS:
                curve_id, orbit_id, exponent, b = curve_info[arm]
                records.append(
                    {
                        "record_id": f"{replicate}-b{row.block_id:04d}-{arm}",
                        "block_id": row.block_id,
                        "subset": row.subset,
                        "replicate": replicate,
                        "pair_id": row.pair_id,
                        "within_pair": row.within_pair,
                        "arm": arm,
                        "level": ARM_LEVEL[arm],
                        "curve_id": curve_id,
                        "orbit_id": orbit_id,
                        "conjugate": exponent,
                        "b": b,
                        "a2": 0,
                        "f_E": ARM_CONDUCTOR[arm],
                        "mode": 0,
                        "setup_seed": seeds["setup_root"],
                        "target_seed": seeds["target_root"],
                        "walk_seed": walk_seed,
                        "target_index": row.block_id,
                    }
                )
    expected = INFERENCE_BLOCKS * 4 + AA_BLOCKS * 8
    if len(records) != expected or len({record["record_id"] for record in records}) != expected:
        raise ValueError("expanded record plan count/key mismatch")
    by_block: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_block[(record["replicate"], record["block_id"])].append(record)
    for key, block in by_block.items():
        if {record["arm"] for record in block} != set(ARMS) or len(block) != 4:
            raise ValueError(f"expanded block {key} does not contain four arms")
        if len({record["target_seed"] for record in block}) != 1 or len({record["target_index"] for record in block}) != 1:
            raise ValueError(f"expanded block {key} does not pair target scalars")
        p = next(record for record in block if record["arm"] == "P")
        b = next(record for record in block if record["arm"] == "B")
        if p["conjugate"] != b["conjugate"]:
            raise ValueError(f"expanded block {key} breaks P/B edge conjugacy")
        pair = pair_by_id[int(p["pair_id"])]
        exponent = int(p["conjugate"])
        if (
            p["b"] != conjugate(pair.parent_b, exponent)
            or b["b"] != conjugate(pair.bottom_b, exponent)
        ):
            raise ValueError(f"expanded block {key} is not a conjugate of the certified P/B edge")
    return records


def build_setup_robustness_plan(
    pairs: list[EndpointPair],
    f271: dict[int, int],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build 16 fresh inferential roots plus one original-root bridge."""
    required = {
        "panel_seed",
        "target_seed",
        "walk_seed",
        "setup_seed_derivation_root",
        "setup_seeds",
        "original_setup_seed",
    }
    if not required <= set(config):
        raise ValueError("setup-robustness configuration is incomplete")
    panel_seed = require_int(config["panel_seed"], "robustness panel_seed", high=UINT64_MASK)
    target_seed = require_int(config["target_seed"], "robustness target_seed", high=UINT64_MASK)
    walk_seed = require_int(config["walk_seed"], "robustness walk_seed", high=UINT64_MASK)
    raw_setup_seeds = config["setup_seeds"]
    if not isinstance(raw_setup_seeds, list) or len(raw_setup_seeds) != ROBUSTNESS_SETUP_ROOTS:
        raise ValueError("setup-robustness requires exactly 16 setup seeds")
    setup_seeds = [
        require_int(value, f"robustness setup_seeds[{index}]", high=UINT64_MASK)
        for index, value in enumerate(raw_setup_seeds)
    ]
    if len(set(setup_seeds)) != ROBUSTNESS_SETUP_ROOTS:
        raise ValueError("setup-robustness setup seeds are not distinct")
    derivation_root = require_int(
        config["setup_seed_derivation_root"],
        "robustness setup_seed_derivation_root",
        high=UINT64_MASK,
    )
    derived_setup_seeds = [
        int.from_bytes(
            hashlib.sha256(
                f"{derivation_root}|setup-robustness|{index}".encode("ascii")
            ).digest()[:8],
            "big",
        )
        for index in range(ROBUSTNESS_SETUP_ROOTS)
    ]
    if setup_seeds != derived_setup_seeds:
        raise ValueError("setup-robustness explicit setup seeds differ from derivation")
    original_setup_seed = require_int(
        config["original_setup_seed"],
        "robustness original_setup_seed",
        high=UINT64_MASK,
    )
    if original_setup_seed in set(setup_seeds):
        raise ValueError("original setup-root bridge duplicates a fresh setup root")
    all_setup_seeds = [*setup_seeds, original_setup_seed]
    disjoint = config.get("disjoint_from_primary_seeds")
    robustness_namespaces = {panel_seed, target_seed, walk_seed, derivation_root}
    if (
        not isinstance(disjoint, list)
        or any(isinstance(value, bool) or not isinstance(value, int) for value in disjoint)
        or len(disjoint) != len(set(disjoint))
        or len(robustness_namespaces) != 4
        or robustness_namespaces & set(disjoint)
        or set(setup_seeds) & (set(disjoint) | robustness_namespaces)
        or original_setup_seed not in set(disjoint)
        or original_setup_seed in robustness_namespaces
    ):
        raise ValueError("setup-robustness seeds are not disjoint from primary namespaces")
    if len(pairs) != PAIR_COUNT or {pair.pair_id for pair in pairs} != set(range(PAIR_COUNT)):
        raise ValueError("setup-robustness requires the exact 32 endpoint pairs")
    if set(f271) != set(range(1, 17)):
        raise ValueError("setup-robustness requires all 16 f271 orbits")

    a_panel: list[tuple[int, int]] = []
    for orbit_id in range(1, 17):
        choices = permuted(range(17), panel_seed, "robustness-a-panel", orbit_id)[:2]
        a_panel.extend((orbit_id, conjugate_id) for conjugate_id in choices)
    pair_by_id = {pair.pair_id: pair for pair in pairs}
    deep_panel = {
        pair_id: permuted(
            range(51), panel_seed, "robustness-pb-panel", pair_id
        )[0]
        for pair_id in range(PAIR_COUNT)
    }

    records: list[dict[str, Any]] = []
    for setup_root_id, setup_seed in enumerate(all_setup_seeds):
        for panel_slot, (a_orbit_id, a_conjugate) in enumerate(a_panel):
            pair = pair_by_id[panel_slot]
            pb_conjugate = deep_panel[panel_slot]
            curve_info = {
                "C": ("C", "", 0, 1),
                "A": (
                    f"A-o{a_orbit_id:02d}-c{a_conjugate:02d}",
                    a_orbit_id,
                    a_conjugate,
                    conjugate(f271[a_orbit_id], a_conjugate),
                ),
                "P": (
                    f"P-p{panel_slot:02d}-c{pb_conjugate:02d}",
                    panel_slot,
                    pb_conjugate,
                    conjugate(pair.parent_b, pb_conjugate),
                ),
                "B": (
                    f"B-p{panel_slot:02d}-c{pb_conjugate:02d}",
                    panel_slot,
                    pb_conjugate,
                    conjugate(pair.bottom_b, pb_conjugate),
                ),
            }
            for arm in ARMS:
                curve_id, orbit_id, exponent, b = curve_info[arm]
                records.append(
                    {
                        "record_id": (
                            f"robust-s{setup_root_id:02d}-b{panel_slot:02d}-{arm}"
                        ),
                        "block_id": setup_root_id * ROBUSTNESS_BLOCKS_PER_ROOT + panel_slot,
                        "subset": "setup_robustness",
                        "replicate": "setup-robustness",
                        "pair_id": panel_slot,
                        "within_pair": panel_slot,
                        "arm": arm,
                        "level": ARM_LEVEL[arm],
                        "curve_id": curve_id,
                        "orbit_id": orbit_id,
                        "conjugate": exponent,
                        "b": b,
                        "a2": 0,
                        "f_E": ARM_CONDUCTOR[arm],
                        "mode": 0,
                        "setup_seed": setup_seed,
                        "target_seed": target_seed,
                        "walk_seed": walk_seed,
                        "target_index": panel_slot,
                    }
                )

    if len(records) != ROBUSTNESS_RECORDS or len({row["record_id"] for row in records}) != ROBUSTNESS_RECORDS:
        raise ValueError("setup-robustness record count/key mismatch")
    by_root_block: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        root_id = all_setup_seeds.index(int(row["setup_seed"]))
        by_root_block[(root_id, int(row["pair_id"]))].append(row)
    if set(by_root_block) != {
        (root_id, panel_slot)
        for root_id in range(ROBUSTNESS_TOTAL_SETUP_ROOTS)
        for panel_slot in range(ROBUSTNESS_BLOCKS_PER_ROOT)
    }:
        raise ValueError("setup-robustness root/block coverage differs")
    for (root_id, panel_slot), block in by_root_block.items():
        if len(block) != 4 or {row["arm"] for row in block} != set(ARMS):
            raise ValueError(f"setup-robustness root/block {(root_id, panel_slot)} is unbalanced")
        if len({(row["target_seed"], row["walk_seed"], row["target_index"]) for row in block}) != 1:
            raise ValueError(f"setup-robustness root/block {(root_id, panel_slot)} is not seed-paired")
        p = next(row for row in block if row["arm"] == "P")
        b = next(row for row in block if row["arm"] == "B")
        pair = pair_by_id[panel_slot]
        exponent = deep_panel[panel_slot]
        if (
            p["conjugate"] != b["conjugate"]
            or p["b"] != conjugate(pair.parent_b, exponent)
            or b["b"] != conjugate(pair.bottom_b, exponent)
        ):
            raise ValueError(f"setup-robustness root/block {(root_id, panel_slot)} breaks its edge")
    for panel_slot in range(ROBUSTNESS_BLOCKS_PER_ROOT):
        rows = [row for row in records if row["pair_id"] == panel_slot]
        for arm in ARMS:
            models = {
                (row["curve_id"], row["b"], row["target_seed"], row["walk_seed"], row["target_index"])
                for row in rows
                if row["arm"] == arm
            }
            if len(models) != 1:
                raise ValueError(f"setup-robustness panel slot {panel_slot}/{arm} changes across roots")
    first_root = [row for row in records if row["setup_seed"] == setup_seeds[0]]
    distinct_by_arm = {
        arm: len(
            {
                (int(row["b"]), int(row["a2"]), int(row["mode"]))
                for row in first_root
                if row["arm"] == arm
            }
        )
        for arm in ARMS
    }
    if distinct_by_arm != {"C": 1, "A": 32, "P": 32, "B": 32} or len(
        {
            (int(row["b"]), int(row["a2"]), int(row["mode"]))
            for row in first_root
        }
    ) != 97:
        raise ValueError("setup-robustness panel does not contain 97 distinct native models")
    return records


def mix64(value: int) -> int:
    value &= UINT64_MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & UINT64_MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & UINT64_MASK
    return (value ^ (value >> 31)) & UINT64_MASK


def indexed_word(seed: int, index: int, domain: int, attempt: int) -> int:
    return mix64(
        seed
        ^ domain
        ^ mix64((index + 0x9E3779B97F4A7C15) & UINT64_MASK)
        ^ mix64((attempt + 0xD1B54A32D192ED03) & UINT64_MASK)
    )


def indexed_bounded(seed: int, index: int, domain: int, bound: int) -> int:
    if not 0 < bound <= UINT64_MASK:
        raise ValueError("bounded RNG bound outside uint64")
    threshold = ((-bound) & UINT64_MASK) % bound
    attempt = 0
    while True:
        value = indexed_word(seed, index, domain, attempt)
        if value >= threshold:
            return value % bound
        attempt += 1
        if attempt > UINT64_MASK:
            raise RuntimeError("indexed RNG rejection loop exhausted")


def expected_scalar(seed: int, index: int) -> int:
    return 1 + indexed_bounded(seed, index, 0x5441524745544B31, SUBGROUP_ORDER - 1)


def expected_walk_stream(seed: int, index: int) -> int:
    return indexed_word(seed, index, 0x57414C4B53545231, 0)


# target_seed, walk_seed, target_index, target_scalar, walk_stream_seed.
# These literals are cross-checked against the compiled C adapter before an
# admitted run; deriving the expected columns at test time would not catch an
# independent drift between the C core and this Python oracle.
RNG_TEST_VECTORS: tuple[tuple[int, int, int, int, int], ...] = (
    (202610136101, 202610136103, 0, 16025288604, 391490649573796340),
    (202610136101, 202610136103, 1, 10809152598, 708265878671456221),
    (202610136101, 202610136104, 3071, 4824054088, 14947724469027381272),
    (202610136101, 202610136105, 4095, 8863510036, 2321043084527788898),
    (0, 0, 0, 10183705979, 10579369430471239669),
    (
        18446744073709551615,
        18446744073709551615,
        18446744073709551615,
        10190091753,
        2897221405534219705,
    ),
    (
        81985529216486895,
        18364758544493064720,
        9223372036854775808,
        14150746353,
        8741266836832296987,
    ),
    (
        202610136101,
        202610136103,
        1234567890123456789,
        16667510271,
        10144411738113154670,
    ),
)


def log2_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator) or numerator <= 0 or denominator <= 0:
        raise ValueError("ratio inputs must be positive finite values")
    return math.log2(numerator / denominator)
