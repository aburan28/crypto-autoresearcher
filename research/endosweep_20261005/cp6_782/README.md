# CP6-782 G1 through the endosweep harness

Drivers that put Zexe's CP6-782 G1 (arkworks `ark-cp6-782`: `y² = x³ + 5x + b`,
782-bit `p`, 377-bit prime subgroup order `r` = BLS12-377 `Fq`) through
`harness/endosweep/`, 5 October 2026. The frozen outputs live in the `crypto`
repository, `research/cp6_782_endomorphism_chain_20261005/` (aburan28/crypto#1440).

| script | what it does |
|:--|:--|
| `cp6_sweep.py` | registers the target, pins the order externally (Hasse interval, `(h·r)·G = O`, `h·G` of prime order `r`; the harness's one-point check cannot pin a 782-bit curve from a 377-bit subgroup) and runs `sweep_target`: `t² − 4p = −339·f²`, class number 6, minimum non-scalar degree 85, best GLV-2 `9+ω` of degree `5²·7` at a modelled 1.50× |
| `cp6_chain.py` | same registration, then `build_chain_endomorphism` for the catalogue's cheapest map, `4+ω` of degree `3·5·7`; verified on a point of prime order (`found: true`, eigenvalue `5 − λ_ω`) |
| `cp6_chain_el.py` | the same for a chosen element: `python cp6_chain_el.py OUT.json 9 1` builds `9+ω` (degree 175, steps 5, 5, 7), verified as `λ_ω − 10` |

Run from the repository root with the project venv:

```sh
.venv/bin/python research/endosweep_20261005/cp6_782/cp6_sweep.py
.venv/bin/python research/endosweep_20261005/cp6_782/cp6_chain.py /tmp/cp6_782_chain_3_5_7.json
.venv/bin/python research/endosweep_20261005/cp6_782/cp6_chain_el.py /tmp/cp6_782_chain_5_5_7.json 9 1
```

`cp6_sweep.py` writes `cp6_782_sweep.{json,md}` into the current directory. Wall
times (about 2 s sweep, 24 s and 84 s for the chains) are Python on a Mac and not
performance claims. Scalar-multiplication construction only: the order's units
are `±1`, so there is no rho equivalence-class gain.
