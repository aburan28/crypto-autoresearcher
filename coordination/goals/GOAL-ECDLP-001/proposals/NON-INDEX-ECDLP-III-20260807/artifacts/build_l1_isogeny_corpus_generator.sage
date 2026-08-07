from random import Random
from math import ceil, sqrt
from pathlib import Path
from hashlib import sha256
import json
import yaml
from sage.all import EllipticCurve, GF

OUT_ROOT = Path('/Volumes/SSD990/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807')
SCRIPT_PATH = Path('coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807/artifacts/build_l1_isogeny_corpus_generator.sage')

FAMILIES = [
    {
        "family_id": "FAM-101-A",
        "seed": 0x20260807,
        "family_name": "small-2to3-volcano",
        "p": 101,
        "a": 80,
        "b": 90,
    },
    {
        "family_id": "FAM-113-B",
        "seed": 0x20260808,
        "family_name": "small-2-3-5-branch",
        "p": 113,
        "a": 89,
        "b": 57,
    },
    {
        "family_id": "FAM-167-C",
        "seed": 0x20260809,
        "family_name": "small-2-3-mixed",
        "p": 167,
        "a": 116,
        "b": 105,
    },
]


def to_int(v):
    return int(v)


def curve_invariants(p, a, b):
    F = GF(p)
    E = EllipticCurve(F, [0, 0, 0, a, b])
    order = to_int(E.order())
    factors = sorted((to_int(pr), to_int(e)) for pr, e in E.order().factor())
    prime_factors = sorted({p for p, _ in factors})
    return {
        "field_modulus": p,
        "a4": to_int(a),
        "a6": to_int(b),
        "j_invariant": to_int(E.j_invariant()),
        "discriminant": to_int((4 * a ** 3 + 27 * b ** 2) % p),
        "group_order": order,
        "group_largest_prime_factor": max(prime_factors),
        "group_structure": [to_int(x) for x in E.abelian_group().invariants()],
        "trace_of_frobenius": to_int(p + 1 - order),
        "automorphism_count": int(len(E.automorphisms())),
        "order_factors": factors,
        "is_supersingular": bool(E.is_supersingular()),
        "two_torsion_rank": int(E.two_torsion_rank()),
    }


def get_isogenies_by_degree(E):
    result = {}
    for deg in (2, 3, 5):
        isogs = list(E.isogenies_prime_degree(deg))
        isogs.sort(
            key=lambda iso: (
                to_int(iso.codomain().j_invariant()),
                to_int(iso.codomain().a4()),
                to_int(iso.codomain().a6()),
            )
        )
        result[deg] = isogs
    return result


def isomorphic_transform(p, a, b, u):
    inv_u4 = pow(to_int(u), -4, p)
    inv_u6 = pow(to_int(u), -6, p)
    return (to_int(a * inv_u4 % p), to_int(b * inv_u6 % p))


def find_cyclic_match(p, target_order, seed):
    rng = Random(seed)
    F = GF(p)
    for attempt in range(1, 5000):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        E = EllipticCurve(F, [0, 0, 0, a, b])
        if to_int(E.order()) == target_order:
            return {
                "attempt": attempt,
                "a4": to_int(a),
                "a6": to_int(b),
                "seed": seed,
                "j_invariant": to_int(E.j_invariant()),
                "order": to_int(E.order()),
            }
    raise RuntimeError(f"no random cyclic match found for p={p}, order={target_order}")


def pollard_baseline(q):
    q = max(2, to_int(q))
    expected = ceil(1.253314137 * sqrt(q))
    return {
        "effective_subgroup_order": q,
        "expected_rho_group_ops": expected,
        "expected_rho_walltime_ms": round(expected * 0.0035, 3),
        "expected_memory_bytes": q * 8,
        "success_prob_per_1e6_steps": float(1 - (1 - 1.0 / q) ** 1000000),
    }


def register_variant(variant_map, variant_list, family_id, curve, counter, chain_id=None):
    key = (
        to_int(curve.base_ring().order()),
        to_int(curve.a4()),
        to_int(curve.a6()),
    )
    if key in variant_map:
        return variant_map[key]["variant_id"]

    vid = f"{family_id}-V{counter[0]:02d}"
    counter[0] += 1

    rec = {
        "variant_id": vid,
        "chain_id": chain_id,
        "curve_role": "variant",
        **curve_invariants(to_int(curve.base_ring().order()), to_int(curve.a4()), to_int(curve.a6())),
    }
    if chain_id is not None:
        rec["is_in_chain"] = True
    variant_map[key] = rec
    variant_list.append(rec)
    return vid

manifest = {
    "artifact_type": "isogeny_class_manifest",
    "objective": "L1 corpus of small isogenous curve families and baseline controls",
    "max_isogeny_degree": 5,
    "families": [],
}

seed_register = {
    "artifact_type": "seed_register",
    "seed_streams": [],
}

baseline = {
    "artifact_type": "control_baseline_report",
    "profiles": [],
}

