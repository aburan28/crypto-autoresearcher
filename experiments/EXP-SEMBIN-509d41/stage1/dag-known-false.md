# DAG known-false control (Stage 1)

{
  "schema": "sembin.topology.dag_known_false.v1",
  "claim": "Merge-DAG counterexample outside the binary-tree class: identify two internal results (share an auxiliary) so the number of distinct auxiliaries is strictly less than t-2 while still covering t leaves.",
  "example_t": 4,
  "tree_auxiliaries": 2,
  "dag_distinct_auxiliaries": 1,
  "reading": "If a written (C1) counting argument still concludes auxiliaries=t-2 on this DAG, the argument proves too much and is O-ARTIFACT.",
  "control_passes_when": "Argument is scoped to full binary trees and refuses the DAG; documented here as known-false object.",
  "control_status": "SCOPED_REFUSAL_RECORDED"
}

(C1) is claimed only for full binary merge trees. This DAG is the proves-too-much null object.
