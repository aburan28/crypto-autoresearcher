# Prime-degree isogeny volcano discovery — initial implementation

Run: `sage experiments/prime_isogeny_volcano/search.sage --p 101 --a 1 --b 0 --primes 2 3 5 7 --out /tmp/isogenies.jsonl`

This first bounded implementation records ordinary-curve Frobenius invariants, tests explicit Sage prime-degree isogeny construction, verifies map degree, separability and point count, and emits one JSONL record per degree including failures and timing.

**Important limitations:** Endomorphism conductor of E and E' is not yet computed; therefore no edge is labeled horizontal/ascending/descending and no conductor-gap record is claimed. The Frobenius conductor is an upper bound on possible endomorphism conductors, not the actual conductor. A prime dividing it indicates a possible vertical transition, not proof. Large-degree construction may be infeasible and Sage APIs may differ across versions. The code has not been executed in a Sage environment in this PR.

Next milestones: (1) Sage-version smoke tests and known volcano fixtures; (2) certified endomorphism orders and edge direction; (3) CM-guided candidate generation; (4) Ray sharding and durable checkpoints; (5) independent verification and cost-normalized benchmarks; (6) literature review before any record claim. Keep compact representations distinct from expanded rational maps, and explicitly account for output size.
