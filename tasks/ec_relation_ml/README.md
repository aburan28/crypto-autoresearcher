# ML-assisted elliptic-curve relation workflow

This standalone engineering task bridges the existing
[polynomial ML selector](../polynomial_solver_ml/README.md) to elliptic-curve
point decomposition. ML chooses a Gröbner configuration; exact finite-field
arithmetic checks its output and measures independent relations and identifiable
target logs. It does not change hypothesis or experiment status in the ledger.

The initial CPU pilot uses small public synthetic curves. It exercises real
elliptic-curve equations, not a prime-family classifier. It is **software
validation**, not a test of cryptographic-size Solinas, P-192 or P-224 security.
Root extraction enumerates a tiny field grid and is unsuitable at large primes.
Summation polynomials are established prior art; no novelty is claimed.

From the repository root, with NumPy and SymPy installed:

```sh
python3 tasks/ec_relation_ml/run.py run --output /tmp/ec-ml-pilot
python3 tasks/ec_relation_ml/run.py verify /tmp/ec-ml-pilot
python3 -m unittest discover -s tasks/ec_relation_ml/tests -v
python3 tasks/ec_relation_ml/audit.py --repo . --output /tmp/ec-ml-data-audit.json
```

Outputs are write-once. Every completed action must match a separate exhaustive
root oracle and its exact point-relation evaluation. The verifier replays those
checks, fitting, selections and metrics. It does not independently authenticate
timings or provide independent scientific review. See [PROTOCOL.md](PROTOCOL.md)
for fixed scope, controls, costs and the path to a confirmatory campaign.

The pipeline retains public input systems, EC1 identities, raw child logs,
per-action observations, plain JSON models, an untouched-test evaluation,
positive/constant/shuffled-label controls, source and artifact hashes, and
environment details. Test fields are excluded from fitting and normalization.
No seed, scalar, point log, curve ID, split label, root or measured outcome is a
model feature. Feature acquisition and all label-collection costs are reported.

The exact evaluator also accepts relations produced by other generators: number
field lifts, low-height point searches or future learned proposals. Register
public seed and target points in `RelationSystem`, then insert an explicit
point equation. Equivalent points and negations share a variable; duplicate or
dependent equations do not inflate rank. Target recovery requires a uniquely
determined scalar that verifies against the original point.

The archived-data audit demonstrates why the earlier number-field rows cannot
simply be shuffled into ML training and test sets: they reuse the same curves,
targets and fields. Fresh scientific evaluation requires a separately frozen
contract and independent fields/curves/challenge entropy, with paired generic
attack controls. A faster algebra solver alone is not evidence of cheaper ECDLP.
