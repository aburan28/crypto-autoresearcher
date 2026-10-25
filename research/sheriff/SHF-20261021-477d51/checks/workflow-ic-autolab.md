# Target 6: `.github/workflows/ic-autolab.yml` (commit ebcd51bda), read-only analysis

Read at crypto b4f056101 with `git show`: the workflow, and
`research/ic_candidate_tournament_20260915/{sat_runtime_execution_v3.py,
static_sat_native_v3.py, frozen_sat_runtime.py}`. Nothing was run.

## The change
1. `apt-get install -y valgrind zstd` (adds zstd; the valgrind version pin stays).
2. New step before the tests: read the RUNPATH of `$pythonLocation/bin/python3`;
   if it is non-empty and does not exist, `sudo mkdir -p` its parent and
   `sudo ln -s "$pythonLocation/lib" "$rp"`; then assert that
   `env -u LD_LIBRARY_PATH python3 -I` reports the same `platform.python_version()`
   as the job's `python`.

## The gate it is about
`sat_runtime_execution_v3.py:47-77` `interpreter_record()` binds
`sys.version`, `platform.system/machine`, `executable_sha256 = digest(sys.executable)`
and a sha256 inventory of every stdlib source file. The gate compares the
record of the child (started with `-I -S -B` and `frozen_environment()`,
lines 202-208, which keeps only PATH/HOME/TMPDIR/LANG/LC_ALL and so drops
LD_LIBRARY_PATH) against the registered `spec['interpreter']`
(lines 241-242, 318-319, 350-351; `static_sat_native_v3.py:114-115, 189`).

## Assessment
- The PR changes no gate code and no registered record. The comparison
  `interpreter_record() == spec['interpreter']` is unchanged and still fails
  closed on any version, executable or stdlib difference.
- The symlink makes the child resolve the libpython of the interpreter the
  parent runs, which is what the gate assumes. It does not make a different
  interpreter pass: a mismatch still raises in the workflow assertion and
  again in the gate.
- A dangling link at `$rp` from an earlier job tests `! -e` true, and then
  `ln -s` fails ("File exists"), so the step fails closed. It does not
  silently reuse a stale link.
- `zstd` is a package install with no version pin. That is the same trust
  class as the existing apt `valgrind`, which is pinned by a version
  assertion; zstd has none. This does not touch the interpreter gate.
- Pre-existing limitation, not introduced here: `executable_sha256` hashes
  only the `python3` launcher. For a shared build (`--enable-shared`, which
  this RUNPATH implies) the interpreter's code is in `libpython3.x.so`,
  which `interpreter_record()` does not hash. Only `sys.version` separates
  two libpythons. The failure this change fixes (3.12.3 against 3.12.15) was
  caught by that string. Two builds with the same version string but
  different libpython bytes would not be caught. The record calls itself
  "local interpreter and stdlib content binding; not remote attestation".

Verdict input: the change does not weaken the interpreter-integrity gate.
Coverage is limited: CI runs of ic-autolab after ebcd51bda were not
inspected. This session's GitHub access is scoped to crypto-autoresearcher,
so that check is `not_covered`. It would be covered by
`gh run list -R aburan28/crypto -w ic-autolab.yml` and reading the
linux-integration-controls job.
