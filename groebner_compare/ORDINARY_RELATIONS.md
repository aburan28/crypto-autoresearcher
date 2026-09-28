# Ordinary-query relation measurement integration

The executable mathematical campaign lives in [cryptanalysis PR #161](https://github.com/aburan28/cryptanalysis/pull/161), under `experiments/pdp-scaling/ordinary_campaign.py`.
Its frozen protocol is `experiments/pdp-scaling/ORDINARY_PROTOCOL.md`.
That runner needs its own repository-local finite-field and polynomial modules;
this repository does not silently import a mutable external checkout.

This repository vendors the same `relation_metrics.py` and tests:

- `RelationRank` receives independently verified coefficient vectors over a
  separately certified prime modulus. It distinguishes independent, dependent
  and duplicate rows, including rows equivalent under scalar multiplication.
- `comparison_gate` requires identical workload/base hashes and timing boundary,
  five independent paired seeds, eight new rows per cell, completed independent
  replay, and a conservative paired 2× cost threshold. Missing or zero-yield
  cells return insufficient evidence. The bootstrap resamples whole seeds.
- Callers must verify original point sums, subgroup membership, signed row
  construction and RHS. Solver-reported or Macaulay rank is never input evidence.

The campaign compares exact direct lookup, native XOR SAT, three-bit assumption
branching, repository F5B and block F4. Original and projected base point sets,
query law, seeds, group order certificate, source digests and resource limits are
frozen. Full construction, failures, timeouts, verification and rank update costs
are charged. The n=83 probe uses ordinary synthetic subgroup queries without
planted decompositions; its deliberately enumerable base has extremely low
coverage. It is a feasibility observation, not a completed large-base evaluation.

Results are stage diagnostics. `candidate_id` and `full_dlp_speedup` stay null;
these utilities cannot promote a hypothesis, update an IC scoreboard, close a
goal, or claim a full-DLP speedup. Measurements and their immutable receipts
will be linked here after the canonical campaign finishes.

```sh
python -m unittest groebner_compare.test_relation_metrics -v
```
