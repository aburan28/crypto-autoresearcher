#!/usr/bin/env python3
"""Read-only, deterministic B5/B6 rederivation from published n=83 rows.

No producer analyzer or result JSON is imported. The input files and every
referenced stdout receipt must match the pinned published-main Git blobs.
"""

import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import subprocess


PIN = "1b4ef77ab8397b736aa74b7b97d163714cb3ede8"
STACK = "experiments/koblitz-n83-stacked-20261016"
COUNT = "experiments/koblitz-n83-opcounts-20261023"
SOURCES = {
    f"{STACK}/protocol.json": "094f59931521bdaf4138d8e81fc165652500d771b555864be44a8408cddd1cc7",
    f"{STACK}/run_github_38862448935/panel/runs.jsonl": "f68af5e3a97da724ea1e8c28cbc8c9f6baf8ae1981aae04cd2eaef108a748d82",
    f"{STACK}/run_github_38862448935/panel/result.json": "fc22111b3d59fc6d5963930f735c29cf14a4d10715228593bbd2c899d125fd9d",
    f"{COUNT}/PROTOCOL.md": "ed0136dc43b30bb1c6fb5248dc8354bdd2b70008006e1a58faeb8cee44b475b7",
    f"{COUNT}/run_github_39882571652/panel/runs.jsonl": "13829d0d020666b50f8345c1ca9176f792025f671045d060940ef1a374b6723d",
    f"{COUNT}/run_github_39882571652/analysis_v2/counts-v2.json": "981c664ca715acb3c5d77586534466357bf854e64d17eb3288402a28cb1de464",
    f"{COUNT}/run_github_39882571652/analysis_v2/opcounts_result-v2.json": "688e56b2cb161945a782c583569c9da0fd0f2975c940f2d64447f7a9c15fe89c",
}
STACK_PANEL = f"{STACK}/run_github_38862448935/panel"
COUNT_PANEL = f"{COUNT}/run_github_39882571652/panel"
IC_GROUP = ("ec_add", "ec_double")
IC_NATIVE = (
    "canonicalizations", "descent_mulmods", "ec_add_trivial",
    "ec_frobenius", "ec_lift_x", "fold_rotations", "frobenius_x",
    "la_inversions", "la_mulmods", "relation_lifts",
    "root_filter_inserts", "root_filter_queries", "root_index_inserts",
    "root_index_probes", "s3_root_solves", "s3_root_solves_library",
)
RHO_NATIVE = (
    "canonicalizations", "failed_collisions", "partition_hashes",
    "table_inserts", "table_queries",
)
NBOOT = 10000


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_id(data):
    body = b"blob " + str(len(data)).encode() + b"\0" + data
    return hashlib.sha1(body).hexdigest()


def mean(xs):
    return sum(xs) / len(xs)


def ci95(xs):
    xs = sorted(xs)
    return [xs[249], xs[9749]]


def tree_blobs(repo):
    paths = [f"{STACK_PANEL}/runs/", f"{COUNT_PANEL}/runs/"]
    raw = git(repo, "ls-tree", "-r", "-z", PIN, "--", *paths)
    out = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        mode, kind, oid = metadata.split(b" ")
        assert kind == b"blob" and mode in (b"100644", b"100755")
        out[name.decode()] = oid.decode()
    return out


def load_panel(repo, panel, blobs):
    rows = [json.loads(line) for line in (repo / panel / "runs.jsonl").read_text().splitlines()]
    decoded = defaultdict(dict)
    blob_checks = 0
    for row in rows:
        assert row["status"] == "valid"
        assert row["returncode"] == 0
        assert not row["timed_out"]
        assert row["fields"]["verified"] == "1"
        rel = f"{panel}/{row['stdout_file']}"
        assert rel in blobs, f"not in published tree: {rel}"
        data = (repo / rel).read_bytes()
        assert git_blob_id(data) == blobs[rel], f"published blob mismatch: {rel}"
        blob_checks += 1
        raw = next(line[8:] for line in data.splitlines() if line.startswith(b"raw_b64="))
        record = json.loads(base64.b64decode(raw, validate=True))
        assert record["arm"] == row["arm"] and record["panel"] == row["point_id"]
        assert str(record["fields"]["recovered_scalar"]) == row["fields"]["recovered_scalar"]
        decoded[row["arm"]][row["point_id"]] = record
    assert blob_checks == len(rows)
    return rows, decoded, blob_checks


