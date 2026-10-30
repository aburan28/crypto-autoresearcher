# F4 command and failure history

Working directory for every command below: `/workspace/crypto-autoresearcher`.
All scientific-looking runs below are fixed implementation/counting checks, not approved performance trials. The producer receipts include HEAD, dirty-tree list, source/input digests, versions, parameters, start/end UTC, wall/CPU and RSS. Native interactive Codex inherited the parent's model; backend/model binding was not independently probed. The exact requested handoff input commit is `2c8c71cfff6f7f63297fbe4de4608cd94d857184`; actual checkout HEAD is bound separately in each receipt. No git mutation was performed.

## Failed implementation attempt, preserved

```sh
SYMPY_GROUND_TYPES=flint /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/tracks/f4/validate.py --out research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-01 > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-01.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-01.stderr
```

Exit 1: SymPy 1.14.0 factor_list's conversion of 256-bit FLINT factors raises `TypeError` inside `fmpz_mod_poly.__cinit__`. Both failed source files are retained as `receipts/check-01-source-*.py`. The output directory exists and is empty because extraction failed before the first certificate. The fix calls the installed FLINT factor API directly; the independent checker uses Python-domain SymPy.

## First successful producer and independent checker

```sh
SYMPY_GROUND_TYPES=flint /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/tracks/f4/validate.py --out research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02 > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02.stderr
SYMPY_GROUND_TYPES=python /usr/local/bin/python3 research/p256_factor_base_parallel_20261025/tracks/f4/independent_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-01.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-01.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-01.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/independent_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-02.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-02.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-02.stderr
```

The middle command exits 127 because the root AGENTS.md recommended `/usr/local/bin/python3` does not exist on this machine. Its stderr is retained. `python3` resolves to `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3` (CPython 3.12.14); this is neither the missing recommended path nor Ubuntu's `/usr/bin/python3`. The first and third commands pass. The check-02 producer source snapshot and independent-02 checker snapshot remain in receipts.

## Counting and corruption controls

```sh
python3 research/p256_factor_base_parallel_20261025/tracks/f4/theory.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/exact-counts.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/exact-counts.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/exact-counts.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/adversarial_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-01.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-01.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-01.stderr
```

Both pass. Counting is exact integer arithmetic plus 18 finite abstract-group enumerations. Corruption controls copy certificates into temporary scratch directories, mutate one field and require the separate checker to reject. Mutation specifications and corrupt-file digests are retained; temporary scratch copies are deleted automatically.

## Final producer after explicit constructed-anchor accounting

```sh
SYMPY_GROUND_TYPES=flint /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/tracks/f4/validate.py --out research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-03 > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-03.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-03.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/independent_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-03 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-03.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-03.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-03.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/adversarial_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-03 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-02.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-02.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-02.stderr
```

All pass. The final source change adds explicit construction anchors, including repeated zeros and inverse pairs, to every split correctness fixture. The separate checker now checks anchor multiplicities. Ranks and original outcomes remain the same. Output directories are exclusive-create: reproduction must choose a fresh directory rather than overwrite these records. No failed samples were discarded.

## Record rendering

```sh
python3 research/p256_factor_base_parallel_20261025/tracks/f4/make_record.py
```

Builds the diagram, derived result and digest manifest from the final retained receipts. Root renders and inspects the aggregate/per-track PDF. No existing canonical graph's scientific status changes here.

## Other lookup failures

The following read-only orientation commands encountered absent files: `cat .agents/skills/executor-implementation/SKILL.md`, `cat research/p256_factor_base_parallel_20261025/tracks/f4/README.txt`, and `cat research/p256_factor_base_parallel_20261025/baseline/sources.json`. The executor policy is named by the task/role contract; no missing skill instructions were invented. The research-visuals pointer and canonical SKILL.md were read. The absent source file was not treated as citation evidence. No Sage/Docker execution or installation was needed.

## Final graph-input guards and replay

```sh
SYMPY_GROUND_TYPES=flint /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/tracks/f4/validate.py --out research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04 > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/independent_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-04.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-04.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-04.stderr
SYMPY_GROUND_TYPES=python python3 research/p256_factor_base_parallel_20261025/tracks/f4/adversarial_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-03.json > research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-03.stdout 2> research/p256_factor_base_parallel_20261025/tracks/f4/receipts/adversarial-03.stderr
```

All pass. This is the final source/receipt set. The API now refuses unresolved divisors and rows with more than two nonzero outside orbit columns before graph construction. Two added expected-rejection cases pass; total expected API refusals is five. Original divisor/graph ranks remain unchanged. The previous producer source is retained as `receipts/check-03-source-*.py` so earlier exact source hashes remain reproducible. No previous attempt was overwritten.
