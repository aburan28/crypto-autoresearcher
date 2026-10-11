# Assessment obligations

## Identify and type

Record characteristic, extension degree, defining field polynomial, subfields,
equations, dimension/genus, field of definition, rational-point group, subgroup
order, representation, and canonical identities. State unknown facts explicitly.
Do not identify subgroups by ambient cardinality or equal field degree.

| Transformation | Required obligation |
|---|---|
| Coordinate isomorphism | Inverses, exceptional points, unchanged group |
| Elliptic isogeny | Homomorphism, kernel, rationality, subgroup restriction |
| Field extension | Embedding and identification of the original subgroup |
| Restriction of scalars | Dimension, rational-point correspondence, arithmetic cost |
| Curve cover | Induced pullback/pushforward on divisor classes |
| Jacobian correspondence | Polarization, explicit group maps, working-field descent |
| Characteristic-zero lift | Compatible specialization, beyond existence of a lift |
| Decomposition representation | Membership, signs/phases, and reconstruction |

## Separate evidence

Maintain six separate obligations: existence, executable construction,
correctness, subgroup preservation, measured advantage, and scaling support.
Neither template completeness nor passing random checks promotes an obligation
to a theorem. Distinguish geometric existence from working-field existence,
and unpolarized decomposition from principally polarized Jacobian identification.
Require equations and formulas before measuring transfer evaluation.

For an additive map Psi require Psi([k]P)=[k]Psi(P) and trivial intersection
of its kernel with the relevant subgroup. A certificate R o Psi=[m], with m
invertible modulo the subgroup order, can establish injectivity there. Identify
the proof, domain, field, exceptional points, and normalization. Audit the
induced group maps of a cover, rather than treating the curve map as a group
embedding. Random checks test implementation; they do not prove the identity.

## Quantify the proposed benefit

Name the benefit: arithmetic, symmetry, decomposition geometry, equation
solving, linear algebra, or reusable preprocessing. State predictions and
falsification conditions. Input sparsity is not elimination complexity.

Use C_new=C_construction+C_transfer+C_destination+C_recovery+C_verification.
Report memory, data, units, uncertainty, workload, parameters, and dependencies.
For N instances disclose setup/N only when the same setup is genuinely
reusable. Include failed searches, timeouts, duplicates, conversions,
verification, and rank updates. Report collection cost per new independent
verified relation without division by zero; also include downstream linear
algebra and recovery before claiming complete advantage. Keep modeled and
measured columns separate. Wall time alone is not a cryptographic complexity
bound; follow host bound/frontier rules. Smaller genus or base field alone does
not prove a lower complete cost.

## Control and challenge

Compare original representation, transported data, reselected data, isomorphic
coordinate changes, and a matched baseline receiving equal optimization effort.
Pair instances and fixed budgets. Include null and known-false controls,
independent classes/seeds, held-out instances, predefined stopping/invalidation
rules, and explicit parameter scope. Record CPU/NUMA pinning, processor, memory
type, OS, dependencies, and GPU where relevant. Infrastructure failures are
not mathematical evidence.

Challenge kernel collapse; extension-field results applied to prime fields;
orders confused with fast formulas; lost signs/Frobenius phases; natural fiber
factorization confused with every equivalent divisor representation; coverage
confused with independent rank; nonreusable setup amortization; and bounded
unsuccessful searches presented as nonexistence.

## Assess families and composed paths

For published construction families record applicability, required inputs,
field restrictions, construction/certificate interfaces, limitations, and the
declared exploration boundary. Automate metadata consistency and evidence
tracking; independently review new mathematical families and scaling arguments.
Do not add autonomous production-target exploitation to this skill.

Represent objects as nodes and correspondences as edges. Compose preservation
and recovery obligations, audit field compatibility at each junction, and
account for setup, conversion, evaluation, memory, and recovery. Do not assume
separate edge restrictions compose or costs are independent. Deduplicate
isomorphic representations and reverse paths as mathematical discoveries.

Return an obligation table with exact evidence, scope, unknowns, and a concrete
successor or revisit condition. Leave official promotion and closure to the
host's Coordinator and required independent reviews.