def rank_details(decoded, arm):
    out = []
    for point in ("s000", "s001"):
        item = decoded[arm][point]
        summary = next(r for r in item["records"] if r.get("kind") == "compact_orbit_dlp_summary")
        attempts = summary["rank_attempt_ns"]
        assert len(attempts) == 600
        nonattempt_ms = item["fields"]["rank_stage_ms"] - sum(attempts) / 1e6
        out.append((attempts, nonattempt_ms))
    return out


def sample_rank(rng, details):
    return mean([
        residual + sum(ns[rng.randrange(len(ns))] for _ in ns) / 1e6
        for ns, residual in details
    ])


def rederive_stack(protocol, rows, decoded):
    assert protocol["design"]["cold_points"] == 20
    assert [b["rank_seed"] for b in protocol["design"]["rank_blocks"]] == [101, 102]
    assert len(rows) == 192
    assert Counter(r["status"] for r in rows) == {"valid": 192}
    assert not any(r["status"] == "skipped_time_guard" for r in rows)
    points = [f"s{i:03d}" for i in range(20)]
    for point in points:
        scalars = {
            str(item["fields"]["recovered_scalar"])
            for arm in decoded
            if point in decoded[arm]
            for item in [decoded[arm][point]]
        }
        assert len(scalars) == 1, f"scalar mismatch at {point}"
        targets = {
            r["fields"]["target_sha256"]
            for r in rows if r["point_id"] == point
        }
        assert len(targets) == 1, f"target mismatch at {point}"

    rank = {
        arm: [decoded[arm][p]["fields"]["rank_stage_ms"] for p in ("s000", "s001")]
        for arm in ("kP", "kS", "kSaa")
    }
    cold = {
        arm: [decoded[arm][p]["fields"]["cold_ms"] for p in points]
        for arm in ("cP", "cS", "cSaa", "cSX")
    }
    online = {
        arm: [decoded[arm][p]["fields"]["online_ms"] for p in points]
        for arm in ("cP", "cS", "rT")
    }
    rho_cold = [
        decoded["rT"][p]["fields"]["setup_ms"] + decoded["rT"][p]["fields"]["online_ms"]
        for p in points
    ]
    rho_steps = [int(decoded["rT"][p]["fields"]["ops"]) for p in points]
    rho_step_ms = sum(online["rT"]) / sum(rho_steps)
    e2e_p = mean(rank["kP"]) + mean(cold["cP"])
    e2e_s = mean(rank["kS"]) + mean(cold["cS"])
    aa = (mean(rank["kS"]) + mean(cold["cS"])) / (
        mean(rank["kSaa"]) + mean(cold["cSaa"])
    )
    aa_cold = mean(cold["cS"]) / mean(cold["cSaa"])
    planted = mean(cold["cSX"]) / mean(cold["cS"])
    assert 0.97 <= aa <= 1.03 and 0.97 <= aa_cold <= 1.03

    ranks = {arm: rank_details(decoded, arm) for arm in rank}
    rng = random.Random(90304)
    primary_draws, aa_draws, plant_draws = [], [], []
    for _ in range(NBOOT):
        ids = [rng.randrange(20) for _ in points]
        mc = {arm: mean([values[i] for i in ids]) for arm, values in cold.items()}
        mr = {arm: sample_rank(rng, details) for arm, details in ranks.items()}
        primary_draws.append((mr["kP"] + mc["cP"]) / (mr["kS"] + mc["cS"]))
        aa_draws.append((mr["kS"] + mc["cS"]) / (mr["kSaa"] + mc["cSaa"]))
        plant_draws.append(mc["cSX"] / mc["cS"])

    rng = random.Random(991)
    online_false_win_draws = []
    for _ in range(NBOOT):
        ids = [rng.randrange(20) for _ in points]
        online_false_win_draws.append(
            sum(online["cP"][i] for i in ids) / sum(online["cS"][i] for i in ids)
        )

    rng = random.Random(90305)
    rho_gap_draws, rho_online_gap_draws = [], []
    for _ in range(NBOOT):
        ids = [rng.randrange(20) for _ in points]
        sampled_rank = sample_rank(rng, ranks["kS"])
        sampled_cold = mean([cold["cS"][i] for i in ids])
        sampled_rho = mean([rho_cold[i] for i in ids])
        rho_gap_draws.append((sampled_rank + sampled_cold) / sampled_rho)
        rho_online_gap_draws.append(
            sum(online["cS"][i] for i in ids) /
            sum(online["rT"][i] for i in ids)
        )

    rank_probes, rank_roots = {}, {}
    for arm in ("kP", "kS"):
        summaries = [
            next(r for r in decoded[arm][p]["records"] if r.get("kind") == "compact_orbit_dlp_summary")
            for p in ("s000", "s001")
        ]
        rank_probes[arm] = sum(s["rank_probes_total"] for s in summaries)
        rank_roots[arm] = sum(s["rank_root_calls_total"] for s in summaries)

    return {
        "row_count": len(rows),
        "valid_rows": sum(r["status"] == "valid" for r in rows),
        "contention_flags": [
            {"serial": r["serial"], "arm": r["arm"], "flags": r["contention_flags"]}
            for r in rows if r["contention_flags"]
        ],
        "cold_points": len(points),
        "rank_seeds": [101, 102],
        "bootstrap_scope": "10000 paired-point resamples and within-process sequential rank-attempt resamples; only two rank seeds and one host class",
        "bootstrap_seed_primary": 90304,
        "rank_mean_ms": {arm: mean(values) for arm, values in rank.items()},
        "cold_mean_ms": {arm: mean(values) for arm, values in cold.items()},
        "e2e_charged_ms": {"P": e2e_p, "S": e2e_s},
        "primary_ratio": e2e_p / e2e_s,
        "primary_ci95": ci95(primary_draws),
        "single_process_full_cold_ratio": {
            p: decoded["kP"][p]["fields"]["cold_ms"] /
            decoded["kS"][p]["fields"]["cold_ms"]
            for p in ("s000", "s001")
        },
        "single_process_pooled_ratio": (
            sum(decoded["kP"][p]["fields"]["cold_ms"] for p in ("s000", "s001")) /
            sum(decoded["kS"][p]["fields"]["cold_ms"] for p in ("s000", "s001"))
        ),
        "controls": {
            "aa_e2e_ratio": aa,
            "aa_e2e_ci95": ci95(aa_draws),
            "aa_cold_ratio": aa_cold,
            "planted_cold_ratio": planted,
            "planted_cold_ci95": ci95(plant_draws),
            "frozen_gate_pass": ci95(plant_draws)[0] > 1,
            "rank_positive_control_present": False,
        },
        "rank_counts": {
            "probes": rank_probes,
            "root_calls": rank_roots,
            "probe_P_over_S": rank_probes["kP"] / rank_probes["kS"],
            "root_P_over_S": rank_roots["kP"] / rank_roots["kS"],
        },
        "matched_rho": {
            "cold_mean_ms": mean(rho_cold),
            "online_mean_ms": mean(online["rT"]),
            "step_ms": rho_step_ms,
            "P_cold_over_rho_cold": e2e_p / mean(rho_cold),
            "S_cold_over_rho_cold": e2e_s / mean(rho_cold),
            "S_cold_gap_ci95": ci95(rho_gap_draws),
            "P_online_over_rho_online": mean(online["cP"]) / mean(online["rT"]),
            "S_online_over_rho_online": mean(online["cS"]) / mean(online["rT"]),
            "S_online_gap_ci95": ci95(rho_online_gap_draws),
            "S_cold_S": e2e_s / rho_step_ms / protocol["online"]["sqrt_r"],
            "P_cold_S": e2e_p / rho_step_ms / protocol["online"]["sqrt_r"],
        },
        "online": {
            "P_mean_ms": mean(online["cP"]),
            "S_mean_ms": mean(online["cS"]),
            "P_over_S": mean(online["cP"]) / mean(online["cS"]),
            "false_online_win_control_ci95": ci95(online_false_win_draws),
            "false_online_win_control_max": max(online_false_win_draws),
        },
        "factor_base_sensitivity": {
            "status": "conditional_on_same_nonnegative_uncharged_X_for_both_arms",
            "shared_base_path": protocol["online"]["base"],
            "shared_base_hash": protocol["online"]["base_hash"],
            "ratios_by_shared_X_ms": {
                str(x): (e2e_p + x) / (e2e_s + x)
                for x in (0, 427.524, 1000, 10000, 60000)
            },
            "arm_specific_construction_costs_measured": False,
        },
    }


