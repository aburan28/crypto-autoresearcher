# Controlled sparse-prime versus random-prime ECDLP benchmark

The user explicitly authorized implementation and execution on 2026-10-11 and requested PR tracking. The complete fixed design is [the preceding protocol](../EXP-ECDLP-4c6a09/reports/prime-resistance-design-20261011T1443Z/protocol.md). `contract.json` and `measurement-boundary.json` are byte-identical copies of its initial plan and cap clarification. Their historical proposed/not-executed fields describe the design at creation; actual execution belongs to each new run manifest. No hypothesis or frontier claim is promoted by running this benchmark.

Main cohort: 36 sparse-prime blocks at 24/28/32 bits, each with random and residue-matched random controls. The six earlier moduli remain separate case studies. All targets are public synthetic points; validation-only scalars never enter the attack kernel’s job inputs.

Preparation command, using an unused output path:

```sh
/workspace/solinas-runtime/report-venv/bin/python experiments/EXP-ECDLP-5184f7/implementation/prepare.py \
  --plan experiments/EXP-ECDLP-5184f7/contract.json \
  --boundary experiments/EXP-ECDLP-5184f7/measurement-boundary.json \
  --out experiments/EXP-ECDLP-5184f7/runs/<RUN-ID>/preparation
```

Dependencies: Python with NumPy/SciPy, PARI/GP 2.17.2, C++20 compiler and OpenSSL. `common.py` uses the local GP installation and an explicit 128 MiB initial PARI stack, with a 4 GiB address-space limit and 600-second per-process watchdog. Two preparation workers are permitted; attack/timing work uses one pinned worker after preparation finishes.

Build and run the public attack jobs:

```sh
g++ -O3 -std=c++20 -Wno-deprecated-declarations \
  experiments/EXP-ECDLP-5184f7/implementation/attack.cpp -lcrypto -o /tmp/prime-attack
/workspace/solinas-runtime/report-venv/bin/python experiments/EXP-ECDLP-5184f7/implementation/run_attacks.py \
  --prep experiments/EXP-ECDLP-5184f7/runs/<RUN-ID>/preparation \
  --kernel /tmp/prime-attack --out experiments/EXP-ECDLP-5184f7/runs/<RUN-ID>/attacks
```

The kernel receives no family label or scalar truth. Its group values keep coordinates private; native encoding exposes compressed coordinates to the standard walk, while the opaque interface supplies HMAC labels. The fixed solvers use only group operations, equality, encodings, subgroup order and public seeds. External Python arithmetic verifies every returned scalar and collision equation. Exact transported-isomorphism, sham-label and counter replay controls preserve traces/counters.

Matching uses a fixed SciPy assignment implementation on candidate-index-sorted rows and columns: dummy cost 100, forbidden cost 1,000,000, eligible cost absolute log-order ratio. The maximum possible eligible-cost sum is below one dummy penalty, so cardinality takes precedence. Stable ordered assignment resolves equal-cost ties. Full edge lists and selected/unmatched rows are retained.

Implementation checks use separate small synthetic controls and an exact historical group; they are excluded from study statistics. The final report must distinguish unconditional curve-generation outcomes, normalized attack cost, and arithmetic timing. A successful run alone does not establish broader ECDLP resistance.
