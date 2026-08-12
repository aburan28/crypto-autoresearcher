# TT Supervised Artifact Development V1

## Handoff: deterministic V22 producer envelope

### Claim or task

Package the reviewed V22 source-producer child result and parent receipt in a
closed, deterministic, bounded development envelope without weakening either
authority's byte identity.

### Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Artifact freeze: unauthorized.

Campaign execution: unauthorized.

This is a harness/publication result. It is not a locator, point-decomposition,
index-calculus, rho, ECDLP-improvement, or breakthrough result.

### Assumptions

- The V22 producer result and receipt are the previously reviewed authorities.
- The reviewed source-staging parent and local host are trusted.
- Malicious or concurrent host mutation is excluded.
- Python 3.13 and its zlib/gzip implementation are part of the deterministic
  byte environment; implementation drift must change the compressed digest.
- Power-loss crash residue is not measured.

### Input identities

| Authority | Bytes | SHA-256 |
|---|---:|---|
| child result | 138,592,835 | `cc7b3e0cf24e28976c11ef6bcbdfa1dd5fea36df42233783fe4a1fe81f36411e` |
| parent receipt | 14,465 | `0a6ce2070abb005c1cb5ac5ce2e462bf09a4683f99440f9e72fd84c477e02a09` |

### Red-team sequence

1. The first review request resolved the two implementation paths relative to
   the repository root and incorrectly reported them absent. That procedural
   finding was rejected. Its trust-model, numeric-bound, and publication-cost
   findings were valid and were fixed.
2. The corrected review returned `NO-GO`: a rebound noncanonical gzip stream
   was accepted, payload reads were double-counted by implementation but
   under-reported, contradictory authority fields were shallowly checked, and
   the corresponding controls were missing.
3. Exact recompression, metadata-only file inspection, instrumented read
   accounting, authority rejection, numeric-cap controls, explicit AppleDouble
   controls, and failure-injected publication cleanup were added.
4. Re-review returned `NO-GO` for nested authority keys. Validation was changed
   to traverse every object and array in both authorities, with the demonstrated
   nested child and receipt counterexamples added as controls.
5. Final independent re-review returned `GO` for measured V22 development
   packaging only, with artifact freeze and campaign execution still forbidden.

### Evidence so far

The focused artifact suite passed 14 tests. The complete experiment suite
passed 78 tests. After the final nested-authority repair, the repository suite
passed 144 tests in 661.864 seconds.

Two independent pack invocations produced byte-identical three-file directories:

| File | Bytes | SHA-256 |
|---|---:|---|
| `child-result.json.gz` | 9,802,189 | `fc44bbc843455fa9e5560e97c2a3e41b91d238dfec5a2cb974ca9c387ad8c0a6` |
| `envelope-manifest.json` | 1,249 | `ea7ce5d98ba3dbf12075a934a675ac8ca3d482a7d6ec3915ec13c4ad5a5779ad` |
| `parent-receipt.json` | 14,465 | `0a6ce2070abb005c1cb5ac5ce2e462bf09a4683f99440f9e72fd84c477e02a09` |

The compression ratio was 0.0707265206. Each pack read 148,425,203 application
bytes and wrote 9,817,903 application bytes. Both observed exactly three exFAT
AppleDouble files before private publication cleanup: 12,288 logical bytes and
1,572,864 allocated bytes. Peak observed temporary publication size was
10,354,479 logical bytes and 13,107,200 allocated bytes.

| Run | Wall seconds | CPU seconds | Peak RSS bytes |
|---|---:|---:|---:|
| package V1 | 186.552649125 | 31.746772 | 1,022,443,520 |
| package V2 | 170.931226292 | 31.822250 | 1,022,312,448 |

A fresh-process standalone verification of package V1 read 9,817,903 bytes,
wrote the 138,592,835-byte extracted child, used 689,684,480 peak RSS, and took
60.041181667 wall seconds and 13.544819 CPU seconds. The extracted file was
byte-identical to V22 and retained SHA-256
`cc7b3e0cf24e28976c11ef6bcbdfa1dd5fea36df42233783fe4a1fe81f36411e`.

### Failure modes

- The envelope is not signed and excludes a malicious or concurrently mutating
  host.
- Exact recompression is intentionally expensive and binds this development
  format to the reviewed compression implementation.
- Caught failures clean private and just-published directories, but power-loss
  residue remains unmeasured.
- The envelope does not provide a clean-Git approval lock, an executor resource
  policy, a verifier predecessor transition, or aggregate campaign accounting.
- A small deterministic package is not evidence that source advice predicts,
  locates, or decomposes elliptic-curve targets.

### Next concrete action

Write `supervised-executor-contract-v1.md` for a separately versioned trusted
parent executor that hash-binds this envelope, its clean Git base, exact argv,
resource and publication accounting, verifier transition, and fast-helper
negative control without changing the generic runner.

### Artifact paths

- `src/tt_supervised_artifact.py`
- `tests/test_supervised_artifact.py`
- `supervised-artifact-contract-v1.md`
- `/Volumes/Volume/autolab/tmp/tt-source-dev/source-supervised-envelope-development-v1`
- `/Volumes/Volume/autolab/tmp/tt-source-dev/source-supervised-envelope-development-v2`
- `/Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-recovered-development-v1.json`

### Reproduction commands

```bash
TMPDIR=/Volumes/Volume/autolab/tmp python3 -B \
  src/tt_supervised_artifact.py pack \
  --child-result /Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-staged-development-v22.json \
  --parent-receipt /Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-staging-receipt-development-v22.json \
  --output-dir /Volumes/Volume/autolab/tmp/tt-source-dev/source-supervised-envelope-development-v1

TMPDIR=/Volumes/Volume/autolab/tmp python3 -B \
  src/tt_supervised_artifact.py verify \
  --artifact-dir /Volumes/Volume/autolab/tmp/tt-source-dev/source-supervised-envelope-development-v1 \
  --extract-child /Volumes/Volume/autolab/tmp/tt-source-dev/source-generator-recovered-development-v1.json
```
