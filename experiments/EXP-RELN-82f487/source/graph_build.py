"""Bipartite {base, relation, target} incidence graph on TRAINING targets
only (specification.yaml's gnn_architecture). A held-out or validation
target has NO incident relation node (its edges are its labels, which are
never revealed outside the training split), so it enters the model only
through its own coordinate features plus the pooled global context g_theta
computed from the trained graph -- this is what the split_by_target /
INV-2''-adjacent design in H-RELN-10ad6b's mechanism section calls out
explicitly.
"""
from __future__ import annotations

import numpy as np


def build_training_graph(D_size: int, train_target_keys, counts_with_triples: dict):
    """counts_with_triples: dict target_key -> list of (i,j,k) base-index
    triples (its certified decompositions). Only entries whose key is in
    train_target_keys contribute relation nodes.

    Returns dict with:
      idx1, idx2, idx3: int arrays (R,) of base indices per relation
      relation_target_idx: int array (R,) of training-target-node index
      train_key_to_node: dict target_key -> node index (0..T-1)
    """
    train_key_to_node = {k: i for i, k in enumerate(train_target_keys)}
    idx1, idx2, idx3, rel_target = [], [], [], []
    for key in train_target_keys:
        triples = counts_with_triples.get(key, [])
        node = train_key_to_node[key]
        for (i, j, k) in triples:
            idx1.append(i)
            idx2.append(j)
            idx3.append(k)
            rel_target.append(node)
    return {
        "idx1": np.array(idx1, dtype=np.int64),
        "idx2": np.array(idx2, dtype=np.int64),
        "idx3": np.array(idx3, dtype=np.int64),
        "relation_target_idx": np.array(rel_target, dtype=np.int64),
        "train_key_to_node": train_key_to_node,
        "n_relations": len(idx1),
        "n_train_targets": len(train_target_keys),
        "n_base": D_size,
    }
