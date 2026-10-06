"""Run the toy: kernel check + lopsided batch decomposition + regime map."""
from __future__ import annotations

import json
import time

import batch_lopsided as bl
import regime_table as rt
import strassen_kernel as sk


def main():
    t0 = time.perf_counter()
    out = {"assumption": "arXiv:2610.06783 Theorems 1/5 + Corollary 26 hold; "
                         "oracle seam behind count_chunk is exact hash/scan today"}
    out["strassen_kernel"] = sk.check()
    instances = []
    for cfg in [dict(mod=10007, f_size=200, n_targets=100, n_planted=50,
                     seed=20261006, chunk_size=25),
                dict(mod=10007, f_size=200, n_targets=100, n_planted=50,
                     seed=77, chunk_size=10),
                dict(mod=2003, f_size=80, n_targets=60, n_planted=30,
                     seed=5, chunk_size=20)]:
        f, index, targets = bl.make_instance(**{k: v for k, v in cfg.items()
                                                 if k in ("mod", "f_size", "n_targets",
                                                          "n_planted", "seed")})
        base, base_ops = bl.baseline_relations(f, index, targets, cfg["mod"])
        lh, lh_ops, g = bl.lopsided_relations(f, index, targets, cfg["mod"],
                                              chunk_size=cfg["chunk_size"], mode="hash")
        ls, ls_ops, _ = bl.lopsided_relations(f, index, targets, cfg["mod"],
                                              chunk_size=cfg["chunk_size"], mode="scan")
        assert bl.relation_sets_equal(base, lh), "hash-seam discrepancy!"
        assert bl.relation_sets_equal(base, ls), "scan-seam discrepancy!"
        n_rel = sum(len(v) for v in base.values())
        instances.append({"cfg": cfg, "chunks": g, "relations": n_rel,
                          "baseline_probes": base_ops, "lopsided_hash_probes": lh_ops,
                          "lopsided_scan_comparisons": ls_ops,
                          "hash_overhead_factor": round(lh_ops / base_ops, 3),
                          "exact_agreement": True})
    out["instances"] = instances
    out["regime_map"] = rt.regime_rows()
    out["elapsed_s"] = round(time.perf_counter() - t0, 3)
    with open("results.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: (v if k != "regime_map" else f"{len(v)} rows")
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