def priced_counts(rows, decoded, original):
    assert len(rows) == 62
    assert Counter(r["status"] for r in rows) == {"valid": 62}
    for r in rows:
        arm, point = r["arm"], r["point_id"]
        if arm in ("cS", "cP", "rT"):
            assert r["fields"]["recovered_scalar"] == str(original[arm][point]["fields"]["recovered_scalar"])
        elif arm in ("kS", "kP"):
            assert r["fields"]["recovered_scalar"] == str(original[arm][point]["fields"]["recovered_scalar"])

    points = [f"s{i:03d}" for i in range(20)]
    counts = {}
    for arm, rank_arm, cold_arm in (("S", "kS", "cS"), ("P", "kP", "cP")):
        rank = next(
            r for r in decoded[rank_arm]["s000"]["records"]
            if r.get("kind") == "compact_orbit_dlp_summary"
        )["op_counts"]["phases"]["rank_stage"]
        counts[arm] = []
        for point in points:
            cold = next(
                r for r in decoded[cold_arm][point]["records"]
                if r.get("kind") == "compact_orbit_dlp_summary"
            )["op_counts"]["end_to_end"]
            total = Counter(rank) + Counter(cold)
            counts[arm].append({
                "group": sum(total[k] for k in IC_GROUP),
                "native": sum(total[k] for k in IC_NATIVE),
                "rho_scalar_muls": 0,
            })
    counts["rT"] = []
    for point in points:
        charge = decoded["rT"][point]["records"][0]["outcome"]["charges_setup_and_solve"]
        counts["rT"].append({
            "group": charge["group_additions"],
            "native": sum(charge[k] for k in RHO_NATIVE),
            "rho_scalar_muls": charge["scalar_multiplications"],
        })

    means = {
        arm: {
            key: mean([point[key] for point in values])
            for key in ("group", "native", "rho_scalar_muls")
        }
        for arm, values in counts.items()
    }
    weights = {}
    rng = random.Random(90306)
    for weight in (0.0, 0.1, 1.0):
        key = f"{weight:g}"
        draws = {bound: {"S_over_rT": [], "P_over_rT": [], "S_over_P": []} for bound in (0, 104)}
        for _ in range(NBOOT):
            ids = [rng.randrange(20) for _ in points]
            for bound in (0, 104):
                priced = {
                    arm: mean([
                        values[i]["group"] + weight * values[i]["native"] +
                        bound * values[i]["rho_scalar_muls"]
                        for i in ids
                    ])
                    for arm, values in counts.items()
                }
                draws[bound]["S_over_rT"].append(priced["S"] / priced["rT"])
                draws[bound]["P_over_rT"].append(priced["P"] / priced["rT"])
                draws[bound]["S_over_P"].append(priced["S"] / priced["P"])
        weights[key] = {}
        for bound in (0, 104):
            prices = {
                arm: m["group"] + weight * m["native"] + bound * m["rho_scalar_muls"]
                for arm, m in means.items()
            }
            weights[key][str(bound)] = {
                "cost_gae": prices,
                "S_over_P": prices["S"] / prices["P"],
                "S_over_P_ci95": ci95(draws[bound]["S_over_P"]),
                "S_over_rT": prices["S"] / prices["rT"],
                "S_over_rT_ci95": ci95(draws[bound]["S_over_rT"]),
                "P_over_rT": prices["P"] / prices["rT"],
                "P_over_rT_ci95": ci95(draws[bound]["P_over_rT"]),
            }
    return {
        "row_count": len(rows),
        "valid_rows": sum(r["status"] == "valid" for r in rows),
        "bootstrap_scope": "10000 paired-point resamples over the 20 archived points; K1 rank block is fixed; 0 and 104 GAE per undecomposed rho scalar multiplication",
        "bootstrap_seed": 90306,
        "mean_counts": means,
        "weights": weights,
        "S_cheaper_than_P_all_weights_and_rho_bounds": all(
            weights[w][b]["S_over_P_ci95"][1] < 1
            for w in ("0", "0.1", "1") for b in ("0", "104")
        ),
        "S_vs_rT_rank_unresolved_across_weights": (
            weights["0"]["0"]["S_over_rT_ci95"][1] < 1 and
            weights["0.1"]["0"]["S_over_rT_ci95"][0] > 1 and
            weights["1"]["0"]["S_over_rT_ci95"][0] > 1
        ),
        "counter_instrumentation_semantics_independently_audited": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("/home/ec2-user/cryptanalysis-sheriff-main-20261024"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    assert git(repo, "rev-parse", "HEAD").decode().strip() == PIN
    assert git(repo, "rev-parse", "origin/main").decode().strip() == PIN
    assert git(repo, "rev-parse", "--show-object-format").decode().strip() == "sha1"
    blobs = tree_blobs(repo)
    source_hashes = {}
    for rel, expected in SOURCES.items():
        data = (repo / rel).read_bytes()
        actual = sha256(data)
        assert actual == expected, f"SHA-256 mismatch: {rel}"
        # A source receipt must also be the blob in the published commit.
        oid = git(repo, "rev-parse", f"{PIN}:{rel}").decode().strip()
        assert git_blob_id(data) == oid, f"published blob mismatch: {rel}"
        source_hashes[rel] = actual
    protocol = json.loads((repo / f"{STACK}/protocol.json").read_text())
    stack_rows, stack_decoded, stack_stdout_count = load_panel(repo, STACK_PANEL, blobs)
    count_rows, count_decoded, count_stdout_count = load_panel(repo, COUNT_PANEL, blobs)
    report = {
        "schema": "sheriff.b5b6-rederive/v1",
        "published_main_commit": PIN,
        "source_sha256": source_hashes,
        "published_stdout_blobs_verified": {
            "stack": stack_stdout_count,
            "counted": count_stdout_count,
        },
        "stack": rederive_stack(protocol, stack_rows, stack_decoded),
        "section_5a": priced_counts(count_rows, count_decoded, stack_decoded),
        "scope": {
            "scientific_trials_run": 0,
            "producer_files_edited": False,
            "statistical_generalization": "original wall bootstrap covers 20 points and within-process attempts of only two rank seeds on one host class; counted band fixes K1 rank",
            "factor_base_cost": "excluded from original charged metric; sensitivity only if same nonnegative construction cost X applies to P and S",
        },
    }
    data = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"output={args.out}")
    print(f"sha256={sha256(data)}")
    print(f"primary={report['stack']['primary_ratio']:.9f}")
    print(f"stack_stdout_verified={stack_stdout_count}")
    print(f"counted_stdout_verified={count_stdout_count}")


if __name__ == "__main__":
    main()
