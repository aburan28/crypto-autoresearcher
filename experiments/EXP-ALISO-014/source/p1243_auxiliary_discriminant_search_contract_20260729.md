# Experiment Contract: Auxiliary Splitting-Discriminant Search

Date: 2026-07-29

## Hypothesis

For a fixed set of `k` odd primes, prime discriminants

```text
Delta_aux=-delta,  delta == 7 mod 8,
```

hit the simultaneous splitting conditions

```text
Kronecker(Delta_aux,p_i)=1
```

after about `2^k` prime candidates. When
`k=O(log log q)`, this supports a polylogarithmic auxiliary search
under the independent-character heuristic.

## Null Hypothesis

The deterministic sweep has failures in the search bound, or normalized
trial counts grow systematically faster than the `2^k` reference.

## Status

HEURISTIC SEARCH EVIDENCE / ARTIFICIAL PRIME SETS /
NO UNCONDITIONAL LEAST-DISCRIMINANT THEOREM

## Parameters

- `k in {2,4,6,8,10,12,14,16}`;
- three deterministic SHA-256-derived prime sets for `k<=14`;
- two sets for `k=16`;
- component primes between roughly `10^4` and `10^6`;
- candidate `delta` scanned in increasing order through `10^8`;
- only prime `delta == 7 mod 8` counted as trials.

## Metrics

- least `delta`;
- prime-candidate trials;
- `trials/2^k`;
- aggregate median and maximum by `k`;
- all splitting symbols;
- wall time.

## Positive Controls

- Every selected `delta` is prime and `7 mod 8`.
- Every prescribed symbol is `+1`.
- Rows record every rejected predecessor; zero predecessors is a legitimate
  immediate success.

## Negative Controls

- `delta == 3 mod 8` is rejected.
- Flipping one accepted symbol rejects the row.
- Reusing a component prime as `delta` is rejected by coprimality.

## Success Criterion

Every row finds a valid `delta<10^8`; all exact and mutation gates pass;
and the maximum normalized trial count stays below `128`.

This threshold is a broad falsification screen, not a distribution
theorem.

## Falsification Criterion

Any exact gate fails, any row exceeds the search bound, or normalized
trials show a clear super-`2^k` trend.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_auxiliary_discriminant_search.py
```
