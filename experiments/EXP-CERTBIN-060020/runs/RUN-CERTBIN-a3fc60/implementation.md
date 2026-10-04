# Implementation notes: EXP-CERTBIN-060020 / RUN-CERTBIN-a3fc60

Executor: TASK-20260924-a50c5b. Specification version 1 (sha256
7da73ae8d55f5997bee0ccead0e77514b32c5c2e93941e147c58e0f8c69a83e0), unchanged.
Trial plan: experiments/EXP-CERTBIN-060020/trial-plan-v1.json, written at
2026-09-25T15:23:35Z. Engine: crypto_autoresearcher.gf2 at 934bee5, imported
with src/ on sys.path, native backend.

## Protocol deviations

Each item gives the deviation, then the reason.

1. **pytest flag.** The C-ENGINE (d) command adds `-p no:cacheprovider`
   (`python3 -m pytest -q -rs -p no:cacheprovider tests/test_gf2_kernels.py`).
   - Reason: pytest would otherwise write `.pytest_cache` at the repository
     root, outside the write scope.
   - The flag does not affect which tests run or how they are scored.
2. **C-SRC and C-SEED placement.** Both run inside `selftest.py`, at its start,
   before any seeded draw. selftest.py also writes `inputs.json`.
   - Reason: the frozen command gives `selftest.py` only `--out selftest.json`.
     The specification lists C-SRC and C-SEED under phase 0, and both still
     precede the first draw of every stream.
3. **C-ELL placement.** C-ELL is evaluated in phase 3 (the rc_b pass), on every
   S_3 system (S3-U400, S3-SAT100, F-RANDX19) and every N-CONV19 system. The
   specification's phase list names C-ELL in phase 1.
   - It is still evaluated before any closure (phase 4). Only the ordering changes.
4. **Extra negative-control randomness.** The negative-control construction
   uses one extra, deterministic source of randomness:
   `numpy PCG64(2026092460600 + 999)`.
   - It only chooses which row or k to corrupt.
   - It touches no arm stream and no measured quantity.
   - It is not one of the seven frozen seeds.
5. **Thread counts.** `CRYPTO_AR_GF2_THREADS=2`, as the dispatch note directs
   (the specification allows <= 3). `OPENBLAS_NUM_THREADS=2` and
   `OMP_NUM_THREADS=2` are also set, as machine protection on the shared host.
6. **Memory cap enforcement.** `ulimit -v` of 3 GiB applies to every stage. An
   in-process RSS guard (3 GiB) runs during phase 4, with checkpoint and exit.
   - Neither fired.
   - The per-system closure watchdog (3600 s) is implemented as a monitor
     thread that checkpoints and exits (code 75). The engine's SIGALRM deadline
     cannot be used inside worker threads. It did not fire.

## Executor interpretations of the frozen text

These are fixed in trial-plan-v1.json before phase 0, and the verifier
implements them independently.

- E_sha256 is the sha256 of the compact JSON list of the 19 lowercase E_hex
  strings. Instance keys are `<ARM>:<i>`, where i is the running index in
  keep order. Role, slot, family and stratum are separate fields.
- **S3-PRIMARY.** A duplicate is an x_R equal to that of an earlier classified
  attempt. The loop stops as soon as both quotas are full.
- **N-CONV19.** The generator is consumed slot by slot. A duplicate is a draw
  equal to an already-kept N-CONV19 system.
- **N-ELL19 and N-F219.** A duplicate is a draw equal to any earlier
  non-duplicate draw of the same stream.
- **N-AFF19.** The "non-degenerate S3-PRIMARY attempts" are the classified
  attempts: R != O, x_R >= 1024, and not a duplicate. Duplicates are counted
  per family.
- **F-RANDX19.** Rejections are applied in this order:
  1. degenerate;
  2. duplicate of an earlier non-degenerate draw;
  3. equal to the x_R of any S3-PRIMARY attempt with R != O.
