"""Freeze public field/curve inputs before any distribution measurement."""
import hashlib
import json
import random
from pathlib import Path

import numpy as np

from measure import identity, naf_weight, seed_for


def primes_in_bits(bits):
    limit = 1 << bits
    sieve = np.ones(limit, dtype=np.bool_)
    sieve[:2] = False
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    return np.flatnonzero(sieve[(1 << (bits - 1)):]).astype(np.int64) + (1 << (bits - 1))


def toy_inputs(config):
    tasks, populations = [], []
    for bits in config["toy_bits"]:
        primes = [int(p) for p in primes_in_bits(bits)]
        sparse = [p for p in primes if naf_weight(p) <= config["maximum_naf_weight"]]
        rng = random.Random(seed_for(config["seed"], "prime-selection", bits))
        structured = rng.sample(sparse, config["blocks_per_stratum"])
        used = set(structured)
        populations.append({"bits": bits, "all_primes": len(primes), "sparse_primes": len(sparse)})
        for block, p in enumerate(structured):
            # Exact integer +/-5% endpoints, intersected with the bit interval.
            lower = max(1 << (bits - 1), (95 * p + 99) // 100)
            upper = min((1 << bits) - 1, 105 * p // 100)
            eligible = [q for q in primes if lower <= q <= upper and q not in used]
            matching = [q for q in eligible if q % config["toy_control_residue_modulus"] == p % config["toy_control_residue_modulus"]]
            c = rng.sample(matching, config["residue_controls_per_block"])
            used.update(c)
            r = rng.sample([q for q in eligible if q not in used], config["random_controls_per_block"])
            used.update(r)
            fields = [("S", 0, p)] + [("R", i, q) for i, q in enumerate(r)] + [("C", i, q) for i, q in enumerate(c)]
            for arm, control, q in fields:
                field_id = f"toy{bits}-B{block:03d}-{arm}{control}"
                models = []
                draw = random.Random(seed_for(config["seed"], field_id, "models"))
                while len(models) < config["models_per_toy_field"]:
                    a, b = draw.randrange(q), draw.randrange(q)
                    if (4 * a**3 + 27 * b**2) % q:
                        models.append({"index": len(models), "p": q, "A": a, "B": b, "curve_id": identity(q, a, b)})
                tasks.append({"id": field_id, "case": f"toy{bits}", "kind": "census", "arm": arm,
                              "block": block, "p": q, "bits": bits, "naf_weight": naf_weight(q), "models": models})
        if len(used) != config["blocks_per_stratum"] * (1 + config["random_controls_per_block"] + config["residue_controls_per_block"]):
            raise ValueError("repeated toy modulus")
    return tasks, populations


def nist_inputs(repo, config):
    source = repo / config["source_nist_run"]
    tasks, sources = [], {}
    for path in sorted((source / "curves").glob("*/curves.json")):
        payload = path.read_bytes()
        sources[str(path.relative_to(repo))] = hashlib.sha256(payload).hexdigest()
        data = json.loads(payload)
        modulus = data["modulus"]
        models = []
        for row in data["curves"]:
            p, a, b = row["p"], row["A"], row["B"]
            if p != modulus["p"] or not (4 * a**3 + 27 * b**2) % p:
                raise ValueError("invalid imported curve")
            models.append({k: row[k] for k in ("index", "p", "A", "B", "N")})
            models[-1]["curve_id"] = identity(p, a, b)
        if len(models) != (512 if modulus["arm"] == "S" else 4):
            raise ValueError("unexpected source model count")
        tasks.append({"id": modulus["id"], "case": modulus["case"], "kind": "probes",
                      "arm": modulus["arm"], "block": None, "p": modulus["p"], "bits": modulus["bits"],
                      "naf_weight": naf_weight(modulus["p"]), "models": models})
    for case, expected in (("P-192", (1 << 192) - (1 << 64) - 1), ("P-224", (1 << 224) - (1 << 96) + 1)):
        selected = [t for t in tasks if t["case"] == case]
        if len(selected) != 289 or sum(len(t["models"]) for t in selected) != 1664:
            raise ValueError("unexpected NIST pool")
        if next(t["p"] for t in selected if t["arm"] == "S") != expected:
            raise ValueError("incorrect NIST prime")
    return tasks, sources


def write_preparation(repo, config, run):
    toys, populations = toy_inputs(config)
    nist, sources = nist_inputs(repo, config)
    tasks = toys + nist
    random.Random(seed_for(config["seed"], "task-order")).shuffle(tasks)
    result = {"schema": 1, "config": config, "prime_populations": populations,
              "source_nist_sha256": sources, "tasks": tasks,
              "fields": len(tasks), "curves": sum(len(t["models"]) for t in tasks)}
    path = run / "inputs.json"
    with path.open("x") as f:
        json.dump(result, f, sort_keys=True)
        f.write("\n")
    return result
