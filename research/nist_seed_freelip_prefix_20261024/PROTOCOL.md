# FreeLIP seven-output prefix: frozen call-level test

2026-10-24 UTC, before any new call-level reconstruction was run. This is a software-process audit, not a claim about the original invocation or a new mathematical weakness.

## Source and prediction

Use the unmodified `lip.c` and `lip.h` from FreeLIP 1.0, archive SHA-256 `cd168c2ba0f9052d84072664b559219506050f583fdf58060517d59422f5bccc`, retrieved from https://ftp.kh.edu.tw/Linux/Debian/debian-archive/dists/Debian-1.3.1/main/source/math/freelip_1.0.orig.tar.gz. The `lip.c` digest is `5c507451e8c13323f106a66b5f76cdf17dfbe9eb7f289eb1ac0c706855625bff`. Its `zrstarts` initializes the state without seven warm-up calls. Its `zprobprime(v,7)` runs one fixed-base test and seven random tests, while `zprime(v,8,2)` runs base 2 first and seven random bases. For a large prime v, each can plausibly consume the seven random states preceding the reconstructed May base points. Each `zrandom` may internally reject a state; exact state capture must check the actual calls rather than assume seven advances.

Fixed prediction: after seeding with each recovered small seed, either call on the field prime p or group order n, followed by the existing `zrandomb(p)` point loop, reproduces each of the six May published Gx values with 26-bit limbs. Such a fit would supply routine call sequences accounting for the prefix, but would not identify which sequence was used historically. Failure rejects the exact tested sequence/configuration only.

## Inputs and complete workload

Pin `traits.json` SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67` and `assessed.json` SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841` under `research/nist_seed_skipped_curves_20261016/`. Use exact field, coefficient, subgroup, generator and full UID from those records. The previously reported FreeLIP seeds, fixed here without a new seed search, are: prime192v1=20000; prime239v1=20420; prime239v2=20507; prime239v3=20509; prime192v2=20512; prime192v3=20517.

Build the original library in `SINGLE_MUL` mode (26-bit limbs) and in `PLAIN` mode (30-bit limbs), with the already documented modern compatibility changes: a temporary `malloc.h` including `stdlib.h`, `-include string.h`, `-DSIZEOFLONG=8`, `-std=gnu89`, `-O0`. Never alter library source. Record both executable digests, compiler, source/configuration and every call.

For each May curve, run eight 26-bit point routes: direct discard 7; `zprobprime(p,7)`; `zprobprime(n,7)`; `zprime(p,8,2)`; `zprime(n,8,2)`; and direct-discard controls 0, 6 and 8. Capture initialization state, state after prefix, return code, point attempts (at most 32), first accepted x and final state. Also run the direct-discard-7 route with 30-bit limbs for all six. This is 54 point cases. Record controls even if any unexpectedly match.

For all 21 named prime orders, run `zprime(n,8,2)` in 26-bit mode with a fixed seed 7157891; record classification and RNG states. Add n=101 and n=15 as small trial-division controls, with expected classifications one and zero. Total workload: **77 cases**, no seed search, no retuning. Ten-second per-process and 120-second whole-launch watchdogs; preserve build/call failures or censoring.

## Independent replay and inference

An independent Python implementation uses the multiplicative RNG modulo `2^107-1`, rejection-sampling bound, library limb packing and modular quadratic-residue test to replay every direct prefix and point case. Verify all captured states and all thirty proposed 26-bit call-route/Gx fits, retaining any mismatch. For source-call prefixes, check whether their captured state equals exactly seven recurrence advances; do not infer this from a successful prime classification alone. For the 21 large order calls, verify classifications and the predicted state count; the two small controls should consume no draws. Verify input/UID/digest bindings. Do not infer a historical call path, a reason for rejecting an omitted curve, or an ECDLP advantage from a fit.

Retain immutable run receipts, stdout/stderr, source/code/protocol/configuration hashes, exact curve identities, independent replay, dated report, editable figure/diagram and an inspected PDF. The original generator or logs remain the historical discriminator; none is assumed acquired by this audit.
