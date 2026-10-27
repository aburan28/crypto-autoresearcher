"""Public source-point bindings for the rootless path-transfer phase."""
from __future__ import annotations

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_graph_solve_input as solve_input
import prepare_graph_input as graph
import verify_prepared_graph as verify

STUDY = Path(__file__).resolve().parents[1]
WALKS = {
    "P29": STUDY / "walk-p29-2048-attempt2.jsonl",
    "P37": STUDY / "walk-p37-256.jsonl",
}


class SourcePointBindings(unittest.TestCase):
    def test_public_source_pair_has_same_scalar_at_saved_vertices(self):
        scalar = 123456789
        for stratum, walk in WALKS.items():
            with self.subTest(stratum=stratum):
                header, source_model, source_curve, source_generator = graph.load_vertex(walk, 0)
                with walk.open(encoding="utf-8") as stream:
                    self.assertEqual(verify.source_generator_from_header(json.loads(next(stream))),
                                     list(source_generator))
                endpoint_index = 24 if stratum == "P37" else 8
                _, endpoint_model, endpoint_curve, endpoint_generator = graph.load_vertex(
                    walk, endpoint_index)
                transfer = solve_input.transfer_points(walk, endpoint_index, scalar)
                model = transfer["source_model"]
                source_g, source_q = transfer["source_generator"], transfer["source_Q"]
                self.assertEqual(model, source_model)
                self.assertEqual(source_g, source_generator)
                self.assertEqual(header["stratum"], stratum)
                self.assertNotEqual(source_q, (0, 0))
                self.assertEqual(
                    source_q,
                    graph.multiply(scalar, source_generator, source_curve),
                )
                edge = next(json.loads(line) for line in walk.read_text().splitlines()
                            if json.loads(line).get("kind") == "edge" and
                            json.loads(line).get("index") == endpoint_index)
                self.assertEqual(edge["image_generator"], list(endpoint_generator))
                self.assertEqual(edge["image_smoke_target"], list(
                    graph.multiply(scalar, endpoint_generator, endpoint_curve)))
                self.assertEqual(transfer["generator"], endpoint_generator)
                self.assertEqual(transfer["Q"], graph.multiply(
                    scalar, endpoint_generator, endpoint_curve))
                self.assertEqual(endpoint_model["j"], edge["canonical_codomain"]["j"])


if __name__ == "__main__":
    unittest.main()
