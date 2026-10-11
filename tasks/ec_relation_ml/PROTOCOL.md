# Frozen engineering pilot, 2026-10-11

Status: engineering specification. This is not an approved ledger campaign or
a scientific security hypothesis test. The user requested an ML research flow;
this pilot implements and validates the missing EC-to-ML bridge.

## Fixed inputs and stopping rule

The default seed is 20261011 and the fit seed is 0. Quick inputs use primes
7, 11, 13, 17, 19, 23 for training; 29, 31 for validation; and 37, 41, 43, 47
for test. Two independently generated nonsingular curve models per field and
one public target per model give 24 cases and 96 solver jobs. A standard profile
uses the first 48 odd primes at least 7, split 28/8/12 by field, two curves and
two targets per field: 192 cases and 768 jobs. These counts are fixed, not a
stopping rule that searches for a positive result.

Toy fields are bounded at 251. The full curve order is counted exactly; the
largest prime factor n >= 5 is used, with cofactor h and a checked order-n
generator G. Public factor-base x coordinates include x(G) and up to three
other subgroup x coordinates. Selection is from enumerated public points;
generation does not export seed-point or target discrete logs. Nonexistence of
a decomposition is a retained outcome. Subgroups of a common field and all
targets of a curve stay together. Fixed model-family holdout is not claimed.

Each job solves three equations in x1,x2: S3(x1,x2,x(Q)) = 0 and two factor-base
membership polynomials. S3 is the standard short-Weierstrass summation
polynomial. Four fixed actions reuse the existing selector's action set:
Buchberger/F5B crossed with lex/grevlex. Each action gets one fresh sequential
child, a 5-second watchdog including startup, and a Linux 2 GiB address-space
limit. Quick jobs have one timed solve; standard jobs have two. Job order is
seeded and shuffled. The complete pilot has a 900-second process watchdog.
A crash is an implementation failure; a timeout is censored, charged PAR-2,
and is never a successful recovery. Complete runs preserve all censored rows.

## Mathematical acceptance

An independent scalar evaluator enumerates the original equations. Every
completed solver must return that exact sorted root set. Each x solution is
lifted to base-field subgroup points, and signed witnesses must satisfy
P1 + P2 - Q = O using exact group arithmetic. An x root alone is not a relation.

For each curve/target case, G and -G have known logs 1 and -1. Other factor-base
point logs and q are unknown. Equal points, negations, repeated terms and O are
canonicalized before forming a row over F_n. Duplicate/scaled/dependent rows
have zero rank gain. A relation's existence does not certify that it identifies
q. The system reports rank, unknown count, verified relations, rank gain and
uniquely identified targets. Every returned target scalar satisfies [q]G=Q.
Relations are evaluated separately from full scalar recovery by paired BSGS.

## Learning, controls and costs

Reuse ridge log-cost regression (lambda 1) and the one-step offline contextual
bandit (1200 steps, learning rate .05). Fit normalization and weights only on
training fields. No tuning uses validation or test. Features are a fixed
allowlist of public polynomial support/degree/coefficient summaries, field and
subgroup bit sizes, and factor-base size. IDs, labels, roots, logs, seeds and
outcomes are excluded. The finite set of prime values is not itself a learning
target, and family-recognition accuracy is not a cryptanalytic objective.

Compare with action 0, best fixed action chosen on training data, uniform
selection (seeded and expected) and an outcome-aware nondeployable oracle.
Check known learnable and constant-reward controls; replay a separately fitted
shuffled-action-label diagnostic. Shuffled labels have no prespecified finite
sample success threshold. Meaningful unit checks reject invalid points,
false relations, rank-only false recovery, point alias leakage and field/curve
split overlap. The pilot has no speedup acceptance requirement or confidence
interval: four quick test fields cannot support a high-confidence security
claim. Timings, valid ranks and verified recoveries may all be negative.

Report construction, Gröbner, root extraction, verification, generation,
public-feature extraction, label acquisition including process startup, fitting,
inference, controls and total wall time; record peak child RSS. Each selector's
cost includes its action's process wall time and feature/inference overhead.
Failed actions have zero delivered relations. Actual one-off offline discovery
cost is also reported; fitting is not silently amortized. Verification group
calls measure verification work only, not symbolic-solver operations. No
comparison between unlike work units is a measured ECDLP bound.

## Next scientific contract (proposed, not executed here)

Use separate discovery, validation and untouched confirmation corpora, with
fresh random challenges whose generator entropy is held by the evaluator until
predictions and checkpoint hashes are committed. Partition connected components
of prime blocks, exact curve identities, known transports and target batches.
For source-field generalization, additionally connect repeated source number
fields; a fixed source/template shared by every case cannot count as an unseen
source. Evaluate new finite fields under a fixed template and wholly new
source-field/templates as separate generalization questions. Discarding failed
or censored fields is prohibited. Canonical isomorphism/transport families need
an additional out-of-distribution holdout. Actual P-192 and P-224 are two fixed fields, not
independent samples from a prime family; evaluate them as separate external
cases, with subgroup limits explicit.

Primary scientific objectives: additional target-identifying independent
relations per complete measured cost, and verified target recoveries per full
cost. Controls: matched random primes, matched random number fields and random
seed points; identical targets/subgroups/resources; random and simple heuristic
proposals; best fixed policy; generic BSGS and rho; shuffled labels; planted
reachable relations; duplicates and transported-isomorphic identities.

For fresh confirmation, target at least 512 independent matched prime blocks
in each toy-bit-size stratum and four independent curve draws per field, with
four random-prime and four random-number-field controls per structured draw
where maps exist. These are design targets, not a power guarantee: estimate
cluster variance on discovery data, compute power for a frozen practical effect,
and increase confirmation counts before opening its labels if required. For
three primary families, reserve two-sided 99.9667% intervals per family to give
99.9% joint coverage by Bonferroni; other sizes/objectives increase the
correction. Resample independent matched blocks, not target rows. Predeclare
effect threshold, missingness, multiplicity, stopping and cost amortization.
Treat adaptive ML discovery as exploratory until fresh confirmation and
independent mathematical review establish what transfers to larger groups.
