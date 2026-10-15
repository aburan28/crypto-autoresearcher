# Exact triple oracle: implementation interface

collector.rs is an exact group-law enumerator for a **prepared** endpoint
input. `prepare_input.py` constructs native, random, transported, and rebuilt
bases with the prespecified target law; `verify_collector.py` independently
checks point equations, group order and rank; `exact_interval.py` inverts
integer hypergeometric tails. These components do not certify the conductor,
enforce the endpoint watchdog, issue a scientific run receipt, or establish
full-size no-hit completeness. The formal experiment remains `review_required`
until those components and an admitted launcher are complete.

Compile with TMPDIR=/private/tmp and rustc --edition=2021 -O collector.rs.
The earlier build with the host's default TMPDIR failed with
No space left on device under /Volumes/SSD990/llm/tmp. This is a compiler
scratch-path failure, not an oracle observation.

## Prepared input

UTF-8, one whitespace-separated record per line:

~~~text
curve p a b r nbase ntarget
base 0 x y
...
base nbase-1 x y
target 0 alpha beta x y
...
target ntarget-1 alpha beta x y
~~~

The a,b in the header are the short-Weierstrass coefficients. The base has
nbase=2B and consecutive pairs are (P,-P). Every point must be finite
and on the curve. Target scalar coefficients satisfy 0<=alpha<r and
1<=beta<r. The preparer/verifier must establish R=[alpha]G+[beta]Q,
target uniqueness and nonidentity, generator/order certificates, factor-base
construction, and all input hashes. The collector checks syntax, field
coordinate bounds, on-curve points, signed pairing, and coefficient ranges.

## Collector output

UTF-8 tab-separated records:

~~~text
collector-v1 p r nbase ntarget
target id alpha beta unordered_count ordered_count useful_count
triple id i j k
...
~~~

The target line precedes its sorted triple lines. A triple has i<=j<=k
and denotes an unordered multiset of base point IDs whose sum is that target.
The collector preserves repeats and opposite pairs in raw counts. Ordered
weight is 1 for i=j=k, 3 for exactly two equal, and 6 for three distinct IDs.
A useful triple has three distinct IDs and three distinct x-orbit IDs
(id/2), which excludes opposite pairs. The runner must retain stdout and
stderr without overwriting attempts.

The output binds alpha,beta but does not itself prove that target coordinates
follow the frozen target law. verify_collector.py rederives targets, replays
all reported triples, and computes modular rank at fixed prefixes. An exhaustive small-group control checks
completeness and the all-target |F|^3 identity.

## Current control

python3 test_collector.py BINARY uses a separate Python point-addition
implementation on a 19-point group, enumerates every ordered triple, invokes
the separate verifier, compares
complete triple sets and counts for all 18 nonidentity targets, and checks
the all-target ordered conservation identity. Passing this control does not
certify the P29/P37 run or the full admission gate.

`test_preparer.py` checks all six specified endpoints and all four arm types
with eight public fixed test targets each. Its count is explicitly marked
outside the formal 32,768-target protocol. Exact prime-order group checks
follow from trial-division primality of p and r, rG=O, and Hasse's bound;
the conductor and isogeny provenance still require the archived source specs.

`test_exact_interval.py` compares integer tail decisions with direct sums
on small populations. `exact_interval.py` uses threshold 1/800 for each
tail and prints display fractions only after computing integer endpoints.
