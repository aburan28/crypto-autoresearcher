# Experiment Contract: Recursive D2 Complement Preflight V1

## Hypothesis

Exact fixed-curve `D4` membership can be answered by a recursive complement
operator using only `D2` advice: for each `A`, scan every `D2` state `U` and
look up `T-A-U` in the same `D2` index. This may trade larger online work for
advice below materialized `D3/D4`, while retaining exact four-source
witnesses.

The companion `R+D3` route and materialized `D4` route are measured on the
same target batch. This is a direct fixed-curve preprocessing experiment,
not a generic-group claim.

## Null Hypotheses

1. Recursive `D2+D2` and `R+D3` routes lose witnesses or support.
2. Recursive advice savings are erased by charged witness records and online
   complement/replay work.
3. The exact recursive query remains too expensive for the typed `A+4R`
   relation path, even when D2 advice is below the rho count.

## Parameters

- immutable input: `TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves and four coordinate families;
- exact nondecreasing source tuples at levels D2, D3, D4;
- target batch: planted, held-out, shifted-control;
- routes: D2+D2, R+D3, materialized D4;
- all witness records retained and replayed as canonical four-index tuples;
- logical advice words include point-key fields and witness-index words;
- `S*T^2/q` is a diagnostic tradeoff report, not a theorem or success claim.

## Metrics

- D2/D3/D4 support, state digests, witness records;
- build additions, inversions, multiplications;
- per-target lookups, candidate witness counts, replay work, online work,
  success, and exact route hit sets;
- advice words and `S*T^2/q` for every route;
- independent replay and mutation receipt.

## Controls

- exact equality of D2+D2 and materialized D4 hit sets;
- exact equality of R+D3 and materialized D4 hit sets;
- all returned witnesses replay to `target-A` and canonical four-source
  tuples;
- independent affine addition and route implementations;
- five deterministic verifier mutations.

## Success Boundary

A valid recursive-operator observation requires exact support and witness
agreement. A practical fixed-curve improvement additionally requires advice
and online work to beat a same-advice baseline after witness payloads,
construction, target count, and success probability are charged.

No generic ECDLP promotion gate exists in this preflight. That would require
fresh curves/seeds, relation rank, individual descent, full offline/online
cost, and a strict comparison with optimized rho and generic preprocessing.

## Falsification

- any route mismatch or witness replay failure;
- recursive advice savings disappear after witness payloads;
- D2+D2 online work grows to the full explicit join floor;
- no strict fixed-curve tradeoff survives the charged cost model.

Failure is scoped to this recursive D2 complement operator. It does not rule
out other nonlinear target selectors, quotient states, or batch operators.

## Reproduction

```bash
python3 src/recursive_d2_complement_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union

python3 src/verify_recursive_d2_complement_preflight.py \
  /path/to/raw-result.json
```
