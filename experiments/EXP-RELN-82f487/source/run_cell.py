"""Main orchestrator for one (rung, curve, base_seed, training_seed, sigma)
cell across the five-arm panel, both model classes (gnn, trees) and both
feature regimes (F0, F1). Produces per-arm metrics.json-shaped dicts plus
the shared fixtures/leak-audit/handoff artifacts for one run directory.

This is NOT one of the required_artifacts source files by name, but is the
script that calls them all; it is committed under source/ alongside them so
the run is exactly reproducible from command.txt.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from harness.toycurve import EllipticCurve
import curve_gen
import enumerate_counts as ec
import features as feat
import graph_build as gb
import model_gnn
import model_trees
import scoring
import nulls
import certificates
import leak_audit
import grammar_reference as gram
import lookup_labels
import cost_instrumentation as costi

SEEDS = dict(
    curve_seeds=[101, 102, 103],
    base_seeds=[201, 202, 203],
    training_seeds=[301, 302, 303],
    split_seed=401,
    node_shuffle_seed=501,
    node_shuffle_seed_variant=502,
    selection_null_seed=601,
    label_permutation_seed=701,
    bootstrap_seed=901,
)

ARMS = ["E_x_interval", "E_random_matched", "ZN_interval", "ZN_random", "E_log_interval_canary"]


def build_arm(arm, curve, curve_rec, points_by_x, B_eff, base_seed):
    N = curve_rec["N"]
    if arm == "E_x_interval":
        D, meta = ec.build_base_E_x_interval(curve, points_by_x, base_seed, B_eff)
        group = "E"
    elif arm == "E_random_matched":
        D, meta = ec.build_base_E_random_matched(curve, points_by_x, base_seed, B_eff)
        group = "E"
    elif arm == "ZN_interval":
        D, meta = ec.build_base_ZN_interval(N, B_eff)
        group = "ZN"
    elif arm == "ZN_random":
        D, meta = ec.build_base_ZN_random(N, base_seed, B_eff)
        group = "ZN"
    elif arm == "E_log_interval_canary":
        P = tuple(curve_rec["P"])
        D, meta = ec.build_base_E_log_canary(curve, P, B_eff)
        group = "E"
    else:
        raise ValueError(arm)
    return D, meta, group


def key_of(pt):
    return pt if pt is not None else "O"


def run_arm_cell(arm, curve, curve_rec, points_by_x, all_points, B_eff, base_seed,
                  training_seed, sigma, regimes=("F0", "F1"), classes=("gnn", "trees"),
                  epochs=100, n_boot=1000, n_null_draws=1000, run_gnn_lr_grid=(1e-3, 3e-3),
                  fixed_gnn_lr=None, fixed_tree_params=None, node_shuffle_seed=None,
                  do_permutation_null=True, log=print):
    t_arm_start = time.time()
    N = curve_rec["N"]
    p = curve_rec.get("p")
    node_shuffle_seed = node_shuffle_seed if node_shuffle_seed is not None else SEEDS["node_shuffle_seed"]

    D, base_meta, group = build_arm(arm, curve, curve_rec, points_by_x, B_eff, base_seed)
    B = len(D)

    if group == "E":
        counts, triples, total, expected = ec.enumerate_with_triples_E(curve, D)
        universe = [pt for pt in all_points if pt not in set(D)]
    else:
        counts, triples, total, expected = ec.enumerate_with_triples_ZN(N, D)
        d_set = set(D)
        universe = [r for r in range(N) if r not in d_set]

    total_check = {"total": total, "expected": expected, "deviation": total - expected}
    if total_check["deviation"] != 0:
        return {"arm": arm, "status": "halted_fixture_failure", "total_check": total_check}

    n_universe = len(universe)
    keys = [key_of(u) if group == "E" else u for u in universe]
    count_arr = np.array([counts.get(k, 0) for k in keys], dtype=np.float64)

    # deterministic split by target (split_seed), independent of node-shuffle
    rng_split = np.random.default_rng(SEEDS["split_seed"] + (0 if group == "E" else 1) + hash(arm) % 1000)
    perm = rng_split.permutation(n_universe)
    n_train = int(0.5 * n_universe)
    n_val = int(0.1 * n_universe)
    train_idx = perm[:n_train]
    val_idx = perm[n_train:n_train + n_val]
    heldout_idx = perm[n_train + n_val:]

    # node order shuffle (independent seed) applied only to how the TRAINING
    # graph's node arrays are laid out -- feature rows are keyed by index so
    # a determinism check on this seed alone (never a feature) is done via
    # re-permuting train_idx's internal order.
    rng_shuffle = np.random.default_rng(node_shuffle_seed)
    train_idx_shuffled = train_idx[rng_shuffle.permutation(len(train_idx))]

    # translates (fixed by base_seed, shared across regimes/classes)
    if group == "E":
        translate_pts = feat.fixed_translate_points_E(curve, base_seed, k=8)
        base_summary = feat.base_summary_E(curve, D)
    else:
        translate_res = feat.fixed_translate_residues_ZN(N, base_seed, k=8)
        base_summary = feat.base_summary_ZN(N, D)

    def compute_feats(idx_list, regime):
        sub = [universe[i] for i in idx_list]
        if group == "E":
            return feat.compute_features_E(curve, sub, translate_pts, regime, base_summary)
        else:
            return feat.compute_features_ZN(N, sub, translate_res, regime, base_summary)

    result = {"arm": arm, "group": group, "B": B, "B_eff": B_eff, "N": N,
              "n_universe": n_universe, "n_train": len(train_idx), "n_val": len(val_idx),
              "n_heldout": len(heldout_idx), "total_check": total_check, "base_meta": base_meta,
              "regimes": {}}

    if group == "E":
        base_feat_source = list(D)
    else:
        base_feat_source = list(D)

    # base node features for the GNN (project D's own coordinates)
    if group == "E":
        base_feat_full = feat.compute_features_E(curve, D, translate_pts, "F0")
    else:
        base_feat_full = feat.compute_features_ZN(N, D, translate_res, "F0")

    heldout_counts = count_arr[heldout_idx]
    sigma_one_mask = scoring.top_sigma_mask(heldout_counts, 1.0)
    sigma_one_metrics = scoring.lift_metrics(heldout_counts, sigma_one_mask)

    xs_heldout = None
    if group == "E":
        xs_heldout = [universe[i][0] for i in heldout_idx]
    else:
        xs_heldout = [universe[i] for i in heldout_idx]
    grammar_check = gram.reproduction_check(xs_heldout, (p if group == "E" else N), heldout_counts, sigma)

    inv6 = None
    if arm == "E_x_interval" and group == "E":
        pairs, keys_sorted = lookup_labels.build_pair_sum_table_E(curve, D)
        indicator = []
        for i in heldout_idx:
            R = universe[i]
            hit = False
            for Pi in translate_pts:
                if Pi is None:
                    continue
                Rm = curve.add(R, curve.negate(Pi))
                found, _ = lookup_labels.lookup_decomposition_E(curve, D, pairs, keys_sorted, Rm)
                if found:
                    hit = True
                    break
            indicator.append(hit)
        indicator = np.array(indicator, dtype=bool)
        m = scoring.lift_metrics(heldout_counts, indicator)
        inv6 = {"lambda": m["lambda"], "n_slice": m["n_slice"], "threshold": 1.4}

    for regime in regimes:
        train_feat_all = compute_feats(train_idx_shuffled, regime)
        val_feat_all = compute_feats(val_idx, regime)
        heldout_feat_all = compute_feats(heldout_idx, regime)
        base_feat_regime = base_feat_full if regime == "F0" else np.concatenate(
            [base_feat_full, np.tile(base_summary, (len(D), 1))], axis=1)

        y_train = np.log1p(count_arr[train_idx_shuffled])
        y_val = np.log1p(count_arr[val_idx])

        train_keys = [keys[i] for i in train_idx_shuffled]
        graph = gb.build_training_graph(B, train_keys, triples)

        regime_result = {"n_relations": graph["n_relations"]}

        model_predictions = {}
        for cls in classes:
            t0 = time.time()
            if cls == "gnn":
                if fixed_gnn_lr is not None:
                    model, info = model_gnn.train_gnn(base_feat_regime, train_feat_all, graph, y_train,
                                                        val_feat_all, y_val, lr=fixed_gnn_lr, epochs=epochs,
                                                        seed=training_seed)
                    params = {"learning_rate": fixed_gnn_lr}
                else:
                    model, params, info = model_gnn.select_and_train_gnn(
                        base_feat_regime, train_feat_all, graph, y_train, val_feat_all, y_val,
                        lr_grid=run_gnn_lr_grid, epochs=epochs, seed=training_seed)
                pred_heldout = model.predict_with_graph(base_feat_regime, train_feat_all, graph, heldout_feat_all)
                model_card = {"architecture": "gnn_K3_width64", "params": params, "train_info": info}
            else:
                if fixed_tree_params is not None:
                    m = model_trees.GradientBoostedTrees(max_depth=fixed_tree_params["max_depth"],
                                                          n_trees=fixed_tree_params["n_trees_used"],
                                                          learning_rate=fixed_tree_params["learning_rate"])
                    m.fit(train_feat_all, np.log1p(count_arr[train_idx_shuffled]), val_feat_all, y_val)
                    model = m
                    params = fixed_tree_params
                    val_mse = float(np.mean((m.predict(val_feat_all) - y_val) ** 2))
                else:
                    model, params, val_mse = model_trees.select_and_fit(
                        train_feat_all, y_train, val_feat_all, y_val,
                        grid_depth=(4, 6), grid_trees=(200,))
                pred_heldout = model.predict(heldout_feat_all)
                model_card = {"architecture": "gbt_custom_cart", "params": params, "val_mse": val_mse}
            t_train = time.time() - t0
            model_card["train_wall_seconds"] = t_train

            slice_mask = scoring.top_sigma_mask(pred_heldout, sigma)
            m_metrics = scoring.lift_metrics(heldout_counts, slice_mask)
            boot = scoring.bootstrap_interval(heldout_counts, slice_mask, n_boot=n_boot,
                                               seed=SEEDS["bootstrap_seed"])
            model_predictions[cls] = {"pred_heldout": pred_heldout, "slice_mask": slice_mask,
                                       "metrics": m_metrics, "bootstrap": boot, "model_card": model_card,
                                       "model": model, "params": params}

        # selection null + analytic null (shared across classes for this arm/regime/sigma)
        sel_null = nulls.selection_null(heldout_counts, sigma, n_draws=n_null_draws,
                                         seed=SEEDS["selection_null_seed"])
        ana_band = nulls.analytic_band(heldout_counts, sigma, len(heldout_idx))
        agreement = nulls.band_agreement(sel_null["rho_band"], ana_band)

        # label-permutation null (training_seed 301 only per spec; caller
        # controls whether this cell is the training_seed==301 cell)
        perm_results = {}
        if do_permutation_null:
            perm_idx = nulls.permutation_index(len(train_idx_shuffled), SEEDS["label_permutation_seed"])
            y_train_perm = y_train[perm_idx]
            for cls in classes:
                if cls == "gnn":
                    params = model_predictions[cls]["params"]
                    model_p, info_p = model_gnn.train_gnn(base_feat_regime, train_feat_all, graph, y_train_perm,
                                                            val_feat_all, y_val,
                                                            lr=params.get("learning_rate", 1e-3),
                                                            epochs=epochs, seed=training_seed)
                    pred_p = model_p.predict_with_graph(base_feat_regime, train_feat_all, graph, heldout_feat_all)
                else:
                    params = model_predictions[cls]["params"]
                    m = model_trees.GradientBoostedTrees(max_depth=params["max_depth"],
                                                          n_trees=params.get("n_trees_used", params.get("n_trees_requested", 100)),
                                                          learning_rate=params.get("learning_rate", 0.05))
                    m.fit(train_feat_all, y_train_perm, val_feat_all, y_val)
                    pred_p = m.predict(heldout_feat_all)
                mask_p = scoring.top_sigma_mask(pred_p, sigma)
                mp = scoring.lift_metrics(heldout_counts, mask_p)
                inside_lambda = sel_null["lambda_band"][0] <= mp["lambda"] <= sel_null["lambda_band"][1]
                inside_rho = sel_null["rho_band"][0] <= mp["rho"] <= sel_null["rho_band"][1]
                perm_results[cls] = {"metrics": mp, "inside_band": bool(inside_lambda and inside_rho)}

        excess = {}
        for cls in classes:
            mm = model_predictions[cls]["metrics"]
            excess[cls] = {
                "rho_excess": mm["rho"] - sel_null["rho_median"],
                "lambda_excess": mm["lambda"] - sel_null["lambda_median"],
                "rho_inside_band": bool(sel_null["rho_band"][0] <= mm["rho"] <= sel_null["rho_band"][1]),
                "lambda_inside_band": bool(sel_null["lambda_band"][0] <= mm["lambda"] <= sel_null["lambda_band"][1]),
            }
        gnn_minus_trees = None
        if "gnn" in classes and "trees" in classes:
            gnn_minus_trees = {
                "rho_excess_diff": excess["gnn"]["rho_excess"] - excess["trees"]["rho_excess"],
                "lambda_excess_diff": excess["gnn"]["lambda_excess"] - excess["trees"]["lambda_excess"],
            }

        regime_result.update({
            "sigma": sigma,
            "selection_null": sel_null,
            "analytic_null": ana_band,
            "null_agreement": agreement,
            "model_metrics": {cls: {"metrics": model_predictions[cls]["metrics"],
                                     "bootstrap": model_predictions[cls]["bootstrap"],
                                     "model_card": model_predictions[cls]["model_card"]}
                               for cls in classes},
            "excess": excess,
            "gnn_minus_trees": gnn_minus_trees,
            "label_permutation_null": perm_results,
        })
        result["regimes"][regime] = regime_result

    result["sigma_one_fixture"] = sigma_one_metrics
    result["grammar_reproduction_fixture"] = grammar_check
    result["inv6_theorem_arm"] = inv6
    result["wall_seconds"] = time.time() - t_arm_start
    return result