for spec in FAMILIES:
    p = to_int(spec["p"])
    a = to_int(spec["a"])
    b = to_int(spec["b"])
    seed = to_int(spec["seed"])

    F = GF(p)
    base_curve = EllipticCurve(F, [0, 0, 0, a, b])
    if to_int((4 * a ** 3 + 27 * b ** 2) % p) == 0:
        raise RuntimeError(f"family {spec['family_id']} has singular base")

    neighbors = get_isogenies_by_degree(base_curve)
    start_degs = [deg for deg in (2, 3, 5) if neighbors.get(deg)]
    if len(start_degs) < 2:
        raise RuntimeError(f"family {spec['family_id']} lacks at least two starter isogeny degrees")

    variant_map = {}
    variant_list = []
    variant_counter = [0]

    base_record = {
        "variant_id": f"{spec['family_id']}-BASE",
        "curve_role": "base",
        "chain_id": None,
        "seed": seed,
        **curve_invariants(p, a, b),
    }
    variant_map[(p, a, b)] = base_record
    variant_list.append(base_record)

    chain_records = []
    chosen_starters = start_degs[:2]

    for chain_idx, deg1 in enumerate(chosen_starters):
        iso1 = neighbors[deg1][0]
        mid = iso1.codomain()
        p_mid = to_int(mid.base_ring().order())

        mid_neighbors = get_isogenies_by_degree(mid)
        deg2 = None
        for d in (2, 3, 5):
            if mid_neighbors.get(d):
                deg2 = d
                break
        if deg2 is None:
            raise RuntimeError(f"family {spec['family_id']} chain {chain_idx} missing second step")

        iso2 = mid_neighbors[deg2][0]
        end_curve = iso2.codomain()

        chain_id = f"{spec['family_id']}-C{chain_idx+1:02d}"
        mid_vid = register_variant(variant_map, variant_list, spec["family_id"], mid, variant_counter, chain_id)
        end_vid = register_variant(variant_map, variant_list, spec["family_id"], end_curve, variant_counter, chain_id)

        chain_records.append(
            {
                "chain_id": chain_id,
                "seeded_from": base_record["variant_id"],
                "degree_sequence": [deg1, deg2],
                "max_degree": max(deg1, deg2),
                "path": [
                    {
                        "from_variant": base_record["variant_id"],
                        "to_variant": mid_vid,
                        "degree": deg1,
                        "kernel_label": f"seeded-{spec['family_id']}-L{chain_idx+1}-01",
                    },
                    {
                        "from_variant": mid_vid,
                        "to_variant": end_vid,
                        "degree": deg2,
                        "kernel_label": f"seeded-{spec['family_id']}-L{chain_idx+1}-02",
                    },
                ],
            }
        )

    # isomorphic-coordinate control
    iso_u = (seed % (p - 3)) + 2
    a_iso, b_iso = isomorphic_transform(p, a, b, iso_u)
    if to_int((4 * a_iso ** 3 + 27 * b_iso ** 2) % p) == 0:
        for u in range(2, p):
            a_iso, b_iso = isomorphic_transform(p, a, b, u)
            if to_int((4 * a_iso ** 3 + 27 * b_iso ** 2) % p) != 0:
                iso_u = u
                break

    # random cyclic matched-order control
    cyclic_seed = seed ^ 0xA5A5A5
    cyclic_raw = find_cyclic_match(p, to_int(base_curve.order()), cyclic_seed)
    cyclic_control = {
        "control_id": f"{spec['family_id']}-CTRL-CYCLIC",
        "control_type": "random_cyclic_matched_order",
        "source_seed": cyclic_seed,
        "attempt": cyclic_raw["attempt"],
        "order_match": True,
        **curve_invariants(p, cyclic_raw["a4"], cyclic_raw["a6"]),
    }

    iso_control = {
        "control_id": f"{spec['family_id']}-CTRL-ISO",
        "control_type": "isomorphic_coordinate",
        "source_seed": seed,
        "transform_u": iso_u,
        "expected_j_invariant_match": True,
        "expected_order_match": True,
        **curve_invariants(p, a_iso, b_iso),
    }

    baseline["profiles"].extend(
        [
            {
                "family_id": spec["family_id"],
                "variant_id": variant["variant_id"],
                "seed": seed,
                **pollard_baseline(variant["group_largest_prime_factor"]),
            }
            for variant in variant_list
        ]
    )

    family_record = {
        "family_id": spec["family_id"],
        "family_name": spec["family_name"],
        "field_modulus": p,
        "seed": seed,
        "field_bits": p.bit_length(),
        "curves": variant_list,
        "isogeny_chains": chain_records,
        "controls": {
            "isomorphic_coordinate": iso_control,
            "random_cyclic_matched_order": cyclic_control,
        },
    }

    manifest["families"].append(family_record)

    seed_register["seed_streams"].extend(
        [
            {
                "label": f"{spec['family_id']}-family",
                "seed": seed,
                "scope": "curve and chain selection",
            },
            {
                "label": f"{spec['family_id']}-cyclic-control",
                "seed": cyclic_seed,
                "scope": "random cyclic matched-order curve search",
            },
        ]
    )


def stable_file_sha(path):
    h = sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

manifest["reproducibility"] = {
    "generated_at_utc": "2026-08-06T00:00:00Z",
    "runtime": "SageMath",
    "max_isogeny_degree": 5,
    "manifest_path": "coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807/artifacts/isogeny_class_manifest.yaml",
    "seed_register_path": "coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807/artifacts/seed_register.yaml",
    "control_baseline_path": "coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807/artifacts/control_baseline_report.json",
    "generator_script_sha256": stable_file_sha(SCRIPT_PATH),
}

seed_register.update(
    {
        "artifact_signature": sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "purpose": "L1 corpus generation and controls",
    }
)

OUT_ROOT.joinpath("artifacts").mkdir(parents=True, exist_ok=True)
out_manifest = OUT_ROOT / "artifacts/isogeny_class_manifest.yaml"
out_seed = OUT_ROOT / "artifacts/seed_register.yaml"
out_control = OUT_ROOT / "artifacts/control_baseline_report.json"

with out_manifest.open('w', encoding='utf-8') as handle:
    yaml.safe_dump(manifest, handle, sort_keys=False)
with out_seed.open('w', encoding='utf-8') as handle:
    yaml.safe_dump(seed_register, handle, sort_keys=False)
with out_control.open('w', encoding='utf-8') as handle:
    json.dump(baseline, handle, indent=2, sort_keys=True)

print(out_manifest)
print(out_seed)
print(out_control)
