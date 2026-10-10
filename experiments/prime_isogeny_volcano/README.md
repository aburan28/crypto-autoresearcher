# Prime-degree isogeny volcano discovery — initial implementation

Run: `sage experiments/prime_isogeny_volcano/search.sage --p 101 --a 1 --b 0 --primes 2 3 5 7 --out /tmp/isogenies.jsonl`

This first bounded implementation records ordinary-curve Frobenius invariants, tests explicit Sage prime-degree isogeny construction, verifies map degree, separability and point count, and emits one JSONL record per degree including failures and timing.

**Important limitations:** Endomorphism conductor of E and E' is not yet computed; therefore no edge is labeled horizontal/ascending/descending and no conductor-gap record is claimed. The Frobenius conductor is an upper bound on possible endomorphism conductors, not the actual conductor. A prime dividing it indicates a possible vertical transition, not proof. Large-degree construction may be infeasible and Sage APIs may differ across versions. The code has not been executed in a Sage environment in this PR.

Next milestones: (1) Sage-version smoke tests and known volcano fixtures; (2) certified endomorphism orders and edge direction; (3) CM-guided candidate generation; (4) Ray sharding and durable checkpoints; (5) independent verification and cost-normalized benchmarks; (6) literature review before any record claim. Keep compact representations distinct from expanded rational maps, and explicitly account for output size.


## Distributed runner

Local: `python3 experiments/prime_isogeny_volcano/distributed.py --manifest experiments/prime_isogeny_volcano/example_manifest.jsonl --output-dir /tmp/volcano-shards --backend local --workers 4`

Ray: `python3 experiments/prime_isogeny_volcano/distributed.py --manifest experiments/prime_isogeny_volcano/example_manifest.jsonl --output-dir /shared/volcano-shards --backend ray --ray-address auto`

Install Ray in the Python interpreter running the orchestrator, and install Sage on every Ray worker. The repository and Sage script must be at the same path on each worker. Ray output-dir must be a shared filesystem visible to every worker. Avoid duplicate manifest rows because they would race on the same output path. One process per shard writes an atomic JSONL result and a receipt; successful jobs are skipped on rerun. Run orchestration unit tests with `python3 -m unittest experiments/prime_isogeny_volcano/test_distributed.py`. No Ray cluster has been launched or verified here.
