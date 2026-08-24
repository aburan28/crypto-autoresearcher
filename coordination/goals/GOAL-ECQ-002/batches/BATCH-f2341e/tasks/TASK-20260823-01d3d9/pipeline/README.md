# Family-agnostic specialise → order → certify → measure → emit pipeline

TASK-20260823-01d3d9 · BATCH-f2341e · GOAL-ECQ-002 · H-ECQ-d60d07

Turns **any** Q(t) family (read from a JSON spec — no family is hard-coded)
plus a **parameter box** into certified curves over Q and ICARM-format
submission records. The campaign's base family is chosen concurrently in
TASK-20260823-d1cb76 and is simply passed in as `--family`.

## Entry point

```sh
python3 pipeline.py \
    --family families/DEMO-SEC5-r5.json \
    --box '{"t": {"num_min": -15, "num_max": 15, "den_max": 2}}' \
    --top-k 15 --control 15 --seed 20260823 --rank-time-limit 15 \
    --out result.json
```

| flag | meaning |
| --- | --- |
| `--family` | path to a family spec (format below) |
| `--box` | JSON parameter box; per parameter `{"num_min":a,"num_max":b,"den_max":d}` (all rationals p/q with a ≤ p ≤ b, 1 ≤ q ≤ d) or `{"values":["1","3/2"]}` |
| `--top-k` | how many Mestre-Nagao-ranked candidates go to descent + certification |
| `--control` | how many **uniformly random** candidates from the same box do too (the control that measures the ordering's efficiency instead of assuming it) |
| `--seed` | RNG seed for the control; the rest of the pipeline is deterministic |
| `--rank-time-limit` | PARI `ellrank` alarm in seconds; a timeout is recorded as an infrastructure outcome |

### Family spec

```json
{
  "name": "MY-FAMILY",
  "params": ["t"],
  "a_invariants": ["0", "0", "0", "-t^2", "t^2"],
  "sections": [["0", "t"], ["t", "t"]],
  "claimed_generic_rank": 2,
  "source": "citation; a CLAIM TO REPRODUCE, never a given"
}
```

`a_invariants` and `sections` are rational functions of the parameters in
ordinary Python arithmetic (`^` is accepted). Specialisation is exact
(`fractions.Fraction`), then scaled to an integral model by
(x, y) → (u²x, u³y); PARI minimalises afterwards.

## What certifies what

| stage | tool | epistemic status |
| --- | --- | --- |
| specialise | `families.py` | exact |
| order | `pipeline.mestre_nagao` — S(N)=Σ_{good p≤500} −a_p log p / p | **heuristic ordering only**, never a rank claim; always run against the random control |
| search for points | PARI `ellrank` under `alarm()` | search only; its `r_low`/`r_high` are never reported as our rank |
| **certify rank** | **`exact_certify.py`** | **exact, stdlib only** (`fractions`/`math`): on-curve check, non-torsion by Mazur, independence by mod-ℓ reduction. This is the only source of a rank number. |
| minimal model / heights / conductor | `icarm_invariants.py` (PARI) | exact integers (c4, c6, Δ, N) plus their logarithms |
| regulator in the emitted record | PARI `ellheightmatrix` | **numerical**, labelled as such, load-bearing for nothing |
| emit | `pipeline.icarm_record` | record only — **nothing is sent to the ICARM endpoint** |

`exact_certify.py` proves independence with no floating point: for a prime ℓ
coprime to an exactly computed torsion bound, and good primes p with ℓ | #E(F_p),
the map ψ_p(X) = (#E(F_p)/ℓ)·X kills ℓE(F_p) and the reduction of E(Q)_tors, so
an F_ℓ-rank-k set of stacked images admits no primitive Z-relation modulo
torsion. Full argument in the module docstring.

## Scripts

| file | purpose |
| --- | --- |
| `pipeline.py` | the entry point above |
| `exact_certify.py` | exact stdlib-only rank-lower-bound certifier (also a CLI: `python3 exact_certify.py cert.json`) |
| `selftest_certifier.py` | negative controls for the certifier (dependent points, off-curve, torsion) — run before trusting any output |
| `reproduce_icarm.py` | CHECK 1: recompute rank/heights/conductor for curves already on the frozen board and compare |
| `falsifier_height.py` | CHECK 2: naive height vs parameter size, the cheap falsifier of H-ECQ-d60d07's mechanism |
| `icarm_invariants.py` | leaderboard invariant definitions (pinned by CHECK 1) |
| `families.py` | family spec + specialisation + parameter box |
| `make_demo_families.py` | builds the internal demo/null families used by the checks |
| `summarise_validation.py` | assembles `pipeline_validation.json` from run results |
| `run_harness.py` | wraps a command as an immutable run record under `runs/<RUN-ID>/` |

## Reproducing every run in this task

```sh
python3 make_demo_families.py families
python3 run_harness.py RUN-<new-id> results/selftest_certifier.json 300 -- \
        python3 selftest_certifier.py ../results/selftest_certifier.json
python3 run_harness.py RUN-<new-id> results/reproduce_icarm_all.json 1200 -- \
        python3 reproduce_icarm.py \
        ../../../../../baseline/icarm_database_20260823.json \
        ../results/reproduce_icarm_all.json --conductor-time-limit 15
python3 run_harness.py RUN-<new-id> results/falsifier_height.json 900 -- \
        python3 falsifier_height.py ../results/falsifier_height.json \
        families/*.json --num-max 30 --den-max 3
```

`run_harness.py` refuses to overwrite an existing run directory: run records are
immutable, and a corrected run gets a new id.

Requires Python 3.11 and `cypari` 2.5.6 (PARI 2.15.4). `exact_certify.py` and
`selftest_certifier.py` need neither.
