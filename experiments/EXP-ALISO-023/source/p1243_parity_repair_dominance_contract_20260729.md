# Experiment Contract: Parity-Repair Divisor Dominance

Date: 2026-07-29

## Hypothesis

For every odd parity-repair fixture with

```text
c=c_3(m),  m_0=m/c,
L=n_1^2*m_0-d,
```

the unmodified dimension-four construction from Remark 4.4 of ePrint
2025/1243 can use the divisor `m_0` directly. It has the same size and
smooth-search condition as the repaired construction, while its torsion
modulus, root count, largest prime, field requirements, and output degree
are no larger.

Consequently the parity-repair candidate is weakly dominated within the
source theorem's own admissible-modulus optimization.

## Null Hypothesis

At least one registered fixture violates an assumption needed to use
`m_0`, obtains a smaller smooth modulus from repair, or has a source
dimension-four norm difference unrelated to the repaired one.

## Status

RESTRICTED DOMINATION THEOREM / EXACT ARITHMETIC CHECK /
NEGATIVE RESULT FOR THE PARITY-REPAIR COMPLEXITY CLAIM

## Inputs

Read every family from:

```text
experiments/ecdlp_isogeny/p1243_parity_repaired_kani_probe_result.json
```

## Metrics

- exact divisibility `m=c*m_0`;
- every `3 mod 4` prime has even valuation in `m_0`;
- `m_0` is a sum of two squares;
- `m_0` divides the registered orientation discriminant;
- `gcd(m_0,d)=1`;
- the same `n_1` is admissible and has the same `L`;
- source difference
  `Delta_0=m_0*(n_1^2*m_0-d)`;
- repaired difference
  `Delta_rep=c^2*Delta_0`;
- source and repaired size gates are equivalent;
- `T(m_0)<=T(m)`;
- `B(m_0)<=B(m)`;
- source output multiplier `m_0` is no larger than repaired multiplier
  `m*c`.

## Positive Controls

All five registered families satisfy every dominance gate, including
`m_0=1`, repeated prime powers, mixed good/bad primes, and no-repair
controls.

## Negative Controls

- Replacing `m_0` by `m_0+1` must reject divisibility or parity.
- Removing one necessary factor from `c` must reject the sum-of-two-squares
  gate.
- Changing the repaired difference by one must reject the square-factor
  identity.

## Success Criterion

Every exact dominance gate passes and every effective mutation is
rejected.

## Falsification Criterion

Any valid fixture where the source cannot use `m_0`, where the repaired
smooth threshold is smaller, or where a charged resource of the source
is larger.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_parity_repair_dominance.py
```