- **C-NONREF controls.** The control set is the first 5 non-refuted
  unsatisfiable systems of each of N-CONV19, N-ELL19, N-F219, N-AFF19 and
  F-RANDX19.
- **"Every arm" in C-BACKEND and C-LIT.** This means S3-U400, N-CONV19,
  N-ELL19, N-F219, N-AFF19 and each F-RANDX19 stratum.
- **C-SELF (v).** "Naive per-assignment evaluation" is implemented in two ways:
  - full-width bit-sliced truth tables, giving the value of every equation at
    every one of the 2^20 assignments (a different algorithm from oracle B's
    split-half evaluation);
  - 3,200 pure-Python per-assignment spot checks.
- **C-SELF (vi).** All 10^4 quadratics are checked for root validity. For 100
  of them, the complete root set is also checked by brute force over all of
  F_{2^19}.
- **C-SELF (viii) and (x).** Stage A draws random 6-variable systems until at
  least 30 exist and at least 3 reach iteration >= 2. Random systems almost
  never give a W_D-only refutation, so stage B CONSTRUCTS affine-rich systems.
  It draws them until at least 3 systems are refuted at iteration >= 1, which
  exercises the general wdag extractor. selftest.json lists the constructed
  systems.
- **N19-DR-7.** "The arm's systems" means every kept system of the arm, both
  roles, excluding UNDETERMINED(budget) systems (there were none).
- **wdag-v1 construction.** Three cases:
  - Iteration-0 refutations use the one-node form.
  - Where ell_route holds (S_3 and N-CONV19), the certificate is the
    prefix-shared chain construction.
  - Otherwise it is the specification's recommended grouped construction. One
    node per (parent, variable j) group holds the sum of the fallen rows used
    with j, expanded level by level with kernels.backtrace.
  - Only extraction is overridden, in a subclass of closure.Closure. The
    engine's W_D iteration (_w_closure) is inherited unchanged.
- **C-DET (c).** It recomputes 20 systems with 1 thread: the first 4
  unsatisfiable systems of each of N-CONV19, N-ELL19, N-F219, N-AFF19 and
  F-RANDX19. They are compared with the phase-4 records, which were computed
  with 2 threads.

## Observations about the specification text (not deviations)

- The specification's sizes_expected says "Total 2150 kept systems". The
  per-arm quotas sum to 2100 (400 + 100 + 4 x 250 + 600). The quotas were
  applied; 2100 systems were kept, with no shortfall.

## Development history (disclosed)

- impl/ and verifier/ were developed and rehearsed end to end in the session
  scratch directory, outside the repository, before this run. The rehearsals
  used development seeds only:
  - arm seeds 91000001..91000006 and 92000001..92000006;
  - self-test seeds 777001..777004.
- The frozen arm seeds were first used by this run. The RC-1 replay and the
  kernel tests (C-ENGINE) were also dry-run into scratch. No rehearsal output
  is reported as a result.
- Before the run, the shared checkout's HEAD moved from 2b58093 to fe1080a: the
  Coordinator's archive commit of EXP-CERTBIN-ddfe75. That commit changes none
  of this experiment's inputs, the specification, src/, tools/gf2_replay_rc1.py
  or tests/test_gf2_kernels.py. The engine tree hash is unchanged (C-ENGINE (a)).
- Files modified or untracked by other sessions are recorded as the dirty-tree
  state in environment.json:
  - tools/run_supersession_registry.yaml;
  - experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e/manifest_v2.yaml.

## Run history

- **One run, no re-run.** Stages ran in this order: main, determinism,
  backend, verify, aggregate. Every stage exited 0. No watchdog, RSS guard or
  infrastructure event occurred. command.txt and the logs record every stage.
- **checkpoint/** is the driver's working state. It holds:
  - per-phase markers;
  - the phase-4 gzipped chunks, which are duplicated in closures.jsonl.gz and
    certificates.jsonl.gz;
  - the per-system ann-v1 files, which are duplicated in annihilators.jsonl.gz;
  - the rc_b records, which are duplicated in closures.jsonl.gz.
