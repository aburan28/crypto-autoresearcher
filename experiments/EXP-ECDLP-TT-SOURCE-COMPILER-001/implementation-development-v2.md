# TT source compiler isolated preflight checkpoint v2

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`.

This successor to `implementation-development-v1.md` records a complete,
isolated, strict development preflight. It is not an authorized experiment
run, an advice freeze, a locator, a relation algorithm, an index-calculus
exponent, a target descent, a Pollard-rho improvement, or an ECDLP
breakthrough. The experiment still has no `execution_plan`.

## Implemented isolation boundary

- The launcher validates the canonical static report against the current
  auditor, target-blind producer closure, and independent verifier closure.
- It copies exactly six source-visible files into a fresh staging root,
  removes only generated AppleDouble sidecars, rejects every other extra file,
  and replaces itself with pinned Python using the same process ID.
- The source environment starts with exactly the six frozen deterministic
  variables. NumPy's two documented temporary `MAIN_FREE=1` settings and their
  removals are accepted only as one exact four-event sequence.
- Runtime reads are restricted to the six staged files, the pinned Python and
  NumPy installation, and
  `/System/Library/CoreServices/SystemVersion.plist`.
- Writes, arbitrary environment mutation, child processes, process
  replacement, network access, and filesystem mutation are denied.
- The runtime receipt binds all staged file identities, all 1,378 observed
  file reads, the static report, event counts, environment events, and final
  environment. The independent verifier checks staged-read identities, the
  runtime path allowlist, receipt integrity, and the harness-supplied expected
  static-report digest without reading that target-hash-bearing report.
- Strict development mode emits only audits and candidate digests with
  `artifact_freeze_authorized=false`. Invoking artifact-freeze mode without an
  execution plan fails before reading the raw transcript.

## Strict development evidence

The pinned Python 3.13.1 and NumPy 2.4.0 source run and independent verifier
both completed successfully. No denied runtime event or semantic mismatch was
observed.

| Measure | Observed |
|---|---:|
| source cells | 7 |
| tensor records | 63 |
| exhaustive verifier tuples | 9,027 |
| exhaustive tensor-value checks | 81,243 |
| IR events | 65,347 |
| allocation/free events | 136,442 |
| independently replayed C08 nodes | 8,641 |
| normalization calls | 1,022 |
| streamed-prefix factorizations | 1,512 |
| two-sweep factorizations | 8,176 |
| total rank factorizations | 9,688 |
| audited runtime file reads | 1,378 |
| audited NumPy environment events | 4 |
| maximum local matrix | 10,800 field words |
| maximum TT object | 6,150 field words |
| peak live storage | 49,580 field words |
| producer logical traffic | 107,717,332 field words |
| producer peak RSS | 630,128,640 bytes |
| verifier peak RSS | 1,115,553,792 bytes |
| raw transcript size | 138,590,695 bytes |

The producer operation vector was:

| Operation | Count |
|---|---:|
| additions | 15,993,829 |
| subtractions | 11,338,088 |
| multiplications | 29,684,153 |
| squares | 0 |
| inversions | 32,318 |
| reductions | 25,205,740 |
| comparisons | 10,970,713 |
| copied words | 6,975,387 |
| hashed bytes | 15,212,273 |

Development-only file digests are:

- static closure audit:
  `6bcdb0df57b31f5a5733ddcfdd36f7c48268d6ed04e6bfc4dbf2598a420ba1e1`
- staged source transcript:
  `1d36899e2731a8f2be04f552c4e76dfa552a498d561c6923f2174d768abc37eb`
- strict preflight verification:
  `e65694b504954beebb63ba47d9c4bb8b63875152074821c8fff4276642e5ef05`
- staged six-file closure:
  `17bd0e56c6a8914670be865565e47e92bd7605efcfbfb9a99eaabc48144114aa`
- runtime receipt:
  `9b0f6eeba3ba083ac932aac8ca401e931c260d5f04bdbf5fbfb9618e15115c64`

Candidate output digests, not frozen artifacts, are:

- retained advice:
  `adfacac64f7a143e9dec8c7f849b7bb9517ff07c7099b80279c7ca9a891c529e`
- source controls:
  `b4ab406a8fd48b697584e03bb681d23be9562ea51a5e4684ac2ca206d6cbb06e`
- candidate source-advice receipt:
  `9e113a17f1bfbd8cbb718c85c7d655547ef96e5e781582383896e822bfd2e0bb`

These values are development evidence and may change after review or repair.

## Repaired preflight failures

- AppleDouble files caused the exact staging allowlist to fail. The launcher
  now removes only `._*` sidecars before rechecking the six-file set.
- `platform.platform()` invoked child processes and silently changed its
  result when those processes were denied. Backend identity now uses a
  child-free macOS normalization with the same frozen value.
- Python import probes for nonexistent bytecode cache files and metadata-only
  parent paths were initially denied. The runtime now permits only those exact
  probes, not arbitrary staged descendants.
- The first strict verifier path could emit objects named `frozen_*` despite
  the absent execution plan. That path is now unavailable; strict preflight is
  explicitly non-freezing.
- The first receipt accepted a self-reported static-audit digest. The launcher
  now validates the report against current source identities and its payload
  checksum; the verifier checks the receipt against the harness-supplied
  expected report digest without adding a fourth data-file input.

## Reproduction

Run the focused tests:

```bash
PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m unittest discover \
  -s experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/tests -p 'test_*.py' -v
```

Generate the static report, launch the staged source partition, and run the
strict non-freezing verifier:

```bash
PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/audit_tt_source_closure.py \
  --source-root experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src \
  --producer-entry experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/compile_tt_source_advice.py \
  --verifier-entry experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/verify_tt_source_advice.py \
  > /Volumes/Volume/autolab/tmp/tt-source-dev/source-static-closure-audit.json

PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/stage_tt_source_partition.py \
  --experiment-dir experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001 \
  --closure-audit /Volumes/Volume/autolab/tmp/tt-source-dev/source-static-closure-audit.json \
  --staging-parent /Volumes/Volume/autolab/tmp/tt-source-staging \
  > /Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-staged-development.json

PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/verify_tt_source_advice.py \
  --manifest experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-instance-manifest-v1.json \
  --execution-matrix experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v2.json \
  --raw-result /Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-staged-development.json \
  --expected-static-closure-audit-sha256 6bcdb0df57b31f5a5733ddcfdd36f7c48268d6ed04e6bfc4dbf2598a420ba1e1 \
  --strict-preflight-development \
  > /Volumes/Volume/autolab/tmp/tt-source-dev/source-verifier-strict-preflight-development.json
```

## Remaining gates

- Obtain independent implementation accounting and red-team reviews of this
  source runner and verifier.
- Implement the target specializer and its disjoint independent verifier.
- Implement all 29 mutations and target-phase isolation.
- Freeze implementation hashes and add a separately reviewed execution plan
  before any artifact freeze or registered experiment run.
- Preserve the toy, structured-coordinate scope: even a fully accepted run
  would measure one compiled decomposition primitive, not establish a locator
  or a sub-rho ECDLP algorithm.

## Next concrete action

Implement the target specializer that consumes only a verified candidate
source-advice object plus one target cell, then build a disjoint verifier for
the specialized TT output before considering implementation freeze.
