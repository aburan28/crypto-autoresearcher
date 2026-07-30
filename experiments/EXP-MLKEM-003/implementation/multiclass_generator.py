#!/usr/bin/env python3
"""Multi-class mutation generator and coverage accounting for EXP-MLKEM-003.

Generator classes (frozen specification):
  G1: xor 0x01 and xor 0xff at every ciphertext index
  G2: seeded coordinated k-byte contiguous/scattered flips + block inversions
  G3: alignment / lane-boundary mutations
  G4: malformed length (API only; never enters silent sets)
  G5: replay of G1-G4 across four keys (handled by callers looping seeds)

Deterministic: seeds drive offsets; no runtime randomness.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterator

PARAM_CT = {
    "ML-KEM-512": 768,
    "ML-KEM-768": 1088,
    "ML-KEM-1024": 1568,
}

KNOWN_PREFIX_AVX2_OMISSION = {
    "ML-KEM-1024": list(range(1536, 1568)),
}

MUTATION_CAP = 20000
SEEDS = [1, 2, 3, 4]


def seeded_rng(seed: int, salt: str) -> Any:
    """Deterministic byte stream from seed+salt (not cryptographic use)."""
    state = hashlib.sha256(f"{seed}:{salt}".encode()).digest()

    def next_bytes(n: int) -> bytes:
        nonlocal state
        out = bytearray()
        while len(out) < n:
            state = hashlib.sha256(state).digest()
            out.extend(state)
        return bytes(out[:n])

    def next_int(lo: int, hi: int) -> int:
        if hi <= lo:
            return lo
        b = next_bytes(4)
        v = int.from_bytes(b, "little")
        return lo + (v % (hi - lo))

    class R:
        pass

    r = R()
    r.bytes = next_bytes
    r.randint = next_int
    return r


@dataclass
class Mutation:
    class_id: str
    kind: str
    indices: list[int]
    xor_mask: int | None = None  # single-byte xor, or None for invert
    invert_blocks: bool = False
    label: str = ""


@dataclass
class ClassPlan:
    class_id: str
    parameter_set: str
    ct_len: int
    seed: int
    mutations: list[Mutation] = field(default_factory=list)
    capped: bool = False
    coverage: dict[str, Any] = field(default_factory=dict)


def plan_g1(parameter_set: str, seed: int, cap: int = MUTATION_CAP) -> ClassPlan:
    ct = PARAM_CT[parameter_set]
    plan = ClassPlan("G1_single_byte", parameter_set, ct, seed)
    count = 0
    indices_touched = set()
    for idx in range(ct):
        for xorv, label in ((0x01, "xor01"), (0xFF, "xorff")):
            if count >= cap:
                plan.capped = True
                break
            plan.mutations.append(
                Mutation("G1_single_byte", "single", [idx], xor_mask=xorv, label=label)
            )
            indices_touched.add(idx)
            count += 1
        if plan.capped:
            break
    plan.coverage = {
        "indices_targeted": sorted(indices_touched),
        "n_indices": len(indices_touched),
        "fraction": len(indices_touched) / ct,
        "mutation_events": count,
        "full_index_coverage": len(indices_touched) == ct and not plan.capped,
        "reaches_known_avx2_omission": bool(
            set(indices_touched) & set(KNOWN_PREFIX_AVX2_OMISSION.get(parameter_set, []))
        ),
    }
    return plan


def plan_g2(parameter_set: str, seed: int, cap: int = MUTATION_CAP) -> ClassPlan:
    ct = PARAM_CT[parameter_set]
    plan = ClassPlan("G2_multi_byte", parameter_set, ct, seed)
    rng = seeded_rng(seed, f"G2:{parameter_set}")
    count = 0
    indices_touched: set[int] = set()

    def add(mut: Mutation) -> bool:
        nonlocal count
        if count >= cap:
            plan.capped = True
            return False
        plan.mutations.append(mut)
        indices_touched.update(mut.indices)
        count += 1
        return True

    # Contiguous k-byte flips at seeded offsets covering full length
    for k in (2, 4, 8, 16):
        stride = max(1, k)
        offsets = list(range(0, ct - k + 1, stride))
        # Ensure known omission region is densely covered for ML-KEM-1024
        if parameter_set == "ML-KEM-1024":
            for o in range(1536 - k + 1, 1568):
                if 0 <= o <= ct - k:
                    offsets.append(o)
        offsets = sorted(set(offsets))
        for off in offsets:
            idxs = list(range(off, off + k))
            for xorv, lab in ((0x01, f"cont_k{k}_xor01"), (0xFF, f"cont_k{k}_xorff")):
                if not add(Mutation("G2_multi_byte", "contiguous", idxs, xor_mask=xorv, label=lab)):
                    break
            if plan.capped:
                break
        if plan.capped:
            break

    # Scattered k-byte flips
    if not plan.capped:
        for k in (2, 4, 8, 16):
            n_trials = max(ct // max(k, 1), 8)
            for t in range(n_trials):
                idxs = []
                used = set()
                for _ in range(k):
                    i = rng.randint(0, ct)
                    while i in used:
                        i = rng.randint(0, ct)
                    used.add(i)
                    idxs.append(i)
                idxs.sort()
                # Force at least one trial that hits omission region
                if parameter_set == "ML-KEM-1024" and t == 0:
                    idxs = sorted(
                        list(range(1536, 1536 + min(k, 32)))[:k]
                        if k <= 32
                        else list(range(1536, 1568))[:k]
                    )
                for xorv, lab in ((0x01, f"scat_k{k}_xor01"), (0xFF, f"scat_k{k}_xorff")):
                    if not add(
                        Mutation("G2_multi_byte", "scattered", idxs, xor_mask=xorv, label=lab)
                    ):
                        break
                if plan.capped:
                    break
            if plan.capped:
                break

    # Whole-block inversions
    if not plan.capped:
        for blen in (16, 32, 64):
            for off in range(0, ct - blen + 1, blen):
                idxs = list(range(off, off + blen))
                if not add(
                    Mutation(
                        "G2_multi_byte",
                        "block_invert",
                        idxs,
                        xor_mask=None,
                        invert_blocks=True,
                        label=f"inv_b{blen}",
                    )
                ):
                    break
            if plan.capped:
                break

    plan.coverage = {
        "indices_targeted": sorted(indices_touched),
        "n_indices": len(indices_touched),
        "fraction": len(indices_touched) / ct,
        "mutation_events": count,
        "full_index_coverage": len(indices_touched) == ct,
        "reaches_known_avx2_omission": bool(
            set(indices_touched) & set(KNOWN_PREFIX_AVX2_OMISSION.get(parameter_set, []))
        ),
        "capped": plan.capped,
    }
    return plan


def plan_g3(parameter_set: str, seed: int, cap: int = MUTATION_CAP) -> ClassPlan:
    ct = PARAM_CT[parameter_set]
    plan = ClassPlan("G3_alignment", parameter_set, ct, seed)
    count = 0
    indices_touched: set[int] = set()

    def add_idx(idx: int, lab: str) -> bool:
        nonlocal count
        if idx < 0 or idx >= ct:
            return True
        for xorv, xlab in ((0x01, "xor01"), (0xFF, "xorff")):
            if count >= cap:
                plan.capped = True
                return False
            plan.mutations.append(
                Mutation("G3_alignment", "align", [idx], xor_mask=xorv, label=f"{lab}_{xlab}")
            )
            indices_touched.add(idx)
            count += 1
        return True

    for align in (16, 32, 64):
        for off in range(0, ct, align):
            if not add_idx(off, f"bound_{align}"):
                break
            last = min(off + align - 1, ct - 1)
            if not add_idx(last, f"last_{align}"):
                break
        if plan.capped:
            break
        # final partial block start
        rem = ct % align
        if rem and not plan.capped:
            partial_start = ct - rem
            if not add_idx(partial_start, f"partial_start_{align}"):
                break
            if not add_idx(ct - 1, f"partial_end_{align}"):
                break

    plan.coverage = {
        "indices_targeted": sorted(indices_touched),
        "n_indices": len(indices_touched),
        "fraction": len(indices_touched) / ct,
        "mutation_events": count,
        "full_index_coverage": False,  # G3 is boundary-scoped by design
        "boundary_scoped": True,
        "reaches_known_avx2_omission": bool(
            set(indices_touched) & set(KNOWN_PREFIX_AVX2_OMISSION.get(parameter_set, []))
        ),
        "capped": plan.capped,
    }
    return plan


def plan_g4(parameter_set: str, seed: int) -> ClassPlan:
    """Malformed lengths — recorded separately; never silent-set contributors."""
    ct = PARAM_CT[parameter_set]
    plan = ClassPlan("G4_malformed_length", parameter_set, ct, seed)
    for delta, lab in (
        (-1, "trunc_1"),
        (-16, "trunc_16"),
        (-32, "trunc_32"),
        (1, "ext_1"),
        (16, "ext_16"),
        (32, "ext_32"),
    ):
        plan.mutations.append(
            Mutation(
                "G4_malformed_length",
                "length",
                [],
                xor_mask=delta,  # reuse field as signed length delta
                label=lab,
            )
        )
    plan.coverage = {
        "length_deltas": [-1, -16, -32, 1, 16, 32],
        "mutation_events": len(plan.mutations),
        "note": "API-only; excluded from silent sets and disagreement counts",
    }
    return plan


def apply_mutation(ct: bytes, mut: Mutation) -> bytes:
    buf = bytearray(ct)
    if mut.kind == "length":
        raise ValueError("G4 length mutations are not content mutations")
    if mut.invert_blocks:
        for i in mut.indices:
            buf[i] ^= 0xFF
    else:
        assert mut.xor_mask is not None
        for i in mut.indices:
            buf[i] ^= mut.xor_mask
    return bytes(buf)


def plans_for_seed(seed: int) -> dict[str, dict[str, ClassPlan]]:
    out: dict[str, dict[str, ClassPlan]] = {}
    for ps in PARAM_CT:
        out[ps] = {
            "G1": plan_g1(ps, seed),
            "G2": plan_g2(ps, seed),
            "G3": plan_g3(ps, seed),
            "G4": plan_g4(ps, seed),
        }
    return out


def coverage_report(all_plans: dict[int, dict[str, dict[str, ClassPlan]]]) -> dict[str, Any]:
    """Aggregate coverage accounting across seeds."""
    report: dict[str, Any] = {"seeds": SEEDS, "classes": {}}
    for cls in ("G1", "G2", "G3", "G4"):
        report["classes"][cls] = {}
        for ps in PARAM_CT:
            fracs = []
            capped = False
            reaches = False
            events = 0
            for seed in SEEDS:
                cov = all_plans[seed][ps][cls].coverage
                fracs.append(cov.get("fraction", 0.0))
                capped = capped or bool(cov.get("capped") or all_plans[seed][ps][cls].capped)
                reaches = reaches or bool(cov.get("reaches_known_avx2_omission"))
                events += int(cov.get("mutation_events", 0))
            report["classes"][cls][ps] = {
                "mean_index_fraction": sum(fracs) / len(fracs) if fracs else 0.0,
                "min_index_fraction": min(fracs) if fracs else 0.0,
                "capped_any_seed": capped,
                "coverage_status": "partial" if capped else "complete_for_class_definition",
                "reaches_known_avx2_omission": reaches,
                "total_mutation_events_all_seeds": events,
            }
    return report


def serialize_plan(plan: ClassPlan) -> dict[str, Any]:
    return {
        "class_id": plan.class_id,
        "parameter_set": plan.parameter_set,
        "ct_len": plan.ct_len,
        "seed": plan.seed,
        "capped": plan.capped,
        "coverage": plan.coverage,
        "n_mutations": len(plan.mutations),
        "mutations": [asdict(m) for m in plan.mutations],
    }


def write_plans(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_plans = {s: plans_for_seed(s) for s in SEEDS}
    for seed, by_ps in all_plans.items():
        for ps, by_cls in by_ps.items():
            for cls, plan in by_cls.items():
                path = out_dir / f"plan_seed{seed}_{ps}_{cls}.json"
                path.write_text(json.dumps(serialize_plan(plan), indent=2) + "\n")
    report = coverage_report(all_plans)
    (out_dir / "coverage_preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    import sys

    d = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/exp-mlkem-003/logs/plans")
    r = write_plans(d)
    print(json.dumps(r, indent=2))
