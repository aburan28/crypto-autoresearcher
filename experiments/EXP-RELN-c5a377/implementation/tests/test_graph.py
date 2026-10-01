import math
import random

import networkx as nx
import pytest

import lpgraph


def G(n, edges):
    return {"n": n, "edges": list(edges)}


def test_cycle_rank_small_cases():
    assert lpgraph.metrics(G(1, []), 5)["cycle_rank"] == 0
    tri = lpgraph.metrics(G(3, [(0, 1), (1, 2), (2, 0)]), 5)
    assert tri["cycle_rank"] == 1 and tri["components_with_cycle"] == 1
    loop = lpgraph.metrics(G(2, [(1, 1)]), 5)
    assert loop["cycle_rank"] == 1 and loop["components"] == 2 and loop["self_loops"] == 1
    par = lpgraph.metrics(G(2, [(0, 1), (0, 1), (0, 1)]), 5)
    assert par["cycle_rank"] == 2


def test_build_root_convention():
    rels = [{"kind": "lp1", "rel": [3, 1, 20, -1]}, {"kind": "lp2", "rel": [20, 1, 31, 1]},
            {"kind": "full", "rel": [1, 1, 2, 1]}, {"kind": "lp2", "rel": [31, 1, 31, 1]}]
    g = lpgraph.build(rels, B=10)
    assert g["n"] == 3 and g["lp_x"] == [20, 31]
    assert g["edges"] == [(1, 0), (1, 2), (2, 2)]


def test_deltas():
    d = lpgraph.deltas(125, 250, 5)
    assert d["delta_proof"] == pytest.approx(2.0)
    assert d["delta_ratio"] == pytest.approx(math.log(0.5) / math.log(5))
    assert lpgraph.deltas(0, 10, 5)["delta_proof"] is None
    assert lpgraph.deltas(10, 10, 1)["delta_proof"] is None


@pytest.mark.parametrize("seed", range(12))
def test_gf2_identity_random_multigraphs(seed):
    rnd = random.Random(seed)
    n = rnd.randint(1, 30)
    edges = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(rnd.randint(0, 60))]
    m = lpgraph.metrics(G(n, edges), 7)
    assert m["cycle_rank_identity_ok"]
    assert m["cycle_rank"] == len(edges) - n + nx.number_connected_components(_nxmulti(n, edges))


def _nxmulti(n, edges):
    g = nx.MultiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return g


@pytest.mark.parametrize("seed", range(10))
def test_horton_matches_networkx_minimum_weight(seed):
    rnd = random.Random(100 + seed)
    n = rnd.randint(4, 18)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = rnd.sample(pairs, min(len(pairs), rnd.randint(n, 3 * n)))
    hb = lpgraph.horton_mcb(G(n, edges))
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    ref = nx.minimum_cycle_basis(g)
    assert hb["size_identity_ok"] and hb["all_even_degree"]
    assert hb["basis_size"] == len(ref)
    assert hb["total_weight"] == sum(len(c) for c in ref)


def test_horton_multigraph_loops_and_parallels():
    hb = lpgraph.horton_mcb(G(3, [(0, 1), (0, 1), (1, 2), (2, 2), (0, 2)]))
    assert hb["basis_size"] == 3
    assert hb["length_histogram"] == {"1": 1, "2": 1, "3": 1}
