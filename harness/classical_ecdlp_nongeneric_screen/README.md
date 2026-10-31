# Fixed public constructor screen implementation

This package is software for EXP-ECDLP-c45dd8 / H-ECDLP-704867 / RUN-ECDLP-a11661, under GOAL-ECDLP-e70832. It has not executed the scientific screen. The accompanying plan is an unfrozen design input, not launch authority. The Coordinator owns source commits, final protocol, admission, checkpoint and scientific interpretation.

`curve.py` supplies counted affine arithmetic. `constructor.py` computes the normalized Miller coefficient by a binary line-coefficient recurrence and evaluates the fixed coordinate circuits. It has no scalar table, truth oracle, coefficient fitting or orbit enumeration. `compute.py` enumerates public curve coordinates, streams all outcomes and refuses source/protocol mismatch or output overwrite. `verify.py` imports neither candidate module and uses its own affine arithmetic, linear scalar orbit and full-group slope-sum primitive. Scalar truth exists only in the verifier and software tests.

The exact crossed case plan is 40 fixed integer templates × 12 coordinate-enumerated bases × 13 targets including O × 10 coordinate-scaling units = 62,400 candidate rows. These scaling views are repeated presentations of one mandatory fixture, not independent statistical samples. Control rows are:

| Fixed arm IDs | Rows |
| --- | ---: |
| `fiber:a0:b0`, `fiber:a1:b0`, `fiber:a2:b0`, `fiber:a-2:b0`, `fiber:a-3:b0` | 7,800 |
| `invalid_anchor:a-1:b1` | 1,560 |
| `wrong_root:anchored_power_root` | 1,560 |
| `aa_replay:a0:b1`, paired with `candidate:a0:b1` | 1,560 |

Total: 74,880 rows in 5,760 setup groups. Identity follows a valid setup as BIT0. A zero/invalid setup remains UNDEFINED even at identity; a zero query numerator is UNDEFINED. The anchored field-root control uses sigma=y(P)*f(x)^((p+1)/4)/f(x(P))^((p+1)/4), giving -f^3 at the seed base. The validator-only truth-half control constructs its own O(r) table, checks pulses and verifies conditional scalar recovery. The valid-circuit anchor H(P)=0 is also a known outcome through the candidate evaluation path; neither control implies all-target ordering.

The candidate setup is O(log r) group/field work, query O(log r+log p), with constant field-element state plus O(log r) scalar bits. Conditional recovery uses r.bit_length()+1 fresh predicate evaluations, target doublings and an actual final public scalar multiplication. It is not a fallback solver. With field multiplication M(b), inversion I(b), and b=ceil(log2 p), the direct affine evaluator costs O(log r I(b)+(log r+b)M(b)) bit operations up to the chosen arithmetic implementation. Tiny-input trial-division certification and O(p²) public-coordinate enumeration are charged separately. This package does not propose them as efficient general input certification. Full family search charges all 40 candidates. Setup counters repeated in raw rows are provenance; `setup_charged` marks the one setup charge per group.

After all 13 target outcomes in a group, compute checks the exact two-pulse identity using public mP, -P and point addition. This all-target validation gate costs O(r) work and uses a retained bit dictionary only to decide whether recovery is attempted. It consults no scalar truth and passes no bit dictionary to the constructor. A failed gate records an explicit no-attempt reason. A passing gate triggers one newly charged public-input preparation, then actual recovery of all 13 targets: five fresh Prepared.evaluate calls per target, fresh public doublings and final scalar verification. Recovery traces retain every public query, fresh answer and operation count. Fresh setup, evaluator, reduction and gate costs are separate from grid costs; the linear gate remains part of the campaign's complete accounting. No asymptotic end-to-end gain follows from this finite validation workflow.

Counter semantics are source-instrumented operations, not machine timings. Inversion calls retain Euclidean iteration counts separately. Squaring and multiplication are disjoint count categories. Membership checks, exceptional branches, identity/vertical group calls and duplicated work remain charged. Public model/point scaling uses raw modular integer arithmetic outside these counters; Python container/control work, JSON, hashing, I/O and runtime/source checks are also unmetered harness work. The operation vector is not a complete machine-cost measurement. The independent verifier checks arithmetic and source-counter shape, totals and A/A equality; it does not independently replay each candidate counter. Python allocation peaks and machine bit-operation counts have not been measured. Static source state bounds are not measured memory bounds. The gate retains 13 outcomes; a passing recovery group retains up to 65 fresh query traces as output, not constructor advice.

Software validation, which does not launch the scientific grid:

```sh
python3 -m unittest -v test_constructor.py test_verify.py
python3 compute.py --protocol protocol.plan.json --plan-only
```

The actual transport stages exactly six production modules: curve.py, constructor.py, compute.py, verify.py, controller.py and driver.py. Its source manifest maps these six basenames to hashes and records the exact source revision C. The Coordinator first commits those modules, then the manifest, then a standalone frozen screen plan that binds the manifest hash, then the official frozen experiment.protocol/v1 record. The scientific CLI is:

```sh
python3 compute.py --protocol /work/stage/compute-plan.json \
  --source-manifest /work/source/source-manifest.json \
  --provider-context /work/stage/provider-context.json --output-dir /work/result/raw
python3 verify.py /work/result/raw/records.jsonl --recoveries /work/result/raw/recovery.jsonl \
  --protocol /work/stage/compute-plan.json --output /work/result/verification.json
```

These are interface examples, not executed commands. Actual CLI requires frozen plan status, exact source hashes, a 40-hex committed revision, UID/GID1000 with no supplementary groups, and source/manifest/protocol read-only to that worker. A provider-context plan probe enforces those runtime facts before enumerating public inputs; a plain local plan-only probe records them without enforcing. The transport owns image validation and an external 3,600-second infrastructure watchdog. Compute records context bytes/hash but does not independently validate image provenance. No environment variables or credential values are collected.

Successful compute writes records.jsonl, recovery.jsonl (one record per group), compute-summary.json and completion.json. Exit0 means the fixed computation completed, regardless of candidate ordering. Verifier exit0 means retained arithmetic/integrity and controls pass, independently of whether any template has ordering. A configuration error returns2; other faults are nonzero. A caught failure writes failure.json and retains partial records; an external termination may leave partial records without a completion marker. Such interruption is operational censoring, not mathematical failure. No resume or automatic retry is implemented. Raw data must be archived through the authorized artifact route rather than committed as large Git data.

The verifier retains every undefined reason, per-base mismatch count/first counterexample, full two-pulse residual vector and symmetry/covariance checks. It independently validates actual fresh recovery queries/answers and scalar equations using its own charged O(r) primitive oracle. Its additional retained-bit reduction diagnostic is explicitly validator-only, with zero fresh evaluations and five bit reads; it is never described as an executed candidate solver. A finite-template pass requires every target of every base/view and actual verified fresh recovery. A failure resolves only that fixed template. No coefficient tuning, larger cohort, global novelty, asymptotic improvement, universal circuit obstruction or research-status transition follows from this package.

Prior-work and assumption receipt: ../proposal.md, ../source-manifest.json and ../primary-source-retrieval.json. The binary primitive is the existing normalized Miller-coefficient/additive cocycle proposal; no literal analytic zeta assumption is used. The x-sensitive decoder family remains untested. The beta-zero fiber obstruction and anchored wrong-root counterexample were derived before this implementation and serve as known-false controls.
