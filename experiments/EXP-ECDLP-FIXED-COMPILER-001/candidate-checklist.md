# ECDLP Candidate Checklist

## Candidate name

Fixed-curve `4+1` witness compiler.

## Target curve family

- prime field: yes;
- binary field: no;
- extension field: no;
- special curve class: explicitly excluded in the scheduled experiment.

## What structure is exploited?

Coordinates select the factor base and may change the support and witness multiplicity of its four-fold sumset. A fixed curve permits the four-sum witness table to be reused across relation targets and individual logarithms.

## Why does deployed prime-field ECDLP not obviously kill it?

Generic-group preprocessing bounds erase affine-coordinate predicates. The compiler is representation-specific, but no useful asymptotic compression is assumed; it must be measured against matched controls and the generic preprocessing frontier.

## Factor base

- definition: a sign-complete coordinate family or matched random control;
- size: smallest sign-complete even `B=2f` whose exact signed five-term formal-class count is at least `0.5q`;
- membership test cost: charged constructor-specific coordinate and field work.

## Relation generation

- relation shape: five factor-base points sum to a known multiple `aP`;
- expected probability: exact signed-class occupancy is the sizing control; actual toy success is the exact EC five-sum support divided by `q`;
- decomposition method: witness-bearing four-sum table plus one-point scan;
- cost per attempt: one EC subtraction and one table probe per scanned factor-base point;
- cost per relation: measured including failed targets and known-multiple generation.

## Linear algebra

- matrix dimensions: retained unique equations by `B` factor-base unknowns;
- density: at most five nonzero coefficient positions before modular cancellation;
- rank expectation: untested and measured exactly;
- modulus: prime group order `q`.

## Individual logarithm / target descent

- method: randomize the target by a known multiple of `P`, decompose, sum recovered factor-base logarithms, and remove the randomizer;
- expected cost: geometric in exact five-term support probability, with every attempt charged.

## Baselines

- rho cost: matched Pollard rho on each curve;
- parallel rho cost: not measured in this toy preflight;
- BSGS cost and memory: fixed-base baby-step advice is executed on the identical targets under the candidate's full advice-bit budget;
- closest known IC cost: recursive Semaev and fixed-curve point-decomposition methods, with this experiment isolating a materialized witness compiler rather than Groebner elimination.

## Claimed advantage

- asymptotic: none;
- constant factor: untested;
- memory: potentially worse because four-sum advice is materialized;
- parallelism: target queries are independently parallelizable;
- amortized many-target setting: offline advice and solved factor-base logs are reusable on the fixed curve.

## Things that would kill the idea

- random-like four-sum support requires `Theta(B^4)` advice;
- first-witness compression destroys relation rank;
- alternate witnesses restore rank only with prohibitive storage;
- individual descent has low support or hidden scalar-multiplication cost;
- coordinate families do not beat random-x after all costs are included;
- the fitted end-to-end exponent remains at least `0.5`.

## First experiment

Compile exact toy four-sum advice at witness caps one and four, collect five-term equations, solve and independently verify all factor-base logarithms, perform randomized target descent, and compare every cost and support metric against random-x, random-scalar, scalar-progression, and Pollard rho.
