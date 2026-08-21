#!/usr/bin/env python3
"""Independent validator driver for Check 2 (TASK-20260820-047039).

Imports the implemented md5_collision_pair verification from harness/runner.py
at the snapshot commit and runs MY OWN known-false objects. Does NOT reuse the
producer's selftest.py; imports the same functions it tested.

Asserts nothing about MD5 (SC-2). This is a mechanical check of the certificate
logic's failure-naming on known-false inputs.
"""
import sys, os, json
REPO = "/Volumes/SSD990/crypto-autoresearcher"
sys.path.insert(0, REPO)
from harness.runner import (
    _verify_md5_collision_pair,
    _MD5_IMPL_FUNCS,
    _md5_pin_mechanism,
    PINNED_MD5_IMPLEMENTATIONS,
)

def md5hex(data: bytes) -> str:
    return hashlib.md5(data, usedforsecurity=False).hexdigest() if False else \
           _MD5_IMPL_FUNCS["IMPL-1"](data).hexdigest()

import hashlib  # noqa: E402

# True digests of single-byte messages, computed by BOTH pinned impls (so the
# "claimed digest" values used below are themselves cross-impl-confirmed).
m1_byte = b"a"   # hex "61"
m2_byte = b"b"   # hex "62"
d_m1_impl1 = _MD5_IMPL_FUNCS["IMPL-1"](m1_byte).hexdigest()
d_m1_impl3 = _MD5_IMPL_FUNCS["IMPL-3"](m1_byte).hexdigest()
d_m2_impl1 = _MD5_IMPL_FUNCS["IMPL-1"](m2_byte).hexdigest()
d_m2_impl3 = _MD5_IMPL_FUNCS["IMPL-3"](m2_byte).hexdigest()
print("=== CROSS-IMPL DIGESTS OF TEST MESSAGES ===")
print(f"MD5_impl1(b'a') = {d_m1_impl1}")
print(f"MD5_impl3(b'a') = {d_m1_impl3}")
print(f"MD5_impl1(b'b') = {d_m2_impl1}")
print(f"MD5_impl3(b'b') = {d_m2_impl3}")
print(f"impl1==impl3 on m1: {d_m1_impl1 == d_m1_impl3}")
print(f"impl1==impl3 on m2: {d_m2_impl1 == d_m2_impl3}")
print(f"m1 collides with m2: {d_m1_impl1 == d_m2_impl1}")

def run_case(name, m1_hex, m2_hex, claimed):
    cert = {
        "kind": "md5_collision_pair",
        "statement": {
            "messages": [m1_hex, m2_hex],
            "digest": claimed,
            "implementations": ["IMPL-1", "IMPL-3"],
        },
    }
    verified, failures = _verify_md5_collision_pair(cert)
    print(f"\n=== CASE: {name} ===")
    print(f"  m1={m1_hex!r} m2={m2_hex!r} claimed={claimed!r}")
    print(f"  verified={verified}")
    print(f"  failing_checks={failures}")
    print(f"  verified_by(wrapper-populated)={cert.get('verified_by')}")
    print(f"  pin_mechanism={cert.get('pin_mechanism')}")
    return verified, failures

print("\n\n########## CHECK 2: KNOWN-FALSE CERTIFICATE OBJECTS ##########")

# Object A: non-colliding pair, claimed digest = true MD5 of m1.
# m1 != m2, MD5(m1) != MD5(m2). claimed = MD5(m1). Expect verified:false with
# digest_mismatch_impl1_m2 and digest_mismatch_impl3_m2 (m2's digest != claimed).
vA, fA = run_case(
    "A_noncolliding_claimed_eq_md5_of_m1",
    "61", "62", d_m1_impl1,
)

# Object B: tampered digest (all zeros). m1 != m2. Expect verified:false with
# all four digest_mismatch_* checks.
vB, fB = run_case(
    "B_tampered_digest_allzero",
    "61", "62", "0" * 32,
)

# Object C: m1 == m2 with the CORRECT digest of that message.
# Expect verified:false with m1_equals_m2 (the equality check fires even though
# all four digests match the claimed value).
vC, fC = run_case(
    "C_m1_equals_m2_correct_digest",
    "61", "61", d_m1_impl1,
)

print("\n\n########## PIN-MECHANISM CHECK (IMPL-1 vs IMPL-3 distinctness) ##########")
pin_record, pin_distinct = _md5_pin_mechanism(_MD5_IMPL_FUNCS)
print(f"PINNED_MD5_IMPLEMENTATIONS = {PINNED_MD5_IMPLEMENTATIONS}")
print(f"pin_record = {json.dumps(pin_record, indent=2)}")
print(f"distinct = {pin_distinct}")
for impl_id in PINNED_MD5_IMPLEMENTATIONS:
    rec = pin_record[impl_id]
    print(f"  {impl_id}: module_file={rec['module_file']}")
    print(f"  {impl_id}: runtime_type={rec['runtime_type']}")

print("\n\n########## SUMMARY ##########")
print(f"Case A verified={vA} failures={fA}  (expected verified=False)")
print(f"Case B verified={vB} failures={fB}  (expected verified=False)")
print(f"Case C verified={vC} failures={fC}  (expected verified=False)")
print(f"pin_distinct={pin_distinct}  (expected True)")
all_false = (not vA) and (not vB) and (not vC)
print(f"ALL_KNOWN_FALSE_OBJECTS_VERIFIED_FALSE = {all_false}")
